"""mazzi: decks, deck_unlocks, readings.deck_id

Revision ID: b8f4d2a6e153
Revisione precedente: a7c3e91f4b02
Creata: 2026-10-02

Additiva (v5, Fase B1). Nasce `decks` (metadati commerciali di un mazzo: prezzo digitale/stampa/
fisico, finestra di attivazione stagionale, il flag `predefinito` per il Thoth), `deck_unlocks` (chi
possiede quale mazzo digitale) e `readings.deck_id` (quale mazzo è stato mostrato in una lettura,
nullo per il predefinito). L'artwork resta fuori dal database (file statici nel frontend) — qui solo
i metadati che decidono prezzo, visibilità e possesso.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b8f4d2a6e153'
down_revision: Union[str, None] = 'a7c3e91f4b02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'decks',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(length=40), nullable=False),
        sa.Column('nome', sa.String(length=80), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('predefinito', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('attivo', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('attivazione_da', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attivazione_fino', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prezzo_digitale', sa.Integer(), nullable=True),
        sa.Column('prezzo_stampa', sa.Integer(), nullable=True),
        sa.Column('prezzo_fisico', sa.Integer(), nullable=True),
        sa.Column('richiede_spedizione', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('valuta', sa.String(length=3), server_default='EUR', nullable=False),
        sa.Column('rank', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint(
            'attivazione_da is null or attivazione_fino is null or attivazione_da < attivazione_fino',
            name='ck_decks_finestra_attivazione',
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    op.create_table(
        'deck_unlocks',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('deck_id', sa.BigInteger(), nullable=False),
        sa.Column('acquired_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('riga_ordine_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'deck_id', name='uq_deck_unlocks_utente_mazzo'),
    )
    op.create_index('ix_deck_unlocks_user_id', 'deck_unlocks', ['user_id'])

    op.add_column('readings', sa.Column('deck_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        'fk_readings_deck_id', 'readings', 'decks', ['deck_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_readings_deck_id', 'readings', type_='foreignkey')
    op.drop_column('readings', 'deck_id')
    op.drop_index('ix_deck_unlocks_user_id', table_name='deck_unlocks')
    op.drop_table('deck_unlocks')
    op.drop_table('decks')
