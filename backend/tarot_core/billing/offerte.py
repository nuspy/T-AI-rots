"""Le offerte commerciali: coupon di sconto, codici regalo e regali di crediti.

I **piani** (abbonamenti e pacchetti) sono già in `plans.py`; qui stanno i modi di venderli a meno o di regalarli.

Un coupon ha uno di tre tipi:

- `percentuale` e `importo` **scontano un pagamento**. Lo sconto vale sul primo pagamento: un abbonamento si rinnova al
  prezzo di listino. Un abbonamento non si può azzerare (un rinnovo a prezzo pieno sarebbe una sorpresa, e senza un
  primo pagamento non c'è un cliente presso il fornitore); un pacchetto sì: a zero si accredita subito, senza
  passare dal fornitore.
- `crediti` è un **codice regalo**: chi lo riscatta riceve crediti, senza pagare.

Le regole si controllano qui e in un posto solo, per l'anteprima del prezzo e per il pagamento: se fossero due, prima o
poi l'anteprima direbbe una cosa e il pagamento un'altra.

L'uso si **registra a pagamento avvenuto** (`registra_uso`), non all'apertura del checkout: chi apre la pagina e poi la
chiude non ha consumato un uso. Due pagamenti simultanei dell'ultimo uso disponibile possono passare entrambi: è una
tolleranza dichiarata, e il tetto si ricontrolla a ogni nuovo checkout.
"""
from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.billing_models import Coupon, CouponRedemption, PaymentCheckout, Plan

CODICE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{2,39}$")
SLUG_PIANO = re.compile(r"^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$")

#: Senza I, O, 0, 1: un codice detto a voce o letto da uno schermo non si confonde.
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

#: Perché un coupon non vale, con il motivo che il frontend traduce e la frase per chi chiama l'API.
MESSAGGI = {
    "coupon_sconosciuto": "Il codice non esiste.",
    "coupon_non_attivo": "Il codice non è più attivo.",
    "coupon_non_ancora_valido": "Il codice non è ancora valido.",
    "coupon_scaduto": "Il codice è scaduto.",
    "coupon_esaurito": "Il codice ha esaurito i suoi usi.",
    "coupon_gia_usato": "Hai già usato questo codice.",
    "coupon_non_per_questo_piano": "Il codice non vale per questa offerta.",
    "coupon_solo_primo_acquisto": "Il codice vale solo sul primo acquisto.",
    "coupon_azzera_abbonamento": "Il codice azzererebbe un abbonamento: non si può applicare.",
    "coupon_sconto": "Questo è uno sconto: si usa nell'acquisto, non si riscatta.",
    "coupon_regalo": "Questo è un codice regalo: si riscatta dal profilo, non si usa nell'acquisto.",
}


class CouponNonValido(Exception):
    """Il codice non si può usare. `motivo` è stabile (lo traduce il frontend), `args[0]` è la frase in italiano."""

    def __init__(self, motivo: str) -> None:
        super().__init__(MESSAGGI[motivo])
        self.motivo = motivo


def normalizza_codice(testo: Optional[str]) -> str:
    """Maiuscolo e senza spazi: chi lo scrive non deve indovinare le maiuscole."""
    return re.sub(r"\s+", "", testo or "").upper()


def codice_nuovo(prefisso: str = "") -> str:
    """Un codice casuale leggibile, da 8 caratteri (con un prefisso facoltativo: `NATALE-K7Q2XM4B`)."""
    corpo = "".join(secrets.choice(ALFABETO) for _ in range(8))
    return f"{normalizza_codice(prefisso)}-{corpo}" if prefisso else corpo


@dataclass
class Sconto:
    coupon: Coupon
    listino: int
    sconto: int
    finale: int


async def trova(session: AsyncSession, codice: str, *, per_aggiornamento: bool = False) -> Optional[Coupon]:
    q = select(Coupon).where(Coupon.code == normalizza_codice(codice))
    if per_aggiornamento:
        q = q.with_for_update()
    return (await session.execute(q)).scalar_one_or_none()


