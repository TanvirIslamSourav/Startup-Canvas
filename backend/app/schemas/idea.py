"""Pydantic v2 schemas for the Ideas module."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.idea import IDEA_STATUSES

# Constraints mirroring the DB CHECK constraints --------------------------------
_TITLE = Annotated[str, Field(min_length=1, max_length=200)]
_TAG = Annotated[str, Field(min_length=1, max_length=64)]
_STATUS_LITERAL = Annotated[str, Field(description="One of IDEA_STATUSES")]


class IdeaBase(BaseModel):
    """Fields shared by create/update/read shapes."""

    title: _TITLE
    problem: str | None = Field(default=None, max_length=10_000)
    solution: str | None = Field(default=None, max_length=10_000)
    audience: str | None = Field(default=None, max_length=10_000)
    category: str | None = Field(default=None, max_length=64)
    tags: list[str] = Field(default_factory=list, max_length=50)
    status: str = "draft"
    priority: int = Field(default=0, ge=0, le=5)
    score: int = Field(default=0, ge=0, le=100)
    is_archived: bool = False

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in IDEA_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(IDEA_STATUSES)} (got {value!r})"
            )
        return value

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, value: list[str]) -> list[str]:
        # Strip whitespace, drop empties, dedupe while preserving order.
        seen: set[str] = set()
        out: list[str] = []
        for raw in value:
            tag = raw.strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            out.append(tag)
        return out


class IdeaCreate(IdeaBase):
    """Payload for ``POST /ideas``."""

    project_id: UUID


class IdeaUpdate(BaseModel):
    """Payload for ``PATCH /ideas/{id}``. All fields optional."""

    model_config = ConfigDict(extra="forbid")

    title: _TITLE | None = None
    problem: str | None = Field(default=None, max_length=10_000)
    solution: str | None = Field(default=None, max_length=10_000)
    audience: str | None = Field(default=None, max_length=10_000)
    category: str | None = Field(default=None, max_length=64)
    tags: list[str] | None = Field(default=None, max_length=50)
    status: str | None = None
    priority: int | None = Field(default=None, ge=0, le=5)
    score: int | None = Field(default=None, ge=0, le=100)
    is_archived: bool | None = None

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in IDEA_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(IDEA_STATUSES)} (got {value!r})"
            )
        return value

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        seen: set[str] = set()
        out: list[str] = []
        for raw in value:
            tag = raw.strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            out.append(tag)
        return out


class IdeaRead(IdeaBase):
    """Response shape for read endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class IdeaListResponse(BaseModel):
    """Pagination envelope for ``GET /ideas``."""

    items: list[IdeaRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)