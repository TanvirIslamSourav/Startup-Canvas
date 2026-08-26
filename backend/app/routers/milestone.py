"""HTTP routes for milestones nested under an idea."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.milestone import (
    MilestoneCreate,
    MilestoneListResponse,
    MilestoneRead,
    MilestoneUpdate,
)
from app.services import milestone as milestone_service

router = APIRouter(prefix="/ideas/{idea_id}/milestones", tags=["milestones"])


@router.get("", response_model=MilestoneListResponse, summary="List milestones")
def list_milestones(
    idea_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> MilestoneListResponse:
    items, total = milestone_service.list_milestones(
        db, idea_id, limit=limit, offset=offset
    )
    return MilestoneListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "",
    response_model=MilestoneRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a milestone",
)
def create_milestone(
    idea_id: UUID,
    payload: MilestoneCreate,
    db: Session = Depends(get_db),
) -> MilestoneRead:
    row = milestone_service.create_milestone(db, idea_id, payload)
    return MilestoneRead.model_validate(row)


@router.get(
    "/{milestone_id}", response_model=MilestoneRead, summary="Get a milestone"
)
def get_milestone(
    idea_id: UUID, milestone_id: UUID, db: Session = Depends(get_db)
) -> MilestoneRead:
    row = milestone_service.get_milestone(db, idea_id, milestone_id)
    return MilestoneRead.model_validate(row)


@router.patch(
    "/{milestone_id}", response_model=MilestoneRead, summary="Update a milestone"
)
def update_milestone(
    idea_id: UUID,
    milestone_id: UUID,
    payload: MilestoneUpdate,
    db: Session = Depends(get_db),
) -> MilestoneRead:
    row = milestone_service.update_milestone(db, idea_id, milestone_id, payload)
    return MilestoneRead.model_validate(row)


@router.delete(
    "/{milestone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a milestone",
)
def delete_milestone(
    idea_id: UUID, milestone_id: UUID, db: Session = Depends(get_db)
) -> Response:
    milestone_service.delete_milestone(db, idea_id, milestone_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)