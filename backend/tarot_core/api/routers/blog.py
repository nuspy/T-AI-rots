"""Il blog, per chi legge: sezioni, articoli, etichette, collegamenti con le carte e le stese.

Tutto pubblico e senza account. Il pubblico vede solo gli articoli **pubblicati** la cui data è
già arrivata (`BlogRepository.pubblico`): le bozze, gli articoli
programmati e quelli archiviati non escono da nessuna di queste rotte.

Le immagini stanno nel database e si servono da `GET /blog/media/{id}.webp` con cache
immutabile: l'id è casuale e cambia a ogni caricamento, quindi il contenuto non cambia mai.
"""
from __future__ import annotations

import random
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select

from ...auth.dependencies import DbSession
from ...domain.blog_models import BlogPost, BlogSection, CatalogoImmagine, MediaImage
from ...domain.blog_repositories import BlogRepository
from ...domain.models import User
from ...tarot import blog as regole
from ...tarot import soggetto as regole_soggetto
from ..deps import get_conoscenza

router = APIRouter(prefix="/blog", tags=["blog"])

_SOLO_MINUSCOLE = re.compile(r"^[a-z0-9-]{1,160}$")


# ---- serializzazione ------------------------------------------------------------------------


def url_immagine(immagine_id: Optional[uuid.UUID]) -> Optional[str]:
    return f"/blog/media/{immagine_id}.webp" if immagine_id else None


def url_miniatura(immagine_id: Optional[uuid.UUID]) -> Optional[str]:
    """La miniatura per gli elenchi. Se un'immagine non l'ha ancora, lo stesso indirizzo serve la grande."""
    return f"/blog/media/{immagine_id}-mini.webp" if immagine_id else None


def immagine_json(immagine_id: Optional[uuid.UUID], alt: Optional[str]) -> Optional[Dict[str, Any]]:
    """`{url, mini, alt}` di un'immagine del blog (sezione, stesa), o None se non c'è."""
    if not immagine_id:
        return None
    return {"url": url_immagine(immagine_id), "mini": url_miniatura(immagine_id), "alt": alt}


def immagine_sezione_json(s: BlogSection) -> Optional[Dict[str, Any]]:
    """L'immagine di una sezione (v9.4: un oggetto, prima era il solo indirizzo); l'alt ripiega sul nome."""
    return immagine_json(s.immagine_id, s.immagine_alt or s.nome)


async def immagini_catalogo(session, tipo: str = "stesa") -> Dict[str, Dict[str, Any]]:
    """Le immagini del catalogo di un tipo (oggi le stese), per riferimento: `{"croce-celtica": {url, mini, alt}}`."""
    righe = (await session.execute(select(CatalogoImmagine).where(CatalogoImmagine.tipo == tipo))).scalars()
    return {r.riferimento: immagine_json(r.immagine_id, r.alt) for r in righe}


def nome_pubblico(utente: Optional[User]) -> str:
    """Come si presenta chi scrive o commenta: il nome scelto, altrimenti il primo nome. Mai l'email."""
    if utente is None:
        return "Redazione"
    if utente.nome_pubblico:
        return utente.nome_pubblico
    primo = (utente.display_name or "").split()
    return primo[0] if primo else "Utente"


def autore_json(utente: Optional[User]) -> Dict[str, Any]:
    return {
        "id": utente.id if utente else None,
        "nome": nome_pubblico(utente),
        "avatar": url_immagine(utente.avatar_id) if utente else None,
    }


def nome_riferimento(tipo: str, riferimento: str) -> Optional[str]:
    """Il nome di una carta o di una stesa citata con una scorciatoia, per gli estratti. Il riferimento è un id o uno
    slug in qualunque lingua (`maj-17`, `the-star`); il nome esce in italiano, come il resto degli estratti."""
    conoscenza = get_conoscenza()
    if tipo == "carta":
        id_ = conoscenza.risolvi_carta(riferimento)
        return conoscenza.carta(id_)["nome_it"] if id_ else None
    if tipo == "stesa":
        stesa = conoscenza.stesa(conoscenza.risolvi_stesa(riferimento) or "")
        return stesa["nome"] if stesa else None
    return None


def sezione_breve_json(s: BlogSection) -> Dict[str, Any]:
    return {"slug": s.slug, "nome": s.nome}


async def _autori(session, posts: List[BlogPost]) -> Dict[int, User]:
    ids = {p.autore_id for p in posts if p.autore_id is not None}
    if not ids:
        return {}
    return {u.id: u for u in (await session.execute(select(User).where(User.id.in_(ids)))).scalars()}


