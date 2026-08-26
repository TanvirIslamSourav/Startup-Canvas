"""Initial schema: users, startup_projects, ideas.

Revision ID: 0001_init
Revises:
Create Date: 2026-08-04
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_init"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # Generic trigger that keeps ``updated_at`` fresh on every row update.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # users ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(120), nullable=True),
        sa.Column("locale", sa.String(8), nullable=False, server_default="en"),
        sa.Column("theme", sa.String(16), nullable=False, server_default="system"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.execute(
        "CREATE TRIGGER trg_users_updated_at "
        "BEFORE UPDATE ON users "
        "FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # startup_projects -------------------------------------------------------
    op.create_table(
        "startup_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("stage", sa.String(32), nullable=False, server_default="idea"),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column(
            "tags",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "status IN ('active','paused','completed')",
            name="ck_startup_projects_status",
        ),
    )
    op.create_index("ix_startup_projects_owner_id", "startup_projects", ["owner_id"])
    op.execute(
        "CREATE TRIGGER trg_startup_projects_updated_at "
        "BEFORE UPDATE ON startup_projects "
        "FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )

    # ideas ------------------------------------------------------------------
    op.create_table(
        "ideas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("startup_projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("problem", sa.Text, nullable=True),
        sa.Column("solution", sa.Text, nullable=True),
        sa.Column("audience", sa.Text, nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("priority", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("score", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column(
            "is_archived", sa.Boolean, nullable=False, server_default=sa.text("false")
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "status IN ('draft','validating','planned','in_progress',"
            "'on_hold','completed','archived')",
            name="ck_ideas_status",
        ),
        sa.CheckConstraint(
            "priority >= 0 AND priority <= 5", name="ck_ideas_priority"
        ),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_ideas_score"),
    )
    op.create_index("ix_ideas_project_status", "ideas", ["project_id", "status"])
    op.create_index("ix_ideas_category", "ideas", ["category"])
    # GIN index for tag searches.
    op.execute('CREATE INDEX "ix_ideas_tags_gin" ON ideas USING gin ("tags");')
    op.execute(
        "CREATE TRIGGER trg_ideas_updated_at "
        "BEFORE UPDATE ON ideas "
        "FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_ideas_updated_at ON ideas;")
    op.execute("DROP TRIGGER IF EXISTS trg_startup_projects_updated_at ON startup_projects;")
    op.execute("DROP TRIGGER IF EXISTS trg_users_updated_at ON users;")
    op.drop_table("ideas")
    op.drop_table("startup_projects")
    op.drop_table("users")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")