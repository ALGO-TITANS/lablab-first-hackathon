import os
import json
import uuid
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import settings
from app.db.database import get_db_connection, get_utc_now_iso
from app.services.csv_service import CSVService
from app.schemas.dataset import (
    DatasetResponse, DatasetListItem, DatasetPreviewResponse
)

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

@router.post("/upload", response_model=DatasetResponse)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".csv", ".tsv", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only .csv, .tsv, and delimited text files are accepted."
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    try:
        df, encoding = CSVService.validate_and_load(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV validation failed: {str(e)}"
        )

    dataset_id = str(uuid.uuid4())
    safe_filename = f"{dataset_id}_{Path(file.filename).name}"
    dest_path = settings.UPLOADS_DIR / safe_filename
    dest_path.write_bytes(file_bytes)

    # Analyze metadata
    analysis = CSVService.analyze_dataset(
        df=df,
        dataset_id=dataset_id,
        original_filename=file.filename,
        file_path=str(dest_path),
        file_size=len(file_bytes)
    )

    # Save to SQLite
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO datasets (
            id, name, original_filename, file_path, file_size_bytes,
            row_count, column_count, columns_json, summary_json, is_sample, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis.id,
            analysis.name,
            analysis.original_filename,
            str(dest_path),
            analysis.file_size_bytes,
            analysis.row_count,
            analysis.column_count,
            json.dumps([c.model_dump() for c in analysis.columns]),
            json.dumps(analysis.summary.model_dump()),
            0,
            analysis.created_at
        ))
        conn.commit()

    return analysis

@router.get("", response_model=List[DatasetListItem])
def list_datasets():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, original_filename, file_size_bytes, row_count, column_count, created_at FROM datasets ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        return DatasetResponse(
            id=row["id"],
            name=row["name"],
            original_filename=row["original_filename"],
            file_size_bytes=row["file_size_bytes"],
            row_count=row["row_count"],
            column_count=row["column_count"],
            columns=json.loads(row["columns_json"]),
            summary=json.loads(row["summary_json"]),
            created_at=row["created_at"]
        )

@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def get_dataset_preview(dataset_id: str, limit: int = 50):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        try:
            import pandas as pd
            df = pd.read_csv(row["file_path"], nrows=limit)
            # Replace NaNs for clean JSON output
            df_cleaned = df.where(pd.notnull(df), None)
            return DatasetPreviewResponse(
                id=row["id"],
                name=row["name"],
                total_rows=row["row_count"],
                total_columns=row["column_count"],
                columns=list(df.columns),
                rows=df_cleaned.to_dict(orient="records")
            )
        except Exception as e:
            detail = f"Failed to read dataset preview: {str(e)}" if settings.DEBUG else "Failed to read dataset preview."
            raise HTTPException(status_code=500, detail=detail)

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        file_path = Path(row["file_path"])
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

        cursor.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
        conn.commit()

    return {"message": "Dataset and associated analysis records deleted successfully."}

@router.post("/load-sample/{sample_name}", response_model=DatasetResponse)
async def load_sample_dataset(sample_name: str):
    filename_map = {
        "sales": "global_sales_transactions.csv",
        "churn": "customer_churn_metrics.csv"
    }

    if sample_name not in filename_map:
        raise HTTPException(status_code=400, detail=f"Unknown sample dataset. Choose from: {list(filename_map.keys())}")

    sample_root = settings.SAMPLE_DATA_DIR.resolve()
    src_file = (settings.SAMPLE_DATA_DIR / filename_map[sample_name]).resolve()
    # Path traversal security validation: ensure resolved path is strictly inside SAMPLE_DATA_DIR
    try:
        src_file.relative_to(sample_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sample file path.")

    if not src_file.is_file():
        raise HTTPException(status_code=404, detail="Sample dataset file not found on disk.")

    file_bytes = src_file.read_bytes()
    df, _ = CSVService.validate_and_load(file_bytes, src_file.name)

    dataset_id = str(uuid.uuid4())
    safe_filename = f"{dataset_id}_{src_file.name}"
    dest_root = settings.UPLOADS_DIR.resolve()
    dest_path = (settings.UPLOADS_DIR / safe_filename).resolve()
    try:
        dest_path.relative_to(dest_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid destination file path.")

    dest_path.write_bytes(file_bytes)

    analysis = CSVService.analyze_dataset(
        df=df,
        dataset_id=dataset_id,
        original_filename=src_file.name,
        file_path=str(dest_path),
        file_size=len(file_bytes)
    )

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO datasets (
            id, name, original_filename, file_path, file_size_bytes,
            row_count, column_count, columns_json, summary_json, is_sample, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis.id,
            analysis.name,
            analysis.original_filename,
            str(dest_path),
            analysis.file_size_bytes,
            analysis.row_count,
            analysis.column_count,
            json.dumps([c.model_dump() for c in analysis.columns]),
            json.dumps(analysis.summary.model_dump()),
            1,
            analysis.created_at
        ))
        conn.commit()

    return analysis
