"""Pydantic v2 schemas for the Roadmap module (1:1 with idea)."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class RoadmapBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str | None = _TXT
    target_completion: date | None = None


class RoadmapCreate(RoadmapBase):
    """Payload for ``POST /ideas/{idea_id}/roadmap``."""

    model_config = ConfigDict(extra="forbid")


class RoadmapUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = _TXT
    target_completion: date | None = None
    completion: int | None = Field(default=None, ge=0, le=100)


class RoadmapRead(RoadmapBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    completion: int = Field(ge=0, le=100)
    created_at: datetime
    updated_at: datetime


class RoadmapReadWithStages(RoadmapRead):
    """Roadmap read with eagerly-loaded stages."""

    model_config = ConfigDict(from_attributes=True)

    stages: list[RoadmapStageRead] = Field(default_factory=list)


# Resolve the forward reference to RoadmapStageRead once both modules
# are importable. The schemas/roadmap_stage module imports nothing from
# this module, so this loop is safe.
from app.schemas.roadmap_stage import RoadmapStageRead  # noqa: E402

RoadmapReadWithStages.model_rebuild()