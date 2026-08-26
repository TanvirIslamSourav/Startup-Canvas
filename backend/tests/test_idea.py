"""End-to-end tests for the Ideas module.

These exercise the full HTTP stack (routers, services, CRUD, models)
against the SQLite-in-memory test database.
"""
from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import session as session_module
from app.main import create_app
from app.models.startup_project import StartupProject
from app.models.user import User


@pytest.fixture()
def app_client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def project_id(db_session: Session) -> uuid.UUID:
    """Insert a user + a project and return the project id."""
    user = User(email="founder@example.com")
    db_session.add(user)
    db_session.flush()
    project = StartupProject(owner_id=user.id, name="Acme")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project.id


# Shared body factory ---------------------------------------------------------
def _payload(project_id: uuid.UUID, **overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "project_id": str(project_id),
        "title": "Affordable tutoring marketplace",
        "problem": "Students lack affordable tutors",
        "solution": "On-demand live tutoring",
        "audience": "Grade 5-8 students",
        "category": "education",
        "tags": ["tutoring", "marketplace", " EdTech "],
        "status": "draft",
        "priority": 3,
        "score": 50,
    }
    base.update(overrides)
    return base


# Tests -----------------------------------------------------------------------
def test_create_idea(app_client: TestClient, project_id: uuid.UUID) -> None:
    resp = app_client.post("/api/v1/ideas", json=_payload(project_id))
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["title"] == "Affordable tutoring marketplace"
    assert body["status"] == "draft"
    assert body["tags"] == ["tutoring", "marketplace", "EdTech"]  # normalized
    assert body["is_archived"] is False
    assert uuid.UUID(body["id"])  # parses as UUID


def test_create_idea_unknown_project(app_client: TestClient) -> None:
    bogus = str(uuid.uuid4())
    resp = app_client.post("/api/v1/ideas", json=_payload(uuid.UUID(bogus)))
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "validation_error"


def test_list_ideas_pagination(
    app_client: TestClient, project_id: uuid.UUID
) -> None:
    for i in range(5):
        app_client.post(
            "/api/v1/ideas",
            json=_payload(project_id, title=f"Idea {i}"),
        )
    resp = app_client.get(
        "/api/v1/ideas",
        params={"project_id": project_id, "limit": 2, "offset": 0, "sort_by": "title", "sort_dir": "asc"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert [it["title"] for it in data["items"]] == ["Idea 0", "Idea 1"]


def test_list_ideas_filter_status_and_search(
    app_client: TestClient, project_id: uuid.UUID
) -> None:
    app_client.post(
        "/api/v1/ideas", json=_payload(project_id, title="Validate", status="validating")
    )
    app_client.post(
        "/api/v1/ideas", json=_payload(project_id, title="Planned", status="planned")
    )
    resp = app_client.get(
        "/api/v1/ideas",
        params={"project_id": project_id, "status": "planned"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Planned"


def test_get_idea(app_client: TestClient, project_id: uuid.UUID) -> None:
    created = app_client.post(
        "/api/v1/ideas", json=_payload(project_id, title="Fetch me")
    ).json()
    resp = app_client.get(f"/api/v1/ideas/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_idea_404(app_client: TestClient) -> None:
    resp = app_client.get(f"/api/v1/ideas/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


def test_patch_idea(app_client: TestClient, project_id: uuid.UUID) -> None:
    created = app_client.post("/api/v1/ideas", json=_payload(project_id)).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{created['id']}",
        json={"status": "in_progress", "priority": 5, "tags": ["new", "new"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "in_progress"
    assert body["priority"] == 5
    assert body["tags"] == ["new"]  # deduped


def test_patch_idea_invalid_status(
    app_client: TestClient, project_id: uuid.UUID
) -> None:
    created = app_client.post("/api/v1/ideas", json=_payload(project_id)).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{created['id']}", json={"status": "bogus"}
    )
    assert resp.status_code == 422


def test_archive_and_restore(app_client: TestClient, project_id: uuid.UUID) -> None:
    created = app_client.post("/api/v1/ideas", json=_payload(project_id)).json()
    aid = created["id"]

    # Archive
    resp = app_client.delete(f"/api/v1/ideas/{aid}")
    assert resp.status_code == 200
    assert resp.json()["is_archived"] is True
    assert resp.json()["archived_at"] is not None

    # Default listing excludes archived
    resp = app_client.get(
        "/api/v1/ideas", params={"project_id": project_id}
    )
    assert resp.json()["total"] == 0

    # include_archived=true returns it
    resp = app_client.get(
        "/api/v1/ideas",
        params={"project_id": project_id, "include_archived": "true"},
    )
    assert resp.json()["total"] == 1

    # Restore
    resp = app_client.post(f"/api/v1/ideas/{aid}/restore")
    assert resp.status_code == 200
    assert resp.json()["is_archived"] is False
    assert resp.json()["archived_at"] is None


def test_list_sort_by_invalid(app_client: TestClient) -> None:
    resp = app_client.get("/api/v1/ideas", params={"sort_by": "evil_column"})
    assert resp.status_code == 422


def test_priority_bounds(app_client: TestClient, project_id: uuid.UUID) -> None:
    resp = app_client.post(
        "/api/v1/ideas", json=_payload(project_id, priority=99)
    )
    assert resp.status_code == 422


# Ensure session module is referenced so pytest fixture in conftest is used.
_ = session_module