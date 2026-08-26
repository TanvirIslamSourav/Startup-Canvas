"""HTTP routes for the append-only activity log."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.activity import (
    ActivityListResponse,
    ActivityRead,
)
from app.services import activity as activity_service

router = APIRouter(prefix="/ideas/{idea_id}/activities", tags=["activities"])


@router.get(
    "", response_model=ActivityListResponse, summary="List activity events"
)
def list_activities(
    idea_id: UUID,
    event_type: str | None = Query(default=None, alias="eventType"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ActivityListResponse:
    items, total = activity_service.list_for_idea(
        db,
        idea_id,
        limit=limit,
        offset=offset,
        event_type=event_type,
    )
    return ActivityListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.get(
    "/{activity_id}",
    response_model=ActivityRead,
    summary="Get a single activity event",
)
def get_activity(
    idea_id: UUID, activity_id: UUID, db: Session = Depends(get_db)
) -> ActivityRead:
    row = activity_service.get(db, idea_id, activity_id)
    return ActivityRead.model_validate(row)