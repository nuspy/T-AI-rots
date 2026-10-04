"""GDPR, Fase 1: i consensi granulari, lo storico append-only, gli IP protetti."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from tarot_core.auth.keycloak import Principal
from tarot_core.domain.consent_models import ConsensoStorico, UserConsent
from tarot_core.domain.memory_models import UserMemory
from tarot_core.domain.models import AuditLog, User
from tarot_core.domain.repositories import AuditRepository
from tarot_core.tarot import ip_protetto

from .conftest import richiede_database

VERSIONE = "v3"


# ---- IP: troncati e con l'impronta, mai interi (senza database) -----------------------------------------------


@pytest.mark.parametrize("ip, atteso", [
    ("93.44.12.201", "93.44.12.0"),
    ("93.44.12.201:51234", "93.44.12.0"),
    ("::ffff:93.44.12.201", "93.44.12.0"),
    ("2001:db8:abcd:12:1:2:3:4", "2001:db8:abcd::"),
    ("[2001:db8:abcd:12::1]:443", "2001:db8:abcd::"),
    ("fe80::1%eth0", "fe80::"),
])
def test_l_ip_si_tronca_alla_rete(ip, atteso):
    assert ip_protetto.tronca(ip) == atteso


@pytest.mark.parametrize("valore", [None, "", "unknown", "999.1.1.1", "testo qualunque"])
def test_un_valore_che_non_e_un_indirizzo_non_si_conserva(valore):
    assert ip_protetto.proteggi(valore, "s") == (None, None)


def test_l_impronta_e_un_hmac_dell_indirizzo_intero_col_segreto():
    a = ip_protetto.impronta("93.44.12.201", "segreto-a")
    assert a is not None and len(a) == 64
    assert a == ip_protetto.impronta("::ffff:93.44.12.201", "segreto-a")      # stesso abbonato, stessa impronta
    assert a != ip_protetto.impronta("93.44.12.202", "segreto-a")             # lo stesso /24 non basta
    assert a != ip_protetto.impronta("93.44.12.201", "segreto-b")             # senza il segreto non si ricalcola
    assert "93.44.12.201" not in a


def test_in_produzione_il_segreto_di_sviluppo_si_rifiuta_ma_la_mancanza_no():
    """Senza ambiente il segreto si genera al primo avvio (v9, Fase 2c): manca, e l'API parte lo stesso."""
    from tarot_core.settings import Settings

    problemi = Settings(environment="prod", ip_hash_secret="segreto-ip-di-sviluppo").validate_production()
    assert any("TAROT_IP_HASH_SECRET" in p for p in problemi)
    assert not any("TAROT_IP_HASH_SECRET" in p for p in Settings(environment="prod").validate_production())
    assert not any("TAROT_IP_HASH_SECRET" in p for p in Settings(environment="prod", ip_hash_secret="altro").validate_production())


@richiede_database
async def test_il_registro_scrive_l_ip_troncato_e_l_impronta(session):
    voce = await AuditRepository(session).record(action="prova.ip", ip="203.0.113.77")
    await session.flush()
    assert voce.ip == "203.0.113.0"
    assert voce.ip_hash == ip_protetto.impronta("203.0.113.77")
    assert (await AuditRepository(session).record(action="prova.ip", ip="non-un-ip")).ip is None


# ---- i consensi ---------------------------------------------------------------------------------------------



@richiede_database
async def test_get_consenso_ha_tutte_le_categorie_e_cookie_solo_per_il_vecchio_sito(client):
    r = await client.get("/consenso")
    assert r.status_code == 200
    assert r.json() == {
        "statistiche": None, "google_analytics": None, "pubblicita": None, "testi_statistiche": None,
        "dati_particolari": None, "marketing": None, "cookie": None,
    }


@richiede_database
async def test_le_scelte_del_banner_insieme_e_lo_storico(client, session, utente):
    r = await client.post("/consensi", json={
        "scelte": [
            {"tipo": "statistiche", "valore": "accettato"},
            {"tipo": "google_analytics", "valore": "rifiutato"},
        ],
        "versione_informativa": VERSIONE,
    })
    assert r.status_code == 200, r.text
    assert r.json()["statistiche"] == "accettato" and r.json()["google_analytics"] == "rifiutato"
    assert r.json()["cookie"] == "accettato" and r.json()["marketing"] is None

    storico = (await session.execute(
        select(ConsensoStorico).where(ConsensoStorico.user_id == utente.id).order_by(ConsensoStorico.id)
    )).scalars().all()
    assert [(s.tipo, s.valore, s.origine, s.versione_informativa) for s in storico] == [
        ("statistiche", "accettato", "web", VERSIONE), ("google_analytics", "rifiutato", "web", VERSIONE),
    ]
    # L'IP del client di prova (127.0.0.1) arriva troncato, con l'impronta: mai intero.
    assert all(s.ip == "127.0.0.0" and len(s.ip_hash) == 64 for s in storico)
    correnti = (await session.execute(select(UserConsent).where(UserConsent.user_id == utente.id))).scalars().all()
    assert {c.ip for c in correnti} == {"127.0.0.0"}


