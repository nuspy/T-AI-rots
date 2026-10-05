"""blog v9.4: il soggetto degli articoli, il testo alternativo delle immagini delle sezioni, le immagini del catalogo

Revision ID: d1f3a5c7e9b2
Revises: c7e9a1b3d5f8
Creata: 2026-10-05

Solo schema, additiva (i dati li sistema la migrazione seguente, `e2a4b6c8d0f3`):

- `blog_posts.soggetto_tipo` ('carta' | 'stesa' | null) e `soggetto_ref` (l'id canonico: `maj-10`, `coppe-01`,
  `croce-celtica`), con un vincolo (o tutti e due o nessuno) e un indice per le pagine di carte e stese;
- `blog_sections.immagine_alt`: il testo alternativo dell'immagine di una sezione;
- `catalogo_immagini` (`tipo`, `riferimento`) → `immagine_id`, `alt`: le illustrazioni delle stese.

Un backend vecchio ignora le colonne e la tabella nuove. Il downgrade le toglie (le immagini restano fra i media).
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d1f3a5c7e9b2"
down_revision: Union[str, None] = "c7e9a1b3d5f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("blog_posts", sa.Column("soggetto_tipo", sa.String(length=10), nullable=True))
    op.add_column("blog_posts", sa.Column("soggetto_ref", sa.String(length=60), nullable=True))
    op.create_check_constraint(
        "ck_blog_posts_soggetto", "blog_posts",
        "(soggetto_tipo is null and soggetto_ref is null) or "
        "(soggetto_tipo in ('carta', 'stesa') and soggetto_ref is not null)",
    )
    op.create_index("ix_blog_posts_soggetto", "blog_posts", ["soggetto_tipo", "soggetto_ref"], unique=False)

    op.add_column("blog_sections", sa.Column("immagine_alt", sa.String(length=200), nullable=True))

    op.create_table(
        "catalogo_immagini",
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("riferimento", sa.String(length=80), nullable=False),
        sa.Column("immagine_id", sa.Uuid(), nullable=False),
        sa.Column("alt", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("tipo in ('stesa')", name="ck_catalogo_immagini_tipo"),
        sa.ForeignKeyConstraint(["immagine_id"], ["media_images.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tipo", "riferimento"),
    )
    op.create_index(op.f("ix_catalogo_immagini_immagine_id"), "catalogo_immagini", ["immagine_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_catalogo_immagini_immagine_id"), table_name="catalogo_immagini")
    op.drop_table("catalogo_immagini")
    op.drop_column("blog_sections", "immagine_alt")
    op.drop_index("ix_blog_posts_soggetto", table_name="blog_posts")
    op.drop_constraint("ck_blog_posts_soggetto", "blog_posts", type_="check")
    op.drop_column("blog_posts", "soggetto_ref")
    op.drop_column("blog_posts", "soggetto_tipo")
