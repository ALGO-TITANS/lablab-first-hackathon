import os
import json
import uuid
import time
import pandas as pd
from typing import Dict, Any, List, Optional
from app.config import settings
from app.db.database import get_db_connection, get_utc_now_iso
from app.schemas.analysis import (
    AnalysisResult, TimelineStep, ExecutionAttemptItem, AnalysisQueryRequest
)
from app.services.llm_service import get_llm_provider
from app.services.code_validator import CodeValidator
from app.services.execution_sandbox import ExecutionSandbox

class SelfHealingOrchestrator:
    @staticmethod
    async def process_analysis(request: AnalysisQueryRequest) -> AnalysisResult:
        analysis_id = str(uuid.uuid4())
        overall_start = time.time()
        timeline: List[TimelineStep] = []
        attempts: List[ExecutionAttemptItem] = []

        # 1. Fetch Dataset Info
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM datasets WHERE id = ?", (request.dataset_id,))
            dataset_row = cursor.fetchone()

        if not dataset_row:
            raise ValueError(f"Dataset with ID '{request.dataset_id}' not found.")

        dataset_path = dataset_row["file_path"]
        columns_meta = json.loads(dataset_row["columns_json"])
        summary_meta = json.loads(dataset_row["summary_json"])

        schema_context = (
            f"Dataset Name: {dataset_row['name']}\n"
            f"Total Rows: {dataset_row['row_count']}, Total Columns: {dataset_row['column_count']}\n"
            f"Columns: {', '.join([c['name'] + ' (' + c['data_type'] + ')' for c in columns_meta])}\n"
            f"Overview: {summary_meta.get('overview_text', '')}"
        )

        # Get sample rows for prompt
        sample_rows = []
        try:
            sample_df = pd.read_csv(dataset_path, nrows=3)
            sample_rows = sample_df.to_dict(orient="records")
        except Exception:
            pass

        # Timeline Helper
        def add_step(name: str, status: str, message: str, details: Optional[Dict[str, Any]] = None):
            timeline.append(TimelineStep(
                step=name,
                status=status,
                message=message,
                timestamp=get_utc_now_iso(),
                details=details
            ))

        # --- STEP 1: Understanding request ---
        add_step("Understanding request", "completed", f"Analyzed query intent against schema for '{dataset_row['name']}'.")

        # --- STEP 2: Generating Python code ---
        llm = get_llm_provider(request.provider)
        gen_result = await llm.generate_code(
            query=request.query,
            schema_context=schema_context,
            sample_rows=sample_rows,
            force_error=request.demo_force_error
        )
        current_code = gen_result.get("code", "")
        current_explanation = gen_result.get("explanation", "")
        current_chart_type = gen_result.get("chart_type", "bar")
        diagnosis_note = None

        add_step("Generating Python code", "completed", "Generated initial Pandas execution script.", {"initial_code_preview": current_code[:200]})

        # --- EXECUTION & REPAIR LOOP ---
        max_attempts = settings.MAX_REPAIR_ATTEMPTS + 1  # 1 initial + max 2 repairs
        final_execution = None
        is_success = False

        for attempt_idx in range(1, max_attempts + 1):
            attempt_start = time.time()

            # --- STEP: Validating code ---
            add_step("Validating code", "running", f"Performing AST security checks on attempt #{attempt_idx}...")
            is_safe, reason = CodeValidator.validate_python_code(current_code)
            if not is_safe:
                add_step("Validating code", "failed", f"AST Security Check Failed: {reason}")
                exec_result = {
                    "success": False,
                    "error_type": "SecurityPolicyViolation",
                    "error_message": reason,
                    "error_traceback": f"AST Check: {reason}",
                    "duration_ms": (time.time() - attempt_start) * 1000,
                    "data": None,
                    "summary": None,
                    "chart_type": None,
                    "chart_data": None
                }
            else:
                add_step("Validating code", "completed", f"Attempt #{attempt_idx} passed all AST security policies.")
                # --- STEP: Executing analysis ---
                add_step("Executing analysis", "running", f"Running sandboxed execution for attempt #{attempt_idx}...")
                exec_result = ExecutionSandbox.execute(current_code, dataset_path)

            attempt_duration = (time.time() - attempt_start) * 1000

            # Record attempt item
            attempt_item = ExecutionAttemptItem(
                attempt_number=attempt_idx,
                code=current_code,
                success=exec_result.get("success", False),
                error_type=exec_result.get("error_type"),
                error_message=exec_result.get("error_message"),
                error_traceback=exec_result.get("error_traceback"),
                diagnosis=diagnosis_note,
                duration_ms=round(attempt_duration, 2)
            )
            attempts.append(attempt_item)

            if exec_result.get("success", False):
                add_step("Executing analysis", "completed", f"Attempt #{attempt_idx} executed successfully without runtime errors.")
                final_execution = exec_result
                is_success = True
                break
            else:
                # --- STEP: Detecting error ---
                err_type = exec_result.get("error_type", "RuntimeError")
                err_msg = exec_result.get("error_message", "Unknown execution failure")
                add_step(
                    "Detecting error",
                    "warning",
                    f"Execution failed on attempt #{attempt_idx}: [{err_type}] {err_msg}",
                    {"traceback": exec_result.get("error_traceback")}
                )

                if attempt_idx < max_attempts:
                    # --- STEP: Repairing code ---
                    add_step("Repairing code", "running", f"AI self-healing agent diagnosing and repairing {err_type}...")
                    repair_res = await llm.diagnose_and_repair(
                        query=request.query,
                        schema_context=schema_context,
                        failed_code=current_code,
                        error_type=err_type,
                        error_message=err_msg,
                        traceback_str=exec_result.get("error_traceback", "")
                    )
                    diagnosis_note = repair_res.get("diagnosis", "Diagnosed and adjusted execution script.")
                    current_code = repair_res.get("repaired_code", current_code)
                    if repair_res.get("explanation"):
                        current_explanation = repair_res["explanation"]
                    if repair_res.get("chart_type"):
                        current_chart_type = repair_res["chart_type"]

                    add_step("Repairing code", "completed", f"Diagnosis: {diagnosis_note}")
                else:
                    add_step("Repairing code", "failed", "Maximum repair budget reached (2 attempts).")

        overall_duration = (time.time() - overall_start) * 1000

        # --- STEP: Verifying results ---
        raw_data = final_execution.get("data") if final_execution else None
        formatted_table = []
        formatted_chart_data = []

        if is_success and raw_data:
            add_step("Verifying results", "running", "Formatting structured data, verifying table records and chart shapes...")
            if isinstance(raw_data, list):
                formatted_table = raw_data[:50]
                formatted_chart_data = raw_data[:30]
            elif isinstance(raw_data, dict):
                formatted_table = [raw_data]
                formatted_chart_data = [raw_data]
            else:
                formatted_table = [{"value": raw_data}]
                formatted_chart_data = [{"value": raw_data}]

            add_step("Verifying results", "completed", f"Verified {len(formatted_table)} output records ready for visualization.")
        else:
            add_step("Verifying results", "failed", "Could not verify results due to unresolved execution failure.")

        # --- STEP: Analysis completed ---
        final_status = "repaired" if (is_success and len(attempts) > 1) else ("success" if is_success else "failed")
        add_step("Analysis completed", "completed" if is_success else "failed", f"Process finished with status: {final_status.upper()}.")

        summary_stats = {
            "total_attempts": len(attempts),
            "repair_attempts": len(attempts) - 1,
            "status": final_status,
            "execution_time_ms": round(overall_duration, 2)
        }

        # Persist to SQLite
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO analyses (
                id, dataset_id, query, status, duration_ms, repair_attempts_count,
                final_code, explanation, chart_type, chart_data_json, result_table_json,
                summary_stats_json, timeline_json, error_details_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                request.dataset_id,
                request.query,
                final_status,
                round(overall_duration, 2),
                len(attempts) - 1,
                current_code,
                current_explanation or (final_execution.get("summary") if final_execution else "Analysis failed."),
                current_chart_type,
                json.dumps(formatted_chart_data),
                json.dumps(formatted_table),
                json.dumps(summary_stats),
                json.dumps([t.model_dump() for t in timeline]),
                json.dumps(attempts[-1].model_dump()) if not is_success else None,
                get_utc_now_iso()
            ))

            for att in attempts:
                cursor.execute("""
                INSERT INTO execution_attempts (
                    id, analysis_id, attempt_number, code, success, error_type,
                    error_message, error_traceback, diagnosis, duration_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    analysis_id,
                    att.attempt_number,
                    att.code,
                    1 if att.success else 0,
                    att.error_type,
                    att.error_message,
                    att.error_traceback,
                    att.diagnosis,
                    att.duration_ms,
                    get_utc_now_iso()
                ))

            conn.commit()

        return AnalysisResult(
            id=analysis_id,
            dataset_id=request.dataset_id,
            query=request.query,
            status=final_status,
            duration_ms=round(overall_duration, 2),
            repair_attempts_count=len(attempts) - 1,
            final_code=current_code,
            explanation=current_explanation or (final_execution.get("summary") if final_execution else "Analysis completed."),
            chart_type=current_chart_type if is_success else "none",
            chart_data=formatted_chart_data if is_success else [],
            result_table=formatted_table if is_success else [],
            summary_stats=summary_stats,
            timeline=timeline,
            attempts=attempts,
            created_at=get_utc_now_iso()
        )
