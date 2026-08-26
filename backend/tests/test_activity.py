"""End-to-end tests for the append-only Activity log."""
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


def _roadmap_payload() -> dict[str, object]:
    return {"title": "Plan", "summary": "x"}


def test_list_activities_seeded_by_roadmap_upsert(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/activities")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    types = {it["event_type"] for it in body["items"]}
    assert "roadmap.upserted" in types


def test_list_activities_filter_by_type(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/activities",
        params={"eventType": "roadmap_stage.created"},
    )
    assert resp.status_code == 200
    for it in resp.json()["items"]:
        assert it["event_type"] == "roadmap_stage.created"


def test_list_activities_pagination(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    for _ in range(5):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/roadmap/stages",
            json={"title": "stage"},
        )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/activities",
        params={"limit": 2, "offset": 0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert len(body["items"]) == 2
    assert body["total"] >= 5


def test_get_activity_by_id(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    items = app_client.get(f"/api/v1/ideas/{idea_id}/activities").json()[
        "items"
    ]
    assert items
    first_id = items[0]["id"]
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/activities/{first_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == first_id


def test_get_activity_404_wrong_idea(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/activities/{uuid.uuid4()}"
    )
    assert resp.status_code == 404


def test_activities_have_no_create_endpoint(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    # The activity log is append-only; clients cannot POST events directly.
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/activities", json={"event_type": "x"}
    )
    # 405 Method Not Allowed (or 404 if not registered; either is OK
    # as long as it isn't 2xx)
    assert resp.status_code in (404, 405)


def test_activities_have_no_update_or_delete(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    items = app_client.get(f"/api/v1/ideas/{idea_id}/activities").json()[
        "items"
    ]
    assert items
    aid = items[0]["id"]
    patch_resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/activities/{aid}", json={"event_type": "y"}
    )
    del_resp = app_client.delete(
        f"/api/v1/ideas/{idea_id}/activities/{aid}"
    )
    assert patch_resp.status_code in (404, 405)
    assert del_resp.status_code in (404, 405)


def test_activities_parent_idea_404(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.get(f"/api/v1/ideas/{bogus}/activities")
    assert resp.status_code == 404