"""Il flusso di una lettura attraverso l'API, col modello finto e un database vero."""
from __future__ import annotations

import pytest

from tarot_core.auth.keycloak import Principal
from tarot_core.billing.credits import RegistroCrediti
from tarot_core.domain.repositories import UserRepository
from tarot_core.tarot.shuffle import verifica

from .conftest import eventi_sse, richiede_database

pytestmark = richiede_database

STESE = {
    "tre-carte": 3,
    "croce-semplice": 4,
    "ferro-di-cavallo": 7,
    "croce-celtica": 10,
    "ruota-astrologica": 13,
}


async def _accredita(session, principal, quanti=1000):
    utente = await UserRepository(session).ensure(principal)
    await RegistroCrediti(session).rettifica(utente.id, quanti, note="crediti di prova")
    await session.commit()
    return utente


QUESITO = "Cosa mi riserva il lavoro nei prossimi mesi?"


async def _lettura_completa(client, spread_id: str, da_scegliere: int, quesito: str = QUESITO) -> dict:
    r = await client.post("/readings", json={"spread_id": spread_id, "question": quesito})
    assert r.status_code == 201, r.text
    lettura = r.json()
    assert lettura["disclaimer"]
    if lettura["lang"] == "it":
        assert "scientifica" in lettura["disclaimer"]
    rid = lettura["id"]

    # Intervista: il modello finto chiude dopo due domande.
    r = await client.post(f"/readings/{rid}/interview", json={})
    domande = 0
    while not r.json().get("completa"):
        domande += 1
        assert r.json()["domanda"]
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Da qualche mese, con alti e bassi."})
    assert domande == 2 and r.json()["riassunto"]

    r = await client.post(f"/readings/{rid}/fan")
    ventaglio = r.json()
    assert ventaglio["slot_count"] == (22 if spread_id in ("tre-carte", "croce-semplice") else 78)
    assert ventaglio["da_scegliere"] == da_scegliere

    # Prima della rivelazione nessuna carta è visibile.
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert "deck_state" not in dettaglio or dettaglio["deck_state"] is None

    for i in range(da_scegliere):
        r = await client.post(f"/readings/{rid}/pick", json={"slot": i * 2})
        assert r.status_code == 200, r.text
        assert "carta" not in r.json()
    assert r.json()["tutte_scelte"]

    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert all("carta" not in c for c in dettaglio["cards"])
    posizioni = [c["posizione"] for c in dettaglio["cards"]]

    for pos in sorted(posizioni):
        r = await client.post(f"/readings/{rid}/reveal/{pos}")
        eventi = eventi_sse(r.text)
        nomi = [e for e, _ in eventi]
        assert nomi[0] == "carta" and nomi[-1] == "fine"
        assert eventi[-1][1]["interpretazione"]

    r = await client.post(f"/readings/{rid}/synthesis")
    eventi = eventi_sse(r.text)
    testo = "".join(d["testo"] for e, d in eventi if e == "token")
    assert "## Il quadro" in testo
    fine = eventi[-1][1]
    assert eventi[-1][0] == "fine" and fine["guardia"] == "ok"
    # A lettura conclusa il mazzo si può verificare contro il commitment.
    assert verifica(fine["deck_state"], fine["deck_salt"], fine["commitment"])
    return fine


@pytest.mark.parametrize("spread_id", list(STESE))
async def test_una_lettura_completa_per_ogni_stesa(client, session, catalogo, spread_id):
    await _accredita(session, client.identita.principal)
    fine = await _lettura_completa(client, spread_id, STESE[spread_id])
    assert fine["saldo"] == 999


