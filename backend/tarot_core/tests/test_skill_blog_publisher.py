"""La skill degli agenti (`skills/tarots-blog-publisher`): il suo script parla con la REST del blog.

Due cose da tenere ferme: che ciò che lo script manda sia ciò che l'API accetta (se cambia un campo, il test
lo dice), e che non faccia mai ciò che non deve — mostrare la chiave, seguire un redirect portandola altrove,
salvare sotto la soglia di SEO, ripetere una POST."""
from __future__ import annotations

import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[3] / "skills" / "tarots-blog-publisher"
SCRIPT = RADICE / "scripts" / "tarots_blog.py"

pytestmark = pytest.mark.skipif(not SCRIPT.exists(), reason="la cartella skills/ non c'è (immagine senza sorgenti)")

CHIAVE = "tk_live_abcdef123456_segreto-da-non-stampare"


@pytest.fixture(autouse=True)
def _cache_isolata(monkeypatch, tmp_path, cli):
    """La cache locale della chiave (`CACHE_PATH` in tarots_blog.py) è per macchina, non per test: senza
    questo isolamento una chiave già salva su questa macchina (da un uso reale della skill, o da un test
    precedente nello stesso lancio) apparirebbe «diversa» dalla `CHIAVE` finta dei test, bloccandoli col
    controllo appena aggiunto. `CACHE_PATH` è una costante di modulo, fissata all'importazione — la sola
    variabile d'ambiente non basta a cambiarla test per test: si riassegna direttamente l'attributo,
    a un percorso nuovo (e quindi inesistente) per ciascun test."""
    monkeypatch.setattr(cli, "CACHE_PATH", tmp_path / "cache-di-prova.json")


@pytest.fixture(scope="module")
def cli():
    spec = importlib.util.spec_from_file_location("tarots_blog", SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class Server:
    """Un finto server dell'API: registra le richieste e risponde con ciò che il test ha preparato."""

    def __init__(self):
        self.richieste = []
        self.risposte = {}      # (metodo, percorso) → (stato, corpo, intestazioni)
        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), self._gestore())
        self.url = f"http://127.0.0.1:{self._httpd.server_port}"
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    def _gestore(self):
        server = self

        class Gestore(BaseHTTPRequestHandler):
            def _rispondi(self):
                lunghezza = int(self.headers.get("content-length") or 0)
                corpo = self.rfile.read(lunghezza) if lunghezza else b""
                server.richieste.append({
                    "metodo": self.command, "percorso": self.path.split("?")[0], "query": self.path.partition("?")[2],
                    "auth": self.headers.get("authorization"), "tipo": self.headers.get("content-type"), "corpo": corpo,
                })
                stato, dati, extra = server.risposte.get((self.command, self.path.split("?")[0]), (404, {"detail": "no"}, {}))
                payload = json.dumps(dati).encode() if dati is not None else b""
                self.send_response(stato)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(payload)))
                for k, v in extra.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_PATCH = do_DELETE = _rispondi

            def log_message(self, *args):
                pass

        return Gestore

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *args):
        self._httpd.shutdown()
        self._httpd.server_close()


@pytest.fixture
def api(monkeypatch):
    with Server() as s:
        monkeypatch.setenv("TAROTS_API_URL", s.url)
        monkeypatch.setenv("TAROTS_API_KEY", CHIAVE)
        yield s


def rapporto(punteggio: int) -> dict:
    return {
        "punteggio": punteggio, "giudizio": "ottimo" if punteggio >= 85 else "buono",
        "controlli": [
            {"id": "lunghezza", "esito": "avviso" if punteggio < 85 else "ok", "peso": 3,
             "messaggio": "The article has 363 words.", "messaggio_it": "…"},
        ],
        "suggerimenti": [], "statistiche": {"parole": 363, "titoli_h2": 3, "collegamenti_interni": 3,
                                             "collegamenti_esterni": 0, "faq": 3},
    }


