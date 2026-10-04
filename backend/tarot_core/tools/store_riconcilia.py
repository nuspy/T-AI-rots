"""La riconciliazione notturna degli acquisti nelle app (v9, Fase 4).

    python -m tarot_core.tools.store_riconcilia

Lo lancia il CronJob `tarots-store-riconcilia` ogni notte (vedi `deploy/k8s/tarots.yaml`). Le notifiche degli store
sono la strada principale, ma una notifica può perdersi (il server giù per un aggiornamento, Pub/Sub che smette di
riprovare dopo sette giorni, Apple dopo cinque tentativi): questo giro rilegge dagli store ciò che conta.

- **Google Play, rimborsi**: `voidedpurchases.list` degli ultimi 30 giorni (abbonamenti compresi). Ogni acquisto
  annullato (rimborso, chargeback, revoca) si storna: i suoi crediti tornano indietro, il saldo può andare sotto
  zero, e un abbonamento rimborsato nel periodo in corso si chiude.
- **Google Play, a metà**: gli acquisti degli ultimi 7 giorni rimasti `in_attesa` (un pagamento in contanti che
  forse è arrivato) o accreditati ma non ancora confermati a Google (che li rimborserebbe da sé dopo tre giorni): si
  rileggono, si registrano e si confermano.
- **App Store**: per ogni acquisto su iPhone degli ultimi 40 giorni, la storia delle transazioni (`/inApps/v2/
  history`) e lo stato dell'abbonamento (`/inApps/v1/subscriptions`): rinnovi persi, rimborsi, revoche, scadenze.

Uno store non configurato in console si salta. Ogni acquisto è un punto di ripristino a sé: un guasto su uno non
annulla gli altri. Tutto passa da `billing/store/comune.registra` e `storna_transazione`, idempotenti: rieseguirlo
non accredita né storna due volte.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from collections import Counter
from datetime import timedelta
from typing import Dict, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..billing.store import app_store, google_play
from ..billing.store.comune import ErroreStore, registra
from ..domain import app_mobili_repositories as app_mobili
from ..domain.acquisti_store_models import AcquistoStore
from ..domain.base import utcnow
from ..settings import Settings, get_settings

logger = logging.getLogger(__name__)

#: Quanto indietro si rileggono gli acquisti rimasti a metà su Google (oltre, Google li ha già rimborsati da sé).
FINESTRA_GOOGLE = timedelta(days=7)
#: Quanto indietro si rilegge la storia di chi ha comprato su iPhone: un mese e qualche giorno copre un rinnovo
#: mensile perso.
FINESTRA_APPLE = timedelta(days=40)


async def _configurato(session: AsyncSession, piattaforma: str) -> bool:
    r = await app_mobili.riga(session, piattaforma)
    parametri, segreti = app_mobili.parametri_di(r, piattaforma), app_mobili.segreti_di(r)
    if piattaforma == "android":
        return bool(segreti.get("service_account") and parametri.get("package_name"))
    return bool(segreti.get("chiave_p8") and parametri.get("key_id") and parametri.get("issuer_id")
                and parametri.get("bundle_id"))


async def _google(session: AsyncSession, conti: Counter) -> None:
    try:
        voci = await google_play.annullati(session, google_play.finestra_rimborsi())
    except ErroreStore as exc:
        logger.error("Rimborsi di Google Play non letti: %s", exc)
        conti["google_errori"] += 1
        voci = []
    for voce in voci:
        try:
            async with session.begin_nested():
                esito = await google_play.storna_voided(session, voce)
        except ErroreStore as exc:
            logger.error("Rimborso Google %s non registrato: %s", voce.get("orderId"), exc)
            conti["google_errori"] += 1
            continue
        if esito in ("crediti stornati", "storno senza crediti collegati", "nessun credito da stornare"):
            conti["google_stornati"] += 1
    await session.commit()

    a_meta = (await session.execute(
        select(AcquistoStore).where(
            AcquistoStore.piattaforma == "android", AcquistoStore.created_at >= utcnow() - FINESTRA_GOOGLE,
            AcquistoStore.purchase_token.is_not(None),
            or_(AcquistoStore.stato == "in_attesa", (AcquistoStore.stato == "accreditato") & ~AcquistoStore.confermato),
        ).order_by(AcquistoStore.id)
    )).scalars().all()
    for riga in a_meta:
        try:
            async with session.begin_nested():
                if riga.tipo == "consumabile":
                    t = await google_play.leggi_prodotto(session, riga.product_id, riga.purchase_token or "")
                else:
                    t = await google_play.leggi_abbonamento(session, riga.purchase_token or "")
                await registra(session, t)
        except ErroreStore as exc:
            logger.warning("Acquisto Google %s non riletto: %s", riga.transazione, exc)
            conti["google_errori"] += 1
            continue
        await session.commit()
        await session.refresh(riga)
        if await google_play.conferma(session, riga):
            conti["google_confermati"] += 1
        conti[f"google_{riga.stato}"] += 1
        await session.commit()


async def _apple(session: AsyncSession, conti: Counter) -> None:
    for originale, ambiente in await app_store.acquisti_recenti(session, utcnow() - FINESTRA_APPLE):
        try:
            async with session.begin_nested():
                esiti = await app_store.riconcilia_utente(session, originale, ambiente)
        except ErroreStore as exc:
            logger.warning("Storia Apple di %s non riletta: %s", originale, exc)
            conti["apple_errori"] += 1
            continue
        conti["apple_riletti"] += 1
        for esito, n in esiti.items():
            if esito.startswith(("crediti", "abbonamento", "prova", "storno")):
                conti["apple_aggiornati"] += n
        await session.commit()


async def giro(session: AsyncSession, settings: Optional[Settings] = None) -> Dict[str, int]:
    """Un giro su entrambi gli store. Restituisce i conteggi; fa i commit."""
    from ..configurazioni import correnti

    settings = settings or get_settings()
    await correnti.assicura(session)       # v9 Fase 2c: la posta (le email di conferma) dalla console
    conti: Counter = Counter()
    if await _configurato(session, "android"):
        await _google(session, conti)
    else:
        conti["google_non_configurato"] = 1
    if await _configurato(session, "ios"):
        await _apple(session, conti)
    else:
        conti["apple_non_configurato"] = 1
    await session.commit()
    return dict(conti)


async def _main() -> None:
    from ..domain.session import dispose_engine, get_session_factory

    try:
        async with get_session_factory()() as sessione:
            conti = await giro(sessione)
        print(", ".join(f"{k}: {v}" for k, v in sorted(conti.items())) or "niente da fare")
    finally:
        await dispose_engine()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(_main())
    return 0


if __name__ == "__main__":
    sys.exit(main())
