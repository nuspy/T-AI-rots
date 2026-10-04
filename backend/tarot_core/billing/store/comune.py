"""Ciò che Google Play e App Store hanno in comune (v9, Fase 4): dall'acquisto verificato all'accredito.

Un modulo dello store (`google_play.py`, `app_store.py`) verifica l'acquisto presso lo store e lo traduce in una
`Transazione`: un incasso, con il prodotto, l'account che l'ha fatto, lo stato presso lo store. Da lì il percorso è
uno solo, `registra()`:

1. **il prodotto → il piano**, con `prodotti_store` (scritta dalla console «App mobili»). Per Google si prova prima
   `abbonamento:base_plan` e poi l'abbonamento da solo: lo stesso abbonamento di Play ha più base plan (mensile,
   annuale, annuale «prova»), e la console può collegarli a piani diversi;
2. **l'acquisto → l'account**: lo store rimanda firmato il token dell'account (`users.app_account_token`) che l'app
   gli ha passato. Un acquisto con il token di un altro account si rifiuta: un token d'acquisto copiato non accredita;
3. **una riga in `acquisti_store`** per transazione, unica per (piattaforma, transazione);
4. **l'accredito passa da `GestorePagamenti.applica`**, come per Stripe: un checkout (lo stesso registro dei ricavi
   e del resoconto) e un evento con id `gp:<ordine>` / `as:<transazione>`. La verifica dall'app, la notifica dello
   store e la riconciliazione notturna producono lo stesso id: **conta una volta sola**, qualunque arrivi prima;
5. **lo stato dell'abbonamento segue lo store** (`_allinea`): la tolleranza dello store (Google grace period, Apple
   Billing Grace Period) è `in_sospeso` con le letture comprese ancora attive; account hold, billing retry senza
   tolleranza, pausa sono `sospeso`; la scadenza è `scaduto` e si torna al piano gratuito. La disdetta del rinnovo
   fatta nello store manda la stessa email di conferma della Fase 2b.

**Un solo abbonamento attivo per utente, qualunque sia il canale.** Un abbonamento nuovo nello store chiude quello
che l'utente aveva (su Stripe lo disdice presso Stripe; in un altro store non si può: lo dice il registro). Se poi
quell'altro store continua a rinnovarlo, l'incasso si registra e si segna `doppio` senza riaprirlo: la console lo
mostra nella scheda dell'utente, perché qualcuno gli dica di disdirlo.

**Gli acquisti di prova** (`ambiente = sandbox`: i tester, la App Review di Apple) si accreditano anche in
produzione — chi rivede l'app deve vedere i crediti arrivare — ma il checkout porta `sandbox` e i ricavi, le
statistiche degli acquisti e le commissioni di chi ha invitato non li contano.

**Il prezzo.** Google non dice quanto ha pagato l'utente, Apple sì (nella valuta del paese). I ricavi del sito sono
in euro e sul listino: il checkout di un acquisto dello store porta il listino del piano (al netto dello sconto
della prova per il prodotto «prova», zero durante la prova gratuita); il prezzo vero, quando c'è, resta nella riga
dell'acquisto per consultazione.
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.acquisti_store_models import AcquistoStore
from ...domain.app_mobili_models import ProdottoStore
from ...domain.base import utcnow
from ...domain.billing_models import CreditEntry, PaymentCheckout, Plan, Subscription
from ...domain.models import User
from ..abbonamenti import impostazioni, listino_di, percentuale
from ..pagamenti import (
    ABBONAMENTO_AGGIORNATO, ABBONAMENTO_CHIUSO, PAGATO, RINNOVATO, STORNO, STORNO_ANNULLATO, EventoPagamento,
    GestorePagamenti, PagamentiNonDisponibili,
)

logger = logging.getLogger(__name__)

#: Il fornitore (`Subscription.provider`, `credit_ledger.provider`) e il prefisso degli id evento per piattaforma.
FORNITORE = {"android": "google_play", "ios": "app_store"}
PREFISSO = {"android": "gp", "ios": "as"}
NOME_STORE = {"android": "Google Play", "ios": "App Store"}

#: Gli stati di un abbonamento presso lo store, già tradotti nei nostri (più `revocato`, che chiude e storna).
STATI_STORE = ("in_prova", "attivo", "in_sospeso", "sospeso", "scaduto", "revocato")


class ErroreStore(Exception):
    """Un acquisto che non si può registrare: il motivo è stabile, il messaggio si mostra, `http` è la risposta."""

    def __init__(self, motivo: str, messaggio: str, http: int = 422) -> None:
        super().__init__(messaggio)
        self.motivo = motivo
        self.http = http


@dataclass
class Transazione:
    """Un incasso dello store, verificato e tradotto: tutto ciò che il resto del codice deve saperne."""

    piattaforma: str
    #: Il prodotto come comprato (Google con il base plan: `abbonamento:annuale`) e gli ID da cercare in
    #: `prodotti_store`, nell'ordine.
    product_id: str
    candidati: List[str]
    tipo: str                                   # consumabile | abbonamento
    transazione: str
    transazione_originale: Optional[str] = None
    ordine: Optional[str] = None
    purchase_token: Optional[str] = None
    ambiente: str = "production"
    #: Il token dell'account che l'app ha passato allo store (`obfuscatedExternalAccountId`, `appAccountToken`).
    account: Optional[str] = None
    #: Lo store non l'ha ancora incassato (Google `PENDING`): niente crediti.
    in_attesa: bool = False
    #: Un acquisto in attesa mai pagato, o annullato dallo store.
    annullato: bool = False
    #: Già confermato allo store (Google: acknowledged/consumed; Apple non lo chiede).
    confermato: bool = False
    acquistato_il: Optional[datetime] = None
    scade_il: Optional[datetime] = None
    prova: bool = False
    rinnovo_automatico: bool = True
    #: Per un abbonamento, lo stato presso lo store tradotto nei nostri (`STATI_STORE`).
    stato_abbonamento: Optional[str] = None
    revocato_il: Optional[datetime] = None
    importo: Optional[int] = None
    valuta: Optional[str] = None
    paese: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)


class FornitoreStore:
    """Lo store visto da `GestorePagamenti` e `GestoreAbbonamenti`: incassa e rinnova da sé.

    Non apre pagine di pagamento e non disdice: tutto si fa nello store, dall'app o dalle impostazioni del telefono.
    Gli eventi non arrivano dal webhook generico ma da `billing/store/`, già verificati.
    """

    def __init__(self, nome: str) -> None:
        self.name = nome

    async def crea_abbonamento(self, user_id: int, piano: Plan, *, annuale: bool = False) -> str:
        """Solo il piano gratuito, che si riapre quando un abbonamento dello store finisce (come per Stripe)."""
        from ..plans import gratuito

        if gratuito(piano):
            return f"gratuito-{uuid.uuid4().hex[:12]}"
        raise PagamentiNonDisponibili("un abbonamento dello store nasce da un acquisto nello store")

    async def disdici(self, external_id: str) -> None:
        """La disdetta di un abbonamento dello store si fa nello store: qui non c'è niente da chiamare."""
        return None

    async def e_pagato(self, external_id: str) -> bool:
        # Mai chiamato: gli store sono in `FORNITORI_ESTERNI`, e i rinnovi arrivano con le loro notifiche.
        return False


