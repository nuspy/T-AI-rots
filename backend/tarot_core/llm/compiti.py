"""Quale modello serve quale compito.

Un solo modello per tutto è comodo finché i compiti non divergono, e
divergono presto. Validare una domanda vuole un modello economico e
rigoroso; scrivere il responso finale vuole il migliore che ci si possa
permettere; verificare se il responso sia sicuro vuole un modello **diverso
da quello che l'ha scritto**, o il giudice finisce per assolvere sé stesso.

Da qui i cinque compiti. Non sono livelli di qualità: sono lavori con
requisiti diversi, e la scelta di ciascuno è indipendente dalle altre.

Questo registro è il punto in cui si innesta `llmswitch` (progetto separato
dell'utente, che tiene un registro di fornitori modificabile da chi
amministra): i fornitori sono quelli di `llm/` (OpenAI-compatibili e
Anthropic), e il registro sceglie fra modelli configurati dalla console.

**Come si configura, e perché così.** Indirizzi, modelli e chiavi si
aggiungono, modificano ed eliminano dalla console (`domain.config_models.
LlmProvider`, cifrati in database — vedi `llm/cifratura.py`), non
nell'ambiente del processo: un amministratore autenticato con il ruolo
`admin` è il confine di fiducia, e tenere le chiavi fuori dall'immagine e
dal Secret di Kubernetes è un guadagno, non un rischio. `TAROT_MODELLI` e le
vecchie `TAROT_LLM_*` restano un ripiego per lo sviluppo locale e i test:
`modelli_da_impostazioni()` si usa solo finché la tabella dei fornitori è
vuota.

Chi non ha un'assegnazione ricade sul modello predefinito. Ricade e non
fallisce: un compito senza modello assegnato è la condizione normale di un
impianto appena installato, e una piattaforma che non risponde finché
qualcuno non ha compilato cinque caselle è una piattaforma che sembra
rotta.
"""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class Compito(str, Enum):
    """I lavori per cui si interroga un modello durante una lettura."""

    #: Le domande di contesto: capire la situazione senza chiedere la risposta.
    INTERVISTA = "intervista"
    #: Il controllo delle domande candidate: nessuna può chiedere all'utente
    #: la risposta al suo quesito, né una previsione.
    VALIDAZIONE = "validazione"
    #: L'interpretazione immediata di ogni carta rivelata.
    INTERPRETAZIONE = "interpretazione"
    #: Il responso finale, con la dottrina nel contesto (CAG).
    SINTESI = "sintesi"
    #: Il guardrail: il giudice che verifica la sicurezza del responso.
    GIUDIZIO = "giudizio"

    @property
    def label(self) -> str:
        return _ETICHETTE[self]

    @property
    def descrizione(self) -> str:
        return _DESCRIZIONI[self]


_ETICHETTE: Dict[Compito, str] = {
    Compito.INTERVISTA: "Intervista di contesto",
    Compito.VALIDAZIONE: "Validazione delle domande",
    Compito.INTERPRETAZIONE: "Interpretazione delle carte",
    Compito.SINTESI: "Sintesi finale (CAG)",
    Compito.GIUDIZIO: "Guardrail del responso",
}

_DESCRIZIONI: Dict[Compito, str] = {
    Compito.INTERVISTA: (
        "Fa le domande che chiariscono il quadro. Conta la sensibilità più "
        "della potenza: poche chiamate, brevi."
    ),
    Compito.VALIDAZIONE: (
        "Scarta le domande che chiedono all'utente la risposta al suo quesito "
        "o una previsione. Un modello piccolo e rigoroso basta."
    ),
    Compito.INTERPRETAZIONE: (
        "Legge ogni carta nella sua posizione, in streaming, mentre l'utente "
        "la guarda girarsi: conta la latenza."
    ),
    Compito.SINTESI: (
        "Mette insieme domanda, intervista, carte e dottrina. È il modello "
        "che si sente: qui la qualità si nota a ogni frase. Beneficia del "
        "prompt caching sul prefisso della dottrina."
    ),
    Compito.GIUDIZIO: (
        "Verifica che il responso non sia pericoloso. **Conviene che sia un "
        "modello diverso** da quello che ha scritto: un giudice che è anche "
        "l'autore assolve sé stesso."
    ),
}


