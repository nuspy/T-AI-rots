"""Le app native (v9, Fase 3): configurazione degli store, prodotti degli store, politica del pulsante Stripe.

Revision ID: e5f7a9b1c3d6
Revises: b2d4f6a8c0e3

Additiva:

- `config_app_mobili`: una riga per piattaforma (`android`, `ios`) e una per gli appunti di Codemagic. Parametri in
  chiaro, segreti cifrati (Fernet, come le chiavi dei fornitori LLM), appunti del profilo pagamenti, esito
  dell'ultima verifica.
- `prodotti_store`: il prodotto dello store (`product_id`, unico per piattaforma) e il piano che accredita.
- `politica_stripe`: come l'app mostra il pulsante Stripe, per piattaforma e paese (`*` = tutti gli altri). Senza
  righe vale «nascosto».
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "e5f7a9b1c3d6"
down_revision = "b2d4f6a8c0e3"
branch_labels = None
depends_on = None


def _timestamp():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def _autore():
    return sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"))


def upgrade() -> None:
    op.create_table(
        "config_app_mobili",
        sa.Column("piattaforma", sa.String(10), primary_key=True),
        sa.Column("parametri", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("segreti", sa.LargeBinary()),
        sa.Column("appunti_pagamenti", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("verificato_il", sa.DateTime(timezone=True)),
        sa.Column("esito_verifica", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        _autore(),
        *_timestamp(),
        sa.CheckConstraint("piattaforma in ('android', 'ios', 'codemagic')", name="ck_config_app_mobili_piattaforma"),
    )
    op.create_table(
        "prodotti_store",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("piattaforma", sa.String(10), nullable=False),
        sa.Column("product_id", sa.String(150), nullable=False),
        sa.Column("plan_id", sa.BigInteger(), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("tipo", sa.String(12), nullable=False),
        sa.Column("attivo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("note", sa.String(500), nullable=False, server_default=""),
        _autore(),
        *_timestamp(),
        sa.UniqueConstraint("piattaforma", "product_id", name="uq_prodotti_store_piattaforma_prodotto"),
        sa.CheckConstraint("piattaforma in ('android', 'ios')", name="ck_prodotti_store_piattaforma"),
        sa.CheckConstraint("tipo in ('consumabile', 'abbonamento')", name="ck_prodotti_store_tipo"),
    )
    op.create_table(
        "politica_stripe",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("piattaforma", sa.String(10), nullable=False),
        sa.Column("paese", sa.String(2), nullable=False),
        sa.Column("modalita", sa.String(20), nullable=False, server_default="nascosto"),
        sa.Column("avviso", sa.String(500), nullable=False, server_default=""),
        _autore(),
        *_timestamp(),
        sa.UniqueConstraint("piattaforma", "paese", name="uq_politica_stripe_piattaforma_paese"),
        sa.CheckConstraint("piattaforma in ('android', 'ios')", name="ck_politica_stripe_piattaforma"),
        sa.CheckConstraint(
            "modalita in ('nascosto', 'link_esterno', 'entitlement_ue', 'scelta_utente')",
            name="ck_politica_stripe_modalita",
        ),
    )


def downgrade() -> None:
    op.drop_table("politica_stripe")
    op.drop_table("prodotti_store")
    op.drop_table("config_app_mobili")
