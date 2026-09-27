"""Bozza di traduzione dei testi lunghi (carte, stese, glossario) in una nuova lingua (v5, Fase D).

    python -m tarot_core.tools.traduci_conoscenza --lang hu
    python -m tarot_core.tools.traduci_conoscenza --lang hu --solo-carte maj-00,maj-01
    python -m tarot_core.tools.traduci_conoscenza --lang hu --riprendi   # salta ciò che il file ha già

**Non è un endpoint, non gira da sola in produzione**: uno strumento offline, per preparare una bozza
che un umano rivede prima che la lingua entri in `LINGUE_CONTENUTO` in `tarot/conoscenza.py` —
esattamente come richiesto ("richiede sempre un passaggio umano di revisione"). Finché quella riga non
cambia, il file scritto qui non ha alcun effetto: `Conoscenza.carica()` lo ignora.

Scala per lingua: 78 carte × 12 campi (`CAMPI_TESTO_CARTA`), 14 stese × (4 campi scalari + `regole` +
`pos` per ogni posizione, 99 posizioni in tutto × 3 campi), più un piccolo glossario di termini
(elemento/seme/rango/arcano). Una chiamata al modello per carta e una per stesa: una novantina in
tutto, scritte una alla volta nel file di uscita — un'interruzione a metà non perde il lavoro già
fatto, e `--riprendi` la ripete da dove si era fermata.

Usa lo stesso registro di modelli dell'applicazione (fornitori in console, o l'ambiente se non ce ne
sono ancora): nessuna chiave o indirizzo hardcoded qui.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..llm.compiti import Compito, ModelloConfigurato, RegistroModelli, modelli_da_impostazioni
from ..paths import KNOWLEDGE_DIR
from ..tarot.conoscenza import CAMPI_TESTO_CARTA, CAMPI_TESTO_POSIZIONE, CAMPI_TESTO_STESA, Conoscenza
from ..tarot.lingue import nome_per_prompt
from ..tarot.llm import genera_json, richiesta

logger = logging.getLogger(__name__)


class TraduzioneVoceNonRiuscita(RuntimeError):
    """Il modello non ha restituito una voce (carta, stesa o glossario) completa e valida."""


def _leggi_parziale(percorso: Path) -> Dict[str, Any]:
    if not percorso.exists():
        return {}
    try:
        return json.loads(percorso.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _scrivi(percorso: Path, dati: Dict[str, Any]) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(json.dumps(dati, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


PROMPT_CARTA = """# Compito: traduzione di una scheda di carta (Tarocco di Thoth)

