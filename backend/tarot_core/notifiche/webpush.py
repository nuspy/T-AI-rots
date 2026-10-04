"""Il Web Push dei browser (v9, Fase 5): RFC 8030 (consegna), 8291 (cifratura `aes128gcm`), 8292 (VAPID).

Il browser, quando la persona dice sì, crea una sottoscrizione presso il **suo** servizio push (Google per Chrome ed
Edge su Android e desktop, Mozilla per Firefox, Apple per Safari): un indirizzo (`endpoint`) e due chiavi. Per
mandare una notifica si cifra il messaggio per quel browser (`p256dh`, `auth`) e lo si posta all'indirizzo, firmato
con la nostra chiave VAPID: il servizio push sa così che il mittente è lo stesso della sottoscrizione.

La cifratura e la firma le fa `pywebpush` (con `http_ece` e `py_vapid`, mantenute dagli autori della specifica); la
richiesta la fa `httpx`, asincrona come il resto. Esiti come in `fcm.py`: `404`/`410` vogliono dire sottoscrizione
finita (la persona ha tolto il permesso, o il browser l'ha rinnovata) e il dispositivo si disattiva.

**iPhone e iPad.** Safari riceve il Web Push solo dal sito aggiunto alla schermata Home (iOS 16.4 e successivi): per
questo il sito ha un manifest e lo spiega a chi usa Safari su iOS.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict
from urllib.parse import urlsplit

import httpx

from .fcm import Esito

#: Quanto tiene il messaggio il servizio push se il dispositivo è spento: un giorno (una carta del giorno vecchia di
#: due giorni non serve a nessuno).
TTL = 24 * 3600


def _client() -> httpx.AsyncClient:
    """Il client HTTP. I test lo sostituiscono con uno su un trasporto finto."""
    return httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0))


def intestazioni_vapid(privata_pem: str, endpoint: str, contatto: str, *, adesso: int | None = None) -> Dict[str, str]:
    """L'intestazione `Authorization: vapid t=<JWT>,k=<chiave pubblica>` per l'origine del servizio push."""
    from cryptography.hazmat.primitives import serialization
    from py_vapid import Vapid02

    parti = urlsplit(endpoint)
    vapid = Vapid02(serialization.load_pem_private_key(privata_pem.encode("ascii"), password=None))
    rivendicazioni = {
        "aud": f"{parti.scheme}://{parti.netloc}",
        "exp": int(adesso if adesso is not None else time.time()) + 12 * 3600,
        "sub": contatto if contatto.startswith(("mailto:", "https://")) else f"mailto:{contatto}",
    }
    return dict(vapid.sign(rivendicazioni))


def cifra(endpoint: str, p256dh: str, auth: str, dati: Dict[str, Any]) -> bytes:
    from pywebpush import WebPusher

    pusher = WebPusher({"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}})
    return pusher.encode(json.dumps(dati, ensure_ascii=False).encode("utf-8"), "aes128gcm")["body"]


async def invia(privata_pem: str, contatto: str, endpoint: str, p256dh: str, auth: str, dati: Dict[str, Any], *,
                urgenza: str = "normal") -> Esito:
    if not privata_pem:
        return Esito("errore", "Chiave VAPID assente: il Web Push è spento.")
    try:
        corpo = cifra(endpoint, p256dh, auth, dati)
        intestazioni = {
            **intestazioni_vapid(privata_pem, endpoint, contatto),
            "Content-Encoding": "aes128gcm",
            "Content-Type": "application/octet-stream",
            "TTL": str(TTL),
            "Urgency": urgenza,
        }
    except Exception as exc:  # noqa: BLE001 — chiavi del browser malformate: quella sottoscrizione non si userà mai
        return Esito("token_invalido", f"Sottoscrizione non valida ({type(exc).__name__})")
    async with _client() as http:
        try:
            r = await http.post(endpoint, content=corpo, headers=intestazioni)
        except httpx.HTTPError as exc:
            return Esito("errore", f"Il servizio push non risponde ({type(exc).__name__})")
    if r.status_code in (200, 201, 202):
        return Esito("ok")
    if r.status_code in (404, 410):
        return Esito("token_invalido", f"{r.status_code}: sottoscrizione scaduta o revocata")
    return Esito("errore", f"{r.status_code}: {r.text[:180]}".strip())
