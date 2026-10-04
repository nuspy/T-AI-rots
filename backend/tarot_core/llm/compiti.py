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
from dataclasses import dataclass, replace
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
    #: L'anteprima breve del responso per chi non è registrato (`tarot/teaser.py`). Senza assegnazione usa il
    #: fornitore della sintesi, ma col ragionamento spento (`LIVELLO_PREDEFINITO_COMPITO`): non eredita il suo livello.
    TEASER = "teaser"
    #: Traduzione di un articolo del blog in un'altra lingua (v5, fase E): non durante una lettura, ma
    #: su richiesta esplicita dalla console, sempre in bozza per la revisione editoriale.
    TRADUZIONE_ARTICOLO = "traduzione_articolo"
    #: Traduzione dei testi lunghi di carte e stese in una nuova lingua (v5, fase D): uno strumento
    #: offline (`tools/traduci_conoscenza.py`), mai in produzione — la bozza richiede sempre una
    #: revisione umana prima di entrare in `LINGUE_CONTENUTO`.
    TRADUZIONE_CONOSCENZA = "traduzione_conoscenza"
    #: Scrittura delle scene per le immagini di un mazzo nuovo (v5, "mazzi multipli"): uno strumento
    #: offline (`tools/crea_mazzo.py`), mai in produzione — la scena scritta è sempre una bozza da
    #: approvare a mano prima di generare l'immagine vera.
    CREAZIONE_MAZZO = "creazione_mazzo"
    #: Vettorizzazione per la memoria RAG (v6, fase A): domande, sintesi e memorie estratte diventano
    #: un vettore per il recupero per pertinenza. Non tutti i fornitori lo offrono (Anthropic no):
    #: verificare `llm.base.supporta_embedding()` prima di assegnarlo, non solo alla chiamata.
    EMBEDDING = "embedding"
    #: Estrae i fatti stabili/variabili da una lettura appena conclusa, per ricordarli alle
    #: prossime (v6, fase B). Gira dopo la sintesi, mai durante: la memoria nasce da un fatto concluso.
    MEMORIA_ESTRAZIONE = "memoria_estrazione"
    #: La chat proattiva (v6, fase E): apre da sola una conversazione basandosi sulle memorie, e
    #: propone letture sul tema in corso. Testo libero + un campo di proposta strutturato.
    CHAT_PROATTIVA = "chat_proattiva"
    #: L'interpretazione dei dati degli analytics (v8): su richiesta dalla console, mai durante una
    #: lettura. Riceve solo aggregati già calcolati (fatti numerati), mai dati di singole persone.
    ANALISI_DATI = "analisi_dati"

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
    Compito.TEASER: "Anteprima del responso (senza account)",
    Compito.TRADUZIONE_ARTICOLO: "Traduzione articoli del blog",
    Compito.TRADUZIONE_CONOSCENZA: "Traduzione di carte e stese (offline)",
    Compito.CREAZIONE_MAZZO: "Scene di un mazzo nuovo (offline)",
    Compito.EMBEDDING: "Vettorizzazione per la memoria (RAG)",
    Compito.MEMORIA_ESTRAZIONE: "Aggiornamento della memoria dopo una lettura",
    Compito.CHAT_PROATTIVA: "Chat proattiva basata sulla memoria",
    Compito.ANALISI_DATI: "Interpretazione dei dati (analytics)",
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
        "Legge tutte le carte della lettura in una chiamata sola (una risposta JSON, divisa dal "
        "codice carta per carta), ognuna nella sua posizione. Le carte che la risposta non copre "
        "si leggono una per una, come prima."
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
    Compito.TEASER: (
        "Scrive le due o tre frasi che chi non ha un account legge al posto del responso. Senza una scelta "
        "qui usa il modello della sintesi, ma senza ragionamento: è un testo breve, non serve pensarci "
        "a lungo (e la sintesi può ragionare molto)."
    ),
    Compito.TRADUZIONE_ARTICOLO: (
        "Traduce titolo, sottotitolo, corpo e campi SEO di un articolo del blog già pubblicato in "
        "un'altra lingua. Non gira durante una lettura: solo su richiesta dalla console, e il "
        "risultato è sempre salvato come bozza, mai pubblicato da solo."
    ),
    Compito.TRADUZIONE_CONOSCENZA: (
        "Traduce le schede di carte e stese in una nuova lingua, una alla volta, per uno script "
        "offline lanciato a mano — mai durante una lettura vera. Il risultato è sempre una bozza da "
        "far rivedere a una persona."
    ),
    Compito.CREAZIONE_MAZZO: (
        "Scrive la scena da dipingere per una carta di un mazzo nuovo, data la sua identità esoterica "
        "e lo stile/ambientazione scelti dall'utente, per uno script offline lanciato a mano — mai "
        "durante una lettura vera. Il risultato è sempre una bozza da approvare prima di generare "
        "l'immagine."
    ),
    Compito.EMBEDDING: (
        "Trasforma un testo (una domanda, una sintesi, una memoria estratta) in un vettore, per "
        "ritrovare ciò che è pertinente a una lettura o una conversazione. Non è generazione di "
        "testo: il fornitore assegnato deve offrire un endpoint di embedding. Oggi non si usa: la "
        "memoria è un riassunto breve, senza vettori (si riaccende con TAROT_MEMORIA_EMBEDDING)."
    ),
    Compito.MEMORIA_ESTRAZIONE: (
        "Dopo ogni lettura conclusa aggiorna il riassunto breve che il lettore tiene su chi consulta: "
        "fatti stabili, situazioni in corso e temi recenti. Una chiamata breve in background, sempre "
        "senza ragionamento qualunque sia la scelta qui sotto; ciò che è vecchio lo dimentica il codice."
    ),
    Compito.CHAT_PROATTIVA: (
        "Apre o continua una conversazione con un utente già loggato, basandosi sulle sue memorie, "
        "e può proporre una lettura sul tema in corso. Non è la sintesi di una lettura: è un "
        "compagno che tiene viva l'interazione, con un tono più leggero e diretto."
    ),
    Compito.ANALISI_DATI: (
        "Legge i fatti numerati di una sezione degli analytics (traffico, utenti, ricavi…) e li mette "
        "in relazione: collegamenti, ipotesi, azioni con la loro metrica. Conta il ragionamento più "
        "della velocità: un modello forte, anche col ragionamento acceso. Riceve solo aggregati."
    ),
}


