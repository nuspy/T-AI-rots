"""Il rapporto settimanale degli analytics (v8): ogni lunedì poco dopo mezzanotte, per la settimana
appena conclusa (lunedì-domenica, giorni italiani), a chi è in elenco nella console.

Contenuto: i numeri principali col confronto sulla settimana prima, canali, campagne e pagine più
viste, l'imbuto della lettura, e — se acceso in console — la sintesi dell'interpretazione AI con le
sole voci **verificate**. In allegato l'Excel della collezione «rapporto». Soglia k attiva ovunque:
una email esce dal sistema, e non deve contenere gruppi di meno di cinque persone.
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
from lanterna.analisi import imbuto
from lanterna.esporta import xlsx_da
from lanterna.insight import scrivi
from lanterna.interroga import Interrogazione, esegui, limiti
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from ..domain.analytics_models import TABELLE
from ..settings import get_settings
from . import catalogo, imbuti, viste

logger = logging.getLogger(__name__)

FUSO = "Europe/Rome"
K_MINIMO = 5
CHIAVE_OPZIONI = "rapporto"


def settimana_conclusa(adesso: Optional[datetime] = None) -> Tuple[date, date]:
    """Il lunedì e la domenica dell'ultima settimana intera prima di oggi."""
    oggi = (adesso or datetime.now(ZoneInfo(FUSO))).astimezone(ZoneInfo(FUSO)).date()
    lunedi_corrente = oggi - timedelta(days=oggi.weekday())
    return lunedi_corrente - timedelta(days=7), lunedi_corrente - timedelta(days=1)


def config_smtp() -> posta.ConfigSmtp:
    s = get_settings()
    return posta.ConfigSmtp(
        host=s.smtp_host, porta=s.smtp_porta, utente=s.smtp_utente, password=s.smtp_password,
        mittente=s.smtp_mittente, nome_mittente="TAROTS chat", ssl=s.smtp_ssl,
    )


async def opzioni(session) -> Dict[str, Any]:
    t = TABELLE.impostazioni
    valore = (await session.execute(select(t.c.valore).where(t.c.chiave == CHIAVE_OPZIONI))).scalar()
    return {"ai": False, **(valore or {})}


async def scrivi_opzioni(session, valori: Dict[str, Any]) -> None:
    t = TABELLE.impostazioni
    await session.execute(
        insert(t).values(chiave=CHIAVE_OPZIONI, valore=valori)
        .on_conflict_do_update(index_elements=[t.c.chiave], set_={"valore": valori})
    )


async def destinatari_attivi(session) -> List[str]:
    t = TABELLE.destinatari
    return list((await session.execute(select(t.c.email).where(t.c.attivo.is_(True)).order_by(t.c.email))).scalars())


# ---- contenuto -----------------------------------------------------------------------------------

KPI = [
    ("visite", "sessioni", "Visite (sessioni)", "intero"),
    ("visite", "visitatori", "Visitatori (univoci giornalieri)", "intero"),
    ("utenti", "utenti", "Nuovi iscritti", "intero"),
    ("letture", "letture", "Letture aperte", "intero"),
    ("letture", "completate", "Letture completate", "intero"),
    ("acquisti", "ricavi", "Ricavi pacchetti e abbonamenti", "euro"),
    ("ordini", "ricavi", "Ricavi del negozio", "euro"),
]


def _variazione(ora: Optional[float], prima: Optional[float]) -> str:
    if ora is None or prima is None:
        return "—"
    if not prima:
        return "nuovo" if ora else "="
    return f"{(ora - prima) / prima * 100:+.0f}%"


async def _kpi(session, da: date, a: date) -> List[List[str]]:
    righe = []
    per_sorgente: Dict[str, List[Tuple[str, str, str]]] = {}
    for sorgente, misura, etichetta, formato in KPI:
        per_sorgente.setdefault(sorgente, []).append((misura, etichetta, formato))
    risultati = {}
    for sorgente, misure in per_sorgente.items():
        q = Interrogazione(sorgente=sorgente, misure=[m for m, _, _ in misure], da=da, a=a, confronto="precedente")
        risultati[sorgente] = await esegui(session, catalogo.CATALOGO, q, fuso=FUSO)
    for sorgente, misura, etichetta, formato in KPI:
        r = risultati[sorgente]
        ora = r.totali.get(misura)
        prima = (r.confronto or {}).get("totali", {}).get(misura)
        righe.append([etichetta, scrivi(ora, formato), scrivi(prima, formato), _variazione(ora, prima)])
    return righe


async def _classifica(session, q: Interrogazione, dimensione: str, misura: str, quante: int = 5) -> List[List[str]]:
    r = await esegui(session, catalogo.CATALOGO, q, fuso=FUSO, k_minimo=K_MINIMO)
    return [[str(x[dimensione]), scrivi(x[misura])] for x in r.righe[:quante]]


