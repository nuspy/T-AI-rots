"""miniature delle immagini

Revision ID: 3e7a9c1d5b20
Revisione precedente: 9d4b2f7e1a55
Creata: 2026-10-01

Additiva (v8.3). La miniatura WebP per gli elenchi del blog, accanto all'immagine grande in `media_images`: si
crea a ogni caricamento e a ogni assegnazione; le immagini già presenti la ricevono con `tools/miniature_blog.py`.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '3e7a9c1d5b20'
down_revision: Union[str, None] = '9d4b2f7e1a55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("media_images", sa.Column("mini_webp", sa.LargeBinary(), nullable=True))
    op.add_column("media_images", sa.Column("mini_larghezza", sa.Integer(), nullable=True))
    op.add_column("media_images", sa.Column("mini_altezza", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("media_images", "mini_altezza")
    op.drop_column("media_images", "mini_larghezza")
    op.drop_column("media_images", "mini_webp")
