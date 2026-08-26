"""phase7_roadmap_activity — Roadmap (1:1 with idea), RoadmapStage (1:N under\nroadmap, ordered), Activity (append-only event log).\n\nRevision ID: 0003_roadmap_activity
Revises: b12e7b274d11
Create Date: 2026-08-05
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_roadmap_activity"
down_revision: str | Sequence[str] | None = "b12e7b274d11"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # 1: roadmaps -----------------------------------------------------------
    op.create_table(
        "roadmaps",
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("target_completion", sa.Date(), nullable=True),
        sa.Column(
            "completion",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "completion >= 0 AND completion <= 100",
            name="ck_roadmaps_completion",
        ),
        sa.ForeignKeyConstraint(
            ["idea_id"], ["ideas.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idea_id", name="uq_roadmaps_idea_id"),
    )
    op.execute(
        "CREATE TRIGGER trg_roadmaps_updated_at "
        "BEFORE UPDATE ON roadmaps "
        "FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # 2: roadmap_stages -----------------------------------------------------
    op.create_table(
        "roadmap_stages",
        sa.Column("roadmap_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column(
            "completed_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "completion",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "position >= 1", name="ck_roadmap_stages_position"
        ),
        sa.CheckConstraint(
            "completion >= 0 AND completion <= 100",
            name="ck_roadmap_stages_completion",
        ),
        sa.ForeignKeyConstraint(
            ["roadmap_id"], ["roadmaps.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_roadmap_stages_roadmap_pos",
        "roadmap_stages",
        ["roadmap_id", "position"],
        unique=False,
    )
    op.execute(
        "CREATE TRIGGER trg_roadmap_stages_updated_at "
        "BEFORE UPDATE ON roadmap_stages "
        "FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # 3: activities (append-only event log) ---------------------------------
    op.create_table(
        "activities",
        sa.Column("idea_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column(
            "event_data",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["idea_id"], ["ideas.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_activities_idea_created",
        "activities",
        ["idea_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_activities_event_type",
        "activities",
        ["event_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_activities_event_type", table_name="activities")
    op.drop_index("ix_activities_idea_created", table_name="activities")
    op.drop_table("activities")
    op.execute("DROP TRIGGER IF EXISTS trg_roadmap_stages_updated_at ON roadmap_stages;")
    op.drop_index("ix_roadmap_stages_roadmap_pos", table_name="roadmap_stages")
    op.drop_table("roadmap_stages")
    op.execute("DROP TRIGGER IF EXISTS trg_roadmaps_updated_at ON roadmaps;")
    op.drop_table("roadmaps")