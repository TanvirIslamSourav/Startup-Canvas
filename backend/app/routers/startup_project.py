"""HTTP routes for ``/projects``."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.crud.startup_project import StartupProjectFilter
from app.db.session import get_db
from app.schemas.startup_project import (
    StartupProjectCreate,
    StartupProjectListResponse,
    StartupProjectRead,
    StartupProjectUpdate,
)
from app.services import startup_project as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "",
    response_model=StartupProjectListResponse,
    summary="List projects (paginated, filterable)",
)
def list_projects(
    db: Session = Depends(get_db),
    owner_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> StartupProjectListResponse:
    filters = StartupProjectFilter(
        owner_id=owner_id, status=status_filter, search=search
    )
    items, total = project_service.list_projects(
        db, filters=filters, limit=limit, offset=offset
    )
    return StartupProjectListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


@router.post(
    "",
    response_model=StartupProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project",
)
def create_project(
    payload: StartupProjectCreate, db: Session = Depends(get_db)
) -> StartupProjectRead:
    project = project_service.create_project(db, payload)
    return StartupProjectRead.model_validate(project)


@router.get(
    "/{project_id}", response_model=StartupProjectRead, summary="Get one project"
)
def get_project(project_id: UUID, db: Session = Depends(get_db)) -> StartupProjectRead:
    project = project_service.get_project(db, project_id)
    return StartupProjectRead.model_validate(project)


@router.patch(
    "/{project_id}", response_model=StartupProjectRead, summary="Update a project"
)
def update_project(
    project_id: UUID,
    payload: StartupProjectUpdate,
    db: Session = Depends(get_db),
) -> StartupProjectRead:
    project = project_service.update_project(db, project_id, payload)
    return StartupProjectRead.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a project (only if empty)",
)
def delete_project(project_id: UUID, db: Session = Depends(get_db)) -> Response:
    project_service.delete_project(db, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
