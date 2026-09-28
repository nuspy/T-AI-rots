"""impostazioni_sessione

Revision ID: e8a2c916f4b7
Revisione precedente: d1f5b8c247a3
Creata: 2026-10-10

Additiva (v6, Fase G). Singleton come `impostazioni_crediti`/`impostazioni_chat`: specchia
`ssoSessionMaxLifespan` del realm Keycloak per mostrarlo in console. La fonte di verità resta
Keycloak — vedi la nota sulla deriva in `domain/config_models.py::ImpostazioniSessione`.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e8a2c916f4b7'
down_revision: Union[str, None] = 'd1f5b8c247a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'impostazioni_sessione',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sso_session_max_lifespan_secondi', sa.Integer(), nullable=False, server_default='36000'),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('id = 1', name='ck_impostazioni_sessione_singleton'),
    )


def downgrade() -> None:
    op.drop_table('impostazioni_sessione')
