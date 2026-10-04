"""Un account per persona: il flusso di Keycloak che unisce gli account al primo accesso social, la sua assegnazione
ai provider dalla console, e l'elenco degli account doppi già esistenti. Keycloak è il finto di
`test_admin_accesso_social.py` (HTTP in memoria), che costruisce i flussi come quello vero.
"""
from __future__ import annotations

import json

from sqlalchemy import select

from tarot_core.auth.keycloak_admin import PASSO_UNIONE_SICURA
from tarot_core.auth.provider_sociali import (
    FLUSSO_STANDARD, FLUSSO_UNIONE, MASCHERA, PER_ALIAS, con_unione, dati_estesi_attivi, rappresentazione,
)
from tarot_core.domain.models import AuditLog, Reading, User

from .conftest import richiede_database
from .test_admin_accesso_social import admin, keycloak  # noqa: F401 - fixture riusate

# ---- la rappresentazione dei provider (niente database) ----------------------------------------------------


def test_unione_solo_per_i_provider_con_email_garantita():
    google = rappresentazione(PER_ALIAS["google"], None, abilitato=True, client_id="g", client_secret="s",
                              flusso_dopo=None, flusso_unione=FLUSSO_UNIONE)
    assert google["firstBrokerLoginFlowAlias"] == FLUSSO_UNIONE and google["trustEmail"] is True
    # Il backend legge il profilo con il token che Keycloak conserva.
    assert google["storeToken"] is True
    # X non garantisce l'email: resta (o torna) al flusso standard con conferma, anche se il flusso c'è.
    gia_unito = {"alias": "twitter", "providerId": "twitter", "firstBrokerLoginFlowAlias": FLUSSO_UNIONE,
                 "config": {"clientId": "x", "clientSecret": MASCHERA}}
    x = rappresentazione(PER_ALIAS["twitter"], gia_unito, abilitato=True, client_id="x", client_secret=None,
                         flusso_dopo=None, flusso_unione=FLUSSO_UNIONE)
    assert x["firstBrokerLoginFlowAlias"] == FLUSSO_STANDARD and "storeToken" not in x
    # Microsoft nemmeno: in Entra ID l'email è un campo che l'amministratore del tenant scrive a piacere.
    ms = rappresentazione(PER_ALIAS["microsoft"], None, abilitato=True, client_id="m", client_secret="s",
                          flusso_dopo=None, flusso_unione=FLUSSO_UNIONE)
    assert ms["firstBrokerLoginFlowAlias"] == FLUSSO_STANDARD and ms["trustEmail"] is False
    # Senza flusso (Keycloak non l'ha lasciato creare) un provider esistente tiene quello che ha.
    senza = rappresentazione(PER_ALIAS["google"], {**google, "firstBrokerLoginFlowAlias": FLUSSO_STANDARD},
                             abilitato=True, client_id="g", client_secret=None, flusso_dopo=None)
    assert senza["firstBrokerLoginFlowAlias"] == FLUSSO_STANDARD


def test_dati_estesi_aggiungono_gli_ambiti_e_si_leggono_da_keycloak():
    base = rappresentazione(PER_ALIAS["google"], None, abilitato=True, client_id="g", client_secret="s",
                            flusso_dopo=None)
    assert base["config"]["defaultScope"] == "openid profile email"
    estesi = rappresentazione(PER_ALIAS["google"], base, abilitato=True, client_id="g", client_secret=None,
                              flusso_dopo=None, dati_estesi=True)
    assert "https://www.googleapis.com/auth/user.birthday.read" in estesi["config"]["defaultScope"]
    assert "https://www.googleapis.com/auth/user.gender.read" in estesi["config"]["defaultScope"]
    assert dati_estesi_attivi(PER_ALIAS["google"], estesi) is True
    # `None` lascia com'è: un salvataggio che non tocca la casella non spegne gli ambiti.
    ancora = rappresentazione(PER_ALIAS["google"], estesi, abilitato=False, client_id="g", client_secret=None,
                              flusso_dopo=None)
    assert dati_estesi_attivi(PER_ALIAS["google"], ancora) is True
    spenti = rappresentazione(PER_ALIAS["google"], estesi, abilitato=True, client_id="g", client_secret=None,
                              flusso_dopo=None, dati_estesi=False)
    assert spenti["config"]["defaultScope"] == "openid profile email"
    fb = rappresentazione(PER_ALIAS["facebook"], None, abilitato=True, client_id="f", client_secret="s",
                          flusso_dopo=None, dati_estesi=True)
    assert fb["config"]["defaultScope"] == "email public_profile user_birthday user_gender user_location"


