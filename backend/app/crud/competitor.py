"""CRUD repository for ``Competitor`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate


def get(db: Session, competitor_id: UUID) -> Competitor | None:
    return db.get(Competitor, competitor_id)


def list_for_idea(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[Competitor], int]:
    stmt = (
        select(Competitor)
        .where(Competitor.idea_id == idea_id)
        .order_by(Competitor.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(Competitor).where(
        Competitor.idea_id == idea_id
    )
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def create(db: Session, idea_id: UUID, payload: CompetitorCreate) -> Competitor:
    row = Competitor(idea_id=idea_id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(
    db: Session, row: Competitor, payload: CompetitorUpdate
) -> Competitor:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: Competitor) -> None:
    db.delete(row)
    db.commit()