"""Annunciare ai motori di ricerca le pagine nuove o cambiate: articoli del blog, home, carte, stese (v8).

Gira una volta al giorno, a mezzanotte (CronJob `tarots-notifica-motori`, vedi
`tools/notifica_motori.py`), o a mano dalla console. Decisione dell'operatore: niente notifica a ogni
singolo articolo — gli articoli escono a gruppi, e un annuncio al giorno basta ed è più ordinato.

I tre canali vengono dalla libreria separata `seo-notify` e sono indipendenti: uno non configurato
si salta, uno che fallisce non ferma gli altri.

- **IndexNow** (Bing, Yandex, …): gli indirizzi precisi degli articoli.
- **Search Console** (Google): la sitemap intera da rileggere — Google non ha un modo supportato per
  annunciare singoli articoli di un blog (la Indexing API vale solo per offerte di lavoro e dirette).
- **WebSub**: il feed RSS aggiornato, verso l'hub dichiarato nel feed stesso.

La finestra parte dall'esecuzione precedente, non da "ieri a mezzanotte": un CronJob saltato o in
ritardo non deve far perdere articoli.

**Le pagine che non sono articoli** (home, carte, stese, prezzi, sezioni ed etichette del blog, nelle lingue
pubbliche) vengono dalla sitemap del sito stesso, così gli indirizzi sono sempre quelli veri anche quando il
frontend li cambia. Si annuncia:
- ogni indirizzo della sitemap **mai annunciato prima** (al primo giro tutte le pagine; poi solo quelle nuove, per
  esempio una lingua aggiunta);
- **ogni giorno** la carta del giorno (il suo contenuto cambia ogni giorno);
- l'**indice del blog** della lingua in cui è uscito o cambiato un articolo;
- **tutte** le pagine quando lo chiede l'operatore dalla console («Annuncia tutte le pagine»), dopo un
  cambiamento dei contenuti. IndexNow chiede di annunciare solo ciò che cambia: niente annuncio totale a ogni giro.
"""
from __future__ import annotations

import asyncio
import logging
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set
from urllib.parse import urlparse

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.blog_models import BlogPost
from ..domain.blog_repositories import BlogRepository, condizione_pubblica
from ..domain.seo_models import NotificaMotori
from ..settings import get_settings

logger = logging.getLogger(__name__)

CANALI = ("indexnow", "search_console", "websub")

#: Alla prima esecuzione non c'è un "precedente": si guarda un giorno indietro.
PRIMA_FINESTRA = timedelta(days=1)

#: Le pagine che cambiano ogni giorno: si annunciano a ogni giro (la parte del percorso dopo la lingua).
GIORNALIERE = ("/card-of-the-day", "/carta-del-giorno")
#: Il tetto di IndexNow per una richiesta.
MAX_URL = 10_000


def url_articolo(sito: str, slug: str, lingua: str) -> str:
    """L'indirizzo pubblico di un articolo: l'inglese alla radice, l'italiano sotto `/it` (come
    `urlPubblico` del frontend)."""
    prefisso = "/it" if lingua == "it" else ""
    return f"{sito.rstrip('/')}{prefisso}/blog/{slug}"


def leggi_sitemap(sito: str) -> List[str]:
    """Gli indirizzi della sitemap pubblica (`<sito>/sitemap.xml`). Solo quelli dello stesso sito."""
    import httpx

    risposta = httpx.get(f"{sito.rstrip('/')}/sitemap.xml", timeout=30, follow_redirects=False)
    risposta.raise_for_status()
    host = urlparse(sito).netloc
    radice = ET.fromstring(risposta.content)
    return [
        (el.text or "").strip() for el in radice.iter()
        if el.tag.endswith("}loc") or el.tag == "loc"
        if urlparse((el.text or "").strip()).netloc == host
    ]


def _e_giornaliera(url: str) -> bool:
    percorso = urlparse(url).path.rstrip("/")
    return any(percorso.endswith(g) for g in GIORNALIERE)


def _indice_blog(sito: str, url_articolo_: str) -> str:
    """L'indice del blog della lingua di un articolo: `/blog` o `/it/blog`."""
    percorso = urlparse(url_articolo_).path
    prefisso = percorso[: percorso.index("/blog/")]
    return f"{sito.rstrip('/')}{prefisso}/blog"


