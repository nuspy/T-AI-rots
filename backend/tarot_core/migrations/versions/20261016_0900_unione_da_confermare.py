"""L'unione degli account da confermare.

Revision ID: d3f6b8c0e2a5
Revises: c2e5a7b9d1f4

Additiva, due colonne facoltative su `users`:

- `unione_in_attesa`: Keycloak ha collegato un social a un account con l'email mai verificata e gli ha tolto i vecchi
  accessi (passo `tarots-unione-sicura`); il sito chiede alla persona se quell'account era suo
  (`tarot/unione_account.py`).
- `unione_risolta`: l'id dell'ultima domanda a cui ha risposto, perché la nota resta nei token di tutta la sessione.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d3f6b8c0e2a5"
down_revision = "c2e5a7b9d1f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("unione_in_attesa", postgresql.JSONB(), nullable=True))
    op.add_column("users", sa.Column("unione_risolta", sa.String(40), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "unione_risolta")
    op.drop_column("users", "unione_in_attesa")
