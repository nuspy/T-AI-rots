"""La commissione di referral: una quota di ogni acquisto futuro di un invitato, per chi lo ha invitato.

Diverso dal regalo di benvenuto (`ImpostazioniCrediti.crediti_iscrizione`/`crediti_invito`, una tantum
all'iscrizione, in `auth/dependencies.py` e `api/routers/profile.py`): questa gira **a ogni acquisto vero** —
un pacchetto, il primo periodo di un abbonamento, ogni rinnovo — per tutta la vita dell'account invitato, non solo
alla prima volta. La percentuale è in `ImpostazioniCrediti.commissione_referral_percentuale` (console).

**Due regole, secondo cosa si compra (v9, Fase 2b).** Un **pacchetto** paga la percentuale dei crediti che
accredita. Un **abbonamento** non dà più crediti (solo letture comprese): la commissione è la percentuale
dell'**importo pagato davvero** — il primo pagamento, ogni rinnovo, il conguaglio di un upgrade, la conversione di una
prova; mai durante la prova gratuita, che non paga niente — convertita in crediti al prezzo per credito del
**pacchetto più economico** in vendita (il pacchetto col prezzo più basso), arrotondata all'unità più vicina. Esempio:
abbonamento pagato 80 €, commissione 20% = 16 €; col pacchetto più economico a 4,90 € per 5 crediti (0,98 € l'uno)
sono 16 crediti. Senza nessun pacchetto in vendita non c'è un cambio, e la commissione non si accredita (si logga).

**Un rimborso non toglie mai la commissione.** È in crediti, non in denaro: un regalo a chi ha invitato, che non
dipende da cosa succede dopo all'acquisto di chi è stato invitato. Lo storno (`pagamenti.GestorePagamenti._storno`)
cerca solo i crediti dati all'acquirente (`acquisto`, `accredito_piano`), mai l'`omaggio` della commissione.

**Non deve mai poter far fallire un acquisto.** Chi ha invitato può aver cancellato l'account nel frattempo (o
non essere mai esistito per un errore altrove): l'acquisto di chi è stato invitato deve comunque completarsi. Per
questo l'intera funzione è avvolta in un `try/except` che logga e basta — è la stessa ragione per cui un log non
interrompe mai una richiesta.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.billing_models import Plan
from ..domain.models import User
from .credits import RegistroCrediti

logger = logging.getLogger(__name__)


async def commissione_da_acquisto(session: AsyncSession, acquirente_id: int, crediti_concessi: int) -> None:
    """Accredita a chi ha invitato `acquirente_id` la sua quota dei crediti appena concessi, se c'è ancora.

    Va chiamata **dopo** che i crediti dell'acquisto sono già stati accreditati al compratore: `crediti_concessi` è
    quel numero, non l'importo pagato — per un pacchetto la commissione è sui crediti, non sui soldi. Gli
    abbonamenti (che dalla Fase 2b non danno crediti) passano da `commissione_da_abbonamento`.
    """
    if crediti_concessi <= 0:
        return
    try:
        acquirente = await session.get(User, acquirente_id)
        if acquirente is None or acquirente.referred_by is None:
            return
        referente = await session.get(User, acquirente.referred_by)
        if referente is None or referente.deleted_at is not None:
            # Chi ha invitato non esiste più (account cancellato) o è stato disattivato: niente da accreditare,
            # e soprattutto niente da far esplodere. L'acquisto di chi ha comprato prosegue senza conseguenze.
            return

        from ..domain.impostazioni_repositories import correnti as impostazioni_correnti

        percentuale = (await impostazioni_correnti(session)).commissione_referral_percentuale
        importo = round(crediti_concessi * percentuale / 100)
        if importo <= 0:
            return
        await RegistroCrediti(session).accredita(
            referente.id, importo, reason="omaggio",
            note=f"commissione {percentuale}% sull'acquisto dell'utente {acquirente.id}",
        )
    except Exception:  # noqa: BLE001 - qualunque guasto qui si logga: non deve mai bloccare un acquisto
        logger.exception(
            "Commissione di referral non accreditata per l'acquisto dell'utente %s", acquirente_id,
        )


async def prezzo_del_credito(session: AsyncSession) -> Optional[Tuple[int, int]]:
    """(prezzo, crediti) del pacchetto più economico in vendita: il cambio fra euro e crediti della commissione."""
    pacchetto = (await session.execute(
        select(Plan)
        .where(Plan.tipo == "pacchetto", Plan.active.is_(True), Plan.price_monthly > 0, Plan.credits_per_period > 0)
        .order_by(Plan.price_monthly, Plan.credits_per_period.desc())
        .limit(1)
    )).scalar_one_or_none()
    if pacchetto is None:
        return None
    return pacchetto.price_monthly, pacchetto.credits_per_period


def crediti_della_commissione(importo_pagato: int, percentuale: int, prezzo: int, crediti: int) -> int:
    """`percentuale`% di `importo_pagato` in crediti, al prezzo per credito `prezzo / crediti`, all'unità più vicina
    (mezza unità per eccesso). Conti interi: niente virgola mobile sul denaro."""
    numeratore = int(importo_pagato) * int(percentuale) * int(crediti)
    denominatore = 100 * int(prezzo)
    if numeratore <= 0 or denominatore <= 0:
        return 0
    return (2 * numeratore + denominatore) // (2 * denominatore)


async def commissione_da_abbonamento(
    session: AsyncSession, acquirente_id: int, importo_pagato: Optional[int], *, riferimento: str = "",
) -> int:
    """La commissione su un periodo di abbonamento pagato (Fase 2b): una percentuale dell'importo, in crediti.

    Si chiama a ogni incasso di un abbonamento: il primo periodo (anche quello di un upgrade, sul conguaglio
    pagato), ogni rinnovo, la conversione di una prova. Una prova gratuita non paga, e con importo zero non c'è niente.
    Restituisce i crediti accreditati (0 se nessuno). Come l'altra, non fa mai fallire l'incasso.
    """
    if not importo_pagato or importo_pagato <= 0:
        return 0
    try:
        acquirente = await session.get(User, acquirente_id)
        if acquirente is None or acquirente.referred_by is None:
            return 0
        referente = await session.get(User, acquirente.referred_by)
        if referente is None or referente.deleted_at is not None:
            return 0

        from ..domain.impostazioni_repositories import correnti as impostazioni_correnti

        percentuale = (await impostazioni_correnti(session)).commissione_referral_percentuale
        cambio = await prezzo_del_credito(session)
        if cambio is None:
            logger.warning(
                "Commissione sull'abbonamento dell'utente %s non accreditata: nessun pacchetto in vendita per il cambio",
                acquirente_id,
            )
            return 0
        crediti = crediti_della_commissione(importo_pagato, percentuale, *cambio)
        if crediti <= 0:
            return 0
        await RegistroCrediti(session).accredita(
            referente.id, crediti, reason="omaggio",
            note=f"commissione {percentuale}% sull'acquisto dell'utente {acquirente.id}",
        )
        return crediti
    except Exception:  # noqa: BLE001 - qualunque guasto qui si logga: non deve mai bloccare un incasso
        logger.exception(
            "Commissione di referral non accreditata per l'abbonamento dell'utente %s (%s)", acquirente_id, riferimento,
        )
        return 0
