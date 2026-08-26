"""CRUD repository for ``LeanCanvas`` (1:1 with idea)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.lean_canvas import LeanCanvas


def get_by_idea(db: Session, idea_id: UUID) -> LeanCanvas | None:
    return db.query(LeanCanvas).filter_by(idea_id=idea_id).one_or_none()


def upsert(db: Session, idea_id: UUID, payload: dict) -> LeanCanvas:
    row = get_by_idea(db, idea_id)
    if row is None:
        row = LeanCanvas(idea_id=idea_id, **payload)
        db.add(row)
    else:
        for field, value in payload.items():
            setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, idea_id: UUID) -> None:
    row = get_by_idea(db, idea_id)
    if row is not None:
        db.delete(row)
        db.commit()