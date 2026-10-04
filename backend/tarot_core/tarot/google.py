"""Google dalla console (v8.6): il service account per Search Console e GA4, configurato con una procedura guidata.

Prima le credenziali di Search Console venivano solo da un file montato (`TAROT_SEARCH_CONSOLE_CREDENZIALI`), e la
console poteva dire soltanto «mancano le credenziali del service account». Ora:

1. si **carica il JSON** del service account dalla console: si salva cifrato (`llm/cifratura.py`, come le chiavi dei
   fornitori LLM) e non esce più — la console vede l'email del service account, il progetto e l'id della chiave;
2. la console mostra quell'**email** da aggiungere come utente in Search Console (proprietà `sc-domain:tarots.chat`)
   e in GA4 (Gestione accessi alla proprietà, ruolo Visualizzatore);
3. **«Verifica»** prova ogni passo e dice quale manca: la chiave (un token da Google), l'accesso alla proprietà Search
   Console, l'invio della sitemap (che parte da solo se l'accesso c'è), l'accesso alla proprietà GA4.

Il file montato resta il ripiego: se in console non c'è nulla, si usa quello.

**Niente librerie di Google.** Il flusso di un service account è piccolo e stabile (un JWT firmato RS256 scambiato con
un token OAuth2, RFC 7523): lo si fa qui con `cryptography` (già una dipendenza) e `httpx`. Così le chiamate si
provano nei test con un trasporto finto, senza rete, e il backend non si porta dietro `google-api-python-client`
solo per tre richieste REST.
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.integrazioni_models import ConfigGoogle
from ..llm.cifratura import cifra, decifra
from ..settings import get_settings

logger = logging.getLogger(__name__)

SCOPE_SEARCH_CONSOLE = "https://www.googleapis.com/auth/webmasters"
SCOPE_ANALYTICS = "https://www.googleapis.com/auth/analytics.readonly"
TOKEN_URI = "https://oauth2.googleapis.com/token"
API_SEARCH_CONSOLE = "https://www.googleapis.com/webmasters/v3"
API_GA4 = "https://analyticsdata.googleapis.com/v1beta"

#: L'ID di misurazione di un flusso web GA4 (`G-` e lettere maiuscole/cifre).
MISURAZIONE = re.compile(r"^G-[A-Z0-9]{4,16}$")
#: L'ID numerico di una proprietà GA4.
PROPRIETA_GA4 = re.compile(r"^\d{5,15}$")
#: Una proprietà Search Console: di dominio o con prefisso URL.
PROPRIETA_SC = re.compile(r"^(sc-domain:[a-z0-9.-]+\.[a-z]{2,}|https?://[^\s]+/)$")

#: Le API da abilitare nel progetto Google Cloud del service account, col loro nome nella libreria delle API.
API_DA_ABILITARE = {
    "search_console": ("Google Search Console API", "searchconsole.googleapis.com"),
    "ga4": ("Google Analytics Data API", "analyticsdata.googleapis.com"),
}


class ErroreGoogle(Exception):
    """Un passo non riuscito, col messaggio da mostrare in console così com'è."""


@dataclass(frozen=True)
class Credenziali:
    info: Dict[str, Any]
    #: `console` (caricate e cifrate nel database) o `file` (il file montato, il ripiego).
    origine: str

    @property
    def email(self) -> str:
        return str(self.info.get("client_email", ""))

    @property
    def progetto(self) -> str:
        return str(self.info.get("project_id", ""))


# ---- il JSON del service account ------------------------------------------------------------------


