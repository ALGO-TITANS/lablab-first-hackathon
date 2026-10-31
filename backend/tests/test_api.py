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