def gestore(piattaforma: str, session: AsyncSession) -> GestorePagamenti:
    return GestorePagamenti(session, FornitoreStore(FORNITORE[piattaforma]))


def id_evento(piattaforma: str, *parti: Any) -> str:
    """L'id dell'evento in `payment_events`: `gp:<ordine>`, `as:<transazione>`, `gp:stato:…`. Al massimo 120
    caratteri: le parti lunghe (un token) entrano già ridotte a un'impronta."""
    return ":".join([PREFISSO[piattaforma], *(str(p) for p in parti)])[:120]


def impronta(testo: str, n: int = 40) -> str:
    """L'impronta di un valore troppo lungo per un id (il purchase token di Google)."""
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:n]


def istante(quando: Optional[datetime]) -> Optional[int]:
    return int(quando.timestamp()) if quando else None


# ---- prodotto, account, riga --------------------------------------------------------------------------------------


async def prodotto_per(
    session: AsyncSession, piattaforma: str, candidati: Sequence[str],
) -> Optional[Tuple[ProdottoStore, Plan]]:
    """Il prodotto della console per il primo ID che c'è (attivo o no: un acquisto di un prodotto ritirato resta
    valido), con il suo piano."""
    candidati = [c for c in candidati if c]
    if not candidati:
        return None
    righe = (await session.execute(
        select(ProdottoStore, Plan).join(Plan, Plan.id == ProdottoStore.plan_id)
        .where(ProdottoStore.piattaforma == piattaforma, ProdottoStore.product_id.in_(candidati))
    )).all()
    per_id = {p.product_id: (p, piano) for p, piano in righe}
    for c in candidati:
        if c in per_id:
            return per_id[c]
    return None


async def utente_per_token(session: AsyncSession, token: Optional[str]) -> Optional[User]:
    if not token:
        return None
    try:
        valore = uuid.UUID(str(token).strip())
    except ValueError:
        return None
    return (await session.execute(select(User).where(User.app_account_token == valore))).scalar_one_or_none()


async def riga_di(session: AsyncSession, piattaforma: str, transazione: str) -> Optional[AcquistoStore]:
    return (await session.execute(select(AcquistoStore).where(
        AcquistoStore.piattaforma == piattaforma, AcquistoStore.transazione == transazione,
    ))).scalar_one_or_none()


