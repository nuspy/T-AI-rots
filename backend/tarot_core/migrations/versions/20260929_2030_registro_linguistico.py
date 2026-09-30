"""registro_linguistico

Revision ID: 5a476e0fae86
Revisione precedente: 1216abd7fc49
Creata: 2026-09-29

Additiva (v7, Fase F). `users.registro_linguistico`: `esoterico` (default, comportamento
identico a prima di v7) o `quotidiano` (le risposte evitano termini tecnici esoterici non
spiegati). Per-utente, non tocca il prefisso stabile/cacheable della sintesi.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '5a476e0fae86'
down_revision: Union[str, None] = '1216abd7fc49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('registro_linguistico', sa.String(length=20), nullable=False, server_default='esoterico'),
    )
    op.create_check_constraint(
        'ck_users_registro_linguistico', 'users',
        "registro_linguistico in ('esoterico', 'quotidiano')",
    )


def downgrade() -> None:
    op.drop_constraint('ck_users_registro_linguistico', 'users', type_='check')
    op.drop_column('users', 'registro_linguistico')
