"""condivisione: testo, clic, visite, immagini, iscrizioni dal link, premi

Revision ID: 8c4f2a7d1e93
Revisione precedente: 5b1e7c3a9d42
Creata: 2026-09-26

Additiva: colonne nulle o con default su `readings` e `users`, e quattro tabelle
nuove. Un backend vecchio le ignora.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '8c4f2a7d1e93'
down_revision: Union[str, None] = '5b1e7c3a9d42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('readings', sa.Column('share_text', sa.String(length=200), nullable=True))
    op.add_column('readings', sa.Column('share_clicked_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('readings', sa.Column('share_verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('share_rewards', sa.Integer(), server_default='0', nullable=False))

    op.create_table(
        'share_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('reading_id', sa.Uuid(), nullable=False),
        sa.Column('canale', sa.String(length=20), nullable=False),
        sa.Column('visitor', sa.String(length=64), nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['reading_id'], ['readings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_share_events_reading_id'), 'share_events', ['reading_id'], unique=False)

    op.create_table(
        'share_visits',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('reading_id', sa.Uuid(), nullable=False),
        sa.Column('visitor', sa.String(length=64), nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['reading_id'], ['readings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reading_id', 'visitor', name='uq_share_visits_reading_visitor'),
    )
    op.create_index(op.f('ix_share_visits_reading_id'), 'share_visits', ['reading_id'], unique=False)

    op.create_table(
        'share_images',
        sa.Column('reading_id', sa.Uuid(), nullable=False),
        sa.Column('webp', sa.LargeBinary(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['reading_id'], ['readings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('reading_id'),
    )

    op.create_table(
        'share_signups',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('sharer_id', sa.BigInteger(), nullable=False),
        sa.Column('new_user_id', sa.BigInteger(), nullable=False),
        sa.Column('reading_id', sa.Uuid(), nullable=True),
        sa.Column('crediti', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['new_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reading_id'], ['readings.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sharer_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('new_user_id'),
    )
    op.create_index(op.f('ix_share_signups_sharer_id'), 'share_signups', ['sharer_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_share_signups_sharer_id'), table_name='share_signups')
    op.drop_table('share_signups')
    op.drop_table('share_images')
    op.drop_index(op.f('ix_share_visits_reading_id'), table_name='share_visits')
    op.drop_table('share_visits')
    op.drop_index(op.f('ix_share_events_reading_id'), table_name='share_events')
    op.drop_table('share_events')
    op.drop_column('users', 'share_rewards')
    op.drop_column('readings', 'share_verified_at')
    op.drop_column('readings', 'share_clicked_at')
    op.drop_column('readings', 'share_text')
