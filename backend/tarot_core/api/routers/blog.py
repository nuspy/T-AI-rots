"""Il blog, per chi legge: sezioni, articoli, etichette, collegamenti con le carte e le stese.

Tutto pubblico e senza account. Il pubblico vede solo gli articoli **pubblicati** la cui data è
già arrivata (`BlogRepository.pubblico`): le bozze, gli articoli
programmati e quelli archiviati non escono da nessuna di queste rotte.

Le immagini stanno nel database e si servono da `GET /blog/media/{id}.webp` con cache
immutabile: l'id è casuale e cambia a ogni caricamento, quindi il contenuto non cambia mai.
"""
from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select

from ...auth.dependencies import DbSession
from ...domain.blog_models import BlogPost, BlogSection, MediaImage
from ...domain.blog_repositories import BlogRepository
from ...domain.models import User
from ...tarot import blog as regole
from ..deps import get_conoscenza

router = APIRouter(prefix="/blog", tags=["blog"])

_SOLO_MINUSCOLE = re.compile(r"^[a-z0-9-]{1,160}$")


# ---- serializzazione ------------------------------------------------------------------------


def url_immagine(immagine_id: Optional[uuid.UUID]) -> Optional[str]:
    return f"/blog/media/{immagine_id}.webp" if immagine_id else None


def url_miniatura(immagine_id: Optional[uuid.UUID]) -> Optional[str]:
    """La miniatura per gli elenchi. Se un'immagine non l'ha ancora, lo stesso indirizzo serve la grande."""
    return f"/blog/media/{immagine_id}-mini.webp" if immagine_id else None


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
    }


async def articoli_json(session, posts: List[BlogPost]) -> List[Dict[str, Any]]:
    repo = BlogRepository(session)
    sezioni = {s.id: s for s in await repo.sezioni(solo_visibili=False)}
    autori = await _autori(session, posts)
    return [post_breve_json(p, autori, sezioni) for p in posts]


# ---- elementi del catalogo per le sezioni «carte» e «stese» ------------------------------------------


def _elementi_catalogo(sezione: BlogSection, lang: Optional[str] = None) -> List[Dict[str, Any]]:
    conoscenza = get_conoscenza()
    filtro = sezione.filtro or {}
    if sezione.tipo == "carte":
        carte = [conoscenza.carta(i) for i in conoscenza.ordine]
        if "arcano" in filtro:
            carte = [c for c in carte if c["arcano"] == filtro["arcano"]]
        if "seme" in filtro:
            carte = [c for c in carte if c.get("seme") == filtro["seme"]]
        return [conoscenza.carta_pubblica(c["id"], lang=lang) for c in carte]
    if sezione.tipo == "stese":
        stese = conoscenza.stese.values()
        if "categoria" in filtro:
            stese = [s for s in stese if conoscenza.categoria_di(s) == filtro["categoria"]]
        return [
            {k: v for k, v in conoscenza.stesa_pubblica(s, lang).items()
             if k in ("id", "nome", "nomi", "descrizione", "categoria", "stile", "posizioni", "lang", "slug", "slugs")}
            for s in stese
        ]
    return []


# ---- sezioni -----------------------------------------------------------------------------------------


def _nodo(s: BlogSection, figli: Dict[Optional[int], List[BlogSection]], conteggi: Dict[int, int]) -> Dict[str, Any]:
    sotto = [_nodo(f, figli, conteggi) for f in figli.get(s.id, [])]
    return {
        "id": s.id,
        "slug": s.slug,
        "nome": s.nome,
        "descrizione": s.descrizione,
        "tipo": s.tipo,
        "filtro": s.filtro,
        "immagine": url_immagine(s.immagine_id),
        "n_articoli": conteggi.get(s.id, 0),
        "n_elementi": len(_elementi_catalogo(s)) if s.tipo in ("carte", "stese") else None,
        "figli": sotto,
    }


