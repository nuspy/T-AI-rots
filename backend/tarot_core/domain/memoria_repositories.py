"""Letture e scritture su `user_memories` e sullo stato sintetico (`memoria_stato`, in fondo al file): ogni funzione
filtra per `owner_id`, mai delegato al chiamante
(vedi il vincolo di `OwnedMixin` — qui non ereditato per la non-nullabilità, ma lo stesso principio vale).
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, Iterable, List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..tarot.memoria_retrieval import CandidatoMemoria, similarita_coseno
from .memory_models import MemoriaStato, UserMemory

#: Sopra questa similarità, una nuova memoria STABILE è considerata lo stesso fatto già noto nello
#: stesso campo: si scarta invece di duplicarlo (l'esempio del backlog: "manca una gamba" non deve
#: riscriversi a ogni lettura in cui il tema fisico riemerge).
SOGLIA_DUPLICATO_STABILE = 0.92


async def candidati_per(session: AsyncSession, owner_id: int) -> List[CandidatoMemoria]:
    """Tutte le memorie correnti dell'utente (non sostituite), pronte per il ranking in `rilevanti()`.

    Niente `LIMIT`/`ORDER BY` per similarità qui: senza un indice vettoriale nativo (vedi
    `memory_models.py`), il filtro utile è solo «di questo utente, non superata» — il ranking vero
    lo fa `rilevanti()` in Python sull'insieme così ottenuto.
    """
    righe = (
        await session.execute(
            select(UserMemory).where(
                UserMemory.owner_id == owner_id,
                UserMemory.superseded_by.is_(None),
            )
        )
    ).scalars()
    return [
        CandidatoMemoria(
            id=r.id, contenuto=r.contenuto, tipo=r.tipo,
            campo_attinenza=r.campo_attinenza, embedding=r.embedding,
        )
        for r in righe
    ]


async def piu_recenti(session: AsyncSession, owner_id: int, *, limite: int = 5) -> List[UserMemory]:
    """Le ultime memorie aggiornate (v6, Fase E): per la chat proattiva, che non ha una domanda
    specifica da vettorizzare come query — a differenza dell'apertura di una lettura (`rilevanti()`
    in `tarot/memoria_retrieval.py`), qui il criterio è solo la recenza."""
    righe = (
        await session.execute(
            select(UserMemory)
            .where(UserMemory.owner_id == owner_id, UserMemory.superseded_by.is_(None))
            .order_by(UserMemory.updated_at.desc())
            .limit(limite)
        )
    ).scalars()
    return list(righe)


async def elenca(session: AsyncSession, owner_id: int) -> List[UserMemory]:
    """Le memorie correnti dell'utente, per la sezione "Memoria" del profilo (Fase D)."""
    righe = (
        await session.execute(
            select(UserMemory)
            .where(UserMemory.owner_id == owner_id, UserMemory.superseded_by.is_(None))
            .order_by(UserMemory.updated_at.desc())
        )
    ).scalars()
    return list(righe)


async def per_id(session: AsyncSession, owner_id: int, memoria_id: uuid.UUID) -> Optional[UserMemory]:
    riga = await session.get(UserMemory, memoria_id)
    return riga if riga is not None and riga.owner_id == owner_id else None


async def catena(session: AsyncSession, owner_id: int, memoria_id: uuid.UUID) -> List[UserMemory]:
    """Una memoria variabile e le versioni che ha sostituito, dalla più vecchia alla più recente.

    Serve al confronto prima/dopo della sintesi (Fase C): senza la catena, «la situazione è
    cambiata rispetto all'ultima volta» non avrebbe un "prima" con cui confrontarsi.
    """
    corrente = await per_id(session, owner_id, memoria_id)
    if corrente is None:
        return []
    catena_righe = [corrente]
    righe = (
        await session.execute(
            select(UserMemory).where(UserMemory.owner_id == owner_id, UserMemory.superseded_by.isnot(None))
        )
    ).scalars()
    per_predecessore = {r.superseded_by: r for r in righe}
    # Risale la catena partendo dalla testa: ogni riga sostituita punta a chi l'ha sostituita, non
    # il contrario, quindi si cerca chi ha `superseded_by == id` della riga corrente.
    cursore = corrente
    visitati = {cursore.id}
    while True:
        precedente = next((r for r in per_predecessore.values() if r.superseded_by == cursore.id), None)
        if precedente is None or precedente.id in visitati:
            break
        catena_righe.append(precedente)
        visitati.add(precedente.id)
        cursore = precedente
    return list(reversed(catena_righe))


async def elimina(session: AsyncSession, owner_id: int, memoria_id: uuid.UUID) -> bool:
    riga = await per_id(session, owner_id, memoria_id)
    if riga is None:
        return False
    await session.delete(riga)
    return True