ESEMPIO = RADICE / "assets" / "example-article.json"


# ---- il formato ---------------------------------------------------------------------------------------------


def test_l_esempio_e_accettato_dall_api_e_analizzabile(cli):
    from tarot_core.api.routers.rest_blog import ArticoloRest
    from tarot_core.tarot import blog_seo

    payload = cli.load_article(str(ESEMPIO))
    articolo = ArticoloRest(**payload)                  # ogni campo che lo script manda esiste nell'API
    assert articolo.lang == "en" and articolo.stato == "bozza" and len(articolo.faq) == 3
    assert articolo.seo_parola_chiave == "the tower tarot card meaning"
    seo = blog_seo.analizza(
        titolo=articolo.titolo, testo=articolo.testo, slug=articolo.slug or "", seo_titolo=articolo.seo_titolo,
        seo_descrizione=articolo.seo_descrizione, parola_chiave=articolo.seo_parola_chiave,
        immagine_presente=True, immagine_alt=articolo.immagine_alt, tags=articolo.tags,
        faq=[f.model_dump() for f in articolo.faq],
    )
    esiti = {c["id"]: c["esito"] for c in seo["controlli"]}
    # L'esempio è accorciato: la lunghezza è l'unica cosa che manca; titolo, descrizione e parola chiave tornano.
    assert esiti["titolo_seo"] == esiti["descrizione_seo"] == esiti["chiave_nel_titolo"] == esiti["chiave_nello_slug"] == "ok"
    assert esiti["chiave_nell_inizio"] == esiti["collegamenti_interni"] == esiti["faq"] == "ok"
    assert esiti["lunghezza"] == "avviso"


def test_ogni_campo_dell_api_ha_un_nome_amichevole_o_lo_stesso(cli):
    from tarot_core.api.routers.rest_blog import ArticoloRest

    campi_api = set(ArticoloRest.model_fields)
    # Tutto ciò che lo script sa scrivere è un campo dell'API (tranne `sezione`, che l'API risolve da slug)...
    assert set(cli.API_FIELDS) <= campi_api
    # ...e ogni campo scrivibile dell'API si può passare dallo script.
    assert campi_api - {"immagine_base64"} <= set(cli.API_FIELDS)


def test_un_campo_sconosciuto_e_un_errore_non_un_silenzio(cli, tmp_path):
    file = tmp_path / "a.json"
    file.write_text(json.dumps({"title": "x", "keyword": "sbagliato"}), encoding="utf-8")
    with pytest.raises(cli.Failure) as e:
        cli.load_article(str(file))
    assert e.value.code == cli.EXIT_USAGE and "keyword" in str(e.value)


def test_stato_faq_e_liste_in_forma_amichevole(cli):
    p = cli.normalize({
        "title": "T", "status": "published", "faq": [{"question": "Q?", "answer": "A."}],
        "secondary_keywords": "uno, due", "tags": "a, b",
    })
    assert p["stato"] == "pubblicato" and p["faq"] == [{"domanda": "Q?", "risposta": "A."}]
    assert p["seo_parole_chiave"] == ["uno", "due"] and p["tags"] == ["a", "b"]


def test_body_file_si_legge_accanto_al_json(cli, tmp_path):
    (tmp_path / "testo.md").write_text("## Ciao\n\nUn testo.", encoding="utf-8")
    p = cli.normalize({"title": "T", "body_file": "testo.md"}, tmp_path)
    assert p["testo"].startswith("## Ciao")
    with pytest.raises(cli.Failure):
        cli.normalize({"title": "T", "body_file": "manca.md"}, tmp_path)


# ---- la configurazione: sicura per costruzione -----------------------------------------------------------------


