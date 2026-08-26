"""Pydantic v2 schemas for the activity log (append-only)."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.activity import ACTIVITY_EVENT_TYPES


class ActivityCreate(BaseModel):
    """Payload for internal append (typically written by service code, not by clients).

    The Pydantic schema is exposed mainly for validation within the
    service layer; clients normally never POST directly to this resource.
    """

    model_config = ConfigDict(extra="forbid")

    idea_id: UUID
    actor_id: UUID | None = None
    event_type: str = Field(min_length=1, max_length=64)
    event_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_type")
    @classmethod
    def _check_event_type(cls, value: str) -> str:
        if value not in ACTIVITY_EVENT_TYPES:
            raise ValueError(
                f"event_type must be one of {sorted(ACTIVITY_EVENT_TYPES)} "
                f"(got {value!r})"
            )
        return value


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    actor_id: UUID | None = None
    event_type: str
    event_data: dict[str, Any]
    created_at: datetime


class ActivityListResponse(BaseModel):
    items: list[ActivityRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)