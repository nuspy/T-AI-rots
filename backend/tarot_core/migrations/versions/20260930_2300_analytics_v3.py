"""analytics v3

Revision ID: 9d4b2f7e1a55
Revisione precedente: 7c1e4a9b2d30
Creata: 2026-09-30

Additiva (v8). Le tabelle v3 di `lanterna`: annotazioni sul calendario (campagne, rilasci…) e
obiettivi di conversione configurabili dalla console.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from lanterna.migrazioni import crea_v3, elimina_v3

revision: str = '9d4b2f7e1a55'
down_revision: Union[str, None] = '7c1e4a9b2d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    crea_v3(op, prefisso="an_", fk_utenti="users.id")


def downgrade() -> None:
    elimina_v3(op, prefisso="an_", fk_utenti="users.id")
