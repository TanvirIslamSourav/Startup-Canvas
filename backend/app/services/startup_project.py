"""Business-logic layer for startup projects."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.crud import idea as idea_crud
from app.crud import startup_project as project_crud
from app.crud.startup_project import StartupProjectFilter
from app.models.startup_project import StartupProject
from app.schemas.startup_project import (
    StartupProjectCreate,
    StartupProjectUpdate,
)


def get_project(db: Session, project_id: UUID) -> StartupProject:
    project = project_crud.get(db, project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} not found")
    return project


def list_projects(
    db: Session,
    *,
    filters: StartupProjectFilter,
    limit: int,
    offset: int,
) -> tuple[list[StartupProject], int]:
    items, total = project_crud.list_projects(
        db, filters=filters, limit=limit, offset=offset
    )
    return list(items), total


def create_project(db: Session, payload: StartupProjectCreate) -> StartupProject:
    return project_crud.create(db, payload)


def update_project(
    db: Session, project_id: UUID, payload: StartupProjectUpdate
) -> StartupProject:
    project = get_project(db, project_id)
    return project_crud.update(db, project, payload)


def delete_project(db: Session, project_id: UUID) -> None:
    project = get_project(db, project_id)
    # Refuse if there are ideas still attached.
    idea_filter = idea_crud.IdeaFilter(project_id=project_id, include_archived=True)
    _, total = idea_crud.list_ideas(db, filters=idea_filter, limit=1, offset=0)
    if total > 0:
        raise ValidationError(
            "Cannot delete project with existing ideas; archive the project instead."
        )
    project_crud.delete(db, project)
