"""HTTP routes for ``/ideas/{idea_id}/swot``."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.swot import SwotRead, SwotUpdate
from app.services import swot as swot_service

router = APIRouter(prefix="/ideas/{idea_id}/swot", tags=["swot"])


@router.get(
    "",
    response_model=SwotRead | None,
    summary="Get the SWOT analysis for an idea",
)
def get_swot(idea_id: UUID, db: Session = Depends(get_db)) -> SwotRead | None:
    swot = swot_service.get_swot(db, idea_id)
    return SwotRead.model_validate(swot) if swot else None


@router.put("", response_model=SwotRead, summary="Upsert the SWOT analysis")
def put_swot(
    idea_id: UUID, payload: SwotUpdate, db: Session = Depends(get_db)
) -> SwotRead:
    swot = swot_service.upsert_swot(db, idea_id, payload)
    return SwotRead.model_validate(swot)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete the SWOT analysis",
)
def delete_swot(idea_id: UUID, db: Session = Depends(get_db)) -> Response:
    swot_service.delete_swot(db, idea_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)