"""letture: colonna manuale

Revision ID: a7c3e91f4b02
Revisione precedente: f1a4c8e2b917
Creata: 2026-10-01

Additiva. Aggiunge `readings.manuale` (v5, Fase C — "Interpreta i miei tarocchi"): vero se le carte
sono state inserite a mano (mazzo fisico già estratto) invece che scelte dal ventaglio. Decide solo la
visibilità dell'identità della carta in `carta_json()`, non tocca il ritmo di rivelazione
dell'interpretazione.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a7c3e91f4b02'
down_revision: Union[str, None] = 'f1a4c8e2b917'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'readings',
        sa.Column('manuale', sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('readings', 'manuale')