async def _blocca(session: AsyncSession, t: Transazione) -> None:
    """Un lock per acquisto (l'abbonamento intero, se lo è) fino alla fine della transazione del database: la
    verifica dall'app e la notifica dello store arrivate insieme non scrivono due righe né due checkout."""
    chiave = f"store:{t.piattaforma}:{t.transazione_originale or (t.purchase_token and impronta(t.purchase_token)) or t.transazione}"
    await session.execute(text("select pg_advisory_xact_lock(hashtext(:k))"), {"k": chiave})


async def _proprietario(
    session: AsyncSession, t: Transazione, riga: Optional[AcquistoStore], utente: Optional[User],
) -> User:
    """Di chi è l'acquisto. Con il token dell'account decide il token; senza (un codice promozionale riscattato nel
    Play Store, un acquisto fatto prima dell'app di oggi) decide chi l'ha già registrato, poi chi lo sta verificando
    dall'app."""
    if t.account:
        proprietario = await utente_per_token(session, t.account)
        if utente is not None and (proprietario is None or proprietario.id != utente.id):
            raise ErroreStore(
                "account_diverso",
                "Questo acquisto è stato fatto da un altro account: accedi con l'account con cui l'hai comprato.", 403,
            )
        if proprietario is None:
            raise ErroreStore("utente_sconosciuto", "L'acquisto porta il token di un account che non esiste più.", 404)
        return proprietario
    gia: Optional[int] = riga.user_id if riga is not None else None
    if gia is None and t.transazione_originale:
        gia = await session.scalar(select(AcquistoStore.user_id).where(
            AcquistoStore.piattaforma == t.piattaforma, AcquistoStore.transazione_originale == t.transazione_originale,
            AcquistoStore.user_id.is_not(None),
        ).limit(1))
    if gia is not None:
        if utente is not None and gia != utente.id:
            raise ErroreStore(
                "account_diverso",
                "Questo acquisto è già registrato su un altro account: accedi con l'account con cui l'hai comprato.",
                403,
            )
        trovato = await session.get(User, gia)
        if trovato is not None:
            return trovato
    if utente is not None:
        logger.warning("Acquisto %s %s senza token dell'account: lo prende %s, che lo verifica",
                       t.piattaforma, t.transazione, utente.id)
        return utente
    raise ErroreStore("utente_sconosciuto", "Non si sa di quale account sia questo acquisto.", 404)


def _aggiorna_riga(riga: AcquistoStore, t: Transazione, piano: Plan) -> None:
    riga.product_id = t.product_id[:150]
    riga.plan_id = piano.id
    riga.transazione_originale = t.transazione_originale
    riga.ordine = t.ordine or riga.ordine
    riga.purchase_token = t.purchase_token or riga.purchase_token
    riga.ambiente = t.ambiente
    riga.confermato = riga.confermato or t.confermato
    riga.prova = t.prova or riga.prova
    riga.acquistato_il = t.acquistato_il or riga.acquistato_il
    riga.scade_il = t.scade_il or riga.scade_il
    if t.importo is not None:
        riga.importo, riga.valuta = t.importo, t.valuta
    riga.paese = t.paese or riga.paese
    riga.payload = {**(riga.payload or {}), **t.payload}


async def _collega_crediti(session: AsyncSession, riga: AcquistoStore) -> None:
    """Le righe dei crediti nate da questo incasso puntano all'acquisto (`credit_ledger.acquisto_id`)."""
    await session.execute(
        update(CreditEntry)
        .where(
            CreditEntry.provider == FORNITORE[riga.piattaforma], CreditEntry.riferimento_esterno == riga.transazione,
            CreditEntry.acquisto_id.is_(None),
        )
        .values(acquisto_id=riga.id)
    )


# ---- il percorso unico ---------------------------------------------------------------------------------------------


