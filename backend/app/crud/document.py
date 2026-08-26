"""CRUD repository for ``Document`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


def get(db: Session, document_id: UUID) -> Document | None:
    return db.get(Document, document_id)


def list_for_idea(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Document], int]:
    stmt = (
        select(Document)
        .where(Document.idea_id == idea_id)
        .order_by(Document.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(Document).where(
        Document.idea_id == idea_id
    )
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def create(db: Session, idea_id: UUID, payload: DocumentCreate) -> Document:
    row = Document(idea_id=idea_id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(
    db: Session, row: Document, payload: DocumentUpdate
) -> Document:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: Document) -> None:
    db.delete(row)
    db.commit()