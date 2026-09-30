"""La pubblicazione sul blog via REST, con una chiave applicativa.

Per gli agenti (Hermes, OpenClaw, uno script) che scrivono e pubblicano articoli senza passare dalla console. Si
presentano con `Authorization: Bearer tk_live_…` o `X-API-Key` (`auth/chiavi.py`); le chiavi si creano dalla console.

Il formato dell'articolo è quello del blog — **titolo, sottotitolo, immagine, testo** — più i campi SEO:
`seo_titolo`, `seo_descrizione`, `seo_parola_chiave`, `seo_parole_chiave`, `slug`, `canonical_url`, `noindex`, `faq`,
`immagine_alt`, `tags`, `sezione`, `lang`. Ogni salvataggio risponde anche con il **rapporto SEO** (`seo`: punteggio,
controlli, suggerimenti), così l'agente sa cosa correggere; `dry_run: true` (o `POST /v1/blog/seo-check`) lo dà senza
salvare niente.

**Le regole di sicurezza** (nessuna si aggira con un parametro):
- una chiave con `blog:write` crea **bozze**; `stato: "pubblicato"`, `pubblicato_il` e `in_evidenza` servono
  `blog:publish`, altrimenti l'articolo resta bozza e la risposta lo dice in `avvisi`;
- una chiave modifica e cancella **solo gli articoli che ha creato**, e cancella solo le bozze;
- l'eccezione è `blog:media`: cambia le **sole immagini** (copertina e immagini nel testo) di qualunque articolo;
- niente scaricamento di immagini da un indirizzo (sarebbe una richiesta dal nostro server verso un indirizzo scelto
  da fuori): l'immagine arriva come corpo (`POST /v1/blog/media`) o come `immagine_base64`;
- un tetto di articoli al giorno e di richieste al minuto per chiave.

La lingua predefinita è l'**inglese** (`lang: "en"`): il sito è pensato per un pubblico internazionale.
"""
from __future__ import annotations

import asyncio
import base64
import binascii
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from ...auth.chiavi import ChiaveVerificata, richiede
from ...auth.dependencies import DbSession
from ...domain.base import utcnow
from ...domain.blog_models import BlogPost, BlogSection, MediaImage
from ...domain.blog_repositories import BlogRepository, ErroreBlog, assicura_miniatura
from ...domain.repositories import AuditRepository
from ...settings import get_settings
from ...tarot import blog as regole
from ...tarot import blog_seo
from ..deps import get_conoscenza
from .admin_blog import FaqIn, articolo_admin_json
from .blog import url_immagine, url_miniatura

router = APIRouter(prefix="/v1/blog", tags=["rest-blog"])

MAX_BASE64 = 11_500_000  # 8 MB di immagine in base64


# ---- il formato dell'articolo -----------------------------------------------------------------------------------


class ArticoloRest(BaseModel):
    titolo: str = Field(min_length=1, max_length=200, description="Il titolo (H1). Meglio sotto i 60 caratteri, con la parola chiave.")
    sottotitolo: Optional[str] = Field(default=None, max_length=300)
    testo: str = Field(default="", max_length=200_000, description="Markdown. Non si esegue HTML. Scorciatoie: [[card:the-star]], [[spread:celtic-cross]], [[post:un-articolo]].")
    lang: str = Field(default="en", pattern="^[a-z]{2}(-[A-Za-z]{2})?$", description="La lingua dell'articolo. Predefinita: en.")
    sezione: Optional[str] = Field(default=None, max_length=80, description="Lo slug (o l'id) di una sezione di tipo «articoli»: vedi GET /v1/blog/sections.")
    tags: List[str] = Field(default_factory=list, max_length=10)
    slug: Optional[str] = Field(default=None, max_length=160, description="Vuoto: lo ricava dal titolo.")
    immagine_id: Optional[uuid.UUID] = Field(default=None, description="L'id di un'immagine già caricata con POST /v1/blog/media.")
    immagine_base64: Optional[str] = Field(default=None, description="In alternativa: l'immagine (PNG, JPEG o WebP) in base64, anche come data URL.")
    immagine_alt: Optional[str] = Field(default=None, max_length=200)
    seo_titolo: Optional[str] = Field(default=None, max_length=200, description="30–60 caratteri, parola chiave all'inizio. Vuoto: usa il titolo.")
    seo_descrizione: Optional[str] = Field(default=None, max_length=320, description="120–160 caratteri.")
    seo_parola_chiave: Optional[str] = Field(default=None, max_length=120, description="La frase per cui l'articolo deve farsi trovare.")
    seo_parole_chiave: List[str] = Field(default_factory=list, max_length=blog_seo.PAROLE_CHIAVE_MAX)
    canonical_url: Optional[str] = Field(default=None, max_length=500)
    noindex: bool = False
    faq: List[FaqIn] = Field(default_factory=list, max_length=blog_seo.FAQ_MAX)
    stato: Literal["bozza", "pubblicato"] = "bozza"
    pubblicato_il: Optional[datetime] = Field(default=None, description="Nel futuro: programma l'uscita (serve blog:publish).")
    in_evidenza: bool = False
    dry_run: bool = Field(default=False, description="Vero: non salva, restituisce solo il rapporto SEO.")


