"""End-to-end tests for the Customer Persona nested resource."""
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
        "name": "Concerned Parent",
        "age": 35,
        "occupation": "Engineer",
        "goals": "Find affordable tutoring",
        "pain_points": "Limited weekend slots",
        "needs": "Live tutors, progress tracking",
        "behaviour": "Mobile-first, busy mornings",
        "avatar_url": None,
    }
    base.update(overrides)
    return base


def test_create_persona(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/personas", json=_payload()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "Concerned Parent"
    assert body["age"] == 35
    assert uuid.UUID(body["id"])


def test_list_personas_pagination(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    for i in range(3):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/personas",
            json=_payload(name=f"Persona {i}"),
        )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/personas", params={"limit": 1, "offset": 0}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["limit"] == 1
    assert len(data["items"]) == 1


def test_get_persona(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/personas", json=_payload()
    ).json()
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/personas/{created['id']}"
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_persona_404(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/personas/{uuid.uuid4()}"
    )
    assert resp.status_code == 404


def test_patch_persona(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/personas", json=_payload()
    ).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/personas/{created['id']}",
        json={"name": "Updated Name", "age": 40},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Updated Name"
    assert body["age"] == 40


def test_delete_persona(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/personas", json=_payload()
    ).json()
    resp = app_client.delete(
        f"/api/v1/ideas/{idea_id}/personas/{created['id']}"
    )
    assert resp.status_code == 204


def test_parent_idea_404(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.post(
        f"/api/v1/ideas/{bogus}/personas", json=_payload()
    )
    assert resp.status_code == 404


def test_extra_field_422(app_client: TestClient, idea_id: uuid.UUID) -> None:
    payload = _payload()
    payload["evil"] = True
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/personas", json=payload
    )
    assert resp.status_code == 422


def test_age_out_of_range(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/personas", json=_payload(age=200)
    )
    assert resp.status_code == 422
