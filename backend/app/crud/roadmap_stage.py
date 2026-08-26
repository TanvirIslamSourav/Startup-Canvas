"""CRUD for ``RoadmapStage`` rows (1:N under a roadmap, ordered)."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.roadmap_stage import RoadmapStage
from app.schemas.roadmap_stage import RoadmapStageCreate, RoadmapStageUpdate


def get(db: Session, stage_id: UUID) -> RoadmapStage | None:
    return db.get(RoadmapStage, stage_id)


def list_for_roadmap(
    db: Session,
    roadmap_id: UUID,
    *,
    limit: int,
    offset: int,
) -> tuple[Sequence[RoadmapStage], int]:
    stmt = (
        select(RoadmapStage)
        .where(RoadmapStage.roadmap_id == roadmap_id)
        .order_by(RoadmapStage.position.asc(), RoadmapStage.created_at.asc())
    )
    count_stmt = select(func.count()).select_from(RoadmapStage).where(
        RoadmapStage.roadmap_id == roadmap_id
    )
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def next_position(db: Session, roadmap_id: UUID) -> int:
    """Return the next free 1-based position for a new stage."""
    row = db.execute(
        select(func.coalesce(func.max(RoadmapStage.position), 0)).where(
            RoadmapStage.roadmap_id == roadmap_id
        )
    ).scalar_one()
    return int(row) + 1


def create(
    db: Session, roadmap_id: UUID, payload: RoadmapStageCreate
) -> RoadmapStage:
    position = payload.position or next_position(db, roadmap_id)
    # If caller explicitly requested a position, shift later stages up.
    if payload.position is not None:
        existing = db.execute(
            select(RoadmapStage)
            .where(RoadmapStage.roadmap_id == roadmap_id)
            .where(RoadmapStage.position >= position)
            .order_by(RoadmapStage.position.desc())
        ).scalars().all()
        for stage in existing:
            stage.position += 1
            db.add(stage)
    row = RoadmapStage(
        roadmap_id=roadmap_id,
        position=position,
        title=payload.title,
        description=payload.description,
        target_date=payload.target_date,
        completion=payload.completion,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(
    db: Session, row: RoadmapStage, payload: RoadmapStageUpdate
) -> RoadmapStage:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: RoadmapStage) -> None:
    db.delete(row)
    db.commit()


def average_completion(db: Session, roadmap_id: UUID) -> int:
    """Compute the average completion across stages (0 if no stages)."""
    avg = db.execute(
        select(func.coalesce(func.avg(RoadmapStage.completion), 0.0)).where(
            RoadmapStage.roadmap_id == roadmap_id
        )
    ).scalar_one()
    return int(round(float(avg)))
