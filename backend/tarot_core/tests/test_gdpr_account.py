"""GDPR, Fase 1: esportazione dei dati, cancellazione dell'account (con l'annullamento e il giro dei 30 giorni),
console «Conservazione dati», cancellazione della chat. Keycloak è finto (HTTP in memoria, come in
`test_admin_accesso_social.py`)."""
from __future__ import annotations

import io
import json
import zipfile
from datetime import timedelta
from typing import List, Tuple

import httpx
import pytest
from sqlalchemy import func, select

from tarot_core.api.routers import privacy
from tarot_core.auth.keycloak_admin import KeycloakAdmin
from tarot_core.domain.base import utcnow
from tarot_core.domain.billing_models import CreditEntry
from tarot_core.domain.chat_models import ChatProattivaTurno
from tarot_core.domain.consent_models import ConsensoStorico
from tarot_core.domain.memory_models import UserMemory
from tarot_core.domain.models import AuditLog, Reading, User
from tarot_core.domain.ordini_models import IndirizzoSpedizione
from tarot_core.settings import Settings
from tarot_core.tarot import cancellazione

from .conftest import richiede_database
from .test_flusso import _accredita, _lettura_completa

pytestmark = richiede_database


class KeycloakFinto:
    """Quanto basta dell'Admin API: il token, le sessioni di un utente, il logout, i consensi dei client, la
    cancellazione. Registra ogni chiamata."""

    def __init__(self, *, giu: bool = False) -> None:
        self.chiamate: List[Tuple[str, str]] = []
        self.utenti = {"sub-utente-1"}
        self.giu = giu

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if self.giu:
            raise httpx.ConnectError("Keycloak spento")
        percorso = request.url.path
        if percorso.endswith("/protocol/openid-connect/token"):
            return httpx.Response(200, json={"access_token": "t", "expires_in": 300})
        self.chiamate.append((request.method, percorso.split("/admin/realms/tarots", 1)[1]))
        if percorso.endswith("/sessions") and request.method == "GET":
            return httpx.Response(200, json=[{"id": "s-1"}, {"id": "s-2"}])
        if request.method == "DELETE" and percorso.endswith("/users/sub-utente-1"):
            if "sub-utente-1" not in self.utenti:
                return httpx.Response(404)
            self.utenti.discard("sub-utente-1")
        return httpx.Response(204)

    def admin(self) -> KeycloakAdmin:
        impostazioni = Settings(keycloak_url="http://kc", keycloak_client_secret="segreto")
        return KeycloakAdmin(impostazioni, transport=httpx.MockTransport(self))


@pytest.fixture
def keycloak(monkeypatch) -> KeycloakFinto:
    finto = KeycloakFinto()
    monkeypatch.setattr(privacy, "keycloak_admin", finto.admin)
    return finto


# ---- esportazione -----------------------------------------------------------------------------------------------


