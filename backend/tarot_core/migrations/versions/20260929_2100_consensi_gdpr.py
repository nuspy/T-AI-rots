"""consensi_gdpr

Revision ID: 834c05b9257c
Revisione precedente: 5a476e0fae86
Creata: 2026-09-29

Additiva (v7, Fase G). `user_consents`: stato corrente del consenso cookie e del consenso alla
condivisione dati con i partner, per utente registrato o per `anon_id` (stesso schema di
`Reading.owner_id`/`Reading.anon_id`, v6 Fase F). Ogni scrittura ha anche un evento gemello in
`audit_log` (tabella già esistente, nessuna migrazione necessaria per quella) per la provenienza
completa (data, IP, ora) richiesta esplicitamente dall'operatore.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '834c05b9257c'
down_revision: Union[str, None] = '5a476e0fae86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_consents',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('anon_id', sa.String(length=64), nullable=True),
        sa.Column('tipo', sa.String(length=40), nullable=False),
        sa.Column('valore', sa.String(length=20), nullable=False),
        sa.Column('versione_informativa', sa.String(length=20), nullable=False),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'tipo', name='uq_user_consents_user_tipo'),
        sa.UniqueConstraint('anon_id', 'tipo', name='uq_user_consents_anon_tipo'),
        sa.CheckConstraint('(user_id is not null) or (anon_id is not null)', name='ck_user_consents_owner'),
        sa.CheckConstraint("tipo in ('cookie', 'condivisione_dati_partner')", name='ck_user_consents_tipo'),
        sa.CheckConstraint("valore in ('accettato', 'rifiutato')", name='ck_user_consents_valore'),
    )
    op.create_index('ix_user_consents_anon_id', 'user_consents', ['anon_id'])


def downgrade() -> None:
    op.drop_index('ix_user_consents_anon_id', table_name='user_consents')
    op.drop_table('user_consents')
