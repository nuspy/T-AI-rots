"""I prompt delle letture speciali: cosa entra, cosa no, e lo standard invariato."""
from __future__ import annotations

import hashlib
import re

import pytest

from tarot_core.guards.policy import Guardrail, RegistroGuardrail, interpreta
from tarot_core.tarot import cag, interpretazione
from tarot_core.tarot.conoscenza import Conoscenza
from tarot_core.tarot.intervista import (
    PROMPT_INTERVISTA_RELAZIONE, prossimo_passo, ricalca_il_quesito, viola_le_regole,
)
from tarot_core.tarot.persone import (
    blocco_compatibilita, blocco_persone, da_json, parole_neutre, soggetto_testo,
)

from .test_intervista import Copione

#: L'impronta del prefisso di sintesi della lettura STANDARD prima delle letture
#: speciali. Se cambia, cambia il prefisso in cache di ogni lettura normale: va
#: cambiata di proposito, non per effetto collaterale.
IMPRONTA_PREFISSO_STANDARD = "688f5c679b985898a8b22ba420c9c4a0f4e3658d3073675e668522d123e5ee09"


@pytest.fixture(scope="module")
def conoscenza() -> Conoscenza:
    return Conoscenza.carica()


@pytest.fixture(scope="module")
def registro() -> RegistroGuardrail:
    return RegistroGuardrail()


PERSONE = da_json({
    "v": 1,
    "tu": {"genere": "donna", "trans": False, "nascita": "1990-03-14"},
    "partner": {"nome": "Marco", "cognome": "Rossi", "genere": "uomo", "trans": False, "nascita": "1988-08-07"},
})


def _prefisso(conoscenza, registro, categoria):
    return cag.prefisso(conoscenza, registro.istruzioni_per("sintesi", categoria), categoria)


# ---- il prefisso: lo standard non cambia, le speciali hanno il loro -------------------------


def test_il_prefisso_della_lettura_standard_e_identico_a_prima(conoscenza, registro):
    standard = _prefisso(conoscenza, registro, "standard")
    assert hashlib.sha256(standard.encode("utf-8")).hexdigest() == IMPRONTA_PREFISSO_STANDARD
    assert standard == cag.prefisso(conoscenza, registro.istruzioni_per("sintesi"))   # il default è lo standard


def test_i_tre_prefissi_sono_distinti_e_ciascuno_e_stabile(conoscenza, registro):
    prefissi = {c: _prefisso(conoscenza, registro, c) for c in ("standard", "compatibilita", "coppia")}
    assert len(set(prefissi.values())) == 3
    for categoria, atteso in prefissi.items():
        assert _prefisso(conoscenza, registro, categoria) == atteso


def test_i_prefissi_speciali_hanno_il_formato_e_le_regole_ma_non_le_stese(conoscenza, registro):
    compat = _prefisso(conoscenza, registro, "compatibilita")
    coppia = _prefisso(conoscenza, registro, "coppia")
    assert "## L'incontro dei segni" in compat and "## Ciò che vi lega" not in compat
    assert "## Ciò che vi lega e ciò che vi mette alla prova" in coppia and "## L'incontro dei segni" not in coppia
    for prefisso in (compat, coppia):
        assert "Regole per le letture di compatibilità e di coppia" in prefisso
        assert "## Il quadro" in prefisso and "450-750 parole" in prefisso
        assert "Non dare verdetti" in prefisso                                  # il guardrail «relazioni»
        for stesa in conoscenza.stese.values():
            assert stesa["descrizione"] not in prefisso
        for carta in conoscenza.carte.values():
            assert carta["dritto"] not in prefisso
    standard = _prefisso(conoscenza, registro, "standard")
    assert "Regole per le letture di compatibilità" not in standard and "Non dare verdetti" not in standard


def test_il_guardrail_relazioni_non_tocca_la_lettura_standard(registro):
    assert "relazioni" not in {g.slug for g in registro.per("sintesi", "standard")}
    assert "relazioni" in {g.slug for g in registro.per("sintesi", "coppia")}
    assert "relazioni" in {g.slug for g in registro.per("interpretazione", "compatibilita")}
    assert "relazioni" in {g.slug for g in registro.per("intervista", "coppia")}


