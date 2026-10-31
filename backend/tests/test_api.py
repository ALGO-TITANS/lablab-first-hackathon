import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db

# Initialize database schema for tests
init_db()
client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "default_provider" in data

def test_load_sample_dataset_endpoint():
    response = client.post("/api/datasets/load-sample/sales")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["row_count"] > 0
    assert len(data["columns"]) > 0

    # Test preview
    preview_res = client.get(f"/api/datasets/{data['id']}/preview")
    assert preview_res.status_code == 200
    assert len(preview_res.json()["rows"]) > 0

    # Test dashboard stats
    stats_res = client.get("/api/stats/dashboard")
    assert stats_res.status_code == 200
    assert stats_res.json()["total_datasets"] >= 1

def test_settings_endpoint():
    get_res = client.get("/api/settings")
    assert get_res.status_code == 200
    data = get_res.json()
    assert "sandbox_timeout_seconds" in data

    # Update setting
    post_res = client.post("/api/settings", json={"sandbox_timeout_seconds": 9.5})
    assert post_res.status_code == 200
    assert post_res.json()["sandbox_timeout_seconds"] == 9.5

def test_cors_allowed_origin():
    # Test that an allowed origin receives its origin back, not a wildcard '*'
    response = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-origin") != "*"

def test_cors_disallowed_origin():
    # Test that an unconfigured origin is NOT reflected in the access-control header
    response = client.get("/api/health", headers={"Origin": "https://malicious-unauthorized-site.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers

def test_cors_preflight_options():
    # Test CORS preflight request from allowed origin
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/api/datasets/upload", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-origin") != "*"

def test_settings_development_retains_localhost(monkeypatch):
    from app.config import Settings
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "development")
    dev_settings = Settings()
    assert "http://localhost:3000" in dev_settings.CORS_ORIGINS
    assert "http://127.0.0.1:3000" in dev_settings.CORS_ORIGINS

def test_settings_production_does_not_include_localhost(monkeypatch):
    from app.config import Settings
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("CORS_ORIGINS", "https://my-app.vercel.app")
    prod_settings = Settings()
    assert prod_settings.CORS_ORIGINS == ["https://my-app.vercel.app"]
    assert "http://localhost:3000" not in prod_settings.CORS_ORIGINS
    assert "http://127.0.0.1:3000" not in prod_settings.CORS_ORIGINS

def test_settings_production_empty_default_without_origins(monkeypatch):
    from app.config import Settings
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    prod_settings = Settings()
    assert prod_settings.CORS_ORIGINS == []

def test_settings_wildcard_rejection_and_normalization(monkeypatch):
    from app.config import Settings
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("CORS_ORIGINS", "https://my-app.vercel.app/, *, https://preview-123.vercel.app/")
    custom_settings = Settings()
    assert "*" not in custom_settings.CORS_ORIGINS
    assert "https://my-app.vercel.app" in custom_settings.CORS_ORIGINS
    assert "https://preview-123.vercel.app" in custom_settings.CORS_ORIGINS
    assert "https://my-app.vercel.app/" not in custom_settings.CORS_ORIGINS

def test_settings_env_var_comma_separated_and_json(monkeypatch):
    from app.config import Settings
    # Comma-separated env var in production
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("CORS_ORIGINS", "https://app1.vercel.app, https://app2.vercel.app")
    s1 = Settings()
    assert s1.CORS_ORIGINS == ["https://app1.vercel.app", "https://app2.vercel.app"]

    # JSON-encoded env var in production
    monkeypatch.setenv("CORS_ORIGINS", '["https://json-app.vercel.app"]')
    s2 = Settings()
    assert s2.CORS_ORIGINS == ["https://json-app.vercel.app"]

def test_settings_production_debug_default(monkeypatch):
    from app.config import Settings
    monkeypatch.delenv("DEBUG", raising=False)
    prod_settings = Settings(ENVIRONMENT="production")
    assert prod_settings.DEBUG is False

def test_settings_configurable_storage(tmp_path):
    from app.config import Settings
    custom_data_dir = tmp_path / "custom_data"
    custom_settings = Settings(DATA_DIR=custom_data_dir)
    assert custom_settings.DATA_DIR == custom_data_dir
    assert custom_settings.UPLOADS_DIR == custom_data_dir / "uploads"
    assert custom_settings.DB_PATH == custom_data_dir / "metadata.db"

    custom_settings.ensure_directories()
    assert custom_settings.DATA_DIR.exists()
    assert custom_settings.UPLOADS_DIR.exists()
    assert custom_settings.DB_PATH.parent.exists()

