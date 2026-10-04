"""Gli articoli del blog su Reddit (v8.6): a ogni pubblicazione, un post con titolo, immagini e link all'originale.

**Cosa parte.** Un post a **galleria** con la copertina e le immagini nel testo (caricate con l'«asset lease» di
Reddit: si chiede il permesso di caricare, si carica sul loro S3, si usa l'id dell'asset), il titolo dell'articolo,
una didascalia per immagine e l'indirizzo dell'articolo come `outbound_url` di ogni immagine e nel testo del post.
Con meno di due immagini, o se il caricamento non riesce, o se il subreddit non accetta gallerie, il ripiego è un
**post link** all'articolo (Reddit ne mostra l'anteprima dall'immagine di condivisione della pagina).

**Quando.** Dopo ogni pubblicazione dalla console o dalla REST (anche in blocco: ogni articolo passa da lì) parte in
background `lavora`; gli articoli programmati li prende il CronJob `tarots-reddit` (ogni quarto d'ora), quando la
loro data arriva. Solo gli articoli usciti **dopo** l'accensione (`attivo_dal`), nelle lingue scelte (le traduzioni
dello stesso articolo sarebbero doppioni), pubblici e indicizzabili.

**Mai due post per articolo.** La riga di `post_reddit` è unica per articolo e nasce prima di parlare con Reddit; un
post solo alla volta in tutto l'impianto (lucchetto consultivo di PostgreSQL al momento di prendere la riga); prima di
riprovare un articolo già tentato si guarda fra gli ultimi post dell'account se c'è già (un errore di rete dopo che
Reddit aveva accettato non diventa un doppione); i post link si mandano con `resubmit=false`.

**Con garbo.** User-Agent nel formato chiesto da Reddit; le intestazioni `X-Ratelimit-*` si rispettano (si aspetta o
si rimanda); un «RATELIMIT» di Reddit rimette l'articolo in coda con l'attesa indicata invece di contarlo come errore;
fra un post e il successivo passano almeno `intervallo_minuti` (60 di partenza): venti articoli pubblicati insieme non
diventano venti post insieme, che su Reddit è la definizione di spam.
"""
from __future__ import annotations

import asyncio
import io
import logging
import re
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import httpx
from fastapi import BackgroundTasks
from sqlalchemy import func, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.blog_models import BlogPost, MediaImage
from ..domain.blog_repositories import BlogRepository, condizione_pubblica
from ..domain.integrazioni_models import ConfigReddit, PostReddit
from ..llm.cifratura import cifra, decifra
from ..settings import get_settings
from .notifiche_motori import url_articolo

logger = logging.getLogger(__name__)

URL_TOKEN = "https://www.reddit.com/api/v1/access_token"
URL_API = "https://oauth.reddit.com"
VERSIONE = "v1.0"
#: Le gallerie di Reddit: da 2 a 20 immagini, didascalie fino a 180 caratteri, titoli fino a 300.
GALLERIA_MIN, GALLERIA_MAX = 2, 20
DIDASCALIA_MAX, TITOLO_MAX = 180, 300
#: Un post «in corso» da più di tanto è un processo morto a metà: l'esito è incerto.
BLOCCATO_DOPO = timedelta(minutes=15)
#: La chiave del lucchetto consultivo: un post alla volta in tutto l'impianto.
LUCCHETTO = 74_221_906
#: Gli indirizzi delle immagini del blog nel Markdown (`/blog/media/<uuid>.webp`, anche con `/api` davanti).
_IMMAGINE = re.compile(r"!\[([^\]]*)\]\(\s*[^)\s]*?/blog/media/([0-9a-fA-F-]{36})\.webp[^)]*\)")
_NOME_SUB = re.compile(r"^(u_[A-Za-z0-9_-]{3,20}|[A-Za-z0-9][A-Za-z0-9_]{1,20})$")
_NOME_UTENTE = re.compile(r"^[A-Za-z0-9_-]{3,20}$")


class ErroreReddit(Exception):
    """Un no di Reddit, col messaggio per la console. `attendi`: secondi da aspettare prima di riprovare (limite di
    frequenza), non un errore vero."""

    def __init__(self, messaggio: str, *, attendi: Optional[int] = None, gia_inviato: bool = False) -> None:
        super().__init__(messaggio)
        self.attendi = attendi
        self.gia_inviato = gia_inviato


@dataclass(frozen=True)
class Credenziali:
    client_id: str
    client_secret: str
    utente: str
    password: str


def user_agent(utente: str) -> str:
    """Il formato che Reddit chiede: `<piattaforma>:<id dell'app>:<versione> (by /u/<utente>)`. Uno User-Agent
    generico (quello di httpx) viene limitato o bloccato."""
    return f"web:chat.tarots.blog-publisher:{VERSIONE} (by /u/{utente or 'unknown'})"


