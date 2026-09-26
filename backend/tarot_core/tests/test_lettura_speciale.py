"""Le letture di compatibilità e di coppia, attraverso l'API e un database vero."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.models import Reading, User
from tarot_core.domain.repositories import UserRepository

from .conftest import richiede_database
from .test_flusso import _accredita, _lettura_completa
from .test_stese_speciali import ATTESE

pytestmark = richiede_database

PARTNER = {
    "nome": "Marco",
    "cognome": "Rossi",
    "genere": "uomo",
    "trans": False,
    "nascita": "1988-08-07",
}

QUESITO = "Compatibilità con Marco"


async def _scheda(client, **campi):
    """Completa la scheda personale come fa il frontend prima di aprire la lettura."""
    corpo = {"gender": "donna", "birth_date": "1990-03-14", **campi}
    r = await client.patch("/me/profile", json=corpo)
    assert r.status_code == 200, r.text
    return r.json()


async def _apri(client, spread_id="compat-tre", **extra):
    corpo = {"spread_id": spread_id, "question": QUESITO, "partner": PARTNER, **extra}
    return await client.post("/readings", json=corpo)


async def _saldo(client):
    return (await client.get("/me/billing")).json()["saldo"]


# ---- la scheda personale ----------------------------------------------------------------------


async def test_il_profilo_dice_cosa_manca_per_le_letture_speciali(client, session, catalogo):
    p = (await client.get("/me/profile")).json()
    assert p["gender"] is None and p["is_trans"] is False and p["partner_ricordato"] is None
    assert p["relazioni"] == {"completo": False, "mancanti": ["genere", "nascita"]}
    p = await _scheda(client)
    assert p["relazioni"] == {"completo": True, "mancanti": []}
    assert p["gender"] == "donna" and p["birth_date"] == "1990-03-14"


@pytest.mark.parametrize("genere", ["donna", "uomo", "non_binario", "non_dice"])
async def test_i_generi_della_scheda_si_salvano(client, session, catalogo, genere):
    assert (await _scheda(client, gender=genere))["gender"] == genere


async def test_altro_porta_un_testo_libero_che_si_azzera_se_il_genere_cambia(client, session, catalogo):
    p = await _scheda(client, gender="altro", gender_custom="  agender  ", is_trans=True)
    assert p["gender"] == "altro" and p["gender_custom"] == "agender" and p["is_trans"] is True
    p = (await client.patch("/me/profile", json={"gender": "donna"})).json()
    assert p["gender_custom"] is None and p["is_trans"] is True   # la casella trans non dipende dal genere
    p = (await client.patch("/me/profile", json={"is_trans": False})).json()
    assert p["is_trans"] is False and p["gender"] == "donna"


async def test_altro_senza_testo_e_un_genere_sconosciuto_si_respingono(client, session, catalogo):
    assert (await client.patch("/me/profile", json={"gender": "altro"})).status_code == 400
    assert (await client.patch("/me/profile", json={"gender": "altro", "gender_custom": "###"})).status_code == 400
    assert (await client.patch("/me/profile", json={"gender": "alieno"})).status_code == 422
    assert (await client.get("/me/profile")).json()["gender"] is None


# ---- l'apertura -------------------------------------------------------------------------------------


async def test_senza_partner_una_lettura_speciale_non_si_apre_e_non_si_paga(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    r = await client.post("/readings", json={"spread_id": "compat-tre", "question": QUESITO})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "partner_mancante"
    assert await _saldo(client) == 5 and (await client.get("/me/readings")).json()["totale"] == 0


async def test_un_partner_in_una_lettura_standard_si_respinge(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Andrà bene?", "partner": PARTNER})
    assert r.status_code == 422 and r.json()["detail"]["motivo"] == "partner_non_ammesso"
    assert await _saldo(client) == 5


@pytest.mark.parametrize("scheda, mancano", [
    ({}, ["genere", "nascita"]),
    ({"birth_date": "1990-03-14"}, ["genere"]),
    ({"gender": "donna"}, ["nascita"]),
])
async def test_con_la_scheda_incompleta_si_dice_cosa_manca_e_non_si_addebita(
    client, session, catalogo, scheda, mancano,
):
    await _accredita(session, client.identita.principal, 5)
    if scheda:
        await client.patch("/me/profile", json=scheda)
    r = await _apri(client)
    assert r.status_code == 422
    dettaglio = r.json()["detail"]
    assert dettaglio["motivo"] == "profilo_incompleto" and dettaglio["mancanti"] == mancano
    assert dettaglio["messaggio"]
    assert await _saldo(client) == 5 and (await client.get("/me/readings")).json()["totale"] == 0


async def test_il_messaggio_di_scheda_incompleta_e_nella_lingua_del_quesito(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    r = await _apri(client, question="El kell fogadnom az új állásajánlatot egy másik városban?")
    assert r.status_code == 422 and "profilodat" in r.json()["detail"]["messaggio"]


@pytest.mark.parametrize("difetto", [
    {"nome": ""},
    {"nome": "###"},
    {"genere": "alieno"},
    {"genere": "altro"},                   # senza testo
    {"nascita": "2999-01-01"},             # nel futuro
    {"nascita": "1800-01-01"},
    {"nascita": "non-una-data"},
])
async def test_un_partner_malformato_si_respinge_senza_addebito(client, session, catalogo, difetto):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    r = await client.post("/readings", json={
        "spread_id": "compat-tre", "question": QUESITO, "partner": {**PARTNER, **difetto},
    })
    assert r.status_code == 422
    assert await _saldo(client) == 5 and (await client.get("/me/readings")).json()["totale"] == 0


async def test_una_lettura_speciale_costa_un_credito_come_le_altre(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    r = await _apri(client)
    assert r.status_code == 201, r.text
    assert r.json()["consumo"] == "credito" and r.json()["saldo"] == 4
    assert r.json()["categoria"] == "compatibilita"
    assert r.json()["stesa"]["categoria"] == "compatibilita" and r.json()["stesa"]["stile"] == "tradizionale"
    assert await _saldo(client) == 4


async def test_senza_crediti_si_riceve_402_e_non_si_ricorda_il_partner(client, session, catalogo):
    await _scheda(client)
    r = await _apri(client, ricorda_partner=True)
    assert r.status_code == 402
    assert (await client.get("/me/profile")).json()["partner_ricordato"] is None
    assert (await client.get("/me/readings")).json()["totale"] == 0


async def test_l_abbonamento_copre_le_letture_speciali_come_le_altre(client, session, catalogo):
    from tarot_core.billing.plans import GestoreAbbonamenti

    utente = await _accredita(session, client.identita.principal, 5)
    gestore = GestoreAbbonamenti(session)
    await gestore.sottoscrivi(utente.id, await gestore.piano_per_slug("mensile-base"))
    await session.commit()
    await _scheda(client)
    r = await _apri(client, "coppia-croce")
    assert r.status_code == 201 and r.json()["consumo"] == "quota" and await _saldo(client) == 5


# ---- il partner ricordato ---------------------------------------------------------------------------------


async def test_ricorda_salva_il_partner_col_cognome_e_il_profilo_lo_restituisce(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    assert (await _apri(client, ricorda_partner=True)).status_code == 201
    ricordato = (await client.get("/me/profile")).json()["partner_ricordato"]
    assert ricordato["nome"] == "Marco" and ricordato["cognome"] == "Rossi"
    assert ricordato["genere"] == "uomo" and ricordato["nascita"] == "1988-08-07"


async def test_senza_ricorda_il_partner_non_si_salva_e_uno_ricordato_non_si_tocca(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await _apri(client, ricorda_partner=True)
    altro = {**PARTNER, "nome": "Luca", "cognome": "Bianchi"}
    r = await client.post("/readings", json={"spread_id": "compat-tre", "question": QUESITO, "partner": altro})
    assert r.status_code == 201
    assert (await client.get("/me/profile")).json()["partner_ricordato"]["nome"] == "Marco"


async def test_un_nuovo_ricorda_sostituisce_il_partner(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await _apri(client, ricorda_partner=True)
    await _apri(client, partner={**PARTNER, "nome": "Luca"}, ricorda_partner=True)
    assert (await client.get("/me/profile")).json()["partner_ricordato"]["nome"] == "Luca"


async def test_il_partner_ricordato_si_cancella_ed_e_idempotente(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await _apri(client, ricorda_partner=True)
    assert (await client.delete("/me/partner")).status_code == 204
    assert (await client.get("/me/profile")).json()["partner_ricordato"] is None
    assert (await client.delete("/me/partner")).status_code == 204
    # La lettura già aperta ha la sua copia: si cancella con la lettura, non col partner ricordato.
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    assert (await client.get(f"/me/readings/{rid}")).json()["persone"]["partner"]["nome"] == "Marco"


async def test_l_audit_della_cancellazione_non_ha_i_dati_del_partner(client, session, catalogo):
    from tarot_core.domain.models import AuditLog

    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await _apri(client, ricorda_partner=True)
    await client.delete("/me/partner")
    righe = (await session.execute(select(AuditLog).where(AuditLog.action == "partner.forget"))).scalars().all()
    assert len(righe) == 1
    assert "Marco" not in repr(righe[0].before) + repr(righe[0].after) + repr(righe[0].target_id)


async def test_un_utente_non_vede_il_partner_ricordato_di_un_altro(client, session, catalogo, principal_altro):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await _apri(client, ricorda_partner=True)
    client.identita.principal = principal_altro
    assert (await client.get("/me/profile")).json()["partner_ricordato"] is None


# ---- lo storico -------------------------------------------------------------------------------------------------


async def test_la_lettura_speciale_compare_nello_storico_come_le_altre(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await client.post("/readings", json={"spread_id": "tre-carte", "question": "Una lettura normale?"})
    r = await _apri(client, "coppia-specchio")
    rid = r.json()["id"]
    elenco = (await client.get("/me/readings")).json()
    assert elenco["totale"] == 2
    speciale = next(x for x in elenco["letture"] if x["id"] == rid)
    normale = next(x for x in elenco["letture"] if x["id"] != rid)
    assert speciale["categoria"] == "coppia" and speciale["stile"] == "moderna"
    assert speciale["partner_nome"] == "Marco" and speciale["stesa"] == "Specchio"
    assert speciale["stesa_nomi"]["hu"] == "Tükör"
    assert normale["categoria"] == "standard" and normale["partner_nome"] is None
    assert "cognome" not in repr(elenco)   # nell'elenco basta il nome


async def test_il_dettaglio_ha_le_persone_e_la_compatibilita_calcolata(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    rid = (await _apri(client)).json()["id"]
    d = (await client.get(f"/me/readings/{rid}")).json()
    assert d["persone"]["partner"]["cognome"] == "Rossi" and d["persone"]["tu"]["genere"] == "donna"
    c = d["compatibilita"]
    assert c["segni"]["tu"]["codice"] == "pesci" and c["segni"]["partner"]["codice"] == "leone"
    assert c["aspetto"] == "quinconce" and c["armonia"] == "impegnativa" and c["distanza"] == 5
    assert c["carta_coppia"]["id"].startswith("maj-") and "Rossi" not in repr(c)
    assert d["categoria"] == "compatibilita"


async def test_la_lettura_standard_non_ha_persone_ne_compatibilita(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Andrà bene?"})).json()["id"]
    d = (await client.get(f"/me/readings/{rid}")).json()
    assert d["persone"] is None and d["compatibilita"] is None and d["categoria"] == "standard"


async def test_la_lettura_conserva_la_copia_delle_persone_anche_se_la_scheda_cambia(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    rid = (await _apri(client)).json()["id"]
    await _scheda(client, gender="uomo", birth_date="1970-01-01")
    d = (await client.get(f"/me/readings/{rid}")).json()
    assert d["persone"]["tu"]["genere"] == "donna" and d["persone"]["tu"]["nascita"] == "1990-03-14"
    assert d["compatibilita"]["segni"]["tu"]["codice"] == "pesci"


async def test_cancellare_la_lettura_porta_via_le_persone(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    rid = (await _apri(client)).json()["id"]
    assert (await client.delete(f"/me/readings/{rid}")).status_code == 204
    assert (await session.execute(select(Reading).where(Reading.persone.is_not(None)))).first() is None


async def test_un_altro_utente_non_vede_le_persone_di_una_lettura(client, session, catalogo, principal_altro):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    rid = (await _apri(client)).json()["id"]
    client.identita.principal = principal_altro
    assert (await client.get(f"/me/readings/{rid}")).status_code == 404


# ---- la condivisione: il nome dell'altra persona non esce -----------------------------------------------------


async def test_una_lettura_speciale_si_condivide_senza_il_nome_dell_altra_persona(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await _lettura_completa(client, "coppia-croce", 5, QUESITO, {"partner": PARTNER})
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    r = await client.post(f"/me/readings/{rid}/share", json={"attiva": True, "testo": "Che bella coppia, Marco!"})
    assert r.status_code == 200
    pubblico = (await client.get(f"/shared/{r.json()['share_token']}")).json()
    assert pubblico["speciale"] is True and pubblico["partner_simbolo"] == "marte"
    assert pubblico["partner_frase"] == "qualcuno di speciale"
    assert pubblico["question"] == "Compatibilità con qualcuno di speciale"
    assert pubblico["share_text"] == "Che bella coppia, qualcuno di speciale!"
    # Né nome, né cognome, né date, né intervista, né compatibilità zodiacale.
    testo = repr(pubblico)
    assert "Marco" not in testo and "Rossi" not in testo and "1988" not in testo
    assert "persone" not in pubblico and "compatibilita" not in pubblico and "interview" not in pubblico


async def test_il_simbolo_dell_altra_persona_segue_il_suo_genere(client, session, catalogo):
    await _accredita(session, client.identita.principal, 10)
    await _scheda(client)
    attesi = {"donna": "venere", "uomo": "marte", "non_binario": "mercurio", "altro": "stella", "non_dice": "stella"}
    viste: set = set()
    for genere, simbolo in attesi.items():
        partner = {**PARTNER, "genere": genere, "genere_altro": "fluido" if genere == "altro" else None}
        await _lettura_completa(client, "compat-tre", 3, QUESITO, {"partner": partner})
        # Nei test le letture nascono nella stessa transazione, con lo stesso `now()`:
        # l'ordine dell'elenco non dice quale sia l'ultima. Si guarda cosa è comparso.
        (rid,) = {x["id"] for x in (await client.get("/me/readings")).json()["letture"]} - viste
        viste.add(rid)
        token = (await client.post(f"/me/readings/{rid}/share", json={"attiva": True})).json()["share_token"]
        assert (await client.get(f"/shared/{token}")).json()["partner_simbolo"] == simbolo


async def test_una_lettura_standard_condivisa_non_e_speciale(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _lettura_completa(client, "tre-carte", 3)
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    token = (await client.post(f"/me/readings/{rid}/share", json={"attiva": True})).json()["share_token"]
    pubblico = (await client.get(f"/shared/{token}")).json()
    assert pubblico["speciale"] is False and pubblico["partner_simbolo"] is None
    assert pubblico["partner_frase"] is None and pubblico["categoria"] == "standard"


async def test_il_ritiro_di_una_condivisione_speciale_funziona(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    await _lettura_completa(client, "coppia-croce", 5, QUESITO, {"partner": PARTNER})
    lettura = (await session.execute(select(Reading))).scalars().first()
    token = (await client.post(f"/me/readings/{lettura.id}/share", json={"attiva": True})).json()["share_token"]
    r = await client.post(f"/me/readings/{lettura.id}/share", json={"attiva": False})
    assert r.status_code == 200 and r.json()["share_token"] is None
    assert (await client.get(f"/shared/{token}")).status_code == 404


# ---- il catalogo pubblico ------------------------------------------------------------------------------------------


async def test_le_stese_si_filtrano_per_categoria(client, catalogo):
    tutte = (await client.get("/spreads")).json()
    assert len(tutte) == 14
    standard = (await client.get("/spreads", params={"categoria": "standard"})).json()
    assert [s["id"] for s in standard] == ["tre-carte", "croce-semplice", "ferro-di-cavallo", "croce-celtica", "ruota-astrologica"]
    compat = (await client.get("/spreads", params={"categoria": "compatibilita"})).json()
    assert len(compat) == 4 and all(s["categoria"] == "compatibilita" for s in compat)
    coppia = (await client.get("/spreads", params={"categoria": "coppia"})).json()
    assert len(coppia) == 5
    assert (await client.get("/spreads", params={"categoria": "amicizia"})).status_code == 422


async def test_una_stesa_si_legge_senza_account_con_i_suoi_significati(client, catalogo):
    r = await client.get("/spreads/coppia-specchio")
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == "coppia-specchio" and d["categoria"] == "coppia" and d["stile"] == "moderna"
    assert len(d["posizioni"]) == 8 and all(p["significato"] and p["domanda"] for p in d["posizioni"])
    assert d["descrizione"] and d["regole"] and d["nomi"]["hu"] == "Tükör"
    assert (await client.get("/spreads/croce-celtica")).status_code == 200
    assert (await client.get("/spreads/non-esiste")).status_code == 404


# ---- il flusso completo, per ciascuna delle nove stese --------------------------------------------------------------


@pytest.mark.parametrize("spread_id", list(ATTESE))
async def test_una_lettura_completa_per_ogni_stesa_speciale(client, session, catalogo, spread_id):
    await _accredita(session, client.identita.principal, 50)
    await _scheda(client)
    carte = ATTESE[spread_id][2]
    fine = await _lettura_completa(client, spread_id, carte, QUESITO, {"partner": PARTNER, "ricorda_partner": True})
    assert fine["saldo"] == 49
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    d = (await client.get(f"/me/readings/{rid}")).json()
    assert d["status"] == "completata" and len(d["cards"]) == carte and d["synthesis"]
    assert d["categoria"] == ATTESE[spread_id][0]
    utente = (await session.execute(select(User))).scalars().first()
    assert utente.partner_ricordato["nome"] == "Marco"


async def test_le_letture_speciali_sono_registrate_come_le_altre_nel_conto(client, session, catalogo):
    utente = await UserRepository(session).ensure(client.identita.principal)
    await _accredita(session, client.identita.principal, 3)
    await _scheda(client)
    await _apri(client, "compat-tre")
    await _apri(client, "coppia-croce")
    movimenti = (await client.get("/me/credits")).json()["movimenti"]
    assert [m["reason"] for m in movimenti].count("consumo") == 2
    assert await RegistroCrediti(session).saldo(utente.id) == 1