async def registra(
    session: AsyncSession, t: Transazione, *, utente: Optional[User] = None, configurato: Any = None,
) -> Dict[str, Any]:
    """Registra un incasso verificato: la riga, l'accredito (una volta), lo stato dell'abbonamento. Idempotente.

    `utente` è chi lo sta verificando dall'app (vuoto per le notifiche e la riconciliazione); `configurato` il
    fornitore di pagamento del sito, per disdire un abbonamento Stripe quando l'utente passa a uno dello store.
    Solleva `ErroreStore`. Non fa il commit: lo fa chi chiama, e solo dopo si conferma l'acquisto allo store.
    """
    await _blocca(session, t)
    trovato = await prodotto_per(session, t.piattaforma, t.candidati)
    if trovato is None:
        raise ErroreStore(
            "prodotto_sconosciuto",
            f"Il prodotto «{t.product_id}» di {NOME_STORE[t.piattaforma]} non è collegato a nessun piano: va aggiunto "
            "in console → App mobili → Prodotti.",
        )
    prodotto, piano = trovato
    if prodotto.tipo != t.tipo:
        raise ErroreStore(
            "tipo_diverso", f"Il prodotto «{t.product_id}» è un {t.tipo} nello store e un {prodotto.tipo} in console.",
        )
    riga = await riga_di(session, t.piattaforma, t.transazione)
    if riga is None and t.purchase_token:
        # Un acquisto registrato quando era ancora in attesa (Google: senza ordine, identificato dal token) e ora
        # pagato: è la stessa riga, che prende l'ordine come transazione.
        riga = (await session.execute(select(AcquistoStore).where(
            AcquistoStore.piattaforma == t.piattaforma, AcquistoStore.purchase_token == t.purchase_token,
            AcquistoStore.stato == "in_attesa", AcquistoStore.transazione.startswith("tok_"),
        ).limit(1))).scalar_one_or_none()
        if riga is not None:
            riga.transazione = t.transazione
    proprietario = await _proprietario(session, t, riga, utente)
    if riga is None:
        riga = AcquistoStore(
            user_id=proprietario.id, piattaforma=t.piattaforma, product_id=t.product_id[:150], tipo=t.tipo,
            plan_id=piano.id, transazione=t.transazione, stato="in_attesa", payload={},
        )
        session.add(riga)
    elif riga.user_id is None:
        riga.user_id = proprietario.id
    _aggiorna_riga(riga, t, piano)
    await session.flush()

    esito = await _applica(session, t, riga, prodotto, piano, proprietario, configurato)
    await session.flush()
    await _collega_crediti(session, riga)
    return {"esito": esito, "acquisto": acquisto_json(riga)}


async def _applica(
    session: AsyncSession, t: Transazione, riga: AcquistoStore, prodotto: ProdottoStore, piano: Plan, utente: User,
    configurato: Any,
) -> str:
    if t.revocato_il is not None or (t.annullato and riga.stato == "accreditato"):
        if riga.stato == "in_attesa":
            riga.stato, riga.revocato_il = "revocato", t.revocato_il or utcnow()
            return "acquisto revocato prima dell'accredito"
        # Un acquisto annullato dallo store dopo l'accredito (Google `purchaseState` 1: rimborsato o stornato) è un
        # rimborso; la revoca vera (un abbonamento revocato) arriva con la sua notifica.
        return await storna_transazione(
            session, t.piattaforma, t.transazione, causa="rimborso", quando=t.revocato_il,
        )
    if t.annullato:
        if riga.stato == "in_attesa":
            riga.stato = "scaduto"
        return "acquisto annullato"
    if t.in_attesa:
        return "in attesa del pagamento" if riga.stato == "in_attesa" else f"acquisto {riga.stato}"
    if t.tipo == "consumabile":
        return await _pacchetto(session, t, riga, prodotto, piano, utente)
    return await _abbonamento(session, t, riga, prodotto, piano, utente, configurato)


async def _checkout(
    session: AsyncSession, t: Transazione, prodotto: ProdottoStore, piano: Plan, utente: User, *, prova: bool,
) -> PaymentCheckout:
    """Il checkout dell'acquisto nello store: lo stesso registro di Stripe, già «pagato» dallo store."""
    abbonamento = t.tipo == "abbonamento"
    listino = listino_di(piano, prodotto.annuale) if abbonamento else piano.price_monthly
    sconto_prova = 0
    if abbonamento and prodotto.prova:
        # Il prodotto «prova» è l'annuale a metà prezzo: lo sconto della prova (Fase 2b), per sempre.
        sconto_prova = percentuale(listino, (await impostazioni(session)).sconto_prova)
    checkout = PaymentCheckout(
        user_id=utente.id, plan_id=piano.id, annuale=bool(abbonamento and prodotto.annuale), status="aperto",
        provider=FORNITORE[t.piattaforma], external_id=id_evento(t.piattaforma, t.transazione),
        importo=0 if prova else max(0, listino - sconto_prova), currency=piano.currency, listino=listino,
        rinnovo=t.rinnovo_automatico if abbonamento else False, sconto_rinnovo=sconto_prova, prova=prova,
        sandbox=t.ambiente == "sandbox",
    )
    session.add(checkout)
    await session.flush()
    return checkout