def post_breve_json(p: BlogPost, autori: Dict[int, User], sezioni: Dict[int, BlogSection]) -> Dict[str, Any]:
    sezione = sezioni.get(p.sezione_id) if p.sezione_id is not None else None
    return {
        "slug": p.slug,
        "titolo": p.titolo,
        "sottotitolo": p.sottotitolo,
        "estratto": regole.estratto(p.testo, 220, nome_riferimento),
        "immagine": (
            {"url": url_immagine(p.immagine_id), "mini": url_miniatura(p.immagine_id), "alt": p.immagine_alt or p.titolo}
            if p.immagine_id else None
        ),
        "sezione": sezione_breve_json(sezione) if sezione else None,
        "autore": autore_json(autori.get(p.autore_id) if p.autore_id is not None else None),
        "pubblicato_il": p.pubblicato_il.isoformat() if p.pubblicato_il else None,
        "aggiornato_il": p.updated_at.isoformat() if p.updated_at else None,
        "tempo_lettura": p.tempo_lettura,
        "tags": [{"slug": t.slug, "nome": t.nome} for t in p.tags],
        "lang": p.lang,
        "in_evidenza": p.in_evidenza,
        # v9.4: la carta o la stesa di cui l'articolo parla, `{tipo, ref, nome, slug}` (nome e slug nella sua lingua).
        "soggetto": regole_soggetto.soggetto_json(p.soggetto_tipo, p.soggetto_ref, p.lang),
    }


async def articoli_json(session, posts: List[BlogPost]) -> List[Dict[str, Any]]:
    repo = BlogRepository(session)
    sezioni = {s.id: s for s in await repo.sezioni(solo_visibili=False)}
    autori = await _autori(session, posts)
    return [post_breve_json(p, autori, sezioni) for p in posts]


# ---- elementi del catalogo per le sezioni «carte» e «stese» ------------------------------------------


#: I nomi di un grado delle carte minori → il `rango` di deck.json (v9.4, il filtro `{"rango": …}` delle sezioni «By
#: number»). Le corrispondenze: Princess = Page = Knave = Fante; si accettano anche il numero (1–10) e i nomi inglesi.
RANGHI: Dict[str, str] = {
    alias: rango for rango, nomi in {
        "asso": ("asso", "ace", "aces", "1"), "due": ("due", "two", "twos", "2"), "tre": ("tre", "three", "threes", "3"),
        "quattro": ("quattro", "four", "fours", "4"), "cinque": ("cinque", "five", "fives", "5"),
        "sei": ("sei", "six", "sixes", "6"), "sette": ("sette", "seven", "sevens", "7"),
        "otto": ("otto", "eight", "eights", "8"), "nove": ("nove", "nine", "nines", "9"),
        "dieci": ("dieci", "ten", "tens", "10"),
        "principessa": ("principessa", "princess", "princesses", "page", "pages", "knave", "fante"),
        "principe": ("principe", "prince", "princes"),
        "regina": ("regina", "queen", "queens"),
        "cavaliere": ("cavaliere", "knight", "knights"),
    }.items() for alias in nomi
}


def rango_canonico(valore: Any) -> Optional[str]:
    """Il `rango` di deck.json da un valore del filtro (`asso`, `ace`, `1`, `page`…), o None se non è un grado."""
    return RANGHI.get(str(valore).strip().lower()) if valore is not None else None


