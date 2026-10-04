"""Un modello finto, deterministico, per sviluppo e test.

Riconosce il compito dall'intestazione del prompt di sistema
(`# Compito: …`) e risponde nella forma attesa: JSON per intervista,
validazione, giudizio e la chiamata unica delle interpretazioni, testo per
l'interpretazione singola e la sintesi. Le risposte
citano i dati che trova nel prompt — il nome della carta, la posizione — così
che l'interfaccia mostri qualcosa di plausibile.

Non è un ripiego di produzione: `validate_production()` rifiuta di partire
con `TAROT_LLM_FINTO` attivo.
"""
from __future__ import annotations

import asyncio
import json
import random
import re
from typing import AsyncIterator, List

from ..llm.base import GenerationRequest, StreamChunk, Usage

#: Le aperture dell'oracolo finto: una a caso, come farebbe un modello vero.
_APERTURE = [
    "Ciao. Come stai oggi? C'è qualcosa che ti gira per la testa?",
    "C'è una decisione che continui a rimandare? Possiamo guardarla insieme.",
    "Qualcosa nel lavoro ti chiede energia in questi giorni?",
    "Come va con le persone che ti stanno vicino, in questo periodo?",
    "Un cambiamento si sta avvicinando? Ti va di raccontarmelo?",
]

#: Le stesse aperture nelle altre lingue del sito: il prompt dice in quale lingua scrivere (riga «Scrivi il messaggio
#: in …»), e il finto la rispetta come un modello vero.
_APERTURE_PER_LINGUA = {
    "inglese": ["Hi. How are you today? Is something on your mind?",
                "Is there a decision you keep putting off? We can look at it together."],
    "ungherese": ["Szia. Hogy vagy ma? Jár valami a fejedben?",
                  "Van egy döntés, amit folyton halogatsz? Megnézhetjük együtt."],
    "russo": ["Привет. Как ты сегодня? Что-то не выходит из головы?",
              "Есть решение, которое ты всё откладываешь? Можем взглянуть на него вместе."],
    "ucraino": ["Привіт. Як ти сьогодні? Щось не дає спокою?",
                "Є рішення, яке ти весь час відкладаєш? Можемо подивитися на нього разом."],
    "spagnolo": ["Hola. ¿Cómo estás hoy? ¿Hay algo que te ronda la cabeza?",
                 "¿Hay una decisión que sigues posponiendo? Podemos mirarla juntos."],
}
_RISPOSTA_PER_LINGUA = {
    "inglese": "I'm listening. You wrote: «{t}». Tell me a little more, if you like.",
    "ungherese": "Figyellek. Ezt írtad: «{t}». Mesélj még egy kicsit, ha szeretnéd.",
    "russo": "Я слушаю. Ты написал(а): «{t}». Расскажи ещё немного, если хочешь.",
    "ucraino": "Я слухаю. Ти написав(-ла): «{t}». Розкажи ще трохи, якщо хочеш.",
    "spagnolo": "Te escucho. Escribiste: «{t}». Cuéntame un poco más, si quieres.",
}

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


def _sistema(req: GenerationRequest) -> str:
    return "\n".join(m.content for m in req.messages if m.role == "system")


def _senza_soggetto(valore: str) -> str:
    """Toglie la coda « [riguarda: …]» che le letture speciali aggiungono alla catena."""
    return re.sub(r"\s*\[riguarda:.*$", "", valore).rstrip(".")


