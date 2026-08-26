"""Business-logic layer for Roadmap (1:1 with idea).

The roadmap keeps a server-computed ``completion`` field that is the
average of stage completion values. Every mutation of the roadmap OR
its stages recomputes the aggregate.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import activity as activity_crud
from app.crud import roadmap as roadmap_crud
from app.crud import roadmap_stage as stage_crud
from app.models.roadmap import Roadmap
from app.models.roadmap_stage import RoadmapStage
from app.schemas.roadmap import RoadmapCreate, RoadmapUpdate
from app.schemas.roadmap_stage import (
    RoadmapStageCreate,
    RoadmapStageUpdate,
)
from app.services._parent import ensure_idea_exists

# ----- roadmap (1:1) ------------------------------------------------------

def get(db: Session, idea_id: UUID) -> Roadmap | None:
    ensure_idea_exists(db, idea_id)
    return roadmap_crud.get_by_idea(db, idea_id)


def upsert(db: Session, idea_id: UUID, payload: RoadmapCreate) -> Roadmap:
    """Create-or-replace the roadmap for an idea. Existing stages are dropped."""
    ensure_idea_exists(db, idea_id)
    existing = roadmap_crud.get_by_idea(db, idea_id)
    if existing is not None:
        db.delete(existing)
        db.commit()
    row = roadmap_crud.create(db, idea_id, payload)
    activity_crud.append(
        db,
        idea_id=idea_id,
        event_type="roadmap.upserted",
        event_data={"roadmap_id": str(row.id), "title": row.title},
    )
    return row


def update(
    db: Session, idea_id: UUID, payload: RoadmapUpdate
) -> Roadmap:
    ensure_idea_exists(db, idea_id)
    row = roadmap_crud.get_by_idea(db, idea_id)
    if row is None:
        raise NotFoundError(
            message=f"Roadmap for idea {idea_id} not found",
            details={"resource": "roadmap", "idea_id": str(idea_id)},
        )
    return roadmap_crud.update(db, row, payload)


def delete(db: Session, idea_id: UUID) -> None:
    ensure_idea_exists(db, idea_id)
    row = roadmap_crud.get_by_idea(db, idea_id)
    if row is not None:
        roadmap_crud.delete(db, row)


def recompute_completion(db: Session, roadmap_id: UUID) -> int:
    """Recompute and persist the roadmap-level completion from stages."""
    avg = stage_crud.average_completion(db, roadmap_id)
    row = roadmap_crud.get(db, roadmap_id)
    if row is None:
        return avg
    roadmap_crud.set_completion(db, row, avg)
    return avg


# ----- stages (1:N under a roadmap) ---------------------------------------

def _load_roadmap_for_idea(
    db: Session, idea_id: UUID
) -> Roadmap:
    ensure_idea_exists(db, idea_id)
    row = roadmap_crud.get_by_idea(db, idea_id)
    if row is None:
        raise NotFoundError(
            message=f"Roadmap for idea {idea_id} not found. Create it first.",
            details={"resource": "roadmap", "idea_id": str(idea_id)},
        )
    return row


def _load_stage(
    db: Session, idea_id: UUID, stage_id: UUID
) -> RoadmapStage:
    roadmap = _load_roadmap_for_idea(db, idea_id)
    row = stage_crud.get(db, stage_id)
    if row is None or row.roadmap_id != roadmap.id:
        raise NotFoundError(
            message=f"Stage {stage_id} not found for idea {idea_id}",
            details={"resource": "roadmap_stage", "id": str(stage_id)},
        )
    return row


def list_stages(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[list[RoadmapStage], int]:
    roadmap = _load_roadmap_for_idea(db, idea_id)
    return stage_crud.list_for_roadmap(
        db, roadmap.id, limit=limit, offset=offset
    )


def create_stage(
    db: Session, idea_id: UUID, payload: RoadmapStageCreate
) -> RoadmapStage:
    roadmap = _load_roadmap_for_idea(db, idea_id)
    row = stage_crud.create(db, roadmap.id, payload)
    recompute_completion(db, roadmap.id)
    activity_crud.append(
        db,
        idea_id=idea_id,
        event_type="roadmap_stage.created",
        event_data={
            "stage_id": str(row.id),
            "title": row.title,
            "position": row.position,
        },
    )
    return row


def get_stage(
    db: Session, idea_id: UUID, stage_id: UUID
) -> RoadmapStage:
    return _load_stage(db, idea_id, stage_id)


def update_stage(
    db: Session,
    idea_id: UUID,
    stage_id: UUID,
    payload: RoadmapStageUpdate,
) -> RoadmapStage:
    roadmap = _load_roadmap_for_idea(db, idea_id)
    row = _load_stage(db, idea_id, stage_id)
    updated = stage_crud.update(db, row, payload)
    new_avg = recompute_completion(db, roadmap.id)
    event_type = (
        "roadmap_stage.completed"
        if updated.completion == 100
        else "roadmap_stage.updated"
    )
    activity_crud.append(
        db,
        idea_id=idea_id,
        event_type=event_type,
        event_data={
            "stage_id": str(updated.id),
            "completion": updated.completion,
            "roadmap_completion": new_avg,
        },
    )
    return updated


def delete_stage(
    db: Session, idea_id: UUID, stage_id: UUID
) -> None:
    roadmap = _load_roadmap_for_idea(db, idea_id)
    row = _load_stage(db, idea_id, stage_id)
    stage_crud.delete(db, row)
    new_avg = recompute_completion(db, roadmap.id)
    activity_crud.append(
        db,
        idea_id=idea_id,
        event_type="roadmap_stage.deleted",
        event_data={
            "stage_id": str(stage_id),
            "roadmap_completion": new_avg,
        },
    )