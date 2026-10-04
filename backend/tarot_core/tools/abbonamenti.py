"""Il giro orario degli abbonamenti (v9, Fase 2).

    python -m tarot_core.tools.abbonamenti

Lo lancia il CronJob `tarots-abbonamenti` ogni ora (vedi `deploy/k8s/tarots.yaml`). Prima nessuno chiamava
`GestoreAbbonamenti.rinnova()`: un abbonamento arrivato a fine periodo restava «attivo» per sempre, senza nuovi
crediti, e lo stato `scaduto` non si vedeva mai.

**Chi rinnova cosa.**

- I piani **interni** — gratuiti, regalati, del simulatore in sviluppo — li rinnova questo giro, con `rinnova()`:
  disdetti a fine periodo si chiudono, quelli del simulatore che «non pagano» si sospendono.
- Quelli di **Stripe** (e degli store, Fase 4) li rinnova il fornitore, con un evento (`invoice.paid` →
  `abbonamento.rinnovato`). Questo giro **non li tocca**: rinnovarli qui accrediterebbe due volte lo stesso periodo.
  Solo se dopo una settimana dalla fine del periodo non è arrivato niente — né il rinnovo, né un pagamento fallito,
  né la chiusura — l'abbonamento diventa `scaduto`: i webhook si sono persi, e un accesso senza fine non è la risposta.
- Un abbonamento **sospeso** di un piano interno che nessuno ha saldato in una settimana diventa `scaduto`.
- Fase 2b: un rinnovo interno non pagato apre la **tolleranza** (`in_sospeso`, letture comprese ancora attive); il
  giro manda i solleciti al terzo e al sesto giorno e sospende alla fine (`billing.abbonamenti.giro_tolleranza`,
  anche per Stripe), e manda il **promemoria della prova** due giorni prima della fine (`giro_promemoria_prova`). Le
  email passano dal registro `invii_email`: un giro ripetuto non le rimanda.

Chi resta senza un abbonamento vivo torna sul piano gratuito, come dopo una disdetta.

**Niente righe di `scadenza`.** I crediti di piano scadono già da soli nella somma del saldo, e con loro i consumi
che li hanno usati (`billing/credits.py`): una riga in più li toglierebbe due volte. Quanti crediti sono scaduti si
ricava dal registro (accrediti con `expires_at` passato meno i consumi con la stessa scadenza) quando servirà a un
rapporto.

Rieseguirlo è innocuo: un periodo già rinnovato ha la fine nel futuro e non viene ripreso, e l'accredito di un
periodo ha un riferimento unico (`rinnovo:<abbonamento>:<inizio>`).
"""
from __future__ import annotations

import asyncio
import logging
import sys
from collections import Counter
from datetime import timedelta
from typing import Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..billing.abbonamenti import giro_promemoria_prova, giro_tolleranza
from ..billing.pagamenti import provider_pagamenti
from ..billing.plans import GestoreAbbonamenti, NienteDaIncassare, gratuito
from ..domain.base import utcnow
from ..domain.billing_models import FORNITORI_ESTERNI, Subscription
from ..settings import Settings, get_settings

logger = logging.getLogger(__name__)

#: Quanto si aspetta il fornitore esterno oltre la fine del periodo prima di dichiarare scaduto un abbonamento. Stripe
#: riprova i webhook per tre giorni: una settimana copre i suoi tentativi e un fine settimana senza nessuno a guardare.
GRAZIA_ESTERNI = timedelta(days=7)
#: Quanto resta sospeso un abbonamento interno non pagato prima di scadere.
GRAZIA_SOSPESI = timedelta(days=7)


async def _torna_al_gratuito(session: AsyncSession, user_id: int) -> None:
    await session.flush()
    await GestoreAbbonamenti(session, NienteDaIncassare()).apri_piano_base(user_id)


async def giro(session: AsyncSession, settings: Optional[Settings] = None, *, limite: int = 500) -> Dict[str, int]:
    """Un giro: rinnova, chiude e fa scadere ciò che è arrivato a fine periodo. Restituisce i conteggi; fa il commit."""
    settings = settings or get_settings()
    from ..configurazioni import correnti

    await correnti.assicura(session)  # v9 Fase 2c: il fornitore e le chiavi scelti in console
    configurato = provider_pagamenti(settings)
    conti: Counter = Counter()
    adesso = utcnow()

    # `skip_locked`: un secondo giro partito per sbaglio insieme a questo salta le righe già prese, non le rinnova due
    # volte (il CronJob ha già `concurrencyPolicy: Forbid`; questa è la cintura con le bretelle).
    finiti = (await session.execute(
        select(Subscription)
        .where(Subscription.status.in_(("in_prova", "attivo")), Subscription.period_end <= adesso)
        .order_by(Subscription.period_end)
        .limit(limite)
        .with_for_update(skip_locked=True)
    )).scalars().all()

    for abbonamento in finiti:
        if abbonamento.provider in FORNITORI_ESTERNI:
            if abbonamento.period_end + GRAZIA_ESTERNI <= adesso:
                logger.warning(
                    "Abbonamento %s (%s) senza rinnovo dal fornitore da oltre %s: scaduto",
                    abbonamento.id, abbonamento.provider, GRAZIA_ESTERNI,
                )
                abbonamento.status = "scaduto"
                conti["scaduti"] += 1
                await _torna_al_gratuito(session, abbonamento.user_id)
            else:
                conti["attesa_fornitore"] += 1
            continue

        if gratuito(abbonamento.plan) or abbonamento.provider == "interno":
            fornitore = NienteDaIncassare()
        elif abbonamento.provider == configurato.name:
            fornitore = configurato
        else:
            # Un abbonamento del simulatore in un'installazione che ora incassa con altri: nessuno può rinnovarlo.
            abbonamento.status = "scaduto"
            conti["scaduti"] += 1
            await _torna_al_gratuito(session, abbonamento.user_id)
            continue

        esito = await GestoreAbbonamenti(session, fornitore).rinnova(abbonamento)
        if esito.chiuso:
            conti["chiusi"] += 1
            await _torna_al_gratuito(session, abbonamento.user_id)
        elif esito.motivo == "pagamento non riuscito":
            conti["in_tolleranza"] += 1
        elif esito.motivo == "già rinnovato":
            conti["gia_rinnovati"] += 1
        else:
            conti["rinnovati"] += 1

    sospesi = (await session.execute(
        select(Subscription)
        .where(
            Subscription.status == "sospeso",
            Subscription.provider.not_in(FORNITORI_ESTERNI),
            Subscription.period_end <= adesso - GRAZIA_SOSPESI,
        )
        .limit(limite)
        .with_for_update(skip_locked=True)
    )).scalars().all()
    for abbonamento in sospesi:
        abbonamento.status = "scaduto"
        conti["scaduti"] += 1
        await _torna_al_gratuito(session, abbonamento.user_id)

    # La tolleranza sui pagamenti falliti (Fase 2b): solleciti al terzo e al sesto giorno, sospensione alla fine; e il
    # promemoria della prova due giorni prima della fine. Entrambi idempotenti (il registro delle email).
    for chiave, n in (await giro_tolleranza(session, configurato=configurato)).items():
        conti[chiave] += n
    promemoria = await giro_promemoria_prova(session)
    if promemoria:
        conti["promemoria_prova"] += promemoria

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
