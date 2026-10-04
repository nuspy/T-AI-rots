"""Tutte le configurazioni dalla console (v9, Fase 2c): Stripe, posta, credenziale del NAS, segreti interni, dati del
titolare, sonda DNS, importazione dall'ambiente.

Nessun servizio vero: Stripe e il DNS sono `httpx.MockTransport`, la posta è una funzione che raccoglie i messaggi,
il NAS è il server SFTP finto delle prove del backup.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List
from urllib.parse import parse_qsl

import httpx
import pytest
from sqlalchemy import select

from tarot_core.billing import stripe as modulo_stripe
from tarot_core.configurazioni import correnti, dns, importa, segreti
from tarot_core.domain.configurazioni_models import ConfigSmtp, ConfigStripe, ImportazioneAmbiente, SegretoSistema
from tarot_core.domain.models import AuditLog
from tarot_core.settings import get_settings
from tarot_core.tarot import ip_protetto

from .conftest import richiede_database

pytestmark = richiede_database

CHIAVE = "sk_test_della_console_123456"
CHIAVE_AMBIENTE = "sk_test_dell_ambiente_654321"
WHSEC = "whsec_nuovo_dalla_creazione"
PASSWORD_SMTP = "password-smtp-segretissima"


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


@pytest.fixture
def ambiente(monkeypatch):
    """Imposta variabili d'ambiente e rilegge le impostazioni."""
    def imposta(**valori: str) -> None:
        for nome, valore in valori.items():
            monkeypatch.setenv(f"TAROT_{nome.upper()}", valore)
        get_settings.cache_clear()

    yield imposta
    get_settings.cache_clear()


async def _audit(session) -> str:
    righe = (await session.execute(select(AuditLog))).scalars().all()
    return json.dumps([{"a": r.action, "b": r.before, "d": r.after} for r in righe], ensure_ascii=False, default=str)


# ---- Stripe ------------------------------------------------------------------------------------------------------


class StripeFinto:
    def __init__(self, esistenti: List[Dict[str, Any]] | None = None) -> None:
        self.richieste: List[Dict[str, Any]] = []
        self.endpoint = list(esistenti or [])

    def gestore(self, request: httpx.Request) -> httpx.Response:
        modulo = parse_qsl(request.content.decode()) if request.content else []
        self.richieste.append({"metodo": request.method, "percorso": request.url.path, "modulo": modulo,
                               "chiave": request.headers.get("authorization")})
        percorso = request.url.path
        if request.headers.get("authorization") != f"Bearer {CHIAVE}":
            return httpx.Response(401, json={"error": {"message": "Invalid API Key"}})
        if percorso == "/v1/account":
            return httpx.Response(200, json={"id": "acct_1", "charges_enabled": True, "country": "IT",
                                             "settings": {"dashboard": {"display_name": "TAROTS chat"}}})
        if percorso == "/v1/webhook_endpoints" and request.method == "GET":
            return httpx.Response(200, json={"data": self.endpoint})
        if percorso == "/v1/webhook_endpoints" and request.method == "POST":
            nuovo = {"id": f"we_{len(self.richieste)}", "url": dict(modulo)["url"], "secret": WHSEC}
            self.endpoint.append({k: v for k, v in nuovo.items() if k != "secret"})
            return httpx.Response(200, json=nuovo)
        if percorso.startswith("/v1/webhook_endpoints/"):
            ident = percorso.rsplit("/", 1)[1]
            if request.method == "DELETE":
                self.endpoint = [e for e in self.endpoint if e["id"] != ident]
                return httpx.Response(200, json={"id": ident, "deleted": True})
            return httpx.Response(200, json={"id": ident, "url": "https://tarots.chat/api/billing/webhook"})
        return httpx.Response(404, json={"error": {"message": "sconosciuto"}})

    def fatte(self, metodo: str, prefisso: str) -> List[Dict[str, Any]]:
        return [r for r in self.richieste if r["metodo"] == metodo and r["percorso"].startswith(prefisso)]


@pytest.fixture
def stripe_finto(monkeypatch, ambiente):
    finto = StripeFinto()
    monkeypatch.setattr(modulo_stripe, "TRASPORTO", httpx.MockTransport(finto.gestore))
    ambiente(api_public_url="https://tarots.chat/api", billing_provider="disattivato")
    return finto


