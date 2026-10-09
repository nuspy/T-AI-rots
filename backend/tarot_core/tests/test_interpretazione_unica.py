"""Le interpretazioni con una chiamata sola (`api/rivelazione.py`): divisione della risposta, ripieghi, una sola
generazione per lettura, compatibilità degli endpoint di prima, letture manuali, tetti col ragionamento acceso.

Sempre il modello finto (`tarot/finto.py`), che risponde anche alla chiamata unica; dove serve una risposta storta
(carte mancanti, JSON illeggibile) la si ottiene sostituendo la sua risposta per quella sola fase."""
from __future__ import annotations

import asyncio
import json

import pytest

from tarot_core.api import rivelazione
from tarot_core.tarot import interpretazione
from tarot_core.tarot.finto import ModelloFinto

from .conftest import eventi_sse, richiede_database
from .test_flusso import QUESITO, _accredita


# ---- la divisione della risposta ---------------------------------------------------------------------------------


def test_la_risposta_si_divide_per_posizione():
    dati = {"carte": [
        {"posizione": 1, "interpretazione": " Il Matto apre. "},
        {"posizione": "2", "interpretazione": "Il Mago agisce."},
        {"posizione": 3.0, "interpretazione": "La Papessa ascolta."},
    ]}
    assert interpretazione.dividi(dati, [1, 2, 3]) == {
        1: "Il Matto apre.", 2: "Il Mago agisce.", 3: "La Papessa ascolta.",
    }
    # Anche la lista nuda, senza la chiave «carte».
    assert interpretazione.dividi(dati["carte"], [2]) == {2: "Il Mago agisce."}


def test_la_divisione_scarta_vuoti_estranei_e_doppioni():
    dati = {"carte": [
        {"posizione": 1, "interpretazione": "   "},              # vuota: si torna alla singola
        {"posizione": 2, "interpretazione": "Prima."},
        {"posizione": 2, "interpretazione": "Doppione."},        # vale la prima
        {"posizione": 9, "interpretazione": "Non richiesta."},   # posizione che non c'è
        {"posizione": True, "interpretazione": "Un booleano non è una posizione."},
        {"posizione": 3},                                        # senza testo
        "non un oggetto",
    ]}
    assert interpretazione.dividi(dati, [1, 2, 3]) == {2: "Prima."}
    assert interpretazione.dividi({"altro": []}, [1]) == {}
    assert interpretazione.dividi("testo", [1]) == {}


# ---- il prompt: le stesse regole e le stesse informazioni ---------------------------------------------------------


def test_il_prompt_unico_ha_tutte_le_regole_della_singola():
    singola = interpretazione.PROMPT_INTERPRETAZIONE.split("\n", 1)[1]
    unica = interpretazione.PROMPT_INTERPRETAZIONE_UNICA
    assert unica.startswith("# Compito: interpretazione_unica\n")
    for riga in singola.replace(interpretazione._UNA_CARTA, "").splitlines():
        assert riga in unica, riga
    assert "UNA PER UNA" in unica
    formato = interpretazione.PROMPT_INTERPRETAZIONE_UNICA_FORMATO
    assert "[[1 dritta]]" in formato and "[[2 rovesciata]]" in formato and "senza JSON" in formato
    # L'esempio del formato si legge con lo stesso codice che legge le risposte.
    assert [n for n, _o, _t, _c in interpretazione.blocchi_testo(formato)] == [1, 2]
    assert "«dritta» o «rovesciata»" in formato
    assert "non anticiparle" in formato


@pytest.fixture
def conoscenza():
    from tarot_core.tarot.conoscenza import Conoscenza

    return Conoscenza.carica()


