"""Tests for the Lean Canvas module."""
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
    user = User(email="lc-founder@example.com")
    db_session.add(user)
    db_session.flush()
    project = StartupProject(owner_id=user.id, name="LC Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return make_idea(db_session, project_id=project.id)


def test_get_lean_canvas_missing_returns_null(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/lean-canvas")
    assert resp.status_code == 200
    assert resp.json() is None


def test_put_lean_canvas_creates_then_updates(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    put = app_client.put(
        f"/api/v1/ideas/{idea_id}/lean-canvas",
        json={"problem": "Students can't find tutors", "solution": "Marketplace"},
    )
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["problem"] == "Students can't find tutors"
    assert body["solution"] == "Marketplace"

    # Upsert: second PUT updates existing record (no duplicate)
    put2 = app_client.put(
        f"/api/v1/ideas/{idea_id}/lean-canvas",
        json={"key_metrics": "MAU"},
    )
    assert put2.status_code == 200
    assert put2.json()["key_metrics"] == "MAU"
    assert put2.json()["problem"] == "Students can't find tutors"


def test_get_lean_canvas_after_put(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(
        f"/api/v1/ideas/{idea_id}/lean-canvas",
        json={"unique_value_prop": "AI-matched tutor in 5 minutes"},
    )
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/lean-canvas")
    assert resp.status_code == 200
    assert resp.json()["unique_value_prop"] == "AI-matched tutor in 5 minutes"


def test_delete_lean_canvas(app_client: TestClient, idea_id: uuid.UUID) -> None:
    app_client.put(
        f"/api/v1/ideas/{idea_id}/lean-canvas",
        json={"problem": "p"},
    )
    resp = app_client.delete(f"/api/v1/ideas/{idea_id}/lean-canvas")
    assert resp.status_code == 204
    assert app_client.get(f"/api/v1/ideas/{idea_id}/lean-canvas").json() is None


def test_lean_canvas_idea_not_found(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    assert (
        app_client.put(
            f"/api/v1/ideas/{bogus}/lean-canvas", json={"problem": "x"}
        ).status_code
        == 404
    )
    assert (
        app_client.get(f"/api/v1/ideas/{bogus}/lean-canvas").status_code == 404
    )


def test_lean_canvas_extra_field_rejected(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/lean-canvas",
        json={"problem": "p", "evil_field": "nope"},
    )
    assert resp.status_code == 422