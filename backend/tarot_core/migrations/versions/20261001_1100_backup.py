"""backup sul NAS

Revision ID: 5c8e1f3a9d24
Revisione precedente: 7b2d9e4f1c63
Creata: 2026-10-01

Additiva (v8.3). La destinazione del backup notturno (una riga, scelta dalla console; la credenziale sta in un
Secret, non qui) e il registro delle esecuzioni: backup, copie di sicurezza, ripristini, prove.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '5c8e1f3a9d24'
down_revision: Union[str, None] = '7b2d9e4f1c63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'impostazioni_backup',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('attivo', sa.Boolean(), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('porta', sa.Integer(), nullable=False),
        sa.Column('utente', sa.String(length=120), nullable=False),
        sa.Column('cartella', sa.String(length=500), nullable=False),
        sa.Column('conserva', sa.Integer(), nullable=False),
        sa.Column('impronta_host', sa.String(length=120), nullable=True),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('id = 1', name='ck_impostazioni_backup_singleton'),
        sa.CheckConstraint('conserva between 1 and 60', name='ck_impostazioni_backup_conserva'),
        sa.CheckConstraint('porta between 1 and 65535', name='ck_impostazioni_backup_porta'),
    )
    op.create_table(
        'backup_esecuzioni',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('tipo', sa.String(length=12), nullable=False),
        sa.Column('manuale', sa.Boolean(), nullable=False),
        sa.Column('esito', sa.String(length=10), nullable=False),
        sa.Column('file', sa.String(length=255), nullable=True),
        sa.Column('byte', sa.BigInteger(), nullable=True),
        sa.Column('sha256', sa.String(length=64), nullable=True),
        sa.Column('durata_secondi', sa.Integer(), nullable=True),
        sa.Column('eliminati', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('dettaglio', sa.Text(), nullable=True),
        sa.Column('finita_il', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actor_id', sa.BigInteger(), nullable=True),
        sa.Column('extra', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("tipo in ('backup', 'sicurezza', 'ripristino', 'prova')", name='ck_backup_esecuzioni_tipo'),
        sa.CheckConstraint("esito in ('in_corso', 'ok', 'errore', 'saltato')", name='ck_backup_esecuzioni_esito'),
    )
    op.create_index('ix_backup_esecuzioni_created_at', 'backup_esecuzioni', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_backup_esecuzioni_created_at', table_name='backup_esecuzioni')
    op.drop_table('backup_esecuzioni')
    op.drop_table('impostazioni_backup')
