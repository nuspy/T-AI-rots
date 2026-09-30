"""Le annotazioni sul calendario (v8): campagne, rilasci, articoli, cambi di prezzo, fatti esterni.

Compaiono sui grafici della console, nel rapporto della settimana e fra i fatti dati all'AI: sono il
contesto che i numeri da soli non hanno («la crescita comincia il giorno della campagna»).
"""
from __future__ import annotations

from datetime import date
from typing import Any, List, Optional

from lanterna.insight import Fatti
from sqlalchemy import and_, func, or_, select

from ..domain.analytics_models import TABELLE

ETICHETTE = {
    "campagna": "campagna", "rilascio": "rilascio del sito", "contenuto": "contenuto pubblicato",
    "prezzo": "cambio di prezzo", "esterno": "fatto esterno", "altro": "nota",
}


async def nel_periodo(session, da: Optional[date], a: Optional[date]) -> List[Any]:
    """Le annotazioni che toccano il periodo (anche solo in parte), in ordine di giorno."""
    t = TABELLE.annotazioni
    condizioni = []
    if a is not None:
        condizioni.append(t.c.giorno <= a)
    if da is not None:
        condizioni.append(or_(func.coalesce(t.c.fine, t.c.giorno) >= da))
    q = select(t).order_by(t.c.giorno, t.c.id)
    if condizioni:
        q = q.where(and_(*condizioni))
    return list((await session.execute(q.limit(200))).mappings().all())


def descrivi(x) -> str:
    periodo = x["giorno"].isoformat() + (f" – {x['fine'].isoformat()}" if x["fine"] else "")
    return f"{periodo}: {x['titolo']} ({ETICHETTE.get(x['tipo'], x['tipo'])})" + (f". {x['nota']}" if x["nota"] else "")


async def come_fatti(session, fatti: Fatti, da: date, a: date) -> None:
    for x in await nel_periodo(session, da, a):
        # Nessun numero: il valore è la data, che il modello cita col giorno.
        fatti.aggiungi("Calendario", descrivi(x) + ".")
