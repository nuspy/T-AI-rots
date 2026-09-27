"""fornitori LLM configurati dalla console

Revision ID: d9a3f6c1b284
Revisione precedente: b5d2e8f31a47
Creata: 2026-09-27

Additiva. Nasce `llm_providers`: indirizzo, modello e chiave (cifrata, `api_key_cifrata`) dei fornitori LLM, che fino
a oggi vivevano solo in `TAROT_MODELLI` (l'ambiente del processo). `model_assignments` non cambia: cita già solo un
nome, non un indirizzo. Un backend vecchio ignora la tabella nuova e continua a leggere `TAROT_MODELLI`.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd9a3f6c1b284'
down_revision: Union[str, None] = 'b5d2e8f31a47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'llm_providers',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nome', sa.String(length=60), nullable=False),
        sa.Column('tipo', sa.String(length=30), nullable=False),
        sa.Column('provider', sa.String(length=20), server_default=sa.text("'openai-compatible'"), nullable=False),
        sa.Column('base_url', sa.String(length=300), server_default=sa.text("''"), nullable=False),
        sa.Column('model', sa.String(length=120), server_default=sa.text("''"), nullable=False),
        sa.Column('embed_model', sa.String(length=120), server_default=sa.text("''"), nullable=False),
        sa.Column('api_key_cifrata', sa.LargeBinary(), nullable=True),
        sa.Column('motore', sa.String(length=20), server_default=sa.text("''"), nullable=False),
        sa.Column('ragiona', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('parametri', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('senza_filtri', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('descrizione', sa.String(length=200), server_default=sa.text("''"), nullable=False),
        sa.Column('attivo', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome'),
    )


def downgrade() -> None:
    op.drop_table('llm_providers')
