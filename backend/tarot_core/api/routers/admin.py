"""La console: utenti, pagamenti, catalogo, statistiche, report, registro, modelli.

Tutto il router pretende il ruolo `admin`, dichiarato una volta sola sul
router: ripeterlo endpoint per endpoint significa dimenticarlo su quello
aggiunto di fretta.

**La console non legge le letture.** Vede quante sono, di che stesa, quali
carte escono, come le giudicano gli utenti; non vede le domande né i
responsi. Sono dati intimi, e l'amministrazione del servizio non ha bisogno
di conoscerli per farlo funzionare.
"""
from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import Date, cast, distinct, func, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...billing.credits import RegistroCrediti
from ...billing.plans import GestoreAbbonamenti
from ...domain.admin_repositories import (
    AdminUserRepository, AssegnazioniModelliRepository, ContestoAmministrativo,
    RegistroAuditRepository,
)
from ...domain.base import utcnow
from ...domain.billing_models import CreditEntry, PaymentCheckout, Plan, Subscription
from ...domain.models import AuditLog, DrawnCard, Reading, User
from ...llm.compiti import Compito
from ..deps import aggiorna_assegnazioni, get_conoscenza, get_registro_modelli

router = APIRouter(
    prefix="/admin", tags=["console"], dependencies=[Depends(require_role("admin"))],
)


def _contesto(user, request: Request) -> ContestoAmministrativo:
    return ContestoAmministrativo(
        user,
        ip=request.client.host if request.client else None,
        correlation_id=getattr(request.state, "correlation_id", None),
    )


# ---- utenti ---------------------------------------------------------------------


class ModificaUtente(BaseModel):
    attivo: Optional[bool] = None


def _utente_json(u: User) -> Dict[str, Any]:
    return {
        "id": u.id,
        "email": u.email,
        "display_name": u.display_name,
        "locale": u.locale,
        "attivo": u.deleted_at is None,
        "creato": u.created_at.isoformat() if u.created_at else None,
        "referral_code": u.referral_code,
        "invitato_da": u.referred_by,
    }


@router.get("/users")
async def utenti(
    request: Request, user: CurrentUser, session: DbSession,
    q: str = "", limite: int = 50, offset: int = 0,
) -> Dict[str, Any]:
    righe, totale = await AdminUserRepository(session, _contesto(user, request)).cerca(
        testo=q.strip(), limite=min(limite, 200), offset=max(offset, 0),
    )
    registro = RegistroCrediti(session)
    gestore = GestoreAbbonamenti(session)
    elenco = []
    for u in righe:
        dati = _utente_json(u)
        dati["saldo"] = await registro.saldo(u.id)
        abb = await gestore.abbonamento_di(u.id)
        dati["piano"] = abb.plan.slug if abb else None
        elenco.append(dati)
    return {"totale": totale, "utenti": elenco}


@router.get("/users/{user_id}")
async def utente(user_id: int, session: DbSession) -> Dict[str, Any]:
    u = await session.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    gestore = GestoreAbbonamenti(session)
    registro = RegistroCrediti(session)
    abb = await gestore.abbonamento_di(u.id)
    letture = (await session.execute(
        select(Reading.status, func.count()).where(Reading.owner_id == u.id).group_by(Reading.status)
    )).all()
    pagamenti = (await session.execute(
        select(PaymentCheckout).where(PaymentCheckout.user_id == u.id)
        .order_by(PaymentCheckout.created_at.desc()).limit(50)
    )).scalars().all()
    return {
        **_utente_json(u),
        "saldo": await registro.saldo(u.id),
        "abbonamento": {
            "piano": abb.plan.slug, "nome": abb.plan.name, "stato": abb.status,
            "fine": abb.period_end.isoformat(),
        } if abb else None,
        "letture": {stato: n for stato, n in letture},
        "movimenti": [m.to_dict() for m in await registro.movimenti(u.id, limite=50)],
        "pagamenti": [_pagamento_json(p) for p in pagamenti],
    }


