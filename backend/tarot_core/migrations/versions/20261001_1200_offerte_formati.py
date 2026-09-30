"""offerte dei mazzi anche su PDF e scatola

Revision ID: 9a4c2e7b1f38
Revisione precedente: 5c8e1f3a9d24
Creata: 2026-10-01

Additiva (v8.5). L'offerta di un mazzo dice a quali prodotti si applica: digitale, PDF da stampare, scatola fisica.
Le offerte già presenti valevano solo sul digitale, e così restano (valore predefinito).
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '9a4c2e7b1f38'
down_revision: Union[str, None] = '5c8e1f3a9d24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("offerte_mazzo", sa.Column(
        "formati", postgresql.JSONB(astext_type=sa.Text()), nullable=False,
        server_default=sa.text("'[\"digitale\"]'::jsonb"),
    ))


def downgrade() -> None:
    op.drop_column("offerte_mazzo", "formati")
