from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "details" in data
    assert "ranker_loaded" in data["details"]
    assert "items_in_feature_store" in data["details"]
