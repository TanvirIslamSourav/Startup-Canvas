"""Pydantic v2 schemas for ordered roadmap stages (1:N under a roadmap)."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class RoadmapStageBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = _TXT
    target_date: date | None = None
    completion: int = Field(default=0, ge=0, le=100)


class RoadmapStageCreate(RoadmapStageBase):
    """Payload for ``POST /ideas/{idea_id}/roadmap/stages``.

    ``position`` is optional; if omitted it is appended at the end.
    """

    model_config = ConfigDict(extra="forbid")

    position: int | None = Field(default=None, ge=1)


class RoadmapStageUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = _TXT
    target_date: date | None = None
    completion: int | None = Field(default=None, ge=0, le=100)
    position: int | None = Field(default=None, ge=1)


class RoadmapStageRead(RoadmapStageBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    roadmap_id: UUID
    position: int = Field(ge=1)
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RoadmapStageListResponse(BaseModel):
    items: list[RoadmapStageRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)