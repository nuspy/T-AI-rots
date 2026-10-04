"""Le offerte commerciali: coupon di sconto, codici regalo e regali di crediti.

I **piani** (abbonamenti e pacchetti) sono già in `plans.py`; qui stanno i modi di venderli a meno o di regalarli.

Un coupon ha uno di tre tipi:

- `percentuale` e `importo` **scontano un pagamento**. Un abbonamento non si può azzerare (un rinnovo a prezzo pieno
  sarebbe una sorpresa, e senza un primo pagamento non c'è un cliente presso il fornitore); un pacchetto sì: a zero
  si accredita subito, senza passare dal fornitore.
- `crediti` è un **codice regalo**: chi lo riscatta riceve crediti, senza pagare.

**Durata (Fase 2d).** Su un abbonamento lo sconto vale sul primo pagamento (`una_volta`), sui primi N (`periodi`, il
primo compreso: «−30% per 3 mesi») o su tutti (`sempre`). Sui rinnovi continua con il meccanismo della Fase 2b: lo
sconto di ogni rinnovo è un importo fisso presso il fornitore (`Subscription.sconto_ricorrente`, su Stripe il coupon
«per sempre» `tarots_<motivo>_<centesimi>_eur`), e quando i periodi del coupon finiscono si torna allo sconto del
solo rinnovo automatico (`dopo_rinnovo`). Un cambio di piano chiude lo sconto del coupon.

**Cumulo (Fase 2d), deciso dall'operatore coupon per coupon.** Su ogni pagamento gli sconti sono, sul listino L:

    B = lo sconto del rinnovo automatico (o della prova, per sempre)       percentuale di L, al centesimo
    C = lo sconto del coupon (finché dura)                                 percentuale di L al centesimo, o l'importo
    cumulabile:     sconto = B + C          (prima il rinnovo, poi il coupon, entrambi sul listino)
    non cumulabile: sconto = max(B, C)      (a pari merito vince B, e il codice non si consuma)

Così chi usa un coupon non paga mai più di chi non lo usa, e il pagamento costa al centesimo ciò che la pagina
mostra (`Composizione`). Un upgrade toglie poi il suo valore residuo (`billing/abbonamenti.py`).

Le regole si controllano qui e in un posto solo, per l'anteprima del prezzo e per il pagamento: se fossero due, prima o
poi l'anteprima direbbe una cosa e il pagamento un'altra.

L'uso si **registra a pagamento avvenuto** (`registra_uso`), non all'apertura del checkout: chi apre la pagina e poi la
chiude non ha consumato un uso. Due pagamenti simultanei dell'ultimo uso disponibile possono passare entrambi: è una
tolleranza dichiarata, e il tetto si ricontrolla a ogni nuovo checkout.
"""
from __future__ import annotations

import logging
import re
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.billing_models import Coupon, CouponLotto, CouponRedemption, PaymentCheckout, Plan, Subscription

logger = logging.getLogger(__name__)

CODICE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{2,39}$")
#: Il prefisso di un lotto: corto, perché il codice intero (prefisso, trattino, otto caratteri) resta sotto i 40.
PREFISSO = re.compile(r"^[A-Z0-9][A-Z0-9_]{1,19}$")
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
    # Non è un rifiuto: il codice è valido, ma un altro sconto è più alto e i due non si sommano (Fase 2d).
    "coupon_non_cumulabile": "Il codice non si somma agli altri sconti, e lo sconto che hai già è più alto.",
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


