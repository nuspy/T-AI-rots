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
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"),
    )


class ImpostazioniSessione(Base, TimestampMixin):
    """La durata massima della sessione (v6, Fase G), solo per mostrarla in console.

    La fonte di verità resta Keycloak (`ssoSessionMaxLifespan` del realm, cambiato da
    `auth/keycloak_admin.py`): questa riga è uno specchio, scritto solo quando il cambio su
    Keycloak riesce. Un admin che guarda solo questa tabella dopo un cambio fatto a mano sul realm
    (o dopo un reimport del realm JSON) vedrebbe un numero non più vero — vedi la nota sulla deriva
    in `deploy/keycloak/README.md`."""

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
