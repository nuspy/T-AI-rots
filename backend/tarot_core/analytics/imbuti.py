"""Gli imbuti predefiniti di TAROTS chat (v8).

I percorsi sono quelli visibili nel browser, in tutte le lingue (inglese alla radice, italiano sotto
`/it`, vedi `frontend/lib/percorsi.ts`). Le fasi della lettura sono quelle di `leggi/lettura.tsx`
(evento `lettura_fase`).

La v2 (`/v2`, `/it/v2`: `frontend/v2/lettura/lettura.tsx`) ha imbuti suoi: la lettura comincia con la
preparazione (domanda, tipo, stesa) invece della scelta della stesa, e gli eventi della sua pagina portano il
percorso della v2. Ogni passo della lettura è legato al percorso, così i due siti non si mescolano.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Tuple

from lanterna.analisi import Passo

from . import eventi as ev

Per = Literal["sessione", "utente"]

_LEGGI = ("/leggi",)
_LEGGI_V2 = ("/v2/read", "/it/v2/read")

IMBUTI: Dict[str, Tuple[str, Per, List[Passo]]] = {
    "lettura": (
        "Lettura: dalla pagina al responso",
        "sessione",
        [
            Passo("page_view", "Apre la pagina della lettura", percorsi=_LEGGI),
            Passo("lettura_fase", "Sceglie la stesa", {"fase": "stesa"}, percorsi=_LEGGI),
            Passo("lettura_fase", "Intervista", {"fase": "intervista"}, percorsi=_LEGGI),
            Passo("lettura_fase", "Sceglie le carte", {"fase": "scelta"}, percorsi=_LEGGI),
            Passo("lettura_fase", "Rivela le carte", {"fase": "rivelazione"}, percorsi=_LEGGI),
            Passo("lettura_fase", "Responso", {"fase": "completata"}, percorsi=_LEGGI),
        ],
    ),
    "lettura_v2": (
        "v2 · Lettura: dalla domanda all'interpretazione",
        "sessione",
        [
            Passo("page_view", "Apre la lettura (v2)", percorsi=_LEGGI_V2),
            Passo("lettura_fase", "Prepara domanda e stesa", {"fase": "preparazione"}, percorsi=_LEGGI_V2),
            Passo("lettura_fase", "Intervista", {"fase": "intervista"}, percorsi=_LEGGI_V2),
            Passo("lettura_fase", "Mescola e taglia", {"fase": "taglio"}, percorsi=_LEGGI_V2),
            Passo("lettura_fase", "Sceglie le carte", {"fase": "scelta"}, percorsi=_LEGGI_V2),
            Passo("lettura_fase", "Rivela le carte", {"fase": "rivelazione"}, percorsi=_LEGGI_V2),
            Passo("lettura_fase", "Interpretazione", {"fase": "completata"}, percorsi=_LEGGI_V2),
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
    "acquisto_v2": (
        "v2 · Prezzi → acquisto (iscritti)",
        "utente",
        [
            Passo("page_view", "Apre i prezzi (v2)", percorsi=("/v2/pricing", "/it/v2/pricing")),
            Passo("piano_scelto", "Sceglie un piano", percorsi=("/v2/pricing", "/it/v2/pricing")),
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
