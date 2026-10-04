"""Riduzione dei costi delle inferenze: i controlli LLM solo sui casi dubbi e lo stato sintetico della memoria.

Revision ID: b6d8f0a2c4e7
Revises: a5c7e9b1d3f6

Additiva:

- `impostazioni_intervista.validatore_domande` e `.guardia_responso`: `dubbi` (predefinito), `spento` o `acceso`. Il
  validatore LLM delle domande e la guardia LLM del responso partono solo quando un controllo deterministico segnala
  qualcosa da guardare (vedi `tarot/intervista.py::sospetta` e `guards/lettura.py::da_guardare`). La riga che c'è già
  prende `dubbi` per entrambi.
- `impostazioni_intervista.memoria_stato_nei_prompt`: spento. Lo stato sintetico si calcola, ma entra nei prompt solo
  quando l'operatore lo accende.
- `memoria_stato`: una riga per utente con le voci dello stato sintetico (`tarot/stato_memoria.py`), cancellata insieme
  all'utente.
- `llm_providers.livello_ragionamento` e `model_assignments.livello_ragionamento`: il livello di ragionamento (`none`
  … `max`, `llm/ragionamento.py`) al posto del vecchio booleano, che resta allineato. Dal booleano: `true` → `medium`,
  `false` → `none`; un compito senza `ragiona_override` resta `NULL` (eredita). Il downgrade riscrive i booleani dai
  livelli.
- `model_assignments.json_schema`: lo schema JSON rigoroso per compito (`llm/schemi_json.py`), con ripiego automatico.
  `NULL`: spento.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "b6d8f0a2c4e7"
down_revision = "a5c7e9b1d3f6"
branch_labels = None
depends_on = None

MODI = "('dubbi', 'spento', 'acceso')"
#: Scritti qui e non importati da `llm/ragionamento.py`: una migrazione non deve cambiare se domani cambia il codice.
LIVELLI = "('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max')"


def upgrade() -> None:
    op.add_column("impostazioni_intervista", sa.Column(
        "validatore_domande", sa.String(10), nullable=False, server_default="dubbi",
    ))
    op.add_column("impostazioni_intervista", sa.Column(
        "guardia_responso", sa.String(10), nullable=False, server_default="dubbi",
    ))
    op.add_column("impostazioni_intervista", sa.Column(
        "memoria_stato_nei_prompt", sa.Boolean(), nullable=False, server_default=sa.false(),
    ))
    op.create_check_constraint(
        "ck_impostazioni_intervista_validatore", "impostazioni_intervista", f"validatore_domande IN {MODI}",
    )
    op.create_check_constraint(
        "ck_impostazioni_intervista_guardia", "impostazioni_intervista", f"guardia_responso IN {MODI}",
    )

    op.create_table(
        "memoria_stato",
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("voci", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.add_column("llm_providers", sa.Column(
        "livello_ragionamento", sa.String(10), nullable=False, server_default="none",
    ))
    op.execute("UPDATE llm_providers SET livello_ragionamento = CASE WHEN ragiona THEN 'medium' ELSE 'none' END")
    op.create_check_constraint(
        "ck_llm_providers_livello", "llm_providers", f"livello_ragionamento IN {LIVELLI}",
    )
    op.add_column("model_assignments", sa.Column("livello_ragionamento", sa.String(10)))
    op.add_column("model_assignments", sa.Column("json_schema", sa.Boolean()))
    op.execute(
        "UPDATE model_assignments SET livello_ragionamento = CASE WHEN ragiona_override THEN 'medium' ELSE 'none' END "
        "WHERE ragiona_override IS NOT NULL"
    )
    op.create_check_constraint(
        "ck_model_assignments_livello", "model_assignments",
        f"livello_ragionamento IS NULL OR livello_ragionamento IN {LIVELLI}",
    )


def downgrade() -> None:
    op.execute("UPDATE llm_providers SET ragiona = (livello_ragionamento <> 'none')")
    op.execute(
        "UPDATE model_assignments SET ragiona_override = CASE WHEN livello_ragionamento IS NULL THEN ragiona_override "
        "ELSE livello_ragionamento <> 'none' END"
    )
    op.drop_constraint("ck_model_assignments_livello", "model_assignments", type_="check")
    op.drop_column("model_assignments", "json_schema")
    op.drop_column("model_assignments", "livello_ragionamento")
    op.drop_constraint("ck_llm_providers_livello", "llm_providers", type_="check")
    op.drop_column("llm_providers", "livello_ragionamento")

    op.drop_table("memoria_stato")
    op.drop_constraint("ck_impostazioni_intervista_guardia", "impostazioni_intervista", type_="check")
    op.drop_constraint("ck_impostazioni_intervista_validatore", "impostazioni_intervista", type_="check")
    op.drop_column("impostazioni_intervista", "memoria_stato_nei_prompt")
    op.drop_column("impostazioni_intervista", "guardia_responso")
    op.drop_column("impostazioni_intervista", "validatore_domande")