def _elementi_catalogo(
    sezione: BlogSection, lang: Optional[str] = None, immagini: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Le carte o le stese di una sezione «carte» o «stese», secondo il suo `filtro`.

    Le stese (v9.4) portano anche ciò che serve a una scheda ricca: `descrizione_breve`, `tradizione` (e
    `tradizioni` per lingua), `n_carte`, la geometria per disegnarne lo schema (`posizioni` con `x`, `y`,
    `rotazione`; `forma`, `larghezza`, `larghezza_stretto`) e `immagine` (`{url, mini, alt}` o None) da `immagini`."""
    conoscenza = get_conoscenza()
    filtro = sezione.filtro or {}
    if sezione.tipo == "carte":
        carte = [conoscenza.carta(i) for i in conoscenza.ordine]
        if "arcano" in filtro:
            carte = [c for c in carte if c["arcano"] == filtro["arcano"]]
        if "seme" in filtro:
            carte = [c for c in carte if c.get("seme") == filtro["seme"]]
        if "rango" in filtro:
            rango = rango_canonico(filtro["rango"])
            carte = [c for c in carte if c["arcano"] == "minore" and c.get("rango") == rango]
        return [conoscenza.carta_pubblica(c["id"], lang=lang) for c in carte]
    if sezione.tipo == "stese":
        stese = conoscenza.stese.values()
        if "tema" in filtro:
            # `{"tema": "lavoro"}`: le stese di lavoro e affari e le standard adatte anche al lavoro.
            stese = conoscenza.stese_per_tema(filtro["tema"])
        if "categoria" in filtro:
            stese = [s for s in stese if conoscenza.categoria_di(s) == filtro["categoria"]]
        elementi = []
        for s in stese:
            pubblica = conoscenza.stesa_pubblica(s, lang)
            elemento = {k: v for k, v in pubblica.items() if k in (
                "id", "nome", "nomi", "descrizione", "categoria", "stile", "posizioni", "lang", "slug", "slugs",
                "tradizione", "tradizioni", "forma", "larghezza", "larghezza_stretto", "carte_da_scegliere", "mazzo",
            )}
            elemento["descrizione_breve"] = regole.estratto(pubblica.get("descrizione") or "", 160)
            elemento["n_carte"] = len(pubblica["posizioni"])
            elemento["immagine"] = (immagini or {}).get(s["id"])
            elementi.append(elemento)
        return elementi
    return []


# ---- sezioni -----------------------------------------------------------------------------------------


def _figli_di(sezioni: List[BlogSection]) -> Dict[Optional[int], List[BlogSection]]:
    """Le sezioni raggruppate per padre. Una sezione il cui padre non è fra quelle date sta alla radice (con
    `sezioni()` non capita: una sezione dentro una nascosta è nascosta anche lei)."""
    ids = {s.id for s in sezioni}
    figli: Dict[Optional[int], List[BlogSection]] = {}
    for s in sezioni:
        figli.setdefault(s.parent_id if s.parent_id in ids else None, []).append(s)
    return figli


def _ramo(
    s: BlogSection, figli: Dict[Optional[int], List[BlogSection]], conteggi: Dict[int, int], visti: set,
) -> Tuple[Dict[str, Any], set, set]:
    """Il nodo di una sezione, con le carte e le stese (gli id) di tutto il suo ramo, per i conti del padre."""
    visti.add(s.id)
    rami = [_ramo(f, figli, conteggi, visti) for f in figli.get(s.id, []) if f.id not in visti]
    elementi = _elementi_catalogo(s) if s.tipo in ("carte", "stese") else []
    carte = {e["id"] for e in elementi} if s.tipo == "carte" else set()
    stese = {e["id"] for e in elementi} if s.tipo == "stese" else set()
    for _, c, x in rami:
        carte |= c
        stese |= x
    sotto = [nodo for nodo, _, _ in rami]
    diretti = conteggi.get(s.id, 0)
    nodo = {
        "id": s.id,
        "slug": s.slug,
        "nome": s.nome,
        "descrizione": s.descrizione,
        "tipo": s.tipo,
        "filtro": s.filtro,
        "immagine": immagine_sezione_json(s),
        "n_articoli": diretti + sum(f["n_articoli"] for f in sotto),
        "n_articoli_diretti": diretti,
        "n_elementi": len(elementi) if s.tipo in ("carte", "stese") else None,
        "n_carte": len(carte),
        "n_stese": len(stese),
        "figli": sotto,
    }
    return nodo, carte, stese


def _nodo(s: BlogSection, figli: Dict[Optional[int], List[BlogSection]], conteggi: Dict[int, int]) -> Dict[str, Any]:
    """Una sezione con le sue sotto-sezioni e i conti di tutto il suo ramo.

    - `n_articoli`: gli articoli pubblici della sezione **e di tutte le sotto-sezioni** — lo stesso numero che dà
      `GET /blog/posts?sezione=<slug>` (che include le sotto-sezioni). Un articolo sta in una sezione sola, quindi la
      somma non ha doppioni. `n_articoli_diretti`: solo quelli della sezione.
    - `n_elementi`: per le sezioni «carte» e «stese», quante carte o stese ha la sezione nel catalogo.
    - `n_carte`, `n_stese`: le carte e le stese diverse in tutto il ramo (una carta in due sotto-sezioni conta una
      volta): «Tarot», che contiene arcani maggiori, minori e stese, ha 78 carte e 19 stese.
    - `immagine`: `{url, mini, alt}` o None (v9.4; l'alt è `immagine_alt` della sezione, o il suo nome)."""
    return _ramo(s, figli, conteggi, set())[0]


async def _articoli_a_caso(repo: BlogRepository, sezione: BlogSection, visibili: List[BlogSection], quanti: int = 3) -> List[BlogPost]:
    """`quanti` articoli pubblici del ramo di una sezione scelti a caso, stabili per un giorno (seme = data UTC +
    slug), dal più recente al più vecchio."""
    candidati, _ = await repo.elenco(sezioni=repo.discendenti(sezione.id, visibili), per_pagina=60)
    if len(candidati) <= quanti:
        return candidati
    caso = random.Random(f"{datetime.now(timezone.utc).date().isoformat()}|figlio|{sezione.slug}")
    scelti = set(p.id for p in caso.sample(candidati, quanti))
    return [p for p in candidati if p.id in scelti]


@router.get("/sections")
async def albero(session: DbSession) -> List[Dict[str, Any]]:
    """L'albero delle sezioni visibili; ognuna conta i suoi articoli più quelli delle sotto-sezioni (`_nodo`)."""
    repo = BlogRepository(session)
    figli = _figli_di(await repo.sezioni())
    conteggi = await repo.conteggi_per_sezione()
    return [_nodo(s, figli, conteggi) for s in figli.get(None, [])]


@router.get("/sections/{slug}")
async def sezione(
    slug: str, session: DbSession,
    lang: Optional[str] = Query(default=None, max_length=10, pattern="^[A-Za-z-]*$"),
) -> Dict[str, Any]:
    """Una sezione. `lang` sceglie la lingua dei nomi e degli slug di carte e stese del catalogo.

    Ogni sotto-sezione diretta (`figli`) porta, oltre a immagine e conteggi del nodo, `articoli`: 3 articoli del suo
    ramo scelti a caso (stabili nella giornata), nel formato degli elenchi (v9.4). Gli `elementi` di una sezione
    «stese» hanno descrizione breve, tradizione, numero di carte, schema e immagine (`_elementi_catalogo`)."""
    repo = BlogRepository(session)
    visibili = await repo.sezioni()
    per_id = {s.id: s for s in visibili}
    s = next((x for x in visibili if x.slug == slug), None)
    if s is None:
        raise HTTPException(status_code=404, detail="Sezione non trovata")
    conteggi = await repo.conteggi_per_sezione()
    nodo = _nodo(s, _figli_di(visibili), conteggi)
    for figlio in nodo["figli"]:
        sezione_figlio = per_id[figlio["id"]]
        figlio["articoli"] = await articoli_json(session, await _articoli_a_caso(repo, sezione_figlio, visibili))
    immagini = await immagini_catalogo(session, "stesa") if s.tipo == "stese" else None
    return nodo | {
        "seo_titolo": s.seo_titolo,
        "seo_descrizione": s.seo_descrizione,
        "briciole": [{"slug": x.slug, "nome": x.nome} for x in repo.percorso(s, per_id)],
        "elementi": _elementi_catalogo(s, lang, immagini),
    }


# ---- articoli --------------------------------------------------------------------------------------------


def _riferimento(carta: Optional[str], stesa: Optional[str]) -> Optional[Tuple[str, str]]:
    """("carta", id) o ("stesa", id) da un id o uno slug; 404 se non esiste. None senza nessuno dei due."""
    conoscenza = get_conoscenza()
    if carta:
        trovata = conoscenza.risolvi_carta(carta)
        if trovata is None:
            raise HTTPException(status_code=404, detail="Carta sconosciuta")
        return "carta", trovata
    if stesa:
        trovata = conoscenza.risolvi_stesa(stesa)
        if trovata is None:
            raise HTTPException(status_code=404, detail="Stesa sconosciuta")
        return "stesa", trovata
    return None


@router.get("/posts")
async def elenco(
    session: DbSession,
    sezione: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,80}$"),
    tag: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,80}$"),
    q: str = Query(default="", max_length=100),
    lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}(-[A-Za-z]{2})?$"),
    evidenza: Optional[bool] = None,
    carta: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,60}$", description="Id o slug di una carta."),
    stesa: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,60}$", description="Id o slug di una stesa."),
    pagina: int = Query(default=1, ge=1, le=1000),
    per_pagina: int = Query(default=12, ge=1, le=50),
) -> Dict[str, Any]:
    """Gli articoli pubblicati, dal più recente. `sezione` include le sotto-sezioni.

    `carta=maj-10` (o `stesa=croce-celtica`; anche per slug, `fortune`, `celtic-cross`): l'elenco completo degli
    articoli su quella carta o stesa, per la sua pagina (v9.4) — prima quelli che l'hanno come **soggetto**, poi quelli
    che la **citano**, ciascun gruppo dal più recente. Una carta o una stesa che non esiste: 404.

    `per_pagina` va da 1 a 50 (predefinito 12, per compatibilità): gli elenchi del Journal e delle pagine di carte e
    stese usano 25, con la scelta 10 / 25 / 50."""
    repo = BlogRepository(session)
    ids = None
    if sezione:
        visibili = await repo.sezioni()
        radice = next((s for s in visibili if s.slug == sezione), None)
        if radice is None:
            raise HTTPException(status_code=404, detail="Sezione non trovata")
        ids = repo.discendenti(radice.id, visibili)
    riferimento = _riferimento(carta, stesa)
    posts, totale = await repo.elenco(
        sezioni=ids, tag=tag, testo=q, lang=lang, evidenza=evidenza, pagina=pagina, per_pagina=per_pagina,
        riferimento=riferimento,
    )
    return {
        "totale": totale, "pagina": pagina, "per_pagina": per_pagina,
        "pagine": max(1, -(-totale // per_pagina)),
        "articoli": await articoli_json(session, posts),
    }


async def _gemella_lingua(repo: BlogRepository, session, p: BlogPost) -> Optional[BlogPost]:
    """L'altra metà della coppia it/en di questo articolo, **se collegata** (una traduzione generata
    dalla console, v5 fase E — non un'euristica su slug o titolo): serve solo a scrivere l'hreflang.
    Un articolo scritto a mano in entrambe le lingue, senza passare da 'Genera traduzione', non ha
    questo collegamento e non ottiene l'hreflang finché qualcuno non lo crea così."""
    altra_lingua = {"it": "en", "en": "it"}.get(p.lang)
    if altra_lingua is None:
        return None
    if p.tradotto_da_id:
        originale = await repo.per_id(p.tradotto_da_id)
        return originale if originale and originale.lang == altra_lingua and originale.stato == "pubblicato" else None
    return (
        await session.execute(
            select(BlogPost).where(
                BlogPost.tradotto_da_id == p.id, BlogPost.lang == altra_lingua, BlogPost.stato == "pubblicato",
            ),
        )
    ).scalars().first()


@router.get("/posts/{slug}")
async def articolo(slug: str, session: DbSession) -> Dict[str, Any]:
    if not _SOLO_MINUSCOLE.match(slug):
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    repo = BlogRepository(session)
    p = await repo.per_slug(slug)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    conoscenza = get_conoscenza()
    visibili = await repo.sezioni(solo_visibili=False)
    per_id = {s.id: s for s in visibili}
    autori = await _autori(session, [p])
    base = post_breve_json(p, autori, per_id)

    immagine = await session.get(MediaImage, p.immagine_id) if p.immagine_id else None
    collegamenti = await repo.collegamenti(p)
    # Carte e stese citate: l'id canonico, il nome e l'indirizzo nella lingua dell'articolo, e gli slug in ogni lingua
    # (il testo può citarle con qualunque forma: `maj-17`, `the-star`, `la-stella`).
    carte = [
        {
            "id": c.riferimento, "nome_it": conoscenza.carta(c.riferimento)["nome_it"],
            "nome": conoscenza.nome_carta(c.riferimento, p.lang), "slug": conoscenza.slug_carta(c.riferimento, p.lang),
            "slugs": {k: conoscenza.slug_carta(c.riferimento, k) for k in ("it", *conoscenza.testi)},
        }
        for c in collegamenti if c.tipo == "carta" and c.riferimento in conoscenza.carte
    ]
    stese = [
        {
            "id": c.riferimento, "nome": conoscenza.nome_stesa(conoscenza.stesa(c.riferimento), p.lang),
            "slug": conoscenza.slug_stesa(c.riferimento, p.lang),
            "slugs": {k: conoscenza.slug_stesa(c.riferimento, k) for k in ("it", *conoscenza.testi)},
        }
        for c in collegamenti if c.tipo == "stesa" and conoscenza.stesa(c.riferimento)
    ]
    citati = [c.riferimento for c in collegamenti if c.tipo == "articolo"]
    articoli_citati: List[BlogPost] = []
    for citato in citati:
        altro = await repo.per_slug(citato)
        if altro is not None:
            articoli_citati.append(altro)
    correlati = await repo.correlati(p)
    precedente, successivo = await repo.vicini(p)
    sezione_p = per_id.get(p.sezione_id) if p.sezione_id is not None else None
    gemella = await _gemella_lingua(repo, session, p)
    return base | {
        "gemella_lingua": {"lang": gemella.lang, "slug": gemella.slug} if gemella else None,
        "testo": p.testo,
        "immagine": (
            {"url": url_immagine(p.immagine_id), "alt": p.immagine_alt or p.titolo,
             "larghezza": immagine.larghezza if immagine else None, "altezza": immagine.altezza if immagine else None}
            if p.immagine_id else None
        ),
        "seo_titolo": p.seo_titolo,
        "seo_descrizione": p.seo_descrizione or regole.estratto(p.testo, 160, nome_riferimento),
        "seo_parola_chiave": p.seo_parola_chiave,
        "parole_chiave": list(p.seo_parole_chiave or []),
        "noindex": bool(p.noindex),
        "canonical_url": p.canonical_url,
        "faq": list(p.faq or []),
        "commenti_aperti": p.commenti_aperti,
        "briciole": [{"slug": x.slug, "nome": x.nome} for x in repo.percorso(sezione_p, per_id)],
        "collegamenti": {
            "carte": carte, "stese": stese, "articoli": await articoli_json(session, articoli_citati),
        },
        "correlati": await articoli_json(session, correlati),
        "precedente": (await articoli_json(session, [precedente]))[0] if precedente else None,
        "successivo": (await articoli_json(session, [successivo]))[0] if successivo else None,
    }


@router.get("/tags")
async def etichette(session: DbSession) -> List[Dict[str, Any]]:
    return [{"slug": t.slug, "nome": t.nome, "n": n} for t, n in await BlogRepository(session).tag_con_conteggi()]


@router.get("/links/{tipo}/{riferimento}")
async def articoli_che_citano(
    tipo: str, riferimento: str, session: DbSession, limite: int = Query(default=6, ge=1, le=20),
) -> List[Dict[str, Any]]:
    """Gli articoli che parlano di una carta o di una stesa: per la pagina della carta o della stesa."""
    if tipo not in ("carta", "stesa") or not _SOLO_MINUSCOLE.match(riferimento):
        raise HTTPException(status_code=404, detail="Riferimento sconosciuto")
    posts = await BlogRepository(session).per_riferimento(tipo, riferimento, limite)
    return await articoli_json(session, posts)


#: I punti della pertinenza (v9.4): il soggetto vince sempre sulle citazioni, le citazioni sui correlati, i correlati
#: (3 per etichetta, 2 per sezione o citazione in comune: al più qualche decina) sulla sola sezione o etichetta.
PUNTI_SOGGETTO = 10_000
PUNTI_CITAZIONE = 1_000
PUNTI_SEZIONE_O_ETICHETTA = 1


async def _nove_per_pertinenza(
    repo: BlogRepository, session, *, carta: Optional[str], stesa: Optional[str], sezione: Optional[str],
    articolo: Optional[str], tag: Optional[str], recenti: int, scelti: int, completa: bool, lang: Optional[str],
) -> Dict[str, Any]:
    """Le scelte per una carta, una stesa o un articolo, ordinate per pertinenza (vedi `nove_articoli`)."""
    conoscenza = get_conoscenza()
    contesti: List[Tuple[str, str]] = []  # le carte e le stese della pagina: (tipo, id canonico)
    if carta:
        contesti.append(("carta", conoscenza.risolvi_carta(carta) or carta))
    if stesa:
        contesti.append(("stesa", conoscenza.risolvi_stesa(stesa) or stesa))
    corrente = await repo.per_slug(articolo) if articolo else None
    if corrente is not None and corrente.soggetto_tipo and corrente.soggetto_ref:
        contesti.append((corrente.soggetto_tipo, corrente.soggetto_ref))

    punti: Dict[uuid.UUID, int] = {}
    per_id: Dict[uuid.UUID, BlogPost] = {}

    def somma(posts: List[BlogPost], valore: int) -> None:
        for p in posts:
            if lang and p.lang != lang:
                continue
            per_id[p.id] = p
            punti[p.id] = punti.get(p.id, 0) + valore

    for tipo, rif in dict.fromkeys(contesti):
        somma(await repo.per_soggetto(tipo, rif, 60, lang=lang), PUNTI_SOGGETTO)
        somma(await repo.per_riferimento(tipo, rif, 60, lang=lang), PUNTI_CITAZIONE)
    if corrente is not None:
        affini = await repo.punteggi_correlati(corrente)
        if affini:
            q = select(BlogPost).where(BlogPost.id.in_(list(affini)), await repo.pubblico())
            for p in (await session.execute(q)).scalars():
                somma([p], affini[p.id])
    if sezione:
        visibili = await repo.sezioni()
        radice = next((x for x in visibili if x.slug == sezione), None)
        if radice is not None:
            somma((await repo.elenco(sezioni=repo.discendenti(radice.id, visibili), lang=lang, per_pagina=60))[0],
                  PUNTI_SEZIONE_O_ETICHETTA)
    if tag:
        somma((await repo.elenco(tag=tag, lang=lang, per_pagina=60))[0], PUNTI_SEZIONE_O_ETICHETTA)

    caso = random.Random(f"{datetime.now(timezone.utc).date().isoformat()}|{carta}|{stesa}|{sezione}|{tag}|{articolo}|{lang}")
    esclusi = {corrente.id} if corrente is not None else set()
    # La casualità solo a parità di punteggio: un numero a caso per articolo, assegnato in un ordine fisso (per id).
    sorteggio = {pid: caso.random() for pid in sorted(punti, key=str)}
    ordinati = sorted((pid for pid in punti if pid not in esclusi), key=lambda pid: (-punti[pid], sorteggio[pid]))
    scelti_post = [per_id[pid] for pid in ordinati[:scelti]]
    if completa and len(scelti_post) < scelti:
        visti = esclusi | {p.id for p in scelti_post}
        resto = [p for p in (await repo.elenco(lang=lang, per_pagina=200))[0] if p.id not in visti]
        caso.shuffle(resto)
        scelti_post += resto[: scelti - len(scelti_post)]

    visti = esclusi | {p.id for p in scelti_post}
    recenti_post: List[BlogPost] = []
    if recenti:
        candidati, _ = await repo.elenco(lang=lang, per_pagina=recenti + len(visti))
        recenti_post = [p for p in candidati if p.id not in visti][:recenti]
    return {"recenti": await articoli_json(session, recenti_post), "scelti": await articoli_json(session, scelti_post)}


@router.get("/nove")
async def nove_articoli(
    session: DbSession,
    carta: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,40}$"),
    stesa: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,60}$"),
    sezione: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,80}$"),
    articolo: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,160}$"),
    tag: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,80}$"),
    recenti: int = Query(default=3, ge=0, le=12),
    scelti: int = Query(default=6, ge=0, le=20),
    completa: bool = True,
    lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}(-[A-Za-z]{2})?$"),
) -> Dict[str, Any]:
    """I nove articoli che il sito mostra in ogni pagina (v8.5): i 3 più recenti, e 6 scelti a caso fra quelli
    attinenti alla pagina — che citano la sua carta o la sua stesa, della sua sezione, con le etichette
    dell'articolo che si sta leggendo —, completati a caso con gli altri se non bastano.

    Il caso è stabile per un giorno (seme = data UTC + contesto): un motore di ricerca che passa due volte nello
    stesso giorno vede la stessa pagina, e domani la scelta cambia. L'articolo che si sta leggendo non compare.

    Le pagine del Diario (indice, sezione, etichetta) lo usano con `recenti=6&scelti=10`: con `sezione` o `tag` le
    recenti sono quelle della sezione o dell'etichetta (le stesse della prima pagina del loro elenco), e le 10 a
    caso le escludono.

    `completa=false` (le pagine di sezione e di etichetta del Diario): le scelte restano fra le attinenti, senza
    completarle con il resto del diario. Così la pagina di una sezione mostra solo articoli della sezione (e delle
    sotto-sezioni), tanti quanti ne conta l'albero delle sezioni; una sezione senza articoli non ne mostra.

    **Per pertinenza** (v9.4) nelle pagine di una carta, di una stesa e di un articolo (`carta`, `stesa`, `articolo`),
    dove «Chosen for this page» sta prima degli ultimi articoli: le scelte vengono **prima** delle recenti (che le
    escludono) e sono ordinate per punteggio — gli articoli che hanno quella carta o stesa come **soggetto** (per un
    articolo: il suo soggetto), poi quelli che la **citano**, poi i `correlati` dell'articolo (etichette, sezione,
    citazioni in comune), e più sotto quelli della `sezione` o dell'`etichetta` se date. Il caso del giorno decide
    solo a parità di punteggio. Con `carta` o `stesa` niente riempimento con il resto del diario (come
    `completa=false`); con un articolo sì, in fondo. `lang` tiene solo gli articoli in quella lingua (recenti
    comprese)."""
    repo = BlogRepository(session)
    if carta or stesa or articolo:
        return await _nove_per_pertinenza(
            repo, session, carta=carta, stesa=stesa, sezione=sezione, articolo=articolo, tag=tag, recenti=recenti,
            scelti=scelti, completa=completa and not (carta or stesa), lang=lang,
        )
    visibili = await repo.sezioni() if sezione else []
    radice = next((x for x in visibili if x.slug == sezione), None) if sezione else None
    # Una sezione che non c'è (o è nascosta) non ha articoli: le sue recenti sono nessuna, non tutto il diario.
    ids_sezione = repo.discendenti(radice.id, visibili) if radice is not None else ([] if sezione else None)
    recenti_post = (await repo.elenco(sezioni=ids_sezione, tag=tag, lang=lang, per_pagina=recenti))[0] if recenti else []
    esclusi = {p.id for p in recenti_post}

    attinenti: List[BlogPost] = []
    if ids_sezione is not None:
        attinenti += (await repo.elenco(sezioni=ids_sezione, lang=lang, per_pagina=60))[0]
    if tag:
        attinenti += (await repo.elenco(tag=tag, lang=lang, per_pagina=60))[0]
    gruppi = [attinenti]
    if completa:
        gruppi.append((await repo.elenco(lang=lang, per_pagina=200))[0])

    caso = random.Random(f"{datetime.now(timezone.utc).date().isoformat()}|{carta}|{stesa}|{sezione}|{tag}|{articolo}")
    visti = set(esclusi)
    quanti = scelti
    scelti_post: List[BlogPost] = []
    for gruppo in gruppi:
        candidati = [p for p in {p.id: p for p in gruppo}.values() if p.id not in visti]
        caso.shuffle(candidati)
        for p in candidati[: quanti - len(scelti_post)]:
            scelti_post.append(p)
            visti.add(p.id)
        if len(scelti_post) >= quanti:
            break
    return {"recenti": await articoli_json(session, recenti_post), "scelti": await articoli_json(session, scelti_post)}


