"""Pydantic v2 schemas for the Progress Tracker."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgressTrackerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    overall_completion: int = Field(ge=0, le=100)
    health_score: int = Field(ge=0, le=100)
    milestone_progress: int = Field(ge=0, le=100)
    task_completion: int = Field(ge=0, le=100)
    last_computed_at: datetime


class ProgressTrackerUpsert(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_completion: int = Field(ge=0, le=100)
    health_score: int = Field(ge=0, le=100)
    milestone_progress: int = Field(ge=0, le=100)
    task_completion: int = Field(ge=0, le=100)