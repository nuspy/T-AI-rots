"""I livelli di ragionamento predefiniti per compito (piano approvato dall'operatore, 4/10/2026).

Revision ID: c7e9a1b3d5f8
Revises: b6d8f0a2c4e7

Solo dati, nessuno schema. Imposta il livello di ragionamento delle assegnazioni dei compiti:

| compito | livello |
|---|---|
| `interpretazione` (la chiamata unica) | `xhigh` |
| `sintesi` | `xhigh` |
| `intervista`, `validazione`, `giudizio` | `none` |
| `chat_proattiva` (l'oracolo) | `none` |
| `memoria_estrazione` | `none` (lo stato sintetico lo spegne già dal codice) |

- **I fornitori assegnati non cambiano**: si scrive solo `livello_ragionamento` (e `ragiona_override`, che resta
  allineato: `livello != none`).
- Un compito **senza assegnazione** (in produzione: l'oracolo e la memoria, che ereditavano il ragionamento del
  fornitore) la riceve sul **fornitore predefinito**, lo stesso che il registro gli dava già: quello che si chiama
  `predefinito` se c'è ed è attivo, altrimenti il primo attivo in ordine di nome (`RegistroModelli.nome_per`). Senza
  fornitori attivi non si crea nulla.
- I menu a tendina della console restano: da lì si cambia tutto.

**Il downgrade** rimette ciò che c'era prima. Lo stato di prima si scrive nel registro delle azioni (`audit_log`,
azione `modello.livelli_predefiniti`, `before`/`after`, attore nullo: «l'ha fatto il sistema»): è anche la traccia che
la console mostra di chi ha cambiato la configurazione. Il downgrade legge l'ultima di quelle righe, rimette livelli e
`ragiona_override` di prima, cancella le assegnazioni che l'upgrade aveva creato e registra l'annullamento.
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "c7e9a1b3d5f8"
down_revision = "b6d8f0a2c4e7"
branch_labels = None
depends_on = None

#: Scritti qui e non importati dal codice: una migrazione non deve cambiare se domani cambia il codice.
LIVELLI = {
    "interpretazione": "xhigh",
    "sintesi": "xhigh",
    "intervista": "none",
    "validazione": "none",
    "giudizio": "none",
    "chat_proattiva": "none",
    "memoria_estrazione": "none",
}
AZIONE = "modello.livelli_predefiniti"


def _predefinito(conn) -> str | None:
    return conn.execute(sa.text(
        "SELECT nome FROM llm_providers WHERE attivo ORDER BY (nome = 'predefinito') DESC, nome LIMIT 1"
    )).scalar()


def upgrade() -> None:
    conn = op.get_bind()
    righe = {
        r.task: r for r in conn.execute(sa.text(
            "SELECT task, model_name, livello_ragionamento, ragiona_override FROM model_assignments"
        ))
    }
    predefinito = _predefinito(conn)
    prima, dopo = {}, {}
    for compito, livello in LIVELLI.items():
        riga = righe.get(compito)
        ragiona = livello != "none"
        if riga is not None:
            prima[compito] = {
                "model_name": riga.model_name, "livello_ragionamento": riga.livello_ragionamento,
                "ragiona_override": riga.ragiona_override,
            }
            conn.execute(sa.text(
                "UPDATE model_assignments SET livello_ragionamento = :livello, ragiona_override = :ragiona, "
                "updated_at = now() WHERE task = :task"
            ), {"livello": livello, "ragiona": ragiona, "task": compito})
            dopo[compito] = {"model_name": riga.model_name, "livello_ragionamento": livello}
        elif predefinito:
            prima[compito] = None
            conn.execute(sa.text(
                "INSERT INTO model_assignments (task, model_name, livello_ragionamento, ragiona_override) "
                "VALUES (:task, :nome, :livello, :ragiona)"
            ), {"task": compito, "nome": predefinito, "livello": livello, "ragiona": ragiona})
            dopo[compito] = {"model_name": predefinito, "livello_ragionamento": livello, "creata": True}
    if dopo:
        conn.execute(sa.text(
            "INSERT INTO audit_log (actor_id, action, target_type, target_id, before, after, created_at) "
            "VALUES (NULL, :azione, 'compito', 'livelli', CAST(:prima AS jsonb), CAST(:dopo AS jsonb), now())"
        ), {"azione": AZIONE, "prima": json.dumps({"righe": prima}), "dopo": json.dumps({"righe": dopo})})


def downgrade() -> None:
    conn = op.get_bind()
    traccia = conn.execute(sa.text(
        "SELECT before FROM audit_log WHERE action = :azione ORDER BY id DESC LIMIT 1"
    ), {"azione": AZIONE}).scalar()
    if not traccia:
        return
    righe = (traccia if isinstance(traccia, dict) else json.loads(traccia)).get("righe") or {}
    for compito, prima in righe.items():
        if prima is None:
            conn.execute(sa.text("DELETE FROM model_assignments WHERE task = :task"), {"task": compito})
        else:
            conn.execute(sa.text(
                "UPDATE model_assignments SET livello_ragionamento = :livello, ragiona_override = :ragiona, "
                "updated_at = now() WHERE task = :task"
            ), {"livello": prima["livello_ragionamento"], "ragiona": prima["ragiona_override"], "task": compito})
    conn.execute(sa.text(
        "INSERT INTO audit_log (actor_id, action, target_type, target_id, before, after, created_at) "
        "VALUES (NULL, :azione, 'compito', 'livelli', NULL, CAST(:prima AS jsonb), now())"
    ), {"azione": AZIONE + ".annulla", "prima": json.dumps({"righe": righe})})
