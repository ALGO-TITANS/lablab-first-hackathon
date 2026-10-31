import pytest
from app.services.code_validator import CodeValidator

def test_safe_pandas_code():
    code = """
import pandas as pd
import numpy as np

grouped = df.groupby('region')['revenue'].sum().reset_index()
result = {
    'data': grouped.to_dict(orient='records'),
    'summary': 'Aggregated revenue by region',
    'chart_type': 'bar'
}
"""
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is True
    assert "passed" in reason.lower()

def test_block_os_system():
    code = """
import os
os.system('ls -la')
"""
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "prohibited" in reason.lower()

def test_block_subprocess():
    code = """
import subprocess
subprocess.run(['cat', '/etc/passwd'])
"""
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "subprocess" in reason

def test_block_eval_exec():
    code = """
payload = "__import__('os').system('id')"
eval(payload)
"""
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "eval" in reason

def test_block_dunder_traversal():
    code = """
classes = ().__class__.__bases__[0].__subclasses__()
"""
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "Security Violation" in reason

def test_syntax_error():
    code = "def invalid_syntax(: pass"
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "Syntax Error" in reason

def test_block_arbitrary_file_read():
    code = "data = pd.read_csv('/etc/passwd')"
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "Security Violation" in reason
    assert "read_csv" in reason

def test_block_arbitrary_file_write():
    code = "df.to_csv('/tmp/stolen_data.csv')"
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "Security Violation" in reason
    assert "to_csv" in reason

def test_block_builtin_open():
    code = "with open('/etc/shadow', 'r') as f: content = f.read()"
    is_safe, reason = CodeValidator.validate_python_code(code)
    assert is_safe is False
    assert "open" in reason