async def elimina_molte(session: AsyncSession, owner_id: int, ids: Sequence[uuid.UUID]) -> int:
    righe = [r for r in await elenca(session, owner_id) if r.id in set(ids)]
    for riga in righe:
        await session.delete(riga)
    return len(righe)


async def scrivi_o_fondi(
    session: AsyncSession,
    owner_id: int,
    *,
    contenuto: str,
    tipo: str,
    campo_attinenza: str,
    embedding: Sequence[float],
    reading_id: Optional[uuid.UUID] = None,
    fonte: str = "lettura",
) -> Optional[UserMemory]:
    """Scrive una memoria nuova, o la fonde con quelle esistenti sullo stesso campo di attinenza.

    STABILE: se una memoria stabile semanticamente vicina esiste già nello stesso campo, si scarta
    (`None`) invece di duplicarla. VARIABILE: sostituisce l'eventuale variabile corrente sullo stesso
    campo — la vecchia riceve `superseded_by`, resta interrogabile per il confronto prima/dopo, non
    più fra i candidati del retrieval (Fase A).
    """
    correnti = [c for c in await candidati_per(session, owner_id) if c.campo_attinenza == campo_attinenza]

    if tipo == "stabile":
        for c in correnti:
            if c.tipo == "stabile" and similarita_coseno(c.embedding, embedding) >= SOGLIA_DUPLICATO_STABILE:
                return None
        nuova = UserMemory(
            owner_id=owner_id, contenuto=contenuto, tipo=tipo, campo_attinenza=campo_attinenza,
            embedding=list(embedding), reading_id=reading_id, fonte=fonte,
        )
        session.add(nuova)
        return nuova

    precedente_id = next((c.id for c in correnti if c.tipo == "variabile"), None)
    nuova = UserMemory(
        owner_id=owner_id, contenuto=contenuto, tipo=tipo, campo_attinenza=campo_attinenza,
        embedding=list(embedding), reading_id=reading_id, fonte=fonte,
    )
    session.add(nuova)
    if precedente_id is not None:
        await session.flush()  # serve nuova.id, assegnato dal default Python solo dopo il flush
        precedente = await per_id(session, owner_id, precedente_id)
        if precedente is not None:
            precedente.superseded_by = nuova.id
    return nuova


async def elimina_tutte(session: AsyncSession, owner_id: int) -> int:
    righe = (
        await session.execute(select(UserMemory).where(UserMemory.owner_id == owner_id))
    ).scalars().all()
    for riga in righe:
        await session.delete(riga)
    return len(righe)


# ---- lo stato sintetico (`tarot/stato_memoria.py`) ----------------------------------------------------------------


async def stato_di(session: AsyncSession, owner_id: int, *, lock: bool = False) -> List[Dict[str, Any]]:
    """Le voci dello stato sintetico di una persona (validate), o un elenco vuoto."""
    from ..tarot.stato_memoria import valida

    query = select(MemoriaStato).where(MemoriaStato.user_id == owner_id)
    if lock:
        query = query.with_for_update()
    riga = (await session.execute(query)).scalar_one_or_none()
    return valida(riga.voci) if riga is not None else []


async def salva_stato(session: AsyncSession, owner_id: int, voci: Sequence[Dict[str, Any]]) -> None:
    """Scrive lo stato (crea la riga se manca). Un elenco vuoto lascia la riga, vuota: «non ricordo nulla»."""
    riga = await session.get(MemoriaStato, owner_id)
    if riga is None:
        session.add(MemoriaStato(user_id=owner_id, voci=list(voci)))
    else:
        riga.voci = list(voci)
    await session.flush()


async def elimina_stato(session: AsyncSession, owner_id: int) -> int:
    """Cancella tutto lo stato di una persona. Restituisce quante voci c'erano."""
    riga = await session.get(MemoriaStato, owner_id)
    if riga is None:
        return 0
    quante = len(riga.voci or [])
    await session.delete(riga)
    return quante


async def converti_in_stato(session: AsyncSession, owner_id: int, *, salute_ammessa: bool = False) -> int:
    """Una tantum: le memorie correnti di `user_memories` diventano voci dello stato (unite a quelle che ci sono già,
    senza doppioni). Le memorie di prima restano dove sono finché non le si cancella. Restituisce le voci aggiunte."""
    from datetime import date

    from ..tarot.stato_memoria import da_memorie, dimentica

    attuali = await stato_di(session, owner_id, lock=True)
    testi = {v["testo"].strip().lower() for v in attuali}
    nuove = [v for v in da_memorie(await elenca(session, owner_id), salute_ammessa=salute_ammessa)
             if v["testo"].strip().lower() not in testi]
    if not nuove:
        return 0
    await salva_stato(session, owner_id, dimentica(attuali + nuove, date.today()))
    return len(nuove)
