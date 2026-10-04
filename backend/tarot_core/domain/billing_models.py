"""Piani, abbonamenti, crediti.

**Il saldo è una somma, non un contatore.** `credit_ledger` è append-only: ogni
accredito e ogni consumo è una riga, e il saldo si ottiene sommandole. Un
contatore aggiornato in place sarebbe più veloce da leggere e perderebbe la
sola cosa che conta quando i conti non tornano — *perché* non tornano. Con il
registro, una sottrazione doppia si vede come due righe; con un contatore,
sparisce dentro un numero.

**I piani portano i loro limiti.** `limits` e `entitlements` sono JSONB e non
colonne perché cambiano più spesso dello schema: aggiungere «quante
personalità può creare» a un piano non deve costare una migrazione, o quel
campo finirà spremuto dentro uno esistente che significava altro.

**Un abbonamento non si cancella: si chiude.** `cancel_at` dice quando smette
di valere, e fino ad allora resta attivo — è ciò che distingue «ha disdetto»
da «non ha mai avuto un abbonamento», e serve sia al servizio sia alla
contabilità.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, Uuid, false, func, text, true,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

#: Gli stati di un abbonamento.
#:
#: `in_prova` è distinto da `attivo` perché i limiti possono differire e
#: perché la fine di una prova è un momento in cui succede qualcosa —
#: qualcuno paga o smette — mentre la fine di un periodo attivo è un rinnovo.
#:
#: `in_sospeso` (v9, Fase 2b) è la tolleranza dopo un pagamento fallito: il fornitore riprova, l'utente può saldare la
#: fattura aperta, e intanto le letture comprese restano attive. Finita la tolleranza diventa `sospeso`.
STATI_ABBONAMENTO = ("in_prova", "attivo", "in_sospeso", "sospeso", "disdetto", "scaduto")

#: Gli stati in cui l'abbonamento dà i suoi diritti.
STATI_VIVI = ("in_prova", "attivo", "in_sospeso")

#: Perché i crediti si muovono. Il motivo è obbligatorio: una riga senza
#: spiegazione rende il registro un elenco di numeri.
MOTIVI = (
    "accredito_piano",      # il rinnovo periodico compreso nell'abbonamento
    "acquisto",             # un pacchetto comprato a parte
    "consumo",              # una risposta generata
    "rimborso",             # una risposta fallita, restituita
    "rettifica",            # correzione manuale, con nota
    "scadenza",             # crediti non usati che decadono
    "omaggio",              # regalo: un invito riscattato, una promozione
    "storno",               # un pagamento tornato indietro: rimborso del fornitore o contestazione (chargeback)
    "storno_annullato",     # una contestazione vinta: lo storno si compensa
)

#: Da dove arriva il movimento (v9): il sito, le app, la console, o il sistema da sé (rinnovi, premi, iscrizione).
CANALI = ("web", "android", "ios", "console", "sistema")

#: Chi ha incassato, o `interno` quando non c'è denaro di mezzo (omaggi, consumi, rettifiche, piani gratuiti).
#: `mock` è il simulatore dello sviluppo. Vale anche per gli abbonamenti: dice chi li rinnova.
FORNITORI = ("stripe", "google_play", "app_store", "mock", "interno")

#: I fornitori che rinnovano da sé e lo dicono con un evento: il CronJob degli abbonamenti non li rinnova mai,
#: altrimenti un periodo pagato una volta verrebbe accreditato due volte.
FORNITORI_ESTERNI = ("stripe", "google_play", "app_store")


def _elenco_sql(valori: tuple) -> str:
    return ", ".join(f"'{v}'" for v in valori)

#: Cosa si vende. Un **abbonamento** dà letture al giorno per un periodo; un
#: **pacchetto** accredita crediti una volta sola, che non scadono.
TIPI_PIANO = ("abbonamento", "pacchetto")


class Plan(Base, TimestampMixin):
    """Un piano commerciale."""

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    #: Nome e descrizione nelle lingue del sito (v8.5, `billing/lingue.py`): lingua → testo. Vuoti: si mostra
    #: l'inglese, poi il nome originale.
    nomi: Mapped[Dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    descrizioni: Mapped[Dict[str, str]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    #: `abbonamento` o `pacchetto`. Stanno nella stessa tabella perché
    #: passano dallo stesso checkout e dalla stessa contabilità: un pacchetto
    #: è un piano che non si rinnova e accredita crediti invece di quota.
    tipo: Mapped[str] = mapped_column(String(20), default="abbonamento", nullable=False)

    #: In centesimi, e interi: i decimali in virgola mobile sul denaro
    #: producono differenze che nessuno sa spiegare a fine mese.
    price_monthly: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    price_yearly: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)

    #: Quanti crediti il piano accredita a ogni periodo; per un pacchetto,
    #: quanti ne accredita all'acquisto.
    credits_per_period: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False,
    )

    #: Quanto si può fare: letture al giorno. JSONB perché l'elenco cresce
    #: senza toccare lo schema.
    limits: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    #: Cosa si può fare, oltre al numero: le stese riservate, per esempio.
    entitlements: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    #: Ordine di presentazione e di confronto.
    rank: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    #: Un piano ritirato non si cancella: gli abbonamenti che lo citano
    #: devono restare leggibili, e la contabilità dell'anno scorso pure.
    #: `active` dice solo se si può ancora sottoscrivere.
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("tipo in ('abbonamento', 'pacchetto')", name="ck_plans_tipo"),
        Index("ix_plans_rank", "rank"),
    )

    @property
    def pacchetto(self) -> bool:
        return self.tipo == "pacchetto"


#: Come si sconta con un coupon. `crediti` non sconta nulla: è un codice regalo, che si riscatta (accredita crediti).
TIPI_COUPON = ("percentuale", "importo", "crediti")


class Coupon(Base, TimestampMixin):
    """Un codice che sconta un acquisto o regala crediti.

    Tre tipi: `percentuale` (`valore` è 1-100) e `importo` (`valore` sono centesimi) scontano un pagamento; `crediti`
    (`valore` sono crediti) è un codice regalo, che si riscatta dal profilo senza pagare. Su un abbonamento lo sconto
    vale sul primo pagamento, sui primi N o su tutti (`durata`, Fase 2d), e si somma o no agli altri sconti
    (`cumulabile`).

    Un coupon usato non si cancella (le righe di `coupon_redemptions` lo citano): si disattiva.
    """

    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: Maiuscolo, senza spazi: chi lo scrive non deve indovinare le maiuscole.
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(String(20), default="percentuale", nullable=False)
    valore: Mapped[int] = mapped_column(Integer, nullable=False)
    #: Gli slug dei piani a cui si applica; vuoto = tutti. Non vale per i codici regalo.
    piani: Mapped[Optional[Any]] = mapped_column(JSONB)
    solo_primo_acquisto: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    valido_dal: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    valido_fino: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: Quante volte in tutto (vuoto = senza tetto) e quante per utente.
    max_riscatti: Mapped[Optional[int]] = mapped_column(Integer)
    max_per_utente: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"), nullable=False)
    riscatti: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    attivo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)

    # -- v9, Fase 2d: durata, cumulo, campagna, lotti ------------------------------------------------------------

    #: Su un abbonamento, quanti pagamenti sconta (`DURATE_COUPON`): `una_volta` il primo, `periodi` i primi
    #: `periodi` (il primo compreso: «−30% per 3 mesi»), `sempre` tutti. Un pacchetto si paga una volta sola.
    durata: Mapped[str] = mapped_column(String(12), default="una_volta", server_default="una_volta", nullable=False)
    periodi: Mapped[Optional[int]] = mapped_column(Integer)
    #: Si somma allo sconto del rinnovo automatico o della prova (`True`), o vale il più alto dei due (`False`).
    cumulabile: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    #: L'etichetta di campagna, testo libero («newsletter-ottobre»): il resoconto raggruppa per questa.
    campagna: Mapped[Optional[str]] = mapped_column(String(80))
    #: Il lotto di codici monouso da cui viene, se ne viene da uno (`coupon_lotti`).
    lotto_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coupon_lotti.id", ondelete="RESTRICT"))

    __table_args__ = (
        CheckConstraint("tipo in ('percentuale', 'importo', 'crediti')", name="ck_coupons_tipo"),
        CheckConstraint("valore > 0", name="ck_coupons_valore"),
        CheckConstraint("tipo <> 'percentuale' or valore <= 100", name="ck_coupons_percentuale"),
        CheckConstraint("max_per_utente >= 1", name="ck_coupons_per_utente"),
        CheckConstraint("durata in ('una_volta', 'periodi', 'sempre')", name="ck_coupons_durata"),
        CheckConstraint("durata <> 'periodi' or periodi >= 2", name="ck_coupons_periodi"),
        Index("ix_coupons_campagna", "campagna"),
        Index("ix_coupons_lotto", "lotto_id"),
    )


#: Quanti pagamenti di un abbonamento sconta un coupon.
DURATE_COUPON = ("una_volta", "periodi", "sempre")


class CouponLotto(Base):
    """Un lotto di codici monouso, generati insieme con un prefisso (`NEWS-K7Q2XM4B`): ogni codice è un `Coupon` con
    un uso solo, le stesse regole e la stessa campagna. Si esporta in CSV per mandarli uno per persona."""

    __tablename__ = "coupon_lotti"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    prefisso: Mapped[str] = mapped_column(String(20), nullable=False)
    campagna: Mapped[Optional[str]] = mapped_column(String(80))
    description: Mapped[Optional[str]] = mapped_column(Text)
    quantita: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (CheckConstraint("quantita >= 1", name="ck_coupon_lotti_quantita"),)


class CouponRedemption(Base):
    """Un uso di un coupon: chi, quando, per quanto. Append-only."""

    __tablename__ = "coupon_redemptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    #: L'acquisto scontato, se c'è (un codice regalo non ne ha).
    checkout_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("payment_checkouts.id", ondelete="SET NULL"))
    #: Centesimi scontati, o crediti regalati.
    sconto: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    crediti: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # -- v9, Fase 2d: il resoconto ------------------------------------------------------------------------------
    #: Quanto è stato incassato in quel pagamento (centesimi): l'incasso lordo del coupon.
    importo: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    #: L'abbonamento che il coupon sconta (anche nei rinnovi), se è un abbonamento.
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subscriptions.id", ondelete="SET NULL"))
    #: Uno sconto su un rinnovo (un coupon «per N periodi» o «per sempre»): non è un uso del codice — non conta nei
    #: riscatti né negli usi a persona —, ma entra nel resoconto. `riferimento` è l'incasso del rinnovo (idempotenza).
    rinnovo: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    riferimento: Mapped[Optional[str]] = mapped_column(String(200))

    __table_args__ = (
        Index("ix_coupon_redemptions_coupon", "coupon_id"),
        Index("ix_coupon_redemptions_utente", "user_id", "coupon_id"),
        Index(
            "uq_coupon_redemptions_rinnovo", "subscription_id", "riferimento", unique=True,
            postgresql_where=text("rinnovo"),
        ),
    )


class Subscription(Base, TimestampMixin):
    """L'abbonamento di un utente a un piano."""

    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    plan_id: Mapped[int] = mapped_column(
        # `RESTRICT`: un piano citato da un abbonamento non deve poter
        # sparire, o la contabilità perde il riferimento a cosa è stato
        # venduto.
        ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False,
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False)

    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    #: Quando smetterà di valere. Valorizzato alla disdetta: fino a quel
    #: momento l'abbonamento resta attivo, perché è già stato pagato.
    cancel_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    #: L'identificativo presso il fornitore di pagamento, quando ce n'è uno.
    #: Nullo in sviluppo, dove gli abbonamenti si creano a mano.
    external_id: Mapped[Optional[str]] = mapped_column(String(120))
    #: Chi lo rinnova (v9, `FORNITORI`): `interno` per i piani gratuiti e regalati, che rinnova il CronJob
    #: `tarots-abbonamenti`; `stripe` e gli store lo rinnovano con un evento, e il CronJob non li tocca.
    provider: Mapped[str] = mapped_column(String(20), default="interno", server_default="interno", nullable=False)
    #: La fattura del fornitore rimasta da pagare dopo un rinnovo fallito (Stripe `in_…`): chi deve saldare torna a
    #: pagare **quella** (la sua pagina ospitata), non apre un secondo checkout che addebiterebbe due volte. Si azzera
    #: quando un rinnovo va a buon fine.
    fattura_aperta: Mapped[Optional[str]] = mapped_column(String(120))

    # -- v9, Fase 2b: rinnovo automatico, conguaglio, prova, tolleranza -----------------------------------------

    #: L'intervallo: annuale o mensile. Prima si ricavava dalla durata del periodo, che durante una prova (14 giorni)
    #: non dice niente.
    annuale: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    #: Nato da una prova gratuita: alla conversione è un annuale con lo sconto della prova per sempre.
    prova: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    #: Il prezzo di listino di un periodo quando è stato sottoscritto (centesimi): il listino può cambiare dopo, e
    #: l'abbonato resta sul suo prezzo finché non cambia piano.
    listino: Mapped[Optional[int]] = mapped_column(Integer)
    #: Quanto è stato pagato davvero per il periodo in corso (centesimi): la base del conguaglio di un upgrade.
    importo_periodo: Mapped[Optional[int]] = mapped_column(Integer)
    #: Lo sconto di ogni rinnovo presso il fornitore (centesimi): quello del rinnovo automatico o della prova. Vale
    #: solo se il rinnovo automatico è acceso — spento, il fornitore non rinnova e non c'è niente da scontare.
    sconto_ricorrente: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    #: Quando il primo pagamento non riuscito di questo giro ha aperto la tolleranza (`in_sospeso`). Si azzera quando
    #: un rinnovo va a buon fine.
    pagamento_fallito_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: Un downgrade programmato: il piano e l'intervallo che partiranno alla fine del periodo pagato.
    piano_successivo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("plans.id", ondelete="RESTRICT"))
    annuale_successivo: Mapped[Optional[bool]] = mapped_column(Boolean)
    #: Il programma presso il fornitore che fa partire il downgrade (Stripe `sub_sched_…`).
    programma_esterno: Mapped[Optional[str]] = mapped_column(String(120))

    # -- v9, Fase 2d: il coupon che continua sui rinnovi ----------------------------------------------------------
    #: `sconto_ricorrente` qui sopra è lo sconto **effettivo** del prossimo rinnovo (quello che ha il fornitore);
    #: `sconto_base` è la sua parte del rinnovo automatico o della prova, senza coupon. Vuoto nelle righe di prima:
    #: allora è `sconto_ricorrente`.
    sconto_base: Mapped[Optional[int]] = mapped_column(Integer)
    #: Il coupon «per N periodi» o «per sempre» e quanto sconta ogni rinnovo (centesimi, sul listino).
    coupon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coupons.id", ondelete="SET NULL"))
    sconto_coupon: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    #: Quanti rinnovi ha ancora lo sconto del coupon: vuoto (con un coupon) = per sempre, 0 = finito.
    coupon_rinnovi_rimasti: Mapped[Optional[int]] = mapped_column(Integer)

    plan: Mapped[Plan] = relationship(lazy="selectin", foreign_keys=[plan_id])
    piano_successivo: Mapped[Optional[Plan]] = relationship(lazy="selectin", foreign_keys=[piano_successivo_id])
    coupon: Mapped[Optional[Coupon]] = relationship(lazy="selectin", foreign_keys=[coupon_id])

    __table_args__ = (
        CheckConstraint(
            "status in ('in_prova', 'attivo', 'in_sospeso', 'sospeso', 'disdetto', 'scaduto')",
            name="ck_subscriptions_status",
        ),
        CheckConstraint(f"provider in ({_elenco_sql(FORNITORI)})", name="ck_subscriptions_provider"),
        CheckConstraint(
            "period_end > period_start", name="ck_subscriptions_periodo",
        ),
        # La query di ogni richiesta: «l'abbonamento attivo di questo utente».
        Index("ix_subscriptions_utente_stato", "user_id", "status"),
    )

    @property
    def vivo(self) -> bool:
        return self.status in STATI_VIVI

    @property
    def rinnovo_automatico(self) -> bool:
        """Il rinnovo automatico è acceso: nessuna disdetta segnata."""
        return self.cancel_at is None


