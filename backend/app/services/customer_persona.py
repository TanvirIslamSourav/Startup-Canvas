"""Business-logic layer for Customer Personas."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.crud import customer_persona as persona_crud
from app.models.customer_persona import CustomerPersona
from app.schemas.customer_persona import (
    CustomerPersonaCreate,
    CustomerPersonaUpdate,
)
from app.services._parent import ensure_idea_exists


def list_personas(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[CustomerPersona], int]:
    ensure_idea_exists(db, idea_id)
    return persona_crud.list_for_idea(db, idea_id, limit=limit, offset=offset)


def create_persona(
    db: Session, idea_id: UUID, payload: CustomerPersonaCreate
) -> CustomerPersona:
    ensure_idea_exists(db, idea_id)
    return persona_crud.create(db, idea_id, payload)


def get_persona(
    db: Session, idea_id: UUID, persona_id: UUID
) -> CustomerPersona:
    ensure_idea_exists(db, idea_id)
    row = persona_crud.get(db, persona_id)
    if row is None or row.idea_id != idea_id:
        raise NotFoundError(
            message=f"Persona {persona_id} not found for idea {idea_id}",
            details={"resource": "persona", "id": str(persona_id)},
        )
    return row


def update_persona(
    db: Session, idea_id: UUID, persona_id: UUID, payload: CustomerPersonaUpdate
) -> CustomerPersona:
    row = get_persona(db, idea_id, persona_id)
    return persona_crud.update(db, row, payload)


def delete_persona(db: Session, idea_id: UUID, persona_id: UUID) -> None:
    row = get_persona(db, idea_id, persona_id)
    persona_crud.delete(db, row)