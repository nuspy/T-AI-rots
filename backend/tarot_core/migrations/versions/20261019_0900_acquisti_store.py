"""Gli acquisti degli store (v9, Fase 4): il token dell'account per gli store, gli acquisti verificati, i prodotti
annuali e «prova», l'ultima notifica degli store, gli acquisti di prova fuori dai ricavi.

Revision ID: c1e3a5b7d9f2
Revises: b8d0f2a4c6e9

Additiva:

- `users.app_account_token`: un UUID casuale per ogni utente, generato qui per tutti quelli che ci sono già e alla
  nascita di ogni nuovo account (default del database). L'app lo passa allo store a ogni acquisto e lo store lo
  rimanda firmato: lega l'acquisto all'account senza dare allo store né l'id né l'email.
- `acquisti_store`: una riga per transazione dello store, unica per (piattaforma, transazione), con stato, ambiente
  (sandbox o produzione), conferma allo store, abbonamento collegato e ciò che lo store ha detto.
- `credit_ledger.acquisto_id` diventa una chiave esterna verso `acquisti_store` (la colonna c'era dalla Fase 2).
- `prodotti_store.annuale` e `prodotti_store.prova`: l'intervallo di un abbonamento venduto nello store e il
  prodotto annuale «prova».
- `config_app_mobili.ultima_notifica(_il)`: l'ultima notifica ricevuta da ogni store, per la console.
- `payment_checkouts.sandbox`: gli acquisti di prova degli store non entrano nei ricavi.
- `config_titolare.hosting`: il predefinito diventa neutro rispetto alla lingua («Hivelocity, London, GB»: fornitore,
  città, codice ISO del paese, che il sito traduce); la riga che ha ancora quello italiano di prima si aggiorna.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "c1e3a5b7d9f2"
down_revision = "b8d0f2a4c6e9"
branch_labels = None
depends_on = None

#: I valori scritti qui e non importati dai modelli: una migrazione non deve cambiare se domani cambia il modello.
HOSTING_VECCHIO = "Hivelocity, data center di Londra (Regno Unito)"
HOSTING_NUOVO = "Hivelocity, London, GB"


def upgrade() -> None:
    # `gen_random_uuid()` è volatile: aggiunta come default, PostgreSQL la calcola per ogni riga esistente, quindi
    # ogni utente di oggi riceve il suo token diverso dagli altri.
    op.add_column("users", sa.Column(
        "app_account_token", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()"),
    ))
    op.create_unique_constraint("users_app_account_token_key", "users", ["app_account_token"])

    op.create_table(
        "acquisti_store",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("piattaforma", sa.String(10), nullable=False),
        sa.Column("product_id", sa.String(150), nullable=False),
        sa.Column("tipo", sa.String(12), nullable=False),
        sa.Column("plan_id", sa.BigInteger(), sa.ForeignKey("plans.id")),
        sa.Column("transazione", sa.String(200), nullable=False),
        sa.Column("transazione_originale", sa.String(200)),
        sa.Column("ordine", sa.String(200)),
        sa.Column("purchase_token", sa.Text()),
        sa.Column("stato", sa.String(12), nullable=False, server_default="in_attesa"),
        sa.Column("ambiente", sa.String(10), nullable=False, server_default="production"),
        sa.Column("confermato", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("subscription_id", sa.Uuid(), sa.ForeignKey("subscriptions.id", ondelete="SET NULL")),
        sa.Column("importo", sa.Integer()),
        sa.Column("valuta", sa.String(3)),
        sa.Column("paese", sa.String(2)),
        sa.Column("prova", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("acquistato_il", sa.DateTime(timezone=True)),
        sa.Column("scade_il", sa.DateTime(timezone=True)),
        sa.Column("revocato_il", sa.DateTime(timezone=True)),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("piattaforma", "transazione", name="uq_acquisti_store_transazione"),
        sa.CheckConstraint("piattaforma in ('android', 'ios')", name="ck_acquisti_store_piattaforma"),
        sa.CheckConstraint(
            "stato in ('in_attesa', 'accreditato', 'rimborsato', 'revocato', 'scaduto')", name="ck_acquisti_store_stato",
        ),
        sa.CheckConstraint("ambiente in ('sandbox', 'production')", name="ck_acquisti_store_ambiente"),
        sa.CheckConstraint("tipo in ('consumabile', 'abbonamento')", name="ck_acquisti_store_tipo"),
    )
    op.create_index("ix_acquisti_store_utente", "acquisti_store", ["user_id", "created_at"])
    op.create_index("ix_acquisti_store_originale", "acquisti_store", ["piattaforma", "transazione_originale"])
    op.create_index(
        "ix_acquisti_store_in_attesa", "acquisti_store", ["stato"],
        postgresql_where=sa.text("stato = 'in_attesa' or not confermato"),
    )

    op.create_foreign_key(
        "credit_ledger_acquisto_id_fkey", "credit_ledger", "acquisti_store", ["acquisto_id"], ["id"],
        ondelete="SET NULL",
    )

    op.add_column("prodotti_store", sa.Column("annuale", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("prodotti_store", sa.Column("prova", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.add_column("config_app_mobili", sa.Column("ultima_notifica_il", sa.DateTime(timezone=True)))
    op.add_column("config_app_mobili", sa.Column(
        "ultima_notifica", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb"),
    ))

    op.add_column("payment_checkouts", sa.Column("sandbox", sa.Boolean(), nullable=False, server_default=sa.false()))

    # Il fornitore dell'hosting dell'informativa, neutro rispetto alla lingua: il sito traduce il paese (ISO) in
    # quella della pagina. Solo dove è ancora il predefinito di prima, scritto in italiano.
    op.alter_column("config_titolare", "hosting", server_default=HOSTING_NUOVO)
    op.execute(sa.text("update config_titolare set hosting = :nuovo where hosting = :vecchio")
               .bindparams(nuovo=HOSTING_NUOVO, vecchio=HOSTING_VECCHIO))


def downgrade() -> None:
    op.execute(sa.text("update config_titolare set hosting = :vecchio where hosting = :nuovo")
               .bindparams(nuovo=HOSTING_NUOVO, vecchio=HOSTING_VECCHIO))
    op.alter_column("config_titolare", "hosting", server_default=HOSTING_VECCHIO)
    op.drop_column("payment_checkouts", "sandbox")
    op.drop_column("config_app_mobili", "ultima_notifica")
    op.drop_column("config_app_mobili", "ultima_notifica_il")
    op.drop_column("prodotti_store", "prova")
    op.drop_column("prodotti_store", "annuale")
    op.drop_constraint("credit_ledger_acquisto_id_fkey", "credit_ledger", type_="foreignkey")
    op.drop_index("ix_acquisti_store_in_attesa", table_name="acquisti_store")
    op.drop_index("ix_acquisti_store_originale", table_name="acquisti_store")
    op.drop_index("ix_acquisti_store_utente", table_name="acquisti_store")
    op.drop_table("acquisti_store")
    op.drop_constraint("users_app_account_token_key", "users", type_="unique")
    op.drop_column("users", "app_account_token")