class CreditEntry(Base):
    """Un movimento di crediti. Append-only.

    Non c'è un metodo per modificarla né per cancellarla, e non è una
    dimenticanza: un registro che si può correggere non è un registro. Uno
    sbaglio si ripara con una riga di `rettifica`, che lascia entrambe visibili.
    """

    __tablename__ = "credit_ledger"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )

    #: Positivo accredita, negativo consuma. Mai zero: una riga che non muove
    #: nulla è rumore in un registro che si legge a mano.
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(30), nullable=False)

    #: Cosa ha causato il movimento. Per un consumo è la lettura, e senza
    #: di essa «dove sono finiti i miei crediti?» non ha risposta. `SET NULL`
    #: perché la lettura si può cancellare, e il movimento deve restare.
    reading_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("readings.id", ondelete="SET NULL"),
    )
    note: Mapped[Optional[str]] = mapped_column(Text)

    #: Quando questi crediti smettono di valere. Per gli accrediti periodici
    #: (quelli comprati non scadono, perché sono stati pagati) e per i consumi
    #: che li hanno usati: un consumo pagato con crediti di piano scade con
    #: loro, così alla scadenza escono dalla somma entrambi e il saldo resta
    #: giusto senza scrivere righe di `scadenza` (`billing/credits.py`).
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    #: Da dove arriva (`CANALI`) e chi ha incassato (`FORNITORI`), v9: un registro che riceve denaro da Stripe,
    #: Google Play e App Store deve poter dire, per ogni riga, di quale incasso è figlia.
    canale: Mapped[str] = mapped_column(String(20), default="sistema", server_default="sistema", nullable=False)
    provider: Mapped[str] = mapped_column(String(20), default="interno", server_default="interno", nullable=False)
    #: L'identificativo dell'incasso presso il fornitore (un PaymentIntent o una fattura Stripe, una transazione
    #: degli store, il checkout del simulatore). Unico per fornitore e motivo: lo stesso pagamento non accredita due
    #: volte e lo stesso rimborso non storna due volte, qualunque strada percorra l'evento.
    riferimento_esterno: Mapped[Optional[str]] = mapped_column(String(200))
    #: L'acquisto in uno store (`acquisti_store`, Fase 4): la transazione che ha portato questi crediti.
    acquisto_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("acquisti_store.id", ondelete="SET NULL"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )

    __table_args__ = (
        CheckConstraint("delta <> 0", name="ck_credit_delta_non_nullo"),
        CheckConstraint(f"reason in ({_elenco_sql(MOTIVI)})", name="ck_credit_reason"),
        CheckConstraint(f"canale in ({_elenco_sql(CANALI)})", name="ck_credit_canale"),
        CheckConstraint(f"provider in ({_elenco_sql(FORNITORI)})", name="ck_credit_provider"),
        # Il saldo è una somma su questo indice: senza, ogni risposta
        # costerebbe una scansione del registro di quell'utente.
        Index("ix_credit_ledger_utente", "user_id", "created_at"),
        # L'idempotenza dei movimenti che vengono da fuori: parziale, perché consumi e omaggi non hanno riferimento.
        Index(
            "uq_credit_ledger_riferimento", "provider", "riferimento_esterno", "reason", unique=True,
            postgresql_where=text("riferimento_esterno is not null"),
        ),
    )


