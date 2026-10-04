"""Le notifiche automatiche (v9, Fase 5): ognuna si accende, si spegne e si riscrive dalla console.

- **Carta del giorno** — all'ora locale scelta dalla persona (predefinita 8:30), se oggi non l'ha ancora aperta.
- **Serie in pericolo** — la sera (20:00), a chi ha almeno tre giorni di fila e oggi non ha ancora girato la carta.
- **Crediti in scadenza** — spenta di base: dalla v9 i crediti comprati non scadono; restano solo quelli di piano dei
  piani vecchi, che scadono con il periodo. Accesa, avvisa tre giorni prima.
- **Benvenuto** — il giorno dopo l'iscrizione (D+1), una volta.
- **Rinnovo non riuscito** — appena il pagamento fallisce (la tolleranza è aperta), una volta per fallimento.
- **Promemoria della prova** — `giorni_promemoria_prova` giorni prima della fine (T−2), una volta per prova. Lo
  chiama anche il giro degli abbonamenti, insieme all'email (`billing.abbonamenti.aggancio_notifica`).

**Le regole comuni.** Si guarda l'ora **locale** di chi riceve (`users.fuso_orario`, altrimenti Europe/Rome). Niente
nelle ore di silenzio. Le automatiche con un'ora partono in una finestra di tre ore da quell'ora: il CronJob gira ogni
15 minuti, e un giro saltato non fa perdere il messaggio; quelle senza ora partono al primo giro fuori dal silenzio.
L'idempotenza è dell'indice unico: un tipo, una persona, un giorno locale; per benvenuto, rinnovo e prova si guarda
anche se c'è già un invio per lo stesso evento.

La carta del giorno e la serie dipendono dall'interruttore «Carta del giorno» della persona; gli altri da
«Promemoria».
"""
from __future__ import annotations

import logging
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.billing_models import CreditEntry, Subscription
from ..domain.models import DailyCard, User
from ..domain.notifiche_models import DispositivoNotifica, InvioNotifica
from . import config as conf
from .invio import Postino, Preferenze, preferenze_di

logger = logging.getLogger(__name__)

#: Quanto resta aperta la finestra di un'automatica con un'ora.
FINESTRA = timedelta(hours=3)
#: Quanti giorni di fila servono perché la serie sia «in pericolo».
SERIE_MINIMA = 3
#: Il benvenuto parte fra uno e quattro giorni dall'iscrizione (poi non ha più senso).
BENVENUTO_DA, BENVENUTO_A = timedelta(days=1), timedelta(days=4)
GIORNI_CREDITI = 3


def _nella_finestra(locale: datetime, ora_testo: Optional[str]) -> bool:
    if not ora_testo:
        return True
    inizio = datetime.combine(locale.date(), conf.ora_da_testo(ora_testo), tzinfo=locale.tzinfo)
    return inizio <= locale < inizio + FINESTRA


async def _gia(session: AsyncSession, user_id: int, tipo: str, dal: Optional[datetime] = None) -> bool:
    condizioni = [InvioNotifica.user_id == user_id, InvioNotifica.tipo == tipo]
    if dal is not None:
        condizioni.append(InvioNotifica.created_at >= dal)
    return bool((await session.execute(select(exists().where(*condizioni)))).scalar())


async def _serie_fino_a(session: AsyncSession, user_id: int, ultimo: date) -> int:
    giorni = set((await session.execute(
        select(DailyCard.giorno).where(DailyCard.user_id == user_id, DailyCard.giorno >= ultimo - timedelta(days=366))
    )).scalars())
    serie, giorno = 0, ultimo
    while giorno in giorni:
        serie += 1
        giorno -= timedelta(days=1)
    return serie


