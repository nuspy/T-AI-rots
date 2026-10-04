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
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...billing import offerte, resoconto_coupon
from ...billing.credits import RegistroCrediti
from ...billing.plans import GestoreAbbonamenti
from ...domain.billing_models import (
    TIPI_PIANO, Coupon, CouponLotto, CouponRedemption, PaymentCheckout, Plan, Subscription,
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
    #: I limiti della Fase 2b; assenti o −1 = senza limite.
    letture_alla_settimana: Optional[int] = Field(default=None, ge=-1, le=10_000)
    letture_al_mese: Optional[int] = Field(default=None, ge=-1, le=10_000)
    letture_totali: Optional[int] = Field(default=None, ge=-1, le=100_000)
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
    limiti: Dict[str, int] = {}
    if payload.tipo == "abbonamento":
        limiti = {"letture_al_giorno": payload.letture_al_giorno}
        for limite in ("letture_alla_settimana", "letture_al_mese", "letture_totali"):
            if getattr(payload, limite) is not None:
                limiti[limite] = getattr(payload, limite)
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
    #: Fase 2d: su un abbonamento, il primo pagamento, i primi `periodi` (2-36, il primo compreso) o tutti.
    durata: Literal["una_volta", "periodi", "sempre"] = "una_volta"
    periodi: Optional[int] = Field(default=None, ge=2, le=36)
    #: Si somma allo sconto del rinnovo automatico o della prova; di default no (vale il più alto).
    cumulabile: bool = False
    campagna: Optional[str] = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def _coerente(self) -> "CouponIn":
        if self.tipo == "percentuale" and self.valore > 100:
            raise ValueError("una percentuale va da 1 a 100")
        if self.tipo == "crediti" and self.valore > TETTO_CREDITI:
            raise ValueError(f"un codice regalo dà al massimo {TETTO_CREDITI} crediti")
        if self.tipo == "crediti" and (self.piani or self.solo_primo_acquisto):
            raise ValueError("un codice regalo non ha piani né «primo acquisto»: dà crediti e basta")
        if self.tipo == "crediti" and (self.durata != "una_volta" or self.cumulabile):
            raise ValueError("un codice regalo non ha durata né cumulo: dà crediti e basta")
        if self.durata == "periodi" and not self.periodi:
            raise ValueError("«per N periodi» vuole il numero dei periodi (da 2 a 36)")
        if self.durata != "periodi":
            self.periodi = None
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
    campagna: Optional[str] = Field(default=None, max_length=80)
    #: Solo se il coupon non è mai stato usato: valore, durata e cumulo sono ciò che chi l'ha usato ha visto.
    valore: Optional[int] = Field(default=None, ge=1, le=TETTO_PREZZO)
    durata: Optional[Literal["una_volta", "periodi", "sempre"]] = None
    periodi: Optional[int] = Field(default=None, ge=2, le=36)
    cumulabile: Optional[bool] = None


def link_coupon(codice: str) -> Dict[str, str]:
    """Il link che applica il coupon da solo: la pagina dei prezzi in inglese e in italiano (`/pricing`, `/it/piano`:
    `frontend/lib/indirizzi.ts`). Il sito lo conserva per la sessione, anche dopo la registrazione."""
    from urllib.parse import quote

    from ...settings import get_settings

    base = get_settings().web_public_url.rstrip("/")
    return {"en": f"{base}/pricing?coupon={quote(codice)}", "it": f"{base}/it/piano?coupon={quote(codice)}"}


def coupon_json(c: Coupon) -> Dict[str, Any]:
    return {
        "id": c.id, "codice": c.code, "descrizione": c.description, "tipo": c.tipo, "valore": c.valore,
        "piani": list(c.piani or []), "solo_primo_acquisto": c.solo_primo_acquisto,
        "valido_dal": c.valido_dal.isoformat() if c.valido_dal else None,
        "valido_fino": c.valido_fino.isoformat() if c.valido_fino else None,
        "max_riscatti": c.max_riscatti, "max_per_utente": c.max_per_utente, "riscatti": c.riscatti,
        "attivo": c.attivo, "creato": c.created_at.isoformat() if c.created_at else None,
        "durata": c.durata, "periodi": c.periodi, "cumulabile": c.cumulabile, "campagna": c.campagna,
        "lotto_id": c.lotto_id, "link": link_coupon(c.code) if c.tipo != "crediti" else None,
    }


def _campagna(testo: Optional[str]) -> Optional[str]:
    """Un'etichetta di campagna: testo libero, senza spazi ai lati; vuota = nessuna."""
    return (testo or "").strip()[:80] or None


async def _controlla_piani(session, slugs: List[str]) -> List[str]:
    puliti = sorted({s.strip() for s in slugs if s and s.strip()})
    if puliti:
        esistenti = set((await session.execute(select(Plan.slug).where(Plan.slug.in_(puliti)))).scalars())
        mancanti = [s for s in puliti if s not in esistenti]
        if mancanti:
            raise HTTPException(status_code=422, detail=f"Piani sconosciuti: {', '.join(mancanti)}")
    return puliti


@router.get("/coupons")
async def elenco_coupon(
    session: DbSession, lotto: Optional[int] = None, resoconto: bool = False,
) -> List[Dict[str, Any]]:
    """I coupon singoli; con `lotto` i codici di quel lotto (Fase 2d: i lotti non affollano l'elenco). Con `resoconto`
    ognuno porta le sue cifre."""
    q = select(Coupon).order_by(Coupon.created_at.desc(), Coupon.id.desc())
    q = q.where(Coupon.lotto_id == lotto) if lotto is not None else q.where(Coupon.lotto_id.is_(None))
    righe = (await session.execute(q)).scalars().all()
    elenco = [coupon_json(c) for c in righe]
    if resoconto:
        cifre = await resoconto_coupon.per_tutti_i_coupon(session, [c.id for c in righe])
        for voce in elenco:
            voce["resoconto"] = cifre.get(voce["id"])
    return elenco


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
        durata=payload.durata, periodi=payload.periodi, cumulabile=payload.cumulabile,
        campagna=_campagna(payload.campagna),
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
    regole = {k: dati.pop(k) for k in ("durata", "periodi", "cumulabile") if k in dati}
    if regole:
        if coupon.tipo == "crediti":
            raise HTTPException(status_code=422, detail="Un codice regalo non ha durata né cumulo.")
        nuove = {"durata": coupon.durata, "periodi": coupon.periodi, "cumulabile": coupon.cumulabile, **regole}
        if nuove["durata"] != "periodi":
            nuove["periodi"] = None
        elif not nuove["periodi"]:
            raise HTTPException(status_code=422, detail="«Per N periodi» vuole il numero dei periodi (da 2 a 36).")
        cambiate = {k: v for k, v in nuove.items() if getattr(coupon, k) != v}
        if cambiate and coupon.riscatti > 0:
            raise HTTPException(
                status_code=409,
                detail="Il coupon è già stato usato: durata e cumulo non si cambiano (creane un altro).",
            )
        for campo, valore in cambiate.items():
            setattr(coupon, campo, valore)
    if "campagna" in dati:
        coupon.campagna = _campagna(dati.pop("campagna"))
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
             "pagamento": str(r.checkout_id) if r.checkout_id else None, "quando": r.created_at.isoformat(),
             "importo": r.importo, "rinnovo": r.rinnovo}
            for r, email in righe
        ],
        "resoconto": await resoconto_coupon.per_coupon(session, coupon.id),
    }


