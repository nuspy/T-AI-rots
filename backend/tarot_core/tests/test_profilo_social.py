"""La scheda utente dai social (`POST /me/profilo-social`): solo i campi vuoti, la provenienza, la posizione attuale.

Keycloak, Google, Facebook e le loro CDN sono un unico server HTTP finto (`httpx.MockTransport` in
`profilo_social.TRASPORTO`): nessuna chiamata vera esce durante le prove.
"""
from __future__ import annotations

import io
import json
from datetime import date
from typing import Any, Dict, List

import httpx
import pytest
from sqlalchemy import select

from tarot_core.auth.keycloak import Principal
from tarot_core.domain.models import AuditLog, User
from tarot_core.domain.repositories import UserRepository
from tarot_core.tarot import profilo_social
from tarot_core.tarot.profilo_social import (
    _token_del_provider, data_da_facebook, data_da_google, genere_da, lingua_da,
)

from .conftest import richiede_database

TOKEN_UTENTE = "tok-della-persona"


def _png() -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (300, 300), (120, 40, 90)).save(buffer, format="PNG")
    return buffer.getvalue()


# ---- le traduzioni dei valori (niente rete, niente database) ----------------------------------------------


def test_genere_dei_provider_nei_valori_della_scheda():
    assert genere_da("male") == ("uomo", None)
    assert genere_da("Female") == ("donna", None)
    assert genere_da("non-binary") == ("non_binario", None)
    assert genere_da("Genderqueer") == ("non_binario", None)
    # «unspecified» non è una risposta: resta vuoto, non diventa «preferisco non dirlo».
    assert genere_da("unspecified") == (None, None)
    assert genere_da(None) == (None, None)
    assert genere_da("Two-spirit") == ("altro", "Two-spirit")


def test_date_di_nascita_complete_o_niente():
    assert data_da_google({"year": 1990, "month": 4, "day": 12}) == date(1990, 4, 12)
    assert data_da_google({"month": 4, "day": 12}) is None  # senza anno
    assert data_da_google({"year": 1850, "month": 1, "day": 1}) is None
    assert data_da_facebook("04/12/1990") == date(1990, 4, 12)
    assert data_da_facebook("04/12") is None
    assert data_da_facebook("1990") is None
    assert data_da_facebook("13/45/1990") is None


def test_lingua_solo_se_il_sito_la_ha():
    assert lingua_da("it-IT") == "it"
    assert lingua_da("hu_HU") == "hu"
    assert lingua_da({"language": "es", "country": "MX"}) == "es"
    assert lingua_da("sv") is None  # non è una lingua del sito: niente, non l'italiano di ripiego
    assert lingua_da(None) is None


def test_token_del_provider_json_o_modulo():
    assert _token_del_provider('{"access_token": "abc", "expires_in": 3599}') == "abc"
    assert _token_del_provider("access_token=gho_123&scope=user%3Aemail&token_type=bearer") == "gho_123"
    assert _token_del_provider("") is None


# ---- il finto: Keycloak (con il token della persona), Google, Facebook, le CDN -------------------------------


