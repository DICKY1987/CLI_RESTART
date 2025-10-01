"""Workstream registry

Revision ID: 002_workstream_registry
Revises: 001_initial_schema
Create Date: 2025-10-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "002_workstream_registry"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workstreams",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("correlation_id", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_workstreams_status", "workstreams", ["status"]) 
    op.create_index("ix_workstreams_created_at", "workstreams", ["created_at"]) 


def downgrade() -> None:
    op.drop_index("ix_workstreams_created_at", table_name="workstreams")
    op.drop_index("ix_workstreams_status", table_name="workstreams")
    op.drop_table("workstreams")

