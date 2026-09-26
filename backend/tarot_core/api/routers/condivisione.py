"""La condivisione delle letture: clic, immagini, visite e iscrizioni dal link.

| chi | endpoint | cosa fa |
|---|---|---|
| proprietario | `POST /me/readings/{id}/share` (in `readings.py`) | pubblica o ritira il link e il testo personalizzato |
| proprietario | `PUT /me/readings/{id}/share-image` | carica l'immagine composta dal browser; si salva in WebP 400×300 |
| proprietario | `POST /me/readings/{id}/share-click` | registra l'uso di un pulsante di condivisione |
| chiunque | `GET /shared/{token}/image.webp` | l'immagine, per le anteprime dei social |
| chiunque | `POST /shared/{token}/visit` | un visitatore vero ha aperto il link |
| chi si iscrive | `POST /me/share-signup` | attribuisce un'iscrizione al link da cui viene |

**Il premio.** Ogni `SOGLIA_PREMIO` letture con condivisione accertata (vedi
`tarot/condivisione.py` per cosa vuol dire «accertata») regalano una lettura, senza
tetto. Ogni persona che si iscrive partendo dal link di un'altra fa guadagnare a
questa `CREDITI_ISCRIZIONE` letture, anche se l'account resta gratuito.

**Contro gli abusi** (il premio non ha un tetto, quindi i controlli stanno altrove):
il visitatore deve essere diverso dal proprietario per browser e per rete, un
crawler non conta, ogni lettura conta una volta sola, un account può far guadagnare
una volta sola, l'iscrizione deve arrivare da un account **nuovo** con email
**verificata**, e ogni accredito passa dal registro dei crediti e dall'audit, dove la
console li vede.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from ...auth.dependencies import CurrentPrincipal, CurrentUser, DbSession
from ...billing.credits import RegistroCrediti
from ...domain.base import utcnow
from ...domain.models import Reading, User
from ...domain.repositories import AuditRepository, ReadingRepository
from ...domain.share_models import ShareEvent, ShareImage, ShareSignup, ShareVisit
from ...settings import get_settings
from ...tarot import condivisione as regole

logger = logging.getLogger(__name__)

router = APIRouter(tags=["condivisione"])


# ---- impronte ---------------------------------------------------------------------


def _indirizzo(request: Request) -> str:
    """L'indirizzo di chi chiama, anche dietro i proxy.

    Dietro NPM e il gateway il socket è quello del proxy. `X-Real-IP` lo scrive NPM
    (sovrascrivendo ciò che manda il client) ed è la fonte più fidata; in mancanza si
    prende l'**ultimo** indirizzo di `X-Forwarded-For`, quello aggiunto dal proxy più
    vicino, non il primo, che può essere scritto da chi chiama. Fuori dai proxy (in
    sviluppo) contano solo le intestazioni che un client può falsificare: il confronto
    «stessa rete» si aggira, ma in sviluppo non protegge niente.
    """
    reale = request.headers.get("x-real-ip", "").strip()
    if reale:
        return reale
    inoltrato = request.headers.get("x-forwarded-for", "")
    if inoltrato:
        return inoltrato.split(",")[-1].strip()
    return request.client.host if request.client else "sconosciuto"


def _impronte(request: Request, visitor: str) -> tuple:
    sale = get_settings().condivisione_sale
    return regole.anonimo(visitor, sale), regole.anonimo(_indirizzo(request), sale)


def _visitatore_o_422(valore: str) -> str:
    if not regole.visitatore_valido(valore):
        raise HTTPException(status_code=422, detail="identificativo del visitatore non valido")
    return valore


# ---- contatore e premi -----------------------------------------------------------------


async def contatore(session, user: User) -> Dict[str, int]:
    """Il contatore della scheda utente: condivisioni accertate, premi, iscrizioni dal link."""
    verificate = int((await session.execute(
        select(func.count()).select_from(Reading).where(
            Reading.owner_id == user.id, Reading.share_verified_at.is_not(None),
        )
    )).scalar_one())
    iscrizioni = int((await session.execute(
        select(func.count()).select_from(ShareSignup).where(ShareSignup.sharer_id == user.id)
    )).scalar_one())
    return regole.progresso(verificate, user.share_rewards, iscrizioni)


async def _assegna_premi(session, user_id: int) -> int:
    """Accredita le letture in omaggio dovute alle condivisioni accertate.

    Le dovute sono `accertate // SOGLIA`; quelle già accreditate stanno in
    `users.share_rewards`. Il lock sulla riga dell'utente fa sì che due visite
    contemporanee non accreditino due volte lo stesso premio.
    """
    utente = (await session.execute(
        select(User).where(User.id == user_id).with_for_update()
    )).scalar_one()
    verificate = int((await session.execute(
        select(func.count()).select_from(Reading).where(
            Reading.owner_id == user_id, Reading.share_verified_at.is_not(None),
        )
    )).scalar_one())
    dovuti = verificate // regole.SOGLIA_PREMIO
    nuovi = dovuti - utente.share_rewards
    if nuovi <= 0:
        return 0
    await RegistroCrediti(session).accredita(
        user_id, nuovi, reason="omaggio",
        note=f"{regole.SOGLIA_PREMIO} condivisioni accertate ({verificate} in tutto)",
    )
    utente.share_rewards = dovuti
    await AuditRepository(session).record(
        action="share.reward", actor_id=user_id, target_type="user", target_id=str(user_id),
        after={"crediti": nuovi, "accertate": verificate},
    )
    logger.info("Premio di condivisione: %d lettura/e all'utente %s", nuovi, user_id)
    return nuovi


async def _registra_visita(session, lettura: Reading, visitor: str, ip: str) -> Dict[str, bool]:
    """Conta un visitatore su una lettura condivisa, se è un visitatore vero.

    Restituisce `{"contata": ..., "accertata": ...}`: la visita è stata registrata,
    e con essa la lettura è diventata una «condivisione accertata».
    """
    eventi = (await session.execute(
        select(ShareEvent.visitor, ShareEvent.ip).where(ShareEvent.reading_id == lettura.id)
    )).all()
    if any(v == visitor or i == ip for v, i in eventi):
        return {"contata": False, "accertata": False}   # è il proprietario, o una persona della sua rete

    await session.execute(
        pg_insert(ShareVisit).values(reading_id=lettura.id, visitor=visitor, ip=ip).on_conflict_do_nothing()
    )
    accertata = False
    ora = utcnow()
    if (
        lettura.share_verified_at is None
        and lettura.share_clicked_at is not None
        and ora - lettura.share_clicked_at <= timedelta(days=regole.GIORNI_FINESTRA)
    ):
        lettura.share_verified_at = ora
        accertata = True
        await _assegna_premi(session, lettura.owner_id)
    return {"contata": True, "accertata": accertata}


# ---- il proprietario ------------------------------------------------------------------


class ClicCondivisione(BaseModel):
    canale: str = Field(pattern="^(" + "|".join(regole.CANALI) + ")$")
    #: L'identificativo casuale del browser di chi preme (lo genera il frontend).
    visitor: str = Field(min_length=16, max_length=64)


async def _completata_condivisa(session, user: User, reading_id: uuid.UUID) -> Reading:
    lettura = await ReadingRepository(session).get(user, reading_id)
    if lettura is None:
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    if lettura.status != "completata" or not lettura.share_token:
        raise HTTPException(status_code=409, detail="La lettura non è condivisa")
    return lettura


TIPI_IMMAGINE = {"image/png", "image/webp", "image/jpeg"}


@router.put("/me/readings/{reading_id}/share-image")
async def carica_immagine(
    reading_id: uuid.UUID, request: Request, user: CurrentUser, session: DbSession,
) -> Response:
    """Salva l'immagine composta dal browser e restituisce quella che si condivide.

    Il browser manda un PNG (l'unico formato che ogni canvas sa produrre, Safari
    compreso) di 800×600 o 400×300; il server lo ricontrolla e lo riscrive in WebP
    400×300 molto compresso (`prepara_immagine`). Si risponde col WebP: è ciò che il
    browser mostra in anteprima e allega ai fogli di condivisione, così ciò che si vede
    è ciò che i social riceveranno.
    """
    lettura = await _completata_condivisa(session, user, reading_id)
    if request.headers.get("content-type", "").split(";")[0].strip() not in TIPI_IMMAGINE:
        raise HTTPException(status_code=415, detail="Serve un'immagine PNG, WebP o JPEG")
    if int(request.headers.get("content-length") or 0) > regole.MAX_CARICO:
        raise HTTPException(status_code=413, detail="Immagine troppo grande")
    try:
        # La decodifica e la ricompressione sono lavoro di CPU: fuori dal ciclo degli eventi.
        webp = await asyncio.to_thread(regole.prepara_immagine, await request.body())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    await session.execute(
        pg_insert(ShareImage).values(reading_id=lettura.id, webp=webp)
        .on_conflict_do_update(index_elements=["reading_id"], set_={"webp": webp, "updated_at": func.now()})
    )
    await session.commit()
    return Response(content=webp, media_type="image/webp", headers={"Cache-Control": "no-store"})


@router.post("/me/readings/{reading_id}/share-click")
async def clic(
    reading_id: uuid.UUID, payload: ClicCondivisione, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Registra che il proprietario ha usato un pulsante di condivisione.

    Da qui, per `GIORNI_FINESTRA` giorni, la prima visita di un visitatore vero al
    link rende la lettura una condivisione accertata. Il clic da solo non conta.
    """
    lettura = await _completata_condivisa(session, user, reading_id)
    visitor, ip = _impronte(request, _visitatore_o_422(payload.visitor))
    session.add(ShareEvent(reading_id=lettura.id, canale=payload.canale, visitor=visitor, ip=ip))
    lettura.share_clicked_at = utcnow()
    await session.commit()
    return {"contatore": await contatore(session, user)}