async def _verifica_comune(session: AsyncSession, coupon: Coupon, user_id: Optional[int], adesso: datetime) -> None:
    """Le regole di ogni codice. Senza `user_id` (un visitatore non ancora entrato) si saltano quelle della persona:
    le ricontrolla il pagamento, che chiede sempre l'accesso."""
    if not coupon.attivo:
        raise CouponNonValido("coupon_non_attivo")
    if coupon.valido_dal and adesso < coupon.valido_dal:
        raise CouponNonValido("coupon_non_ancora_valido")
    if coupon.valido_fino and adesso > coupon.valido_fino:
        raise CouponNonValido("coupon_scaduto")
    if coupon.max_riscatti is not None and coupon.riscatti >= coupon.max_riscatti:
        raise CouponNonValido("coupon_esaurito")
    if user_id is None:
        return
    usi = int(await session.scalar(
        select(func.count()).select_from(CouponRedemption)
        .where(
            CouponRedemption.coupon_id == coupon.id, CouponRedemption.user_id == user_id,
            CouponRedemption.rinnovo.is_(False),          # lo sconto di un rinnovo non è un uso del codice
        )
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


def sconto_su(coupon: Coupon, listino: int) -> int:
    """Quanto sconta il coupon su un listino (centesimi): la percentuale al centesimo (mezzo per eccesso, in interi,
    come lo sconto del rinnovo), o l'importo, mai oltre il listino."""
    if coupon.tipo == "percentuale":
        return (int(listino) * coupon.valore + 50) // 100
    return min(coupon.valore, int(listino))


async def verifica_sconto(
    session: AsyncSession, user_id: Optional[int], codice: str, *, adesso: Optional[datetime] = None,
) -> Coupon:
    """Il coupon di sconto, se vale in generale (e per la persona, se c'è), o `CouponNonValido`. Non scrive niente."""
    adesso = adesso or utcnow()
    coupon = await trova(session, codice)
    if coupon is None:
        raise CouponNonValido("coupon_sconosciuto")
    if coupon.tipo == "crediti":
        raise CouponNonValido("coupon_regalo")
    await _verifica_comune(session, coupon, user_id, adesso)
    if coupon.solo_primo_acquisto and user_id is not None and await ha_gia_comprato(session, user_id):
        raise CouponNonValido("coupon_solo_primo_acquisto")
    return coupon


def sconto_piano(coupon: Coupon, piano: Plan, annuale: bool) -> Sconto:
    """Lo sconto del coupon su un piano, o `CouponNonValido` se non vale per quel piano."""
    if coupon.piani and piano.slug not in coupon.piani:
        raise CouponNonValido("coupon_non_per_questo_piano")
    listino = listino_di(piano, annuale)
    sconto = sconto_su(coupon, listino)
    finale = listino - sconto
    if finale <= 0 and not piano.pacchetto:
        raise CouponNonValido("coupon_azzera_abbonamento")
    return Sconto(coupon=coupon, listino=listino, sconto=sconto, finale=max(finale, 0))


async def valuta(
    session: AsyncSession, user_id: Optional[int], codice: str, piano: Plan, *, annuale: bool = False,
    adesso: Optional[datetime] = None,
) -> Sconto:
    """Lo sconto che il coupon dà su un piano, o `CouponNonValido`. Non scrive niente. Senza `user_id` non si
    controllano le regole della persona (già usato, solo primo acquisto)."""
    coupon = await verifica_sconto(session, user_id, codice, adesso=adesso)
    return sconto_piano(coupon, piano, annuale)


def coupon_pubblico(coupon: Coupon) -> Dict[str, Any]:
    """Ciò che il sito mostra di un coupon: com'è fatto, quanto dura, se si somma, quando scade."""
    return {
        "codice": coupon.code, "tipo": coupon.tipo, "valore": coupon.valore, "durata": coupon.durata,
        "periodi": coupon.periodi, "cumulabile": coupon.cumulabile, "piani": list(coupon.piani or []),
        "valido_fino": coupon.valido_fino.isoformat() if coupon.valido_fino else None,
    }


def preventivi(
    coupon: Coupon, piani: list, *, percento_rinnovo: int, percento_prova: int, con_prova: bool,
) -> list:
    """Il prezzo con il coupon di ogni offerta in vendita, in ogni variante che la pagina dei prezzi mostra:
    pacchetto; abbonamento mensile e annuale, con e senza rinnovo automatico; la prova (annuale). Un'offerta per cui
    il codice non vale dice perché (`motivo`). Sono i conti che il pagamento rifarà, identici."""
    from .abbonamenti import percentuale

    righe = []
    for piano in piani:
        if piano.price_monthly <= 0 and piano.price_yearly <= 0:
            continue
        varianti = [(False, False, False)] if piano.pacchetto else [
            (annuale, rinnovo, False) for annuale in (False, True) for rinnovo in (True, False)
            if not annuale or piano.price_yearly > 0
        ] + ([(True, False, True)] if con_prova and piano.price_yearly > 0 else [])
        for annuale, rinnovo, prova in varianti:
            voce: Dict[str, Any] = {"piano": piano.slug, "annuale": annuale, "rinnovo": rinnovo, "prova": prova}
            try:
                valutato = sconto_piano(coupon, piano, annuale)
                percento = percento_prova if prova else (percento_rinnovo if rinnovo else 0)
                base = percentuale(valutato.listino, percento) if not piano.pacchetto else 0
                voce.update(componi(
                    valutato.listino, base=base, valutato=valutato, abbonamento=not piano.pacchetto,
                    rinnovo=rinnovo, prova=prova,
                ).to_dict())
            except CouponNonValido as exc:
                voce["motivo"] = exc.motivo
            righe.append(voce)
    return righe


# ---- il cumulo con il rinnovo automatico e la prova (Fase 2d) --------------------------------------------------------


def combina(base: int, coupon: int, cumulabile: bool) -> int:
    """Lo sconto di un pagamento: la somma, o il più alto dei due (il più alto per chi paga)."""
    return base + coupon if cumulabile else max(base, coupon)


def rinnovi_del_coupon(coupon: Coupon, *, prova: bool) -> Optional[int]:
    """Quanti rinnovi avranno lo sconto del coupon dopo il primo pagamento: `None` = tutti. Con una prova il primo
    pagamento è la conversione, che è già un rinnovo: il coupon «una volta» sconta quella."""
    if coupon.durata == "sempre":
        return None
    pagamenti = int(coupon.periodi or 1) if coupon.durata == "periodi" else 1
    return pagamenti if prova else pagamenti - 1


@dataclass
class Composizione:
    """Il prezzo di un pagamento con tutti i suoi sconti, e i rinnovi che ne seguono. La stessa per l'anteprima e per
    il pagamento: l'importo che Stripe addebita è `importo` (meno un eventuale conguaglio)."""

    listino: int
    #: Lo sconto del rinnovo automatico o della prova (B) e quello del coupon (C), entrambi sul listino.
    base: int
    sconto_coupon: int
    cumulabile: bool
    #: `coupon` (vale il coupon), `entrambi` (si sommano), `rinnovo` o `prova` (vale lo sconto che c'era già), None.
    vince: Optional[str]
    #: Il coupon si usa (si consuma un uso e resta sull'acquisto).
    applicato: bool
    #: Lo sconto di adesso e quanto si paga adesso (con la prova, niente adesso).
    sconto: int
    importo: int
    #: Il primo rinnovo: con quale sconto parte, e quanti rinnovi avranno ancora quello del coupon (None = tutti).
    sconto_ricorrente: int
    rinnovi_coupon: Optional[int]
    prova: bool = False
    #: Il coupon (se ce n'è uno valido, anche non applicato) e lo `Sconto` da passare al pagamento.
    valutato: Optional[Sconto] = None

    @property
    def extra_coupon(self) -> int:
        """Ciò che il coupon aggiunge allo sconto che ci sarebbe comunque: è la parte che scrive il checkout
        (`PaymentCheckout.sconto`) e il «concesso» del resoconto."""
        return max(0, self.sconto - self.base) if self.applicato and not self.prova else 0

    def sconto_per_pagamento(self) -> Optional[Sconto]:
        """Lo `Sconto` che `GestorePagamenti.apri` vuole: il solo pezzo del coupon, sopra lo sconto del rinnovo."""
        if not self.applicato or self.valutato is None:
            return None
        return Sconto(
            coupon=self.valutato.coupon, listino=self.listino, sconto=self.extra_coupon, finale=self.importo,
        )

    def to_dict(self) -> Dict[str, Any]:
        c = self.valutato.coupon if self.valutato is not None else None
        return {
            "listino": self.listino, "sconto_base": self.base, "sconto_coupon": self.sconto_coupon,
            "sconto": self.sconto, "importo": self.importo, "risparmio": self.listino - self.importo if not self.prova else self.sconto,
            "vince": self.vince, "applicato": self.applicato, "cumulabile": self.cumulabile,
            "prova": self.prova, "sconto_ricorrente": self.sconto_ricorrente, "rinnovi_coupon": self.rinnovi_coupon,
            "nota": "coupon_non_cumulabile" if c is not None and not self.applicato else None,
        }


def componi(
    listino: int, *, base: int = 0, valutato: Optional[Sconto] = None, abbonamento: bool = True,
    rinnovo: bool = True, prova: bool = False,
) -> Composizione:
    """Mette insieme lo sconto del rinnovo automatico o della prova (`base`) e quello del coupon, secondo il cumulo.

    Un pacchetto ha solo il coupon. Senza rinnovo automatico non ci sono rinnovi, quindi niente sconto ricorrente
    (si riaccende dal profilo, e allora riparte con lo sconto del rinnovo e quel che resta del coupon). Solleva
    `CouponNonValido("coupon_azzera_abbonamento")` se il primo pagamento o i rinnovi di un abbonamento andrebbero a
    zero."""
    coupon = valutato.coupon if valutato is not None else None
    if not abbonamento:
        base, rinnovo, prova = 0, False, False
    c = sconto_su(coupon, listino) if coupon is not None else 0
    cumulabile = bool(coupon.cumulabile) if coupon is not None else False
    # Il coupon si usa se aggiunge qualcosa: cumulabile, o più alto dello sconto che c'è già (a pari merito, no).
    applicato = coupon is not None and c > 0 and (cumulabile or c > base)
    sconto = combina(base, c if applicato else 0, cumulabile)
    rimasti = rinnovi_del_coupon(coupon, prova=prova) if applicato and abbonamento else 0
    coupon_ancora = rimasti is None or rimasti > 0
    ricorrente = combina(base, c if applicato and coupon_ancora else 0, cumulabile) if (rinnovo or prova) else 0
    if applicato:
        vince = "entrambi" if cumulabile and base > 0 else "coupon"
    elif base > 0:
        vince = "prova" if prova else "rinnovo"
    else:
        vince = None
    importo = 0 if prova else max(0, listino - sconto)
    if abbonamento and (listino - (0 if prova else sconto) <= 0 or (rinnovo or prova) and listino - ricorrente <= 0):
        raise CouponNonValido("coupon_azzera_abbonamento")
    return Composizione(
        listino=listino, base=base, sconto_coupon=c, cumulabile=cumulabile, vince=vince, applicato=applicato,
        sconto=sconto, importo=importo, sconto_ricorrente=ricorrente, rinnovi_coupon=rimasti if applicato else None,
        prova=prova, valutato=valutato,
    )


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
        importo=checkout.importo,
    ))
    await session.execute(update(Coupon).where(Coupon.id == checkout.coupon_id).values(riscatti=Coupon.riscatti + 1))


