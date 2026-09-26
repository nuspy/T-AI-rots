"""Gli utenti creati a mano con il loro saldo: nascono una volta sola, e i crediti non si raddoppiano."""
from __future__ import annotations

from sqlalchemy import select

from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.models import User
from tarot_core.tools.utenti import crea_utenti

from .conftest import richiede_database

pytestmark = richiede_database

VOCI = [
    {"sub": "sub-martina", "email": "martina@tarots.local", "nome": "Martina", "crediti": 1_000_000},
    {"sub": "sub-andrea", "email": "andrea@tarots.local", "nome": "Andrea", "crediti": 1_000_000},
]


async def test_crea_gli_utenti_con_il_saldo(session, catalogo):
    esiti = await crea_utenti(session, VOCI)
    await session.commit()
    assert [e["creato"] for e in esiti] == [True, True]
    assert [e["saldo"] for e in esiti] == [1_000_000, 1_000_000]
    utenti = (await session.execute(select(User).where(User.keycloak_sub.in_(["sub-martina", "sub-andrea"])))).scalars().all()
    assert len(utenti) == 2 and all(u.referral_code for u in utenti)


async def test_rilanciarlo_non_raddoppia_nulla(session, catalogo):
    await crea_utenti(session, VOCI)
    await session.commit()
    esiti = await crea_utenti(session, VOCI)
    await session.commit()
    assert [e["creato"] for e in esiti] == [False, False]
    assert [e["accreditati"] for e in esiti] == [False, False]
    utente = (await session.execute(select(User).where(User.keycloak_sub == "sub-martina"))).scalar_one()
    assert await RegistroCrediti(session).saldo(utente.id) == 1_000_000
