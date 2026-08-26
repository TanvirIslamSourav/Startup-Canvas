"""Pydantic v2 schemas for the Tasks module."""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.task import TASK_PRIORITIES, TASK_STATUSES

_TXT = Field(default=None, max_length=10_000)


def _validate_choice(value: str | None, choices: tuple[str, ...], field: str) -> str | None:
    if value is not None and value not in choices:
        raise ValueError(
            f"{field} must be one of {sorted(choices)} (got {value!r})"
        )
    return value


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = _TXT
    priority: str = "medium"
    status: str = "todo"
    progress: int = Field(default=0, ge=0, le=100)
    due_date: date | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @field_validator("priority")
    @classmethod
    def _check_priority(cls, value: str) -> str:
        if value not in TASK_PRIORITIES:
            raise ValueError(
                f"priority must be one of {sorted(TASK_PRIORITIES)} (got {value!r})"
            )
        return value

    @field_validator("status")
    @classmethod
    def _check_status(cls, value: str) -> str:
        if value not in TASK_STATUSES:
            raise ValueError(
                f"status must be one of {sorted(TASK_STATUSES)} (got {value!r})"
            )
        return value


class TaskCreate(TaskBase):
    """Payload for ``POST``."""

    model_config = ConfigDict(extra="forbid")


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = _TXT
    priority: str | None = None
    status: str | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    due_date: date | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @field_validator("priority")
    @classmethod
    def _check_priority(cls, value: str | None) -> str | None:
        return _validate_choice(value, TASK_PRIORITIES, "priority")

    @field_validator("status")
    @classmethod
    def _check_status(cls, value: str | None) -> str | None:
        return _validate_choice(value, TASK_STATUSES, "status")


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    idea_id: UUID
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)