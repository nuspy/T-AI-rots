"""notifiche_motori

Revision ID: 545b3689315b
Revisione precedente: 94c558e43bd6
Creata: 2026-09-30

Additiva (v8). Il registro degli invii ai motori di ricerca (IndexNow, Search Console, WebSub):
una riga per esecuzione, notturna o manuale dalla console.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '545b3689315b'
down_revision: Union[str, None] = '94c558e43bd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notifiche_motori',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('finestra_da', sa.DateTime(timezone=True), nullable=False),
        sa.Column('manuale', sa.Boolean(), nullable=False),
        sa.Column('url', postgresql.JSONB(), nullable=False),
        sa.Column('esiti', postgresql.JSONB(), nullable=False),
        sa.Column('riuscita', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('notifiche_motori')