async def _pacchetto(
    session: AsyncSession, t: Transazione, riga: AcquistoStore, prodotto: ProdottoStore, piano: Plan, utente: User,
) -> str:
    if riga.stato in ("accreditato", "rimborsato", "revocato"):
        return f"acquisto già {riga.stato}"
    checkout = await _checkout(session, t, prodotto, piano, utente, prova=False)
    esito = await gestore(t.piattaforma, session).applica(EventoPagamento(
        id=id_evento(t.piattaforma, t.transazione), tipo=PAGATO,
        dati={"checkout_id": str(checkout.id), "riferimento": t.transazione, "canale": t.piattaforma},
    ))
    riga.stato = "accreditato"
    return esito


async def _abbonamento(
    session: AsyncSession, t: Transazione, riga: AcquistoStore, prodotto: ProdottoStore, piano: Plan, utente: User,
    configurato: Any,
) -> str:
    from ..plans import GestoreAbbonamenti, gratuito

    esterno = t.transazione_originale or t.transazione
    fornitore = FORNITORE[t.piattaforma]
    sub = await _abbonamento_esterno(session, fornitore, esterno)
    vivo_presso_store = t.stato_abbonamento in ("in_prova", "attivo", "in_sospeso", "sospeso")
    g = gestore(t.piattaforma, session)
    esito = "abbonamento allineato"

    if riga.stato == "in_attesa":
        if sub is None:
            if not vivo_presso_store:
                # Già finito presso lo store (lo trova tardi la riconciliazione): niente periodo da aprire.
                riga.stato = "scaduto"
                return "abbonamento già scaduto presso lo store"
            await _chiudi_altri_canali(session, utente.id, fornitore, esterno, configurato)
            checkout = await _checkout(session, t, prodotto, piano, utente, prova=t.prova)
            esito = await g.applica(EventoPagamento(
                id=id_evento(t.piattaforma, t.transazione), tipo=PAGATO,
                dati={
                    "checkout_id": str(checkout.id), "riferimento": t.transazione, "canale": t.piattaforma,
                    "subscription_id": esterno, "fine": istante(t.scade_il),
                },
            ))
        else:
            altro = await GestoreAbbonamenti(session, FornitoreStore(fornitore)).abbonamento_di(utente.id)
            if sub.status in ("disdetto", "scaduto") and altro is not None and altro.id != sub.id \
                    and not gratuito(altro.plan):
                # L'utente ha già un altro abbonamento (preso dopo, su un altro canale) e questo store continua a
                # rinnovare il vecchio: l'incasso si registra, l'abbonamento non si riapre.
                riga.stato = "accreditato"
                riga.subscription_id = sub.id
                riga.payload = {**(riga.payload or {}), "doppio": True}
                logger.warning(
                    "Abbonamento doppio: l'utente %s ha %s vivo e %s rinnova ancora %s", utente.id, altro.provider,
                    fornitore, esterno,
                )
                return "abbonamento doppio: incasso registrato, abbonamento non riaperto"
            if sub.plan_id != piano.id or sub.annuale != prodotto.annuale:
                # Un cambio di piano fatto nello store (Apple lo fa nello stesso abbonamento): il periodo nuovo è
                # del piano nuovo.
                sub.plan_id, sub.plan, sub.annuale = piano.id, piano, prodotto.annuale
                sub.listino = listino_di(piano, prodotto.annuale)
                sub.piano_successivo_id, sub.annuale_successivo = None, None
            esito = await g.applica(EventoPagamento(
                id=id_evento(t.piattaforma, t.transazione), tipo=RINNOVATO,
                dati={
                    "subscription_id": esterno, "riferimento": t.transazione, "canale": t.piattaforma,
                    "fine": istante(t.scade_il),
                    "importo": 0 if t.ambiente == "sandbox" else max(0, (sub.listino or 0) - sub.sconto_ricorrente),
                },
            ))
            if t.acquistato_il and sub.period_start < t.acquistato_il < sub.period_end:
                # Un abbonamento ripreso dopo una pausa (Apple RESUBSCRIBE, stesso abbonamento): il periodo parte
                # dall'acquisto, non dalla fine di quello vecchio.
                sub.period_start = t.acquistato_il
        riga.stato = "accreditato"
        sub = await _abbonamento_esterno(session, fornitore, esterno)

    if sub is None:
        return esito
    riga.subscription_id = sub.id
    await _allinea(session, g, sub, t, utente)
    return esito


async def _abbonamento_esterno(session: AsyncSession, fornitore: str, esterno: str) -> Optional[Subscription]:
    return (await session.execute(
        select(Subscription).where(Subscription.provider == fornitore, Subscription.external_id == esterno)
        .order_by(Subscription.created_at.desc()).limit(1)
    )).scalar_one_or_none()


