"""End-to-end tests for the Competitors nested resource."""
from __future__ import annotations

import uuid
from collections.abc import Iterator
from decimal import Decimal

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
        "name": "Acme Corp",
        "website_url": "https://acme.example",
        "pricing": 99.0,
        "pricing_currency": "USD",
        "strengths": "Strong brand",
        "weaknesses": "Expensive",
        "features": [{"name": "speed", "score": 8}],
        "market_position": "challenger",
        "notes": "Watch closely",
    }
    base.update(overrides)
    return base


def test_create_competitor(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/competitors", json=_payload()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "Acme Corp"
    assert Decimal(body["pricing"]) == Decimal("99")
    assert body["idea_id"] == str(idea_id)
    assert uuid.UUID(body["id"])


def test_list_competitors_pagination(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    for i in range(4):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/competitors",
            json=_payload(name=f"Competitor {i}"),
        )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/competitors", params={"limit": 2, "offset": 0}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 4
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) == 2


def test_get_competitor(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/competitors", json=_payload()
    ).json()
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/competitors/{created['id']}"
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_competitor_404(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/competitors/{uuid.uuid4()}"
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


def test_patch_competitor(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/competitors", json=_payload()
    ).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/competitors/{created['id']}",
        json={"name": "Acme Renamed", "pricing": 149.5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Acme Renamed"
    assert Decimal(body["pricing"]) == Decimal("149.5")


def test_delete_competitor(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/competitors", json=_payload()
    ).json()
    resp = app_client.delete(
        f"/api/v1/ideas/{idea_id}/competitors/{created['id']}"
    )
    assert resp.status_code == 204
    # Confirm gone
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/competitors/{created['id']}"
    )
    assert resp.status_code == 404


def test_parent_idea_404_create(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.post(
        f"/api/v1/ideas/{bogus}/competitors", json=_payload()
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


def test_extra_field_422(app_client: TestClient, idea_id: uuid.UUID) -> None:
    payload = _payload()
    payload["extra"] = "not-allowed"
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/competitors", json=payload
    )
    assert resp.status_code == 422


def test_pricing_negative_422(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/competitors", json=_payload(pricing=-1)
    )
    assert resp.status_code == 422
