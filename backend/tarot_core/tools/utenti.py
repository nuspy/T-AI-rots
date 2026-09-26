"""Crea utenti dell'app con i loro crediti, per account già esistenti in Keycloak.

    echo '[{"sub": "<id Keycloak>", "email": "a@x.it", "nome": "Andrea", "crediti": 1000000}]' \
        | python -m tarot_core.tools.utenti -
    python -m tarot_core.tools.utenti utenti.json

Un utente nasce nel database al primo accesso, con i crediti del piano base. Per
dargli subito un saldo diverso — un account di prova, un collaboratore — si crea
la riga qui, con lo stesso `sub` che Keycloak scrive nel token: al primo accesso
l'utente trova già i suoi crediti. Come `seed`, si può rilanciare senza
raddoppiare nulla: l'utente e l'accredito si riconoscono dal `sub` e dalla nota.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from typing import Any, Dict, Iterable, List

from sqlalchemy import select

from ..billing.credits import RegistroCrediti
from ..billing.plans import GestoreAbbonamenti
from ..domain.billing_models import CreditEntry
from ..domain.models import User
from ..domain.repositories import nuovo_codice_invito
from ..domain.session import dispose_engine, get_session_factory

logger = logging.getLogger(__name__)


async def crea_utenti(session, voci: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Crea gli utenti che mancano e accredita i crediti che mancano.

    Ogni voce: `sub`, `email`, `nome` e `crediti`. Restituisce, per ciascuna, se
    l'utente è stato creato e se i crediti sono stati accreditati.
    """
    gestore = GestoreAbbonamenti(session)
    registro = RegistroCrediti(session)
    esiti: List[Dict[str, Any]] = []
    for voce in voci:
        utente = (
            await session.execute(select(User).where(User.keycloak_sub == voce["sub"]))
        ).scalar_one_or_none()
        creato = utente is None
        if creato:
            utente = User(
                keycloak_sub=voce["sub"], email=voce["email"], display_name=voce["nome"],
                locale="it", referral_code=nuovo_codice_invito(),
            )
            session.add(utente)
            await session.flush()
            await gestore.apri_piano_base(utente.id)

        crediti = int(voce.get("crediti") or 0)
        nota = f"crediti iniziali: {crediti}"
        accreditati = False
        if crediti > 0:
            gia = await session.scalar(
                select(CreditEntry.id).where(
                    CreditEntry.user_id == utente.id, CreditEntry.note == nota,
                ).limit(1)
            )
            if gia is None:
                await registro.accredita(utente.id, crediti, reason="rettifica", note=nota)
                accreditati = True
        esiti.append({
            "email": voce["email"], "creato": creato, "accreditati": accreditati,
            "saldo": await registro.saldo(utente.id),
        })
    return esiti


async def esegui(voci: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    factory = get_session_factory()
    async with factory() as session:
        esiti = await crea_utenti(session, voci)
        await session.commit()
    await dispose_engine()
    return esiti


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="tarot_core.tools.utenti")
    parser.add_argument("file", help="file JSON con l'elenco degli utenti, oppure - per stdin")
    args = parser.parse_args()
    testo = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    for esito in asyncio.run(esegui(json.loads(testo))):
        logger.info(
            "%s: %s, %s, saldo %d", esito["email"],
            "creato" if esito["creato"] else "già presente",
            "crediti accreditati" if esito["accreditati"] else "crediti già accreditati",
            esito["saldo"],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
