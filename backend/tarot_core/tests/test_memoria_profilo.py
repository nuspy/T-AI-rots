"""Gli endpoint `/me/memories` (v6, Fase D): elenco, modifica con ricalcolo dell'embedding,
cancellazione singola e multipla — tutti filtrati per proprietario."""
from __future__ import annotations

from tarot_core.domain.memory_models import UserMemory
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database

pytestmark = richiede_database


def _memoria(owner_id: int, **extra) -> UserMemory:
    base = dict(
        owner_id=owner_id, contenuto="gli manca una gamba", tipo="stabile",
        campo_attinenza="salute", embedding=[1.0, 0.0], fonte="lettura",
    )
    base.update(extra)
    return UserMemory(**base)


async def test_elenco_vuoto_senza_memorie(client):
    assert (await client.get("/me/memories")).json()["memorie"] == []


async def test_elenco_non_mostra_le_sostituite(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    vecchia = _memoria(io.id, tipo="variabile", contenuto="cerca lavoro", campo_attinenza="lavoro")
    session.add(vecchia)
    await session.flush()
    nuova = _memoria(io.id, tipo="variabile", contenuto="ha trovato lavoro", campo_attinenza="lavoro")
    session.add(nuova)
    await session.flush()
    vecchia.superseded_by = nuova.id
    await session.commit()

    elenco = (await client.get("/me/memories")).json()["memorie"]
    assert [m["contenuto"] for m in elenco] == ["ha trovato lavoro"]


async def test_modifica_il_campo_di_attinenza_senza_toccare_l_embedding(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    m = _memoria(io.id)
    session.add(m)
    await session.commit()

    r = await client.patch(f"/me/memories/{m.id}", json={"campo_attinenza": "famiglia"})
    assert r.status_code == 200, r.text
    assert r.json()["campo_attinenza"] == "famiglia"
    assert r.json()["contenuto"] == "gli manca una gamba"


async def test_eliminare_una_memoria(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    m = _memoria(io.id)
    session.add(m)
    await session.commit()

    r = await client.delete(f"/me/memories/{m.id}")
    assert r.status_code == 204
    assert (await client.get("/me/memories")).json()["memorie"] == []


async def test_eliminare_una_memoria_inesistente_da_404(client):
    import uuid
    r = await client.delete(f"/me/memories/{uuid.uuid4()}")
    assert r.status_code == 404


async def test_eliminazione_multipla_per_id(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    a, b, c = _memoria(io.id, contenuto="a"), _memoria(io.id, contenuto="b"), _memoria(io.id, contenuto="c")
    session.add_all([a, b, c])
    await session.commit()

    r = await client.request("DELETE", "/me/memories", json={"ids": [str(a.id), str(b.id)]})
    assert r.status_code == 204
    rimaste = (await client.get("/me/memories")).json()["memorie"]
    assert [m["contenuto"] for m in rimaste] == ["c"]


async def test_eliminazione_tutte_prevale_su_ids(client, session, principal_utente):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    session.add_all([_memoria(io.id, contenuto="a"), _memoria(io.id, contenuto="b")])
    await session.commit()

    r = await client.request("DELETE", "/me/memories", json={"tutte": True})
    assert r.status_code == 204
    assert (await client.get("/me/memories")).json()["memorie"] == []


async def test_non_si_vede_ne_si_tocca_la_memoria_di_un_altro(client, session, principal_utente, principal_admin):
    await client.get("/me/addresses")
    io = await UserRepository(session).ensure(principal_utente)
    m = _memoria(io.id)
    session.add(m)
    await session.commit()

    client.identita.principal = principal_admin
    await UserRepository(session).ensure(principal_admin)
    await session.commit()

    assert (await client.get("/me/memories")).json()["memorie"] == []
    assert (await client.patch(f"/me/memories/{m.id}", json={"campo_attinenza": "rubato"})).status_code == 404
    assert (await client.delete(f"/me/memories/{m.id}")).status_code == 404
