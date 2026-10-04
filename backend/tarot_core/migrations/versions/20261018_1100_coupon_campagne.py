"""Coupon secondo le buone regole del marketing, e la lingua scelta dal menu (v9, Fase 2d).

Revision ID: b8d0f2a4c6e9
Revises: a7c9e1b3d5f8

- `coupon_lotti`: i lotti di codici monouso (prefisso, campagna, quantità).
- `coupons`: `durata` (`una_volta`, `periodi`, `sempre`) e `periodi`; `cumulabile` (di default no: vale lo sconto più
  alto fra coupon, rinnovo automatico e prova); `campagna`; `lotto_id`.
- `coupon_redemptions`: `importo` incassato, `subscription_id`, `rinnovo` (lo sconto di un rinnovo, che non è un uso
  del codice) con il suo `riferimento` (indice unico parziale: un rinnovo, una riga).
- `subscriptions`: `sconto_base` (rinnovo automatico o prova, senza coupon), `coupon_id`, `sconto_coupon`,
  `coupon_rinnovi_rimasti`.
- `payment_checkouts`: `sconto_ricorrente` (lo sconto con cui partono i rinnovi).
- `users`: `locale_scelta_il` (la lingua scelta dal sito: il claim del token non la riscrive più).

Dati: `importo` dei riscatti già registrati dal loro pagamento; `sconto_base` degli abbonamenti uguale a
`sconto_ricorrente` (prima non c'erano coupon sui rinnovi). I coupon già creati diventano non cumulabili e «solo il
primo pagamento», come vuole il default nuovo: prima si sommavano sempre, ed erano solo in locale.

Indietro: le colonne nuove e i lotti spariscono (i codici dei lotti restano come coupon semplici).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b8d0f2a4c6e9"
down_revision = "a7c9e1b3d5f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coupon_lotti",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("prefisso", sa.String(20), nullable=False),
        sa.Column("campagna", sa.String(80)),
        sa.Column("description", sa.Text()),
        sa.Column("quantita", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("quantita >= 1", name="ck_coupon_lotti_quantita"),
    )

    op.add_column("coupons", sa.Column("durata", sa.String(12), nullable=False, server_default="una_volta"))
    op.add_column("coupons", sa.Column("periodi", sa.Integer()))
    op.add_column("coupons", sa.Column("cumulabile", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("coupons", sa.Column("campagna", sa.String(80)))
    op.add_column("coupons", sa.Column(
        "lotto_id", sa.BigInteger(), sa.ForeignKey("coupon_lotti.id", ondelete="RESTRICT"),
    ))
    op.create_check_constraint("ck_coupons_durata", "coupons", "durata in ('una_volta', 'periodi', 'sempre')")
    op.create_check_constraint("ck_coupons_periodi", "coupons", "durata <> 'periodi' or periodi >= 2")
    op.create_index("ix_coupons_campagna", "coupons", ["campagna"])
    op.create_index("ix_coupons_lotto", "coupons", ["lotto_id"])

    op.add_column("coupon_redemptions", sa.Column("importo", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("coupon_redemptions", sa.Column(
        "subscription_id", sa.Uuid(), sa.ForeignKey("subscriptions.id", ondelete="SET NULL"),
    ))
    op.add_column("coupon_redemptions", sa.Column("rinnovo", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("coupon_redemptions", sa.Column("riferimento", sa.String(200)))
    op.create_index(
        "uq_coupon_redemptions_rinnovo", "coupon_redemptions", ["subscription_id", "riferimento"], unique=True,
        postgresql_where=sa.text("rinnovo"),
    )
    op.execute(
        "update coupon_redemptions r set importo = c.importo from payment_checkouts c "
        "where r.checkout_id = c.id and c.status = 'pagato'"
    )

    op.add_column("subscriptions", sa.Column("sconto_base", sa.Integer()))
    op.add_column("subscriptions", sa.Column(
        "coupon_id", sa.BigInteger(), sa.ForeignKey("coupons.id", ondelete="SET NULL"),
    ))
    op.add_column("subscriptions", sa.Column("sconto_coupon", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("subscriptions", sa.Column("coupon_rinnovi_rimasti", sa.Integer()))
    op.execute("update subscriptions set sconto_base = sconto_ricorrente")

    op.add_column("payment_checkouts", sa.Column("sconto_ricorrente", sa.Integer()))

    op.add_column("users", sa.Column("locale_scelta_il", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("users", "locale_scelta_il")
    op.drop_column("payment_checkouts", "sconto_ricorrente")
    op.drop_column("subscriptions", "coupon_rinnovi_rimasti")
    op.drop_column("subscriptions", "sconto_coupon")
    op.drop_column("subscriptions", "coupon_id")
    op.drop_column("subscriptions", "sconto_base")
    op.drop_index("uq_coupon_redemptions_rinnovo", table_name="coupon_redemptions")
    op.execute("delete from coupon_redemptions where rinnovo")
    op.drop_column("coupon_redemptions", "riferimento")
    op.drop_column("coupon_redemptions", "rinnovo")
    op.drop_column("coupon_redemptions", "subscription_id")
    op.drop_column("coupon_redemptions", "importo")
    op.drop_index("ix_coupons_lotto", table_name="coupons")
    op.drop_index("ix_coupons_campagna", table_name="coupons")
    op.drop_constraint("ck_coupons_periodi", "coupons", type_="check")
    op.drop_constraint("ck_coupons_durata", "coupons", type_="check")
    op.drop_column("coupons", "lotto_id")
    op.drop_column("coupons", "campagna")
    op.drop_column("coupons", "cumulabile")
    op.drop_column("coupons", "periodi")
    op.drop_column("coupons", "durata")
    op.drop_table("coupon_lotti")
