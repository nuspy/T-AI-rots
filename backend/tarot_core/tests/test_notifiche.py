"""Le notifiche push (v9, Fase 5): segmenti in SQL, giro con i fusi e le ore di silenzio, idempotenza giornaliera,
410 → dispositivo disattivato, FCM e Web Push finti (il Web Push cifrato davvero e decifrato qui con la chiave del
«browser»), la console (conteggio in anteprima, «invia a me», segreti mai in chiaro, traduzione con il modello
finto), la disiscrizione con il token HMAC, il promemoria della prova, la carta del giorno sul giorno locale.

Nessuna chiamata vera: Google, FCM e i servizi Web Push rispondono da un trasporto finto."""
from __future__ import annotations

import base64
import json
import os
import uuid
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

import httpx
import pytest
from sqlalchemy import select

from ..auth.keycloak import Principal
from ..domain.base import utcnow
from ..domain.configurazioni_models import SegretoSistema
from ..domain.consent_models import UserConsent
from ..domain.models import DailyCard, User
from ..domain.notifiche_models import CampagnaNotifica, ConfigNotifiche, DispositivoNotifica, InvioNotifica
from ..domain.repositories import UserRepository
from ..notifiche import automatiche, fcm, invio, segmenti, webpush
from ..notifiche import config as conf
from ..notifiche.invio import Postino
from ..tarot import google
from .conftest import richiede_database

pytestmark = richiede_database

ROMA = ZoneInfo("Europe/Rome")
NEW_YORK = ZoneInfo("America/New_York")


def _b64(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).rstrip(b"=").decode()


def _b64d(testo: str) -> bytes:
    return base64.urlsafe_b64decode(testo + "=" * (-len(testo) % 4))