#: I compiti che, **senza assegnazione**, usano il fornitore di un altro compito invece del predefinito: l'anteprima
#: è scritta dallo stesso modello del responso, come prima che avesse un compito suo.
FORNITORE_DI: Dict[Compito, Compito] = {Compito.TEASER: Compito.SINTESI}

#: I compiti con un livello di ragionamento proprio quando la console non ne sceglie uno (assegnazione assente, o senza
#: livello): non ereditano quello del fornitore. L'anteprima non deve ragionare a `xhigh` solo perché la sintesi lo fa.
LIVELLO_PREDEFINITO_COMPITO: Dict[Compito, str] = {Compito.TEASER: "none"}


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
    #: Il modello che VETTORIZZA, quando questo fornitore ne offre uno diverso da quello di chat.
    #: Vuoto: `embed()` ricade su `model`.
    embed_model: str = ""
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
    #: Il tipo del catalogo (`llm/catalogo_fornitori.py`: `nebius`, `nvidia`, `lmstudio`…): decide il dialetto del
    #: ragionamento (`llm/ragionamento.py`). Vuoto per i modelli dall'ambiente.
    tipo: str = ""
    #: Il livello di ragionamento predefinito del fornitore (`none` … `max`), che i compiti ereditano. Vuoto: un
    #: modello configurato prima dei livelli, che segue ancora `ragiona` e i suoi `parametri` come prima.
    livello_ragionamento: str = ""

    @field_validator("parametri")
    @classmethod
    def _parametri_ammessi(cls, valore: Dict[str, Any]) -> Dict[str, Any]:
        return controlla_parametri(valore)

    @field_validator("livello_ragionamento")
    @classmethod
    def _livello_ammesso(cls, valore: str) -> str:
        from .ragionamento import valido

        return valido(valore) or ""


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