def normalizza_subreddit(valore: str) -> str:
    """`r/tarot`, `/r/tarot/`, `u/nome`, `https://www.reddit.com/user/nome` → `tarot` o `u_nome`."""
    v = (valore or "").strip()
    v = re.sub(r"^https?://(www\.|old\.|new\.)?reddit\.com", "", v, flags=re.I).strip("/")
    m = re.match(r"^(?:u|user)/([^/]+)", v, flags=re.I)
    if m:
        return f"u_{m.group(1)}"
    v = re.sub(r"^r/", "", v, flags=re.I).split("/")[0]
    return v


# ---- configurazione ---------------------------------------------------------------------------------


async def config(session: AsyncSession) -> Optional[ConfigReddit]:
    return (await session.execute(select(ConfigReddit).where(ConfigReddit.id == 1))).scalar_one_or_none()


async def config_o_nuova(session: AsyncSession) -> ConfigReddit:
    riga = await config(session)
    if riga is None:
        riga = ConfigReddit(id=1, lingue=["en"], intervallo_minuti=60, esito_prova={}, attivo=False)
        session.add(riga)
        await session.flush()
    return riga


def credenziali_di(riga: Optional[ConfigReddit]) -> Optional[Credenziali]:
    if riga is None or not (riga.client_id and riga.utente):
        return None
    segreto, password = decifra(riga.client_secret_cifrato), decifra(riga.password_cifrata)
    if not (segreto and password):
        return None
    return Credenziali(riga.client_id, segreto, riga.utente, password)


def mancanti(riga: Optional[ConfigReddit]) -> List[str]:
    """Cosa manca perché si possa pubblicare, in parole."""
    voci = []
    if riga is None or not riga.client_id:
        voci.append("client id dell'app Reddit")
    if riga is None or not riga.client_secret_cifrato:
        voci.append("secret dell'app")
    if riga is None or not riga.utente:
        voci.append("utente Reddit")
    if riga is None or not riga.password_cifrata:
        voci.append("password")
    if riga is None or not riga.subreddit:
        voci.append("subreddit di destinazione")
    return voci


def pronta(riga: Optional[ConfigReddit]) -> bool:
    return bool(riga and riga.attivo and not mancanti(riga) and credenziali_di(riga))


def _fine(cifrato: Optional[bytes]) -> Optional[str]:
    chiaro = decifra(cifrato)
    return f"…{chiaro[-4:]}" if len(chiaro) >= 8 else ("impostato" if chiaro else None)


def config_json(riga: Optional[ConfigReddit]) -> Dict[str, Any]:
    """Per la console: i segreti mai, solo se ci sono e (per il secret) gli ultimi caratteri."""
    return {
        "client_id": riga.client_id if riga else None,
        "client_secret_impostato": bool(riga and riga.client_secret_cifrato),
        "client_secret_fine": _fine(riga.client_secret_cifrato) if riga else None,
        "utente": riga.utente if riga else None,
        "password_impostata": bool(riga and riga.password_cifrata),
        "subreddit": riga.subreddit if riga else None,
        "flair_id": riga.flair_id if riga else None,
        "attivo": bool(riga and riga.attivo),
        "attivo_dal": riga.attivo_dal.isoformat() if riga and riga.attivo_dal else None,
        "lingue": list(riga.lingue) if riga else ["en"],
        "intervallo_minuti": riga.intervallo_minuti if riga else 60,
        "ultima_prova_il": riga.ultima_prova_il.isoformat() if riga and riga.ultima_prova_il else None,
        "esito_prova": (riga.esito_prova if riga else {}) or {},
        "mancano": mancanti(riga),
        "user_agent": user_agent(riga.utente if riga and riga.utente else "<utente>"),
    }


