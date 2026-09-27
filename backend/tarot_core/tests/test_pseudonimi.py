"""I nomi di persona non lasciano il server: al modello «Persona_1», a chi legge il nome vero."""
from __future__ import annotations

import random

import pytest

from tarot_core.llm.base import GenerationRequest, Message, StreamChunk
from tarot_core.tarot.pseudonimi import Pseudonimi, ProviderProtetto, protetto

from .conftest import richiede_database


# ---- nascondere e ripristinare ---------------------------------------------------------------------------------------


def test_un_nome_diventa_un_segnaposto_e_torna():
    p = Pseudonimi(["Marco"])
    assert p.nascondi("Compatibilità con Marco, davvero.") == "Compatibilità con Persona_1, davvero."
    assert p.ripristina("Persona_1 è una persona tranquilla.") == "Marco è una persona tranquilla."


def test_maiuscole_e_punteggiatura_non_lo_nascondono():
    p = Pseudonimi(["Marco"])
    assert p.nascondi("marco? MARCO! «Marco» (Marco)") == "Persona_1? Persona_1! «Persona_1» (Persona_1)"


def test_una_forma_flessa_si_nasconde_e_torna_esatta():
    p = Pseudonimi(["Marcó"])                                   # un nome di 5 lettere si riconosce come inizio di parola
    frase = "Marcóval és Marcónak"
    assert p.nascondi(frase) == "Persona_1val és Persona_1nak"
    assert p.ripristina(p.nascondi(frase)) == frase


def test_un_nome_corto_si_riconosce_solo_come_parola_intera():
    p = Pseudonimi(["Ed"])
    assert p.nascondi("Ed è qui, ma l'edificio no") == "Persona_1 è qui, ma l'edificio no"


def test_un_nome_di_piu_parole_si_riconosce_anche_a_pezzi():
    p = Pseudonimi(["Maria Grazia"])
    nascosto = p.nascondi("Maria Grazia, cioè Maria, e Grazia")
    assert "Maria" not in nascosto and "Grazia" not in nascosto
    assert p.ripristina(nascosto) == "Maria Grazia, cioè Maria, e Grazia"


def test_il_segnaposto_non_si_confonde_con_una_parola():
    p = Pseudonimi(["Persona", "Marco"])                        # «Persona» si scambierebbe col prefisso: si ignora
    assert p.nascondi("Persona Marco") == "Persona Persona_1"


def test_un_segnaposto_sconosciuto_resta_com_e():
    assert Pseudonimi(["Marco"]).ripristina("Persona_7 non esiste") == "Persona_7 non esiste"


def test_senza_nomi_non_cambia_niente():
    p = Pseudonimi([])
    assert p.vuoto and p.nascondi("Marco") == "Marco" and p.ripristina("Persona_1") == "Persona_1"


def test_il_ripristino_dentro_un_json_tocca_i_valori_non_le_chiavi():
    p = Pseudonimi(["Marco"])
    dati = {"domanda": "Da quanto conosci Persona_1?", "elenco": ["Persona_1", 3, None], "Persona_1": {"x": "Persona_1"}}
    assert p.ripristina_dati(dati) == {"domanda": "Da quanto conosci Marco?", "elenco": ["Marco", 3, None], "Persona_1": {"x": "Marco"}}


def test_andata_e_ritorno_su_testi_a_caso():
    rnd = random.Random(7)
    parole = ["il", "la", "carta", "Marco", "marco", "Persona", "e", "Luna,", "«Marco»", "di", "Marcovaldo", "Ed", "edificio"]
    p = Pseudonimi(["Marco", "Ed"])
    for _ in range(300):
        testo = " ".join(rnd.choice(parole) for _ in range(rnd.randint(1, 12)))
        # Il ripristino rende il nome con la maiuscola canonica: si confronta senza badare alle maiuscole.
        assert p.ripristina(p.nascondi(testo)).lower() == testo.lower()


# ---- in streaming -------------------------------------------------------------------------------------------------------


def _rendi(p: Pseudonimi, pezzi):
    r = p.flusso()
    return "".join(r.feed(x) for x in pezzi) + r.fine()


TESTO = "Persona_1 e Persona_2 si guardano; Persona_1, dico, Persona_ non finita e Pers"


def test_il_flusso_rende_lo_stesso_testo_a_qualunque_taglio():
    p = Pseudonimi(["Marco", "Lucia"])
    atteso = p.ripristina(TESTO)
    assert atteso.startswith("Marco e Lucia si guardano; Marco,")
    for i in range(len(TESTO) + 1):
        assert _rendi(p, [TESTO[:i], TESTO[i:]]) == atteso, i
    assert _rendi(p, list(TESTO)) == atteso                       # un carattere per volta


