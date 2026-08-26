"""CRUD for ``ProgressTracker`` (1:1 with idea, server-computed)."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.progress_tracker import ProgressTracker


def get_by_idea(db: Session, idea_id: UUID) -> ProgressTracker | None:
    return db.query(ProgressTracker).filter_by(idea_id=idea_id).one_or_none()


def upsert(
    db: Session,
    idea_id: UUID,
    *,
    overall_completion: int,
    health_score: int,
    milestone_progress: int,
    task_completion: int,
) -> ProgressTracker:
    row = get_by_idea(db, idea_id)
    if row is None:
        row = ProgressTracker(
            idea_id=idea_id,
            overall_completion=overall_completion,
            health_score=health_score,
            milestone_progress=milestone_progress,
            task_completion=task_completion,
            last_computed_at=datetime.now(UTC),
        )
        db.add(row)
    else:
        row.overall_completion = overall_completion
        row.health_score = health_score
        row.milestone_progress = milestone_progress
        row.task_completion = task_completion
        row.last_computed_at = datetime.now(UTC)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, idea_id: UUID) -> None:
    row = get_by_idea(db, idea_id)
    if row is not None:
        db.delete(row)
        db.commit()