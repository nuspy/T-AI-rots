"""L'invio di un'email a un utente, una volta sola per chiave (v9, Fase 2b).

`manda(session, utente, tipo, chiave, valori)` compone il modello nella lingua dell'utente, lo spedisce e scrive la
riga di `invii_email`. **La chiave rende l'invio idempotente**: il cron che gira ogni ora, il webhook che il
fornitore rimanda, due repliche dello stesso giro — una chiave già registrata come inviata non riparte. Un invio
fallito per un errore SMTP si ritenta alla chiamata successiva con la stessa chiave (la riga `errore` si aggiorna),
mentre «SMTP non configurato» si registra e basta: in sviluppo e nelle prove non c'è un server di posta, e quelle
email non devono partire tutte insieme il giorno in cui lo si configura.

L'SMTP è sincrono (`smtplib`): si spedisce in un thread, per non fermare il loop. Le prove sostituiscono `SPEDISCI`
con una funzione finta che raccoglie i messaggi: nessuna prova manda email vere.
"""
from __future__ import annotations

import asyncio
import html
import logging
import smtplib
from datetime import datetime
from typing import Any, Callable, Dict, Mapping, Optional, Sequence

from lanterna import posta as lanterna_posta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.abbonamenti_models import InvioEmail
from ..domain.models import User
from ..settings import get_settings
from .modelli import LINGUE, MESI, MODELLI, PIEDE

logger = logging.getLogger(__name__)

#: Chi spedisce davvero: `lanterna.posta.invia(config, messaggi)`. Le prove lo sostituiscono.
SPEDISCI: Callable[[lanterna_posta.ConfigSmtp, Sequence[Any]], Dict[str, str]] = lanterna_posta.invia


def config_smtp() -> lanterna_posta.ConfigSmtp:
    """La posta in uscita: quella della console, poi l'ambiente (v9, Fase 2c, `configurazioni/correnti.py`)."""
    from ..configurazioni import correnti

    return correnti.smtp()


def lingua_di(utente: Optional[User]) -> str:
    """La lingua delle email: quella dell'interfaccia dell'utente se è una delle sei, altrimenti l'inglese."""
    codice = ((getattr(utente, "locale", None) or "en").split("-")[0].split("_")[0]).lower()
    return codice if codice in LINGUE else "en"


def data_in(quando: datetime, lingua: str) -> str:
    """Una data come la scrive una persona in quella lingua."""
    mese = MESI.get(lingua, MESI["en"])[quando.month - 1]
    if lingua == "en":
        return f"{quando.day} {mese} {quando.year}"
    if lingua == "hu":
        return f"{quando.year}. {mese} {quando.day}."
    if lingua == "es":
        return f"{quando.day} de {mese} de {quando.year}"
    return f"{quando.day} {mese} {quando.year}"


def importo_in(centesimi: int, valuta: str, lingua: str) -> str:
    """Un importo con la valuta: «€75.00» in inglese, «75,00 €» nelle altre lingue."""
    simbolo = {"EUR": "€", "USD": "$", "GBP": "£"}.get(valuta.upper(), valuta.upper())
    intero, resto = divmod(abs(int(centesimi)), 100)
    segno = "-" if centesimi < 0 else ""
    if lingua == "en":
        return f"{segno}{simbolo}{intero:,}.{resto:02d}"
    migliaia = f"{intero:,}".replace(",", " " if lingua in ("hu", "ru", "uk") else ".")
    return f"{segno}{migliaia},{resto:02d} {simbolo}"


