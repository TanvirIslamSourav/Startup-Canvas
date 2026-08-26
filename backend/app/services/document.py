"""Business-logic layer for Documents."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import document as document_crud
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services._parent import ensure_idea_exists


def list_documents(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Document], int]:
    ensure_idea_exists(db, idea_id)
    return document_crud.list_for_idea(db, idea_id, limit=limit, offset=offset)


def create_document(
    db: Session, idea_id: UUID, payload: DocumentCreate
) -> Document:
    ensure_idea_exists(db, idea_id)
    return document_crud.create(db, idea_id, payload)


def get_document(db: Session, idea_id: UUID, document_id: UUID) -> Document:
    ensure_idea_exists(db, idea_id)
    row = document_crud.get(db, document_id)
    if row is None or row.idea_id != idea_id:
        raise NotFoundError(
            message=f"Document {document_id} not found for idea {idea_id}",
            details={"resource": "document", "id": str(document_id)},
        )
    return row


def update_document(
    db: Session, idea_id: UUID, document_id: UUID, payload: DocumentUpdate
) -> Document:
    row = get_document(db, idea_id, document_id)
    return document_crud.update(db, row, payload)


def delete_document(db: Session, idea_id: UUID, document_id: UUID) -> None:
    row = get_document(db, idea_id, document_id)
    document_crud.delete(db, row)