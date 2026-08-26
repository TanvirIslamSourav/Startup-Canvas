"""Tests for the Progress Tracker module."""
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
    user = User(email="pt-founder@example.com")
    db_session.add(user)
    db_session.flush()
    project = StartupProject(owner_id=user.id, name="PT Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return make_idea(db_session, project_id=project.id)


def test_get_progress_missing_returns_null(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/progress")
    assert resp.status_code == 200
    assert resp.json() is None


def test_put_progress(app_client: TestClient, idea_id: uuid.UUID) -> None:
    put = app_client.put(
        f"/api/v1/ideas/{idea_id}/progress",
        json={
            "overall_completion": 40,
            "health_score": 60,
            "milestone_progress": 30,
            "task_completion": 50,
        },
    )
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["overall_completion"] == 40
    assert body["health_score"] == 60
    assert body["last_computed_at"] is not None


def test_progress_bounds(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/progress",
        json={
            "overall_completion": 200,
            "health_score": 50,
            "milestone_progress": 50,
            "task_completion": 50,
        },
    )
    assert resp.status_code == 422


def test_delete_progress(app_client: TestClient, idea_id: uuid.UUID) -> None:
    app_client.put(
        f"/api/v1/ideas/{idea_id}/progress",
        json={
            "overall_completion": 10,
            "health_score": 10,
            "milestone_progress": 10,
            "task_completion": 10,
        },
    )
    resp = app_client.delete(f"/api/v1/ideas/{idea_id}/progress")
    assert resp.status_code == 204
    assert app_client.get(f"/api/v1/ideas/{idea_id}/progress").json() is None


def test_progress_idea_not_found(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    assert (
        app_client.put(
            f"/api/v1/ideas/{bogus}/progress",
            json={
                "overall_completion": 0,
                "health_score": 0,
                "milestone_progress": 0,
                "task_completion": 0,
            },
        ).status_code
        == 404
    )


def test_progress_extra_field_rejected(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/progress",
        json={
            "overall_completion": 0,
            "health_score": 0,
            "milestone_progress": 0,
            "task_completion": 0,
            "evil": "x",
        },
    )
    assert resp.status_code == 422