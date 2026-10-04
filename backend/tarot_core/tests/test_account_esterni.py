"""La console «Account» (v9, Fase 3): il registro dei servizi esterni.

Ogni voce ha una categoria nota, una sezione che esiste davvero nella console (o nessuna, per ciò che vive fuori dalla
console), un primo link https (o nessuno, dove non c'è un fornitore), e una sonda che non solleva e non chiama
nessuno. La verifica riusa le prove delle sezioni; qui solo quelle che non escono dalla macchina."""
from __future__ import annotations

from pathlib import Path

import pytest

from ..servizi_esterni.registro import CATEGORIE, PER_ID, REGISTRO, STATI
from .conftest import richiede_database

APP_ADMIN = Path(__file__).resolve().parents[3] / "admin" / "app"

#: Le voci che non si impostano dalla console (ambiente, file nell'immagine, servizi fuori dal sito). Firebase, APNs e
#: VAPID dalla Fase 5 puntano a Notifications → Impostazioni.
FUORI_CONSOLE = {
    "newsletter", "dbip", "otlp", "redis", "dns", "npm", "litmedia",
    "database", "chiave_master", "segreti_interni",
}
#: Le voci senza un fornitore da cui iscriversi.
SENZA_FORNITORE = {"chiavi_rest", "newsletter", "segreti_interni"}
#: v9 Fase 2c: sul server restano solo questi (password del database, chiave master, segreto client di Keycloak).
SUL_SERVER = {"database", "chiave_master", "keycloak"}


def test_voci_complete_e_coerenti():
    assert len(PER_ID) == len(REGISTRO), "id duplicati"
    for s in REGISTRO:
        assert s.categoria in CATEGORIE, s.id
        assert s.nome and s.come_fare and s.dove_sta_il_segreto and s.costi, s.id
        if s.primo_link is None:
            assert s.id in SENZA_FORNITORE, s.id
        else:
            assert s.primo_link.startswith("https://"), s.id
        if s.sezione is None:
            assert s.id in FUORI_CONSOLE, s.id
        else:
            assert s.sezione.startswith("/"), s.id
    # I servizi chiesti dall'operatore ci sono tutti.
    attesi = {
        "llm", "google_service_account", "search_console", "ga4", "keycloak", "social_google", "social_apple",
        "social_facebook", "social_microsoft", "social_github", "social_linkedin", "social_twitter", "reddit",
        "adsense", "smtp", "nas_backup", "indexnow", "websub", "litmedia", "chiavi_rest", "colab", "dbip", "stripe",
        "otlp", "dns", "npm", "redis", "google_play", "google_pagamenti", "apple_developer", "app_store_connect",
        "apple_pagamenti", "codemagic", "firebase", "apns", "vapid", "newsletter",
    }
    assert attesi <= set(PER_ID), attesi - set(PER_ID)


def test_ogni_voce_dice_dove_si_imposta_e_sul_server_restano_solo_tre_segreti():
    from ..servizi_esterni.registro import DOVE

    for s in REGISTRO:
        assert s.dove_si_imposta in DOVE, s.id
        if s.dove_si_imposta == "console":
            assert s.sezione, s.id
    assert {s.id for s in REGISTRO if s.dove_si_imposta == "server"} == SUL_SERVER
    # Stripe, posta e NAS si impostano dalla console; il DNS è Namecheap, con il primo link alla lista dei domini.
    assert PER_ID["stripe"].sezione == "/pagamenti/stripe" and PER_ID["stripe"].dove_si_imposta == "console"
    assert PER_ID["smtp"].sezione == "/impostazioni/posta" and PER_ID["smtp"].verifica is not None
    assert "solo spedisce" in " ".join(PER_ID["smtp"].come_fare)
    assert PER_ID["nas_backup"].dove_si_imposta == "console"
    assert "Namecheap" in PER_ID["dns"].nome
    assert PER_ID["dns"].primo_link == "https://ap.www.namecheap.com/domains/list/"
    passi = " ".join(PER_ID["dns"].come_fare)
    assert "eforward" in passi and "a.taini@gmail.com" in passi and "Redirect Email" in passi


@pytest.mark.skipif(not APP_ADMIN.is_dir(), reason="la console (admin/) non è in questa copia")
def test_ogni_sezione_e_una_pagina_della_console():
    for s in REGISTRO:
        if s.sezione is None:
            continue
        pagina = APP_ADMIN / s.sezione.strip("/") / "page.tsx"
        assert pagina.is_file(), f"{s.id}: {s.sezione} non è una pagina della console ({pagina})"


@richiede_database
async def test_le_sonde_non_sollevano(session):
    for s in REGISTRO:
        esito = await s.sonda(session)
        assert esito["stato"] in STATI, (s.id, esito)
        assert isinstance(esito["dettaglio"], str)
    assert (await PER_ID["redis"].sonda(session))["stato"] == "non_usato"
    assert (await PER_ID["google_play"].sonda(session))["stato"] == "da_configurare"
    assert (await PER_ID["stripe"].sonda(session))["stato"] in ("da_configurare", "configurato")


@richiede_database
async def test_elenco_e_verifica(client, principal_admin):
    assert (await client.get("/admin/account-esterni")).status_code == 403
    client.identita.principal = principal_admin
    r = await client.get("/admin/account-esterni")
    assert r.status_code == 200, r.text
    d = r.json()
    assert len(d["servizi"]) == len(REGISTRO)
    assert sum(d["riepilogo"].values()) == len(REGISTRO)
    voce = next(v for v in d["servizi"] if v["id"] == "google_play")
    assert voce["sezione"] == "/app-mobili" and voce["primo_link"] == "https://play.google.com/console/signup"
    assert voce["verificabile"] is True

    assert (await client.post("/admin/account-esterni/inesistente/verifica")).status_code == 404
    assert (await client.post("/admin/account-esterni/redis/verifica")).status_code == 422
    # Senza credenziali la verifica dello store non chiama nessuno e lo dice.
    r = await client.post("/admin/account-esterni/google_play/verifica")
    assert r.status_code == 200, r.text
    assert r.json()["esito"]["stato"] == "errore" and "Manca il JSON" in r.json()["esito"]["dettaglio"]
    r = await client.post("/admin/account-esterni/llm/verifica")
    assert r.json()["esito"]["stato"] == "da_configurare"
