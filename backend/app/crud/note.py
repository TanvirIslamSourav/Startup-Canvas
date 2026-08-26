"""CRUD repository for ``Note`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def get(db: Session, note_id: UUID) -> Note | None:
    return db.get(Note, note_id)


def list_for_idea(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Note], int]:
    stmt = (
        select(Note)
        .where(Note.idea_id == idea_id)
        .order_by(Note.pinned.desc(), Note.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(Note).where(
        Note.idea_id == idea_id
    )
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def create(db: Session, idea_id: UUID, payload: NoteCreate) -> Note:
    row = Note(idea_id=idea_id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(db: Session, row: Note, payload: NoteUpdate) -> Note:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: Note) -> None:
    db.delete(row)
    db.commit()