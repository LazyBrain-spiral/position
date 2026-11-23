"""Integration tests for API service endpoints."""

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"


def test_healthz_endpoint():
    response = client.get("/api/v1/health/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


def test_resource_endpoints():
    resp = client.get("/api/v1/resources")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert len(resp.json()["data"]["items"]) >= 2

    create_payload = {"name": "Test Resource", "description": "Verification test resource"}
    create_resp = client.post("/api/v1/resources", json=create_payload)
    assert create_resp.status_code == 201
    assert create_resp.json()["data"]["name"] == "Test Resource"
