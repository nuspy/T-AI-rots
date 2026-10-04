"""La migrazione dei livelli di ragionamento predefiniti (`c7e9a1b3d5f8`) sui dati di prima: i compiti assegnati
cambiano livello e non fornitore, quelli senza assegnazione la ricevono sul fornitore predefinito, e il downgrade
rimette tutto com'era. Su un database a parte, creato e distrutto qui (come `test_migrazione.py`)."""
from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import URL_TEST, richiede_database

pytestmark = richiede_database

BACKEND = Path(__file__).resolve().parents[2]
NOME = "tarot_migrazione_livelli"
PRIMA = "b6d8f0a2c4e7"
DOPO = "c7e9a1b3d5f8"


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
    get_settings.cache_clear()
    yield url
    get_settings.cache_clear()
    ricrea(False)


def _config():
    from alembic.config import Config

    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "tarot_core" / "migrations"))
    return cfg


def _assegnazioni(c):
    from sqlalchemy import text

    return {
        r.task: (r.model_name, r.livello_ragionamento, r.ragiona_override)
        for r in c.execute(text("SELECT task, model_name, livello_ragionamento, ragiona_override FROM model_assignments"))
    }


def test_i_livelli_predefiniti_si_applicano_e_tornano_indietro(database_scratch):
    from alembic import command
    from sqlalchemy import create_engine, text

    command.upgrade(_config(), PRIMA)
    motore = create_engine(database_scratch)
    try:
        with motore.begin() as c:
            # Com'è in produzione: Nebius per i cinque compiti della lettura, senza ragionamento; un fornitore spento
            # che in ordine di nome verrebbe prima; l'oracolo e la memoria senza assegnazione.
            c.execute(text("""
                INSERT INTO llm_providers (nome, tipo, provider, base_url, model, embed_model, motore, ragiona,
                                           livello_ragionamento, parametri, senza_filtri, descrizione, attivo,
                                           created_at, updated_at)
                VALUES ('aaa-spento', 'nebius', 'openai-compatible', 'http://x', 'm', '', '', false, 'none', '{}',
                        false, '', false, now(), now()),
                       ('nebius-nemotron-lightning', 'nebius', 'openai-compatible', 'http://n', 'm', '', '', true,
                        'medium', '{}', false, '', true, now(), now()),
                       ('zzz-altro', 'deepinfra', 'openai-compatible', 'http://d', 'm', '', '', false, 'none', '{}',
                        false, '', true, now(), now())
            """))
            c.execute(text("""
                INSERT INTO model_assignments (task, model_name, ragiona_override, livello_ragionamento)
                VALUES ('intervista', 'nebius-nemotron-lightning', false, 'none'),
                       ('validazione', 'nebius-nemotron-lightning', false, 'none'),
                       ('interpretazione', 'nebius-nemotron-lightning', false, 'none'),
                       ('sintesi', 'zzz-altro', false, 'none'),
                       ('giudizio', 'nebius-nemotron-lightning', NULL, NULL),
                       ('analisi_dati', 'zzz-altro', true, 'high')
            """))
            prima = _assegnazioni(c)

        command.upgrade(_config(), DOPO)

        with motore.connect() as c:
            dopo = _assegnazioni(c)
            # I fornitori assegnati non cambiano; cambia solo il livello (con il booleano allineato).
            assert dopo["interpretazione"] == ("nebius-nemotron-lightning", "xhigh", True)
            assert dopo["sintesi"] == ("zzz-altro", "xhigh", True)
            assert dopo["intervista"] == ("nebius-nemotron-lightning", "none", False)
            assert dopo["validazione"] == ("nebius-nemotron-lightning", "none", False)
            assert dopo["giudizio"] == ("nebius-nemotron-lightning", "none", False)
            # Oracolo e memoria: creati sul predefinito (il primo attivo per nome, non quello spento).
            assert dopo["chat_proattiva"] == ("nebius-nemotron-lightning", "none", False)
            assert dopo["memoria_estrazione"] == ("nebius-nemotron-lightning", "none", False)
            # Un compito fuori dal piano non si tocca.
            assert dopo["analisi_dati"] == ("zzz-altro", "high", True)
            traccia = c.execute(text(
                "SELECT actor_id, before FROM audit_log WHERE action = 'modello.livelli_predefiniti'"
            )).one()
            assert traccia.actor_id is None and traccia.before["righe"]["chat_proattiva"] is None

        command.downgrade(_config(), PRIMA)

        with motore.connect() as c:
            assert _assegnazioni(c) == prima
            assert c.execute(text(
                "SELECT count(*) FROM audit_log WHERE action = 'modello.livelli_predefiniti.annulla'"
            )).scalar() == 1

        # E di nuovo avanti: la catena regge in entrambe le direzioni.
        command.upgrade(_config(), DOPO)
        with motore.connect() as c:
            assert _assegnazioni(c)["chat_proattiva"] == ("nebius-nemotron-lightning", "none", False)
    finally:
        motore.dispose()


def test_senza_fornitori_non_crea_nulla(database_scratch):
    from alembic import command
    from sqlalchemy import create_engine, text

    command.upgrade(_config(), DOPO)
    motore = create_engine(database_scratch)
    try:
        with motore.connect() as c:
            assert c.execute(text("SELECT count(*) FROM model_assignments")).scalar() == 0
            assert c.execute(text("SELECT count(*) FROM audit_log")).scalar() == 0
        command.downgrade(_config(), PRIMA)
    finally:
        motore.dispose()