async def test_stripe_dalla_console_senza_mai_rivelare_le_chiavi(admin, session, stripe_finto):
    r = await admin.put("/admin/configurazioni/stripe", json={"chiave_segreta": "pk_test_sbagliata"})
    assert r.status_code == 422 and "pubblicabile" in r.json()["detail"]
    r = await admin.put("/admin/configurazioni/stripe", json={"chiave_segreta": CHIAVE, "modalita": "live"})
    assert r.status_code == 422  # chiave di prova, modalità reale
    r = await admin.put("/admin/configurazioni/stripe", json={
        "chiave_segreta": CHIAVE, "chiave_pubblicabile": "pk_test_pubblica", "modalita": "test",
    })
    assert r.status_code == 200, r.text
    stato = r.json()
    assert stato["chiave_segreta"] == {"impostata": True, "origine": "console", "tipo": "sk"}
    assert stato["modalita"] == "test" and stato["chiave_pubblicabile"] == "pk_test_pubblica"
    assert stato["segreto_webhook"]["impostata"] is False
    assert stato["webhook"]["url_atteso"] == "https://tarots.chat/api/billing/webhook"
    assert "customer.subscription.trial_will_end" in stato["eventi"]

    prova = (await admin.post("/admin/configurazioni/stripe/prova")).json()
    assert prova["esito"]["ok"] is True and "TAROTS chat" in prova["esito"]["messaggio"]

    web = await admin.post("/admin/configurazioni/stripe/webhook")
    assert web.status_code == 200, web.text
    assert web.json()["azione"] == "creato"
    creazione = stripe_finto.fatte("POST", "/v1/webhook_endpoints")[0]
    eventi = [v for k, v in creazione["modulo"] if k.startswith("enabled_events")]
    assert set(eventi) == set(modulo_stripe.EVENTI)
    assert dict(creazione["modulo"])["url"] == "https://tarots.chat/api/billing/webhook"
    assert web.json()["stato"]["segreto_webhook"] == {"impostata": True, "origine": "console"}

    # Il segreto è salvato cifrato e Stripe verifica le firme con quello.
    riga = await session.get(ConfigStripe, 1)
    await session.refresh(riga)
    assert WHSEC.encode() not in bytes(riga.segreto_webhook_cifrato) and CHIAVE.encode() not in bytes(riga.chiave_segreta_cifrata)
    fornitore = modulo_stripe.PagamentiStripe()
    corpo = json.dumps({"id": "evt_1", "type": "invoice.created", "data": {"object": {"id": "in_1"}}}).encode()
    assert fornitore.verifica(corpo, {"stripe-signature": modulo_stripe.firma(corpo, WHSEC)}).tipo == "stripe.invoice.created"

    # Mai in chiaro: né nelle risposte, né nell'audit.
    risposte = json.dumps([stato, prova, web.json(), (await admin.get("/admin/configurazioni/stripe")).json()])
    assert CHIAVE not in risposte and WHSEC not in risposte
    registro = await _audit(session)
    assert CHIAVE not in registro and WHSEC not in registro and "configurazioni.stripe_webhook" in registro


async def test_il_webhook_esistente_si_aggiorna_e_non_si_duplica(admin, session, stripe_finto):
    await admin.put("/admin/configurazioni/stripe", json={"chiave_segreta": CHIAVE})
    assert (await admin.post("/admin/configurazioni/stripe/webhook")).json()["azione"] == "creato"
    # Di nuovo: l'endpoint c'è e il sito ne ha il segreto → si aggiornano gli eventi, nessuna creazione.
    seconda = (await admin.post("/admin/configurazioni/stripe/webhook")).json()
    assert seconda["azione"] == "aggiornato"
    assert len(stripe_finto.fatte("POST", "/v1/webhook_endpoints")) == 2  # una creazione + un aggiornamento
    assert len([r for r in stripe_finto.fatte("POST", "/v1/webhook_endpoints/") if r["percorso"] != "/v1/webhook_endpoints"]) == 1
    assert len(stripe_finto.endpoint) == 1


async def test_un_endpoint_di_cui_non_si_ha_il_segreto_si_sostituisce(admin, stripe_finto):
    stripe_finto.endpoint.append({"id": "we_vecchio", "url": "https://tarots.chat/api/billing/webhook"})
    await admin.put("/admin/configurazioni/stripe", json={"chiave_segreta": CHIAVE})
    r = (await admin.post("/admin/configurazioni/stripe/webhook")).json()
    assert r["azione"] == "sostituito"
    assert [e["id"] for e in stripe_finto.endpoint] != ["we_vecchio"] and len(stripe_finto.endpoint) == 1