def test_il_blocco_di_ogni_carta_e_quello_della_chiamata_singola(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    comune = dict(
        stesa=stesa, quesito=QUESITO, contesto="Un cambio di lavoro in vista.",
        colloquio="Oracolo: Da quanto?\nTu: Da mesi.", persone="", registro="quotidiano",
    )
    carte = [
        dict(
            carta=conoscenza.carta(cid), rovescio=n == 2, posizione=conoscenza.posizione(stesa, n),
            dignita=None, precedenti="" if n == 1 else "- Passato: Il Matto (dritta)",
            note=[], doppia_valenza=False, nomi=("The Fool", "Past"), soggetto="",
        )
        for n, cid in ((1, "maj-00"), (2, "maj-01"), (3, "maj-02"))
    ]
    unico = interpretazione.messaggio_unico(carte=carte, lang="en", **comune)
    # Il contesto comune una volta sola.
    assert unico.count("Quesito: ") == 1 and unico.count("Colloquio (domande") == 1
    assert unico.count("Registro linguistico richiesto") == 1 and unico.count("Scrivi in ") == 1
    assert "Carte da interpretare: 3, nelle posizioni 1, 2, 3." in unico
    for voce in carte:
        singolo = interpretazione.messaggio(lang="en", **comune, **voce)
        # La parte «carta» del messaggio singolo, parola per parola, sta nel blocco della carta.
        parte_carta = singolo.split(f"Stesa: {stesa['nome']} — {stesa['descrizione']}\n", 1)[1]
        parte_carta = parte_carta.rsplit("\nRegistro linguistico richiesto", 1)[0]
        blocco = unico.split(f"## Carta in posizione {voce['posizione']['n']}\n", 1)[1]
        assert blocco.startswith(parte_carta), voce["posizione"]["n"]


# ---- il flusso, con il modello finto -------------------------------------------------------------------------------


async def _fino_alla_rivelazione(client, session, spread_id="tre-carte", n=3) -> str:
    await _accredita(session, client.identita.principal)
    r = await client.post("/readings", json={"spread_id": spread_id, "question": QUESITO})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Da qualche mese."})
    await client.post(f"/readings/{rid}/fan")
    for i in range(n):
        assert (await client.post(f"/readings/{rid}/pick", json={"slot": i * 2})).status_code == 200
    return rid


def _compiti(prompt_visti) -> list:
    return [v["compito"] for v in prompt_visti if v["compito"].startswith("interpretazione")]


def _leggi(testo: str) -> list:
    """La risposta unica in testo come lista di [posizione, orientamento, testo], da modificare nei test."""
    return [[n, o, t.strip()] for n, o, t, _chiuso in interpretazione.blocchi_testo(testo)]


def _scrivi(voci: list) -> str:
    return "\n".join(f"[[{n} {o}]]\n{t}" for n, o, t in voci)


@pytest.fixture
def risposta_unica(monkeypatch):
    """Sostituisce la risposta del finto alla sola chiamata unica: `risposta_unica(funzione)`, dove la funzione
    riceve il testo che il finto avrebbe dato (intestazioni «[[N orientamento]]») e restituisce quello da dare."""
    originale = ModelloFinto._rispondi

    def imposta(trasforma):
        def finto(self, req):
            testo = originale(self, req)
            if any(m.role == "system" and "# Compito: interpretazione_unica" in m.content for m in req.messages):
                return trasforma(testo)
            return testo

        monkeypatch.setattr(ModelloFinto, "_rispondi", finto)

    return imposta


@richiede_database
async def test_la_prima_carta_genera_tutte_le_interpretazioni_le_altre_le_trovano_pronte(
    client, session, catalogo, prompt_visti,
):
    rid = await _fino_alla_rivelazione(client, session)
    prompt_visti.clear()
    testi = {}
    for pos in (1, 2, 3):
        eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal/{pos}")).text)
        nomi = [e for e, _ in eventi]
        # Gli stessi eventi di prima: un client vecchio non vede differenze.
        assert nomi[0] == "carta" and nomi[-1] == "fine" and "token" in nomi, nomi
        fine = eventi[-1][1]
        assert fine["posizione"] == pos and fine["interpretazione"] and fine["ultima"] is (pos == 3)
        testo = "".join(d["testo"] for e, d in eventi if e == "token")
        assert testo == fine["interpretazione"]
        testi[pos] = testo
        if pos == 1:
            # Una chiamata sola, alla prima carta.
            assert _compiti(prompt_visti) == ["interpretazione_unica"]
    assert _compiti(prompt_visti) == ["interpretazione_unica"]          # nessun'altra chiamata dopo
    assert len(set(testi.values())) == 3
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert dettaglio["status"] == "sintesi"
    assert {c["posizione"]: c["interpretazione"] for c in dettaglio["cards"]} == testi
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    assert eventi[-1][0] == "fine"


@richiede_database
async def test_le_carte_coperte_non_mostrano_l_interpretazione_gia_scritta(client, session, catalogo):
    rid = await _fino_alla_rivelazione(client, session)
    await client.post(f"/readings/{rid}/reveal/1")
    carte = {c["posizione"]: c for c in (await client.get(f"/me/readings/{rid}")).json()["cards"]}
    assert carte[1]["interpretazione"]
    assert "interpretazione" not in carte[2] and "carta" not in carte[2]     # coperta: niente di niente


@richiede_database
async def test_carte_mancanti_tornano_alla_chiamata_singola_solo_per_quelle(
    client, session, catalogo, prompt_visti, risposta_unica,
):
    def senza_la_seconda(testo):
        return _scrivi([v for v in _leggi(testo) if v[0] != 2])

    risposta_unica(senza_la_seconda)
    rid = await _fino_alla_rivelazione(client, session)
    prompt_visti.clear()
    for pos in (1, 2, 3):
        eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal/{pos}")).text)
        assert eventi[-1][0] == "fine" and eventi[-1][1]["interpretazione"], pos
        token = [d["testo"] for e, d in eventi if e == "token"]
        # La posizione mancante arriva a pezzi, in streaming, come prima; le altre in un colpo.
        assert len(token) > 1 if pos == 2 else len(token) == 1
    assert _compiti(prompt_visti) == ["interpretazione_unica", "interpretazione"]
    singola = next(v for v in prompt_visti if v["compito"] == "interpretazione")
    assert singola["sistema"].startswith("# Compito: interpretazione\n")
    assert "Posizione 2:" in singola["utente"] and "Posizione 3:" not in singola["utente"]


def test_l_orientamento_deve_coincidere_con_quello_vero():
    dati = {"carte": [
        {"posizione": 1, "orientamento": "dritta", "interpretazione": "Il Matto apre."},
        {"posizione": 2, "orientamento": "dritta", "interpretazione": "Il Mago, scivolato."},       # è rovesciata
        {"posizione": 3, "interpretazione": "Senza orientamento."},
        {"posizione": 4, "orientamento": "Rovesciata", "interpretazione": "La Torre trattiene."},
        {"posizione": 5, "orientamento": "boh", "interpretazione": "Non si capisce."},
    ]}
    scarti: dict = {}
    divise = interpretazione.dividi(
        dati, [1, 2, 3, 4, 5], orientamenti={1: False, 2: True, 3: False, 4: True, 5: False}, scarti=scarti,
    )
    assert divise == {1: "Il Matto apre.", 4: "La Torre trattiene."}
    assert set(scarti) == {2, 3, 5} and "invece di «rovesciata»" in scarti[2]
    # Senza gli orientamenti veri non si controlla (il comportamento di prima).
    assert set(interpretazione.dividi(dati, [1, 2, 3, 4, 5])) == {1, 2, 3, 4, 5}


@pytest.mark.parametrize("lang, testo", [
    ("it", "La carta, rovesciata, chiede pazienza."),
    ("en", "Reversed, the card asks for patience."),
    ("es", "La carta invertida pide paciencia."),
    ("es", "Al revés, la carta pide paciencia."),
    ("hu", "A fordított lap türelmet kér."),
    ("ru", "Перевёрнутая карта просит терпения."),
    ("ru", "Перевернутая карта просит терпения."),
    ("uk", "Перевернута карта просить терпіння."),
])
def test_una_carta_dritta_detta_rovesciata_nel_testo_torna_alla_singola(lang, testo):
    voce = {"carte": [{"posizione": 1, "orientamento": "dritta", "interpretazione": testo}]}
    scarti: dict = {}
    assert interpretazione.dividi(voce, [1], orientamenti={1: False}, lang=lang, scarti=scarti) == {}
    assert scarti[1] == "carta dritta detta rovesciata nel testo"
    # La stessa parola in una carta davvero rovesciata va bene.
    voce["carte"][0]["orientamento"] = "rovesciata"
    assert interpretazione.dividi(voce, [1], orientamenti={1: True}, lang=lang) == {1: testo}


def test_senza_radici_per_la_lingua_il_testo_non_si_controlla():
    voce = {"carte": [{"posizione": 1, "orientamento": "dritta", "interpretazione": "Reversed? Odwrócona."}]}
    assert interpretazione.dividi(voce, [1], orientamenti={1: False}, lang="pl") == {1: "Reversed? Odwrócona."}
    assert not interpretazione.dice_rovesciata("La carta è dritta.", "it")


@richiede_database
async def test_orientamento_scambiato_torna_alla_chiamata_singola(
    client, session, catalogo, prompt_visti, risposta_unica,
):
    def scambia_la_seconda(testo):
        voci = _leggi(testo)
        for v in voci:
            if v[0] == 2:
                v[1] = "dritta" if v[1] == "rovesciata" else "rovesciata"
        return _scrivi(voci)

    risposta_unica(scambia_la_seconda)
    rid = await _fino_alla_rivelazione(client, session)
    prompt_visti.clear()
    for pos in (1, 2, 3):
        assert eventi_sse((await client.post(f"/readings/{rid}/reveal/{pos}")).text)[-1][1]["interpretazione"]
    assert _compiti(prompt_visti) == ["interpretazione_unica", "interpretazione"]
    singola = next(v for v in prompt_visti if v["compito"] == "interpretazione")
    assert "Posizione 2:" in singola["utente"]


@richiede_database
async def test_le_carte_dritte_dette_rovesciate_tornano_alla_singola(
    client, session, catalogo, prompt_visti, risposta_unica,
):
    dritte = []

    def dice_rovesciata(testo):
        voci = _leggi(testo)
        for v in voci:
            if v[1] == "dritta":
                dritte.append(v[0])
                v[2] += " Qui la carta appare rovesciata."
        return _scrivi(voci)

    risposta_unica(dice_rovesciata)
    rid = await _fino_alla_rivelazione(client, session, "croce-celtica", 10)
    prompt_visti.clear()
    eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal-all")).text)
    assert all(d["interpretazione"] for e, d in eventi if e == "fine")
    assert dritte, "il mazzo di prova ha almeno una carta dritta"
    assert _compiti(prompt_visti) == ["interpretazione_unica"] + ["interpretazione"] * len(dritte)
    rifatte = [v["utente"] for v in prompt_visti if v["compito"] == "interpretazione"]
    for n, utente in zip(sorted(dritte), rifatte):
        assert f"Posizione {n}:" in utente and "Orientamento: dritta" in utente


@richiede_database
async def test_risposta_illeggibile_tutte_singole_e_la_chiamata_unica_non_si_ripete(
    client, session, catalogo, prompt_visti, risposta_unica,
):
    risposta_unica(lambda _testo: "niente intestazioni, solo un testo qualunque")
    rid = await _fino_alla_rivelazione(client, session)
    prompt_visti.clear()
    for pos in (1, 2, 3):
        eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal/{pos}")).text)
        assert eventi[-1][1]["interpretazione"], pos
    assert _compiti(prompt_visti) == ["interpretazione_unica", "interpretazione", "interpretazione", "interpretazione"]


@richiede_database
async def test_testo_vuoto_errore_pulito_come_prima(client, session, catalogo, risposta_unica, monkeypatch):
    risposta_unica(lambda _testo: json.dumps({"carte": []}))

    async def muto(self, req):
        if False:  # pragma: no cover - un generatore che non produce niente
            yield None
        raise RuntimeError("il fornitore non risponde")

    monkeypatch.setattr(ModelloFinto, "stream", muto)
    rid = await _fino_alla_rivelazione(client, session)
    eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal/1")).text)
    nomi = [e for e, _ in eventi]
    assert nomi[0] == "carta" and "errore" in nomi and nomi[-1] == "fine"
    assert eventi[-1][1]["interpretazione"] == ""
    # La lettura va avanti: la carta dopo si può girare.
    assert (await client.post(f"/readings/{rid}/reveal/2")).status_code == 200


@richiede_database
async def test_svelamenti_durante_la_chiamata_unica_non_ne_avviano_un_altra(
    client, session, catalogo, prompt_visti, monkeypatch,
):
    rid = await _fino_alla_rivelazione(client, session)
    prompt_visti.clear()
    via = asyncio.Event()
    originale = ModelloFinto.stream

    async def lento(self, req):
        await via.wait()
        async for pezzo in originale(self, req):
            yield pezzo

    monkeypatch.setattr(ModelloFinto, "stream", lento)
    import uuid

    from tarot_core.llm.base import GenerationRequest

    prima = asyncio.create_task(client.post(f"/readings/{rid}/reveal/1"))
    for _ in range(300):
        if rivelazione.in_corso(uuid.UUID(rid)) is not None:
            break
        await asyncio.sleep(0.01)
    in_corso = rivelazione.in_corso(uuid.UUID(rid))
    assert in_corso is not None
    # Una seconda richiesta della stessa lettura mentre il lettore legge riceve lo stesso task, non ne avvia un
    # altro. (Due richieste HTTP davvero simultanee qui non si possono fare: il database dei test è una connessione
    # sola, con i savepoint; il meccanismo è lo stesso, provato senza HTTP in `test_lo_stesso_task_per_la_stessa_lettura`.)
    altra = rivelazione.Preparata(reading_id=uuid.UUID(rid), posizioni=[2, 3], req=GenerationRequest(messages=[]))
    assert rivelazione.avvia(altra, object(), None) is in_corso
    via.set()
    e1 = eventi_sse((await prima).text)
    e2 = eventi_sse((await client.post(f"/readings/{rid}/reveal/2")).text)
    assert e1[-1][1]["interpretazione"] and e2[-1][1]["interpretazione"]
    assert _compiti(prompt_visti) == ["interpretazione_unica"]


async def test_lo_stesso_task_per_la_stessa_lettura():
    """Il meccanismo, senza HTTP: due richieste della stessa lettura ricevono lo stesso task; finito quello, la
    chiamata unica non si ritenta (si torna alle singole)."""
    import uuid

    from tarot_core.llm.base import GenerationRequest, StreamChunk

    rivelazione.dimentica()
    chiamate = []
    via = asyncio.Event()

    class Fornitore:
        async def stream(self, req):
            chiamate.append(req)
            await via.wait()
            yield StreamChunk(text="[[1 dritta]]\nUno.\n[[2 dri")
            yield StreamChunk(text="tta]]\nDue.")
            yield StreamChunk(done=True)

    salvate = {}

    class Sessione:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

        async def execute(self, _query):
            raise RuntimeError("niente database in questo test")

    def fabbrica():
        return Sessione()

    rid = uuid.uuid4()
    preparata = rivelazione.Preparata(
        reading_id=rid, posizioni=[1, 2], req=GenerationRequest(messages=[]),
        carte={1: ({"dritto": "x"}, False), 2: ({"dritto": "y"}, False)},
    )
    primo = rivelazione.avvia(preparata, Fornitore(), fabbrica)
    secondo = rivelazione.avvia(preparata, Fornitore(), fabbrica)
    assert primo is secondo and primo is not None
    via.set()
    salvate.update(await primo)
    assert salvate == {1: "Uno.", 2: "Due."} and len(chiamate) == 1
    await asyncio.sleep(0)
    assert rivelazione.in_corso(rid) is None
    assert rivelazione.avvia(preparata, Fornitore(), fabbrica) is None          # già tentata: solo singole
    # Con una carta sola da leggere non serve la chiamata unica.
    sola = rivelazione.Preparata(reading_id=uuid.uuid4(), posizioni=[3], req=GenerationRequest(messages=[]))
    assert rivelazione.avvia(sola, Fornitore(), fabbrica) is None


@richiede_database
async def test_svela_tutte_in_un_flusso(client, session, catalogo, prompt_visti):
    rid = await _fino_alla_rivelazione(client, session, "croce-semplice", 4)
    posizioni = sorted(c["posizione"] for c in (await client.get(f"/me/readings/{rid}")).json()["cards"])
    n = len(posizioni)                      # anche la carta calcolata, non scelta
    prompt_visti.clear()
    eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal-all")).text)
    nomi = [e for e, _ in eventi]
    # Prima tutte le carte, poi il lettore legge, poi un testo e una fine per carta.
    assert nomi[:n] == ["carta"] * n and nomi[n] == "fase" and eventi[n][1] == {"fase": "lettura"}
    fini = [d for e, d in eventi if e == "fine"]
    assert [f["posizione"] for f in fini] == posizioni
    assert [f["ultima"] for f in fini] == [False] * (n - 1) + [True]
    assert "sostituisci" not in nomi
    token: dict = {}
    for e, d in eventi:
        if e == "token":
            token[d["posizione"]] = token.get(d["posizione"], "") + d["testo"]
    assert {p: t.strip() for p, t in token.items()} == {f["posizione"]: f["interpretazione"] for f in fini}
    assert _compiti(prompt_visti) == ["interpretazione_unica"]
    assert (await client.get(f"/me/readings/{rid}")).json()["status"] == "sintesi"
    assert (await client.post(f"/readings/{rid}/reveal-all")).status_code == 409
    assert eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)[-1][0] == "fine"


