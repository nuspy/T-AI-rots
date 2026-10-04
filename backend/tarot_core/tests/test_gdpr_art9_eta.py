"""GDPR, Fase 1: le categorie particolari (art. 9) e l'età minima."""
from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import select

from tarot_core.domain.analytics_models import TABELLE
from tarot_core.domain.consent_models import ConsensoStorico
from tarot_core.domain.memory_models import UserMemory
from tarot_core.domain.models import AuditLog, User
from tarot_core.tarot import eta_minima
from tarot_core.tarot.memoria import estrai_e_salva

from .conftest import richiede_database
from .test_flusso import _accredita, _lettura_completa
from .test_lettura_speciale import PARTNER, QUESITO, _scheda

VERSIONE = "v3"


async def _consenso(client, tipo, valore="accettato"):
    r = await client.post("/consenso", json={"tipo": tipo, "valore": valore, "versione_informativa": VERSIONE})
    assert r.status_code == 200, r.text


# ---- art. 9: «persona trans» -----------------------------------------------------------------------------------


@richiede_database
async def test_senza_consenso_trans_non_arriva_al_modello_ne_si_salva(client, session, catalogo, prompt_visti):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client, gender="donna")
    # Una casella «trans» già salvata prima della Fase 1 (senza consenso): non deve uscire.
    utente = (await session.execute(select(User).where(User.keycloak_sub == "sub-utente-1"))).scalar_one()
    utente.is_trans = True
    await session.commit()
    await _lettura_completa(client, "coppia-specchio", 8, QUESITO, {"partner": {**PARTNER, "trans": True}})
    assert prompt_visti
    for v in prompt_visti:
        assert "persona trans" not in v["utente"], v["compito"]
    [lettura] = (await client.get("/me/readings")).json()["letture"]
    dettaglio = (await client.get(f"/me/readings/{lettura['id']}")).json()
    assert dettaglio["persone"]["tu"]["trans"] is False and dettaglio["persone"]["partner"]["trans"] is False


@richiede_database
async def test_col_consenso_trans_arriva_al_modello(client, session, catalogo, prompt_visti):
    await _accredita(session, client.identita.principal, 5)
    await _consenso(client, "dati_particolari")
    await _scheda(client, gender="donna", is_trans=True)
    await _lettura_completa(client, "coppia-specchio", 8, QUESITO, {"partner": {**PARTNER, "trans": True}})
    intervista = [v for v in prompt_visti if v["compito"] == "intervista"]
    assert intervista and all("genere donna, persona trans" in v["utente"] for v in intervista)


@richiede_database
async def test_revocare_a_meta_lettura_ferma_trans_ai_prompt_successivi(client, session, catalogo, prompt_visti):
    await _accredita(session, client.identita.principal, 5)
    await _consenso(client, "dati_particolari")
    await _scheda(client, gender="donna", is_trans=True)
    r = await client.post("/readings", json={"spread_id": "coppia-specchio", "question": QUESITO, "partner": PARTNER})
    assert r.status_code == 201, r.text
    await _consenso(client, "dati_particolari", "rifiutato")
    await client.post(f"/readings/{r.json()['id']}/interview", json={})
    intervista = [v for v in prompt_visti if v["compito"] == "intervista"]
    assert intervista and all("persona trans" not in v["utente"] for v in intervista)


# ---- art. 9: la crisi si conta senza la persona -------------------------------------------------------------


