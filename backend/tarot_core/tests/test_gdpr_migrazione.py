"""La migrazione del GDPR (Fase 1, `a1c3e5f7b9d2`) sui dati veri di prima: conversione d'ufficio di `cookie`, storico
ricostruito dal registro, IP troncati con l'impronta, e il ritorno indietro. Su un database a parte, creato e
distrutto qui (come `test_migrazione.py`, ma con un nome suo)."""
from __future__ import annotations

from pathlib import Path

import pytest

from tarot_core.tarot import ip_protetto

from .conftest import URL_TEST, richiede_database

pytestmark = richiede_database

BACKEND = Path(__file__).resolve().parents[2]
NOME = "tarot_migrazione_gdpr_p1"
PRIMA = "d3f6b8c0e2a5"
DOPO = "a1c3e5f7b9d2"


def _amministrazione() -> str:
    return URL_TEST.rsplit("/", 1)[0].replace("postgresql+psycopg://", "postgresql://") + "/postgres"


@pytest.fixture
def database_scratch(monkeypatch):
    import psycopg
    from psycopg import sql

    def ricrea(crea: bool) -> None:
        with psycopg.connect(_amministrazione(), autocommit=True) as c:
            c.execute("select pg_terminate_backend(pid) from pg_stat_activity where datname = %s", (NOME,))
            c.execute(sql.SQL("drop database if exists {}").format(sql.Identifier(NOME)))
            if crea:
                c.execute(sql.SQL("create database {}").format(sql.Identifier(NOME)))

    ricrea(True)
    url = URL_TEST.rsplit("/", 1)[0] + f"/{NOME}"
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_DATABASE_URL", url)
    monkeypatch.setenv("TAROT_IP_HASH_SECRET", "segreto-della-prova")
    get_settings.cache_clear()
    yield url
    get_settings.cache_clear()
    ricrea(False)


def _config():
    from alembic.config import Config

    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "tarot_core" / "migrations"))
    return cfg


