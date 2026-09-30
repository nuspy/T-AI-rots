"""Iniezione della memoria nel prompt dell'intervista e della sintesi (v6, Fase C): nessun database."""
from __future__ import annotations

import uuid

import pytest

from tarot_core.llm.base import GenerationRequest, Message
from tarot_core.tarot import cag
from tarot_core.tarot.conoscenza import Conoscenza
from tarot_core.tarot.intervista import prossimo_passo
from tarot_core.tarot.memoria_retrieval import MemoriaRilevante, formatta_per_sintesi


@pytest.fixture(scope="module")
def conoscenza() -> Conoscenza:
    return Conoscenza.carica()


def _memoria(contenuto: str, tipo: str = "stabile", campo: str = "salute") -> MemoriaRilevante:
    return MemoriaRilevante(id=uuid.uuid4(), contenuto=contenuto, tipo=tipo, campo_attinenza=campo, distanza=0.9)


# ---- sintesi: blocco iniettato nella parte variabile, prefisso invariato ---------------------------


def test_il_prefisso_resta_byte_identico_con_o_senza_memorie(conoscenza):
    p1 = cag.prefisso(conoscenza, ["Regola."])
    p2 = cag.prefisso(conoscenza, ["Regola."])
    assert p1 == p2


def test_la_parte_variabile_porta_il_blocco_memoria_quando_presente(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    carte = [
        {"card_id": cid, "rovescio": False, "posizione": i + 1, "calcolata": False, "interpretazione": ""}
        for i, cid in enumerate(conoscenza.mazzo_per(stesa)[:3])
    ]
    testo = cag.parte_variabile(
        conoscenza=conoscenza, stesa=stesa, quesito="q", contesto="c", carte=carte,
        dignita={}, prevalenze={}, memorie_rilevanti="- [STABILE — salute] gli manca una gamba",
    )
    assert "## Memoria: letture precedenti" in testo
    assert "gli manca una gamba" in testo


def test_la_parte_variabile_non_porta_la_sezione_memoria_se_vuota(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    carte = [
        {"card_id": cid, "rovescio": False, "posizione": i + 1, "calcolata": False, "interpretazione": ""}
        for i, cid in enumerate(conoscenza.mazzo_per(stesa)[:3])
    ]
    testo = cag.parte_variabile(
        conoscenza=conoscenza, stesa=stesa, quesito="q", contesto="c", carte=carte, dignita={}, prevalenze={},
    )
    assert "Memoria" not in testo


# ---- registro linguistico (v7, Fase F): blocco iniettato nella parte variabile ----------------------


def _carte_prova(conoscenza, stesa):
    return [
        {"card_id": cid, "rovescio": False, "posizione": i + 1, "calcolata": False, "interpretazione": ""}
        for i, cid in enumerate(conoscenza.mazzo_per(stesa)[:3])
    ]


def test_registro_quotidiano_aggiunge_l_istruzione(conoscenza):
    stesa = conoscenza.stesa("tre-carte")
    testo = cag.parte_variabile(
        conoscenza=conoscenza, stesa=stesa, quesito="q", contesto="c",
        carte=_carte_prova(conoscenza, stesa), dignita={}, prevalenze={}, registro="quotidiano",
    )
    assert "Registro linguistico richiesto: quotidiano" in testo


@pytest.mark.parametrize("registro", ["", "esoterico"])
def test_registro_esoterico_o_vuoto_non_cambia_il_prompt(conoscenza, registro):
    stesa = conoscenza.stesa("tre-carte")
    carte = _carte_prova(conoscenza, stesa)
    con_default = cag.parte_variabile(
        conoscenza=conoscenza, stesa=stesa, quesito="q", contesto="c", carte=carte, dignita={}, prevalenze={},
    )
    con_registro_esplicito = cag.parte_variabile(
        conoscenza=conoscenza, stesa=stesa, quesito="q", contesto="c", carte=carte, dignita={}, prevalenze={},
        registro=registro,
    )
    assert con_default == con_registro_esplicito
    assert "Registro linguistico" not in con_default


def test_formatta_per_sintesi_aggiunge_il_prima_per_le_variabili_con_storia():
    voci = [{"id": "abc", "contenuto": "ha trovato lavoro", "tipo": "variabile", "campo_attinenza": "lavoro"}]
    testo = formatta_per_sintesi(voci, {"abc": "cercava lavoro"})
    assert "ha trovato lavoro" in testo
    assert "prima si sapeva: cercava lavoro" in testo


def test_formatta_per_sintesi_senza_storia_non_aggiunge_il_prima():
    voci = [{"id": "abc", "contenuto": "gli manca una gamba", "tipo": "stabile", "campo_attinenza": "salute"}]
    testo = formatta_per_sintesi(voci, {})
    assert "prima si sapeva" not in testo


# ---- intervista: le memorie entrano nel prompt utente, mai in quello di sistema --------------------


class _ProviderCattura:
    """Cattura la richiesta invece di rispondere davvero: serve a leggere il prompt costruito."""

    def __init__(self, risposta):
        self.ultima: GenerationRequest | None = None
        self._risposta = risposta

    async def complete_json(self, req: GenerationRequest):
        self.ultima = req
        return self._risposta


async def test_le_memorie_entrano_nel_messaggio_utente_dell_intervista():
    # Un contenuto che non coincide con l'esempio già scritto nel prompt statico dell'intervista
    # ("gli manca una gamba"): altrimenti il test non distinguerebbe l'iniezione per-utente dal
    # testo fisso del prompt, che lo cita apposta come esempio.
    intervista_ = _ProviderCattura({"completo": False, "domanda": "Come sta il tuo progetto?"})
    validazione_ = _ProviderCattura({"valida": True, "motivo": ""})
    stabile = _memoria("soffre di emicrania cronica", tipo="stabile", campo="salute")
    await prossimo_passo(
        provider_intervista=intervista_, provider_validazione=validazione_,
        quesito="Come va il lavoro?", stesa_nome="Tre carte", turni=[],
        max_domande=6, memorie=[stabile],
    )
    utente = next(m.content for m in intervista_.ultima.messages if m.role == "user")
    assert "soffre di emicrania cronica" in utente
    assert "Cose già note su questa persona" in utente
    sistema = "\n".join(m.content for m in intervista_.ultima.messages if m.role == "system")
    assert "soffre di emicrania cronica" not in sistema


async def test_senza_memorie_non_compare_la_sezione():
    intervista_ = _ProviderCattura({"completo": False, "domanda": "Come sta il tuo progetto?"})
    validazione_ = _ProviderCattura({"valida": True, "motivo": ""})
    await prossimo_passo(
        provider_intervista=intervista_, provider_validazione=validazione_,
        quesito="Come va il lavoro?", stesa_nome="Tre carte", turni=[],
        max_domande=6,
    )
    utente = next(m.content for m in intervista_.ultima.messages if m.role == "user")
    assert "Cose già note" not in utente
