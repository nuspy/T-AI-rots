"""Reddit (v8.6): la configurazione coi segreti cifrati, la prova, il post a galleria a ogni pubblicazione, il
ripiego sul link, un post solo per articolo, l'intervallo, il limite di frequenza, «Riprova». Nessuna chiamata vera
a Reddit: un trasporto HTTP finto."""
from __future__ import annotations

import io
import json
import uuid
from datetime import timedelta
from urllib.parse import parse_qs

import httpx
import pytest
from sqlalchemy import select

from ..domain.base import utcnow
from ..domain.blog_models import MediaImage
from ..domain.integrazioni_models import ConfigReddit, PostReddit
from ..tarot import reddit
from .conftest import richiede_database

pytestmark = richiede_database


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


@pytest.fixture
def reddit_finto(monkeypatch):
    """Reddit finto. `stato` decide le risposte, `chiamate` registra (metodo, url, corpo, intestazioni)."""
    stato = {"token": 200, "submit_errori": [], "gallerie": True, "inviati": [], "upload": 201}
    chiamate: list = []

    def gestore(req: httpx.Request) -> httpx.Response:
        corpo = req.content.decode("utf-8", "replace") if req.content else ""
        chiamate.append((req.method, str(req.url), corpo, dict(req.headers)))
        ua = req.headers.get("user-agent", "")
        assert ua.startswith("web:chat.tarots.blog-publisher:v1.0 (by /u/"), ua
        host, percorso = req.url.host, req.url.path
        if host == "www.reddit.com" and percorso == "/api/v1/access_token":
            if stato["token"] == 401:
                return httpx.Response(401, json={"message": "Unauthorized"})
            dati = parse_qs(corpo)
            if dati.get("password") != ["segreta-password"]:
                return httpx.Response(200, json={"error": "invalid_grant"})
            return httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        if host == "reddit-uploaded-media.s3-accelerate.amazonaws.com":
            return httpx.Response(stato["upload"])
        assert host == "oauth.reddit.com" and req.headers["authorization"] == "bearer tok"
        if percorso == "/api/v1/me":
            return httpx.Response(200, json={"name": "tarotsbot", "total_karma": 12, "created_utc": utcnow().timestamp() - 86400 * 3})
        if percorso == "/r/tarotschat/about":
            return httpx.Response(200, json={"kind": "t5", "data": {
                "display_name": "tarotschat", "subreddit_type": "public", "submission_type": "any",
                "allow_galleries": stato["gallerie"], "subscribers": 120, "user_is_banned": False}})
        if percorso == "/r/inesistente/about":
            return httpx.Response(404, json={"error": 404})
        if percorso.endswith("/api/link_flair_v2"):
            return httpx.Response(200, json=[{"id": "flair-1", "text": "Article"}])
        if percorso == "/api/media/asset.json":
            n = sum(1 for c in chiamate if c[1].endswith("/api/media/asset.json"))
            return httpx.Response(200, json={
                "args": {"action": "//reddit-uploaded-media.s3-accelerate.amazonaws.com",
                         "fields": [{"name": "key", "value": f"k{n}"}, {"name": "acl", "value": "private"}]},
                "asset": {"asset_id": f"asset{n}"}})
        if percorso in ("/api/submit_gallery_post.json", "/api/submit"):
            if stato["submit_errori"]:
                return httpx.Response(200, json={"json": {"errors": [stato["submit_errori"].pop(0)], "data": {}}})
            n = len(stato["inviati"]) + 1
            dati = json.loads(corpo) if percorso.endswith(".json") else {k: v[0] for k, v in parse_qs(corpo).items()}
            stato["inviati"].append({"tipo": "galleria" if percorso.endswith(".json") else "link", "dati": dati})
            if percorso.endswith(".json"):
                return httpx.Response(200, json={"json": {"errors": [], "data": {"id": f"t3_g{n}", "url": f"https://www.reddit.com/gallery/g{n}"}}})
            return httpx.Response(200, json={"json": {"errors": [], "data": {"name": f"t3_l{n}", "id": f"l{n}",
                                                                             "url": f"https://www.reddit.com/r/tarotschat/comments/l{n}/x/"}}})
        if percorso == "/user/tarotsbot/submitted":
            figli = [{"data": {"title": i["dati"].get("title"), "subreddit": "tarotschat", "name": "t3_vecchio",
                               "permalink": "/r/tarotschat/comments/vecchio/x/"}} for i in stato["inviati"]]
            return httpx.Response(200, json={"data": {"children": figli}})
        return httpx.Response(404)

    monkeypatch.setattr(reddit, "_client", lambda: httpx.AsyncClient(transport=httpx.MockTransport(gestore)))

    async def niente(_secondi):
        return None

    monkeypatch.setattr(reddit, "_dormi", niente)
    return stato, chiamate


