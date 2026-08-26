"""HTTP routes for ``/ideas/{idea_id}/business-canvas``."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.business_canvas import BusinessCanvasRead, BusinessCanvasUpdate
from app.services import business_canvas as bc_service

router = APIRouter(
    prefix="/ideas/{idea_id}/business-canvas", tags=["business-canvas"]
)


@router.get(
    "",
    response_model=BusinessCanvasRead | None,
    summary="Get the business canvas for an idea",
)
def get_business_canvas(
    idea_id: UUID, db: Session = Depends(get_db)
) -> BusinessCanvasRead | None:
    canvas = bc_service.get_canvas(db, idea_id)
    return BusinessCanvasRead.model_validate(canvas) if canvas else None


@router.put(
    "", response_model=BusinessCanvasRead, summary="Upsert the business canvas"
)
def put_business_canvas(
    idea_id: UUID, payload: BusinessCanvasUpdate, db: Session = Depends(get_db)
) -> BusinessCanvasRead:
    canvas = bc_service.upsert_canvas(db, idea_id, payload)
    return BusinessCanvasRead.model_validate(canvas)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete the business canvas",
)
def delete_business_canvas(
    idea_id: UUID, db: Session = Depends(get_db)
) -> Response:
    bc_service.delete_canvas(db, idea_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)