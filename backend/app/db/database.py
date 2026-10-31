import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from app.config import settings

def init_db():
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Datasets Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            row_count INTEGER NOT NULL,
            column_count INTEGER NOT NULL,
            columns_json TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            is_sample INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """)

        # Add is_sample column if existing database lacks it
        cursor.execute("PRAGMA table_info(datasets)")
        existing_cols = [r[1] for r in cursor.fetchall()]
        if "is_sample" not in existing_cols:
            cursor.execute("ALTER TABLE datasets ADD COLUMN is_sample INTEGER NOT NULL DEFAULT 0")

        # Analyses Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            dataset_id TEXT NOT NULL,
            query TEXT NOT NULL,
            status TEXT NOT NULL,
            duration_ms REAL NOT NULL,
            repair_attempts_count INTEGER NOT NULL DEFAULT 0,
            final_code TEXT NOT NULL,
            explanation TEXT,
            chart_type TEXT,
            chart_data_json TEXT,
            result_table_json TEXT,
            summary_stats_json TEXT,
            timeline_json TEXT NOT NULL,
            error_details_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
        )
        """)

        # Execution Attempts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_attempts (
            id TEXT PRIMARY KEY,
            analysis_id TEXT NOT NULL,
            attempt_number INTEGER NOT NULL,
            code TEXT NOT NULL,
            success INTEGER NOT NULL,
            error_type TEXT,
            error_message TEXT,
            error_traceback TEXT,
            diagnosis TEXT,
            duration_ms REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
        )
        """)
        
        conn.commit()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(str(settings.DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
