"""Oracolo: massimo di aperture automatiche per visita, dalla console (v8.5).

Revision ID: a9c3e5f7b1d2
Revises: f7ab5c9d4e2a
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a9c3e5f7b1d2"
down_revision = "f7ab5c9d4e2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "impostazioni_chat",
        sa.Column("proattiva_max_per_visita", sa.Integer(), nullable=False, server_default="3"),
    )


def downgrade() -> None:
    op.drop_column("impostazioni_chat", "proattiva_max_per_visita")
