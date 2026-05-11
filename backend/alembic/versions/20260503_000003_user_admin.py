"""user_admin

Revision ID: 20260503_000003
Revises: 20260503_000002
Create Date: 2026-05-03 01:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260503_000003"
down_revision = "20260503_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