@router.patch("/users/{user_id}")
async def modifica_utente(
    user_id: int, payload: ModificaUtente, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    u = await session.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    if u.id == user.id and payload.attivo is False:
        raise HTTPException(status_code=400, detail="Non puoi disattivare il tuo account")
    repo = AdminUserRepository(session, _contesto(user, request))
    if payload.attivo is False:
        await repo.disattiva(u)
    elif payload.attivo is True:
        await repo.riattiva(u)
    await session.commit()
    return _utente_json(u)


# ---- pagamenti e catalogo ------------------------------------------------------------


def _pagamento_json(p: PaymentCheckout) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "user_id": p.user_id,
        "piano": p.plan.slug,
        "nome": p.plan.name,
        "tipo": p.plan.tipo,
        "annuale": p.annuale,
        "stato": p.status,
        "fornitore": p.provider,
        "importo": p.importo,
        "valuta": p.currency,
        "creato": p.created_at.isoformat() if p.created_at else None,
        "completato": p.completed_at.isoformat() if p.completed_at else None,
    }


@router.get("/payments")
async def pagamenti(
    session: DbSession, stato: str = "", limite: int = 100, offset: int = 0,
) -> Dict[str, Any]:
    filtro = [PaymentCheckout.status == stato] if stato else []
    totale = int(await session.scalar(
        select(func.count()).select_from(PaymentCheckout).where(*filtro)
    ) or 0)
    righe = (await session.execute(
        select(PaymentCheckout).where(*filtro).order_by(PaymentCheckout.created_at.desc())
        .limit(min(limite, 500)).offset(max(offset, 0))
    )).scalars().all()
    incassato = int(await session.scalar(
        select(func.coalesce(func.sum(PaymentCheckout.importo), 0))
        .where(PaymentCheckout.status == "pagato")
    ) or 0)
    return {"totale": totale, "incassato": incassato, "pagamenti": [_pagamento_json(p) for p in righe]}


class PianoModificato(BaseModel):
    name: Optional[str] = Field(default=None, max_length=80)
    description: Optional[str] = Field(default=None, max_length=1000)
    price_monthly: Optional[int] = Field(default=None, ge=0)
    price_yearly: Optional[int] = Field(default=None, ge=0)
    credits_per_period: Optional[int] = Field(default=None, ge=0)
    letture_al_giorno: Optional[int] = Field(default=None, ge=-1)
    active: Optional[bool] = None


def _piano_admin_json(p: Plan, abbonati: int = 0) -> Dict[str, Any]:
    return {
        "id": p.id, "slug": p.slug, "nome": p.name, "tipo": p.tipo,
        "descrizione": p.description, "prezzo_mensile": p.price_monthly,
        "prezzo_annuale": p.price_yearly, "crediti": p.credits_per_period,
        "limiti": p.limits or {}, "attivo": p.active, "rango": p.rank,
        "abbonati": abbonati,
    }


@router.get("/plans")
async def catalogo(session: DbSession) -> List[Dict[str, Any]]:
    abbonati = dict((await session.execute(
        select(Subscription.plan_id, func.count())
        .where(Subscription.status.in_(("attivo", "in_prova"))).group_by(Subscription.plan_id)
    )).all())
    piani = await GestoreAbbonamenti(session).piani(solo_attivi=False)
    return [_piano_admin_json(p, abbonati.get(p.id, 0)) for p in piani]


