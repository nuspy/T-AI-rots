"""analytics v2

Revision ID: 7c1e4a9b2d30
Revisione precedente: 2556daf22909
Creata: 2026-09-30

Additiva (v8). Le tabelle v2 di `lanterna`: storico delle analisi AI con giudizi, destinatari e
registro dei rapporti email, token di export per Colab e risultati importati.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from lanterna.migrazioni import crea_v2, elimina_v2

revision: str = '7c1e4a9b2d30'
down_revision: Union[str, None] = '2556daf22909'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    crea_v2(op, prefisso="an_", fk_utenti="users.id")


def downgrade() -> None:
    elimina_v2(op, prefisso="an_", fk_utenti="users.id")