async def aggiorna(session: AsyncSession, valori: Dict[str, Any], *, autore_id: Optional[int]) -> ConfigReddit:
    """Solo i campi passati. I segreti: `None` li lascia come sono, una stringa vuota li toglie."""
    riga = await config_o_nuova(session)
    if "client_id" in valori:
        riga.client_id = (valori["client_id"] or "").strip() or None
    if valori.get("client_secret") is not None:
        riga.client_secret_cifrato = cifra(valori["client_secret"])
    if "utente" in valori:
        utente = (valori["utente"] or "").strip().removeprefix("u/").removeprefix("/u/")
        if utente and not _NOME_UTENTE.match(utente):
            raise ValueError("Nome utente Reddit non valido (3-20 caratteri: lettere, cifre, _ e -).")
        riga.utente = utente or None
    if valori.get("password") is not None:
        riga.password_cifrata = cifra(valori["password"])
    if "subreddit" in valori:
        sub = normalizza_subreddit(valori["subreddit"] or "")
        if sub and not _NOME_SUB.match(sub):
            raise ValueError("Subreddit non valido: scrivi il nome (es. tarot) o u/<utente> per il tuo profilo.")
        riga.subreddit = sub or None
    if "flair_id" in valori:
        riga.flair_id = (valori["flair_id"] or "").strip() or None
    if "lingue" in valori and valori["lingue"] is not None:
        riga.lingue = sorted({str(x)[:5] for x in valori["lingue"] if x}) or ["en"]
    if "intervallo_minuti" in valori and valori["intervallo_minuti"] is not None:
        riga.intervallo_minuti = int(valori["intervallo_minuti"])
    if "attivo" in valori and valori["attivo"] is not None:
        acceso = bool(valori["attivo"])
        if acceso and mancanti(riga):
            raise ValueError("Per accendere la pubblicazione su Reddit mancano: " + ", ".join(mancanti(riga)) + ".")
        if acceso and not riga.attivo:
            riga.attivo_dal = utcnow()  # da adesso: l'archivio non parte
        riga.attivo = acceso
    riga.updated_by = autore_id
    return riga


# ---- il client ----------------------------------------------------------------------------------------


def _client() -> httpx.AsyncClient:
    """Il client HTTP. I test lo sostituiscono con uno su un trasporto finto."""
    return httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0), follow_redirects=False)


async def _dormi(secondi: float) -> None:
    """`asyncio.sleep`, sostituibile nei test."""
    await asyncio.sleep(secondi)


def _attesa_da_messaggio(messaggio: str) -> int:
    m = re.search(r"(\d+)\s*(minut|second|ms)", messaggio, flags=re.I)
    if not m:
        return 600
    n = int(m.group(1))
    return n * 60 + 30 if m.group(2).lower().startswith("minut") else max(n, 5)


