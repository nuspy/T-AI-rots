"""La console «Abbonamenti» (v9, Fase 2b): le impostazioni e l'elenco degli abbonamenti, con le azioni.

**Impostazioni** (una riga): sconto del rinnovo automatico (20%), sconto della prova (50%), giorni della prova (14),
di tolleranza (7) e del promemoria (2), condoni per periodo (2), banner della prova. Valgono per i pagamenti e i
rinnovi **da adesso**: un abbonamento già aperto tiene lo sconto che ha (presso Stripe è un coupon sull'abbonamento).

**Elenco** per stato (`in_prova`, `attivo`, `in_sospeso`, `sospeso`, `disdetto`, `scaduto`), con ricerca per email.
**Azioni**, ognuna con un motivo obbligatorio e il suo record di audit:

| azione | cosa fa |
|---|---|
| `rinnovo_spento` | spegne il rinnovo automatico per conto dell'utente (presso il fornitore; email di conferma) |
| `rinnovo_acceso` | lo riaccende, prima della scadenza |
| `sospendi` | chiude subito la tolleranza di un pagamento fallito (`in_sospeso` → `sospeso`) |
| `proroga` | allunga il periodo di N giorni — solo per gli abbonamenti interni: per Stripe e gli store la data la decide chi incassa |
| `chiudi` | chiude adesso, senza rimborso (il rimborso, se dovuto, si fa nel Dashboard del fornitore) |

Gli abbonamenti degli store non hanno azioni qui: si gestiscono nelle console di Google e Apple.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...billing import abbonamenti as gestione
from ...billing.pagamenti import PagamentiNonDisponibili, provider_pagamenti
from ...billing.plans import GestoreAbbonamenti
from ...domain.base import utcnow
from ...domain.billing_models import STATI_ABBONAMENTO, Subscription
from ...domain.models import User
from ...domain.repositories import AuditRepository

router = APIRouter(prefix="/admin/abbonamenti", tags=["abbonamenti"], dependencies=[Depends(require_role("admin"))])

AZIONI = ("rinnovo_spento", "rinnovo_acceso", "sospendi", "proroga", "chiudi")


class Impostazioni(BaseModel):
    sconto_rinnovo: Optional[int] = Field(default=None, ge=0, le=90)
    sconto_prova: Optional[int] = Field(default=None, ge=0, le=90)
    giorni_prova: Optional[int] = Field(default=None, ge=1, le=60)
    giorni_tolleranza: Optional[int] = Field(default=None, ge=1, le=30)
    giorni_promemoria_prova: Optional[int] = Field(default=None, ge=1, le=7)
    condoni_per_periodo: Optional[int] = Field(default=None, ge=0, le=10)
    banner_prova: Optional[bool] = None


class Azione(BaseModel):
    azione: str = Field(pattern="^(rinnovo_spento|rinnovo_acceso|sospendi|proroga|chiudi)$")
    motivo: str = Field(min_length=3, max_length=500)
    giorni: Optional[int] = Field(default=None, ge=1, le=366)


def _riga_json(a: Subscription, utente: Optional[User], tolleranza: int) -> Dict[str, Any]:
    dati = gestione.abbonamento_json(a, tolleranza=tolleranza) or {}
    dati.update({
        "utente": {"id": a.user_id, "email": utente.email if utente else None},
        "external_id": a.external_id,
        "creato": a.created_at.isoformat() if a.created_at else None,
        "azioni": _azioni_possibili(a),
    })
    return dati


def _azioni_possibili(a: Subscription) -> list[str]:
    if gestione.nello_store(a) or gestione.gratuito(a.plan) or a.status in ("disdetto", "scaduto"):
        return []
    azioni = []
    if a.vivo:
        azioni.append("rinnovo_spento" if a.rinnovo_automatico else "rinnovo_acceso")
    if a.status == "in_sospeso":
        azioni.append("sospendi")
    if a.provider in ("interno", "mock"):
        azioni.append("proroga")
    azioni.append("chiudi")
    return azioni


@router.get("/impostazioni")
async def leggi_impostazioni(session: DbSession) -> Dict[str, Any]:
    riga = await gestione.impostazioni(session)
    await session.commit()
    return gestione.impostazioni_json(riga)


@router.put("/impostazioni")
async def scrivi_impostazioni(payload: Impostazioni, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    riga = await gestione.aggiorna_impostazioni(
        session, payload.model_dump(exclude_none=True), attore_id=user.id, ip=ip_client(request),
    )
    await session.commit()
    return gestione.impostazioni_json(riga)


@router.get("")
async def elenco(
    session: DbSession,
    stato: str = Query(default="", max_length=20),
    q: str = Query(default="", max_length=200),
    limite: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    provider: str = Query(default="", max_length=20),
) -> Dict[str, Any]:
    """Gli abbonamenti, i più recenti prima: per stato, per chi li incassa (Stripe, Google Play, App Store…, Fase 4)
    e per email. Il piano gratuito non c'è (non si gestisce)."""
    from ...domain.billing_models import FORNITORI, Plan

    if stato and stato not in STATI_ABBONAMENTO:
        raise HTTPException(status_code=422, detail="Stato sconosciuto")
    if provider and provider not in FORNITORI:
        raise HTTPException(status_code=422, detail="Fornitore sconosciuto")

    condizioni = [or_(Plan.price_monthly > 0, Plan.price_yearly > 0)]
    if stato:
        condizioni.append(Subscription.status == stato)
    if provider:
        condizioni.append(Subscription.provider == provider)
    if q.strip():
        condizioni.append(User.email.ilike(f"%{q.strip()}%"))
    base = select(Subscription).join(Plan, Plan.id == Subscription.plan_id).join(User, User.id == Subscription.user_id)
    totale = int(await session.scalar(select(func.count()).select_from(base.where(*condizioni).subquery())) or 0)
    righe = (await session.execute(
        base.where(*condizioni).order_by(Subscription.created_at.desc()).limit(limite).offset(offset)
    )).scalars().all()
    conteggi = dict((await session.execute(
        select(Subscription.status, func.count()).join(Plan, Plan.id == Subscription.plan_id)
        .where(or_(Plan.price_monthly > 0, Plan.price_yearly > 0), *([Subscription.provider == provider] if provider else []))
        .group_by(Subscription.status)
    )).all())
    per_fornitore = dict((await session.execute(
        select(Subscription.provider, func.count()).join(Plan, Plan.id == Subscription.plan_id)
        .where(or_(Plan.price_monthly > 0, Plan.price_yearly > 0)).group_by(Subscription.provider)
    )).all())
    riga = await gestione.impostazioni(session)
    utenti = {u.id: u for u in (await session.execute(
        select(User).where(User.id.in_({a.user_id for a in righe}))
    )).scalars()} if righe else {}
    await session.commit()
    return {
        "totale": totale,
        "conteggi": {s: int(conteggi.get(s, 0)) for s in STATI_ABBONAMENTO},
        "per_fornitore": {p: int(n) for p, n in per_fornitore.items()},
        "abbonamenti": [_riga_json(a, utenti.get(a.user_id), riga.giorni_tolleranza) for a in righe],
    }


