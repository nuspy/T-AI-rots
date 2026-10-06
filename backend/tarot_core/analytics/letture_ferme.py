"""Dove si fermano le letture (v9.5): dal database delle letture, non dagli eventi.

Gli eventi (`uscite.py`) dicono l'ultima azione di chi ha accettato le statistiche; le letture stesse dicono, per
TUTTE le letture aperte nel periodo (anche quelle di prima e di chi non ha accettato), fino a che punto sono arrivate:
lo stato (`readings.status`: intervista → ventaglio → scelta → rivelazione → sintesi → completata, oppure annullata),
quante risposte ha dato la persona all'intervista e quante carte ha scelto o rivelato.

- **Imbuto**: quante letture raggiungono ogni passo, la quota sul totale e quante se ne perdono dal passo prima.
- **Dove si fermano**: per le letture ferme in intervista, il numero di risposte date; in scelta, le carte già scelte;
  in rivelazione, le carte già rivelate su quelle posate.
- **Gruppi**: `iscritti` (lettura nata da un account), `anonimi` (nata senza account: per loro «completata» vuol dire
  l'anteprima, e si conta quante sono poi passate a un account).

Solo conteggi: nessun testo, nessuna persona.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Literal

from lanterna.interroga import limiti
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import DrawnCard, InterviewTurn, Reading

FUSO = "Europe/Rome"
Gruppo = Literal["tutti", "iscritti", "anonimi"]

#: Gli stati in ordine di avanzamento; `annullata` sta fuori dall'ordine.
ORDINE = ("intervista", "ventaglio", "scelta", "rivelazione", "sintesi", "completata")
PASSI = (
    ("aperte", "Lettura aperta (domanda e stesa inviate)", 0),
    ("intervista_finita", "Intervista conclusa", 1),
    ("mescolate", "Mescolate e tagliate: ventaglio aperto, scelta in corso", 2),
    ("scelte", "Carte scelte, rivelazione in corso", 3),
    ("rivelate", "Carte rivelate, interpretazione finale in corso", 4),
    ("completate", "Interpretazione finale ricevuta", 5),
)
FERMA_IN = {
    "intervista": "Ferme durante l'intervista",
    "ventaglio": "Ferme a mescolare e tagliare (ventaglio non ancora usato)",
    "scelta": "Ferme durante la scelta delle carte",
    "rivelazione": "Ferme durante la rivelazione",
    "sintesi": "Ferme mentre arriva l'interpretazione finale",
    "annullata": "Annullate",
}


def _filtro_gruppo(gruppo: Gruppo):
    if gruppo == "iscritti":
        return Reading.anon_id.is_(None)
    if gruppo == "anonimi":
        return Reading.anon_id.isnot(None)
    return None


Variante = Literal["tutte", "classica", "chat"]
Piattaforma = Literal["tutte", "web", "android", "ios", "nd"]


def _filtri_versione(variante: Variante, piattaforma: Piattaforma) -> List[Any]:
    """v9.5: la versione della lettura (le letture senza variante sono di prima della prova: classiche) e la
    piattaforma (`nd`: non dichiarata, cioè di prima o da un'app non aggiornata)."""
    filtri: List[Any] = []
    if variante == "classica":
        filtri.append(or_(Reading.variante == "classica", Reading.variante.is_(None)))
    elif variante == "chat":
        filtri.append(Reading.variante == "chat")
    if piattaforma == "nd":
        filtri.append(Reading.piattaforma.is_(None))
    elif piattaforma != "tutte":
        filtri.append(Reading.piattaforma == piattaforma)
    return filtri


async def letture_ferme(session: AsyncSession, da: date, a: date, gruppo: Gruppo = "tutti",
                        variante: Variante = "tutte", piattaforma: Piattaforma = "tutte") -> Dict[str, Any]:
    inizio, fine = limiti(da, a, FUSO)
    condizioni = [Reading.created_at >= inizio, Reading.created_at < fine, *_filtri_versione(variante, piattaforma)]
    filtro = _filtro_gruppo(gruppo)
    if filtro is not None:
        condizioni.append(filtro)

    per_stato = dict((await session.execute(
        select(Reading.status, func.count()).where(*condizioni).group_by(Reading.status)
    )).all())
    annullate = per_stato.pop("annullata", 0)
    totale = sum(per_stato.values())

    # L'imbuto: una lettura ha raggiunto il passo k se il suo stato è al k-esimo posto o oltre.
    imbuto: List[Dict[str, Any]] = []
    precedente = None
    for chiave, etichetta, k in PASSI:
        n = sum(c for s, c in per_stato.items() if s in ORDINE and ORDINE.index(s) >= k)
        imbuto.append({
            "passo": chiave, "etichetta": etichetta, "letture": n,
            "quota": round(n / totale, 4) if totale else None,
            "perse_dal_passo_prima": (precedente - n) if precedente is not None else None,
            "tasso_passaggio": round(n / precedente, 4) if precedente else None,
        })
        precedente = n

    # Dove si fermano, con il dettaglio del passo.
    risposte = (
        select(InterviewTurn.reading_id, func.count().label("n"))
        .where(InterviewTurn.ruolo == "utente").group_by(InterviewTurn.reading_id).subquery()
    )
    intervista = (await session.execute(
        select(func.coalesce(risposte.c.n, 0).label("risposte"), func.count())
        .select_from(Reading).outerjoin(risposte, risposte.c.reading_id == Reading.id)
        .where(*condizioni, Reading.status == "intervista")
        .group_by("risposte").order_by("risposte")
    )).all()

    carte = (
        select(DrawnCard.reading_id, func.count().label("posate"),
               func.count().filter(DrawnCard.rivelata).label("rivelate"))
        .where(DrawnCard.calcolata.is_(False)).group_by(DrawnCard.reading_id).subquery()
    )
    scelta = (await session.execute(
        select(func.coalesce(carte.c.posate, 0).label("posate"), func.count())
        .select_from(Reading).outerjoin(carte, carte.c.reading_id == Reading.id)
        .where(*condizioni, Reading.status == "scelta")
        .group_by("posate").order_by("posate")
    )).all()
    rivelazione = (await session.execute(
        select(func.coalesce(carte.c.rivelate, 0).label("rivelate"), func.coalesce(carte.c.posate, 0).label("posate"),
               func.count())
        .select_from(Reading).outerjoin(carte, carte.c.reading_id == Reading.id)
        .where(*condizioni, Reading.status == "rivelazione")
        .group_by("rivelate", "posate").order_by("posate", "rivelate")
    )).all()

    ferme = []
    for stato, etichetta in FERMA_IN.items():
        n = annullate if stato == "annullata" else per_stato.get(stato, 0)
        voce: Dict[str, Any] = {"stato": stato, "etichetta": etichetta, "letture": n,
                                "quota": round(n / (totale + annullate), 4) if (totale + annullate) else None}
        if stato == "intervista":
            voce["dettaglio"] = [{"etichetta": f"dopo {r} risposte" if r != 1 else "dopo 1 risposta", "letture": c}
                                 for r, c in intervista]
        elif stato == "scelta":
            voce["dettaglio"] = [{"etichetta": f"con {p} carte già scelte" if p != 1 else "con 1 carta già scelta",
                                  "letture": c} for p, c in scelta]
        elif stato == "rivelazione":
            voce["dettaglio"] = [{"etichetta": f"{r} carte rivelate su {p}", "letture": c} for r, p, c in rivelazione]
        ferme.append(voce)

    esito: Dict[str, Any] = {
        "da": da.isoformat(), "a": a.isoformat(), "gruppo": gruppo, "variante": variante, "piattaforma": piattaforma,
        "letture": totale, "annullate": annullate, "imbuto": imbuto, "ferme": ferme,
    }
    if gruppo == "anonimi":
        # Per una lettura anonima «completata» è l'anteprima: quante poi sono passate a un account.
        completate = per_stato.get("completata", 0)
        passate = (await session.execute(
            select(func.count()).where(*condizioni, Reading.status == "completata", Reading.owner_id.isnot(None))
        )).scalar_one()
        esito["anteprima"] = {"completate": completate, "passate_a_un_account": passate,
                              "quota": round(passate / completate, 4) if completate else None}
    return esito
