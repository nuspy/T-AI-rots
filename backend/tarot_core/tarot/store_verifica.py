"""«Verifica» degli account degli store dalla console «App mobili» (v9, Fase 3): una chiamata di sola lettura, gratis.

- **Google Play**: un token OAuth del service account caricato in console (lo stesso flusso RS256 di
  `tarot/google.py`, riusato: `google.token`) con l'ambito `androidpublisher`, poi l'elenco dei prodotti in-app
  dell'app (`inappproducts.list`). Riesce solo se il service account è stato invitato in Play Console con i permessi
  sulle finanze, l'API «Google Play Android Developer API» è abilitata nel suo progetto e l'app esiste.
- **Apple**: un JWT ES256 firmato con la chiave `.p8` (Key ID e Issuer ID di App Store Connect), poi
  `POST /inApps/v1/notifications/test` all'ambiente scelto (sandbox o produzione). Apple risponde con un token e
  manda una notifica di prova all'indirizzo delle Server Notifications V2: che la chiave vada si vede dalla risposta,
  che la notifica arrivi lo dirà l'endpoint della Fase 4.

Niente librerie degli store: due richieste REST, provate nei test con un trasporto finto (`_client`).
"""
from __future__ import annotations

import base64
import json
import time
from typing import Any, Dict, Optional
from urllib.parse import quote

import httpx

from ..domain import app_mobili_repositories as app_mobili
from . import google

SCOPE_ANDROIDPUBLISHER = "https://www.googleapis.com/auth/androidpublisher"
API_ANDROIDPUBLISHER = "https://androidpublisher.googleapis.com/androidpublisher/v3"
API_APPLE = {
    "production": "https://api.storekit.itunes.apple.com",
    "sandbox": "https://api.storekit-sandbox.itunes.apple.com",
}


def _client() -> httpx.AsyncClient:
    """Il client HTTP. I test lo sostituiscono con uno su un trasporto finto."""
    return httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0))


def _b64(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).rstrip(b"=").decode("ascii")


# ---- Google Play ------------------------------------------------------------------------------------------------


async def verifica_play(parametri: Dict[str, Any], segreti: Dict[str, str]) -> Dict[str, Any]:
    """`{"ok": bool, "messaggio": str}`: ogni guasto diventa una frase che dice cosa fare."""
    if not segreti.get("service_account"):
        return {"ok": False, "messaggio": "Manca il JSON del service account per la Play Developer API: caricalo qui sopra."}
    package = parametri.get("package_name") or ""
    if not package:
        return {"ok": False, "messaggio": "Manca il package name dell'app."}
    cred = google.Credenziali(json.loads(segreti["service_account"]), "console")
    try:
        t = await google.token(cred, SCOPE_ANDROIDPUBLISHER)
    except google.ErroreGoogle as exc:
        return {"ok": False, "messaggio": str(exc)}
    async with _client() as http:
        try:
            r = await http.get(f"{API_ANDROIDPUBLISHER}/applications/{quote(package, safe='')}/inappproducts",
                               headers={"Authorization": f"Bearer {t}"}, params={"maxResults": 1})
        except httpx.HTTPError as exc:
            return {"ok": False, "messaggio": f"Google Play non risponde ({type(exc).__name__}): riprova fra poco."}
    if r.status_code == 200:
        return {"ok": True, "messaggio": (
            f"Il service account {cred.email} legge i prodotti in-app di {package}: la Play Developer API risponde.")}
    stato, motivo, messaggio = google._errore_api(r)
    if motivo in ("SERVICE_DISABLED", "accessNotConfigured") or "has not been used in project" in messaggio:
        progetto = cred.progetto or "<progetto>"
        return {"ok": False, "messaggio": (
            f"L'API «Google Play Android Developer API» non è abilitata nel progetto «{progetto}»: abilitala da "
            f"https://console.cloud.google.com/apis/library/androidpublisher.googleapis.com?project={progetto} e "
            "riprova fra qualche minuto.")}
    if r.status_code in (401, 403):
        return {"ok": False, "messaggio": (
            f"Google Play non concede l'accesso a {cred.email}: in Play Console → Utenti e autorizzazioni → Invita "
            "nuovi utenti, incolla l'email del service account e dagli accesso all'app (almeno «Visualizza dati "
            "finanziari» e «Gestisci ordini e abbonamenti»). I permessi nuovi possono metterci fino a 24 ore.")}
    if r.status_code == 404:
        return {"ok": False, "messaggio": (
            f"Google Play non trova l'app {package}: va creata in Play Console (e caricato almeno un pacchetto) "
            "prima che l'API la veda. Controlla anche il package name.")}
    return {"ok": False, "messaggio": f"Google Play risponde {r.status_code}: {messaggio or r.text[:200]}"}


