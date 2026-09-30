"""Le collezioni standard di TAROTS chat (v8): gruppi di interrogazioni già pronte.

Servono a tre cose con la stessa definizione: l'export «collezione» dalla console (un file Excel con
un foglio per interrogazione), il rapporto email della domenica, e i dati per Colab. Ogni voce è
`(nome del foglio, interrogazione, descrizione)`.
"""
from __future__ import annotations

from datetime import date
from typing import Callable, Dict, List, Tuple

from lanterna.interroga import Interrogazione

Voce = Tuple[str, Interrogazione, str]


def _q(da: date, a: date, sorgente: str, misure: List[str], dimensioni: List[str] = (), **altro) -> Interrogazione:
    return Interrogazione(sorgente=sorgente, misure=list(misure), dimensioni=list(dimensioni), da=da, a=a, **altro)


def traffico(da: date, a: date) -> List[Voce]:
    m = ["sessioni", "visitatori", "pagine", "tasso_coinvolgimento", "tempo_medio"]
    return [
        ("Visite al giorno", _q(da, a, "visite", m, granularita="giorno", limite=1000), "giorni italiani"),
        ("Canali", _q(da, a, "visite", m, ["canale"], confronto="precedente"), "col periodo precedente"),
        ("Siti di provenienza", _q(da, a, "visite", ["sessioni", "tasso_coinvolgimento"], ["referrer"], limite=50), ""),
        ("Campagne", _q(da, a, "visite", ["sessioni", "utenti", "tasso_coinvolgimento"], ["campagna", "sorgente_utm"], limite=100), ""),
        ("Paesi", _q(da, a, "visite", ["sessioni", "visitatori"], ["paese"], limite=50), "stimati dall'IP"),
        ("Dispositivi", _q(da, a, "visite", m, ["dispositivo", "so"]), ""),
        ("Nuovi e di ritorno", _q(da, a, "visite", ["sessioni", "giorni_tra_visite"], ["tipo_visitatore"]),
         "ritorni riconoscibili solo con accesso o cookie"),
        ("Pagine d'ingresso", _q(da, a, "visite", ["sessioni", "tasso_coinvolgimento"], ["ingresso"], limite=50), ""),
        ("Pagine più viste", _q(
            da, a, "eventi", ["eventi", "sessioni"], ["percorso"], limite=50,
            filtri=[{"dimensione": "nome", "valori": ["page_view"]}],
        ), ""),
        ("Azioni", _q(
            da, a, "eventi", ["eventi", "sessioni", "utenti"], ["nome"], limite=100,
            filtri=[{"dimensione": "nome", "operatore": "non_in", "valori": ["page_view", "engagement"]}],
        ), "tutto tranne pagine viste e tempo attivo"),
    ]


def utenti(da: date, a: date) -> List[Voce]:
    m = ["utenti", "eta_media", "attivi_30g"]
    return [
        ("Iscritti al giorno", _q(da, a, "utenti", ["utenti"], granularita="giorno", limite=1000), ""),
        ("Fasce d'età", _q(da, a, "utenti", m, ["fascia_eta"]), ""),
        ("Genere", _q(da, a, "utenti", m, ["genere"]), ""),
        ("Età e genere", _q(da, a, "utenti", ["utenti"], ["fascia_eta", "genere"], limite=100), ""),
        ("Primo canale", _q(da, a, "utenti", m, ["primo_canale"]), "per chi si è iscritto con gli analytics attivi"),
        ("Prima campagna", _q(da, a, "utenti", m, ["prima_campagna", "prima_sorgente"], limite=100), ""),
        ("Paese", _q(da, a, "utenti", ["utenti"], ["paese"], limite=50), "dall'ultima visita con l'accesso"),
        ("Visite prima di iscriversi", _q(da, a, "utenti", ["utenti"], ["visite_prima_fascia"]), "solo con i cookie accettati"),
    ]


def ricavi(da: date, a: date) -> List[Voce]:
    m = ["ricavi", "acquisti", "clienti", "valore_medio"]
    return [
        ("Acquisti al giorno", _q(da, a, "acquisti", m, granularita="giorno", limite=1000), ""),
        ("Per piano", _q(da, a, "acquisti", m, ["piano"], confronto="precedente"), ""),
        ("Per primo canale", _q(da, a, "acquisti", m, ["primo_canale"]), ""),
        ("Per prima campagna", _q(da, a, "acquisti", m, ["prima_campagna"], limite=100), ""),
        ("Per età e genere", _q(da, a, "acquisti", ["ricavi", "clienti"], ["fascia_eta", "genere"], limite=100), ""),
        ("Ordini del negozio", _q(da, a, "ordini", ["ricavi", "ordini", "clienti"], granularita="giorno", limite=1000), ""),
    ]


def letture(da: date, a: date) -> List[Voce]:
    m = ["letture", "completate", "tasso_completamento", "lettori"]
    return [
        ("Letture al giorno", _q(da, a, "letture", m, granularita="giorno", limite=1000), ""),
        ("Per stesa", _q(da, a, "letture", m, ["stesa"], confronto="precedente", limite=50), ""),
        ("Per pagamento", _q(da, a, "letture", m, ["consumo"]), "quota, credito, omaggio, anonima"),
        ("Per lingua", _q(da, a, "letture", m, ["lingua"]), ""),
        ("Si è avverato?", _q(da, a, "letture", ["con_feedback", "avverate"], ["feedback"]), ""),
    ]


def rapporto(da: date, a: date) -> List[Voce]:
    """Il rapporto settimanale: il meglio di ogni collezione, in poche pagine."""
    tutte = {titolo: voce for gruppo in (traffico, utenti, ricavi, letture) for voce in gruppo(da, a) for titolo in [voce[0]]}
    scelte = ["Visite al giorno", "Canali", "Nuovi e di ritorno", "Pagine più viste", "Iscritti al giorno", "Primo canale",
              "Per piano", "Per primo canale", "Per stesa"]
    return [tutte[titolo] for titolo in scelte]


COLLEZIONI: Dict[str, Tuple[str, Callable[[date, date], List[Voce]]]] = {
    "traffico": ("Traffico", traffico),
    "utenti": ("Utenti", utenti),
    "ricavi": ("Ricavi", ricavi),
    "letture": ("Letture", letture),
    "rapporto": ("Rapporto settimanale", rapporto),
}