@richiede_database
async def test_la_crisi_si_registra_senza_utente(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Voglio morire, che cosa faccio?"})
    assert r.status_code == 201 and r.json()["crisi"] is True
    [voce] = (await session.execute(select(AuditLog).where(AuditLog.action == "reading.crisis"))).scalars().all()
    assert voce.actor_id is None and voce.target_id is None and voce.target_type is None
    assert voce.after == {"fase": "apertura"}
    e = TABELLE.eventi
    eventi = (await session.execute(select(e).where(e.c.nome == "lettura_crisi"))).mappings().all()
    assert len(eventi) == 1 and eventi[0]["utente_id"] is None


@richiede_database
async def test_la_crisi_nell_intervista_non_lega_registro_ne_crediti_alla_crisi(client, session, catalogo):
    from tarot_core.domain.billing_models import CreditEntry

    utente = await _accredita(session, client.identita.principal, 5)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Come andrà il lavoro?"})
    rid = r.json()["id"]
    await client.post(f"/readings/{rid}/interview", json={})
    r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Non voglio più vivere"})
    assert r.json()["crisi"] is True
    [voce] = (await session.execute(select(AuditLog).where(AuditLog.action == "reading.crisis"))).scalars().all()
    assert voce.actor_id is None and voce.target_id is None
    note = (await session.execute(select(CreditEntry.note).where(CreditEntry.user_id == utente.id))).scalars().all()
    assert not any("crisi" in (n or "") for n in note)


# ---- art. 9: i ricordi sulla salute ----------------------------------------------------------------------------


class _Estrattore:
    def __init__(self, memorie):
        self.memorie = memorie

    async def complete_json(self, req):
        return {"memorie": self.memorie}


class _Vettori:
    async def embed(self, testi):
        return [[0.1, 0.2] for _ in testi]


@richiede_database
@pytest.mark.parametrize("ammessa, attesi", [(False, {"lavoro"}), (True, {"lavoro", "salute"})])
async def test_i_ricordi_sulla_salute_solo_col_consenso(session_factory, session, utente, ammessa, attesi):
    memorie = [
        {"contenuto": "Ha cambiato lavoro", "tipo": "variabile", "campo_attinenza": "lavoro"},
        {"contenuto": "Ha una malattia cronica", "tipo": "stabile", "campo_attinenza": "salute"},
    ]
    await session.commit()
    await estrai_e_salva(
        session_factory, utente.id, None, quesito="q", colloquio="c", sintesi="s",
        provider_estrazione=_Estrattore(memorie), provider_embedding=_Vettori(), salute_ammessa=ammessa,
    )
    campi = set((await session.execute(
        select(UserMemory.campo_attinenza).where(UserMemory.owner_id == utente.id)
    )).scalars())
    assert campi == attesi


# ---- pseudonimi nella chat e nelle memorie -----------------------------------------------------------------------


@richiede_database
async def test_la_chat_non_manda_i_nomi_della_persona(client, session, prompt_visti):
    await client.patch("/me/profile", json={"nome": "Gianfranco", "cognome": "Bertolazzi"})
    r = await client.post("/chat/proattiva/messaggio", json={"testo": "Sono Gianfranco e parlo di Bertolazzi"})
    assert r.status_code == 200, r.text
    chat = [v for v in prompt_visti if v["compito"] == "chat_proattiva"]
    assert chat and all("Gianfranco" not in v["utente"] and "Bertolazzi" not in v["utente"] for v in chat)
    assert any("Persona_" in v["utente"] for v in chat)


@richiede_database
async def test_la_modifica_di_una_memoria_vettorizza_senza_nomi(client, session, utente, monkeypatch):
    from tarot_core.api.routers import profile

    visti = []

    class Embed:
        async def embed(self, testi):
            visti.extend(testi)
            return [[0.3] for _ in testi]

    from tarot_core.tarot.pseudonimi import protetto

    monkeypatch.setattr(profile, "provider_per", lambda compito, persone=None: protetto(Embed(), persone))
    await client.patch("/me/profile", json={"nome": "Gianfranco"})
    memoria = UserMemory(owner_id=utente.id, contenuto="vecchio", tipo="stabile", campo_attinenza="lavoro",
                         embedding=[0.1], fonte="lettura")
    session.add(memoria)
    await session.commit()
    r = await client.patch(f"/me/memories/{memoria.id}", json={"contenuto": "Gianfranco ha un lavoro nuovo"})
    assert r.status_code == 200, r.text
    assert r.json()["contenuto"] == "Gianfranco ha un lavoro nuovo"
    assert visti and all("Gianfranco" not in t for t in visti)


# ---- età minima ---------------------------------------------------------------------------------------------------


def test_le_eta_per_paese_e_il_minimo_predefinito():
    assert eta_minima.anni_minimi("IT") == 14 and eta_minima.anni_minimi("es") == 14
    assert eta_minima.anni_minimi("FR") == 15
    assert eta_minima.anni_minimi("DE") == 16 and eta_minima.anni_minimi(None) == 16
    oggi = date(2026, 10, 3)
    assert eta_minima.anni_compiuti(date(2012, 10, 4), oggi) == 13
    assert eta_minima.anni_compiuti(date(2012, 10, 3), oggi) == 14


@richiede_database
@pytest.mark.eta_vera
async def test_senza_conferma_dell_eta_niente_letture_ne_chat(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Come andrà il lavoro?"})
    assert r.status_code == 403 and r.json()["detail"]["motivo"] == "eta_da_confermare"
    assert r.json()["detail"]["anni"] == 16                 # paese sconosciuto: il minimo predefinito
    r = await client.post("/chat/proattiva/messaggio", json={"testo": "ciao"})
    assert r.status_code == 403
    profilo = (await client.get("/me/profile")).json()
    assert profilo["eta"]["da_confermare"] is True and profilo["eta"]["anni"] == 16


@richiede_database
@pytest.mark.eta_vera
async def test_la_conferma_dell_eta_sblocca_e_resta_nello_storico(client, session, catalogo):
    await client.patch("/me/profile", json={"posizione_paese": "IT"})
    utente = await _accredita(session, client.identita.principal, 5)
    assert (await client.post("/me/eta", json={"anni": 13})).status_code == 422      # sotto il minimo italiano
    r = await client.post("/me/eta", json={"anni": 14})
    assert r.status_code == 200, r.text
    assert r.json()["da_confermare"] is False and r.json()["anni"] == 14
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Come andrà il lavoro?"})
    assert r.status_code == 201, r.text
    [prova] = (await session.execute(
        select(ConsensoStorico).where(ConsensoStorico.user_id == utente.id, ConsensoStorico.tipo == "eta_minima")
    )).scalars().all()
    assert prova.valore == "confermato" and prova.versione_informativa.endswith(":14") and prova.ip == "127.0.0.0"


@richiede_database
@pytest.mark.eta_vera
async def test_in_francia_14_anni_non_bastano(client):
    await client.patch("/me/profile", json={"posizione_paese": "FR"})
    r = await client.post("/me/eta", json={"anni": 14})
    assert r.status_code == 422 and r.json()["detail"]["anni"] == 15


@richiede_database
@pytest.mark.eta_vera
async def test_una_data_di_nascita_sotto_il_minimo_non_si_salva_e_toglie_la_conferma(client, session):
    await client.patch("/me/profile", json={"posizione_paese": "IT"})
    assert (await client.post("/me/eta", json={"anni": 14})).status_code == 200
    nascita = date(date.today().year - 12, 1, 1).isoformat()
    r = await client.patch("/me/profile", json={"birth_date": nascita})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "eta_insufficiente"
    profilo = (await client.get("/me/profile")).json()
    assert profilo["birth_date"] is None and profilo["eta"]["da_confermare"] is True


@richiede_database
@pytest.mark.eta_vera
async def test_la_lettura_anonima_chiede_l_eta(client):
    client.identita.principal = None
    corpo = {"spread_id": "tre-carte", "question": "Come andrà il mio anno?"}
    r = await client.post("/readings/anonime", json=corpo)
    assert r.status_code == 403 and r.json()["detail"]["motivo"] == "eta_da_confermare"
    minimo = (await client.get("/eta-minima")).json()["anni"]
    r = await client.post("/readings/anonime", json={**corpo, "eta_confermata": True, "eta_anni": minimo})
    assert r.status_code == 201, r.text
