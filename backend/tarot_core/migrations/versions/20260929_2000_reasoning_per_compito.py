"""reasoning_per_compito

Revision ID: 1216abd7fc49
Revisione precedente: e8a2c916f4b7
Creata: 2026-09-29

Additiva (v7, Fase B). Due colonne nullable su `model_assignments`: `ragiona_override` e
`parametri_override`. Prima di questa migrazione, `ragiona`/`parametri` vivevano solo sul
fornitore (`llm_providers`): due compiti sullo stesso fornitore condividevano per forza lo stesso
reasoning, e l'unico modo per avere lo stesso modello con e senza ragionamento era duplicare il
fornitore in console.

Il backfill mette `ragiona_override = false` su OGNI riga esistente, non solo sulle nuove: il
backlog v7 vuole il reasoning disattivato per default su ogni compito già assegnato, non
"eredita dal fornitore" per quelli non ancora toccati dall'amministratore — e il fornitore
attivo in produzione (`nebius-nemotron-lightning`) ha `ragiona: true`, causa diretta della
lentezza/troncamenti diagnosticati in questa stessa sessione.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '1216abd7fc49'
down_revision: Union[str, None] = 'e8a2c916f4b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('model_assignments', sa.Column('ragiona_override', sa.Boolean(), nullable=True))
    op.add_column('model_assignments', sa.Column('parametri_override', postgresql.JSONB(), nullable=True))
    op.execute("UPDATE model_assignments SET ragiona_override = false WHERE ragiona_override IS NULL")


def downgrade() -> None:
    op.drop_column('model_assignments', 'parametri_override')
    op.drop_column('model_assignments', 'ragiona_override')