@pytest.mark.parametrize("url", ["http://tarots.example.com/api", "ftp://x", "tarots.example.com"])
def test_senza_https_la_chiave_non_parte(cli, monkeypatch, url):
    monkeypatch.setenv("TAROTS_API_URL", url)
    monkeypatch.setenv("TAROTS_API_KEY", CHIAVE)
    with pytest.raises(cli.Failure) as e:
        cli.config()
    assert e.value.code == cli.EXIT_CONFIG


def test_senza_chiave_o_url_lo_script_lo_dice(cli, monkeypatch):
    monkeypatch.delenv("TAROTS_API_KEY", raising=False)
    monkeypatch.setenv("TAROTS_API_URL", "https://tarots.example.com/api")
    with pytest.raises(cli.Failure) as e:
        cli.config()
    assert e.value.code == cli.EXIT_CONFIG and "TAROTS_API_KEY" in str(e.value)
    monkeypatch.setenv("TAROTS_API_KEY", "una-chiave-qualsiasi")
    with pytest.raises(cli.Failure):
        cli.config()
    monkeypatch.delenv("TAROTS_API_URL")
    monkeypatch.setenv("TAROTS_API_KEY", CHIAVE)
    with pytest.raises(cli.Failure) as e:
        cli.config()
    assert "TAROTS_API_URL" in str(e.value)


def test_la_chiave_si_manda_ma_non_si_stampa_mai(cli, api, capsys):
    api.risposte[("GET", "/v1/blog/sections")] = (200, [{"slug": "learn", "nome": "Learn", "percorso": "Learn"}], {})
    assert cli.main(["sections"]) == cli.EXIT_OK
    assert api.richieste[0]["auth"] == f"Bearer {CHIAVE}"
    fuori = capsys.readouterr()
    assert CHIAVE not in fuori.out and CHIAVE not in fuori.err and "learn" in fuori.out


def test_un_errore_dell_api_non_riporta_la_chiave_e_da_un_suggerimento(cli, api, capsys):
    api.risposte[("GET", "/v1/blog/guide")] = (401, {"detail": "Chiave non valida"}, {})
    assert cli.main(["guide"]) == cli.EXIT_API
    err = capsys.readouterr().err
    assert "HTTP 401" in err and "Blog > Keys" in err and CHIAVE not in err


def test_un_redirect_non_si_segue_e_la_chiave_non_va_altrove(cli, monkeypatch, capsys):
    with Server() as altrove, Server() as api:
        api.risposte[("GET", "/v1/blog/guide")] = (302, None, {"location": f"{altrove.url}/v1/blog/guide"})
        altrove.risposte[("GET", "/v1/blog/guide")] = (200, {"ok": True}, {})
        monkeypatch.setenv("TAROTS_API_URL", api.url)
        monkeypatch.setenv("TAROTS_API_KEY", CHIAVE)
        assert cli.main(["guide"]) == cli.EXIT_API
        assert altrove.richieste == []                     # la chiave non ci è arrivata
        assert "redirect" in capsys.readouterr().err


# ---- pubblicare -----------------------------------------------------------------------------------------------------


def _articolo(tmp_path, **extra):
    file = tmp_path / "a.json"
    file.write_text(json.dumps({"title": "Titolo di prova per la skill", "body": "## Uno\n\nTesto.", **extra}), encoding="utf-8")
    return str(file)


def test_sotto_la_soglia_non_si_salva_niente(cli, api, tmp_path, capsys):
    api.risposte[("POST", "/v1/blog/posts")] = (201, {"dry_run": True, "seo": rapporto(60), "avvisi": []}, {})
    assert cli.main(["post", _articolo(tmp_path)]) == cli.EXIT_SCORE
    veri = [r for r in api.richieste if json.loads(r["corpo"] or b"{}").get("dry_run") is not True]
    assert veri == []                                      # solo la prova, nessun salvataggio
    assert "Not saved" in capsys.readouterr().err