@router.get("/mappa")
async def mappa(session: DbSession) -> Dict[str, Any]:
    """Cosa c'è di pubblico, per la mappa del sito."""
    repo = BlogRepository(session)
    visibili = await repo.sezioni()
    per_sezione, per_tag = await repo.lingue_per_sezione_e_tag()
    per_id = {s.id: s for s in visibili}
    sezioni_lingue: Dict[str, List[str]] = {}
    for s in visibili:
        if s.tipo in ("carte", "stese"):
            sezioni_lingue[s.slug] = ["en", "it"]
            continue
        lingue: set = set()
        for sid in repo.discendenti(s.id, visibili):
            lingue |= per_sezione.get(sid, set())
            # Un contenitore con un catalogo nel ramo («Minor Arcana», con i quattro semi) non è vuoto anche senza
            # articoli: è l'indice delle carte e delle stese. La sua lista è la stessa in ogni lingua, quindi conta
            # per l'inglese, la lingua canonica.
            if per_id[sid].tipo in ("carte", "stese"):
                lingue.add("en")
        sezioni_lingue[s.slug] = sorted(lingue)
    return {
        # Un articolo `noindex` non sta nella mappa: la mappa dice ai motori di ricerca cosa indicizzare.
        "articoli": [
            {"slug": s, "aggiornato": d.isoformat(), "lang": lingua}
            for s, d, lingua, noindex in await repo.slug_pubblici() if not noindex
        ],
        "sezioni": [s.slug for s in visibili],
        # Le sezioni tradotte (cataloghi di carte e stese): solo queste hanno una pagina per lingua; le altre sono la
        # stessa lista in ogni lingua, col canonical all'inglese.
        "sezioni_tradotte": [s.slug for s in visibili if s.tipo in ("carte", "stese")],
        "tags": [t.slug for t, _ in await repo.tag_con_conteggi()],
        # Le lingue in cui una sezione (con le sue sotto-sezioni) o un'etichetta ha articoli da indicizzare. Le
        # sezioni «carte» e «stese» sono cataloghi: esistono in ogni lingua.
        "sezioni_lingue": sezioni_lingue,
        "tags_lingue": {slug: sorted(lingue) for slug, lingue in per_tag.items()},
    }


@router.get("/media/{nome}")
async def immagine(nome: str, session: DbSession) -> Response:
    """Un'immagine caricata (articolo, sezione, avatar), o la sua miniatura (`<id>-mini.webp`, per gli elenchi; la
    grande se la miniatura non c'è ancora). Cache immutabile: l'id non si riusa, e la miniatura di un'immagine non
    cambia."""
    if not nome.endswith(".webp"):
        raise HTTPException(status_code=404, detail="Immagine non trovata")
    base = nome[: -len(".webp")]
    mini = base.endswith("-mini")
    try:
        immagine_id = uuid.UUID(base[: -len("-mini")] if mini else base)
    except ValueError:
        raise HTTPException(status_code=404, detail="Immagine non trovata") from None
    img = await session.get(MediaImage, immagine_id)
    if img is None:
        raise HTTPException(status_code=404, detail="Immagine non trovata")
    return Response(
        content=(img.mini_webp or img.webp) if mini else img.webp, media_type="image/webp",
        headers={"Cache-Control": "public, max-age=31536000, immutable", "X-Content-Type-Options": "nosniff"},
    )
