"""offerte_mazzo: sconto a tempo per mazzo

Revision ID: c2e6f8a1d374
Revisione precedente: b8f4d2a6e153
Creata: 2026-10-03

Additiva (v5, Fase B2). Nasce `offerte_mazzo`: uno sconto a tempo sul prezzo digitale di un mazzo,
con `deck_id` come chiave primaria (un solo sconto attivo per mazzo alla volta, sostituito con un
`PUT` — non un codice da riscattare come `Coupon`). Nessuna scadenza pianificata: il confronto con
`now()` avviene a ogni lettura del prezzo (`billing/mazzi.py::prezzo_effettivo()`).
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c2e6f8a1d374'
down_revision: Union[str, None] = 'b8f4d2a6e153'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'offerte_mazzo',
        sa.Column('deck_id', sa.BigInteger(), nullable=False),
        sa.Column('tipo', sa.String(length=12), nullable=False),
        sa.Column('valore', sa.Integer(), nullable=False),
        sa.Column('valido_dal', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valido_fino', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("tipo in ('percentuale', 'importo')", name='ck_offerte_mazzo_tipo'),
        sa.CheckConstraint("tipo <> 'percentuale' or valore <= 100", name='ck_offerte_mazzo_percentuale'),
        sa.CheckConstraint(
            'valido_dal is null or valido_fino is null or valido_dal < valido_fino',
            name='ck_offerte_mazzo_finestra',
        ),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('deck_id'),
    )


def downgrade() -> None:
    op.drop_table('offerte_mazzo')
