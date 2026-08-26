"""Shared test factories for setting up rows."""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.crud import startup_project as project_crud
from app.crud import user as user_crud
from app.models.startup_project import StartupProject
from app.models.user import User
from app.schemas.idea import IdeaCreate
from app.schemas.startup_project import StartupProjectCreate


def make_user(db: Session, *, email: str = "tester@startup.local", name: str | None = "Tester") -> User:
    return user_crud.create(db, email=email, display_name=name)


def make_project(
    db: Session,
    *,
    owner: User,
    name: str = "Test Project",
    description: str | None = None,
) -> StartupProject:
    return project_crud.create(
        db,
        StartupProjectCreate(
            owner_id=owner.id,
            name=name,
            description=description,
        ),
    )


def make_idea(db: Session, *, project_id: uuid.UUID, title: str = "Idea") -> uuid.UUID:
    from app.crud import idea as idea_crud

    row = idea_crud.create(
        db,
        IdeaCreate(
            project_id=project_id,
            title=title,
            problem="",
            solution="",
            audience="",
        ),
    )
    return row.id
