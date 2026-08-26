"""Business-logic layer for Competitors."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import competitor as competitor_crud
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate
from app.services._parent import ensure_idea_exists


def list_competitors(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Competitor], int]:
    ensure_idea_exists(db, idea_id)
    return competitor_crud.list_for_idea(db, idea_id, limit=limit, offset=offset)


def create_competitor(
    db: Session, idea_id: UUID, payload: CompetitorCreate
) -> Competitor:
    ensure_idea_exists(db, idea_id)
    return competitor_crud.create(db, idea_id, payload)


def _get_or_404(db: Session, competitor_id: UUID) -> Competitor:
    row = competitor_crud.get(db, competitor_id)
    if row is None:
        raise NotFoundError(
            message=f"Competitor {competitor_id} not found",
            details={"resource": "competitor", "id": str(competitor_id)},
        )
    return row


def get_competitor(db: Session, idea_id: UUID, competitor_id: UUID) -> Competitor:
    ensure_idea_exists(db, idea_id)
    row = _get_or_404(db, competitor_id)
    if row.idea_id != idea_id:
        raise NotFoundError(
            message=f"Competitor {competitor_id} not found for idea {idea_id}",
            details={"resource": "competitor", "id": str(competitor_id)},
        )
    return row


def update_competitor(
    db: Session, idea_id: UUID, competitor_id: UUID, payload: CompetitorUpdate
) -> Competitor:
    row = get_competitor(db, idea_id, competitor_id)
    return competitor_crud.update(db, row, payload)


def delete_competitor(db: Session, idea_id: UUID, competitor_id: UUID) -> None:
    row = get_competitor(db, idea_id, competitor_id)
    competitor_crud.delete(db, row)