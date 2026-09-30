"""voto_mazzo

Revision ID: 59cecc660692
Revisione precedente: ba2543e3657b
Creata: 2026-09-29

Additiva (v7, Fase K). `voting_rounds` (tornate), `deck_candidates` (mazzi candidati, con le carte
di prova come JSONB di riferimenti a `media_images`), `deck_votes` (un voto per utente per tornata,
vincolo di unicità — un nuovo voto sostituisce il precedente, mai sommato). Estende il vincolo
`ck_media_images_uso` per ammettere `'voto'`: le carte di prova riusano lo stesso schema blob già
in produzione per le immagini del blog, servite dallo stesso endpoint `GET /blog/media/{id}.webp`
(che non filtra per `uso`).
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '59cecc660692'
down_revision: Union[str, None] = 'ba2543e3657b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('ck_media_images_uso', 'media_images', type_='check')
    op.create_check_constraint(
        'ck_media_images_uso', 'media_images', "uso in ('blog', 'avatar', 'voto')",
    )

    op.create_table(
        'voting_rounds',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('stato', sa.String(length=20), nullable=False, server_default='aperta'),
        sa.Column('chiusa_il', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("stato in ('aperta', 'chiusa')", name='ck_voting_rounds_stato'),
    )

    op.create_table(
        'deck_candidates',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('round_id', sa.Uuid(), nullable=False),
        sa.Column('nome', sa.String(length=80), nullable=False),
        sa.Column('descrizione', sa.String(length=2000), nullable=True),
        sa.Column('campioni', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('accettato', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('deck_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['round_id'], ['voting_rounds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_deck_candidates_round_id', 'deck_candidates', ['round_id'])

    op.create_table(
        'deck_votes',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('round_id', sa.Uuid(), nullable=False),
        sa.Column('candidate_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['round_id'], ['voting_rounds.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['candidate_id'], ['deck_candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('round_id', 'user_id', name='uq_deck_votes_round_user'),
    )


def downgrade() -> None:
    op.drop_table('deck_votes')
    op.drop_index('ix_deck_candidates_round_id', table_name='deck_candidates')
    op.drop_table('deck_candidates')
    op.drop_table('voting_rounds')
    op.drop_constraint('ck_media_images_uso', 'media_images', type_='check')
    op.create_check_constraint(
        'ck_media_images_uso', 'media_images', "uso in ('blog', 'avatar')",
    )
