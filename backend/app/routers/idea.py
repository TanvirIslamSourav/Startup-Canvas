"""HTTP routes for ``/ideas``."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.idea import IdeaFilter
from app.db.session import get_db
from app.schemas.idea import (
    IdeaCreate,
    IdeaListResponse,
    IdeaRead,
    IdeaUpdate,
)
from app.services import idea as idea_service

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.get(
    "",
    response_model=IdeaListResponse,
    summary="List ideas (paginated, filterable)",
)
def list_ideas(
    db: Session = Depends(get_db),
    project_id: UUID | None = Query(default=None, description="Filter by project id"),
    status_filter: str | None = Query(default=None, alias="status", description="Idea status"),
    category: str | None = Query(default=None),
    search: str | None = Query(default=None, description="Substring match against title"),
    include_archived: bool = Query(default=False),
    sort_by: str = Query(default="updated_at", pattern="^(created_at|updated_at|title|priority|score|status)$"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> IdeaListResponse:
    filters = IdeaFilter(
        project_id=project_id,
        status=status_filter,
        category=category,
        include_archived=include_archived,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items, total = idea_service.list_ideas(db, filters=filters, limit=limit, offset=offset)
    return IdeaListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "",
    response_model=IdeaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an idea",
)
def create_idea(payload: IdeaCreate, db: Session = Depends(get_db)) -> IdeaRead:
    idea = idea_service.create_idea(db, payload)
    return IdeaRead.model_validate(idea)


@router.get("/{idea_id}", response_model=IdeaRead, summary="Get one idea")
def get_idea(idea_id: UUID, db: Session = Depends(get_db)) -> IdeaRead:
    idea = idea_service.get_idea(db, idea_id)
    return IdeaRead.model_validate(idea)


@router.patch("/{idea_id}", response_model=IdeaRead, summary="Update an idea")
def update_idea(
    idea_id: UUID, payload: IdeaUpdate, db: Session = Depends(get_db)
) -> IdeaRead:
    idea = idea_service.update_idea(db, idea_id, payload)
    return IdeaRead.model_validate(idea)


@router.delete(
    "/{idea_id}",
    response_model=IdeaRead,
    summary="Soft-archive an idea",
)
def archive_idea(idea_id: UUID, db: Session = Depends(get_db)) -> IdeaRead:
    idea = idea_service.archive_idea(db, idea_id)
    return IdeaRead.model_validate(idea)


@router.post(
    "/{idea_id}/restore",
    response_model=IdeaRead,
    summary="Restore an archived idea",
)
def restore_idea(idea_id: UUID, db: Session = Depends(get_db)) -> IdeaRead:
    idea = idea_service.restore_idea(db, idea_id)
    return IdeaRead.model_validate(idea)


# 404 fallback for unknown ideas — service raises NotFoundError which the
# exception handler in main.py converts to a 404 response.
_ = HTTPException  # keep the import for future use without lint warnings