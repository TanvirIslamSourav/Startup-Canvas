"""CRUD repository for ``CustomerPersona`` rows."""
from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer_persona import CustomerPersona
from app.schemas.customer_persona import (
    CustomerPersonaCreate,
    CustomerPersonaUpdate,
)


def get(db: Session, persona_id: UUID) -> CustomerPersona | None:
    return db.get(CustomerPersona, persona_id)


def list_for_idea(
    db: Session, idea_id: UUID, *, limit: int, offset: int
) -> tuple[Sequence[CustomerPersona], int]:
    stmt = (
        select(CustomerPersona)
        .where(CustomerPersona.idea_id == idea_id)
        .order_by(CustomerPersona.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(CustomerPersona).where(
        CustomerPersona.idea_id == idea_id
    )
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()
    total = int(db.execute(count_stmt).scalar_one())
    return items, total


def create(
    db: Session, idea_id: UUID, payload: CustomerPersonaCreate
) -> CustomerPersona:
    row = CustomerPersona(idea_id=idea_id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update(
    db: Session, row: CustomerPersona, payload: CustomerPersonaUpdate
) -> CustomerPersona:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: CustomerPersona) -> None:
    db.delete(row)
    db.commit()