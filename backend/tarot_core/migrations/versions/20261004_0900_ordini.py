"""ordini, righe_ordine, deck_unlocks.riga_ordine_id

Revision ID: d5a9c3f7b862
Revisione precedente: c2e6f8a1d374
Creata: 2026-10-04

Additiva (v5, Fase B3). Nasce `ordini` (un carrello, dall'apertura al pagamento — parallelo a
`payment_checkouts`, non innestato: un carrello è eterogeneo, un `PaymentCheckout` è un solo piano) e
`righe_ordine` (una voce per mazzo/prodotto, con prezzo pieno e prezzo davvero pagato dopo lo sconto
per-mazzo — lo sconto a scaglioni riguarda l'ordine intero ed è solo su `ordini.sconto_scaglioni`).

`deck_unlocks.riga_ordine_id` (nata nella migrazione di B1 come `Uuid`, prima che `righe_ordine`
esistesse e si sapesse che avrebbe avuto una chiave `BigInteger` come le altre righe interne) cambia
tipo di conseguenza: si ricrea, non c'è ancora nessun ordine reale che la valorizzi.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd5a9c3f7b862'
down_revision: Union[str, None] = 'c2e6f8a1d374'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ordini',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(length=12), server_default='aperto', nullable=False),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('external_id', sa.String(length=80), nullable=True),
        sa.Column('importo_totale', sa.Integer(), nullable=False),
        sa.Column('sconto_scaglioni', sa.Integer(), server_default='0', nullable=False),
        sa.Column('valuta', sa.String(length=3), server_default='EUR', nullable=False),
        sa.Column('indirizzo_spedizione_id', sa.Uuid(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status in ('aperto', 'pagato', 'annullato', 'scaduto')", name='ck_ordini_status'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
    )
    op.create_index('ix_ordini_user_id', 'ordini', ['user_id'])

    op.create_table(
        'righe_ordine',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('ordine_id', sa.Uuid(), nullable=False),
        sa.Column('tipo', sa.String(length=10), nullable=False),
        sa.Column('deck_id', sa.BigInteger(), nullable=False),
        sa.Column('quantita', sa.Integer(), server_default='1', nullable=False),
        sa.Column('prezzo_pieno_unitario', sa.Integer(), nullable=False),
        sa.Column('prezzo_finale_unitario', sa.Integer(), nullable=False),
        sa.Column('stato_evasione', sa.String(length=12), nullable=True),
        sa.CheckConstraint("tipo in ('digitale', 'pdf', 'fisico')", name='ck_righe_ordine_tipo'),
        sa.CheckConstraint('quantita > 0', name='ck_righe_ordine_quantita'),
        sa.CheckConstraint(
            "stato_evasione is null or stato_evasione in ('in_attesa', 'spedito', 'consegnato')",
            name='ck_righe_ordine_stato_evasione',
        ),
        sa.ForeignKeyConstraint(['ordine_id'], ['ordini.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_righe_ordine_ordine_id', 'righe_ordine', ['ordine_id'])

    op.drop_column('deck_unlocks', 'riga_ordine_id')
    op.add_column('deck_unlocks', sa.Column('riga_ordine_id', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('deck_unlocks', 'riga_ordine_id')
    op.add_column('deck_unlocks', sa.Column('riga_ordine_id', sa.Uuid(), nullable=True))
    op.drop_index('ix_righe_ordine_ordine_id', table_name='righe_ordine')
    op.drop_table('righe_ordine')
    op.drop_index('ix_ordini_user_id', table_name='ordini')
    op.drop_table('ordini')
