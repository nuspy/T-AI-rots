"""L'interpretazione AI degli analytics (v8): una sezione della console → fatti → modello → verifica.

Per ogni sezione si rifanno lato server le stesse interrogazioni della console (le collezioni di
`viste.py`, gli imbuti, le coorti), sempre col periodo precedente e con la **soglia k** attiva: al
modello arrivano solo aggregati di almeno cinque persone, mai righe di singoli. I numeri diventano
fatti numerati (`lanterna.insight`); il modello (`Compito.ANALISI_DATI`, scelto in console) li mette
in relazione; la risposta si verifica contro i fatti e si salva con i fatti stessi, così resta
controllabile anche dopo.

Una chiamata sola per clic: niente catene di richieste, niente costi a sorpresa.
"""
from __future__ import annotations

import logging
import time
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from lanterna.analisi import coorti, imbuto
from lanterna.insight import Fatti, da_coorti, da_imbuto, da_risultato, prompt, valida
from lanterna.interroga import Interrogazione, esegui, limiti
from sqlalchemy import desc, select, update
from sqlalchemy.dialects.postgresql import insert

from ..domain.analytics_models import TABELLE
from ..llm.base import GenerationError
from ..tarot.llm import genera_json, richiesta
from . import catalogo, imbuti, viste

logger = logging.getLogger(__name__)

FUSO = "Europe/Rome"
K_MINIMO = 5

SEZIONI: Dict[str, str] = {
    "traffico": "Traffico",
    "utenti": "Utenti",
    "ricavi": "Ricavi",
    "letture": "Letture",
    "imbuti": "Imbuti",
    "panoramica": "Panoramica (tutte le sezioni)",
    "vista": "Vista dell'Esploratore",
}

DEFINIZIONI = """- Le visite si misurano senza cookie: «visitatori» somma gli univoci di ogni giorno; lo stesso
  browser in due giorni conta due volte. Chi blocca gli script non è contato.
- Paese e città vengono dall'IP e sono indicativi (spesso la città del fornitore di connessione).
- Primo canale e campagna esistono solo per chi si è iscritto dopo l'avvio degli analytics e non si
  è opposto; le «visite prima dell'iscrizione» solo per chi ha accettato i cookie.
- I ricavi sono i pagamenti conclusi, dopo gli sconti; i rinnovi automatici non sono inclusi.
- Gruppi con meno di 5 persone non sono mostrati.
- I giorni sono italiani (Europe/Rome). Il periodo precedente ha la stessa durata."""


def _con_confronto(q: Interrogazione) -> Interrogazione:
    # Ogni fatto porta il periodo precedente: senza, il modello non distingue un numero da una variazione.
    return q.model_copy(update={"confronto": q.confronto or "precedente"})


async def _da_collezione(session, fatti: Fatti, nome: str, da: date, a: date, etichetta: Optional[str] = None) -> None:
    _, costruisci = viste.COLLEZIONI[nome]
    for titolo, q, _ in costruisci(da, a):
        r = await esegui(session, catalogo.CATALOGO, _con_confronto(q), fuso=FUSO, k_minimo=K_MINIMO)
        da_risultato(fatti, f"{etichetta or viste.COLLEZIONI[nome][0]} · {titolo}", r)


async def _da_imbuto(session, fatti: Fatti, nome: str, da: date, a: date) -> None:
    etichetta, per, passi = imbuti.IMBUTI[nome]
    inizio, fine = limiti(da, a, FUSO)
    esito = await imbuto(session, TABELLE, passi, inizio, fine, per=per,
                         segmento="canale" if per == "sessione" else None)
    # Anche i segmenti degli imbuti rispettano la soglia: un canale con meno di 5 visite non si nomina.
    if esito.get("segmenti"):
        esito["segmenti"] = [s for s in esito["segmenti"] if s["passi"][0]["n"] >= K_MINIMO]
    da_imbuto(fatti, f"Imbuto · {etichetta}", esito)


