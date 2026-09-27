"""offerte: coupon e regali di crediti

Revision ID: b5d2e8f31a47
Revisione precedente: a41c7e92d3b6
Creata: 2026-09-29

Additiva. Nascono `coupons` (sconti in percentuale o in importo, e codici regalo in crediti) e
`coupon_redemptions` (chi ha usato cosa); `payment_checkouts` riceve il coupon usato e lo sconto. Un backend vecchio
ignora le colonne nuove.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b5d2e8f31a47'
down_revision: Union[str, None] = 'a41c7e92d3b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'coupons',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=40), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('valore', sa.Integer(), nullable=False),
        sa.Column('piani', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('solo_primo_acquisto', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('valido_dal', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valido_fino', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_riscatti', sa.Integer(), nullable=True),
        sa.Column('max_per_utente', sa.Integer(), server_default=sa.text('1'), nullable=False),
        sa.Column('riscatti', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('attivo', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("tipo in ('percentuale', 'importo', 'crediti')", name='ck_coupons_tipo'),
        sa.CheckConstraint('valore > 0', name='ck_coupons_valore'),
        sa.CheckConstraint("tipo <> 'percentuale' or valore <= 100", name='ck_coupons_percentuale'),
        sa.CheckConstraint('max_per_utente >= 1', name='ck_coupons_per_utente'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_table(
        'coupon_redemptions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('coupon_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('checkout_id', sa.Uuid(), nullable=True),
        sa.Column('sconto', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('crediti', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['checkout_id'], ['payment_checkouts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_coupon_redemptions_coupon', 'coupon_redemptions', ['coupon_id'], unique=False)
    op.create_index('ix_coupon_redemptions_utente', 'coupon_redemptions', ['user_id', 'coupon_id'], unique=False)

    op.add_column('payment_checkouts', sa.Column('coupon_id', sa.BigInteger(), nullable=True))
    op.add_column('payment_checkouts', sa.Column('sconto', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.create_foreign_key('fk_payment_checkouts_coupon', 'payment_checkouts', 'coupons', ['coupon_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_payment_checkouts_coupon', 'payment_checkouts', type_='foreignkey')
    op.drop_column('payment_checkouts', 'sconto')
    op.drop_column('payment_checkouts', 'coupon_id')
    op.drop_index('ix_coupon_redemptions_utente', table_name='coupon_redemptions')
    op.drop_index('ix_coupon_redemptions_coupon', table_name='coupon_redemptions')
    op.drop_table('coupon_redemptions')
    op.drop_table('coupons')