def test_il_testo_in_diretta_non_mostra_le_intestazioni_a_meta():
    orientamenti = {1: False, 2: True}
    # L'intestazione della seconda carta è a metà: non finisce nel testo della prima, e la seconda non c'è ancora.
    assert interpretazione.in_diretta("[[1 dritta]]\nIl Matto apre.\n[[2 rov", [1, 2], orientamenti=orientamenti) == {
        1: ("Il Matto apre.\n", True),
    }
    visti = interpretazione.in_diretta(
        "[[1 dritta]]\nIl Matto apre.\n[[2 rovesciata]]\nIl Mago", [1, 2], orientamenti=orientamenti,
    )
    assert visti == {1: ("Il Matto apre.\n", True), 2: ("Il Mago", True)}
    # Orientamento sbagliato nell'intestazione: non si mostra niente di quella carta.
    assert interpretazione.in_diretta("[[2 dritta]]\nIl Mago", [2], orientamenti=orientamenti) == {2: ("", False)}
    # Una carta dritta detta rovesciata smette di valere.
    assert interpretazione.in_diretta(
        "[[1 dritta]]\nQui la carta appare rovesciata", [1], orientamenti=orientamenti,
    )[1][1] is False


def test_la_risposta_in_testo_si_divide_e_un_json_si_legge_ancora():
    testo = "Preambolo da ignorare.\n[[1 dritta]]\n Il Matto apre. \n\n[[Posizione 2: rovesciata]]\nIl Mago trattiene."
    assert interpretazione.dividi_testo(testo, [1, 2], orientamenti={1: False, 2: True}) == {
        1: "Il Matto apre.", 2: "Il Mago trattiene.",
    }
    vecchio = json.dumps({"carte": [{"posizione": 1, "orientamento": "dritta", "interpretazione": "Uno."}]})
    assert interpretazione.dividi_testo(vecchio, [1], orientamenti={1: False}) == {1: "Uno."}
    assert interpretazione.dividi_testo("{non json", [1]) == {}
    assert interpretazione.senza_ultimo_blocco("[[1 dritta]]\nUno.\n[[2 dritta]]\nDu") == "[[1 dritta]]\nUno.\n"


