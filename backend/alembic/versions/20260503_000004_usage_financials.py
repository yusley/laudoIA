"""usage_financials

Revision ID: 20260503_000004
Revises: 20260503_000003
Create Date: 2026-05-03 02:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260503_000004"
down_revision = "20260503_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usage_events",
        sa.Column("openrouter_cost_usd", sa.Numeric(12, 6), nullable=False, server_default="0"),
    )
    op.add_column(
        "usage_events",
        sa.Column("exchange_rate_usd_brl", sa.Numeric(12, 4), nullable=False, server_default="0"),
    )
    op.add_column(
        "usage_events",
        sa.Column("openrouter_cost_brl", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "usage_events",
        sa.Column("platform_revenue_brl", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.add_column(
        "usage_events",
        sa.Column("platform_margin_brl", sa.Numeric(12, 2), nullable=False, server_default="0"),
    )
    op.execute(
        """
        UPDATE usage_events
        SET
            openrouter_cost_usd = openrouter_cost_credit,
            exchange_rate_usd_brl = 5.2000,
            openrouter_cost_brl = ROUND((openrouter_cost_credit * 5.20)::numeric, 2),
            platform_revenue_brl = ROUND(platform_cost_credit::numeric, 2),
            platform_margin_brl = ROUND((platform_cost_credit - (openrouter_cost_credit * 5.20))::numeric, 2)
        """
    )


def downgrade() -> None:
    op.drop_column("usage_events", "platform_margin_brl")
    op.drop_column("usage_events", "platform_revenue_brl")
    op.drop_column("usage_events", "openrouter_cost_brl")
    op.drop_column("usage_events", "exchange_rate_usd_brl")
    op.drop_column("usage_events", "openrouter_cost_usd")