async def test_il_webhook_vuole_un_indirizzo_pubblico_https(admin, stripe_finto, ambiente):
    ambiente(api_public_url="http://localhost:8100")
    await admin.put("/admin/configurazioni/stripe", json={"chiave_segreta": CHIAVE})
    r = await admin.post("/admin/configurazioni/stripe/webhook")
    assert r.status_code == 502 and "https" in r.json()["detail"]
    assert not stripe_finto.fatte("POST", "/v1/webhook_endpoints")


async def test_fornitore_dalla_console_con_i_controlli(admin, ambiente, stripe_finto):
    from tarot_core.billing.pagamenti import PagamentiDisattivati, PagamentiSimulati, provider_pagamenti

    r = await admin.put("/admin/configurazioni/stripe", json={"provider": "stripe"})
    assert r.status_code == 422 and "chiave segreta" in r.json()["detail"]
    await admin.put("/admin/configurazioni/stripe", json={"chiave_segreta": CHIAVE})
    r = await admin.put("/admin/configurazioni/stripe", json={"provider": "stripe"})
    assert r.status_code == 200 and r.json()["provider"] == "stripe" and r.json()["origine_provider"] == "console"
    assert provider_pagamenti().name == "stripe"

    r = await admin.put("/admin/configurazioni/stripe", json={"provider": "mock"})
    assert r.status_code == 200 and isinstance(provider_pagamenti(), PagamentiSimulati)
    ambiente(environment="prod")
    # In produzione il simulatore non si sceglie, e se c'è già non vale.
    assert isinstance(provider_pagamenti(), PagamentiDisattivati)
    r = await admin.put("/admin/configurazioni/stripe", json={"provider": "mock"})
    assert r.status_code == 422 and "simulato" in r.json()["detail"]


async def test_priorita_database_poi_ambiente(session, ambiente):
    ambiente(billing_provider="mock", stripe_secret_key=CHIAVE_AMBIENTE, stripe_webhook_secret="whsec_ambiente",
             smtp_host="smtp.ambiente.invalid", smtp_mittente="env@tarots.chat", smtp_password="pw-env")
    # Senza istantanea, e con la console vuota: l'ambiente.
    assert correnti.pagamenti().chiave_segreta == CHIAVE_AMBIENTE and correnti.pagamenti().origine_chiavi == "ambiente"
    assert correnti.smtp().host == "smtp.ambiente.invalid" and correnti.origine_smtp() == "ambiente"
    await correnti.carica(session)
    assert correnti.pagamenti().provider == "mock" and correnti.smtp().password == "pw-env"

    from tarot_core.llm.cifratura import cifra

    session.add(ConfigStripe(id=1, provider="stripe", chiave_segreta_cifrata=cifra(CHIAVE),
                             segreto_webhook_cifrato=cifra("whsec_console")))
    session.add(ConfigSmtp(id=1, host="mail.console.invalid", porta=587, sicurezza="starttls", utente="u",
                           password_cifrata=cifra("pw-console"), mittente="noreply@tarots.chat"))
    await session.flush()
    await correnti.carica(session)
    p = correnti.pagamenti()
    assert (p.provider, p.chiave_segreta, p.segreto_webhook, p.origine_chiavi) == ("stripe", CHIAVE, "whsec_console", "console")
    assert modulo_stripe.PagamentiStripe()._chiave == CHIAVE
    s = correnti.smtp()
    assert (s.host, s.porta, s.ssl, s.password, s.mittente) == ("mail.console.invalid", 587, False, "pw-console", "noreply@tarots.chat")

    # Svuotata la console, si torna all'ambiente (le chiavi in coppia: mai la chiave della console col segreto
    # dell'ambiente).
    riga = await session.get(ConfigStripe, 1)
    riga.chiave_segreta_cifrata = None
    (await session.get(ConfigSmtp, 1)).host = ""
    await session.flush()
    await correnti.carica(session)
    assert correnti.pagamenti().chiave_segreta == CHIAVE_AMBIENTE and correnti.pagamenti().segreto_webhook == "whsec_ambiente"
    assert correnti.smtp().host == "smtp.ambiente.invalid"


# ---- importazione dall'ambiente -------------------------------------------------------------------------------------