async def _chiudi_altri_canali(
    session: AsyncSession, user_id: int, fornitore: str, esterno: str, configurato: Any,
) -> None:
    """Prima di aprire l'abbonamento dello store, quello vivo su un altro canale si disdice presso chi lo incassa
    (Stripe: niente rinnovo a fine periodo). Lo chiude poi `GestoreAbbonamenti.sottoscrivi`, come in ogni cambio."""
    from ..abbonamenti import fornitore_per
    from ..plans import GestoreAbbonamenti, gratuito

    vivo = await GestoreAbbonamenti(session, FornitoreStore(fornitore)).abbonamento_di(user_id)
    if vivo is None or gratuito(vivo.plan) or (vivo.provider == fornitore and vivo.external_id == esterno):
        return
    if vivo.provider in FORNITORE.values():
        logger.warning(
            "L'utente %s passa a %s con un abbonamento ancora vivo su %s: quello va disdetto nello store",
            user_id, fornitore, vivo.provider,
        )
        return
    if configurato is None:
        from ..pagamenti import provider_pagamenti

        configurato = provider_pagamenti()
    altro = fornitore_per(vivo, configurato)
    if altro is not None and vivo.cancel_at is None and vivo.external_id:
        try:
            await altro.disdici(vivo.external_id)
        except PagamentiNonDisponibili as exc:
            logger.error("Disdetta presso %s non riuscita per %s: %s", vivo.provider, vivo.external_id, exc)
            return
        vivo.cancel_at = utcnow()


async def _allinea(
    session: AsyncSession, g: GestorePagamenti, sub: Subscription, t: Transazione, utente: User,
) -> None:
    """Lo stato locale segue quello dello store, senza mai accreditare; la disdetta (e la riaccensione) del rinnovo
    fatta nello store manda l'email di conferma come quella fatta dal profilo."""
    stato = t.stato_abbonamento
    if stato is None or stato == "revocato":
        return
    esterno = sub.external_id or ""
    prima = sub.cancel_at
    era_vivo = sub.vivo
    if stato == "scaduto":
        if sub.status in ("disdetto", "scaduto"):
            return
        await g.applica(EventoPagamento(
            id=id_evento(t.piattaforma, "scaduto", esterno, istante(t.scade_il) or 0), tipo=ABBONAMENTO_AGGIORNATO,
            dati={"subscription_id": esterno, "stato": "scaduto"},
        ))
        ultima = await riga_di(session, t.piattaforma, t.transazione)
        if ultima is not None and ultima.stato == "accreditato":
            ultima.stato = "scaduto"
        return
    if sub.status in ("disdetto", "scaduto"):
        return
    if sub.status != stato or (sub.cancel_at is None) != t.rinnovo_automatico:
        # Solo se qualcosa cambia, e con un id nuovo ogni volta: lo stesso cambio può tornare (rinnovo spento,
        # riacceso, rispento), e un id fatto dello stato lo farebbe scartare come «già applicato». Applicare due volte
        # lo stesso stato non fa niente, quindi qui l'idempotenza non serve.
        await g.applica(EventoPagamento(
            id=id_evento(t.piattaforma, "stato", esterno, uuid.uuid4().hex[:16]), tipo=ABBONAMENTO_AGGIORNATO,
            dati={
                "subscription_id": esterno, "stato": stato, "disdetta_a_fine_periodo": not t.rinnovo_automatico,
                "fine": istante(t.scade_il),
            },
        ))
    if t.scade_il and stato in ("attivo", "in_prova") and t.scade_il > sub.period_start:
        # Lo store è la fonte della data: i suoi mesi sono di calendario, e una proroga (Apple RENEWAL_EXTENDED) la
        # sposta senza un nuovo incasso.
        sub.period_end = t.scade_il
    await session.flush()
    if era_vivo and prima is None and sub.cancel_at is not None:
        await _email_rinnovo(session, sub, utente, spento=True)
    elif era_vivo and prima is not None and sub.cancel_at is None:
        await _email_rinnovo(session, sub, utente, spento=False)


async def _email_rinnovo(session: AsyncSession, sub: Subscription, utente: User, *, spento: bool) -> None:
    """Le email della Fase 2b per il rinnovo spento o riacceso nello store: una per cambio (la chiave porta la data
    del periodo, così una seconda notifica dello stesso cambio non la rimanda)."""
    from ...posta import data_in, importo_in, lingua_di, manda
    from ..abbonamenti import prossimo_rinnovo

    lingua = lingua_di(utente)
    fine = istante(sub.period_end)
    if spento:
        await manda(session, utente, "rinnovo_spento", f"rinnovo_spento:{sub.id}:store:{fine}", {
            "piano": sub.plan.name, "data": data_in(sub.period_end, lingua), "oggi": data_in(utcnow(), lingua),
        })
    else:
        await manda(session, utente, "rinnovo_riacceso", f"rinnovo_riacceso:{sub.id}:store:{fine}", {
            "piano": sub.plan.name, "data": data_in(sub.period_end, lingua),
            "importo": importo_in(prossimo_rinnovo(sub) or 0, sub.plan.currency, lingua),
        })


