"""I numeri del regalo d'iscrizione e del referral: lettura (con creazione al bisogno) e scrittura con audit.

Una riga sola (`ImpostazioniCrediti`, id fisso a 1): `correnti()` la crea con i valori di default se ancora non
esiste, così la console ha sempre qualcosa da mostrare e da modificare senza un passo di inizializzazione a parte.
"""
from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from .config_models import ImpostazioniChat, ImpostazioniCrediti
from .repositories import AuditRepository

ID_RIGA = 1


async def correnti(session: AsyncSession) -> ImpostazioniCrediti:
    """La riga delle impostazioni, creandola con i valori di default se manca."""
    riga = await session.get(ImpostazioniCrediti, ID_RIGA)
    if riga is None:
        riga = ImpostazioniCrediti(id=ID_RIGA)
        session.add(riga)
        await session.flush()
    return riga


def pubblico(riga: ImpostazioniCrediti) -> Dict[str, int]:
    return {
        "crediti_iscrizione": riga.crediti_iscrizione,
        "crediti_invito": riga.crediti_invito,
        "commissione_referral_percentuale": riga.commissione_referral_percentuale,
    }


async def aggiorna(
    session: AsyncSession, campi: Dict[str, Any], *, attore_id: int, ip: str | None = None,
) -> ImpostazioniCrediti:
    """Aggiorna solo i campi presenti in `campi`; registra il prima/dopo nell'audit."""
    riga = await correnti(session)
    prima = pubblico(riga)

    for campo in ("crediti_iscrizione", "crediti_invito", "commissione_referral_percentuale"):
        if campo in campi and campi[campo] is not None:
            setattr(riga, campo, int(campi[campo]))
    riga.updated_by = attore_id

    dopo = pubblico(riga)
    if prima != dopo:
        await AuditRepository(session).record(
            action="impostazioni_credito.modifica", actor_id=attore_id, target_type="impostazioni_credito",
            target_id=str(ID_RIGA), before=prima, after=dopo, ip=ip,
        )
    return riga


# ---- chat proattiva (v6, Fase E) -------------------------------------------------------------------


async def correnti_chat(session: AsyncSession) -> ImpostazioniChat:
    riga = await session.get(ImpostazioniChat, ID_RIGA)
    if riga is None:
        riga = ImpostazioniChat(id=ID_RIGA)
        session.add(riga)
        await session.flush()
    return riga


def pubblico_chat(riga: ImpostazioniChat) -> Dict[str, int]:
    return {"proattiva_minuti_inattivita": riga.proattiva_minuti_inattivita}


async def aggiorna_chat(
    session: AsyncSession, campi: Dict[str, Any], *, attore_id: int, ip: str | None = None,
) -> ImpostazioniChat:
    riga = await correnti_chat(session)
    prima = pubblico_chat(riga)

    if "proattiva_minuti_inattivita" in campi and campi["proattiva_minuti_inattivita"] is not None:
        riga.proattiva_minuti_inattivita = int(campi["proattiva_minuti_inattivita"])
    riga.updated_by = attore_id

    dopo = pubblico_chat(riga)
    if prima != dopo:
        await AuditRepository(session).record(
            action="impostazioni_chat.modifica", actor_id=attore_id, target_type="impostazioni_chat",
            target_id=str(ID_RIGA), before=prima, after=dopo, ip=ip,
        )
    return riga
