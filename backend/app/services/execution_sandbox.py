import os
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple
from app.config import settings
from app.services.code_validator import CodeValidator

class ExecutionSandbox:
    @staticmethod
    def execute(code: str, dataset_path: str) -> Dict[str, Any]:
        """
        Executes code inside an isolated, non-root worker process.
        - Enforces AST security validation
        - Clears all environment variables (API keys, host secrets never exposed)
        - Imposes strict timeout (e.g. 8s) to prevent infinite loops
        - Restricts output payload size
        """
        start_time = time.time()

        # Step 0: Production Demo Mode Guard
        if not settings.ENABLE_ARBITRARY_EXECUTION:
            duration = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error_type": "ArbitraryExecutionDisabled",
                "error_message": (
                    "Arbitrary Python code execution is disabled on this public instance for security. "
                    "Run locally with ENABLE_ARBITRARY_EXECUTION=true for unrestricted execution."
                ),
                "error_traceback": "PolicyEnforcement: Host code execution is restricted in public demo mode.",
                "duration_ms": duration,
                "data": None,
                "summary": None,
                "chart_type": None,
                "chart_data": None
            }

        # Step 1: AST Security Validation
        is_safe, reason = CodeValidator.validate_python_code(code)
        if not is_safe:
            duration = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error_type": "SecurityPolicyViolation",
                "error_message": reason,
                "error_traceback": f"Code validation failed: {reason}",
                "duration_ms": duration,
                "data": None,
                "summary": None,
                "chart_type": None,
                "chart_data": None
            }

        # Step 2: Prepare temporary isolated directory and script
        worker_path = Path(__file__).parent / "sandbox_worker.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_code_file = Path(temp_dir) / "user_script.py"
            temp_code_file.write_text(code, encoding="utf-8")

            # Minimal safe environment: strip all host secrets
            safe_env = {
                "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
                "LANG": "en_US.UTF-8",
                "PYTHONIOENCODING": "utf-8",
                "PYTHONPATH": str(Path(__file__).parent.parent.parent)
            }

            cmd = [
                sys.executable,
                str(worker_path),
                str(dataset_path),
                str(temp_code_file)
            ]

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=safe_env,
                    cwd=temp_dir,
                    text=True
                )

                try:
                    stdout, stderr = proc.communicate(timeout=settings.SANDBOX_TIMEOUT_SECONDS)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    duration = (time.time() - start_time) * 1000
                    return {
                        "success": False,
                        "error_type": "TimeoutError",
                        "error_message": f"Execution exceeded safety limit of {settings.SANDBOX_TIMEOUT_SECONDS}s.",
                        "error_traceback": f"TimeoutError: Execution cancelled after {settings.SANDBOX_TIMEOUT_SECONDS} seconds.",
                        "duration_ms": duration,
                        "data": None,
                        "summary": None,
                        "chart_type": None,
                        "chart_data": None
                    }

                duration = (time.time() - start_time) * 1000

                # Cap output characters
                if len(stdout) > settings.SANDBOX_MAX_OUTPUT_CHARS:
                    stdout = stdout[:settings.SANDBOX_MAX_OUTPUT_CHARS]

                # Parse result marker
                if "__RESULT_START__" in stdout and "__RESULT_END__" in stdout:
                    raw_json = stdout.split("__RESULT_START__")[1].split("__RESULT_END__")[0]
                    try:
                        res = json.loads(raw_json)
                        res["duration_ms"] = duration
                        return res
                    except json.JSONDecodeError as je:
                        return {
                            "success": False,
                            "error_type": "OutputParsingError",
                            "error_message": f"Failed to parse worker output: {str(je)}",
                            "error_traceback": stdout,
                            "duration_ms": duration,
                            "data": None,
                            "summary": None,
                            "chart_type": None,
                            "chart_data": None
                        }
                else:
                    return {
                        "success": False,
                        "error_type": "WorkerExecutionError",
                        "error_message": stderr or stdout or "Worker terminated without standard output marker.",
                        "error_traceback": stderr or stdout,
                        "duration_ms": duration,
                        "data": None,
                        "summary": None,
                        "chart_type": None,
                        "chart_data": None
                    }

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                return {
                    "success": False,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "error_traceback": str(e),
                    "duration_ms": duration,
                    "data": None,
                    "summary": None,
                    "chart_type": None,
                    "chart_data": None
                }
