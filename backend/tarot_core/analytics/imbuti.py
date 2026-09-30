"""Gli imbuti predefiniti di TAROTS chat (v8).

I percorsi sono quelli visibili nel browser, in tutte le lingue (inglese alla radice, italiano sotto
`/it`, vedi `frontend/lib/percorsi.ts`). Le fasi della lettura sono quelle di `leggi/lettura.tsx`
(evento `lettura_fase`).
"""
from __future__ import annotations

from typing import Dict, List, Literal, Tuple

from lanterna.analisi import Passo

from . import eventi as ev

Per = Literal["sessione", "utente"]

IMBUTI: Dict[str, Tuple[str, Per, List[Passo]]] = {
    "lettura": (
        "Lettura: dalla pagina al responso",
        "sessione",
        [
            Passo("page_view", "Apre la pagina della lettura", percorsi=("/leggi",)),
            Passo("lettura_fase", "Sceglie la stesa", {"fase": "stesa"}),
            Passo("lettura_fase", "Intervista", {"fase": "intervista"}),
            Passo("lettura_fase", "Sceglie le carte", {"fase": "scelta"}),
            Passo("lettura_fase", "Rivela le carte", {"fase": "rivelazione"}),
            Passo("lettura_fase", "Responso", {"fase": "completata"}),
        ],
    ),
    "iscrizione": (
        "Visita → iscrizione",
        "sessione",
        [
            Passo("page_view", "Visita"),
            Passo("cta_iscrizione", "Tocca «Registrati»"),
            Passo(ev.REGISTRAZIONE, "Si iscrive"),
        ],
    ),
    "acquisto": (
        "Prezzi → acquisto (iscritti)",
        "utente",
        [
            Passo("page_view", "Apre i prezzi", percorsi=("/pricing", "/it/piano")),
            Passo("piano_scelto", "Sceglie un piano"),
            Passo(ev.CHECKOUT_AVVIATO, "Va al pagamento"),
            Passo(ev.ACQUISTO, "Paga"),
        ],
    ),
    "negozio": (
        "Negozio → ordine (iscritti)",
        "utente",
        [
            Passo("page_view", "Apre il mazzo", percorsi=("/deck", "/it/mazzo")),
            Passo("carrello_aggiunto", "Aggiunge al carrello"),
            Passo(ev.CHECKOUT_AVVIATO, "Va al pagamento", {"tipo": "ordine"}),
            Passo(ev.ACQUISTO, "Paga", {"tipo": "ordine"}),
        ],
    ),
}


def descrivi() -> Dict[str, Dict]:
    return {
        nome: {"etichetta": etichetta, "per": per, "passi": [p.etichetta or p.evento for p in passi]}
        for nome, (etichetta, per, passi) in IMBUTI.items()
    }
