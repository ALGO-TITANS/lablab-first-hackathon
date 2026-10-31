import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.config import settings
from app.db.database import get_db_connection
from app.schemas.analysis import (
    AnalysisQueryRequest, AnalysisResult, AnalysisHistoryItem,
    TimelineStep, ExecutionAttemptItem
)
from app.services.self_healing_orchestrator import SelfHealingOrchestrator

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

@router.post("/query", response_model=AnalysisResult)
async def run_query(request: AnalysisQueryRequest):
    try:
        result = await SelfHealingOrchestrator.process_analysis(request)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        detail = f"Analysis orchestrator error: {str(e)}" if settings.DEBUG else "An error occurred while processing the analysis request."
        raise HTTPException(status_code=500, detail=detail)

@router.get("/history", response_model=List[AnalysisHistoryItem])
def get_analysis_history(dataset_id: Optional[str] = Query(None)):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if dataset_id:
            cursor.execute("""
            SELECT a.id, a.dataset_id, d.name as dataset_name, a.query, a.status,
                   a.duration_ms, a.repair_attempts_count, a.chart_type, a.created_at
            FROM analyses a
            LEFT JOIN datasets d ON a.dataset_id = d.id
            WHERE a.dataset_id = ?
            ORDER BY a.created_at DESC
            """, (dataset_id,))
        else:
            cursor.execute("""
            SELECT a.id, a.dataset_id, d.name as dataset_name, a.query, a.status,
                   a.duration_ms, a.repair_attempts_count, a.chart_type, a.created_at
            FROM analyses a
            LEFT JOIN datasets d ON a.dataset_id = d.id
            ORDER BY a.created_at DESC
            """)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.get("/{analysis_id}", response_model=AnalysisResult)
def get_analysis_details(analysis_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Analysis record not found.")

        # Fetch execution attempts
        cursor.execute("SELECT * FROM execution_attempts WHERE analysis_id = ? ORDER BY attempt_number ASC", (analysis_id,))
        attempt_rows = cursor.fetchall()

        attempts = [
            ExecutionAttemptItem(
                attempt_number=r["attempt_number"],
                code=r["code"],
                success=bool(r["success"]),
                error_type=r["error_type"],
                error_message=r["error_message"],
                error_traceback=r["error_traceback"],
                diagnosis=r["diagnosis"],
                duration_ms=r["duration_ms"]
            )
            for r in attempt_rows
        ]

        timeline_data = json.loads(row["timeline_json"])
        timeline = [TimelineStep(**t) for t in timeline_data]

        return AnalysisResult(
            id=row["id"],
            dataset_id=row["dataset_id"],
            query=row["query"],
            status=row["status"],
            duration_ms=row["duration_ms"],
            repair_attempts_count=row["repair_attempts_count"],
            final_code=row["final_code"],
            explanation=row["explanation"] or "",
            chart_type=row["chart_type"] or "none",
            chart_data=json.loads(row["chart_data_json"]) if row["chart_data_json"] else [],
            result_table=json.loads(row["result_table_json"]) if row["result_table_json"] else [],
            summary_stats=json.loads(row["summary_stats_json"]) if row["summary_stats_json"] else {},
            timeline=timeline,
            attempts=attempts,
            created_at=row["created_at"]
        )
