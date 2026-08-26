"""HTTP routes for customer personas nested under an idea."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.customer_persona import (
    CustomerPersonaCreate,
    CustomerPersonaListResponse,
    CustomerPersonaRead,
    CustomerPersonaUpdate,
)
from app.services import customer_persona as persona_service

router = APIRouter(prefix="/ideas/{idea_id}/personas", tags=["personas"])


@router.get("", response_model=CustomerPersonaListResponse, summary="List personas")
def list_personas(
    idea_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> CustomerPersonaListResponse:
    items, total = persona_service.list_personas(
        db, idea_id, limit=limit, offset=offset
    )
    return CustomerPersonaListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "",
    response_model=CustomerPersonaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a persona",
)
def create_persona(
    idea_id: UUID,
    payload: CustomerPersonaCreate,
    db: Session = Depends(get_db),
) -> CustomerPersonaRead:
    row = persona_service.create_persona(db, idea_id, payload)
    return CustomerPersonaRead.model_validate(row)


@router.get(
    "/{persona_id}", response_model=CustomerPersonaRead, summary="Get a persona"
)
def get_persona(
    idea_id: UUID, persona_id: UUID, db: Session = Depends(get_db)
) -> CustomerPersonaRead:
    row = persona_service.get_persona(db, idea_id, persona_id)
    return CustomerPersonaRead.model_validate(row)


@router.patch(
    "/{persona_id}", response_model=CustomerPersonaRead, summary="Update a persona"
)
def update_persona(
    idea_id: UUID,
    persona_id: UUID,
    payload: CustomerPersonaUpdate,
    db: Session = Depends(get_db),
) -> CustomerPersonaRead:
    row = persona_service.update_persona(db, idea_id, persona_id, payload)
    return CustomerPersonaRead.model_validate(row)


@router.delete(
    "/{persona_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a persona",
)
def delete_persona(
    idea_id: UUID, persona_id: UUID, db: Session = Depends(get_db)
) -> Response:
    persona_service.delete_persona(db, idea_id, persona_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)