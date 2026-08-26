"""Tests for the Business Model Canvas module."""
from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.models.startup_project import StartupProject
from app.models.user import User
from tests._factories import make_idea


@pytest.fixture()
def app_client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def idea_id(db_session: Session) -> uuid.UUID:
    user = User(email="bc-founder@example.com")
    db_session.add(user)
    db_session.flush()
    project = StartupProject(owner_id=user.id, name="BC Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return make_idea(db_session, project_id=project.id)


def test_get_business_canvas_missing_returns_null(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/business-canvas")
    assert resp.status_code == 200
    assert resp.json() is None


def test_put_business_canvas(app_client: TestClient, idea_id: uuid.UUID) -> None:
    put = app_client.put(
        f"/api/v1/ideas/{idea_id}/business-canvas",
        json={"key_partners": "Universities", "revenue_streams": "Subscription"},
    )
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["key_partners"] == "Universities"
    assert body["revenue_streams"] == "Subscription"


def test_put_business_canvas_updates(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(
        f"/api/v1/ideas/{idea_id}/business-canvas",
        json={"key_partners": "Original"},
    )
    put2 = app_client.put(
        f"/api/v1/ideas/{idea_id}/business-canvas", json={"key_partners": "Updated"}
    )
    assert put2.status_code == 200
    assert put2.json()["key_partners"] == "Updated"


def test_delete_business_canvas(app_client: TestClient, idea_id: uuid.UUID) -> None:
    app_client.put(
        f"/api/v1/ideas/{idea_id}/business-canvas", json={"key_partners": "x"}
    )
    resp = app_client.delete(f"/api/v1/ideas/{idea_id}/business-canvas")
    assert resp.status_code == 204
    assert (
        app_client.get(f"/api/v1/ideas/{idea_id}/business-canvas").json() is None
    )


def test_business_canvas_idea_not_found(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    assert (
        app_client.put(
            f"/api/v1/ideas/{bogus}/business-canvas", json={"key_partners": "x"}
        ).status_code
        == 404
    )


def test_business_canvas_extra_field_rejected(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/business-canvas",
        json={"key_partners": "x", "evil": "y"},
    )
    assert resp.status_code == 422