async def test_importazione_dall_ambiente_una_volta_sola(session, ambiente, tmp_path):
    import paramiko

    file_chiave = tmp_path / "ssh-key"
    paramiko.Ed25519Key  # noqa: B018 — la chiave del NAS può essere di qualunque tipo
    paramiko.RSAKey.generate(2048).write_private_key_file(str(file_chiave))
    ambiente(smtp_host="mail.tadamoo.com", smtp_mittente="noreply@tarots.chat", smtp_utente="noreply@tarots.chat",
             smtp_password=PASSWORD_SMTP, stripe_secret_key=CHIAVE_AMBIENTE, stripe_webhook_secret="whsec_env",
             billing_provider="disattivato", backup_chiave_ssh=str(file_chiave), backup_password="")

    copiate = await importa.dall_ambiente(session)
    assert set(copiate) == {"smtp", "stripe_chiavi", "stripe_provider", "backup_credenziale"}
    await correnti.carica(session)
    assert correnti.origine_smtp() == "console" and correnti.smtp().password == PASSWORD_SMTP
    assert correnti.pagamenti().origine_chiavi == "console" and correnti.pagamenti().origine_provider == "console"
    from tarot_core.tarot import backup

    cred = backup.credenziale(await backup.impostazioni(session))
    assert cred["origine"] == "console" and cred["chiave_impronta"].startswith("SHA256:")
    registro = await _audit(session)
    assert registro.count("configurazioni.importato_dall_ambiente") == 4
    assert PASSWORD_SMTP not in registro and CHIAVE_AMBIENTE not in registro

    # Una volta sola: anche svuotando la console e cambiando l'ambiente, non si ricopia nulla.
    (await session.get(ConfigSmtp, 1)).host = ""
    await session.flush()
    ambiente(smtp_host="altro.invalid")
    assert await importa.dall_ambiente(session) == []
    assert (await session.get(ConfigSmtp, 1)).host == ""
    assert {r.voce for r in (await session.execute(select(ImportazioneAmbiente))).scalars()} == {
        "smtp", "stripe_chiavi", "stripe_provider", "backup_credenziale"}


async def test_l_importazione_non_tocca_la_console_gia_piena(session, ambiente):
    from tarot_core.llm.cifratura import cifra

    session.add(ConfigSmtp(id=1, host="mail.console.invalid", mittente="a@tarots.chat", password_cifrata=cifra("pc")))
    await session.flush()
    ambiente(smtp_host="mail.ambiente.invalid", smtp_mittente="b@tarots.chat")
    assert "smtp" not in await importa.dall_ambiente(session)
    assert (await session.get(ConfigSmtp, 1)).host == "mail.console.invalid"
    assert (await session.get(ImportazioneAmbiente, "smtp")).esito == "gia_in_console"


async def test_niente_simulatore_importato_in_produzione(session, ambiente):
    ambiente(billing_provider="mock", environment="prod")
    assert "stripe_provider" not in await importa.dall_ambiente(session)


# ---- segreti interni ---------------------------------------------------------------------------------------------


async def test_segreto_ip_generato_e_stabile(session, ambiente):
    ambiente(ip_hash_secret="", condivisione_sale="")
    primo = await segreti.assicura(session, "ip_hash")
    assert len(primo) >= 40 and primo != ip_protetto.SEGRETO_SVILUPPO
    assert ip_protetto.segreto_corrente() == primo
    assert ip_protetto.impronta("93.44.12.201") == ip_protetto.impronta("93.44.12.201", primo)
    riga = await session.get(SegretoSistema, "ip_hash")
    assert riga.origine == "generato" and primo.encode() not in bytes(riga.valore_cifrato)
    # Un riavvio (processo nuovo) rilegge lo stesso.
    ip_protetto.imposta_segreto(None)
    assert await segreti.assicura(session, "ip_hash") == primo
    await segreti.assicura_tutti(session)
    assert segreti.sale_condivisione() not in ("", segreti.SALE_SVILUPPO)


async def test_se_l_ambiente_lo_da_vince_e_resta_dopo_averlo_tolto(session, ambiente):
    ambiente(ip_hash_secret="")
    generato = await segreti.assicura(session, "ip_hash")
    ambiente(ip_hash_secret="segreto-dell-ambiente")
    assert await segreti.assicura(session, "ip_hash") == "segreto-dell-ambiente" != generato
    assert (await session.get(SegretoSistema, "ip_hash")).origine == "ambiente"
    ambiente(ip_hash_secret="")
    ip_protetto.imposta_segreto(None)
    assert await segreti.assicura(session, "ip_hash") == "segreto-dell-ambiente"


