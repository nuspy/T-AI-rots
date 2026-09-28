"""user_memories

Revision ID: f3c8a1d92e57
Revisione precedente: a7f1e4c9b230
Creata: 2026-10-06

Additiva (v6, Fase A). Nasce `user_memories`: la memoria per utente estratta dalle letture concluse
(e, in una fase successiva, dalla chat proattiva). `embedding` è un array di float, non un tipo
`vector` di pgvector — l'estensione non è disponibile sul Postgres condiviso di produzione (Alpine,
namespace `tadamoo`, verificato con `CREATE EXTENSION IF NOT EXISTS vector` fallito) e installarla
richiederebbe ricostruire e riavviare un servizio condiviso con Keycloak, fuori scope qui. La
similarità si calcola lato applicazione (`tarot/memoria_retrieval.py`): vedi la nota in
`domain/memory_models.py` per il dettaglio e il ripiego futuro se pgvector diventasse disponibile.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f3c8a1d92e57'
down_revision: Union[str, None] = 'a7f1e4c9b230'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_memories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('owner_id', sa.BigInteger(), nullable=False),
        sa.Column('contenuto', sa.Text(), nullable=False),
        sa.Column('tipo', sa.String(length=10), nullable=False),
        sa.Column('campo_attinenza', sa.String(length=40), nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column('reading_id', sa.Uuid(), nullable=True),
        sa.Column('fonte', sa.String(length=20), nullable=False),
        sa.Column('superseded_by', sa.Uuid(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reading_id'], ['readings.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['superseded_by'], ['user_memories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("tipo IN ('stabile', 'variabile')", name='ck_user_memories_tipo'),
        sa.CheckConstraint("fonte IN ('lettura', 'chat')", name='ck_user_memories_fonte'),
    )
    op.create_index(
        'ix_user_memories_owner_campo_attinenza', 'user_memories', ['owner_id', 'campo_attinenza'],
    )


def downgrade() -> None:
    op.drop_index('ix_user_memories_owner_campo_attinenza', table_name='user_memories')
    op.drop_table('user_memories')
