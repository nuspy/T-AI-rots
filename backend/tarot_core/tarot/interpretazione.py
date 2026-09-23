"""L'interpretazione immediata di una carta appena girata.

Si legge **la carta in quella posizione**, non la carta in astratto: lo stesso
Tre di Spade dice cose diverse come «passato recente» e come «esito». Entrano
nel prompt la voce del mazzo, il significato della posizione nella stesa,
l'orientamento, la dignità rispetto alle vicine già rivelate e il quadro
emerso dall'intervista.

Le vicine non ancora rivelate non entrano: la dignità si calcola solo con ciò
che l'utente ha già visto, altrimenti l'interpretazione anticiperebbe carte
ancora coperte.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .testi import lingua

PROMPT_INTERPRETAZIONE = """# Compito: interpretazione

Sei l'oracolo di T-AI-rots, lettore rigoroso del Tarocco di Thoth di Aleister
Crowley. Interpreti UNA carta appena girata, nella sua posizione della stesa.

Come interpretare:
- Parti dal significato della posizione nella stesa e leggi la carta attraverso
  di essa.
- Usa i livelli di significato della carta (essoterico, psicologico,
  iniziatico) e i suoi riferimenti (lettera ebraica, percorso, sefira,
  astrologia, elemento) quando illuminano il senso, senza fare lezione.
- Se la carta è rovesciata, leggila come espressione bloccata, interiorizzata,
  ritardata o eccessiva della sua energia, mai come il suo contrario banale.
- Se la dignità è indicata, tienine conto: ben dignificata esprime il lato
  luminoso, mal dignificata il lato d'ombra.
- Collega la carta al quesito e al contesto emerso dall'intervista.
- 3-5 frasi, in seconda persona, tono serio, caldo, evocativo ma chiaro.
- Mai fatalismo: parla di tendenze e forze, non di sentenze. Niente diagnosi,
  consigli medici, legali o finanziari. Niente certezze sui sentimenti altrui.
- Non anticipare il responso finale: questa è la lettura di una sola carta.
- Scrivi solo il testo dell'interpretazione, senza titoli né elenchi.
"""


def _voce(carta: Dict[str, Any]) -> str:
    righe = [
        f"Carta: {carta['nome_it']} ({carta['nome_thoth']})",
    ]
    if carta.get("lettera_ebraica"):
        lettera = carta["lettera_ebraica"]
        collega = " – ".join(carta.get("collega") or [])
        righe.append(
            f"Lettera ebraica: {lettera.get('nome')} {lettera.get('glifo')} — "
            f"percorso {carta.get('percorso')} ({collega})"
        )
    if carta.get("sefira"):
        righe.append(f"Sefira: {carta['sefira']}")
    righe.append(f"Elemento: {carta.get('elemento')} · Astrologia: {carta.get('astrologia')}")
    righe.append(f"Parole chiave: {', '.join(carta.get('parole_chiave') or [])}")
    s = carta.get("significati") or {}
    for livello in ("essoterico", "psicologico", "iniziatico", "ombra"):
        if s.get(livello):
            righe.append(f"Significato {livello}: {s[livello]}")
    righe.append(f"Dritta: {carta.get('dritto')}")
    righe.append(f"Rovesciata: {carta.get('rovescio')}")
    ambiti = carta.get("ambiti") or {}
    for k, v in ambiti.items():
        righe.append(f"Ambito {k}: {v}")
    if carta.get("nota_crowley"):
        righe.append(f"Nota su Crowley: {carta['nota_crowley']}")
    return "\n".join(righe)


def messaggio(
    *,
    carta: Dict[str, Any],
    rovescio: bool,
    stesa: Dict[str, Any],
    posizione: Dict[str, Any],
    quesito: str,
    contesto: str,
    dignita: Optional[Dict[str, Any]] = None,
    precedenti: str = "",
    doppia_valenza: bool = False,
    lang: str = "it",
) -> str:
    parti = [
        f"Quesito: {quesito}",
        f"Contesto emerso dall'intervista: {contesto or 'non disponibile'}",
        "",
        f"Stesa: {stesa['nome']} — {stesa['descrizione']}",
        f"Posizione {posizione['n']}: {posizione['nome']} — {posizione['significato']}",
        f"Orientamento: {'rovesciata' if rovescio else 'dritta'}",
    ]
    if posizione.get("calcolata"):
        parti.append(
            "Questa carta non è stata scelta: è la sintesi calcolata (somma "
            "teosofica degli Arcani della stesa)."
        )
    if doppia_valenza:
        parti.append(
            "Doppia valenza: questo Arcano è già presente nella stesa, il suo "
            "messaggio è rafforzato ed è la chiave della lettura."
        )
    if dignita and dignita.get("relazioni"):
        rel = ", ".join(
            f"posizione {r['posizione']} ({r['elemento']}): {r['relazione']}"
            for r in dignita["relazioni"]
        )
        parti.append(f"Dignità elementale rispetto alle carte già rivelate: {dignita['giudizio']} ({rel})")
    if precedenti:
        parti.append(f"Carte già rivelate:\n{precedenti}")
    parti += ["", _voce(carta), "",
              "Scrivi in inglese." if lingua(lang) == "en" else "Scrivi in italiano."]
    return "\n".join(parti)
