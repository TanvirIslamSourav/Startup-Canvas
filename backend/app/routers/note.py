"""HTTP routes for notes nested under an idea."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.note import (
    NoteCreate,
    NoteListResponse,
    NoteRead,
    NoteUpdate,
)
from app.services import note as note_service

router = APIRouter(prefix="/ideas/{idea_id}/notes", tags=["notes"])


@router.get("", response_model=NoteListResponse, summary="List notes")
def list_notes(
    idea_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> NoteListResponse:
    items, total = note_service.list_notes(
        db, idea_id, limit=limit, offset=offset
    )
    return NoteListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
)
def create_note(
    idea_id: UUID, payload: NoteCreate, db: Session = Depends(get_db)
) -> NoteRead:
    row = note_service.create_note(db, idea_id, payload)
    return NoteRead.model_validate(row)


@router.get("/{note_id}", response_model=NoteRead, summary="Get a note")
def get_note(
    idea_id: UUID, note_id: UUID, db: Session = Depends(get_db)
) -> NoteRead:
    row = note_service.get_note(db, idea_id, note_id)
    return NoteRead.model_validate(row)


@router.patch("/{note_id}", response_model=NoteRead, summary="Update a note")
def update_note(
    idea_id: UUID,
    note_id: UUID,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
) -> NoteRead:
    row = note_service.update_note(db, idea_id, note_id, payload)
    return NoteRead.model_validate(row)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a note",
)
def delete_note(
    idea_id: UUID, note_id: UUID, db: Session = Depends(get_db)
) -> Response:
    note_service.delete_note(db, idea_id, note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)