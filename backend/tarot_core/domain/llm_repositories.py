"""I fornitori LLM: la lettura che li trasforma in modelli utilizzabili, e la loro forma pubblica.

Il CRUD vero e proprio (validazione, audit) sta nel router `api/routers/admin_llm.py`, come per le offerte
(`admin_offerte.py`): qui restano solo le funzioni che servono anche fuori da un endpoint di scrittura — la lettura
usata dal registro dei modelli a ogni rinfresco, e la serializzazione senza chiave che sia il router sia l'audit
possono riusare.

Le chiavi non lasciano mai questo file in chiaro verso l'esterno: `pubblico()` le riduce a `has_key: bool`, ed è la
sola forma che un endpoint di lettura può restituire. Solo `modelli_da_db()` le decifra, e il risultato resta
in-process (diventa un `ModelloConfigurato` da cui si costruisce il fornitore che parla con l'LLM).
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..llm.cifratura import decifra
from ..llm.compiti import ModelloConfigurato
from .config_models import LlmProvider


def pubblico(f: LlmProvider) -> Dict[str, Any]:
    """La riga senza la chiave: quello che un endpoint (o un record di audit) può conservare."""
    return {
        "id": f.id, "nome": f.nome, "tipo": f.tipo, "provider": f.provider,
        "base_url": f.base_url, "model": f.model, "embed_model": f.embed_model,
        "has_key": f.api_key_cifrata is not None,
        "motore": f.motore, "ragiona": f.ragiona, "parametri": f.parametri or {},
        "senza_filtri": f.senza_filtri, "descrizione": f.descrizione, "attivo": f.attivo,
        "aggiornato": f.updated_at.isoformat() if f.updated_at else None,
    }


async def fornitori_correnti(session: AsyncSession) -> Sequence[LlmProvider]:
    """Tutti i fornitori, attivi e no: serve alla console, che li mostra entrambi."""
    return (await session.execute(select(LlmProvider).order_by(LlmProvider.nome))).scalars().all()


async def modelli_da_db(session: AsyncSession) -> List[ModelloConfigurato]:
    """I fornitori attivi, come modelli utilizzabili (chiave decifrata, solo in-process).

    Vuoto se la tabella non ha righe attive: chi chiama ricade su `modelli_da_impostazioni()`, l'elenco ricavato
    dall'ambiente — così un impianto appena installato, senza ancora un fornitore in console, non smette di
    funzionare se prima girava con `TAROT_MODELLI` o `TAROT_LLM_*`.
    """
    righe = (
        await session.execute(select(LlmProvider).where(LlmProvider.attivo.is_(True)).order_by(LlmProvider.nome))
    ).scalars().all()
    return [
        ModelloConfigurato(
            nome=f.nome, provider=f.provider, base_url=f.base_url, model=f.model,
            embed_model=f.embed_model, api_key=decifra(f.api_key_cifrata), ragiona=f.ragiona, motore=f.motore,
            parametri=f.parametri or {}, descrizione=f.descrizione, senza_filtri=f.senza_filtri,
        )
        for f in righe
    ]
