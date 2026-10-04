"""La console verso Keycloak: accesso con i social e login persistente, contro un Keycloak finto (HTTP in memoria).

Il finto fa ciò che fa quello vero per quanto serve qui: rilascia il token client-credentials, legge e scrive il
realm, elenca e costruisce i flussi (passi, sottoflussi, requisiti, configurazioni), crea e aggiorna gli identity
provider mascherando il segreto (e tenendo quello che ha quando gli si rimanda `**********`).
"""
from __future__ import annotations

import copy
import json
import uuid
from typing import Any, Dict, List, Optional

import httpx
import pytest
from sqlalchemy import select

from tarot_core.api.routers import admin_accesso_social, admin_impostazioni
from tarot_core.auth.keycloak_admin import KeycloakAdmin
from tarot_core.auth.provider_sociali import FLUSSO_DOPO_ACCESSO_ESTERNO, MASCHERA
from tarot_core.domain.models import AuditLog
from tarot_core.settings import Settings, get_settings

from .conftest import richiede_database

pytestmark = richiede_database

PREFISSO = "/auth/admin/realms/tarots"  # Keycloak sotto /auth, come nel cluster


class KeycloakFinto:
    def __init__(self, *, flussi: List[str] | None = None, vietato: bool = False) -> None:
        self.realm: Dict[str, Any] = {
            "realm": "tarots", "offlineSessionIdleTimeout": 2_592_000,
            "offlineSessionMaxLifespanEnabled": False, "offlineSessionMaxLifespan": 5_184_000,
        }
        self.provider: Dict[str, Dict[str, Any]] = {
            "google": {
                "alias": "google", "providerId": "google", "enabled": False, "internalId": "g-1",
                "config": {"clientId": "non-usato", "clientSecret": "non-usato", "syncMode": "IMPORT"},
            },
        }
        self.flussi = flussi if flussi is not None else ["browser", "first broker login"]
        self.vietato = vietato
        self.scritture: List[tuple[str, str, Dict[str, Any]]] = []
        #: I passi di ogni flusso (anche dei sottoflussi), in ordine, e le configurazioni dei passi.
        self.passi: Dict[str, List[Dict[str, Any]]] = {}
        self.configurazioni: Dict[str, Dict[str, Any]] = {}
        #: Vieta solo le scritture sui flussi (all'account di servizio manca `manage-realm`).
        self.flussi_vietati = False
        #: Fa fallire l'aggiunta di questo passo, per provare la pulizia di un flusso costruito a metà.
        self.passo_che_fallisce: Optional[str] = None
        #: Le password impostate (`reset-password`), per utente; e la regola finta del realm: almeno 6 caratteri.
        self.password: Dict[str, str] = {}

    def _tutti_i_passi(self, flusso: str, livello: int = 0) -> List[Dict[str, Any]]:
        """Come Keycloak: i passi di un flusso con quelli dei sottoflussi, in profondità."""
        elenco = []
        for passo in self.passi.get(flusso, []):
            elenco.append({**passo, "level": livello})
            if passo.get("authenticationFlow"):
                elenco.extend(self._tutti_i_passi(passo["displayName"], livello + 1))
        return elenco

    def struttura(self, flusso: str) -> List[tuple]:
        """Il flusso come (livello, passo, requisito): ciò che conta per l'unione degli account."""
        return [
            (p["level"], p.get("providerId") or p["displayName"], p["requirement"])
            for p in self._tutti_i_passi(flusso)
        ]

    def _flussi(self, request: httpx.Request, percorso: str, corpo: Any) -> httpx.Response:
        base = f"{PREFISSO}/authentication"
        if request.method != "GET" and self.flussi_vietati:
            return httpx.Response(403, json={"error": "HTTP 403 Forbidden"})
        if percorso == f"{base}/flows":
            if request.method == "GET":
                return httpx.Response(200, json=[{"alias": a, "id": f"id-{a}"} for a in self.flussi])
            self.flussi.append(corpo["alias"])
            self.passi[corpo["alias"]] = []
            return httpx.Response(201)
        if percorso.startswith(f"{base}/executions/") and percorso.endswith("/config"):
            self.configurazioni[percorso.split("/")[-2]] = corpo
            return httpx.Response(201)
        if percorso.startswith(f"{base}/executions/") and request.method == "DELETE":
            id_passo = percorso.rsplit("/", 1)[1]
            for passi in self.passi.values():
                passi[:] = [p for p in passi if p["id"] != id_passo]
            return httpx.Response(204)
        resto = percorso[len(f"{base}/flows/"):]
        if request.method == "DELETE":
            alias = resto.removeprefix("id-")
            self.flussi.remove(alias)
            self.passi.pop(alias, None)
            return httpx.Response(204)
        flusso, _, coda = resto.partition("/")
        if flusso not in self.passi:
            return httpx.Response(404, json={"error": "Flow not found"})
        if coda == "executions" and request.method == "GET":
            return httpx.Response(200, json=self._tutti_i_passi(flusso))
        if coda == "executions" and request.method == "PUT":
            for passi in self.passi.values():
                for passo in passi:
                    if passo["id"] == corpo["id"]:
                        passo["requirement"] = corpo["requirement"]
            return httpx.Response(204)
        if coda == "executions/execution":
            if corpo["provider"] == self.passo_che_fallisce:
                return httpx.Response(500, json={"error": "unknown_error"})
            self.passi[flusso].append({
                "id": str(uuid.uuid4()), "providerId": corpo["provider"], "displayName": corpo["provider"],
                "requirement": "DISABLED", "priority": 10 * len(self.passi[flusso]),
            })
            return httpx.Response(201)
        if coda == "executions/flow":
            self.passi[flusso].append({
                "id": str(uuid.uuid4()), "displayName": corpo["alias"], "authenticationFlow": True,
                "requirement": "DISABLED", "priority": 10 * len(self.passi[flusso]),
            })
            self.passi[corpo["alias"]] = []
            return httpx.Response(201)
        return httpx.Response(404)

    def _mascherato(self, p: Dict[str, Any]) -> Dict[str, Any]:
        p = copy.deepcopy(p)
        if p.get("config", {}).get("clientSecret"):
            p["config"]["clientSecret"] = MASCHERA
        return p

    def __call__(self, request: httpx.Request) -> httpx.Response:
        percorso = request.url.path
        if percorso.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 300})
        assert request.headers.get("authorization") == "Bearer tok"
        if self.vietato:
            return httpx.Response(403, json={"error": "HTTP 403 Forbidden"})
        corpo = json.loads(request.content) if request.content else None
        if request.method != "GET":
            self.scritture.append((request.method, percorso, corpo))

        if percorso == PREFISSO:
            if request.method == "GET":
                return httpx.Response(200, json=self.realm)
            self.realm.update(corpo)
            return httpx.Response(204)
        if percorso.startswith(f"{PREFISSO}/authentication/"):
            return self._flussi(request, percorso, corpo)
        if percorso.startswith(f"{PREFISSO}/users/") and percorso.endswith("/reset-password"):
            if len(corpo["value"]) < 6:
                return httpx.Response(400, json={
                    "error": "invalidPasswordMinLengthMessage", "error_description": "Invalid password: minimum length 6.",
                })
            self.password[percorso.split("/")[-2]] = corpo["value"]
            return httpx.Response(204)
        if percorso == f"{PREFISSO}/identity-provider/instances":
            if request.method == "GET":
                return httpx.Response(200, json=[self._mascherato(p) for p in self.provider.values()])
            if corpo["alias"] in self.provider:
                return httpx.Response(409, json={"errorMessage": "esiste"})
            self.provider[corpo["alias"]] = corpo
            return httpx.Response(201)
        if percorso.startswith(f"{PREFISSO}/identity-provider/instances/"):
            alias = percorso.rsplit("/", 1)[1]
            if alias not in self.provider:
                return httpx.Response(404, json={"error": "Could not find identity provider"})
            if request.method == "GET":
                return httpx.Response(200, json=self._mascherato(self.provider[alias]))
            if corpo["config"].get("clientSecret") == MASCHERA:
                corpo["config"]["clientSecret"] = self.provider[alias]["config"].get("clientSecret")
            self.provider[alias] = corpo
            return httpx.Response(204)
        return httpx.Response(404)


