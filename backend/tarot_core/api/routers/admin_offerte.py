"""La console: le offerte commerciali. Piani (abbonamenti e pacchetti), coupon di sconto, codici regalo, regali di crediti.

Modificare un piano già esiste (`PATCH /admin/plans/{slug}` in `admin.py`); qui si **creano** e si **eliminano**, e si
gestiscono i coupon. Ogni scrittura finisce nel registro di audit con lo stato di prima.

**Cosa non si cancella.** Un piano usato (con abbonamenti o pagamenti) si disattiva, non si elimina: i conti dell'anno
scorso devono restare leggibili. Un coupon già usato pure. Ciò che non è mai stato usato si può eliminare.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from lanterna.rete import ip_client
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...billing import offerte
from ...billing.credits import RegistroCrediti
from ...billing.plans import GestoreAbbonamenti
from ...domain.billing_models import (
    TIPI_PIANO, Coupon, CouponRedemption, PaymentCheckout, Plan, Subscription,
)
from ...domain.models import User
from ...domain.repositories import AuditRepository
from .admin import _piano_admin_json

router = APIRouter(prefix="/admin", tags=["offerte"], dependencies=[Depends(require_role("admin"))])

TETTO_PREZZO = 1_000_000          # centesimi: diecimila euro, oltre è un refuso
TETTO_CREDITI = 100_000


def _ip(request: Request) -> Optional[str]:
    return ip_client(request)


# ---- piani ------------------------------------------------------------------------------------------------------


class PianoNuovo(BaseModel):
    slug: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=80)
    description: Optional[str] = Field(default=None, max_length=1000)
    tipo: Literal["abbonamento", "pacchetto"] = "abbonamento"
    #: In centesimi. Per un pacchetto è il prezzo dell'acquisto (il backend lo chiama «mensile»).
    price_monthly: int = Field(default=0, ge=0, le=TETTO_PREZZO)
    price_yearly: int = Field(default=0, ge=0, le=TETTO_PREZZO)
    credits_per_period: int = Field(default=0, ge=0, le=TETTO_CREDITI)
    #: Letture al giorno di un abbonamento; -1 = senza limite, 0 = nessuna (si pagano coi crediti).
    letture_al_giorno: int = Field(default=0, ge=-1, le=1000)
    rank: int = Field(default=100, ge=0, le=10_000)
    active: bool = True

    @model_validator(mode="after")
    def _coerente(self) -> "PianoNuovo":
        if not offerte.SLUG_PIANO.match(self.slug):
            raise ValueError("lo slug ha lettere minuscole, cifre e trattini (2-40 caratteri), e non comincia né finisce con un trattino")
        if self.tipo == "pacchetto":
            if self.credits_per_period < 1:
                raise ValueError("un pacchetto accredita almeno un credito")
            if self.price_yearly:
                raise ValueError("un pacchetto ha un prezzo solo")
        return self


async def _usato(session, piano: Plan) -> bool:
    """Un piano è usato se qualcuno lo ha sottoscritto o ha aperto un pagamento: da lì in poi non si elimina."""
    abbonamenti = await session.scalar(select(func.count()).select_from(Subscription).where(Subscription.plan_id == piano.id))
    pagamenti = await session.scalar(select(func.count()).select_from(PaymentCheckout).where(PaymentCheckout.plan_id == piano.id))
    return bool(abbonamenti or pagamenti)


@router.post("/plans", status_code=201)
async def crea_piano(payload: PianoNuovo, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if await GestoreAbbonamenti(session).piano_per_slug(payload.slug) is not None:
        raise HTTPException(status_code=409, detail=f"Esiste già un piano con lo slug «{payload.slug}».")
    limiti = {"letture_al_giorno": payload.letture_al_giorno} if payload.tipo == "abbonamento" else {}
    piano = Plan(
        slug=payload.slug, name=payload.name.strip(), description=(payload.description or "").strip() or None,
        tipo=payload.tipo, price_monthly=payload.price_monthly,
        price_yearly=payload.price_yearly if payload.tipo == "abbonamento" else 0,
        currency="EUR", credits_per_period=payload.credits_per_period, limits=limiti, rank=payload.rank,
        active=payload.active,
    )
    session.add(piano)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Esiste già un piano con lo slug «{payload.slug}».") from exc
    await AuditRepository(session).record(
        action="plan.create", actor_id=user.id, target_type="plan", target_id=piano.slug, after=_piano_admin_json(piano),
        ip=_ip(request),
    )
    await session.commit()
    return _piano_admin_json(piano)


@router.delete("/plans/{slug}", status_code=204)
async def elimina_piano(slug: str, request: Request, user: CurrentUser, session: DbSession) -> Response:
    """Elimina un piano **mai usato**. Uno usato si disattiva: sparisce dalla vendita e chi lo ha lo tiene."""
    piano = await GestoreAbbonamenti(session).piano_per_slug(slug)
    if piano is None:
        raise HTTPException(status_code=404, detail="Piano non trovato")
    if await _usato(session, piano):
        raise HTTPException(
            status_code=409,
            detail="Il piano è stato usato (abbonamenti o pagamenti): disattivalo, non si elimina.",
        )
    prima = _piano_admin_json(piano)
    await session.delete(piano)
    await AuditRepository(session).record(
        action="plan.delete", actor_id=user.id, target_type="plan", target_id=slug, before=prima, ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)


# ---- coupon -----------------------------------------------------------------------------------------------------


class CouponIn(BaseModel):
    #: Vuoto: lo sceglie il server (8 caratteri leggibili).
    code: Optional[str] = Field(default=None, max_length=40)
    description: Optional[str] = Field(default=None, max_length=500)
    tipo: Literal["percentuale", "importo", "crediti"] = "percentuale"
    #: Percentuale (1-100), centesimi, o crediti, secondo il tipo.
    valore: int = Field(ge=1, le=TETTO_PREZZO)
    #: Gli slug dei piani a cui vale; vuoto = tutti. Non si usa con un codice regalo.
    piani: List[str] = Field(default_factory=list, max_length=50)
    solo_primo_acquisto: bool = False
    valido_dal: Optional[datetime] = None
    valido_fino: Optional[datetime] = None
    max_riscatti: Optional[int] = Field(default=None, ge=1, le=10_000_000)
    max_per_utente: int = Field(default=1, ge=1, le=100)
    attivo: bool = True

    @model_validator(mode="after")
    def _coerente(self) -> "CouponIn":
        if self.tipo == "percentuale" and self.valore > 100:
            raise ValueError("una percentuale va da 1 a 100")
        if self.tipo == "crediti" and self.valore > TETTO_CREDITI:
            raise ValueError(f"un codice regalo dà al massimo {TETTO_CREDITI} crediti")
        if self.tipo == "crediti" and (self.piani or self.solo_primo_acquisto):
            raise ValueError("un codice regalo non ha piani né «primo acquisto»: dà crediti e basta")
        if self.valido_dal and self.valido_fino and self.valido_fino <= self.valido_dal:
            raise ValueError("«valido fino» deve venire dopo «valido dal»")
        return self


class CouponMod(BaseModel):
    """Si cambia ciò che non altera il passato: il tipo e il valore di un coupon già usato restano com'erano."""

    description: Optional[str] = Field(default=None, max_length=500)
    piani: Optional[List[str]] = Field(default=None, max_length=50)
    solo_primo_acquisto: Optional[bool] = None
    valido_dal: Optional[datetime] = None
    valido_fino: Optional[datetime] = None
    max_riscatti: Optional[int] = Field(default=None, ge=1, le=10_000_000)
    max_per_utente: Optional[int] = Field(default=None, ge=1, le=100)
    attivo: Optional[bool] = None
    #: Solo se il coupon non è mai stato usato.
    valore: Optional[int] = Field(default=None, ge=1, le=TETTO_PREZZO)