# ---- rimborsi e revoche --------------------------------------------------------------------------------------------


async def storna_transazione(
    session: AsyncSession, piattaforma: str, transazione: str, *, causa: str = "rimborso", revoca: bool = False,
    quando: Optional[datetime] = None,
) -> str:
    """Lo store ha rimborsato (o revocato) un incasso: i suoi crediti si stornano (il saldo può andare sotto zero,
    `RegistroCrediti.storna`) e, se era il periodo in corso di un abbonamento, l'abbonamento si chiude. Idempotente."""
    riga = await riga_di(session, piattaforma, transazione)
    if riga is None:
        logger.warning("Rimborso %s di un acquisto mai registrato: %s", piattaforma, transazione)
        return "acquisto sconosciuto"
    if riga.stato in ("rimborsato", "revocato"):
        return f"acquisto già {riga.stato}"
    g = gestore(piattaforma, session)
    accreditato = riga.stato in ("accreditato", "scaduto")
    esito = "nessun credito da stornare"
    if accreditato:
        esito = await g.applica(EventoPagamento(
            id=id_evento(piattaforma, "storno", transazione), tipo=STORNO,
            dati={"riferimenti": [transazione], "causa": causa},
        ))
    riga.stato = "revocato" if revoca else "rimborsato"
    riga.revocato_il = quando or utcnow()
    if accreditato and riga.tipo == "abbonamento" and riga.subscription_id is not None:
        sub = await session.get(Subscription, riga.subscription_id)
        successivi = await session.scalar(select(AcquistoStore.id).where(
            AcquistoStore.piattaforma == piattaforma,
            AcquistoStore.transazione_originale == riga.transazione_originale,
            AcquistoStore.stato == "accreditato", AcquistoStore.id != riga.id,
            AcquistoStore.acquistato_il > (riga.acquistato_il or riga.created_at),
        ).limit(1))
        if sub is not None and sub.vivo and successivi is None and sub.external_id:
            # Era il periodo in corso: lo store ha tolto l'accesso, e qui si torna al piano gratuito.
            await g.applica(EventoPagamento(
                id=id_evento(piattaforma, "chiuso", transazione), tipo=ABBONAMENTO_CHIUSO,
                dati={"subscription_id": sub.external_id},
            ))
    await session.flush()
    return esito


async def annulla_storno(session: AsyncSession, piattaforma: str, transazione: str) -> str:
    """Il rimborso è stato annullato (Apple `REFUND_REVERSED`): i crediti stornati tornano. Un abbonamento chiuso
    dal rimborso non si riapre da solo: lo riapre il prossimo rinnovo, o la console."""
    riga = await riga_di(session, piattaforma, transazione)
    if riga is None or riga.stato not in ("rimborsato", "revocato"):
        return "nessuno storno da annullare"
    esito = await gestore(piattaforma, session).applica(EventoPagamento(
        id=id_evento(piattaforma, "storno_annullato", transazione), tipo=STORNO_ANNULLATO,
        dati={"riferimenti": [transazione]},
    ))
    riga.stato, riga.revocato_il = "accreditato", None
    await session.flush()
    return esito


# ---- per la console e le notifiche ---------------------------------------------------------------------------------


async def segna_notifica(
    session: AsyncSession, piattaforma: str, tipo: str, *, ambiente: Optional[str] = None, esito: str = "",
) -> None:
    """L'ultima notifica ricevuta dallo store, per la console «App mobili» (la prova che il collegamento va)."""
    from ...domain import app_mobili_repositories as app_mobili

    r = await app_mobili.riga(session, piattaforma)
    r.ultima_notifica_il = utcnow()
    r.ultima_notifica = {"tipo": tipo[:80], "ambiente": ambiente, "esito": esito[:300]}


def acquisto_json(a: AcquistoStore) -> Dict[str, Any]:
    return {
        "id": a.id,
        "piattaforma": a.piattaforma,
        "store": NOME_STORE.get(a.piattaforma, a.piattaforma),
        "product_id": a.product_id,
        "tipo": a.tipo,
        "transazione": a.transazione,
        "transazione_originale": a.transazione_originale,
        "ordine": a.ordine,
        "stato": a.stato,
        "ambiente": a.ambiente,
        "confermato": a.confermato,
        "prova": a.prova,
        "doppio": bool((a.payload or {}).get("doppio")),
        "importo": a.importo,
        "valuta": a.valuta,
        "paese": a.paese,
        "acquistato_il": a.acquistato_il.isoformat() if a.acquistato_il else None,
        "scade_il": a.scade_il.isoformat() if a.scade_il else None,
        "revocato_il": a.revocato_il.isoformat() if a.revocato_il else None,
        "creato_il": a.created_at.isoformat() if a.created_at else None,
    }


