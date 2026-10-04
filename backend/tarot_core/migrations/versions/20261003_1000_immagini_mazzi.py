"""immagini dei mazzi nel database

Revision ID: c4d8a2f6e1b7
Revisione precedente: b2e7c4a19d05
Creata: 2026-10-03

Additiva. `deck_card_images`: le 78 carte e il dorso di un mazzo caricati dalla console (uno ZIP o una cartella),
già convertiti in WebP alla misura web e serviti dall'API (`GET /decks/{slug}/cards/{id}.webp`) — un mazzo nuovo
non richiede più di ricostruire l'immagine del sito. `bozza` distingue i file di un caricamento a più passi ancora
in corso (la cartella, un file per richiesta) da quelli pubblicati: il sito vede soltanto i secondi.
`decks.immagini_versione`: l'impronta dell'ultima serie pubblicata (vuota = il mazzo usa i file del sito).
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'c4d8a2f6e1b7'
down_revision: Union[str, None] = 'b2e7c4a19d05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('decks', sa.Column('immagini_versione', sa.String(length=16), nullable=True))
    op.create_table(
        'deck_card_images',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('deck_id', sa.BigInteger(), nullable=False),
        sa.Column('card_id', sa.String(length=20), nullable=False),
        sa.Column('bozza', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('webp', sa.LargeBinary(), nullable=False),
        sa.Column('larghezza', sa.Integer(), nullable=False),
        sa.Column('altezza', sa.Integer(), nullable=False),
        sa.Column('etag', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('deck_id', 'card_id', 'bozza', name='uq_deck_card_images_carta'),
    )


def downgrade() -> None:
    op.drop_table('deck_card_images')
    op.drop_column('decks', 'immagini_versione')
