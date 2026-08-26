"""CRUD repository for ``StartupProject`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.startup_project import StartupProject
from app.schemas.startup_project import StartupProjectCreate, StartupProjectUpdate


class StartupProjectFilter:
    __slots__ = ("include_archived", "owner_id", "search", "status")

    def __init__(
        self,
        *,
        owner_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        include_archived: bool = True,
    ) -> None:
        self.owner_id = owner_id
        self.status = status
        self.search = search
        self.include_archived = include_archived


def get(db: Session, project_id: UUID) -> StartupProject | None:
    return db.get(StartupProject, project_id)


def list_projects(
    db: Session,
    *,
    filters: StartupProjectFilter,
    limit: int,
    offset: int,
) -> tuple[Sequence[StartupProject], int]:
    stmt = select(StartupProject)
    count_stmt = select(func.count()).select_from(StartupProject)

    if filters.owner_id is not None:
        stmt = stmt.where(StartupProject.owner_id == filters.owner_id)
        count_stmt = count_stmt.where(StartupProject.owner_id == filters.owner_id)
    if filters.status is not None:
        stmt = stmt.where(StartupProject.status == filters.status)
        count_stmt = count_stmt.where(StartupProject.status == filters.status)
    if filters.search:
        like = f"%{filters.search.strip()}%"
        stmt = stmt.where(StartupProject.name.ilike(like))
        count_stmt = count_stmt.where(StartupProject.name.ilike(like))

    stmt = stmt.order_by(StartupProject.updated_at.desc())
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def create(db: Session, payload: StartupProjectCreate) -> StartupProject:
    project = StartupProject(
        owner_id=payload.owner_id,
        name=payload.name,
        description=payload.description,
        stage=payload.stage,
        status=payload.status,
        tags=payload.tags,
        metadata_json=payload.metadata_json,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update(
    db: Session, project: StartupProject, payload: StartupProjectUpdate
) -> StartupProject:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(project, field, value)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, project: StartupProject) -> None:
    db.delete(project)
    db.commit()