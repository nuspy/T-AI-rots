"""Gli obiettivi di conversione di TAROTS chat (v8), configurati dalla console.

Un obiettivo è un evento (es. `acquisto`, o `lettura_fase` con `fase=completata`) o una pagina
(prefissi di percorso, es. `/pricing,/it/piano`). Si misurano sessioni che lo raggiungono, quota sulle
sessioni del periodo e confronto col periodo precedente; entrano nel rapporto e nei fatti dell'AI.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from lanterna.insight import Fatti
from lanterna.interroga import limiti
from lanterna.obiettivi import conversioni
from sqlalchemy import select

from ..domain.analytics_models import TABELLE

FUSO = "Europe/Rome"


async def attivi(session) -> List[Dict[str, Any]]:
    t = TABELLE.obiettivi
    return [dict(x) for x in (await session.execute(select(t).where(t.c.attivo.is_(True)).order_by(t.c.id))).mappings()]


async def nel_periodo(session, da: date, a: date) -> Dict[str, Any]:
    elenco = await attivi(session)
    durata = (a - da).days + 1
    pda, pa = da - timedelta(days=durata), da - timedelta(days=1)
    ora = await conversioni(session, TABELLE, elenco, *limiti(da, a, FUSO))
    prima = {x["id"]: x for x in await conversioni(session, TABELLE, elenco, *limiti(pda, pa, FUSO))}
    for x in ora:
        p = prima.get(x["id"], {})
        x["sessioni_prima"] = p.get("sessioni")
        x["tasso_prima"] = p.get("tasso")
        x["proprieta"] = next((o["proprieta"] for o in elenco if o["id"] == x["id"]), {})
    return {"da": da.isoformat(), "a": a.isoformat(), "obiettivi": ora}


async def risultati(session, giorni: int) -> Dict[str, Any]:
    a = datetime.now(ZoneInfo(FUSO)).date()
    return await nel_periodo(session, a - timedelta(days=giorni - 1), a)


async def come_fatti(session, fatti: Fatti, da: date, a: date) -> None:
    for x in (await nel_periodo(session, da, a))["obiettivi"]:
        testo = f"Obiettivo «{x['nome']}»: raggiunto in {x['sessioni']} sessioni"
        valori = [x["sessioni"], x["completamenti"]]
        if x["tasso"] is not None:
            testo += f" ({x['tasso'] * 100:.1f}% delle sessioni)"
            valori.append(x["tasso"] * 100)
        if x["sessioni_prima"] is not None:
            testo += f"; periodo precedente {x['sessioni_prima']}"
            valori.append(x["sessioni_prima"])
            if x["tasso_prima"] is not None:
                testo += f" ({x['tasso_prima'] * 100:.1f}%)"
                valori.append(x["tasso_prima"] * 100)
        fatti.aggiungi("Obiettivi", testo + ".", *valori)