def coupon_json(c: Coupon) -> Dict[str, Any]:
    return {
        "id": c.id, "codice": c.code, "descrizione": c.description, "tipo": c.tipo, "valore": c.valore,
        "piani": list(c.piani or []), "solo_primo_acquisto": c.solo_primo_acquisto,
        "valido_dal": c.valido_dal.isoformat() if c.valido_dal else None,
        "valido_fino": c.valido_fino.isoformat() if c.valido_fino else None,
        "max_riscatti": c.max_riscatti, "max_per_utente": c.max_per_utente, "riscatti": c.riscatti,
        "attivo": c.attivo, "creato": c.created_at.isoformat() if c.created_at else None,
    }


async def _controlla_piani(session, slugs: List[str]) -> List[str]:
    puliti = sorted({s.strip() for s in slugs if s and s.strip()})
    if puliti:
        esistenti = set((await session.execute(select(Plan.slug).where(Plan.slug.in_(puliti)))).scalars())
        mancanti = [s for s in puliti if s not in esistenti]
        if mancanti:
            raise HTTPException(status_code=422, detail=f"Piani sconosciuti: {', '.join(mancanti)}")
    return puliti


@router.get("/coupons")
async def elenco_coupon(session: DbSession) -> List[Dict[str, Any]]:
    righe = (await session.execute(select(Coupon).order_by(Coupon.created_at.desc()))).scalars().all()
    return [coupon_json(c) for c in righe]


