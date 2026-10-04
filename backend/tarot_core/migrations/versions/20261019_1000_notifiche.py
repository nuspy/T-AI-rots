"""Le notifiche push dell'app e del sito (v9, Fase 5).

Revision ID: d2f4b6c8e0a3
Revises: c1e3a5b7d9f2

- `users.fuso_orario`: il fuso IANA rilevato dal sito (`Intl`) e dall'app; decide il giorno locale della carta del
  giorno e l'ora delle notifiche. Vuoto per tutti: finché il sito non lo rileva vale `Europe/Rome`, come prima.
- `dispositivi_notifica`: token FCM delle app e sottoscrizioni Web Push del sito.
- `preferenze_notifica`: cosa e quando, per persona (senza riga valgono i predefiniti della console).
- `campagne_notifica`: i messaggi della console a un segmento di utenti.
- `invii_notifica`: il registro degli invii, con gli indici unici dell'idempotenza (automatiche: tipo + persona +
  giorno locale; campagne: campagna + persona).
- `config_notifiche`: service account di Firebase (cifrato), chiave pubblica VAPID, predefiniti e automatiche.

Nessun dato da convertire. Indietro: le tabelle e la colonna spariscono (i dispositivi andranno registrati di nuovo).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d2f4b6c8e0a3"
down_revision = "c1e3a5b7d9f2"
branch_labels = None
depends_on = None


def _momenti():
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def upgrade() -> None:
    op.add_column("users", sa.Column("fuso_orario", sa.String(64), nullable=True))

    op.create_table(
        "dispositivi_notifica",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("anon_id", sa.String(64)),
        sa.Column("canale", sa.String(10), nullable=False),
        sa.Column("piattaforma", sa.String(10), nullable=False),
        sa.Column("token", sa.Text()),
        sa.Column("endpoint", sa.Text()),
        sa.Column("p256dh", sa.String(200)),
        sa.Column("auth", sa.String(100)),
        sa.Column("impronta", sa.String(64), nullable=False),
        sa.Column("lingua", sa.String(10)),
        sa.Column("fuso_orario", sa.String(64)),
        sa.Column("versione_app", sa.String(40)),
        sa.Column("attivo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ultimo_visto", sa.DateTime(timezone=True)),
        sa.Column("errori", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ultimo_errore", sa.String(300)),
        sa.Column("disattivato_il", sa.DateTime(timezone=True)),
        *_momenti(),
        sa.UniqueConstraint("impronta", name="dispositivi_notifica_impronta_key"),
        sa.CheckConstraint("(user_id is not null) or (anon_id is not null)", name="ck_dispositivi_notifica_owner"),
        sa.CheckConstraint("canale in ('fcm', 'webpush')", name="ck_dispositivi_notifica_canale"),
        sa.CheckConstraint("piattaforma in ('android', 'ios', 'web')", name="ck_dispositivi_notifica_piattaforma"),
        sa.CheckConstraint(
            "(canale = 'fcm' and token is not null) or "
            "(canale = 'webpush' and endpoint is not null and p256dh is not null and auth is not null)",
            name="ck_dispositivi_notifica_recapito",
        ),
    )
    op.create_index("ix_dispositivi_notifica_anon_id", "dispositivi_notifica", ["anon_id"])
    op.create_index("ix_dispositivi_notifica_utente", "dispositivi_notifica", ["user_id", "attivo"])

    op.create_table(
        "preferenze_notifica",
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("carta_giorno", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ora_carta", sa.Time(), nullable=False, server_default=sa.text("'08:30'")),
        sa.Column("silenzio_dal", sa.Time(), server_default=sa.text("'22:00'")),
        sa.Column("silenzio_al", sa.Time(), server_default=sa.text("'08:00'")),
        sa.Column("promemoria", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("tetto_promozioni_settimana", sa.Integer(), nullable=False, server_default="2"),
        *_momenti(),
        sa.CheckConstraint("tetto_promozioni_settimana between 0 and 14", name="ck_preferenze_notifica_tetto"),
    )

    op.create_table(
        "campagne_notifica",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(12), nullable=False),
        sa.Column("testi", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("lingua_base", sa.String(5), nullable=False, server_default="it"),
        sa.Column("deep_link", sa.String(300), nullable=False, server_default="/"),
        sa.Column("immagine", sa.String(500)),
        sa.Column("filtro", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("canali", postgresql.JSONB(), nullable=False, server_default=sa.text("'[\"fcm\", \"webpush\"]'::jsonb")),
        sa.Column("programmata_il", sa.DateTime(timezone=True)),
        sa.Column("stato", sa.String(12), nullable=False, server_default="bozza"),
        sa.Column("rispetta_silenzio", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("destinatari", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inviati", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errori", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("saltati", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("aperti", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("iniziata_il", sa.DateTime(timezone=True)),
        sa.Column("finita_il", sa.DateTime(timezone=True)),
        sa.Column("creata_da", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        *_momenti(),
        sa.CheckConstraint("tipo in ('servizio', 'promozione')", name="ck_campagne_notifica_tipo"),
        sa.CheckConstraint(
            "stato in ('bozza', 'programmata', 'in_invio', 'inviata', 'annullata')", name="ck_campagne_notifica_stato",
        ),
        sa.CheckConstraint("deep_link like '/%'", name="ck_campagne_notifica_deep_link"),
    )
    op.create_index("ix_campagne_notifica_stato", "campagne_notifica", ["stato", "programmata_il"])

    op.create_table(
        "invii_notifica",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tipo", sa.String(24), nullable=False),
        sa.Column("campagna_id", sa.BigInteger(), sa.ForeignKey("campagne_notifica.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("dispositivo_id", sa.BigInteger(), sa.ForeignKey("dispositivi_notifica.id", ondelete="SET NULL")),
        sa.Column("giorno", sa.Date()),
        sa.Column("stato", sa.String(16), nullable=False),
        sa.Column("dispositivi", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consegnati", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errore", sa.String(300)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("aperto_il", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "tipo in ('carta_giorno', 'serie_in_pericolo', 'crediti_in_scadenza', 'benvenuto', 'rinnovo_fallito', "
            "'promemoria_prova', 'campagna', 'prova')",
            name="ck_invii_notifica_tipo",
        ),
        sa.CheckConstraint(
            "stato in ('inviato', 'errore', 'token_invalido', 'aperto')", name="ck_invii_notifica_stato",
        ),
    )
    op.create_index(
        "uq_invii_notifica_giorno", "invii_notifica", ["tipo", "user_id", "giorno"], unique=True,
        postgresql_where=sa.text("campagna_id is null and giorno is not null"),
    )
    op.create_index(
        "uq_invii_notifica_campagna", "invii_notifica", ["campagna_id", "user_id"], unique=True,
        postgresql_where=sa.text("tipo = 'campagna'"),
    )
    op.create_index("ix_invii_notifica_creato", "invii_notifica", ["created_at"])
    op.create_index("ix_invii_notifica_utente", "invii_notifica", ["user_id", "tipo", "created_at"])

    op.create_table(
        "config_notifiche",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("firebase_cifrato", sa.LargeBinary()),
        sa.Column("firebase_progetto", sa.String(120)),
        sa.Column("firebase_email", sa.String(320)),
        sa.Column("firebase_caricato_il", sa.DateTime(timezone=True)),
        sa.Column("firebase_prova_il", sa.DateTime(timezone=True)),
        sa.Column("firebase_esito", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("vapid_pubblica", sa.String(120)),
        sa.Column("vapid_creata_il", sa.DateTime(timezone=True)),
        sa.Column("vapid_contatto", sa.String(200), nullable=False, server_default="mailto:privacy@tarots.chat"),
        sa.Column("ora_carta", sa.Time(), nullable=False, server_default=sa.text("'08:30'")),
        sa.Column("silenzio_dal", sa.Time(), server_default=sa.text("'22:00'")),
        sa.Column("silenzio_al", sa.Time(), server_default=sa.text("'08:00'")),
        sa.Column("tetto_promozioni_settimana", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("limite_al_minuto", sa.Integer(), nullable=False, server_default="600"),
        sa.Column("automatiche", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        *_momenti(),
        sa.CheckConstraint("id = 1", name="ck_config_notifiche_singleton"),
        sa.CheckConstraint("tetto_promozioni_settimana between 0 and 14", name="ck_config_notifiche_tetto"),
        sa.CheckConstraint("limite_al_minuto between 10 and 100000", name="ck_config_notifiche_limite"),
    )


def downgrade() -> None:
    op.drop_table("config_notifiche")
    op.drop_index("ix_invii_notifica_utente", table_name="invii_notifica")
    op.drop_index("ix_invii_notifica_creato", table_name="invii_notifica")
    op.drop_index("uq_invii_notifica_campagna", table_name="invii_notifica")
    op.drop_index("uq_invii_notifica_giorno", table_name="invii_notifica")
    op.drop_table("invii_notifica")
    op.drop_index("ix_campagne_notifica_stato", table_name="campagne_notifica")
    op.drop_table("campagne_notifica")
    op.drop_table("preferenze_notifica")
    op.drop_index("ix_dispositivi_notifica_utente", table_name="dispositivi_notifica")
    op.drop_index("ix_dispositivi_notifica_anon_id", table_name="dispositivi_notifica")
    op.drop_table("dispositivi_notifica")
    op.drop_column("users", "fuso_orario")