def test_in_produzione_mancano_i_segreti_e_le_chiavi_stripe_ma_si_parte():
    from tarot_core.settings import Settings

    problemi = Settings(environment="prod", database_url="postgresql+psycopg://x@db/x",
                        llm_provider_key="Zm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyZm9vYmFyMTI=",
                        billing_provider="stripe").validate_production()
    assert problemi == [], problemi
    assert any("simulato" in p for p in Settings(environment="prod", billing_provider="mock").validate_production())


# ---- posta in uscita ---------------------------------------------------------------------------------------------


@pytest.fixture
def posta_finta(monkeypatch):
    from tarot_core.posta import invio

    inviate: List[Any] = []

    def spedisci(config, messaggi):
        inviate.append((config, list(messaggi)))
        return {m["To"]: "ok" for m in messaggi}

    monkeypatch.setattr(invio, "SPEDISCI", spedisci)
    return inviate


async def test_posta_dalla_console_e_email_di_prova(admin, session, posta_finta, ambiente):
    ambiente(smtp_host="", smtp_mittente="")
    stato = (await admin.get("/admin/configurazioni/smtp")).json()
    assert stato["origine"] == "nessuna" and stato["email_admin"] == "admin@example.com"
    r = await admin.put("/admin/configurazioni/smtp", json={
        "host": "mail.tadamoo.com", "porta": 465, "sicurezza": "ssl", "utente": "noreply@tarots.chat",
        "password": PASSWORD_SMTP, "mittente": "noreply@tarots.chat", "nome_mittente": "TAROTS chat",
    })
    assert r.status_code == 200, r.text
    assert r.json()["origine"] == "console" and r.json()["console"]["password"] == {"impostata": True}

    prova = (await admin.post("/admin/configurazioni/smtp/prova", json={"destinatario": "admin@example.com"})).json()
    assert prova["ok"] is True
    config, messaggi = posta_finta[-1]
    assert config.host == "mail.tadamoo.com" and config.password == PASSWORD_SMTP
    assert messaggi[0]["To"] == "admin@example.com" and "prova" in messaggi[0]["Subject"]

    # Un salvataggio senza password tiene quella di prima.
    await admin.put("/admin/configurazioni/smtp", json={
        "host": "mail.tadamoo.com", "porta": 465, "sicurezza": "ssl", "utente": "noreply@tarots.chat",
        "mittente": "noreply@tarots.chat",
    })
    assert correnti.smtp().password == PASSWORD_SMTP

    # Le email agli utenti passano dalla stessa configurazione.
    from tarot_core.posta.invio import manda
    from tarot_core.domain.repositories import UserRepository
    from tarot_core.auth.keycloak import Principal

    utente = await UserRepository(session).ensure(Principal(subject="sub-x", email="x@example.com", roles={"user"}))
    assert await manda(session, utente, "sospensione", "prova-console:1", {}) == "inviata"
    assert posta_finta[-1][0].host == "mail.tadamoo.com"

    risposte = json.dumps([r.json(), prova, (await admin.get("/admin/configurazioni/smtp")).json()])
    registro = await _audit(session)
    assert PASSWORD_SMTP not in risposte and PASSWORD_SMTP not in registro


async def test_email_di_prova_non_configurata_o_rifiutata(admin, monkeypatch, ambiente):
    import smtplib

    from tarot_core.posta import invio

    ambiente(smtp_host="", smtp_mittente="")
    assert (await admin.post("/admin/configurazioni/smtp/prova", json={"destinatario": "a@b.it"})).json()["ok"] is False

    def rifiuta(config, messaggi):
        raise smtplib.SMTPAuthenticationError(535, b"bad credentials")

    monkeypatch.setattr(invio, "SPEDISCI", rifiuta)
    await admin.put("/admin/configurazioni/smtp", json={"host": "mail.x.invalid", "mittente": "n@tarots.chat"})
    esito = (await admin.post("/admin/configurazioni/smtp/prova", json={"destinatario": "a@b.it"})).json()
    assert esito["ok"] is False and "utente o password" in esito["messaggio"]


# ---- sonda DNS ---------------------------------------------------------------------------------------------------


