"""L'accesso dalle app (v9, Fase 6).

Revision ID: e3a5c7e9b1d4
Revises: d2f4b6c8e0a3

- `config_accesso_apple`: Team ID, Key ID, Services ID e la chiave «Sign in with Apple» (cifrata) con cui il backend
  firma il segreto dell'identity provider `apple` di Keycloak; scadenza del segreto in uso ed esito dell'ultima
  scrittura.
- `codici_collegamento`: i codici monouso che spostano le identità social da un account nato nell'app a quello che la
  persona aveva già (solo l'impronta del codice).

Nessun dato da convertire. Indietro: le due tabelle spariscono (la chiave .p8 va ricaricata dalla console; il segreto
già scritto in Keycloak resta valido fino alla sua scadenza).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "e3a5c7e9b1d4"
down_revision = "d2f4b6c8e0a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "config_accesso_apple",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.String(10), nullable=False, server_default=""),
        sa.Column("key_id", sa.String(10), nullable=False, server_default=""),
        sa.Column("services_id", sa.String(150), nullable=False, server_default=""),
        sa.Column("chiave_cifrata", sa.LargeBinary()),
        sa.Column("segreto_generato_il", sa.DateTime(timezone=True)),
        sa.Column("segreto_scade_il", sa.DateTime(timezone=True)),
        sa.Column("esito", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="ck_config_accesso_apple_singleton"),
    )

    op.create_table(
        "codici_collegamento",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("impronta", sa.String(64), nullable=False),
        sa.Column("creato_il", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("scade_il", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usato_il", sa.DateTime(timezone=True)),
        sa.Column("usato_da", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.UniqueConstraint("impronta", name="codici_collegamento_impronta_key"),
    )
    op.create_index("ix_codici_collegamento_user_id", "codici_collegamento", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_codici_collegamento_user_id", table_name="codici_collegamento")
    op.drop_table("codici_collegamento")
    op.drop_table("config_accesso_apple")