def test_con_unione_cambia_solo_cio_che_serve():
    esistente = {"alias": "google", "internalId": "g-1", "firstBrokerLoginFlowAlias": FLUSSO_STANDARD,
                 "storeToken": False, "config": {"clientId": "g", "clientSecret": MASCHERA, "guiOrder": "1"}}
    nuova = con_unione(PER_ALIAS["google"], esistente, FLUSSO_UNIONE)
    assert nuova["firstBrokerLoginFlowAlias"] == FLUSSO_UNIONE and nuova["storeToken"] is True
    assert nuova["internalId"] == "g-1" and nuova["config"]["clientSecret"] == MASCHERA
    assert esistente["firstBrokerLoginFlowAlias"] == FLUSSO_STANDARD  # l'originale non si tocca
    assert con_unione(PER_ALIAS["google"], nuova, FLUSSO_UNIONE) is None  # già a posto: niente da scrivere
    x = {"alias": "twitter", "firstBrokerLoginFlowAlias": FLUSSO_STANDARD, "config": {}}
    assert con_unione(PER_ALIAS["twitter"], x, FLUSSO_UNIONE) is None
    # Un X portato per errore sul flusso che unisce torna a quello standard.
    assert con_unione(PER_ALIAS["twitter"], {**x, "firstBrokerLoginFlowAlias": FLUSSO_UNIONE},
                      FLUSSO_UNIONE)["firstBrokerLoginFlowAlias"] == FLUSSO_STANDARD


# ---- il flusso, costruito sul Keycloak finto ----------------------------------------------------------------

#: La ricetta di Keycloak «Automatically link existing first login flow»: rivedere il profilo solo se manca qualcosa,
#: poi creare l'utente se l'email è nuova, altrimenti collegare l'identità social a quello che c'è, con il nostro
#: passo al posto di «idp-auto-link» (toglie i vecchi accessi a un account con l'email mai verificata).
STRUTTURA_ATTESA = [
    (0, "idp-review-profile", "REQUIRED"),
    (0, f"{FLUSSO_UNIONE} - crea o collega", "REQUIRED"),
    (1, "idp-create-user-if-unique", "ALTERNATIVE"),
    (1, PASSO_UNIONE_SICURA, "ALTERNATIVE"),
]


@richiede_database
async def test_accendere_google_crea_e_assegna_il_flusso_che_unisce(admin, keycloak):  # noqa: F811
    r = await admin.put("/admin/accesso-social/google", json={
        "abilitato": True, "client_id": "123.apps.googleusercontent.com", "client_secret": "segreto-google",
    })
    assert r.status_code == 200, r.text
    assert r.json()["unione_automatica"] is True and r.json()["avviso"] is None
    assert FLUSSO_UNIONE in keycloak.flussi
    assert keycloak.struttura(FLUSSO_UNIONE) == STRUTTURA_ATTESA
    # «Review profile» solo se manca qualcosa (l'email di chi arriva senza): non a ogni primo accesso.
    assert list(keycloak.configurazioni.values()) == [{
        "alias": "unione - rivedi il profilo se manca qualcosa",
        "config": {"update.profile.on.first.login": "missing"},
    }]
    salvato = keycloak.provider["google"]
    assert salvato["firstBrokerLoginFlowAlias"] == FLUSSO_UNIONE and salvato["storeToken"] is True

    # Un secondo provider riusa lo stesso flusso, senza ricostruirlo.
    scritture = len(keycloak.scritture)
    r = await admin.put("/admin/accesso-social/facebook", json={
        "abilitato": True, "client_id": "fb-app", "client_secret": "segreto-fb",
    })
    assert r.status_code == 200, r.text
    assert keycloak.flussi.count(FLUSSO_UNIONE) == 1
    assert [w for w in keycloak.scritture[scritture:] if "/authentication/" in w[1]] == []
    assert keycloak.provider["facebook"]["firstBrokerLoginFlowAlias"] == FLUSSO_UNIONE


@richiede_database
async def test_un_flusso_di_prima_passa_al_collegamento_sicuro(admin, keycloak):  # noqa: F811
    # Il flusso creato prima di questo passo, con il collegamento di Keycloak che non toglie niente a nessuno.
    sotto = f"{FLUSSO_UNIONE} - crea o collega"
    keycloak.flussi.append(FLUSSO_UNIONE)
    keycloak.passi[FLUSSO_UNIONE] = [
        {"id": "r", "providerId": "idp-review-profile", "displayName": "r", "requirement": "REQUIRED"},
        {"id": "s", "displayName": sotto, "authenticationFlow": True, "requirement": "REQUIRED"},
    ]
    keycloak.passi[sotto] = [
        {"id": "c", "providerId": "idp-create-user-if-unique", "displayName": "c", "requirement": "ALTERNATIVE"},
        {"id": "a", "providerId": "idp-auto-link", "displayName": "a", "requirement": "ALTERNATIVE"},
    ]
    r = await admin.put("/admin/accesso-social/google", json={
        "abilitato": True, "client_id": "id-vero", "client_secret": "s",
    })
    assert r.status_code == 200, r.text
    assert keycloak.struttura(FLUSSO_UNIONE) == STRUTTURA_ATTESA


@richiede_database
async def test_x_resta_sul_flusso_con_conferma(admin, keycloak):  # noqa: F811
    r = await admin.put("/admin/accesso-social/twitter", json={
        "abilitato": True, "client_id": "consumer-key", "client_secret": "consumer-secret",
    })
    assert r.status_code == 200, r.text
    assert keycloak.provider["twitter"]["firstBrokerLoginFlowAlias"] == FLUSSO_STANDARD
    assert FLUSSO_UNIONE not in keycloak.flussi  # per X non serve, e non lo si crea


