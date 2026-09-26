"""letture speciali: genere, partner ricordato, persone della lettura

Revision ID: 5b1e7c3a9d42
Revisione precedente: 824583d91378
Creata: 2026-09-26

Additiva: tre colonne nuove su `users` più una su `readings`, tutte nulle (o con
`false` di default), quindi un backend vecchio le ignora e su PostgreSQL 11+ non
si riscrive la tabella.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '5b1e7c3a9d42'
down_revision: Union[str, None] = '824583d91378'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('gender_custom', sa.String(length=40), nullable=True))
    op.add_column('users', sa.Column('is_trans', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('users', sa.Column('partner_ricordato', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_check_constraint(
        'ck_users_gender', 'users',
        "gender is null or gender in ('donna', 'uomo', 'non_binario', 'altro', 'non_dice')",
    )
    op.add_column('readings', sa.Column('persone', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('readings', 'persone')
    op.drop_constraint('ck_users_gender', 'users', type_='check')
    op.drop_column('users', 'partner_ricordato')
    op.drop_column('users', 'is_trans')
    op.drop_column('users', 'gender_custom')
    op.drop_column('users', 'gender')
