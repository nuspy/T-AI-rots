"""Le prove di Stripe dalla console (v9, Fase 2c): la chiave funziona? e il webhook, registrato da qui.

**«Prova la chiave»** è una lettura leggera e gratuita: `GET /v1/account` (chi è l'account, se può incassare); una
chiave limitata (`rk_…`) senza il permesso di leggere l'account riprova con `GET /v1/balance`. Nessun addebito,
nessuna scrittura.

**Il webhook.** Stripe avvisa il sito di ogni pagamento chiamando un indirizzo del sito (l'«endpoint del webhook»)
e firmando ogni avviso con un segreto (`whsec_…`) che solo Stripe e il sito conoscono. Da qui lo si registra senza
aprire la dashboard di Stripe:

- l'indirizzo è quello pubblico dell'API più `/billing/webhook` (dietro il gateway: `https://tarots.chat/api/billing/
  webhook`, il prefisso `/api` lo toglie il proxy, `deploy/k8s/tarots.yaml`);
- gli eventi sono tutti quelli che il codice gestisce (`billing.stripe.EVENTI`);
- se esiste già un endpoint con quell'indirizzo lo si **aggiorna** (eventi), non se ne crea un doppione. Stripe però
  rivela il segreto solo quando l'endpoint nasce: se il sito non ha il segreto di quell'endpoint, l'unico modo di
  averlo è sostituirlo (si cancella e si ricrea, sempre uno solo);
- il segreto restituito si salva cifrato e si usa subito per verificare le firme.

Le prove sostituiscono la rete con `billing.stripe.TRASPORTO` (un `httpx.MockTransport`), come per i pagamenti.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlsplit

import httpx

from ..billing import stripe as modulo_stripe
from ..settings import get_settings

logger = logging.getLogger(__name__)

DESCRIZIONE_ENDPOINT = "TAROTS chat (registrato dalla console)"


class ErroreStripeConsole(Exception):
    """Un errore da mostrare all'operatore così com'è (in italiano, senza dettagli tecnici inutili)."""


def url_webhook() -> str:
    return f"{get_settings().api_public_url.rstrip('/')}/billing/webhook"


async def _chiama(chiave: str, metodo: str, percorso: str, dati: Optional[Dict[str, Any]] = None) -> Tuple[int, Dict[str, Any]]:
    intestazioni = {"Authorization": f"Bearer {chiave}"}
    corpo = None
    parametri = None
    if dati is not None and metodo == "GET":
        parametri = modulo_stripe._modulo(dati)
    elif dati is not None:
        intestazioni["Content-Type"] = "application/x-www-form-urlencoded"
        corpo = urlencode(modulo_stripe._modulo(dati))
    try:
        async with httpx.AsyncClient(timeout=modulo_stripe.TIMEOUT, transport=modulo_stripe.TRASPORTO) as client:
            risposta = await client.request(
                metodo, f"{modulo_stripe.API}{percorso}", content=corpo, params=parametri, headers=intestazioni,
            )
    except httpx.HTTPError as exc:
        raise ErroreStripeConsole(f"Stripe non risponde ({type(exc).__name__}): riprova fra poco.") from exc
    try:
        contenuto = risposta.json()
    except ValueError:
        contenuto = {}
    return risposta.status_code, contenuto if isinstance(contenuto, dict) else {}


def _messaggio(stato: int, contenuto: Dict[str, Any]) -> str:
    errore = (contenuto.get("error") or {}) if isinstance(contenuto, dict) else {}
    testo = str(errore.get("message") or "")[:300]
    if stato == 401:
        return "Stripe non riconosce questa chiave: controlla di averla copiata intera (Sviluppatori → Chiavi API)."
    if stato == 403:
        return ("La chiave è valida ma non ha il permesso per questa operazione: se è una chiave limitata (rk_…), "
                "aggiungi il permesso in Stripe o usa la chiave segreta (sk_…).")
    return f"Stripe ha risposto con un errore ({stato}){': ' + testo if testo else ''}."


async def prova_chiave(chiave: str) -> Dict[str, Any]:
    """Legge l'account (o il saldo, per una chiave limitata). Restituisce l'esito da mostrare e salvare."""
    if not chiave:
        return {"ok": False, "messaggio": "Nessuna chiave segreta da provare."}
    stato, account = await _chiama(chiave, "GET", "/account")
    if stato == 200:
        nome = ((account.get("settings") or {}).get("dashboard") or {}).get("display_name") \
            or (account.get("business_profile") or {}).get("name") or account.get("email") or account.get("id")
        incassa = bool(account.get("charges_enabled"))
        messaggio = f"Chiave valida: account «{nome}»" + (
            ", pronto a incassare." if incassa
            else ". Stripe non ha ancora abilitato gli incassi: completa i dati dell'attività nella dashboard."
        )
        return {"ok": True, "messaggio": messaggio, "account": account.get("id"), "nome": nome, "incassa": incassa,
                "paese": account.get("country")}
    if stato == 403:
        stato, saldo = await _chiama(chiave, "GET", "/balance")
        if stato == 200:
            return {"ok": True, "messaggio": "Chiave limitata valida (letto il saldo; l'account non è leggibile con "
                                             "questa chiave).", "account": None, "nome": None,
                    "incassa": None, "livemode": saldo.get("livemode")}
        return {"ok": False, "messaggio": _messaggio(stato, saldo)}
    return {"ok": False, "messaggio": _messaggio(stato, account)}


async def _endpoint_esistenti(chiave: str) -> List[Dict[str, Any]]:
    stato, elenco = await _chiama(chiave, "GET", "/webhook_endpoints", {"limit": 100})
    if stato != 200:
        raise ErroreStripeConsole(_messaggio(stato, elenco))
    return [e for e in (elenco.get("data") or []) if isinstance(e, dict)]


async def registra_webhook(
    chiave: str, *, webhook_id_noto: Optional[str], segreto_noto: str,
) -> Dict[str, Any]:
    """Crea o aggiorna l'endpoint del webhook. Restituisce `{"id", "url", "azione", "segreto"}`: `segreto` è il nuovo
    `whsec_…` quando l'endpoint nasce (o si sostituisce), altrimenti `None` (resta quello che il sito ha già)."""
    if not chiave:
        raise ErroreStripeConsole("Prima salva la chiave segreta di Stripe.")
    indirizzo = url_webhook()
    parti = urlsplit(indirizzo)
    if parti.scheme != "https" or parti.hostname in (None, "localhost", "127.0.0.1"):
        raise ErroreStripeConsole(
            f"L'indirizzo pubblico dell'API ({indirizzo}) non è raggiungibile da Internet in https: Stripe non può "
            "chiamarlo. Si registra dal sito pubblicato (TAROT_API_PUBLIC_URL), non da un'installazione locale.",
        )
    eventi = list(modulo_stripe.EVENTI)
    esistenti = [e for e in await _endpoint_esistenti(chiave) if (e.get("url") or "").rstrip("/") == indirizzo.rstrip("/")]

    # Quello che il sito conosce già (registrato da qui, o il cui segreto arriva dall'ambiente): si aggiorna.
    conosciuto = next((e for e in esistenti if e.get("id") == webhook_id_noto), None)
    if conosciuto is None and segreto_noto and len(esistenti) == 1 and not webhook_id_noto:
        conosciuto = esistenti[0]
    if conosciuto is not None and segreto_noto:
        stato, aggiornato = await _chiama(chiave, "POST", f"/webhook_endpoints/{conosciuto['id']}", {
            "enabled_events": eventi, "disabled": False, "description": DESCRIZIONE_ENDPOINT,
        })
        if stato != 200:
            raise ErroreStripeConsole(_messaggio(stato, aggiornato))
        doppioni = [e for e in esistenti if e.get("id") != conosciuto["id"]]
        for e in doppioni:
            await _chiama(chiave, "DELETE", f"/webhook_endpoints/{e['id']}")
        return {"id": conosciuto["id"], "url": indirizzo, "azione": "aggiornato", "segreto": None,
                "eventi": eventi, "doppioni_tolti": len(doppioni)}

    # Senza il segreto di quell'endpoint non si verificherebbe nessuna firma: lo si sostituisce (sempre uno solo).
    for e in esistenti:
        stato, risposta = await _chiama(chiave, "DELETE", f"/webhook_endpoints/{e['id']}")
        if stato not in (200, 404):
            raise ErroreStripeConsole(_messaggio(stato, risposta))
    stato, creato = await _chiama(chiave, "POST", "/webhook_endpoints", {
        "url": indirizzo, "enabled_events": eventi, "description": DESCRIZIONE_ENDPOINT,
        "metadata": {"origine": "console tarots"},
    })
    if stato != 200 or not creato.get("secret"):
        raise ErroreStripeConsole(_messaggio(stato, creato))
    return {"id": creato.get("id"), "url": indirizzo, "azione": "sostituito" if esistenti else "creato",
            "segreto": creato["secret"], "eventi": eventi, "doppioni_tolti": max(0, len(esistenti) - 1)}
