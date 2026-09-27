"""indirizzi_spedizione, ordini.indirizzo_spedizione

Revision ID: a7f1e4c9b230
Revisione precedente: d5a9c3f7b862
Creata: 2026-10-05

Additiva (v5, Fase B5). Nasce `indirizzi_spedizione` (il profilo può averne più di uno, uno solo
predefinito) e `ordini.indirizzo_spedizione` — una copia JSON dei campi dell'indirizzo scelto al
checkout, presa al momento dell'ordine: `indirizzo_spedizione_id` (già in `ordini` dalla migrazione
di B3) resta solo un riferimento di comodo, senza vincolo di chiave esterna — un indirizzo poi
corretto o cancellato non deve riscrivere la storia di un ordine già fatto.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a7f1e4c9b230'
down_revision: Union[str, None] = 'd5a9c3f7b862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'indirizzi_spedizione',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('via', sa.String(length=200), nullable=False),
        sa.Column('citta', sa.String(length=120), nullable=False),
        sa.Column('cap', sa.String(length=20), nullable=False),
        sa.Column('provincia', sa.String(length=80), nullable=True),
        sa.Column('paese', sa.String(length=2), nullable=False),
        sa.Column('telefono', sa.String(length=30), nullable=True),
        sa.Column('predefinito', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_indirizzi_spedizione_user_id', 'indirizzi_spedizione', ['user_id'])

    op.add_column('ordini', sa.Column('indirizzo_spedizione', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('ordini', 'indirizzo_spedizione')
    op.drop_index('ix_indirizzi_spedizione_user_id', table_name='indirizzi_spedizione')
    op.drop_table('indirizzi_spedizione')