def _dns_finto(record: Dict[str, List[str]]):
    def gestore(request: httpx.Request) -> httpx.Response:
        nome, tipo = request.url.params["name"], request.url.params["type"]
        risposte = [{"name": nome, "type": 16 if tipo == "TXT" else 15, "data": d} for d in record.get(f"{tipo} {nome}", [])]
        return httpx.Response(200, json={"Status": 0 if risposte else 3, "Answer": risposte})

    return httpx.MockTransport(gestore)


async def test_sonda_dns_spf_presente_dkim_e_dmarc_assenti(admin, monkeypatch, ambiente):
    monkeypatch.setattr(dns, "TRASPORTO", _dns_finto({
        "TXT tarots.chat": ['"v=spf1 include:spf.efwd.registrar-servers.com a:mail.tadamoo.com ~all"',
                            '"google-site-verification=abc"'],
        "MX tarots.chat": ["10 eforward1.registrar-servers.com."],
    }))
    ambiente(smtp_host="mail.tadamoo.com", smtp_mittente="noreply@tarots.chat")
    esito = (await admin.get("/admin/configurazioni/smtp/dns")).json()
    assert esito["dominio"] == "tarots.chat"
    assert esito["spf"]["stato"] == "presente" and "a:mail.tadamoo.com" in esito["spf"]["valore"]
    assert esito["dkim"]["stato"] == "assente" and esito["dmarc"]["stato"] == "assente"
    assert esito["mx"] == ["10 eforward1.registrar-servers.com"]

    # La voce «Posta in uscita» di Account: la verifica fa la sonda, poi lo stato la ricorda senza rifarla.
    v = (await admin.post("/admin/account-esterni/smtp/verifica")).json()
    assert v["esito"]["stato"] == "configurato" and "DKIM assente" in v["esito"]["dettaglio"]
    assert "DMARC assente" in v["servizio"]["dettaglio"]


async def test_sonda_dns_tutto_presente_con_record_spezzati(monkeypatch):
    monkeypatch.setattr(dns, "TRASPORTO", _dns_finto({
        "TXT tarots.chat": ['"v=spf1 a ~all"'],
        "TXT _dmarc.tarots.chat": ['"v=DMARC1; p=quarantine; rua=mailto:dmarc@tarots.chat"'],
        "TXT 202610r._domainkey.tarots.chat": ['"v=DKIM1; k=rsa; " "p=MIIBIjANBgkq"'],
    }))
    esito = await dns.controlla("tarots.chat", "202610r", forza=True)
    assert esito["dkim"] == {**esito["dkim"], "stato": "presente", "selettore": "202610r"}
    assert esito["dkim"]["valore"] == "v=DKIM1; k=rsa; p=MIIBIjANBgkq"
    assert esito["dmarc"]["stato"] == "presente" and esito["spf"]["stato"] == "presente"


async def test_sonda_dns_irraggiungibile_non_solleva(monkeypatch):
    def guasto(request):
        raise httpx.ConnectError("niente rete")

    monkeypatch.setattr(dns, "TRASPORTO", httpx.MockTransport(guasto))
    esito = await dns.controlla("tarots.chat", forza=True)
    assert esito["errore"] and esito["spf"]["stato"] == "errore"


# ---- dati del titolare e informativa ---------------------------------------------------------------------------


async def test_titolare_dalla_console_e_informativa_senza_segnaposto(admin, client, session):
    from tarot_core.domain.config_models import LlmProvider
    from tarot_core.llm.cifratura import cifra

    session.add_all([
        LlmProvider(nome="nim", tipo="nvidia", provider="openai-compatible", base_url="https://x", model="m",
                    api_key_cifrata=cifra("chiave-llm-segreta"), attivo=True),
        LlmProvider(nome="ds", tipo="deepseek", provider="openai-compatible", base_url="https://y", model="m", attivo=True),
        LlmProvider(nome="spento", tipo="openai", provider="openai-compatible", base_url="https://z", model="m", attivo=False),
        LlmProvider(nome="locale", tipo="lmstudio", provider="openai-compatible", base_url="http://127.0.0.1", model="m", attivo=True),
    ])
    await session.commit()

    vuoto = (await client.get("/privacy/titolare")).json()
    assert vuoto["nome"] is None and vuoto["email_privacy"] == "privacy@tarots.chat"
    assert vuoto["hosting"].startswith("Hivelocity") and vuoto["dpo"] == {"nominato": False, "contatto": None}

    r = await admin.put("/admin/configurazioni/titolare", json={"dpo_nominato": True})
    assert r.status_code == 422
    r = await admin.put("/admin/configurazioni/titolare", json={
        "nome": "Andrea Taini", "indirizzo": "Via Roma 1, 20100 Milano (MI), Italia", "codice_fiscale": "",
        "email_privacy": "privacy@tarots.chat", "dpo_nominato": False, "dpo_contatto": "",
        "hosting": "Hivelocity, data center di Londra (Regno Unito)",
    })
    assert r.status_code == 200, r.text

    client.identita.principal = None
    pubblico = (await client.get("/privacy/titolare")).json()
    assert pubblico["nome"] == "Andrea Taini" and pubblico["indirizzo"].startswith("Via Roma 1")
    assert pubblico["codice_fiscale"] is None
    fornitori = {f["nome"]: f for f in pubblico["fornitori_ai"]}
    assert fornitori["NVIDIA"]["paese"] == "US" and fornitori["DeepSeek"]["paese"] == "CN"
    assert fornitori["LM Studio"]["proprio"] is True
    assert "OpenAI" not in fornitori  # spento
    testo = json.dumps(pubblico, ensure_ascii=False)
    assert "TODO" not in testo and "chiave-llm-segreta" not in testo


