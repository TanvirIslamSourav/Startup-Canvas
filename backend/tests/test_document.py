"""End-to-end tests for the Document nested resource."""
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
        "kind": "business_plan",
        "title": "2026 Business Plan",
        "file_path": "s3://docs/2026-plan.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 1_048_576,
        "notes": "Draft v3",
    }
    base.update(overrides)
    return base


def test_create_document(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/documents", json=_payload()
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["kind"] == "business_plan"
    assert body["title"] == "2026 Business Plan"
    assert body["size_bytes"] == 1_048_576


def test_list_documents_pagination(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    for i in range(3):
        app_client.post(
            f"/api/v1/ideas/{idea_id}/documents",
            json=_payload(title=f"D{i}"),
        )
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/documents",
        params={"limit": 1, "offset": 0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["limit"] == 1


def test_get_document(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/documents", json=_payload()
    ).json()
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/documents/{created['id']}"
    )
    assert resp.status_code == 200


def test_get_document_404(app_client: TestClient, idea_id: uuid.UUID) -> None:
    resp = app_client.get(
        f"/api/v1/ideas/{idea_id}/documents/{uuid.uuid4()}"
    )
    assert resp.status_code == 404


def test_patch_document(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/documents", json=_payload()
    ).json()
    resp = app_client.patch(
        f"/api/v1/ideas/{idea_id}/documents/{created['id']}",
        json={"title": "Renamed", "size_bytes": 2_000_000},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Renamed"
    assert body["size_bytes"] == 2_000_000


def test_delete_document(app_client: TestClient, idea_id: uuid.UUID) -> None:
    created = app_client.post(
        f"/api/v1/ideas/{idea_id}/documents", json=_payload()
    ).json()
    resp = app_client.delete(
        f"/api/v1/ideas/{idea_id}/documents/{created['id']}"
    )
    assert resp.status_code == 204


def test_parent_idea_404(app_client: TestClient) -> None:
    bogus = uuid.uuid4()
    resp = app_client.post(
        f"/api/v1/ideas/{bogus}/documents", json=_payload()
    )
    assert resp.status_code == 404


def test_extra_field_422(app_client: TestClient, idea_id: uuid.UUID) -> None:
    payload = _payload()
    payload["leak"] = True
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/documents", json=payload
    )
    assert resp.status_code == 422


def test_invalid_kind_422(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/documents",
        json=_payload(kind="mystery_kind"),
    )
    assert resp.status_code == 422


def test_size_negative_422(
    app_client: TestClient, idea_id: uuid.UUID
) -> None:
    resp = app_client.post(
        f"/api/v1/ideas/{idea_id}/documents",
        json=_payload(size_bytes=-1),
    )
    assert resp.status_code == 422