@pytest.fixture
def keycloak(monkeypatch):
    """Il Keycloak finto al posto di quello vero, nei due router che parlano con lui."""
    finto = KeycloakFinto()

    def fabbrica() -> KeycloakAdmin:
        impostazioni = Settings(
            keycloak_url="http://kc.interno:8080/auth", keycloak_issuer_url="https://tarots.chat/auth",
            keycloak_realm="tarots", keycloak_client_secret="segreto-api",
        )
        return KeycloakAdmin(impostazioni, transport=httpx.MockTransport(finto))

    monkeypatch.setattr(admin_accesso_social, "KeycloakAdmin", fabbrica)
    monkeypatch.setattr(admin_impostazioni, "KeycloakAdmin", fabbrica)
    finto.fabbrica = fabbrica
    # L'URI di ritorno si scrive con l'indirizzo pubblico di Keycloak, letto dalle impostazioni a ogni richiesta.
    monkeypatch.setenv("TAROT_KEYCLOAK_ISSUER_URL", "https://tarots.chat/auth")
    get_settings.cache_clear()
    yield finto
    get_settings.cache_clear()


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


# ---- accesso con i social ----------------------------------------------------------------------


async def test_solo_l_amministratore(client, keycloak):
    assert (await client.get("/admin/accesso-social")).status_code == 403
    assert (await client.put("/admin/accesso-social/google", json={"abilitato": False})).status_code == 403