class ModelloConfigurato(BaseModel):
    """Un modello raggiungibile, con il nome con cui la console lo chiama."""

    #: Il nome che si vede in console e che l'assegnazione registra. Stabile:
    #: cambiarlo fa ricadere sui predefiniti i compiti che lo citavano.
    nome: str = Field(min_length=1, max_length=60)
    #: `openai-compatible` (OpenAI, LM Studio, vLLM, llama.cpp) o `anthropic`.
    provider: str = "openai-compatible"
    base_url: str = ""
    #: Vuoto: il primo modello che il server ha caricato.
    model: str = ""
    api_key: str = ""
    #: Il modello ragiona prima di rispondere, e il ragionamento consuma il
    #: budget di uscita insieme alla risposta. Dichiararlo evita due tentativi
    #: sprecati a ogni chiamata strutturata: la scala dei budget parte da un
    #: valore che copre il ragionamento invece di scoprirlo fallendo — e su
    #: un modello lento ogni tentativo è un minuto.
    ragiona: bool = False
    #: Che motore c'è dietro l'indirizzo: decide la `ContextStrategy`, cioè
    #: se il prefisso stabile viene riusato dalla KV-cache, scontato dal
    #: prompt caching del fornitore, o niente. Vuoto lo deduce dall'indirizzo;
    #: si indica quando l'indirizzo non basta — un llama.cpp su una porta
    #: qualunque somiglia a qualunque altra cosa.
    #: Valori: vuoto, `openai`, `vllm`, `llamacpp`, `lmstudio`, `other`.
    motore: str = ""
    #: Campi che si aggiungono a **ogni** richiesta a questo modello, per ciò che dipende dal motore e dal modello e
    #: non ha un nome comune: soprattutto il ragionamento, che si spegne (o si regola) **nella richiesta**, non al
    #: caricamento del modello. Per esempio `{"reasoning_effort": "low"}` o
    #: `{"chat_template_kwargs": {"enable_thinking": false}}`: il campo giusto lo dice il motore (LM Studio, vLLM,
    #: llama.cpp). Per avere lo stesso modello con e senza ragionamento lo si dichiara due volte, con nomi e
    #: `parametri` diversi, e la console assegna l'uno o l'altro a ciascun compito. Un modello con il
    #: ragionamento spento non è `ragiona`.
    parametri: Dict[str, Any] = Field(default_factory=dict)
    #: Come si presenta in console. Non ha effetto sul comportamento.
    descrizione: str = ""
    #: Dichiara che il modello non rifiuta nulla — un modello «abliterato» ha
    #: perso la capacità di dire di no. Non impedisce nessuna assegnazione:
    #: è l'amministratore a decidere. Serve perché la scelta sia informata
    #: invece che accidentale, e perché resti scritto cosa si è scelto.
    senza_filtri: bool = False

    @field_validator("parametri")
    @classmethod
    def _parametri_ammessi(cls, valore: Dict[str, Any]) -> Dict[str, Any]:
        return controlla_parametri(valore)


#: I campi della richiesta che l'applicazione scrive da sé: `parametri` non li può toccare (un modello che
#: cambiasse `messages` o `stream` romperebbe la lettura, o la leggerebbe di nascosto).
CAMPI_RISERVATI = frozenset({"model", "messages", "stream", "stream_options", "stop", "temperature", "max_tokens"})


def controlla_parametri(parametri: Dict[str, Any]) -> Dict[str, Any]:
    """`parametri` senza i campi che l'applicazione scrive da sé; altrimenti `ValueError`."""
    riservati = sorted(CAMPI_RISERVATI & set(parametri))
    if riservati:
        raise ValueError(f"parametri non ammessi (li scrive l'applicazione): {', '.join(riservati)}")
    return parametri


#: Il nome che prende il modello ricavato dalle vecchie impostazioni, quando
#: nessun elenco è configurato.
PREDEFINITO = "predefinito"


