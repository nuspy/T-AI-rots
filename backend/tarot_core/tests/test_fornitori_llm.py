"""I fornitori LLM in console: CRUD, cifratura della chiave a riposo, prova di connessione, assegnazione."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from tarot_core.llm import cifratura

from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def come(client, principal_utente, principal_admin):
    """Cambia chi fa le richieste: `come("admin")` o `come("utente")`."""

    def scegli(chi: str):
        client.identita.principal = principal_admin if chi == "admin" else principal_utente
        return client

    return scegli


class ServerModelli:
    """Un finto server OpenAI-compatibile: risponde a GET /models e registra l'Authorization ricevuto."""

    def __init__(self, modelli=("m-uno", "m-due")):
        self.autorizzazioni: list[str | None] = []
        self._modelli = list(modelli)
        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), self._gestore())
        self.url = f"http://127.0.0.1:{self._httpd.server_port}/v1"
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    def _gestore(self):
        server = self

        class Gestore(BaseHTTPRequestHandler):
            def do_GET(self):
                server.autorizzazioni.append(self.headers.get("authorization"))
                corpo = json.dumps({"data": [{"id": m} for m in server._modelli]}).encode()
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(corpo)))
                self.end_headers()
                self.wfile.write(corpo)

            def log_message(self, *a):
                pass

        return Gestore

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *a):
        self._httpd.shutdown()


async def test_solo_l_amministratore_vede_e_scrive_i_fornitori(come):
    utente = come("utente")
    assert (await utente.get("/admin/llm/providers")).status_code == 403
    assert (await utente.post("/admin/llm/providers", json={"nome": "x", "tipo": "openai"})).status_code == 403


async def test_si_crea_un_fornitore_e_la_chiave_non_torna_mai(come):
    admin = come("admin")
    r = await admin.post("/admin/llm/providers", json={
        "nome": "prova-uno", "tipo": "nvidia", "api_key": "segreta-123", "model": "un-modello",
    })
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["has_key"] is True
    assert "api_key" not in corpo and "segreta-123" not in json.dumps(corpo)
    assert corpo["base_url"] == "https://integrate.api.nvidia.com/v1"          # dal catalogo, non passato
    assert corpo["provider"] == "openai-compatible"

    elenco = (await admin.get("/admin/llm/providers")).json()
    nomi = {f["nome"] for f in elenco["fornitori"]}
    assert "prova-uno" in nomi
    assert all("api_key" not in f and "segreta-123" not in json.dumps(f) for f in elenco["fornitori"])
    assert any(t["tipo"] == "nvidia" for t in elenco["catalogo"])


async def test_il_nome_e_univoco(come):
    admin = come("admin")
    await admin.post("/admin/llm/providers", json={"nome": "doppio-fornitore", "tipo": "openai_compat"})
    r = await admin.post("/admin/llm/providers", json={"nome": "doppio-fornitore", "tipo": "openai_compat"})
    assert r.status_code == 409


async def test_un_tipo_sconosciuto_e_rifiutato(come):
    admin = come("admin")
    r = await admin.post("/admin/llm/providers", json={"nome": "tipo-sbagliato", "tipo": "non-esiste"})
    assert r.status_code == 422


async def test_i_parametri_riservati_sono_rifiutati_anche_qui(come):
    admin = come("admin")
    r = await admin.post("/admin/llm/providers", json={
        "nome": "parametri-vietati", "tipo": "openai_compat", "parametri": {"model": "x"},
    })
    assert r.status_code == 422


async def test_la_modifica_lascia_la_chiave_se_non_la_tocca_e_la_svuota_se_manda_vuota(come):
    admin = come("admin")
    creato = (await admin.post("/admin/llm/providers", json={
        "nome": "prova-due", "tipo": "openai_compat", "api_key": "prima-chiave",
    })).json()

    r = await admin.put(f"/admin/llm/providers/{creato['id']}", json={"descrizione": "cambiata"})
    assert r.json()["has_key"] is True             # non toccata: resta
    assert r.json()["descrizione"] == "cambiata"

    r = await admin.put(f"/admin/llm/providers/{creato['id']}", json={"api_key": ""})
    assert r.json()["has_key"] is False             # mandata vuota: si svuota


async def test_si_elimina_un_fornitore(come):
    admin = come("admin")
    creato = (await admin.post("/admin/llm/providers", json={"nome": "da-eliminare", "tipo": "openai_compat"})).json()
    assert (await admin.delete(f"/admin/llm/providers/{creato['id']}")).status_code == 204
    elenco = (await admin.get("/admin/llm/providers")).json()
    assert creato["id"] not in {f["id"] for f in elenco["fornitori"]}
    assert (await admin.delete(f"/admin/llm/providers/{creato['id']}")).status_code == 404


async def test_la_chiave_e_cifrata_nel_database_e_si_decifra_per_usarla(session, come):
    from tarot_core.domain.config_models import LlmProvider

    admin = come("admin")
    creato = (await admin.post("/admin/llm/providers", json={
        "nome": "prova-cifrata", "tipo": "openai_compat", "api_key": "la-mia-chiave-segreta",
    })).json()

    riga = await session.get(LlmProvider, creato["id"])
    assert riga.api_key_cifrata is not None
    assert b"la-mia-chiave-segreta" not in bytes(riga.api_key_cifrata)
    assert cifratura.decifra(riga.api_key_cifrata) == "la-mia-chiave-segreta"


async def test_la_prova_di_connessione_usa_la_chiave_decifrata(come):
    admin = come("admin")
    with ServerModelli(["m-uno", "m-due"]) as server:
        creato = (await admin.post("/admin/llm/providers", json={
            "nome": "prova-connessione", "tipo": "openai_compat", "base_url": server.url, "api_key": "sesamo",
        })).json()
        r = await admin.post(f"/admin/llm/providers/{creato['id']}/prova")
        corpo = r.json()
        assert corpo["ok"] is True and corpo["modelli"] == ["m-uno", "m-due"]
        assert server.autorizzazioni == ["Bearer sesamo"]


async def test_la_prova_dice_l_errore_senza_farlo_esplodere(come):
    admin = come("admin")
    creato = (await admin.post("/admin/llm/providers", json={
        "nome": "prova-morto", "tipo": "openai_compat", "base_url": "http://127.0.0.1:1",
    })).json()
    r = await admin.post(f"/admin/llm/providers/{creato['id']}/prova")
    assert r.status_code == 200 and r.json()["ok"] is False


async def test_l_assegnazione_sceglie_fra_i_fornitori_in_console(come):
    admin = come("admin")
    await admin.post("/admin/llm/providers", json={"nome": "per-l-assegnazione", "tipo": "openai_compat"})
    stato = (await admin.get("/admin/models")).json()
    assert any(m["nome"] == "per-l-assegnazione" for m in stato["modelli"])
    r = await admin.put("/admin/models/interpretazione", json={"modello": "per-l-assegnazione"})
    assert r.status_code == 200
    assert any(
        c["compito"] == "interpretazione" and c["in_uso"] == "per-l-assegnazione" for c in r.json()["compiti"]
    )