async def test_l_esportazione_e_uno_zip_con_tutti_i_dati_una_volta_al_giorno(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await client.patch("/me/profile", json={"nome": "Anna"})
    await client.post("/consenso", json={"tipo": "marketing", "valore": "rifiutato", "versione_informativa": "v3"})
    await _lettura_completa(client, "tre-carte", 3)
    await client.post("/chat/proattiva/messaggio", json={"testo": "Ciao oracolo"})

    r = await client.get("/me/esportazione")
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/zip"
    archivio = zipfile.ZipFile(io.BytesIO(r.content))
    nomi = set(archivio.namelist())
    assert {"profilo.json", "letture.json", "memorie.json", "chat.json", "consensi.json", "crediti.json",
            "abbonamenti.json", "ordini.json", "dati_social.json", "altro.json", "LEGGIMI.txt"} <= nomi
    profilo = json.loads(archivio.read("profilo.json"))
    assert profilo["nome"] == "Anna" and "keycloak_sub" not in profilo
    [lettura] = json.loads(archivio.read("letture.json"))
    assert lettura["question"] and lettura["intervista"] and len(lettura["carte"]) == 3
    assert "deck_salt" not in lettura and "deck_state" not in lettura
    consensi = json.loads(archivio.read("consensi.json"))
    assert consensi["attuali"][0]["tipo"] == "marketing" and consensi["storico"][0]["ip"] == "127.0.0.0"
    assert "ip_hash" not in consensi["storico"][0]
    assert any(c["delta"] == 5 for c in json.loads(archivio.read("crediti.json")))
    assert [t["ruolo"] for t in json.loads(archivio.read("chat.json"))] == ["utente", "ai"]

    seconda = await client.get("/me/esportazione")
    assert seconda.status_code == 429 and int(seconda.headers["retry-after"]) > 0
    stato = (await client.get("/me/privacy")).json()
    assert stato["esportazione"]["ultima_il"] and stato["esportazione"]["prossima_dal"]


# ---- cancellazione dell'account -------------------------------------------------------------------------------------


async def test_senza_riconferma_non_si_cancella_niente(client, keycloak):
    r = await client.post("/me/cancellazione", json={"conferma": False})
    assert r.status_code == 422
    assert keycloak.chiamate == []


async def test_la_cancellazione_chiude_le_sessioni_e_si_puo_annullare(client, session, keycloak):
    assert (await client.get("/me/profile")).status_code == 200
    r = await client.post("/me/cancellazione", json={"conferma": True})
    assert r.status_code == 200, r.text
    assert r.json()["sessioni_chiuse"] is True and r.json()["annullabile"] is True
    assert ("DELETE", "/sessions/s-1") in keycloak.chiamate and ("DELETE", "/sessions/s-2") in keycloak.chiamate
    assert ("POST", "/users/sub-utente-1/logout") in keycloak.chiamate
    assert ("DELETE", "/users/sub-utente-1/consents/tarot-frontend") in keycloak.chiamate     # i token offline
    assert not any(m == "DELETE" and p == "/users/sub-utente-1" for m, p in keycloak.chiamate)  # l'utente resta

    # Rientrando: ogni endpoint normale risponde 409, la richiesta si vede e si annulla.
    r = await client.get("/me/profile")
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "account_in_cancellazione"
    assert (await client.get("/me/cancellazione")).json()["richiesta_il"]
    assert (await client.get("/me/esportazione")).status_code == 200          # i dati si possono ancora scaricare
    r = await client.post("/me/cancellazione/annulla")
    assert r.status_code == 200 and r.json()["richiesta_il"] is None
    assert (await client.get("/me/profile")).status_code == 200
    azioni = set((await session.execute(select(AuditLog.action).where(AuditLog.action.like("account.%")))).scalars())
    assert {"account.cancellazione_richiesta", "account.cancellazione_annullata"} <= azioni


async def test_se_keycloak_non_risponde_l_account_si_chiude_lo_stesso(client, monkeypatch):
    finto = KeycloakFinto(giu=True)
    monkeypatch.setattr(privacy, "keycloak_admin", finto.admin)
    r = await client.post("/me/cancellazione", json={"conferma": True})
    assert r.status_code == 200 and r.json()["sessioni_chiuse"] is False
    assert (await client.get("/me/profile")).status_code == 409


async def test_dopo_30_giorni_il_giro_notturno_cancella_i_dati_e_tiene_la_contabilita(
    client, session, session_factory, catalogo, keycloak,
):
    utente = await _accredita(session, client.identita.principal, 5)
    uid = utente.id
    await client.patch("/me/profile", json={"nome": "Anna", "cognome": "Verdi", "birth_date": "1990-03-14"})
    await _lettura_completa(client, "tre-carte", 3)
    session.add(UserMemory(owner_id=uid, contenuto="un fatto", tipo="stabile", campo_attinenza="lavoro",
                           embedding=[0.1], fonte="lettura"))
    session.add(IndirizzoSpedizione(user_id=uid, nome="Anna Verdi", via="Via Roma 1", citta="Milano",
                                    cap="20100", paese="IT"))
    await client.post("/chat/proattiva/messaggio", json={"testo": "Ciao"})
    await client.post("/consenso", json={"tipo": "marketing", "valore": "accettato", "versione_informativa": "v3"})
    await session.commit()
    movimenti_prima = await session.scalar(select(func.count()).select_from(CreditEntry).where(CreditEntry.user_id == uid))
    assert (await client.post("/me/cancellazione", json={"conferma": True})).status_code == 200

    # A 29 giorni non tocca niente.
    esito = await cancellazione.esegui_scadute(session_factory, keycloak.admin(), adesso=utcnow() + timedelta(days=29))
    assert esito == {"eseguite": [], "fallite": []}

    esito = await cancellazione.esegui_scadute(session_factory, keycloak.admin(), adesso=utcnow() + timedelta(days=31))
    assert esito == {"eseguite": [uid], "fallite": []}
    assert ("DELETE", "/users/sub-utente-1") in keycloak.chiamate

    riga = (await session.execute(
        select(User).where(User.id == uid).execution_options(populate_existing=True)
    )).scalar_one()
    assert riga.keycloak_sub.startswith("cancellato:") and riga.cancellazione_eseguita_il is not None
    assert riga.email is None and riga.nome is None and riga.cognome is None and riga.birth_date is None
    for modello, colonna in ((Reading, Reading.owner_id), (UserMemory, UserMemory.owner_id),
                             (ChatProattivaTurno, ChatProattivaTurno.owner_id), (IndirizzoSpedizione, IndirizzoSpedizione.user_id)):
        assert await session.scalar(select(func.count()).select_from(modello).where(colonna == uid)) == 0, modello
    # La contabilità resta, legata allo pseudonimo; lo storico dei consensi pure.
    assert await session.scalar(select(func.count()).select_from(CreditEntry).where(CreditEntry.user_id == uid)) == movimenti_prima
    assert await session.scalar(select(func.count()).select_from(ConsensoStorico).where(ConsensoStorico.user_id == uid)) >= 1

    # Lo stesso accesso di prima ora è una persona nuova, senza niente.
    r = await client.get("/me/profile")
    assert r.status_code == 200 and r.json()["id"] != uid


async def test_se_keycloak_non_risponde_il_giro_non_cancella_e_riprova(client, session, session_factory, keycloak):
    assert (await client.post("/me/cancellazione", json={"conferma": True})).status_code == 200
    esito = await cancellazione.esegui_scadute(
        session_factory, KeycloakFinto(giu=True).admin(), adesso=utcnow() + timedelta(days=31),
    )
    assert len(esito["fallite"]) == 1 and esito["eseguite"] == []
    riga = (await session.execute(select(User).where(User.keycloak_sub == "sub-utente-1"))).scalar_one()
    assert riga.cancellazione_eseguita_il is None


# ---- console «Conservazione dati» -----------------------------------------------------------------------------------


async def test_la_console_conta_per_eta_e_cancella_con_anteprima(client, session, principal_admin):
    vecchia = Reading(owner_id=None, anon_id="anon-vecchio", spread_id="tre-carte", question="Q vecchia?",
                      consumo="anonimo", lang="it", status="completata")
    nuova = Reading(owner_id=None, anon_id="anon-nuovo", spread_id="tre-carte", question="Q nuova?",
                    consumo="anonimo", lang="it", status="completata")
    session.add_all([vecchia, nuova])
    await session.flush()
    vecchia.created_at = utcnow() - timedelta(days=400)
    await session.commit()

    client.identita.principal = principal_admin
    riepilogo = (await client.get("/admin/conservazione")).json()
    voce = next(v for v in riepilogo["voci"] if v["chiave"] == "letture_anonime")
    assert voce["totale"] == 2
    assert {f["etichetta"]: f["quanti"] for f in voce["fasce"]}["1 – 2 anni"] == 1
    assert {v["chiave"] for v in riepilogo["voci"]} == {
        "letture_anonime", "chat_proattiva", "ip_audit", "account_in_cancellazione", "consensi_storici",
    }

    anteprima = (await client.post("/admin/conservazione/letture_anonime/anteprima", json={"giorni": 365})).json()
    assert anteprima["quanti"] == 1
    sbagliata = await client.post("/admin/conservazione/letture_anonime/esegui", json={"giorni": 365, "attesi": 2})
    assert sbagliata.status_code == 409
    r = await client.post("/admin/conservazione/letture_anonime/esegui", json={"giorni": 365, "attesi": 1})
    assert r.status_code == 200 and r.json()["fatti"] == 1
    rimaste = (await session.execute(select(Reading.anon_id).where(Reading.owner_id.is_(None)))).scalars().all()
    assert rimaste == ["anon-nuovo"]
    [voce_audit] = (await session.execute(
        select(AuditLog).where(AuditLog.action == "conservazione.letture_anonime")
    )).scalars().all()
    assert voce_audit.after["fatti"] == 1 and voce_audit.actor_id is not None


async def test_la_console_toglie_gli_ip_e_tiene_l_ultima_scelta_dei_consensi(client, session, utente, principal_admin):
    for valore in ("accettato", "rifiutato"):
        await client.post("/consenso", json={"tipo": "marketing", "valore": valore, "versione_informativa": "v3"})
    client.identita.principal = principal_admin
    quanti = (await client.post("/admin/conservazione/consensi_storici/anteprima", json={"giorni": 0})).json()["quanti"]
    assert quanti == 1                                       # la prima scelta: la seconda è quella in vigore
    r = await client.post("/admin/conservazione/consensi_storici/esegui", json={"giorni": 0, "attesi": 1})
    assert r.status_code == 200, r.text
    rimasto = (await session.execute(
        select(ConsensoStorico.valore).where(ConsensoStorico.user_id == utente.id, ConsensoStorico.tipo == "marketing")
    )).scalars().all()
    assert rimasto == ["rifiutato"]

    con_ip = (await client.post("/admin/conservazione/ip_audit/anteprima", json={"giorni": 0})).json()["quanti"]
    assert con_ip > 0
    r = await client.post("/admin/conservazione/ip_audit/esegui", json={"giorni": 0, "attesi": con_ip})
    assert r.status_code == 200
    # Restano solo l'IP della voce che registra questa esecuzione.
    assert await session.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.ip.is_not(None))) == 1


