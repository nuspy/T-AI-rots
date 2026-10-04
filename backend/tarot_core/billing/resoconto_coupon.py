"""Il resoconto dei coupon (v9, Fase 2d): per coupon e per campagna, quanto hanno reso.

Le cifre vengono dagli usi (`coupon_redemptions`), che citano il pagamento (`payment_checkouts`) e, per un
abbonamento, l'abbonamento (`subscriptions`):

| cifra | da dove |
|---|---|
| **riscatti** | gli usi del codice (non i rinnovi scontati) |
| **incasso lordo** | quanto è stato pagato nei pagamenti scontati dal coupon, rinnovi compresi (centesimi) |
| **sconto concesso** | ciò che il coupon ha tolto **in più** rispetto agli sconti che ci sarebbero stati comunque (il rinnovo automatico, la prova): è il costo vero della campagna |
| **crediti regalati** | i codici regalo |
| **nuovi utenti** | chi l'ha usato con un account nato dopo il coupon: arrivato, verosimilmente, con la campagna |
| **prove avviate** / **conversioni da prova** | le prove gratuite partite col codice, e quelle diventate un abbonamento pagato |

Nessuna cifra si ricostruisce da un contatore: si sommano le righe, come il registro dei crediti.
"""
from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import and_, case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.billing_models import Coupon, CouponRedemption, PaymentCheckout, Subscription
from ..domain.models import User

#: L'etichetta dei coupon senza campagna, nel resoconto per campagna.
SENZA_CAMPAGNA = ""


def _vuoto() -> Dict[str, int]:
    return {
        "coupon": 0, "riscatti": 0, "incasso_lordo": 0, "sconto_concesso": 0, "crediti_regalati": 0,
        "nuovi_utenti": 0, "prove": 0, "conversioni_da_prova": 0, "rinnovi_scontati": 0,
    }


async def _metriche(session: AsyncSession, chiave, filtro=None) -> Dict[Any, Dict[str, int]]:
    """Le cifre raggruppate per `chiave` (l'id del coupon o la sua campagna)."""
    uso = CouponRedemption.rinnovo.is_(False)
    nuovo = and_(uso, User.created_at >= Coupon.created_at)
    q = (
        select(
            chiave.label("k"),
            func.count().filter(uso).label("riscatti"),
            func.count().filter(CouponRedemption.rinnovo.is_(True)).label("rinnovi_scontati"),
            func.coalesce(func.sum(CouponRedemption.importo), 0).label("incasso_lordo"),
            func.coalesce(func.sum(CouponRedemption.sconto), 0).label("sconto_concesso"),
            func.coalesce(func.sum(CouponRedemption.crediti), 0).label("crediti_regalati"),
            func.count(distinct(case((nuovo, CouponRedemption.user_id)))).label("nuovi_utenti"),
            func.count().filter(and_(uso, PaymentCheckout.prova.is_(True))).label("prove"),
            func.count(distinct(case((
                and_(CouponRedemption.rinnovo.is_(True), Subscription.prova.is_(True)), CouponRedemption.subscription_id,
            )))).label("conversioni_da_prova"),
        )
        .select_from(CouponRedemption)
        .join(Coupon, Coupon.id == CouponRedemption.coupon_id)
        .join(User, User.id == CouponRedemption.user_id)
        .outerjoin(PaymentCheckout, PaymentCheckout.id == CouponRedemption.checkout_id)
        .outerjoin(Subscription, Subscription.id == CouponRedemption.subscription_id)
        .group_by(chiave)
    )
    if filtro is not None:
        q = q.where(filtro)
    risultato: Dict[Any, Dict[str, int]] = {}
    for riga in (await session.execute(q)).mappings():
        cifre = {k: int(v or 0) for k, v in riga.items() if k != "k"}
        risultato[riga["k"]] = cifre
    return risultato


async def per_coupon(session: AsyncSession, coupon_id: int) -> Dict[str, int]:
    cifre = (await _metriche(session, Coupon.id, Coupon.id == coupon_id)).get(coupon_id) or _vuoto()
    cifre["coupon"] = 1
    return {**_vuoto(), **cifre}


async def per_campagna(session: AsyncSession) -> List[Dict[str, Any]]:
    """Una riga per campagna (i coupon senza etichetta in una riga a parte), con quanti coupon e lotti ha."""
    etichetta = func.coalesce(Coupon.campagna, SENZA_CAMPAGNA)
    cifre = await _metriche(session, etichetta)
    conti = (await session.execute(
        select(
            etichetta.label("k"), func.count().label("coupon"), func.count(distinct(Coupon.lotto_id)).label("lotti"),
        ).group_by(etichetta)
    )).all()
    righe = []
    for k, coupon, lotti in conti:
        righe.append({"campagna": k or None, **_vuoto(), **cifre.get(k, {}), "coupon": int(coupon), "lotti": int(lotti)})
    righe.sort(key=lambda r: (r["campagna"] is None, -r["incasso_lordo"], -r["riscatti"], r["campagna"] or ""))
    return righe


async def per_tutti_i_coupon(session: AsyncSession, ids: List[int]) -> Dict[int, Dict[str, int]]:
    """Le cifre di più coupon in una query (l'elenco della console)."""
    if not ids:
        return {}
    cifre = await _metriche(session, Coupon.id, Coupon.id.in_(ids))
    return {i: {**_vuoto(), **cifre.get(i, {}), "coupon": 1} for i in ids}