# ---- il coupon sui rinnovi (Fase 2d) -----------------------------------------------------------------------------


def coupon_attivo(abbonamento: Subscription) -> bool:
    """Lo sconto del coupon vale ancora sul prossimo rinnovo?"""
    if abbonamento.coupon_id is None:
        return False
    return abbonamento.coupon_rinnovi_rimasti is None or abbonamento.coupon_rinnovi_rimasti > 0


def base_di(abbonamento: Subscription) -> int:
    """Lo sconto del rinnovo automatico o della prova, senza coupon (le righe di prima della 2d non lo distinguono)."""
    return abbonamento.sconto_ricorrente if abbonamento.sconto_base is None else abbonamento.sconto_base


def ricalcola_sconto(abbonamento: Subscription) -> int:
    """Lo sconto effettivo del prossimo rinnovo, dalla base e dal coupon (se dura ancora), secondo il cumulo."""
    cumulabile = bool(abbonamento.coupon.cumulabile) if abbonamento.coupon is not None else False
    coupon = abbonamento.sconto_coupon if coupon_attivo(abbonamento) else 0
    return combina(base_di(abbonamento), coupon, cumulabile) if abbonamento.rinnovo_automatico else 0


def motivo_sconto(abbonamento: Subscription) -> str:
    """Il nome del coupon «per sempre» presso il fornitore: `sconto` se dentro c'è il coupon, se no `prova` o
    `rinnovo` come nella 2b (`tarots_<motivo>_<centesimi>_eur`)."""
    if coupon_attivo(abbonamento) and abbonamento.sconto_ricorrente != base_di(abbonamento):
        return "sconto"
    return "prova" if abbonamento.prova else "rinnovo"


