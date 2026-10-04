"""Firebase Cloud Messaging, API HTTP v1 (v9, Fase 5).

Una notifica = una `POST https://fcm.googleapis.com/v1/projects/<progetto>/messages:send` con il token OAuth del
service account di Firebase (scope `firebase.messaging`, `tarot/google.py` lo ottiene e lo tiene in memoria un'ora).
Lo stesso messaggio arriva ad Android e a iOS: per l'iPhone FCM lo passa ad APNs con la chiave `.p8` che l'operatore
carica in Firebase (Impostazioni progetto → Cloud Messaging → app Apple). Il backend non vede mai la chiave APNs.

Gli esiti che contano:

- `ok`: consegnato a FCM;
- `token_invalido`: il token non vale più (`404 UNREGISTERED`, `400` sul token, `403 SENDER_ID_MISMATCH`): l'app è
  stata disinstallata o il token è cambiato. Il dispositivo si disattiva;
- `errore`: tutto il resto (credenziali sbagliate, quota, FCM che non risponde): si riprova al giro successivo, e un
  dispositivo si disattiva solo dopo troppi errori di fila.

Le prove sostituiscono `_client()` con un trasporto finto: nessuna prova chiama Google.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from .config import SCOPE_FCM


@dataclass(frozen=True)
class Esito:
    stato: str  # ok | token_invalido | errore
    messaggio: str = ""


def _client() -> httpx.AsyncClient:
    """Il client HTTP. I test lo sostituiscono con uno su un trasporto finto."""
    return httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=8.0))


def url_invio(progetto: str) -> str:
    return f"https://fcm.googleapis.com/v1/projects/{progetto}/messages:send"


def messaggio_fcm(token: Optional[str], titolo: str, corpo: str, dati: Dict[str, str], *, immagine: Optional[str] = None,
                  canale_android: str = "servizio", topic: Optional[str] = None) -> Dict[str, Any]:
    """Il corpo di `messages:send`. `data` porta il percorso da aprire e l'id dell'invio (per l'apertura): solo
    stringhe, come vuole FCM."""
    notifica: Dict[str, Any] = {"title": titolo, "body": corpo}
    if immagine:
        notifica["image"] = immagine
    aps: Dict[str, Any] = {"sound": "default"}
    if immagine:
        aps["mutable-content"] = 1
    messaggio: Dict[str, Any] = {
        "notification": notifica,
        "data": {k: str(v) for k, v in dati.items() if v is not None},
        # Il canale Android (l'app crea `servizio` e `promozioni`): la persona può spegnere le promozioni dalle
        # impostazioni del telefono senza perdere la carta del giorno.
        "android": {"priority": "normal", "notification": {"channel_id": canale_android}},
        "apns": {"payload": {"aps": aps}, **({"fcm_options": {"image": immagine}} if immagine else {})},
    }
    if topic:
        messaggio["topic"] = topic
    else:
        messaggio["token"] = token
    return {"message": messaggio}


def _dettaglio(r: httpx.Response) -> tuple[str, str]:
    try:
        errore = r.json().get("error", {}) or {}
    except ValueError:
        return "", r.text[:200]
    codice = ""
    for d in errore.get("details") or []:
        if isinstance(d, dict) and d.get("errorCode"):
            codice = str(d["errorCode"])
    return codice or str(errore.get("status") or ""), str(errore.get("message") or "")[:200]


def interpreta(r: httpx.Response) -> Esito:
    if r.status_code == 200:
        return Esito("ok")
    codice, messaggio = _dettaglio(r)
    if codice in ("UNREGISTERED", "SENDER_ID_MISMATCH") or r.status_code == 404:
        return Esito("token_invalido", f"{r.status_code} {codice}: {messaggio}".strip())
    if r.status_code == 400 and "registration token" in messaggio.lower():
        return Esito("token_invalido", f"400 {codice}: {messaggio}".strip())
    return Esito("errore", f"{r.status_code} {codice}: {messaggio}".strip())


async def invia(cred: Any, corpo: Dict[str, Any], *, convalida: bool = False) -> Esito:
    """Manda un messaggio già composto (`messaggio_fcm`). `convalida`: FCM lo controlla senza consegnarlo."""
    from ..tarot import google

    try:
        accesso = await google.token(cred, SCOPE_FCM)
    except google.ErroreGoogle as exc:
        return Esito("errore", str(exc))
    if convalida:
        corpo = {**corpo, "validate_only": True}
    async with _client() as http:
        try:
            r = await http.post(url_invio(cred.progetto), json=corpo, headers={"Authorization": f"Bearer {accesso}"})
        except httpx.HTTPError as exc:
            return Esito("errore", f"FCM non risponde ({type(exc).__name__})")
    return interpreta(r)


async def prova(cred: Any) -> Esito:
    """La prova della console: token OAuth e un messaggio **solo convalidato** verso un argomento (`validate_only`):
    dimostra che il service account può mandare per quel progetto, senza recapitare niente a nessuno."""
    esito = await invia(cred, messaggio_fcm(None, "Prova", "Prova della console", {}, topic="prova-console"), convalida=True)
    if esito.stato == "ok":
        return Esito("ok", f"FCM accetta il service account per il progetto «{cred.progetto}» (messaggio solo convalidato, "
                           "non recapitato).")
    if "403" in esito.messaggio or "PERMISSION_DENIED" in esito.messaggio:
        return Esito("errore", f"Il service account {cred.email} non ha il permesso di mandare messaggi: in Google Cloud "
                               "dagli il ruolo «Firebase Cloud Messaging API Admin» (o usa quello creato da Firebase), e "
                               "controlla che l'API «Firebase Cloud Messaging API» sia abilitata. " + esito.messaggio)
    return esito