@richiede_database
async def test_svela_tutte_manda_il_testo_mentre_il_modello_scrive(client, session, catalogo, monkeypatch):
    rid = await _fino_alla_rivelazione(client, session)
    monkeypatch.setattr(ModelloFinto, "pausa", 0.002)
    eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal-all")).text)
    nomi = [e for e, _ in eventi]
    # Più pezzi per la stessa carta, e tutti prima della prima `fine`: il testo arriva mentre si scrive.
    prima_fine = nomi.index("fine")
    pezzi_prima = [d["posizione"] for e, d in eventi[:prima_fine] if e == "token"]
    assert pezzi_prima.count(1) > 1 and set(pezzi_prima) == {1, 2, 3}
    assert "sostituisci" not in nomi


@richiede_database
async def test_una_formula_proibita_si_ferma_in_diretta_e_si_sostituisce(
    client, session, catalogo, risposta_unica, monkeypatch,
):
    from tarot_core.guards.lettura import uscita_proibita

    proibita = "morirai presto"
    assert uscita_proibita(proibita), "la frase di prova deve essere una formula proibita"

    def con_formula(testo):
        voci = _leggi(testo)
        voci[1][2] = f"{voci[1][2]} Ma attenzione: {proibita}, dicono le carte."
        return _scrivi(voci)

    risposta_unica(con_formula)
    monkeypatch.setattr(ModelloFinto, "pausa", 0.002)
    rid = await _fino_alla_rivelazione(client, session)
    eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal-all")).text)
    visto = "".join(d["testo"] for e, d in eventi if e == "token" and d["posizione"] == 2)
    assert proibita not in visto
    sostituito = [d for e, d in eventi if e == "sostituisci" and d["posizione"] == 2]
    fine = next(d for e, d in eventi if e == "fine" and d["posizione"] == 2)
    assert sostituito and sostituito[-1]["testo"] == fine["interpretazione"] and proibita not in fine["interpretazione"]


