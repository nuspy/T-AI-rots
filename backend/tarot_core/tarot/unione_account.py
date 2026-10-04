"""L'unione degli account da confermare: «l'account che c'era con la tua email era tuo?».

Il collegamento lo fa Keycloak, al primo accesso con un social che garantisce l'email (passo
`tarots-unione-sicura`, `deploy/keycloak/spi`). Se l'utente che aveva già quell'email non l'aveva mai verificata,
potrebbe averlo creato chiunque: prima di collegare, Keycloak gli toglie i vecchi accessi (password, OTP, social non
fidati, sessioni) e lo scrive in una nota della sessione, che arriva qui come claim `tarots_unione`:
`istante|creato|credenziali|social` (secondi Unix; liste separate da virgole).

Il sito allora chiede alla persona:

- **è mio** → niente da fare, l'account resta com'è (con la password nuova, se la sceglie);
- **non è mio** → ciò che c'era (letture, memorie, crediti, ordini) era di qualcun altro: si **separa** in una riga
  disattivata (mai cancellata: gli acquisti restano per la contabilità), e la persona riparte con un account nuovo.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.billing_models import CreditEntry
from ..domain.memory_models import UserMemory
from ..domain.models import Reading, User
from ..domain.ordini_models import Ordine

#: Il claim (e la nota della sessione Keycloak) con cosa è stato tolto.
CLAIM = "tarots_unione"
#: Il prefisso della `keycloak_sub` di una riga separata: non corrisponde più a nessun utente di Keycloak.
PREFISSO_SEPARATO = "separato:"


def _istante(testo: str) -> Optional[str]:
    try:
        return datetime.fromtimestamp(int(testo), tz=timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def leggi_nota(claims: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """La nota del claim, o None se non c'è o non si capisce (meglio non chiedere niente che chiedere a vuoto)."""
    testo = claims.get(CLAIM)
    if not isinstance(testo, str) or testo.count("|") != 3:
        return None
    istante, creato, credenziali, social = testo.split("|")
    il = _istante(istante)
    if il is None:
        return None
    return {
        "id": istante[:40],
        "il": il,
        "creato_il": _istante(creato) if creato else None,
        "credenziali": [c for c in credenziali.split(",") if c],
        "social": [s for s in social.split(",") if s],
    }


def registra(user: User, claims: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Annota la domanda se il token porta una nota nuova. Restituisce quella in attesa (nuova o di prima)."""
    nota = leggi_nota(claims)
    if nota is not None and nota["id"] != user.unione_risolta:
        if (user.unione_in_attesa or {}).get("id") != nota["id"]:
            user.unione_in_attesa = nota
    return user.unione_in_attesa


async def attivita(session: AsyncSession, user: User) -> Dict[str, Any]:
    """Cosa contiene l'account, per decidere se era proprio: senza letture, memorie e acquisti è «vuoto»."""

    async def conta(stmt) -> int:
        return int((await session.execute(stmt)).scalar_one() or 0)

    letture = await conta(select(func.count()).select_from(Reading).where(Reading.owner_id == user.id))
    memorie = await conta(select(func.count()).select_from(UserMemory).where(UserMemory.owner_id == user.id))
    # Più le voci dello stato sintetico della memoria (`tarot/stato_memoria.py`).
    from ..domain import memoria_repositories

    memorie += len(await memoria_repositories.stato_di(session, user.id))
    ordini = await conta(select(func.count()).select_from(Ordine).where(Ordine.user_id == user.id))
    acquisti = await conta(
        select(func.count()).select_from(CreditEntry)
        .where(CreditEntry.user_id == user.id, CreditEntry.reason == "acquisto")
    )
    crediti = await conta(select(func.coalesce(func.sum(CreditEntry.delta), 0)).where(CreditEntry.user_id == user.id))
    return {
        "letture": letture, "memorie": memorie, "ordini": ordini, "acquisti": acquisti, "crediti": crediti,
        "vuoto": letture == 0 and memorie == 0 and ordini == 0 and acquisti == 0,
        "iscritto_il": user.created_at.isoformat() if user.created_at else None,
    }


def separa(user: User) -> str:
    """Stacca la riga dall'identità di Keycloak e la disattiva: la prossima `ensure` con lo stesso token crea un
    utente nuovo. Restituisce la `keycloak_sub` data alla riga separata."""
    nuova = f"{PREFISSO_SEPARATO}{uuid.uuid4().hex}"
    user.keycloak_sub = nuova
    user.deleted_at = utcnow()
    user.unione_in_attesa = None
    return nuova


def risolvi(user: User, nota: Dict[str, Any]) -> None:
    user.unione_risolta = str(nota.get("id") or "")[:40] or None
    user.unione_in_attesa = None


def tolti(nota: Dict[str, Any]) -> List[str]:
    return list(nota.get("credenziali") or []) + list(nota.get("social") or [])
