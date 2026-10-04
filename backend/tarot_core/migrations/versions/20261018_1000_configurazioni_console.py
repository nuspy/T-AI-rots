"""Tutte le configurazioni dalla console (v9, Fase 2c).

Revision ID: a7c9e1b3d5f8
Revises: f6a8b0c2d4e7

- `config_stripe` (una riga): fornitore di pagamento scelto in console, modalità, chiave segreta e segreto del
  webhook cifrati, chiave pubblicabile, endpoint del webhook registrato da qui, ultima prova della chiave.
- `config_smtp` (una riga): la posta in uscita (password cifrata), il selettore DKIM per la sonda DNS, ultima prova.
- `config_titolare` (una riga): i dati del titolare per l'informativa. Nasce con il titolare che l'informativa già
  nominava (Andrea Taini), l'email privacy e l'hosting predefiniti.
- `segreti_sistema`: i segreti interni generati al primo avvio (impronta degli IP, sale delle condivisioni). Se la
  migrazione GDPR di questo stesso giro ha dovuto generare il segreto degli IP (ambiente senza
  `TAROT_IP_HASH_SECRET`), lo si salva qui, cifrato: le impronte degli IP già salvati restano confrontabili.
- `importazioni_ambiente`: il registro delle copie una tantum dall'ambiente al database.
- `impostazioni_backup`: la credenziale del NAS dalla console (chiave SSH o password, cifrate), tipo e impronta.

Indietro: le tabelle e le colonne nuove si tolgono (le configurazioni tornano a venire dall'ambiente).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "a7c9e1b3d5f8"
down_revision = "f6a8b0c2d4e7"
branch_labels = None
depends_on = None

EMAIL_PRIVACY = "privacy@tarots.chat"
HOSTING = "Hivelocity, data center di Londra (Regno Unito)"


def _tempi():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def _utente():
    return sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"))


def upgrade() -> None:
    op.create_table(
        "config_stripe",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(12)),
        sa.Column("modalita", sa.String(4)),
        sa.Column("chiave_segreta_cifrata", sa.LargeBinary()),
        sa.Column("chiave_pubblicabile", sa.String(200)),
        sa.Column("segreto_webhook_cifrato", sa.LargeBinary()),
        sa.Column("webhook_id", sa.String(80)),
        sa.Column("webhook_url", sa.String(300)),
        sa.Column("webhook_registrato_il", sa.DateTime(timezone=True)),
        sa.Column("ultima_prova_il", sa.DateTime(timezone=True)),
        sa.Column("esito_prova", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        _utente(),
        *_tempi(),
        sa.CheckConstraint("id = 1", name="ck_config_stripe_singleton"),
        sa.CheckConstraint(
            "provider is null or provider in ('disattivato', 'mock', 'stripe')", name="ck_config_stripe_provider",
        ),
        sa.CheckConstraint("modalita is null or modalita in ('test', 'live')", name="ck_config_stripe_modalita"),
    )

    op.create_table(
        "config_smtp",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("host", sa.String(255), nullable=False, server_default=""),
        sa.Column("porta", sa.Integer(), nullable=False, server_default="465"),
        sa.Column("sicurezza", sa.String(8), nullable=False, server_default="ssl"),
        sa.Column("utente", sa.String(320), nullable=False, server_default=""),
        sa.Column("password_cifrata", sa.LargeBinary()),
        sa.Column("mittente", sa.String(320), nullable=False, server_default=""),
        sa.Column("nome_mittente", sa.String(120), nullable=False, server_default="TAROTS chat"),
        sa.Column("dkim_selettore", sa.String(63), nullable=False, server_default=""),
        sa.Column("ultima_prova_il", sa.DateTime(timezone=True)),
        sa.Column("esito_prova", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        _utente(),
        *_tempi(),
        sa.CheckConstraint("id = 1", name="ck_config_smtp_singleton"),
        sa.CheckConstraint("porta between 1 and 65535", name="ck_config_smtp_porta"),
        sa.CheckConstraint("sicurezza in ('ssl', 'starttls')", name="ck_config_smtp_sicurezza"),
    )

    op.create_table(
        "config_titolare",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(200), nullable=False, server_default=""),
        sa.Column("indirizzo", sa.String(400), nullable=False, server_default=""),
        sa.Column("codice_fiscale", sa.String(40), nullable=False, server_default=""),
        sa.Column("email_privacy", sa.String(320), nullable=False, server_default=EMAIL_PRIVACY),
        sa.Column("dpo_nominato", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("dpo_contatto", sa.String(400), nullable=False, server_default=""),
        sa.Column("hosting", sa.String(300), nullable=False, server_default=HOSTING),
        _utente(),
        *_tempi(),
        sa.CheckConstraint("id = 1", name="ck_config_titolare_singleton"),
    )
    # Il titolare che l'informativa nominava già: la pagina non perde il nome nel passaggio alla console.
    op.execute(sa.text("INSERT INTO config_titolare (id, nome) VALUES (1, 'Andrea Taini')"))

    op.create_table(
        "segreti_sistema",
        sa.Column("nome", sa.String(40), primary_key=True),
        sa.Column("valore_cifrato", sa.LargeBinary(), nullable=False),
        sa.Column("origine", sa.String(10), nullable=False),
        *_tempi(),
        sa.CheckConstraint("origine in ('generato', 'ambiente')", name="ck_segreti_sistema_origine"),
    )
    _salva_segreto_della_migrazione_gdpr()

    op.create_table(
        "importazioni_ambiente",
        sa.Column("voce", sa.String(40), primary_key=True),
        sa.Column("esito", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.add_column("impostazioni_backup", sa.Column("chiave_ssh_cifrata", sa.LargeBinary()))
    op.add_column("impostazioni_backup", sa.Column("password_cifrata", sa.LargeBinary()))
    op.add_column("impostazioni_backup", sa.Column("chiave_ssh_tipo", sa.String(40)))
    op.add_column("impostazioni_backup", sa.Column("chiave_ssh_impronta", sa.String(120)))


def _salva_segreto_della_migrazione_gdpr() -> None:
    """Il segreto degli IP generato dalla migrazione GDPR in questo stesso processo (ambiente senza segreto), cifrato:
    senza, le impronte degli IP già salvati non si confronterebbero più con le nuove."""
    from tarot_core.llm.cifratura import cifra
    from tarot_core.tarot.ip_protetto import generato_in_migrazione

    segreto = generato_in_migrazione()
    if segreto:
        op.get_bind().execute(
            sa.text("INSERT INTO segreti_sistema (nome, valore_cifrato, origine) VALUES ('ip_hash', :v, 'generato') "
                    "ON CONFLICT (nome) DO NOTHING"),
            {"v": cifra(segreto)},
        )


def downgrade() -> None:
    op.drop_column("impostazioni_backup", "chiave_ssh_impronta")
    op.drop_column("impostazioni_backup", "chiave_ssh_tipo")
    op.drop_column("impostazioni_backup", "password_cifrata")
    op.drop_column("impostazioni_backup", "chiave_ssh_cifrata")
    op.drop_table("importazioni_ambiente")
    op.drop_table("segreti_sistema")
    op.drop_table("config_titolare")
    op.drop_table("config_smtp")
    op.drop_table("config_stripe")