async def _da_coorti(session, fatti: Fatti, tipo: str) -> None:
    etichetta, attivita, somma = catalogo.COORTI[tipo]
    righe = await coorti(session, catalogo.primo_iscrizione(), attivita(), granularita="mese", periodi=6,
                         somma=somma, fuso=FUSO)
    da_coorti(fatti, f"Coorti · {etichetta}", righe, somma)


async def raccogli_fatti(session, sezione: str, da: date, a: date, vista: Optional[Interrogazione] = None) -> Fatti:
    fatti = Fatti()
    if sezione == "traffico":
        await _da_collezione(session, fatti, "traffico", da, a)
        await _da_imbuto(session, fatti, "iscrizione", da, a)
    elif sezione == "utenti":
        await _da_collezione(session, fatti, "utenti", da, a)
        await _da_imbuto(session, fatti, "iscrizione", da, a)
        await _da_coorti(session, fatti, "visite")
    elif sezione == "ricavi":
        await _da_collezione(session, fatti, "ricavi", da, a)
        await _da_imbuto(session, fatti, "acquisto", da, a)
        await _da_imbuto(session, fatti, "negozio", da, a)
        await _da_coorti(session, fatti, "spesa")
    elif sezione == "letture":
        await _da_collezione(session, fatti, "letture", da, a)
        await _da_imbuto(session, fatti, "lettura", da, a)
        await _da_coorti(session, fatti, "letture")
    elif sezione == "imbuti":
        for nome in imbuti.IMBUTI:
            await _da_imbuto(session, fatti, nome, da, a)
    elif sezione == "panoramica":
        await _da_collezione(session, fatti, "rapporto", da, a, "Panoramica")
        await _da_imbuto(session, fatti, "lettura", da, a)
        await _da_imbuto(session, fatti, "acquisto", da, a)
    elif sezione == "vista":
        if vista is None:
            raise ValueError("manca l'interrogazione della vista")
        q = _con_confronto(vista.model_copy(update={"da": da, "a": a}))
        r = await esegui(session, catalogo.CATALOGO, q, fuso=FUSO, k_minimo=K_MINIMO)
        da_risultato(fatti, catalogo.CATALOGO[q.sorgente].etichetta, r, righe_max=12)
    else:
        raise ValueError(f"sezione sconosciuta: {sezione}")
    return fatti


# ---- impostazioni ------------------------------------------------------------------------------

CHIAVE_CONTESTO = "contesto_ai"


async def leggi_contesto(session) -> str:
    t = TABELLE.impostazioni
    valore = (await session.execute(select(t.c.valore).where(t.c.chiave == CHIAVE_CONTESTO))).scalar()
    return str((valore or {}).get("testo", ""))


async def scrivi_contesto(session, testo: str) -> None:
    t = TABELLE.impostazioni
    valore = {"testo": testo[:4000]}
    await session.execute(
        insert(t).values(chiave=CHIAVE_CONTESTO, valore=valore)
        .on_conflict_do_update(index_elements=[t.c.chiave], set_={"valore": valore, "updated_at": datetime.now(ZoneInfo("UTC"))})
    )


# ---- l'analisi -----------------------------------------------------------------------------------


def periodo_di(giorni: int) -> tuple[date, date]:
    a = datetime.now(ZoneInfo(FUSO)).date()
    return a - timedelta(days=giorni - 1), a


async def _precedente(session, sezione: str) -> Optional[Dict[str, Any]]:
    t = TABELLE.analisi
    riga = (await session.execute(
        select(t.c.created_at, t.c.risposta, t.c.azione_adottata)
        .where(t.c.sezione == sezione, t.c.risposta.is_not(None))
        .order_by(desc(t.c.created_at)).limit(1)
    )).first()
    if riga is None:
        return None
    return {"quando": riga.created_at.date().isoformat(), "sintesi": (riga.risposta or {}).get("sintesi", ""),
            "azione": riga.azione_adottata}