def test_la_migrazione_converte_i_cookie_tronca_gli_ip_e_torna_indietro(database_scratch):
    from alembic import command
    from sqlalchemy import create_engine, text

    command.upgrade(_config(), PRIMA)
    motore = create_engine(database_scratch)
    try:
        with motore.begin() as c:
            uid = c.execute(text(
                "INSERT INTO users (keycloak_sub, locale) VALUES ('sub-1', 'it') RETURNING id"
            )).scalar_one()
            # Lo stato com'era: un utente che ha accettato i cookie (sull'informativa v1) e gli annunci, un anonimo
            # che ha rifiutato i cookie (v2); ognuno con il suo evento nel registro, con l'IP intero.
            c.execute(text("""
                INSERT INTO user_consents (id, user_id, anon_id, tipo, valore, versione_informativa, ip)
                VALUES (gen_random_uuid(), :uid, NULL, 'cookie', 'accettato', 'v1', '93.44.12.201'),
                       (gen_random_uuid(), :uid, NULL, 'pubblicita', 'rifiutato', 'pubblicita-v1', '93.44.12.201'),
                       (gen_random_uuid(), NULL, 'anon-1', 'cookie', 'rifiutato', 'v2', '2001:db8:abcd:12::9')
            """), {"uid": uid})
            c.execute(text("""
                INSERT INTO audit_log (actor_id, action, target_type, target_id, after, ip, created_at) VALUES
                (:uid, 'consenso.cookie', 'consenso', :suid, '{"valore": "rifiutato", "versione_informativa": "v1"}', '93.44.12.201', now() - interval '2 days'),
                (:uid, 'consenso.cookie', 'consenso', :suid, '{"valore": "accettato", "versione_informativa": "v1"}', '93.44.12.201', now() - interval '1 day'),
                (:uid, 'consenso.pubblicita', 'consenso', :suid, '{"valore": "rifiutato", "versione_informativa": "pubblicita-v1"}', '93.44.12.201', now()),
                (NULL, 'consenso.cookie', 'consenso', 'anon-1', '{"valore": "rifiutato", "versione_informativa": "v2"}', '2001:db8:abcd:12::9', now()),
                (:uid, 'profilo.altro', 'user', :suid, NULL, 'unknown', now())
            """), {"uid": uid, "suid": str(uid)})

        command.upgrade(_config(), DOPO)

        with motore.connect() as c:
            correnti = {
                (r.user_id, r.anon_id, r.tipo): r for r in c.execute(text("SELECT * FROM user_consents"))
            }
            # Niente più «cookie»: al suo posto statistiche e Google Analytics, con la scelta e la versione di allora.
            assert not any(t == "cookie" for _, _, t in correnti)
            assert correnti[(uid, None, "statistiche")].valore == "accettato"
            assert correnti[(uid, None, "google_analytics")].valore == "accettato"
            assert correnti[(uid, None, "google_analytics")].versione_informativa == "v1"   # GA da riconfermare
            assert correnti[(None, "anon-1", "statistiche")].valore == "rifiutato"
            assert correnti[(None, "anon-1", "google_analytics")].valore == "rifiutato"
            assert correnti[(uid, None, "pubblicita")].valore == "rifiutato"
            assert not any(t in ("dati_particolari", "marketing", "testi_statistiche") for _, _, t in correnti)
            # Gli IP: troncati, con l'impronta dell'intero calcolata col segreto.
            riga = correnti[(uid, None, "statistiche")]
            assert riga.ip == "93.44.12.0"
            assert riga.ip_hash == ip_protetto.impronta("93.44.12.201", "segreto-della-prova")
            assert correnti[(None, "anon-1", "statistiche")].ip == "2001:db8:abcd::"
            registro = c.execute(text("SELECT action, ip, ip_hash FROM audit_log ORDER BY id")).all()
            assert {r.ip for r in registro} == {"93.44.12.0", "2001:db8:abcd::", None}
            assert all(r.ip_hash for r in registro if r.ip)
            # Lo storico: gli eventi del registro, poi le conversioni d'ufficio con origine «sistema».
            storico = c.execute(text(
                "SELECT user_id, anon_id, tipo, valore, origine, ip FROM consensi_storico ORDER BY id"
            )).all()
            dal_registro = [(s.user_id, s.anon_id, s.tipo, s.valore) for s in storico if s.origine == "web"]
            assert dal_registro == [
                (uid, None, "cookie", "rifiutato"), (uid, None, "cookie", "accettato"),
                (uid, None, "pubblicita", "rifiutato"), (None, "anon-1", "cookie", "rifiutato"),
            ]
            conversioni = {(s.user_id, s.anon_id, s.tipo, s.valore) for s in storico if s.origine == "sistema"}
            assert conversioni == {
                (uid, None, "statistiche", "accettato"), (uid, None, "google_analytics", "accettato"),
                (None, "anon-1", "statistiche", "rifiutato"), (None, "anon-1", "google_analytics", "rifiutato"),
            }
            assert all(s.ip in (None, "93.44.12.0", "2001:db8:abcd::") for s in storico)

        command.downgrade(_config(), PRIMA)

        with motore.connect() as c:
            tornati = {(r.user_id, r.anon_id, r.tipo): r.valore for r in c.execute(text(
                "SELECT user_id, anon_id, tipo, valore FROM user_consents"
            ))}
            assert tornati == {
                (uid, None, "cookie"): "accettato", (uid, None, "pubblicita"): "rifiutato",
                (None, "anon-1", "cookie"): "rifiutato",
            }
            assert c.execute(text("SELECT to_regclass('consensi_storico')")).scalar() is None

        # E di nuovo avanti: la catena regge in entrambe le direzioni.
        command.upgrade(_config(), DOPO)
    finally:
        motore.dispose()
