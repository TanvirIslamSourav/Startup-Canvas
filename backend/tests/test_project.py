"""Tests for the Startup Project module."""
from __future__ import annotations

from tests._factories import make_project, make_user


def _setup_user(client):
    r = client.post(
        "/api/v1/users",
        json={"email": "owner@example.com", "display_name": "Owner"},
    )
    return r.json()


def test_create_project(client):
    user = _setup_user(client)
    resp = client.post(
        "/api/v1/projects",
        json={
            "owner_id": user["id"],
            "name": "My Startup",
            "description": "First test",
            "tags": ["saas", " b2b ", "saas"],
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "My Startup"
    assert body["stage"] == "idea"
    assert body["status"] == "active"
    assert body["tags"] == ["saas", "b2b"]
    assert body["metadata_json"] == {}


def test_list_projects(client):
    user = _setup_user(client)
    for i in range(3):
        client.post("/api/v1/projects", json={"owner_id": user["id"], "name": f"P{i}"})
    resp = client.get("/api/v1/projects", params={"owner_id": user["id"]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_list_projects_search(client):
    user = _setup_user(client)
    client.post(
        "/api/v1/projects",
        json={"owner_id": user["id"], "name": "Alpha project"},
    )
    client.post(
        "/api/v1/projects",
        json={"owner_id": user["id"], "name": "Beta project"},
    )
    resp = client.get("/api/v1/projects", params={"search": "Beta"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Beta project"


def test_get_project_404(client):
    resp = client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_update_project(client):
    user = _setup_user(client)
    r = client.post(
        "/api/v1/projects", json={"owner_id": user["id"], "name": "Old name"}
    )
    pid = r.json()["id"]
    r2 = client.patch(
        f"/api/v1/projects/{pid}",
        json={"name": "New name", "stage": "mvp", "status": "paused"},
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["name"] == "New name"
    assert body["stage"] == "mvp"
    assert body["status"] == "paused"


def test_update_project_invalid_status(client):
    user = _setup_user(client)
    r = client.post(
        "/api/v1/projects", json={"owner_id": user["id"], "name": "P"}
    )
    pid = r.json()["id"]
    r2 = client.patch(f"/api/v1/projects/{pid}", json={"status": "bogus"})
    assert r2.status_code == 422


def test_delete_empty_project(client, db_session):
    user = make_user(db_session)
    project = make_project(db_session, owner=user)
    resp = client.delete(f"/api/v1/projects/{project.id}")
    assert resp.status_code == 204
    # And 404 on subsequent fetch
    resp = client.get(f"/api/v1/projects/{project.id}")
    assert resp.status_code == 404


def test_delete_project_with_ideas_rejected(client, db_session):

    from app.crud import idea as idea_crud
    from app.schemas.idea import IdeaCreate
    from tests._factories import make_project, make_user

    user = make_user(db_session)
    project = make_project(db_session, owner=user)
    idea_crud.create(
        db_session,
        IdeaCreate(project_id=project.id, title="Anchor idea"),
    )
    db_session.commit()
    resp = client.delete(f"/api/v1/projects/{project.id}")
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "validation_error"
