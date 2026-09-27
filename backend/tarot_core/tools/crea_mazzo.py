"""Descrizioni per le immagini di un mazzo di tarocchi NUOVO (v5, "mazzi multipli"): uno strumento
offline che scrive, con un LLM, la scena da dipingere per ogni carta — mai un endpoint, mai in
produzione. Come `traduci_conoscenza.py`, tutto quello che scrive è una bozza da rivedere a mano prima
di passare alla generazione vera dell'immagine.

    python -m tarot_core.tools.crea_mazzo campione --set Lovers --stile-file stile.md
    python -m tarot_core.tools.crea_mazzo campione --set Lovers --stile-file stile.md --cambia "meno rosso, piu' oro"
    python -m tarot_core.tools.crea_mazzo tutte --set Lovers
    python -m tarot_core.tools.crea_mazzo salva --set Lovers maj-06 C:\\Users\\...\\Downloads\\scaricata.png
    python -m tarot_core.tools.crea_mazzo salva --set Lovers dorso C:\\Users\\...\\Downloads\\dorso.png

**Identità esoterica invariata, scena nuova.** L'identità (lettera ebraica, percorso, sefira,
elemento, attribuzione astrologica, parole chiave) resta quella del mazzo Thoth in `deck.json` — è
ciò che il resto dell'app conosce di ogni carta. Solo la SCENA (cosa è dipinto) è scritta da zero
dall'LLM, adattata allo stile e all'ambientazione che l'operatore fornisce: non un restyle delle
scene di `knowledge/immagini/scene_*.py` (quelle restano quelle del mazzo Thoth), un'illustrazione
diversa della stessa identità.

**Stile senza dimensioni.** Il blocco di stile che l'operatore scrive non deve mai menzionare pixel o
rapporto d'aspetto: quelli si impostano nell'interfaccia dove l'immagine viene poi generata (v. skill
`crea-mazzo-tarocchi`), non nel prompt. Una scena che ci scivola dentro comunque è un errore di forma
(`SceneNonRiuscita`), come i campi mancanti in `traduci_conoscenza.py`.

**Due cancelli umani**: `campione` genera un fronte e il dorso, sempre da approvare (o correggere con
`--cambia`) prima di lanciare `tutte`; `tutte` scrive una bozza incrementale (`descrizioni.json`) e
non parte mai da zero — le carte già presenti (il campione approvato, o quelle di una corsa
precedente interrotta) restano intoccate, così un'interruzione a metà non perde il lavoro fatto e
rilanciare il comando prosegue da solo con quelle mancanti. La generazione dell'immagine vera (GPT
Image, nel browser) e il suo stesso cancello di approvazione restano fuori da questo script: sono un
lavoro interattivo, non automatizzabile in un comando.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image

from ..llm.compiti import Compito, RegistroModelli, modelli_da_impostazioni
from ..paths import PROJECT_ROOT
from ..tarot.conoscenza import Conoscenza
from ..tarot.llm import genera_json, richiesta
from .prompt_immagini import _identita, _testi  # riuso: stessa identità esoterica, stessa lingua

logger = logging.getLogger(__name__)

#: La cartella dove vivono i mazzi grafici, un livello sopra il repo del backend.
GRAFICA_DIR = PROJECT_ROOT.parent / "Grafica" / "Cards"

#: Carta di prova predefinita quando l'operatore non ne indica una: un Arcano maggiore qualunque,
#: scelto solo perché è quello dell'esempio discusso in sessione.
CARTA_CAMPIONE_PREDEFINITA = "maj-06"

#: Segnali che una dimensione in pixel o un rapporto d'aspetto si è infilato dove non deve: qui la
#: risoluzione e il formato si impostano nell'interfaccia di generazione, non nel prompt.
_VIETATO_DIMENSIONI = re.compile(
    r"\d+\s*[x×]\s*\d+\s*(px|pixel)?|aspect\s*ratio|\b\d{1,2}\s*:\s*\d{1,2}\b", re.IGNORECASE,
)

NEGATIVO_BASE = (
    "photograph, photorealistic, 3D render, CGI, anime, cartoon, comic style, flat vector clip art, "
    "watermark, signature, logo, extra text, captions, misspelled text, garbled letters, random "
    "letters, wrong card name, modern objects, cropped frame, missing border, low resolution, blurry, "
    "jpeg artifacts, deformed anatomy, extra limbs, extra fingers, nudity, gore, horror"
)

TESTO_CARTA = (
    "TEXT ON THE CARD (render it exactly, correctly spelled, perfectly legible, and write nothing "
    "else): in the upper text area, centred: \"{alto}\". In the lower title area, centred: \"{basso}\". "
    "Use a font, letter case, spacing and colour consistent with the style described above, identical "
    "across every card of this deck. Apart from these two lines, the only other marks allowed are the "
    "esoteric glyphs described in the scene, drawn as symbols inside the painting and not as captions."
)

TESTO_DORSO = (
    "TEXT ON THE CARD: none — no readable text, no card name, no numbers. A purely ornamental pattern, "
    "consistent with the style described above, symmetric enough that it reads correctly from either "
    "orientation (this exact design is printed identically on the back of all 78 cards of this deck)."
)

IDENTITA_DORSO = (
    "THE CARD: the shared back design, printed identically on the reverse of all 78 cards of this deck "
    "— it has no identity of its own, unlike the fronts."
)

PROMPT_SCENA_CARTA = """# Compito: inventare la scena di un'illustrazione per una carta di un mazzo di tarocchi nuovo

