"""Cosa si passa al modello di una carta e di una posizione: solo ciò che serve.

**Il codice sceglie, il modello non cerca.** Quale carta è uscita, in quale
posizione e in quale orientamento lo sa il codice; il modello riceve già i
valori di *quella* posizione per *quella* posa, e nient'altro. Non riceve i
significati delle altre carte, né quelli delle altre posizioni, né quelli
dell'orientamento che non è uscito: costano token, rallentano l'inferenza e sono
il posto in cui il modello sbaglia — legge il «rovesciato» a una carta dritta,
o attribuisce a una posizione il significato di un'altra.

Questo modulo decide, in modo deterministico, quali campi della scheda di una
carta entrano nel messaggio:

- dritta: il significato dritto e i tre livelli (essoterico, psicologico,
  iniziatico);
- rovesciata: il significato rovesciato, l'ombra e il significato di base, che
  è l'energia che si blocca, si interiorizza o eccede.

Sono comuni a entrambe le pose i riferimenti (lettera, percorso, sefira,
elemento, astrologia), le parole chiave, gli ambiti e la nota su Crowley.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List


def _riga(etichetta: str, valore: Any) -> List[str]:
    return [f"{etichetta}: {valore}"] if valore else []


def scheda(carta: Dict[str, Any], rovescio: bool) -> str:
    """La scheda di una carta per l'orientamento estratto."""
    righe = [f"Carta: {carta['nome_it']} ({carta['nome_thoth']})"]
    if carta.get("lettera_ebraica"):
        lettera = carta["lettera_ebraica"]
        collega = " – ".join(carta.get("collega") or [])
        righe.append(
            f"Lettera ebraica: {lettera.get('nome')} {lettera.get('glifo')} — "
            f"percorso {carta.get('percorso')} ({collega})"
        )
    righe += _riga("Sefira", carta.get("sefira"))
    righe.append(f"Elemento: {carta.get('elemento')} · Astrologia: {carta.get('astrologia')}")
    righe += _riga("Parole chiave", ", ".join(carta.get("parole_chiave") or []))

    livelli = carta.get("significati") or {}
    if rovescio:
        righe += _riga("Significato di base (l'energia che qui si blocca, si interiorizza o eccede)", livelli.get("essoterico"))
        righe += _riga("Significato da rovesciata", carta.get("rovescio"))
        righe += _riga("Lato d'ombra", livelli.get("ombra"))
    else:
        righe += _riga("Significato da dritta", carta.get("dritto"))
        for livello in ("essoterico", "psicologico", "iniziatico"):
            righe += _riga(f"Livello {livello}", livelli.get(livello))

    for ambito, testo in (carta.get("ambiti") or {}).items():
        righe.append(f"Ambito {ambito}: {testo}")
    righe += _riga("Nota su Crowley", carta.get("nota_crowley"))
    return "\n".join(righe)


def valore_sintetico(carta: Dict[str, Any], rovescio: bool, *, massimo: int = 150) -> str:
    """Il valore della carta in quell'orientamento, in una frase.

    È la prima frase del significato dritto o rovesciato del mazzo: serve a
    tenere il filo del racconto («stasi», «rovina», «fine di un periodo»…) senza
    ripetere la scheda intera.
    """
    testo = (carta.get("rovescio") if rovescio else carta.get("dritto")) or ""
    prima = re.split(r"(?<=[.!?])\s", testo.strip(), maxsplit=1)[0]
    if len(prima) > massimo:
        prima = prima[: massimo - 1].rsplit(" ", 1)[0] + "…"
    return prima