def test_le_interpretazioni_speciali_ricevono_solo_le_regole_di_categoria(registro):
    assert registro.istruzioni_per("interpretazione", "standard", solo_categoria=True) == []
    solo = registro.istruzioni_per("interpretazione", "coppia", solo_categoria=True)
    assert len(solo) == 1 and "Non dare verdetti" in solo[0]
    tutte = registro.istruzioni_per("interpretazione", "coppia")
    assert len(tutte) > len(solo)


def test_un_guardrail_con_categorie_vale_solo_per_quelle():
    g = interpreta(
        "---\nslug: prova\nnome: Prova\ncategorie: [coppia]\napplica_a: [sintesi]\n---\n\n## Istruzioni\n\nX\n"
    )
    assert isinstance(g, Guardrail)
    assert g.vale_per("sintesi", "coppia") and not g.vale_per("sintesi", "standard")
    assert not g.vale_per("sintesi", "compatibilita") and not g.vale_per("intervista", "coppia")
    libero = interpreta("---\nslug: libero\nnome: Libero\n---\n\n## Istruzioni\n\nX\n")
    assert libero.vale_per("sintesi", "standard") and libero.vale_per("intervista", "coppia")


# ---- la parte variabile della sintesi --------------------------------------------------------


def _variabile(conoscenza, stesa_id, con_persone=True):
    stesa = conoscenza.stesa(stesa_id)
    ids = conoscenza.mazzo_per(stesa)[: len(stesa["posizioni"])]
    carte = [
        {"card_id": cid, "rovescio": i % 2 == 0, "posizione": i + 1, "calcolata": False, "interpretazione": f"Lettura {i + 1}."}
        for i, cid in enumerate(ids)
    ]
    soggetti = {p["n"]: soggetto_testo(p["soggetto"], PERSONE) for p in stesa["posizioni"]} if con_persone else None
    return cag.parte_variabile(
        conoscenza=conoscenza, stesa=stesa, quesito="Compatibilità con Marco", contesto="Quadro.",
        carte=carte, dignita={}, prevalenze={}, colloquio="Oracolo: Da quanto?\nChi consulta: Da un mese.",
        persone=blocco_persone(PERSONE, conoscenza) if con_persone else "",
        compatibilita=blocco_compatibilita(PERSONE, conoscenza) if con_persone else "",
        soggetti=soggetti,
    )


def test_la_sintesi_speciale_ha_le_persone_la_compatibilita_e_il_soggetto_di_ogni_posizione(conoscenza):
    testo = _variabile(conoscenza, "coppia-specchio")
    assert "## Le persone" in testo and "## Compatibilità zodiacale (calcolata dal sistema, non da te)" in testo
    assert "«Marco» (l'altra persona)" in testo and "Rossi" not in testo
    assert testo.count("Riguarda: ") == 8
    assert "Riguarda: chi consulta (tu)" in testo and "Riguarda: la relazione fra chi consulta e «Marco»" in testo


def test_il_soggetto_sta_in_coda_alla_catena_e_non_sposta_le_posizioni(conoscenza):
    testo = _variabile(conoscenza, "coppia-bivio")
    sezione = testo.split("## Ordine del racconto", 1)[1].split("\n## ", 1)[0]
    righe = [r for r in sezione.splitlines() if re.match(r"\d+\. ", r)]
    assert [int(re.search(r"\(posizione (\d+)\)", r).group(1)) for r in righe] == [2, 1, 3, 4, 5, 6, 7, 8]
    for riga in righe:
        assert riga.rstrip().endswith("]") and "[riguarda: " in riga
        assert riga.index("(posizione") < riga.index("[riguarda:")
    assert "[riguarda: la Strada A" in righe[2] and "[riguarda: la Strada B" in righe[5]


def test_senza_persone_la_sintesi_e_quella_di_prima(conoscenza):
    testo = _variabile(conoscenza, "tre-carte", con_persone=False)
    assert "## Le persone" not in testo and "Riguarda:" not in testo and "[riguarda" not in testo


# ---- l'interpretazione di una carta --------------------------------------------------------------


def _msg(conoscenza, stesa_id, n, **extra):
    stesa = conoscenza.stesa(stesa_id)
    return interpretazione.messaggio(
        carta=conoscenza.carta("maj-07"), rovescio=True, stesa=stesa,
        posizione=conoscenza.posizione(stesa, n), quesito="Compatibilità con Marco",
        contesto="Quadro.", **extra,
    )


