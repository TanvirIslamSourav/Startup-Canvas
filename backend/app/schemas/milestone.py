"""Pydantic v2 schemas for the Milestones module."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class MilestoneBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = _TXT
    target_date: date | None = None
    completed_at: datetime | None = None
    completion: int = Field(default=0, ge=0, le=100)


class MilestoneCreate(MilestoneBase):
    """Payload for ``POST``."""

    model_config = ConfigDict(extra="forbid")


class MilestoneUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = _TXT
    target_date: date | None = None
    completed_at: datetime | None = None
    completion: int | None = Field(default=None, ge=0, le=100)


class MilestoneRead(MilestoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime


class MilestoneListResponse(BaseModel):
    items: list[MilestoneRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)