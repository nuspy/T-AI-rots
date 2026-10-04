"""«Invia un'email di prova» dalla console (v9, Fase 2c).

Usa la stessa configurazione e la stessa funzione di spedizione di tutte le altre email (`correnti.smtp()` e
`posta.invio.SPEDISCI`): se la prova arriva, arrivano anche le email agli utenti e i rapporti agli admin. Le prove
sostituiscono `SPEDISCI` con un finto: nessuna prova manda email vere.
"""
from __future__ import annotations

import asyncio
import smtplib
import ssl
from typing import Any, Dict

from lanterna import posta as lanterna_posta

from . import correnti


def _spiega(errore: Exception) -> str:
    """Una frase per l'operatore, con il dettaglio tecnico in coda."""
    if isinstance(errore, smtplib.SMTPAuthenticationError):
        return "Il server di posta ha rifiutato utente o password."
    if isinstance(errore, (smtplib.SMTPConnectError, ConnectionRefusedError)):
        return "Il server di posta non accetta connessioni su quella porta."
    if isinstance(errore, ssl.SSLError):
        return "La connessione cifrata non è riuscita: prova l'altra sicurezza (SSL sulla 465, STARTTLS sulla 587)."
    if isinstance(errore, (TimeoutError, OSError)) and not isinstance(errore, smtplib.SMTPException):
        return "Il server di posta non risponde: controlla host e porta."
    if isinstance(errore, smtplib.SMTPRecipientsRefused):
        return "Il server ha rifiutato il destinatario."
    if isinstance(errore, smtplib.SMTPSenderRefused):
        return "Il server ha rifiutato il mittente: deve essere una casella che l'utente può usare."
    return "Il server di posta ha risposto con un errore."


async def invia_prova(destinatario: str) -> Dict[str, Any]:
    from ..posta import invio

    config = correnti.smtp()
    if not config.configurato:
        return {"ok": False, "messaggio": "La posta non è configurata: servono almeno host e mittente."}
    testo = (
        "Questa è un'email di prova della console di TAROTS chat.\n\n"
        "Se la leggi, la posta in uscita funziona: le email agli utenti (rinnovi, solleciti, conferme) e i rapporti "
        "agli amministratori partono da qui."
    )
    corpo = lanterna_posta.pagina_html(
        "Email di prova", "La posta in uscita di TAROTS chat funziona",
        ["<p>Se la leggi, le email agli utenti e i rapporti agli amministratori partono correttamente.</p>"],
    )
    messaggio = lanterna_posta.componi(config, destinatario, "TAROTS chat — email di prova", testo, corpo)
    try:
        esiti = await asyncio.to_thread(invio.SPEDISCI, config, [messaggio])
    except (OSError, smtplib.SMTPException) as errore:
        return {"ok": False, "messaggio": f"{_spiega(errore)} ({type(errore).__name__}: {str(errore)[:200]})"}
    risultato = (esiti or {}).get(destinatario, "ok")
    if risultato != "ok":
        return {"ok": False, "messaggio": f"Il server non l'ha accettata: {str(risultato)[:300]}"}
    return {"ok": True, "messaggio": f"Email di prova consegnata al server di posta per {destinatario}. "
                                     "Se non arriva entro qualche minuto, guarda nello spam."}
