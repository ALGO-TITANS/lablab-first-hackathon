import ast
from typing import Tuple, Set

FORBIDDEN_MODULES: Set[str] = {
    "os", "sys", "subprocess", "shutil", "socket", "pty", "commands",
    "posix", "nt", "importlib", "pickle", "ctypes", "threading",
    "multiprocessing", "urllib", "requests", "http", "ftplib", "smtplib",
    "telnetlib", "webbrowser", "signal", "tempfile", "glob", "inspect",
    "builtins", "asyncio", "concurrent", "gc", "resource", "platform",
    "site", "pkgutil", "distutils", "codecs"
}

FORBIDDEN_CALLS: Set[str] = {
    "eval", "exec", "compile", "open", "input", "__import__",
    "globals", "locals", "vars", "breakpoint", "getattr", "setattr", "delattr",
    # Block arbitrary filesystem read/write via pandas/numpy
    "read_csv", "read_table", "read_json", "read_html", "read_xml", "read_sql",
    "read_sql_query", "read_sql_table", "read_parquet", "read_feather", "read_hdf",
    "read_pickle", "read_clipboard", "read_excel", "to_pickle", "to_sql",
    "to_csv", "to_excel", "to_parquet", "to_feather", "to_hdf"
}

FORBIDDEN_ATTRS: Set[str] = {
    "__subclasses__", "__bases__", "__globals__", "__code__",
    "__class__", "__mro__", "__dict__", "func_globals", "gi_frame"
}

ALLOWED_TOP_LEVEL_MODULES: Set[str] = {
    "pandas", "pd", "numpy", "np", "math", "datetime", "date",
    "time", "json", "re", "collections", "itertools", "scipy"
}

class SecurityASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors: list[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in FORBIDDEN_MODULES or base_mod not in ALLOWED_TOP_LEVEL_MODULES:
                self.errors.append(f"Security Violation: Import of module '{alias.name}' is strictly prohibited.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_mod = node.module.split(".")[0]
            if base_mod in FORBIDDEN_MODULES or base_mod not in ALLOWED_TOP_LEVEL_MODULES:
                self.errors.append(f"Security Violation: Import from module '{node.module}' is strictly prohibited.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.errors.append(f"Security Violation: Execution of built-in function '{node.func.id}()' is prohibited.")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_CALLS or node.func.attr in FORBIDDEN_ATTRS:
                self.errors.append(f"Security Violation: Access to attribute '{node.func.attr}' is prohibited.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr in FORBIDDEN_ATTRS:
            self.errors.append(f"Security Violation: Access to forbidden dunder attribute '{node.attr}' is prohibited.")
        self.generic_visit(node)


class CodeValidator:
    @staticmethod
    def validate_python_code(code: str) -> Tuple[bool, str]:
        if not code or not code.strip():
            return False, "Code string is empty."

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax Error at line {e.lineno}: {e.msg}"

        visitor = SecurityASTVisitor()
        visitor.visit(tree)

        if visitor.errors:
            return False, " | ".join(visitor.errors)

        return True, "Code passed AST security validation."