def test_il_flusso_trattiene_solo_cio_che_potrebbe_essere_un_segnaposto():
    p = Pseudonimi(["Marco"])
    r = p.flusso()
    assert r.feed("Ciao Pers") == "Ciao "
    assert r.feed("ona_1!") == "Marco!"
    assert r.feed("Persona_") == ""                                 # potrebbe diventare Persona_1
    assert r.fine() == "Persona_"                                   # ma il flusso è finito: non si perde


# ---- l'involucro del fornitore ------------------------------------------------------------------------------------------


class FornitoreSpia:
    """Un fornitore che registra ciò che riceve e risponde citando i segnaposto."""

    name = "spia"
    motore = "prova"

    def __init__(self):
        self.viste: list[str] = []

    def _registra(self, req):
        self.viste.append("\n".join(m.content for m in req.messages))

    async def complete(self, req):
        self._registra(req)
        return "Persona_1 risponde bene."

    async def complete_json(self, req):
        self._registra(req)
        return {"completo": False, "domanda": "Da quanto conosci Persona_1?"}

    async def stream(self, req):
        self._registra(req)
        for pezzo in ["Persona", "_1 ", "ascolta. Pers", "ona_1 sorride."]:
            yield StreamChunk(text=pezzo)
        yield StreamChunk(done=True, finish_reason="stop")


def _req():
    return GenerationRequest(messages=[Message("system", "Regole."), Message("user", "Compatibilità con Marco, cioè marco.")])


async def test_i_prompt_di_sistema_non_si_toccano():
    spia = FornitoreSpia()
    p = ProviderProtetto(spia, Pseudonimi(["Rosa Bianchi"]))          # «Rosa» è anche una parola comune
    req = GenerationRequest(messages=[Message("system", "La rosa è un simbolo. # Compito: sintesi"), Message("user", "Rosa Bianchi, cioè rosa")])
    await p.complete(req)
    assert spia.viste == ["La rosa è un simbolo. # Compito: sintesi" + chr(10) + "Persona_1, cioè Persona_2"]


def test_le_particelle_comuni_non_si_nascondono_da_sole():
    p = Pseudonimi(["Anna Maria Della Rosa"])
    assert "Della" not in p.nascondi("Anna Maria Della Rosa") and p.nascondi("della luna") == "della luna"
    assert p.ripristina(p.nascondi("Rosa e Anna")) == "Rosa e Anna"


async def test_il_fornitore_non_vede_il_nome_e_le_risposte_tornano_col_nome():
    spia = FornitoreSpia()
    p = ProviderProtetto(spia, Pseudonimi(["Marco"]))
    assert await p.complete(_req()) == "Marco risponde bene."
    assert await p.complete_json(_req()) == {"completo": False, "domanda": "Da quanto conosci Marco?"}
    testo = "".join([c.text async for c in p.stream(_req())])
    assert testo == "Marco ascolta. Marco sorride."
    assert len(spia.viste) == 3
    assert all("Marco" not in v and "marco" not in v.lower() and "Persona_1" in v for v in spia.viste)


async def test_l_involucro_si_comporta_come_il_fornitore():
    spia = FornitoreSpia()
    p = ProviderProtetto(spia, Pseudonimi(["Marco"]))
    assert p.name == "spia" and p.motore == "prova" and hasattr(p, "complete_json")


def test_l_involucro_c_e_solo_se_serve():
    spia = FornitoreSpia()

    class Persone:
        class partner:
            nome = "Marco"

        class tu:
            nome = None

    assert isinstance(protetto(spia, Persone), ProviderProtetto)
    assert protetto(spia, None) is spia                            # letture standard: nessun nome da nascondere
    assert protetto(spia, Persone, attivo=False) is spia           # spenta da impostazione

    class Senza:
        class partner:
            nome = None

        class tu:
            nome = None

    assert protetto(spia, Senza) is spia


# ---- una lettura intera --------------------------------------------------------------------------------------------------


@richiede_database
async def test_una_lettura_di_coppia_non_fa_arrivare_il_nome_e_non_fa_uscire_i_segnaposto(client, session, catalogo, prompt_visti):
    from .test_flusso import _accredita, _lettura_completa
    from .test_lettura_speciale import PARTNER, QUESITO, _scheda

    await _accredita(session, client.identita.principal, 5)
    await _scheda(client)
    fine = await _lettura_completa(client, "compat-tre", 3, QUESITO, {"partner": PARTNER})
    assert prompt_visti and all("Marco" not in (v["sistema"] + v["utente"]) for v in prompt_visti)
    assert any("Persona_1" in v["utente"] for v in prompt_visti)
    # Ciò che torna a chi legge non porta mai un segnaposto: né il responso, né l'intervista, né il quadro salvato.
    rid = (await client.get("/me/readings")).json()["letture"][0]["id"]
    dettaglio = (await client.get(f"/me/readings/{rid}")).json()
    assert "Persona_" not in repr(dettaglio) and "Persona_" not in repr(fine)
