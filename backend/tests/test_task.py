"""End-to-end tests for the Task nested resource."""
from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from tests._factories import make_idea, make_project, make_user


@pytest.fixture()
def app_client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def idea_id(db_session: Session) -> uuid.UUID:
    user = make_user(db_session)
    project = make_project(db_session, owner=user)
    return make_idea(db_session, project_id=project.id)


def _payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "title": "Ship landing page",
        "description": "Need hero copy + 3 features",
        "priority": "high",
        "status": "todo",
        "progress": 0,
    }
    base.update(overrides)
    return base


def test_create_task(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks", json=_payload()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["title"] == "Ship landing page"
    assert body["priority"] == "high"
    assert body["status"] == "todo"


def test_list_tasks_pagination(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    for i in range(5):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/tasks", json=_payload(title=f"T{i}")
        )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/tasks", params={"limit": 2, "offset": 1}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 1
    assert len(data["items"]) == 2


def test_list_tasks_filter_by_status(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks",
        json=_payload(title="Open", status="todo"),
    )
    app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks",
        json=_payload(title="Closed", status="done"),
    )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/tasks", params={"status": "done"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Closed"


def test_get_task(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks", json=_payload()
    ).json()
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/tasks/{created['id']}")
    assert resp.status_code == 200


def test_get_task_404(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/tasks/{uuid.uuid4()}"
    )
    assert resp.status_code == 404


def test_patch_task(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks", json=_payload()
    ).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/tasks/{created['id']}",
        json={"status": "in_progress", "progress": 50},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "in_progress"
    assert body["progress"] == 50


def test_delete_task(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks", json=_payload()
    ).json()
    resp = app_client.delete(
        f"/api/v1/ideas/{idea_id}/tasks/{created['id']}"
    )
    assert resp.status_code == 204


def test_parent_idea_404(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.post(
        f"/api/v1/ideas/{bogus}/tasks", json=_payload()
    )
    assert resp.status_code == 404


def test_extra_field_422(app_client: TestClient, idea_id: uuid.UUID) -> None:
    payload = _payload()
    payload["oops"] = 1
    resp = app_client.post(f"/api/v1/ideas/{idea_id}/tasks", json=payload)
    assert resp.status_code == 422


def test_invalid_priority_422(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks",
        json=_payload(priority="super-urgent"),
    )
    assert resp.status_code == 422


def test_progress_out_of_range(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/tasks", json=_payload(progress=150)
    )
    assert resp.status_code == 422