@dataclass(frozen=True)
class AssegnazioneModello:
    """A quale modello serve un compito, con eventuali sovrascritture SOLO per lui (v7).

    Prima di v7 un'assegnazione era solo un nome: due compiti sullo stesso fornitore condividevano
    inevitabilmente `ragiona`/`parametri`, e l'unico modo per avere lo stesso modello con e senza
    ragionamento era duplicare il fornitore in console (vedi il commento su `ModelloConfigurato.
    parametri`). `ragiona_override`/`parametri_override` (`None` = eredita dal fornitore assegnato)
    tolgono quel bisogno.
    """

    nome: str
    ragiona_override: Optional[bool] = None
    parametri_override: Optional[Dict[str, Any]] = None
    #: Il livello di ragionamento di questo compito (`none` … `max`). `None`: eredita dal fornitore.
    livello: Optional[str] = None
    #: Lo schema JSON rigoroso nelle risposte strutturate (`llm/schemi_json.py`), con ripiego automatico se il
    #: fornitore lo rifiuta. `None`: spento (il predefinito, finché non lo si prova su Nebius).
    json_schema: Optional[bool] = None

    def sostituisce(self) -> bool:
        """Se l'assegnazione cambia qualcosa oltre al nome del fornitore."""
        return (
            self.ragiona_override is not None or bool(self.parametri_override) or self.livello is not None
            or self.json_schema is not None
        )


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
        assegnazioni: Optional[Dict[Compito, AssegnazioneModello]] = None,
        configurato: bool = True,
    ) -> None:
        self._modelli = {m.nome: m for m in modelli}
        self._assegnazioni: Dict[Compito, AssegnazioneModello] = dict(assegnazioni or {})
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

    def assegna(
        self, compito: Compito, nome: Optional[str], *,
        ragiona_override: Optional[bool] = None, parametri_override: Optional[Dict[str, Any]] = None,
        livello: Optional[str] = None, json_schema: Optional[bool] = None,
    ) -> None:
        """Registra o toglie un'assegnazione. `None` fa tornare al predefinito."""
        if nome is None:
            self._assegnazioni.pop(compito, None)
            return
        if nome not in self._modelli:
            raise ValueError(f"modello sconosciuto: {nome!r}")
        self._assegnazioni[compito] = AssegnazioneModello(
            nome, ragiona_override, parametri_override, livello=livello, json_schema=json_schema,
        )

    def aggiorna(self, assegnazioni: Dict[Compito, AssegnazioneModello]) -> None:
        """Sostituisce tutte le assegnazioni con quelle lette dal database.

        Sostituisce e non fonde: un compito tolto dalla tabella deve tornare
        al predefinito, e una fusione lo lascerebbe assegnato per sempre al
        modello di prima.
        """
        import time

        self._assegnazioni = {
            compito: a for compito, a in assegnazioni.items() if a.nome
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
        assegnazione = self._assegnazioni.get(compito)
        nome = assegnazione.nome if assegnazione else None
        if nome and nome in self._modelli:
            return nome
        if nome:
            # Un modello tolto dall'ambiente mentre l'assegnazione restava:
            # va detto, perché il compito sta girando su un altro modello e
            # nessuno se ne accorgerebbe dai risultati.
            logger.warning(
                "Il compito «%s» era assegnato a «%s», che non è più fra i "
                "modelli configurati: si usa il predefinito",
                compito.value, nome,
            )
        if compito in FORNITORE_DI:
            return self.nome_per(FORNITORE_DI[compito])
        if PREDEFINITO in self._modelli:
            return PREDEFINITO
        return next(iter(self._modelli), "")

    def per(self, compito: Compito, *, senza_ragionamento: bool = False):
        """Il fornitore che serve questo compito.

        `senza_ragionamento`: per le chiamate che il codice vuole brevi qualunque cosa dica la console (l'aggiornamento
        dello stato sintetico della memoria, `tarot/stato_memoria.py`). Il ragionamento si spegne nello stesso modo di
        un livello `none` scelto in console — `_configurazione_per`, il punto unico.
        """
        nome = self.nome_per(compito)
        if not nome:
            raise RuntimeError(
                "nessun modello configurato: nessun fornitore in console e "
                "non esiste nemmeno un modello predefinito dall'ambiente"
            )
        valida = self._assegnazione_valida(compito, nome)
        if senza_ragionamento:
            valida = replace(valida or AssegnazioneModello(nome), ragiona_override=False, livello="none")
        if (valida is not None and valida.sostituisce()) or compito in LIVELLO_PREDEFINITO_COMPITO:
            # Mai in cache (anche un compito col suo livello predefinito, che non è quello del fornitore): due compiti sullo stesso fornitore con sostituzioni diverse non devono scambiarsele.
            # Costruire un oggetto è economico (nessuna rete), e il dialetto JSON negoziato si ricorda comunque per
            # indirizzo e modello (`openai_compatible._DIALETTI_NOTI`).
            return self._costruisci(self._configurazione_per(nome, compito, valida), f"{nome}+override", compito)
        return self._fornitore(nome, compito)

    def _assegnazione_valida(self, compito: Compito, nome: str) -> Optional[AssegnazioneModello]:
        """L'assegnazione del compito se punta ancora al modello in uso: se `nome_per` è ricaduto sul predefinito
        (modello assegnato sparito), le sostituzioni di un'assegnazione ormai orfana non si applicano."""
        assegnazione = self._assegnazioni.get(compito)
        if isinstance(assegnazione, AssegnazioneModello) and assegnazione.nome == nome:
            return assegnazione
        return None

    def json_schema_di(self, compito: Compito) -> bool:
        """Se il compito prova lo schema JSON rigoroso: l'assegnazione se lo dice, altrimenti spento."""
        a = self._assegnazione_valida(compito, self.nome_per(compito))
        return bool(a is not None and a.json_schema)

    def ragionamento_di(self, compito: Compito) -> Dict[str, Any]:
        """Quanto ragiona **davvero** questo compito, e da dove viene la scelta.

        È lo stesso calcolo di `per()` (`_configurazione_per`), senza costruire il fornitore: la console deve mostrare
        ciò che succede, non solo ciò che è scritto nell'assegnazione. Un compito senza assegnazione (o con
        un'assegnazione che non dice il livello) eredita dal fornitore in uso — in produzione è il caso dell'oracolo e
        della memoria, che ragionavano senza che la casella lo mostrasse.

        - `livello`: `none` … `max`, o `None` per un fornitore configurato prima dei livelli (lì conta `effettivo`);
        - `effettivo`: il modello riceve il ragionamento acceso;
        - `origine`: `compito` (scelto per questo compito in console), `parametri` (deciso dai parametri scritti a mano
          sull'assegnazione), `fornitore` (ereditato dal fornitore in uso), `predefinito` (il livello proprio del
          compito, `LIVELLO_PREDEFINITO_COMPITO`, finché la console non ne sceglie un altro) o `codice` (spento dal
          servizio comunque: `_spento_dal_codice`);
        - `fornitore`: il nome del fornitore in uso; `livello_fornitore`: il suo predefinito;
        - `spegnibile`: l'applicazione sa come spegnerlo nella richiesta (un livello c'è sempre, o il fornitore di prima
          dichiara `chat_template_kwargs.enable_thinking`). Se no, cambia solo il margine di budget lato applicazione.
        """
        nome = self.nome_per(compito)
        base = self._modelli.get(nome)
        if base is None:
            return {"livello": None, "effettivo": False, "origine": "fornitore", "fornitore": nome,
                    "livello_fornitore": None, "spegnibile": False}
        if self._spento_dal_codice(compito):
            # Il vettore non ragiona; lo stato sintetico della memoria chiede sempre `senza_ragionamento`.
            return {"livello": "none", "effettivo": False, "origine": "codice", "fornitore": nome,
                    "livello_fornitore": base.livello_ragionamento or None, "spegnibile": True}
        livello, origine = self._livello(base, self._assegnazione_valida(compito, nome), compito)
        configurazione = self._configurazione_per(nome, compito, self._assegnazione_valida(compito, nome))
        kwargs = (self._assegnazione_valida(compito, nome) or AssegnazioneModello(nome)).parametri_override or {}
        if isinstance(kwargs.get("chat_template_kwargs"), dict) and "enable_thinking" in kwargs["chat_template_kwargs"]:
            origine = "parametri"
        kwargs_base = base.parametri.get("chat_template_kwargs")
        spegnibile = livello is not None or (isinstance(kwargs_base, dict) and "enable_thinking" in kwargs_base)
        return {
            "livello": livello, "effettivo": configurazione.ragiona, "origine": origine, "fornitore": nome,
            "livello_fornitore": base.livello_ragionamento or None, "spegnibile": spegnibile,
        }

    def stato(self) -> List[dict]:
        """Cosa mostrare in console: i compiti, chi li serve, e perché."""
        from .schemi_json import COMPITI_CON_SCHEMA

        righe = []
        for compito in Compito:
            assegnazione = self._assegnazioni.get(compito)
            assegnazione = assegnazione if isinstance(assegnazione, AssegnazioneModello) else None
            in_uso = self.nome_per(compito)
            ragionamento = self.ragionamento_di(compito)
            righe.append({
                "compito": compito.value,
                "label": compito.label,
                "descrizione": compito.descrizione,
                "assegnato": assegnazione.nome if assegnazione else None,
                "ragiona_override": assegnazione.ragiona_override if assegnazione else None,
                #: Il livello scelto per il compito (`None`: eredita dal fornitore).
                "livello": assegnazione.livello if assegnazione else None,
                #: Lo stato vero: il livello in uso, acceso o spento, e chi l'ha deciso (vedi `ragionamento_di`).
                "livello_effettivo": ragionamento["livello"],
                "livello_fornitore": ragionamento["livello_fornitore"],
                "ragiona_effettivo": ragionamento["effettivo"],
                "ragiona_origine": ragionamento["origine"],
                "ragiona_spegnibile": ragionamento["spegnibile"],
                #: Il livello del compito quando la console non ne sceglie uno (`None`: eredita dal fornitore).
                "livello_predefinito": LIVELLO_PREDEFINITO_COMPITO.get(compito),
                #: Senza assegnazione usa il fornitore di questo compito invece del predefinito (`None`: il predefinito).
                "segue": FORNITORE_DI[compito].value if compito in FORNITORE_DI else None,
                #: Lo schema JSON rigoroso: in uso, e se il compito risponde in JSON (altrimenti non si offre).
                "json_schema": self.json_schema_di(compito),
                "schema_possibile": compito.value in COMPITI_CON_SCHEMA,
                "in_uso": in_uso,
                "senza_filtri": bool((m := self._modelli.get(in_uso)) and m.senza_filtri),
            })
        return righe

    # ------------------------------------------------------------- interno

    @staticmethod
    def _spento_dal_codice(compito: Compito) -> bool:
        """I compiti che non ragionano qualunque cosa dica la console: l'embedding (non genera testo) e l'aggiornamento
        della memoria, che chiama sempre `per(..., senza_ragionamento=True)` — finché non si riaccende la memoria di
        prima (`TAROT_MEMORIA_EMBEDDING`), la cui estrazione segue invece la console."""
        if compito == Compito.EMBEDDING:
            return True
        if compito == Compito.MEMORIA_ESTRAZIONE:
            from ..settings import get_settings

            return not get_settings().memoria_embedding
        return False

    def _fornitore(self, nome: str, compito: Optional[Compito] = None):
        """Il fornitore condiviso dei compiti senza sostituzioni, in cache per nome: quello che li distingue (livello,
        schema JSON) passa solo dalle sostituzioni, che non usano questa cache."""
        if nome in self._fornitori:
            return self._fornitori[nome]
        fornitore = self._costruisci(self._configurazione_per(nome, None, None), nome)
        self._fornitori[nome] = fornitore
        return fornitore

    @staticmethod
    def _livello(
        base: ModelloConfigurato, assegnazione: Optional[AssegnazioneModello], compito: Optional[Compito] = None,
    ) -> tuple:
        """Il livello di ragionamento del compito e la sua origine. `(None, …)`: un fornitore di prima dei livelli,
        senza livello neanche sul compito — lì vale ancora il booleano (`_parametri_coerenti`). Un compito con un
        livello proprio (`LIVELLO_PREDEFINITO_COMPITO`) senza una scelta in console usa quello (origine `predefinito`)."""
        from .ragionamento import livello_da_bool, valido

        if assegnazione is not None and valido(assegnazione.livello):
            return assegnazione.livello, "compito"
        if compito in LIVELLO_PREDEFINITO_COMPITO and (assegnazione is None or assegnazione.ragiona_override is None):
            return LIVELLO_PREDEFINITO_COMPITO[compito], "predefinito"
        if base.livello_ragionamento:
            if assegnazione is not None and assegnazione.ragiona_override is not None:
                return livello_da_bool(assegnazione.ragiona_override), "compito"
            return base.livello_ragionamento, "fornitore"
        origine = "compito" if assegnazione is not None and assegnazione.ragiona_override is not None else "fornitore"
        return None, origine

    def _configurazione_per(
        self, nome: str, compito: Optional[Compito], assegnazione: Optional[AssegnazioneModello],
    ) -> ModelloConfigurato:
        """La configurazione con cui si costruisce il fornitore di un compito: **il punto unico** in cui il livello di
        ragionamento diventa parametri (`llm/ragionamento.py`) e `ragiona` (il margine di budget) lo segue.

        Con un livello (del compito o del fornitore) i parametri si riscrivono nel dialetto del fornitore, senza
        conflitti. Senza (un fornitore di prima dei livelli) vale il booleano: `ragiona_override` o `ragiona` del
        fornitore, allineato a `enable_thinking` se il fornitore lo dichiara (`_parametri_coerenti`). Un
        `parametri_override` scritto a mano resta l'ultima parola, e se accende o spegne `enable_thinking` il margine
        di budget lo segue: «app spenta, modello acceso» faceva finire il ragionamento nel testo (budget esaurito a
        metà pensiero, verificato su Nebius il 2026-09-30).
        """
        from .ragionamento import dialetto, parametri_per_livello, ragiona_da_livello, senza_conflitti

        base = self._modelli[nome]
        livello, _ = self._livello(base, assegnazione, compito)
        dialetto_ = dialetto(base.tipo, base.provider, base.parametri)
        if livello is not None:
            ragiona = ragiona_da_livello(livello)
            parametri = parametri_per_livello(base.parametri, livello, dialetto_)
        else:
            ragiona = base.ragiona
            if assegnazione is not None and assegnazione.ragiona_override is not None:
                ragiona = assegnazione.ragiona_override
            parametri = _parametri_coerenti(base.parametri, ragiona)
        if assegnazione is not None and assegnazione.parametri_override:
            parametri = {**parametri, **assegnazione.parametri_override}
            if livello is not None:
                parametri = senza_conflitti(parametri, dialetto_)
            kwargs = parametri.get("chat_template_kwargs")
            if isinstance(kwargs, dict) and "enable_thinking" in kwargs:
                ragiona = bool(kwargs["enable_thinking"])
        return base.model_copy(update={
            "ragiona": ragiona, "parametri": parametri, "livello_ragionamento": livello or "",
        })

    def _costruisci(self, configurazione: ModelloConfigurato, nome_traccia: str, compito: Optional[Compito] = None):
        from .ragionamento import budget_anthropic

        if configurazione.provider == "anthropic":
            from .anthropic import AnthropicProvider

            return AnthropicProvider(
                base_url=configurazione.base_url or None,
                api_key=configurazione.api_key or None,
                default_model=configurazione.model,
                budget_ragionamento=budget_anthropic(configurazione.livello_ragionamento or None),
            )

        from .openai_compatible import OpenAICompatibleProvider

        return OpenAICompatibleProvider(
            base_url=configurazione.base_url or None,
            api_key=configurazione.api_key or None,
            default_model=configurazione.model,
            embed_model=configurazione.embed_model,
            motore=configurazione.motore or None,
            ragiona=configurazione.ragiona,
            livello_ragionamento=configurazione.livello_ragionamento,
            parametri=configurazione.parametri,
            # Il nome finisce nelle tracce: senza, due modelli diversi
            # comparirebbero entrambi come «openai-compatibile» e non si
            # saprebbe quale ha prodotto quale risposta.
            name=nome_traccia,
            json_schema=self.json_schema_di(compito) if compito is not None else False,
        )


def _parametri_coerenti(parametri: Dict[str, Any], ragiona: bool) -> Dict[str, Any]:
    """I `parametri` di un fornitore allineati al `ragiona` effettivo del compito.

    **Solo per i fornitori configurati prima dei livelli di ragionamento** (senza `livello_ragionamento`): per gli
    altri decide `llm/ragionamento.py`, chiamato da `RegistroModelli._configurazione_per`, il punto unico. Non aggiunge
    campi che il fornitore non dichiara già: si limita ad allineare quelli presenti.

    `ragiona` da solo decide soltanto il margine di budget lato applicazione (vedi
    `pavimento_ragionamento`): il MODELLO ragiona o no secondo `chat_template_kwargs.enable_thinking`
    che il fornitore manda. Bug osservato in produzione (2026-09-30): v7 aveva messo
    `ragiona_override=False` su ogni compito, ma il fornitore continuava a mandare
    `enable_thinking: true` — il modello ragionava sempre (risposte lente), senza più il margine di
    budget, e Nebius restituiva il ragionamento come testo normale ("Here's a thinking process:")
    dentro l'interpretazione delle carte e prima del JSON dei validatori.

    Si tocca solo una chiave che il fornitore dichiara già (`enable_thinking` dentro
    `chat_template_kwargs`): per un motore che non la conosce, nessuna modifica. Da spento si toglie
    anche `reasoning_budget`, che senza ragionamento non ha senso."""
    kwargs = parametri.get("chat_template_kwargs")
    if not isinstance(kwargs, dict) or "enable_thinking" not in kwargs:
        return parametri
    coerenti = {**parametri, "chat_template_kwargs": {**kwargs, "enable_thinking": ragiona}}
    if not ragiona:
        coerenti.pop("reasoning_budget", None)
    return coerenti


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
