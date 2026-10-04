"""L'anteprima per chi non è registrato ha un compito suo (`Compito.TEASER`): senza assegnazione usa il modello della
sintesi ma col ragionamento spento, e non eredita il livello (`xhigh`) della sintesi; dalla console si può scegliere
modello e livello come per gli altri compiti."""
from __future__ import annotations

from tarot_core.llm import ragionamento
from tarot_core.llm.compiti import Compito, ModelloConfigurato, RegistroModelli

from .conftest import eventi_sse, richiede_database


def _registro() -> RegistroModelli:
    registro = RegistroModelli([
        ModelloConfigurato(nome="a-predefinito", base_url="http://a/v1", model="m", tipo="nebius",
                           livello_ragionamento="medium"),
        ModelloConfigurato(nome="b-sintesi", base_url="http://b/v1", model="m", tipo="nebius",
                           livello_ragionamento="medium"),
    ])
    registro.assegna(Compito.SINTESI, "b-sintesi", livello="xhigh")
    return registro


def test_senza_assegnazione_usa_il_modello_della_sintesi_senza_ragionare():
    registro = _registro()
    assert registro.nome_per(Compito.TEASER) == "b-sintesi"              # non il predefinito
    teaser = registro.per(Compito.TEASER)
    assert teaser.ragiona is False and teaser.livello_ragionamento == "none"
    assert teaser._parametri["reasoning_effort"] == "none"
    assert teaser._tetto(200) == 200                                       # nessun margine di ragionamento
    sintesi = registro.per(Compito.SINTESI)
    assert sintesi._tetto(2600) == 2600 + ragionamento.MARGINE_LIVELLO["xhigh"]


def test_la_console_lo_mostra_e_lo_spiega():
    riga = next(r for r in _registro().stato() if r["compito"] == "teaser")
    assert riga["assegnato"] is None and riga["in_uso"] == "b-sintesi"
    assert riga["livello_effettivo"] == "none" and riga["ragiona_effettivo"] is False
    assert riga["ragiona_origine"] == "predefinito" and riga["ragiona_spegnibile"] is True
    assert riga["livello_predefinito"] == "none" and riga["segue"] == "sintesi"
    # Gli altri compiti non cambiano: ereditano dal fornitore e seguono il predefinito.
    oracolo = next(r for r in _registro().stato() if r["compito"] == "chat_proattiva")
    assert oracolo["livello_predefinito"] is None and oracolo["segue"] is None
    assert oracolo["ragiona_origine"] == "fornitore" and oracolo["livello_effettivo"] == "medium"


def test_dalla_console_si_sceglie_modello_e_livello():
    registro = _registro()
    registro.assegna(Compito.TEASER, "a-predefinito", livello="low")
    teaser = registro.per(Compito.TEASER)
    assert registro.nome_per(Compito.TEASER) == "a-predefinito"
    assert teaser.ragiona and teaser.livello_ragionamento == "low"
    assert registro.ragionamento_di(Compito.TEASER)["origine"] == "compito"
    # Un'assegnazione senza livello (solo il modello) tiene il predefinito del compito, non quello del fornitore.
    registro.assegna(Compito.TEASER, "a-predefinito")
    assert registro.per(Compito.TEASER).livello_ragionamento == "none"
    assert registro.ragionamento_di(Compito.TEASER)["origine"] == "predefinito"
    # Tolta l'assegnazione, torna al modello della sintesi.
    registro.assegna(Compito.TEASER, None)
    assert registro.nome_per(Compito.TEASER) == "b-sintesi"


@richiede_database
async def test_la_lettura_anonima_chiede_l_anteprima_al_suo_compito(client, session, monkeypatch):
    from tarot_core.api.routers import readings

    chiesti = []
    originale = readings.provider_per

    def spia(compito, *argomenti, **opzioni):
        chiesti.append(compito)
        return originale(compito, *argomenti, **opzioni)

    monkeypatch.setattr(readings, "provider_per", spia)
    client.identita.principal = None
    r = await client.post("/readings/anonime", json={"spread_id": "tre-carte", "question": "Come andrà il lavoro?"})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    r = await client.post(f"/readings/{rid}/interview", json={})
    while not r.json().get("completa"):
        r = await client.post(f"/readings/{rid}/interview", json={"risposta": "Da qualche mese."})
    await client.post(f"/readings/{rid}/fan")
    for slot in range(3):
        await client.post(f"/readings/{rid}/pick", json={"slot": slot})
    await client.post(f"/readings/{rid}/reveal-all")
    eventi = eventi_sse((await client.post(f"/readings/{rid}/synthesis")).text)
    assert next(d for e, d in eventi if e == "fine")["anonimo"] is True
    assert Compito.TEASER in chiesti
