"""Initial schema baseline

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-10-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "schema_info",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("notes", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("schema_info")