@router.post("/coupons", status_code=201)
async def crea_coupon(payload: CouponIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    codice = offerte.normalizza_codice(payload.code) if payload.code else offerte.codice_nuovo()
    if not offerte.CODICE.match(codice):
        raise HTTPException(status_code=422, detail="Il codice ha da 3 a 40 caratteri: lettere maiuscole, cifre, trattino e trattino basso.")
    if await offerte.trova(session, codice) is not None:
        raise HTTPException(status_code=409, detail=f"Il codice «{codice}» esiste già.")
    coupon = Coupon(
        code=codice, description=(payload.description or "").strip() or None, tipo=payload.tipo, valore=payload.valore,
        piani=await _controlla_piani(session, payload.piani), solo_primo_acquisto=payload.solo_primo_acquisto,
        valido_dal=payload.valido_dal, valido_fino=payload.valido_fino, max_riscatti=payload.max_riscatti,
        max_per_utente=payload.max_per_utente, attivo=payload.attivo,
    )
    session.add(coupon)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail=f"Il codice «{codice}» esiste già.") from exc
    await AuditRepository(session).record(
        action="coupon.create", actor_id=user.id, target_type="coupon", target_id=codice, after=coupon_json(coupon),
        ip=_ip(request),
    )
    await session.commit()
    return coupon_json(coupon)