def riga_json(r) -> Dict[str, Any]:
    return {
        "id": str(r.id), "sezione": r.sezione, "parametri": r.parametri, "fatti": r.fatti, "risposta": r.risposta,
        "errore": r.errore, "modello": r.modello, "durata_ms": r.durata_ms, "giudizio": r.giudizio,
        "azione_adottata": r.azione_adottata, "creata_il": r.created_at.isoformat() if r.created_at else None,
    }


async def analizza(
    session, provider, *, sezione: str, giorni: int, vista: Optional[Interrogazione] = None,
    autore_id: Optional[int] = None, periodo: Optional[tuple[date, date]] = None,
) -> Dict[str, Any]:
    """Calcola i fatti, chiede al modello, verifica, salva. Solleva `GenerationError` se il modello
    non risponde (la riga resta salvata con l'errore). `periodo` (da, a) sostituisce «gli ultimi
    `giorni` fino a oggi»: serve al rapporto, che guarda la settimana conclusa."""
    if sezione not in SEZIONI:
        raise ValueError(f"sezione sconosciuta: {sezione}")
    da, a = periodo or periodo_di(giorni)
    giorni = (a - da).days + 1
    fatti = await raccogli_fatti(session, sezione, da, a, vista)
    contesto = await leggi_contesto(session)
    precedente = await _precedente(session, sezione)
    sistema, utente = prompt(SEZIONI[sezione], f"dal {da.isoformat()} al {a.isoformat()} ({giorni} giorni)",
                             contesto, DEFINIZIONI, fatti, precedente)
    parametri = {"giorni": giorni, "da": da.isoformat(), "a": a.isoformat(),
                 "vista": vista.model_dump(mode="json") if vista else None}
    riga_id = uuid.uuid4()
    inizio = time.monotonic()
    risposta, errore = None, None
    if not fatti.elenco:
        risposta = valida({"sintesi": "Nel periodo non ci sono dati sufficienti da interpretare.",
                           "dati_mancanti": ["Visite o eventi nel periodo scelto."]}, fatti)
    else:
        try:
            grezza = await genera_json(provider, richiesta([sistema], utente, temperatura=0.3, max_tokens=5000))
            risposta = valida(grezza, fatti)
        except GenerationError as exc:
            errore = str(exc)[:500]
    durata = int((time.monotonic() - inizio) * 1000)
    t = TABELLE.analisi
    await session.execute(insert(t).values(
        id=riga_id, sezione=sezione, parametri=parametri, fatti=fatti.json(), risposta=risposta, errore=errore,
        modello=getattr(provider, "model", None) or getattr(provider, "name", None), durata_ms=durata, creato_da=autore_id,
    ))
    await session.commit()
    riga = (await session.execute(select(t).where(t.c.id == riga_id))).first()
    if errore:
        raise GenerationError(errore)
    return riga_json(riga)


async def storico(session, sezione: Optional[str], limite: int = 20) -> List[Dict[str, Any]]:
    t = TABELLE.analisi
    q = select(t).order_by(desc(t.c.created_at)).limit(limite)
    if sezione:
        q = q.where(t.c.sezione == sezione)
    return [riga_json(r) for r in (await session.execute(q)).all()]


async def annota(session, analisi_id: uuid.UUID, *, giudizio: Optional[int], azione: Optional[str],
                 campi: set) -> Optional[Dict[str, Any]]:
    t = TABELLE.analisi
    valori: Dict[str, Any] = {}
    if "giudizio" in campi:
        valori["giudizio"] = giudizio
    if "azione_adottata" in campi:
        valori["azione_adottata"] = (azione or "").strip()[:1000] or None
    if valori:
        await session.execute(update(t).where(t.c.id == analisi_id).values(**valori))
        await session.commit()
    riga = (await session.execute(select(t).where(t.c.id == analisi_id))).first()
    return riga_json(riga) if riga else None
