"""Business-logic layer for ideas.

Encapsulates cross-entity checks (project must exist) and computed fields
(``score`` recompute on update). Routers should call these functions
instead of touching CRUD directly.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.crud import idea as idea_crud
from app.crud import startup_project as project_crud
from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaUpdate


def get_idea(db: Session, idea_id: UUID) -> Idea:
    idea = idea_crud.get(db, idea_id)
    if idea is None:
        raise NotFoundError(f"Idea {idea_id} not found")
    return idea


def list_ideas(
    db: Session,
    *,
    filters: idea_crud.IdeaFilter,
    limit: int,
    offset: int,
) -> tuple[list[Idea], int]:
    items, total = idea_crud.list_ideas(db, filters=filters, limit=limit, offset=offset)
    return list(items), total


def create_idea(db: Session, payload: IdeaCreate) -> Idea:
    project = project_crud.get(db, payload.project_id)
    if project is None:
        raise ValidationError(f"project_id {payload.project_id} does not exist")
    return idea_crud.create(db, payload)


def update_idea(db: Session, idea_id: UUID, payload: IdeaUpdate) -> Idea:
    idea = get_idea(db, idea_id)
    return idea_crud.update(db, idea, payload)


def archive_idea(db: Session, idea_id: UUID) -> Idea:
    idea = get_idea(db, idea_id)
    if idea.is_archived:
        return idea  # idempotent
    idea_crud.delete(db, idea)
    db.refresh(idea)
    return idea


def restore_idea(db: Session, idea_id: UUID) -> Idea:

    idea = get_idea(db, idea_id)
    if not idea.is_archived:
        return idea  # idempotent
    idea.is_archived = False
    idea.archived_at = None
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea