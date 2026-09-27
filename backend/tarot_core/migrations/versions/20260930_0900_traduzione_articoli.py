"""blog: collegamento articolo -> traduzione

Revision ID: f1a4c8e2b917
Revisione precedente: e2b6a917c5d4
Creata: 2026-09-30

Additiva. Aggiunge `blog_posts.tradotto_da_id`, un riferimento auto-referenziale nullable
all'articolo di origine (v5, Fase E — traduzione automatica): una catena radicata sull'originale
basta a sapere quali lingue esistono per un articolo, non serve una tabella di gruppo-traduzione a
parte. `ON DELETE SET NULL`: se l'originale viene cancellato la traduzione resta un articolo a sé,
non sparisce con lui.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f1a4c8e2b917'
down_revision: Union[str, None] = 'e2b6a917c5d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('blog_posts', sa.Column('tradotto_da_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_blog_posts_tradotto_da_id', 'blog_posts', 'blog_posts',
        ['tradotto_da_id'], ['id'], ondelete='SET NULL',
    )
    op.create_index('ix_blog_posts_tradotto_da_id', 'blog_posts', ['tradotto_da_id'])


def downgrade() -> None:
    op.drop_index('ix_blog_posts_tradotto_da_id', table_name='blog_posts')
    op.drop_constraint('fk_blog_posts_tradotto_da_id', 'blog_posts', type_='foreignkey')
    op.drop_column('blog_posts', 'tradotto_da_id')
