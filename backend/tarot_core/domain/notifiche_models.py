"""Le notifiche push dell'app e del sito (v9, Fase 5).

Richiesta dell'operatore: «ogni giorno la notifica per ricordare la carta del giorno e altri messaggi», un tab della
console per mandare messaggi e promozioni filtrati sulle caratteristiche degli utenti, e le notifiche anche sul sito.

- **`DispositivoNotifica`** (`dispositivi_notifica`): dove si può recapitare. Le app registrano il token di Firebase
  Cloud Messaging (`fcm`, Android e iOS: su iPhone FCM passa ad APNs con la chiave caricata in Firebase); il sito
  registra la sottoscrizione Web Push del browser (`webpush`: endpoint del servizio push e le due chiavi del
  browser). Un dispositivo che il servizio dichiara sparito (404/410, `UNREGISTERED`) si disattiva e non si usa più.
- **`PreferenzeNotifica`** (`preferenze_notifica`): cosa vuole ricevere la persona, e quando. Senza una riga valgono
  le impostazioni predefinite della console.
- **`CampagnaNotifica`** (`campagne_notifica`): un messaggio della console a un segmento di utenti. Le promozioni
  partono solo verso chi ha dato il consenso `marketing`.
- **`InvioNotifica`** (`invii_notifica`): il registro degli invii, una riga per persona e messaggio. Gli indici unici
  rendono idempotenti le automatiche (una per tipo, persona e **giorno locale**) e le campagne (una per persona): il
  CronJob ogni 15 minuti, due repliche, un giro ripetuto — nessuno manda due volte.
- **`ConfigNotifiche`** (`config_notifiche`): la console. Il service account di Firebase cifrato (come gli altri,
  `llm/cifratura.py`), la chiave pubblica VAPID (la privata, generata da sola, sta cifrata in `segreti_sistema`),
  le ore di silenzio e i tetti predefiniti, e le notifiche automatiche con i loro testi per lingua.

Il fuso orario della persona sta in `users.fuso_orario` (IANA, rilevato dal sito con `Intl` e dall'app): decide il
«giorno» della carta del giorno e l'ora in cui arrivano i promemoria.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, LargeBinary, String, Text,
    Time, Uuid, func, text, true,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

CANALI = ("fcm", "webpush")
PIATTAFORME = ("android", "ios", "web")
TIPI_CAMPAGNA = ("servizio", "promozione")
STATI_CAMPAGNA = ("bozza", "programmata", "in_invio", "inviata", "annullata")
STATI_INVIO = ("inviato", "errore", "token_invalido", "aperto")
#: Le notifiche automatiche (`notifiche/automatiche.py`), e i due tipi delle campagne: `campagna` (l'invio vero, uno
#: per persona) e `prova` («invia a me» dalla console: nessun vincolo di unicità).
TIPI_AUTOMATICI = (
    "carta_giorno", "serie_in_pericolo", "crediti_in_scadenza", "benvenuto", "rinnovo_fallito", "promemoria_prova",
)
TIPI_INVIO = TIPI_AUTOMATICI + ("campagna", "prova")

#: Le ore predefinite: la carta del giorno alle 8:30, silenzio dalle 22 alle 8 (ora locale di chi riceve).
ORA_CARTA_PREDEFINITA = time(8, 30)
SILENZIO_DAL_PREDEFINITO = time(22, 0)
SILENZIO_AL_PREDEFINITO = time(8, 0)
#: Quante promozioni al massimo in sette giorni, per persona (la persona può abbassarlo, non alzarlo).
TETTO_PROMOZIONI_PREDEFINITO = 2


def _in(valori: tuple) -> str:
    return "(" + ", ".join(f"'{v}'" for v in valori) + ")"


class DispositivoNotifica(Base, TimestampMixin):
    __tablename__ = "dispositivi_notifica"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: Di chi è. Oggi si registrano solo dispositivi di persone con un account (la carta del giorno e le promozioni
    #: hanno senso per chi ha un account); `anon_id` resta per l'app che registra il token prima dell'accesso, e il
    #: dispositivo passa all'account appena la persona entra.
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    anon_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    canale: Mapped[str] = mapped_column(String(10), nullable=False)
    piattaforma: Mapped[str] = mapped_column(String(10), nullable=False)
    #: FCM: il token di registrazione dell'app.
    token: Mapped[Optional[str]] = mapped_column(Text)
    #: Web Push: l'indirizzo del servizio push del browser e le due chiavi della sottoscrizione (pubbliche per
    #: definizione: servono a cifrare il messaggio per quel browser, non ad aprirlo).
    endpoint: Mapped[Optional[str]] = mapped_column(Text)
    p256dh: Mapped[Optional[str]] = mapped_column(String(200))
    auth: Mapped[Optional[str]] = mapped_column(String(100))
    #: SHA-256 del token o dell'endpoint: lo stesso dispositivo registrato due volte resta una riga.
    impronta: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    lingua: Mapped[Optional[str]] = mapped_column(String(10))
    fuso_orario: Mapped[Optional[str]] = mapped_column(String(64))
    versione_app: Mapped[Optional[str]] = mapped_column(String(40))
    attivo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    ultimo_visto: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: Errori di consegna di fila (si azzerano a una consegna riuscita), l'ultimo, e quando il dispositivo è stato
    #: disattivato (dal servizio push, dalla persona, o dopo troppi errori).
    errori: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    ultimo_errore: Mapped[Optional[str]] = mapped_column(String(300))
    disattivato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("(user_id is not null) or (anon_id is not null)", name="ck_dispositivi_notifica_owner"),
        CheckConstraint(f"canale in {_in(CANALI)}", name="ck_dispositivi_notifica_canale"),
        CheckConstraint(f"piattaforma in {_in(PIATTAFORME)}", name="ck_dispositivi_notifica_piattaforma"),
        CheckConstraint(
            "(canale = 'fcm' and token is not null) or "
            "(canale = 'webpush' and endpoint is not null and p256dh is not null and auth is not null)",
            name="ck_dispositivi_notifica_recapito",
        ),
        Index("ix_dispositivi_notifica_utente", "user_id", "attivo"),
    )


class PreferenzeNotifica(Base, TimestampMixin):
    __tablename__ = "preferenze_notifica"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    carta_giorno: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    #: L'ora locale del promemoria della carta del giorno.
    ora_carta: Mapped[time] = mapped_column(Time, nullable=False, default=ORA_CARTA_PREDEFINITA,
                                            server_default=text("'08:30'"))
    #: Le ore di silenzio (ora locale): niente notifiche fra `silenzio_dal` e `silenzio_al`, anche a cavallo della
    #: mezzanotte. Entrambe nulle: nessun silenzio.
    silenzio_dal: Mapped[Optional[time]] = mapped_column(Time, default=SILENZIO_DAL_PREDEFINITO,
                                                         server_default=text("'22:00'"))
    silenzio_al: Mapped[Optional[time]] = mapped_column(Time, default=SILENZIO_AL_PREDEFINITO,
                                                        server_default=text("'08:00'"))
    #: I promemoria di servizio: la serie in pericolo, il benvenuto, la prova che finisce, il pagamento non riuscito.
    promemoria: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    #: Al massimo quante promozioni in sette giorni (oltre al consenso `marketing`, che resta la condizione).
    tetto_promozioni_settimana: Mapped[int] = mapped_column(
        Integer, nullable=False, default=TETTO_PROMOZIONI_PREDEFINITO, server_default=str(TETTO_PROMOZIONI_PREDEFINITO),
    )

    __table_args__ = (
        CheckConstraint("tetto_promozioni_settimana between 0 and 14", name="ck_preferenze_notifica_tetto"),
    )


class CampagnaNotifica(Base, TimestampMixin):
    __tablename__ = "campagne_notifica"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #: Il nome interno, per riconoscerla in console. Non arriva a nessuno.
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(12), nullable=False)
    #: `{"it": {"titolo": …, "corpo": …}, "en": {…}}`: chi riceve legge la sua lingua, poi l'inglese, poi la base.
    testi: Mapped[Dict[str, Dict[str, str]]] = mapped_column(JSONB, nullable=False, default=dict,
                                                             server_default=text("'{}'::jsonb"))
    lingua_base: Mapped[str] = mapped_column(String(5), nullable=False, default="it", server_default="it")
    #: Dove porta il tocco: un percorso del sito (`/daily-card`), lo stesso nell'app (le rotte coincidono).
    deep_link: Mapped[str] = mapped_column(String(300), nullable=False, default="/", server_default="/")
    #: Un'immagine grande facoltativa (https): Android e il Web Push la mostrano, iOS solo con l'estensione dell'app.
    immagine: Mapped[Optional[str]] = mapped_column(String(500))
    #: Il segmento (`notifiche/segmenti.py`): lingua, paese, età, primo canale, attività, acquisti, piano, crediti…
    filtro: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"))
    canali: Mapped[List[str]] = mapped_column(JSONB, nullable=False, default=lambda: list(CANALI),
                                              server_default=text("'[\"fcm\", \"webpush\"]'::jsonb"))
    programmata_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    stato: Mapped[str] = mapped_column(String(12), nullable=False, default="bozza", server_default="bozza")
    #: Rimandare chi è nelle ore di silenzio al primo giro dopo la fine del silenzio.
    rispetta_silenzio: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    #: I contatori, aggiornati dall'invio: persone raggiunte, consegne riuscite, errori, saltate (tetto, nessun
    #: dispositivo), aperture.
    destinatari: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    inviati: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    errori: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    saltati: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    aperti: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    iniziata_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finita_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    creata_da: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))

    __table_args__ = (
        CheckConstraint(f"tipo in {_in(TIPI_CAMPAGNA)}", name="ck_campagne_notifica_tipo"),
        CheckConstraint(f"stato in {_in(STATI_CAMPAGNA)}", name="ck_campagne_notifica_stato"),
        CheckConstraint("deep_link like '/%'", name="ck_campagne_notifica_deep_link"),
        Index("ix_campagne_notifica_stato", "stato", "programmata_il"),
    )


class InvioNotifica(Base):
    __tablename__ = "invii_notifica"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tipo: Mapped[str] = mapped_column(String(24), nullable=False)
    campagna_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("campagne_notifica.id", ondelete="CASCADE"))
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    #: Il dispositivo che ha ricevuto (il primo, se sono più d'uno); `SET NULL` se poi la persona lo toglie.
    dispositivo_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("dispositivi_notifica.id", ondelete="SET NULL"),
    )
    #: Il giorno **locale** di chi riceve: con il tipo e la persona, la chiave dell'idempotenza delle automatiche.
    giorno: Mapped[Optional[date]] = mapped_column(Date)
    stato: Mapped[str] = mapped_column(String(16), nullable=False)
    #: Su quanti dispositivi si è provato, e su quanti è arrivato.
    dispositivi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    consegnati: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    errore: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    aperto_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(f"tipo in {_in(TIPI_INVIO)}", name="ck_invii_notifica_tipo"),
        CheckConstraint(f"stato in {_in(STATI_INVIO)}", name="ck_invii_notifica_stato"),
        Index(
            "uq_invii_notifica_giorno", "tipo", "user_id", "giorno", unique=True,
            postgresql_where=text("campagna_id is null and giorno is not null"),
        ),
        Index(
            "uq_invii_notifica_campagna", "campagna_id", "user_id", unique=True,
            postgresql_where=text("tipo = 'campagna'"),
        ),
        Index("ix_invii_notifica_creato", "created_at"),
        Index("ix_invii_notifica_utente", "user_id", "tipo", "created_at"),
    )


class ConfigNotifiche(Base, TimestampMixin):
    __tablename__ = "config_notifiche"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_config_notifiche_singleton"),
        CheckConstraint("tetto_promozioni_settimana between 0 and 14", name="ck_config_notifiche_tetto"),
        CheckConstraint("limite_al_minuto between 10 and 100000", name="ck_config_notifiche_limite"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    #: Il JSON del service account di Firebase (progetto dell'app), cifrato. Serve a ottenere il token OAuth con cui
    #: si chiama FCM HTTP v1.
    firebase_cifrato: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    firebase_progetto: Mapped[Optional[str]] = mapped_column(String(120))
    firebase_email: Mapped[Optional[str]] = mapped_column(String(320))
    firebase_caricato_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: L'ultima «Prova»: quando, e l'esito (`{"ok": …, "messaggio": …}`).
    firebase_prova_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    firebase_esito: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict,
                                                           server_default=text("'{}'::jsonb"))
    #: La chiave pubblica VAPID (punto P-256 non compresso, base64url): la si dà ai browser. La privata è in
    #: `segreti_sistema` (`vapid_privata`), generata al primo bisogno.
    vapid_pubblica: Mapped[Optional[str]] = mapped_column(String(120))
    vapid_creata_il: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    #: Il contatto che i servizi push vedono nel token VAPID (`mailto:`), per avvisare in caso di abusi.
    vapid_contatto: Mapped[str] = mapped_column(String(200), nullable=False, default="mailto:privacy@tarots.chat",
                                                server_default="mailto:privacy@tarots.chat")
    #: I predefiniti per chi non ha mai toccato le sue preferenze.
    ora_carta: Mapped[time] = mapped_column(Time, nullable=False, default=ORA_CARTA_PREDEFINITA,
                                            server_default=text("'08:30'"))
    silenzio_dal: Mapped[Optional[time]] = mapped_column(Time, default=SILENZIO_DAL_PREDEFINITO,
                                                         server_default=text("'22:00'"))
    silenzio_al: Mapped[Optional[time]] = mapped_column(Time, default=SILENZIO_AL_PREDEFINITO,
                                                        server_default=text("'08:00'"))
    tetto_promozioni_settimana: Mapped[int] = mapped_column(
        Integer, nullable=False, default=TETTO_PROMOZIONI_PREDEFINITO, server_default=str(TETTO_PROMOZIONI_PREDEFINITO),
    )
    #: Quante notifiche al minuto al massimo (tutte le persone insieme): FCM e i servizi Web Push non amano le
    #: raffiche, e un giro lento non fa danni.
    limite_al_minuto: Mapped[int] = mapped_column(Integer, nullable=False, default=600, server_default="600")
    #: Le automatiche: `{tipo: {"attiva": bool, "ora": "HH:MM" | null, "testi": {lingua: {titolo, corpo}}}}`. Un tipo
    #: che manca vale come i predefiniti di `notifiche/automatiche.py`.
    automatiche: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict,
                                                        server_default=text("'{}'::jsonb"))
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
