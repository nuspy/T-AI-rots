"""impostazioni dei crediti: iscrizione, referral, commissione

Revision ID: e2b6a917c5d4
Revisione precedente: d9a3f6c1b284
Creata: 2026-09-27

Additiva. Nasce `impostazioni_crediti`, una riga sola (vincolo `id = 1`): quanti crediti regala l'iscrizione,
quanti il riscatto di un codice d'invito (il totale per l'invitato, non un extra), e la percentuale di commissione
che chi ha invitato riceve su ogni acquisto futuro dell'invitato. Un backend vecchio, senza questa tabella, ricade
sulle vecchie impostazioni d'ambiente (`TAROT_CREDITI_INVITO`) e non regala nulla all'iscrizione, come già faceva.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e2b6a917c5d4'
down_revision: Union[str, None] = 'd9a3f6c1b284'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'impostazioni_crediti',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crediti_iscrizione', sa.Integer(), server_default=sa.text('3'), nullable=False),
        sa.Column('crediti_invito', sa.Integer(), server_default=sa.text('5'), nullable=False),
        sa.Column('commissione_referral_percentuale', sa.Integer(), server_default=sa.text('20'), nullable=False),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('id = 1', name='ck_impostazioni_crediti_singleton'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('impostazioni_crediti')
