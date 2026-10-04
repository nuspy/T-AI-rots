"""Impostazioni dell'intervista: minimo e massimo di domande dalla console (v8.5).

Revision ID: f7ab5c9d4e2a
Revises: d5e9b3a7f2c8
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f7ab5c9d4e2a"
down_revision = "d5e9b3a7f2c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "impostazioni_intervista",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("min_domande", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("max_domande", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="ck_impostazioni_intervista_singleton"),
        sa.CheckConstraint(
            "min_domande >= 1 AND max_domande >= min_domande AND max_domande <= 12",
            name="ck_impostazioni_intervista_limiti",
        ),
    )


def downgrade() -> None:
    op.drop_table("impostazioni_intervista")
