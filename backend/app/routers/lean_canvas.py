"""HTTP routes for ``/ideas/{idea_id}/lean-canvas``."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.lean_canvas import LeanCanvasRead, LeanCanvasUpdate
from app.services import lean_canvas as lc_service

router = APIRouter(prefix="/ideas/{idea_id}/lean-canvas", tags=["lean-canvas"])


@router.get(
    "",
    response_model=LeanCanvasRead | None,
    summary="Get the lean canvas for an idea (or null if absent)",
)
def get_lean_canvas(idea_id: UUID, db: Session = Depends(get_db)) -> LeanCanvasRead | None:
    canvas = lc_service.get_canvas(db, idea_id)
    return LeanCanvasRead.model_validate(canvas) if canvas else None


@router.put(
    "",
    response_model=LeanCanvasRead,
    summary="Upsert the lean canvas for an idea",
)
def put_lean_canvas(
    idea_id: UUID, payload: LeanCanvasUpdate, db: Session = Depends(get_db)
) -> LeanCanvasRead:
    canvas = lc_service.upsert_canvas(db, idea_id, payload)
    return LeanCanvasRead.model_validate(canvas)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete the lean canvas for an idea",
)
def delete_lean_canvas(idea_id: UUID, db: Session = Depends(get_db)) -> Response:
    lc_service.delete_canvas(db, idea_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)