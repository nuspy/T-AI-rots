"""Un modello finto, deterministico, per sviluppo e test.

Riconosce il compito dall'intestazione del prompt di sistema
(`# Compito: …`) e risponde nella forma attesa: JSON per intervista,
validazione e giudizio, testo per interpretazione e sintesi. Le risposte
citano i dati che trova nel prompt — il nome della carta, la posizione — così
che l'interfaccia mostri qualcosa di plausibile.

Non è un ripiego di produzione: `validate_production()` rifiuta di partire
con `TAROT_LLM_FINTO` attivo.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import AsyncIterator, List

from ..llm.base import GenerationRequest, StreamChunk, Usage

_DOMANDE = [
    "Da quanto tempo questa situazione è presente nella tua vita, e cosa l'ha messa in moto?",
    "Chi sono le persone coinvolte, e che ruolo hanno per te?",
    "Come ti senti, in questo periodo, quando ci pensi?",
]


def _compito(req: GenerationRequest) -> str:
    for m in req.messages:
        if m.role == "system":
            trovato = re.search(r"# Compito: (\w+)", m.content)
            if trovato:
                return trovato.group(1)
    return ""


def _utente(req: GenerationRequest) -> str:
    return next((m.content for m in reversed(req.messages) if m.role == "user"), "")


class ModelloFinto:
    name = "finto"

    #: Pausa fra i frammenti: abbastanza per vedere lo streaming, non per
    #: rallentare i test.
    pausa = 0.0

    async def available_models(self) -> List[str]:
        return ["finto"]

    async def complete_json(self, req: GenerationRequest):
        return json.loads(self._rispondi(req))

    async def complete(self, req: GenerationRequest) -> str:
        return self._rispondi(req)

    async def stream(self, req: GenerationRequest) -> AsyncIterator[StreamChunk]:
        testo = self._rispondi(req)
        for parola in re.findall(r"\S+\s*", testo):
            if self.pausa:
                await asyncio.sleep(self.pausa)
            yield StreamChunk(text=parola)
        yield StreamChunk(done=True, usage=Usage(model="finto"), finish_reason="stop")

    # ------------------------------------------------------------------

    def _rispondi(self, req: GenerationRequest) -> str:
        compito = _compito(req)
        utente = _utente(req)
        if compito == "intervista":
            poste = re.search(r"Domande già poste: (\d+)", utente)
            n = int(poste.group(1)) if poste else 0
            if n >= 2 or "conclusa" in utente or "numero massimo" in utente:
                quesito = re.search(r"Quesito: (.+)", utente)
                return json.dumps({
                    "completo": True,
                    "riassunto": (
                        f"Chi consulta chiede: «{quesito.group(1).strip() if quesito else ''}». "
                        "Dal colloquio emerge una situazione in movimento, vissuta con "
                        "partecipazione emotiva e il desiderio di vedere più chiaro."
                    ),
                }, ensure_ascii=False)
            return json.dumps({"completo": False, "domanda": _DOMANDE[n % len(_DOMANDE)]}, ensure_ascii=False)
        if compito == "validazione":
            return json.dumps({"valida": True, "motivo": ""})
        if compito == "giudizio":
            return json.dumps({"esito": "ok", "violazioni": []})
        if compito == "interpretazione":
            carta = re.search(r"Carta: (.+)", utente)
            pos = re.search(r"Posizione \d+: ([^—\n]+)", utente)
            ori = "rovesciata" if "Orientamento: rovesciata" in utente else "dritta"
            nome = carta.group(1).strip() if carta else "la carta"
            posizione = pos.group(1).strip() if pos else "questa posizione"
            return (
                f"{nome}, {ori}, nella posizione «{posizione}», porta la sua energia "
                f"proprio nel punto che la stesa dedica a questo aspetto della tua domanda. "
                f"Il suo simbolo invita a guardare con lucidità ciò che si sta muovendo, "
                f"senza fretta di concludere. È una forza da riconoscere e da orientare, "
                f"non una sentenza."
            )
        if compito == "sintesi":
            carte = re.findall(r"«([^»]+)» \([^)]*\): ([^\[]+) \[", utente)
            elenco = "; ".join(f"{c.strip()} in «{p}»" for p, c in carte) or "le carte"
            return (
                "## Il quadro\n\n"
                f"La stesa mostra {elenco}. Insieme descrivono una situazione che chiede "
                "presenza e chiarezza più che velocità.\n\n"
                "## Le forze in gioco\n\n"
                "Le carte si parlano: alcune sostengono il tuo movimento, altre ne mostrano "
                "il costo. Le dignità elementali indicano dove l'energia scorre e dove si "
                "inceppa.\n\n"
                "## Il consiglio delle carte\n\n"
                "Agisci a partire da ciò che senti vero, senza forzare i tempi degli altri.\n\n"
                "## La tendenza più probabile\n\n"
                "Se le forze restano quelle attuali, la situazione tende a chiarirsi. "
                "Le tue scelte possono cambiarne la direzione."
            )
        return "…"
