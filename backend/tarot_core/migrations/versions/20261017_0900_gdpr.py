"""GDPR, Fase 1: consensi granulari con lo storico, IP protetti, età minima, cancellazione dell'account.

Revision ID: a1c3e5f7b9d2
Revises: d3f6b8c0e2a5

- `consensi_storico` (nuova, append-only): ogni scelta con tipo, valore, versione del testo, origine (web, android,
  ios, sistema) e IP protetto. Nasce già piena: si ricostruisce dagli eventi `consenso.*` del registro, che ogni
  scelta ha sempre lasciato (con l'IP, qui già troncato).
- `user_consents`: `origine` e `ip_hash`; i tipi diventano quelli granulari (`statistiche`, `google_analytics`,
  `pubblicita`, `testi_statistiche`, `dati_particolari`, `marketing`), e restano ammessi `cookie` e
  `condivisione_dati_partner` per lo storico. **Conversione d'ufficio** (decisione dell'operatore): ogni scelta
  `cookie` diventa la stessa scelta su `statistiche` e su `google_analytics` (con la versione del testo di allora, così
  chi aveva accettato un'informativa che non nominava Google Analytics se lo vede richiedere), poi la riga `cookie`
  si toglie; nello storico la conversione resta come scelta di origine `sistema`. Le categorie nuove partono senza
  scelta (cioè spente).
- `audit_log.ip_hash` e `user_consents.ip_hash`: gli IP già salvati si **troncano** (IPv4 /24, IPv6 /48) e se ne tiene
  l'impronta HMAC con `TAROT_IP_HASH_SECRET` (`tarot/ip_protetto.py`). Un valore che non è un indirizzo si toglie.
- `users`: `eta_confermata_il`, `eta_confermata_anni` (l'età minima, `tarot/eta_minima.py`),
  `cancellazione_richiesta_il` (con indice) e `cancellazione_eseguita_il` (`tarot/cancellazione.py`).

Il downgrade toglie tutto e ricostruisce le righe `cookie` da `statistiche`; gli IP troncati restano troncati
(l'indirizzo intero non esiste più da nessuna parte: è il senso della migrazione).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a1c3e5f7b9d2"
down_revision = "d3f6b8c0e2a5"
branch_labels = None
depends_on = None

TIPI_CORRENTI = ("statistiche", "google_analytics", "pubblicita", "testi_statistiche", "dati_particolari", "marketing")
TIPI_STORICI = ("cookie", "condivisione_dati_partner")
TIPI_CONSENSO = TIPI_CORRENTI + TIPI_STORICI
TIPI_STORICO = TIPI_CONSENSO + ("eta_minima",)
TIPI_PRIMA = ("cookie", "condivisione_dati_partner", "pubblicita")
ORIGINI = ("web", "android", "ios", "sistema")


def _in(valori) -> str:
    return "(" + ", ".join(f"'{v}'" for v in valori) + ")"


def _proteggi_ip(conn, tabella: str) -> None:
    """Tronca gli IP di `tabella` e ne scrive l'impronta. Un indirizzo alla volta (fra quelli distinti), solo sulle
    righe non ancora trattate (`ip_hash` nullo): un IP troncato che coincide con un altro indirizzo ancora da trattare
    non si ricalcola."""
    from tarot_core.tarot.ip_protetto import proteggi, segreto_per_migrazione

    # L'ambiente se c'è; altrimenti uno casuale, che la migrazione della Fase 2c (a7c9e1b3d5f8) salva cifrato.
    segreto = segreto_per_migrazione()
    indirizzi = conn.execute(sa.text(f"SELECT DISTINCT ip FROM {tabella} WHERE ip IS NOT NULL")).scalars().all()
    for ip in indirizzi:
        troncato, impronta = proteggi(ip, segreto)
        conn.execute(
            sa.text(f"UPDATE {tabella} SET ip = :t, ip_hash = :h WHERE ip = :ip AND ip_hash IS NULL"),
            {"t": troncato, "h": impronta, "ip": ip},
        )


def upgrade() -> None:
    conn = op.get_bind()

    # ---- users ----
    op.add_column("users", sa.Column("eta_confermata_il", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("eta_confermata_anni", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("cancellazione_richiesta_il", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("cancellazione_eseguita_il", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_cancellazione_richiesta_il", "users", ["cancellazione_richiesta_il"])

    # ---- IP protetti ----
    op.add_column("audit_log", sa.Column("ip_hash", sa.String(64), nullable=True))
    op.add_column("user_consents", sa.Column("ip_hash", sa.String(64), nullable=True))
    op.add_column(
        "user_consents", sa.Column("origine", sa.String(10), nullable=False, server_default="web"),
    )
    op.create_check_constraint("ck_user_consents_origine", "user_consents", f"origine in {_in(ORIGINI)}")
    _proteggi_ip(conn, "audit_log")
    _proteggi_ip(conn, "user_consents")

    # ---- lo storico ----
    op.create_table(
        "consensi_storico",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("anon_id", sa.String(64), nullable=True),
        sa.Column("tipo", sa.String(40), nullable=False),
        sa.Column("valore", sa.String(20), nullable=False),
        sa.Column("versione_informativa", sa.String(20), nullable=False),
        sa.Column("origine", sa.String(10), nullable=False),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"tipo in {_in(TIPI_STORICO)}", name="ck_consensi_storico_tipo"),
        sa.CheckConstraint("valore in ('accettato', 'rifiutato', 'confermato')", name="ck_consensi_storico_valore"),
        sa.CheckConstraint(f"origine in {_in(ORIGINI)}", name="ck_consensi_storico_origine"),
    )
    op.create_index("ix_consensi_storico_user_id", "consensi_storico", ["user_id"])
    op.create_index("ix_consensi_storico_anon_id", "consensi_storico", ["anon_id"])
    op.create_index("ix_consensi_storico_creato", "consensi_storico", ["created_at"])

    # Lo storico dalle scelte già registrate: ogni scrittura di un consenso ha sempre lasciato un evento
    # `consenso.<tipo>` nel registro, con valore, versione, chi (`actor_id`) o il cookie anonimo (`target_id`), IP.
    conn.execute(sa.text(f"""
        INSERT INTO consensi_storico (user_id, anon_id, tipo, valore, versione_informativa, origine, ip, ip_hash, created_at)
        SELECT a.actor_id,
               CASE WHEN a.actor_id IS NULL THEN a.target_id END,
               substring(a.action from 10),
               a.after ->> 'valore',
               left(coalesce(a.after ->> 'versione_informativa', 'sconosciuta'), 20),
               'web', a.ip, a.ip_hash, a.created_at
        FROM audit_log a
        WHERE a.action LIKE 'consenso.%'
          AND substring(a.action from 10) IN {_in(TIPI_PRIMA)}
          AND a.after ->> 'valore' IN ('accettato', 'rifiutato')
          AND (a.actor_id IS NOT NULL OR a.target_id IS NOT NULL)
        ORDER BY a.created_at, a.id
    """))

    # ---- la conversione d'ufficio di `cookie` ----
    op.drop_constraint("ck_user_consents_tipo", "user_consents", type_="check")
    nuove = """
        FROM user_consents c CROSS JOIN (VALUES ('statistiche'), ('google_analytics')) AS t(tipo)
        WHERE c.tipo = 'cookie' AND NOT EXISTS (
            SELECT 1 FROM user_consents d
            WHERE d.tipo = t.tipo
              AND ((c.user_id IS NOT NULL AND d.user_id = c.user_id) OR (c.user_id IS NULL AND d.anon_id = c.anon_id))
        )
    """
    conn.execute(sa.text(f"""
        INSERT INTO consensi_storico (user_id, anon_id, tipo, valore, versione_informativa, origine, ip, ip_hash, created_at)
        SELECT c.user_id, CASE WHEN c.user_id IS NULL THEN c.anon_id END, t.tipo, c.valore, c.versione_informativa,
               'sistema', NULL, NULL, now()
        {nuove}
    """))
    conn.execute(sa.text(f"""
        INSERT INTO user_consents (id, user_id, anon_id, tipo, valore, versione_informativa, ip, ip_hash, origine,
                                   created_at, updated_at)
        SELECT gen_random_uuid(), c.user_id, c.anon_id, t.tipo, c.valore, c.versione_informativa, c.ip, c.ip_hash,
               c.origine, c.created_at, c.updated_at
        {nuove}
    """))
    conn.execute(sa.text("DELETE FROM user_consents WHERE tipo = 'cookie'"))
    op.create_check_constraint("ck_user_consents_tipo", "user_consents", f"tipo in {_in(TIPI_CONSENSO)}")


def downgrade() -> None:
    conn = op.get_bind()

    # `cookie` torna dalla scelta su `statistiche` (la più vicina al vecchio significato: l'identificativo del
    # browser); i tipi nuovi spariscono. Lo storico non ha un posto dove andare: si perde con la sua tabella.
    op.drop_constraint("ck_user_consents_tipo", "user_consents", type_="check")
    conn.execute(sa.text("""
        INSERT INTO user_consents (id, user_id, anon_id, tipo, valore, versione_informativa, ip, created_at, updated_at)
        SELECT gen_random_uuid(), s.user_id, s.anon_id, 'cookie', s.valore, s.versione_informativa, s.ip,
               s.created_at, s.updated_at
        FROM user_consents s
        WHERE s.tipo = 'statistiche' AND NOT EXISTS (
            SELECT 1 FROM user_consents d
            WHERE d.tipo = 'cookie'
              AND ((s.user_id IS NOT NULL AND d.user_id = s.user_id) OR (s.user_id IS NULL AND d.anon_id = s.anon_id))
        )
    """))
    conn.execute(sa.text(
        "DELETE FROM user_consents WHERE tipo IN "
        "('statistiche', 'google_analytics', 'testi_statistiche', 'dati_particolari', 'marketing')"
    ))
    op.create_check_constraint("ck_user_consents_tipo", "user_consents", f"tipo in {_in(TIPI_PRIMA)}")

    op.drop_index("ix_consensi_storico_creato", table_name="consensi_storico")
    op.drop_index("ix_consensi_storico_anon_id", table_name="consensi_storico")
    op.drop_index("ix_consensi_storico_user_id", table_name="consensi_storico")
    op.drop_table("consensi_storico")

    op.drop_constraint("ck_user_consents_origine", "user_consents", type_="check")
    op.drop_column("user_consents", "origine")
    op.drop_column("user_consents", "ip_hash")
    op.drop_column("audit_log", "ip_hash")

    op.drop_index("ix_users_cancellazione_richiesta_il", table_name="users")
    op.drop_column("users", "cancellazione_eseguita_il")
    op.drop_column("users", "cancellazione_richiesta_il")
    op.drop_column("users", "eta_confermata_anni")
    op.drop_column("users", "eta_confermata_il")