class ArticoloRestMod(BaseModel):
    titolo: Optional[str] = Field(default=None, min_length=1, max_length=200)
    sottotitolo: Optional[str] = Field(default=None, max_length=300)
    testo: Optional[str] = Field(default=None, max_length=200_000)
    lang: Optional[str] = Field(default=None, pattern="^[a-z]{2}(-[A-Za-z]{2})?$")
    sezione: Optional[str] = Field(default=None, max_length=80)
    tags: Optional[List[str]] = Field(default=None, max_length=10)
    slug: Optional[str] = Field(default=None, max_length=160)
    immagine_id: Optional[uuid.UUID] = None
    immagine_base64: Optional[str] = None
    immagine_alt: Optional[str] = Field(default=None, max_length=200)
    seo_titolo: Optional[str] = Field(default=None, max_length=200)
    seo_descrizione: Optional[str] = Field(default=None, max_length=320)
    seo_parola_chiave: Optional[str] = Field(default=None, max_length=120)
    seo_parole_chiave: Optional[List[str]] = Field(default=None, max_length=blog_seo.PAROLE_CHIAVE_MAX)
    canonical_url: Optional[str] = Field(default=None, max_length=500)
    noindex: Optional[bool] = None
    faq: Optional[List[FaqIn]] = Field(default=None, max_length=blog_seo.FAQ_MAX)
    stato: Optional[Literal["bozza", "pubblicato", "archiviato"]] = None
    pubblicato_il: Optional[datetime] = None
    in_evidenza: Optional[bool] = None


# ---- aiuti ---------------------------------------------------------------------------------------------------


def _errore(detail: Any, stato: int = 422) -> HTTPException:
    return HTTPException(status_code=stato, detail=detail)


def _host() -> Optional[str]:
    return urlparse(get_settings().web_public_url or "").netloc or None


def _url_pubblico(p: BlogPost) -> str:
    base = (get_settings().web_public_url or "").rstrip("/")
    return f"{base}{'/it' if p.lang == 'it' else ''}/blog/{p.slug}"


def _in_utc(quando: Optional[datetime]) -> Optional[datetime]:
    if quando is None:
        return None
    return quando if quando.tzinfo else quando.replace(tzinfo=timezone.utc)


async def _sezione_id(repo: BlogRepository, valore: Optional[str]) -> Optional[int]:
    """Da uno slug (o un id) alla sezione; deve essere di tipo «articoli». Altrimenti l'errore elenca quelle valide."""
    if valore is None or not valore.strip():
        return None
    valore = valore.strip()
    sezioni = await repo.sezioni()
    trovata = next((s for s in sezioni if s.slug == valore or str(s.id) == valore), None)
    valide = sorted(s.slug for s in sezioni if s.tipo == "articoli")
    if trovata is None or trovata.tipo != "articoli":
        raise _errore({"errore": "sezione_non_valida", "sezione": valore, "sezioni_valide": valide})
    return trovata.id


