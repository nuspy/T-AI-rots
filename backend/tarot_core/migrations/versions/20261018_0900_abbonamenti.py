"""Abbonamenti: rinnovo automatico, conguaglio, prova gratuita, tolleranza, condoni, email (v9, Fase 2b).

Revision ID: f6a8b0c2d4e7
Revises: e5f7a9b1c3d6

- `impostazioni_abbonamenti` (una riga): sconto del rinnovo automatico (20%), sconto della prova (50%), giorni della
  prova (14), di tolleranza (7) e del promemoria (2), condoni per periodo (2), banner della prova (acceso).
- `prove_gratuite`: una per utente, con l'impronta della carta (una prova per carta).
- `invii_email`: il registro delle email agli utenti, una per chiave (niente doppioni).
- `subscriptions`: lo stato `in_sospeso` (tolleranza dopo un pagamento fallito, letture comprese ancora attive);
  `annuale`, `prova`, `listino`, `importo_periodo` (base del conguaglio), `sconto_ricorrente`,
  `pagamento_fallito_il`, il downgrade programmato (`piano_successivo_id`, `annuale_successivo`,
  `programma_esterno`).
- `payment_checkouts`: `listino`, `rinnovo` e `sconto_rinnovo`, il conguaglio (`residuo`, `sostituisce_id`),
  `prova`, `esito`.
- `readings`: il consumo `condono` e il `limite` superato all'apertura.

Dati: `annuale` si ricava dalla durata del periodo (più di 60 giorni), `listino` dal piano; i piani abbonamento
smettono di dare crediti (`credits_per_period = 0`: decisione dell'operatore del 3/10 — l'abbonamento dà solo
letture comprese). I crediti di piano già accreditati restano con la loro scadenza.

Indietro: `in_sospeso` torna `sospeso`, le letture `condono` tornano `omaggio`; i crediti per periodo azzerati non
si ripristinano (non si sa più quanti erano: si rimettono dalla console).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f6a8b0c2d4e7"
down_revision = "e5f7a9b1c3d6"
branch_labels = None
depends_on = None

STATI_PRIMA = "'in_prova', 'attivo', 'sospeso', 'disdetto', 'scaduto'"
STATI_DOPO = "'in_prova', 'attivo', 'in_sospeso', 'sospeso', 'disdetto', 'scaduto'"
CONSUMI_PRIMA = "'credito', 'quota', 'omaggio', 'anonimo'"
CONSUMI_DOPO = CONSUMI_PRIMA + ", 'condono'"


def upgrade() -> None:
    op.create_table(
        "impostazioni_abbonamenti",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sconto_rinnovo", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("sconto_prova", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("giorni_prova", sa.Integer(), nullable=False, server_default="14"),
        sa.Column("giorni_tolleranza", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("giorni_promemoria_prova", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("condoni_per_periodo", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("banner_prova", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("updated_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="ck_impostazioni_abbonamenti_singleton"),
        sa.CheckConstraint("sconto_rinnovo between 0 and 90", name="ck_impostazioni_abbonamenti_sconto_rinnovo"),
        sa.CheckConstraint("sconto_prova between 0 and 90", name="ck_impostazioni_abbonamenti_sconto_prova"),
    )

    op.create_table(
        "prove_gratuite",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("subscription_id", sa.Uuid(), sa.ForeignKey("subscriptions.id", ondelete="SET NULL")),
        sa.Column("impronta_carta", sa.String(64)),
        sa.Column("provider", sa.String(20), nullable=False, server_default="interno"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_prove_gratuite_impronta", "prove_gratuite", ["impronta_carta"])

    op.create_table(
        "invii_email",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("chiave", sa.String(200), nullable=False, unique=True),
        sa.Column("lingua", sa.String(5), nullable=False, server_default="en"),
        sa.Column("esito", sa.String(20), nullable=False),
        sa.Column("dettaglio", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "esito in ('inviata', 'non_configurato', 'errore', 'senza_indirizzo')", name="ck_invii_email_esito",
        ),
    )
    op.create_index("ix_invii_email_utente", "invii_email", ["user_id", "created_at"])

    op.drop_constraint("ck_subscriptions_status", "subscriptions", type_="check")
    op.create_check_constraint("ck_subscriptions_status", "subscriptions", f"status in ({STATI_DOPO})")
    op.add_column("subscriptions", sa.Column("annuale", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("subscriptions", sa.Column("prova", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("subscriptions", sa.Column("listino", sa.Integer()))
    op.add_column("subscriptions", sa.Column("importo_periodo", sa.Integer()))
    op.add_column("subscriptions", sa.Column("sconto_ricorrente", sa.Integer(), server_default="0", nullable=False))
    op.add_column("subscriptions", sa.Column("pagamento_fallito_il", sa.DateTime(timezone=True)))
    op.add_column("subscriptions", sa.Column(
        "piano_successivo_id", sa.BigInteger(), sa.ForeignKey("plans.id", ondelete="RESTRICT"),
    ))
    op.add_column("subscriptions", sa.Column("annuale_successivo", sa.Boolean()))
    op.add_column("subscriptions", sa.Column("programma_esterno", sa.String(120)))
    op.execute("update subscriptions set annuale = (period_end - period_start) > interval '60 days'")
    op.execute(
        "update subscriptions s set listino = case when s.annuale then p.price_yearly else p.price_monthly end "
        "from plans p where p.id = s.plan_id"
    )

    op.add_column("payment_checkouts", sa.Column("listino", sa.Integer()))
    op.add_column("payment_checkouts", sa.Column("rinnovo", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.add_column("payment_checkouts", sa.Column("sconto_rinnovo", sa.Integer(), server_default="0", nullable=False))
    op.add_column("payment_checkouts", sa.Column("residuo", sa.Integer(), server_default="0", nullable=False))
    op.add_column("payment_checkouts", sa.Column(
        "sostituisce_id", sa.Uuid(), sa.ForeignKey("subscriptions.id", ondelete="SET NULL"),
    ))
    op.add_column("payment_checkouts", sa.Column("prova", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("payment_checkouts", sa.Column("esito", sa.String(40)))

    op.add_column("readings", sa.Column("limite", sa.String(30)))
    op.drop_constraint("ck_readings_consumo", "readings", type_="check")
    op.create_check_constraint("ck_readings_consumo", "readings", f"consumo in ({CONSUMI_DOPO})")

    # L'abbonamento dà solo letture comprese: i crediti si comprano a parte e non scadono.
    op.execute("update plans set credits_per_period = 0 where tipo = 'abbonamento'")


def downgrade() -> None:
    op.execute("update readings set consumo = 'omaggio' where consumo = 'condono'")
    op.drop_constraint("ck_readings_consumo", "readings", type_="check")
    op.create_check_constraint("ck_readings_consumo", "readings", f"consumo in ({CONSUMI_PRIMA})")
    op.drop_column("readings", "limite")

    for colonna in ("esito", "prova", "sostituisce_id", "residuo", "sconto_rinnovo", "rinnovo", "listino"):
        op.drop_column("payment_checkouts", colonna)

    for colonna in (
        "programma_esterno", "annuale_successivo", "piano_successivo_id", "pagamento_fallito_il", "sconto_ricorrente",
        "importo_periodo", "listino", "prova", "annuale",
    ):
        op.drop_column("subscriptions", colonna)
    op.execute("update subscriptions set status = 'sospeso' where status = 'in_sospeso'")
    op.drop_constraint("ck_subscriptions_status", "subscriptions", type_="check")
    op.create_check_constraint("ck_subscriptions_status", "subscriptions", f"status in ({STATI_PRIMA})")

    op.drop_index("ix_invii_email_utente", table_name="invii_email")
    op.drop_table("invii_email")
    op.drop_index("ix_prove_gratuite_impronta", table_name="prove_gratuite")
    op.drop_table("prove_gratuite")
    op.drop_table("impostazioni_abbonamenti")
