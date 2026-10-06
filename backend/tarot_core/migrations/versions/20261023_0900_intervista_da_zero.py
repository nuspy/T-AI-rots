"""Intervista più corta (v9.5): il minimo di domande può essere 0, e da 2–6 si passa a 0–2.

I dati di produzione (6/10/2026: 15 letture su 26 ferme nell'intervista, 9 senza nessuna risposta, quasi tutte davanti
alla prima domanda) hanno portato l'operatore ad accorciarla: con il minimo a 0 chi consulta può passare alle carte fin
dalla prima domanda. Il cambio dei valori vale solo se sono ancora quelli predefiniti (2 e 6): una scelta fatta in
console non si tocca.

Revision ID: f3b5c7d9e1a4
Revises: e2a4b6c8d0f3
Creata: 2026-10-06
"""
from __future__ import annotations

from alembic import op

revision = "f3b5c7d9e1a4"
down_revision = "e2a4b6c8d0f3"
branch_labels = None
depends_on = None

VINCOLO = "ck_impostazioni_intervista_limiti"


def upgrade() -> None:
    op.drop_constraint(VINCOLO, "impostazioni_intervista", type_="check")
    op.create_check_constraint(
        VINCOLO, "impostazioni_intervista",
        "min_domande >= 0 AND max_domande >= 1 AND max_domande >= min_domande AND max_domande <= 12",
    )
    op.alter_column("impostazioni_intervista", "min_domande", server_default="0")
    op.alter_column("impostazioni_intervista", "max_domande", server_default="2")
    op.execute("UPDATE impostazioni_intervista SET min_domande = 0, max_domande = 2 WHERE min_domande = 2 AND max_domande = 6")


def downgrade() -> None:
    op.execute("UPDATE impostazioni_intervista SET min_domande = 1 WHERE min_domande = 0")
    op.drop_constraint(VINCOLO, "impostazioni_intervista", type_="check")
    op.create_check_constraint(
        VINCOLO, "impostazioni_intervista", "min_domande >= 1 AND max_domande >= min_domande AND max_domande <= 12",
    )
    op.alter_column("impostazioni_intervista", "min_domande", server_default="2")
    op.alter_column("impostazioni_intervista", "max_domande", server_default="6")
