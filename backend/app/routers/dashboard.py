"""HTTP routes for the dashboard summary endpoint."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get a per-idea roll-up of resource counts and progress",
)
def get_summary(
    idea_id: UUID,
    db: Session = Depends(get_db),
) -> DashboardSummary:
    """Compose a read-only roll-up of all sub-resources for an idea.

    The ``idea_id`` is passed as a query string parameter so the endpoint
    can be cached by an upstream proxy.
    """
    return dashboard_service.summarise(db, idea_id)