async def componi_rapporto(session, da: date, a: date, *, con_ai: bool = False, provider=None) -> Dict[str, Any]:
    """Titolo, testo, HTML e allegato del rapporto. Non invia niente."""
    kpi = await _kpi(session, da, a)
    base = {"da": da, "a": a}
    canali = await _classifica(session, Interrogazione(sorgente="visite", misure=["sessioni"], dimensioni=["canale"], **base), "canale", "sessioni")
    campagne = await _classifica(session, Interrogazione(sorgente="visite", misure=["sessioni"], dimensioni=["campagna"], **base), "campagna", "sessioni")
    pagine = await _classifica(session, Interrogazione(
        sorgente="eventi", misure=["eventi"], dimensioni=["percorso"],
        filtri=[{"dimensione": "nome", "valori": ["page_view"]}], **base), "percorso", "eventi")
    etichetta_imbuto, per, passi = imbuti.IMBUTI["lettura"]
    inizio, fine = limiti(da, a, FUSO)
    esito = await imbuto(session, TABELLE, passi, inizio, fine, per=per)
    righe_imbuto = [[p["etichetta"], str(p["n"]), scrivi((p["dal_primo"] or 0), "percento")] for p in esito["passi"]]

    blocchi = [
        posta.tabella_html("I numeri della settimana", ["", "Settimana", "Settimana prima", "Variazione"], kpi),
        posta.tabella_html("Canali", ["Canale", "Sessioni"], canali),
        posta.tabella_html("Campagne", ["Campagna", "Sessioni"], campagne),
        posta.tabella_html("Pagine più viste", ["Pagina", "Viste"], pagine),
        posta.tabella_html(f"Imbuto: {etichetta_imbuto}", ["Passo", "Visite", "Dal primo"], righe_imbuto),
    ]
    testo = [f"TAROTS chat — settimana dal {da.isoformat()} al {a.isoformat()}", ""]
    testo += [f"{r[0]}: {r[1]} (prima {r[2]}, {r[3]})" for r in kpi]

    sintesi_ai = None
    if con_ai and provider is not None:
        from . import ai
        from ..llm.base import GenerationError

        try:
            analisi = await ai.analizza(session, provider, sezione="panoramica", giorni=7, periodo=(da, a))
            risposta = analisi["risposta"] or {}
            voci = [v for v in (risposta.get("osservazioni", []) + risposta.get("collegamenti", []) + risposta.get("azioni", []))
                    if v.get("verificato")]
            sintesi_ai = {"sintesi": risposta.get("sintesi") if risposta.get("sintesi_verificata") else None, "voci": voci[:6]}
            elenco = "".join(f"<li>{html.escape(v.get('titolo') or v.get('testo', ''))}"
                             + (f" — {html.escape(v['testo'])}" if v.get("titolo") else "") + "</li>" for v in voci[:6])
            blocchi.insert(1, '<h2 style="font-size:16px;margin:24px 0 8px">Lettura dei dati (AI, solo voci verificate)</h2>'
                           + (f"<p>{html.escape(sintesi_ai['sintesi'])}</p>" if sintesi_ai["sintesi"] else "")
                           + (f"<ul>{elenco}</ul>" if elenco else ""))
        except (GenerationError, ValueError):
            logger.warning("rapporto: interpretazione AI non disponibile", exc_info=True)

    s = get_settings()
    console = f"{s.web_public_url.rstrip('/')}/admin/analytics"
    piede = (f'Dettagli nella console: <a href="{console}">{console}</a>. Visite misurate senza cookie; '
             "gruppi di meno di 5 persone omessi.")
    fogli = []
    for titolo, q, descrizione in viste.rapporto(da, a):
        fogli.append((titolo, await esegui(session, catalogo.CATALOGO, q, fuso=FUSO, k_minimo=K_MINIMO), descrizione))
    return {
        "oggetto": f"TAROTS chat — rapporto settimanale {da.strftime('%d/%m')}–{a.strftime('%d/%m/%Y')}",
        "testo": "\n".join(testo + ["", f"Console: {console}"]),
        "html": posta.pagina_html("Rapporto settimanale", f"Dal {da.strftime('%d/%m/%Y')} al {a.strftime('%d/%m/%Y')}", blocchi, piede),
        "allegato": (f"tarots-rapporto-{da.isoformat()}.xlsx", xlsx_da(fogli),
                     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        "ai": sintesi_ai,
    }


async def invia_rapporto(session, *, manuale: bool = False, provider=None,
                         adesso: Optional[datetime] = None, solo: Optional[List[str]] = None) -> Dict[str, Any]:
    """Compone e invia il rapporto della settimana conclusa; registra l'esito in `an_invii`."""
    da, a = settimana_conclusa(adesso)
    destinatari = solo if solo is not None else await destinatari_attivi(session)
    config = config_smtp()
    esito: Dict[str, Any] = {"da": da.isoformat(), "a": a.isoformat(), "destinatari": destinatari}
    if not config.configurato:
        riuscito, dettaglio = False, "SMTP non configurato (TAROT_SMTP_HOST, TAROT_SMTP_MITTENTE)"
    elif not destinatari:
        riuscito, dettaglio = False, "nessun destinatario attivo"
    else:
        opz = await opzioni(session)
        contenuto = await componi_rapporto(session, da, a, con_ai=bool(opz.get("ai")), provider=provider)
        messaggi = [posta.componi(config, d, contenuto["oggetto"], contenuto["testo"], contenuto["html"],
                                  [contenuto["allegato"]]) for d in destinatari]
        try:
            esiti = posta.invia(config, messaggi)
            falliti = {d: e for d, e in esiti.items() if e != "ok"}
            riuscito = not falliti
            dettaglio = "inviato a tutti" if riuscito else f"non recapitato a: {', '.join(falliti)}"
        except (OSError, smtplib.SMTPException) as errore:
            riuscito, dettaglio = False, f"errore SMTP: {errore}"[:1000]
    await session.execute(insert(TABELLE.invii).values(
        id=uuid.uuid4(), tipo="settimanale", da=da, a=a, destinatari=destinatari, riuscito=riuscito,
        dettaglio=dettaglio, manuale=manuale,
    ))
    await session.commit()
    return {**esito, "riuscito": riuscito, "dettaglio": dettaglio}
