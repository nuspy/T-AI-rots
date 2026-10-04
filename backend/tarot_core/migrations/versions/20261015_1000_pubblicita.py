"""Gli spazi pubblicitari: impostazioni generali, parametri per fornitore, e il consenso alla pubblicità.

Revision ID: c2e5a7b9d1f4
Revises: b1d4f6a8c2e3

Additiva:

- `impostazioni_pubblicita`: una riga sola (interruttore generale, spento per default; quale fornitore riempie gli
  spazi; le caselle dei tre banner; le pagine escluse).
- `pubblicita_fornitori`: una riga per fornitore (oggi `google`): i parametri che il sito legge e i dati
  dell'iscrizione, che restano della console.
- `user_consents.tipo` ammette anche `pubblicita`: il consenso agli annunci è distinto da quello ai cookie.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "c2e5a7b9d1f4"
down_revision = "b1d4f6a8c2e3"
branch_labels = None
depends_on = None


def _timestamp():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "impostazioni_pubblicita",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attiva", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("fornitore", sa.String(40), nullable=False, server_default="google"),
        sa.Column("posizioni", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("pagine_escluse", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        *_timestamp(),
        sa.CheckConstraint("id = 1", name="ck_impostazioni_pubblicita_singleton"),
    )
    op.create_table(
        "pubblicita_fornitori",
        sa.Column("fornitore", sa.String(40), primary_key=True),
        sa.Column("parametri", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("registrazione", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        *_timestamp(),
    )
    op.drop_constraint("ck_user_consents_tipo", "user_consents", type_="check")
    op.create_check_constraint(
        "ck_user_consents_tipo", "user_consents", "tipo in ('cookie', 'condivisione_dati_partner', 'pubblicita')",
    )


def downgrade() -> None:
    op.execute("DELETE FROM user_consents WHERE tipo = 'pubblicita'")
    op.drop_constraint("ck_user_consents_tipo", "user_consents", type_="check")
    op.create_check_constraint(
        "ck_user_consents_tipo", "user_consents", "tipo in ('cookie', 'condivisione_dati_partner')",
    )
    op.drop_table("pubblicita_fornitori")
    op.drop_table("impostazioni_pubblicita")
