"""impostazioni_chat, chat_proattiva_turni

Revision ID: c7e1a5d834f0
Revisione precedente: b6d4f9a2c831
Creata: 2026-10-08

Additiva (v6, Fase E). `impostazioni_chat` è il singleton con il timer di inattività (come
`impostazioni_crediti`). `chat_proattiva_turni` è la trascrizione della chat proattiva, per
utente e non per lettura: nessuna FK verso `readings`, perché la conversazione esiste
indipendentemente da una lettura specifica.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c7e1a5d834f0'
down_revision: Union[str, None] = 'b6d4f9a2c831'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'impostazioni_chat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('proattiva_minuti_inattivita', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('id = 1', name='ck_impostazioni_chat_singleton'),
    )

    op.create_table(
        'chat_proattiva_turni',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('ordine', sa.Integer(), nullable=False),
        sa.Column('ruolo', sa.String(length=10), nullable=False),
        sa.Column('testo', sa.Text(), nullable=False),
        sa.Column('proposta', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("ruolo IN ('ai', 'utente')", name='ck_chat_proattiva_turni_ruolo'),
    )
    op.create_index(
        'ix_chat_proattiva_turni_owner_ordine', 'chat_proattiva_turni', ['owner_id', 'ordine'],
    )


def downgrade() -> None:
    op.drop_index('ix_chat_proattiva_turni_owner_ordine', table_name='chat_proattiva_turni')
    op.drop_table('chat_proattiva_turni')
    op.drop_table('impostazioni_chat')