@router.post("/{abbonamento_id}/azione")
async def azione(
    abbonamento_id: str, payload: Azione, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    import uuid

    try:
        ident = uuid.UUID(abbonamento_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Abbonamento non trovato") from exc
    abbonamento = await session.get(Subscription, ident, with_for_update=True)
    if abbonamento is None:
        raise HTTPException(status_code=404, detail="Abbonamento non trovato")
    if payload.azione not in _azioni_possibili(abbonamento):
        raise HTTPException(status_code=409, detail="Questa azione non vale per questo abbonamento.")
    utente = await session.get(User, abbonamento.user_id)
    prima = gestione.abbonamento_json(abbonamento)
    configurato = provider_pagamenti()
    try:
        if payload.azione in ("rinnovo_spento", "rinnovo_acceso"):
            await gestione.imposta_rinnovo(
                session, abbonamento, payload.azione == "rinnovo_acceso", configurato=configurato, utente=utente,
            )
        elif payload.azione == "sospendi":
            abbonamento.status = "sospeso"
        elif payload.azione == "proroga":
            if not payload.giorni:
                raise HTTPException(status_code=422, detail="Quanti giorni?")
            abbonamento.period_end = abbonamento.period_end + timedelta(days=payload.giorni)
            if abbonamento.cancel_at is not None:
                abbonamento.cancel_at = abbonamento.period_end
        elif payload.azione == "chiudi":
            fornitore = gestione.fornitore_per(abbonamento, configurato)
            if fornitore is not None and hasattr(fornitore, "chiudi_subito"):
                await fornitore.chiudi_subito(abbonamento.external_id)
            abbonamento.status = "disdetto"
            abbonamento.cancel_at = utcnow()
            await session.flush()
            await GestoreAbbonamenti(session, configurato).apri_piano_base(abbonamento.user_id)
    except gestione.ErroreAbbonamento as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PagamentiNonDisponibili as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    await session.flush()
    await AuditRepository(session).record(
        action=f"subscription.admin.{payload.azione}", actor_id=user.id, target_type="subscription",
        target_id=str(abbonamento.id), before=prima,
        after={**(gestione.abbonamento_json(abbonamento) or {}), "motivo": payload.motivo, "giorni": payload.giorni},
        ip=ip_client(request),
    )
    await session.commit()
    await session.refresh(abbonamento, ["plan", "piano_successivo"])
    riga = await gestione.impostazioni(session)
    return _riga_json(abbonamento, utente, riga.giorni_tolleranza)
