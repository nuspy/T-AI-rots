"""readings.memorie_recuperate

Revision ID: b6d4f9a2c831
Revisione precedente: f3c8a1d92e57
Creata: 2026-10-07

Additiva (v6, Fase C). `readings.memorie_recuperate` è l'istantanea delle memorie rilevanti
recuperate all'apertura della lettura (come `persone`): resta la stessa per tutta l'intervista.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b6d4f9a2c831'
down_revision: Union[str, None] = 'f3c8a1d92e57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('readings', sa.Column('memorie_recuperate', postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('readings', 'memorie_recuperate')
