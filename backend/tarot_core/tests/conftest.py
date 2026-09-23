"""Attrezzatura comune ai test della piattaforma.

Viene da Personalities, con in più il client HTTP sull'app e il modello finto.

**Perché un PostgreSQL vero e non SQLite.** I modelli usano `JSONB` e i lock
`FOR UPDATE` del registro crediti: su SQLite non esistono, e riscriverli in tipi portabili
significherebbe provare uno schema diverso da quello che andrà in produzione —
cioè non provarlo. I test che toccano il database si saltano da soli se il
database non c'è, così la suite resta utilizzabile senza Docker; quelli che
contano davvero sull'isolamento, però, sono fra questi, e un `skipped` va letto
come «non verificato», non come «a posto».

Ogni test lavora in una transazione che viene annullata alla fine: le prove si
possono eseguire in qualunque ordine e nessuna vede i dati di un'altra.
"""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import sys
from typing import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tarot_core.auth.keycloak import Principal
from tarot_core.domain.base import Base
from tarot_core.domain.models import User

@pytest.fixture(autouse=True)
def niente_modelli_veri(monkeypatch):
    """Durante le prove i modelli stanno su una porta morta.

    Una prova che per sbaglio ricade sul fornitore vero altrimenti chiamerebbe
    un modello: passerebbe o fallirebbe secondo che sia raggiungibile. Con la
    porta 9 la chiamata fallisce subito e dice dove.
    """
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_LLM_BASE_URL", "http://127.0.0.1:9/v1")
    monkeypatch.setenv("TAROT_ANTHROPIC_BASE_URL", "http://127.0.0.1:9")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


#: Un database separato da quello di sviluppo: le prove creano e cancellano
#: righe senza riguardo, e farlo su dati veri è un incidente che capita una
#: volta sola.
URL_TEST = os.getenv(
    "TAROT_TEST_DATABASE_URL",
    "postgresql+psycopg://tarot:tarot@localhost:5433/tarot_test",
)


def _database_raggiungibile() -> bool:
    """Il database di test esiste ed è raggiungibile? Lo si crea se manca."""
    try:
        import psycopg
        from psycopg import sql
    except ImportError:  # pragma: no cover
        return False

    amministrazione = URL_TEST.rsplit("/", 1)[0].replace("postgresql+psycopg://", "postgresql://")
    nome = URL_TEST.rsplit("/", 1)[1]
    try:
        with psycopg.connect(f"{amministrazione}/postgres", connect_timeout=3, autocommit=True) as c:
            esiste = c.execute(
                "select 1 from pg_database where datname = %s", (nome,)
            ).fetchone()
            if not esiste:
                c.execute(sql.SQL("create database {}").format(sql.Identifier(nome)))

        return True
    except Exception:
        return False


DATABASE_DISPONIBILE = _database_raggiungibile()

richiede_database = pytest.mark.skipif(
    not DATABASE_DISPONIBILE,
    reason=(
        "PostgreSQL non raggiungibile: `docker compose up -d postgres`. "
        "I test del flusso di lettura e dei crediti NON sono stati eseguiti."
    ),
)


if sys.platform == "win32":

    def pytest_asyncio_loop_factories(config, item):
        """Su Windows il loop dev'essere quello a selettore.

        psycopg 3 non funziona in modalità asincrona sul `ProactorEventLoop`,
        che è il predefinito di Windows: senza questo, i test sul database
        fallirebbero tutti con `InterfaceError`. Altrove l'hook non si
        definisce affatto: le versioni recenti di pytest-asyncio rifiutano una
        mappa vuota.
        """
        return {"asyncio": asyncio.SelectorEventLoop}


