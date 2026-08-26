"""End-to-end tests for the Note nested resource."""
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
        "body": "Remember to follow up with the pilot school",
        "pinned": False,
    }
    base.update(overrides)
    return base


def test_create_note(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/notes", json=_payload()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["body"].startswith("Remember")
    assert body["pinned"] is False


def test_list_notes_pagination(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    for i in range(3):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/notes", json=_payload(body=f"Note {i}")
        )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/notes",
        params={"limit": 1, "offset": 0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["limit"] == 1


def test_get_note(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/notes", json=_payload()
    ).json()
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/notes/{created['id']}")
    assert resp.status_code == 200


def test_get_note_404(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/notes/{uuid.uuid4()}"
    )
    assert resp.status_code == 404


def test_patch_note(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/notes", json=_payload()
    ).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/notes/{created['id']}",
        json={"pinned": True, "body": "Updated body"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["pinned"] is True
    assert body["body"] == "Updated body"


def test_delete_note(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/notes", json=_payload()
    ).json()
    resp = app_client.delete(
        f"/api/v1/ideas/{idea_id}/notes/{created['id']}"
    )
    assert resp.status_code == 204


def test_parent_idea_404(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.post(
        f"/api/v1/ideas/{bogus}/notes", json=_payload()
    )
    assert resp.status_code == 404


def test_extra_field_422(app_client: TestClient, idea_id: uuid.UUID) -> None:
    payload = _payload()
    payload["stray"] = "no"
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/notes", json=payload
    )
    assert resp.status_code == 422


def test_empty_body_422(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/notes", json=_payload(body="")
    )
    assert resp.status_code == 422
