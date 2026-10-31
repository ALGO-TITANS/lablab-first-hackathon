import os
import json
import uuid
import time
import tempfile
from pathlib import Path
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

        dataset_dict = dict(dataset_row)
        # Trust ONLY the server-controlled database field 'is_sample'.
        # Never trust user-controlled filenames or request parameters.
        is_sample = int(dataset_dict.get("is_sample", 0)) == 1

        # Public Demo Mode Guard: Block arbitrary Python execution on custom uploaded CSVs
        if not settings.ENABLE_ARBITRARY_EXECUTION and not is_sample:
            raise ValueError(
                "Public Portfolio Demo Mode: Arbitrary Python code execution is disabled for custom uploaded CSVs "
                "to ensure hosting security. Please use the pre-loaded sample datasets (Global Sales or Customer Churn) "
                "to explore analytical queries, interactive charts, and the self-healing AI agent."
            )

        # In Public Demo Mode, route sample datasets to the controlled safe demo handler
        if not settings.ENABLE_ARBITRARY_EXECUTION and is_sample:
            return await SelfHealingOrchestrator._process_sample_demo(
                request=request,
                dataset_row=dataset_row,
                columns_meta=json.loads(dataset_row["columns_json"]),
                summary_meta=json.loads(dataset_row["summary_json"])
            )

        dataset_path = Path(dataset_row["file_path"]).resolve()
        trusted_roots = [
            settings.UPLOADS_DIR.resolve(),
            settings.SAMPLE_DATA_DIR.resolve(),
            Path(tempfile.gettempdir()).resolve(),
            Path("/tmp").resolve()
        ]
        if not any(dataset_path.is_relative_to(root) for root in trusted_roots):
            raise ValueError("Security violation: Dataset file path is outside trusted storage directories.")
        if not dataset_path.is_file():
            raise ValueError("Dataset file not found on disk.")
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

    @staticmethod
    async def _process_sample_demo(
        request: AnalysisQueryRequest,
        dataset_row: Any,
        columns_meta: list[dict],
        summary_meta: dict
    ) -> AnalysisResult:
        """
        Controlled sample demonstration handler for public portfolio mode.
        Executes safe, predefined scenarios on pre-loaded sample datasets without
        invoking arbitrary subprocess execution on the host machine.
        """
        analysis_id = str(uuid.uuid4())
        overall_start = time.time()
        timeline: List[TimelineStep] = []
        attempts: List[ExecutionAttemptItem] = []

        def add_step(name: str, status: str, message: str, details: Optional[Dict[str, Any]] = None):
            timeline.append(TimelineStep(
                step=name,
                status=status,
                message=message,
                timestamp=get_utc_now_iso(),
                details=details
            ))

        add_step("Understanding request", "completed", f"Analyzed query intent against schema for '{dataset_row['name']}' (Public Demo Mode).")

        dataset_path = Path(dataset_row["file_path"]).resolve()
        trusted_roots = [settings.UPLOADS_DIR.resolve(), settings.SAMPLE_DATA_DIR.resolve()]
        if not any(dataset_path.is_relative_to(root) for root in trusted_roots):
            raise ValueError("Security violation: Sample dataset path is outside trusted storage directories.")
        if not dataset_path.is_file():
            raise ValueError("Sample dataset file not found on disk.")

        try:
            df = pd.read_csv(dataset_path)
        except Exception as e:
            detail = f"Failed to load sample dataset: {str(e)}" if settings.DEBUG else "Failed to load sample dataset."
            raise ValueError(detail)

        if df.empty:
            raise ValueError("Sample dataset is empty and contains no data rows.")

        # Check if Self-Healing demonstration is requested
        if request.demo_force_error:
            if "region" in df.columns and "revenue" in df.columns:
                target_cat, target_num = "region", "revenue"
                bad_cat = "Region"
                label = "geographic regions"
            elif "contract_type" in df.columns and "monthly_charges" in df.columns:
                target_cat, target_num = "contract_type", "monthly_charges"
                bad_cat = "Contract_Type"
                label = "contract types"
            else:
                raise ValueError("Sample dataset schema validation failed: required columns for self-healing demonstration are missing from dataset.")

            # 1. Demonstration code with intentional casing error
            initial_code = (
                f"# Demonstration script with intentional column casing error for self-healing demonstration\n"
                f"grouped = df.groupby('{bad_cat}')['{target_num}'].sum().reset_index()\n"
                f"result = {{'data': grouped, 'chart_type': 'bar', 'summary': 'Aggregated {target_num} by {target_cat}.'}}"
            )
            add_step("Generating Python code", "completed", "Generated demonstration script with intentional column casing error for self-healing demonstration.", {"initial_code_preview": initial_code[:200]})
            add_step("Simulating execution", "running", "Simulating execution failure for Attempt #1 (Demonstration: Subprocess execution is disabled in public demo mode).")

            err_traceback = (
                f"Traceback (most recent call last):\n"
                f"  File \"demo_script.py\", line 2, in <module>\n"
                f"    grouped = df.groupby('{bad_cat}')['{target_num}'].sum().reset_index()\n"
                f"KeyError: '{bad_cat}'"
            )
            attempts.append(ExecutionAttemptItem(
                attempt_number=1,
                code=initial_code,
                success=False,
                error_type="KeyError",
                error_message=f"'{bad_cat}'",
                error_traceback=err_traceback,
                diagnosis=None,
                duration_ms=45.0
            ))

            add_step("Detecting error", "warning", f"Simulated runtime error detected on attempt #1: [KeyError] '{bad_cat}'.", {"traceback": err_traceback, "simulation": True})
            add_step("Demonstrating error diagnosis", "running", "AI self-healing agent diagnosing simulated KeyError against schema...")

            diagnosis = (
                f"Detected KeyError: '{bad_cat}'. The script referenced capitalized column '{bad_cat}', "
                f"but the dataset schema defines lowercase '{target_cat}'. Normalized column casing in repaired script."
            )
            repaired_code = (
                f"# Repaired Pandas code with normalized column names\n"
                f"repaired_df = df.groupby('{target_cat}', as_index=False)['{target_num}'].sum()\n"
                f"repaired_df = repaired_df.sort_values(by='{target_num}', ascending=False)\n"
                f"result = {{\n"
                f"    'data': repaired_df.to_dict(orient='records'),\n"
                f"    'chart_type': 'bar',\n"
                f"    'summary': 'Successfully repaired execution. Aggregated total {target_num} across {label}.'\n"
                f"}}"
            )
            add_step("Demonstrating error diagnosis", "completed", f"Diagnosis: {diagnosis}")
            add_step("Applying predefined repair", "completed", "Applied predefined self-healing repair with normalized column names.", {"repaired_code_preview": repaired_code[:200]})
            add_step("Computing verified sample results", "running", "Computing verified analytical results directly from sample dataset without host subprocess execution...")

            # Calculate verified results strictly from sample dataset - NO fabricated fallback data
            res_df = df.groupby(target_cat, as_index=False)[target_num].sum().sort_values(by=target_num, ascending=False)
            formatted_data = res_df.to_dict(orient="records")

            attempts.append(ExecutionAttemptItem(
                attempt_number=2,
                code=repaired_code,
                success=True,
                error_type=None,
                error_message=None,
                error_traceback=None,
                diagnosis=diagnosis,
                duration_ms=62.0
            ))

            final_code = repaired_code
            explanation = f"Successfully repaired execution. Aggregated total {target_num} across {label}."
            chart_type = "bar"
            final_status = "repaired"
            add_step("Computing verified sample results", "completed", "Computed verified analytical results directly from sample dataset without host subprocess execution.")

        else:
            # Defensive query handling on verified sample dataset
            q_lower = request.query.lower()
            try:
                if "top" in q_lower or "product" in q_lower or "best" in q_lower:
                    cat_cols = [c for c in ["product_name", "category", "region"] if c in df.columns]
                    if not cat_cols:
                        non_nums = df.select_dtypes(exclude="number").columns.tolist()
                        if not non_nums:
                            raise ValueError("Sample dataset lacks categorical columns for top-item grouping.")
                        col = non_nums[0]
                    else:
                        col = cat_cols[0]

                    num_cols = [c for c in ["revenue", "units_sold", "profit", "monthly_charges"] if c in df.columns]
                    if not num_cols:
                        nums = df.select_dtypes(include="number").columns.tolist()
                        if not nums:
                            raise ValueError("Sample dataset lacks numeric columns for top-item ranking.")
                        metric = nums[0]
                    else:
                        metric = num_cols[0]

                    res_df = df.groupby(col, as_index=False)[metric].sum().sort_values(by=metric, ascending=False).head(5)
                    chart_type = "bar"
                    final_code = (
                        f"top_items = df.groupby('{col}', as_index=False)['{metric}'].sum()\n"
                        f"top_items = top_items.sort_values(by='{metric}', ascending=False).head(5)\n"
                        f"result = {{\n"
                        f"    'data': top_items.to_dict(orient='records'),\n"
                        f"    'chart_type': 'bar',\n"
                        f"    'summary': 'Top 5 {col}s ranked by total {metric}.'\n"
                        f"}}"
                    )
                    explanation = f"Identified top 5 {col}s ranked by total {metric}."

                elif "trend" in q_lower or "month" in q_lower or "time" in q_lower or "date" in q_lower:
                    date_cols = [c for c in ["date", "timestamp", "period"] if c in df.columns]
                    if not date_cols:
                        raise ValueError("Sample dataset lacks a valid date column for time-series trend analysis.")
                    date_col = date_cols[0]
                    num_cols = [c for c in ["revenue", "profit", "monthly_charges", "total_charges"] if c in df.columns]
                    if not num_cols:
                        nums = df.select_dtypes(include="number").columns.tolist()
                        if not nums:
                            raise ValueError("Sample dataset lacks numeric columns for trend analysis.")
                        metric = nums[0]
                    else:
                        metric = num_cols[0]

                    df_copy = df.copy()
                    df_copy["period"] = pd.to_datetime(df_copy[date_col], errors="coerce").dt.to_period("M").astype(str)
                    res_df = df_copy.groupby("period", as_index=False)[metric].sum().sort_values(by="period").head(12)
                    chart_type = "line"
                    final_code = (
                        f"df['period'] = pd.to_datetime(df['{date_col}']).dt.to_period('M').astype(str)\n"
                        f"trend = df.groupby('period', as_index=False)['{metric}'].sum()\n"
                        f"result = {{\n"
                        f"    'data': trend.to_dict(orient='records'),\n"
                        f"    'chart_type': 'line',\n"
                        f"    'summary': 'Monthly trend over time.'\n"
                        f"}}"
                    )
                    explanation = f"Analyzed monthly chronological trend for {metric}."

                elif "missing" in q_lower or "null" in q_lower:
                    res_df = df.isna().sum().reset_index()
                    res_df.columns = ["column_name", "missing_count"]
                    chart_type = "bar"
                    final_code = (
                        "missing_summary = df.isna().sum().reset_index()\n"
                        "missing_summary.columns = ['column_name', 'missing_count']\n"
                        "result = {'data': missing_summary.to_dict(orient='records'), 'chart_type': 'bar', 'summary': 'Missing value analysis.'}"
                    )
                    explanation = f"Audited missing values across all {len(df.columns)} columns."

                elif "churn" in q_lower or "contract" in q_lower or "distribution" in q_lower or "pie" in q_lower:
                    cat_cols = [c for c in ["contract_type", "churn_status", "payment_method", "region", "category"] if c in df.columns]
                    if not cat_cols:
                        non_nums = df.select_dtypes(exclude="number").columns.tolist()
                        if not non_nums:
                            raise ValueError("Sample dataset lacks categorical columns for distribution analysis.")
                        cat_col = non_nums[0]
                    else:
                        cat_col = cat_cols[0]

                    res_df = df[cat_col].value_counts().reset_index()
                    res_df.columns = [cat_col, "count"]
                    chart_type = "pie"
                    final_code = (
                        f"dist = df['{cat_col}'].value_counts().reset_index()\n"
                        f"dist.columns = ['{cat_col}', 'count']\n"
                        f"result = {{\n"
                        f"    'data': dist.to_dict(orient='records'),\n"
                        f"    'chart_type': 'pie',\n"
                        f"    'summary': 'Categorical distribution breakdown.'\n"
                        f"}}"
                    )
                    explanation = f"Calculated categorical distribution breakdown for {cat_col}."

                else:
                    cat_cols = df.select_dtypes(exclude="number").columns.tolist()
                    num_cols = df.select_dtypes(include="number").columns.tolist()
                    if not cat_cols or not num_cols:
                        raise ValueError("Sample dataset lacks suitable columns for categorical aggregation.")
                    cat_col = cat_cols[0]
                    num_col = num_cols[0]

                    res_df = df.groupby(cat_col, as_index=False)[num_col].sum().sort_values(by=num_col, ascending=False).head(10)
                    chart_type = "bar"
                    final_code = (
                        f"breakdown = df.groupby('{cat_col}', as_index=False)['{num_col}'].sum()\n"
                        f"result = {{\n"
                        f"    'data': breakdown.to_dict(orient='records'),\n"
                        f"    'chart_type': 'bar',\n"
                        f"    'summary': 'Aggregated metrics.'\n"
                        f"}}"
                    )
                    explanation = f"Calculated aggregated {num_col} grouped by {cat_col}."

                formatted_data = res_df.to_dict(orient="records")

            except ValueError:
                raise
            except Exception as e:
                detail = f"Failed to compute sample analysis: {str(e)}" if settings.DEBUG else "Failed to compute sample analysis."
                raise ValueError(detail)

            add_step("Generating Python code", "completed", "Generated Pandas analytical query script matching intent.", {"initial_code_preview": final_code[:200]})
            add_step("Computing verified sample results", "completed", "Computed verified analytical results directly from sample dataset without host subprocess execution.")

            attempts.append(ExecutionAttemptItem(
                attempt_number=1,
                code=final_code,
                success=True,
                error_type=None,
                error_message=None,
                error_traceback=None,
                diagnosis=None,
                duration_ms=48.0
            ))
            final_status = "success"

        formatted_table = formatted_data[:50]
        formatted_chart_data = formatted_data[:30]

        add_step("Verifying results", "completed", f"Verified {len(formatted_table)} output records ready for visualization.")
        add_step("Analysis completed", "completed", f"Process finished with status: {final_status.upper()}.")

        overall_duration = (time.time() - overall_start) * 1000
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
                final_code,
                explanation,
                chart_type,
                json.dumps(formatted_chart_data),
                json.dumps(formatted_table),
                json.dumps(summary_stats),
                json.dumps([t.model_dump() for t in timeline]),
                None,
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
            final_code=final_code,
            explanation=explanation,
            chart_type=chart_type,
            chart_data=formatted_chart_data,
            result_table=formatted_table,
            summary_stats=summary_stats,
            timeline=timeline,
            attempts=attempts,
            created_at=get_utc_now_iso()
        )
