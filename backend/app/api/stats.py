from fastapi import APIRouter
from app.db.database import get_db_connection

router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("/dashboard")
def get_dashboard_metrics():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM datasets")
        total_datasets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM analyses")
        total_queries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM analyses WHERE status = 'success'")
        successful_executions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM analyses WHERE status = 'repaired'")
        repaired_executions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM analyses WHERE status = 'failed'")
        failed_executions = cursor.fetchone()[0]

        # Recent datasets
        cursor.execute("SELECT id, name, original_filename, file_size_bytes, row_count, column_count, created_at FROM datasets ORDER BY created_at DESC LIMIT 5")
        recent_datasets = [dict(r) for r in cursor.fetchall()]

        # Recent activities
        cursor.execute("""
        SELECT a.id, a.dataset_id, d.name as dataset_name, a.query, a.status,
               a.duration_ms, a.repair_attempts_count, a.chart_type, a.created_at
        FROM analyses a
        LEFT JOIN datasets d ON a.dataset_id = d.id
        ORDER BY a.created_at DESC LIMIT 5
        """)
        recent_analyses = [dict(r) for r in cursor.fetchall()]

        return {
            "total_datasets": total_datasets,
            "total_queries": total_queries,
            "successful_executions": successful_executions,
            "repaired_executions": repaired_executions,
            "failed_executions": failed_executions,
            "total_successful_with_repairs": successful_executions + repaired_executions,
            "recent_datasets": recent_datasets,
            "recent_analyses": recent_analyses,
            "ai_worker_status": "Online & Sandboxed"
        }