# ---- il pubblico -------------------------------------------------------------------------


@router.get("/shared/{token}/image.webp")
async def immagine(token: str, session: DbSession) -> Response:
    """L'immagine di una lettura condivisa: quella che i social mostrano come anteprima."""
    lettura = await ReadingRepository(session).by_share_token(token)
    if lettura is None or lettura.status != "completata":
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    riga = (await session.execute(
        select(ShareImage.webp).where(ShareImage.reading_id == lettura.id)
    )).scalar_one_or_none()
    if riga is None:
        raise HTTPException(status_code=404, detail="Immagine non disponibile")
    return Response(
        content=riga, media_type="image/webp",
        headers={"Cache-Control": "public, max-age=300", "X-Content-Type-Options": "nosniff"},
    )


class Visita(BaseModel):
    visitor: str = Field(min_length=16, max_length=64)


@router.post("/shared/{token}/visit")
async def visita(token: str, payload: Visita, request: Request, session: DbSession) -> Dict[str, bool]:
    """Un browser ha aperto il link e ci è rimasto: lo manda la pagina, dopo qualche secondo.

    Un crawler non esegue la pagina e non arriva qui; se ci arriva lo stesso, lo
    scarta lo `User-Agent`. La risposta non dice mai perché una visita non conta:
    non deve servire a imparare come si aggira il controllo.
    """
    lettura = await ReadingRepository(session).by_share_token(token)
    if lettura is None or lettura.status != "completata":
        raise HTTPException(status_code=404, detail="Lettura non trovata")
    if regole.e_un_bot(request.headers.get("user-agent")) or not regole.visitatore_valido(payload.visitor):
        return {"contata": False, "accertata": False}
    visitor, ip = _impronte(request, payload.visitor)
    esito = await _registra_visita(session, lettura, visitor, ip)
    await session.commit()
    return {"contata": esito["contata"], "accertata": False}   # l'esito vero lo vede solo il proprietario


