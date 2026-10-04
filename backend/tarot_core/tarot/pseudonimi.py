"""I nomi di persona non lasciano il server: al modello arriva «Persona_1», e chi legge rivede «Marco».

**Perché.** Il nome dell'altra persona, scritto da chi consulta, va a un fornitore esterno (spesso fuori dall'Unione).
Il modello non ne ha bisogno per leggere le carte: gli basta un segnaposto coerente. Si nasconde **al confine di
rete**, in un involucro attorno al fornitore (`ProviderProtetto`): il resto dell'applicazione — prompt, controlli,
storico — continua a lavorare con i nomi veri, e nessun punto di chiamata deve ricordarsi di farlo.

**Come.** Ogni lettura ha i suoi nomi (oggi il nome dell'altra persona, dall'istantanea `Reading.persone`) e a ciascuno un
segnaposto (`Persona_1`, `Persona_2`…). In uscita ogni occorrenza del nome, in qualunque messaggio, diventa il
segnaposto; in ingresso, nel testo e nei JSON, il segnaposto torna il nome. Anche in streaming: un segnaposto spezzato fra
due frammenti (`Pers` + `ona_1`) si trattiene finché si capisce cosa è.

**Forme flesse.** Un nome di almeno quattro lettere si riconosce anche seguito da altre lettere («Marco», «Marcóval»,
«Marcovaldo»): il ripristino è esatto, quindi un nascondiglio in più non perde niente. Un nome corto si riconosce solo
come parola intera, per non spezzare parole comuni.

**Perimetro.** Si nascondono i messaggi che portano dati (utente, assistente); i prompt di sistema, che sono regole fisse,
non contengono nomi (un test lo verifica su una lettura intera) e non si toccano.

**Cosa non fa.** Non riconosce nomi che non conosce: se chi consulta scrive il nome di un collega nel quesito, quel nome
parte com'è. Non è anonimato in senso legale — il testo libero può ancora identificare qualcuno —: è minimizzazione, e
riduce di molto ciò che un fornitore vede. Il cognome non entra mai nei prompt (lo garantisce `tarot/persone.py`).
"""
from __future__ import annotations

import re
from dataclasses import replace
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..llm.base import GenerationRequest, Message, StreamChunk

PREFISSO = "Persona_"
_SEGNAPOSTO = re.compile(re.escape(PREFISSO) + r"(\d+)")

#: Particelle che si incontrano dentro i nomi («Anna Maria Della Rosa») e sono parole comuni: da sole non si nascondono.
PARTICELLE = frozenset({
    "della", "delle", "dello", "degli", "dalla", "dalle", "dallo", "dagli", "nella", "sulla", "von", "van", "den",
    "der", "des", "dos", "das", "bint", "abd",
})


class Pseudonimi:
    """I nomi di una lettura e i loro segnaposto."""

    def __init__(self, nomi: Iterable[str]) -> None:
        visti: set = set()
        elenco: List[str] = []
        for nome in nomi:
            pulito = " ".join((nome or "").split())
            chiave = pulito.lower()
            # Un nome che coincide col prefisso dei segnaposto si scambierebbe con essi.
            if len(pulito) < 2 or chiave in visti or chiave == "persona":
                continue
            visti.add(chiave)
            elenco.append(pulito)
            # Un nome di più parole si riconosce anche a pezzi («Maria Grazia» → «Maria», «Grazia»), ma solo le parti
            # lunghe e non comuni: «Della» o «prompt» nascosti ovunque guasterebbero il testo intorno.
            for parte in pulito.split():
                if len(parte) >= 4 and parte.lower() not in visti and parte.lower() not in PARTICELLE and parte.lower() != "persona":
                    visti.add(parte.lower())
                    elenco.append(parte)
        self._nomi: Dict[int, str] = {i + 1: nome for i, nome in enumerate(elenco)}
        # I nomi più lunghi per primi: «Maria Grazia» prima di «Maria».
        ordine = sorted(self._nomi.items(), key=lambda kv: -len(kv[1]))
        self._nascondi: List[Tuple[re.Pattern, str]] = [
            (re.compile(r"(?<!\w)" + re.escape(nome) + (r"" if len(nome) >= 4 else r"(?!\w)"), re.IGNORECASE),
             f"{PREFISSO}{n}")
            for n, nome in ordine
        ]

    @classmethod
    def da_persone(cls, persone: Any) -> "Pseudonimi":
        """I nomi da `tarot.persone.Persone` (l'altra persona; chi consulta non ha nome nei prompt)."""
        if persone is None:
            return cls([])
        return cls([getattr(persone.partner, "nome", None) or "", getattr(persone.tu, "nome", None) or ""])

    @property
    def vuoto(self) -> bool:
        return not self._nomi

    def nascondi(self, testo: str) -> str:
        for regola, segnaposto in self._nascondi:
            testo = regola.sub(segnaposto, testo)
        return testo

    def ripristina(self, testo: str) -> str:
        def torna(m: "re.Match[str]") -> str:
            return self._nomi.get(int(m.group(1)), m.group(0))

        return _SEGNAPOSTO.sub(torna, testo)

    def ripristina_dati(self, valore: Any) -> Any:
        """Il ripristino dentro un JSON già letto: stringhe, liste e dizionari, senza toccare le chiavi."""
        if isinstance(valore, str):
            return self.ripristina(valore)
        if isinstance(valore, list):
            return [self.ripristina_dati(v) for v in valore]
        if isinstance(valore, dict):
            return {k: self.ripristina_dati(v) for k, v in valore.items()}
        return valore

    def flusso(self) -> "RipristinoInFlusso":
        return RipristinoInFlusso(self)


class RipristinoInFlusso:
    """Il ripristino su un testo che arriva a pezzi: trattiene la coda che potrebbe essere l'inizio di un segnaposto."""

    def __init__(self, pseudonimi: Pseudonimi) -> None:
        self._p = pseudonimi
        self._coda = ""

    def _trattenere(self, testo: str) -> int:
        """Quanti caratteri in fondo a `testo` potrebbero essere l'inizio di un segnaposto."""
        for k in range(min(len(testo), len(PREFISSO)), 0, -1):
            if PREFISSO.startswith(testo[-k:]):
                return k
        # «Persona_» seguito da cifre: potrebbe ancora allungarsi («Persona_1» → «Persona_12»).
        m = re.search(re.escape(PREFISSO) + r"\d*$", testo)
        return len(m.group(0)) if m else 0

    def feed(self, pezzo: str) -> str:
        testo = self._coda + pezzo
        trattieni = self._trattenere(testo)
        pronto, self._coda = testo[: len(testo) - trattieni], testo[len(testo) - trattieni:]
        return self._p.ripristina(pronto)

    def fine(self) -> str:
        resto, self._coda = self._coda, ""
        return self._p.ripristina(resto)


class ProviderProtetto:
    """Un fornitore che non vede i nomi: li nasconde in uscita e li ripristina in ingresso.

    Ha lo stesso aspetto del fornitore che avvolge (`__getattr__` gli passa tutto il resto: il nome, il motore, la scelta
    del modello), quindi il codice che lo usa non cambia."""

    def __init__(self, fornitore: Any, pseudonimi: Pseudonimi) -> None:
        self._fornitore = fornitore
        self._p = pseudonimi

    def __getattr__(self, nome: str) -> Any:
        valore = getattr(self._fornitore, nome)
        if nome == "embed":
            # Anche i testi da vettorizzare (memorie, quesiti) vanno al fornitore senza nomi (GDPR, Fase 1). Qui e non
            # come metodo: `supporta_embedding()` guarda se `embed` esiste, e deve restare vero solo se il fornitore
            # avvolto lo sa fare.
            async def embed(testi, *argomenti, **opzioni):
                return await valore([self._p.nascondi(t) for t in testi], *argomenti, **opzioni)

            return embed
        return valore

    def _richiesta(self, req: GenerationRequest) -> GenerationRequest:
        """Solo i messaggi che portano dati (utente, assistente): quelli di sistema sono regole fisse, senza nomi, e un
        nome che coincide con una parola comune («Rosa», «Grazia») ne guasterebbe il testo."""
        return replace(req, messages=[
            m if m.role == "system" else Message(m.role, self._p.nascondi(m.content)) for m in req.messages
        ])

    async def complete(self, req: GenerationRequest) -> str:
        return self._p.ripristina(await self._fornitore.complete(self._richiesta(req)))

    async def complete_json(self, req: GenerationRequest) -> Any:
        return self._p.ripristina_dati(await self._fornitore.complete_json(self._richiesta(req)))

    async def stream(self, req: GenerationRequest):
        ripristino = self._p.flusso()
        async for pezzo in self._fornitore.stream(self._richiesta(req)):
            testo = ripristino.feed(pezzo.text)
            if pezzo.done:
                testo += ripristino.fine()
            yield StreamChunk(
                text=testo, reasoning=pezzo.reasoning, done=pezzo.done, usage=pezzo.usage,
                finish_reason=pezzo.finish_reason,
            )
        # Un flusso finito senza il pezzo `done`: il testo trattenuto non va perso.
        resto = ripristino.fine()
        if resto:
            yield StreamChunk(text=resto)


def protetto(fornitore: Any, persone: Any, *, attivo: bool = True) -> Any:
    """Il fornitore, avvolto se ci sono nomi da nascondere (e la protezione è accesa). `persone` sono le persone di
    una lettura (`tarot.persone.Persone`) oppure dei `Pseudonimi` già pronti (la chat e le memorie, `nomi_utente`)."""
    if not attivo:
        return fornitore
    pseudonimi = persone if isinstance(persone, Pseudonimi) else Pseudonimi.da_persone(persone)
    return fornitore if pseudonimi.vuoto else ProviderProtetto(fornitore, pseudonimi)


async def nomi_utente(session: Any, user: Any, *, letture: int = 20) -> Pseudonimi:
    """I nomi che possono comparire nei testi di una persona fuori da una lettura — la chat con l'oracolo, le memorie
    (GDPR, Fase 1): il suo nome e cognome (della scheda e quello mostrato da Keycloak), il partner ricordato, e gli
    altri nomi delle ultime letture di coppia. Al fornitore arrivano come «Persona_N»; le risposte tornano col nome."""
    from sqlalchemy import desc, func, select

    from ..domain.models import Reading

    nomi: List[str] = [
        getattr(user, "nome", None) or "", getattr(user, "cognome", None) or "",
        getattr(user, "display_name", None) or "",
    ]
    ricordato = getattr(user, "partner_ricordato", None) or {}
    nomi += [ricordato.get("nome") or "", ricordato.get("cognome") or ""]
    persone = (await session.execute(
        select(Reading.persone)
        # `jsonb_typeof`: un `None` scritto in una colonna JSON diventa il `null` di JSON, non il NULL di SQL.
        .where(Reading.owner_id == user.id, func.jsonb_typeof(Reading.persone) == "object")
        .order_by(desc(Reading.created_at)).limit(letture)
    )).scalars().all()
    for p in persone:
        partner = (p or {}).get("partner") or {}
        nomi += [partner.get("nome") or "", partner.get("cognome") or ""]
    return Pseudonimi(nomi)