class ClientReddit:
    def __init__(self, cred: Credenziali, http: httpx.AsyncClient) -> None:
        self.cred = cred
        self.http = http
        self._token: Optional[str] = None

    @property
    def intestazioni(self) -> Dict[str, str]:
        return {"User-Agent": user_agent(self.cred.utente)}

    async def token(self) -> str:
        if self._token:
            return self._token
        try:
            r = await self.http.post(
                URL_TOKEN, auth=(self.cred.client_id, self.cred.client_secret), headers=self.intestazioni,
                data={"grant_type": "password", "username": self.cred.utente, "password": self.cred.password},
            )
        except httpx.HTTPError as exc:
            raise ErroreReddit(f"Reddit non risponde ({type(exc).__name__}): riprova fra poco.") from exc
        if r.status_code == 401:
            raise ErroreReddit("Reddit rifiuta l'app: client id o secret sbagliati (li trovi in "
                               "https://www.reddit.com/prefs/apps, sotto il nome dell'app di tipo «script»).")
        if r.status_code == 429:
            raise ErroreReddit("Reddit chiede di rallentare (troppi tentativi di accesso): riprova fra qualche minuto.",
                               attendi=300)
        try:
            dati = r.json()
        except ValueError:
            dati = {}
        if r.status_code != 200 or "access_token" not in dati:
            errore = dati.get("error", r.status_code)
            if errore == "invalid_grant":
                raise ErroreReddit("Reddit rifiuta utente o password. Se l'account ha la verifica in due passaggi, le app "
                                   "«script» non possono accedere: disattivala o usa un account dedicato.")
            raise ErroreReddit(f"Reddit non concede il token ({errore}).")
        self._token = dati["access_token"]
        return self._token

    async def richiesta(self, metodo: str, percorso: str, **opzioni) -> Any:
        for tentativo in range(2):
            t = await self.token()
            try:
                r = await self.http.request(
                    metodo, f"{URL_API}{percorso}",
                    headers={**self.intestazioni, "Authorization": f"bearer {t}"}, **opzioni,
                )
            except httpx.HTTPError as exc:
                raise ErroreReddit(f"Reddit non risponde ({type(exc).__name__}).") from exc
            await self._rispetta_limiti(r)
            if r.status_code == 401 and tentativo == 0:
                self._token = None  # scaduto: un token nuovo e si riprova una volta
                continue
            if r.status_code == 429:
                raise ErroreReddit("Reddit chiede di rallentare.", attendi=int(float(r.headers.get("Retry-After", 60))))
            return r
        raise ErroreReddit("Reddit rifiuta l'accesso anche con un token nuovo.")

    async def _rispetta_limiti(self, r: httpx.Response) -> None:
        """`X-Ratelimit-Remaining` e `X-Ratelimit-Reset`: con le richieste quasi finite si aspetta il rinnovo della
        finestra se è vicino, altrimenti si rimanda tutto."""
        try:
            rimaste = float(r.headers.get("X-Ratelimit-Remaining", "100"))
            rinnovo = float(r.headers.get("X-Ratelimit-Reset", "0"))
        except ValueError:
            return
        if rimaste >= 2:
            return
        if rinnovo <= 60:
            await _dormi(rinnovo + 1)
        else:
            raise ErroreReddit("Limite di richieste di Reddit raggiunto per ora.", attendi=int(rinnovo) + 5)

    async def json(self, metodo: str, percorso: str, **opzioni) -> Any:
        r = await self.richiesta(metodo, percorso, **opzioni)
        if r.status_code >= 400:
            raise ErroreReddit(f"Reddit risponde {r.status_code} a {percorso}.")
        try:
            return r.json()
        except ValueError as exc:
            raise ErroreReddit(f"Risposta di Reddit non leggibile da {percorso}.") from exc

    # -- prove ---------------------------------------------------------------------------------------

    async def io(self) -> Dict[str, Any]:
        return await self.json("GET", "/api/v1/me")

    async def destinazione(self, subreddit: str) -> Dict[str, Any]:
        """Le informazioni del subreddit (o del profilo `u_<nome>`), e se ci si può pubblicare."""
        if subreddit.lower().startswith("u_"):
            r = await self.richiesta("GET", f"/user/{subreddit[2:]}/about", params={"raw_json": 1})
        else:
            r = await self.richiesta("GET", f"/r/{subreddit}/about", params={"raw_json": 1})
        if r.status_code in (302, 404) or (r.status_code == 200 and (r.json() or {}).get("kind") == "Listing"):
            raise ErroreReddit(f"r/{subreddit} non esiste (controlla il nome).")
        if r.status_code == 403:
            raise ErroreReddit(f"r/{subreddit} è privato o bannato: l'account non lo vede.")
        if r.status_code >= 400:
            raise ErroreReddit(f"Reddit risponde {r.status_code} per r/{subreddit}.")
        dati = (r.json() or {}).get("data") or {}
        if subreddit.lower().startswith("u_"):
            dati = dati.get("subreddit") or {}
        return dati

    async def flair(self, subreddit: str) -> List[Dict[str, str]]:
        if subreddit.lower().startswith("u_"):
            return []
        r = await self.richiesta("GET", f"/r/{subreddit}/api/link_flair_v2")
        if r.status_code != 200:
            return []
        try:
            return [{"id": str(f.get("id")), "testo": str(f.get("text") or "")} for f in r.json() or [] if f.get("id")]
        except (ValueError, AttributeError):
            return []

    # -- pubblicazione -----------------------------------------------------------------------------------

    async def carica_immagine(self, dati: bytes, nome: str, mime: str = "image/jpeg") -> str:
        """L'asset lease: Reddit dà un modulo di caricamento per il suo S3, lo si riempie col file, e l'id dell'asset
        diventa il `media_id` della galleria."""
        lease = await self.json("POST", "/api/media/asset.json", data={"filepath": nome, "mimetype": mime})
        try:
            azione = lease["args"]["action"]
            campi = {c["name"]: c["value"] for c in lease["args"]["fields"]}
            asset_id = lease["asset"]["asset_id"]
        except (KeyError, TypeError) as exc:
            raise ErroreReddit("Reddit non ha dato il permesso di caricare l'immagine.") from exc
        destinazione = azione if azione.startswith("http") else f"https:{azione}"
        try:
            r = await self.http.post(destinazione, data=campi, files={"file": (nome, dati, mime)},
                                     headers={"User-Agent": user_agent(self.cred.utente)})
        except httpx.HTTPError as exc:
            raise ErroreReddit(f"Caricamento dell'immagine non riuscito ({type(exc).__name__}).") from exc
        if r.status_code not in (200, 201, 204):
            raise ErroreReddit(f"Caricamento dell'immagine rifiutato ({r.status_code}).")
        return str(asset_id)

    @staticmethod
    def _esito_invio(corpo: Any) -> Tuple[str, str]:
        risposta = (corpo or {}).get("json") or {}
        errori = risposta.get("errors") or []
        if errori:
            codice, messaggio = str(errori[0][0]), str(errori[0][1] if len(errori[0]) > 1 else "")
            if codice == "RATELIMIT":
                raise ErroreReddit(f"Reddit: {messaggio}", attendi=_attesa_da_messaggio(messaggio))
            if codice == "ALREADY_SUB":
                raise ErroreReddit("Reddit: link già pubblicato in questo subreddit.", gia_inviato=True)
            if codice in ("SUBREDDIT_NOTALLOWED", "SUBREDDIT_NOEXIST"):
                raise ErroreReddit(f"Reddit non permette di pubblicare qui ({codice}: {messaggio}).")
            if codice in ("SUBMIT_VALIDATION_FLAIR_REQUIRED", "BAD_FLAIR_TEMPLATE_ID"):
                raise ErroreReddit(f"Il subreddit vuole un flair valido: sceglilo nella configurazione ({messaggio}).")
            raise ErroreReddit(f"Reddit rifiuta il post ({codice}: {messaggio}).")
        dati = risposta.get("data") or {}
        nome = str(dati.get("name") or dati.get("id") or "")
        if nome and not nome.startswith("t3_"):
            nome = f"t3_{nome}"
        return nome, str(dati.get("url") or "")

    async def pubblica_galleria(self, subreddit: str, titolo: str, voci: List[Dict[str, str]], testo: str,
                                flair_id: Optional[str]) -> Tuple[str, str]:
        corpo: Dict[str, Any] = {
            "sr": subreddit, "title": titolo, "items": voci, "text": testo, "api_type": "json",
            "nsfw": False, "spoiler": False, "sendreplies": True, "show_error_list": True, "validate_on_submit": True,
        }
        if flair_id:
            corpo["flair_id"] = flair_id
        return self._esito_invio(await self.json("POST", "/api/submit_gallery_post.json", params={"raw_json": 1}, json=corpo))

    async def pubblica_link(self, subreddit: str, titolo: str, url: str, flair_id: Optional[str]) -> Tuple[str, str]:
        dati = {"sr": subreddit, "kind": "link", "title": titolo, "url": url, "resubmit": "false",
                "sendreplies": "true", "api_type": "json"}
        if flair_id:
            dati["flair_id"] = flair_id
        return self._esito_invio(await self.json("POST", "/api/submit", params={"raw_json": 1}, data=dati))

    async def gia_pubblicato(self, subreddit: str, titolo: str) -> Optional[Tuple[str, str]]:
        """Fra gli ultimi post dell'account, uno con lo stesso titolo nello stesso posto: allora il tentativo di prima
        era riuscito anche se non lo sapevamo."""
        r = await self.richiesta("GET", f"/user/{self.cred.utente}/submitted", params={"limit": 25, "sort": "new", "raw_json": 1})
        if r.status_code != 200:
            return None
        for figlio in ((r.json() or {}).get("data") or {}).get("children") or []:
            d = figlio.get("data") or {}
            if d.get("title") == titolo and str(d.get("subreddit", "")).lower() == subreddit.lower():
                return str(d.get("name") or ""), f"https://www.reddit.com{d.get('permalink', '')}"
        return None


