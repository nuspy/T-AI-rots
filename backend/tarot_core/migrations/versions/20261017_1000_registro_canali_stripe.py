"""Il registro dei crediti multicanale, per Stripe e gli store (v9, Fase 2).

Revision ID: b2d4f6a8c0e3
Revises: a1c3e5f7b9d2

Su `credit_ledger`:

- `canale` (web, android, ios, console, sistema) e `provider` (stripe, google_play, app_store, mock, interno): di
  quale incasso è figlia ogni riga;
- `riferimento_esterno`: l'identificativo dell'incasso presso il fornitore, con un indice **unico parziale** su
  (`provider`, `riferimento_esterno`, `reason`) dove c'è — lo stesso pagamento non accredita due volte, lo stesso
  rimborso non storna due volte;
- `acquisto_id`: l'acquisto in uno store (Fase 4), per ora senza chiave esterna;
- i motivi `storno` (rimborso o contestazione) e `storno_annullato` (contestazione vinta).

Su `subscriptions`, `provider`: chi rinnova l'abbonamento. Il CronJob `tarots-abbonamenti` rinnova solo quelli
interni (piani gratuiti, regalati, del simulatore); Stripe e gli store rinnovano con un evento. E `fattura_aperta`:
la fattura del fornitore rimasta da pagare dopo un rinnovo fallito, perché si torni a pagare quella e non un'altra.

Le righe esistenti ricevono valori deducibili dal motivo — nessun riferimento, perché prima non si registrava:
acquisti → web/mock (in produzione il fornitore era `disattivato`, che non ne produce: un acquisto può venire solo
dal simulatore), consumi e rimborsi → web/interno, rettifiche → console/interno, il resto → sistema/interno.
Gli abbonamenti con un id del simulatore (`mock_…`) diventano `mock`, gli altri `interno`.

Il ritorno indietro non perde il saldo: storni e storni annullati diventano rettifiche con la nota che lo dice.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b2d4f6a8c0e3"
down_revision = "a1c3e5f7b9d2"
branch_labels = None
depends_on = None

MOTIVI_PRIMA = (
    "'accredito_piano', 'acquisto', 'consumo', 'rimborso', 'rettifica', 'scadenza', 'omaggio'"
)
MOTIVI_DOPO = MOTIVI_PRIMA + ", 'storno', 'storno_annullato'"
CANALI = "'web', 'android', 'ios', 'console', 'sistema'"
FORNITORI = "'stripe', 'google_play', 'app_store', 'mock', 'interno'"


def upgrade() -> None:
    op.add_column("credit_ledger", sa.Column("canale", sa.String(20), server_default="sistema", nullable=False))
    op.add_column("credit_ledger", sa.Column("provider", sa.String(20), server_default="interno", nullable=False))
    op.add_column("credit_ledger", sa.Column("riferimento_esterno", sa.String(200), nullable=True))
    op.add_column("credit_ledger", sa.Column("acquisto_id", sa.BigInteger(), nullable=True))

    op.execute("update credit_ledger set canale = 'web', provider = 'mock' where reason = 'acquisto'")
    op.execute("update credit_ledger set canale = 'web' where reason in ('consumo', 'rimborso')")
    op.execute("update credit_ledger set canale = 'console' where reason = 'rettifica'")

    op.drop_constraint("ck_credit_reason", "credit_ledger", type_="check")
    op.create_check_constraint("ck_credit_reason", "credit_ledger", f"reason in ({MOTIVI_DOPO})")
    op.create_check_constraint("ck_credit_canale", "credit_ledger", f"canale in ({CANALI})")
    op.create_check_constraint("ck_credit_provider", "credit_ledger", f"provider in ({FORNITORI})")
    op.create_index(
        "uq_credit_ledger_riferimento", "credit_ledger", ["provider", "riferimento_esterno", "reason"],
        unique=True, postgresql_where=sa.text("riferimento_esterno is not null"),
    )

    op.add_column("subscriptions", sa.Column("provider", sa.String(20), server_default="interno", nullable=False))
    op.execute("update subscriptions set provider = 'mock' where external_id like 'mock\\_%'")
    op.create_check_constraint("ck_subscriptions_provider", "subscriptions", f"provider in ({FORNITORI})")
    op.add_column("subscriptions", sa.Column("fattura_aperta", sa.String(120), nullable=True))


def downgrade() -> None:
    op.drop_column("subscriptions", "fattura_aperta")
    op.drop_constraint("ck_subscriptions_provider", "subscriptions", type_="check")
    op.drop_column("subscriptions", "provider")

    op.drop_index("uq_credit_ledger_riferimento", table_name="credit_ledger")
    op.drop_constraint("ck_credit_provider", "credit_ledger", type_="check")
    op.drop_constraint("ck_credit_canale", "credit_ledger", type_="check")
    op.drop_constraint("ck_credit_reason", "credit_ledger", type_="check")
    # Il saldo non deve cambiare tornando indietro: uno storno resta un movimento, con il nome che lo schema vecchio
    # conosce e la nota che dice cos'era.
    op.execute(
        "update credit_ledger set note = '[' || reason || '] ' || coalesce(note, ''), reason = 'rettifica' "
        "where reason in ('storno', 'storno_annullato')"
    )
    op.create_check_constraint("ck_credit_reason", "credit_ledger", f"reason in ({MOTIVI_PRIMA})")
    op.drop_column("credit_ledger", "acquisto_id")
    op.drop_column("credit_ledger", "riferimento_esterno")
    op.drop_column("credit_ledger", "provider")
    op.drop_column("credit_ledger", "canale")
