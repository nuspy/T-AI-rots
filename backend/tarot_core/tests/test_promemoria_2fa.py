"""Il promemoria della verifica in due passaggi: solo la preferenza dell'utente.

La verifica vera (l'app di autenticazione, il codice a 6 cifre) è di Keycloak: il
sito non la vede né ne conserva niente. Qui si prova ciò che è del sito, cioè il
«non mostrare più» che vale su ogni dispositivo.
"""
from __future__ import annotations

from .conftest import richiede_database

pytestmark = richiede_database


async def test_il_promemoria_e_acceso_per_chi_non_ha_detto_niente(client, catalogo):
    assert (await client.get("/me/profile")).json()["promemoria_2fa"] is True


async def test_non_mostrare_piu_si_ricorda_e_si_puo_riaccendere(client, catalogo):
    r = await client.patch("/me/profile", json={"promemoria_2fa": False})
    assert r.status_code == 200 and r.json()["promemoria_2fa"] is False
    assert (await client.get("/me/profile")).json()["promemoria_2fa"] is False
    r = await client.patch("/me/profile", json={"promemoria_2fa": True})
    assert r.json()["promemoria_2fa"] is True


async def test_le_altre_modifiche_non_toccano_la_preferenza(client, catalogo):
    await client.patch("/me/profile", json={"promemoria_2fa": False})
    p = (await client.patch("/me/profile", json={"gender": "donna", "birth_date": "1990-03-14"})).json()
    assert p["promemoria_2fa"] is False and p["gender"] == "donna"


async def test_la_preferenza_e_di_ciascun_utente(client, catalogo, principal_altro):
    await client.patch("/me/profile", json={"promemoria_2fa": False})
    client.identita.principal = principal_altro
    assert (await client.get("/me/profile")).json()["promemoria_2fa"] is True