@richiede_database
async def test_svela_tutte_dopo_una_carta_girata_coi_vecchi_endpoint(client, session, catalogo, prompt_visti):
    rid = await _fino_alla_rivelazione(client, session)
    prompt_visti.clear()
    await client.post(f"/readings/{rid}/reveal/1")
    eventi = eventi_sse((await client.post(f"/readings/{rid}/reveal-all")).text)
    assert [d["posizione"] for e, d in eventi if e == "carta"] == [2, 3]
    assert all(d["interpretazione"] for e, d in eventi if e == "fine")
    assert _compiti(prompt_visti) == ["interpretazione_unica"]          # le 2 e 3 erano già pronte


@richiede_database
async def test_la_sintesi_sblocca_una_lettura_con_tutte_le_carte_girate(client, session, catalogo):
    """Il client chiude la connessione prima della `fine` dell'ultima carta: tutte girate, stato ancora
    «rivelazione». La sintesi non resta bloccata."""
    from sqlalchemy import update

    from tarot_core.domain.models import DrawnCard, Reading

    rid = await _fino_alla_rivelazione(client, session)
    import uuid

    await session.execute(update(DrawnCard).where(DrawnCard.reading_id == uuid.UUID(rid)).values(rivelata=True))
    await session.execute(update(Reading).where(Reading.id == uuid.UUID(rid)).values(status="rivelazione"))
    await session.commit()
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    assert eventi[-1][0] == "fine"


