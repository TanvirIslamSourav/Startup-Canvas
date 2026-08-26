"""Health endpoint tests."""
from __future__ import annotations


def test_health_ok(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root_metadata(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Startup Canvas API"
    assert body["api"] == "/api/v1"


def test_openapi_generated(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert "paths" in spec
    assert "/api/v1/health" in spec["paths"]
    assert "/api/v1/ai/validate" in spec["paths"]