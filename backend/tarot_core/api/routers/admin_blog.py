"""La console del blog: sezioni, articoli, immagini, etichette, versioni.

Come il resto della console, tutto il router pretende il ruolo `admin`, dichiarato una volta
sola. Ogni scrittura finisce nel registro (`blog.*`) con chi l'ha fatta.

Gli articoli si salvano con `BlogRepository.salva`, lo stesso punto che userà la pubblicazione
via REST con chiave applicativa: le regole (slug, versioni, collegamenti, tempo di lettura) sono
una sola.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.blog_models import BlogPost, BlogSection, BlogTag, MediaImage
from ...domain.blog_repositories import BlogRepository, ErroreBlog
from ...domain.models import User
from ...domain.repositories import AuditRepository
from ...tarot import blog as regole
from .blog import url_immagine

router = APIRouter(prefix="/admin/blog", tags=["console-blog"], dependencies=[Depends(require_role("admin"))])

TipoSezione = Literal["articoli", "carte", "stese", "contenitore"]
StatoArticolo = Literal["bozza", "pubblicato", "archiviato"]


def _errore(exc: ErroreBlog) -> HTTPException:
    return HTTPException(status_code=422, detail=str(exc))


# ---- sezioni ------------------------------------------------------------------------------------


class SezioneIn(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    slug: Optional[str] = Field(default=None, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)
    tipo: TipoSezione = "articoli"
    #: Per `carte`: `{"arcano": "maggiore"}` o `{"seme": "bastoni"}`; per `stese`: `{"categoria": "coppia"}`.
    filtro: Optional[Dict[str, str]] = None
    parent_id: Optional[int] = None
    ordine: int = 0
    visibile: bool = True
    immagine_id: Optional[uuid.UUID] = None
    seo_titolo: Optional[str] = Field(default=None, max_length=200)
    seo_descrizione: Optional[str] = Field(default=None, max_length=320)


class SezioneMod(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=120)
    slug: Optional[str] = Field(default=None, max_length=80)
    descrizione: Optional[str] = Field(default=None, max_length=2000)
    tipo: Optional[TipoSezione] = None
    filtro: Optional[Dict[str, str]] = None
    parent_id: Optional[int] = None
    ordine: Optional[int] = None
    visibile: Optional[bool] = None
    immagine_id: Optional[uuid.UUID] = None
    seo_titolo: Optional[str] = Field(default=None, max_length=200)
    seo_descrizione: Optional[str] = Field(default=None, max_length=320)


class Riordino(BaseModel):
    id: int
    parent_id: Optional[int] = None
    ordine: int


def _sezione_json(s: BlogSection, n_articoli: int = 0) -> Dict[str, Any]:
    return {
        "id": s.id, "parent_id": s.parent_id, "slug": s.slug, "nome": s.nome, "descrizione": s.descrizione,
        "tipo": s.tipo, "filtro": s.filtro, "ordine": s.ordine, "visibile": s.visibile,
        "immagine_id": str(s.immagine_id) if s.immagine_id else None, "immagine": url_immagine(s.immagine_id),
        "seo_titolo": s.seo_titolo, "seo_descrizione": s.seo_descrizione, "n_articoli": n_articoli,
    }


async def _conteggi_admin(session) -> Dict[int, int]:
    q = select(BlogPost.sezione_id, func.count()).where(BlogPost.sezione_id.is_not(None)).group_by(BlogPost.sezione_id)
    return {sid: n for sid, n in (await session.execute(q)).all()}


@router.get("/sections")
async def sezioni(session: DbSession) -> List[Dict[str, Any]]:
    """Tutte le sezioni, anche quelle nascoste, in elenco piatto (l'albero lo ricostruisce la console)."""
    conteggi = await _conteggi_admin(session)
    return [_sezione_json(s, conteggi.get(s.id, 0)) for s in await BlogRepository(session).sezioni(solo_visibili=False)]


@router.post("/sections", status_code=201)
async def crea_sezione(payload: SezioneIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    repo = BlogRepository(session)
    dati = payload.model_dump()
    dati["slug"] = await repo.slug_sezione_libero(dati["slug"] or dati["nome"])
    if payload.parent_id is not None and await repo.sezione(payload.parent_id) is None:
        raise HTTPException(status_code=422, detail="la sezione padre non esiste")
    sezione = BlogSection(**dati)
    session.add(sezione)
    await session.flush()
    await AuditRepository(session).record(
        action="blog.section.create", actor_id=user.id, target_type="blog_section", target_id=str(sezione.id),
        after={"slug": sezione.slug, "nome": sezione.nome},
    )
    await session.commit()
    return _sezione_json(sezione)


@router.patch("/sections/{sezione_id}")
async def modifica_sezione(sezione_id: int, payload: SezioneMod, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    repo = BlogRepository(session)
    sezione = await repo.sezione(sezione_id)
    if sezione is None:
        raise HTTPException(status_code=404, detail="Sezione non trovata")
    dati = payload.model_dump(exclude_unset=True)
    if "parent_id" in dati:
        try:
            await repo.valida_albero(sezione.id, dati["parent_id"])
        except ErroreBlog as exc:
            raise _errore(exc) from exc
    if dati.get("slug"):
        dati["slug"] = await repo.slug_sezione_libero(dati["slug"], sezione.id)
    elif "slug" in dati:
        del dati["slug"]
    prima = {"slug": sezione.slug, "nome": sezione.nome, "parent_id": sezione.parent_id}
    for campo, valore in dati.items():
        setattr(sezione, campo, valore)
    await AuditRepository(session).record(
        action="blog.section.update", actor_id=user.id, target_type="blog_section", target_id=str(sezione.id),
        before=prima, after={k: dati.get(k) for k in ("slug", "nome", "parent_id") if k in dati},
    )
    await session.commit()
    return _sezione_json(sezione)


@router.post("/sections/riordina")
async def riordina_sezioni(voci: List[Riordino], user: CurrentUser, session: DbSession) -> Dict[str, int]:
    """Sposta e riordina più sezioni in una volta: `[{id, parent_id, ordine}]`."""
    repo = BlogRepository(session)
    for voce in voci:
        sezione = await repo.sezione(voce.id)
        if sezione is None:
            raise HTTPException(status_code=404, detail=f"Sezione {voce.id} non trovata")
        try:
            await repo.valida_albero(sezione.id, voce.parent_id)
        except ErroreBlog as exc:
            raise _errore(exc) from exc
        sezione.parent_id = voce.parent_id
        sezione.ordine = voce.ordine
        await session.flush()
    await AuditRepository(session).record(
        action="blog.section.reorder", actor_id=user.id, target_type="blog_section", after={"n": len(voci)},
    )
    await session.commit()
    return {"aggiornate": len(voci)}


@router.delete("/sections/{sezione_id}", status_code=204)
async def elimina_sezione(
    sezione_id: int, user: CurrentUser, session: DbSession, forza: bool = Query(default=False),
) -> Response:
    """Elimina una sezione. Con articoli o sotto-sezioni serve `forza=true`: gli articoli restano,
    senza sezione, e le sotto-sezioni salgono alla radice."""
    repo = BlogRepository(session)
    sezione = await repo.sezione(sezione_id)
    if sezione is None:
        raise HTTPException(status_code=404, detail="Sezione non trovata")
    n_articoli = (await _conteggi_admin(session)).get(sezione.id, 0)
    n_figli = int((await session.execute(
        select(func.count()).select_from(BlogSection).where(BlogSection.parent_id == sezione.id)
    )).scalar_one())
    if (n_articoli or n_figli) and not forza:
        raise HTTPException(
            status_code=409,
            detail={"motivo": "sezione_non_vuota", "articoli": n_articoli, "sotto_sezioni": n_figli},
        )
    await AuditRepository(session).record(
        action="blog.section.delete", actor_id=user.id, target_type="blog_section", target_id=str(sezione.id),
        before={"slug": sezione.slug, "nome": sezione.nome},
    )
    await session.delete(sezione)
    await session.commit()
    return Response(status_code=204)


# ---- articoli -------------------------------------------------------------------------------------


class ArticoloIn(BaseModel):
    titolo: str = Field(min_length=1, max_length=200)
    sottotitolo: Optional[str] = Field(default=None, max_length=300)
    testo: str = Field(default="", max_length=200_000)
    slug: Optional[str] = Field(default=None, max_length=160)
    lang: str = Field(default="it", pattern="^[a-z]{2}(-[A-Za-z]{2})?$")
    sezione_id: Optional[int] = None
    immagine_id: Optional[uuid.UUID] = None
    immagine_alt: Optional[str] = Field(default=None, max_length=200)
    tags: List[str] = Field(default_factory=list, max_length=10)
    in_evidenza: bool = False
    commenti_aperti: bool = True
    seo_titolo: Optional[str] = Field(default=None, max_length=200)
    seo_descrizione: Optional[str] = Field(default=None, max_length=320)
    stato: StatoArticolo = "bozza"
    pubblicato_il: Optional[datetime] = None


class ArticoloMod(BaseModel):
    titolo: Optional[str] = Field(default=None, min_length=1, max_length=200)
    sottotitolo: Optional[str] = Field(default=None, max_length=300)
    testo: Optional[str] = Field(default=None, max_length=200_000)
    slug: Optional[str] = Field(default=None, max_length=160)
    lang: Optional[str] = Field(default=None, pattern="^[a-z]{2}(-[A-Za-z]{2})?$")
    sezione_id: Optional[int] = None
    immagine_id: Optional[uuid.UUID] = None
    immagine_alt: Optional[str] = Field(default=None, max_length=200)
    tags: Optional[List[str]] = Field(default=None, max_length=10)
    in_evidenza: Optional[bool] = None
    commenti_aperti: Optional[bool] = None
    seo_titolo: Optional[str] = Field(default=None, max_length=200)
    seo_descrizione: Optional[str] = Field(default=None, max_length=320)
    stato: Optional[StatoArticolo] = None
    pubblicato_il: Optional[datetime] = None


async def articolo_admin_json(session, p: BlogPost, *, con_testo: bool = True) -> Dict[str, Any]:
    # Date e valori calcolati dal database (`updated_at`, l'etichetta appena scritta) dopo un
    # salvataggio sono scaduti: si rileggono qui invece di lasciare che il primo accesso lo faccia
    # fuori dal contesto asincrono.
    await session.refresh(p)
    autore = await session.get(User, p.autore_id) if p.autore_id else None
    dati = {
        "id": str(p.id), "slug": p.slug, "titolo": p.titolo, "sottotitolo": p.sottotitolo, "lang": p.lang,
        "stato": p.stato, "pubblicato_il": p.pubblicato_il.isoformat() if p.pubblicato_il else None,
        "programmato": bool(p.stato == "pubblicato" and p.pubblicato_il and p.pubblicato_il > _adesso()),
        "sezione_id": p.sezione_id, "immagine_id": str(p.immagine_id) if p.immagine_id else None,
        "immagine": url_immagine(p.immagine_id), "immagine_alt": p.immagine_alt,
        "tags": [t.nome for t in p.tags], "in_evidenza": p.in_evidenza, "commenti_aperti": p.commenti_aperti,
        "seo_titolo": p.seo_titolo, "seo_descrizione": p.seo_descrizione, "tempo_lettura": p.tempo_lettura,
        "autore": {"id": autore.id, "nome": autore.display_name or autore.email} if autore else None,
        "creato": p.created_at.isoformat() if p.created_at else None,
        "aggiornato": p.updated_at.isoformat() if p.updated_at else None,
    }
    if con_testo:
        dati["testo"] = p.testo
    return dati


def _adesso() -> datetime:
    from ...domain.base import utcnow

    return utcnow()


@router.get("/posts")
async def articoli(
    session: DbSession,
    stato: Optional[StatoArticolo] = None,
    sezione_id: Optional[int] = None,
    q: str = Query(default="", max_length=100),
    pagina: int = Query(default=1, ge=1),
    per_pagina: int = Query(default=25, ge=1, le=100),
) -> Dict[str, Any]:
    posts, totale = await BlogRepository(session).elenco(
        pubblico=False, stato=stato, sezioni=[sezione_id] if sezione_id else None, testo=q,
        pagina=pagina, per_pagina=per_pagina,
    )
    return {
        "totale": totale, "pagina": pagina, "per_pagina": per_pagina,
        "articoli": [await articolo_admin_json(session, p, con_testo=False) for p in posts],
    }


@router.get("/posts/{post_id}")
async def articolo(post_id: uuid.UUID, session: DbSession) -> Dict[str, Any]:
    p = await BlogRepository(session).per_id(post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    return await articolo_admin_json(session, p)


@router.post("/posts", status_code=201)
async def crea_articolo(payload: ArticoloIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    repo = BlogRepository(session)
    dati = payload.model_dump(exclude={"tags"})
    try:
        p = await repo.salva(None, dati, autore_id=user.id, tag=payload.tags)
    except ErroreBlog as exc:
        raise _errore(exc) from exc
    await AuditRepository(session).record(
        action="blog.post.create", actor_id=user.id, target_type="blog_post", target_id=str(p.id),
        after={"slug": p.slug, "titolo": p.titolo, "stato": p.stato},
    )
    await session.commit()
    return await articolo_admin_json(session, p)


@router.patch("/posts/{post_id}")
async def modifica_articolo(post_id: uuid.UUID, payload: ArticoloMod, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    repo = BlogRepository(session)
    p = await repo.per_id(post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    dati = payload.model_dump(exclude_unset=True)
    tag = dati.pop("tags", None)
    prima = {"stato": p.stato, "slug": p.slug}
    try:
        await repo.salva(p, dati, autore_id=user.id, tag=tag)
    except ErroreBlog as exc:
        raise _errore(exc) from exc
    await AuditRepository(session).record(
        action="blog.post.update", actor_id=user.id, target_type="blog_post", target_id=str(p.id),
        before=prima, after={"stato": p.stato, "slug": p.slug},
    )
    await session.commit()
    return await articolo_admin_json(session, p)


@router.post("/posts/{post_id}/{azione}")
async def cambia_stato(post_id: uuid.UUID, azione: Literal["pubblica", "archivia", "bozza"], user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Pubblica (adesso, o alla data già scritta), archivia o riporta a bozza."""
    repo = BlogRepository(session)
    p = await repo.per_id(post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    nuovo = {"pubblica": "pubblicato", "archivia": "archiviato", "bozza": "bozza"}[azione]
    await repo.salva(p, {"stato": nuovo}, autore_id=user.id)
    await AuditRepository(session).record(
        action=f"blog.post.{azione}", actor_id=user.id, target_type="blog_post", target_id=str(p.id), after={"stato": nuovo},
    )
    await session.commit()
    return await articolo_admin_json(session, p)


@router.delete("/posts/{post_id}", status_code=204)
async def elimina_articolo(post_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Response:
    repo = BlogRepository(session)
    p = await repo.per_id(post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    await AuditRepository(session).record(
        action="blog.post.delete", actor_id=user.id, target_type="blog_post", target_id=str(p.id),
        before={"slug": p.slug, "titolo": p.titolo},
    )
    await repo.elimina(p)
    await session.commit()
    return Response(status_code=204)


@router.get("/posts/{post_id}/revisions")
async def revisioni(post_id: uuid.UUID, session: DbSession) -> List[Dict[str, Any]]:
    repo = BlogRepository(session)
    p = await repo.per_id(post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    return [
        {"id": r.id, "titolo": r.titolo, "sottotitolo": r.sottotitolo, "testo": r.testo, "quando": r.created_at.isoformat()}
        for r in await repo.revisioni(p)
    ]


@router.post("/posts/{post_id}/revisions/{revisione_id}/restore")
async def ripristina(post_id: uuid.UUID, revisione_id: int, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    repo = BlogRepository(session)
    p = await repo.per_id(post_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    r = next((x for x in await repo.revisioni(p) if x.id == revisione_id), None)
    if r is None:
        raise HTTPException(status_code=404, detail="Versione non trovata")
    await repo.salva(p, {"titolo": r.titolo, "sottotitolo": r.sottotitolo, "testo": r.testo}, autore_id=user.id)
    await AuditRepository(session).record(
        action="blog.post.restore", actor_id=user.id, target_type="blog_post", target_id=str(p.id), after={"revisione": r.id},
    )
    await session.commit()
    return await articolo_admin_json(session, p)


# ---- immagini ---------------------------------------------------------------------------------------


@router.post("/media", status_code=201)
async def carica_immagine(request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Carica un'immagine (PNG, JPEG o WebP) come corpo della richiesta: si orienta, si porta a
    1600 px di larghezza al massimo e si riscrive in WebP."""
    if not request.headers.get("content-type", "").startswith("image/"):
        raise HTTPException(status_code=415, detail="Serve un'immagine")
    if int(request.headers.get("content-length") or 0) > regole.MAX_CARICO_IMMAGINE:
        raise HTTPException(status_code=413, detail="Immagine troppo grande")
    try:
        webp, larghezza, altezza = await asyncio.to_thread(regole.prepara_immagine_articolo, await request.body())
    except regole.ImmagineNonValida as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    img = MediaImage(uso="blog", webp=webp, larghezza=larghezza, altezza=altezza, owner_id=user.id)
    session.add(img)
    await session.flush()
    await AuditRepository(session).record(
        action="blog.media.upload", actor_id=user.id, target_type="media_image", target_id=str(img.id),
        after={"byte": len(webp), "larghezza": larghezza, "altezza": altezza},
    )
    await session.commit()
    return {"id": str(img.id), "url": url_immagine(img.id), "larghezza": larghezza, "altezza": altezza, "byte": len(webp)}


@router.get("/media")
async def immagini(session: DbSession, limite: int = Query(default=60, ge=1, le=200)) -> List[Dict[str, Any]]:
    q = select(MediaImage).where(MediaImage.uso == "blog").order_by(MediaImage.created_at.desc()).limit(limite)
    return [
        {"id": str(i.id), "url": url_immagine(i.id), "larghezza": i.larghezza, "altezza": i.altezza,
         "creata": i.created_at.isoformat()}
        for i in (await session.execute(q)).scalars()
    ]


@router.delete("/media/{immagine_id}", status_code=204)
async def elimina_immagine(immagine_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Response:
    img = await session.get(MediaImage, immagine_id)
    if img is None or img.uso != "blog":
        raise HTTPException(status_code=404, detail="Immagine non trovata")
    usata = (await session.execute(select(func.count()).select_from(BlogPost).where(BlogPost.immagine_id == img.id))).scalar_one()
    usata += (await session.execute(select(func.count()).select_from(BlogSection).where(BlogSection.immagine_id == img.id))).scalar_one()
    if usata:
        raise HTTPException(status_code=409, detail={"motivo": "immagine_in_uso", "usi": int(usata)})
    await AuditRepository(session).record(
        action="blog.media.delete", actor_id=user.id, target_type="media_image", target_id=str(img.id),
    )
    await session.delete(img)
    await session.commit()
    return Response(status_code=204)


# ---- etichette --------------------------------------------------------------------------------------


class EtichettaMod(BaseModel):
    nome: str = Field(min_length=1, max_length=80)


@router.get("/tags")
async def etichette(session: DbSession) -> List[Dict[str, Any]]:
    from ...domain.blog_models import BlogPostTag

    q = (
        select(BlogTag, func.count(BlogPostTag.post_id))
        .outerjoin(BlogPostTag, BlogPostTag.tag_id == BlogTag.id)
        .group_by(BlogTag.id).order_by(BlogTag.nome)
    )
    return [{"id": t.id, "slug": t.slug, "nome": t.nome, "n": int(n)} for t, n in (await session.execute(q)).all()]


@router.patch("/tags/{tag_id}")
async def rinomina_etichetta(tag_id: int, payload: EtichettaMod, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    tag = await session.get(BlogTag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Etichetta non trovata")
    slug, nome = regole.normalizza_etichetta(payload.nome)
    if not slug:
        raise HTTPException(status_code=422, detail="Nome non valido")
    altro = (await session.execute(select(BlogTag).where(BlogTag.slug == slug, BlogTag.id != tag.id))).scalar_one_or_none()
    if altro is not None:
        raise HTTPException(status_code=409, detail="Esiste già un'etichetta con questo nome")
    tag.slug, tag.nome = slug, nome
    await AuditRepository(session).record(action="blog.tag.rename", actor_id=user.id, target_type="blog_tag", target_id=str(tag.id), after={"nome": nome})
    await session.commit()
    return {"id": tag.id, "slug": tag.slug, "nome": tag.nome}


@router.delete("/tags/{tag_id}", status_code=204)
async def elimina_etichetta(tag_id: int, user: CurrentUser, session: DbSession) -> Response:
    tag = await session.get(BlogTag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Etichetta non trovata")
    await session.execute(delete(BlogTag).where(BlogTag.id == tag.id))
    await AuditRepository(session).record(action="blog.tag.delete", actor_id=user.id, target_type="blog_tag", target_id=str(tag_id))
    await session.commit()
    return Response(status_code=204)
