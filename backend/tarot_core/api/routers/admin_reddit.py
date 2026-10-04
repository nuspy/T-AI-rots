"""Reddit dalla console (v8.6): l'account, la prova senza pubblicare, i post fatti e da fare, «Riprova».

I segreti (secret dell'app e password) entrano e non escono: le risposte dicono solo se ci sono (e gli ultimi
caratteri del secret, per riconoscerlo). Ogni pubblicazione vera parte in background dopo la risposta.
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.blog_models import BlogPost
from ...domain.integrazioni_models import PostReddit
from ...domain.repositories import AuditRepository
from ...domain.session import get_session_factory
from ...tarot import reddit

router = APIRouter(prefix="/admin/reddit", tags=["reddit"], dependencies=[Depends(require_role("admin"))])


async def _stato(session, limite: int = 50) -> Dict[str, Any]:
    return {"config": reddit.config_json(await reddit.config(session)), "post": await reddit.elenco(session, limite)}


@router.get("")
async def stato(session: DbSession, limite: int = Query(default=50, ge=1, le=200)) -> Dict[str, Any]:
    return await _stato(session, limite)


class ConfigRedditIn(BaseModel):
    client_id: Optional[str] = Field(default=None, max_length=100)
    #: `None`: resta quello di prima; stringa vuota: si toglie.
    client_secret: Optional[str] = Field(default=None, max_length=200)
    utente: Optional[str] = Field(default=None, max_length=40)
    password: Optional[str] = Field(default=None, max_length=200)
    subreddit: Optional[str] = Field(default=None, max_length=120)
    flair_id: Optional[str] = Field(default=None, max_length=64)
    attivo: Optional[bool] = None
    lingue: Optional[List[str]] = Field(default=None, max_length=20)
    intervallo_minuti: Optional[int] = Field(default=None, ge=0, le=7 * 24 * 60)


@router.put("")
async def configura(payload: ConfigRedditIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    dati = payload.model_dump(exclude_unset=True)
    try:
        await reddit.aggiorna(session, dati, autore_id=user.id)
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await AuditRepository(session).record(
        action="reddit.config", actor_id=user.id, target_type="config_reddit", target_id="1",
        after={**{k: v for k, v in dati.items() if k not in ("client_secret", "password")},
               "client_secret": "cambiato" if dati.get("client_secret") is not None else None,
               "password": "cambiata" if dati.get("password") is not None else None},
    )
    await session.commit()
    return await _stato(session)


@router.post("/prova")
async def prova(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Ottiene un token, legge l'account e la destinazione: non pubblica nulla."""
    await reddit.prova(session)
    await session.commit()
    return await _stato(session)


@router.post("/invia", status_code=202)
async def giro_ora(compiti: BackgroundTasks, session: DbSession, fabbrica=Depends(get_session_factory)) -> Dict[str, Any]:
    """Un giro della coda adesso (lo stesso del CronJob), in background."""
    riga = await reddit.config(session)
    if not reddit.pronta(riga):
        raise HTTPException(status_code=409, detail="La pubblicazione su Reddit è spenta o incompleta.")
    await session.commit()  # nessuna transazione aperta: il giro in background ha una sessione sua
    compiti.add_task(reddit.lavora, fabbrica)
    return {"avviato": True}


@router.post("/post/{post_id}/riprova", status_code=202)
async def riprova(
    post_id: uuid.UUID, user: CurrentUser, session: DbSession, compiti: BackgroundTasks, fabbrica=Depends(get_session_factory),
) -> Dict[str, Any]:
    post = await session.get(PostReddit, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post non trovato")
    if post.stato not in ("errore", "saltato", "in_coda"):
        raise HTTPException(status_code=409, detail="Si riprovano solo i post in errore.")
    post.stato, post.errore, post.riprova_dopo = "in_coda", None, None
    await AuditRepository(session).record(
        action="reddit.riprova", actor_id=user.id, target_type="post_reddit", target_id=str(post.id),
    )
    await session.commit()
    articolo = await session.get(BlogPost, post.articolo_id)
    risposta = reddit.post_json(post, articolo)
    if reddit.pronta(await reddit.config(session)):
        compiti.add_task(reddit.lavora, fabbrica)
    await session.commit()  # nessuna transazione aperta: il giro in background ha una sessione sua
    return risposta


@router.post("/articoli/{articolo_id}", status_code=202)
async def accoda_articolo(
    articolo_id: uuid.UUID, user: CurrentUser, session: DbSession, compiti: BackgroundTasks,
    fabbrica=Depends(get_session_factory),
) -> Dict[str, Any]:
    """Porta su Reddit un articolo preciso, anche uscito prima dell'accensione. Mai due volte lo stesso."""
    articolo = await session.get(BlogPost, articolo_id)
    if articolo is None:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    if articolo.stato != "pubblicato":
        raise HTTPException(status_code=409, detail="Si portano su Reddit solo gli articoli pubblicati.")
    post = await reddit.accoda(session, articolo_id)
    await AuditRepository(session).record(
        action="reddit.accoda", actor_id=user.id, target_type="blog_post", target_id=str(articolo_id),
    )
    await session.commit()
    risposta = reddit.post_json(post, articolo)
    if reddit.pronta(await reddit.config(session)):
        compiti.add_task(reddit.lavora, fabbrica)
    await session.commit()  # nessuna transazione aperta: il giro in background ha una sessione sua
    return risposta


@router.get("/articoli")
async def articoli_senza_post(session: DbSession, limite: int = Query(default=30, ge=1, le=100)) -> List[Dict[str, Any]]:
    """Gli ultimi articoli pubblicati che non sono ancora passati da Reddit: per portarne uno a mano."""
    righe = (await session.execute(
        select(BlogPost.id, BlogPost.titolo, BlogPost.slug, BlogPost.lang, BlogPost.pubblicato_il)
        .where(BlogPost.stato == "pubblicato", ~select(PostReddit.id).where(PostReddit.articolo_id == BlogPost.id).exists())
        .order_by(BlogPost.pubblicato_il.desc().nulls_last()).limit(limite)
    )).all()
    return [{"id": str(r.id), "titolo": r.titolo, "slug": r.slug, "lang": r.lang,
             "pubblicato_il": r.pubblicato_il.isoformat() if r.pubblicato_il else None} for r in righe]
