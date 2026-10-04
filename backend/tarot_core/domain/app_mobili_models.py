"""Le app native (v9, Fase 3): gli account degli store, i prodotti in vendita negli store, il pulsante Stripe.

Tre tabelle, tutte scritte solo dalla console «App mobili»:

- `config_app_mobili` (`ConfigAppMobile`): una riga per piattaforma (`android`, `ios`) e una per gli appunti di
  **Codemagic** (che costruisce le app). I campi che non sono segreti stanno in chiaro in `parametri` (package name,
  Team ID, versione minima, topic Pub/Sub…); le credenziali delle API degli store (il JSON del service account per la
  Play Developer API, la chiave `.p8` della App Store Server API) stanno in `segreti`, **cifrati** come le chiavi dei
  fornitori LLM (`llm/cifratura.py`): la console vede solo se ci sono, l'email del service account e gli ultimi
  caratteri dell'id della chiave, mai la chiave. `appunti_pagamenti` è il promemoria del profilo pagamenti dello store
  (beneficiario, banca, **solo le ultime 4 cifre** del conto): lo stesso trattamento degli appunti di AdSense.
- `prodotti_store` (`ProdottoStore`): il prodotto creato nello store (`product_id`) e il piano del sito che accredita
  (`plans`): un pacchetto di crediti è un prodotto **consumabile**, un abbonamento un **abbonamento**. Un `product_id`
  è unico per piattaforma: la Fase 4 risale dal prodotto comprato al piano senza ambiguità.
- `politica_stripe` (`PoliticaStripe`): se e come l'app mostra il pulsante per pagare con Stripe, per piattaforma e
  paese (ISO 3166-1 alpha-2, o `*` per «tutti gli altri»). Le regole degli store cambiano per paese e nel tempo:
  per questo è configurabile, e **senza una riga vale «nascosto»**.

Niente di questo esce verso le app tranne ciò che `GET /app/config` sceglie apposta (versione minima, flag).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, LargeBinary, String, UniqueConstraint, text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

#: Le righe di `config_app_mobili`: le due piattaforme e gli appunti di Codemagic.
RIGHE_CONFIG = ("android", "ios", "codemagic")
PIATTAFORME = ("android", "ios")
TIPI_PRODOTTO = ("consumabile", "abbonamento")
#: Come l'app mostra il pulsante Stripe:
#: - `nascosto`: non c'è (il predefinito, e l'unico sicuro ovunque);
#: - `link_esterno`: un collegamento al sito per pagare fuori dallo store, dove le regole lo permettono;
#: - `entitlement_ue`: nello Spazio economico europeo, con l'autorizzazione dello store (Apple «StoreKit External
#:   Purchase Link Entitlement», Google «programma di fatturazione alternativa»);
#: - `scelta_utente`: lo store e Stripe affiancati, l'utente sceglie (Google «User Choice Billing»).
MODALITA_STRIPE = ("nascosto", "link_esterno", "entitlement_ue", "scelta_utente")


class ConfigAppMobile(Base, TimestampMixin):
    __tablename__ = "config_app_mobili"
    __table_args__ = (
        CheckConstraint("piattaforma in ('android', 'ios', 'codemagic')", name="ck_config_app_mobili_piattaforma"),
    )

    piattaforma: Mapped[str] = mapped_column(String(10), primary_key=True)
    #: I campi in chiaro (vedi `domain/app_mobili_repositories.py` per l'elenco di ogni piattaforma).
    parametri: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"),
    )
    #: Un JSON cifrato (Fernet) con le credenziali delle API dello store. Nullo: nessuna.
    segreti: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    #: Il promemoria del profilo pagamenti dello store: solo appunti, del conto solo le ultime 4 cifre.
    appunti_pagamenti: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"),
    )
    #: L'ultima «Verifica» e il suo esito (`{"ok": …, "messaggio": …}`).
    verificato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    esito_verifica: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"),
    )
    #: L'ultima notifica ricevuta dallo store (Fase 4: RTDN di Google, Server Notifications V2 di Apple): quando, di che
    #: tipo, da quale ambiente e com'è andata. La console la mostra: è la prova che il collegamento funziona.
    ultima_notifica_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ultima_notifica: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"),
    )
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class ProdottoStore(Base, TimestampMixin):
    __tablename__ = "prodotti_store"
    __table_args__ = (
        UniqueConstraint("piattaforma", "product_id", name="uq_prodotti_store_piattaforma_prodotto"),
        CheckConstraint("piattaforma in ('android', 'ios')", name="ck_prodotti_store_piattaforma"),
        CheckConstraint("tipo in ('consumabile', 'abbonamento')", name="ck_prodotti_store_tipo"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    piattaforma: Mapped[str] = mapped_column(String(10), nullable=False)
    #: L'ID del prodotto come creato in Play Console o in App Store Connect (`crediti_100`, `chat.tarots.app.mese`).
    product_id: Mapped[str] = mapped_column(String(150), nullable=False)
    #: Il piano del sito che il prodotto accredita. Un piano non si cancella mai (lo si ritira), quindi niente cascata.
    plan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("plans.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(12), nullable=False)
    #: Per un abbonamento (Fase 4): se il prodotto è l'annuale (altrimenti il mensile) e se è il prodotto «prova» (un
    #: annuale a metà prezzo con il periodo di prova gratuito dello store: Google offerta di prova sul base plan, Apple
    #: introductory offer). Un pacchetto li ha sempre spenti.
    annuale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    prova: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    #: Spento: resta nel registro (gli acquisti vecchi devono restare leggibili) ma l'app non lo propone.
    attivo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    note: Mapped[str] = mapped_column(String(500), nullable=False, default="", server_default="")
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))


class PoliticaStripe(Base, TimestampMixin):
    __tablename__ = "politica_stripe"
    __table_args__ = (
        UniqueConstraint("piattaforma", "paese", name="uq_politica_stripe_piattaforma_paese"),
        CheckConstraint("piattaforma in ('android', 'ios')", name="ck_politica_stripe_piattaforma"),
        CheckConstraint(
            "modalita in ('nascosto', 'link_esterno', 'entitlement_ue', 'scelta_utente')",
            name="ck_politica_stripe_modalita",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    piattaforma: Mapped[str] = mapped_column(String(10), nullable=False)
    #: ISO 3166-1 alpha-2 maiuscolo (`IT`, `US`) o `*`: tutti i paesi senza una riga propria.
    paese: Mapped[str] = mapped_column(String(2), nullable=False)
    modalita: Mapped[str] = mapped_column(String(20), nullable=False, default="nascosto", server_default="nascosto")
    #: Il testo che le regole dello store chiedono accanto al pulsante (o una nota per chi amministra).
    avviso: Mapped[str] = mapped_column(String(500), nullable=False, default="", server_default="")
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
