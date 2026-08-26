"""HTTP routes for competitors nested under an idea."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorListResponse,
    CompetitorRead,
    CompetitorUpdate,
)
from app.services import competitor as competitor_service

router = APIRouter(prefix="/ideas/{idea_id}/competitors", tags=["competitors"])


@router.get(
    "", response_model=CompetitorListResponse, summary="List competitors"
)
def list_competitors(
    idea_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> CompetitorListResponse:
    items, total = competitor_service.list_competitors(
        db, idea_id, limit=limit, offset=offset
    )
    return CompetitorListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "",
    response_model=CompetitorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a competitor",
)
def create_competitor(
    idea_id: UUID,
    payload: CompetitorCreate,
    db: Session = Depends(get_db),
) -> CompetitorRead:
    row = competitor_service.create_competitor(db, idea_id, payload)
    return CompetitorRead.model_validate(row)


@router.get(
    "/{competitor_id}", response_model=CompetitorRead, summary="Get a competitor"
)
def get_competitor(
    idea_id: UUID, competitor_id: UUID, db: Session = Depends(get_db)
) -> CompetitorRead:
    row = competitor_service.get_competitor(db, idea_id, competitor_id)
    return CompetitorRead.model_validate(row)


@router.patch(
    "/{competitor_id}", response_model=CompetitorRead, summary="Update a competitor"
)
def update_competitor(
    idea_id: UUID,
    competitor_id: UUID,
    payload: CompetitorUpdate,
    db: Session = Depends(get_db),
) -> CompetitorRead:
    row = competitor_service.update_competitor(db, idea_id, competitor_id, payload)
    return CompetitorRead.model_validate(row)


@router.delete(
    "/{competitor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a competitor",
)
def delete_competitor(
    idea_id: UUID, competitor_id: UUID, db: Session = Depends(get_db)
) -> Response:
    competitor_service.delete_competitor(db, idea_id, competitor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)