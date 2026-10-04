"""La scheda utente dai social: cosa si prende, da dove, e la regola che non cambia mai — **solo i campi vuoti**.

Chi entra con Google, Facebook, GitHub, Microsoft o LinkedIn ha già dato al provider nome, cognome, a volte la data
di nascita, il sesso, la lingua, una foto e la città. Il sito chiama `POST /me/profilo-social` una volta dopo ogni
accesso; qui:

1. si chiede a Keycloak, **con il token della persona** (mai con quello dell'API), a quali social è collegata
   (`/account/linked-accounts`) e il token che ciascun provider le ha rilasciato (`/broker/<alias>/token`: il
   provider deve avere `storeToken`, la persona il ruolo `broker/read-token`, che sta nei ruoli predefiniti);
2. con quel token si legge il profilo dal provider (People API di Google, Graph di Facebook e di Microsoft, l'API
   di GitHub, lo userinfo di LinkedIn);
3. si compilano nella scheda i soli campi vuoti, annotando da quale provider e quando (`users.dati_social`);
4. si aggiorna la **posizione attuale** (paese e città): dal social se la dà, altrimenti dall'IP di questa
   richiesta con il database geografico locale delle analytics (`TAROT_ANALYTICS_GEO`, DB-IP: l'IP non esce mai
   dal server e non si salva). Sta in colonne sue, non negli indirizzi che la persona compila, e non si tocca più
   se la persona l'ha corretta a mano.

Niente di tutto questo è necessario all'accesso: un provider che non risponde, un token scaduto, un ambito non
concesso (Google concede data di nascita e sesso solo alle app verificate, Facebook dopo l'App Review) vogliono
dire solo meno campi compilati, mai un errore per chi entra.

Il sesso e la data di nascita servono alle letture (la carta dell'anima e dell'anno, i pronomi e le concordanze):
la persona li vede, li corregge o li cancella dal profilo, e può spegnere l'importazione.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import httpx

from ..domain.models import GENERI, User
from ..settings import Settings
from .lingue import LINGUE
from .persone import pulisci

logger = logging.getLogger(__name__)

#: Il tempo massimo di ogni chiamata: l'importazione gira dopo l'accesso, e non deve trattenere nessuno.
TIMEOUT = 6.0
#: Le foto si scaricano solo da qui (le CDN dei provider): l'indirizzo arriva da un servizio esterno, e scaricare
#: da un indirizzo qualunque vorrebbe dire far chiamare al server ciò che vuole chi controlla quel profilo.
HOST_FOTO = ("googleusercontent.com", "fbsbx.com", "fbcdn.net", "githubusercontent.com", "licdn.com")
#: Una foto di profilo più grande di così non è una foto di profilo.
MAX_FOTO = 5_000_000

#: I campi della scheda che un social può compilare, con il nome che compare nella provenienza.
CAMPI = ("nome", "cognome", "birth_date", "gender", "locale", "avatar")

#: Il trasporto HTTP verso Keycloak e i provider: `None` è la rete vera. I test ci mettono un finto
#: (`httpx.MockTransport`): nessuna chiamata vera a Google o Facebook durante le prove.
TRASPORTO: Optional[httpx.AsyncBaseTransport] = None


@dataclass
class DatiSocial:
    """Il profilo di un provider, già tradotto nei valori della scheda."""

    provider: str
    nome: Optional[str] = None
    cognome: Optional[str] = None
    nascita: Optional[date] = None
    genere: Optional[str] = None
    genere_altro: Optional[str] = None
    lingua: Optional[str] = None
    foto: Optional[str] = None
    paese: Optional[str] = None
    citta: Optional[str] = None


# ---- i valori dei provider → i valori della scheda ----------------------------------------------------------------


_NON_BINARIO = re.compile(r"non[\s-]?binar|nonbinar|genderqueer|genderfluid|agender", re.IGNORECASE)


def genere_da(valore: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Il sesso come lo scrive il provider (Google: `male`/`female`/`unspecified` o un testo libero; Facebook:
    `male`/`female` o il genere personalizzato) → `(genere, testo di «altro»)` della scheda. `unspecified` e il
    vuoto non sono una risposta: restano vuoti, non diventano «preferisco non dirlo» (che è una scelta)."""
    testo = (valore or "").strip()
    v = testo.lower()
    if not v or v in ("unspecified", "unknown", "undefined"):
        return None, None
    if v in ("male", "man", "m", "uomo", "maschio"):
        return "uomo", None
    if v in ("female", "woman", "f", "donna", "femmina"):
        return "donna", None
    if _NON_BINARIO.search(v):
        return "non_binario", None
    altro = pulisci(testo, 30)
    return ("altro", altro) if altro else (None, None)


