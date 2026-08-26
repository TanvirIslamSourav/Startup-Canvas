"""Business-logic layer for Milestones."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import milestone as milestone_crud
from app.models.milestone import Milestone
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate
from app.services._parent import ensure_idea_exists


def list_milestones(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Milestone], int]:
    ensure_idea_exists(db, idea_id)
    return milestone_crud.list_for_idea(db, idea_id, limit=limit, offset=offset)


def create_milestone(
    db: Session, idea_id: UUID, payload: MilestoneCreate
) -> Milestone:
    ensure_idea_exists(db, idea_id)
    return milestone_crud.create(db, idea_id, payload)


def get_milestone(db: Session, idea_id: UUID, milestone_id: UUID) -> Milestone:
    ensure_idea_exists(db, idea_id)
    row = milestone_crud.get(db, milestone_id)
    if row is None or row.idea_id != idea_id:
        raise NotFoundError(
            message=f"Milestone {milestone_id} not found for idea {idea_id}",
            details={"resource": "milestone", "id": str(milestone_id)},
        )
    return row


def update_milestone(
    db: Session, idea_id: UUID, milestone_id: UUID, payload: MilestoneUpdate
) -> Milestone:
    row = get_milestone(db, idea_id, milestone_id)
    return milestone_crud.update(db, row, payload)


def delete_milestone(db: Session, idea_id: UUID, milestone_id: UUID) -> None:
    row = get_milestone(db, idea_id, milestone_id)
    milestone_crud.delete(db, row)