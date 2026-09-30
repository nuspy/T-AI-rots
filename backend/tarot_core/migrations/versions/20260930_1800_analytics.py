"""analytics

Revision ID: 2556daf22909
Revisione precedente: 545b3689315b
Creata: 2026-09-30

Additiva (v8). Le tabelle `an_*` della libreria `lanterna`: sali giornalieri, sessioni, eventi,
attribuzione degli utenti, riepilogo giornaliero, impostazioni. Lo schema è quello congelato della
versione 1 della libreria: una sua modifica futura arriverà con una revisione nuova (`crea_v2`...).
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from lanterna.migrazioni import crea_v1, elimina_v1

revision: str = '2556daf22909'
down_revision: Union[str, None] = '545b3689315b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    crea_v1(op, prefisso="an_", fk_utenti="users.id")


def downgrade() -> None:
    elimina_v1(op, prefisso="an_", fk_utenti="users.id")
