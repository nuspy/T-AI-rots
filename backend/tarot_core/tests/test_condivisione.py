"""La condivisione delle letture: regole pure, accertamento, premi, immagini, iscrizioni.

Le regole pure (testo, anonimizzazione, PNG, bot) non hanno bisogno del database;
il resto attraversa l'API con un database vero. Nei test chi visita si distingue da
chi condivide con l'intestazione `X-Real-IP` (altrimenti tutte le richieste
hanno lo stesso indirizzo) e con lo `User-Agent` di un browser (quello di httpx è
di uno strumento, e non conterebbe).
"""
from __future__ import annotations

import dataclasses
import io
import struct
import zlib
from datetime import timedelta

import pytest
from sqlalchemy import select

from tarot_core.domain.base import utcnow
from tarot_core.domain.models import Reading, User
from tarot_core.tarot import condivisione as regole

from .conftest import richiede_database
from .test_flusso import _accredita, _lettura_completa

# ---- gli strumenti --------------------------------------------------------------------------------


def _immagine(larghezza: int = 800, altezza: int = 600, formato: str = "PNG", **salva) -> bytes:
    """Un'immagine di prova con un po' di dettaglio (sfondo sfumato, forme, testo)."""
    from PIL import Image, ImageDraw

    img = Image.linear_gradient("L").resize((larghezza, altezza)).convert("RGB")
    disegno = ImageDraw.Draw(img)
    for i in range(0, larghezza, 40):
        disegno.rectangle([i, altezza // 3, i + 24, altezza // 2], outline=(216, 180, 90), width=2)
    disegno.text((larghezza // 8, altezza // 8), "T-AI-rots", fill=(241, 214, 142))
    uscita = io.BytesIO()
    img.save(uscita, format=formato, **salva)
    return uscita.getvalue()


def _blocco(tipo: bytes, corpo: bytes) -> bytes:
    return struct.pack(">I", len(corpo)) + tipo + corpo + struct.pack(">I", zlib.crc32(tipo + corpo) & 0xFFFFFFFF)


def _con_blocco_di_testo(png: bytes, testo: bytes) -> bytes:
    """Lo stesso PNG con un blocco `tEXt` prima dei dati: dove finiscono i metadati."""
    fine_intestazione = 8 + 12 + 13
    return png[:fine_intestazione] + _blocco(b"tEXt", b"Comment\x00" + testo) + png[fine_intestazione:]


def _webp(immagine: bytes):
    from PIL import Image

    return Image.open(io.BytesIO(immagine))


BROWSER = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile Safari/604.1"


def _chi(ip: str, *, user_agent: str = BROWSER) -> dict:
    return {"x-real-ip": ip, "user-agent": user_agent}


PROPRIETARIO = ("proprietario-abcdef-0001", "10.0.0.1")
AMICO = ("amico-di-prova-abcdef-02", "10.0.0.2")


# ---- le regole pure -------------------------------------------------------------------------------


def test_il_testo_personalizzato_e_una_riga_pulita():
    assert regole.pulisci_testo("  Ciao\n\ta   tutti\x00\x07  ") == "Ciao a tutti"
    assert regole.pulisci_testo(None) == "" and regole.pulisci_testo("   ") == ""
    assert len(regole.pulisci_testo("x" * 500)) == regole.LUNGHEZZA_TESTO
    assert regole.pulisci_testo("✨ Le carte parlano ✨") == "✨ Le carte parlano ✨"


def test_l_anonimizzazione_sostituisce_il_nome_intero_e_non_le_parole_che_lo_contengono():
    frase = "qualcuno di speciale"
    assert regole.anonimizza("Marco e Sara: Marcotti no", "Marco", frase) == f"{frase} e Sara: Marcotti no"
    assert regole.anonimizza("MARCO?", "marco", frase) == f"{frase}?"
    assert regole.anonimizza("Con Anna Maria", "Anna Maria", frase) == f"Con {frase}"
    assert regole.anonimizza("Con Maria e Anna", "Anna Maria", frase) == f"Con {frase} e {frase}"
    assert regole.anonimizza(None, "Marco", frase) is None
    assert regole.anonimizza("Marco", None, frase) == "Marco" and regole.anonimizza("Marco", " ", frase) == "Marco"


def test_in_ungherese_le_desinenze_si_attaccano_al_nome():
    assert regole.anonimizza("Marcóval jó", "Marcó", "valaki különleges", lang="hu") == "valaki különleges jó"
    # Un nome breve non si estende: toccherebbe parole che iniziano allo stesso modo.
    assert regole.anonimizza("Alma", "Al", "x", lang="hu") == "Alma"


@pytest.mark.parametrize("ua, bot", [
    (BROWSER, False),
    ("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/126.0 Safari/537.36", False),
    ("facebookexternalhit/1.1", True),
    ("Twitterbot/1.0", True),
    ("WhatsApp/2.23", True),
    ("Mozilla/5.0 (compatible; Googlebot/2.1)", True),
    ("python-httpx/0.27", True),
    ("curl/8.0", True),
    ("", True),
    (None, True),
])
def test_un_crawler_non_e_un_visitatore(ua, bot):
    assert regole.e_un_bot(ua) is bot


def test_l_impronta_e_stabile_e_dipende_dal_sale():
    a = regole.anonimo("10.0.0.1", "sale-1")
    assert a == regole.anonimo("10.0.0.1", "sale-1") and a != regole.anonimo("10.0.0.1", "sale-2")
    assert a != regole.anonimo("10.0.0.2", "sale-1") and "10.0.0.1" not in a


@pytest.mark.parametrize("formato", ["PNG", "WEBP", "JPEG"])
@pytest.mark.parametrize("misura", [(800, 600), (400, 300)])
def test_un_immagine_valida_diventa_un_webp_400x300(formato, misura):
    webp = regole.prepara_immagine(_immagine(*misura, formato=formato))
    img = _webp(webp)
    assert img.format == "WEBP" and img.size == (400, 300)


def test_l_immagine_e_molto_compressa():
    """Poche decine di KB: pesa poco nel database, nel link e nelle anteprime."""
    webp = regole.prepara_immagine(_immagine(800, 600))
    assert len(webp) < 30_000, len(webp)


def test_i_metadati_e_i_dati_nascosti_non_passano():
    sporco = _con_blocco_di_testo(_immagine(800, 600), b"dati nascosti")
    assert b"dati nascosti" in sporco
    webp = regole.prepara_immagine(sporco)
    assert b"dati nascosti" not in webp
    img = _webp(webp)
    assert not img.info.get("exif") and not img.info.get("icc_profile") and not img.info.get("xmp")
    # Riscrivere l'uscita non aggiunge niente: la misura è già quella finale.
    assert regole.prepara_immagine(webp)


@pytest.mark.parametrize("dati, motivo", [
    pytest.param(b"", "vuota", id="vuoto"),
    pytest.param(b"GIF89a" + b"\x00" * 30, "non è un'immagine", id="intestazione-gif-rotta"),
    pytest.param(b"<html><script>alert(1)</script></html>", "non è un'immagine", id="html"),
    pytest.param(_immagine(800, 600, "GIF"), "formato", id="gif"),
    pytest.param(_immagine(1080, 1350), "dimensioni", id="1080x1350"),
    pytest.param(_immagine(1200, 630), "dimensioni", id="1200x630"),
    pytest.param(_immagine(400, 400), "dimensioni", id="quadrata"),
    pytest.param(_immagine(800, 600)[:-200], "danneggiata", id="troncata"),
    pytest.param(b"x" * (regole.MAX_CARICO + 1), "troppo grande", id="troppo-grande"),
])
def test_un_file_sbagliato_si_rifiuta(dati, motivo):
    with pytest.raises(ValueError, match=motivo):
        regole.prepara_immagine(dati)


def test_un_file_che_dichiara_una_misura_enorme_non_arriva_al_decodificatore():
    """Una «bomba di decompressione»: un PNG minuscolo che dichiara 60000×60000 pixel."""
    intestazione = struct.pack(">IIBBBBB", 60000, 60000, 8, 2, 0, 0, 0)
    bomba = b"\x89PNG\r\n\x1a\n" + _blocco(b"IHDR", intestazione) + _blocco(b"IEND", b"")
    # Pillow stesso rifiuta l'intestazione (`DecompressionBombError`); una misura più
    # piccola ma non ammessa la ferma il controllo delle dimensioni. In nessun caso si decodifica.
    with pytest.raises(ValueError, match="immagine valida|dimensioni"):
        regole.prepara_immagine(bomba)


def test_il_progresso_conta_i_prossimi_cinque():
    assert regole.progresso(0, 0)["prossimo_tra"] == 5
    assert regole.progresso(4, 0)["prossimo_tra"] == 1
    assert regole.progresso(5, 1)["prossimo_tra"] == 5
    p = regole.progresso(7, 1, 3)
    assert p == {"verificate": 7, "premi": 1, "prossimo_tra": 3, "iscrizioni": 3, "soglia": 5, "crediti_iscrizione": 5}


def _richiesta(**intestazioni):
    from starlette.requests import Request

    scope = {
        "type": "http", "method": "GET", "path": "/", "query_string": b"",
        "headers": [(k.replace("_", "-").encode(), v.encode()) for k, v in intestazioni.items()],
        "client": ("172.16.0.9", 5000),
    }
    return Request(scope)


def test_l_indirizzo_e_quello_che_scrive_il_proxy_non_quello_che_scrive_il_client():
    from tarot_core.api.routers.condivisione import _indirizzo

    # NPM sovrascrive X-Real-IP: è la fonte più fidata.
    assert _indirizzo(_richiesta(x_real_ip="203.0.113.7", x_forwarded_for="1.2.3.4, 203.0.113.7")) == "203.0.113.7"
    # Senza, conta l'ultimo indirizzo di X-Forwarded-For (aggiunto dal proxy più vicino),
    # non il primo: chi chiama può scrivere quello.
    assert _indirizzo(_richiesta(x_forwarded_for="6.6.6.6, 203.0.113.7")) == "203.0.113.7"
    assert _indirizzo(_richiesta()) == "172.16.0.9"


# ---- l'API ------------------------------------------------------------------------------------------


async def _saldo(client) -> int:
    return (await client.get("/me/billing")).json()["saldo"]


async def _condivisa(client, session, *, testo=None, spread="tre-carte", carte=3, extra=None):
    """Una lettura conclusa e pubblicata: `(id, token)`."""
    prima = {x["id"] for x in (await client.get("/me/readings")).json()["letture"]}
    await _lettura_completa(client, spread, carte, extra=extra)
    # Nei test le letture nascono nella stessa transazione, con lo stesso `now()`:
    # l'ordine dell'elenco non dice quale sia l'ultima. Si guarda cosa è comparso.
    (rid,) = {x["id"] for x in (await client.get("/me/readings")).json()["letture"]} - prima
    corpo = {"attiva": True} if testo is None else {"attiva": True, "testo": testo}
    r = await client.post(f"/me/readings/{rid}/share", json=corpo)
    assert r.status_code == 200, r.text
    return rid, r.json()["share_token"]


async def _clic(client, rid, chi=PROPRIETARIO, canale="x"):
    visitor, ip = chi
    r = await client.post(
        f"/me/readings/{rid}/share-click", json={"canale": canale, "visitor": visitor}, headers=_chi(ip),
    )
    assert r.status_code == 200, r.text
    return r.json()


async def _visita(client, token, chi=AMICO, user_agent=BROWSER):
    visitor, ip = chi
    r = await client.post(f"/shared/{token}/visit", json={"visitor": visitor}, headers=_chi(ip, user_agent=user_agent))
    assert r.status_code == 200, r.text
    return r.json()


async def _contatore(client) -> dict:
    return (await client.get("/me/profile")).json()["condivisioni"]


@richiede_database
async def test_il_testo_personalizzato_si_salva_si_pulisce_e_si_puo_lasciare_com_e(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session, testo="  Guarda\n cosa\x00 mi hanno detto ✨  ")
    assert (await client.get(f"/shared/{token}")).json()["share_text"] == "Guarda cosa mi hanno detto ✨"
    r = await client.post(f"/me/readings/{rid}/share", json={"attiva": True})          # senza `testo`: resta
    assert r.json()["share_text"] == "Guarda cosa mi hanno detto ✨" and r.json()["share_token"] == token
    r = await client.post(f"/me/readings/{rid}/share", json={"attiva": True, "testo": ""})
    assert r.json()["share_text"] is None
    assert (await client.post(f"/me/readings/{rid}/share", json={"attiva": True, "testo": "x" * 401})).status_code == 422
    assert (await client.get(f"/me/readings/{rid}")).json()["share_text"] is None


@richiede_database
async def test_un_clic_da_solo_non_accerta_niente(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, _ = await _condivisa(client, session)
    c = await _clic(client, rid)
    assert c["contatore"]["verificate"] == 0 and c["contatore"]["prossimo_tra"] == 5
    assert (await client.get(f"/me/readings/{rid}")).status_code == 200


@richiede_database
async def test_la_visita_di_un_visitatore_vero_dopo_il_clic_accerta_la_condivisione(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    esito = await _visita(client, token)
    assert esito == {"contata": True, "accertata": False}     # l'esito vero lo vede solo il proprietario
    assert await _contatore(client) == {
        "verificate": 1, "premi": 0, "prossimo_tra": 4, "iscrizioni": 0, "soglia": 5, "crediti_iscrizione": 5,
    }
    # Una seconda visita non conta due volte la stessa lettura.
    await _visita(client, token, ("altro-amico-abcdef-003", "10.0.0.3"))
    assert (await _contatore(client))["verificate"] == 1


@richiede_database
async def test_senza_clic_del_proprietario_la_visita_non_accerta(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    _, token = await _condivisa(client, session)
    await _visita(client, token)
    assert (await _contatore(client))["verificate"] == 0


@richiede_database
@pytest.mark.parametrize("chi", [
    ("proprietario-abcdef-0001", "10.9.9.9"),      # stesso browser, altra rete
    ("browser-diverso-abcdef-4", "10.0.0.1"),      # stessa rete, altro browser
])
async def test_il_proprietario_non_e_un_visitatore_vero(client, session, catalogo, chi):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    assert (await _visita(client, token, chi))["contata"] is False
    assert (await _contatore(client))["verificate"] == 0


@richiede_database
@pytest.mark.parametrize("user_agent", ["facebookexternalhit/1.1", "Twitterbot/1.0", "python-httpx/0.27", ""])
async def test_un_crawler_non_accerta(client, session, catalogo, user_agent):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    assert (await _visita(client, token, user_agent=user_agent)) == {"contata": False, "accertata": False}
    assert (await _contatore(client))["verificate"] == 0


@richiede_database
async def test_un_identificativo_malformato_non_conta(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    r = await client.post(f"/shared/{token}/visit", json={"visitor": "corto"}, headers=_chi("10.0.0.2"))
    assert r.status_code == 422
    r = await client.post(
        f"/me/readings/{rid}/share-click", json={"canale": "x", "visitor": "a b c d e f g h i j k l"},
        headers=_chi("10.0.0.1"),
    )
    assert r.status_code == 422
    assert (await _contatore(client))["verificate"] == 0


@richiede_database
async def test_la_finestra_di_sette_giorni(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    lettura = (await session.execute(select(Reading))).scalars().first()
    lettura.share_clicked_at = utcnow() - timedelta(days=regole.GIORNI_FINESTRA, hours=1)
    await session.commit()
    await _visita(client, token)
    assert (await _contatore(client))["verificate"] == 0
    await _clic(client, rid)                                   # un nuovo clic riapre la finestra
    await _visita(client, token, ("terzo-amico-abcdef-0004", "10.0.0.4"))
    assert (await _contatore(client))["verificate"] == 1


@richiede_database
async def test_ogni_cinque_condivisioni_accertate_una_lettura_in_omaggio_senza_tetto(client, session, catalogo):
    await _accredita(session, client.identita.principal, 60)
    partenza = await _saldo(client)
    for i in range(1, 11):
        rid, token = await _condivisa(client, session)
        await _clic(client, rid, canale="instagram")
        await _visita(client, token, (f"amico-numero-{i:02d}-abcdef", f"10.1.0.{i}"))
        c = await _contatore(client)
        assert c["verificate"] == i and c["premi"] == i // 5 and c["prossimo_tra"] == 5 - (i % 5)
    # Dieci letture pagate un credito ciascuna, due omaggi (al 5° e al 10°): non c'è tetto.
    assert await _saldo(client) == partenza - 10 + 2


@richiede_database
async def test_il_premio_non_si_accredita_due_volte(client, session, catalogo):
    from tarot_core.api.routers.condivisione import _assegna_premi

    await _accredita(session, client.identita.principal, 60)
    for i in range(1, 6):
        rid, token = await _condivisa(client, session)
        await _clic(client, rid)
        await _visita(client, token, (f"amico-numero-{i:02d}-abcdef", f"10.1.0.{i}"))
    prima = await _saldo(client)
    utente = (await session.execute(select(User))).scalars().first()
    assert await _assegna_premi(session, utente.id) == 0 and await _assegna_premi(session, utente.id) == 0
    assert await _saldo(client) == prima and (await _contatore(client))["premi"] == 1


# ---- le immagini ---------------------------------------------------------------------------------------


async def _carica(client, rid, dati, tipo="image/png"):
    return await client.put(f"/me/readings/{rid}/share-image", content=dati, headers={"content-type": tipo})


@richiede_database
async def test_l_immagine_si_carica_si_riscrive_e_si_serve_ai_social(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    assert (await client.get(f"/shared/{token}")).json()["immagine"] is False
    assert (await client.get(f"/shared/{token}/image.webp")).status_code == 404

    r = await _carica(client, rid, _con_blocco_di_testo(_immagine(800, 600), b"segreto"))
    assert r.status_code == 200 and r.headers["content-type"] == "image/webp"
    assert _webp(r.content).size == (400, 300) and b"segreto" not in r.content

    assert (await client.get(f"/shared/{token}")).json()["immagine"] is True
    img = await client.get(f"/shared/{token}/image.webp")          # senza autenticazione né cookie
    assert img.status_code == 200 and img.headers["content-type"] == "image/webp"
    assert img.content == r.content and len(img.content) < 30_000
    assert "public" in img.headers["cache-control"] and img.headers["x-content-type-options"] == "nosniff"

    # Ricaricare sostituisce, non aggiunge.
    nuova = await _carica(client, rid, _immagine(400, 300, "WEBP", quality=90))
    assert nuova.status_code == 200 and nuova.content != r.content
    assert (await client.get(f"/shared/{token}/image.webp")).content == nuova.content


@richiede_database
async def test_un_file_che_non_e_un_immagine_giusta_non_si_carica(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    assert (await _carica(client, rid, b"<html><script>alert(1)</script>")).status_code == 422
    assert (await _carica(client, rid, _immagine(800, 600), tipo="text/html")).status_code == 415
    assert (await _carica(client, rid, _immagine(1080, 1350))).status_code == 422
    assert (await _carica(client, rid, _immagine(800, 600, "GIF"), tipo="image/gif")).status_code == 415
    assert (await _carica(client, rid, b"x" * (regole.MAX_CARICO + 1))).status_code == 413
    assert (await client.get(f"/shared/{token}/image.webp")).status_code == 404


@richiede_database
async def test_solo_il_proprietario_carica_e_solo_se_e_condivisa(client, session, catalogo, principal_altro):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    client.identita.principal = principal_altro
    assert (await _carica(client, rid, _immagine())).status_code == 404
    r = await client.post(
        f"/me/readings/{rid}/share-click", json={"canale": "x", "visitor": AMICO[0]}, headers=_chi(AMICO[1]),
    )
    assert r.status_code == 404
    assert (await client.get(f"/shared/{token}/image.webp")).status_code == 404

    client.identita.principal = dataclasses.replace(principal_altro, subject="sub-utente-1", email="utente@example.com")
    await client.post(f"/me/readings/{rid}/share", json={"attiva": False})
    assert (await _carica(client, rid, _immagine())).status_code == 409


@richiede_database
async def test_ritirare_il_link_cancella_le_immagini(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, token = await _condivisa(client, session)
    await _carica(client, rid, _immagine())
    await client.post(f"/me/readings/{rid}/share", json={"attiva": False})
    assert (await client.get(f"/shared/{token}/image.webp")).status_code == 404
    # Ripubblicando il link è nuovo e non ha immagini: il frontend le ricarica.
    nuovo = (await client.post(f"/me/readings/{rid}/share", json={"attiva": True})).json()["share_token"]
    assert nuovo != token
    assert (await client.get(f"/shared/{nuovo}")).json()["immagine"] is False


@richiede_database
async def test_i_canali_ammessi(client, session, catalogo):
    await _accredita(session, client.identita.principal, 5)
    rid, _ = await _condivisa(client, session)
    for canale in regole.CANALI:
        await _clic(client, rid, canale=canale)
    r = await client.post(
        f"/me/readings/{rid}/share-click", json={"canale": "myspace", "visitor": PROPRIETARIO[0]},
        headers=_chi(PROPRIETARIO[1]),
    )
    assert r.status_code == 422


# ---- le iscrizioni dal link ---------------------------------------------------------------------------


def _verificato(principal, **campi):
    return dataclasses.replace(principal, raw_claims={"email_verified": True}, **campi)


async def _iscrizione(client, token, chi=AMICO):
    visitor, ip = chi
    r = await client.post(
        "/me/share-signup", json={"token": token, "visitor": visitor}, headers=_chi(ip),
    )
    assert r.status_code == 200, r.text
    return r.json()


@richiede_database
async def test_chi_si_iscrive_dal_link_fa_guadagnare_cinque_letture(client, session, catalogo, principal_altro):
    proprietario = client.identita.principal
    await _accredita(session, proprietario, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    prima = await _saldo(client)

    client.identita.principal = _verificato(principal_altro)
    assert await _iscrizione(client, token) == {"attribuita": True}
    assert await _iscrizione(client, token) == {"attribuita": False, "motivo": "gia_attribuita"}

    client.identita.principal = proprietario
    assert await _saldo(client) == prima + regole.CREDITI_ISCRIZIONE
    c = await _contatore(client)
    assert c["iscrizioni"] == 1
    # Chi arriva dal link l'ha anche aperto: anche la condivisione è accertata.
    assert c["verificate"] == 1


@richiede_database
async def test_un_account_senza_email_verificata_non_fa_guadagnare(client, session, catalogo, principal_altro):
    proprietario = client.identita.principal
    await _accredita(session, proprietario, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    prima = await _saldo(client)
    client.identita.principal = principal_altro           # nessun claim `email_verified`
    assert (await _iscrizione(client, token))["motivo"] == "email_non_verificata"
    client.identita.principal = proprietario
    assert await _saldo(client) == prima and (await _contatore(client))["iscrizioni"] == 0


@richiede_database
async def test_un_account_vecchio_non_e_un_iscritto_nuovo(client, session, catalogo, principal_altro):
    proprietario = client.identita.principal
    await _accredita(session, proprietario, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    client.identita.principal = _verificato(principal_altro)
    await client.get("/me/profile")                        # l'account nasce qui
    altro = (await session.execute(select(User).where(User.email == "altro@example.com"))).scalar_one()
    altro.created_at = utcnow() - timedelta(hours=regole.ORE_ACCOUNT_NUOVO + 1)
    await session.commit()
    assert (await _iscrizione(client, token))["motivo"] == "non_nuovo"


@richiede_database
async def test_non_ci_si_iscrive_dal_proprio_link_ne_dalla_propria_rete(client, session, catalogo, principal_altro):
    proprietario = client.identita.principal
    await _accredita(session, proprietario, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    assert (await _iscrizione(client, token, PROPRIETARIO))["motivo"] == "propria"       # è il proprietario
    client.identita.principal = _verificato(principal_altro)
    assert (await _iscrizione(client, token, ("nuovo-browser-abcdef-0005", PROPRIETARIO[1])))["motivo"] == "stessa_persona"
    assert (await _iscrizione(client, token, (PROPRIETARIO[0], "10.7.7.7")))["motivo"] == "stessa_persona"
    assert (await _iscrizione(client, "token-inesistente"))["motivo"] == "link_sconosciuto"
    assert (await _iscrizione(client, token, ("spazi non validi!!", "10.7.7.7")))["motivo"] == "visitatore_non_valido"


@richiede_database
async def test_il_premio_dell_iscrizione_non_ha_tetto(client, session, catalogo, principal_altro):
    proprietario = client.identita.principal
    await _accredita(session, proprietario, 5)
    rid, token = await _condivisa(client, session)
    await _clic(client, rid)
    prima = await _saldo(client)
    for i in range(3):
        client.identita.principal = _verificato(principal_altro, subject=f"sub-iscritto-{i}", email=f"iscritto{i}@example.com")
        assert await _iscrizione(client, token, (f"iscritto-numero-{i}-abcdef", f"10.2.0.{i}")) == {"attribuita": True}
    client.identita.principal = proprietario
    assert await _saldo(client) == prima + 3 * regole.CREDITI_ISCRIZIONE
    assert (await _contatore(client))["iscrizioni"] == 3


# ---- il profilo -----------------------------------------------------------------------------------------


@richiede_database
async def test_il_profilo_ha_il_contatore_anche_da_zero(client, catalogo):
    assert await _contatore(client) == {
        "verificate": 0, "premi": 0, "prossimo_tra": 5, "iscrizioni": 0, "soglia": 5, "crediti_iscrizione": 5,
    }
    r = await client.patch("/me/profile", json={"gender": "donna"})
    assert r.json()["condivisioni"]["soglia"] == 5