def test_settings_execution_defaults_in_production_and_dev(monkeypatch):
    from app.config import Settings
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("ENABLE_ARBITRARY_EXECUTION", raising=False)
    monkeypatch.delenv("DEMO_MODE", raising=False)

    dev_settings = Settings(ENVIRONMENT="development")
    assert dev_settings.ENABLE_ARBITRARY_EXECUTION is True
    assert dev_settings.DEMO_MODE is False
    assert dev_settings.DEBUG is True
    prod_settings = Settings(ENVIRONMENT="production")
    assert prod_settings.ENABLE_ARBITRARY_EXECUTION is False
    assert prod_settings.DEMO_MODE is True
    assert prod_settings.DEBUG is False

def test_public_demo_blocks_arbitrary_execution_on_custom_upload():
    from app.config import settings
    # 1. Upload custom CSV file
    csv_content = b"user_id,action,score\n1,click,10\n2,view,5\n3,buy,20"
    upload_res = client.post(
        "/api/datasets/upload",
        files={"file": ("custom_user_dataset.csv", csv_content, "text/csv")}
    )
    assert upload_res.status_code == 200
    dataset_id = upload_res.json()["id"]

    # 2. Simulate public demo mode (arbitrary execution disabled)
    original_setting = settings.ENABLE_ARBITRARY_EXECUTION
    try:
        settings.ENABLE_ARBITRARY_EXECUTION = False
        query_res = client.post(
            "/api/analysis/query",
            json={"dataset_id": dataset_id, "query": "What is the highest score?"}
        )
        assert query_res.status_code == 400
        assert "Arbitrary Python code execution is disabled" in query_res.json()["detail"]
    finally:
        settings.ENABLE_ARBITRARY_EXECUTION = original_setting
def test_public_demo_allows_sample_dataset_query():
    from app.config import settings
    # 1. Load pre-loaded sample dataset
    sample_res = client.post("/api/datasets/load-sample/sales")
    assert sample_res.status_code == 200
    dataset_id = sample_res.json()["id"]

    # 2. In public demo mode, query on sample dataset should succeed safely
    original_setting = settings.ENABLE_ARBITRARY_EXECUTION
    try:
        settings.ENABLE_ARBITRARY_EXECUTION = False
        query_res = client.post(
            "/api/analysis/query",
            json={"dataset_id": dataset_id, "query": "Top 5 products by revenue"}
        )
        assert query_res.status_code == 200
        data = query_res.json()
        assert data["status"] == "success"
        assert data["repair_attempts_count"] == 0
        assert len(data["chart_data"]) > 0
        assert len(data["result_table"]) > 0
    finally:
        settings.ENABLE_ARBITRARY_EXECUTION = original_setting
def test_public_demo_simulated_self_healing():
    from app.config import settings
    sample_res = client.post("/api/datasets/load-sample/sales")
    assert sample_res.status_code == 200
    dataset_id = sample_res.json()["id"]

    original_setting = settings.ENABLE_ARBITRARY_EXECUTION
    try:
        settings.ENABLE_ARBITRARY_EXECUTION = False
        query_res = client.post(
            "/api/analysis/query",
            json={
                "dataset_id": dataset_id,
                "query": "Show revenue by region",
                "demo_force_error": True
            }
        )
        assert query_res.status_code == 200
        data = query_res.json()
        assert data["status"] == "repaired"
        assert data["repair_attempts_count"] == 1
        assert len(data["attempts"]) == 2
        assert data["attempts"][0]["success"] is False
        assert data["attempts"][0]["error_type"] == "KeyError"
        assert data["attempts"][1]["success"] is True
        assert len(data["chart_data"]) > 0
    finally:
        settings.ENABLE_ARBITRARY_EXECUTION = original_setting
def test_execution_sandbox_hard_kill_switch():
    from app.config import settings
    from app.services.execution_sandbox import ExecutionSandbox
    original_setting = settings.ENABLE_ARBITRARY_EXECUTION
    try:
        settings.ENABLE_ARBITRARY_EXECUTION = False
        res = ExecutionSandbox.execute("import math; print(math.pi)", "nonexistent.csv")
        assert res["success"] is False
        assert res["error_type"] == "ArbitraryExecutionDisabled"
    finally:
        settings.ENABLE_ARBITRARY_EXECUTION = original_setting

def test_custom_upload_spoofed_filename_is_not_sample():
    from app.config import settings
    from app.db.database import get_db_connection
    # Attacker names upload with trusted sample filename
    spoofed_csv = b"col1,col2\na,1\nb,2"
    res = client.post(
        "/api/datasets/upload",
        files={"file": ("global_sales_transactions.csv", spoofed_csv, "text/csv")}
    )
    assert res.status_code == 200
    dataset_id = res.json()["id"]

    # Verify is_sample is strictly 0 in database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_sample, original_filename FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        assert row["is_sample"] == 0
        assert row["original_filename"] == "global_sales_transactions.csv"

    # Verify that in demo mode, spoofed filename does NOT bypass arbitrary execution block
    original_setting = settings.ENABLE_ARBITRARY_EXECUTION
    try:
        settings.ENABLE_ARBITRARY_EXECUTION = False
        query_res = client.post(
            "/api/analysis/query",
            json={"dataset_id": dataset_id, "query": "Top revenue"}
        )
        assert query_res.status_code == 400
        assert "Arbitrary Python code execution is disabled" in query_res.json()["detail"]
    finally:
        settings.ENABLE_ARBITRARY_EXECUTION = original_setting

