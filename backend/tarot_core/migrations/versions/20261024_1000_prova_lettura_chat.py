"""La prova della lettura in chat (v9.5): la percentuale in console e la variante di ogni persona.

`impostazioni_intervista.chat_percentuale` (0–100, predefinito 90): quante persone, al primo arrivo su `/read`,
ricevono la lettura in chat. `users.variante_lettura`: la variante con cui una persona con account ha aperto la prima
lettura, perché resti la stessa su tutti i dispositivi.

Revision ID: b5d7f9a1c3e6
Revises: a4c6e8f0b2d5
Creata: 2026-10-06
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b5d7f9a1c3e6"
down_revision = "a4c6e8f0b2d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("impostazioni_intervista",
                  sa.Column("chat_percentuale", sa.Integer(), nullable=False, server_default="90"))
    op.create_check_constraint("ck_impostazioni_intervista_chat", "impostazioni_intervista",
                               "chat_percentuale >= 0 AND chat_percentuale <= 100")
    op.add_column("users", sa.Column("variante_lettura", sa.String(10), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "variante_lettura")
    op.drop_constraint("ck_impostazioni_intervista_chat", "impostazioni_intervista", type_="check")
    op.drop_column("impostazioni_intervista", "chat_percentuale")
