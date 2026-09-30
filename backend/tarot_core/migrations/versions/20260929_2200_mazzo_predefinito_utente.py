"""mazzo_predefinito_utente

Revision ID: ba2543e3657b
Revisione precedente: 36328fd967b7
Creata: 2026-09-29

Additiva (v7, Fase J). `users.mazzo_predefinito_id`: il mazzo scelto come default per le nuove
letture. `NULL` (default) = il mazzo predefinito globale (`Deck.predefinito`), comportamento
identico a prima di v7.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'ba2543e3657b'
down_revision: Union[str, None] = '36328fd967b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('mazzo_predefinito_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        'fk_users_mazzo_predefinito_id', 'users', 'decks',
        ['mazzo_predefinito_id'], ['id'], ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_mazzo_predefinito_id', 'users', type_='foreignkey')
    op.drop_column('users', 'mazzo_predefinito_id')