# ---- l'iscrizione dal link ----------------------------------------------------------------


class Iscrizione(BaseModel):
    token: str = Field(min_length=8, max_length=40)
    visitor: str = Field(min_length=16, max_length=64)


@router.post("/me/share-signup")
async def iscrizione(
    payload: Iscrizione, request: Request, user: CurrentUser, principal: CurrentPrincipal, session: DbSession,
) -> Dict[str, Any]:
    """Attribuisce l'iscrizione di questo account al link da cui è arrivato.

    Chiamata dal frontend, una volta, al primo accesso di un account nuovo che
    ha in memoria il link di una lettura condivisa. Il server decide se vale: non
    fa errori, risponde `attribuita: false` con il motivo, perché il frontend
    dimentichi il link in ogni caso.
    """
    def rifiuto(motivo: str) -> Dict[str, Any]:
        return {"attribuita": False, "motivo": motivo}

    lettura = await ReadingRepository(session).by_share_token(payload.token)
    if lettura is None:
        return rifiuto("link_sconosciuto")
    if lettura.owner_id == user.id:
        return rifiuto("propria")
    già = (await session.execute(
        select(ShareSignup.id).where(ShareSignup.new_user_id == user.id)
    )).scalar_one_or_none()
    if già is not None:
        return rifiuto("gia_attribuita")
    if user.created_at is None or utcnow() - user.created_at > timedelta(hours=regole.ORE_ACCOUNT_NUOVO):
        return rifiuto("non_nuovo")
    if principal.raw_claims.get("email_verified") is not True:
        return rifiuto("email_non_verificata")
    if not regole.visitatore_valido(payload.visitor):
        return rifiuto("visitatore_non_valido")

    visitor, ip = _impronte(request, payload.visitor)
    eventi = (await session.execute(
        select(ShareEvent.visitor, ShareEvent.ip).where(ShareEvent.reading_id == lettura.id)
    )).all()
    if any(v == visitor or i == ip for v, i in eventi):
        return rifiuto("stessa_persona")

    session.add(ShareSignup(
        sharer_id=lettura.owner_id, new_user_id=user.id, reading_id=lettura.id,
        crediti=regole.CREDITI_ISCRIZIONE,
    ))
    await RegistroCrediti(session).accredita(
        lettura.owner_id, regole.CREDITI_ISCRIZIONE, reason="omaggio",
        note=f"iscrizione dal link condiviso (utente {user.id})",
    )
    await AuditRepository(session).record(
        action="share.signup", actor_id=user.id, target_type="user", target_id=str(lettura.owner_id),
        after={"crediti": regole.CREDITI_ISCRIZIONE, "lettura": str(lettura.id)},
    )
    # Chi arriva dal link l'ha anche aperto: la lettura può diventare accertata.
    await _registra_visita(session, lettura, visitor, ip)
    await session.commit()
    return {"attribuita": True}