Sei un concept artist ed esperto di Tarocco di Thoth, Golden Dawn ed esoterismo. Questa carta ha
un'identità esoterica fissa (sotto, in inglese): non cambiarla. Il tuo compito è immaginare come
quell'identità si manifesta in un mazzo completamente nuovo, con lo stile e l'ambientazione che
l'operatore ha scelto.

{identita}

I colori indicati sopra sono un'attribuzione esoterica tradizionale: usali come accenti o dettagli
simbolici nella scena, non necessariamente come palette dominante — la palette dominante segue lo
stile del mazzo qui sotto.

STILE E AMBIENTAZIONE DEL MAZZO (fornito dall'operatore — seguilo per tecnica, palette, tono e mondo
immaginario; la scena deve viverci dentro, non limitarsi a citarlo):
{stile}
{feedback}
Scrivi, in inglese, una sola scena originale (indicativamente 120-220 parole) che dipinga la carta:
cosa si vede, chi/cosa è raffigurato, come i riferimenti esoterici sopra (lettera, pianeta/segno,
elemento) compaiono come simboli dipinti nella scena — non come etichette di testo. Non descrivere
alcuna scritta da rendere sulla carta (il nome lo aggiunge un altro blocco a parte) e non menzionare
mai dimensioni in pixel o rapporti d'aspetto.

Rispondi in JSON con questa forma esatta: {{"scena": "..."}}. Nessun testo prima o dopo il JSON."""

PROMPT_SCENA_DORSO = """# Compito: inventare il disegno del dorso condiviso di un mazzo di tarocchi nuovo

Sei un concept artist di tarocchi esoterici. Scrivi, in inglese, la descrizione di un motivo
ornamentale per il DORSO — lo stesso identico dorso stampato sul retro di tutte le 78 carte del
mazzo, quindi senza alcun riferimento a una carta specifica.