async def test_cinque_letture_consumano_cinque_crediti(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    for spread_id, n in STESE.items():
        fine = await _lettura_completa(client, spread_id, n)
    assert fine["saldo"] == 995


async def test_senza_crediti_si_riceve_402(client, catalogo):
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Andrà bene?"})
    assert r.status_code == 402
    assert r.json()["detail"]["motivo"] == "crediti"
    assert (await client.get("/me/readings")).json()["totale"] == 0


async def test_senza_un_modello_configurato_non_si_apre_ne_si_paga(client, session, catalogo, monkeypatch):
    """Nessuna lettura di ripiego: senza modello vero risponde 503 e non addebita."""
    from tarot_core.settings import get_settings

    await _accredita(session, client.identita.principal)
    monkeypatch.setenv("TAROT_LLM_FINTO", "false")
    for nome in ("TAROT_LLM_PROVIDER", "TAROT_LLM_BASE_URL", "TAROT_ANTHROPIC_API_KEY", "TAROT_MODELLI"):
        monkeypatch.delenv(nome, raising=False)
    get_settings.cache_clear()

    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Andrà bene?"})
    assert r.status_code == 503
    assert r.json()["detail"]["motivo"] == "modello_non_configurato"
    assert (await client.get("/me/readings")).json()["totale"] == 0
    assert (await RegistroCrediti(session).saldo((await UserRepository(session).ensure(client.identita.principal)).id)) == 1000


def test_llm_configurato(monkeypatch):
    """Il valore predefinito (LM Studio su localhost) non conta come configurato."""
    from tarot_core.settings import Settings

    for nome in ("TAROT_LLM_FINTO", "TAROT_LLM_PROVIDER", "TAROT_LLM_BASE_URL", "TAROT_ANTHROPIC_API_KEY", "TAROT_MODELLI"):
        monkeypatch.delenv(nome, raising=False)
    assert not Settings(_env_file=None).llm_configurato()
    assert Settings(_env_file=None, llm_finto=True).llm_configurato()
    assert Settings(_env_file=None, llm_base_url="http://llm.interno:8000/v1").llm_configurato()
    assert not Settings(_env_file=None, llm_provider="anthropic").llm_configurato()
    assert Settings(_env_file=None, llm_provider="anthropic", anthropic_api_key="sk-x").llm_configurato()


async def test_la_croce_semplice_calcola_la_sintesi_di_wirth(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    await _lettura_completa(client, "croce-semplice", 4)
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    carte = (await client.get(f"/me/readings/{rid}")).json()["cards"]
    assert len(carte) == 5
    scelte = [c for c in carte if not c["calcolata"]]
    sintesi = next(c for c in carte if c["calcolata"])
    somma = sum(c["carta"]["numero"] for c in scelte)
    while somma > 22:
        somma = sum(int(x) for x in str(somma))
    assert sintesi["carta"]["numero"] == (0 if somma in (0, 22) else somma)
    assert sintesi["posizione"] == 5 and sintesi["rovescio"] is False


async def test_le_carte_si_rivelano_in_ordine(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Una domanda?"})).json()["id"]
    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Risposta"})
    await client.post(f"/readings/{rid}/fan")
    # Lo stesso slot non si sceglie due volte.
    assert (await client.post(f"/readings/{rid}/pick", json={"slot": 3})).status_code == 200
    assert (await client.post(f"/readings/{rid}/pick", json={"slot": 3})).status_code == 409
    for s in (4, 5):
        await client.post(f"/readings/{rid}/pick", json={"slot": s})
    assert (await client.post(f"/readings/{rid}/reveal/2")).status_code == 409
    assert (await client.post(f"/readings/{rid}/synthesis")).status_code == 409


async def test_una_crisi_ferma_la_lettura_e_restituisce_il_credito(client, session, catalogo):
    await _accredita(session, client.identita.principal, 1)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Cosa succederà?"})).json()["id"]
    await client.post(f"/readings/{rid}/interview", json={})
    r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Non voglio più vivere"})
    assert r.json()["crisi"] and "112" in r.json()["messaggio"]
    assert (await client.get("/me/billing")).json()["saldo"] == 1
    assert (await client.get(f"/me/readings/{rid}")).json()["status"] == "annullata"


async def test_una_domanda_di_crisi_non_apre_la_lettura(client, session, catalogo):
    await _accredita(session, client.identita.principal, 1)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Voglio farla finita"})
    assert r.json()["crisi"]
    assert (await client.get("/me/billing")).json()["saldo"] == 1


async def test_le_letture_di_un_altro_non_si_vedono_ne_si_cancellano(client, session, catalogo, principal_altro):
    await _accredita(session, client.identita.principal)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "La mia domanda?"})).json()["id"]
    client.identita.principal = principal_altro
    assert (await client.get(f"/me/readings/{rid}")).status_code == 404
    assert (await client.delete(f"/me/readings/{rid}")).status_code == 404
    assert (await client.post(f"/readings/{rid}/interview", json={})).status_code == 404


