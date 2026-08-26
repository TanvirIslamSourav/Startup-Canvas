"""HTTP routes for ``/ideas/{idea_id}/progress``."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.crud import idea as idea_crud
from app.db.session import get_db
from app.schemas.progress_tracker import (
    ProgressTrackerRead,
    ProgressTrackerUpsert,
)
from app.services import progress_tracker as pt_service

router = APIRouter(prefix="/ideas/{idea_id}/progress", tags=["progress"])


@router.get(
    "",
    response_model=ProgressTrackerRead | None,
    summary="Get the cached progress snapshot (or null)",
)
def get_progress(
    idea_id: UUID, db: Session = Depends(get_db)
) -> ProgressTrackerRead | None:
    row = pt_service.get(db, idea_id)
    return ProgressTrackerRead.model_validate(row) if row else None


@router.put("", response_model=ProgressTrackerRead, summary="Upsert progress")
def put_progress(
    idea_id: UUID,
    payload: ProgressTrackerUpsert,
    db: Session = Depends(get_db),
) -> ProgressTrackerRead:
    row = pt_service.upsert(db, idea_id, **payload.model_dump())
    return ProgressTrackerRead.model_validate(row)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete the progress snapshot",
)
def delete_progress(
    idea_id: UUID, db: Session = Depends(get_db)
) -> Response:
    from app.crud import progress_tracker as pt_crud

    idea_crud.get(db, idea_id)
    pt_crud.delete(db, idea_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)