def _data_valida(anno: Any, mese: Any, giorno: Any) -> Optional[date]:
    try:
        d = date(int(anno), int(mese), int(giorno))
    except (TypeError, ValueError):
        return None
    # Le stesse regole del profilo: niente date future, niente prima del 1900.
    return d if 1900 <= d.year and d <= date.today() else None


def data_da_google(voce: Optional[Dict[str, Any]]) -> Optional[date]:
    """`{"year": 1990, "month": 4, "day": 12}`. Senza l'anno (Google lo permette) non è una data di nascita."""
    if not isinstance(voce, dict):
        return None
    return _data_valida(voce.get("year"), voce.get("month"), voce.get("day"))


def data_da_facebook(testo: Optional[str]) -> Optional[date]:
    """`MM/DD/YYYY`; Facebook dà anche `MM/DD` o `YYYY` a seconda di ciò che la persona mostra: incompleta, niente."""
    m = re.fullmatch(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*", testo or "")
    return _data_valida(m.group(3), m.group(1), m.group(2)) if m else None


def lingua_da(valore: Any) -> Optional[str]:
    """`it`, `it-IT`, `it_IT` o `{"language": "it", "country": "IT"}` → il codice di una lingua del sito, o niente
    (non l'italiano di ripiego di `lingue.lingua`: una lingua che il sito non ha non è un'informazione)."""
    if isinstance(valore, dict):
        valore = valore.get("language")
    codice = str(valore or "").strip().lower().replace("_", "-").split("-")[0]
    return codice if codice in LINGUE else None


def _paese(valore: Any) -> Optional[str]:
    v = str(valore or "").strip()
    return v.upper() if re.fullmatch(r"[A-Za-z]{2}", v) else None


def _citta(valore: Any) -> Optional[str]:
    """Una città da un testo libero («Milano, Italia» → «Milano»)."""
    return pulisci(str(valore or "").split(",")[0], 100) or None


def _nome_cognome(intero: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    parti = (intero or "").split()
    if len(parti) < 2:
        return (pulisci(parti[0], 100) or None, None) if parti else (None, None)
    return pulisci(parti[0], 100) or None, pulisci(" ".join(parti[1:]), 100) or None


def _primario(voci: Any) -> Optional[Dict[str, Any]]:
    """La voce primaria di un elenco della People API (o la prima)."""
    if not isinstance(voci, list) or not voci:
        return None
    for v in voci:
        if isinstance(v, dict) and (v.get("metadata") or {}).get("primary"):
            return v
    return voci[0] if isinstance(voci[0], dict) else None


# ---- i lettori: un provider, una chiamata --------------------------------------------------------------------------


Lettore = Callable[[httpx.AsyncClient, str], Awaitable[DatiSocial]]


async def _json(client: httpx.AsyncClient, url: str, token: str, **params: Any) -> Dict[str, Any]:
    risposta = await client.get(url, params=params or None, headers={"Authorization": f"Bearer {token}"})
    risposta.raise_for_status()
    dati = risposta.json()
    return dati if isinstance(dati, dict) else {}


async def leggi_google(client: httpx.AsyncClient, token: str) -> DatiSocial:
    """People API. Nomi, lingua e foto vengono con gli ambiti di base; data di nascita e sesso solo con
    `user.birthday.read` e `user.gender.read` (app verificata): senza, quei campi mancano dalla risposta."""
    p = await _json(
        client, "https://people.googleapis.com/v1/people/me", token,
        personFields="names,birthdays,genders,locales,photos",
    )
    d = DatiSocial("google")
    nome = _primario(p.get("names")) or {}
    d.nome = pulisci(nome.get("givenName"), 100) or None
    d.cognome = pulisci(nome.get("familyName"), 100) or None
    # Fra i compleanni, il primo con l'anno: Google ne può dare due (quello del profilo e quello dell'account).
    for b in p.get("birthdays") or []:
        if isinstance(b, dict) and (nascita := data_da_google(b.get("date"))):
            d.nascita = nascita
            break
    genere = _primario(p.get("genders")) or {}
    d.genere, d.genere_altro = genere_da(genere.get("value") or genere.get("formattedValue"))
    d.lingua = lingua_da((_primario(p.get("locales")) or {}).get("value"))
    foto = _primario(p.get("photos")) or {}
    if foto.get("url") and not foto.get("default"):
        # `=s100` è la dimensione: se ne chiede una adatta all'avatar (256 px).
        d.foto = re.sub(r"=s\d+(-c)?$", "=s512", str(foto["url"]))
    return d


async def leggi_facebook(client: httpx.AsyncClient, token: str) -> DatiSocial:
    """Graph API. Compleanno, sesso e città solo con `user_birthday`, `user_gender` e `user_location` (App Review):
    un campo senza permesso manca dalla risposta, senza errore."""
    p = await _json(
        client, "https://graph.facebook.com/me", token,
        fields="first_name,last_name,birthday,gender,location{location{city,country_code}},"
               "picture.width(512).height(512){url,is_silhouette}",
    )
    d = DatiSocial("facebook")
    d.nome = pulisci(p.get("first_name"), 100) or None
    d.cognome = pulisci(p.get("last_name"), 100) or None
    d.nascita = data_da_facebook(p.get("birthday"))
    d.genere, d.genere_altro = genere_da(p.get("gender"))
    luogo = p.get("location") or {}
    dettagli = luogo.get("location") or {}
    d.citta = _citta(dettagli.get("city") or luogo.get("name"))
    d.paese = _paese(dettagli.get("country_code"))
    foto = (p.get("picture") or {}).get("data") or {}
    if foto.get("url") and not foto.get("is_silhouette"):
        d.foto = str(foto["url"])
    return d


async def leggi_github(client: httpx.AsyncClient, token: str) -> DatiSocial:
    p = await _json(client, "https://api.github.com/user", token)
    d = DatiSocial("github")
    d.nome, d.cognome = _nome_cognome(p.get("name"))
    d.citta = _citta(p.get("location"))
    if p.get("avatar_url"):
        d.foto = str(p["avatar_url"])
    return d


async def leggi_microsoft(client: httpx.AsyncClient, token: str) -> DatiSocial:
    p = await _json(
        client, "https://graph.microsoft.com/v1.0/me", token,
        **{"$select": "givenName,surname,preferredLanguage,city,country"},
    )
    d = DatiSocial("microsoft")
    d.nome = pulisci(p.get("givenName"), 100) or None
    d.cognome = pulisci(p.get("surname"), 100) or None
    d.lingua = lingua_da(p.get("preferredLanguage"))
    d.citta = _citta(p.get("city"))
    d.paese = _paese(p.get("country"))
    return d


async def leggi_linkedin(client: httpx.AsyncClient, token: str) -> DatiSocial:
    p = await _json(client, "https://api.linkedin.com/v2/userinfo", token)
    d = DatiSocial("linkedin")
    d.nome = pulisci(p.get("given_name"), 100) or None
    d.cognome = pulisci(p.get("family_name"), 100) or None
    d.lingua = lingua_da(p.get("locale"))
    if p.get("picture"):
        d.foto = str(p["picture"])
    return d


LETTORI: Dict[str, Lettore] = {
    "google": leggi_google,
    "facebook": leggi_facebook,
    "github": leggi_github,
    "microsoft": leggi_microsoft,
    "linkedin": leggi_linkedin,
}


# ---- Keycloak, con il token della persona ---------------------------------------------------------------------------


def _token_del_provider(testo: str) -> Optional[str]:
    """Il token che Keycloak ha conservato è la risposta del provider così com'era: JSON per gli OIDC (Google,
    Microsoft, LinkedIn, Facebook), a volte un modulo `access_token=…&scope=…` (GitHub)."""
    try:
        dati = json.loads(testo)
        if isinstance(dati, dict) and dati.get("access_token"):
            return str(dati["access_token"])
    except ValueError:
        pass
    valori = parse_qs(testo or "").get("access_token")
    return valori[0] if valori else None


async def provider_collegati(client: httpx.AsyncClient, base_realm: str, token_utente: str) -> List[str]:
    """Gli alias dei social collegati all'account (l'API dell'account di Keycloak, con il token della persona)."""
    risposta = await client.get(
        f"{base_realm}/account/linked-accounts",
        headers={"Authorization": f"Bearer {token_utente}", "Accept": "application/json"},
    )
    risposta.raise_for_status()
    voci = risposta.json()
    return [
        str(v.get("providerAlias")) for v in (voci if isinstance(voci, list) else [])
        if isinstance(v, dict) and v.get("connected") and v.get("providerAlias")
    ]


async def token_provider(client: httpx.AsyncClient, base_realm: str, alias: str, token_utente: str) -> Optional[str]:
    risposta = await client.get(
        f"{base_realm}/broker/{alias}/token", headers={"Authorization": f"Bearer {token_utente}"},
    )
    if risposta.status_code >= 400:
        # 400 «not stored» (il provider non conserva i token), 403 senza `broker/read-token`: si va avanti.
        logger.info("Token di %s non disponibile (%s)", alias, risposta.status_code)
        return None
    return _token_del_provider(risposta.text)


async def leggi_dai_social(
    settings: Settings, token_utente: str, *, transport: Optional[httpx.AsyncBaseTransport] = None,
) -> List[DatiSocial]:
    """I profili di tutti i social collegati che sappiamo leggere. Uno che fallisce non ferma gli altri."""
    base_realm = f"{settings.keycloak_url.rstrip('/')}/realms/{settings.keycloak_realm}"
    risultati: List[DatiSocial] = []
    async with httpx.AsyncClient(timeout=TIMEOUT, transport=transport or TRASPORTO) as client:
        try:
            collegati = await provider_collegati(client, base_realm, token_utente)
        except (httpx.HTTPError, ValueError) as exc:
            logger.info("Social collegati non leggibili: %s", type(exc).__name__)
            return []
        for alias in collegati:
            lettore = LETTORI.get(alias)
            if lettore is None:
                continue
            try:
                token = await token_provider(client, base_realm, alias, token_utente)
                if token:
                    risultati.append(await lettore(client, token))
            except (httpx.HTTPError, ValueError) as exc:
                # Un token scaduto (l'accesso con quel social è di giorni fa), un ambito non concesso, il
                # provider che non risponde: meno dati, nessun errore per chi entra.
                logger.info("Profilo %s non letto: %s", alias, type(exc).__name__)
    return risultati


def dati_dal_token(claims: Dict[str, Any]) -> Optional[DatiSocial]:
    """Nome, cognome e lingua dell'account Keycloak (i claim standard `given_name`, `family_name`, `locale`): li ha
    scritti la persona iscrivendosi, o li ha portati il social al primo accesso."""
    if not claims:
        return None
    d = DatiSocial("account")
    d.nome = pulisci(claims.get("given_name"), 100) or None
    d.cognome = pulisci(claims.get("family_name"), 100) or None
    return d if (d.nome or d.cognome) else None


# ---- la scheda --------------------------------------------------------------------------------------------------


def _ora() -> datetime:
    return datetime.now(timezone.utc)


def scelto_dalla_persona(user: User, campo: str) -> bool:
    """La persona ha scritto, corretto o cancellato lei quel campo: un social non lo riempie più, nemmeno vuoto."""
    return (((user.dati_social or {}).get("campi") or {}).get(campo) or {}).get("da") == "utente"


def lingua_vuota(user: User, claims: Dict[str, Any]) -> bool:
    """La lingua non è mai vuota in colonna (nasce «it»): è «vuota» se nessuno l'ha scelta — il token non porta
    la lingua dell'account Keycloak e né la persona né un social l'hanno già impostata."""
    return not claims.get("locale") and "locale" not in ((user.dati_social or {}).get("campi") or {})


def compila(user: User, d: DatiSocial, *, claims: Dict[str, Any], ora: datetime) -> List[str]:
    """Riempie i campi vuoti della scheda con i dati di un provider e ne annota la provenienza. Restituisce i
    campi compilati. Non tocca mai un valore che c'è già, né un campo che la persona ha svuotato apposta."""
    compilati: List[str] = []

    def scrivi(campo: str) -> None:
        compilati.append(campo)
        segna(user, campo, d.provider, ora)

    for campo, nuovo, attuale in (
        ("nome", d.nome, user.nome), ("cognome", d.cognome, user.cognome),
        ("birth_date", d.nascita, user.birth_date),
    ):
        if nuovo and attuale in (None, "") and not scelto_dalla_persona(user, campo):
            setattr(user, campo, nuovo)
            scrivi(campo)
    if d.genere in GENERI and not user.gender and not scelto_dalla_persona(user, "gender"):
        user.gender = d.genere
        user.gender_custom = d.genere_altro if d.genere == "altro" else None
        scrivi("gender")
    if d.lingua and lingua_vuota(user, claims):
        user.locale = d.lingua
        scrivi("locale")
    return compilati


def segna(user: User, campo: str, provider: str, ora: datetime) -> None:
    """Annota da dove viene un campo: un provider, o `utente` se l'ha scritto la persona."""
    provenienza = dict(user.dati_social or {})
    provenienza["campi"] = {**(provenienza.get("campi") or {}), campo: {"da": provider, "il": ora.isoformat()}}
    user.dati_social = provenienza


def dimentica_campo(user: User, campo: str) -> None:
    """La persona ha scritto (o svuotato) lei quel campo: non è più «dal social», e un social non lo riempirà più.
    Senza il segno, un campo svuotato tornerebbe pieno al primo accesso — e la lingua, che non è mai vuota, verrebbe
    sovrascritta."""
    segna(user, campo, "utente", _ora())


def aggiorna_posizione(
    user: User, *, paese: Optional[str], citta: Optional[str], fonte: str, ora: datetime,
) -> Optional[Dict[str, Any]]:
    """La posizione attuale: si aggiorna a ogni accesso, salvo che la persona l'abbia spenta o corretta a mano."""
    if not user.rileva_posizione or user.posizione_fonte == "utente" or not (paese or citta):
        return None
    user.posizione_paese = paese
    user.posizione_citta = citta
    user.posizione_fonte = fonte
    user.posizione_il = ora
    return posizione_json(user)


def posizione_json(user: User) -> Optional[Dict[str, Any]]:
    if not (user.posizione_paese or user.posizione_citta):
        return None
    return {
        "paese": user.posizione_paese, "citta": user.posizione_citta, "fonte": user.posizione_fonte,
        "il": user.posizione_il.isoformat() if user.posizione_il else None,
    }


async def scarica_foto(url: str, *, transport: Optional[httpx.AsyncBaseTransport] = None) -> Optional[bytes]:
    """La foto del profilo social, solo dalle CDN dei provider, senza seguire reindirizzamenti, entro `MAX_FOTO`."""
    host = (urlparse(url).hostname or "").lower()
    if urlparse(url).scheme != "https" or not any(host == h or host.endswith("." + h) for h in HOST_FOTO):
        logger.info("Foto da un indirizzo non ammesso: %s", host or "?")
        return None
    try:
        cliente = httpx.AsyncClient(timeout=TIMEOUT, transport=transport or TRASPORTO, follow_redirects=False)
        async with cliente as client:
            async with client.stream("GET", url) as risposta:
                if risposta.status_code != 200 or not risposta.headers.get("content-type", "").startswith("image/"):
                    return None
                corpo = bytearray()
                async for pezzo in risposta.aiter_bytes():
                    corpo.extend(pezzo)
                    if len(corpo) > MAX_FOTO:
                        return None
                return bytes(corpo)
    except httpx.HTTPError as exc:
        logger.info("Foto non scaricata: %s", type(exc).__name__)
        return None