@router.get("/sections")
async def albero(session: DbSession) -> List[Dict[str, Any]]:
    """L'albero delle sezioni visibili, con il numero di articoli di ciascuna."""
    repo = BlogRepository(session)
    sezioni = await repo.sezioni()
    figli: Dict[Optional[int], List[BlogSection]] = {}
    ids = {s.id for s in sezioni}
    for s in sezioni:
        figli.setdefault(s.parent_id if s.parent_id in ids else None, []).append(s)
    conteggi = await repo.conteggi_per_sezione()
    return [_nodo(s, figli, conteggi) for s in figli.get(None, [])]


@router.get("/sections/{slug}")
async def sezione(
    slug: str, session: DbSession,
    lang: Optional[str] = Query(default=None, max_length=10, pattern="^[A-Za-z-]*$"),
) -> Dict[str, Any]:
    """Una sezione. `lang` sceglie la lingua dei nomi e degli slug di carte e stese del catalogo."""
    repo = BlogRepository(session)
    visibili = await repo.sezioni()
    per_id = {s.id: s for s in visibili}
    s = next((x for x in visibili if x.slug == slug), None)
    if s is None:
        raise HTTPException(status_code=404, detail="Sezione non trovata")
    conteggi = await repo.conteggi_per_sezione()
    figli_di: Dict[Optional[int], List[BlogSection]] = {}
    for x in visibili:
        figli_di.setdefault(x.parent_id, []).append(x)
    nodo = _nodo(s, figli_di, conteggi)
    return nodo | {
        "seo_titolo": s.seo_titolo,
        "seo_descrizione": s.seo_descrizione,
        "briciole": [{"slug": x.slug, "nome": x.nome} for x in repo.percorso(s, per_id)],
        "elementi": _elementi_catalogo(s, lang),
    }


# ---- articoli --------------------------------------------------------------------------------------------


@router.get("/posts")
async def elenco(
    session: DbSession,
    sezione: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,80}$"),
    tag: Optional[str] = Query(default=None, pattern="^[a-z0-9-]{1,80}$"),
    q: str = Query(default="", max_length=100),
    lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}(-[A-Za-z]{2})?$"),
    evidenza: Optional[bool] = None,
    pagina: int = Query(default=1, ge=1, le=1000),
    per_pagina: int = Query(default=12, ge=1, le=50),
) -> Dict[str, Any]:
    """Gli articoli pubblicati, dal più recente. `sezione` include le sotto-sezioni."""
    repo = BlogRepository(session)
    ids = None
    if sezione:
        visibili = await repo.sezioni()
        radice = next((s for s in visibili if s.slug == sezione), None)
        if radice is None:
            raise HTTPException(status_code=404, detail="Sezione non trovata")
        ids = repo.discendenti(radice.id, visibili)
    posts, totale = await repo.elenco(
        sezioni=ids, tag=tag, testo=q, lang=lang, evidenza=evidenza, pagina=pagina, per_pagina=per_pagina,
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


@router.get("/mappa")
async def mappa(session: DbSession) -> Dict[str, Any]:
    """Cosa c'è di pubblico, per la mappa del sito."""
    repo = BlogRepository(session)
    visibili = await repo.sezioni()
    per_sezione, per_tag = await repo.lingue_per_sezione_e_tag()
    sezioni_lingue: Dict[str, List[str]] = {}
    for s in visibili:
        if s.tipo in ("carte", "stese"):
            sezioni_lingue[s.slug] = ["en", "it"]
            continue
        lingue: set = set()
        for sid in repo.discendenti(s.id, visibili):
            lingue |= per_sezione.get(sid, set())
        sezioni_lingue[s.slug] = sorted(lingue)
    return {
        # Un articolo `noindex` non sta nella mappa: la mappa dice ai motori di ricerca cosa indicizzare.
        "articoli": [
            {"slug": s, "aggiornato": d.isoformat(), "lang": lingua}
            for s, d, lingua, noindex in await repo.slug_pubblici() if not noindex
        ],
        "sezioni": [s.slug for s in await repo.sezioni()],
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
