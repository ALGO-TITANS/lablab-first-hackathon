import pytest
import pandas as pd
from app.services.csv_service import CSVService

def test_validate_and_load_valid_csv():
    csv_bytes = b"id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300\n"
    df, encoding = CSVService.validate_and_load(csv_bytes, "test.csv")
    assert len(df) == 3
    assert list(df.columns) == ["id", "name", "value"]
    assert df["value"].sum() == 600

def test_validate_and_load_semicolon_delimited():
    csv_bytes = b"city;temperature;humidity\nKarachi;34;70\nLahore;32;65\n"
    df, encoding = CSVService.validate_and_load(csv_bytes, "climate.csv")
    assert len(df) == 2
    assert "city" in df.columns
    assert len(df.columns) == 3

def test_empty_csv_raises_error():
    with pytest.raises(ValueError, match="empty"):
        CSVService.validate_and_load(b"", "empty.csv")

def test_analyze_dataset_metadata():
    csv_bytes = b"product,price,quantity,is_active\nWidget A,25.5,10,True\nWidget B,15.0,20,False\n"
    df, _ = CSVService.validate_and_load(csv_bytes, "inventory.csv")
    meta = CSVService.analyze_dataset(df, "test-id", "inventory.csv", "/tmp/inventory.csv", len(csv_bytes))
    
    assert meta.row_count == 2
    assert meta.column_count == 4
    assert "price" in meta.summary.numerical_columns
    assert "product" in meta.summary.categorical_columns
