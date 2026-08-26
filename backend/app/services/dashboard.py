"""Service layer for the dashboard summary endpoint.

The dashboard is a **read-only** composition: it aggregates counts and
averages from the existing 1:N tables for a given idea. No writes. No
new tables. Performance: at most one count query per resource plus a
small fetch for the latest 10 activities.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import idea as idea_crud
from app.models.activity import Activity
from app.models.competitor import Competitor
from app.models.customer_persona import CustomerPersona
from app.models.document import Document
from app.models.milestone import Milestone
from app.models.note import Note
from app.models.roadmap import Roadmap
from app.models.roadmap_stage import RoadmapStage
from app.models.task import Task
from app.schemas.dashboard import (
    DashboardSummary,
    ResourceCounts,
    TaskCounts,
)


def _count(db: Session, model, **filters: object) -> int:
    stmt = select(func.count()).select_from(model)
    for col, val in filters.items():
        stmt = stmt.where(getattr(model, col) == val)
    return int(db.execute(stmt).scalar_one())


def summarise(db: Session, idea_id: UUID) -> DashboardSummary:
    if idea_crud.get(db, idea_id) is None:
        raise NotFoundError(
            message=f"Idea {idea_id} not found",
            details={"resource": "idea", "id": str(idea_id)},
        )

    # task counts by status
    task_counts = TaskCounts(
        todo=_count(db, Task, idea_id=idea_id, status="todo"),
        in_progress=_count(db, Task, idea_id=idea_id, status="in_progress"),
        blocked=_count(db, Task, idea_id=idea_id, status="blocked"),
        done=_count(db, Task, idea_id=idea_id, status="done"),
        total=_count(db, Task, idea_id=idea_id),
    )

    resource_counts = ResourceCounts(
        competitors=_count(db, Competitor, idea_id=idea_id),
        personas=_count(db, CustomerPersona, idea_id=idea_id),
        tasks=task_counts.total,
        milestones=_count(db, Milestone, idea_id=idea_id),
        documents=_count(db, Document, idea_id=idea_id),
        notes=_count(db, Note, idea_id=idea_id),
        activities=_count(db, Activity, idea_id=idea_id),
    )

    # average milestone completion (0 if no milestones)
    avg = db.execute(
        select(func.coalesce(func.avg(Milestone.completion), 0.0)).where(
            Milestone.idea_id == idea_id
        )
    ).scalar_one()
    milestone_avg = int(round(float(avg)))

    # roadmap (optional)
    roadmap: Roadmap | None = db.execute(
        select(Roadmap).where(Roadmap.idea_id == idea_id)
    ).scalar_one_or_none()

    roadmap_id: UUID | None = roadmap.id if roadmap else None
    roadmap_completion: int | None = roadmap.completion if roadmap else None
    stage_count = 0
    if roadmap is not None:
        stage_count = _count(db, RoadmapStage, roadmap_id=roadmap.id)

    return DashboardSummary(
        idea_id=idea_id,
        task_counts=task_counts,
        resource_counts=resource_counts,
        milestone_completion_avg=milestone_avg,
        roadmap_id=roadmap_id,
        roadmap_completion=roadmap_completion,
        roadmap_stage_count=stage_count,
        generated_at=datetime.now(UTC),
    )