@pytest_asyncio.fixture(scope="session")
async def engine():
    if not DATABASE_DISPONIBILE:
        pytest.skip("database non disponibile")

    motore = create_async_engine(URL_TEST, poolclass=None)
    async with motore.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield motore
    await motore.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    """Una fabbrica di sessioni su una transazione che verrà annullata.

    La transazione esterna non viene mai confermata: anche un `commit()` del
    codice sotto prova resta dentro di essa e sparisce al termine. È ciò che
    rende i test indipendenti dall'ordine senza ricreare lo schema ogni volta.

    Si espone la **fabbrica** e non solo una sessione perché il codice che
    continua a lavorare dopo la risposta — lo streaming — ne apre una propria:
    se quella finisse sul database vero invece che qui, il test smetterebbe di
    osservare ciò che voleva osservare, e passerebbe lo stesso.
    """
    async with engine.connect() as connessione:
        transazione = await connessione.begin()
        factory = async_sessionmaker(
            bind=connessione,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        yield factory
        await transazione.rollback()


@pytest_asyncio.fixture
async def session(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as sessione:
        yield sessione


@pytest.fixture
def principal_utente() -> Principal:
    return Principal(
        subject="sub-utente-1",
        email="utente@example.com",
        display_name="Utente Di Prova",
        roles={"user"},
    )


@pytest.fixture
def principal_altro() -> Principal:
    return Principal(
        subject="sub-utente-2",
        email="altro@example.com",
        display_name="Altro Utente",
        roles={"user"},
    )


@pytest.fixture
def principal_admin() -> Principal:
    return Principal(
        subject="sub-admin",
        email="admin@example.com",
        display_name="Amministratore",
        roles={"user", "admin"},
    )


@pytest_asyncio.fixture
async def utente(session, principal_utente) -> User:
    from tarot_core.domain.repositories import UserRepository

    return await UserRepository(session).ensure(principal_utente)


@pytest_asyncio.fixture
async def altro_utente(session, principal_altro) -> User:
    from tarot_core.domain.repositories import UserRepository

    return await UserRepository(session).ensure(principal_altro)

@contextlib.contextmanager
def avvisi_di(modulo, livello: int = logging.WARNING):
    """Raccoglie i messaggi che un modulo registra, senza passare da caplog.

    `caplog` attacca il suo gestore alla radice e dipende dalla propagazione e
    dai livelli globali: basta che un altro test — o un'istrumentazione —
    tocchi quella configurazione, e la cattura smette di funzionare *in certi
    ordini di esecuzione soltanto*. Un difetto così costa più tempo di quanto
    ne valga il test.

    Questo si attacca al logger del modulo e non dipende da nient'altro.
    """
    raccolti: list[str] = []

    class Raccoglitore(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            raccolti.append(record.getMessage())

    gestore = Raccoglitore(level=livello)
    logger = modulo.logger
    livello_prima = logger.level
    spento_prima = logger.disabled
    logger.addHandler(gestore)
    logger.setLevel(livello)
    # Un `fileConfig` altrui — quello di Alembic, per dirne uno — può aver
    # spento questo logger: un gestore attaccato a un logger disattivato non
    # riceve niente, e il test fallirebbe per un motivo che non è il suo.
    logger.disabled = False
    try:
        yield raccolti
    finally:
        logger.removeHandler(gestore)
        logger.setLevel(livello_prima)
        logger.disabled = spento_prima


# ---- il client HTTP sull'app ---------------------------------------------------


@pytest_asyncio.fixture
async def catalogo(session):
    """Il catalogo del seed: le letture si pagano, come in produzione."""
    from tarot_core.tools.seed import scrivi_catalogo

    await scrivi_catalogo(session)
    await session.commit()


class Identita:
    """Chi fa la richiesta. Si cambia a metà test per provare l'isolamento."""

    def __init__(self, principal: Principal) -> None:
        self.principal = principal


@pytest_asyncio.fixture
async def client(session_factory, principal_utente, monkeypatch):
    """Un client sull'app vera, con il database di test e il modello finto.

    L'autenticazione si sostituisce a livello di `current_principal`: tutto il
    resto — utenti creati al primo accesso, piano gratuito, crediti — passa dal
    codice di produzione.
    """
    import httpx

    from tarot_core.api import deps
    from tarot_core.api.app import create_app
    from tarot_core.auth.dependencies import current_principal
    from tarot_core.domain.session import get_db_session, get_session_factory
    from tarot_core.settings import get_settings

    monkeypatch.setenv("TAROT_LLM_FINTO", "true")
    monkeypatch.setenv("TAROT_TRACING_ENABLED", "false")
    get_settings.cache_clear()
    deps.reset_dependencies()

    identita = Identita(principal_utente)
    app = create_app()

    async def sessione():
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_db_session] = sessione
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    app.dependency_overrides[current_principal] = lambda: identita.principal

    trasporto = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=trasporto, base_url="http://test") as c:
        c.identita = identita
        yield c
    deps.reset_dependencies()


def eventi_sse(testo: str) -> list[tuple[str, dict]]:
    """Da un corpo SSE all'elenco di (evento, dati)."""
    import json

    eventi = []
    for blocco in testo.split("\n\n"):
        nome, dati = "", ""
        for riga in blocco.splitlines():
            if riga.startswith("event: "):
                nome = riga[7:]
            elif riga.startswith("data: "):
                dati += riga[6:]
        if nome:
            eventi.append((nome, json.loads(dati or "{}")))
    return eventi