async def test_la_cancellazione_e_vera(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    rid = (await client.post("/readings", json={"spread_id": "tre-carte", "question": "Da cancellare?"})).json()["id"]
    assert (await client.delete(f"/me/readings/{rid}")).status_code == 204
    assert (await client.get(f"/me/readings/{rid}")).status_code == 404
    # Il movimento di credito resta, senza riferimento alla lettura.
    movimenti = (await client.get("/me/credits")).json()["movimenti"]
    assert any(m["reason"] == "consumo" and m["reading_id"] is None for m in movimenti)


async def test_l_abbonamento_usa_la_quota_prima_dei_crediti(client, session, catalogo):
    from tarot_core.billing.plans import GestoreAbbonamenti

    utente = await _accredita(session, client.identita.principal, 5)
    gestore = GestoreAbbonamenti(session)
    await gestore.sottoscrivi(utente.id, await gestore.piano_per_slug("mensile-base"))
    await session.commit()
    consumi = []
    for _ in range(4):
        r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Oggi?"})
        consumi.append(r.json()["consumo"])
    assert consumi == ["quota", "quota", "quota", "credito"]
    assert (await client.get("/me/billing")).json()["saldo"] == 4


async def test_un_pacchetto_pagato_accredita_i_crediti(client, catalogo):
    r = await client.post("/me/checkout", json={"piano": "pacchetto-15", "ritorno": "/leggi"})
    assert r.status_code == 201, r.text
    checkout = r.json()["checkout_id"]
    r = await client.post(f"/billing/mock/checkout/{checkout}/esito", data={"esito": "paga", "ritorno": "http://localhost:3000/leggi"})
    assert r.status_code == 303
    assert (await client.get(f"/me/checkout/{checkout}")).json()["stato"] == "pagato"
    assert (await client.get("/me/billing")).json()["saldo"] == 15


async def test_il_ritorno_del_checkout_non_esce_dal_sito(client, catalogo):
    r = await client.post("/me/checkout", json={"piano": "pacchetto-5", "ritorno": "//evil.example"})
    assert r.status_code == 400


async def test_condivisione_e_diario(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    await _lettura_completa(client, "tre-carte", 3)
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    r = await client.post(f"/me/readings/{rid}/share", json={"attiva": True})
    assert r.status_code == 200, r.text
    token = r.json()["share_token"]
    pubblica = (await client.get(f"/shared/{token}")).json()
    assert pubblica["synthesis"] and "interview" not in pubblica
    # Chi apre il link legge nella lingua del quesito: la lettura la porta con sé.
    assert pubblica["lang"] == "it"
    await client.post(f"/me/readings/{rid}/share", json={"attiva": False})
    assert (await client.get(f"/shared/{token}")).status_code == 404
    assert (await client.post(f"/me/readings/{rid}/feedback", json={"esito": "in_parte"})).status_code == 200


async def test_inviti_e_carta_del_giorno(client, session, catalogo, principal_altro):
    codice = (await client.get("/me/profile")).json()["referral_code"]
    client.identita.principal = principal_altro
    r = await client.post("/me/referral", json={"codice": codice})
    assert r.status_code == 200 and r.json()["saldo"] == 3
    assert (await client.post("/me/referral", json={"codice": codice})).status_code == 409
    prima = (await client.get("/me/daily-card")).json()
    seconda = (await client.get("/me/daily-card")).json()
    assert prima["carta"]["id"] == seconda["carta"]["id"] and prima["serie"] == 1


async def test_la_console_richiede_il_ruolo_admin(client, catalogo, principal_admin):
    assert (await client.get("/admin/stats")).status_code == 403
    client.identita.principal = principal_admin
    stats = (await client.get("/admin/stats?giorni=7")).json()
    assert "attuale" in stats and "per_stesa" in stats
    assert (await client.get("/admin/users")).status_code == 200
    r = await client.get("/admin/reports/letture.csv")
    assert r.status_code == 200 and r.text.lstrip("﻿").startswith("id,")


def test_principal_admin_ha_il_ruolo(principal_admin: Principal):
    assert principal_admin.is_admin


# ---- la lingua del quesito e i valori passati al modello -----------------------------


@pytest.fixture
def prompt_visti(monkeypatch):
    """Registra ogni chiamata al modello finto: compito, sistema e messaggio utente."""
    from tarot_core.tarot.finto import ModelloFinto, _compito, _utente

    visti: list[dict] = []
    originale = ModelloFinto._rispondi

    def spia(self, req):
        visti.append({
            "compito": _compito(req),
            "sistema": "\n".join(m.content for m in req.messages if m.role == "system"),
            "utente": _utente(req),
        })
        return originale(self, req)

    monkeypatch.setattr(ModelloFinto, "_rispondi", spia)
    return visti


async def test_la_lingua_e_quella_del_quesito_e_si_rinnova_a_ogni_quesito(
    client, session, catalogo, prompt_visti,
):
    from tarot_core.tarot.lingue import in_lingua
    from tarot_core.tarot.testi import DISCLAIMER

    from .test_lingue import QUESITI

    await _accredita(session, client.identita.principal)

    # L'interfaccia è in italiano (`lang` del payload), il quesito in ungherese: vale il quesito.
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITI["hu"], "lang": "it"})
    assert r.status_code == 201, r.text
    assert r.json()["lang"] == "hu"
    assert r.json()["disclaimer"] == in_lingua(DISCLAIMER, "hu")
    rid = r.json()["id"]
    assert (await client.get(f"/me/readings/{rid}")).json()["lang"] == "hu"
    await client.delete(f"/me/readings/{rid}")
    prompt_visti.clear()

    await _lettura_completa(client, "tre-carte", 3, QUESITI["hu"])
    assert {v["compito"] for v in prompt_visti} >= {"intervista", "interpretazione", "sintesi"}
    for v in prompt_visti:
        if v["compito"] in ("intervista", "interpretazione", "sintesi"):
            assert "ungherese" in v["utente"], v["compito"]
            assert "Scrivi in italiano" not in v["utente"], v["compito"]
    # Nell'interpretazione i nomi tradotti da usare accompagnano quelli italiani.
    assert all("Nomi da usare nella risposta" in v["utente"] for v in prompt_visti if v["compito"] == "interpretazione")

    # Un nuovo quesito, in inglese, rinnova la lingua: la lettura di prima non la trascina.
    prompt_visti.clear()
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITI["en"], "lang": "hu"})
    assert r.json()["lang"] == "en"
    await _lettura_completa(client, "tre-carte", 3, QUESITI["en"])
    for v in prompt_visti:
        if v["compito"] in ("intervista", "interpretazione", "sintesi"):
            assert "inglese" in v["utente"] and "ungherese" not in v["utente"], v["compito"]
            assert "Nomi da usare nella risposta" not in v["utente"] or v["compito"] == "interpretazione"


