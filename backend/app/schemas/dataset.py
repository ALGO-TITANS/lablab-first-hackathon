from typing import Any, Optional
from pydantic import BaseModel, Field

class ColumnMeta(BaseModel):
    name: str
    data_type: str
    non_null_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: list[Any] = []
    is_numeric: bool = False
    is_datetime: bool = False
    is_categorical: bool = False
    stats: Optional[dict[str, Any]] = None

class DatasetSummary(BaseModel):
    total_rows: int
    total_columns: int
    total_cells: int
    missing_cells: int
    missing_percentage: float
    duplicate_rows: int
    numerical_columns: list[str]
    categorical_columns: list[str]
    datetime_columns: list[str]
    overview_text: str

class DatasetResponse(BaseModel):
    id: str
    name: str
    original_filename: str
    file_size_bytes: int
    row_count: int
    column_count: int
    columns: list[ColumnMeta]
    summary: DatasetSummary
    created_at: str

class DatasetListItem(BaseModel):
    id: str
    name: str
    original_filename: str
    file_size_bytes: int
    row_count: int
    column_count: int
    created_at: str

class DatasetPreviewResponse(BaseModel):
    id: str
    name: str
    total_rows: int
    total_columns: int
    columns: list[str]
    rows: list[dict[str, Any]]
