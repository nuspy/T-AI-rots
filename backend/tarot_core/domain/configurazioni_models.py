"""Le configurazioni che l'operatore imposta dalla console (v9, Fase 2c): «Tutte le configurazioni devono essere lì».

Fino alla Fase 2 Stripe, la posta in uscita e i segreti interni arrivavano dall'ambiente del server (Secret di
Kubernetes): l'operatore non usa kubectl, e non deve doverlo fare. Ora stanno qui, cifrate come le chiavi dei
fornitori LLM (`llm/cifratura.py`, chiave master `TAROT_LLM_PROVIDER_KEY` che resta sul server e non nel database):
un dump del database — che finisce sul NAS — porta solo testo cifrato.

- **`ConfigStripe`**: il fornitore di pagamento attivo (`disattivato`/`mock`/`stripe`), la chiave segreta, la chiave
  pubblicabile, la modalità (prova o reale) e l'endpoint del webhook registrato da qui con il suo segreto `whsec_`.
- **`ConfigSmtp`**: la posta in uscita (email agli utenti e rapporti agli admin).
- **`ConfigTitolare`**: chi è il titolare del trattamento, per l'informativa privacy del sito.
- **`SegretoSistema`**: i segreti interni che nessuno deve vedere né scegliere (l'HMAC degli IP, il sale delle
  condivisioni): generati al primo avvio, o presi dall'ambiente se c'è.
- **`ImportazioneAmbiente`**: il registro delle copie fatte dall'ambiente al database al primo avvio — una per voce,
  mai due (la chiave primaria lo garantisce anche con più repliche dell'API che partono insieme).

Le tre configurazioni sono singleton (`id = 1`), come `ConfigGoogle`. L'ambiente resta il ripiego: una configurazione
vuota qui vuol dire «quello che dice l'ambiente» (`configurazioni/correnti.py`).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, LargeBinary, String, func, text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

FORNITORI_PAGAMENTO = ("disattivato", "mock", "stripe")
#: Il contatto privacy predefinito dell'informativa, finché l'operatore non ne scrive un altro.
EMAIL_PRIVACY_PREDEFINITA = "privacy@tarots.chat"
#: Fornitore, città e paese (codice ISO a due lettere, in fondo): neutro rispetto alla lingua. L'informativa traduce il
#: paese nella lingua della pagina («Hivelocity, London, Regno Unito» in italiano); fornitore e città restano così.
#: Prima (Fase 2c) era una frase in italiano, che compariva tale e quale anche nelle pagine in altre lingue.
HOSTING_PREDEFINITO = "Hivelocity, London, GB"
#: Il valore predefinito di prima: la migrazione della Fase 4 lo sostituisce dove nessuno l'ha cambiato.
HOSTING_PREDEFINITO_VECCHIO = "Hivelocity, data center di Londra (Regno Unito)"


class ConfigStripe(Base, TimestampMixin):
    __tablename__ = "config_stripe"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_config_stripe_singleton"),
        CheckConstraint(
            "provider is null or provider in ('disattivato', 'mock', 'stripe')", name="ck_config_stripe_provider",
        ),
        CheckConstraint("modalita is null or modalita in ('test', 'live')", name="ck_config_stripe_modalita"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: Chi incassa. Nullo: quello dell'ambiente (`TAROT_BILLING_PROVIDER`).
    provider: Mapped[Optional[str]] = mapped_column(String(12))
    #: `test` (chiavi `sk_test_`/`rk_test_`) o `live`: deve coincidere con la chiave, lo controlla la console.
    modalita: Mapped[Optional[str]] = mapped_column(String(4))
    #: La chiave segreta dell'API (`sk_…` o la limitata `rk_…`), cifrata. Nulla: quella dell'ambiente.
    chiave_segreta_cifrata: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: La chiave pubblicabile (`pk_…`): **non è un segreto** (Stripe la mette in ogni pagina di pagamento), per questo
    #: in chiaro e mostrata in console.
    chiave_pubblicabile: Mapped[Optional[str]] = mapped_column(String(200))
    #: Il segreto con cui Stripe firma gli eventi del webhook (`whsec_…`), cifrato. Lo restituisce Stripe una volta
    #: sola, quando l'endpoint si crea da qui.
    segreto_webhook_cifrato: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: L'endpoint registrato da qui (`we_…`) e il suo indirizzo, per aggiornarlo invece di crearne un doppione.
    webhook_id: Mapped[Optional[str]] = mapped_column(String(80))
    webhook_url: Mapped[Optional[str]] = mapped_column(String(300))
    webhook_registrato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: L'ultima «Prova la chiave»: quando, e l'esito (`{"ok": …, "messaggio": …, "account": …}`).
    ultima_prova_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    esito_prova: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class ConfigSmtp(Base, TimestampMixin):
    __tablename__ = "config_smtp"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_config_smtp_singleton"),
        CheckConstraint("porta between 1 and 65535", name="ck_config_smtp_porta"),
        CheckConstraint("sicurezza in ('ssl', 'starttls')", name="ck_config_smtp_sicurezza"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: Vuoto: si usa la posta dell'ambiente (`TAROT_SMTP_*`), se c'è.
    host: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    porta: Mapped[int] = mapped_column(Integer, nullable=False, default=465, server_default="465")
    #: `ssl`: SMTPS implicito (di solito 465). `starttls`: connessione in chiaro che passa a cifrata (di solito 587).
    sicurezza: Mapped[str] = mapped_column(String(8), nullable=False, default="ssl", server_default="ssl")
    utente: Mapped[str] = mapped_column(String(320), nullable=False, default="", server_default="")
    password_cifrata: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    mittente: Mapped[str] = mapped_column(String(320), nullable=False, default="", server_default="")
    nome_mittente: Mapped[str] = mapped_column(String(120), nullable=False, default="TAROTS chat", server_default="TAROTS chat")
    #: Il selettore DKIM del dominio del mittente (`<selettore>._domainkey.<dominio>`), per la sonda DNS. Vuoto: si
    #: provano i selettori più comuni.
    dkim_selettore: Mapped[str] = mapped_column(String(63), nullable=False, default="", server_default="")
    ultima_prova_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    esito_prova: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class ConfigTitolare(Base, TimestampMixin):
    """I dati del titolare del trattamento mostrati nell'informativa del sito. Nessun segreto: sono pubblici."""

    __tablename__ = "config_titolare"
    __table_args__ = (CheckConstraint("id = 1", name="ck_config_titolare_singleton"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: Nome e cognome, o ragione sociale.
    nome: Mapped[str] = mapped_column(String(200), nullable=False, default="", server_default="")
    indirizzo: Mapped[str] = mapped_column(String(400), nullable=False, default="", server_default="")
    #: Partita IVA o codice fiscale: facoltativo.
    codice_fiscale: Mapped[str] = mapped_column(String(40), nullable=False, default="", server_default="")
    email_privacy: Mapped[str] = mapped_column(
        String(320), nullable=False, default=EMAIL_PRIVACY_PREDEFINITA, server_default=EMAIL_PRIVACY_PREDEFINITA,
    )
    #: Il responsabile della protezione dei dati (DPO, art. 37 GDPR): nominato o no, e come contattarlo.
    dpo_nominato: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    dpo_contatto: Mapped[str] = mapped_column(String(400), nullable=False, default="", server_default="")
    hosting: Mapped[str] = mapped_column(
        String(300), nullable=False, default=HOSTING_PREDEFINITO, server_default=HOSTING_PREDEFINITO,
    )
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class SegretoSistema(Base):
    """Un segreto interno: mai mostrato, mai scelto da una persona. Una riga per nome, scritta una volta (o
    riallineata all'ambiente quando l'ambiente ne dà uno: vince l'ambiente, e resta qui se un giorno lo si toglie)."""

    __tablename__ = "segreti_sistema"
    __table_args__ = (
        CheckConstraint("origine in ('generato', 'ambiente')", name="ck_segreti_sistema_origine"),
    )

    nome: Mapped[str] = mapped_column(String(40), primary_key=True)
    valore_cifrato: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    origine: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(),
    )


class ImportazioneAmbiente(Base):
    """Una voce copiata dall'ambiente del server al database, al primo avvio. Esiste: non si copia più."""

    __tablename__ = "importazioni_ambiente"

    #: `smtp`, `stripe_chiavi`, `stripe_provider`, `backup_credenziale`.
    voce: Mapped[str] = mapped_column(String(40), primary_key=True)
    #: `importato` (copiato), `gia_in_console` (c'era già un valore: non si è toccato niente).
    esito: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
