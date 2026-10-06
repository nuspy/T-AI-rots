"""Le scelte di configurazione che si fanno dalla console.

**I fornitori LLM si configurano da qui, non dall'ambiente.** Fino al 2026-09-27 questo file diceva il contrario
(«un endpoint modificabile dall'interfaccia è traffico dirottabile»): la console poteva solo *scegliere* fra nomi
elencati in `TAROT_MODELLI`. La scelta è cambiata (progetto `llmswitch` dell'utente, che tiene i fornitori in un
registro modificabile da chi amministra, non nell'ambiente del processo): un'amministrazione già autenticata con il
ruolo `admin` è il confine di fiducia giusto, e tenere indirizzi e chiavi fuori dal repository (niente nel Secret di
Kubernetes, niente da ridistribuire con l'immagine) è comunque un guadagno. La chiave resta **cifrata a riposo**
(`llm/cifratura.py`) e non esce mai in chiaro da un endpoint: la console vede solo `has_key: bool`.

`ModelAssignment` resta una riga per compito, non uno storico: conta l'assegnazione di adesso. Non ha vincolo di
chiave esterna verso `llm_providers` per la stessa ragione di sempre — se il nome sparisce (fornitore cancellato) il
compito ricade sul predefinito, e il registro lo dice nei log invece di rompersi. Chi ha cambiato cosa sta nel
registro di audit, che è il posto delle storie.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ModelAssignment(Base, TimestampMixin):
    """A quale modello è assegnato un compito."""

    __tablename__ = "model_assignments"

    #: Il valore di `Compito`: conversazione, digestione, recupero, giudizio.
    task: Mapped[str] = mapped_column(String(40), primary_key=True)
    #: Il nome del fornitore in `llm_providers.nome`. Non c'è vincolo di chiave
    #: esterna: se il nome sparisce (fornitore cancellato) il compito ricade
    #: sul predefinito, e il registro lo dice nei log invece di far fallire
    #: l'avvio.
    model_name: Mapped[str] = mapped_column(String(60), nullable=False)
    #: Chi l'ha deciso. Nullo se l'ha fatto un processo automatico.
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )
    #: Se questo COMPITO ragiona, a prescindere da cosa dichiara il fornitore assegnato.
    #: `NULL` = eredita da `llm_providers.ragiona` (comportamento di prima di v7). Un valore
    #: esplicito sovrascrive: due compiti sullo stesso fornitore possono così avere reasoning
    #: diverso (bug corretto in v7: prima si duplicava il fornitore per ottenere lo stesso
    #: effetto, vedi `llm/compiti.py`). Le righe nuove nascono a `False` (default richiesto
    #: dall'operatore), non `NULL`: v7 vuole il ragionamento spento ovunque per default, non
    #: "eredita" per i compiti non ancora toccati.
    ragiona_override: Mapped[Optional[bool]] = mapped_column(Boolean)
    #: Parametri aggiuntivi (`reasoning_budget`, `chat_template_kwargs`, ecc.) SOLO per questo
    #: compito, sovrapposti a quelli del fornitore assegnato. `NULL`/vuoto = eredita.
    parametri_override: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    #: Il livello di ragionamento del compito (`none` … `max`). `NULL` = eredita dal fornitore. `ragiona_override`
    #: resta, allineato (`NULL` se il livello è `NULL`, altrimenti `livello != none`).
    livello_ragionamento: Mapped[Optional[str]] = mapped_column(String(10))
    #: Lo schema JSON rigoroso nelle risposte strutturate, con ripiego automatico. `NULL` = spento.
    json_schema: Mapped[Optional[bool]] = mapped_column(Boolean)


class ImpostazioniCrediti(Base, TimestampMixin):
    """I numeri del regalo d'iscrizione e del referral: una riga sola, configurata dalla console.

    `crediti_invito` è il **totale** che l'invitato deve avere in saldo dopo il riscatto, non un extra rispetto al
    regalo d'iscrizione: chi riscatta un codice non deve sommare i due, deve arrivare esattamente a questo numero
    (vedi `billing/referral.py`). `commissione_referral_percentuale` è la quota (0-100) di ogni acquisto futuro di
    un invitato che finisce a chi lo ha invitato, per sempre — non solo alla prima volta.

    Una riga sola (`id` fisso a 1, come `ModelAssignment` per lo stile ma qui un solo record invece di uno per
    chiave): non serve un elenco, e un singleton evita la domanda «quale riga vale» che una tabella libera
    porrebbe."""

    __tablename__ = "impostazioni_crediti"
    __table_args__ = (CheckConstraint("id = 1", name="ck_impostazioni_crediti_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    crediti_iscrizione: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    crediti_invito: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    commissione_referral_percentuale: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )


class ImpostazioniChat(Base, TimestampMixin):
    """La sola manopola della chat proattiva (v6, Fase E): dopo quanti minuti di inattività l'AI
    apre da sola una conversazione. Singleton come `ImpostazioniCrediti`, stessa ragione."""

    __tablename__ = "impostazioni_chat"
    __table_args__ = (CheckConstraint("id = 1", name="ck_impostazioni_chat_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    proattiva_minuti_inattivita: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    #: v8.5: quante volte, al più, l'oracolo apre da solo in una visita (al caricamento e dopo il silenzio).
    #: Ogni apertura è un'inferenza: le risposte ai messaggi scritti dall'utente non contano.
    proattiva_max_per_visita: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )


class ImpostazioniSessione(Base, TimestampMixin):
    """La durata massima della sessione (v6, Fase G): **non più usata**.

    Era uno specchio di `ssoSessionMaxLifespan`, che poteva mentire dopo un cambio fatto a mano sul realm. Il
    login persistente ora è la sessione offline di Keycloak, e la console ne legge e scrive le durate
    direttamente lì (`api/routers/admin_impostazioni.py`, `auth/keycloak_admin.py`): nessuno scrive più questa
    tabella. Resta finché una migrazione non la toglie."""

    __tablename__ = "impostazioni_sessione"
    __table_args__ = (CheckConstraint("id = 1", name="ck_impostazioni_sessione_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    sso_session_max_lifespan_secondi: Mapped[int] = mapped_column(Integer, nullable=False, default=36000)
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )


class LlmProvider(Base, TimestampMixin):
    """Un fornitore LLM configurato dalla console: indirizzo, modello, chiave cifrata.

    `nome` è l'identificativo stabile che `ModelAssignment.model_name` cita: non si rinomina da qui (si cancella e se
    ne crea uno nuovo), perché cambiarlo farebbe ricadere sui predefiniti, senza preavviso, i compiti che lo citavano.
    `tipo` viene dal catalogo chiuso di `llm.catalogo_fornitori` (decide l'etichetta e i valori predefiniti mostrati
    in console); `provider` è il dialetto che il codice sa parlare (`openai-compatible` o `anthropic`).
    """

    __tablename__ = "llm_providers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False, default="openai-compatible")
    base_url: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    #: Il modello che VETTORIZZA, quando questo fornitore ne offre uno diverso da quello di chat.
    embed_model: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    #: La chiave, cifrata con `llm/cifratura.py` (Fernet). Nullo: nessuna chiave (server locale senza autenticazione).
    api_key_cifrata: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: Che motore sta dietro l'indirizzo: vuoto (deduce), openai, vllm, llamacpp, lmstudio, other.
    motore: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    ragiona: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Il livello di ragionamento predefinito (`none` … `max`, `llm/ragionamento.py`), che i compiti ereditano.
    #: `ragiona` resta, allineato (`livello != none`), per il margine di budget lato applicazione.
    livello_ragionamento: Mapped[str] = mapped_column(String(10), nullable=False, default="none")
    #: Campi aggiunti a ogni richiesta a questo fornitore (vedi `ModelloConfigurato.parametri`).
    parametri: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    #: Un modello «abliterato»: non rifiuta nulla. Solo informativo, non blocca l'assegnazione.
    senza_filtri: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Come si presenta in console. Non ha effetto sul comportamento.
    descrizione: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    #: Un fornitore spento non compare fra quelli assegnabili, ma resta configurato (si riaccende senza rifare la
    #: chiave): utile per un fornitore in prova o momentaneamente giù.
    attivo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )


class ImpostazioniPubblicita(Base, TimestampMixin):
    """Gli spazi pubblicitari del sito: l'interruttore generale, chi li riempie, quali dei tre si vedono.

    Singleton come le altre impostazioni. **Spenta per default**: senza la riga, o con `attiva` falso, il sito non
    riserva spazi e non carica script. Le tre posizioni (`terzo`, `due_terzi`, `fine`) hanno ognuna la sua casella,
    indipendente dall'interruttore: si può spegnere un solo banner senza toccare gli altri. `fornitore` dice quale
    riga di `pubblicita_fornitori` riempie gli spazi (oggi solo `google`); i parametri di ciascuno stanno là, così
    un fornitore nuovo (affiliazioni, spazi venduti direttamente) è una riga in più, non una colonna in più."""

    __tablename__ = "impostazioni_pubblicita"
    __table_args__ = (CheckConstraint("id = 1", name="ck_impostazioni_pubblicita_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    attiva: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fornitore: Mapped[str] = mapped_column(String(40), nullable=False, default="google")
    #: `{"terzo": bool, "due_terzi": bool, "fine": bool}`: quali banner si vedono.
    posizioni: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    #: Prefissi d'indirizzo (`/pricing`, `/it/prezzi`) dove non compare nessuno spazio, oltre a quelli esclusi nel codice.
    pagine_escluse: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )


class PubblicitaFornitore(Base, TimestampMixin):
    """I parametri di un fornitore di pubblicità (oggi Google AdSense), una riga per fornitore.

    `parametri` sono pubblici per natura (l'ID editore e gli ID degli slot stanno nell'HTML di ogni pagina che mostra
    un annuncio): il sito li riceve. `registrazione` sono i dati dell'iscrizione (email dell'account, titolare, stato
    della verifica, note): non sono segreti, ma restano della console — nessun endpoint pubblico li espone."""

    __tablename__ = "pubblicita_fornitori"

    fornitore: Mapped[str] = mapped_column(String(40), primary_key=True)
    parametri: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    registrazione: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )


class ImpostazioniIntervista(Base, TimestampMixin):
    """Quante domande fa l'oracolo prima delle carte (v8.5): il minimo e il massimo, dalla console.

    Fra i due decide il modello; dopo il minimo chi consulta può dire «basta così» e passare al rituale. Singleton
    come le altre impostazioni. Senza la riga valgono i default di `settings` (`intervista_min_domande`,
    `intervista_max_domande`)."""

    __tablename__ = "impostazioni_intervista"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_impostazioni_intervista_singleton"),
        CheckConstraint(
            "min_domande >= 0 AND max_domande >= 1 AND max_domande >= min_domande AND max_domande <= 12",
            name="ck_impostazioni_intervista_limiti",
        ),
        CheckConstraint("validatore_domande IN ('dubbi', 'spento', 'acceso')", name="ck_impostazioni_intervista_validatore"),
        CheckConstraint("guardia_responso IN ('dubbi', 'spento', 'acceso')", name="ck_impostazioni_intervista_guardia"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: v9.5: da 0 (si può passare alle carte fin dalla prima domanda) e predefiniti 0–2 (prima 2–6).
    min_domande: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_domande: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    #: Il controllo LLM delle domande candidate (`tarot/intervista.py::_giudica`), dopo i controlli deterministici che
    #: restano sempre: `dubbi` solo quando una regola leggera segnala un sospetto (`sospetta`), `spento` mai, `acceso`
    #: per ogni domanda (com'era prima).
    validatore_domande: Mapped[str] = mapped_column(String(10), nullable=False, default="dubbi")
    #: La guardia LLM del responso (`guards/lettura.py::giudica`): `dubbi` solo quando il controllo deterministico
    #: (`guards/lettura.py::da_guardare`) trova qualcosa, `spento` mai (resta il filtro deterministico), `acceso` sempre.
    guardia_responso: Mapped[str] = mapped_column(String(10), nullable=False, default="dubbi")
    #: Lo stato sintetico della memoria (`tarot/stato_memoria.py`) entra nei prompt di oracolo, intervista e sintesi al
    #: posto delle memorie di prima. Spento finché l'operatore non approva: lo stato si aggiorna comunque.
    memoria_stato_nei_prompt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )
