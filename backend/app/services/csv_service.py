import os
import uuid
try:
    import chardet
except ImportError:
    import charset_normalizer as chardet
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Any
from app.config import settings
from app.schemas.dataset import ColumnMeta, DatasetSummary, DatasetResponse

class CSVService:
    @staticmethod
    def detect_encoding(file_bytes: bytes) -> str:
        sample = file_bytes[:50000]
        result = chardet.detect(sample)
        encoding = result.get("encoding") or "utf-8"
        # Fallback if detection is ambiguous
        if encoding.lower() in ["ascii", "iso-8859-1", "windows-1252"]:
            try:
                sample.decode("utf-8")
                return "utf-8"
            except UnicodeDecodeError:
                return encoding
        return encoding

    @staticmethod
    def validate_and_load(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
        if not file_bytes:
            raise ValueError("The uploaded CSV file is empty.")

        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise ValueError(f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB} MB.")

        encoding = CSVService.detect_encoding(file_bytes)

        # Attempt to detect delimiter using Sniffer or find the delimiter that yields the most columns
        from io import BytesIO
        import csv
        sample_str = file_bytes[:10000].decode(encoding, errors="ignore")
        
        detected_sep = ","
        try:
            dialect = csv.Sniffer().sniff(sample_str, delimiters=[",", ";", "\t", "|"])
            detected_sep = dialect.delimiter
        except Exception:
            pass

        delimiters = [detected_sep] + [d for d in [",", ";", "\t", "|"] if d != detected_sep]
        df = None
        best_df = None
        max_cols = 0

        for sep in delimiters:
            try:
                df_candidate = pd.read_csv(BytesIO(file_bytes), sep=sep, encoding=encoding, engine="python")
                if len(df_candidate.columns) > max_cols:
                    max_cols = len(df_candidate.columns)
                    best_df = df_candidate
                    if max_cols > 1:
                        break
            except Exception:
                continue

        df = best_df if best_df is not None else pd.read_csv(BytesIO(file_bytes), encoding=encoding)

        if df.empty and len(df.columns) == 0:
            raise ValueError("Parsed dataset has 0 rows and 0 columns.")

        # Clean column names (strip whitespace, ensure uniqueness)
        cleaned_cols = []
        seen = {}
        for col in df.columns:
            clean = str(col).strip()
            if not clean:
                clean = "unnamed_column"
            if clean in seen:
                seen[clean] += 1
                clean = f"{clean}_{seen[clean]}"
            else:
                seen[clean] = 0
            cleaned_cols.append(clean)
        df.columns = cleaned_cols

        return df, encoding

    @staticmethod
    def analyze_dataset(df: pd.DataFrame, dataset_id: str, original_filename: str, file_path: str, file_size: int) -> DatasetResponse:
        total_rows = int(len(df))
        total_columns = int(len(df.columns))
        total_cells = total_rows * total_columns
        missing_cells = int(df.isna().sum().sum())
        missing_pct = round((missing_cells / total_cells * 100) if total_cells > 0 else 0, 2)
        duplicate_rows = int(df.duplicated().sum())

        numerical_cols = []
        categorical_cols = []
        datetime_cols = []
        columns_meta: list[ColumnMeta] = []

        for col in df.columns:
            series = df[col]
            non_null = int(series.count())
            null_count = int(series.isna().sum())
            null_pct = round((null_count / total_rows * 100) if total_rows > 0 else 0, 2)
            unique_count = int(series.nunique(dropna=True))

            # Sample values (up to 5 non-null, json serializable)
            sample_vals = []
            for val in series.dropna().head(5):
                if isinstance(val, (np.integer, int)):
                    sample_vals.append(int(val))
                elif isinstance(val, (np.floating, float)):
                    sample_vals.append(float(val) if not np.isnan(val) else None)
                elif isinstance(val, (bool, np.bool_)):
                    sample_vals.append(bool(val))
                else:
                    sample_vals.append(str(val))

            is_numeric = bool(pd.api.types.is_numeric_dtype(series))
            is_datetime = False
            is_categorical = False
            stats: dict[str, Any] = {}

            if is_numeric:
                numerical_cols.append(col)
                clean_num = series.dropna()
                if not clean_num.empty:
                    stats = {
                        "min": float(clean_num.min()),
                        "max": float(clean_num.max()),
                        "mean": round(float(clean_num.mean()), 3),
                        "median": round(float(clean_num.median()), 3),
                        "std": round(float(clean_num.std()), 3) if len(clean_num) > 1 else 0.0
                    }
            else:
                # Check if potential datetime
                if series.dtype == "object":
                    sample_head = series.dropna().head(20)
                    try:
                        if not sample_head.empty:
                            pd.to_datetime(sample_head, errors="raise")
                            is_datetime = True
                            datetime_cols.append(col)
                    except Exception:
                        pass

                if not is_datetime:
                    is_categorical = True
                    categorical_cols.append(col)
                    top_vals = series.value_counts(dropna=True).head(5).to_dict()
                    stats = {"top_frequencies": {str(k): int(v) for k, v in top_vals.items()}}

            col_meta = ColumnMeta(
                name=col,
                data_type=str(series.dtype),
                non_null_count=non_null,
                null_count=null_count,
                null_percentage=null_pct,
                unique_count=unique_count,
                sample_values=sample_vals,
                is_numeric=is_numeric,
                is_datetime=is_datetime,
                is_categorical=is_categorical,
                stats=stats
            )
            columns_meta.append(col_meta)

        overview_text = (
            f"Dataset '{original_filename}' contains {total_rows:,} rows across {total_columns} columns. "
            f"It features {len(numerical_cols)} numerical dimensions ({', '.join(numerical_cols[:4])}{'...' if len(numerical_cols) > 4 else ''}) "
            f"and {len(categorical_cols)} categorical fields. "
            f"Data quality is solid with {missing_cells} missing values ({missing_pct}% total missingness) "
            f"and {duplicate_rows} duplicate rows."
        )

        summary = DatasetSummary(
            total_rows=total_rows,
            total_columns=total_columns,
            total_cells=total_cells,
            missing_cells=missing_cells,
            missing_percentage=missing_pct,
            duplicate_rows=duplicate_rows,
            numerical_columns=numerical_cols,
            categorical_columns=categorical_cols,
            datetime_columns=datetime_cols,
            overview_text=overview_text
        )

        from app.db.database import get_utc_now_iso

        return DatasetResponse(
            id=dataset_id,
            name=Path(original_filename).stem,
            original_filename=original_filename,
            file_size_bytes=file_size,
            row_count=total_rows,
            column_count=total_columns,
            columns=columns_meta,
            summary=summary,
            created_at=get_utc_now_iso()
        )