def leggi_service_account(testo: str) -> Dict[str, Any]:
    """Il contenuto del file JSON, controllato: è davvero la chiave di un service account e la chiave privata si
    legge. Ogni problema diventa un messaggio che dice cosa caricare invece."""
    try:
        info = json.loads(testo)
    except (ValueError, TypeError) as exc:
        raise ErroreGoogle("Il file non è un JSON valido: carica il file .json scaricato da Google Cloud "
                           "(IAM → Service account → Chiavi → Aggiungi chiave → JSON).") from exc
    if not isinstance(info, dict):
        raise ErroreGoogle("Il file non è la chiave di un service account.")
    if info.get("type") != "service_account":
        tipo = info.get("type") or ("client OAuth" if "installed" in info or "web" in info else "sconosciuto")
        raise ErroreGoogle(f"Questo file è di tipo «{tipo}», non la chiave di un service account: in Google Cloud apri "
                           "IAM → Service account, scegli il service account → Chiavi → Aggiungi chiave → JSON.")
    mancanti = [k for k in ("client_email", "private_key", "private_key_id") if not info.get(k)]
    if mancanti:
        raise ErroreGoogle(f"Nel file mancano dei campi ({', '.join(mancanti)}): scarica di nuovo la chiave JSON.")
    try:
        _chiave_privata(info)
    except Exception as exc:  # noqa: BLE001 — qualunque errore di lettura della chiave ha lo stesso rimedio
        raise ErroreGoogle("La chiave privata nel file non si legge: scarica di nuovo la chiave JSON, senza modificarla.") from exc
    return info


def _chiave_privata(info: Dict[str, Any]):
    from cryptography.hazmat.primitives import serialization

    return serialization.load_pem_private_key(str(info["private_key"]).encode("utf-8"), password=None)


def _b64(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).rstrip(b"=").decode("ascii")


def asserzione(info: Dict[str, Any], scope: str, adesso: Optional[int] = None) -> str:
    """Il JWT firmato (RS256) che si scambia con un token di accesso (RFC 7523)."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    adesso = int(adesso if adesso is not None else time.time())
    intestazione = {"alg": "RS256", "typ": "JWT", "kid": info.get("private_key_id", "")}
    corpo = {
        "iss": info["client_email"], "scope": scope, "aud": info.get("token_uri") or TOKEN_URI,
        "iat": adesso, "exp": adesso + 3600,
    }
    da_firmare = f"{_b64(json.dumps(intestazione, separators=(',', ':')).encode())}.{_b64(json.dumps(corpo, separators=(',', ':')).encode())}"
    firma = _chiave_privata(info).sign(da_firmare.encode("ascii"), padding.PKCS1v15(), hashes.SHA256())
    return f"{da_firmare}.{_b64(firma)}"


# ---- configurazione --------------------------------------------------------------------------------


async def config(session: AsyncSession) -> Optional[ConfigGoogle]:
    return (await session.execute(select(ConfigGoogle).where(ConfigGoogle.id == 1))).scalar_one_or_none()


async def config_o_nuova(session: AsyncSession) -> ConfigGoogle:
    riga = await config(session)
    if riga is None:
        riga = ConfigGoogle(id=1, esito_verifica={})
        session.add(riga)
        await session.flush()
    return riga


def _dal_file() -> Optional[Dict[str, Any]]:
    percorso = get_settings().search_console_credenziali
    if not percorso or not os.path.isfile(percorso):
        return None
    try:
        with open(percorso, encoding="utf-8") as f:
            return leggi_service_account(f.read())
    except (OSError, ErroreGoogle) as exc:
        logger.warning("Credenziali Google dal file %s non leggibili: %s", percorso, exc)
        return None


def credenziali_di(riga: Optional[ConfigGoogle]) -> Optional[Credenziali]:
    """Quelle della console se ci sono, altrimenti il file montato, altrimenti nessuna."""
    if riga is not None and riga.service_account_cifrato:
        chiaro = decifra(riga.service_account_cifrato)
        if chiaro:
            try:
                return Credenziali(json.loads(chiaro), "console")
            except ValueError:
                logger.error("Credenziali Google in console illeggibili (chiave di cifratura cambiata?)")
    info = _dal_file()
    return Credenziali(info, "file") if info else None


async def credenziali(session: AsyncSession) -> Optional[Credenziali]:
    return credenziali_di(await config(session))


def proprieta_sc(riga: Optional[ConfigGoogle]) -> str:
    s = get_settings()
    return (riga.sc_proprieta if riga and riga.sc_proprieta else None) or s.search_console_proprieta or f"sc-domain:{s.analytics_dominio}"


def url_sitemap() -> str:
    return f"{get_settings().web_public_url.rstrip('/')}/sitemap.xml"


async def salva_credenziali(session: AsyncSession, testo: str, *, autore_id: Optional[int]) -> ConfigGoogle:
    info = leggi_service_account(testo)
    riga = await config_o_nuova(session)
    riga.service_account_cifrato = cifra(json.dumps(info))
    riga.client_email = str(info["client_email"])[:320]
    riga.project_id = str(info.get("project_id") or "")[:120] or None
    riga.private_key_id = str(info.get("private_key_id") or "")[:80] or None
    # Credenziali nuove, verifica da rifare: l'esito di prima parlava di un altro service account.
    riga.verificato_il = None
    riga.esito_verifica = {}
    riga.updated_by = autore_id
    _TOKEN.clear()
    return riga


async def togli_credenziali(session: AsyncSession, *, autore_id: Optional[int]) -> ConfigGoogle:
    riga = await config_o_nuova(session)
    riga.service_account_cifrato = None
    riga.client_email = riga.project_id = riga.private_key_id = None
    riga.verificato_il = None
    riga.esito_verifica = {}
    riga.updated_by = autore_id
    _TOKEN.clear()
    return riga


def stato_json(riga: Optional[ConfigGoogle]) -> Dict[str, Any]:
    """Per la console: mai la chiave, solo cosa c'è e da dove viene."""
    cred = credenziali_di(riga)
    return {
        "credenziali": {
            "presenti": cred is not None,
            "origine": cred.origine if cred else None,
            "client_email": cred.email if cred else None,
            "project_id": cred.progetto if cred else None,
            # Gli ultimi caratteri dell'id della chiave: per riconoscerla in Google Cloud, non per usarla.
            "chiave_fine": (str(cred.info.get("private_key_id", ""))[-6:] if cred else None),
        },
        "sc_proprieta": proprieta_sc(riga),
        "sc_proprieta_personalizzata": bool(riga and riga.sc_proprieta),
        "ga4_proprieta_id": riga.ga4_proprieta_id if riga else None,
        "ga4_misurazione_id": riga.ga4_misurazione_id if riga else None,
        "sitemap": url_sitemap(),
        "verificato_il": riga.verificato_il.isoformat() if riga and riga.verificato_il else None,
        "esito_verifica": (riga.esito_verifica if riga else {}) or {},
    }