async def _crediti_in_scadenza(session: AsyncSession, user_id: int, adesso: datetime) -> Optional[tuple[datetime, int]]:
    righe = (await session.execute(
        select(CreditEntry.expires_at, func.sum(CreditEntry.delta))
        .where(CreditEntry.user_id == user_id, CreditEntry.expires_at > adesso,
               CreditEntry.expires_at <= adesso + timedelta(days=GIORNI_CREDITI))
        .group_by(CreditEntry.expires_at).order_by(CreditEntry.expires_at)
    )).all()
    for scadenza, residuo in righe:
        if residuo and residuo > 0:
            return scadenza, int(residuo)
    return None


async def valuta(
    session: AsyncSession, postino: Postino, utente: User, pref: Preferenze, *,
    tipi: Optional[List[str]] = None, dati: Optional[Dict[str, Any]] = None,
) -> Counter:
    """Le automatiche di una persona, adesso. `tipi` restringe a quelle indicate; `dati` dà i valori già calcolati da
    chi chiama (il promemoria della prova arriva con quelli dell'email)."""
    conti: Counter = Counter()
    adesso = postino.adesso
    fuso = conf.fuso_di(utente)
    locale = adesso.astimezone(fuso)
    if conf.in_silenzio(locale, pref.silenzio_dal, pref.silenzio_al):
        conti["silenzio"] += 1
        return conti
    oggi = locale.date()
    cfg = postino.cfg

    async def manda(tipo: str, valori: Dict[str, Any]) -> None:
        a = conf.automatica(cfg, tipo)
        r = await postino.manda(utente, tipo, a["testi"], a["link"], giorno=oggi, valori=valori)
        conti[f"{tipo}:{r.esito}"] += 1

    def accesa(tipo: str) -> Optional[Dict[str, Any]]:
        if tipi is not None and tipo not in tipi:
            return None
        a = conf.automatica(cfg, tipo)
        return a if a["attiva"] else None

    carta_oggi: Optional[bool] = None

    async def ha_carta_oggi() -> bool:
        nonlocal carta_oggi
        if carta_oggi is None:
            carta_oggi = bool((await session.execute(select(exists().where(
                DailyCard.user_id == utente.id, DailyCard.giorno == oggi,
            )))).scalar())
        return carta_oggi

    if pref.carta_giorno and accesa("carta_giorno"):
        if _nella_finestra(locale, conf.ora_testo(pref.ora_carta)) and not await ha_carta_oggi():
            await manda("carta_giorno", {})

    a = accesa("serie_in_pericolo")
    if pref.carta_giorno and a and _nella_finestra(locale, a["ora"]) and not await ha_carta_oggi():
        serie = await _serie_fino_a(session, utente.id, oggi - timedelta(days=1))
        if serie >= SERIE_MINIMA:
            await manda("serie_in_pericolo", {"n": serie})

    if not pref.promemoria:
        return conti

    a = accesa("benvenuto")
    if a and _nella_finestra(locale, a["ora"]) and utente.created_at is not None:
        eta = adesso - utente.created_at
        if BENVENUTO_DA <= eta <= BENVENUTO_A and not await _gia(session, utente.id, "benvenuto"):
            await manda("benvenuto", {})

    a = accesa("crediti_in_scadenza")
    if a and _nella_finestra(locale, a["ora"]):
        scadenza = await _crediti_in_scadenza(session, utente.id, adesso)
        if scadenza and not await _gia(session, utente.id, "crediti_in_scadenza", adesso - timedelta(days=GIORNI_CREDITI)):
            from ..posta import data_in

            await manda("crediti_in_scadenza", {"n": scadenza[1], "data": data_in(scadenza[0].astimezone(fuso), _lingua(utente))})

    if accesa("rinnovo_fallito"):
        sospeso = (await session.execute(
            select(Subscription).where(Subscription.user_id == utente.id, Subscription.status == "in_sospeso",
                                       Subscription.pagamento_fallito_il.is_not(None))
            .order_by(Subscription.pagamento_fallito_il.desc()).limit(1)
        )).scalar_one_or_none()
        if sospeso is not None and not await _gia(session, utente.id, "rinnovo_fallito", sospeso.pagamento_fallito_il):
            await manda("rinnovo_fallito", {"piano": sospeso.plan.name})

    if accesa("promemoria_prova"):
        valori = dati or await _dati_prova(session, utente, adesso)
        if valori is not None:
            dal = valori.pop("_dal", None)
            if not await _gia(session, utente.id, "promemoria_prova", dal):
                await manda("promemoria_prova", valori)
    return conti