def test_sopra_la_soglia_si_prova_e_poi_si_salva_una_volta(cli, api, tmp_path, capsys):
    def esito(stato):
        return {
            "articolo": {"id": "7f1c", "stato": stato, "lang": "en", "slug": "x"}, "url": "https://tarots.chat/blog/x",
            "seo": rapporto(90), "avvisi": ["Saved as a draft: this key has no `blog:publish` permission."],
        }

    # Il finto server risponde alla prova (dry_run) e al salvataggio con la stessa rotta: si distingue dal corpo.
    api.risposte[("POST", "/v1/blog/posts")] = (201, {**esito("bozza"), "dry_run": True}, {})
    assert cli.main(["post", _articolo(tmp_path, status="published")]) == cli.EXIT_OK
    posts = [r for r in api.richieste if r["metodo"] == "POST" and r["percorso"] == "/v1/blog/posts"]
    assert len(posts) == 2                                 # prova + salvataggio, mai di più (niente retry su POST)
    prima, seconda = (json.loads(r["corpo"]) for r in posts)
    assert prima["dry_run"] is True and "dry_run" not in seconda
    assert seconda["stato"] == "pubblicato" and seconda["titolo"].startswith("Titolo")
    fuori = capsys.readouterr()
    assert "saved: id=7f1c" in fuori.out and "not public until an editor publishes it" in fuori.out
    assert "note:  Saved as a draft" in fuori.out


def test_save_anyway_tiene_una_bozza_anche_sotto_la_soglia(cli, api, tmp_path):
    api.risposte[("POST", "/v1/blog/posts")] = (
        201, {"dry_run": True, "seo": rapporto(50), "articolo": {"id": "1", "stato": "bozza", "lang": "en"}, "url": "u", "avvisi": []}, {},
    )
    assert cli.main(["post", _articolo(tmp_path, status="published", publish_at="2030-01-01T00:00:00Z"), "--save-anyway"]) == cli.EXIT_OK
    reale = json.loads([r for r in api.richieste if r["metodo"] == "POST"][-1]["corpo"])
    assert reale["stato"] == "bozza" and "pubblicato_il" not in reale


def test_dry_run_non_salva(cli, api, tmp_path):
    api.risposte[("POST", "/v1/blog/posts")] = (201, {"dry_run": True, "seo": rapporto(90), "avvisi": []}, {})
    assert cli.main(["post", _articolo(tmp_path), "--dry-run"]) == cli.EXIT_OK
    assert len([r for r in api.richieste if r["metodo"] == "POST"]) == 1


def test_la_copertina_si_carica_come_corpo_grezzo_e_il_suo_id_entra_nell_articolo(cli, api, tmp_path):
    immagine = tmp_path / "c.png"
    immagine.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
    api.risposte[("POST", "/v1/blog/media")] = (201, {"id": "0b1c2d3e-0000-4000-8000-000000000001", "larghezza": 1600, "altezza": 900, "byte": 40}, {})
    api.risposte[("POST", "/v1/blog/posts")] = (
        201, {"dry_run": True, "seo": rapporto(90), "articolo": {"id": "1", "stato": "bozza", "lang": "en"}, "url": "u", "avvisi": []}, {},
    )
    assert cli.main(["post", _articolo(tmp_path), "--cover", str(immagine)]) == cli.EXIT_OK
    carico = next(r for r in api.richieste if r["percorso"] == "/v1/blog/media")
    assert carico["tipo"] == "image/png" and carico["corpo"].startswith(b"\x89PNG")
    ultimo = json.loads([r for r in api.richieste if r["percorso"] == "/v1/blog/posts"][-1]["corpo"])
    assert ultimo["immagine_id"] == "0b1c2d3e-0000-4000-8000-000000000001"


def test_la_copertina_deve_essere_un_immagine(cli, api, tmp_path, capsys):
    (tmp_path / "c.gif").write_bytes(b"GIF89a")
    assert cli.main(["upload", str(tmp_path / "c.gif")]) == cli.EXIT_USAGE
    assert "PNG, JPEG or WebP" in capsys.readouterr().err
    assert api.richieste == []
