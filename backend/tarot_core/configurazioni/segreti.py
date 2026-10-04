"""I segreti interni: generati al primo avvio, conservati cifrati, mai mostrati (v9, Fase 2c).

Due segreti che nessuno deve scegliere né vedere:

- `ip_hash`: la chiave dell'HMAC con cui si conserva l'impronta degli indirizzi IP (`tarot/ip_protetto.py`);
- `condivisione_sale`: il sale delle impronte anonime di chi apre un link condiviso (e, con separazione di dominio,
  dell'identificativo esteso degli analytics).

**La regola, per ognuno.** Se l'ambiente lo dà (`TAROT_IP_HASH_SECRET`, `TAROT_CONDIVISIONE_SALE`), vince l'ambiente,
e il valore si salva nel database: toglierlo un giorno dall'ambiente non cambia le impronte già scritte. Se l'ambiente
non lo dà, vale quello del database; se nemmeno quello c'è, se ne genera uno casuale e si salva. Con più repliche che
partono insieme vince la prima scrittura (`INSERT … ON CONFLICT DO NOTHING` sulla chiave primaria): tutte rileggono
lo stesso valore.

La risoluzione avviene all'avvio dell'API (`avvio.prepara`), prima della prima richiesta; i CronJob che ne hanno
bisogno chiamano `assicura_tutti`. Prima della risoluzione si usa l'ambiente, o un valore di sviluppo (solo prove).
"""
from __future__ import annotations

import logging
import secrets
from typing import Callable, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings import get_settings

logger = logging.getLogger(__name__)

SALE_SVILUPPO = "sale-di-sviluppo"

_sale: Optional[str] = None


def _imposta_sale(valore: Optional[str]) -> None:
    global _sale
    _sale = valore or None


def sale_condivisione() -> str:
    """Il sale in uso: quello risolto all'avvio; prima, l'ambiente; senza nemmeno quello, il valore di sviluppo."""
    return _sale or get_settings().condivisione_sale or SALE_SVILUPPO


def _imposta_ip(valore: Optional[str]) -> None:
    from ..tarot import ip_protetto

    ip_protetto.imposta_segreto(valore)


#: nome → (campo delle impostazioni, chi lo riceve nel processo).
SEGRETI: Dict[str, Tuple[str, Callable[[Optional[str]], None]]] = {
    "ip_hash": ("ip_hash_secret", _imposta_ip),
    "condivisione_sale": ("condivisione_sale", _imposta_sale),
}


async def assicura(session: AsyncSession, nome: str) -> str:
    """Risolve un segreto (ambiente → database → generato), lo salva se serve e lo mette in uso. Non fa il commit."""
    from ..domain.configurazioni_models import SegretoSistema
    from ..llm.cifratura import cifra, decifra

    campo, imposta = SEGRETI[nome]
    ambiente = (getattr(get_settings(), campo) or "").strip()
    riga = await session.get(SegretoSistema, nome)
    if ambiente:
        if riga is None:
            await session.execute(insert(SegretoSistema).values(
                nome=nome, valore_cifrato=cifra(ambiente), origine="ambiente",
            ).on_conflict_do_nothing(index_elements=["nome"]))
            await session.flush()
            riga = await session.get(SegretoSistema, nome)
        if riga is not None and decifra(riga.valore_cifrato) != ambiente:
            # Vince l'ambiente: lo si riallinea, così una futura rimozione della variabile non cambia nulla.
            riga.valore_cifrato, riga.origine = cifra(ambiente), "ambiente"
            await session.flush()
        imposta(ambiente)
        return ambiente

    if riga is None:
        await session.execute(insert(SegretoSistema).values(
            nome=nome, valore_cifrato=cifra(secrets.token_urlsafe(48)), origine="generato",
        ).on_conflict_do_nothing(index_elements=["nome"]))
        await session.flush()
        # Rilettura: se un'altra replica ha scritto per prima, vale il suo.
        riga = (await session.execute(
            select(SegretoSistema).where(SegretoSistema.nome == nome).execution_options(populate_existing=True)
        )).scalar_one()
        logger.info("Segreto interno «%s» generato al primo avvio e salvato cifrato", nome)
    valore = decifra(riga.valore_cifrato)
    if not valore:
        # La chiave master è cambiata: il segreto vecchio non si legge più. Non se ne inventa un altro in silenzio
        # (cambierebbe tutte le impronte): si dice, e si resta sul ripiego finché qualcuno non decide.
        logger.error(
            "Il segreto interno «%s» non si decifra con la chiave master attuale (TAROT_LLM_PROVIDER_KEY cambiata?)",
            nome,
        )
        return ""
    imposta(valore)
    return valore


async def assicura_tutti(session: AsyncSession) -> None:
    for nome in SEGRETI:
        await assicura(session, nome)