# ---- lotti di codici monouso e campagne (Fase 2d) -----------------------------------------------------------------


class LottoIn(BaseModel):
    """«Genera N codici»: ognuno si usa una volta sola, con le regole di sconto qui sotto, per la campagna del lotto."""

    prefisso: str = Field(min_length=2, max_length=20)
    quantita: int = Field(ge=1, le=offerte.MAX_LOTTO)
    campagna: str = Field(min_length=1, max_length=80)
    description: Optional[str] = Field(default=None, max_length=500)
    tipo: Literal["percentuale", "importo", "crediti"] = "percentuale"
    valore: int = Field(ge=1, le=TETTO_PREZZO)
    piani: List[str] = Field(default_factory=list, max_length=50)
    solo_primo_acquisto: bool = False
    valido_dal: Optional[datetime] = None
    valido_fino: Optional[datetime] = None
    durata: Literal["una_volta", "periodi", "sempre"] = "una_volta"
    periodi: Optional[int] = Field(default=None, ge=2, le=36)
    cumulabile: bool = False

    @model_validator(mode="after")
    def _coerente(self) -> "LottoIn":
        self.prefisso = offerte.normalizza_codice(self.prefisso).rstrip("-")
        if not offerte.PREFISSO.match(self.prefisso):
            raise ValueError("il prefisso ha da 2 a 20 caratteri: lettere, cifre e trattino basso")
        # Le stesse regole di un coupon singolo (un lotto è N coupon uguali).
        CouponIn(
            tipo=self.tipo, valore=self.valore, piani=self.piani, solo_primo_acquisto=self.solo_primo_acquisto,
            valido_dal=self.valido_dal, valido_fino=self.valido_fino, durata=self.durata, periodi=self.periodi,
            cumulabile=self.cumulabile,
        )
        if self.durata != "periodi":
            self.periodi = None
        return self


