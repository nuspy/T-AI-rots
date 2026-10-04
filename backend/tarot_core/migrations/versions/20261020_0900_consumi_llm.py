"""I consumi delle chiamate ai modelli e i listini della pagina «Costi».

Revision ID: a5c7e9b1d3f6
Revises: e3a5c7e9b1d4

- `llm_consumi`: una riga per chiamata HTTP a un modello (compito, fase, token in ingresso, in cache, in uscita e di
  ragionamento, durata, esito, lettura). La scrive `llm/consumi.py` in background, anche in produzione.
- `llm_listini`: i prezzi dei fornitori (dollari per milione di token) e la quota di cache stimata, modificabili dalla
  console. Si parte con Nebius (il fornitore in uso), Darkbloom e DeepInfra.

Nessun dato da convertire. Indietro: le due tabelle spariscono, con lo storico dei consumi.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a5c7e9b1d3f6"
down_revision = "e3a5c7e9b1d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "llm_consumi",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("compito", sa.String(40), nullable=False, server_default=""),
        sa.Column("fase", sa.String(40), nullable=False, server_default=""),
        sa.Column("fornitore", sa.String(80), nullable=False, server_default=""),
        sa.Column("modello", sa.String(160), nullable=False, server_default=""),
        sa.Column("token_ingresso", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("token_cache", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("token_uscita", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("token_ragionamento", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("caratteri_ingresso", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("caratteri_uscita", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("caratteri_ragionamento", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("caratteri_sistema", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_tokens", sa.Integer()),
        sa.Column("durata_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("esito", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("finish_reason", sa.String(20), nullable=False, server_default=""),
        sa.Column("streaming", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("usage_riportato", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reading_id", sa.Uuid()),
        sa.Column("riferimento", sa.String(80), nullable=False, server_default=""),
        sa.Column("errore", sa.String(300), nullable=False, server_default=""),
    )
    op.create_index("ix_llm_consumi_created_at", "llm_consumi", ["created_at"])
    op.create_index("ix_llm_consumi_reading_id", "llm_consumi", ["reading_id"])
    op.create_index("ix_llm_consumi_compito_created", "llm_consumi", ["compito", "created_at"])

    listini = op.create_table(
        "llm_listini",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(60), nullable=False),
        sa.Column("prezzo_ingresso", sa.Numeric(10, 4), nullable=False, server_default="0"),
        sa.Column("prezzo_cache", sa.Numeric(10, 4), nullable=False, server_default="0"),
        sa.Column("prezzo_uscita", sa.Numeric(10, 4), nullable=False, server_default="0"),
        sa.Column("cache_hit", sa.Numeric(5, 4), nullable=False, server_default="0"),
        sa.Column("attuale", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("nota", sa.String(300), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("nome", name="llm_listini_nome_key"),
    )
    op.bulk_insert(listini, [
        {
            "nome": "Nebius (in uso)", "prezzo_ingresso": 0.06, "prezzo_cache": 0.06, "prezzo_uscita": 0.24,
            "cache_hit": 0, "attuale": True,
            "nota": "Token Factory, nvidia/Nemotron-3_5-Lightning: listino pubblico, sconto cache da verificare",
        },
        {
            "nome": "Darkbloom", "prezzo_ingresso": 0.039, "prezzo_cache": 0.019, "prezzo_uscita": 0.18,
            "cache_hit": 0.70, "attuale": False, "nota": "cache hit stimato 70%",
        },
        {
            "nome": "DeepInfra", "prezzo_ingresso": 0.06, "prezzo_cache": 0.03, "prezzo_uscita": 0.16,
            "cache_hit": 0.90, "attuale": False, "nota": "cache hit stimato 90%",
        },
    ])


def downgrade() -> None:
    op.drop_table("llm_listini")
    op.drop_index("ix_llm_consumi_compito_created", table_name="llm_consumi")
    op.drop_index("ix_llm_consumi_reading_id", table_name="llm_consumi")
    op.drop_index("ix_llm_consumi_created_at", table_name="llm_consumi")
    op.drop_table("llm_consumi")