# ---- HTTP -------------------------------------------------------------------------------------------


def _client() -> httpx.AsyncClient:
    """Il client HTTP. I test lo sostituiscono con uno su un trasporto finto."""
    return httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0))


#: I token per (email, scope), con la scadenza: un'ora di validità, si rinnovano un minuto prima.
_TOKEN: Dict[Tuple[str, str], Tuple[str, float]] = {}


async def token(cred: Credenziali, scope: str) -> str:
    chiave = (cred.email, scope)
    noto = _TOKEN.get(chiave)
    if noto and noto[1] > time.time() + 60:
        return noto[0]
    async with _client() as http:
        try:
            r = await http.post(
                cred.info.get("token_uri") or TOKEN_URI,
                data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": asserzione(cred.info, scope)},
            )
        except httpx.HTTPError as exc:
            raise ErroreGoogle(f"Google non risponde ({type(exc).__name__}): riprova fra poco.") from exc
    if r.status_code != 200:
        raise ErroreGoogle(_spiega_token(r, cred))
    dati = r.json()
    _TOKEN[chiave] = (dati["access_token"], time.time() + float(dati.get("expires_in", 3600)))
    return dati["access_token"]


def _spiega_token(r: httpx.Response, cred: Credenziali) -> str:
    try:
        corpo = r.json()
    except ValueError:
        corpo = {}
    errore, descrizione = str(corpo.get("error", "")), str(corpo.get("error_description", ""))
    if "signature" in descrizione.lower() or errore == "invalid_client" or "not found" in descrizione.lower():
        return (f"Google rifiuta la chiave del service account {cred.email} (revocata o cancellata?): in Google Cloud "
                "crea una nuova chiave JSON per lo stesso service account e caricala qui.")
    if "time" in descrizione.lower() or "iat" in descrizione.lower() or "exp" in descrizione.lower():
        return "Google rifiuta il token per l'orologio: l'ora del server non è giusta (controlla NTP)."
    if "disabled" in descrizione.lower():
        return f"Il service account {cred.email} è disattivato in Google Cloud: riattivalo o usane un altro."
    return f"Google non concede il token ({r.status_code} {errore}: {descrizione})".strip()