# ---- i paesi degli store -------------------------------------------------------------------------------------------

#: ISO 3166-1 alpha-3 → alpha-2: Apple dice il paese dello store in alpha-3 (`storefront`, `Storefront.countryCode`),
#: la politica del pulsante Stripe e il resto del sito usano alpha-2.
_ALPHA3 = (
    "AFG:AF ALA:AX ALB:AL DZA:DZ ASM:AS AND:AD AGO:AO AIA:AI ATA:AQ ATG:AG ARG:AR ARM:AM ABW:AW AUS:AU AUT:AT "
    "AZE:AZ BHS:BS BHR:BH BGD:BD BRB:BB BLR:BY BEL:BE BLZ:BZ BEN:BJ BMU:BM BTN:BT BOL:BO BES:BQ BIH:BA BWA:BW "
    "BVT:BV BRA:BR IOT:IO BRN:BN BGR:BG BFA:BF BDI:BI CPV:CV KHM:KH CMR:CM CAN:CA CYM:KY CAF:CF TCD:TD CHL:CL "
    "CHN:CN CXR:CX CCK:CC COL:CO COM:KM COG:CG COD:CD COK:CK CRI:CR CIV:CI HRV:HR CUB:CU CUW:CW CYP:CY CZE:CZ "
    "DNK:DK DJI:DJ DMA:DM DOM:DO ECU:EC EGY:EG SLV:SV GNQ:GQ ERI:ER EST:EE SWZ:SZ ETH:ET FLK:FK FRO:FO FJI:FJ "
    "FIN:FI FRA:FR GUF:GF PYF:PF ATF:TF GAB:GA GMB:GM GEO:GE DEU:DE GHA:GH GIB:GI GRC:GR GRL:GL GRD:GD GLP:GP "
    "GUM:GU GTM:GT GGY:GG GIN:GN GNB:GW GUY:GY HTI:HT HMD:HM VAT:VA HND:HN HKG:HK HUN:HU ISL:IS IND:IN IDN:ID "
    "IRN:IR IRQ:IQ IRL:IE IMN:IM ISR:IL ITA:IT JAM:JM JPN:JP JEY:JE JOR:JO KAZ:KZ KEN:KE KIR:KI PRK:KP KOR:KR "
    "KWT:KW KGZ:KG LAO:LA LVA:LV LBN:LB LSO:LS LBR:LR LBY:LY LIE:LI LTU:LT LUX:LU MAC:MO MDG:MG MWI:MW MYS:MY "
    "MDV:MV MLI:ML MLT:MT MHL:MH MTQ:MQ MRT:MR MUS:MU MYT:YT MEX:MX FSM:FM MDA:MD MCO:MC MNG:MN MNE:ME MSR:MS "
    "MAR:MA MOZ:MZ MMR:MM NAM:NA NRU:NR NPL:NP NLD:NL NCL:NC NZL:NZ NIC:NI NER:NE NGA:NG NIU:NU NFK:NF MKD:MK "
    "MNP:MP NOR:NO OMN:OM PAK:PK PLW:PW PSE:PS PAN:PA PNG:PG PRY:PY PER:PE PHL:PH PCN:PN POL:PL PRT:PT PRI:PR "
    "QAT:QA REU:RE ROU:RO RUS:RU RWA:RW BLM:BL SHN:SH KNA:KN LCA:LC MAF:MF SPM:PM VCT:VC WSM:WS SMR:SM STP:ST "
    "SAU:SA SEN:SN SRB:RS SYC:SC SLE:SL SGP:SG SXM:SX SVK:SK SVN:SI SLB:SB SOM:SO ZAF:ZA SGS:GS SSD:SS ESP:ES "
    "LKA:LK SDN:SD SUR:SR SJM:SJ SWE:SE CHE:CH SYR:SY TWN:TW TJK:TJ TZA:TZ THA:TH TLS:TL TGO:TG TKL:TK TON:TO "
    "TTO:TT TUN:TN TUR:TR TKM:TM TCA:TC TUV:TV UGA:UG UKR:UA ARE:AE GBR:GB USA:US UMI:UM URY:UY UZB:UZ VUT:VU "
    "VEN:VE VNM:VN VGB:VG VIR:VI WLF:WF ESH:EH YEM:YE ZMB:ZM ZWE:ZW XKX:XK"
)
ALPHA3 = dict(coppia.split(":") for coppia in _ALPHA3.split())


def paese_alpha2(codice: Optional[str]) -> Optional[str]:
    """Il paese in alpha-2 (`IT`), da alpha-2 o alpha-3 (`ITA`); `None` se non si riconosce."""
    c = (codice or "").strip().upper()
    if len(c) == 2 and c.isalpha():
        return c
    return ALPHA3.get(c)