@router.patch("/plans/{slug}")
async def modifica_piano(
    slug: str, payload: PianoModificato, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Prezzi e limiti si cambiano da qui; il nuovo prezzo vale per i
    pagamenti successivi — chi sta pagando paga quello che ha visto."""
    piano = await GestoreAbbonamenti(session).piano_per_slug(slug)
    if piano is None:
        raise HTTPException(status_code=404, detail="Piano non trovato")
    prima = _piano_admin_json(piano)
    for campo in ("name", "description", "price_monthly", "price_yearly", "credits_per_period", "active"):
        valore = getattr(payload, campo)
        if valore is not None:
            setattr(piano, campo, valore)
    if payload.letture_al_giorno is not None:
        piano.limits = {**(piano.limits or {}), "letture_al_giorno": payload.letture_al_giorno}
    from ...domain.repositories import AuditRepository

    await AuditRepository(session).record(
        action="plan.update", actor_id=user.id, target_type="plan", target_id=slug,
        before=prima, after=_piano_admin_json(piano),
        ip=request.client.host if request.client else None,
    )
    await session.commit()
    return _piano_admin_json(piano)


# ---- statistiche -------------------------------------------------------------------------


async def _conteggi(session, dal: datetime, al: datetime) -> Dict[str, int]:
    def tra(col):
        return (col >= dal) & (col < al)

    letture = int(await session.scalar(select(func.count()).select_from(Reading).where(tra(Reading.created_at))) or 0)
    completate = int(await session.scalar(
        select(func.count()).select_from(Reading).where(tra(Reading.created_at), Reading.status == "completata")
    ) or 0)
    attivi = int(await session.scalar(
        select(func.count(distinct(Reading.owner_id))).where(tra(Reading.created_at))
    ) or 0)
    nuovi = int(await session.scalar(select(func.count()).select_from(User).where(tra(User.created_at))) or 0)
    consumati = int(await session.scalar(
        select(func.coalesce(func.sum(-CreditEntry.delta), 0))
        .where(tra(CreditEntry.created_at), CreditEntry.reason == "consumo")
    ) or 0)
    venduti = int(await session.scalar(
        select(func.coalesce(func.sum(CreditEntry.delta), 0))
        .where(tra(CreditEntry.created_at), CreditEntry.reason == "acquisto")
    ) or 0)
    ricavi = int(await session.scalar(
        select(func.coalesce(func.sum(PaymentCheckout.importo), 0))
        .where(PaymentCheckout.status == "pagato", tra(PaymentCheckout.completed_at))
    ) or 0)
    bloccate = int(await session.scalar(
        select(func.count()).select_from(Reading)
        .where(tra(Reading.created_at), Reading.guard_outcome.in_(("bloccato", "riscritto")))
    ) or 0)
    crisi = int(await session.scalar(
        select(func.count()).select_from(AuditLog)
        .where(tra(AuditLog.created_at), AuditLog.action == "reading.crisis")
    ) or 0)
    return {
        "letture": letture, "completate": completate, "utenti_attivi": attivi,
        "nuovi_utenti": nuovi, "crediti_consumati": consumati, "crediti_venduti": venduti,
        "ricavi": ricavi, "guardia_interventi": bloccate, "crisi": crisi,
    }


@router.get("/stats")
async def statistiche(session: DbSession, giorni: int = 30) -> Dict[str, Any]:
    giorni = max(1, min(giorni, 365))
    adesso = utcnow()
    dal = adesso - timedelta(days=giorni)
    precedente = await _conteggi(session, dal - timedelta(days=giorni), dal)
    attuale = await _conteggi(session, dal, adesso)

    giorno = cast(Reading.created_at, Date)
    serie = (await session.execute(
        select(giorno, func.count()).where(Reading.created_at >= dal).group_by(giorno).order_by(giorno)
    )).all()
    per_stesa = (await session.execute(
        select(Reading.spread_id, func.count()).where(Reading.created_at >= dal)
        .group_by(Reading.spread_id).order_by(func.count().desc())
    )).all()
    carte = (await session.execute(
        select(DrawnCard.card_id, func.count())
        .join(Reading, Reading.id == DrawnCard.reading_id)
        .where(Reading.created_at >= dal, DrawnCard.calcolata.is_(False))
        .group_by(DrawnCard.card_id).order_by(func.count().desc()).limit(12)
    )).all()
    feedback = (await session.execute(
        select(Reading.feedback, func.count()).where(Reading.feedback.is_not(None))
        .group_by(Reading.feedback)
    )).all()
    consumo = (await session.execute(
        select(Reading.consumo, func.count()).where(Reading.created_at >= dal).group_by(Reading.consumo)
    )).all()
    abbonamenti = (await session.execute(
        select(Plan.name, func.count()).join(Subscription, Subscription.plan_id == Plan.id)
        .where(Subscription.status.in_(("attivo", "in_prova"))).group_by(Plan.name)
    )).all()

    conoscenza = get_conoscenza()
    stese = {s["id"]: s["nome"] for s in conoscenza.stese.values()}
    return {
        "giorni": giorni,
        "attuale": attuale,
        "precedente": precedente,
        "serie": [{"giorno": g.isoformat(), "letture": n} for g, n in serie],
        "per_stesa": [{"stesa": stese.get(s, s), "letture": n} for s, n in per_stesa],
        "carte": [
            {"carta": conoscenza.carta(c)["nome_it"] if c in conoscenza.carte else c, "uscite": n}
            for c, n in carte
        ],
        "feedback": {f: n for f, n in feedback},
        "consumo": {c: n for c, n in consumo},
        "abbonamenti": {p: n for p, n in abbonamenti},
    }


# ---- report ------------------------------------------------------------------------------


def _csv(nome: str, intestazione: List[str], righe) -> StreamingResponse:
    buffer = io.StringIO()
    scrittore = csv.writer(buffer)
    scrittore.writerow(intestazione)
    for r in righe:
        scrittore.writerow(r)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue().encode("utf-8-sig")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}.csv"'},
    )


@router.get("/reports/{tipo}.csv")
async def report(tipo: str, session: DbSession, giorni: int = 30) -> StreamingResponse:
    """Esportazioni per la contabilità e l'analisi. Le letture escono senza
    domanda né responso: metadati, non contenuti."""
    dal = utcnow() - timedelta(days=max(1, min(giorni, 3650)))
    if tipo == "utenti":
        righe = (await session.execute(select(User).order_by(User.id))).scalars().all()
        return _csv("utenti", ["id", "email", "nome", "lingua", "attivo", "creato", "invitato_da"], (
            [u.id, u.email, u.display_name, u.locale, u.deleted_at is None,
             u.created_at.isoformat() if u.created_at else "", u.referred_by or ""] for u in righe
        ))
    if tipo == "pagamenti":
        righe = (await session.execute(
            select(PaymentCheckout).where(PaymentCheckout.created_at >= dal).order_by(PaymentCheckout.created_at)
        )).scalars().all()
        return _csv("pagamenti", ["id", "utente", "piano", "tipo", "stato", "importo_centesimi", "valuta", "creato", "completato"], (
            [str(p.id), p.user_id, p.plan.slug, p.plan.tipo, p.status, p.importo, p.currency,
             p.created_at.isoformat() if p.created_at else "",
             p.completed_at.isoformat() if p.completed_at else ""] for p in righe
        ))
    if tipo == "crediti":
        righe = (await session.execute(
            select(CreditEntry).where(CreditEntry.created_at >= dal).order_by(CreditEntry.created_at)
        )).scalars().all()
        return _csv("crediti", ["id", "utente", "delta", "motivo", "lettura", "nota", "quando"], (
            [r.id, r.user_id, r.delta, r.reason, str(r.reading_id or ""), r.note or "", r.created_at.isoformat()]
            for r in righe
        ))
    if tipo == "letture":
        righe = (await session.execute(
            select(Reading).where(Reading.created_at >= dal).order_by(Reading.created_at)
        )).scalars().all()
        return _csv("letture", ["id", "utente", "stesa", "stato", "consumo", "guardia", "diario", "creata", "conclusa"], (
            [str(r.id), r.owner_id, r.spread_id, r.status, r.consumo, r.guard_outcome or "",
             r.feedback or "", r.created_at.isoformat(),
             r.completed_at.isoformat() if r.completed_at else ""] for r in righe
        ))
    raise HTTPException(status_code=404, detail="Report sconosciuto")


# ---- registro e modelli -------------------------------------------------------------------


@router.get("/audit")
async def registro(
    session: DbSession, limite: int = 100, azione: str = "", target_type: str = "",
) -> List[Dict[str, Any]]:
    righe = await RegistroAuditRepository(session).recenti(
        limite=min(limite, 500), azione=azione or None, target_type=target_type or None,
    )
    return [
        {
            "id": r.id, "attore": r.actor_id, "azione": r.action,
            "tipo": r.target_type, "target": r.target_id,
            "prima": r.before, "dopo": r.after, "ip": r.ip,
            "quando": r.created_at.isoformat(),
        }
        for r in righe
    ]


class Assegnazione(BaseModel):
    modello: Optional[str] = Field(default=None, max_length=60)


@router.get("/models")
async def modelli(session: DbSession) -> Dict[str, Any]:
    await aggiorna_assegnazioni(session, forza=True)
    registro = get_registro_modelli()
    return {
        "modelli": [
            {"nome": m.nome, "provider": m.provider, "model": m.model, "descrizione": m.descrizione}
            for m in registro.modelli
        ],
        "compiti": registro.stato(),
    }


@router.put("/models/{compito}")
async def assegna(
    compito: str, payload: Assegnazione, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    try:
        c = Compito(compito)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Compito sconosciuto") from exc
    registro = get_registro_modelli()
    if payload.modello is not None and not registro.esiste(payload.modello):
        raise HTTPException(status_code=400, detail="Modello non configurato")
    await AssegnazioniModelliRepository(session, _contesto(user, request)).assegna(c.value, payload.modello)
    await session.commit()
    registro.assegna(c, payload.modello)
    return {"compiti": registro.stato()}