def test_il_messaggio_speciale_ha_il_soggetto_subito_dopo_la_posizione(conoscenza):
    stesa = conoscenza.stesa("coppia-stazione")
    for p in stesa["posizioni"]:
        testo = _msg(
            conoscenza, "coppia-stazione", p["n"],
            persone=blocco_persone(PERSONE, conoscenza), soggetto=soggetto_testo(p["soggetto"], PERSONE),
        )
        righe = testo.splitlines()
        i = next(k for k, r in enumerate(righe) if r.startswith(f"Posizione {p['n']}:"))
        assert righe[i + 1] == f"Questa posizione riguarda: {soggetto_testo(p['soggetto'], PERSONE)}"
        assert righe[i + 2] == "Orientamento: rovesciata"
        assert testo.count("Orientamento:") == 1 and "## Le persone" in testo and "Rossi" not in testo
        assert "Compatibilità zodiacale" not in testo    # nell'interpretazione bastano le persone


def test_senza_soggetto_il_messaggio_e_identico_a_prima(conoscenza):
    con = _msg(conoscenza, "tre-carte", 2)
    assert "Questa posizione riguarda" not in con and "## Le persone" not in con
    assert con == _msg(conoscenza, "tre-carte", 2, persone="", soggetto="")


def test_il_prompt_di_relazione_non_ha_l_intestazione_del_compito():
    # `finto._compito` e i fornitori leggono il PRIMO messaggio di sistema: il secondo non deve ridefinirlo.
    assert "# Compito:" not in interpretazione.PROMPT_INTERPRETAZIONE_RELAZIONE
    assert "# Compito: interpretazione" in interpretazione.PROMPT_INTERPRETAZIONE
    assert "# Compito:" not in PROMPT_INTERVISTA_RELAZIONE


@pytest.mark.parametrize("testo", [interpretazione.PROMPT_INTERPRETAZIONE_RELAZIONE, PROMPT_INTERVISTA_RELAZIONE, cag._REGOLE_RELAZIONE])
def test_i_prompt_di_relazione_dichiarano_le_regole_di_genere_e_del_terzo(testo):
    minuscolo = testo.lower()
    assert "orientamento" in minuscolo
    assert "cognom" in minuscolo or "stereotip" in minuscolo or "non chiedere" in minuscolo


def test_i_prompt_di_relazione_non_usano_pronomi_di_genere():
    for testo in (interpretazione.PROMPT_INTERPRETAZIONE_RELAZIONE, PROMPT_INTERVISTA_RELAZIONE, cag._REGOLE_RELAZIONE,
                  cag._FORMATO_COMPATIBILITA, cag._FORMATO_COPPIA):
        assert not re.search(r"\b(lui|lei|egli|ella)\b", testo, re.IGNORECASE), testo[:60]


# ---- l'intervista ----------------------------------------------------------------------------------


@pytest.mark.parametrize("domanda", [
    "Cosa pensa di te l'altra persona?",
    "Che cosa prova lui per te?",
    "Cosa vuole davvero lei da questa storia?",
    "Quanto ti ama il tuo partner?",
    "Secondo te lei prova ancora qualcosa?",
    "Pensi che lui ti ami ancora?",
    "What does he think of you?",
    "Do you think she still loves you?",
])
def test_nelle_letture_di_relazione_si_scartano_le_domande_sul_mondo_interiore_dell_altro(domanda):
    assert viola_le_regole("Compatibilità con Marco", domanda, categoria="coppia") is not None


@pytest.mark.parametrize("domanda", [
    "Da quanto tempo conoscete Marco?",
    "Come vi siete conosciuti?",
    "Cosa è successo di recente fra voi?",
    "Come ti senti quando siete lontani?",
    "Come si comporta l'altra persona quando siete insieme?",
    "Cosa desideri da questa relazione?",
    "Qual è la cosa che ti preoccupa di più?",
])
def test_le_domande_di_contesto_passano_anche_nelle_letture_di_relazione(domanda):
    neutre = parole_neutre(PERSONE)
    assert viola_le_regole("Compatibilità con Marco", domanda, categoria="compatibilita", neutre=neutre) is None