def _browser():
    """Una sottoscrizione Web Push come la crea un browser: la sua chiave privata resta qui, per decifrare."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    privata = ec.generate_private_key(ec.SECP256R1())
    p256dh = _b64(privata.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint))
    auth = os.urandom(16)
    return privata, p256dh, auth


def _service_account() -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    chiave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = chiave.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                               serialization.NoEncryption()).decode()
    return json.dumps({
        "type": "service_account", "project_id": "tarots-app", "private_key_id": "abcdef0123456789",
        "private_key": pem, "client_email": "fcm@tarots-app.iam.gserviceaccount.com", "client_id": "1",
        "token_uri": "https://oauth2.googleapis.com/token",
    })


class Servizi:
    """Google OAuth, FCM e i servizi Web Push, finti. Le risposte dei Web Push si scelgono per endpoint."""

    def __init__(self) -> None:
        self.richieste: List[httpx.Request] = []
        self.web_stato: Dict[str, int] = {}

    def gestore(self, request: httpx.Request) -> httpx.Response:
        self.richieste.append(request)
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "token-finto", "expires_in": 3600})
        if request.url.host == "fcm.googleapis.com":
            messaggio = json.loads(request.content)["message"]
            if str(messaggio.get("token", "")).startswith("morto"):
                return httpx.Response(404, json={"error": {"status": "NOT_FOUND", "message": "Requested entity was not found.",
                                                           "details": [{"errorCode": "UNREGISTERED"}]}})
            return httpx.Response(200, json={"name": "projects/tarots-app/messages/1"})
        return httpx.Response(self.web_stato.get(str(request.url), 201))

    def fcm(self) -> List[Dict[str, Any]]:
        return [json.loads(r.content)["message"] for r in self.richieste if r.url.host == "fcm.googleapis.com"]

    def web(self) -> List[httpx.Request]:
        return [r for r in self.richieste if r.url.host.endswith("push.invalid")]


@pytest.fixture
def servizi(monkeypatch):
    s = Servizi()
    finto = lambda: httpx.AsyncClient(transport=httpx.MockTransport(s.gestore))  # noqa: E731
    monkeypatch.setattr(google, "_client", finto)
    monkeypatch.setattr(fcm, "_client", finto)
    monkeypatch.setattr(webpush, "_client", finto)
    monkeypatch.setattr(google, "_TOKEN", {})

    async def niente(_secondi: float) -> None:
        return None

    monkeypatch.setattr(invio, "ATTESA", niente)
    return s


async def _persona(session, nome: str, **campi) -> User:
    utente = await UserRepository(session).ensure(Principal(subject=f"sub-{nome}", email=f"{nome}@example.com",
                                                             display_name=nome.title(), roles={"user"}))
    for k, v in campi.items():
        setattr(utente, k, v)
    await session.flush()
    return utente


def _web(utente: User, browser=None, *, nome: str = "a") -> DispositivoNotifica:
    _, p256dh, auth = browser or _browser()
    endpoint = f"https://web.push.invalid/{nome}-{uuid.uuid4().hex[:6]}"
    return DispositivoNotifica(user_id=utente.id, canale="webpush", piattaforma="web", endpoint=endpoint, p256dh=p256dh,
                               auth=_b64(auth), impronta=uuid.uuid4().hex, lingua=utente.locale, attivo=True)


def _fcm(utente: User, token: str, piattaforma: str = "android") -> DispositivoNotifica:
    return DispositivoNotifica(user_id=utente.id, canale="fcm", piattaforma=piattaforma, token=token,
                               impronta=uuid.uuid4().hex, lingua=utente.locale, attivo=True)


async def _marketing(session, utente: User) -> None:
    session.add(UserConsent(user_id=utente.id, tipo="marketing", valore="accettato", versione_informativa="t"))
    await session.flush()


def _alle(giorno: date, ora: time, fuso: ZoneInfo) -> datetime:
    return datetime.combine(giorno, ora, tzinfo=fuso).astimezone(ZoneInfo("UTC"))


# ---- segmenti ------------------------------------------------------------------------------------------------------


async def test_segmenti_in_sql_e_promozioni_solo_con_il_consenso(session):
    it = await _persona(session, "anna", locale="it", posizione_paese="IT", birth_date=date(1990, 5, 1))
    en = await _persona(session, "bob", locale="en-GB", posizione_paese="GB", birth_date=date(2001, 1, 1))
    senza = await _persona(session, "carla", locale="it", posizione_paese="IT")
    chiuso = await _persona(session, "dario", locale="it", posizione_paese="IT", deleted_at=utcnow())
    for u in (it, en, senza, chiuso):
        session.add(_web(u))
    await _marketing(session, it)
    await _marketing(session, en)
    await session.flush()

    async def ids(filtro: Dict[str, Any], tipo: str = "servizio") -> set:
        q = segmenti.destinatari(segmenti.Filtro.model_validate(filtro), tipo)
        return set((await session.execute(q)).scalars())

    assert await ids({"lingue": ["it"]}) == {it.id, senza.id}            # chi ha chiuso l'account non c'è mai
    assert await ids({"lingue": ["en"]}) == {en.id}                       # «en-GB» conta come inglese
    assert await ids({"paesi": ["gb"]}) == {en.id}
    assert await ids({"fasce_eta": ["35-44"]}) == {it.id}
    assert await ids({"fasce_eta": ["nd"]}) == {senza.id}
    assert await ids({"lingue": ["it"]}, "promozione") == {it.id}         # senza consenso «marketing» niente promozioni
    assert await ids({"piattaforme": ["android"]}) == set()
    assert await ids({"crediti_max": 0}) >= {it.id}

    conta = await segmenti.conta(session, segmenti.Filtro(lingue=["it"]), "promozione")
    assert (conta["corrispondono"], conta["senza_consenso"], conta["destinatari"]) == (2, 1, 1)
    assert conta["per_piattaforma"]["web"] == 1

    # Il genere e i dati dell'art. 9 non sono filtri: un campo sconosciuto è un errore, non un campo ignorato.
    for vietato in ({"genere": ["donna"]}, {"gender": "uomo"}, {"is_trans": True}):
        with pytest.raises(ValueError):
            segmenti.Filtro.model_validate(vietato)


# ---- il giro: fusi, silenzio, idempotenza, 410 -----------------------------------------------------------------------


async def test_carta_del_giorno_all_ora_locale_fuori_dal_silenzio_una_volta_al_giorno(session, servizi):
    domani = (utcnow() + timedelta(days=1)).date()
    adesso = _alle(domani, time(8, 45), ROMA)
    roma = await _persona(session, "romana", locale="it", fuso_orario="Europe/Rome", created_at=adesso - timedelta(days=30))
    ny = await _persona(session, "newyorkese", locale="en", fuso_orario="America/New_York",
                        created_at=adesso - timedelta(days=30))
    browser = _browser()
    session.add_all([_web(roma, browser, nome="roma"), _web(ny, nome="ny")])
    await session.commit()

    from ..tools.notifiche import giro

    conti = await giro(session, adesso=adesso)
    assert conti.get("carta_giorno:inviato") == 1 and conti.get("silenzio") == 1   # a New York sono le 2:45
    invii = (await session.execute(select(InvioNotifica))).scalars().all()
    assert [(i.user_id, i.tipo, i.giorno, i.stato) for i in invii] == [(roma.id, "carta_giorno", domani, "inviato")]

    # Il messaggio è cifrato davvero per quel browser: lo si decifra con la sua chiave privata.
    import http_ece

    richiesta = servizi.web()[0]
    assert richiesta.headers["content-encoding"] == "aes128gcm" and richiesta.headers["authorization"].startswith("vapid t=")
    dati = json.loads(http_ece.decrypt(richiesta.content, private_key=browser[0], auth_secret=browser[2], version="aes128gcm"))
    assert dati["titolo"] == "La tua carta del giorno" and dati["link"] == "/daily-card" and dati["invio"] == str(invii[0].id)

    # Lo stesso giro un quarto d'ora dopo non rimanda niente (idempotenza del giorno locale).
    conti = await giro(session, adesso=adesso + timedelta(minutes=15))
    assert not any(k.startswith("carta_giorno:inviato") for k in conti)
    assert len(servizi.web()) == 1

    # Alle 8:45 di New York tocca a New York; Roma è già servita.
    conti = await giro(session, adesso=_alle(domani, time(8, 45), NEW_YORK))
    assert conti.get("carta_giorno:inviato") == 1
    assert {i.user_id for i in (await session.execute(select(InvioNotifica))).scalars()} == {roma.id, ny.id}

    # Chi ha già aperto la carta oggi non riceve il promemoria.
    dopodomani = domani + timedelta(days=1)
    session.add(DailyCard(user_id=roma.id, giorno=dopodomani, card_id="maj-00", created_at=utcnow()))
    await session.commit()
    conti = await giro(session, adesso=_alle(dopodomani, time(9, 0), ROMA))
    assert not conti.get("carta_giorno:inviato")


async def test_410_disattiva_il_browser_e_404_unregistered_il_telefono(session, servizi):
    domani = (utcnow() + timedelta(days=1)).date()
    adesso = _alle(domani, time(9, 0), ROMA)
    utente = await _persona(session, "elena", locale="it", fuso_orario="Europe/Rome", created_at=adesso - timedelta(days=30))
    web = _web(utente, nome="scaduto")
    telefono = _fcm(utente, "morto-" + "x" * 30)
    session.add_all([web, telefono])
    cfg = await conf.config(session)
    conf.salva_firebase(cfg, _service_account(), autore_id=None)
    await session.commit()
    servizi.web_stato[web.endpoint] = 410

    postino = await Postino.prepara(session, adesso=adesso)
    conti = await automatiche.giro(session, postino)
    assert conti.get("carta_giorno:token_invalido") == 1
    await session.refresh(web)
    await session.refresh(telefono)
    assert (web.attivo, telefono.attivo) == (False, False) and web.disattivato_il is not None
    assert "UNREGISTERED" in (telefono.ultimo_errore or "")
    # Disattivati, non si riprovano: il giro dopo non trova nessuno da raggiungere.
    n = len(servizi.richieste)
    await automatiche.giro(session, await Postino.prepara(session, adesso=adesso + timedelta(minutes=15)))
    assert len(servizi.richieste) == n


async def test_fcm_finto_messaggio_nella_lingua_del_dispositivo(session, servizi):
    domani = (utcnow() + timedelta(days=1)).date()
    utente = await _persona(session, "fiona", locale="hu", fuso_orario="Europe/Budapest",
                            created_at=utcnow() - timedelta(days=30))
    session.add(_fcm(utente, "token-buono-" + "y" * 30, "ios"))
    conf.salva_firebase(await conf.config(session), _service_account(), autore_id=None)
    await session.commit()

    await automatiche.giro(session, await Postino.prepara(session, adesso=_alle(domani, time(8, 31), ZoneInfo("Europe/Budapest"))))
    [messaggio] = servizi.fcm()
    assert messaggio["notification"]["title"] == "A napi kártyád"
    assert messaggio["data"]["link"] == "/daily-card" and messaggio["apns"]["payload"]["aps"]["sound"] == "default"
    oauth = [r for r in servizi.richieste if r.url.host == "oauth2.googleapis.com"]
    from urllib.parse import parse_qs

    asserzione = parse_qs(oauth[0].content.decode())["assertion"][0]
    assert json.loads(_b64d(asserzione.split(".")[1]))["scope"] == conf.SCOPE_FCM
    assert servizi.richieste[-1].headers["authorization"] == "Bearer token-finto"


async def test_altre_automatiche_benvenuto_serie_rinnovo(session, servizi, catalogo):
    from ..domain.billing_models import Plan, Subscription

    domani = (utcnow() + timedelta(days=1)).date()
    sera = _alle(domani, time(20, 30), ROMA)
    utente = await _persona(session, "gino", locale="it", fuso_orario="Europe/Rome", created_at=sera - timedelta(days=2))
    session.add(_web(utente))
    for giorni in (1, 2, 3, 4):
        session.add(DailyCard(user_id=utente.id, giorno=domani - timedelta(days=giorni), card_id="maj-01", created_at=utcnow()))
    piano = (await session.execute(select(Plan).where(Plan.slug == "mensile-oro"))).scalar_one()
    session.add(Subscription(user_id=utente.id, plan_id=piano.id, status="in_sospeso", period_start=sera - timedelta(days=31),
                             period_end=sera - timedelta(days=1), provider="mock", pagamento_fallito_il=sera - timedelta(hours=5)))
    await session.commit()

    conti = await automatiche.giro(session, await Postino.prepara(session, adesso=sera))
    assert conti.get("serie_in_pericolo:inviato") == 1
    assert conti.get("rinnovo_fallito:inviato") == 1
    assert not conti.get("benvenuto:inviato")                    # alle 20:30 la finestra del benvenuto (11:00) è chiusa
    conti = await automatiche.giro(session, await Postino.prepara(session, adesso=_alle(domani, time(11, 30), ROMA)))
    assert conti.get("benvenuto:inviato") == 1
    # Il rinnovo fallito non si ripete il giorno dopo per lo stesso fallimento.
    conti = await automatiche.giro(session, await Postino.prepara(session, adesso=sera + timedelta(days=1)))
    assert not conti.get("rinnovo_fallito:inviato")


# ---- console ---------------------------------------------------------------------------------------------------------


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


async def test_console_segreti_mai_in_chiaro_e_prova_firebase(admin, session, servizi):
    assert (await admin.get("/admin/notifiche")).status_code == 200
    sa = _service_account()
    r = await admin.put("/admin/notifiche/firebase", json={"service_account_json": sa})
    assert r.status_code == 200, r.text
    corpo = r.text
    assert "PRIVATE KEY" not in corpo and "private_key" not in corpo
    assert r.json()["firebase"]["progetto"] == "tarots-app" and r.json()["firebase"]["presente"]
    # VAPID: la pubblica si vede, la privata no; nel database sono cifrate.
    assert r.json()["vapid"]["pubblica"] and "BEGIN" not in corpo
    riga = await session.get(ConfigNotifiche, 1)
    assert b"PRIVATE KEY" not in (riga.firebase_cifrato or b"")
    segreto = await session.get(SegretoSistema, "vapid_privata")
    assert segreto is not None and b"PRIVATE KEY" not in segreto.valore_cifrato

    r = await admin.post("/admin/notifiche/firebase/prova")
    assert r.json()["firebase"]["esito"]["ok"] is True
    assert servizi.fcm()[0]["topic"] == "prova-console"
    assert json.loads(servizi.richieste[-1].content)["validate_only"] is True

    r = await admin.put("/admin/notifiche/firebase", json={"service_account_json": '{"type": "authorized_user"}'})
    assert r.status_code == 422
    # Il registro «Account» ora punta qui.
    from ..servizi_esterni.registro import PER_ID

    assert PER_ID["firebase"].sezione == "/notifiche/impostazioni" and PER_ID["vapid"].dove_si_imposta == "automatico"


async def test_console_conteggio_invia_a_me_e_programmazione(admin, client, session, servizi, principal_admin):
    lettore = await _persona(session, "ines", locale="it", posizione_paese="IT")
    session.add(_web(lettore))
    await _marketing(session, lettore)
    await session.commit()

    r = await admin.post("/admin/notifiche/conteggio", json={"tipo": "promozione", "filtro": {"lingue": ["it"]}})
    assert r.status_code == 200, r.text
    assert r.json()["destinatari"] == 1
    assert (await admin.post("/admin/notifiche/conteggio", json={"tipo": "servizio", "filtro": {"genere": "donna"}})).status_code == 422

    nuova = {"nome": "Luna piena", "tipo": "promozione", "lingua_base": "it", "deep_link": "/pricing",
             "testi": {"it": {"titolo": "Luna piena", "corpo": "Stasera una stesa speciale"}}, "filtro": {"lingue": ["it"]}}
    assert (await admin.post("/admin/notifiche/campagne", json={**nuova, "deep_link": "//altro.example"})).status_code == 422
    r = await admin.post("/admin/notifiche/campagne", json=nuova)
    assert r.status_code == 201, r.text
    cid = r.json()["id"]

    # «Invia a me»: senza dispositivi lo dice; con il browser dell'amministratore registrato, parte.
    r = await admin.post(f"/admin/notifiche/campagne/{cid}/invia-a-me")
    assert r.json()["esito"] == "nessun_dispositivo"
    browser = _browser()
    r = await admin.post("/me/dispositivi", json={"canale": "webpush", "piattaforma": "web",
                                                  "endpoint": "https://web.push.invalid/admin", "p256dh": browser[1],
                                                  "auth": _b64(browser[2]), "fuso_orario": "Europe/Rome", "lingua": "it"})
    assert r.status_code == 200, r.text
    r = await admin.post(f"/admin/notifiche/campagne/{cid}/invia-a-me")
    assert r.json()["esito"] == "inviato", r.text
    import http_ece

    dati = json.loads(http_ece.decrypt(servizi.web()[-1].content, private_key=browser[0], auth_secret=browser[2]))
    assert dati["titolo"] == "Luna piena" and dati["azioni"][0]["azione"] == "disiscrivi"

    # Programmata adesso: il giro la manda (fuori dal silenzio) e la chiude.
    r = await admin.post(f"/admin/notifiche/campagne/{cid}/programma", json={})
    assert r.json()["stato"] == "programmata"
    from ..tools.notifiche import giro

    mezzogiorno = _alle((utcnow() + timedelta(days=1)).date(), time(12, 0), ROMA)
    await giro(session, adesso=mezzogiorno)
    c = await session.get(CampagnaNotifica, cid)
    await session.refresh(c)
    assert c.stato == "inviata" and (c.destinatari, c.inviati) == (1, 1)
    assert (await admin.post(f"/admin/notifiche/campagne/{cid}/annulla")).status_code == 409

    # Il tetto delle promozioni: con tetto 1 una seconda promozione nella settimana si salta.
    await admin.put("/admin/notifiche/impostazioni", json={"tetto_promozioni_settimana": 1})
    r = await admin.post("/admin/notifiche/campagne", json={**nuova, "nome": "Seconda"})
    seconda = r.json()["id"]
    await admin.post(f"/admin/notifiche/campagne/{seconda}/programma", json={})
    await giro(session, adesso=mezzogiorno + timedelta(hours=1))
    c2 = await session.get(CampagnaNotifica, seconda)
    await session.refresh(c2)
    assert c2.stato == "inviata" and c2.saltati == 1 and c2.inviati == 0

    st = (await admin.get("/admin/notifiche/statistiche")).json()
    assert st["totali"]["consegnati"] >= 2


async def test_traduzione_con_il_modello_finto(admin):
    r = await admin.post("/admin/notifiche/traduci", json={"base": "it", "titolo": "Ciao {n}", "corpo": "Prova",
                                                           "lingue": ["en", "ru"]})
    assert r.status_code == 200, r.text
    assert r.json()["testi"]["ru"] == {"titolo": "[ru] Ciao {n}", "corpo": "[ru] Prova"}


async def test_automatiche_dalla_console(admin, session):
    r = await admin.put("/admin/notifiche/automatiche/crediti_in_scadenza",
                        json={"attiva": True, "testi": {"it": {"titolo": "Crediti", "corpo": "Scadono {data}"}}})
    assert r.status_code == 200, r.text
    voce = next(a for a in r.json()["automatiche"] if a["tipo"] == "crediti_in_scadenza")
    assert voce["attiva"] and voce["testi"]["it"]["titolo"] == "Crediti" and voce["testi"]["en"]["titolo"]
    assert (await admin.put("/admin/notifiche/automatiche/inesistente", json={"attiva": True})).status_code == 404


async def test_solo_l_amministratore(client):
    assert (await client.get("/admin/notifiche")).status_code == 403
    assert (await client.post("/admin/notifiche/conteggio", json={"tipo": "servizio"})).status_code == 403


# ---- dal lato di chi riceve ---------------------------------------------------------------------------------------


async def test_dispositivi_preferenze_vapid_e_apertura(client, session, servizi):
    pubblica = (await client.get("/notifiche/vapid")).json()["chiave"]
    assert len(_b64d(pubblica)) == 65

    browser = _browser()
    iscrizione = {"canale": "webpush", "piattaforma": "web", "endpoint": "https://web.push.invalid/io",
                  "p256dh": browser[1], "auth": _b64(browser[2]), "fuso_orario": "America/New_York", "lingua": "en"}
    assert (await client.post("/me/dispositivi", json={**iscrizione, "piattaforma": "android"})).status_code == 422
    r = await client.post("/me/dispositivi", json=iscrizione)
    assert r.status_code == 200, r.text
    assert (await client.post("/me/dispositivi", json=iscrizione)).json()["id"] == r.json()["id"]   # una riga sola

    p = (await client.get("/me/preferenze-notifica")).json()
    assert (p["carta_giorno"], p["ora_carta"], p["silenzio_dal"], p["fuso_orario"]) == (True, "08:30", "22:00", "America/New_York")
    p = (await client.put("/me/preferenze-notifica", json={"ora_carta": "07:15", "silenzio": False})).json()
    assert (p["ora_carta"], p["silenzio"]) == ("07:15", False)
    assert (await client.put("/me/fuso-orario", json={"fuso_orario": "Marte/Olympus"})).status_code == 422

    # L'apertura vale solo con la firma giusta.
    utente = (await session.execute(select(User).where(User.keycloak_sub == "sub-utente-1"))).scalar_one()
    postino = await Postino.prepara(session)
    r2 = await postino.manda(utente, "prova", {"en": {"titolo": "T", "corpo": "C"}}, "/")
    await session.commit()
    firma = conf.firma(postino.chiave, f"aperta:{r2.invio.id}")
    assert (await client.post("/notifiche/aperta", json={"invio": str(r2.invio.id), "firma": "x" * 24})).status_code == 403
    assert (await client.post("/notifiche/aperta", json={"invio": str(r2.invio.id), "firma": firma})).status_code == 204
    await session.refresh(r2.invio)
    assert r2.invio.stato == "aperto"

    assert (await client.request("DELETE", "/me/dispositivi", json={"canale": "webpush",
                                                                    "endpoint": iscrizione["endpoint"]})).status_code == 204
    assert (await client.get("/me/preferenze-notifica")).json()["dispositivi"] == []


async def test_disiscrizione_in_un_clic_con_token_hmac(client, session):
    utente = await _persona(session, "luca", locale="it")
    await _marketing(session, utente)
    chiave = await conf.chiave_firma(session)
    await session.commit()
    token = conf.token_disiscrizione(chiave, utente.id, "promozioni")

    falso = token[:-3] + ("AAA" if not token.endswith("AAA") else "BBB")
    assert (await client.get(f"/notifiche/disiscrivi?t={falso}")).status_code == 400
    altro = f"{utente.id + 1}.promozioni.{token.split('.')[2]}"
    assert (await client.get(f"/notifiche/disiscrivi?t={altro}")).status_code == 400

    r = await client.get(f"/notifiche/disiscrivi?t={token}")
    assert r.status_code == 200 and "Non riceverai più promozioni" in r.text
    valore = (await session.execute(select(UserConsent.valore).where(
        UserConsent.user_id == utente.id, UserConsent.tipo == "marketing"))).scalar_one()
    assert valore == "rifiutato"


# ---- promemoria della prova e carta del giorno locale -----------------------------------------------------------------


async def test_promemoria_della_prova_anche_come_notifica(session, servizi, catalogo, monkeypatch):
    from ..billing import abbonamenti as gestione
    from ..domain.billing_models import Plan, Subscription

    utente = await _persona(session, "marta", locale="it", fuso_orario="UTC")
    session.add(_web(utente))
    oro = (await session.execute(select(Plan).where(Plan.slug == "mensile-oro"))).scalar_one()
    adesso = utcnow()
    session.add(Subscription(user_id=utente.id, plan_id=oro.id, status="in_prova", prova=True, annuale=True,
                             period_start=adesso - timedelta(days=12, hours=12), period_end=adesso + timedelta(days=1, hours=12),
                             provider="mock", listino=19900, importo_periodo=0))
    await session.commit()
    # Fuori dalle ore di silenzio comunque sia l'orologio di chi esegue la prova.
    riga = await conf.config(session)
    riga.silenzio_dal = riga.silenzio_al = None
    await session.commit()

    assert await gestione.giro_promemoria_prova(session) == 1
    await session.commit()
    invii = (await session.execute(select(InvioNotifica).where(InvioNotifica.user_id == utente.id))).scalars().all()
    assert [(i.tipo, i.stato) for i in invii] == [("promemoria_prova", "inviato")]
    # Il giro delle notifiche non lo ripete.
    postino = await Postino.prepara(session)
    conti = await automatiche.giro(session, postino)
    assert not conti.get("promemoria_prova:inviato")


async def test_carta_del_giorno_sul_giorno_locale_senza_spezzare_la_serie(client, session):
    kiritimati = ZoneInfo("Pacific/Kiritimati")   # UTC+14: spesso è già «domani» rispetto a Roma
    oggi_k = datetime.now(kiritimati).date()
    r = await client.get("/me/daily-card", params={"fuso": "Pacific/Kiritimati"})
    assert r.status_code == 200, r.text
    assert r.json()["giorno"] == oggi_k.isoformat()
    utente = (await session.execute(select(User).where(User.keycloak_sub == "sub-utente-1"))).scalar_one()
    await session.refresh(utente)
    assert utente.fuso_orario == "Pacific/Kiritimati"

    # La serie: i giorni prima, nel fuso locale, continuano a contare.
    for giorni in (1, 2):
        session.add(DailyCard(user_id=utente.id, giorno=oggi_k - timedelta(days=giorni), card_id="maj-02", created_at=utcnow()))
    await session.commit()
    assert (await client.get("/me/daily-card")).json()["serie"] == 3

    # Tornato a ovest (Honolulu, UTC−10: lì è «ieri»), la carta di «domani» già presa non spezza la serie.
    r = await client.get("/me/daily-card", params={"fuso": "Pacific/Honolulu"})
    oggi_h = datetime.now(ZoneInfo("Pacific/Honolulu")).date()
    assert r.json()["giorno"] == oggi_h.isoformat()
    assert r.json()["serie"] >= 3