async def _configura(admin, **altro):
    corpo = {"client_id": "app-id", "client_secret": "secret-dell-app-1234", "utente": "tarotsbot",
             "password": "segreta-password", "subreddit": "r/tarotschat", "intervallo_minuti": 0, **altro}
    r = await admin.put("/admin/reddit", json=corpo)
    assert r.status_code == 200, r.text
    return r.json()


async def _accendi(admin, session, indietro: int = 5):
    r = await admin.put("/admin/reddit", json={"attivo": True})
    assert r.status_code == 200, r.text
    # `attivo_dal` è l'istante dell'accensione: gli articoli dei test escono subito dopo.
    riga = await session.get(ConfigReddit, 1)
    riga.attivo_dal = utcnow() - timedelta(seconds=indietro)
    await session.commit()


async def _immagine(session) -> uuid.UUID:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (24, 16), (120, 40, 160)).save(buf, "WEBP")
    img = MediaImage(uso="blog", webp=buf.getvalue(), larghezza=24, altezza=16)
    session.add(img)
    await session.commit()
    return img.id


async def _articolo(admin, titolo, **campi):
    corpo = {"titolo": titolo, "testo": "Un testo abbastanza lungo per fare da descrizione al post di Reddit.",
             "stato": "pubblicato", "lang": "en", **campi}
    r = await admin.post("/admin/blog/posts", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


async def _post_di(session, articolo_id):
    return (await session.execute(select(PostReddit).where(PostReddit.articolo_id == uuid.UUID(articolo_id)))).scalar_one_or_none()


def test_subreddit_e_user_agent():
    assert reddit.normalizza_subreddit("r/Tarot") == "Tarot"
    assert reddit.normalizza_subreddit("https://www.reddit.com/r/tarot/") == "tarot"
    assert reddit.normalizza_subreddit("u/tarotsbot") == "u_tarotsbot"
    assert reddit.normalizza_subreddit("https://www.reddit.com/user/tarotsbot") == "u_tarotsbot"
    assert reddit.user_agent("tarotsbot") == "web:chat.tarots.blog-publisher:v1.0 (by /u/tarotsbot)"


async def test_configurazione_segreti_cifrati_e_mai_restituiti(admin, session):
    dati = await _configura(admin)
    conf = dati["config"]
    assert conf["client_secret_impostato"] and conf["password_impostata"] and conf["client_secret_fine"] == "…1234"
    assert conf["subreddit"] == "tarotschat" and conf["attivo"] is False and conf["mancano"] == []
    testo = json.dumps(dati)
    assert "segreta-password" not in testo and "secret-dell-app-1234" not in testo
    riga = await session.get(ConfigReddit, 1)
    assert b"segreta" not in bytes(riga.password_cifrata)

    # Senza mandarli di nuovo, i segreti restano.
    conf = (await admin.put("/admin/reddit", json={"subreddit": "u/tarotsbot"})).json()["config"]
    assert conf["subreddit"] == "u_tarotsbot" and conf["password_impostata"]
    r = await admin.put("/admin/reddit", json={"subreddit": "r/nome con spazi"})
    assert r.status_code == 422


async def test_non_si_accende_senza_credenziali(admin):
    r = await admin.put("/admin/reddit", json={"attivo": True})
    assert r.status_code == 422 and "mancano" in r.json()["detail"]


async def test_prova_senza_pubblicare(admin, reddit_finto):
    stato, chiamate = reddit_finto
    await _configura(admin)
    esito = (await admin.post("/admin/reddit/prova")).json()["config"]["esito_prova"]
    assert esito["accesso"]["ok"] and "u/tarotsbot" in esito["accesso"]["messaggio"]
    assert "poco karma" in esito["accesso"]["messaggio"]
    assert esito["destinazione"]["ok"] and esito["destinazione"]["gallerie"] is True
    assert esito["destinazione"]["flair"] == [{"id": "flair-1", "testo": "Article"}]
    assert not any("/api/submit" in c[1] for c in chiamate)

    await admin.put("/admin/reddit", json={"subreddit": "inesistente"})
    esito = (await admin.post("/admin/reddit/prova")).json()["config"]["esito_prova"]
    assert esito["destinazione"]["ok"] is False and "non esiste" in esito["destinazione"]["messaggio"]

    stato["token"] = 401
    esito = (await admin.post("/admin/reddit/prova")).json()["config"]["esito_prova"]
    assert esito["accesso"]["ok"] is False and "client id o secret" in esito["accesso"]["messaggio"]

    stato["token"] = 200
    await admin.put("/admin/reddit", json={"password": "sbagliata"})
    esito = (await admin.post("/admin/reddit/prova")).json()["config"]["esito_prova"]
    assert "utente o password" in esito["accesso"]["messaggio"]


async def test_un_articolo_pubblicato_diventa_una_galleria(admin, session, reddit_finto):
    stato, chiamate = reddit_finto
    await _configura(admin, flair_id="flair-1")
    await admin.post("/admin/reddit/prova")
    await _accendi(admin, session)
    copertina, dentro = await _immagine(session), await _immagine(session)
    a = await _articolo(admin, "The Star in love readings", sottotitolo="Hope after the storm.",
                        immagine_id=str(copertina), immagine_alt="The Star card",
                        testo=f"Primo paragrafo abbastanza lungo da essere una descrizione.\n\n![Una stella](/blog/media/{dentro}.webp)\n\nFine.")

    post = await _post_di(session, a["id"])
    await session.refresh(post)
    assert post.stato == "pubblicato" and post.tipo == "galleria", post.errore
    assert post.url == "https://www.reddit.com/gallery/g1" and post.reddit_id == "t3_g1"
    inviato = stato["inviati"][0]["dati"]
    assert inviato["sr"] == "tarotschat" and inviato["title"] == "The Star in love readings" and inviato["flair_id"] == "flair-1"
    assert [v["media_id"] for v in inviato["items"]] == ["asset1", "asset2"]
    assert inviato["items"][0]["caption"] == "The Star card" and inviato["items"][1]["caption"] == "Una stella"
    atteso = f"http://localhost:3000/blog/{a['slug']}?utm_source=reddit&utm_medium=social&utm_campaign=blog"
    assert all(v["outbound_url"].endswith(f"/blog/{a['slug']}?utm_source=reddit&utm_medium=social&utm_campaign=blog") for v in inviato["items"])
    assert "Hope after the storm." in inviato["text"] and a["slug"] in inviato["text"]
    # le immagini sono andate su S3 come JPEG, coi campi del lease
    caricamenti = [c for c in chiamate if "s3-accelerate" in c[1]]
    assert len(caricamenti) == 2 and "image/jpeg" in caricamenti[0][2] and 'name="key"' in caricamenti[0][2]
    assert atteso.split("/blog/")[1] in inviato["items"][0]["outbound_url"]

    # Modificarlo o ripubblicarlo non fa un secondo post.
    r = await admin.patch(f"/admin/blog/posts/{a['id']}", json={"sottotitolo": "Nuovo"})
    assert r.status_code == 200
    await admin.post(f"/admin/blog/posts/{a['id']}/pubblica")
    assert len(stato["inviati"]) == 1

    elenco = (await admin.get("/admin/reddit")).json()["post"]
    assert elenco[0]["url"] == "https://www.reddit.com/gallery/g1" and elenco[0]["articolo"]["slug"] == a["slug"]


async def test_con_una_sola_immagine_si_pubblica_il_link(admin, session, reddit_finto):
    stato, _ = reddit_finto
    await _configura(admin)
    await _accendi(admin, session)
    a = await _articolo(admin, "Only a cover", immagine_id=str(await _immagine(session)))
    post = await _post_di(session, a["id"])
    await session.refresh(post)
    assert post.stato == "pubblicato" and post.tipo == "link"
    assert stato["inviati"][0]["tipo"] == "link" and stato["inviati"][0]["dati"]["resubmit"] == "false"
    assert stato["inviati"][0]["dati"]["kind"] == "link" and "utm_source=reddit" in stato["inviati"][0]["dati"]["url"]


async def test_se_il_caricamento_fallisce_ripiega_sul_link(admin, session, reddit_finto):
    stato, _ = reddit_finto
    stato["upload"] = 500
    await _configura(admin)
    await _accendi(admin, session)
    a = await _articolo(admin, "Two pictures", immagine_id=str(await _immagine(session)),
                        testo=f"Testo.\n\n![x](/blog/media/{await _immagine(session)}.webp)")
    post = await _post_di(session, a["id"])
    await session.refresh(post)
    assert post.stato == "pubblicato" and post.tipo == "link" and "Galleria non riuscita" in post.errore


async def test_cosa_non_va_su_reddit(admin, session, reddit_finto):
    stato, _ = reddit_finto
    await _configura(admin)
    vecchio = await _articolo(admin, "Before activation")  # uscito prima dell'accensione: mai
    await _accendi(admin, session, indietro=0)
    bozza = await _articolo(admin, "Draft", stato="bozza")
    italiano = await _articolo(admin, "In italiano", lang="it")
    nascosto = await _articolo(admin, "Noindex", noindex=True)
    programmato = await _articolo(admin, "Later", pubblicato_il=(utcnow() + timedelta(days=2)).isoformat())
    for a in (vecchio, bozza, italiano, nascosto, programmato):
        assert await _post_di(session, a["id"]) is None
    assert stato["inviati"] == []
    # A mano, dalla console, un articolo di prima si può portare comunque.
    r = await admin.post(f"/admin/reddit/articoli/{vecchio['id']}")
    assert r.status_code == 202, r.text
    assert (await _post_di(session, vecchio["id"])).stato == "pubblicato"
    assert (await admin.post(f"/admin/reddit/articoli/{bozza['id']}")).status_code == 409


async def test_intervallo_fra_un_post_e_l_altro(admin, session, reddit_finto):
    stato, _ = reddit_finto
    await _configura(admin, intervallo_minuti=60)
    await _accendi(admin, session)
    primo = await _articolo(admin, "First")
    secondo = await _articolo(admin, "Second")
    assert (await _post_di(session, primo["id"])).stato == "pubblicato"
    assert (await _post_di(session, secondo["id"])).stato == "in_coda"
    assert len(stato["inviati"]) == 1


async def test_limite_di_frequenza_rimanda_senza_errore(admin, session, reddit_finto):
    stato, _ = reddit_finto
    stato["submit_errori"] = [["RATELIMIT", "Looks like you've been doing that a lot. Take a break for 9 minutes before trying again.", "ratelimit"]]
    await _configura(admin)
    await _accendi(admin, session)
    a = await _articolo(admin, "Too fast")
    post = await _post_di(session, a["id"])
    await session.refresh(post)
    assert post.stato == "in_coda" and post.riprova_dopo > utcnow() + timedelta(minutes=9)
    # prima dell'attesa il giro non lo riprende
    await reddit.lavora(lambda: _Sessione(session))
    assert len(stato["inviati"]) == 0


class _Sessione:
    """La sessione del test come fabbrica per `lavora` (senza chiuderla)."""

    def __init__(self, s):
        self.s = s

    async def __aenter__(self):
        return self.s

    async def __aexit__(self, *a):
        return False


async def test_errore_e_riprova_senza_doppioni(admin, session, reddit_finto):
    stato, _ = reddit_finto
    stato["submit_errori"] = [["SUBMIT_VALIDATION_FLAIR_REQUIRED", "Your post must contain post flair.", "flair"]]
    await _configura(admin)
    await _accendi(admin, session)
    a = await _articolo(admin, "Needs flair")
    post = await _post_di(session, a["id"])
    await session.refresh(post)
    assert post.stato == "errore" and "flair" in post.errore

    r = await admin.post(f"/admin/reddit/post/{post.id}/riprova")
    assert r.status_code == 202, r.text
    await session.refresh(post)
    assert post.stato == "pubblicato" and post.tentativi == 2 and len(stato["inviati"]) == 1

    # Un tentativo «in corso» interrotto (processo morto) e poi riprovato: se su Reddit il post c'è già, non si rifà.
    post.stato, post.errore = "errore", "Esito incerto"
    await session.commit()
    await admin.post(f"/admin/reddit/post/{post.id}/riprova")
    await session.refresh(post)
    assert post.stato == "pubblicato" and post.url == "https://www.reddit.com/r/tarotschat/comments/vecchio/x/"
    assert len(stato["inviati"]) == 1
    assert (await admin.post(f"/admin/reddit/post/{post.id}/riprova")).status_code == 409


async def test_spento_non_fa_nulla(admin, session, reddit_finto):
    stato, chiamate = reddit_finto
    await _configura(admin)
    await _articolo(admin, "Off")
    assert chiamate == [] and stato["inviati"] == []
    assert (await reddit.lavora(lambda: _Sessione(session)))["stato"] == "spento"
    assert (await admin.post("/admin/reddit/invia")).status_code == 409


async def test_reddit_solo_admin(client):
    assert (await client.get("/admin/reddit")).status_code == 403
    assert (await client.put("/admin/reddit", json={})).status_code == 403