async def gia_annunciati(session: AsyncSession) -> Set[str]:
    visti: Set[str] = set()
    for (urls,) in (await session.execute(select(NotificaMotori.url))).all():
        visti.update(urls or [])
    return visti


def _saltato(motivo: str) -> Dict[str, str]:
    return {"stato": "saltato", "dettaglio": motivo}


def stato_configurazione() -> Dict[str, Dict[str, Any]]:
    """Quali canali sono pronti, e perché no quelli che non lo sono: per la console."""
    s = get_settings()
    sito = s.web_public_url.rstrip("/")
    credenziali_presenti = bool(s.search_console_credenziali) and os.path.isfile(s.search_console_credenziali)
    return {
        "indexnow": {
            "configurato": bool(s.indexnow_chiave),
            "dettaglio": (f"file di verifica: {sito}/{s.indexnow_chiave}.txt" if s.indexnow_chiave
                          else "manca TAROT_INDEXNOW_CHIAVE"),
        },
        "search_console": {
            "configurato": credenziali_presenti and bool(s.search_console_proprieta),
            "dettaglio": (
                f"proprietà {s.search_console_proprieta}, sitemap {sito}/sitemap.xml"
                if credenziali_presenti and s.search_console_proprieta
                else "mancano le credenziali del service account" if not credenziali_presenti
                else "manca TAROT_SEARCH_CONSOLE_PROPRIETA"
            ),
        },
        "websub": {
            "configurato": bool(s.websub_hub),
            "dettaglio": f"hub {s.websub_hub}, feed {sito}/blog/feed.xml" if s.websub_hub else "manca TAROT_WEBSUB_HUB",
        },
    }


def _indexnow(urls: List[str]) -> Dict[str, str]:
    s = get_settings()
    if not s.indexnow_chiave:
        return _saltato("chiave IndexNow non configurata")
    from seo_notify import ClientIndexNow

    esito = ClientIndexNow(urlparse(s.web_public_url).netloc, s.indexnow_chiave).invia(urls)
    dettaglio = f"HTTP {esito.codice_stato}" if esito.codice_stato else "nessuna risposta"
    if esito.errore and not esito.ok:
        dettaglio += f": {esito.errore}"
    return {"stato": "ok" if esito.ok else "errore", "dettaglio": dettaglio}


def _search_console(_urls: List[str]) -> Dict[str, str]:
    s = get_settings()
    if not s.search_console_credenziali or not os.path.isfile(s.search_console_credenziali):
        return _saltato("credenziali del service account non configurate")
    if not s.search_console_proprieta:
        return _saltato("proprietà Search Console non configurata")
    from seo_notify.search_console import sottometti_sitemap

    esito = sottometti_sitemap(
        site_url=s.search_console_proprieta,
        sitemap_url=f"{s.web_public_url.rstrip('/')}/sitemap.xml",
        service_account_file=s.search_console_credenziali,
    )
    return {"stato": "ok", "dettaglio": "sitemap risottomessa"} if esito.ok else {"stato": "errore", "dettaglio": esito.errore or ""}


def _websub(_urls: List[str]) -> Dict[str, str]:
    s = get_settings()
    if not s.websub_hub:
        return _saltato("hub WebSub non configurato")
    from seo_notify import notifica_hub

    esito = notifica_hub(f"{s.web_public_url.rstrip('/')}/blog/feed.xml", hub=s.websub_hub)
    dettaglio = f"HTTP {esito.codice_stato}" if esito.codice_stato else (esito.errore or "nessuna risposta")
    return {"stato": "ok" if esito.ok else "errore", "dettaglio": dettaglio}


_ESECUTORI: Dict[str, Callable[[List[str]], Dict[str, str]]] = {
    "indexnow": _indexnow, "search_console": _search_console, "websub": _websub,
}


