"""I numeri del regalo d'iscrizione e del referral: lettura (con creazione al bisogno) e scrittura con audit.

Una riga sola (`ImpostazioniCrediti`, id fisso a 1): `correnti()` la crea con i valori di default se ancora non
esiste, così la console ha sempre qualcosa da mostrare e da modificare senza un passo di inizializzazione a parte.
"""
from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from ..settings import get_settings
from .config_models import ImpostazioniChat, ImpostazioniCrediti, ImpostazioniIntervista
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
    return {
        "proattiva_minuti_inattivita": riga.proattiva_minuti_inattivita,
        "proattiva_max_per_visita": riga.proattiva_max_per_visita,
    }


async def aggiorna_chat(
    session: AsyncSession, campi: Dict[str, Any], *, attore_id: int, ip: str | None = None,
) -> ImpostazioniChat:
    riga = await correnti_chat(session)
    prima = pubblico_chat(riga)

    if "proattiva_minuti_inattivita" in campi and campi["proattiva_minuti_inattivita"] is not None:
        riga.proattiva_minuti_inattivita = int(campi["proattiva_minuti_inattivita"])
    if "proattiva_max_per_visita" in campi and campi["proattiva_max_per_visita"] is not None:
        riga.proattiva_max_per_visita = int(campi["proattiva_max_per_visita"])
    riga.updated_by = attore_id

    dopo = pubblico_chat(riga)
    if prima != dopo:
        await AuditRepository(session).record(
            action="impostazioni_chat.modifica", actor_id=attore_id, target_type="impostazioni_chat",
            target_id=str(ID_RIGA), before=prima, after=dopo, ip=ip,
        )
    return riga


# La sessione (login persistente) non ha più una riga qui: la console legge e scrive le durate direttamente su
# Keycloak (`api/routers/admin_impostazioni.py`), che ne è l'unica fonte. Vedi `config_models.ImpostazioniSessione`.


# ---- intervista (v8.5) -----------------------------------------------------------------------------


async def correnti_intervista(session: AsyncSession) -> ImpostazioniIntervista:
    """La riga dell'intervista, creata coi valori di `settings` se manca (così il primo avvio non cambia nulla)."""
    riga = await session.get(ImpostazioniIntervista, ID_RIGA)
    if riga is None:
        s = get_settings()
        minimo = max(0, s.intervista_min_domande)
        riga = ImpostazioniIntervista(id=ID_RIGA, min_domande=minimo,
                                      max_domande=max(minimo, 1, s.intervista_max_domande))
        session.add(riga)
        await session.flush()
    return riga


#: I tre modi del validatore delle domande e della guardia del responso.
MODI_CONTROLLO = ("dubbi", "spento", "acceso")


def pubblico_intervista(riga: ImpostazioniIntervista) -> Dict[str, Any]:
    return {
        "min_domande": riga.min_domande, "max_domande": riga.max_domande,
        # Una riga appena creata in memoria non ha ancora i default del database: si dicono qui.
        "validatore_domande": riga.validatore_domande or "dubbi",
        "guardia_responso": riga.guardia_responso or "dubbi",
        "memoria_stato_nei_prompt": bool(riga.memoria_stato_nei_prompt),
        # v9.5: la prova della lettura in chat (una riga appena creata in memoria non ha ancora il default del database)
        "chat_percentuale": 90 if riga.chat_percentuale is None else riga.chat_percentuale,
    }


async def aggiorna_intervista(
    session: AsyncSession, campi: Dict[str, Any], *, attore_id: int, ip: str | None = None,
) -> ImpostazioniIntervista:
    """Aggiorna minimo e massimo, i modi dei controlli e la memoria nei prompt; il chiamante ha già controllato che il
    minimo non superi il massimo e che i modi siano fra `MODI_CONTROLLO`."""
    riga = await correnti_intervista(session)
    prima = pubblico_intervista(riga)
    for campo in ("min_domande", "max_domande"):
        if campo in campi and campi[campo] is not None:
            setattr(riga, campo, int(campi[campo]))
    for campo in ("validatore_domande", "guardia_responso"):
        if campi.get(campo) in MODI_CONTROLLO:
            setattr(riga, campo, campi[campo])
    if campi.get("memoria_stato_nei_prompt") is not None:
        riga.memoria_stato_nei_prompt = bool(campi["memoria_stato_nei_prompt"])
    if campi.get("chat_percentuale") is not None:
        riga.chat_percentuale = int(campi["chat_percentuale"])
    riga.updated_by = attore_id
    dopo = pubblico_intervista(riga)
    if prima != dopo:
        await AuditRepository(session).record(
            action="impostazioni_intervista.modifica", actor_id=attore_id, target_type="impostazioni_intervista",
            target_id=str(ID_RIGA), before=prima, after=dopo, ip=ip,
        )
    return riga
