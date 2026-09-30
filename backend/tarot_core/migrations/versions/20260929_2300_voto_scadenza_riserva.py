"""voto_scadenza_riserva

Revision ID: cea0131661de
Revisione precedente: 59cecc660692
Creata: 2026-09-29

Additiva (v7, Fase K, estensione "tornate elettorali"). Due cambi allo schema della Fase K:
`voting_rounds.chiude_il` (la scadenza dichiarata alla creazione: la tornata si chiude da sola
quando passa, vedi `voting_repositories.chiudi_tornate_scadute`), e `deck_candidates.round_id`
diventa opzionale — un candidato può esistere in una **riserva** di proposte non ancora scelte per
nessuna tornata, e la creazione di una tornata seleziona fra quelle in riserva invece di crearne di
nuovi al volo.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'cea0131661de'
down_revision: Union[str, None] = '59cecc660692'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('voting_rounds', sa.Column('chiude_il', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('deck_candidates', 'round_id', existing_type=sa.Uuid(), nullable=True)


def downgrade() -> None:
    op.alter_column('deck_candidates', 'round_id', existing_type=sa.Uuid(), nullable=False)
    op.drop_column('voting_rounds', 'chiude_il')