@richiede_database
async def test_lettura_manuale_con_la_chiamata_unica(client, session, catalogo, prompt_visti):
    from tarot_core.billing.credits import RegistroCrediti
    from tarot_core.domain.repositories import UserRepository

    utente = await UserRepository(session).ensure(client.identita.principal)
    await RegistroCrediti(session).rettifica(utente.id, 10, note="prova")
    await session.commit()
    manuali = [{"posizione": n, "card_id": f"maj-0{n}"} for n in (1, 2, 3)]
    r = await client.post("/readings", json={"spread_id": "tre-carte", "question": QUESITO, "manual_cards": manuali})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Da qualche mese."})
    prompt_visti.clear()
    await client.post(f"/readings/{rid}/reveal/1")
    carte = {c["posizione"]: c for c in (await client.get(f"/me/readings/{rid}")).json()["cards"]}
    # La carta si vede da subito (mazzo fisico), la sua lettura solo quando la si gira.
    assert carte[2]["carta"]["id"] == "maj-02" and carte[2]["interpretazione"] is None
    assert carte[1]["interpretazione"]
    unica = next(v for v in prompt_visti if v["compito"] == "interpretazione_unica")
    assert unica["utente"].count("## Carta in posizione ") == 3
    for pos in (2, 3):
        assert eventi_sse((await client.post(f"/readings/{rid}/reveal/{pos}")).text)[-1][1]["interpretazione"]
    assert _compiti(prompt_visti) == ["interpretazione_unica"]


