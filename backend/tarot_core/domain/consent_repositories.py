"""Lettura e scrittura dei consensi GDPR (v7, Fase G; granulari e con lo storico dalla Fase 1 del GDPR)."""
from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..tarot.ip_protetto import proteggi
from .consent_models import ConsensoStorico, UserConsent
from .repositories import AuditRepository


async def correnti_per(
    session: AsyncSession, *, user_id: Optional[int], anon_id: Optional[str],
) -> dict[str, UserConsent]:
    """I consensi attuali di questa persona (loggata o anonima), per tipo."""
    if user_id is not None:
        condizione = UserConsent.user_id == user_id
    elif anon_id is not None:
        condizione = UserConsent.anon_id == anon_id
    else:
        return {}
    righe = (await session.execute(select(UserConsent).where(condizione))).scalars()
    return {r.tipo: r for r in righe}


async def accettato(session: AsyncSession, user_id: Optional[int], tipo: str) -> bool:
    """Vero solo con un «accettato» esplicito: un consenso mai dato vale come rifiutato (art. 7, art. 9.2.a)."""
    if user_id is None:
        return False
    valore = (await session.execute(
        select(UserConsent.valore).where(UserConsent.user_id == user_id, UserConsent.tipo == tipo)
    )).scalar_one_or_none()
    return valore == "accettato"


def annota_storico(
    session: AsyncSession, *,
    user_id: Optional[int], anon_id: Optional[str], tipo: str, valore: str,
    versione_informativa: str, origine: str = "web", ip: Optional[str] = None,
) -> ConsensoStorico:
    """Una riga dello storico (append-only). L'IP si tronca e se ne tiene l'impronta, mai l'intero."""
    troncato, impronta = proteggi(ip)
    voce = ConsensoStorico(
        user_id=user_id, anon_id=anon_id if user_id is None else None, tipo=tipo, valore=valore,
        versione_informativa=versione_informativa, origine=origine, ip=troncato, ip_hash=impronta,
    )
    session.add(voce)
    return voce


async def registra(
    session: AsyncSession, *,
    user_id: Optional[int], anon_id: Optional[str], tipo: str, valore: str,
    versione_informativa: str, ip: Optional[str], origine: str = "web",
) -> UserConsent:
    """Scrive lo stato corrente del consenso (sovrascrive se già presente), una riga nello storico e un evento di
    audit.

    Esattamente uno fra `user_id`/`anon_id` deve essere valorizzato: lo garantisce il chiamante
    (l'endpoint pubblico), non questa funzione — qui si assume già validato, come per
    `Reading.owner_id`/`Reading.anon_id`.
    """
    if user_id is not None:
        riga = (await session.execute(
            select(UserConsent).where(UserConsent.user_id == user_id, UserConsent.tipo == tipo)
        )).scalar_one_or_none()
    else:
        riga = (await session.execute(
            select(UserConsent).where(UserConsent.anon_id == anon_id, UserConsent.tipo == tipo)
        )).scalar_one_or_none()

    if riga is None:
        riga = UserConsent(user_id=user_id, anon_id=anon_id, tipo=tipo)
        session.add(riga)
    troncato, impronta = proteggi(ip)
    riga.valore = valore
    riga.versione_informativa = versione_informativa
    riga.ip = troncato
    riga.ip_hash = impronta
    riga.origine = origine
    # `updated_at` lo calcola il database (`onupdate=func.now()` in TimestampMixin), mai Python:
    # con più repliche dell'API l'orologio del database è l'unico riferimento condiviso.

    annota_storico(
        session, user_id=user_id, anon_id=anon_id, tipo=tipo, valore=valore,
        versione_informativa=versione_informativa, origine=origine, ip=ip,
    )
    await AuditRepository(session).record(
        action=f"consenso.{tipo}", actor_id=user_id,
        target_type="consenso", target_id=str(user_id) if user_id is not None else anon_id,
        after={"valore": valore, "versione_informativa": versione_informativa, "origine": origine},
        ip=ip,
    )
    return riga


async def storico_di(
    session: AsyncSession, *, user_id: Optional[int], anon_id: Optional[str] = None, tipi: Optional[Iterable[str]] = None,
) -> list[ConsensoStorico]:
    """Lo storico delle scelte di questa persona, dalla più vecchia (per l'esportazione e il profilo)."""
    if user_id is not None:
        condizione = ConsensoStorico.user_id == user_id
    elif anon_id is not None:
        condizione = ConsensoStorico.anon_id == anon_id
    else:
        return []
    query = select(ConsensoStorico).where(condizione).order_by(ConsensoStorico.created_at, ConsensoStorico.id)
    if tipi is not None:
        query = query.where(ConsensoStorico.tipo.in_(list(tipi)))
    return list((await session.execute(query)).scalars())


async def trasferisci_anonimi(session: AsyncSession, *, anon_id: str, user_id: int) -> int:
    """Al primo accesso, le scelte fatte da anonimo con lo stesso cookie diventano dell'account, se l'account non ne
    ha già una sua per quel tipo: chi ha rifiutato le statistiche nel banner non deve ritrovarsele chieste (o peggio,
    attive) appena entra. Lo storico resta com'era, con l'`anon_id`: è la prova di quella scelta, fatta allora così.
    Restituisce quante ne ha trasferite."""
    anonime = await correnti_per(session, user_id=None, anon_id=anon_id)
    if not anonime:
        return 0
    proprie = await correnti_per(session, user_id=user_id, anon_id=None)
    spostate = 0
    for tipo, riga in anonime.items():
        if tipo in proprie:
            continue
        session.add(UserConsent(
            user_id=user_id, anon_id=None, tipo=tipo, valore=riga.valore,
            versione_informativa=riga.versione_informativa, ip=riga.ip, ip_hash=riga.ip_hash, origine=riga.origine,
        ))
        spostate += 1
    return spostate