def lotto_json(lotto: CouponLotto, usati: int = 0, attivi: int = 0, esempio: Optional[Coupon] = None) -> Dict[str, Any]:
    return {
        "id": lotto.id, "prefisso": lotto.prefisso, "campagna": lotto.campagna, "descrizione": lotto.description,
        "quantita": lotto.quantita, "usati": usati, "attivi": attivi,
        "creato": lotto.created_at.isoformat() if lotto.created_at else None,
        # Le regole sono uguali per tutti i codici: si mostrano dal primo.
        "regole": None if esempio is None else {
            k: v for k, v in coupon_json(esempio).items()
            if k in ("tipo", "valore", "piani", "solo_primo_acquisto", "valido_dal", "valido_fino", "durata", "periodi",
                     "cumulabile")
        },
    }


async def _conti_lotti(session) -> Dict[int, tuple]:
    righe = (await session.execute(
        select(
            Coupon.lotto_id, func.count().filter(Coupon.riscatti > 0), func.count().filter(Coupon.attivo.is_(True)),
            func.min(Coupon.id),
        ).where(Coupon.lotto_id.is_not(None)).group_by(Coupon.lotto_id)
    )).all()
    return {lotto_id: (int(usati), int(attivi), primo) for lotto_id, usati, attivi, primo in righe}


@router.get("/coupon-lotti")
async def elenco_lotti(session: DbSession) -> List[Dict[str, Any]]:
    lotti = (await session.execute(select(CouponLotto).order_by(CouponLotto.created_at.desc()))).scalars().all()
    conti = await _conti_lotti(session)
    esempi = {
        c.id: c for c in (await session.execute(
            select(Coupon).where(Coupon.id.in_([v[2] for v in conti.values()]))
        )).scalars()
    } if conti else {}
    return [
        lotto_json(l, *conti.get(l.id, (0, 0, None))[:2], esempio=esempi.get(conti.get(l.id, (0, 0, None))[2]))
        for l in lotti
    ]