def _errore_api(r: httpx.Response) -> Tuple[str, str, str]:
    """(stato, motivo, messaggio) dal corpo d'errore delle API di Google."""
    try:
        e = r.json().get("error", {})
    except ValueError:
        return "", "", r.text[:300]
    if not isinstance(e, dict):
        return "", str(e), ""
    motivo = ""
    for dettaglio in e.get("details") or []:
        if isinstance(dettaglio, dict) and dettaglio.get("reason"):
            motivo = str(dettaglio["reason"])
    for voce in e.get("errors") or []:
        if isinstance(voce, dict) and voce.get("reason") and not motivo:
            motivo = str(voce["reason"])
    return str(e.get("status", "")), motivo, str(e.get("message", ""))


def _api_disabilitata(r: httpx.Response, cred: Credenziali, quale: str) -> Optional[str]:
    stato, motivo, messaggio = _errore_api(r)
    if motivo in ("SERVICE_DISABLED", "accessNotConfigured") or "has not been used in project" in messaggio or "is disabled" in messaggio:
        nome, servizio = API_DA_ABILITARE[quale]
        progetto = cred.progetto or "<progetto>"
        return (f"L'API «{nome}» non è abilitata nel progetto Google Cloud «{progetto}»: abilitala da "
                f"https://console.cloud.google.com/apis/library/{servizio}?project={progetto} e riprova fra qualche minuto.")
    return None


# ---- Search Console ------------------------------------------------------------------------------


async def verifica_search_console(cred: Credenziali, proprieta: str) -> Dict[str, Any]:
    """L'accesso del service account alla proprietà, e con quale livello."""
    t = await token(cred, SCOPE_SEARCH_CONSOLE)
    async with _client() as http:
        r = await http.get(f"{API_SEARCH_CONSOLE}/sites/{quote(proprieta, safe='')}", headers={"Authorization": f"Bearer {t}"})
    if r.status_code == 200:
        livello = str(r.json().get("permissionLevel", ""))
        if livello == "siteUnverifiedUser":
            return {"ok": False, "livello": livello, "messaggio": (
                f"La proprietà {proprieta} non risulta verificata in Search Console: verificala (record DNS per una "
                "proprietà di dominio) e riprova.")}
        if livello == "siteRestrictedUser":
            return {"ok": True, "livello": livello, "messaggio": (
                f"Accesso alla proprietà {proprieta} con permesso «Limitato»: per inviare la sitemap serve «Completo». "
                f"In Search Console → Impostazioni → Utenti e autorizzazioni cambia il permesso di {cred.email}.")}
        return {"ok": True, "livello": livello, "messaggio": f"Accesso alla proprietà {proprieta} ({livello})."}
    disabilitata = _api_disabilitata(r, cred, "search_console")
    if disabilitata:
        return {"ok": False, "messaggio": disabilitata}
    if r.status_code in (403, 404):
        return {"ok": False, "messaggio": (
            f"Il service account non vede la proprietà {proprieta}: in Search Console apri la proprietà → Impostazioni → "
            f"Utenti e autorizzazioni → Aggiungi utente, incolla {cred.email} con permesso «Completo», poi riprova. "
            "Se la proprietà ha un altro nome (per esempio https://tarots.chat/), correggilo qui sopra.")}
    _, _, messaggio = _errore_api(r)
    return {"ok": False, "messaggio": f"Search Console risponde {r.status_code}: {messaggio or r.text[:200]}"}


