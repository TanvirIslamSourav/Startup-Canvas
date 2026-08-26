"""HTTP routes for tasks nested under an idea."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskRead,
    TaskUpdate,
)
from app.services import task as task_service

router = APIRouter(prefix="/ideas/{idea_id}/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse, summary="List tasks")
def list_tasks(
    idea_id: UUID,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> TaskListResponse:
    items, total = task_service.list_tasks(
        db, idea_id, limit=limit, offset=offset, status=status_filter
    )
    return TaskListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
def create_task(
    idea_id: UUID, payload: TaskCreate, db: Session = Depends(get_db)
) -> TaskRead:
    row = task_service.create_task(db, idea_id, payload)
    return TaskRead.model_validate(row)


@router.get("/{task_id}", response_model=TaskRead, summary="Get a task")
def get_task(
    idea_id: UUID, task_id: UUID, db: Session = Depends(get_db)
) -> TaskRead:
    row = task_service.get_task(db, idea_id, task_id)
    return TaskRead.model_validate(row)


@router.patch("/{task_id}", response_model=TaskRead, summary="Update a task")
def update_task(
    idea_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskRead:
    row = task_service.update_task(db, idea_id, task_id, payload)
    return TaskRead.model_validate(row)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a task",
)
def delete_task(
    idea_id: UUID, task_id: UUID, db: Session = Depends(get_db)
) -> Response:
    task_service.delete_task(db, idea_id, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)