"""CRUD repository for ``Swot`` (1:1 with idea)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.swot import Swot


def get_by_idea(db: Session, idea_id: UUID) -> Swot | None:
    return db.query(Swot).filter_by(idea_id=idea_id).one_or_none()


def upsert(db: Session, idea_id: UUID, payload: dict) -> Swot:
    row = get_by_idea(db, idea_id)
    if row is None:
        row = Swot(idea_id=idea_id, **payload)
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