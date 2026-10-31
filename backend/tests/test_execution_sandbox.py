import pytest
import tempfile
from pathlib import Path
from app.services.execution_sandbox import ExecutionSandbox

@pytest.fixture
def sample_csv_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("region,sales,units\nNorth,1500,10\nSouth,2500,20\nEast,1800,15\nWest,3200,25\n")
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)

def test_sandbox_successful_execution(sample_csv_file):
    code = """
total_sales = df['sales'].sum()
result = {
    'data': [{'total_sales': float(total_sales)}],
    'summary': f'Total sales is {total_sales}'
}
"""
    res = ExecutionSandbox.execute(code, sample_csv_file)
    assert res["success"] is True
    assert res["data"][0]["total_sales"] == 9000.0

def test_sandbox_catches_runtime_error(sample_csv_file):
    code = """
# Non-existent column raises KeyError
bad_calc = df['non_existent_column'].sum()
result = {'data': bad_calc}
"""
    res = ExecutionSandbox.execute(code, sample_csv_file)
    assert res["success"] is False
    assert res["error_type"] == "KeyError"
    assert "non_existent_column" in res["error_message"]

def test_sandbox_blocks_malicious_code(sample_csv_file):
    code = """
import os
os.listdir('.')
"""
    res = ExecutionSandbox.execute(code, sample_csv_file)
    assert res["success"] is False
    assert res["error_type"] == "SecurityPolicyViolation"

def test_sandbox_enforces_timeout(sample_csv_file, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "SANDBOX_TIMEOUT_SECONDS", 1.0)
    code = """
import time
# Safe loop that simulates long calculation
start = time.time()
while time.time() - start < 5.0:
    pass
result = {'data': 'finished'}
"""
    res = ExecutionSandbox.execute(code, sample_csv_file)
    assert res["success"] is False
    assert res["error_type"] == "TimeoutError"

def test_sandbox_blocks_file_reading(sample_csv_file):
    code = "data = pd.read_csv('/etc/passwd')\nresult = {'data': data}"
    res = ExecutionSandbox.execute(code, sample_csv_file)
    assert res["success"] is False
    assert res["error_type"] == "SecurityPolicyViolation"