class RegistroModelli:
    """L'elenco dei modelli e chi serve cosa.

    Costruisce i fornitori una volta sola per modello: l'oggetto ricorda
    quale modello il server ha caricato, e ricrearlo a ogni chiamata
    significherebbe chiedere di nuovo l'elenco dei modelli prima di ogni
    singola risposta.
    """

    def __init__(
        self,
        modelli: List[ModelloConfigurato],
        *,
        assegnazioni: Optional[Dict[Compito, str]] = None,
        configurato: bool = True,
    ) -> None:
        self._modelli = {m.nome: m for m in modelli}
        self._assegnazioni: Dict[Compito, str] = dict(assegnazioni or {})
        self._fornitori: Dict[str, object] = {}
        #: Quando le assegnazioni sono state lette dal database. Zero: mai.
        self._lette_a = 0.0
        #: Quando l'elenco dei fornitori è stato riletto dal database. Zero: mai (all'avvio si parte da quello
        #: costruito nel costruttore, tipicamente `modelli_da_impostazioni()`).
        self._modelli_lette_a = 0.0
        #: Se `modelli` è una configurazione vera, non solo il segnaposto `PREDEFINITO` che
        #: `modelli_da_impostazioni()` ricava da impostazioni mai impostate esplicitamente (vedi `configurato`
        #: sotto). Chi costruisce il registro con un elenco scelto a mano — i test, soprattutto — lo intende
        #: sempre vero: il default è `True` apposta.
        self._reale = configurato

    # ------------------------------------------------------------- elenco

    @property
    def modelli(self) -> List[ModelloConfigurato]:
        return list(self._modelli.values())

    @property
    def configurato(self) -> bool:
        """C'è almeno un modello vero a cui chiedere le letture?

        Un elenco non vuoto non basta: `modelli_da_impostazioni()` restituisce sempre almeno il segnaposto
        `PREDEFINITO`, anche quando nessuna variabile d'ambiente è stata impostata — punterebbe a un LM Studio
        locale che nel container non esiste. Questo flag distingue le due situazioni.
        """
        return self._reale

    def esiste(self, nome: str) -> bool:
        return nome in self._modelli

    def configurazione(self, nome: str) -> Optional[ModelloConfigurato]:
        return self._modelli.get(nome)

    def aggiorna_modelli(self, modelli: List[ModelloConfigurato], *, reale: bool) -> None:
        """Sostituisce l'elenco dei fornitori con quello letto dal database (la console).

        Sostituisce e non fonde, come `aggiorna()` per le assegnazioni: un fornitore eliminato in console deve
        sparire anche da qui, non restare finché il processo non riparte. Svuota anche la cache dei fornitori
        costruiti: un indirizzo o una chiave cambiati non devono restare quelli di prima fino al riavvio.
        """
        import time

        self._modelli = {m.nome: m for m in modelli}
        self._fornitori.clear()
        self._modelli_lette_a = time.monotonic()
        self._reale = reale

    def da_rileggere_modelli(self, ttl: float = 30.0) -> bool:
        """Come `da_rileggere()`, per l'elenco dei fornitori invece delle assegnazioni."""
        import time

        return time.monotonic() - self._modelli_lette_a > ttl

    # -------------------------------------------------------- assegnazioni

    def assegna(self, compito: Compito, nome: Optional[str]) -> None:
        """Registra o toglie un'assegnazione. `None` fa tornare al predefinito."""
        if nome is None:
            self._assegnazioni.pop(compito, None)
            return
        if nome not in self._modelli:
            raise ValueError(f"modello sconosciuto: {nome!r}")
        self._assegnazioni[compito] = nome

    def aggiorna(self, assegnazioni: Dict[Compito, str]) -> None:
        """Sostituisce tutte le assegnazioni con quelle lette dal database.

        Sostituisce e non fonde: un compito tolto dalla tabella deve tornare
        al predefinito, e una fusione lo lascerebbe assegnato per sempre al
        modello di prima.
        """
        import time

        self._assegnazioni = {
            compito: nome for compito, nome in assegnazioni.items() if nome
        }
        self._lette_a = time.monotonic()

    def da_rileggere(self, ttl: float = 30.0) -> bool:
        """Se vale la pena rileggere le assegnazioni dal database.

        Con più repliche dell'API, una modifica fatta su una deve arrivare
        alle altre: nessuna se ne accorgerebbe da sola. Mezzo minuto di
        ritardo è accettabile — è un cambio di configurazione, non una
        risposta — e costa una riga letta ogni trenta secondi per replica.
        """
        import time

        return time.monotonic() - self._lette_a > ttl

    def nome_per(self, compito: Compito) -> str:
        """Il nome del modello che serve questo compito, assegnato o no."""
        assegnato = self._assegnazioni.get(compito)
        if assegnato and assegnato in self._modelli:
            return assegnato
        if assegnato:
            # Un modello tolto dall'ambiente mentre l'assegnazione restava:
            # va detto, perché il compito sta girando su un altro modello e
            # nessuno se ne accorgerebbe dai risultati.
            logger.warning(
                "Il compito «%s» era assegnato a «%s», che non è più fra i "
                "modelli configurati: si usa il predefinito",
                compito.value, assegnato,
            )
        if PREDEFINITO in self._modelli:
            return PREDEFINITO
        return next(iter(self._modelli), "")

    def per(self, compito: Compito):
        """Il fornitore che serve questo compito."""
        nome = self.nome_per(compito)
        if not nome:
            raise RuntimeError(
                "nessun modello configurato: nessun fornitore in console e "
                "non esiste nemmeno un modello predefinito dall'ambiente"
            )
        return self._fornitore(nome)

    def stato(self) -> List[dict]:
        """Cosa mostrare in console: i compiti, chi li serve, e perché."""
        return [
            {
                "compito": compito.value,
                "label": compito.label,
                "descrizione": compito.descrizione,
                "assegnato": self._assegnazioni.get(compito),
                "in_uso": self.nome_per(compito),
                "senza_filtri": bool(
                    (m := self._modelli.get(self.nome_per(compito)))
                    and m.senza_filtri
                ),
            }
            for compito in Compito
        ]

    # ------------------------------------------------------------- interno

    def _fornitore(self, nome: str):
        if nome in self._fornitori:
            return self._fornitori[nome]

        configurazione = self._modelli[nome]
        if configurazione.provider == "anthropic":
            from .anthropic import AnthropicProvider

            fornitore = AnthropicProvider(
                base_url=configurazione.base_url or None,
                api_key=configurazione.api_key or None,
                default_model=configurazione.model,
            )
        else:
            from .openai_compatible import OpenAICompatibleProvider

            fornitore = OpenAICompatibleProvider(
                base_url=configurazione.base_url or None,
                api_key=configurazione.api_key or None,
                default_model=configurazione.model,
                motore=configurazione.motore or None,
                ragiona=configurazione.ragiona,
                parametri=configurazione.parametri,
                # Il nome finisce nelle tracce: senza, due modelli diversi
                # comparirebbero entrambi come «openai-compatibile» e non si
                # saprebbe quale ha prodotto quale risposta.
                name=nome,
            )

        self._fornitori[nome] = fornitore
        return fornitore


def modelli_da_impostazioni() -> List[ModelloConfigurato]:
    """L'elenco dei modelli, dall'ambiente.

    Senza elenco se ne ricava uno di un elemento dalle vecchie impostazioni
    `TAROT_LLM_*`: un impianto che funzionava prima continua a funzionare
    senza toccare nulla, e i cinque compiti girano tutti su quel modello
    finché qualcuno non decide altrimenti.
    """
    from ..settings import get_settings

    s = get_settings()
    if s.modelli:
        return list(s.modelli)

    return [
        ModelloConfigurato(
            nome=PREDEFINITO,
            provider=s.llm_provider,
            base_url=(
                s.anthropic_base_url if s.llm_provider == "anthropic" else s.llm_base_url
            ),
            model=(
                s.anthropic_model if s.llm_provider == "anthropic" else s.llm_model
            ),
            api_key=(
                s.anthropic_api_key if s.llm_provider == "anthropic" else s.llm_api_key
            ),
            parametri={} if s.llm_provider == "anthropic" else s.llm_parametri,
            descrizione="Dalle impostazioni TAROT_LLM_*",
        )
    ]
