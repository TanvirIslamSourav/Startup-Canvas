"""Business-logic layer for SWOT."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.crud import swot as swot_crud
from app.models.swot import Swot
from app.schemas.swot import SwotUpdate
from app.services._parent import ensure_idea_exists


def get_swot(db: Session, idea_id: UUID) -> Swot | None:
    ensure_idea_exists(db, idea_id)
    return swot_crud.get_by_idea(db, idea_id)


def upsert_swot(db: Session, idea_id: UUID, payload: SwotUpdate) -> Swot:
    ensure_idea_exists(db, idea_id)
    data = payload.model_dump(exclude_unset=True)
    return swot_crud.upsert(db, idea_id, data)


def delete_swot(db: Session, idea_id: UUID) -> None:
    ensure_idea_exists(db, idea_id)
    swot_crud.delete(db, idea_id)