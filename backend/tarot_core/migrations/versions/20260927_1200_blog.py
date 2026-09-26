"""blog: sezioni ad albero, articoli, etichette, collegamenti interni, immagini, avatar

Revision ID: 6f2b8d4a1c73
Revisione precedente: 3d7a9c1e5b28
Creata: 2026-09-27

Additiva: tabelle nuove e due colonne nulle su `users` (nome pubblico, avatar). Un backend
vecchio le ignora.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '6f2b8d4a1c73'
down_revision: Union[str, None] = '3d7a9c1e5b28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'media_images',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('uso', sa.String(length=10), nullable=False),
        sa.Column('webp', sa.LargeBinary(), nullable=False),
        sa.Column('larghezza', sa.Integer(), nullable=False),
        sa.Column('altezza', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("uso in ('blog', 'avatar')", name='ck_media_images_uso'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_media_images_owner_id'), 'media_images', ['owner_id'], unique=False)

    op.add_column('users', sa.Column('nome_pubblico', sa.String(length=60), nullable=True))
    op.add_column('users', sa.Column('avatar_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_users_avatar_id', 'users', 'media_images', ['avatar_id'], ['id'], ondelete='SET NULL')

    op.create_table(
        'blog_sections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('nome', sa.String(length=120), nullable=False),
        sa.Column('descrizione', sa.Text(), nullable=True),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('filtro', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ordine', sa.Integer(), server_default='0', nullable=False),
        sa.Column('visibile', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('immagine_id', sa.Uuid(), nullable=True),
        sa.Column('seo_titolo', sa.String(length=200), nullable=True),
        sa.Column('seo_descrizione', sa.String(length=320), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("tipo in ('articoli', 'carte', 'stese', 'contenitore')", name='ck_blog_sections_tipo'),
        sa.CheckConstraint('parent_id is null or parent_id <> id', name='ck_blog_sections_non_padre_di_se'),
        sa.ForeignKeyConstraint(['immagine_id'], ['media_images.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['blog_sections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index(op.f('ix_blog_sections_parent_id'), 'blog_sections', ['parent_id'], unique=False)

    op.create_table(
        'blog_tags',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('nome', sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    op.create_table(
        'blog_posts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('slug', sa.String(length=160), nullable=False),
        sa.Column('titolo', sa.String(length=200), nullable=False),
        sa.Column('sottotitolo', sa.String(length=300), nullable=True),
        sa.Column('testo', sa.Text(), server_default='', nullable=False),
        sa.Column('lang', sa.String(length=5), server_default='it', nullable=False),
        sa.Column('immagine_id', sa.Uuid(), nullable=True),
        sa.Column('immagine_alt', sa.String(length=200), nullable=True),
        sa.Column('sezione_id', sa.BigInteger(), nullable=True),
        sa.Column('autore_id', sa.BigInteger(), nullable=True),
        sa.Column('stato', sa.String(length=12), server_default='bozza', nullable=False),
        sa.Column('pubblicato_il', sa.DateTime(timezone=True), nullable=True),
        sa.Column('in_evidenza', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('commenti_aperti', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('seo_titolo', sa.String(length=200), nullable=True),
        sa.Column('seo_descrizione', sa.String(length=320), nullable=True),
        sa.Column('tempo_lettura', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("stato in ('bozza', 'pubblicato', 'archiviato')", name='ck_blog_posts_stato'),
        sa.ForeignKeyConstraint(['autore_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['immagine_id'], ['media_images.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sezione_id'], ['blog_sections.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index(op.f('ix_blog_posts_autore_id'), 'blog_posts', ['autore_id'], unique=False)
    op.create_index(op.f('ix_blog_posts_sezione_id'), 'blog_posts', ['sezione_id'], unique=False)
    op.create_index('ix_blog_posts_stato_data', 'blog_posts', ['stato', 'pubblicato_il'], unique=False)

    op.create_table(
        'blog_post_tags',
        sa.Column('post_id', sa.Uuid(), nullable=False),
        sa.Column('tag_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['blog_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('post_id', 'tag_id'),
    )

    op.create_table(
        'blog_post_links',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('post_id', sa.Uuid(), nullable=False),
        sa.Column('tipo', sa.String(length=10), nullable=False),
        sa.Column('riferimento', sa.String(length=160), nullable=False),
        sa.CheckConstraint("tipo in ('carta', 'stesa', 'articolo')", name='ck_blog_post_links_tipo'),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'tipo', 'riferimento', name='uq_blog_post_links'),
    )
    op.create_index('ix_blog_post_links_riferimento', 'blog_post_links', ['tipo', 'riferimento'], unique=False)

    op.create_table(
        'blog_post_revisions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('post_id', sa.Uuid(), nullable=False),
        sa.Column('titolo', sa.String(length=200), nullable=False),
        sa.Column('sottotitolo', sa.String(length=300), nullable=True),
        sa.Column('testo', sa.Text(), nullable=False),
        sa.Column('autore_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['autore_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['post_id'], ['blog_posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_blog_post_revisions_post_id'), 'blog_post_revisions', ['post_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_blog_post_revisions_post_id'), table_name='blog_post_revisions')
    op.drop_table('blog_post_revisions')
    op.drop_index('ix_blog_post_links_riferimento', table_name='blog_post_links')
    op.drop_table('blog_post_links')
    op.drop_table('blog_post_tags')
    op.drop_index('ix_blog_posts_stato_data', table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_sezione_id'), table_name='blog_posts')
    op.drop_index(op.f('ix_blog_posts_autore_id'), table_name='blog_posts')
    op.drop_table('blog_posts')
    op.drop_table('blog_tags')
    op.drop_index(op.f('ix_blog_sections_parent_id'), table_name='blog_sections')
    op.drop_table('blog_sections')
    op.drop_constraint('fk_users_avatar_id', 'users', type_='foreignkey')
    op.drop_column('users', 'avatar_id')
    op.drop_column('users', 'nome_pubblico')
    op.drop_index(op.f('ix_media_images_owner_id'), table_name='media_images')
    op.drop_table('media_images')