class PaymentCheckout(Base, TimestampMixin):
    """Una sessione di pagamento: l'utente è andato a pagare un piano o un pacchetto.

    L'abbonamento **non** nasce qui: nasce quando il fornitore conferma il
    pagamento con un evento firmato. Attivarlo all'apertura del checkout
    significherebbe dare il piano a chiunque apra la pagina e poi la chiuda.
    """

    __tablename__ = "payment_checkouts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False,
    )
    annuale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    #: `aperto` finché l'utente non paga o rinuncia; poi `pagato`,
    #: `annullato` o `scaduto`. Uno stato finale non torna indietro.
    status: Mapped[str] = mapped_column(String(20), default="aperto", nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    #: La sessione presso il fornitore, e l'abbonamento che ne nasce.
    external_id: Mapped[Optional[str]] = mapped_column(String(120))
    subscription_external_id: Mapped[Optional[str]] = mapped_column(String(120))
    #: Quanto è stato chiesto, in centesimi, fissato all'apertura: se il
    #: prezzo del piano cambia mentre l'utente paga, vale quello che ha visto.
    #: È l'importo **dopo** lo sconto del coupon, se c'è.
    importo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    #: Il coupon usato e quanto ha scontato (centesimi). Il listino è `importo + sconto`.
    coupon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coupons.id", ondelete="SET NULL"))
    sconto: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # -- v9, Fase 2b ------------------------------------------------------------------------------------------
    #: Il prezzo di listino del periodo (centesimi). Vuoto nei checkout di prima: il listino era `importo + sconto`.
    listino: Mapped[Optional[int]] = mapped_column(Integer)
    #: Il rinnovo automatico scelto: acceso, il prezzo ha lo sconto del rinnovo (`sconto_rinnovo`, centesimi) e lo
    #: avranno i rinnovi; spento, si paga il listino e il periodo non si rinnova.
    rinnovo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
    sconto_rinnovo: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    #: Il conguaglio di un upgrade (centesimi): il valore residuo dell'abbonamento che `sostituisce_id` chiude.
    residuo: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    sostituisce_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("subscriptions.id", ondelete="SET NULL"))
    #: Una prova gratuita: il metodo di pagamento si registra ora, si paga alla fine della prova (`sconto_rinnovo`
    #: è allora lo sconto della prova, per sempre).
    prova: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    #: Perché un checkout pagato non ha prodotto ciò che chiedeva (`prova_gia_usata`: la carta aveva già avuto una
    #: prova). La pagina di ritorno lo dice.
    esito: Mapped[Optional[str]] = mapped_column(String(40))
    #: Fase 2d: lo sconto con cui partono i rinnovi (centesimi): rinnovo automatico o prova, più o contro il coupon
    #: secondo il cumulo (`billing/offerte.py`). Vuoto: `sconto_rinnovo`, come prima.
    sconto_ricorrente: Mapped[Optional[int]] = mapped_column(Integer)
    #: Fase 4: un acquisto di prova degli store (tester, App Review di Apple). Accredita come gli altri, ma i ricavi
    #: non lo contano.
    sandbox: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)

    plan: Mapped[Plan] = relationship(lazy="selectin")

    __table_args__ = (
        CheckConstraint(
            "status in ('aperto', 'pagato', 'annullato', 'scaduto')",
            name="ck_payment_checkouts_status",
        ),
        Index("ix_payment_checkouts_utente", "user_id", "created_at"),
    )


class PaymentEvent(Base):
    """Un evento ricevuto dal fornitore di pagamento. Append-only.

    La chiave è l'identificativo dell'evento presso il fornitore: i fornitori
    rimandano lo stesso evento finché non ricevono un 200, e senza questa riga
    un pagamento confermato due volte accrediterebbe due periodi.
    """

    __tablename__ = "payment_events"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    tipo: Mapped[str] = mapped_column(String(60), nullable=False)
    payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
