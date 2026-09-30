"""Scritture amministrative, ciascuna col suo record di audit.

Ogni repository qui prende un `ContestoAmministrativo` — chi agisce e da
dove — e scrive nel registro nella stessa transazione dell'effetto: un'azione
senza traccia non può esistere, perché non c'è un metodo che la compia senza
lasciarla.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..llm.compiti import AssegnazioneModello
from .base import utcnow
from .config_models import ModelAssignment
from .models import AuditLog, User
from .repositories import AuditRepository

logger = logging.getLogger(__name__)


class ContestoAmministrativo:
    """Chi sta agendo e da dove. Accompagna ogni operazione.

    Esiste perché un record di audit senza autore e senza indirizzo è poco
    più di un log: la domanda a cui un registro deve rispondere è «chi», e
    dev'essere presente al momento dell'azione, non ricostruita dopo.
    """

    def __init__(
        self,
        attore: User,
        *,
        ip: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        self.attore = attore
        self.ip = ip
        self.correlation_id = correlation_id


class _ConAudit:
    """Base per i repository che devono lasciare traccia."""

    def __init__(self, session: AsyncSession, contesto: ContestoAmministrativo) -> None:
        self._session = session
        self._contesto = contesto
        self._audit = AuditRepository(session)

    async def _registra(
        self,
        azione: str,
        *,
        tipo: str,
        target_id: Any,
        prima: Optional[Dict[str, Any]] = None,
        dopo: Optional[Dict[str, Any]] = None,
    ) -> None:
        await self._audit.record(
            action=azione,
            actor_id=self._contesto.attore.id,
            target_type=tipo,
            target_id=str(target_id),
            before=prima,
            after=dopo,
            ip=self._contesto.ip,
            correlation_id=self._contesto.correlation_id,
        )


class AdminUserRepository(_ConAudit):
    """Gli utenti, visti dalla console."""

    async def cerca(
        self, *, testo: str = "", limite: int = 50, offset: int = 0,
        solo_attivi: bool = False,
    ) -> tuple[Sequence[User], int]:
        filtro = []
        if testo:
            modello = f"%{testo.lower()}%"
            filtro.append(or_(
                func.lower(User.email).like(modello),
                func.lower(User.display_name).like(modello),
                func.lower(User.referral_code) == testo.lower(),
            ))
        if solo_attivi:
            filtro.append(User.deleted_at.is_(None))
        totale = int(await self._session.scalar(
            select(func.count()).select_from(User).where(*filtro)
        ) or 0)
        righe = (await self._session.execute(
            select(User).where(*filtro).order_by(User.created_at.desc())
            .limit(limite).offset(offset)
        )).scalars().all()
        return righe, totale

    async def disattiva(self, utente: User) -> None:
        if utente.deleted_at is not None:
            return
        utente.deleted_at = utcnow()
        await self._registra(
            "user.disable", tipo="user", target_id=utente.id,
            prima={"attivo": True}, dopo={"attivo": False},
        )

    async def riattiva(self, utente: User) -> None:
        if utente.deleted_at is None:
            return
        utente.deleted_at = None
        await self._registra(
            "user.enable", tipo="user", target_id=utente.id,
            prima={"attivo": False}, dopo={"attivo": True},
        )


class RegistroAuditRepository:
    """Lettura del registro. Solo lettura: non c'è un metodo per modificarlo."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def recenti(
        self,
        *,
        limite: int = 100,
        offset: int = 0,
        azione: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> Sequence[AuditLog]:
        query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limite).offset(offset)
        if azione:
            query = query.where(AuditLog.action == azione)
        if target_type:
            query = query.where(AuditLog.target_type == target_type)
        return (await self._session.execute(query)).scalars().all()


class AssegnazioniModelliRepository(_ConAudit):
    """Quale modello serve quale compito.

    Scrive **solo il nome**: l'indirizzo e la chiave del modello stanno
    nell'ambiente, e questa tabella non li conosce. È ciò che rende
    innocuo dare a un amministratore il potere di cambiare assegnazione.
    """

    async def correnti(self) -> Dict[str, AssegnazioneModello]:
        righe = (await self._session.execute(select(ModelAssignment))).scalars()
        return {
            r.task: AssegnazioneModello(r.model_name, r.ragiona_override, r.parametri_override)
            for r in righe
        }

    async def assegna(
        self, compito: str, modello: Optional[str], *,
        ragiona: Optional[bool] = None, parametri_override: Optional[Dict[str, Any]] = None,
    ) -> Optional[AssegnazioneModello]:
        """Assegna un modello a un compito, o toglie l'assegnazione.

        `None` cancella la riga invece di scrivere il nome del predefinito:
        un compito senza riga *ricade* sul predefinito e continua a seguirlo
        se un giorno cambia, mentre un nome scritto resterebbe quello.

        `ragiona`/`parametri_override` (v7): `None` lascia il campo invariato per una riga già
        esistente (questa chiamata non tocca il reasoning, solo il modello) — **tranne** alla
        creazione di una riga nuova, dove `ragiona=None` diventa esplicitamente `False`: il
        backlog vuole il reasoning spento per default su ogni compito, non "eredita dal
        fornitore" per quelli non ancora toccati dall'amministratore.
        """
        riga = await self._session.get(ModelAssignment, compito)
        prima = (
            {"modello": riga.model_name, "ragiona": riga.ragiona_override, "parametri_override": riga.parametri_override}
            if riga else None
        )

        if modello is None:
            if riga is not None:
                await self._session.delete(riga)
            dopo = None
        else:
            if riga is None:
                riga = ModelAssignment(
                    task=compito, model_name=modello,
                    ragiona_override=False if ragiona is None else ragiona,
                )
                self._session.add(riga)
            else:
                riga.model_name = modello
                if ragiona is not None:
                    riga.ragiona_override = ragiona
            if parametri_override is not None:
                riga.parametri_override = parametri_override
            riga.updated_by = self._contesto.attore.id
            dopo = {"modello": modello, "ragiona": riga.ragiona_override, "parametri_override": riga.parametri_override}

        risultato = (
            AssegnazioneModello(riga.model_name, riga.ragiona_override, riga.parametri_override)
            if modello is not None else None
        )

        if prima == dopo:
            return risultato

        await self._registra(
            "modello.assegna", tipo="compito", target_id=compito,
            prima=prima, dopo=dopo,
        )
        return risultato


async def assegnazioni_correnti(session: AsyncSession) -> Dict[str, AssegnazioneModello]:
    """Le assegnazioni, senza contesto amministrativo.

    Serve a chi legge e basta: l'API a ogni rinfresco, il worker all'inizio
    di un lavoro. Il repository con l'audit serve a chi scrive.
    """
    righe = (await session.execute(select(ModelAssignment))).scalars()
    return {
        r.task: AssegnazioneModello(r.model_name, r.ragiona_override, r.parametri_override)
        for r in righe
    }
