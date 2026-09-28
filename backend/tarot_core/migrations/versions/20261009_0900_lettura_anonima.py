"""readings.anon_id, consumo 'anonimo'

Revision ID: d1f5b8c247a3
Revisione precedente: c7e1a5d834f0
Creata: 2026-10-09

Additiva (v6, Fase F). `Reading.owner_id` era già nullable (`OwnedMixin`): non serve un modello
parallelo per le letture anonime, basta `anon_id` (il valore del cookie `tarots_anon`) e un nuovo
valore ammesso in `consumo` per chi non ha ancora un account.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd1f5b8c247a3'
down_revision: Union[str, None] = 'c7e1a5d834f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('readings', sa.Column('anon_id', sa.String(length=64), nullable=True))
    op.add_column('readings', sa.Column('teaser', sa.Text(), nullable=True))
    op.create_index('ix_readings_anon_id', 'readings', ['anon_id'])

    op.drop_constraint('ck_readings_consumo', 'readings', type_='check')
    op.create_check_constraint(
        'ck_readings_consumo', 'readings', "consumo in ('credito', 'quota', 'omaggio', 'anonimo')",
    )


def downgrade() -> None:
    op.drop_constraint('ck_readings_consumo', 'readings', type_='check')
    op.create_check_constraint(
        'ck_readings_consumo', 'readings', "consumo in ('credito', 'quota', 'omaggio')",
    )
    op.drop_index('ix_readings_anon_id', table_name='readings')
    op.drop_column('readings', 'teaser')
    op.drop_column('readings', 'anon_id')