class Rete:
    def __init__(self) -> None:
        self.collegati = ["google", "facebook"]
        self.google: Dict[str, Any] = {
            "names": [{"metadata": {"primary": True}, "givenName": "Ada", "familyName": "Lovelace"}],
            "birthdays": [{"date": {"month": 12, "day": 10}}, {"date": {"year": 1985, "month": 12, "day": 10}}],
            "genders": [{"value": "female"}],
            "locales": [{"value": "hu"}],
            "photos": [{"url": "https://lh3.googleusercontent.com/a/foto=s100", "metadata": {"primary": True}}],
        }
        self.facebook: Dict[str, Any] = {
            "first_name": "Adele", "last_name": "Byron", "birthday": "01/01/1990", "gender": "male",
            "location": {"name": "Milano, Italia", "location": {"city": "Milano", "country_code": "IT"}},
            "picture": {"data": {"url": "https://platform-lookaside.fbsbx.com/foto.jpg", "is_silhouette": False}},
        }
        self.token_vietati: List[str] = []
        self.chiamate: List[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        url = request.url
        self.chiamate.append(f"{url.host}{url.path}")
        auth = request.headers.get("authorization")
        if url.path.endswith("/account/linked-accounts"):
            assert auth == f"Bearer {TOKEN_UTENTE}"
            return httpx.Response(200, json=[
                {"providerAlias": a, "connected": a in self.collegati, "social": True}
                for a in ("google", "facebook", "github")
            ])
        if "/broker/" in url.path and url.path.endswith("/token"):
            assert auth == f"Bearer {TOKEN_UTENTE}"  # il token della persona, mai quello dell'API
            alias = url.path.split("/")[-2]
            if alias in self.token_vietati:
                return httpx.Response(403, json={"errorMessage": "Client [tarot-frontend] not authorized"})
            return httpx.Response(200, text=json.dumps({"access_token": f"tok-{alias}", "expires_in": 3599}))
        if url.host == "people.googleapis.com":
            assert auth == "Bearer tok-google"
            assert "birthdays" in url.params["personFields"]
            return httpx.Response(200, json=self.google)
        if url.host == "graph.facebook.com":
            assert auth == "Bearer tok-facebook"
            return httpx.Response(200, json=self.facebook)
        if url.host in ("lh3.googleusercontent.com", "platform-lookaside.fbsbx.com"):
            return httpx.Response(200, content=_png(), headers={"content-type": "image/png"})
        raise AssertionError(f"chiamata inattesa: {url}")


@pytest.fixture
def rete(monkeypatch):
    finta = Rete()
    monkeypatch.setattr(profilo_social, "TRASPORTO", httpx.MockTransport(finta))
    return finta


@pytest.fixture
def luogo_ip(monkeypatch):
    """Il database geografico delle analytics, finto: l'IP della richiesta → paese e città."""
    from lanterna import geo

    visti: List[Any] = []

    def finto(percorso, ip):
        visti.append(ip)
        return geo.Luogo(paese="HU", regione="Budapest", citta="Budapest")

    monkeypatch.setattr(geo, "luogo", finto)
    return visti


@pytest.fixture
def social(client):
    """Una persona entrata da poco con un social: il token porta nome e cognome dell'account Keycloak."""
    client.identita.principal = Principal(
        subject="sub-social-1", email="ada@example.com", display_name="Ada Lovelace", roles={"user"},
        raw_claims={"sub": "sub-social-1", "email": "ada@example.com", "azp": "tarot-frontend"},
    )
    return client


async def _importa(client) -> httpx.Response:
    return await client.post("/me/profilo-social", headers={"Authorization": f"Bearer {TOKEN_UTENTE}"})


pytestmark = richiede_database


async def test_riempie_i_campi_vuoti_da_google_e_annota_la_provenienza(social, rete, luogo_ip, session):
    rete.collegati = ["google"]
    r = await _importa(social)
    assert r.status_code == 200, r.text
    esito = r.json()
    assert esito["provider"] == ["google"]
    assert set(esito["compilati"]) == {"nome", "cognome", "birth_date", "gender", "locale", "avatar"}

    profilo = (await social.get("/me/profile")).json()
    assert (profilo["nome"], profilo["cognome"]) == ("Ada", "Lovelace")
    assert profilo["birth_date"] == "1985-12-10"  # il compleanno con l'anno, non quello senza
    assert profilo["gender"] == "donna" and profilo["locale"] == "hu"
    assert profilo["avatar"]  # la foto di Google, scaricata e riscritta come avatar
    assert profilo["dati_social"]["birth_date"]["da"] == "google"
    # Google non dà la città: la posizione attuale viene dall'IP della richiesta.
    assert profilo["posizione"]["paese"] == "HU" and profilo["posizione"]["fonte"] == "ip"
    assert luogo_ip  # interrogato una volta

    voce = (await session.execute(select(AuditLog).where(AuditLog.action == "profilo.dati_social"))).scalar_one()
    assert "1985" not in json.dumps(voce.after)  # nel registro i campi, mai i valori


async def test_mai_sopra_un_valore_gia_inserito(social, rete, luogo_ip):
    await social.patch("/me/profile", json={"birth_date": "1970-05-05", "gender": "uomo", "nome": "Augusta"})
    r = await _importa(social)
    assert r.status_code == 200, r.text
    assert "birth_date" not in r.json()["compilati"] and "gender" not in r.json()["compilati"]
    profilo = (await social.get("/me/profile")).json()
    assert profilo["birth_date"] == "1970-05-05" and profilo["gender"] == "uomo" and profilo["nome"] == "Augusta"
    assert profilo["cognome"] == "Lovelace"  # questo era vuoto


async def test_idempotente(social, rete, luogo_ip):
    primo = (await _importa(social)).json()
    assert primo["compilati"]
    secondo = (await _importa(social)).json()
    assert secondo["compilati"] == []
    # Fra due social, il primo che compila un campo vince: Facebook non riscrive ciò che ha messo Google.
    profilo = (await social.get("/me/profile")).json()
    assert profilo["nome"] == "Ada"


async def test_facebook_da_anche_la_citta(social, rete, luogo_ip):
    rete.collegati = ["facebook"]
    r = await _importa(social)
    assert r.status_code == 200, r.text
    profilo = (await social.get("/me/profile")).json()
    assert profilo["birth_date"] == "1990-01-01" and profilo["gender"] == "uomo"
    assert profilo["posizione"] == {**profilo["posizione"], "paese": "IT", "citta": "Milano", "fonte": "facebook"}
    assert luogo_ip == []  # il social l'ha data: l'IP non serve


async def test_un_social_che_non_risponde_non_e_un_errore(social, rete, luogo_ip):
    rete.token_vietati = ["google", "facebook"]  # niente `broker/read-token`, o il token non è conservato
    r = await _importa(social)
    assert r.status_code == 200, r.text
    assert r.json()["provider"] == [] and r.json()["posizione"]["fonte"] == "ip"


async def test_nome_e_cognome_anche_dal_token_senza_social(client, rete, luogo_ip):
    """Chi si è iscritto con email e password: nome e cognome scritti nel modulo di Keycloak arrivano col token."""
    rete.collegati = []
    client.identita.principal = Principal(
        subject="sub-password", email="bea@example.com", display_name="Bea Rossi", roles={"user"},
        raw_claims={"sub": "sub-password", "given_name": "Bea", "family_name": "Rossi"},
    )
    r = await _importa(client)
    assert sorted(r.json()["compilati"]) == ["cognome", "nome"]
    profilo = (await client.get("/me/profile")).json()
    assert profilo["dati_social"]["nome"]["da"] == "account"


async def test_foto_solo_dalle_cdn_dei_provider(social, rete, luogo_ip):
    rete.collegati = ["google"]
    rete.google["photos"] = [{"url": "https://attaccante.example/interno.png"}]
    r = await _importa(social)
    assert "avatar" not in r.json()["compilati"]
    assert not any("attaccante" in c for c in rete.chiamate)


async def test_correggere_un_campo_lo_toglie_dai_social_e_non_torna(social, rete, luogo_ip):
    await _importa(social)
    r = await social.patch("/me/profile", json={"nome": ""})  # svuotato apposta
    assert r.status_code == 200, r.text
    assert r.json()["nome"] is None and r.json()["dati_social"]["nome"]["da"] == "utente"
    await social.delete("/me/avatar")
    secondo = (await _importa(social)).json()
    assert "nome" not in secondo["compilati"] and "avatar" not in secondo["compilati"]


async def test_posizione_corretta_a_mano_non_si_sovrascrive(social, rete, luogo_ip):
    rete.collegati = ["google"]
    await _importa(social)
    r = await social.patch("/me/profile", json={"posizione_paese": "at", "posizione_citta": "Vienna"})
    assert r.json()["posizione"]["fonte"] == "utente" and r.json()["posizione"]["paese"] == "AT"
    await _importa(social)
    assert (await social.get("/me/profile")).json()["posizione"]["citta"] == "Vienna"
    # Svuotata: si torna al rilevamento automatico.
    r = await social.patch("/me/profile", json={"posizione_paese": "", "posizione_citta": ""})
    assert r.json()["posizione"] is None
    await _importa(social)
    assert (await social.get("/me/profile")).json()["posizione"]["fonte"] == "ip"


async def test_spegnere_importazione_e_rilevamento(social, rete, luogo_ip):
    await _importa(social)
    r = await social.patch("/me/profile", json={"importa_social": False, "rileva_posizione": False})
    assert r.json()["posizione"] is None and r.json()["importa_social"] is False
    rete.chiamate.clear()
    esito = (await _importa(social)).json()
    assert esito == {"compilati": [], "provider": [], "posizione": None, "unione": False}
    assert rete.chiamate == []  # spenta: non si chiede niente a nessuno


async def test_cancellare_i_dati_dei_social(social, rete, luogo_ip, session):
    await _importa(social)
    await social.patch("/me/profile", json={"gender": "non_binario"})  # questo l'ha scelto la persona
    r = await social.delete("/me/dati-social")
    assert r.status_code == 204
    profilo = (await social.get("/me/profile")).json()
    assert profilo["birth_date"] is None and profilo["nome"] is None and profilo["avatar"] is None
    assert profilo["gender"] == "non_binario"  # corretto a mano: resta
    assert profilo["posizione"] is None
    assert profilo["importa_social"] is False and profilo["rileva_posizione"] is False
    assert (await _importa(social)).json()["compilati"] == []  # e non tornano


async def test_la_lingua_del_token_non_si_perde_e_quella_vuota_non_ricade_sull_italiano(session):
    repo = UserRepository(session)
    senza = Principal(subject="sub-lingua", email="l@example.com", roles={"user"}, raw_claims={"sub": "sub-lingua"})
    utente = await repo.ensure(senza)
    utente.locale = "hu"  # presa da un social
    await session.flush()
    utente = await repo.ensure(senza)
    assert utente.locale == "hu"  # il token non porta la lingua: «it» di ripiego non la sovrascrive
    con = Principal(subject="sub-lingua", email="l@example.com", roles={"user"},
                    raw_claims={"sub": "sub-lingua", "locale": "es"}, locale="es")
    assert (await repo.ensure(con)).locale == "es"  # quella scelta in Keycloak sì


async def test_la_console_vede_scheda_e_provenienza(client, rete, luogo_ip, principal_admin, session):
    rete.collegati = ["google"]
    client.identita.principal = Principal(
        subject="sub-social-2", email="carla@example.com", roles={"user"}, raw_claims={"sub": "sub-social-2"},
    )
    await _importa(client)
    utente = (await session.execute(select(User).where(User.keycloak_sub == "sub-social-2"))).scalar_one()
    client.identita.principal = principal_admin
    r = await client.get(f"/admin/users/{utente.id}")
    assert r.status_code == 200, r.text
    anagrafica = r.json()["anagrafica"]
    assert anagrafica["nascita"] == "1985-12-10" and anagrafica["genere"] == "donna"
    assert anagrafica["dati_social"]["campi"]["birth_date"]["da"] == "google"
    assert anagrafica["posizione"]["fonte"] == "ip"