# ---- i tetti col ragionamento acceso ---------------------------------------------------------------------------------


async def _payload(fornitore, max_tokens):
    from tarot_core.llm.base import GenerationRequest, Message

    fornitore._modello_risolto = "m"
    return await fornitore._build_payload(
        GenerationRequest(messages=[Message("user", "x")], max_tokens=max_tokens, model="m"), stream=True,
    )


async def test_col_ragionamento_il_tetto_e_visibile_piu_margine(monkeypatch):
    from tarot_core.llm import ragionamento
    from tarot_core.llm.openai_compatible import OpenAICompatibleProvider
    from tarot_core.settings import get_settings

    monkeypatch.delenv("TAROT_MARGINI_RAGIONAMENTO", raising=False)
    get_settings.cache_clear()
    acceso = OpenAICompatibleProvider(
        base_url="http://x/v1", api_key="k", default_model="m", ragiona=True, livello_ragionamento="xhigh",
        parametri={"reasoning_effort": "xhigh"},
    )
    assert (await _payload(acceso, 1700))["max_tokens"] == 1700 + ragionamento.MARGINE_LIVELLO["xhigh"]
    spento = OpenAICompatibleProvider(
        base_url="http://x/v1", api_key="k", default_model="m", ragiona=False, livello_ragionamento="none",
    )
    assert (await _payload(spento, 1700))["max_tokens"] == 1700
    # Un fornitore di prima dei livelli che ragiona: il pavimento di sempre.
    vecchio = OpenAICompatibleProvider(
        base_url="http://x/v1", api_key="k", default_model="m", ragiona=True,
        parametri={"reasoning_budget": 16384, "chat_template_kwargs": {"enable_thinking": True}},
    )
    assert (await _payload(vecchio, 500))["max_tokens"] == 16384 + 2048
    # NIM (dialetto thinking): il margine copre almeno il budget mandato al modello.
    nim = OpenAICompatibleProvider(
        base_url="http://x/v1", api_key="k", default_model="m", ragiona=True, livello_ragionamento="low",
        parametri={"reasoning_budget": 9000, "chat_template_kwargs": {"enable_thinking": True}},
    )
    assert (await _payload(nim, 500))["max_tokens"] == 500 + 9000

    # Configurabile, per livello.
    monkeypatch.setenv("TAROT_MARGINI_RAGIONAMENTO", '{"xhigh": 30000}')
    get_settings.cache_clear()
    try:
        assert (await _payload(acceso, 2600))["max_tokens"] == 32600
        assert ragionamento.margine("high") == ragionamento.MARGINE_LIVELLO["high"]
    finally:
        monkeypatch.delenv("TAROT_MARGINI_RAGIONAMENTO")
        get_settings.cache_clear()