@router.patch("/coupons/{coupon_id}")
async def modifica_coupon(
    coupon_id: int, payload: CouponMod, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    coupon = await session.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon non trovato")
    prima = coupon_json(coupon)
    dati = payload.model_dump(exclude_unset=True)
    if "valore" in dati:
        if coupon.riscatti > 0:
            raise HTTPException(status_code=409, detail="Il coupon è già stato usato: il valore non si cambia (creane un altro).")
        if coupon.tipo == "percentuale" and dati["valore"] > 100:
            raise HTTPException(status_code=422, detail="Una percentuale va da 1 a 100.")
        coupon.valore = dati.pop("valore")
    if "piani" in dati:
        if coupon.tipo == "crediti" and dati["piani"]:
            raise HTTPException(status_code=422, detail="Un codice regalo non ha piani.")
        coupon.piani = await _controlla_piani(session, dati.pop("piani") or [])
    if "description" in dati:
        coupon.description = (dati.pop("description") or "").strip() or None
    for campo, valore in dati.items():
        setattr(coupon, campo, valore)
    if coupon.valido_dal and coupon.valido_fino and coupon.valido_fino <= coupon.valido_dal:
        raise HTTPException(status_code=422, detail="«Valido fino» deve venire dopo «valido dal».")
    await AuditRepository(session).record(
        action="coupon.update", actor_id=user.id, target_type="coupon", target_id=coupon.code, before=prima,
        after=coupon_json(coupon), ip=_ip(request),
    )
    await session.commit()
    return coupon_json(coupon)


@router.delete("/coupons/{coupon_id}", status_code=204)
async def elimina_coupon(coupon_id: int, request: Request, user: CurrentUser, session: DbSession) -> Response:
    coupon = await session.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon non trovato")
    usi = await session.scalar(select(func.count()).select_from(CouponRedemption).where(CouponRedemption.coupon_id == coupon.id))
    if coupon.riscatti or usi:
        raise HTTPException(status_code=409, detail="Il coupon è già stato usato: disattivalo, non si elimina.")
    prima = coupon_json(coupon)
    await session.delete(coupon)
    await AuditRepository(session).record(
        action="coupon.delete", actor_id=user.id, target_type="coupon", target_id=coupon.code, before=prima, ip=_ip(request),
    )
    await session.commit()
    return Response(status_code=204)


@router.get("/coupons/{coupon_id}/riscatti")
async def riscatti_coupon(coupon_id: int, session: DbSession, limite: int = 100) -> Dict[str, Any]:
    coupon = await session.get(Coupon, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon non trovato")
    righe = (await session.execute(
        select(CouponRedemption, User.email)
        .join(User, User.id == CouponRedemption.user_id)
        .where(CouponRedemption.coupon_id == coupon.id)
        .order_by(CouponRedemption.created_at.desc()).limit(min(max(limite, 1), 500))
    )).all()
    return {
        "coupon": coupon_json(coupon),
        "riscatti": [
            {"id": r.id, "utente": r.user_id, "email": email, "sconto": r.sconto, "crediti": r.crediti,
             "pagamento": str(r.checkout_id) if r.checkout_id else None, "quando": r.created_at.isoformat()}
            for r, email in righe
        ],
    }


# ---- regalare crediti --------------------------------------------------------------------------------------------


class Regalo(BaseModel):
    """Un regalo di crediti: un pacchetto del catalogo (`piano`) o una quantità (`crediti`), non entrambi."""

    piano: Optional[str] = Field(default=None, max_length=40)
    crediti: Optional[int] = Field(default=None, ge=1, le=TETTO_CREDITI)
    nota: Optional[str] = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def _uno_dei_due(self) -> "Regalo":
        if (self.piano is None) == (self.crediti is None):
            raise ValueError("indica un pacchetto (`piano`) oppure una quantità (`crediti`)")
        return self


@router.post("/users/{user_id}/regalo")
async def regala_crediti(
    user_id: int, payload: Regalo, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Regala crediti a un utente. Compaiono nel suo registro come `omaggio`, con chi li ha regalati nell'audit."""
    destinatario = await session.get(User, user_id)
    if destinatario is None or destinatario.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    crediti = payload.crediti
    origine = "quantità"
    if payload.piano is not None:
        piano = await GestoreAbbonamenti(session).piano_per_slug(payload.piano)
        if piano is None or not piano.pacchetto:
            raise HTTPException(status_code=422, detail="Il piano indicato non è un pacchetto di crediti.")
        crediti, origine = piano.credits_per_period, f"pacchetto {piano.slug}"
    registro = RegistroCrediti(session)
    prima = await registro.saldo(user_id)
    nota = f"regalo: {origine}" + (f" — {payload.nota.strip()}" if payload.nota and payload.nota.strip() else "")
    await registro.accredita(user_id, int(crediti), reason="omaggio", note=nota[:500])
    dopo = await registro.saldo(user_id)
    await AuditRepository(session).record(
        action="credits.gift", actor_id=user.id, target_type="user", target_id=str(user_id),
        before={"saldo": prima}, after={"saldo": dopo, "crediti": crediti, "origine": origine, "nota": payload.nota},
        ip=_ip(request),
    )
    await session.commit()
    return {"saldo": dopo, "crediti": crediti}
