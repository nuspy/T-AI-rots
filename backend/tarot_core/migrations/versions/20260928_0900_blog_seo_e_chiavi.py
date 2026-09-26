"""blog: campi SEO degli articoli e chiavi applicative per la pubblicazione via REST

Revision ID: a41c7e92d3b6
Revisione precedente: 6f2b8d4a1c73
Creata: 2026-09-28

Additiva. `blog_posts` riceve la parola chiave principale e le secondarie, `noindex`, l'indirizzo canonico, le
domande frequenti e il riferimento alla chiave che ha creato l'articolo; nasce `api_keys`. Un backend vecchio
ignora le colonne nuove.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a41c7e92d3b6'
down_revision: Union[str, None] = '6f2b8d4a1c73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'api_keys',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nome', sa.String(length=80), nullable=False),
        sa.Column('prefisso', sa.String(length=16), nullable=False),
        sa.Column('impronta', sa.String(length=64), nullable=False),
        sa.Column('scopes', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column('limite_minuto', sa.Integer(), server_default='30', nullable=False),
        sa.Column('limite_giorno', sa.Integer(), server_default='20', nullable=False),
        sa.Column('attiva', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('creata_da', sa.BigInteger(), nullable=True),
        sa.Column('ultimo_uso', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usi', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revocata_il', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['creata_da'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prefisso'),
    )

    op.add_column('blog_posts', sa.Column('seo_parola_chiave', sa.String(length=120), nullable=True))
    op.add_column('blog_posts', sa.Column('seo_parole_chiave', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False))
    op.add_column('blog_posts', sa.Column('noindex', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('blog_posts', sa.Column('canonical_url', sa.String(length=500), nullable=True))
    op.add_column('blog_posts', sa.Column('faq', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False))
    op.add_column('blog_posts', sa.Column('creato_da_chiave_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_blog_posts_creato_da_chiave', 'blog_posts', 'api_keys', ['creato_da_chiave_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_blog_posts_creato_da_chiave_id'), 'blog_posts', ['creato_da_chiave_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_blog_posts_creato_da_chiave_id'), table_name='blog_posts')
    op.drop_constraint('fk_blog_posts_creato_da_chiave', 'blog_posts', type_='foreignkey')
    for colonna in ('creato_da_chiave_id', 'faq', 'canonical_url', 'noindex', 'seo_parole_chiave', 'seo_parola_chiave'):
        op.drop_column('blog_posts', colonna)
    op.drop_table('api_keys')
