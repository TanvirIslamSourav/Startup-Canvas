"""End-to-end tests for the Roadmap (1:1) + nested RoadmapStage (1:N)."""
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


def _roadmap_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "title": "12-Week MVP Plan",
        "summary": "Discover -> design -> build -> measure",
        "target_completion": "2025-12-31",
    }
    base.update(overrides)
    return base


def test_get_roadmap_when_absent(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/roadmap")
    assert resp.status_code == 200
    assert resp.json() is None


def test_put_creates_roadmap(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload()
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["title"] == "12-Week MVP Plan"
    assert body["completion"] == 0


def test_put_replaces_existing(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    resp = app_client.put(
        f"/api/v1/ideas/{idea_id}/roadmap",
        json=_roadmap_payload(title="New title"),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"


def test_patch_roadmap(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/roadmap",
        json={"summary": "Updated summary"},
    )
    assert resp.status_code == 200
    assert resp.json()["summary"] == "Updated summary"


def test_patch_roadmap_missing_404(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/roadmap", json={"title": "x"}
    )
    assert resp.status_code == 404


def test_delete_roadmap(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())
    resp = app_client.delete(f"/api/v1/ideas/{idea_id}/roadmap")
    assert resp.status_code == 204
    assert app_client.get(f"/api/v1/ideas/{idea_id}/roadmap").json() is None


def test_roadmap_extra_field_422(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    bad = _roadmap_payload()
    bad["oops"] = 1
    resp = app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=bad)
    assert resp.status_code == 422


def test_roadmap_parent_idea_404(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.put(
        f"/api/v1/ideas/{bogus}/roadmap", json=_roadmap_payload()
    )
    assert resp.status_code == 404


# ----- stages -------------------------------------------------------------

def _stage_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "title": "Discovery",
        "description": "Customer interviews",
        "completion": 0,
    }
    base.update(overrides)
    return base


def _create_roadmap(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    app_client.put(f"/api/v1/ideas/{idea_id}/roadmap", json=_roadmap_payload())


def test_create_stage(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages", json=_stage_payload()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["position"] == 1
    assert body["title"] == "Discovery"


def test_stages_auto_position(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    for i in range(3):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/roadmap/stages",
            json=_stage_payload(title=f"S{i}"),
        )
    resp = app_client.get(f"/api/v1/ideas/{idea_id}/roadmap/stages")
    items = resp.json()["items"]
    assert [s["position"] for s in items] == [1, 2, 3]


def test_stages_explicit_position_shifts_others(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(title="A"),
    )
    app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(title="C"),
    )
    inserted = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(title="B", position=2),
    ).json()
    assert inserted["position"] == 2
    items = app_client.get(f"/api/v1/ideas/{idea_id}/roadmap/stages").json()[
        "items"
    ]
    by_title = {s["title"]: s["position"] for s in items}
    assert by_title == {"A": 1, "B": 2, "C": 3}


def test_get_stage(app_client: TestClient, idea_id: uuid.UUID) -> None:
    _create_roadmap(app_client, idea_id)
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages", json=_stage_payload()
    ).json()
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/roadmap/stages/{created['id']}"
    )
    assert resp.status_code == 200


def test_get_stage_404_wrong_idea(
    app_client: TestClient, idea_id: uuid.UUID, db_session: Session
) -> None:
    _create_roadmap(app_client, idea_id)
    other_user = make_user(db_session, email="other@startup.local")
    other_project = make_project(db_session, owner=other_user)
    other_idea_id = make_idea(
        db_session, project_id=other_project.id, title="Other"
    )
    # other_idea has no roadmap — create_stage should 404
    resp = app_client.post(
        f"/api/v1/ideas/{other_idea_id}/roadmap/stages",
        json=_stage_payload(),
    )
    assert resp.status_code == 404


def test_patch_stage_updates_completion(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages", json=_stage_payload()
    ).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/roadmap/stages/{created['id']}",
        json={"completion": 60},
    )
    assert resp.status_code == 200
    assert resp.json()["completion"] == 60


def test_roadmap_completion_recomputed_on_stage_change(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    s1 = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(title="S1"),
    ).json()
    s2 = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(title="S2"),
    ).json()
    app_client.patch(
        f"/api/v1/ideas/{idea_id}/roadmap/stages/{s1['id']}",
        json={"completion": 50},
    )
    app_client.patch(
        f"/api/v1/ideas/{idea_id}/roadmap/stages/{s2['id']}",
        json={"completion": 100},
    )
    roadmap = app_client.get(f"/api/v1/ideas/{idea_id}/roadmap").json()
    assert roadmap["completion"] == 75


def test_delete_stage_recomputes(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(title="S1", completion=40),
    )
    s2 = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(title="S2", completion=60),
    ).json()
    app_client.delete(f"/api/v1/ideas/{idea_id}/roadmap/stages/{s2['id']}")
    roadmap = app_client.get(f"/api/v1/ideas/{idea_id}/roadmap").json()
    assert roadmap["completion"] == 40


def test_stage_extra_field_422(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    bad = _stage_payload()
    bad["oops"] = 1
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages", json=bad
    )
    assert resp.status_code == 422


def test_stage_out_of_range_completion_422(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(completion=150),
    )
    assert resp.status_code == 422


def test_stage_position_must_be_positive(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    _create_roadmap(app_client, idea_id)
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages",
        json=_stage_payload(position=0),
    )
    assert resp.status_code == 422


def test_stage_requires_roadmap_first(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/roadmap/stages", json=_stage_payload()
    )
    assert resp.status_code == 404