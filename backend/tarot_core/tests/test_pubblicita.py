"""Gli spazi pubblicitari: spenti per default, solo l'amministratore li configura, il sito riceve solo ciò che gli
serve (mai i dati di registrazione), `ads.txt` dall'ID editore, audit di ogni cambio, consenso «pubblicita»."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from tarot_core.domain.models import AuditLog

from .conftest import richiede_database

pytestmark = richiede_database

EDITORE = "ca-pub-1234567890123456"


@pytest.fixture
def come(client, principal_utente, principal_admin):
    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


async def _configura_google(admin, **parametri):
    corpo = {
        "editore": EDITORE,
        "slot": {"terzo": "1111111111", "due_terzi": "2222222222", "fine": "3333333333"},
        **parametri,
    }
    r = await admin.put("/admin/pubblicita/fornitori/google", json={"parametri": corpo})
    assert r.status_code == 200, r.text
    return r


async def test_spenta_per_default_e_il_sito_non_riceve_nulla(come, client):
    r = await come("admin").get("/admin/pubblicita")
    assert r.status_code == 200
    dati = r.json()
    assert dati["generale"]["attiva"] is False
    assert dati["generale"]["posizioni"] == {"terzo": True, "due_terzi": True, "fine": True}
    assert dati["fornitori"]["google"]["pronto"] is False
    assert dati["catalogo"]["posizioni"] == ["terzo", "due_terzi", "fine"]

    client.identita.principal = None
    assert (await client.get("/impostazioni-pubblicita")).json() == {"attiva": False}
    assert (await client.get("/ads.txt")).status_code == 404


async def test_solo_l_amministratore_configura(come):
    utente = come("utente")
    assert (await utente.get("/admin/pubblicita")).status_code == 403
    assert (await utente.put("/admin/pubblicita", json={"attiva": True})).status_code == 403
    r = await utente.put("/admin/pubblicita/fornitori/google", json={"parametri": {"editore": EDITORE}})
    assert r.status_code == 403


async def test_non_si_accende_senza_id_editore(come):
    r = await come("admin").put("/admin/pubblicita", json={"attiva": True})
    assert r.status_code == 422
    assert "ID editore" in r.json()["detail"]


async def test_valori_sbagliati_rifiutati(come):
    admin = come("admin")
    r = await admin.put("/admin/pubblicita/fornitori/google", json={"parametri": {"editore": "G-123"}})
    assert r.status_code == 422
    r = await admin.put("/admin/pubblicita/fornitori/google", json={"parametri": {"slot": {"terzo": "abc"}}})
    assert r.status_code == 422
    r = await admin.put("/admin/pubblicita/fornitori/google", json={"parametri": {"formato": {"fine": "enorme"}}})
    assert r.status_code == 422
    r = await admin.put("/admin/pubblicita/fornitori/google", json={"registrazione": {"stato": "boh"}})
    assert r.status_code == 422
    r = await admin.put("/admin/pubblicita", json={"pagine_escluse": ["senza-barra"]})
    assert r.status_code == 422


async def test_pub_senza_ca_si_normalizza(come):
    r = await come("admin").put(
        "/admin/pubblicita/fornitori/google", json={"parametri": {"editore": "pub-1234567890123456"}})
    assert r.status_code == 200
    assert r.json()["fornitori"]["google"]["parametri"]["editore"] == EDITORE


async def test_accesa_il_sito_riceve_slot_e_caselle_ma_non_la_registrazione(come, client):
    admin = come("admin")
    await _configura_google(admin, formato={"fine": "horizontal"}, prova=True)
    r = await admin.put("/admin/pubblicita/fornitori/google", json={"registrazione": {
        "email": "conto@example.com", "titolare": "Mario Rossi", "id_cliente": "123-456-7890",
        "data_iscrizione": "2026-10-01", "stato": "in_revisione", "note": "in attesa di Google",
    }})
    assert r.status_code == 200
    reg = r.json()["fornitori"]["google"]["registrazione"]
    assert reg["email"] == "conto@example.com" and reg["data_iscrizione"] == "2026-10-01"

    r = await admin.put("/admin/pubblicita", json={
        "attiva": True, "posizioni": {"due_terzi": False}, "pagine_escluse": ["/pricing/", "/it/prezzi"],
    })
    assert r.status_code == 200, r.text
    assert r.json()["generale"]["pagine_escluse"] == ["/pricing", "/it/prezzi"]

    client.identita.principal = None
    pubblica = (await client.get("/impostazioni-pubblicita")).json()
    assert pubblica["attiva"] is True
    assert set(pubblica["posizioni"]) == {"terzo", "fine"}, "la casella spenta non arriva al sito"
    assert pubblica["posizioni"]["fine"] == {"slot": "3333333333", "formato": "horizontal"}
    assert pubblica["google"] == {"editore": EDITORE, "responsive": True, "prova": True, "personalizzati": False}
    assert pubblica["pagine_escluse"] == ["/pricing", "/it/prezzi"]
    testo = str(pubblica)
    for privato in ("conto@example.com", "Mario Rossi", "123-456-7890", "in_revisione", "registrazione"):
        assert privato not in testo


async def test_tutte_le_caselle_spente_vuol_dire_spenta(come, client):
    admin = come("admin")
    await _configura_google(admin)
    spente = {"terzo": False, "due_terzi": False, "fine": False}
    await admin.put("/admin/pubblicita", json={"attiva": True, "posizioni": spente})
    client.identita.principal = None
    assert (await client.get("/impostazioni-pubblicita")).json() == {"attiva": False}


async def test_una_posizione_senza_slot_non_si_mostra(come, client):
    admin = come("admin")
    await _configura_google(admin, slot={"terzo": "1111111111", "due_terzi": "", "fine": ""})
    await admin.put("/admin/pubblicita", json={"attiva": True})
    client.identita.principal = None
    assert set((await client.get("/impostazioni-pubblicita")).json()["posizioni"]) == {"terzo"}


async def test_ads_txt_anche_a_pubblicita_spenta(come, client):
    await _configura_google(come("admin"))
    client.identita.principal = None
    r = await client.get("/ads.txt")
    assert r.status_code == 200
    assert r.text == "google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0\n"
    assert r.headers["content-type"].startswith("text/plain")


async def test_ogni_cambio_lascia_traccia_e_uno_inutile_no(come, session):
    admin = come("admin")
    await _configura_google(admin)
    await admin.put("/admin/pubblicita", json={"attiva": True})
    await admin.put("/admin/pubblicita", json={"attiva": True})  # nessun cambio
    azioni = (await session.execute(
        select(AuditLog.action).where(AuditLog.action.like("pubblicita.%")).order_by(AuditLog.created_at)
    )).scalars().all()
    assert azioni.count("pubblicita.google") == 1
    assert azioni.count("pubblicita.impostazioni") == 1


async def test_il_consenso_alla_pubblicita_si_registra_a_parte(client):
    r = await client.post(
        "/consenso", json={"tipo": "pubblicita", "valore": "accettato", "versione_informativa": "v3"})
    assert r.status_code == 200
    stato = (await client.get("/consenso")).json()
    assert stato["pubblicita"] == "accettato"
    assert stato["cookie"] is None


# ---- i dettagli dei pagamenti (solo appunti della console) ----

PAGAMENTI = {
    "id_profilo": "1234-5678-9012", "beneficiario": "Ditta Esempio", "tipo_profilo": "azienda",
    "indirizzo": "Via Roma 1, Milano", "metodo": "bonifico", "banca": "Banca Esempio", "conto_ultime4": "1234",
    "soglia": 70, "valuta": "eur", "stato_fiscale": "inviate", "modulo_fiscale": "W-8BEN-E",
    "stato_pin": "verificato", "ultimo_pagamento": "2026-09-21", "note": "primo pagamento ricevuto",
}
URL_PAGAMENTI = "/admin/pubblicita/fornitori/google/pagamenti"


async def test_i_pagamenti_si_salvano_e_tornano_in_console(come):
    r = await come("admin").put(URL_PAGAMENTI, json=PAGAMENTI)
    assert r.status_code == 200, r.text
    p = r.json()["fornitori"]["google"]["pagamenti"]
    assert p["conto_ultime4"] == "1234" and p["valuta"] == "EUR" and p["ultimo_pagamento"] == "2026-09-21"
    assert p["tipo_profilo"] == "azienda" and p["soglia"] == 70


async def test_salvare_l_iscrizione_non_cancella_i_pagamenti_e_viceversa(come):
    admin = come("admin")
    await admin.put(URL_PAGAMENTI, json=PAGAMENTI)
    await admin.put("/admin/pubblicita/fornitori/google", json={"registrazione": {"email": "conto@example.com"}})
    google = (await admin.get("/admin/pubblicita")).json()["fornitori"]["google"]
    assert google["pagamenti"]["beneficiario"] == "Ditta Esempio"
    await admin.put(URL_PAGAMENTI, json={"note": "altro"})
    google = (await admin.get("/admin/pubblicita")).json()["fornitori"]["google"]
    assert google["registrazione"]["email"] == "conto@example.com"


@pytest.mark.parametrize("valore", [
    "IT60X0542811101000000123456", "IT60 X054 2811 1010 0000 0123 456", "12345", "4111111111111111",
])
async def test_l_iban_intero_si_rifiuta(come, valore):
    r = await come("admin").put(URL_PAGAMENTI, json={"conto_ultime4": valore})
    assert r.status_code == 422


@pytest.mark.parametrize("campo", ["note", "banca", "indirizzo", "beneficiario"])
@pytest.mark.parametrize("valore", ["IBAN IT60X0542811101000000123456", "carta 4111 1111 1111 1111"])
async def test_niente_iban_o_carte_nemmeno_nei_testi_liberi(come, session, campo, valore):
    r = await come("admin").put(URL_PAGAMENTI, json={campo: valore})
    assert r.status_code == 422
    voci = (await session.execute(
        select(AuditLog).where(AuditLog.action == "pubblicita.google.pagamenti"))).scalars().all()
    assert voci == []


async def test_scelte_sconosciute_rifiutate(come):
    admin = come("admin")
    for corpo in ({"tipo_profilo": "ente"}, {"stato_fiscale": "boh"}, {"stato_pin": "x"}, {"valuta": "EURO"}):
        assert (await admin.put(URL_PAGAMENTI, json=corpo)).status_code == 422


async def test_solo_l_amministratore_scrive_i_pagamenti(come):
    assert (await come("utente").put(URL_PAGAMENTI, json={"note": "x"})).status_code == 403


async def test_i_pagamenti_non_arrivano_al_sito(come, client):
    admin = come("admin")
    await _configura_google(admin)
    await admin.put(URL_PAGAMENTI, json=PAGAMENTI)
    await admin.put("/admin/pubblicita", json={"attiva": True})
    client.identita.principal = None
    pubblica = (await client.get("/impostazioni-pubblicita")).json()
    assert pubblica["attiva"] is True
    testo = str(pubblica)
    for privato in ("pagamenti", "1234-5678-9012", "Ditta Esempio", "Via Roma", "Banca Esempio", "W-8BEN",
                    "2026-09-21", "primo pagamento", "verificato", "azienda"):
        assert privato not in testo
    assert "Ditta" not in (await client.get("/ads.txt")).text


async def test_ogni_cambio_dei_pagamenti_lascia_traccia(come, session):
    admin = come("admin")
    await admin.put(URL_PAGAMENTI, json={"banca": "Banca Esempio"})
    await admin.put(URL_PAGAMENTI, json={"banca": "Banca Esempio"})  # nessun cambio
    voci = (await session.execute(
        select(AuditLog).where(AuditLog.action == "pubblicita.google.pagamenti"))).scalars().all()
    assert len(voci) == 1
    assert voci[0].before["banca"] == "" and voci[0].after["banca"] == "Banca Esempio"
