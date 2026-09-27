"""La commissione di referral: una quota di ogni acquisto futuro di un invitato, per chi lo ha invitato.

Diverso dal regalo di benvenuto (`ImpostazioniCrediti.crediti_iscrizione`/`crediti_invito`, una tantum
all'iscrizione, in `auth/dependencies.py` e `api/routers/profile.py`): questa gira **a ogni acquisto vero** —
un pacchetto, il primo periodo di un abbonamento, ogni rinnovo — per tutta la vita dell'account invitato, non solo
alla prima volta. La percentuale è in `ImpostazioniCrediti.commissione_referral_percentuale` (console).

**Non deve mai poter far fallire un acquisto.** Chi ha invitato può aver cancellato l'account nel frattempo (o
non essere mai esistito per un errore altrove): l'acquisto di chi è stato invitato deve comunque completarsi. Per
questo l'intera funzione è avvolta in un `try/except` che logga e basta — è la stessa ragione per cui un log non
interrompe mai una richiesta.
"""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import User
from .credits import RegistroCrediti

logger = logging.getLogger(__name__)


async def commissione_da_acquisto(session: AsyncSession, acquirente_id: int, crediti_concessi: int) -> None:
    """Accredita a chi ha invitato `acquirente_id` la sua quota dei crediti appena concessi, se c'è ancora.

    Va chiamata **dopo** che i crediti dell'acquisto sono già stati accreditati al compratore (pacchetto, primo
    periodo di un abbonamento, un rinnovo): `crediti_concessi` è quel numero, non l'importo pagato — la
    commissione è sui crediti, non sui soldi.
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