async def sottometti_sitemap(cred: Credenziali, proprieta: str, sitemap: str) -> Dict[str, Any]:
    t = await token(cred, SCOPE_SEARCH_CONSOLE)
    async with _client() as http:
        r = await http.put(
            f"{API_SEARCH_CONSOLE}/sites/{quote(proprieta, safe='')}/sitemaps/{quote(sitemap, safe='')}",
            headers={"Authorization": f"Bearer {t}"},
        )
    if r.status_code in (200, 204):
        return {"ok": True, "messaggio": f"Sitemap {sitemap} inviata a Search Console."}
    disabilitata = _api_disabilitata(r, cred, "search_console")
    if disabilitata:
        return {"ok": False, "messaggio": disabilitata}
    if r.status_code == 403:
        return {"ok": False, "messaggio": (
            f"Search Console non accetta la sitemap da {cred.email}: serve il permesso «Completo» (o proprietario) "
            "sulla proprietà.")}
    _, _, messaggio = _errore_api(r)
    return {"ok": False, "messaggio": f"Invio della sitemap non riuscito ({r.status_code}): {messaggio or r.text[:200]}"}


# ---- GA4 (Data API) --------------------------------------------------------------------------------


async def _ga4(cred: Credenziali, proprieta_id: str, metodo: str, corpo: Dict[str, Any]) -> httpx.Response:
    t = await token(cred, SCOPE_ANALYTICS)
    async with _client() as http:
        return await http.post(f"{API_GA4}/properties/{proprieta_id}:{metodo}", json=corpo,
                               headers={"Authorization": f"Bearer {t}"})


def _spiega_ga4(r: httpx.Response, cred: Credenziali, proprieta_id: str) -> str:
    disabilitata = _api_disabilitata(r, cred, "ga4")
    if disabilitata:
        return disabilitata
    stato, _, messaggio = _errore_api(r)
    if r.status_code == 403 or stato == "PERMISSION_DENIED":
        return (f"Il service account non ha accesso alla proprietà GA4 {proprieta_id}: in Google Analytics apri "
                f"Amministrazione → Gestione accessi alla proprietà → «+» → Aggiungi utenti, incolla {cred.email} con "
                "ruolo «Visualizzatore», poi riprova.")
    if r.status_code in (400, 404) or stato in ("INVALID_ARGUMENT", "NOT_FOUND"):
        return (f"La proprietà GA4 {proprieta_id} non esiste o l'ID non è giusto: l'ID è il numero in Amministrazione "
                "→ Dettagli proprietà (non l'ID di misurazione G-…).")
    if r.status_code == 429 or stato == "RESOURCE_EXHAUSTED":
        return "Quota della Data API di GA4 esaurita per ora: riprova più tardi."
    return f"GA4 risponde {r.status_code}: {messaggio or r.text[:200]}"


async def verifica_ga4(cred: Credenziali, proprieta_id: str) -> Dict[str, Any]:
    r = await _ga4(cred, proprieta_id, "runReport", {
        "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}], "metrics": [{"name": "activeUsers"}], "limit": 1,
    })
    if r.status_code == 200:
        righe = r.json().get("rows") or []
        utenti = int(float(righe[0]["metricValues"][0]["value"])) if righe else 0
        return {"ok": True, "messaggio": f"Accesso alla proprietà GA4 {proprieta_id}: {utenti} utenti negli ultimi 7 giorni."}
    return {"ok": False, "messaggio": _spiega_ga4(r, cred, proprieta_id)}


#: Le statistiche già chieste: (proprietà, da, a) → (istante, risultato). La Data API ha quote giornaliere, e la
#: console può ricaricare spesso: dieci minuti di memoria bastano.
_CACHE: Dict[Tuple[str, str, str], Tuple[float, Dict[str, Any]]] = {}
CACHE_SECONDI = 600

METRICHE_TOTALI = ["activeUsers", "newUsers", "sessions", "screenPageViews", "engagementRate", "averageSessionDuration"]


def _numero(valore: Any) -> float:
    try:
        return float(valore)
    except (TypeError, ValueError):
        return 0.0


def _righe(report: Dict[str, Any]) -> List[Tuple[List[str], List[float]]]:
    return [([d.get("value", "") for d in r.get("dimensionValues") or []],
             [_numero(m.get("value")) for m in r.get("metricValues") or []]) for r in report.get("rows") or []]


