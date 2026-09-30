"""piani e mazzi nelle lingue del sito

Revision ID: b2e7c4a19d05
Revisione precedente: 9a4c2e7b1f38
Creata: 2026-10-01

Additiva (v8.5). Nome e descrizione per lingua di piani e mazzi (`nomi`, `descrizioni`: lingua → testo). Per il
catalogo iniziale (i sei piani, il Thoth) le traduzioni si scrivono qui, solo dove mancano: una traduzione già
scritta in console non si tocca. I testi stanno in `billing/lingue.py`, gli stessi che usa il seed.
"""
from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = 'b2e7c4a19d05'
down_revision: Union[str, None] = '9a4c2e7b1f38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _colonne(tabella: str) -> None:
    for nome in ("nomi", "descrizioni"):
        op.add_column(tabella, sa.Column(
            nome, postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb"),
        ))


def upgrade() -> None:
    from tarot_core.billing.lingue import TRADUZIONI_MAZZI, TRADUZIONI_PIANI

    _colonne("plans")
    _colonne("decks")
    conn = op.get_bind()
    for tabella, traduzioni in (("plans", TRADUZIONI_PIANI), ("decks", TRADUZIONI_MAZZI)):
        for slug, t in traduzioni.items():
            conn.execute(
                sa.text(
                    f"UPDATE {tabella} SET nomi = CAST(:nomi AS jsonb), descrizioni = CAST(:descrizioni AS jsonb) "
                    "WHERE slug = :slug AND nomi = '{}'::jsonb AND descrizioni = '{}'::jsonb"
                ),
                {"slug": slug, "nomi": json.dumps(t["nomi"]), "descrizioni": json.dumps(t["descrizioni"])},
            )


def downgrade() -> None:
    for tabella in ("decks", "plans"):
        op.drop_column(tabella, "descrizioni")
        op.drop_column(tabella, "nomi")