@richiede_database
async def test_senza_manage_realm_il_provider_si_salva_e_lo_si_dice(admin, keycloak):  # noqa: F811
    keycloak.flussi_vietati = True
    r = await admin.put("/admin/accesso-social/google", json={
        "abilitato": True, "client_id": "id-vero", "client_secret": "s",
    })
    assert r.status_code == 200, r.text
    assert r.json()["unione_automatica"] is False
    assert "manage-realm" in r.json()["avviso"]
    assert keycloak.provider["google"]["enabled"] is True
    assert keycloak.provider["google"].get("firstBrokerLoginFlowAlias") != FLUSSO_UNIONE


@richiede_database
async def test_un_flusso_costruito_a_meta_si_cancella(admin, keycloak):  # noqa: F811
    keycloak.passo_che_fallisce = PASSO_UNIONE_SICURA
    r = await admin.put("/admin/accesso-social/google", json={
        "abilitato": True, "client_id": "id-vero", "client_secret": "s",
    })
    assert r.status_code == 200, r.text
    # Un flusso senza il collegamento automatico bloccherebbe ogni primo accesso: meglio nessun flusso.
    assert FLUSSO_UNIONE not in keycloak.flussi
    assert r.json()["avviso"] and r.json()["unione_automatica"] is False


@richiede_database
async def test_applicare_l_unione_a_tutti_i_provider_presenti(admin, keycloak, session):  # noqa: F811
    keycloak.provider["facebook"] = {
        "alias": "facebook", "providerId": "facebook", "enabled": True, "storeToken": False,
        "firstBrokerLoginFlowAlias": FLUSSO_STANDARD, "config": {"clientId": "fb", "clientSecret": "vero-fb"},
    }
    keycloak.provider["twitter"] = {
        "alias": "twitter", "providerId": "twitter", "enabled": True,
        "firstBrokerLoginFlowAlias": FLUSSO_STANDARD, "config": {"clientId": "x", "clientSecret": "vero-x"},
    }
    prima = (await admin.get("/admin/accesso-social")).json()
    assert prima["unione"] == {"flusso": FLUSSO_UNIONE, "flusso_presente": False, "completa": False}

    r = await admin.post("/admin/accesso-social/unione")
    assert r.status_code == 200, r.text
    assert sorted(r.json()["provider_aggiornati"]) == ["facebook", "google"]
    assert r.json()["unione"]["completa"] is True
    assert keycloak.provider["facebook"]["firstBrokerLoginFlowAlias"] == FLUSSO_UNIONE
    assert keycloak.provider["facebook"]["storeToken"] is True
    # Il segreto rimandato mascherato: Keycloak tiene il suo.
    assert keycloak.provider["facebook"]["config"]["clientSecret"] == "vero-fb"
    assert keycloak.provider["twitter"]["firstBrokerLoginFlowAlias"] == FLUSSO_STANDARD

    # Idempotente.
    r = await admin.post("/admin/accesso-social/unione")
    assert r.json()["provider_aggiornati"] == []
    voci = (await session.execute(select(AuditLog).where(AuditLog.action == "accesso_social.unione"))).scalars().all()
    assert len(voci) == 2 and "vero-fb" not in json.dumps([v.after for v in voci])


@richiede_database
async def test_unione_solo_per_l_amministratore(client, keycloak):  # noqa: F811
    assert (await client.post("/admin/accesso-social/unione")).status_code == 403
    assert (await client.get("/admin/accesso-social/doppioni")).status_code == 403


# ---- gli account doppi già esistenti ------------------------------------------------------------------------


@richiede_database
async def test_doppioni_per_email_senza_badare_alle_maiuscole(admin, keycloak, session):  # noqa: F811
    vecchio = User(keycloak_sub="sub-password", email="Maria@Example.com", display_name="Maria", locale="it")
    nuovo = User(keycloak_sub="sub-google", email="maria@example.com", display_name="Maria R.", locale="it")
    solo = User(keycloak_sub="sub-solo", email="solo@example.com", locale="it")
    session.add_all([vecchio, nuovo, solo])
    await session.flush()
    session.add(Reading(owner_id=vecchio.id, question="?", spread_id="tre_carte", status="completata", consumo="omaggio"))
    await session.commit()

    r = await admin.get("/admin/accesso-social/doppioni")
    assert r.status_code == 200, r.text
    gruppi = r.json()["gruppi"]
    assert [g["email"] for g in gruppi] == ["maria@example.com"]
    righe = {u["keycloak_sub"]: u for u in gruppi[0]["utenti"]}
    assert set(righe) == {"sub-password", "sub-google"}
    assert righe["sub-password"]["letture"] == 1 and righe["sub-google"]["letture"] == 0
    # Non si fonde niente da solo: i due account restano.
    assert len((await session.execute(select(User).where(User.keycloak_sub.in_(["sub-password", "sub-google"])))).all()) == 2
