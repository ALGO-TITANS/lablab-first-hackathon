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
