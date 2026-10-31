from typing import Any, Optional
from pydantic import BaseModel, Field

class TimelineStep(BaseModel):
    step: str
    status: str  # "completed", "running", "failed", "skipped", "warning"
    message: str
    timestamp: str
    details: Optional[dict[str, Any]] = None

class ExecutionAttemptItem(BaseModel):
    attempt_number: int
    code: str
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    diagnosis: Optional[str] = None
    duration_ms: float

class AnalysisQueryRequest(BaseModel):
    dataset_id: str
    query: str
    demo_force_error: bool = False  # Allows intentional demo of self-healing error recovery
    provider: Optional[str] = None   # "mock", "gemini", "openai"

class AnalysisResult(BaseModel):
    id: str
    dataset_id: str
    query: str
    status: str  # "success", "repaired", "failed"
    duration_ms: float
    repair_attempts_count: int
    final_code: str
    explanation: str
    chart_type: Optional[str] = None  # "bar", "line", "pie", "area", "scatter", "none"
    chart_data: Optional[list[dict[str, Any]]] = None
    result_table: Optional[list[dict[str, Any]]] = None
    summary_stats: Optional[dict[str, Any]] = None
    timeline: list[TimelineStep]
    attempts: list[ExecutionAttemptItem]
    created_at: str

class AnalysisHistoryItem(BaseModel):
    id: str
    dataset_id: str
    dataset_name: Optional[str] = None
    query: str
    status: str
    duration_ms: float
    repair_attempts_count: int
    chart_type: Optional[str] = None
    created_at: str
