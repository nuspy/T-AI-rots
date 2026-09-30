"""il Thoth sempre in catalogo

Revision ID: 7b2d9e4f1c63
Revisione precedente: 3e7a9c1d5b20
Creata: 2026-10-01

Solo dati (v8.5). Il mazzo predefinito lo creava `tools/seed.py`, che in produzione non è più stato lanciato dopo
l'arrivo dei mazzi: il negozio restava vuoto («per ora c'è solo il Thoth»). Qui la riga nasce se manca, senza prezzi
(PDF e scatola fisica si prezzano dalla console, Mazzi); se esiste già non si tocca. Il ritorno indietro non la
cancella: potrebbe avere ordini e prezzi.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = '7b2d9e4f1c63'
down_revision: Union[str, None] = '3e7a9c1d5b20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO decks (slug, nome, predefinito, attivo, rank, valuta, richiede_spedizione, created_at, updated_at)
        SELECT 'thoth', 'Thoth Tarot', true, true, 0, 'EUR', false, now(), now()
        WHERE NOT EXISTS (SELECT 1 FROM decks WHERE predefinito)
          AND NOT EXISTS (SELECT 1 FROM decks WHERE slug = 'thoth')
        """
    )


def downgrade() -> None:
    pass
