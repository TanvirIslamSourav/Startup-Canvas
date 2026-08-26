"""Re-exports so Alembic autogenerate sees every model."""
from app.db.base import Base  # noqa: F401
from app.models import *  # noqa: F403