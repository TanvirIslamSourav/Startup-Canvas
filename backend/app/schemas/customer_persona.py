"""Pydantic v2 schemas for the Customer Personas module."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_TXT = Field(default=None, max_length=10_000)


class CustomerPersonaBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    age: int | None = Field(default=None, ge=0, le=150)
    occupation: str | None = Field(default=None, max_length=120)
    goals: str | None = _TXT
    pain_points: str | None = _TXT
    needs: str | None = _TXT
    behaviour: str | None = _TXT
    avatar_url: str | None = Field(default=None, max_length=512)


class CustomerPersonaCreate(CustomerPersonaBase):
    """Payload for ``POST``."""

    model_config = ConfigDict(extra="forbid")


class CustomerPersonaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    age: int | None = Field(default=None, ge=0, le=150)
    occupation: str | None = Field(default=None, max_length=120)
    goals: str | None = _TXT
    pain_points: str | None = _TXT
    needs: str | None = _TXT
    behaviour: str | None = _TXT
    avatar_url: str | None = Field(default=None, max_length=512)


class CustomerPersonaRead(CustomerPersonaBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime


class CustomerPersonaListResponse(BaseModel):
    items: list[CustomerPersonaRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)