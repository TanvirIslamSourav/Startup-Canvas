"""Business-logic layer for the Lean Canvas."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.crud import lean_canvas as lc_crud
from app.models.lean_canvas import LeanCanvas
from app.schemas.lean_canvas import LeanCanvasUpdate
from app.services._parent import ensure_idea_exists


def get_canvas(db: Session, idea_id: UUID) -> LeanCanvas | None:
    ensure_idea_exists(db, idea_id)
    return lc_crud.get_by_idea(db, idea_id)


def upsert_canvas(db: Session, idea_id: UUID, payload: LeanCanvasUpdate) -> LeanCanvas:
    ensure_idea_exists(db, idea_id)
    data = payload.model_dump(exclude_unset=True)
    return lc_crud.upsert(db, idea_id, data)


def delete_canvas(db: Session, idea_id: UUID) -> None:
    ensure_idea_exists(db, idea_id)
    lc_crud.delete(db, idea_id)