async def _immagine_da_base64(session, testo: str) -> uuid.UUID:
    dati = testo.strip()
    if dati.startswith("data:"):
        dati = dati.split(",", 1)[-1]
    if len(dati) > MAX_BASE64:
        raise _errore("Immagine troppo grande (8 MB al massimo).", 413)
    try:
        grezzi = base64.b64decode(dati, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise _errore("L'immagine non è base64 valido.") from exc
    try:
        webp, larghezza, altezza = await asyncio.to_thread(regole.prepara_immagine_articolo, grezzi)
    except regole.ImmagineNonValida as exc:
        raise _errore(str(exc)) from exc
    img = MediaImage(uso="blog", webp=webp, larghezza=larghezza, altezza=altezza, owner_id=None)
    await assicura_miniatura(img)
    session.add(img)
    await session.flush()
    return img.id


def _rapporto(*, titolo: str, testo: str, slug: str, sottotitolo: Optional[str], seo_titolo: Optional[str],
              seo_descrizione: Optional[str], parola_chiave: Optional[str], immagine_presente: bool,
              immagine_alt: Optional[str], tags: List[str], faq: List[Any]) -> Dict[str, Any]:
    return blog_seo.analizza(
        titolo=titolo, testo=testo, slug=slug, sottotitolo=sottotitolo, seo_titolo=seo_titolo, seo_descrizione=seo_descrizione,
        parola_chiave=parola_chiave, immagine_presente=immagine_presente, immagine_alt=immagine_alt, tags=tags, faq=faq,
        host=_host(),
    )


def _rapporto_di(p: BlogPost) -> Dict[str, Any]:
    return _rapporto(
        titolo=p.titolo, testo=p.testo, slug=p.slug, sottotitolo=p.sottotitolo, seo_titolo=p.seo_titolo,
        seo_descrizione=p.seo_descrizione, parola_chiave=p.seo_parola_chiave, immagine_presente=bool(p.immagine_id),
        immagine_alt=p.immagine_alt, tags=[t.nome for t in p.tags], faq=list(p.faq or []),
    )


async def _risposta(session, p: BlogPost, avvisi: List[str]) -> Dict[str, Any]:
    articolo = await articolo_admin_json(session, p)
    return {"articolo": articolo, "url": _url_pubblico(p), "seo": _rapporto_di(p), "avvisi": avvisi}


def _regole_di_pubblicazione(chiave: ChiaveVerificata, dati: Dict[str, Any], avvisi: List[str]) -> None:
    """Senza `blog:publish` lo stato torna a bozza e la programmazione e l'evidenza si ignorano: sempre con un avviso."""
    if chiave.puo("blog:publish"):
        return
    if dati.get("stato") in ("pubblicato", "archiviato"):
        dati["stato"] = "bozza"
        avvisi.append("Saved as a draft: this key has no `blog:publish` permission. An editor publishes it from the console.")
    if dati.get("pubblicato_il") is not None:
        dati.pop("pubblicato_il")
        avvisi.append("`pubblicato_il` ignored: this key cannot schedule or publish.")
    if dati.get("in_evidenza"):
        dati["in_evidenza"] = False
        avvisi.append("`in_evidenza` ignored: this key cannot feature articles.")


async def _dati_per_salvare(
    session, repo: BlogRepository, payload: BaseModel, *, esclusi_none: bool,
) -> Dict[str, Any]:
    """Dal payload REST ai campi di `BlogRepository.salva` (con la sezione risolta e l'immagine caricata)."""
    grezzi = payload.model_dump(exclude_unset=esclusi_none)
    campi = (
        "titolo", "sottotitolo", "testo", "lang", "slug", "immagine_alt", "seo_titolo", "seo_descrizione",
        "seo_parola_chiave", "seo_parole_chiave", "canonical_url", "noindex", "stato", "pubblicato_il", "in_evidenza",
    )
    dati: Dict[str, Any] = {c: grezzi[c] for c in campi if c in grezzi}
    if "pubblicato_il" in dati:
        dati["pubblicato_il"] = _in_utc(dati["pubblicato_il"])
    if grezzi.get("faq") is not None:
        dati["faq"] = grezzi["faq"]
    if "sezione" in grezzi:
        dati["sezione_id"] = await _sezione_id(repo, grezzi["sezione"])
    if grezzi.get("immagine_base64"):
        dati["immagine_id"] = await _immagine_da_base64(session, grezzi["immagine_base64"])
    elif grezzi.get("immagine_id") is not None:
        dati["immagine_id"] = grezzi["immagine_id"]
    return dati


# ---- scoprire cosa si può fare ------------------------------------------------------------------------------------


@router.get("/guide")
async def guida(chiave: ChiaveVerificata = Depends(richiede("blog:write", "blog:media"))) -> Dict[str, Any]:
    """Cosa accetta il blog e con quali soglie SEO: da leggere una volta, prima di scrivere."""
    return {
        "chiave": {"nome": chiave.nome, "prefisso": chiave.prefisso, "scopes": list(chiave.scopes), "limite_giorno": chiave.limite_giorno},
        "lingua_predefinita": "en",
        "formato": "Markdown, senza HTML. Titoli di sezione con `##`; il titolo dell'articolo è già l'H1.",
        "scorciatoie": {
            "carta": "[[card:the-star]]  (anche [[carta:maj-17]])",
            "stesa": "[[spread:celtic-cross]]  (anche [[stesa:croce-celtica]])",
            "articolo": "[[post:slug-di-un-articolo]]  (anche [[articolo:slug]])",
        },
        "soglie_seo": blog_seo.SOGLIE,
        "limiti": {"faq": blog_seo.FAQ_MAX, "parole_chiave_secondarie": blog_seo.PAROLE_CHIAVE_MAX, "etichette": 10, "immagine": "8 MB, PNG/JPEG/WebP"},
        "regole": [
            "Con blog:write si creano bozze; per pubblicare serve blog:publish.",
            "Una chiave modifica e cancella solo i propri articoli; cancella solo bozze.",
            "Le immagini non si scaricano da un indirizzo: si caricano (POST /v1/blog/media) o arrivano in base64.",
        ],
        "percorsi": {
            "sezioni": "GET /v1/blog/sections", "catalogo_carte_e_stese": "GET /v1/blog/catalog", "etichette": "GET /v1/blog/tags",
            "articoli_miei": "GET /v1/blog/posts", "controllo_seo": "POST /v1/blog/seo-check", "immagine": "POST /v1/blog/media",
            "crea": "POST /v1/blog/posts", "modifica": "PATCH /v1/blog/posts/{id}", "elimina_bozza": "DELETE /v1/blog/posts/{id}",
            "immagini_di_tutti_con_blog_media": "GET /v1/blog/media-posts, GET /v1/blog/media-posts/{id}, PUT /v1/blog/posts/{id}/cover, PUT /v1/blog/posts/{id}/inline",
        },
        "immagini": [
            "Nel testo: ![testo alternativo](/blog/media/<id>.webp), su una riga da sola, dove l'immagine serve al discorso.",
            "Ogni immagine caricata riceve da sola la sua miniatura per gli elenchi (campo `mini`): non va caricata a parte.",
            "Didascalia: nel titolo dell'immagine, ![alt](/blog/media/<id>.webp \"la didascalia\").",
            "Video: [[video:youtube:ID]] o [[video:vimeo:ID]] su una riga da sola.",
            "Testo ricco, con misura: :text[frase]{color=brass|plum|verdigris|muted size=small|large|title}, "
            ":underline[frase] (anche in italiano: :testo[…]{colore=ottone dimensione=grande}, :sottolineato[…]). "
            "Solo questi valori: il resto si ignora, e nessun HTML viene eseguito.",
        ],
    }


@router.get("/sections")
async def sezioni(session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:write"))) -> List[Dict[str, Any]]:
    """Le sezioni in cui si può pubblicare (tipo «articoli»), con il percorso nell'albero."""
    repo = BlogRepository(session)
    visibili = await repo.sezioni()
    per_id = {s.id: s for s in visibili}
    return [
        {"id": s.id, "slug": s.slug, "nome": s.nome, "percorso": " › ".join(x.nome for x in repo.percorso(s, per_id)), "descrizione": s.descrizione}
        for s in visibili if s.tipo == "articoli"
    ]


@router.get("/tags")
async def etichette(session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:write"))) -> List[Dict[str, Any]]:
    """Le etichette già usate, con quanti articoli: meglio riusarle che moltiplicarne di quasi uguali."""
    return [{"slug": t.slug, "nome": t.nome, "n": n} for t, n in await BlogRepository(session).tag_con_conteggi()]


@router.get("/catalog")
async def catalogo(chiave: ChiaveVerificata = Depends(richiede("blog:write"))) -> Dict[str, Any]:
    """Carte e stese con la scorciatoia pronta da scrivere nel testo per un collegamento interno."""
    k = get_conoscenza()
    return {
        "carte": [
            {"id": i, "slug": k.slug_carta(i, "en"), "nome": k.nome_carta(i, "en"), "scorciatoia": f"[[card:{k.slug_carta(i, 'en')}]]"}
            for i in k.ordine
        ],
        "stese": [
            {"id": s["id"], "slug": k.slug_stesa(s["id"], "en"), "nome": k.stesa_pubblica(s, "en")["nome"],
             "scorciatoia": f"[[spread:{k.slug_stesa(s['id'], 'en')}]]"}
            for s in k.stese.values()
        ],
    }


# ---- SEO senza salvare --------------------------------------------------------------------------------------------


@router.post("/seo-check")
async def controllo_seo(payload: ArticoloRest, chiave: ChiaveVerificata = Depends(richiede("blog:write"))) -> Dict[str, Any]:
    """Il rapporto SEO di un articolo senza salvarlo: punteggio, controlli, suggerimenti."""
    return _rapporto(
        titolo=payload.titolo, testo=payload.testo, slug=payload.slug or regole.slugify(payload.titolo),
        sottotitolo=payload.sottotitolo, seo_titolo=payload.seo_titolo, seo_descrizione=payload.seo_descrizione,
        parola_chiave=payload.seo_parola_chiave, immagine_presente=bool(payload.immagine_id or payload.immagine_base64),
        immagine_alt=payload.immagine_alt, tags=payload.tags, faq=[f.model_dump() for f in payload.faq],
    )


# ---- immagini ------------------------------------------------------------------------------------------------------


@router.post("/media", status_code=201)
async def carica_immagine(request: Request, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:write", "blog:media"))) -> Dict[str, Any]:
    """Carica un'immagine: come corpo grezzo (`Content-Type: image/png|jpeg|webp`) o come JSON
    `{"immagine_base64": "…"}`. Si orienta, si porta a 1600 px di larghezza al massimo e si riscrive in WebP."""
    tipo = request.headers.get("content-type", "")
    if tipo.startswith("application/json"):
        corpo = await request.json()
        testo = corpo.get("immagine_base64") if isinstance(corpo, dict) else None
        if not isinstance(testo, str):
            raise _errore("Manca `immagine_base64`.")
        immagine_id = await _immagine_da_base64(session, testo)
    elif tipo.startswith("image/"):
        if int(request.headers.get("content-length") or 0) > regole.MAX_CARICO_IMMAGINE:
            raise _errore("Immagine troppo grande (8 MB al massimo).", 413)
        try:
            webp, larghezza, altezza = await asyncio.to_thread(regole.prepara_immagine_articolo, await request.body())
        except regole.ImmagineNonValida as exc:
            raise _errore(str(exc)) from exc
        img = MediaImage(uso="blog", webp=webp, larghezza=larghezza, altezza=altezza, owner_id=None)
        await assicura_miniatura(img)
        session.add(img)
        await session.flush()
        immagine_id = img.id
    else:
        raise HTTPException(status_code=415, detail="Serve un'immagine (`image/*`) o JSON con `immagine_base64`.")
    img = await session.get(MediaImage, immagine_id)
    await AuditRepository(session).record(
        action="blog.rest.media", actor_id=None, target_type="media_image", target_id=str(immagine_id),
        after={"chiave": chiave.prefisso, "byte": len(img.webp) if img else 0},
    )
    await session.commit()
    assert img is not None
    return {
        "id": str(immagine_id), "url": url_immagine(immagine_id), "mini": url_miniatura(immagine_id),
        "larghezza": img.larghezza, "altezza": img.altezza, "byte": len(img.webp),
    }


# ---- gli articoli --------------------------------------------------------------------------------------------------


async def _proprio(session, post_id: uuid.UUID, chiave: ChiaveVerificata) -> BlogPost:
    p = await BlogRepository(session).per_id(post_id)
    if p is None or p.creato_da_chiave_id != chiave.id:
        # Lo stesso errore per «non esiste» e «non è tuo»: non si rivela quali articoli ci sono.
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    return p


@router.post("/posts", status_code=201)
async def crea(payload: ArticoloRest, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:write"))) -> Dict[str, Any]:
    """Crea un articolo. Con `dry_run: true` restituisce solo il rapporto SEO."""
    repo = BlogRepository(session)
    avvisi: List[str] = []
    if payload.dry_run:
        rapporto = await controllo_seo(payload, chiave)
        await _sezione_id(repo, payload.sezione)  # una sezione sbagliata si scopre anche in prova
        return {"dry_run": True, "seo": rapporto, "avvisi": avvisi}

    inizio_giorno = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    creati = int((await session.execute(
        select(func.count()).select_from(BlogPost).where(BlogPost.creato_da_chiave_id == chiave.id, BlogPost.created_at >= inizio_giorno)
    )).scalar_one())
    if creati >= chiave.limite_giorno:
        raise HTTPException(status_code=429, detail=f"Limite giornaliero raggiunto ({chiave.limite_giorno} articoli).")

    dati = await _dati_per_salvare(session, repo, payload, esclusi_none=False)
    _regole_di_pubblicazione(chiave, dati, avvisi)
    try:
        p = await repo.salva(None, dati, autore_id=None, tag=payload.tags, chiave_id=chiave.id)
    except ErroreBlog as exc:
        await session.rollback()
        raise _errore(str(exc)) from exc
    await AuditRepository(session).record(
        action="blog.rest.create", actor_id=None, target_type="blog_post", target_id=str(p.id),
        after={"chiave": chiave.prefisso, "slug": p.slug, "stato": p.stato},
    )
    risposta = await _risposta(session, p, avvisi)
    await session.commit()
    return risposta


@router.get("/posts")
async def elenco(
    session: DbSession,
    stato: Optional[Literal["bozza", "pubblicato", "archiviato"]] = None,
    pagina: int = Query(default=1, ge=1),
    per_pagina: int = Query(default=25, ge=1, le=100),
    chiave: ChiaveVerificata = Depends(richiede("blog:write")),
) -> Dict[str, Any]:
    """Gli articoli creati da questa chiave (per evitare doppioni e scegliere una parola chiave non ancora usata)."""
    q = select(BlogPost).where(BlogPost.creato_da_chiave_id == chiave.id)
    if stato:
        q = q.where(BlogPost.stato == stato)
    totale = int((await session.execute(select(func.count()).select_from(q.subquery()))).scalar_one())
    q = q.order_by(BlogPost.created_at.desc()).limit(per_pagina).offset((pagina - 1) * per_pagina)
    posts = list((await session.execute(q)).scalars())
    return {
        "totale": totale, "pagina": pagina, "per_pagina": per_pagina,
        "articoli": [await articolo_admin_json(session, p, con_testo=False) for p in posts],
    }


@router.get("/posts/{post_id}")
async def leggi(post_id: uuid.UUID, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:write"))) -> Dict[str, Any]:
    p = await _proprio(session, post_id, chiave)
    return await _risposta(session, p, [])


@router.patch("/posts/{post_id}")
async def modifica(
    post_id: uuid.UUID, payload: ArticoloRestMod, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:write")),
) -> Dict[str, Any]:
    """Modifica un articolo creato da questa chiave: si mandano solo i campi da cambiare."""
    p = await _proprio(session, post_id, chiave)
    repo = BlogRepository(session)
    avvisi: List[str] = []
    dati = await _dati_per_salvare(session, repo, payload, esclusi_none=True)
    _regole_di_pubblicazione(chiave, dati, avvisi)
    # Un articolo già pubblicato da un editor non torna bozza per mano di una chiave senza permesso.
    if not chiave.puo("blog:publish") and p.stato != "bozza":
        raise HTTPException(status_code=403, detail="L'articolo è già stato pubblicato: modificarlo serve `blog:publish`.")
    try:
        await repo.salva(p, dati, autore_id=None, tag=payload.tags if payload.tags is not None else None)
    except ErroreBlog as exc:
        await session.rollback()
        raise _errore(str(exc)) from exc
    await AuditRepository(session).record(
        action="blog.rest.update", actor_id=None, target_type="blog_post", target_id=str(p.id),
        after={"chiave": chiave.prefisso, "slug": p.slug, "stato": p.stato},
    )
    risposta = await _risposta(session, p, avvisi)
    await session.commit()
    return risposta


@router.delete("/posts/{post_id}", status_code=204)
async def elimina(post_id: uuid.UUID, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:write"))) -> None:
    """Elimina una **bozza** creata da questa chiave. Un articolo pubblicato si toglie dalla console."""
    p = await _proprio(session, post_id, chiave)
    if p.stato != "bozza":
        raise HTTPException(status_code=409, detail="Si cancellano solo le bozze; un articolo pubblicato si archivia dalla console.")
    await AuditRepository(session).record(
        action="blog.rest.delete", actor_id=None, target_type="blog_post", target_id=str(p.id),
        before={"chiave": chiave.prefisso, "slug": p.slug},
    )
    await BlogRepository(session).elimina(p)
    await session.commit()


# ---- le immagini di qualunque articolo (`blog:media`) ------------------------------------------------------------
#
# Uno skill che rifà le immagini del blog lavora su tutti gli articoli, anche pubblicati e scritti da altri: per
# questo c'è un permesso a parte, che tocca **solo** le immagini. Il testo cambia soltanto nelle righe delle immagini
# (e si salva con `BlogRepository.salva`, quindi con la versione precedente conservata); titolo, SEO e stato mai.

_IMMAGINE_MD = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)')


def _immagini_nel_testo(testo: str) -> List[Dict[str, Any]]:
    return [{"indice": i, "alt": m.group(1), "url": m.group(2)} for i, m in enumerate(_IMMAGINE_MD.finditer(testo))]


def _alt_pulito(alt: str) -> str:
    return re.sub(r"[\[\]\n]+", " ", alt).strip()[:200]


async def _media_post_json(session, p: BlogPost, *, con_testo: bool) -> Dict[str, Any]:
    sezione = await session.get(BlogSection, p.sezione_id) if p.sezione_id is not None else None
    dati: Dict[str, Any] = {
        "id": str(p.id), "slug": p.slug, "titolo": p.titolo, "sottotitolo": p.sottotitolo, "lang": p.lang,
        "stato": p.stato, "sezione": sezione.nome if sezione else None, "parola_chiave": p.seo_parola_chiave,
        "tags": [t.nome for t in p.tags], "url": _url_pubblico(p),
        "estratto": regole.estratto(p.testo, 400),
        "copertina": (
            {"id": str(p.immagine_id), "url": url_immagine(p.immagine_id), "mini": url_miniatura(p.immagine_id), "alt": p.immagine_alt}
            if p.immagine_id else None
        ),
        "immagini_nel_testo": _immagini_nel_testo(p.testo),
    }
    if con_testo:
        dati["testo"] = p.testo
    return dati


async def _articolo_qualunque(session, post_id: uuid.UUID) -> BlogPost:
    p = await BlogRepository(session).per_id(post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    return p


async def _immagine_scelta(session, immagine_id: Optional[uuid.UUID], immagine_base64: Optional[str]) -> uuid.UUID:
    """L'immagine indicata (già caricata) o quella in base64 (che si carica adesso), con la sua miniatura."""
    if immagine_base64:
        return await _immagine_da_base64(session, immagine_base64)
    if immagine_id is None:
        raise _errore("Serve `immagine_id` (da POST /v1/blog/media) o `immagine_base64`.")
    img = await session.get(MediaImage, immagine_id)
    if img is None:
        raise _errore("L'immagine non esiste.", 404)
    await assicura_miniatura(img)
    return img.id


@router.get("/media-posts")
async def media_articoli(
    session: DbSession,
    stato: Optional[Literal["bozza", "pubblicato", "archiviato"]] = None,
    lang: Optional[str] = Query(default=None, pattern="^[a-z]{2}$"),
    pagina: int = Query(default=1, ge=1),
    per_pagina: int = Query(default=25, ge=1, le=100),
    chiave: ChiaveVerificata = Depends(richiede("blog:media")),
) -> Dict[str, Any]:
    """Tutti gli articoli, con copertina e immagini nel testo: per scegliere quali immagini rifare."""
    q = select(BlogPost)
    if stato:
        q = q.where(BlogPost.stato == stato)
    if lang:
        q = q.where(BlogPost.lang == lang)
    totale = int((await session.execute(select(func.count()).select_from(q.subquery()))).scalar_one())
    q = q.order_by(BlogPost.created_at.desc()).limit(per_pagina).offset((pagina - 1) * per_pagina)
    posts = list((await session.execute(q)).scalars())
    return {
        "totale": totale, "pagina": pagina, "per_pagina": per_pagina,
        "articoli": [await _media_post_json(session, p, con_testo=False) for p in posts],
    }


@router.get("/media-posts/{post_id}")
async def media_articolo(post_id: uuid.UUID, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:media"))) -> Dict[str, Any]:
    """Un articolo con il testo intero: per capire di che cosa parla e dove un'immagine serve al discorso."""
    return await _media_post_json(session, await _articolo_qualunque(session, post_id), con_testo=True)


class CopertinaIn(BaseModel):
    immagine_id: Optional[uuid.UUID] = None
    immagine_base64: Optional[str] = None
    alt: str = Field(min_length=3, max_length=200, description="Descrive l'immagine per chi non la vede (e per i motori).")


@router.put("/posts/{post_id}/cover")
async def cambia_copertina(
    post_id: uuid.UUID, payload: CopertinaIn, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:media")),
) -> Dict[str, Any]:
    """Sostituisce la copertina di un articolo (qualunque, anche pubblicato). Tocca solo immagine e testo alternativo."""
    p = await _articolo_qualunque(session, post_id)
    prima = str(p.immagine_id) if p.immagine_id else None
    nuova = await _immagine_scelta(session, payload.immagine_id, payload.immagine_base64)
    try:
        await BlogRepository(session).salva(p, {"immagine_id": nuova, "immagine_alt": _alt_pulito(payload.alt)}, autore_id=None)
    except ErroreBlog as exc:
        await session.rollback()
        raise _errore(str(exc)) from exc
    await AuditRepository(session).record(
        action="blog.rest.cover", actor_id=None, target_type="blog_post", target_id=str(p.id),
        before={"immagine_id": prima}, after={"chiave": chiave.prefisso, "immagine_id": str(p.immagine_id)},
    )
    risposta = await _media_post_json(session, p, con_testo=False)
    await session.commit()
    return risposta


class SostituzioneInline(BaseModel):
    #: Quale immagine del testo: per posizione (0 = la prima) o per indirizzo attuale.
    indice: Optional[int] = Field(default=None, ge=0)
    url_attuale: Optional[str] = None
    immagine_id: Optional[uuid.UUID] = None
    immagine_base64: Optional[str] = None
    alt: Optional[str] = Field(default=None, max_length=200)


class AggiuntaInline(BaseModel):
    #: Dopo quale paragrafo (0 = il primo; i paragrafi sono separati da una riga vuota).
    dopo_paragrafo: int = Field(ge=0)
    immagine_id: Optional[uuid.UUID] = None
    immagine_base64: Optional[str] = None
    alt: str = Field(min_length=3, max_length=200)


class ImmaginiInlineIn(BaseModel):
    sostituisci: List[SostituzioneInline] = Field(default_factory=list, max_length=20)
    aggiungi: List[AggiuntaInline] = Field(default_factory=list, max_length=10)
    rimuovi: List[int] = Field(default_factory=list, max_length=20, description="Indici delle immagini da togliere.")


@router.put("/posts/{post_id}/inline")
async def cambia_immagini_nel_testo(
    post_id: uuid.UUID, payload: ImmaginiInlineIn, session: DbSession, chiave: ChiaveVerificata = Depends(richiede("blog:media")),
) -> Dict[str, Any]:
    """Sostituisce, aggiunge o toglie immagini nel testo di un articolo (qualunque). Cambiano solo le righe delle
    immagini; il resto del testo resta com'è, e la versione precedente si conserva."""
    p = await _articolo_qualunque(session, post_id)
    testo = p.testo
    trovate = list(_IMMAGINE_MD.finditer(testo))

    # Le sostituzioni e le rimozioni si decidono sugli indici del testo di partenza, poi si applicano dal fondo.
    modifiche: Dict[int, Optional[str]] = {}
    for s in payload.sostituisci:
        if s.indice is not None:
            indice = s.indice
        elif s.url_attuale:
            indice = next((i for i, m in enumerate(trovate) if m.group(2) == s.url_attuale), -1)
        else:
            raise _errore("Ogni sostituzione indica `indice` o `url_attuale`.")
        if not 0 <= indice < len(trovate):
            raise _errore(f"Nel testo non c'è l'immagine {s.indice if s.indice is not None else s.url_attuale}.")
        nuova = await _immagine_scelta(session, s.immagine_id, s.immagine_base64)
        alt = _alt_pulito(s.alt) if s.alt else trovate[indice].group(1)
        modifiche[indice] = f"![{alt}]({url_immagine(nuova)})"
    for indice in payload.rimuovi:
        if not 0 <= indice < len(trovate):
            raise _errore(f"Nel testo non c'è l'immagine {indice}.")
        modifiche[indice] = None
    for indice in sorted(modifiche, reverse=True):
        m = trovate[indice]
        nuovo = modifiche[indice]
        if nuovo is None:
            # Via l'immagine e, se stava su una riga da sola, anche la riga vuota che la separava dal seguito.
            prima, dopo = testo[: m.start()].rstrip(" \t"), testo[m.end():]
            if (prima.endswith("\n\n") or not prima) and dopo.startswith("\n\n"):
                dopo = dopo[2:]
            testo = prima + dopo
        else:
            testo = testo[: m.start()] + nuovo + testo[m.end():]

    if payload.aggiungi:
        paragrafi = testo.split("\n\n")
        inserimenti: Dict[int, List[str]] = {}
        for a in payload.aggiungi:
            if a.dopo_paragrafo >= len(paragrafi):
                raise _errore(f"Il testo ha {len(paragrafi)} paragrafi: `dopo_paragrafo` va da 0 a {len(paragrafi) - 1}.")
            nuova = await _immagine_scelta(session, a.immagine_id, a.immagine_base64)
            inserimenti.setdefault(a.dopo_paragrafo, []).append(f"![{_alt_pulito(a.alt)}]({url_immagine(nuova)})")
        uscita: List[str] = []
        for i, par in enumerate(paragrafi):
            uscita.append(par)
            uscita.extend(inserimenti.get(i, []))
        testo = "\n\n".join(uscita)

    if testo != p.testo:
        try:
            await BlogRepository(session).salva(p, {"testo": testo}, autore_id=None)
        except ErroreBlog as exc:
            await session.rollback()
            raise _errore(str(exc)) from exc
    await AuditRepository(session).record(
        action="blog.rest.inline", actor_id=None, target_type="blog_post", target_id=str(p.id),
        after={"chiave": chiave.prefisso, "sostituite": len(payload.sostituisci), "aggiunte": len(payload.aggiungi),
               "rimosse": len(payload.rimuovi)},
    )
    risposta = await _media_post_json(session, p, con_testo=True)
    await session.commit()
    return risposta
