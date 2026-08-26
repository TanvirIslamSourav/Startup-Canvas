"""HTTP routes for documents nested under an idea."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import (
    DocumentCreate,
    DocumentListResponse,
    DocumentRead,
    DocumentUpdate,
)
from app.services import document as document_service

router = APIRouter(prefix="/ideas/{idea_id}/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse, summary="List documents")
def list_documents(
    idea_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    items, total = document_service.list_documents(
        db, idea_id, limit=limit, offset=offset
    )
    return DocumentListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a document",
)
def create_document(
    idea_id: UUID,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
) -> DocumentRead:
    row = document_service.create_document(db, idea_id, payload)
    return DocumentRead.model_validate(row)


@router.get(
    "/{document_id}", response_model=DocumentRead, summary="Get a document"
)
def get_document(
    idea_id: UUID, document_id: UUID, db: Session = Depends(get_db)
) -> DocumentRead:
    row = document_service.get_document(db, idea_id, document_id)
    return DocumentRead.model_validate(row)


@router.patch(
    "/{document_id}", response_model=DocumentRead, summary="Update a document"
)
def update_document(
    idea_id: UUID,
    document_id: UUID,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
) -> DocumentRead:
    row = document_service.update_document(db, idea_id, document_id, payload)
    return DocumentRead.model_validate(row)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a document",
)
def delete_document(
    idea_id: UUID, document_id: UUID, db: Session = Depends(get_db)
) -> Response:
    document_service.delete_document(db, idea_id, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)