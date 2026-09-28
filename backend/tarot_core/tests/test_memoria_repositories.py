"""`user_memories` (v6, Fase A): query dei candidati, elenco, cancellazione — filtrate per owner_id."""
from __future__ import annotations

from tarot_core.domain import memoria_repositories as repo
from tarot_core.domain.memory_models import UserMemory
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database

pytestmark = richiede_database


def _memoria(owner_id: int, campo: str = "amore", tipo: str = "stabile", embedding=None, **extra) -> UserMemory:
    base = dict(
        owner_id=owner_id, contenuto="manca una gamba", tipo=tipo,
        campo_attinenza=campo, embedding=embedding or [1.0, 0.0], fonte="lettura",
    )
    base.update(extra)
    return UserMemory(**base)


async def test_candidati_per_esclude_le_memorie_di_un_altro_utente(client, session, principal_utente, principal_admin):
    await client.get("/me/addresses")  # forza la creazione della riga `users` per l'utente corrente
    io = await UserRepository(session).ensure(principal_utente)
    altro = await UserRepository(session).ensure(principal_admin)
    session.add(_memoria(io.id))
    session.add(_memoria(altro.id))
    await session.commit()

    candidati = await repo.candidati_per(session, io.id)
    assert len(candidati) == 1


async def test_candidati_per_esclude_le_memorie_sostituite(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    vecchia = _memoria(io.id, tipo="variabile", contenuto="prima")
    session.add(vecchia)
    await session.flush()
    nuova = _memoria(io.id, tipo="variabile", contenuto="dopo")
    session.add(nuova)
    await session.flush()
    vecchia.superseded_by = nuova.id
    await session.commit()

    candidati = await repo.candidati_per(session, io.id)
    assert [c.contenuto for c in candidati] == ["dopo"]


async def test_elimina_molte_cancella_solo_gli_id_indicati(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    a, b, c = _memoria(io.id, contenuto="a"), _memoria(io.id, contenuto="b"), _memoria(io.id, contenuto="c")
    session.add_all([a, b, c])
    await session.commit()

    cancellate = await repo.elimina_molte(session, io.id, [a.id, b.id])
    await session.commit()

    assert cancellate == 2
    rimaste = await repo.elenca(session, io.id)
    assert [r.contenuto for r in rimaste] == ["c"]


async def test_elimina_tutte_svuota_lo_scope_dell_utente(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    session.add_all([_memoria(io.id, contenuto="a"), _memoria(io.id, contenuto="b")])
    await session.commit()

    cancellate = await repo.elimina_tutte(session, io.id)
    await session.commit()

    assert cancellate == 2
    assert await repo.elenca(session, io.id) == []


# ---- scrivi_o_fondi (v6, Fase B) -------------------------------------------------------------------


async def test_una_stabile_duplicata_si_scarta(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    session.add(_memoria(io.id, tipo="stabile", campo="salute", embedding=[1.0, 0.0], contenuto="manca una gamba"))
    await session.commit()

    esito = await repo.scrivi_o_fondi(
        session, io.id, contenuto="gli manca una gamba", tipo="stabile",
        campo_attinenza="salute", embedding=[0.99, 0.01],
    )
    await session.commit()

    assert esito is None
    assert len(await repo.elenca(session, io.id)) == 1


async def test_una_stabile_non_simile_si_aggiunge(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    session.add(_memoria(io.id, tipo="stabile", campo="salute", embedding=[1.0, 0.0], contenuto="manca una gamba"))
    await session.commit()

    esito = await repo.scrivi_o_fondi(
        session, io.id, contenuto="e' allergico ai gatti", tipo="stabile",
        campo_attinenza="salute", embedding=[0.0, 1.0],
    )
    await session.commit()

    assert esito is not None
    assert len(await repo.elenca(session, io.id)) == 2


async def test_una_variabile_nuova_sostituisce_quella_sullo_stesso_campo(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    session.add(_memoria(io.id, tipo="variabile", campo="lavoro", embedding=[1.0, 0.0], contenuto="cerca lavoro"))
    await session.commit()

    esito = await repo.scrivi_o_fondi(
        session, io.id, contenuto="ha trovato lavoro", tipo="variabile",
        campo_attinenza="lavoro", embedding=[0.0, 1.0],
    )
    await session.commit()

    correnti = await repo.elenca(session, io.id)
    assert [r.contenuto for r in correnti] == ["ha trovato lavoro"]
    catena = await repo.catena(session, io.id, esito.id)
    assert [r.contenuto for r in catena] == ["cerca lavoro", "ha trovato lavoro"]


async def test_catena_risale_dalla_testa_alla_piu_vecchia(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    v1 = _memoria(io.id, tipo="variabile", contenuto="v1")
    session.add(v1)
    await session.flush()
    v2 = _memoria(io.id, tipo="variabile", contenuto="v2")
    session.add(v2)
    await session.flush()
    v1.superseded_by = v2.id
    await session.commit()

    risultato = await repo.catena(session, io.id, v2.id)
    assert [r.contenuto for r in risultato] == ["v1", "v2"]