# ---- Apple ------------------------------------------------------------------------------------------------------


def jwt_apple(chiave_p8: str, key_id: str, issuer_id: str, bundle_id: str, adesso: Optional[int] = None) -> str:
    """Il token della App Store Server API: ES256, `aud` `appstoreconnect-v1`, al massimo un'ora di vita."""
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

    adesso = int(adesso if adesso is not None else time.time())
    intestazione = {"alg": "ES256", "kid": key_id, "typ": "JWT"}
    corpo = {"iss": issuer_id, "iat": adesso, "exp": adesso + 20 * 60, "aud": "appstoreconnect-v1", "bid": bundle_id}
    da_firmare = (f"{_b64(json.dumps(intestazione, separators=(',', ':')).encode())}."
                  f"{_b64(json.dumps(corpo, separators=(',', ':')).encode())}")
    chiave = serialization.load_pem_private_key(chiave_p8.encode("utf-8"), password=None)
    # `cryptography` firma in DER; un JWS ES256 vuole r e s affiancati, 32 byte ciascuno (RFC 7518, 3.4).
    r, s = decode_dss_signature(chiave.sign(da_firmare.encode("ascii"), ec.ECDSA(hashes.SHA256())))
    return f"{da_firmare}.{_b64(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}"


async def verifica_apple(parametri: Dict[str, Any], segreti: Dict[str, str]) -> Dict[str, Any]:
    mancano = [nome for nome, valore in (
        ("la chiave .p8", segreti.get("chiave_p8")), ("il Key ID", parametri.get("key_id")),
        ("l'Issuer ID", parametri.get("issuer_id")), ("il bundle ID", parametri.get("bundle_id")),
    ) if not valore]
    if mancano:
        return {"ok": False, "messaggio": "Mancano " + ", ".join(mancano) + "."}
    ambiente = parametri.get("ambiente") if parametri.get("ambiente") in API_APPLE else "sandbox"
    try:
        token = jwt_apple(segreti["chiave_p8"], parametri["key_id"], parametri["issuer_id"], parametri["bundle_id"])
    except Exception:  # noqa: BLE001 — la chiave è stata controllata al caricamento: qui solo se si è rovinata
        return {"ok": False, "messaggio": "La chiave .p8 salvata non si legge più: caricala di nuovo."}
    async with _client() as http:
        try:
            r = await http.post(f"{API_APPLE[ambiente]}/inApps/v1/notifications/test",
                                headers={"Authorization": f"Bearer {token}"})
        except httpx.HTTPError as exc:
            return {"ok": False, "messaggio": f"Apple non risponde ({type(exc).__name__}): riprova fra poco."}
    if r.status_code == 200:
        return {"ok": True, "messaggio": (
            f"La App Store Server API ({ambiente}) accetta la chiave {parametri['key_id']}: Apple manda una notifica "
            f"di prova a {app_mobili.url_api(app_mobili.PERCORSO_NOTIFICHE_APPLE)}.")}
    if r.status_code == 401:
        return {"ok": False, "messaggio": (
            "Apple rifiuta il token: controlla che Key ID e Issuer ID siano quelli della chiave caricata (App Store "
            "Connect → Utenti e accesso → Integrazioni → Acquisti in-app), che la chiave non sia revocata e che "
            "l'orologio del server sia giusto.")}
    try:
        corpo = r.json()
    except ValueError:
        corpo = {}
    if r.status_code in (400, 404):
        return {"ok": False, "messaggio": (
            f"Apple risponde {r.status_code} ({corpo.get('errorMessage') or 'richiesta rifiutata'}): di solito l'app con "
            f"bundle ID {parametri['bundle_id']} non esiste ancora in App Store Connect, o non ha un indirizzo per "
            "le Server Notifications V2 in questo ambiente.")}
    if r.status_code == 429:
        return {"ok": False, "messaggio": "Troppe richieste ad Apple: riprova fra qualche minuto."}
    return {"ok": False, "messaggio": f"Apple risponde {r.status_code}: {corpo.get('errorMessage') or r.text[:200]}"}


async def verifica(session, piattaforma: str) -> Dict[str, Any]:
    """La verifica della piattaforma, con l'esito salvato nella sua riga."""
    r = await app_mobili.riga(session, piattaforma)
    parametri, segreti = app_mobili.parametri_di(r, piattaforma), app_mobili.segreti_di(r)
    esito = await (verifica_play(parametri, segreti) if piattaforma == "android" else verifica_apple(parametri, segreti))
    await app_mobili.salva_esito(session, piattaforma, esito)
    return esito
