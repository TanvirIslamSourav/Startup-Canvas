"""Business-logic layer for Tasks."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import task as task_crud
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.services._parent import ensure_idea_exists


def list_tasks(
    db: Session,
    idea_id: UUID,
    *,
    limit: int,
    offset: int,
    status: str | None = None,
) -> tuple[Sequence[Task], int]:
    ensure_idea_exists(db, idea_id)
    return task_crud.list_for_idea(
        db, idea_id, limit=limit, offset=offset, status=status
    )


def create_task(db: Session, idea_id: UUID, payload: TaskCreate) -> Task:
    ensure_idea_exists(db, idea_id)
    return task_crud.create(db, idea_id, payload)


def get_task(db: Session, idea_id: UUID, task_id: UUID) -> Task:
    ensure_idea_exists(db, idea_id)
    row = task_crud.get(db, task_id)
    if row is None or row.idea_id != idea_id:
        raise NotFoundError(
            message=f"Task {task_id} not found for idea {idea_id}",
            details={"resource": "task", "id": str(task_id)},
        )
    return row


def update_task(
    db: Session, idea_id: UUID, task_id: UUID, payload: TaskUpdate
) -> Task:
    row = get_task(db, idea_id, task_id)
    return task_crud.update(db, row, payload)


def delete_task(db: Session, idea_id: UUID, task_id: UUID) -> None:
    row = get_task(db, idea_id, task_id)
    task_crud.delete(db, row)