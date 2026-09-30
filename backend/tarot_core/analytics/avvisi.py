"""Gli avvisi automatici di TAROTS chat (v8): ogni notte, dopo il riepilogo, si confronta ieri con i
28 giorni prima per poche metriche vitali; se qualcosa esce dal normale parte un'email ai destinatari
del rapporto (si spegne in console → Analytics → Rapporti).

Le metriche sono quelle che dicono se il servizio funziona e rende: visite, iscrizioni, letture aperte
e completate, acquisti; e gli errori del modello nel responso (solo in salita). I ricavi no: con pochi
acquisti al giorno sono troppo irregolari per un «normale».
"""
from __future__ import annotations

import html
import logging
import smtplib
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from lanterna import posta
from lanterna.avvisi import Avviso, valuta
from lanterna.interroga import Interrogazione, esegui
from sqlalchemy.dialects.postgresql import insert

from ..domain.analytics_models import TABELLE
from ..settings import get_settings
from . import catalogo, rapporto

logger = logging.getLogger(__name__)

FUSO = "Europe/Rome"
STORIA_GIORNI = 28

#: nome, etichetta, sorgente, misura, filtri, cattiva
METRICHE: List[Tuple[str, str, str, str, list, bool]] = [
    ("visite", "Visite", "visite", "sessioni", [], False),
    ("iscrizioni", "Nuovi iscritti", "utenti", "utenti", [], False),
    ("letture_aperte", "Letture aperte", "letture", "letture", [], False),
    ("letture_completate", "Letture completate", "letture", "completate", [], False),
    ("acquisti", "Acquisti", "acquisti", "acquisti", [], False),
    ("errori_responso", "Responsi non generati (errori del modello)", "eventi", "eventi",
     [{"dimensione": "nome", "valori": ["lettura_errore"]}], True),
]


async def serie_giornaliera(session, sorgente: str, misura: str, filtri: list, da: date, a: date) -> Dict[str, float]:
    q = Interrogazione(sorgente=sorgente, misure=[misura], filtri=filtri, da=da, a=a, granularita="giorno", limite=1000)
    r = await esegui(session, catalogo.CATALOGO, q, fuso=FUSO)
    return {str(x["periodo"])[:10]: float(x[misura] or 0) for x in r.righe}


async def controlla(session, *, adesso: Optional[datetime] = None) -> Tuple[date, List[Avviso]]:
    """Gli avvisi di ieri (giorno italiano). Non invia nulla."""
    oggi = (adesso or datetime.now(ZoneInfo(FUSO))).astimezone(ZoneInfo(FUSO)).date()
    ieri = oggi - timedelta(days=1)
    inizio = ieri - timedelta(days=STORIA_GIORNI)
    giorni = [(inizio + timedelta(days=i)).isoformat() for i in range(STORIA_GIORNI)]
    trovati: List[Avviso] = []
    for nome, etichetta, sorgente, misura, filtri, cattiva in METRICHE:
        valori = await serie_giornaliera(session, sorgente, misura, filtri, inizio, ieri)
        storia = [valori.get(g, 0.0) for g in giorni]
        # Una metrica che non è mai esistita (il servizio è giovane) non ha un normale.
        if not any(storia) and not cattiva:
            continue
        avviso = valuta(nome, etichetta, storia, valori.get(ieri.isoformat(), 0.0), cattiva=cattiva)
        if avviso:
            trovati.append(avviso)
    return ieri, trovati


async def controlla_e_avvisa(session, *, adesso: Optional[datetime] = None) -> Dict[str, Any]:
    """Il passo notturno: se ci sono avvisi e gli avvisi sono accesi, email e registro."""
    ieri, trovati = await controlla(session, adesso=adesso)
    esito: Dict[str, Any] = {"giorno": ieri.isoformat(), "avvisi": [a.testo() for a in trovati], "inviato": False}
    opzioni = await rapporto.opzioni(session)
    if not trovati or not opzioni.get("avvisi", True):
        return esito
    destinatari = await rapporto.destinatari_attivi(session)
    config = rapporto.config_smtp()
    if not config.configurato or not destinatari:
        riuscito, dettaglio = False, "avvisi non inviati: SMTP o destinatari mancanti"
    else:
        console = f"{get_settings().web_public_url.rstrip('/')}/admin/analytics"
        voci = "".join(f"<li>{html.escape(a.testo())}</li>" for a in trovati)
        corpo = posta.pagina_html(
            "Avviso analytics", f"Ieri, {ieri.strftime('%d/%m/%Y')}, qualcosa è uscito dal normale",
            [f"<ul>{voci}</ul>", f'<p>Il normale è la mediana dei {STORIA_GIORNI} giorni precedenti. '
             f'Dettagli: <a href="{console}">{console}</a></p>'],
        )
        testo = "\n".join([f"Avviso analytics — {ieri.isoformat()}"] + [f"- {a.testo()}" for a in trovati] + ["", console])
        oggetto = f"TAROTS chat — avviso: {trovati[0].etichetta.lower()}" + (f" e altri {len(trovati) - 1}" if len(trovati) > 1 else "")
        try:
            esiti = posta.invia(config, [posta.componi(config, d, oggetto, testo, corpo) for d in destinatari])
            falliti = [d for d, e in esiti.items() if e != "ok"]
            riuscito = not falliti
            dettaglio = "; ".join(a.testo() for a in trovati)[:900] + (f" — non recapitato a {', '.join(falliti)}" if falliti else "")
        except (OSError, smtplib.SMTPException) as errore:
            riuscito, dettaglio = False, f"errore SMTP: {errore}"[:1000]
    await session.execute(insert(TABELLE.invii).values(
        id=uuid.uuid4(), tipo="avviso", da=ieri, a=ieri, destinatari=destinatari, riuscito=riuscito, dettaglio=dettaglio,
    ))
    await session.commit()
    esito.update(inviato=riuscito, dettaglio=dettaglio)
    return esito
