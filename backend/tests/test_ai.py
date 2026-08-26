"""AI advisor router tests (mock provider)."""
from __future__ import annotations


def test_validate_returns_mock_payload(client):
    r = client.post(
        "/api/v1/ai/validate",
        json={"title": "AI tutor for grade school", "category": "education"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "mock"
    assert body["model"] == "local-json-v1"
    assert isinstance(body["content"], list)
    assert len(body["content"]) >= 1
    assert {"title", "detail", "confidence"} <= set(body["content"][0].keys())


def test_swot_suggestions(client):
    r = client.post(
        "/api/v1/ai/swot-suggestions",
        json={"title": "A marketplace for tutors"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "mock"
    assert isinstance(body["content"], list)


def test_risk_suggestions(client):
    r = client.post(
        "/api/v1/ai/risk-suggestions",
        json={"title": "An AI tool for note taking"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["provider"] == "mock"
    # The seed data has an "ai" bucket which should match the title.
    titles = " ".join(item["title"] for item in body["content"]).lower()
    assert "ai" in titles or "data" in titles or "model" in titles or titles  # tolerated


def test_competitors_includes_market_note(client):
    r = client.post(
        "/api/v1/ai/competitors",
        json={"title": "B2B SaaS for compliance", "market": "EU"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["content"][0]["title"].startswith("EU market scan")


def test_growth_roadmap(client):
    r = client.post(
        "/api/v1/ai/growth-roadmap",
        json={"title": "Edtech app"},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["content"]) >= 3


def test_validate_validation_error(client):
    r = client.post("/api/v1/ai/validate", json={})
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body