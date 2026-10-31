import sys
import json
import traceback
import math
import numpy as np
import pandas as pd
from typing import Any

# Custom JSON encoder to handle pandas/numpy types cleanly
class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, (np.ndarray, pd.Series)):
            return [self.default(x) for x in obj.tolist()]
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
            return str(obj)
        return str(obj)

def run_isolated(dataset_path: str, code_path: str):
    # Enforce memory safety limits where supported
    try:
        import resource
        max_mem_bytes = 512 * 1024 * 1024  # 512MB
        if hasattr(resource, "RLIMIT_DATA"):
            resource.setrlimit(resource.RLIMIT_DATA, (max_mem_bytes, max_mem_bytes))
    except Exception:
        pass

    # Load dataset
    try:
        df = pd.read_csv(dataset_path)
    except Exception as e:
        error_payload = {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": f"Failed to load dataset: {str(e)}",
            "error_traceback": traceback.format_exc()
        }
        print("__RESULT_START__" + json.dumps(error_payload) + "__RESULT_END__")
        sys.exit(0)

    # Disable filesystem I/O methods on pandas runtime to prevent arbitrary host file access
    for fn in [
        "read_csv", "read_table", "read_json", "read_html", "read_xml",
        "read_sql", "read_sql_query", "read_sql_table", "read_parquet",
        "read_feather", "read_hdf", "read_pickle", "read_clipboard", "read_excel"
    ]:
        if hasattr(pd, fn):
            setattr(pd, fn, None)

    for fn in ["to_csv", "to_pickle", "to_sql", "to_parquet", "to_excel", "to_hdf"]:
        if hasattr(pd.DataFrame, fn):
            setattr(pd.DataFrame, fn, None)

    # Read code
    try:
        with open(code_path, "r", encoding="utf-8") as f:
            code_str = f.read()
    except Exception as e:
        error_payload = {
            "success": False,
            "error_type": "IOError",
            "error_message": f"Failed to read code file: {str(e)}",
            "error_traceback": traceback.format_exc()
        }
        print("__RESULT_START__" + json.dumps(error_payload) + "__RESULT_END__")
        sys.exit(0)

    # Safe import handler for whitelisted modules only
    allowed_modules = {
        "pandas", "pd", "numpy", "np", "math", "datetime",
        "date", "time", "json", "re", "collections", "itertools", "scipy"
    }

    import importlib
    def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        base_name = name.split(".")[0]
        if base_name in allowed_modules:
            return importlib.__import__(name, globals, locals, fromlist, level)
        raise ImportError(f"Import of module '{name}' is restricted by execution policy.")

    # Safe built-in dictionary
    safe_builtins = {
        "abs": abs, "round": round, "min": min, "max": max, "sum": sum,
        "len": len, "range": range, "enumerate": enumerate, "zip": zip,
        "map": map, "filter": filter, "sorted": sorted, "list": list,
        "dict": dict, "set": set, "tuple": tuple, "str": str, "int": int,
        "float": float, "bool": bool, "print": print, "isinstance": isinstance,
        "issubclass": issubclass, "True": True, "False": False, "None": None,
        "__import__": safe_import
    }

    # Isolated execution namespace
    import time
    exec_globals = {
        "__builtins__": safe_builtins,
        "pd": pd,
        "pandas": pd,
        "np": np,
        "numpy": np,
        "time": time,
        "math": math,
        "df": df,
        "result": None
    }

    try:
        # Execute user code in isolated globals
        exec(code_str, exec_globals)
        raw_result = exec_globals.get("result")

        # Standardize result structure
        formatted_result = {
            "success": True,
            "data": None,
            "summary": None,
            "chart_type": None,
            "chart_data": None
        }

        if isinstance(raw_result, pd.DataFrame):
            formatted_result["data"] = raw_result.head(100).to_dict(orient="records")
            formatted_result["summary"] = f"Result computed with {len(raw_result)} rows and {len(raw_result.columns)} columns."
        elif isinstance(raw_result, pd.Series):
            formatted_result["data"] = raw_result.reset_index().to_dict(orient="records")
            formatted_result["summary"] = f"Result computed with {len(raw_result)} values."
        elif isinstance(raw_result, dict):
            formatted_result["data"] = raw_result.get("data") or raw_result
            formatted_result["summary"] = raw_result.get("summary") or "Analysis completed successfully."
            formatted_result["chart_type"] = raw_result.get("chart_type")
            formatted_result["chart_data"] = raw_result.get("chart_data")
        elif raw_result is not None:
            formatted_result["data"] = raw_result
            formatted_result["summary"] = f"Calculated value: {raw_result}"
        else:
            # If result wasn't set explicitly, check if df was modified or return a summary
            formatted_result["data"] = []
            formatted_result["summary"] = "Code executed without explicit 'result' assignment."

        encoded = json.dumps(formatted_result, cls=SafeJSONEncoder)
        print("__RESULT_START__" + encoded + "__RESULT_END__")

    except Exception as e:
        tb = traceback.format_exc()
        error_payload = {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "error_traceback": tb
        }
        print("__RESULT_START__" + json.dumps(error_payload) + "__RESULT_END__")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python sandbox_worker.py <dataset_path> <code_path>")
        sys.exit(1)
    run_isolated(sys.argv[1], sys.argv[2])
