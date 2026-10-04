"""Profilo dai social e posizione attuale (accesso unificato).

Revision ID: b1d4f6a8c2e3
Revises: a9c3e5f7b1d2

Additiva, tutte colonne facoltative o con default su `users`:

- `nome`, `cognome`: la scheda anagrafica. Nascono vuoti; li riempie chi si iscrive o, se vuoti, i dati del social
  con cui entra (`POST /me/profilo-social`).
- `posizione_*`: dove si trova la persona *adesso* (paese e città, dal social o dall'IP all'accesso), separata
  dagli indirizzi che compila lei.
- `dati_social`: la provenienza dei campi compilati da un social (quale provider, quando), per la scheda e per la
  console.
- `importa_social`, `rileva_posizione`: le due scelte della persona (dal profilo), accese di partenza.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "b1d4f6a8c2e3"
down_revision = "a9c3e5f7b1d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("nome", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("cognome", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("posizione_paese", sa.String(2), nullable=True))
    op.add_column("users", sa.Column("posizione_citta", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("posizione_fonte", sa.String(20), nullable=True))
    op.add_column("users", sa.Column("posizione_il", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("dati_social", postgresql.JSONB(), nullable=True))
    op.add_column("users", sa.Column("importa_social", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column("users", sa.Column("rileva_posizione", sa.Boolean(), server_default=sa.true(), nullable=False))


def downgrade() -> None:
    for colonna in (
        "rileva_posizione", "importa_social", "dati_social", "posizione_il", "posizione_fonte",
        "posizione_citta", "posizione_paese", "cognome", "nome",
    ):
        op.drop_column("users", colonna)