# ---- la prova dalla console ---------------------------------------------------------------------------


async def prova(session: AsyncSession) -> Dict[str, Any]:
    """Token, account e destinazione, senza pubblicare nulla. L'esito si salva per la console."""
    riga = await config_o_nuova(session)
    passi: Dict[str, Any] = {}
    cred = credenziali_di(riga)
    if cred is None:
        passi["accesso"] = {"ok": False, "messaggio": "Mancano: " + ", ".join(mancanti(riga) or ["credenziali"]) + "."}
    else:
        async with _client() as http:
            c = ClientReddit(cred, http)
            try:
                me = await c.io()
                giorni = int((utcnow().timestamp() - float(me.get("created_utc") or utcnow().timestamp())) // 86400)
                karma = int(me.get("total_karma") or (me.get("link_karma", 0) + me.get("comment_karma", 0)))
                avviso = ""
                if giorni < 30 or karma < 100:
                    avviso = (" Account giovane o con poco karma: molti subreddit filtrano i suoi post come spam. "
                              "Partecipa (commenti utili) prima di pubblicare link.")
                passi["accesso"] = {"ok": True, "messaggio": f"Accesso come u/{me.get('name')} (karma {karma}, account di {giorni} giorni).{avviso}",
                                    "karma": karma, "giorni": giorni}
            except ErroreReddit as exc:
                passi["accesso"] = {"ok": False, "messaggio": str(exc)}
            if passi["accesso"]["ok"] and riga.subreddit:
                try:
                    d = await c.destinazione(riga.subreddit)
                    passi["destinazione"] = valuta_destinazione(riga.subreddit, d)
                    passi["destinazione"]["flair"] = await c.flair(riga.subreddit)
                except ErroreReddit as exc:
                    passi["destinazione"] = {"ok": False, "messaggio": str(exc)}
            elif not riga.subreddit:
                passi["destinazione"] = {"ok": False, "messaggio": "Manca il subreddit di destinazione."}
    riga.ultima_prova_il = utcnow()
    riga.esito_prova = passi
    return passi


def valuta_destinazione(subreddit: str, d: Dict[str, Any]) -> Dict[str, Any]:
    nome = f"u/{subreddit[2:]}" if subreddit.lower().startswith("u_") else f"r/{subreddit}"
    if d.get("user_is_banned"):
        return {"ok": False, "messaggio": f"L'account è bannato da {nome}."}
    tipo = d.get("subreddit_type")
    if tipo in ("private", "restricted") and not d.get("user_is_contributor") and not d.get("user_is_moderator"):
        return {"ok": False, "messaggio": f"{nome} è {'privato' if tipo == 'private' else 'riservato'}: possono pubblicare solo gli utenti approvati."}
    if d.get("submission_type") == "self":
        return {"ok": False, "messaggio": f"{nome} accetta solo post di testo: né link né immagini."}
    gallerie = d.get("allow_galleries")
    if gallerie is None:
        gallerie = d.get("allow_images", True)
    note = [] if gallerie else ["niente gallerie: si pubblicherà il link all'articolo"]
    if d.get("over18"):
        note.append("subreddit per adulti")
    iscritti = d.get("subscribers")
    return {
        "ok": True, "gallerie": bool(gallerie),
        "messaggio": f"Si può pubblicare in {nome}" + (f" ({iscritti} iscritti)" if iscritti is not None else "")
        + (f": {'; '.join(note)}." if note else "."),
    }


# ---- la coda ---------------------------------------------------------------------------------------------


async def accoda_nuovi(session: AsyncSession, riga: ConfigReddit) -> int:
    """Gli articoli pubblici usciti dopo l'accensione, nelle lingue scelte, ancora senza riga: in coda."""
    if not riga.attivo_dal:
        return 0
    visibili = [s.id for s in await BlogRepository(session).sezioni()]
    candidati = select(BlogPost.id).where(
        condizione_pubblica(visibili),
        BlogPost.noindex.is_(False),
        BlogPost.pubblicato_il >= riga.attivo_dal,
        BlogPost.lang.in_(list(riga.lingue or ["en"])),
        ~select(PostReddit.id).where(PostReddit.articolo_id == BlogPost.id).exists(),
    )
    nuovi = [i for (i,) in (await session.execute(candidati)).all()]
    for articolo_id in nuovi:
        await session.execute(
            insert(PostReddit).values(id=uuid.uuid4(), articolo_id=articolo_id, stato="in_coda", tentativi=0)
            .on_conflict_do_nothing(constraint="uq_post_reddit_articolo")
        )
    return len(nuovi)


async def accoda(session: AsyncSession, articolo_id: uuid.UUID) -> PostReddit:
    """Un articolo preciso, a mano dalla console (anche uno uscito prima dell'accensione). Se ha già una riga non se
    ne crea un'altra: un errore torna in coda, un post già fatto resta com'è."""
    esistente = (await session.execute(select(PostReddit).where(PostReddit.articolo_id == articolo_id))).scalar_one_or_none()
    if esistente is not None:
        if esistente.stato in ("errore", "saltato"):
            esistente.stato, esistente.errore, esistente.riprova_dopo = "in_coda", None, None
        return esistente
    riga = PostReddit(id=uuid.uuid4(), articolo_id=articolo_id, stato="in_coda", tentativi=0)
    session.add(riga)
    await session.flush()
    return riga


async def _sblocca(session: AsyncSession) -> None:
    await session.execute(
        update(PostReddit)
        .where(PostReddit.stato == "in_corso", PostReddit.updated_at < utcnow() - BLOCCATO_DOPO)
        .values(stato="errore", errore="Esito incerto: l'invio si è interrotto a metà. «Riprova» controlla prima su "
                                       "Reddit se il post c'è già.")
    )


async def _prendi(session: AsyncSession, riga: ConfigReddit) -> Optional[PostReddit]:
    """La prossima riga da pubblicare, se è il momento: nessun altro post in corso e l'intervallo trascorso. Il
    lucchetto consultivo (fino al commit) fa sì che due processi non ne prendano due insieme."""
    await session.execute(text("select pg_advisory_xact_lock(:k)"), {"k": LUCCHETTO})
    if (await session.execute(select(PostReddit.id).where(PostReddit.stato == "in_corso").limit(1))).first():
        return None
    adesso = utcnow()
    if riga.intervallo_minuti > 0:
        ultimo = (await session.execute(select(func.max(PostReddit.pubblicato_il)))).scalar()
        if ultimo is not None and ultimo > adesso - timedelta(minutes=riga.intervallo_minuti):
            return None
    prossima = (await session.execute(
        select(PostReddit)
        .where(PostReddit.stato == "in_coda", (PostReddit.riprova_dopo.is_(None)) | (PostReddit.riprova_dopo <= adesso))
        .order_by(PostReddit.created_at, PostReddit.id).limit(1).with_for_update(skip_locked=True)
    )).scalar_one_or_none()
    if prossima is None:
        return None
    prossima.stato = "in_corso"
    prossima.tentativi += 1
    prossima.subreddit = riga.subreddit
    return prossima


def _url_con_utm(url: str) -> str:
    return f"{url}?{urlencode({'utm_source': 'reddit', 'utm_medium': 'social', 'utm_campaign': 'blog'})}"


def _in_jpeg(webp: bytes) -> bytes:
    from PIL import Image

    with Image.open(io.BytesIO(webp)) as img:
        uscita = io.BytesIO()
        img.convert("RGB").save(uscita, "JPEG", quality=90, optimize=True)
        return uscita.getvalue()


def _taglia(testo: str, massimo: int) -> str:
    testo = re.sub(r"\s+", " ", testo or "").strip()
    return testo if len(testo) <= massimo else testo[: massimo - 1].rsplit(" ", 1)[0] + "…"


def _primo_paragrafo(markdown: str) -> str:
    for blocco in (markdown or "").split("\n\n"):
        pulito = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", blocco)
        pulito = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", pulito)
        pulito = re.sub(r"[#>*_`]+", "", pulito).strip()
        if len(pulito) > 40:
            return pulito
    return ""


async def immagini_articolo(session: AsyncSession, p: BlogPost) -> List[Tuple[MediaImage, str]]:
    """La copertina e poi le immagini del testo, nell'ordine, senza doppioni; con la didascalia di ciascuna."""
    voci: List[Tuple[uuid.UUID, str]] = []
    if p.immagine_id:
        voci.append((p.immagine_id, p.immagine_alt or p.titolo))
    for m in _IMMAGINE.finditer(p.testo or ""):
        try:
            voci.append((uuid.UUID(m.group(2)), m.group(1)))
        except ValueError:
            continue
    viste: set = set()
    uniche = [(i, d) for i, d in voci if not (i in viste or viste.add(i))][:GALLERIA_MAX]
    if not uniche:
        return []
    trovate = {m.id: m for m in (await session.execute(select(MediaImage).where(MediaImage.id.in_([i for i, _ in uniche])))).scalars()}
    return [(trovate[i], d) for i, d in uniche if i in trovate]


async def _pubblica(session: AsyncSession, c: ClientReddit, riga: ConfigReddit, post: PostReddit) -> None:
    p = await session.get(BlogPost, post.articolo_id)
    if p is None:
        post.stato, post.errore = "saltato", "Articolo cancellato."
        return
    sub = riga.subreddit or ""
    titolo = _taglia(p.titolo, TITOLO_MAX)
    originale = url_articolo(get_settings().web_public_url, p.slug, p.lang)
    collegamento = _url_con_utm(originale)
    descrizione = p.sottotitolo or p.seo_descrizione or _primo_paragrafo(p.testo)

    if post.tentativi > 1:
        trovato = await c.gia_pubblicato(sub, titolo)
        if trovato:
            post.stato, post.reddit_id, post.url, post.errore = "pubblicato", trovato[0], trovato[1], None
            post.pubblicato_il = post.pubblicato_il or utcnow()
            return

    tipo, nome, indirizzo, nota = "link", "", "", None
    immagini = await immagini_articolo(session, p)
    if len(immagini) >= GALLERIA_MIN and (riga.esito_prova or {}).get("destinazione", {}).get("gallerie", True):
        try:
            voci = []
            for i, (img, didascalia) in enumerate(immagini):
                jpeg = await asyncio.to_thread(_in_jpeg, img.webp)
                asset = await c.carica_immagine(jpeg, f"{p.slug[:60]}-{i + 1}.jpg")
                voci.append({"media_id": asset, "caption": _taglia(didascalia or descrizione, DIDASCALIA_MAX),
                             "outbound_url": collegamento})
            testo = (f"{_taglia(descrizione, 600)}\n\n" if descrizione else "") + f"Read the full article: {collegamento}"
            nome, indirizzo = await c.pubblica_galleria(sub, titolo, voci, testo, riga.flair_id)
            tipo = "galleria"
        except ErroreReddit as exc:
            if exc.attendi is not None or exc.gia_inviato:
                raise
            nota = f"Galleria non riuscita ({exc}): pubblicato come link."
            logger.warning("Reddit, galleria per %s non riuscita, ripiego sul link: %s", p.slug, exc)
    if tipo == "link":
        try:
            nome, indirizzo = await c.pubblica_link(sub, titolo, collegamento, riga.flair_id)
        except ErroreReddit as exc:
            if not exc.gia_inviato:
                raise
            trovato = await c.gia_pubblicato(sub, titolo)
            nome, indirizzo = trovato or ("", "")
            nota = "Il link era già stato pubblicato in questo subreddit."
    post.stato, post.tipo, post.reddit_id = "pubblicato", tipo, nome or None
    post.url = (indirizzo or (f"https://redd.it/{nome[3:]}" if nome.startswith("t3_") else None))
    post.errore, post.riprova_dopo, post.pubblicato_il = nota, None, utcnow()


async def lavora(fabbrica, *, massimo: int = 20) -> Dict[str, Any]:
    """Un giro: accoda gli articoli nuovi, sblocca quelli interrotti, pubblica finché è il momento (uno solo con un
    intervallo, fino a `massimo` senza). Non solleva: ogni errore finisce sulla riga del suo articolo."""
    esito: Dict[str, Any] = {"accodati": 0, "pubblicati": 0, "errori": 0, "rimandati": 0}
    try:
        async with fabbrica() as session:
            riga = await config(session)
            if not pronta(riga):
                esito["stato"] = "spento"
                return esito
            esito["accodati"] = await accoda_nuovi(session, riga)
            await _sblocca(session)
            await session.commit()
            cred = credenziali_di(riga)
            async with _client() as http:
                c = ClientReddit(cred, http)
                for _ in range(massimo):
                    post = await _prendi(session, riga)
                    await session.commit()
                    if post is None:
                        break
                    try:
                        await _pubblica(session, c, riga, post)
                        esito["pubblicati"] += 1
                    except ErroreReddit as exc:
                        if exc.attendi is not None:
                            post.stato, post.riprova_dopo = "in_coda", utcnow() + timedelta(seconds=exc.attendi)
                            post.errore = f"Rimandato: {exc}"[:1000]
                            esito["rimandati"] += 1
                        else:
                            post.stato, post.errore = "errore", str(exc)[:1000]
                            esito["errori"] += 1
                    except Exception as exc:  # noqa: BLE001 — un articolo rotto non ferma la coda
                        logger.exception("Reddit: pubblicazione dell'articolo %s non riuscita", post.articolo_id)
                        post.stato, post.errore = "errore", f"{type(exc).__name__}: {exc}"[:1000]
                        esito["errori"] += 1
                    await session.commit()
                    if riga.intervallo_minuti > 0 or post.stato != "pubblicato":
                        break
                    await _dormi(2)
            esito["stato"] = "ok"
    except Exception:  # noqa: BLE001 — in background nessuno raccoglierebbe l'eccezione
        logger.exception("Reddit: giro della coda non riuscito")
        esito["stato"] = "errore"
    return esito


async def dopo_pubblicazione(session: AsyncSession, compiti: BackgroundTasks, fabbrica, articolo: BlogPost) -> None:
    """Da chiamare per ultima, dopo il commit del salvataggio e dopo aver composto la risposta: se l'articolo è
    pubblicato e Reddit è acceso, un giro della coda parte dopo la risposta. Una query sola se Reddit è spento;
    nessuna se l'articolo è una bozza. La transazione di lettura si chiude qui: il giro in background lavora con una
    sessione sua e non deve trovare aperta quella della richiesta."""
    if articolo.stato != "pubblicato":
        return
    try:
        acceso = (await session.execute(select(ConfigReddit.attivo).where(ConfigReddit.id == 1))).scalar()
        await session.commit()
    except Exception:  # noqa: BLE001 — la pubblicazione dell'articolo è già confermata: Reddit non deve romperla
        logger.exception("Reddit: stato della configurazione non letto")
        return
    if acceso:
        compiti.add_task(lavora, fabbrica)


def post_json(post: PostReddit, articolo: Optional[BlogPost] = None) -> Dict[str, Any]:
    return {
        "id": str(post.id), "articolo_id": str(post.articolo_id), "stato": post.stato, "tipo": post.tipo,
        "subreddit": post.subreddit, "reddit_id": post.reddit_id, "url": post.url, "errore": post.errore,
        "tentativi": post.tentativi,
        "riprova_dopo": post.riprova_dopo.isoformat() if post.riprova_dopo else None,
        "pubblicato_il": post.pubblicato_il.isoformat() if post.pubblicato_il else None,
        "creato_il": post.created_at.isoformat() if post.created_at else None,
        "articolo": ({"titolo": articolo.titolo, "slug": articolo.slug, "lang": articolo.lang,
                      "url": url_articolo(get_settings().web_public_url, articolo.slug, articolo.lang)}
                     if articolo is not None else None),
    }


async def elenco(session: AsyncSession, limite: int = 50) -> List[Dict[str, Any]]:
    righe = (await session.execute(
        select(PostReddit, BlogPost).join(BlogPost, BlogPost.id == PostReddit.articolo_id)
        .order_by(PostReddit.created_at.desc()).limit(limite)
    )).all()
    return [post_json(p, a) for p, a in righe]