def test_le_domande_sul_terzo_non_si_scartano_nella_lettura_standard():
    # La regola è delle letture di relazione: altrove «cosa pensa il mio capo?» non è un problema di questo controllo.
    assert viola_le_regole("Otterrò la promozione?", "Cosa pensa di te il tuo capo?") is None


@pytest.mark.parametrize("quesito, domanda", [
    ("Relazione di coppia con Marco", "Da quanto siete in relazione con Marco?"),
    ("Relazione con Marco", "Da quanto siete in relazione con Marco?"),
    ("Compatibilità con Marco", "Com'è la vostra compatibilità con Marco?"),
])
def test_il_nome_del_partner_non_conta_come_ricalco_del_quesito(quesito, domanda):
    # Il quesito generato dal frontend è «Relazione di coppia con Marco»: senza parole neutre
    # una domanda naturale sulla relazione lo ricalcherebbe, e prima del minimo di 2 domande
    # tre scarti fanno scattare il 503.
    assert ricalca_il_quesito(quesito, domanda) is True                                   # senza parole neutre: scartata
    assert ricalca_il_quesito(quesito, domanda, neutre=parole_neutre(PERSONE)) is False   # con: passa
    # Il ricalco vero resta scartato.
    assert ricalca_il_quesito("Il mio ragazzo mi ama?", "Il tuo ragazzo ti ama?", neutre=parole_neutre(PERSONE)) is True


async def test_l_intervista_speciale_riceve_le_regole_di_relazione_e_la_nota():
    visti = []

    class Spia(Copione):
        async def complete_json(self, req):
            visti.append(req)
            return await super().complete_json(req)

    passo = await prossimo_passo(
        provider_intervista=Spia([{"completo": False, "domanda": "Da quanto conoscete Marco?"}]),
        provider_validazione=Spia([{"valida": True}]),
        quesito="Compatibilità con Marco", stesa_nome="Bivio", turni=[], max_domande=5,
        categoria="coppia", nota="Chiarisci le due strade.", parole_neutre=parole_neutre(PERSONE),
        profilo=blocco_persone(PERSONE, Conoscenza.carica()) + "\n",
    )
    assert passo.domanda == "Da quanto conoscete Marco?" and passo.scartate == 0
    intervista, validazione = visti
    sistemi = [m.content for m in intervista.messages if m.role == "system"]
    assert sistemi[0].startswith("# Compito: intervista") and sistemi[1] == PROMPT_INTERVISTA_RELAZIONE
    utente = [m.content for m in intervista.messages if m.role == "user"][-1]
    assert "Nota sulla stesa: Chiarisci le due strade." in utente and "## Le persone" in utente and "Rossi" not in utente
    sistemi_validatore = [m.content for m in validazione.messages if m.role == "system"]
    assert sistemi_validatore[0].startswith("# Compito: validazione") and "cosa pensa, prova, vuole" in sistemi_validatore[1]


async def test_l_intervista_standard_non_riceve_le_regole_di_relazione():
    visti = []

    class Spia(Copione):
        async def complete_json(self, req):
            visti.append(req)
            return await super().complete_json(req)

    await prossimo_passo(
        provider_intervista=Spia([{"completo": False, "domanda": "Da quanto tempo lavori lì?"}]),
        provider_validazione=Spia([{"valida": True}]),
        quesito="Devo cambiare lavoro?", stesa_nome="Tre carte", turni=[], max_domande=5,
    )
    for req in visti:
        sistemi = [m.content for m in req.messages if m.role == "system"]
        assert len(sistemi) == 1 and "Regole aggiuntive" not in sistemi[0]


async def test_una_domanda_sul_terzo_si_rigenera_nelle_letture_di_relazione():
    intervista = Copione([
        {"completo": False, "domanda": "Cosa prova lui per te?"},
        {"completo": False, "domanda": "Come vi siete conosciuti?"},
    ])
    passo = await prossimo_passo(
        provider_intervista=intervista, provider_validazione=Copione([{"valida": True}]),
        quesito="Compatibilità con Marco", stesa_nome="Croce", turni=[], max_domande=5,
        categoria="coppia", parole_neutre=parole_neutre(PERSONE),
    )
    assert passo.domanda == "Come vi siete conosciuti?" and passo.scartate == 1
