"""Business-logic layer for Notes."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import note as note_crud
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from app.services._parent import ensure_idea_exists


def list_notes(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Note], int]:
    ensure_idea_exists(db, idea_id)
    return note_crud.list_for_idea(db, idea_id, limit=limit, offset=offset)


def create_note(db: Session, idea_id: UUID, payload: NoteCreate) -> Note:
    ensure_idea_exists(db, idea_id)
    return note_crud.create(db, idea_id, payload)


def get_note(db: Session, idea_id: UUID, note_id: UUID) -> Note:
    ensure_idea_exists(db, idea_id)
    row = note_crud.get(db, note_id)
    if row is None or row.idea_id != idea_id:
        raise NotFoundError(
            message=f"Note {note_id} not found for idea {idea_id}",
            details={"resource": "note", "id": str(note_id)},
        )
    return row


def update_note(
    db: Session, idea_id: UUID, note_id: UUID, payload: NoteUpdate
) -> Note:
    row = get_note(db, idea_id, note_id)
    return note_crud.update(db, row, payload)


def delete_note(db: Session, idea_id: UUID, note_id: UUID) -> None:
    row = get_note(db, idea_id, note_id)
    note_crud.delete(db, row)