"""upload_artwork_mazzo

Revision ID: 36328fd967b7
Revisione precedente: 834c05b9257c
Creata: 2026-09-29

Additiva (v7, Fase I). `deck_artwork_uploads`: staging temporaneo per l'upload di un mazzo da GUI
admin — un blob ZIP già validato (nomi corretti, tutte le carte presenti), scaricato con sessione
autenticata ed estratto a mano nel repository prima del prossimo rilascio del frontend. Non sostituisce
il modello di storage dell'artwork finale (file statici nell'immagine, deciso con l'operatore).
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '36328fd967b7'
down_revision: Union[str, None] = '834c05b9257c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'deck_artwork_uploads',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('slug', sa.String(length=40), nullable=False),
        sa.Column('zip_bytes', sa.LargeBinary(), nullable=False),
        sa.Column('file_count', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_deck_artwork_uploads_slug', 'deck_artwork_uploads', ['slug'])


def downgrade() -> None:
    op.drop_index('ix_deck_artwork_uploads_slug', table_name='deck_artwork_uploads')
    op.drop_table('deck_artwork_uploads')