@router.post("/coupon-lotti", status_code=201)
async def crea_lotto(payload: LottoIn, request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Genera i codici del lotto in una volta (al massimo `MAX_LOTTO`)."""
    lotto = CouponLotto(
        prefisso=payload.prefisso, campagna=_campagna(payload.campagna), quantita=payload.quantita,
        description=(payload.description or "").strip() or None, created_by=user.id,
    )
    session.add(lotto)
    await session.flush()
    modello = {
        "tipo": payload.tipo, "valore": payload.valore, "piani": await _controlla_piani(session, payload.piani),
        "solo_primo_acquisto": payload.solo_primo_acquisto, "valido_dal": payload.valido_dal,
        "valido_fino": payload.valido_fino, "durata": payload.durata, "periodi": payload.periodi,
        "cumulabile": payload.cumulabile, "attivo": True,
    }
    codici = await offerte.genera_lotto(session, lotto, modello)
    await AuditRepository(session).record(
        action="coupon.batch", actor_id=user.id, target_type="coupon_lotto", target_id=str(lotto.id),
        after={"prefisso": lotto.prefisso, "campagna": lotto.campagna, "quantita": lotto.quantita, **{
            k: v for k, v in modello.items() if k not in ("valido_dal", "valido_fino")
        }}, ip=_ip(request),
    )
    await session.commit()
    return lotto_json(lotto, 0, len(codici), esempio=codici[0] if codici else None)


class LottoMod(BaseModel):
    attivo: bool


@router.patch("/coupon-lotti/{lotto_id}")
async def attiva_lotto(
    lotto_id: int, payload: LottoMod, request: Request, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Disattiva (o riattiva) tutti i codici di un lotto in una volta: quelli usati restano nel resoconto."""
    lotto = await session.get(CouponLotto, lotto_id)
    if lotto is None:
        raise HTTPException(status_code=404, detail="Lotto non trovato")
    await session.execute(update(Coupon).where(Coupon.lotto_id == lotto.id).values(attivo=payload.attivo))
    await AuditRepository(session).record(
        action="coupon.batch_update", actor_id=user.id, target_type="coupon_lotto", target_id=str(lotto.id),
        after={"attivo": payload.attivo}, ip=_ip(request),
    )
    await session.commit()
    usati, attivi, _ = (await _conti_lotti(session)).get(lotto.id, (0, 0, None))
    return lotto_json(lotto, usati, attivi)


@router.get("/coupon-lotti/{lotto_id}/csv")
async def esporta_lotto(lotto_id: int, request: Request, user: CurrentUser, session: DbSession) -> Response:
    """I codici del lotto in CSV (UTF-8 con BOM, così Excel legge gli accenti): codice, stato, usato il, link."""
    import csv
    import io

    lotto = await session.get(CouponLotto, lotto_id)
    if lotto is None:
        raise HTTPException(status_code=404, detail="Lotto non trovato")
    usi = dict((await session.execute(
        select(CouponRedemption.coupon_id, func.min(CouponRedemption.created_at))
        .join(Coupon, Coupon.id == CouponRedemption.coupon_id)
        .where(Coupon.lotto_id == lotto.id, CouponRedemption.rinnovo.is_(False))
        .group_by(CouponRedemption.coupon_id)
    )).all())
    codici = (await session.execute(select(Coupon).where(Coupon.lotto_id == lotto.id).order_by(Coupon.code))).scalars()
    buffer = io.StringIO()
    scrittore = csv.writer(buffer, lineterminator="\r\n")
    scrittore.writerow(["codice", "campagna", "stato", "usato_il", "link"])
    for c in codici:
        stato = "usato" if c.riscatti > 0 else ("attivo" if c.attivo else "disattivato")
        quando = usi.get(c.id)
        scrittore.writerow([
            c.code, lotto.campagna or "", stato, quando.isoformat() if quando else "",
            link_coupon(c.code)["en"] if c.tipo != "crediti" else "",
        ])
    await AuditRepository(session).record(
        action="coupon.batch_export", actor_id=user.id, target_type="coupon_lotto", target_id=str(lotto.id),
        ip=_ip(request),
    )
    await session.commit()
    nome = f"coupon-{lotto.prefisso.lower()}-{lotto.id}.csv"
    return Response(
        content="﻿" + buffer.getvalue(), media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.get("/coupon-campagne")
async def resoconto_campagne(session: DbSession) -> Dict[str, Any]:
    """Il resoconto per campagna: riscatti, incasso lordo, sconto concesso, nuovi utenti, conversioni da prova."""
    righe = await resoconto_coupon.per_campagna(session)
    totale: Dict[str, int] = {}
    for riga in righe:
        for k, v in riga.items():
            if isinstance(v, int) and not isinstance(v, bool):
                totale[k] = totale.get(k, 0) + v
    return {"campagne": righe, "totale": totale}


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
    await registro.accredita(user_id, int(crediti), reason="omaggio", note=nota[:500], canale="console")
    dopo = await registro.saldo(user_id)
    await AuditRepository(session).record(
        action="credits.gift", actor_id=user.id, target_type="user", target_id=str(user_id),
        before={"saldo": prima}, after={"saldo": dopo, "crediti": crediti, "origine": origine, "nota": payload.nota},
        ip=_ip(request),
    )
    await session.commit()
    return {"saldo": dopo, "crediti": crediti}
