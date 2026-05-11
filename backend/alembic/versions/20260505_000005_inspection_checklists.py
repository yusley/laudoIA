"""inspection checklists

Revision ID: 20260505_000005
Revises: 20260503_000004
Create Date: 2026-05-05 00:00:05
"""

from alembic import op
import sqlalchemy as sa


revision = "20260505_000005"
down_revision = "20260503_000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inspection_checklists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("process_id", sa.Integer(), sa.ForeignKey("processes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checklist_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(op.f("ix_inspection_checklists_id"), "inspection_checklists", ["id"], unique=False)
    op.create_unique_constraint("uq_inspection_checklists_process_id", "inspection_checklists", ["process_id"])


def downgrade() -> None:
    op.drop_constraint("uq_inspection_checklists_process_id", "inspection_checklists", type_="unique")
    op.drop_index(op.f("ix_inspection_checklists_id"), table_name="inspection_checklists")
    op.drop_table("inspection_checklists")