async def test_elenco_con_stato_guida_e_uri_di_ritorno(admin, keycloak):
    r = await admin.get("/admin/accesso-social")
    assert r.status_code == 200
    dati = r.json()
    assert dati["keycloak_raggiungibile"] is True
    per_alias = {p["alias"]: p for p in dati["provider"]}
    assert set(per_alias) == {"google", "facebook", "microsoft", "apple", "github", "linkedin", "twitter", "instagram"}
    google = per_alias["google"]
    # I segnaposto del manifest non sono credenziali, e il segreto non esce mai.
    assert google["presente"] is True and google["client_id"] == "" and google["segreto_impostato"] is False
    assert MASCHERA not in json.dumps(dati)
    assert google["uri_reindirizzamento"] == "https://tarots.chat/auth/realms/tarots/broker/google/endpoint"
    assert google["guida"] and google["console"].startswith("https://")
    assert per_alias["github"]["presente"] is False
    assert per_alias["instagram"]["disponibile"] is False


async def test_accendere_un_provider_esistente(admin, keycloak, session):
    r = await admin.put("/admin/accesso-social/google", json={
        "abilitato": True, "client_id": "123.apps.googleusercontent.com", "client_secret": "segreto-google",
    })
    assert r.status_code == 200, r.text
    assert r.json()["abilitato"] is True and r.json()["segreto_impostato"] is True
    assert r.json()["client_id"] == "123.apps.googleusercontent.com"
    salvato = keycloak.provider["google"]
    assert salvato["enabled"] is True and salvato["internalId"] == "g-1"
    assert salvato["config"]["clientSecret"] == "segreto-google"

    voce = (await session.execute(
        select(AuditLog).where(AuditLog.action == "accesso_social.modifica")
    )).scalar_one()
    assert voce.target_id == "google" and voce.after["segreto_cambiato"] is True
    assert "segreto-google" not in json.dumps(voce.before) + json.dumps(voce.after)


async def test_senza_segreto_nuovo_si_tiene_quello_di_keycloak(admin, keycloak):
    await admin.put("/admin/accesso-social/google", json={
        "abilitato": True, "client_id": "id-vero", "client_secret": "primo-segreto",
    })
    r = await admin.put("/admin/accesso-social/google", json={"abilitato": False, "client_id": "id-vero"})
    assert r.status_code == 200, r.text
    assert keycloak.provider["google"]["config"]["clientSecret"] == "primo-segreto"
    assert keycloak.provider["google"]["enabled"] is False


async def test_un_provider_nuovo_si_crea_con_il_flusso_2fa_se_il_realm_lo_ha(admin, keycloak):
    keycloak.flussi.append(FLUSSO_DOPO_ACCESSO_ESTERNO)
    r = await admin.put("/admin/accesso-social/github", json={
        "abilitato": True, "client_id": "Iv1.abc", "client_secret": "s3greto",
    })
    assert r.status_code == 200, r.text
    creato = keycloak.provider["github"]
    assert ("POST", f"{PREFISSO}/identity-provider/instances", creato) in keycloak.scritture
    assert creato["providerId"] == "github" and creato["postBrokerLoginFlowAlias"] == FLUSSO_DOPO_ACCESSO_ESTERNO
    assert creato["config"]["defaultScope"] == "user:email"