def test_le_informative_del_sito_non_hanno_piu_segnaposto():
    from pathlib import Path

    radice = Path(__file__).resolve().parents[3] / "frontend" / "v2"
    if not radice.is_dir():
        pytest.skip("il sito non è in questa copia")
    for file in [radice / "pagine" / "privacy.tsx", *(radice / "i18n").glob("*/privacy.ts")]:
        assert "TODO_OPERATORE" not in file.read_text(encoding="utf-8"), file


# ---- credenziale del NAS dalla console ---------------------------------------------------------------------------


@pytest.fixture
def nas(tmp_path, ambiente):
    import paramiko

    from .sftp_finto import ServerSftpFinto

    chiave = paramiko.RSAKey.generate(2048)
    radice = tmp_path / "nas"
    radice.mkdir()
    server = ServerSftpFinto(radice, chiave).avvia()
    # Nessun Secret montato: la credenziale arriva solo dalla console.
    ambiente(backup_chiave_ssh=str(tmp_path / "non-c-e"), backup_password="")
    server.chiave_client = chiave
    yield server
    server.ferma()


async def test_backup_con_la_chiave_caricata_in_console(admin, session, nas):
    import io

    testo = io.StringIO()
    nas.chiave_client.write_private_key(testo)
    chiave_pem = testo.getvalue()

    await admin.put("/admin/backup/impostazioni", json={
        "attivo": False, "host": "127.0.0.1", "porta": nas.porta, "utente": "nuspy", "cartella": "/backup/tarots",
        "conserva": 7,
    })
    stato = (await admin.get("/admin/backup")).json()
    assert stato["credenziale"]["configurata"] is False
    senza = (await admin.post("/admin/backup/prova", json={})).json()
    assert senza["riuscita"] is False and "credenziale" in senza["dettaglio"]

    assert (await admin.put("/admin/backup/credenziale", json={"chiave_ssh": "ssh-rsa AAAA pubblica"})).status_code == 422
    r = await admin.put("/admin/backup/credenziale", json={"chiave_ssh": chiave_pem})
    assert r.status_code == 200, r.text
    cred = r.json()
    assert cred["origine"] == "console" and cred["chiave_tipo"] == "ssh-rsa" and cred["chiave_impronta"].startswith("SHA256:")
    prova = (await admin.post("/admin/backup/prova", json={"fidati": True})).json()
    assert prova["riuscita"] is True, prova

    risposte = json.dumps([cred, (await admin.get("/admin/backup")).json()])
    registro = await _audit(session)
    corpo_chiave = chiave_pem.splitlines()[1]
    assert corpo_chiave not in risposte and corpo_chiave not in registro

    tolta = (await admin.put("/admin/backup/credenziale", json={"togli": True})).json()
    assert tolta["configurata"] is False


async def test_solo_l_amministratore(client):
    for metodo, percorso in (("get", "/admin/configurazioni/stripe"), ("get", "/admin/configurazioni/smtp"),
                             ("get", "/admin/configurazioni/titolare"), ("put", "/admin/backup/credenziale")):
        r = await getattr(client, metodo)(percorso, **({"json": {}} if metodo == "put" else {}))
        assert r.status_code == 403, percorso