async def test_senza_indizi_nel_quesito_vale_la_lingua_dell_interfaccia(client, session, catalogo):
    await _accredita(session, client.identita.principal)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "???", "lang": "hu"})
    assert r.json()["lang"] == "hu"


async def test_la_crisi_risponde_nella_lingua_del_quesito(client, session, catalogo):
    await _accredita(session, client.identita.principal, 1)
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": "Meg akarok halni", "lang": "it"})
    assert r.json()["crisi"] and "116-123" in r.json()["messaggio"]
    assert (await client.get("/me/billing")).json()["saldo"] == 1


async def test_l_interpretazione_riceve_solo_la_sua_posizione(client, session, catalogo, prompt_visti):
    from tarot_core.tarot.conoscenza import Conoscenza

    stesa = Conoscenza.carica().stesa("tre-carte")
    await _accredita(session, client.identita.principal)
    await _lettura_completa(client, "tre-carte", 3)
    letture = [v for v in prompt_visti if v["compito"] == "interpretazione"]
    assert len(letture) == 3
    for n, v in enumerate(letture, start=1):
        assert stesa["posizioni"][n - 1]["significato"] in v["utente"]
        for altra in stesa["posizioni"]:
            if altra["n"] != n:
                assert altra["significato"] not in v["utente"], (n, altra["nome"])
        # Le sole carte già girate prima di questa, mai le successive.
        assert v["utente"].count("Orientamento:") == 1


async def test_la_sintesi_riceve_le_carte_nell_ordine_del_racconto(client, session, catalogo, prompt_visti):
    import re

    from tarot_core.tarot.conoscenza import Conoscenza

    conoscenza = Conoscenza.carica()
    await _accredita(session, client.identita.principal)
    await _lettura_completa(client, "croce-semplice", 4)
    sintesi = next(v for v in prompt_visti if v["compito"] == "sintesi")
    sezione = sintesi["utente"].split("## Ordine del racconto", 1)[1].split("\n## ", 1)[0]
    posizioni = [int(n) for n in re.findall(r"\(posizione (\d+)\)", sezione)]
    assert posizioni == conoscenza.stesa("croce-semplice")["racconto"]
    # Il prefisso stabile non porta le altre stese.
    for altra in ("tre-carte", "croce-celtica", "ferro-di-cavallo", "ruota-astrologica"):
        assert conoscenza.stesa(altra)["descrizione"] not in sintesi["sistema"]
        assert conoscenza.stesa(altra)["descrizione"] not in sintesi["utente"]
