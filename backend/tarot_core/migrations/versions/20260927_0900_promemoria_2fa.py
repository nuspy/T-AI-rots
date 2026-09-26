"""promemoria della verifica in due passaggi

Revision ID: 3d7a9c1e5b28
Revisione precedente: 8c4f2a7d1e93
Creata: 2026-09-27

Additiva: una colonna con default su `users`. Chi non l'ha toccata continua a vedere
il promemoria; chi spunta «non mostrare più» lo spegne, su ogni dispositivo.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '3d7a9c1e5b28'
down_revision: Union[str, None] = '8c4f2a7d1e93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('promemoria_2fa', sa.Boolean(), server_default=sa.true(), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'promemoria_2fa')
