"""phase7_canvas_swot_progress — adds LeanCanvas, BusinessCanvas, Swot, ProgressTracker (1:1 with idea).

Revision ID: 0004_canvas_swot_progress
Revises: 0003_roadmap_activity
Create Date: 2026-08-06
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_canvas_swot_progress"
down_revision: str | Sequence[str] | None = "0003_roadmap_activity"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # 1: lean_canvas -----------------------------------------------------
    op.create_table(
        "lean_canvas",
        sa.Column("idea_id", sa.UUID(), nullable=False),
        sa.Column("problem", sa.Text(), nullable=True),
        sa.Column("solution", sa.Text(), nullable=True),
        sa.Column("key_metrics", sa.Text(), nullable=True),
        sa.Column("unique_value_prop", sa.Text(), nullable=True),
        sa.Column("unfair_advantage", sa.Text(), nullable=True),
        sa.Column("channels", sa.Text(), nullable=True),
        sa.Column("customer_segments", sa.Text(), nullable=True),
        sa.Column("cost_structure", sa.Text(), nullable=True),
        sa.Column("revenue_streams", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("idea_id", name="uq_lean_canvas_idea"),
    )

    # 2: business_canvas -------------------------------------------------
    op.create_table(
        "business_canvas",
        sa.Column("idea_id", sa.UUID(), nullable=False),
        sa.Column("key_partners", sa.Text(), nullable=True),
        sa.Column("key_activities", sa.Text(), nullable=True),
        sa.Column("key_resources", sa.Text(), nullable=True),
        sa.Column("value_propositions", sa.Text(), nullable=True),
        sa.Column("customer_relationships", sa.Text(), nullable=True),
        sa.Column("channels", sa.Text(), nullable=True),
        sa.Column("customer_segments", sa.Text(), nullable=True),
        sa.Column("cost_structure", sa.Text(), nullable=True),
        sa.Column("revenue_streams", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("idea_id", name="uq_business_canvas_idea"),
    )

    # 3: swot ------------------------------------------------------------
    op.create_table(
        "swot",
        sa.Column("idea_id", sa.UUID(), nullable=False),
        sa.Column("strengths", sa.Text(), nullable=True),
        sa.Column("weaknesses", sa.Text(), nullable=True),
        sa.Column("opportunities", sa.Text(), nullable=True),
        sa.Column("threats", sa.Text(), nullable=True),
        sa.Column(
            "score",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("summary", sa.Text(), nullable=True),
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
            "score >= 0 AND score <= 100", name="ck_swot_score"
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idea_id", name="uq_swot_idea"),
    )

    # 4: progress_tracker -----------------------------------------------
    op.create_table(
        "progress_tracker",
        sa.Column("idea_id", sa.UUID(), nullable=False),
        sa.Column(
            "overall_completion",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "health_score",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "milestone_progress",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "task_completion",
            sa.SmallInteger(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "last_computed_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.CheckConstraint(
            "overall_completion >= 0 AND overall_completion <= 100",
            name="ck_progress_overall",
        ),
        sa.CheckConstraint(
            "health_score >= 0 AND health_score <= 100",
            name="ck_progress_health",
        ),
        sa.CheckConstraint(
            "milestone_progress >= 0 AND milestone_progress <= 100",
            name="ck_progress_milestone",
        ),
        sa.CheckConstraint(
            "task_completion >= 0 AND task_completion <= 100",
            name="ck_progress_task",
        ),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idea_id", name="uq_progress_idea"),
    )


def downgrade() -> None:
    op.drop_table("progress_tracker")
    op.drop_table("swot")
    op.drop_table("business_canvas")
    op.drop_table("lean_canvas")
