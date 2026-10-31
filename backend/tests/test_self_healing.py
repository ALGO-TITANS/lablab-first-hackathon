import pytest
import json
import uuid
import tempfile
from pathlib import Path
from app.db.database import init_db, get_db_connection, get_utc_now_iso
from app.services.self_healing_orchestrator import SelfHealingOrchestrator
from app.schemas.analysis import AnalysisQueryRequest

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def registered_dataset():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("region,revenue,profit\nNorth,1000,200\nSouth,2000,400\nEast,1500,300\nWest,2500,500\n")
        path = f.name

    dataset_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        columns_meta = [
            {"name": "region", "data_type": "object", "non_null_count": 4, "null_count": 0, "null_percentage": 0.0, "unique_count": 4, "sample_values": ["North"], "is_numeric": False, "is_datetime": False, "is_categorical": True},
            {"name": "revenue", "data_type": "int64", "non_null_count": 4, "null_count": 0, "null_percentage": 0.0, "unique_count": 4, "sample_values": [1000], "is_numeric": True, "is_datetime": False, "is_categorical": False},
            {"name": "profit", "data_type": "int64", "non_null_count": 4, "null_count": 0, "null_percentage": 0.0, "unique_count": 4, "sample_values": [200], "is_numeric": True, "is_datetime": False, "is_categorical": False}
        ]
        summary_meta = {
            "total_rows": 4, "total_columns": 3, "total_cells": 12, "missing_cells": 0,
            "missing_percentage": 0.0, "duplicate_rows": 0,
            "numerical_columns": ["revenue", "profit"], "categorical_columns": ["region"],
            "datetime_columns": [], "overview_text": "Sales test dataset"
        }
        cursor.execute("""
        INSERT INTO datasets (
            id, name, original_filename, file_path, file_size_bytes,
            row_count, column_count, columns_json, summary_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dataset_id, "Sales Test", "sales_test.csv", path, 100, 4, 3,
            json.dumps(columns_meta), json.dumps(summary_meta), get_utc_now_iso()
        ))
        conn.commit()

    yield dataset_id
    Path(path).unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_self_healing_recovery_workflow(registered_dataset):
    # Request with demo_force_error=True triggers an intentional first-attempt failure
    req = AnalysisQueryRequest(
        dataset_id=registered_dataset,
        query="Show total revenue by region",
        demo_force_error=True,
        provider="mock"
    )

    result = await SelfHealingOrchestrator.process_analysis(req)

    # Assert recovery occurred
    assert result.status == "repaired"
    assert result.repair_attempts_count == 1
    assert len(result.attempts) == 2

    # Attempt 1: Failed
    assert result.attempts[0].success is False
    assert result.attempts[0].error_type == "KeyError"

    # Attempt 2: Repaired & Successful
    assert result.attempts[1].success is True
    assert result.attempts[1].diagnosis is not None

    # Timeline verification
    step_names = [s.step for s in result.timeline]
    assert "Understanding request" in step_names
    assert "Generating Python code" in step_names
    assert "Validating code" in step_names
    assert "Executing analysis" in step_names
    assert "Detecting error" in step_names
    assert "Repairing code" in step_names
    assert "Verifying results" in step_names
    assert "Analysis completed" in step_names
    assert len(result.result_table) > 0

@pytest.mark.asyncio
async def test_successful_first_try_analysis(registered_dataset):
    req = AnalysisQueryRequest(
        dataset_id=registered_dataset,
        query="What is the top region by revenue?",
        demo_force_error=False,
        provider="mock"
    )

    result = await SelfHealingOrchestrator.process_analysis(req)
    assert result.status == "success"
    assert result.repair_attempts_count == 0
    assert len(result.attempts) == 1
    assert result.attempts[0].success is True
