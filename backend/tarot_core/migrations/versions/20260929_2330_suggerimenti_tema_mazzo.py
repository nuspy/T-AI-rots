"""suggerimenti_tema_mazzo

Revision ID: 94c558e43bd6
Revisione precedente: cea0131661de
Creata: 2026-09-29

Additiva (v7, Fase K, estensione "suggerisci tema mazzo"). `deck_suggestions`: un iscritto propone
liberamente un tema in testo libero; l'admin lo rivede in console e, se lo trasforma in una proposta
vera, il suggerimento porta il riferimento al `DeckCandidate` risultante.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '94c558e43bd6'
down_revision: Union[str, None] = 'cea0131661de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'deck_suggestions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('testo', sa.String(length=1000), nullable=False),
        sa.Column('stato', sa.String(length=20), nullable=False, server_default='nuovo'),
        sa.Column('candidate_id', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['candidate_id'], ['deck_candidates.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("stato in ('nuovo', 'usato', 'scartato')", name='ck_deck_suggestions_stato'),
    )
    op.create_index('ix_deck_suggestions_user_id', 'deck_suggestions', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_deck_suggestions_user_id', table_name='deck_suggestions')
    op.drop_table('deck_suggestions')