async def test_la_console_esegue_subito_una_cancellazione_in_attesa(client, session, keycloak, principal_admin):
    assert (await client.post("/me/cancellazione", json={"conferma": True})).status_code == 200
    client.identita.principal = principal_admin
    quanti = (await client.post("/admin/conservazione/account_in_cancellazione/anteprima", json={"giorni": 0})).json()["quanti"]
    assert quanti == 1
    r = await client.post("/admin/conservazione/account_in_cancellazione/esegui", json={"giorni": 0, "attesi": 1})
    assert r.status_code == 200 and r.json()["fatti"] == 1 and r.json()["falliti"] == []
    assert ("DELETE", "/users/sub-utente-1") in keycloak.chiamate


async def test_la_console_e_solo_per_gli_amministratori(client):
    assert (await client.get("/admin/conservazione")).status_code == 403


# ---- la chat si cancella ------------------------------------------------------------------------------------------


async def test_un_messaggio_della_chat_e_tutta_la_chat_si_cancellano(client, session, principal_utente, principal_altro):
    await client.post("/chat/proattiva/messaggio", json={"testo": "Primo"})
    await client.post("/chat/proattiva/messaggio", json={"testo": "Secondo"})
    turni = (await client.get("/chat/proattiva")).json()["turni"]
    assert len(turni) == 4
    primo = turni[0]["id"]

    client.identita.principal = principal_altro
    assert (await client.delete(f"/chat/proattiva/{primo}")).status_code == 404      # non è suo

    client.identita.principal = principal_utente
    assert (await client.delete(f"/chat/proattiva/{primo}")).status_code == 204
    assert len((await client.get("/chat/proattiva")).json()["turni"]) == 3
    assert (await client.delete("/chat/proattiva")).status_code == 204
    assert (await client.get("/chat/proattiva")).json()["turni"] == []
