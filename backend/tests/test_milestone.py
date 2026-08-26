"""End-to-end tests for the Milestone nested resource."""
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
        "title": "MVP launch",
        "description": "First public release",
        "target_date": "2026-12-31",
        "completion": 25,
    }
    base.update(overrides)
    return base


def test_create_milestone(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/milestones", json=_payload()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["title"] == "MVP launch"
    assert body["completion"] == 25


def test_list_milestones_pagination(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    for i in range(4):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/milestones",
            json=_payload(title=f"M{i}"),
        )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/milestones",
        params={"limit": 2, "offset": 0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 4
    assert data["limit"] == 2


def test_get_milestone(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/milestones", json=_payload()
    ).json()
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/milestones/{created['id']}"
    )
    assert resp.status_code == 200


def test_get_milestone_404(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/milestones/{uuid.uuid4()}"
    )
    assert resp.status_code == 404


def test_patch_milestone(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/milestones", json=_payload()
    ).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/milestones/{created['id']}",
        json={"completion": 75, "completed_at": "2026-09-01T10:00:00Z"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["completion"] == 75


def test_delete_milestone(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/milestones", json=_payload()
    ).json()
    resp = app_client.delete(
        f"/api/v1/ideas/{idea_id}/milestones/{created['id']}"
    )
    assert resp.status_code == 204


def test_parent_idea_404(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.post(
        f"/api/v1/ideas/{bogus}/milestones", json=_payload()
    )
    assert resp.status_code == 404


def test_extra_field_422(app_client: TestClient, idea_id: uuid.UUID) -> None:
    payload = _payload()
    payload["junk"] = "x"
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/milestones", json=payload
    )
    assert resp.status_code == 422


def test_completion_out_of_range(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/milestones", json=_payload(completion=150)
    )
    assert resp.status_code == 422