def test_il_registro_passa_il_livello_al_fornitore():
    from tarot_core.llm import ragionamento
    from tarot_core.llm.compiti import Compito, ModelloConfigurato, RegistroModelli

    registro = RegistroModelli([ModelloConfigurato(
        nome="nebius", base_url="http://x/v1", model="m", tipo="nebius", livello_ragionamento="none",
    )])
    registro.assegna(Compito.SINTESI, "nebius", livello="xhigh")
    registro.assegna(Compito.INTERVISTA, "nebius", livello="none")
    sintesi, intervista = registro.per(Compito.SINTESI), registro.per(Compito.INTERVISTA)
    assert sintesi.ragiona and sintesi.livello_ragionamento == "xhigh"
    assert sintesi._parametri["reasoning_effort"] == "xhigh"
    assert sintesi._tetto(2600) == 2600 + ragionamento.MARGINE_LIVELLO["xhigh"]
    assert not intervista.ragiona and intervista._tetto(400) == 400


def test_anthropic_tetto_visibile_piu_budget():
    from tarot_core.llm.anthropic import AnthropicProvider
    from tarot_core.llm.base import GenerationRequest, Message

    fornitore = AnthropicProvider(api_key="k", default_model="claude", budget_ragionamento=16384)
    corpo = fornitore.costruisci(GenerationRequest(messages=[Message("user", "x")], max_tokens=2600))
    assert corpo["max_tokens"] == 2600 + 16384 and corpo["thinking"]["budget_tokens"] == 16384
