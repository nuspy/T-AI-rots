"""Gli schemi JSON rigorosi delle risposte strutturate, per fase («# Compito: …» del prompt).

Servono a `response_format: {"type": "json_schema", "json_schema": {..., "strict": true}}`: il fornitore che lo
supporta (Nebius, da provare) vincola la generazione allo schema, e una risposta malformata non può più arrivare. Si
accendono per compito dalla console (`json_schema`, spento per default); dove il fornitore li rifiuta si ripiega da sé
su `json_object` e poi sul testo, e l'esito si ricorda per tutta la vita del processo
(`openai_compatible._DIALETTI_NOTI`).

Lo schema si sceglie dalla **fase**, non dal compito: lo stesso compito può fare chiamate diverse (l'estrazione delle
memorie di prima e lo stato sintetico girano entrambe come `memoria_estrazione`, con risposte diverse). Una fase senza
schema negozia come sempre.

Gli schemi sono nella forma che il modo `strict` vuole: tutte le proprietà richieste, `additionalProperties: false`.
Dove una risposta ha due forme (l'intervista: una domanda o il riassunto finale) entrambi i campi ci sono e quello che
non serve resta vuoto — il codice che legge le risposte lo tratta già così.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

_CAMPI = ["amore", "lavoro", "salute", "famiglia", "denaro", "spirituale", "altro"]


def _oggetto(proprieta: Dict[str, Any]) -> Dict[str, Any]:
    return {"type": "object", "properties": proprieta, "required": list(proprieta), "additionalProperties": False}


SCHEMI: Dict[str, Dict[str, Any]] = {
    "intervista": _oggetto({
        "completo": {"type": "boolean"},
        "domanda": {"type": "string"},
        "riassunto": {"type": "string"},
    }),
    "validazione": _oggetto({
        "valida": {"type": "boolean"},
        "motivo": {"type": "string"},
    }),
    "giudizio": _oggetto({
        "esito": {"type": "string", "enum": ["ok", "riscrivi", "blocca"]},
        "violazioni": {"type": "array", "items": _oggetto({
            "regola": {"type": "string"}, "motivo": {"type": "string"}, "estratto": {"type": "string"},
        })},
    }),
    "chat_proattiva": _oggetto({
        "messaggio": {"type": "string"},
        "proposta": {"anyOf": [
            {"type": "null"},
            _oggetto({
                "argomento": {"type": "string"},
                "tema": {"type": "string", "enum": ["amore", "coppia", "lavoro", "generico"]},
            }),
        ]},
    }),
    "memoria_stato": _oggetto({
        "aggiungi": {"type": "array", "items": _oggetto({
            "categoria": {"type": "string", "enum": ["stabile", "volatile"]},
            "campo": {"type": "string", "enum": _CAMPI},
            "testo": {"type": "string"},
        })},
        "conferma": {"type": "array", "items": {"type": "string"}},
        "rimuovi": {"type": "array", "items": {"type": "string"}},
        "campo_quesito": {"type": "string", "enum": _CAMPI},
    }),
    #: La chiamata unica delle interpretazioni (`tarot/interpretazione.py`): una voce per carta. La chiamata singola
    #: di ripiego (fase `interpretazione`) resta testo e non ha schema.
    "interpretazione_unica": _oggetto({
        "carte": {"type": "array", "items": _oggetto({
            "posizione": {"type": "integer"},
            # Prima del testo: costringe il modello a ripetere l'orientamento della carta (`interpretazione.dividi`).
            "orientamento": {"type": "string", "enum": ["dritta", "rovesciata"]},
            "interpretazione": {"type": "string"},
        })},
    }),
}

#: I compiti che rispondono in JSON e per cui la console offre lo schema rigoroso.
COMPITI_CON_SCHEMA = (
    "intervista", "validazione", "interpretazione", "giudizio", "chat_proattiva", "memoria_estrazione",
)


def schema_per(fase: str) -> Optional[Dict[str, Any]]:
    """Lo schema della fase (`intervista.riassunto` usa quello dell'intervista), o `None`."""
    return SCHEMI.get(fase) or SCHEMI.get(fase.split(".")[0]) if fase else None


def formato_rigoroso(fase: str) -> Optional[Dict[str, Any]]:
    """Il `response_format` rigoroso per la fase, o `None` se la fase non ha schema."""
    schema = schema_per(fase)
    if schema is None:
        return None
    return {"type": "json_schema", "json_schema": {"name": fase.replace(".", "_"), "strict": True, "schema": schema}}
