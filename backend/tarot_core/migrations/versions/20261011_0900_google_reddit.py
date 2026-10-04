"""google_reddit

Revision ID: d5e9b3a7f2c8
Revisione precedente: c4d8a2f6e1b7
Creata: 2026-10-11

Additiva (v8.6). Le integrazioni configurate dalla console:
- `config_google`: il service account Google (cifrato) per Search Console e GA4, la proprietà GA4 e l'ID di
  misurazione del contatore del sito;
- `config_reddit`: l'account Reddit (app «script», segreto e password cifrati) e dove pubblicare;
- `post_reddit`: un post Reddit per articolo del blog, mai due (vincolo unico sull'articolo).

Le uscite degli analytics (pagina d'uscita e ultima azione della lettura) non toccano lo schema: la pagina d'uscita
è già `an_sessioni.uscita`, l'ultima azione si ricava dagli eventi della sessione.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd5e9b3a7f2c8'
down_revision: Union[str, None] = 'c4d8a2f6e1b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tempi() -> list:
    return [
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        'config_google',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_account_cifrato', sa.LargeBinary(), nullable=True),
        sa.Column('client_email', sa.String(length=320), nullable=True),
        sa.Column('project_id', sa.String(length=120), nullable=True),
        sa.Column('private_key_id', sa.String(length=80), nullable=True),
        sa.Column('sc_proprieta', sa.String(length=300), nullable=True),
        sa.Column('ga4_proprieta_id', sa.String(length=20), nullable=True),
        sa.Column('ga4_misurazione_id', sa.String(length=20), nullable=True),
        sa.Column('verificato_il', sa.DateTime(timezone=True), nullable=True),
        sa.Column('esito_verifica', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        *_tempi(),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('id = 1', name='ck_config_google_singleton'),
    )
    op.create_table(
        'config_reddit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=True),
        sa.Column('client_secret_cifrato', sa.LargeBinary(), nullable=True),
        sa.Column('utente', sa.String(length=40), nullable=True),
        sa.Column('password_cifrata', sa.LargeBinary(), nullable=True),
        sa.Column('subreddit', sa.String(length=60), nullable=True),
        sa.Column('flair_id', sa.String(length=64), nullable=True),
        sa.Column('attivo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('attivo_dal', sa.DateTime(timezone=True), nullable=True),
        sa.Column('lingue', postgresql.JSONB(), server_default=sa.text('\'["en"]\'::jsonb'), nullable=False),
        sa.Column('intervallo_minuti', sa.Integer(), server_default='60', nullable=False),
        sa.Column('ultima_prova_il', sa.DateTime(timezone=True), nullable=True),
        sa.Column('esito_prova', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
        *_tempi(),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('id = 1', name='ck_config_reddit_singleton'),
        sa.CheckConstraint('intervallo_minuti >= 0', name='ck_config_reddit_intervallo'),
    )
    op.create_table(
        'post_reddit',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('articolo_id', sa.Uuid(), nullable=False),
        sa.Column('stato', sa.String(length=12), server_default='in_coda', nullable=False),
        sa.Column('tipo', sa.String(length=10), nullable=True),
        sa.Column('subreddit', sa.String(length=60), nullable=True),
        sa.Column('reddit_id', sa.String(length=20), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('errore', sa.String(length=1000), nullable=True),
        sa.Column('tentativi', sa.Integer(), server_default='0', nullable=False),
        sa.Column('riprova_dopo', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pubblicato_il', sa.DateTime(timezone=True), nullable=True),
        *_tempi(),
        sa.ForeignKeyConstraint(['articolo_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('articolo_id', name='uq_post_reddit_articolo'),
        sa.CheckConstraint(
            "stato in ('in_coda', 'in_corso', 'pubblicato', 'errore', 'saltato')", name='ck_post_reddit_stato',
        ),
    )
    op.create_index('ix_post_reddit_stato_creato', 'post_reddit', ['stato', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_post_reddit_stato_creato', table_name='post_reddit')
    op.drop_table('post_reddit')
    op.drop_table('config_reddit')
    op.drop_table('config_google')
