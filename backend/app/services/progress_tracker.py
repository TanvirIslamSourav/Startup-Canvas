"""Business-logic layer for Progress Tracker.

The progress tracker is **server-computed** and cached per idea. Once
the tasks/milestones modules land, the recompute will aggregate from
them. For now we expose a stable read/write contract.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.crud import progress_tracker as pt_crud
from app.models.progress_tracker import ProgressTracker
from app.services._parent import ensure_idea_exists


def get(db: Session, idea_id: UUID) -> ProgressTracker | None:
    ensure_idea_exists(db, idea_id)
    return pt_crud.get_by_idea(db, idea_id)


def upsert(
    db: Session,
    idea_id: UUID,
    *,
    overall_completion: int,
    health_score: int,
    milestone_progress: int,
    task_completion: int,
) -> ProgressTracker:
    ensure_idea_exists(db, idea_id)
    return pt_crud.upsert(
        db,
        idea_id,
        overall_completion=overall_completion,
        health_score=health_score,
        milestone_progress=milestone_progress,
        task_completion=task_completion,
    )