STILE E AMBIENTAZIONE DEL MAZZO (fornito dall'operatore):
{stile}
{feedback}
Scrivi una sola descrizione (indicativamente 80-160 parole): un motivo simmetrico o comunque privo di
un "verso giusto" (deve restare riconoscibile anche capovolto di 180 gradi), coerente con lo stile
sopra, senza alcun testo leggibile e senza il nome di nessuna carta. Non menzionare mai dimensioni in
pixel o rapporti d'aspetto.

Rispondi in JSON con questa forma esatta: {{"scena": "..."}}. Nessun testo prima o dopo il JSON."""


class SceneNonRiuscita(RuntimeError):
    """L'LLM non ha restituito una scena valida (vuota, o con dimensioni/rapporto infilati dentro)."""


def _valida_scena(scena: Any, *, chi: str) -> str:
    if not isinstance(scena, str) or not scena.strip():
        raise SceneNonRiuscita(f"{chi}: scena vuota o non testuale")
    if _VIETATO_DIMENSIONI.search(scena):
        raise SceneNonRiuscita(f"{chi}: la scena menziona una dimensione o un rapporto d'aspetto")
    return scena.strip()


def avverti_se_stile_ha_dimensioni(stile: str) -> Optional[str]:
    """Un avviso (non bloccante) se il blocco di stile scritto dall'operatore contiene già una
    dimensione o un rapporto d'aspetto — quelli si impostano nell'interfaccia di generazione."""
    if _VIETATO_DIMENSIONI.search(stile):
        return (
            "Attenzione: lo stile fornito sembra contenere una dimensione in pixel o un rapporto "
            "d'aspetto — verranno impostati nell'interfaccia di generazione dell'immagine, meglio "
            "toglierli dal testo dello stile."
        )
    return None


async def scrivi_scena_carta(provider: Any, carta: Dict[str, Any], stile: str, *, feedback: str = "") -> str:
    prompt = PROMPT_SCENA_CARTA.format(
        identita=_identita(carta), stile=stile.strip(),
        feedback=f"\nCORREZIONE RICHIESTA DALL'OPERATORE (tienine conto rispetto al tentativo precedente): {feedback}\n" if feedback else "",
    )
    dati = await genera_json(provider, richiesta([prompt], "Scrivi la scena.", temperatura=0.8, max_tokens=1024))
    return _valida_scena(dati.get("scena"), chi=carta["id"])


async def scrivi_scena_dorso(provider: Any, stile: str, *, feedback: str = "") -> str:
    prompt = PROMPT_SCENA_DORSO.format(
        stile=stile.strip(),
        feedback=f"\nCORREZIONE RICHIESTA DALL'OPERATORE (tienine conto rispetto al tentativo precedente): {feedback}\n" if feedback else "",
    )
    dati = await genera_json(provider, richiesta([prompt], "Scrivi il motivo del dorso.", temperatura=0.8, max_tokens=768))
    return _valida_scena(dati.get("scena"), chi="dorso")


def costruisci_prompt_carta(carta: Dict[str, Any], stile: str, scena: str) -> Dict[str, Any]:
    alto, basso, nome = _testi(carta)
    prompt = "\n\n".join([
        stile.strip(), _identita(carta),
        "SCENE (what is painted inside the frame): " + scena.strip(),
        TESTO_CARTA.format(alto=alto, basso=basso),
    ])
    return {
        "id": carta["id"], "name": nome, "top_text": alto, "bottom_text": basso,
        "scene": scena.strip(), "prompt": prompt, "negative_prompt": NEGATIVO_BASE,
    }


def costruisci_prompt_dorso(stile: str, scena: str) -> Dict[str, Any]:
    prompt = "\n\n".join([
        stile.strip(), IDENTITA_DORSO,
        "SCENE (the back design, no text): " + scena.strip(),
        TESTO_DORSO,
    ])
    return {"scene": scena.strip(), "prompt": prompt, "negative_prompt": NEGATIVO_BASE}


# ---------------------------------------------------------------------------------------- file I/O


def _cartella(nome_set: str) -> Path:
    return GRAFICA_DIR / nome_set


def _leggi_json(percorso: Path) -> Dict[str, Any]:
    if not percorso.exists():
        return {}
    try:
        return json.loads(percorso.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _scrivi_json(percorso: Path, dati: Dict[str, Any]) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(json.dumps(dati, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _aggiorna_manifest(cartella: Path, *, carta_id: Optional[str] = None, dorso: bool = False, campo: str = "descritta") -> None:
    percorso = cartella / "manifest.json"
    manifest = _leggi_json(percorso)
    manifest.setdefault("set", cartella.name)
    manifest.setdefault("carte", {})
    manifest.setdefault("dorso", {"descritta": False, "scaricata": False})
    manifest["aggiornato"] = datetime.now(timezone.utc).isoformat()
    if dorso:
        manifest["dorso"][campo] = True
    if carta_id:
        manifest["carte"].setdefault(carta_id, {"descritta": False, "scaricata": False})
        manifest["carte"][carta_id][campo] = True
    _scrivi_json(percorso, manifest)


# --------------------------------------------------------------------------------------- comandi


async def _provider() -> Any:
    """Il registro modelli dell'applicazione, fuori da una richiesta HTTP — stessa regola di
    `traduci_conoscenza.py`: fornitori dal database se ce ne sono, altrimenti dall'ambiente."""
    from ..domain.session import dispose_engine, get_session_factory

    fabbrica = get_session_factory()
    async with fabbrica() as session:
        try:
            from ..domain.admin_repositories import assegnazioni_correnti
            from ..domain.llm_repositories import modelli_da_db

            modelli = await modelli_da_db(session)
            assegnazioni_grezze = await assegnazioni_correnti(session)
        finally:
            await dispose_engine()
    modelli = modelli or modelli_da_impostazioni()
    registro = RegistroModelli(modelli, assegnazioni={
        c: assegnazioni_grezze[c.value] for c in Compito if assegnazioni_grezze.get(c.value)
    })
    return registro.per(Compito.CREAZIONE_MAZZO)


async def genera_campione(
    provider: Any, conoscenza: Conoscenza, stile: str, card_id: str, cartella: Path, *,
    feedback: str = "", solo: str = "entrambi",
) -> Dict[str, Any]:
    """Scrive (e restituisce) il campione in `descrizioni.json` dentro `cartella`. Pura rispetto alla
    riga di comando: chi chiama fornisce già `provider` e `cartella`, così è testabile con un modello
    finto e una cartella temporanea, come `traduci_conoscenza.esegui()`."""
    if card_id not in conoscenza.carte:
        raise KeyError(f"carta sconosciuta: {card_id}")
    descrizioni = _leggi_json(cartella / "descrizioni.json")
    descrizioni.setdefault("set", cartella.name)
    descrizioni.setdefault("carte", {})

    if solo in ("fronte", "entrambi"):
        scena = await scrivi_scena_carta(provider, conoscenza.carte[card_id], stile, feedback=feedback)
        descrizioni["carte"][card_id] = costruisci_prompt_carta(conoscenza.carte[card_id], stile, scena)
        _aggiorna_manifest(cartella, carta_id=card_id, campo="descritta")

    if solo in ("dorso", "entrambi"):
        scena_dorso = await scrivi_scena_dorso(provider, stile, feedback=feedback)
        descrizioni["dorso"] = costruisci_prompt_dorso(stile, scena_dorso)
        _aggiorna_manifest(cartella, dorso=True, campo="descritta")

    _scrivi_json(cartella / "descrizioni.json", descrizioni)
    return descrizioni


async def genera_tutte(
    provider: Any, conoscenza: Conoscenza, stile: str, cartella: Path, *,
    solo_carte: Optional[List[str]] = None, silenzioso: bool = False,
) -> Dict[str, List[str]]:
    """Scrive le carte restanti in `descrizioni.json`, una alla volta (bozza incrementale, come
    `traduci_conoscenza.esegui()`). Restituisce `{"ok": [...], "falliti": [...]}`.

    **Non parte mai da zero**: le carte già presenti (il campione approvato, o quelle di una corsa
    precedente interrotta) restano intoccate e si saltano — a differenza di
    `traduci_conoscenza.esegui()`, qui ripartire da zero per sbaglio vorrebbe dire buttare via un
    campione già approvato dall'operatore, non solo rifare una traduzione. Chi vuole rigenerare
    proprio quelle carte lo dice esplicitamente con `solo_carte`: un id nominato lì si rifà sempre,
    anche se già presente."""
    def stampa(msg: str) -> None:
        if not silenzioso:
            print(msg, file=sys.stderr)

    descrizioni = _leggi_json(cartella / "descrizioni.json")
    descrizioni.setdefault("set", cartella.name)
    carte_fatte = descrizioni.setdefault("carte", {})

    id_carte = solo_carte if solo_carte is not None else list(conoscenza.ordine)
    esito: Dict[str, List[str]] = {"ok": [], "falliti": []}
    for card_id in id_carte:
        if solo_carte is None and card_id in carte_fatte:
            stampa(f"carta {card_id}: già fatta, salto")
            continue
        try:
            scena = await scrivi_scena_carta(provider, conoscenza.carte[card_id], stile)
            carte_fatte[card_id] = costruisci_prompt_carta(conoscenza.carte[card_id], stile, scena)
            _scrivi_json(cartella / "descrizioni.json", descrizioni)
            _aggiorna_manifest(cartella, carta_id=card_id, campo="descritta")
            esito["ok"].append(card_id)
            stampa(f"carta {card_id}: fatta")
        except SceneNonRiuscita as exc:
            esito["falliti"].append(f"{card_id}: {exc}")
            stampa(f"carta {card_id}: FALLITA — {exc}")
    return esito


def salva_immagine(cartella: Path, id_o_dorso: str, file_scaricato: Path) -> Path:
    """Converte il file scaricato in WebP a piena risoluzione, col nome standard del mazzo, e
    aggiorna il manifest. Pura rispetto alla riga di comando."""
    if not file_scaricato.exists():
        raise FileNotFoundError(file_scaricato)
    nome_file = "dorso.webp" if id_o_dorso == "dorso" else f"{id_o_dorso}.webp"
    destinazione = cartella / nome_file
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(file_scaricato) as im:
        im.load()
        im.convert("RGB").save(destinazione, "WEBP", quality=95, method=6)
    _aggiorna_manifest(
        cartella, carta_id=None if id_o_dorso == "dorso" else id_o_dorso,
        dorso=(id_o_dorso == "dorso"), campo="scaricata",
    )
    return destinazione


async def _campione(args: argparse.Namespace) -> int:
    stile = Path(args.stile_file).read_text(encoding="utf-8")
    avviso = avverti_se_stile_ha_dimensioni(stile)
    if avviso:
        print(avviso, file=sys.stderr)

    conoscenza = Conoscenza.carica()
    card_id = args.carta or CARTA_CAMPIONE_PREDEFINITA
    if card_id not in conoscenza.carte:
        print(f"carta sconosciuta: {card_id}", file=sys.stderr)
        return 1

    cartella = _cartella(args.set)
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / "stile.md").write_text(stile, encoding="utf-8")

    provider = await _provider()
    descrizioni = await genera_campione(
        provider, conoscenza, stile, card_id, cartella, feedback=args.cambia or "", solo=args.solo,
    )

    if args.solo in ("fronte", "entrambi"):
        print(f"\n=== FRONTE — {card_id} ===\n{descrizioni['carte'][card_id]['prompt']}\n")
        print(f"--- negative prompt ---\n{NEGATIVO_BASE}\n")
    if args.solo in ("dorso", "entrambi"):
        print(f"\n=== DORSO ===\n{descrizioni['dorso']['prompt']}\n")
        print(f"--- negative prompt ---\n{NEGATIVO_BASE}\n")

    print(f"Scritto in {cartella / 'descrizioni.json'} — revisione umana prima di generare l'immagine.", file=sys.stderr)
    return 0


async def _tutte(args: argparse.Namespace) -> int:
    conoscenza = Conoscenza.carica()
    cartella = _cartella(args.set)
    percorso_stile = cartella / "stile.md"
    if not percorso_stile.exists():
        print(f"{percorso_stile} non esiste: lanciare prima 'campione' per fissare e approvare lo stile.", file=sys.stderr)
        return 1
    stile = percorso_stile.read_text(encoding="utf-8")

    if "dorso" not in _leggi_json(cartella / "descrizioni.json"):
        print("dorso non ancora descritto: lanciare prima 'campione' (anche solo --solo dorso).", file=sys.stderr)
        return 1

    id_carte = args.solo_carte.split(",") if args.solo_carte else None
    provider = await _provider()
    esito = await genera_tutte(provider, conoscenza, stile, cartella, solo_carte=id_carte)

    print(f"fatte: {len(esito['ok'])}  fallite: {len(esito['falliti'])}", file=sys.stderr)
    if esito["falliti"]:
        print("Rilanciare lo stesso comando per riprovare le carte fallite (non sono state scritte).", file=sys.stderr)
        return 1
    return 0


def _salva(args: argparse.Namespace) -> int:
    try:
        destinazione = salva_immagine(_cartella(args.set), args.id, Path(args.file_scaricato))
    except FileNotFoundError as exc:
        print(f"file non trovato: {exc}", file=sys.stderr)
        return 1
    with Image.open(destinazione) as salvata:
        print(f"salvata {destinazione} ({salvata.size[0]}x{salvata.size[1]})")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(prog="tarot_core.tools.crea_mazzo", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="comando", required=True)

    p_campione = sub.add_parser("campione", help="Descrive una carta di prova e il dorso, per approvazione.")
    p_campione.add_argument("--set", required=True, help="Nome del mazzo, es. 'Lovers' (nome della sua cartella).")
    p_campione.add_argument("--stile-file", required=True, help="File di testo con stile e ambientazione.")
    p_campione.add_argument("--carta", default=None, help=f"Id della carta di prova (default: {CARTA_CAMPIONE_PREDEFINITA}).")
    p_campione.add_argument("--cambia", default=None, help="Cosa correggere rispetto al tentativo precedente.")
    p_campione.add_argument("--solo", choices=("fronte", "dorso", "entrambi"), default="entrambi")

    p_tutte = sub.add_parser("tutte", help="Descrive tutte le altre carte, una volta approvato il campione.")
    p_tutte.add_argument("--set", required=True)
    p_tutte.add_argument(
        "--solo-carte", default=None,
        help="Id separati da virgola, es. maj-00,maj-01: rigenera proprio queste anche se già presenti "
             "(senza, salta quelle già fatte e prosegue con le mancanti).",
    )

    p_salva = sub.add_parser("salva", help="Converte un'immagine scaricata e la salva col nome standard.")
    p_salva.add_argument("--set", required=True)
    p_salva.add_argument("id", help="Id della carta, o 'dorso'.")
    p_salva.add_argument("file_scaricato", help="Percorso del file scaricato dal browser.")

    args = p.parse_args(argv)
    if args.comando == "campione":
        return asyncio.run(_campione(args))
    if args.comando == "tutte":
        return asyncio.run(_tutte(args))
    return _salva(args)


if __name__ == "__main__":
    sys.exit(main())
