"""CRUD for ``Roadmap`` rows (1:1 with idea)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.roadmap import Roadmap
from app.schemas.roadmap import RoadmapCreate, RoadmapUpdate


def get_by_idea(db: Session, idea_id: UUID) -> Roadmap | None:
    return db.query(Roadmap).filter_by(idea_id=idea_id).one_or_none()


def get(db: Session, roadmap_id: UUID) -> Roadmap | None:
    return db.get(Roadmap, roadmap_id)


def create(db: Session, idea_id: UUID, payload: RoadmapCreate) -> Roadmap:
    row = Roadmap(idea_id=idea_id, completion=0, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(db: Session, row: Roadmap, payload: RoadmapUpdate) -> Roadmap:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: Roadmap) -> None:
    db.delete(row)
    db.commit()


def set_completion(db: Session, row: Roadmap, completion: int) -> Roadmap:
    """Persist the recomputed roadmap-level completion percentage."""
    row.completion = max(0, min(100, int(completion)))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row