def _lingua(utente: User) -> str:
    from .invio import lingua_di

    return lingua_di(utente.locale)


async def _dati_prova(session: AsyncSession, utente: User, adesso: datetime) -> Optional[Dict[str, Any]]:
    """La prova di questa persona che finisce entro i giorni del promemoria, con i valori del messaggio."""
    from ..billing.abbonamenti import impostazioni
    from ..posta import data_in

    riga = await impostazioni(session)
    prova = (await session.execute(
        select(Subscription).where(
            Subscription.user_id == utente.id, Subscription.status == "in_prova", Subscription.prova.is_(True),
            Subscription.cancel_at.is_(None), Subscription.period_end > adesso,
            Subscription.period_end <= adesso + timedelta(days=riga.giorni_promemoria_prova),
        ).limit(1)
    )).scalar_one_or_none()
    if prova is None:
        return None
    return {
        "giorni": riga.giorni_promemoria_prova, "sconto": riga.sconto_prova,
        "data": data_in(prova.period_end.astimezone(conf.fuso_di(utente)), _lingua(utente)),
        # Un invio per prova: conta quello fatto da quando la finestra del promemoria si è aperta.
        "_dal": prova.period_end - timedelta(days=riga.giorni_promemoria_prova + 1),
    }


async def giro(session: AsyncSession, postino: Postino, *, limite: int = 5000) -> Dict[str, int]:
    """Le automatiche per tutte le persone con un dispositivo raggiungibile. Fa il commit a ogni persona."""
    conti: Counter = Counter()
    canali = postino.canali_disponibili
    if not canali:
        conti["nessun_canale"] += 1
        return dict(conti)
    ids = list((await session.execute(
        select(User.id).where(
            User.deleted_at.is_(None),
            exists().where(DispositivoNotifica.user_id == User.id, DispositivoNotifica.attivo.is_(True),
                           DispositivoNotifica.canale.in_(canali)),
        ).order_by(User.id).limit(limite)
    )).scalars())
    for inizio in range(0, len(ids), 200):
        blocco = ids[inizio:inizio + 200]
        preferenze = await preferenze_di(session, blocco, postino.cfg)
        utenti = {u.id: u for u in (await session.execute(select(User).where(User.id.in_(blocco)))).scalars()}
        for user_id in blocco:
            try:
                conti.update(await valuta(session, postino, utenti[user_id], preferenze[user_id]))
                await session.commit()
            except Exception:  # noqa: BLE001 — una persona che fa sbagliare il giro non deve fermare le altre
                await session.rollback()
                logger.exception("Notifiche automatiche: errore per l'utente %s", user_id)
                conti["errori_giro"] += 1
    return dict(conti)


async def promemoria_prova(session: AsyncSession, utente: Optional[User], dati: Dict[str, Any]) -> Optional[str]:
    """Dal giro degli abbonamenti, insieme all'email: prova subito (se non è l'ora di silenzio della persona); se non
    si può, ci pensa il giro delle notifiche entro 15 minuti. Non fa il commit."""
    if utente is None or utente.deleted_at is not None:
        return None
    postino = await Postino.prepara(session)
    if not postino.canali_disponibili:
        return None
    pref = (await preferenze_di(session, [utente.id], postino.cfg))[utente.id]
    valori = await _dati_prova(session, utente, postino.adesso)
    if valori is None:
        return None
    conti = await valuta(session, postino, utente, pref, tipi=["promemoria_prova"], dati=valori)
    return next(iter(conti), None)