def test_request_data_cannot_set_is_sample():
    from app.db.database import get_db_connection
    # Try injecting is_sample in form data
    res = client.post(
        "/api/datasets/upload",
        data={"is_sample": "1"},
        files={"file": ("test.csv", b"a,b\n1,2", "text/csv")}
    )
    assert res.status_code == 200
    dataset_id = res.json()["id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_sample FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        assert row["is_sample"] == 0

def test_sample_path_traversal_rejected():
    res = client.post("/api/datasets/load-sample/..%2F..%2Fetc%2Fpasswd")
    assert res.status_code in [400, 404]
    res_direct = client.post("/api/datasets/load-sample/../../etc/passwd")
    assert res_direct.status_code in [400, 404]
    res2 = client.post("/api/datasets/load-sample/unknown_dataset")
    assert res2.status_code == 400

def test_missing_columns_no_fabricated_fallback(tmp_path):
    from app.config import settings
    from app.db.database import get_db_connection, get_utc_now_iso
    # Create sample-flagged dataset pointing to CSV with missing expected columns
    dummy_csv = settings.UPLOADS_DIR / "dummy_sample_missing_cols.csv"
    dummy_csv.write_text("unrelated_col1,unrelated_col2\n10,20\n30,40")
    dummy_id = "test-missing-cols-sample"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO datasets (
            id, name, original_filename, file_path, file_size_bytes,
            row_count, column_count, columns_json, summary_json, is_sample, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dummy_id, "Missing Cols Sample", "dummy.csv", str(dummy_csv),
            len(dummy_csv.read_bytes()), 2, 2, "[]", "{}", 1, get_utc_now_iso()
        ))
        conn.commit()

    original_setting = settings.ENABLE_ARBITRARY_EXECUTION
    try:
        settings.ENABLE_ARBITRARY_EXECUTION = False
        query_res = client.post(
            "/api/analysis/query",
            json={"dataset_id": dummy_id, "query": "Show revenue by region", "demo_force_error": True}
        )
        # Must return controlled error, NEVER fabricated fallback data
        assert query_res.status_code == 400
        assert "schema validation failed" in query_res.json()["detail"].lower()
    finally:
        settings.ENABLE_ARBITRARY_EXECUTION = original_setting
        if dummy_csv.exists():
            dummy_csv.unlink()

def test_simulated_self_healing_explicitly_identified_as_simulation():
    from app.config import settings
    sample_res = client.post("/api/datasets/load-sample/sales")
    dataset_id = sample_res.json()["id"]

    original_setting = settings.ENABLE_ARBITRARY_EXECUTION
    try:
        settings.ENABLE_ARBITRARY_EXECUTION = False
        res = client.post(
            "/api/analysis/query",
            json={"dataset_id": dataset_id, "query": "Revenue by region", "demo_force_error": True}
        )
        assert res.status_code == 200
        data = res.json()
        step_names = [s["step"] for s in data["timeline"]]
        assert "Simulating execution" in step_names
        assert "Demonstrating error diagnosis" in step_names
        assert "Applying predefined repair" in step_names

        # Verify simulation notification in message
        sim_step = next(s for s in data["timeline"] if s["step"] == "Simulating execution")
        assert "Demonstration: Subprocess execution is disabled" in sim_step["message"]
    finally:
        settings.ENABLE_ARBITRARY_EXECUTION = original_setting

def test_production_environment_overrides_explicit_security_env_vars(monkeypatch):
    from app.config import Settings
    # Even if environment variables explicitly attempt to enable execution and debug,
    # production mode must unconditionally force safe values
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ENABLE_ARBITRARY_EXECUTION", "true")
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("DEBUG", "true")

    settings_obj = Settings()
    assert settings_obj.ENABLE_ARBITRARY_EXECUTION is False
    assert settings_obj.DEMO_MODE is True
    assert settings_obj.DEBUG is False

def test_development_execution_behavior_remains_unchanged(monkeypatch):
    from app.config import Settings
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("ENABLE_ARBITRARY_EXECUTION", raising=False)
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "development")

    dev_settings = Settings()
    assert dev_settings.ENABLE_ARBITRARY_EXECUTION is True
    assert dev_settings.DEMO_MODE is False
    assert dev_settings.DEBUG is True
