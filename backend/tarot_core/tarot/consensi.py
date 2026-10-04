"""Ciò che una scelta sui consensi cambia nei dati, oltre alla scelta stessa (GDPR, Fase 1).

Un consenso revocato vale da subito anche per i dati già raccolti in base a quel consenso (art. 7.3, art. 17.1.b):

- `dati_particolari` (art. 9): la casella «persona trans» si spegne nella scheda e nel partner ricordato, e i ricordi
  sulla salute si cancellano. Le letture già fatte restano com'erano (sono il racconto di allora, e si cancellano
  dalla storia); da qui in poi niente di tutto questo arriva più al modello;
- `statistiche`: l'identificativo del browser lo dimentica il sito stesso (`/e/dimentica`, dal browser che lo ha);
- gli altri non hanno dati propri da togliere: smettono di valere e basta.

Le categorie particolari si riconoscono qui, in un posto solo: `campo_salute()` per le memorie, `trans_ammesso()` per
la casella.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.memory_models import UserMemory
from ..domain.models import User

#: Il campo di attinenza delle memorie che parlano di salute. Il modello lo sceglie fra quelli del prompt
#: (`tarot/memoria.py`, in italiano), ma può rispondere nella lingua della lettura: si riconoscono anche le traduzioni.
CAMPI_SALUTE = frozenset({
    "salute", "health", "salud", "saúde", "santé", "gesundheit", "egészség", "sănătate", "zdrowie",
    "здоровье", "здоров'я", "здоров’я", "健康", "건강", "स्वास्थ्य", "الصحة",
})


def campo_salute(campo: Optional[str]) -> bool:
    return (campo or "").strip().lower() in CAMPI_SALUTE


def trans_ammesso(dati_particolari: bool, valore: Any) -> bool:
    """La casella «persona trans» vale solo con il consenso alle categorie particolari."""
    return bool(valore) and dati_particolari


def senza_trans(persona: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not persona or not persona.get("trans"):
        return persona
    return {**persona, "trans": False}


async def dopo_la_scelta(session: AsyncSession, user: Optional[User], tipo: str, valore: str) -> Dict[str, int]:
    """Applica ai dati una scelta appena registrata. Restituisce cosa ha tolto (per l'audit e per i test)."""
    tolti: Dict[str, int] = {}
    if user is None or valore != "rifiutato":
        return tolti
    if tipo == "dati_particolari":
        if user.is_trans:
            user.is_trans = False
            tolti["trans"] = 1
        if (user.partner_ricordato or {}).get("trans"):
            user.partner_ricordato = senza_trans(user.partner_ricordato)
            tolti["partner_trans"] = 1
        esito = await session.execute(
            delete(UserMemory)
            .where(UserMemory.owner_id == user.id, func.lower(func.trim(UserMemory.campo_attinenza)).in_(sorted(CAMPI_SALUTE)))
        )
        if esito.rowcount:
            tolti["memorie_salute"] = int(esito.rowcount)
        # Lo stato sintetico della memoria (`tarot/stato_memoria.py`): via le voci sulla salute.
        from ..domain import memoria_repositories
        from .stato_memoria import senza_salute

        voci = await memoria_repositories.stato_di(session, user.id, lock=True)
        rimaste = senza_salute(voci)
        if len(rimaste) != len(voci):
            await memoria_repositories.salva_stato(session, user.id, rimaste)
            tolti["stato_memoria_salute"] = len(voci) - len(rimaste)
    return tolti