async def lega_abbonamento(session: AsyncSession, abbonamento: Subscription, checkout: PaymentCheckout) -> None:
    """A pagamento avvenuto: il coupon che continua sui rinnovi resta sull'abbonamento, con i rinnovi che gli restano;
    l'uso registrato da `registra_uso` prende l'abbonamento (il resoconto conta le conversioni delle prove)."""
    abbonamento.sconto_base = checkout.sconto_rinnovo if (checkout.rinnovo or checkout.prova) else 0
    if checkout.coupon_id is None:
        return
    coupon = await session.get(Coupon, checkout.coupon_id)
    if coupon is None:
        return
    await session.execute(
        update(CouponRedemption)
        .where(CouponRedemption.checkout_id == checkout.id, CouponRedemption.rinnovo.is_(False))
        .values(subscription_id=abbonamento.id)
    )
    rimasti = rinnovi_del_coupon(coupon, prova=checkout.prova)
    if rimasti is not None and rimasti <= 0:
        return
    listino = checkout.listino if checkout.listino is not None else checkout.importo + checkout.sconto
    abbonamento.coupon_id = coupon.id
    abbonamento.coupon = coupon
    abbonamento.sconto_coupon = sconto_su(coupon, listino)
    abbonamento.coupon_rinnovi_rimasti = rimasti


