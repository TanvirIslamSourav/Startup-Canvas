"""CRUD repository for ``Idea`` rows.

A thin SQLAlchemy layer. Service layer is responsible for business rules
(validation, cross-entity checks, computed fields, etc.).
"""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaUpdate


class IdeaFilter:
    """Filter/sort options accepted by :func:`list_ideas`."""

    __slots__ = (
        "category",
        "include_archived",
        "project_id",
        "search",
        "sort_by",
        "sort_dir",
        "status",
    )

    def __init__(
        self,
        *,
        project_id: UUID | None = None,
        status: str | None = None,
        category: str | None = None,
        include_archived: bool = False,
        search: str | None = None,
        sort_by: str = "updated_at",
        sort_dir: str = "desc",
    ) -> None:
        self.project_id = project_id
        self.status = status
        self.category = category
        self.include_archived = include_archived
        self.search = search
        self.sort_by = sort_by
        self.sort_dir = sort_dir


_SORT_COLUMNS = {"created_at", "updated_at", "title", "priority", "score", "status"}


def get(db: Session, idea_id: UUID) -> Idea | None:
    """Return a single idea by id or ``None``."""
    return db.get(Idea, idea_id)


def list_ideas(
    db: Session,
    *,
    filters: IdeaFilter,
    limit: int,
    offset: int,
) -> tuple[Sequence[Idea], int]:
    """Return ``(items, total)`` honoring filter + pagination."""
    stmt = select(Idea)
    count_stmt = select(func.count()).select_from(Idea)

    if filters.project_id is not None:
        stmt = stmt.where(Idea.project_id == filters.project_id)
        count_stmt = count_stmt.where(Idea.project_id == filters.project_id)
    if filters.status is not None:
        stmt = stmt.where(Idea.status == filters.status)
        count_stmt = count_stmt.where(Idea.status == filters.status)
    if filters.category is not None:
        stmt = stmt.where(Idea.category == filters.category)
        count_stmt = count_stmt.where(Idea.category == filters.category)
    if not filters.include_archived:
        stmt = stmt.where(Idea.is_archived.is_(False))
        count_stmt = count_stmt.where(Idea.is_archived.is_(False))
    if filters.search:
        like = f"%{filters.search.strip()}%"
        stmt = stmt.where(Idea.title.ilike(like))
        count_stmt = count_stmt.where(Idea.title.ilike(like))

    sort_col = filters.sort_by if filters.sort_by in _SORT_COLUMNS else "updated_at"
    sort_attr = getattr(Idea, sort_col)
    stmt = stmt.order_by(sort_attr.desc() if filters.sort_dir == "desc" else sort_attr.asc())

    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = db.execute(count_stmt).scalar_one()
    return items, int(total)


def create(db: Session, payload: IdeaCreate) -> Idea:
    """Insert a new idea and return it (refreshed)."""
    idea = Idea(
        project_id=payload.project_id,
        title=payload.title,
        problem=payload.problem,
        solution=payload.solution,
        audience=payload.audience,
        category=payload.category,
        tags=payload.tags,
        status=payload.status,
        priority=payload.priority,
        score=payload.score,
        is_archived=payload.is_archived,
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


def update(db: Session, idea: Idea, payload: IdeaUpdate) -> Idea:
    """Apply a partial update to an idea and return it."""
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(idea, field, value)
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


def delete(db: Session, idea: Idea) -> None:
    """Soft-archive an idea (we never hard-delete user content in v1)."""
    from datetime import UTC, datetime

    idea.is_archived = True
    idea.archived_at = datetime.now(UTC)
    db.add(idea)
    db.commit()