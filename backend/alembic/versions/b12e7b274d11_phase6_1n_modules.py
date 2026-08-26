"""phase6_1n_modules — 6 nested 1:N resources for an idea.

Adds:
- competitors
- customer_personas
- tasks
- milestones
- documents
- notes

Revision ID: b12e7b274d11
Revises: 0001_init
Create Date: 2026-08-04 21:36:44.886975
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.db.types import JSONBType, UUIDType

revision: str = "b12e7b274d11"
down_revision: str | Sequence[str] | None = "0001_init"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # 1: competitors --------------------------------------------------
    op.create_table(
        "competitors",
        sa.Column("idea_id", UUIDType(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("website_url", sa.String(length=255), nullable=True),
        sa.Column("pricing", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column(
            "pricing_currency",
            sa.String(length=8),
            server_default="USD",
            nullable=False,
        ),
        sa.Column("strengths", sa.Text(), nullable=True),
        sa.Column("weaknesses", sa.Text(), nullable=True),
        sa.Column("features", JSONBType(), server_default="[]", nullable=False),
        sa.Column("market_position", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "pricing IS NULL OR pricing >= 0", name="ck_competitors_pricing"
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_competitors_idea", "competitors", ["idea_id"], unique=False)

    # 2: customer_personas --------------------------------------------
    op.create_table(
        "customer_personas",
        sa.Column("idea_id", UUIDType(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("age", sa.SmallInteger(), nullable=True),
        sa.Column("occupation", sa.String(length=120), nullable=True),
        sa.Column("goals", sa.Text(), nullable=True),
        sa.Column("pain_points", sa.Text(), nullable=True),
        sa.Column("needs", sa.Text(), nullable=True),
        sa.Column("behaviour", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "age IS NULL OR (age >= 0 AND age <= 150)",
            name="ck_personas_age",
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3: tasks --------------------------------------------------------
    op.create_table(
        "tasks",
        sa.Column("idea_id", UUIDType(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "priority",
            sa.String(length=16),
            server_default="medium",
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=16), server_default="todo", nullable=False
        ),
        sa.Column(
            "progress", sa.SmallInteger(), server_default="0", nullable=False
        ),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "priority IN ('low','medium','high','urgent')",
            name="ck_tasks_priority",
        ),
        sa.CheckConstraint(
            "status IN ('todo','in_progress','blocked','done')",
            name="ck_tasks_status",
        ),
        sa.CheckConstraint(
            "progress >= 0 AND progress <= 100", name="ck_tasks_progress"
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tasks_idea_status", "tasks", ["idea_id", "status"], unique=False
    )
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"], unique=False)

    # 4: milestones ---------------------------------------------------
    op.create_table(
        "milestones",
        sa.Column("idea_id", UUIDType(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "completion", sa.SmallInteger(), server_default="0", nullable=False
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "completion >= 0 AND completion <= 100", name="ck_milestones_completion"
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 5: documents ----------------------------------------------------
    op.create_table(
        "documents",
        sa.Column("idea_id", UUIDType(), nullable=False),
        sa.Column(
            "kind",
            sa.String(length=32),
            server_default="attachment",
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "kind IN ('business_plan','pitch_deck','note','attachment')",
            name="ck_documents_kind",
        ),
        sa.CheckConstraint(
            "size_bytes IS NULL OR size_bytes >= 0", name="ck_documents_size"
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 6: notes --------------------------------------------------------
    op.create_table(
        "notes",
        sa.Column("idea_id", UUIDType(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("notes")
    op.drop_table("documents")
    op.drop_table("milestones")
    op.drop_index("ix_tasks_due_date", table_name="tasks")
    op.drop_index("ix_tasks_idea_status", table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("customer_personas")
    op.drop_index("ix_competitors_idea", table_name="competitors")
    op.drop_table("competitors")