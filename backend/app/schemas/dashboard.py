"""Pydantic schemas for the dashboard summary endpoint."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCounts(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    todo: int = Field(ge=0)
    in_progress: int = Field(ge=0)
    blocked: int = Field(ge=0)
    done: int = Field(ge=0)
    total: int = Field(ge=0)


class ResourceCounts(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    competitors: int = Field(ge=0)
    personas: int = Field(ge=0)
    tasks: int = Field(ge=0)
    milestones: int = Field(ge=0)
    documents: int = Field(ge=0)
    notes: int = Field(ge=0)
    activities: int = Field(ge=0)


class DashboardSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idea_id: UUID
    task_counts: TaskCounts
    resource_counts: ResourceCounts
    milestone_completion_avg: int = Field(ge=0, le=100)
    roadmap_id: UUID | None = None
    roadmap_completion: int | None = Field(default=None, ge=0, le=100)
    roadmap_stage_count: int = Field(ge=0)
    generated_at: datetime