Sei un traduttore ed esperto di Tarocco di Thoth, Golden Dawn ed esoterismo. Traduci in {lingua} la
scheda seguente di "{nome}" (mantieni i nomi propri e i termini tecnici consolidati nella lingua di
arrivo, se esistono; altrimenti come nell'originale). Rispondi in JSON con esattamente questi campi,
tutti tradotti dall'italiano:

{{"astro": "...", "kw": ["...", ...] (esattamente {n_parole} elementi, come l'originale),
"exo": "...", "psy": "...", "ini": "...", "sha": "...", "up": "...", "rev": "...",
"love": "...", "work": "...", "spirit": "...", "crowley": "..."}}

Non aggiungere né togliere significato: è una traduzione, non una nuova interpretazione. Nessun testo
prima o dopo il JSON."""

PROMPT_STESA = """# Compito: traduzione di una stesa (Tarocco di Thoth)

Sei un traduttore ed esperto di Tarocco di Thoth. Traduci in {lingua} la stesa "{nome}" e tutte le sue
posizioni. Rispondi in JSON con esattamente questa forma:

{{"slug": "...-in-minuscolo-con-trattini", "nome": "...", "origine": "...", "descrizione": "...",
"regole": ["...", ...] (esattamente {n_regole} elementi, come l'originale),
"pos": {{{esempio_pos}}}}}

Ogni voce di "pos" ha "nome", "significato", "domanda". Non aggiungere né togliere significato: è una
traduzione. Nessun testo prima o dopo il JSON."""

PROMPT_GLOSSARIO = """# Compito: traduzione del glossario dei termini (Tarocco di Thoth)

Traduci in {lingua} ciascuno di questi termini italiani, come si scriverebbero in un testo divulgativo
di tarocchi in quella lingua. Rispondi in JSON con questa forma esatta, una voce per ogni termine
elencato sotto ogni categoria:

{{"elemento": {{"Fuoco": "...", ...}}, "seme": {{"bastoni": "...", ...}},
"rango": {{"asso": "...", ...}}, "arcano": {{"maggiore": "...", "minore": "..."}}}}

Termini da tradurre, per categoria:
{termini}

Nessun testo prima o dopo il JSON."""


async def traduci_carta(provider: Any, carta: Dict[str, Any], lingua: str) -> Dict[str, Any]:
    prompt = PROMPT_CARTA.format(
        lingua=nome_per_prompt(lingua), nome=carta.get("nome_thoth") or carta["id"],
        n_parole=len(carta.get("parole_chiave", [])),
    )
    dati = await genera_json(provider, richiesta([prompt], json.dumps(carta, ensure_ascii=False), temperatura=0.3, max_tokens=4096))
    mancanti = [c for c in CAMPI_TESTO_CARTA if not dati.get(c)]
    if mancanti:
        raise TraduzioneVoceNonRiuscita(f"{carta['id']}: campi mancanti {mancanti}")
    if not isinstance(dati.get("kw"), list) or len(dati["kw"]) != len(carta.get("parole_chiave", [])):
        raise TraduzioneVoceNonRiuscita(f"{carta['id']}: numero di parole chiave diverso dall'originale")
    return {k: dati[k] for k in CAMPI_TESTO_CARTA}


async def traduci_stesa(provider: Any, stesa: Dict[str, Any], lingua: str) -> Dict[str, Any]:
    esempio_pos = ", ".join(f'"{p["n"]}": {{"nome": "...", "significato": "...", "domanda": "..."}}' for p in stesa["posizioni"][:1])
    prompt = PROMPT_STESA.format(
        lingua=nome_per_prompt(lingua), nome=stesa.get("nome_en") or stesa["nome"],
        n_regole=len(stesa.get("regole", [])), esempio_pos=esempio_pos,
    )
    corpo = {
        "nome": stesa["nome"], "origine": stesa["origine"], "descrizione": stesa["descrizione"],
        "regole": stesa["regole"],
        "posizioni": [{"n": p["n"], "nome": p["nome"], "significato": p["significato"], "domanda": p["domanda"]} for p in stesa["posizioni"]],
    }
    dati = await genera_json(provider, richiesta([prompt], json.dumps(corpo, ensure_ascii=False), temperatura=0.3, max_tokens=8192))
    mancanti = [c for c in CAMPI_TESTO_STESA if not dati.get(c)]
    if mancanti:
        raise TraduzioneVoceNonRiuscita(f"{stesa['id']}: campi mancanti {mancanti}")
    if len(dati.get("regole") or []) != len(stesa["regole"]):
        raise TraduzioneVoceNonRiuscita(f"{stesa['id']}: numero di regole diverso dall'originale")
    pos = dati.get("pos") or {}
    for p in stesa["posizioni"]:
        voce = pos.get(str(p["n"]))
        if not voce or any(not voce.get(k) for k in CAMPI_TESTO_POSIZIONE):
            raise TraduzioneVoceNonRiuscita(f"{stesa['id']}: posizione {p['n']} incompleta")
    return {k: dati[k] for k in CAMPI_TESTO_STESA}


async def traduci_glossario(provider: Any, conoscenza: Conoscenza, lingua: str) -> Dict[str, Dict[str, str]]:
    categorie = {
        campo: sorted({c.get(campo) for c in conoscenza.carte.values() if c.get(campo)})
        for campo in ("elemento", "seme", "rango", "arcano")
    }
    elenco = "\n".join(f"- {campo}: {', '.join(valori)}" for campo, valori in categorie.items())
    prompt = PROMPT_GLOSSARIO.format(lingua=nome_per_prompt(lingua), termini=elenco)
    dati = await genera_json(provider, richiesta([prompt], "Traduci.", temperatura=0.2, max_tokens=2048))
    for campo, valori in categorie.items():
        mancanti = [v for v in valori if not (dati.get(campo) or {}).get(v)]
        if mancanti:
            raise TraduzioneVoceNonRiuscita(f"glossario: {campo} senza {mancanti}")
    return dati


async def esegui(
    provider: Any, conoscenza: Conoscenza, lingua: str, out_dir: Path, *,
    solo_carte: Optional[List[str]] = None, solo_stese: Optional[List[str]] = None,
    riprendi: bool = False, quieto: bool = False,
) -> Dict[str, List[str]]:
    """Scrive `cards-bozza.json`, `spreads-bozza.json`, `termini.json` in `out_dir`, una voce alla
    volta (così un'interruzione a metà non perde il lavoro già fatto). Restituisce `{"ok": [...],
    "falliti": [...]}`."""
    def stampa(msg: str) -> None:
        if not quieto:
            print(msg, file=sys.stderr)

    carte_out = out_dir / "cards-bozza.json"
    stese_out = out_dir / "spreads-bozza.json"
    termini_out = out_dir / "termini.json"
    carte_fatte = _leggi_parziale(carte_out) if riprendi else {}
    stese_fatte = _leggi_parziale(stese_out) if riprendi else {}

    esito: Dict[str, List[str]] = {"ok": [], "falliti": []}

    # Con uno solo dei due filtri dato, si fa SOLO quella categoria (non anche l'altra per intero): chi
    # chiede `--solo-carte` vuole tradurre solo carte adesso, non tutte le 14 stese come effetto
    # collaterale. Con nessun filtro, o con entrambi, si fa tutto ciò che è stato chiesto.
    fare_carte = solo_carte is not None or solo_stese is None
    fare_stese = solo_stese is not None or solo_carte is None
    fare_glossario = solo_carte is None and solo_stese is None

    id_carte = solo_carte if solo_carte is not None else (list(conoscenza.carte) if fare_carte else [])
    for card_id in id_carte:
        if card_id in carte_fatte:
            stampa(f"carta {card_id}: già fatta, salto")
            continue
        try:
            carte_fatte[card_id] = await traduci_carta(provider, conoscenza.carte[card_id], lingua)
            _scrivi(carte_out, carte_fatte)
            esito["ok"].append(f"carta:{card_id}")
            stampa(f"carta {card_id}: fatta")
        except TraduzioneVoceNonRiuscita as exc:
            esito["falliti"].append(f"carta:{card_id}: {exc}")
            stampa(f"carta {card_id}: FALLITA — {exc}")

    id_stese = solo_stese if solo_stese is not None else (list(conoscenza.stese) if fare_stese else [])
    for spread_id in id_stese:
        if spread_id in stese_fatte:
            stampa(f"stesa {spread_id}: già fatta, salto")
            continue
        try:
            stese_fatte[spread_id] = await traduci_stesa(provider, conoscenza.stese[spread_id], lingua)
            _scrivi(stese_out, stese_fatte)
            esito["ok"].append(f"stesa:{spread_id}")
            stampa(f"stesa {spread_id}: fatta")
        except TraduzioneVoceNonRiuscita as exc:
            esito["falliti"].append(f"stesa:{spread_id}: {exc}")
            stampa(f"stesa {spread_id}: FALLITA — {exc}")

    if fare_glossario:
        try:
            glossario = await traduci_glossario(provider, conoscenza, lingua)
            _scrivi(termini_out, glossario)
            esito["ok"].append("glossario")
            stampa("glossario: fatto")
        except TraduzioneVoceNonRiuscita as exc:
            esito["falliti"].append(f"glossario: {exc}")
            stampa(f"glossario: FALLITO — {exc}")

    return esito


async def _provider_predefinito() -> Any:
    """Il registro modelli dell'applicazione, fuori da una richiesta HTTP: i fornitori dal database se
    ce ne sono, altrimenti quelli ricavati dall'ambiente — stessa regola di sempre."""
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
    return registro.per(Compito.TRADUZIONE_CONOSCENZA)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--lang", required=True, help="Codice della lingua di arrivo, es. 'hu'.")
    p.add_argument("--out-dir", default=None, help=f"Predefinito: {KNOWLEDGE_DIR}/<lang>/")
    p.add_argument("--solo-carte", default=None, help="Id separati da virgola, es. maj-00,maj-01.")
    p.add_argument("--solo-stese", default=None, help="Id separati da virgola.")
    p.add_argument("--riprendi", action="store_true", help="Salta le voci già presenti nel file di uscita.")
    args = p.parse_args(argv)

    out_dir = Path(args.out_dir) if args.out_dir else (KNOWLEDGE_DIR / args.lang)
    conoscenza = Conoscenza.carica()

    async def corri() -> Dict[str, List[str]]:
        provider = await _provider_predefinito()
        return await esegui(
            provider, conoscenza, args.lang, out_dir,
            solo_carte=args.solo_carte.split(",") if args.solo_carte else None,
            solo_stese=args.solo_stese.split(",") if args.solo_stese else None,
            riprendi=args.riprendi,
        )

    esito = asyncio.run(corri())
    print(f"fatte: {len(esito['ok'])}  fallite: {len(esito['falliti'])}", file=sys.stderr)
    if esito["falliti"]:
        print("Bozza scritta in " + str(out_dir) + " — RIVEDERE PRIMA di aggiungere la lingua a "
              "LINGUE_CONTENUTO. Rilanciare con --riprendi per riprovare le voci fallite.", file=sys.stderr)
        return 1
    print(f"Bozza completa in {out_dir} — revisione umana richiesta prima di aggiungere '{args.lang}' "
          "a LINGUE_CONTENUTO in tarot/conoscenza.py.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
