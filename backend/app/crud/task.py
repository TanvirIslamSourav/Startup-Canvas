"""CRUD repository for ``Task`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def get(db: Session, task_id: UUID) -> Task | None:
    return db.get(Task, task_id)


def list_for_idea(
    db: Session,
    idea_id: UUID,
    *,
    limit: int,
    offset: int,
    status: str | None = None,
) -> tuple[Sequence[Task], int]:
    stmt = select(Task).where(Task.idea_id == idea_id)
    count_stmt = (
        select(func.count()).select_from(Task).where(Task.idea_id == idea_id)
    )
    if status is not None:
        stmt = stmt.where(Task.status == status)
        count_stmt = count_stmt.where(Task.status == status)
    stmt = stmt.order_by(Task.created_at.desc())
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def create(db: Session, idea_id: UUID, payload: TaskCreate) -> Task:
    row = Task(idea_id=idea_id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(db: Session, row: Task, payload: TaskUpdate) -> Task:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: Task) -> None:
    db.delete(row)
    db.commit()