async def test_senza_flusso_2fa_non_lo_si_inventa(admin, keycloak):
    await admin.put("/admin/accesso-social/linkedin", json={
        "abilitato": True, "client_id": "77abc", "client_secret": "s",
    })
    creato = keycloak.provider["linkedin"]
    assert creato["providerId"] == "linkedin-openid-connect" and "postBrokerLoginFlowAlias" not in creato


async def test_accendere_senza_credenziali_e_rifiutato(admin, keycloak):
    r = await admin.put("/admin/accesso-social/google", json={"abilitato": True, "client_id": "id-vero"})
    assert r.status_code == 422  # il segreto del manifest è un segnaposto: serve quello vero
    r = await admin.put("/admin/accesso-social/google", json={"abilitato": True, "client_secret": "s"})
    assert r.status_code == 422
    r = await admin.put("/admin/accesso-social/github", json={"abilitato": False, "client_id": "x"})
    assert r.status_code == 422  # nuovo: Keycloak pretende un segreto
    assert keycloak.scritture == []


async def test_instagram_e_un_provider_sconosciuto(admin, keycloak):
    r = await admin.put("/admin/accesso-social/instagram", json={"abilitato": True, "client_id": "a", "client_secret": "b"})
    assert r.status_code == 400 and "Basic Display" in r.json()["detail"]
    assert (await admin.put("/admin/accesso-social/myspace", json={"abilitato": False})).status_code == 404


async def test_il_ruolo_mancante_si_spiega(admin, keycloak):
    keycloak.vietato = True
    r = await admin.get("/admin/accesso-social")
    assert r.status_code == 200
    assert r.json()["keycloak_raggiungibile"] is False
    assert "manage-identity-providers" in r.json()["errore"]
    assert all(p["uri_reindirizzamento"] for p in r.json()["provider"])  # guide e indirizzi restano

    r = await admin.put("/admin/accesso-social/google", json={"abilitato": False, "client_id": "a", "client_secret": "b"})
    assert r.status_code == 502 and "manage-identity-providers" in r.json()["detail"]


# ---- login persistente -------------------------------------------------------------------------


async def test_sessione_letta_da_keycloak(admin, keycloak):
    r = await admin.get("/admin/impostazioni-sessione")
    assert r.status_code == 200
    assert r.json() == {
        "keycloak_raggiungibile": True, "errore": None, "inattivita_giorni": 30, "durata_massima_giorni": 0,
    }


async def test_sessione_fino_al_logout(admin, keycloak, session):
    r = await admin.put("/admin/impostazioni-sessione", json={"inattivita_giorni": 365, "durata_massima_giorni": 0})
    assert r.status_code == 200, r.text
    assert r.json()["inattivita_giorni"] == 365 and r.json()["durata_massima_giorni"] == 0
    assert keycloak.realm["offlineSessionIdleTimeout"] == 365 * 86_400
    assert keycloak.realm["offlineSessionMaxLifespanEnabled"] is False

    voce = (await session.execute(
        select(AuditLog).where(AuditLog.action == "impostazioni_sessione.modifica")
    )).scalar_one()
    assert voce.before == {"inattivita_giorni": 30, "durata_massima_giorni": 0}
    assert voce.after == {"inattivita_giorni": 365, "durata_massima_giorni": 0}


async def test_sessione_con_durata_massima(admin, keycloak):
    r = await admin.put("/admin/impostazioni-sessione", json={"inattivita_giorni": 30, "durata_massima_giorni": 90})
    assert r.status_code == 200
    assert keycloak.realm["offlineSessionMaxLifespanEnabled"] is True
    assert keycloak.realm["offlineSessionMaxLifespan"] == 90 * 86_400
    assert r.json()["durata_massima_giorni"] == 90


async def test_sessione_limiti(admin, keycloak):
    assert (await admin.put("/admin/impostazioni-sessione", json={"inattivita_giorni": 0})).status_code == 422
    r = await admin.put("/admin/impostazioni-sessione", json={"inattivita_giorni": 60, "durata_massima_giorni": 30})
    assert r.status_code == 422
    assert keycloak.scritture == []


async def test_sessione_con_keycloak_che_rifiuta(admin, keycloak):
    keycloak.vietato = True
    r = await admin.get("/admin/impostazioni-sessione")
    assert r.status_code == 200 and r.json()["keycloak_raggiungibile"] is False
    assert r.json()["inattivita_giorni"] is None
    r = await admin.put("/admin/impostazioni-sessione", json={"inattivita_giorni": 30})
    assert r.status_code == 502 and "Keycloak non ha accettato" in r.json()["detail"]
