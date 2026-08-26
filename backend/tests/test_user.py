"""Tests for the User module."""
from __future__ import annotations


def test_create_user(client):
    resp = client.post(
        "/api/v1/users",
        json={"email": "alice@example.com", "display_name": "Alice"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert body["locale"] == "en"
    assert body["theme"] == "system"
    assert body["is_active"] is True
    assert "id" in body


def test_create_user_email_lowercased(client):
    resp = client.post(
        "/api/v1/users",
        json={"email": "BOB@Example.COM", "display_name": "Bob"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "bob@example.com"


def test_create_user_duplicate_email_returns_409(client):
    payload = {"email": "carol@example.com", "display_name": "Carol"}
    r1 = client.post("/api/v1/users", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/users", json=payload)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "conflict"


def test_create_user_invalid_email_returns_422(client):
    resp = client.post("/api/v1/users", json={"email": "not-an-email"})
    assert resp.status_code == 422


def test_list_users(client):
    for i in range(3):
        client.post("/api/v1/users", json={"email": f"u{i}@example.com"})
    resp = client.get("/api/v1/users")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_get_user_404(client):
    resp = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


def test_update_user(client):
    r = client.post("/api/v1/users", json={"email": "dan@example.com"})
    uid = r.json()["id"]
    r2 = client.patch(
        f"/api/v1/users/{uid}",
        json={"display_name": "Dan", "theme": "dark", "locale": "bn"},
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["display_name"] == "Dan"
    assert body["theme"] == "dark"
    assert body["locale"] == "bn"


def test_update_user_extra_field_forbidden(client):
    r = client.post("/api/v1/users", json={"email": "eve@example.com"})
    uid = r.json()["id"]
    r2 = client.patch(f"/api/v1/users/{uid}", json={"is_admin": True})
    assert r2.status_code == 422
