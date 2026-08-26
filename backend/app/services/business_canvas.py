"""Business-logic layer for the Business Model Canvas."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.crud import business_canvas as bc_crud
from app.models.business_canvas import BusinessCanvas
from app.schemas.business_canvas import BusinessCanvasUpdate
from app.services._parent import ensure_idea_exists


def get_canvas(db: Session, idea_id: UUID) -> BusinessCanvas | None:
    ensure_idea_exists(db, idea_id)
    return bc_crud.get_by_idea(db, idea_id)


def upsert_canvas(db: Session, idea_id: UUID, payload: BusinessCanvasUpdate) -> BusinessCanvas:
    ensure_idea_exists(db, idea_id)
    data = payload.model_dump(exclude_unset=True)
    return bc_crud.upsert(db, idea_id, data)


def delete_canvas(db: Session, idea_id: UUID) -> None:
    ensure_idea_exists(db, idea_id)
    bc_crud.delete(db, idea_id)