def _interpreta(testo: str) -> str:
    """La lettura finta di una carta: cita il nome, l'orientamento e la posizione che trova nel testo."""
    carta = re.search(r"Carta: (.+)", testo)
    pos = re.search(r"Posizione \d+: ([^—\n]+)", testo)
    ori = "rovesciata" if "Orientamento: rovesciata" in testo else "dritta"
    nome = carta.group(1).strip() if carta else "la carta"
    posizione = pos.group(1).strip() if pos else "questa posizione"
    return (
        f"{nome}, {ori}, nella posizione «{posizione}», porta la sua energia "
        f"proprio nel punto che la stesa dedica a questo aspetto della tua domanda. "
        f"Il suo simbolo invita a guardare con lucidità ciò che si sta muovendo, "
        f"senza fretta di concludere. È una forza da riconoscere e da orientare, "
        f"non una sentenza."
    )


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
        if compito == "chat_proattiva":
            scritto = re.search(r"L'utente ha appena scritto: (.+)", utente)
            nome_lingua = re.search(r"Scrivi il messaggio in ([^,]+),", utente)
            nome_lingua = nome_lingua.group(1).strip() if nome_lingua else "italiano"
            if nome_lingua in _APERTURE_PER_LINGUA:
                messaggio = (
                    _RISPOSTA_PER_LINGUA[nome_lingua].format(t=scritto.group(1).strip()[:120])
                    if scritto else random.choice(_APERTURE_PER_LINGUA[nome_lingua])
                )
            else:
                messaggio = (
                    f"Ti ascolto. Hai scritto: «{scritto.group(1).strip()[:120]}». Raccontami un po' di più, "
                    "se vuoi: cosa ti porta a pensarci proprio adesso?"
                    if scritto else random.choice(_APERTURE)
                )
            return json.dumps({"messaggio": messaggio, "proposta": None}, ensure_ascii=False)
        if compito == "analisi_dati":
            # Cita i primi fatti del prompt e ne riusa i numeri così come sono: la verifica deve
            # passare. Un test che vuole il caso contrario lo ottiene con un numero inventato.
            fatti = re.findall(r"^\[(M\d+)\] \(([^)]*)\) (.+)$", utente, re.M)
            if not fatti:
                return json.dumps({"sintesi": "Nessun dato nel periodo.", "osservazioni": []}, ensure_ascii=False)
            primo_id, sezione, testo = fatti[0]
            ids = [f[0] for f in fatti[:3]]
            return json.dumps({
                "sintesi": f"Nel periodo: {testo}",
                "osservazioni": [{"titolo": f"Il dato principale di {sezione}", "testo": testo,
                                  "importanza": "alta", "fatti": [primo_id]}],
                "collegamenti": [{"testo": "I primi fatti della sezione si muovono insieme.", "fatti": ids}],
                "ipotesi": [{"testo": "La variazione dipende dal canale principale.", "confidenza": "media",
                             "verifica": "Confrontare i canali nel periodo successivo.", "fatti": ids[:1]}],
                "azioni": [{"testo": "Rafforzare il canale che porta più visite.", "impatto": "medio",
                            "sforzo": "basso", "metrica": "sessioni dal canale", "fatti": ids[:1]}],
                "dati_mancanti": ["Il costo delle campagne."],
                "avvertenze": ["Periodo breve."],
            }, ensure_ascii=False)
        if compito == "giudizio":
            return json.dumps({"esito": "ok", "violazioni": []})
        if compito == "memoria_stato":
            # Lo stato sintetico della memoria: conferma tutto ciò che c'è, aggiunge la prima frase del quadro come
            # situazione in corso. Basta a provare il percorso intero (applicazione, oblio, profilo) senza un modello.
            ids = re.findall(r"^- \[(\w+)\]", utente, re.MULTILINE)
            quadro = re.search(r"Quadro emerso dal colloquio: ([^.\n]+)", utente)
            aggiungi = [{"categoria": "volatile", "campo": "altro", "testo": quadro.group(1).strip()}] \
                if quadro and "non disponibile" not in quadro.group(1) else []
            return json.dumps({"aggiungi": aggiungi, "conferma": ids, "rimuovi": [], "campo_quesito": "altro"},
                              ensure_ascii=False)
        if compito == "traduzione_notifica":
            # v9, Fase 5: il testo di partenza con la lingua davanti, segnaposto intatti (la console lo mostra così).
            origine = json.loads(utente)
            return json.dumps({
                lingua: {"titolo": f"[{lingua}] {origine['titolo']}", "corpo": f"[{lingua}] {origine['corpo']}"}
                for lingua in origine.get("lingue", [])
            }, ensure_ascii=False)
        if compito == "interpretazione":
            return _interpreta(utente)
        if compito == "interpretazione_unica":
            # La chiamata unica: un blocco «## Carta in posizione N» per carta, la stessa lettura della chiamata
            # singola per ciascuno, nel JSON chiesto dal prompt.
            blocchi = re.split(r"^## Carta in posizione (\d+)$", utente, flags=re.MULTILINE)[1:]
            return json.dumps({"carte": [
                {
                    "posizione": int(n),
                    "orientamento": "rovesciata" if "Orientamento: rovesciata" in blocco else "dritta",
                    "interpretazione": _interpreta(blocco),
                }
                for n, blocco in zip(blocchi[::2], blocchi[1::2])
            ]}, ensure_ascii=False)
        if compito == "teaser":
            # L'anteprima per chi non ha un account: due o tre frasi, che si fermano prima del consiglio.
            return (
                "Le carte che hai scelto descrivono un passaggio che chiede presenza più che velocità. "
                "Al centro della stesa c'è una forza che merita di essere guardata da vicino, "
                "e il modo in cui si lega alle altre dice molto della tua domanda…"
            )
        if compito == "sintesi":
            # L'«Ordine del racconto» del messaggio: una tappa per riga.
            tappe = re.findall(
                r"^\d+\. (.+?) \(posizione \d+\) — (.+?), (dritta|rovesciata): (.+)$", utente, re.MULTILINE,
            )
            elenco = "; ".join(f"{c} in «{p}»" for p, c, _o, _v in tappe) or "le carte"
            legami = ["Ora", "Poi", "Perciò", "E così", "Fino a"]
            # In coda alla riga può esserci « [riguarda: …]»: nelle letture speciali.
            filo = " ".join(
                f"{legami[min(i, len(legami) - 1)]}: {_senza_soggetto(v)} ({c}, {o})."
                for i, (_p, c, o, v) in enumerate(tappe)
            ) or "Le carte si parlano."
            # Le letture speciali hanno una sezione dedicata: la categoria si
            # riconosce dal formato che il prompt di sistema chiede.
            sistema = _sistema(req)
            if "## L'incontro dei segni" in sistema:
                seconda = "## L'incontro dei segni\n\nI segni solari sono uno sfondo, non un verdetto.\n\n"
            elif "## Ciò che vi lega" in sistema:
                seconda = "## Ciò che vi lega e ciò che vi mette alla prova\n\nIl legame ha forze e attriti.\n\n"
            else:
                seconda = ""
            return (
                "## Il quadro\n\n"
                f"La stesa mostra {elenco}. Insieme descrivono una situazione che chiede "
                "presenza e chiarezza più che velocità.\n\n"
                f"{seconda}"
                "## Le forze in gioco\n\n"
                f"{filo}\n\n"
                "## Il consiglio delle carte\n\n"
                "Agisci a partire da ciò che senti vero, senza forzare i tempi degli altri.\n\n"
                "## La tendenza più probabile\n\n"
                "Se le forze restano quelle attuali, la situazione tende a chiarirsi. "
                "Le tue scelte possono cambiarne la direzione."
            )
        return "…"
