"""Variante e piattaforma di ogni lettura (v9.5).

La prova della lettura in chat (90%) contro quella classica (10%) si confronta anche sul database delle letture, che
vale per tutti (non solo per chi accetta le statistiche): ogni lettura dice con quale versione è nata e da dove.
Nulle per le letture di prima.

Revision ID: a4c6e8f0b2d5
Revises: f3b5c7d9e1a4
Creata: 2026-10-06
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a4c6e8f0b2d5"
down_revision = "f3b5c7d9e1a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("readings", sa.Column("variante", sa.String(10), nullable=True))
    op.add_column("readings", sa.Column("piattaforma", sa.String(10), nullable=True))


def downgrade() -> None:
    op.drop_column("readings", "piattaforma")
    op.drop_column("readings", "variante")
