"""Scrive il catalogo e gli utenti di prova.

    python -m tarot_core.tools.seed            # catalogo + utenti di prova
    python -m tarot_core.tools.seed --forza    # riscrive anche i piani esistenti

Deriva da `seed_piani` di Personalities: stesso principio, catalogo diverso.

**Il catalogo.**

| slug | tipo | prezzo | cosa dà |
|---|---|---|---|
| free | abbonamento | 0 | la carta del giorno; ogni lettura costa un credito |
| mensile-base | abbonamento | 9,90 €/mese | 3 letture al giorno |
| mensile-oro | abbonamento | 19,90 €/mese | 10 letture al giorno |
| pacchetto-5 / -15 / -50 | pacchetto | 4,90 / 12,90 / 34,90 € | crediti che non scadono |

**Gli utenti di prova** hanno gli stessi identificativi del realm di sviluppo
di Keycloak (`deploy/keycloak/realm-tarots.json`): al primo login il token
porta quel `sub`, e l'utente trova già i suoi crediti. Ricevono 1000 crediti
una volta sola — rilanciare il seed non li raddoppia.

I prezzi sono in centesimi: un `float` per il denaro è il modo classico di
scoprire dopo mesi che una somma di importi non torna per un millesimo.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import Any, Dict, List

from sqlalchemy import select

from ..auth.dependencies import PRINCIPAL_DI_SVILUPPO
from ..billing.credits import RegistroCrediti
from ..billing.plans import GestoreAbbonamenti
from ..domain.billing_models import CreditEntry, Plan
from ..domain.models import User
from ..domain.repositories import nuovo_codice_invito
from ..domain.session import dispose_engine, get_session_factory
from ..settings import get_settings

logger = logging.getLogger(__name__)

CATALOGO: List[Dict[str, Any]] = [
    {
        "slug": "free", "name": "Gratuito", "tipo": "abbonamento", "rank": 0,
        "description": "La carta del giorno ogni giorno. Le letture si pagano con i crediti.",
        "price_monthly": 0, "price_yearly": 0, "credits_per_period": 0,
        "limits": {"letture_al_giorno": 0},
    },
    {
        "slug": "mensile-base", "name": "Mensile Base", "tipo": "abbonamento", "rank": 10,
        "description": "Tre letture al giorno, tutte le stese, storico illimitato.",
        "price_monthly": 990, "price_yearly": 9900, "credits_per_period": 0,
        "limits": {"letture_al_giorno": 3},
    },
    {
        "slug": "mensile-oro", "name": "Mensile Oro", "tipo": "abbonamento", "rank": 20,
        "description": "Dieci letture al giorno per chi consulta spesso le carte.",
        "price_monthly": 1990, "price_yearly": 19900, "credits_per_period": 0,
        "limits": {"letture_al_giorno": 10},
    },
    {
        "slug": "pacchetto-5", "name": "5 letture", "tipo": "pacchetto", "rank": 30,
        "description": "Cinque consulti, senza scadenza.",
        "price_monthly": 490, "price_yearly": 0, "credits_per_period": 5, "limits": {},
    },
    {
        "slug": "pacchetto-15", "name": "15 letture", "tipo": "pacchetto", "rank": 31,
        "description": "Quindici consulti, senza scadenza. Il più scelto.",
        "price_monthly": 1290, "price_yearly": 0, "credits_per_period": 15, "limits": {},
    },
    {
        "slug": "pacchetto-50", "name": "50 letture", "tipo": "pacchetto", "rank": 32,
        "description": "Cinquanta consulti, senza scadenza.",
        "price_monthly": 3490, "price_yearly": 0, "credits_per_period": 50, "limits": {},
    },
]

#: Gli utenti del realm di sviluppo, con il loro `sub` fisso.
UTENTI_DI_PROVA = [
    {"sub": "11111111-1111-4111-8111-111111111111", "email": "test@tarots.local", "nome": "Utente di prova"},
    {"sub": "22222222-2222-4222-8222-222222222222", "email": "admin@tarots.local", "nome": "Amministratore"},
    {"sub": PRINCIPAL_DI_SVILUPPO.subject, "email": PRINCIPAL_DI_SVILUPPO.email, "nome": PRINCIPAL_DI_SVILUPPO.display_name},
]


async def scrivi_catalogo(session, *, forza: bool = False) -> int:
    scritti = 0
    for voce in CATALOGO:
        piano = (await session.execute(select(Plan).where(Plan.slug == voce["slug"]))).scalar_one_or_none()
        if piano is None:
            session.add(Plan(**voce, currency="EUR", active=True))
            scritti += 1
        elif forza:
            for k, v in voce.items():
                setattr(piano, k, v)
            scritti += 1
    await session.flush()
    return scritti


async def scrivi_utenti(session) -> int:
    crediti = get_settings().crediti_utente_di_prova
    gestore = GestoreAbbonamenti(session)
    registro = RegistroCrediti(session)
    creati = 0
    for voce in UTENTI_DI_PROVA:
        utente = (await session.execute(select(User).where(User.keycloak_sub == voce["sub"]))).scalar_one_or_none()
        if utente is None:
            utente = User(
                keycloak_sub=voce["sub"], email=voce["email"], display_name=voce["nome"],
                locale="it", referral_code=nuovo_codice_invito(),
            )
            session.add(utente)
            await session.flush()
            await gestore.apri_piano_base(utente.id)
            creati += 1
        gia = await session.scalar(
            select(CreditEntry.id).where(
                CreditEntry.user_id == utente.id, CreditEntry.note == "crediti di prova",
            ).limit(1)
        )
        if gia is None:
            await registro.accredita(utente.id, crediti, reason="rettifica", note="crediti di prova")
    return creati


async def scrivi(*, forza: bool = False, utenti: bool = True) -> None:
    factory = get_session_factory()
    async with factory() as session:
        piani = await scrivi_catalogo(session, forza=forza)
        creati = await scrivi_utenti(session) if utenti else 0
        await session.commit()
    await dispose_engine()
    logger.info("Seed: %d piani scritti, %d utenti di prova creati", piani, creati)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="tarot_core.tools.seed")
    parser.add_argument("--forza", action="store_true", help="riscrive anche i piani esistenti")
    parser.add_argument("--senza-utenti", action="store_true", help="solo il catalogo")
    args = parser.parse_args()
    asyncio.run(scrivi(forza=args.forza, utenti=not args.senza_utenti))
    return 0


if __name__ == "__main__":
    sys.exit(main())
