from fastapi.testclient import TestClient
from server import app


def test_health_endpoint_ok():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "uptime_seconds" in data


def test_ready_endpoint_ok():
    client = TestClient(app)
    r = client.get("/ready")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in {"healthy", "degraded", "unhealthy"}
    assert isinstance(data.get("checks"), dict)