async def _verifica_comune(session: AsyncSession, coupon: Coupon, user_id: int, adesso: datetime) -> None:
    if not coupon.attivo:
        raise CouponNonValido("coupon_non_attivo")
    if coupon.valido_dal and adesso < coupon.valido_dal:
        raise CouponNonValido("coupon_non_ancora_valido")
    if coupon.valido_fino and adesso > coupon.valido_fino:
        raise CouponNonValido("coupon_scaduto")
    if coupon.max_riscatti is not None and coupon.riscatti >= coupon.max_riscatti:
        raise CouponNonValido("coupon_esaurito")
    usi = int(await session.scalar(
        select(func.count()).select_from(CouponRedemption)
        .where(CouponRedemption.coupon_id == coupon.id, CouponRedemption.user_id == user_id)
    ) or 0)
    if usi >= coupon.max_per_utente:
        raise CouponNonValido("coupon_gia_usato")


async def ha_gia_comprato(session: AsyncSession, user_id: int) -> bool:
    return bool(await session.scalar(
        select(func.count()).select_from(PaymentCheckout)
        .where(PaymentCheckout.user_id == user_id, PaymentCheckout.status == "pagato", PaymentCheckout.importo > 0)
    ))


def listino_di(piano: Plan, annuale: bool) -> int:
    return piano.price_yearly if annuale and not piano.pacchetto else piano.price_monthly


async def valuta(
    session: AsyncSession, user_id: int, codice: str, piano: Plan, *, annuale: bool = False,
    adesso: Optional[datetime] = None,
) -> Sconto:
    """Lo sconto che il coupon dà su un piano, o `CouponNonValido`. Non scrive niente."""
    adesso = adesso or utcnow()
    coupon = await trova(session, codice)
    if coupon is None:
        raise CouponNonValido("coupon_sconosciuto")
    if coupon.tipo == "crediti":
        raise CouponNonValido("coupon_regalo")
    await _verifica_comune(session, coupon, user_id, adesso)
    if coupon.piani and piano.slug not in coupon.piani:
        raise CouponNonValido("coupon_non_per_questo_piano")
    if coupon.solo_primo_acquisto and await ha_gia_comprato(session, user_id):
        raise CouponNonValido("coupon_solo_primo_acquisto")

    listino = listino_di(piano, annuale)
    if coupon.tipo == "percentuale":
        sconto = (listino * coupon.valore + 50) // 100        # mezzi centesimi per eccesso, in interi
    else:
        sconto = min(coupon.valore, listino)
    finale = listino - sconto
    if finale <= 0 and not piano.pacchetto:
        raise CouponNonValido("coupon_azzera_abbonamento")
    return Sconto(coupon=coupon, listino=listino, sconto=sconto, finale=max(finale, 0))


async def registra_uso(session: AsyncSession, checkout: PaymentCheckout) -> None:
    """Conta l'uso di un coupon a pagamento avvenuto (o a pacchetto regalato). Idempotente per checkout."""
    if checkout.coupon_id is None:
        return
    gia = await session.scalar(
        select(func.count()).select_from(CouponRedemption).where(CouponRedemption.checkout_id == checkout.id)
    )
    if gia:
        return
    session.add(CouponRedemption(
        coupon_id=checkout.coupon_id, user_id=checkout.user_id, checkout_id=checkout.id, sconto=checkout.sconto,
    ))
    await session.execute(update(Coupon).where(Coupon.id == checkout.coupon_id).values(riscatti=Coupon.riscatti + 1))


async def riscatta_regalo(session: AsyncSession, user_id: int, codice: str) -> tuple[Coupon, int]:
    """Riscatta un codice regalo: accredita i crediti. Restituisce il coupon e i crediti dati."""
    from .credits import RegistroCrediti

    coupon = await trova(session, codice, per_aggiornamento=True)    # la riga si blocca: due riscatti non si sovrappongono
    if coupon is None:
        raise CouponNonValido("coupon_sconosciuto")
    if coupon.tipo != "crediti":
        raise CouponNonValido("coupon_sconto")
    await _verifica_comune(session, coupon, user_id, utcnow())
    await RegistroCrediti(session).accredita(user_id, coupon.valore, reason="omaggio", note=f"codice {coupon.code}")
    session.add(CouponRedemption(coupon_id=coupon.id, user_id=user_id, crediti=coupon.valore))
    coupon.riscatti += 1
    await session.flush()
    return coupon, coupon.valore
