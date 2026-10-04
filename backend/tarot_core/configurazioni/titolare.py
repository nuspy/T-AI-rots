"""I dati del titolare del trattamento, per l'informativa privacy del sito (v9, Fase 2c).

L'operatore li scrive in console (Impostazioni → Dati del titolare); il sito li legge da `GET /privacy/titolare` e li
mette al posto dei segnaposto in tutte le lingue. Sono dati pubblici (stanno nell'informativa): nessun segreto.

L'elenco dei **fornitori di intelligenza artificiale** non si scrive a mano: si ricava dai fornitori LLM attivi in
console (`llm_providers`), con l'azienda e il paese dal catalogo (`llm/catalogo_fornitori.SEDI`). Così l'informativa
dice la verità anche il giorno in cui si cambia fornitore. Un fornitore «generico» (un indirizzo qualunque) compare
col nome che gli ha dato l'operatore, senza paese.
"""
from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.configurazioni_models import EMAIL_PRIVACY_PREDEFINITA, HOSTING_PREDEFINITO, ConfigTitolare


async def riga(session: AsyncSession) -> ConfigTitolare:
    """La riga (creata con i valori predefiniti se manca; il commit lo fa chi scrive)."""
    trovata = await session.get(ConfigTitolare, 1)
    if trovata is None:
        trovata = ConfigTitolare(id=1, email_privacy=EMAIL_PRIVACY_PREDEFINITA, hosting=HOSTING_PREDEFINITO)
        session.add(trovata)
        await session.flush()
    return trovata


def json_admin(r: ConfigTitolare) -> Dict[str, Any]:
    return {
        "nome": r.nome, "indirizzo": r.indirizzo, "codice_fiscale": r.codice_fiscale, "email_privacy": r.email_privacy,
        "dpo_nominato": r.dpo_nominato, "dpo_contatto": r.dpo_contatto, "hosting": r.hosting,
        "aggiornato_il": r.updated_at.isoformat() if r.updated_at else None,
    }


async def fornitori_ai(session: AsyncSession) -> List[Dict[str, Any]]:
    """I fornitori LLM attivi, uno per azienda: `{"nome", "paese", "proprio"}` (paese ISO o `None`)."""
    from ..domain.config_models import LlmProvider
    from ..llm.catalogo_fornitori import CATALOGO, SEDI

    righe = (await session.execute(
        select(LlmProvider).where(LlmProvider.attivo.is_(True)).order_by(LlmProvider.nome)
    )).scalars().all()
    visti: Dict[str, Dict[str, Any]] = {}
    for f in righe:
        sede = SEDI.get(f.tipo)
        nome = (sede["azienda"] if sede and sede["azienda"] else None) \
            or (CATALOGO[f.tipo]["label"] if f.tipo in CATALOGO and f.tipo != "openai_compat" else None) \
            or f.descrizione or f.nome
        if nome in visti:
            continue
        visti[nome] = {"nome": nome, "paese": (sede["paese"] if sede else "") or None,
                       "proprio": bool(sede and sede["proprio"])}
    return list(visti.values())


async def json_pubblico(session: AsyncSession) -> Dict[str, Any]:
    """Ciò che l'informativa mostra. I campi vuoti sono `None`: il sito scrive al loro posto un testo neutro."""
    r = await session.get(ConfigTitolare, 1)
    nome = (r.nome if r else "").strip()
    return {
        "nome": nome or None,
        "indirizzo": (r.indirizzo if r else "").strip() or None,
        "codice_fiscale": (r.codice_fiscale if r else "").strip() or None,
        "email_privacy": ((r.email_privacy if r else EMAIL_PRIVACY_PREDEFINITA) or "").strip() or None,
        "dpo": {
            "nominato": bool(r and r.dpo_nominato),
            "contatto": ((r.dpo_contatto if r else "") or "").strip() or None,
        },
        "hosting": ((r.hosting if r else HOSTING_PREDEFINITO) or "").strip() or None,
        "fornitori_ai": await fornitori_ai(session),
    }
