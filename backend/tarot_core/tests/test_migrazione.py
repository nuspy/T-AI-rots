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


def _modulo_dati_v94():
    """La migrazione dei dati del Journal v9.4, per chiamarne `applica` e `annulla` su una connessione qualunque."""
    import importlib.util

    percorso = BACKEND / "tarot_core" / "migrations" / "versions" / "20261022_1000_blog_sezioni_ricche_dati.py"
    spec = importlib.util.spec_from_file_location("migrazione_dati_v94", percorso)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_la_migrazione_dei_dati_v94_e_idempotente_e_si_annulla(database_scratch):
    """Minor Arcana per seme e per numero, il soggetto degli articoli, gli articoli su una carta nella sua sezione (solo
    da una sezione generica): su un albero «di prima», poi di nuovo (niente cambia), poi giù e di nuovo su."""
    import uuid

    from alembic import command
    from sqlalchemy import create_engine, text

    cfg = _config()
    command.upgrade(cfg, "d1f3a5c7e9b2")
    motore = create_engine(database_scratch)

    def sezione(conn, slug, nome, tipo, padre=None, filtro=None, descrizione=None):
        return conn.execute(text(
            "INSERT INTO blog_sections (slug, nome, tipo, filtro, parent_id, descrizione) "
            "VALUES (:s, :n, :t, CAST(:f AS jsonb), :p, :d) RETURNING id"
        ), {"s": slug, "n": nome, "t": tipo, "f": filtro, "p": padre, "d": descrizione}).scalar()

    def articolo(conn, titolo, sezione_id=None, soggetto=None):
        pid = uuid.uuid4()
        conn.execute(text(
            "INSERT INTO blog_posts (id, slug, titolo, testo, lang, stato, sezione_id, soggetto_tipo, soggetto_ref) "
            "VALUES (:id, :slug, :titolo, '', 'en', 'pubblicato', :sez, :st, :sr)"
        ), {"id": pid, "slug": str(pid), "titolo": titolo, "sez": sezione_id,
            "st": soggetto[0] if soggetto else None, "sr": soggetto[1] if soggetto else None})
        return pid

    try:
        with motore.begin() as conn:
            tarot = sezione(conn, "tarot", "Tarot", "contenitore")
            maggiori = sezione(conn, "major-arcana", "Major Arcana", "carte", tarot, '{"arcano": "maggiore"}')
            minori = sezione(conn, "minor-arcana", "Minor Arcana", "contenitore", tarot,
                             descrizione="The fifty-six cards of everyday life, divided into four suits.")
            bastoni = sezione(conn, "wands", "Wands", "carte", minori, '{"seme": "bastoni"}')
            coppe = sezione(conn, "cups", "Cups", "carte", minori, '{"seme": "coppe"}')
            impara = sezione(conn, "learn-tarot", "Learn Tarot", "articoli", tarot)
            amore = sezione(conn, "love", "Love", "articoli")
            sezione(conn, "queens", "Queens of the blog", "articoli")         # uno slug già occupato: non si tocca
            ruota = articolo(conn, "Wheel of Fortune Tarot Meaning", impara)
            asso = articolo(conn, "Ace of Cups")
            amanti = articolo(conn, "The Lovers tarot card in love", amore)
            luna = articolo(conn, "Full Moon Tarot Spread", impara)
            croce = articolo(conn, "How to read the Celtic Cross", impara)
            scelto = articolo(conn, "The Tower tarot card", impara, soggetto=("carta", "maj-17"))

        command.upgrade(cfg, "head")
        with motore.connect() as conn:
            def padre(slug):
                return conn.execute(text("SELECT parent_id FROM blog_sections WHERE slug = :s"), {"s": slug}).scalar()

            def post(pid):
                return conn.execute(text("SELECT sezione_id, soggetto_tipo, soggetto_ref FROM blog_posts WHERE id = :i"),
                                    {"i": pid}).one()

            per_seme = conn.execute(text("SELECT id FROM blog_sections WHERE slug = 'by-suit'")).scalar()
            per_numero = conn.execute(text("SELECT id FROM blog_sections WHERE slug = 'by-number'")).scalar()
            assert padre("by-suit") == padre("by-number") == minori
            assert padre("wands") == padre("cups") == per_seme
            gradi = conn.execute(text(
                "SELECT slug, filtro->>'rango' FROM blog_sections WHERE parent_id = :p ORDER BY ordine"
            ), {"p": per_numero}).all()
            assert [g[0] for g in gradi] == ["aces", "twos", "threes", "fours", "fives", "sixes", "sevens", "eights",
                                            "nines", "tens", "princesses", "princes", "knights"]
            assert dict(gradi)["aces"] == "asso" and padre("queens") is None
            assert tuple(post(ruota)) == (maggiori, "carta", "maj-10")     # da una sezione generica alla sua
            assert tuple(post(asso)) == (coppe, "carta", "coppe-01")       # da nessuna sezione alla sua
            assert tuple(post(amanti)) == (amore, "carta", "maj-06")       # una sezione a tema resta
            assert tuple(post(luna)) == (impara, None, None)
            assert tuple(post(croce)) == (impara, "stesa", "croce-celtica")  # le stese non si spostano
            assert tuple(post(scelto)) == (maggiori, "carta", "maj-17")    # il soggetto già scritto non si ricalcola
            assert conn.execute(text("SELECT descrizione FROM blog_sections WHERE id = :i"), {"i": minori}).scalar() \
                == "The fifty-six cards of everyday life, by suit and by number."
            n_sezioni = conn.execute(text("SELECT count(*) FROM blog_sections")).scalar()

        # Idempotente: una seconda volta non cambia niente e non lascia tracce.
        modulo = _modulo_dati_v94()
        with motore.begin() as conn:
            traccia = modulo.applica(conn)
        assert not any(traccia.values())
        with motore.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM blog_sections")).scalar() == n_sezioni

        # Giù: tutto com'era.
        command.downgrade(cfg, "d1f3a5c7e9b2")
        with motore.connect() as conn:
            assert conn.execute(text("SELECT count(*) FROM blog_sections WHERE slug IN ('by-suit', 'by-number', 'aces')")).scalar() == 0
            assert conn.execute(text("SELECT parent_id FROM blog_sections WHERE id = :i"), {"i": bastoni}).scalar() == minori
            assert conn.execute(text("SELECT slug FROM blog_sections WHERE slug = 'queens'")).scalar() == "queens"
            righe = {r.id: r for r in conn.execute(text("SELECT id, sezione_id, soggetto_tipo, soggetto_ref FROM blog_posts"))}
            assert (righe[ruota].sezione_id, righe[ruota].soggetto_ref) == (impara, None)
            assert (righe[asso].sezione_id, righe[asso].soggetto_ref) == (None, None)
            assert (righe[scelto].sezione_id, righe[scelto].soggetto_ref) == (impara, "maj-17")
            assert conn.execute(text("SELECT descrizione FROM blog_sections WHERE id = :i"), {"i": minori}).scalar() \
                == "The fifty-six cards of everyday life, divided into four suits."

        # E di nuovo su: lo stesso risultato.
        command.upgrade(cfg, "head")
        with motore.connect() as conn:
            assert conn.execute(text("SELECT sezione_id FROM blog_posts WHERE id = :i"), {"i": ruota}).scalar() == maggiori
            assert conn.execute(text("SELECT count(*) FROM blog_sections")).scalar() == n_sezioni
    finally:
        motore.dispose()


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

        blog = {"media_images", "blog_sections", "blog_tags", "blog_posts", "blog_post_tags", "blog_post_links", "blog_post_revisions"}
        assert blog <= tabelle and {"nome_pubblico", "avatar_id"} <= _colonne(motore, "users")

        # Prima il blog...
        command.downgrade(cfg, "3d7a9c1e5b28")
        assert not (blog & set(inspect(motore).get_table_names()))
        assert not ({"nome_pubblico", "avatar_id"} & _colonne(motore, "users"))
        assert "promemoria_2fa" in _colonne(motore, "users")

        # ...poi il promemoria della 2FA...
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