async def dopo_rinnovo(
    session: AsyncSession, abbonamento: Subscription, fornitore: Any, *, riferimento: str, sconto_pagato: int,
) -> None:
    """Un rinnovo pagato: se aveva lo sconto del coupon lo si scrive nel resoconto (una riga per rinnovo), si conta un
    rinnovo in meno, e quando finiscono si torna allo sconto del solo rinnovo automatico — anche presso il
    fornitore, così il rinnovo dopo costa ciò che il profilo mostra. Mai un errore che fermi il rinnovo: il periodo è
    già pagato."""
    if not coupon_attivo(abbonamento):
        return
    base = base_di(abbonamento)
    gia = await session.scalar(
        select(func.count()).select_from(CouponRedemption).where(
            CouponRedemption.subscription_id == abbonamento.id, CouponRedemption.riferimento == riferimento,
            CouponRedemption.rinnovo.is_(True),
        )
    )
    if gia:
        return
    session.add(CouponRedemption(
        coupon_id=abbonamento.coupon_id, user_id=abbonamento.user_id, subscription_id=abbonamento.id,
        rinnovo=True, riferimento=riferimento, sconto=max(0, sconto_pagato - base),
        importo=abbonamento.importo_periodo or 0,
    ))
    if abbonamento.coupon_rinnovi_rimasti is None:
        await session.flush()
        return
    abbonamento.coupon_rinnovi_rimasti -= 1
    nuovo = ricalcola_sconto(abbonamento)
    if nuovo != abbonamento.sconto_ricorrente:
        abbonamento.sconto_ricorrente = nuovo
        esterno = abbonamento.external_id if abbonamento.provider == getattr(fornitore, "name", None) else None
        applica = getattr(fornitore, "applica_sconto_ricorrente", None)
        if esterno and applica is not None:
            from .pagamenti import PagamentiNonDisponibili

            try:
                await applica(esterno, nuovo, abbonamento.plan.currency, motivo=motivo_sconto(abbonamento))
            except PagamentiNonDisponibili:
                # Il periodo è pagato: lo sconto presso il fornitore si riallinea a mano (console → Abbonamenti).
                logger.error("Sconto del coupon non tolto presso %s per %s", abbonamento.provider, abbonamento.id)
    await session.flush()


async def riscatta_regalo(session: AsyncSession, user_id: int, codice: str) -> tuple[Coupon, int]:
    """Riscatta un codice regalo: accredita i crediti. Restituisce il coupon e i crediti dati."""
    from .credits import RegistroCrediti

    coupon = await trova(session, codice, per_aggiornamento=True)    # la riga si blocca: due riscatti non si sovrappongono
    if coupon is None:
        raise CouponNonValido("coupon_sconosciuto")
    if coupon.tipo != "crediti":
        raise CouponNonValido("coupon_sconto")
    await _verifica_comune(session, coupon, user_id, utcnow())
    await RegistroCrediti(session).accredita(
        user_id, coupon.valore, reason="omaggio", note=f"codice {coupon.code}", canale="web",
    )
    session.add(CouponRedemption(coupon_id=coupon.id, user_id=user_id, crediti=coupon.valore))
    coupon.riscatti += 1
    await session.flush()
    return coupon, coupon.valore


# ---- lotti di codici monouso (Fase 2d) -----------------------------------------------------------------------------

#: Quanti codici al massimo in un lotto: oltre, l'esportazione e la console diventano pesanti (si fanno due lotti).
MAX_LOTTO = 5000


async def genera_lotto(
    session: AsyncSession, lotto: "CouponLotto", modello: Dict[str, Any],
) -> list:
    """I codici di un lotto: `prefisso-XXXXXXXX`, ognuno un coupon con un uso solo (in tutto e a persona), le regole
    di `modello` e la campagna del lotto. I codici nuovi non collidono fra loro né con quelli che esistono già."""
    prefisso = normalizza_codice(lotto.prefisso)
    nuovi: set = set()
    while len(nuovi) < lotto.quantita:
        mancano = lotto.quantita - len(nuovi)
        candidati = {codice_nuovo(prefisso) for _ in range(mancano)} - nuovi
        esistenti = set((await session.execute(select(Coupon.code).where(Coupon.code.in_(candidati)))).scalars())
        nuovi |= candidati - esistenti
    coupon = [
        Coupon(
            code=codice, lotto_id=lotto.id, campagna=lotto.campagna, description=lotto.description,
            max_riscatti=1, max_per_utente=1, **modello,
        )
        for codice in sorted(nuovi)
    ]
    session.add_all(coupon)
    await session.flush()
    return coupon