async def _canale(nome: str, urls: List[str]) -> Dict[str, str]:
    """Un canale, in un thread (la libreria è sincrona) e isolato: qualunque errore, anche una
    dipendenza mancante, diventa un esito "errore" di quel canale e non ferma gli altri."""
    try:
        return await asyncio.to_thread(_ESECUTORI[nome], urls)
    except Exception as exc:  # noqa: BLE001 — un canale rotto non deve fermare gli altri
        logger.exception("Notifica ai motori, canale %s fallito", nome)
        return {"stato": "errore", "dettaglio": f"{type(exc).__name__}: {exc}"[:500]}


async def ultima(session: AsyncSession) -> Optional[NotificaMotori]:
    q = select(NotificaMotori).order_by(NotificaMotori.created_at.desc()).limit(1)
    return (await session.execute(q)).scalar_one_or_none()


async def novita(session: AsyncSession, da: datetime, adesso: datetime) -> List[str]:
    """Gli articoli pubblici e indicizzabili pubblicati o modificati in `(da, adesso]`. Un articolo
    programmato conta quando arriva la sua data, non quando è stato scritto."""
    visibili = [s.id for s in await BlogRepository(session).sezioni()]
    q = (
        select(BlogPost.slug, BlogPost.lang)
        .where(
            condizione_pubblica(visibili, adesso),
            BlogPost.noindex.is_(False),
            or_(
                and_(BlogPost.pubblicato_il > da, BlogPost.pubblicato_il <= adesso),
                and_(BlogPost.updated_at > da, BlogPost.updated_at <= adesso),
            ),
        )
        .order_by(BlogPost.pubblicato_il)
    )
    sito = get_settings().web_public_url
    return [url_articolo(sito, slug, lingua) for slug, lingua in (await session.execute(q)).all()]


async def esegui(session: AsyncSession, *, manuale: bool = False, tutte: bool = False) -> NotificaMotori:
    """Un giro completo: raccoglie le novità, le annuncia sui canali configurati, registra l'esito.
    Senza novità non parte nulla (ma il giro si registra, così la console mostra che è girato).
    `tutte`: annuncia tutta la sitemap, non solo il nuovo (a mano, dopo un cambiamento dei contenuti)."""
    adesso = utcnow()
    sito = get_settings().web_public_url
    precedente = await ultima(session)
    da = precedente.created_at if precedente else adesso - PRIMA_FINESTRA
    articoli = await novita(session, da, adesso)

    esiti: Dict[str, Dict[str, str]] = {}
    try:
        mappa = await asyncio.to_thread(leggi_sitemap, sito)
    except Exception as exc:  # noqa: BLE001 — senza sitemap si annunciano comunque gli articoli
        logger.warning("Notifica ai motori: sitemap non letta (%s)", exc)
        mappa = []
        esiti["sitemap"] = {"stato": "errore", "dettaglio": f"sitemap non letta: {type(exc).__name__}: {exc}"[:500]}
    if tutte:
        pagine = mappa
    else:
        visti = await gia_annunciati(session)
        pagine = [u for u in mappa if u not in visti or _e_giornaliera(u)]
        pagine += sorted({_indice_blog(sito, u) for u in articoli})
    urls = list(dict.fromkeys(articoli + pagine))[:MAX_URL]

    if urls:
        esiti.update({nome: await _canale(nome, urls) for nome in CANALI})
    else:
        esiti.update({nome: _saltato("nessuna pagina nuova o aggiornata") for nome in CANALI})

    # `created_at` = `adesso`, non l'ora dell'inserimento: è l'inizio della finestra del giro dopo, e
    # deve coincidere con la fine di questa, altrimenti un articolo pubblicato nel mezzo si perde.
    riga = NotificaMotori(
        finestra_da=da, manuale=manuale, url=urls, esiti=esiti,
        riuscita=all(e["stato"] != "errore" for e in esiti.values()),
        created_at=adesso,
    )
    session.add(riga)
    await session.commit()
    logger.info("Notifica ai motori: %d indirizzi (%d articoli), esiti %s", len(urls), len(articoli),
                {k: v["stato"] for k, v in esiti.items()})
    return riga


def riga_json(r: NotificaMotori) -> Dict[str, Any]:
    return {
        "id": str(r.id), "avviata_il": r.created_at.isoformat() if r.created_at else None,
        "finestra_da": r.finestra_da.isoformat(), "manuale": r.manuale, "url": r.url,
        "esiti": r.esiti, "riuscita": r.riuscita,
    }