def componi(tipo: str, lingua: str, valori: Mapping[str, Any], *, link: str) -> Dict[str, str]:
    """Oggetto, testo semplice e HTML di un modello, coi valori al loro posto."""
    modello = MODELLI[tipo].get(lingua) or MODELLI[tipo]["en"]

    def riempi(testo: str) -> str:
        for nome, valore in valori.items():
            testo = testo.replace("{" + nome + "}", str(valore))
        return testo

    oggetto = riempi(modello["oggetto"])
    titolo = riempi(modello["titolo"])
    paragrafi = [riempi(p) for p in modello["paragrafi"]]
    pulsante = riempi(modello["pulsante"])
    piede = PIEDE.get(lingua, PIEDE["en"])

    testo = "\n\n".join([titolo, *paragrafi, f"{pulsante}: {link}", "—", piede])
    corpo = "".join(f'<p style="margin:0 0 14px">{html.escape(p)}</p>' for p in paragrafi)
    pagina = (
        '<!doctype html><html><body style="margin:0;padding:0;background:#f6f1e7">'
        '<div style="max-width:560px;margin:0 auto;padding:24px 20px;font-family:Georgia,\'Times New Roman\',serif;'
        'color:#201026;line-height:1.55;font-size:16px">'
        '<p style="margin:0 0 18px;font:600 13px/1.4 Arial,Helvetica,sans-serif;letter-spacing:.12em;'
        'text-transform:uppercase;color:#7a5a1e">TAROTS chat</p>'
        f'<h1 style="font-size:24px;font-weight:400;margin:0 0 16px">{html.escape(titolo)}</h1>'
        f"{corpo}"
        f'<p style="margin:22px 0"><a href="{html.escape(link, quote=True)}" style="display:inline-block;'
        'background:#201026;color:#f6f1e7;text-decoration:none;padding:13px 22px;border-radius:999px;'
        f'font:600 15px/1.2 Arial,Helvetica,sans-serif">{html.escape(pulsante)}</a></p>'
        f'<p style="margin:28px 0 0;font:12px/1.5 Arial,Helvetica,sans-serif;color:#5b4f6b">{html.escape(piede)}</p>'
        "</div></body></html>"
    )
    return {"oggetto": oggetto, "testo": testo, "html": pagina}


def link_sito(percorso: str, lingua: str) -> str:
    """Un indirizzo del sito nella lingua dell'email: l'italiano sotto `/it`, il resto alla radice (inglese)."""
    base = get_settings().web_public_url.rstrip("/")
    return f"{base}{'/it' if lingua == 'it' else ''}{percorso}"


async def manda(
    session: AsyncSession,
    utente: Optional[User],
    tipo: str,
    chiave: str,
    valori: Optional[Mapping[str, Any]] = None,
    *,
    percorso: str = "/profile#abbonamento",
) -> str:
    """Manda l'email `tipo` all'utente, se con questa `chiave` non è già partita. Restituisce l'esito registrato.

    Non solleva mai: un'email che non parte non deve far fallire un rinnovo o una disdetta. L'esito resta nel
    registro (`invii_email`) e nei log.
    """
    if tipo not in MODELLI:
        raise ValueError(f"modello di email sconosciuto: {tipo}")
    precedente = (await session.execute(
        select(InvioEmail).where(InvioEmail.chiave == chiave).with_for_update()
    )).scalar_one_or_none()
    if precedente is not None and precedente.esito != "errore":
        return "già inviata" if precedente.esito == "inviata" else precedente.esito

    lingua = lingua_di(utente)
    indirizzo = getattr(utente, "email", None)
    from ..configurazioni import correnti

    await correnti.assicura(session)  # anche nei CronJob: la posta impostata in console
    config = config_smtp()
    if not indirizzo:
        esito, dettaglio = "senza_indirizzo", None
    elif not config.configurato:
        esito, dettaglio = "non_configurato", "SMTP non configurato (console: Impostazioni → Posta in uscita)"
    else:
        contenuto = componi(tipo, lingua, dict(valori or {}), link=link_sito(percorso, lingua))
        messaggio = lanterna_posta.componi(config, indirizzo, contenuto["oggetto"], contenuto["testo"], contenuto["html"])
        try:
            esiti = await asyncio.to_thread(SPEDISCI, config, [messaggio])
            risultato = esiti.get(indirizzo, "ok") if esiti else "ok"
            esito, dettaglio = ("inviata", None) if risultato == "ok" else ("errore", str(risultato)[:500])
        except (OSError, smtplib.SMTPException) as errore:
            esito, dettaglio = "errore", f"errore SMTP: {errore}"[:500]

    if precedente is not None:
        precedente.esito, precedente.dettaglio, precedente.lingua = esito, dettaglio, lingua
        await session.flush()
    else:
        try:
            # Un savepoint: due giri concorrenti con la stessa chiave non devono far fallire la transazione di chi
            # perde la corsa (il rinnovo o la disdetta che stava registrando).
            async with session.begin_nested():
                session.add(InvioEmail(
                    user_id=getattr(utente, "id", None), tipo=tipo, chiave=chiave[:200], lingua=lingua, esito=esito,
                    dettaglio=dettaglio,
                ))
        except IntegrityError:
            return "già inviata"
    if esito == "errore":
        logger.warning("Email %s non partita (%s): %s", tipo, chiave, dettaglio)
    else:
        logger.info("Email %s (%s): %s", tipo, chiave, esito)
    return esito
