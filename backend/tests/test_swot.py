"""Tests for the SWOT module."""
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
    user = User(email="swot-founder@example.com")
    db_session.add(user)
    db_session.flush()
    project = StartupProject(owner_id=user.id, name="SWOT Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return make_idea(db_session, project_id=project.id)


def test_get_swot_missing_returns_null(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/swot")
    assert resp.status_code == 200
    assert resp.json() is None


def test_put_swot(app_client: TestClient, idea_id: uuid.UUID) -> None:
    put = app_client.put(
        f"/api/v1/ideas/{idea_id}/swot",
        json={
            "strengths": "Strong team",
            "weaknesses": "Limited runway",
            "opportunities": "Rising demand",
            "threats": "Big competitors",
            "score": 75,
        },
    )
    assert put.status_code == 200, put.text
    body = put.json()
    assert body["strengths"] == "Strong team"
    assert body["score"] == 75


def test_swot_score_bounds(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/swot", json={"score": 150}
    )
    assert resp.status_code == 422
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/swot", json={"score": -1}
    )
    assert resp.status_code == 422


def test_delete_swot(app_client: TestClient, idea_id: uuid.UUID) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/swot", json={"strengths": "x"})
    resp = app_client.delete(f"/api/v1/ideas/{idea_id}/swot")
    assert resp.status_code == 204
    assert app_client.get(f"/api/v1/ideas/{idea_id}/swot").json() is None


def test_swot_idea_not_found(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    assert (
        app_client.put(
            f"/api/v1/ideas/{bogus}/swot", json={"strengths": "x"}
        ).status_code
        == 404
    )


def test_swot_extra_field_rejected(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/swot",
        json={"strengths": "x", "evil": "y"},
    )
    assert resp.status_code == 422