def periodo(giorni: int, oggi: Optional[date] = None) -> Tuple[date, date, date, date]:
    oggi = oggi or datetime.now(ZoneInfo("Europe/Rome")).date()
    da = oggi - timedelta(days=giorni - 1)
    return da, oggi, da - timedelta(days=giorni), da - timedelta(days=1)


async def statistiche_ga4(cred: Credenziali, proprieta_id: str, giorni: int) -> Dict[str, Any]:
    """Utenti, sessioni e visualizzazioni (col periodo precedente), l'andamento per giorno, le pagine e le sorgenti
    principali: una sola chiamata (`batchRunReports`, cinque rapporti)."""
    da, a, da_prec, a_prec = periodo(giorni)
    chiave = (proprieta_id, da.isoformat(), a.isoformat())
    nota = _CACHE.get(chiave)
    if nota and nota[0] > time.time() - CACHE_SECONDI:
        return nota[1]
    intervallo = [{"startDate": da.isoformat(), "endDate": a.isoformat()}]
    richieste = [
        {"dateRanges": intervallo + [{"startDate": da_prec.isoformat(), "endDate": a_prec.isoformat()}],
         "metrics": [{"name": m} for m in METRICHE_TOTALI]},
        {"dateRanges": intervallo, "dimensions": [{"name": "date"}],
         "metrics": [{"name": "activeUsers"}, {"name": "sessions"}, {"name": "screenPageViews"}],
         "orderBys": [{"dimension": {"dimensionName": "date"}}], "limit": 400},
        {"dateRanges": intervallo, "dimensions": [{"name": "pagePath"}],
         "metrics": [{"name": "screenPageViews"}, {"name": "activeUsers"}],
         "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}], "limit": 15},
        {"dateRanges": intervallo, "dimensions": [{"name": "sessionSourceMedium"}],
         "metrics": [{"name": "sessions"}, {"name": "activeUsers"}],
         "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 15},
        {"dateRanges": intervallo, "dimensions": [{"name": "sessionDefaultChannelGroup"}],
         "metrics": [{"name": "sessions"}],
         "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}], "limit": 12},
    ]
    r = await _ga4(cred, proprieta_id, "batchRunReports", {"requests": richieste})
    if r.status_code != 200:
        raise ErroreGoogle(_spiega_ga4(r, cred, proprieta_id))
    rapporti = r.json().get("reports") or [{}] * 5
    rapporti += [{}] * (5 - len(rapporti))

    # Due intervalli senza dimensioni: GA4 aggiunge da sé la dimensione `dateRange` (date_range_0, date_range_1).
    totali: Dict[str, float] = {}
    precedenti: Dict[str, float] = {}
    for dimensioni, valori in _righe(rapporti[0]):
        bersaglio = precedenti if dimensioni and dimensioni[0] == "date_range_1" else totali
        bersaglio.update(dict(zip(METRICHE_TOTALI, valori)))
    risultato = {
        "da": da.isoformat(), "a": a.isoformat(),
        "totali": totali, "precedente": precedenti or None,
        "giorni": [
            {"giorno": f"{d[0][:4]}-{d[0][4:6]}-{d[0][6:8]}", "utenti": v[0], "sessioni": v[1], "visualizzazioni": v[2]}
            for d, v in _righe(rapporti[1]) if d and len(d[0]) == 8
        ],
        "pagine": [{"pagina": d[0], "visualizzazioni": v[0], "utenti": v[1]} for d, v in _righe(rapporti[2]) if d],
        "sorgenti": [{"sorgente": d[0], "sessioni": v[0], "utenti": v[1]} for d, v in _righe(rapporti[3]) if d],
        "canali": [{"canale": d[0], "sessioni": v[0]} for d, v in _righe(rapporti[4]) if d],
        "aggiornato_il": utcnow().isoformat(),
    }
    _CACHE[chiave] = (time.time(), risultato)
    return risultato


# ---- la verifica guidata --------------------------------------------------------------------------


async def verifica(session: AsyncSession, *, invia_sitemap: bool = True) -> Dict[str, Any]:
    """Ogni passo con il suo esito (`ok`, `messaggio`); un passo che dipende da uno fallito si salta e lo dice.
    L'esito si salva per la console. Se l'accesso a Search Console c'è, la sitemap parte subito."""
    riga = await config_o_nuova(session)
    cred = credenziali_di(riga)
    passi: Dict[str, Dict[str, Any]] = {}
    if cred is None:
        passi["credenziali"] = {"ok": False, "messaggio": "Manca il file JSON del service account: caricalo al passo 1."}
    else:
        try:
            await token(cred, SCOPE_SEARCH_CONSOLE)
            passi["credenziali"] = {"ok": True, "messaggio": (
                f"Google riconosce il service account {cred.email}"
                + (" (dal file montato sul server)." if cred.origine == "file" else "."))}
        except ErroreGoogle as exc:
            passi["credenziali"] = {"ok": False, "messaggio": str(exc)}

    proprieta = proprieta_sc(riga)
    if not passi["credenziali"]["ok"]:
        passi["search_console"] = {"ok": False, "saltato": True, "messaggio": "Prima servono credenziali valide."}
    else:
        try:
            passi["search_console"] = await verifica_search_console(cred, proprieta)
        except ErroreGoogle as exc:
            passi["search_console"] = {"ok": False, "messaggio": str(exc)}

    sc = passi["search_console"]
    if not invia_sitemap:
        pass
    elif not sc.get("ok"):
        passi["sitemap"] = {"ok": False, "saltato": True, "messaggio": "Si invia quando l'accesso a Search Console c'è."}
    elif sc.get("livello") == "siteRestrictedUser":
        passi["sitemap"] = {"ok": False, "saltato": True, "messaggio": "Con il permesso «Limitato» non si può inviare la sitemap."}
    else:
        try:
            passi["sitemap"] = await sottometti_sitemap(cred, proprieta, url_sitemap())
        except ErroreGoogle as exc:
            passi["sitemap"] = {"ok": False, "messaggio": str(exc)}

    if not riga.ga4_proprieta_id:
        passi["ga4"] = {"ok": False, "saltato": True, "messaggio": (
            "Manca l'ID della proprietà GA4 (il numero in Amministrazione → Dettagli proprietà): inseriscilo al passo 3.")}
    elif not passi["credenziali"]["ok"]:
        passi["ga4"] = {"ok": False, "saltato": True, "messaggio": "Prima servono credenziali valide."}
    else:
        try:
            passi["ga4"] = await verifica_ga4(cred, riga.ga4_proprieta_id)
        except ErroreGoogle as exc:
            passi["ga4"] = {"ok": False, "messaggio": str(exc)}

    if not riga.ga4_misurazione_id:
        passi["contatore"] = {"ok": False, "saltato": True, "messaggio": (
            "Manca l'ID di misurazione (G-…) del flusso web GA4: senza, il sito non carica il contatore di Google.")}
    else:
        passi["contatore"] = {"ok": True, "messaggio": (
            f"Il sito carica il contatore {riga.ga4_misurazione_id} solo a chi accetta i cookie (Consent Mode v2).")}

    riga.verificato_il = utcnow()
    riga.esito_verifica = passi
    return passi


async def sitemap_dalla_console(session: AsyncSession) -> Optional[Dict[str, str]]:
    """Per il giro notturno dei motori (`notifiche_motori`): l'invio della sitemap con le credenziali caricate in
    console. `None` se in console non ce ne sono (allora vale il file montato, come prima)."""
    riga = await config(session)
    if riga is None or not riga.service_account_cifrato:
        return None
    cred = credenziali_di(riga)
    if cred is None or cred.origine != "console":
        return {"stato": "errore", "dettaglio": "credenziali Google della console illeggibili: ricaricale"}
    try:
        esito = await sottometti_sitemap(cred, proprieta_sc(riga), url_sitemap())
    except ErroreGoogle as exc:
        return {"stato": "errore", "dettaglio": str(exc)[:500]}
    return {"stato": "ok" if esito["ok"] else "errore", "dettaglio": esito["messaggio"][:500]}
