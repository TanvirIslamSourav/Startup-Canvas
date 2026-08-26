"""CRUD repository for ``BusinessCanvas`` (1:1 with idea)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.business_canvas import BusinessCanvas


def get_by_idea(db: Session, idea_id: UUID) -> BusinessCanvas | None:
    return db.query(BusinessCanvas).filter_by(idea_id=idea_id).one_or_none()


def upsert(db: Session, idea_id: UUID, payload: dict) -> BusinessCanvas:
    row = get_by_idea(db, idea_id)
    if row is None:
        row = BusinessCanvas(idea_id=idea_id, **payload)
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