@richiede_database
async def test_cambiare_idea_sovrascrive_lo_stato_ma_allunga_lo_storico(client, session, utente):
    for valore in ("accettato", "rifiutato", "accettato"):
        r = await client.post("/consenso", json={"tipo": "marketing", "valore": valore, "versione_informativa": VERSIONE})
        assert r.status_code == 200, r.text
    correnti = (await session.execute(
        select(UserConsent).where(UserConsent.user_id == utente.id, UserConsent.tipo == "marketing")
    )).scalars().all()
    assert len(correnti) == 1 and correnti[0].valore == "accettato"
    storico = (await session.execute(
        select(ConsensoStorico.valore).where(ConsensoStorico.user_id == utente.id, ConsensoStorico.tipo == "marketing")
        .order_by(ConsensoStorico.id)
    )).scalars().all()
    assert storico == ["accettato", "rifiutato", "accettato"]
    eventi = (await session.execute(
        select(AuditLog).where(AuditLog.action == "consenso.marketing", AuditLog.actor_id == utente.id)
    )).scalars().all()
    assert len(eventi) == 3 and all(e.ip == "127.0.0.0" for e in eventi)


@richiede_database
async def test_il_vecchio_cookie_vale_per_statistiche_e_google_analytics(client, session, utente):
    r = await client.post("/consenso", json={"tipo": "cookie", "valore": "accettato", "versione_informativa": "v2"})
    assert r.status_code == 200, r.text
    tipi = set((await session.execute(
        select(UserConsent.tipo).where(UserConsent.user_id == utente.id)
    )).scalars())
    assert tipi == {"statistiche", "google_analytics"}             # nessuna riga «cookie»: è solo un sinonimo
    assert (await client.get("/consenso-google")).json() == {"attivo": True, "da_rinnovare": False}


@richiede_database
async def test_condivisione_partner_non_si_sceglie_piu(client):
    r = await client.post("/consenso", json={
        "tipo": "condivisione_dati_partner", "valore": "accettato", "versione_informativa": VERSIONE,
    })
    assert r.status_code == 422


@richiede_database
async def test_senza_account_solo_le_categorie_del_banner(client):
    client.identita.principal = None
    ok = await client.post("/consensi", json={
        "scelte": [{"tipo": "statistiche", "valore": "rifiutato"}, {"tipo": "pubblicita", "valore": "rifiutato"}],
        "versione_informativa": VERSIONE,
    })
    assert ok.status_code == 200 and "tarots_anon" in ok.cookies
    for tipo in ("dati_particolari", "testi_statistiche", "marketing"):
        r = await client.post("/consenso", json={"tipo": tipo, "valore": "accettato", "versione_informativa": VERSIONE})
        assert r.status_code == 401, tipo


@richiede_database
async def test_le_scelte_fatte_da_anonimo_passano_all_account_nuovo(client, session):
    client.identita.principal = None
    await client.post("/consensi", json={
        "scelte": [{"tipo": "statistiche", "valore": "rifiutato"}, {"tipo": "google_analytics", "valore": "accettato"}],
        "versione_informativa": VERSIONE,
    })
    client.identita.principal = Principal(subject="sub-nuovo-gdpr", email="nuovo@example.com", display_name="Nuovo", roles={"user"})
    stato = (await client.get("/consenso")).json()
    assert stato["statistiche"] == "rifiutato" and stato["google_analytics"] == "accettato"


@richiede_database
async def test_revocare_i_dati_particolari_toglie_trans_e_i_ricordi_sulla_salute(client, session, utente):
    await client.post("/consenso", json={"tipo": "dati_particolari", "valore": "accettato", "versione_informativa": VERSIONE})
    r = await client.patch("/me/profile", json={"is_trans": True})
    assert r.status_code == 200 and r.json()["is_trans"] is True
    for campo in ("salute", "Salute ", "lavoro"):
        session.add(UserMemory(owner_id=utente.id, contenuto=f"un fatto su {campo}", tipo="stabile",
                               campo_attinenza=campo, embedding=[0.1], fonte="lettura"))
    await session.commit()

    await client.post("/consenso", json={"tipo": "dati_particolari", "valore": "rifiutato", "versione_informativa": VERSIONE})
    assert (await client.get("/me/profile")).json()["is_trans"] is False
    rimaste = (await session.execute(
        select(UserMemory.campo_attinenza).where(UserMemory.owner_id == utente.id)
    )).scalars().all()
    assert rimaste == ["lavoro"]


@richiede_database
async def test_trans_si_salva_solo_col_consenso(client, session):
    r = await client.patch("/me/profile", json={"is_trans": True})
    assert r.status_code == 409 and r.json()["detail"]["motivo"] == "consenso_dati_particolari"
    assert (await client.patch("/me/profile", json={"is_trans": False})).status_code == 200
    utente = (await session.execute(select(User).where(User.keycloak_sub == "sub-utente-1"))).scalar_one()
    assert utente.is_trans is False
