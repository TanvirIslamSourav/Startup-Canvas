"""CRUD repository for ``Milestone`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.milestone import Milestone
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate


def get(db: Session, milestone_id: UUID) -> Milestone | None:
    return db.get(Milestone, milestone_id)


def list_for_idea(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Milestone], int]:
    stmt = (
        select(Milestone)
        .where(Milestone.idea_id == idea_id)
        .order_by(Milestone.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(Milestone).where(
        Milestone.idea_id == idea_id
    )
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def create(
    db: Session, idea_id: UUID, payload: MilestoneCreate
) -> Milestone:
    row = Milestone(idea_id=idea_id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(
    db: Session, row: Milestone, payload: MilestoneUpdate
) -> Milestone:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: Milestone) -> None:
    db.delete(row)
    db.commit()