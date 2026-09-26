"""Le migrazioni Alembic: applicabili, reversibili e uguali ai modelli.

La suite dei test crea lo schema con `Base.metadata.create_all`, quindi **non
prova le migrazioni**: una colonna aggiunta ai modelli e dimenticata nella
migrazione passerebbe ogni test e romperebbe la produzione all'avvio. Questo
test la prova su un database a parte, creato e distrutto qui:

1. `alembic upgrade head` da zero;
2. `compare_metadata` fra il database migrato e i modelli deve essere vuoto;
3. `downgrade` di una revisione e `upgrade` di nuovo, senza errori.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import URL_TEST, richiede_database

pytestmark = richiede_database

BACKEND = Path(__file__).resolve().parents[2]
NOME = "tarot_migrazione_prova"


def _amministrazione() -> str:
    return URL_TEST.rsplit("/", 1)[0].replace("postgresql+psycopg://", "postgresql://") + "/postgres"


@pytest.fixture
def database_scratch(monkeypatch):
    import psycopg
    from psycopg import sql

    def ricrea(crea: bool) -> None:
        with psycopg.connect(_amministrazione(), autocommit=True) as c:
            c.execute(
                "select pg_terminate_backend(pid) from pg_stat_activity where datname = %s", (NOME,)
            )
            c.execute(sql.SQL("drop database if exists {}").format(sql.Identifier(NOME)))
            if crea:
                c.execute(sql.SQL("create database {}").format(sql.Identifier(NOME)))

    ricrea(True)
    url = URL_TEST.rsplit("/", 1)[0] + f"/{NOME}"
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_DATABASE_URL", url)
    get_settings.cache_clear()
    yield url
    get_settings.cache_clear()
    ricrea(False)


def _config():
    from alembic.config import Config

    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "tarot_core" / "migrations"))
    return cfg


def test_le_migrazioni_si_applicano_da_zero_e_coincidono_con_i_modelli(database_scratch):
    from alembic import command
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext
    from sqlalchemy import create_engine

    command.upgrade(_config(), "head")

    from tarot_core import domain  # noqa: F401  (registra tutte le tabelle)
    from tarot_core.domain.base import Base

    motore = create_engine(database_scratch)
    try:
        with motore.connect() as conn:
            contesto = MigrationContext.configure(conn, opts={"compare_type": True})
            differenze = compare_metadata(contesto, Base.metadata)
    finally:
        motore.dispose()
    assert differenze == [], f"le migrazioni non coincidono con i modelli: {differenze}"


def _colonne(motore, tabella):
    from sqlalchemy import inspect

    return {c["name"] for c in inspect(motore).get_columns(tabella)}


def test_ogni_migrazione_e_reversibile(database_scratch):
    """Giù una revisione alla volta fino allo schema iniziale, e di nuovo su."""
    from alembic import command
    from sqlalchemy import create_engine, inspect

    cfg = _config()
    command.upgrade(cfg, "head")
    motore = create_engine(database_scratch)
    try:
        speciali = {"gender", "gender_custom", "is_trans", "partner_ricordato"}
        assert speciali <= _colonne(motore, "users") and "persone" in _colonne(motore, "readings")
        assert {"share_rewards", "promemoria_2fa"} <= _colonne(motore, "users")
        assert {"share_text", "share_clicked_at", "share_verified_at"} <= _colonne(motore, "readings")
        tabelle = set(inspect(motore).get_table_names())
        assert {"share_events", "share_visits", "share_images", "share_signups"} <= tabelle

        # Prima il promemoria della 2FA...
        command.downgrade(cfg, "8c4f2a7d1e93")
        assert "promemoria_2fa" not in _colonne(motore, "users") and "share_rewards" in _colonne(motore, "users")

        # ...poi la condivisione...
        command.downgrade(cfg, "5b1e7c3a9d42")
        tabelle = set(inspect(motore).get_table_names())
        assert not ({"share_events", "share_visits", "share_images", "share_signups"} & tabelle)
        assert "share_rewards" not in _colonne(motore, "users")
        assert not ({"share_text", "share_clicked_at", "share_verified_at"} & _colonne(motore, "readings"))
        assert speciali <= _colonne(motore, "users")          # le letture speciali restano

        # ...poi le letture speciali.
        command.downgrade(cfg, "824583d91378")
        assert not (speciali & _colonne(motore, "users")) and "persone" not in _colonne(motore, "readings")

        command.upgrade(cfg, "head")
        assert "share_verified_at" in _colonne(motore, "readings")
    finally:
        motore.dispose()
