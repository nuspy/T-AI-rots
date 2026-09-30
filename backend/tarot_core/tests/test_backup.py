"""Il backup sul NAS e il ripristino (v8.3), con un server SFTP finto e `pg_dump`/`pg_restore` veri su database di
prova: nessun NAS e nessun database veri."""
from __future__ import annotations

import os
import shutil
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text
from sqlalchemy.engine import make_url

from tarot_core.domain.backup_models import BackupEsecuzione
from tarot_core.settings import get_settings
from tarot_core.tarot import backup

from .conftest import richiede_database

pytestmark = [
    richiede_database,
    pytest.mark.skipif(not shutil.which("pg_dump") or not shutil.which("pg_restore"), reason="serve il client PostgreSQL"),
]

URL_TEST = os.environ.get("TAROT_TEST_DATABASE_URL", "")


@pytest.fixture
def nas(tmp_path, monkeypatch):
    import paramiko

    from .sftp_finto import ServerSftpFinto

    chiave = paramiko.RSAKey.generate(2048)
    file_chiave = tmp_path / "chiave"
    chiave.write_private_key_file(str(file_chiave))
    radice = tmp_path / "nas"
    radice.mkdir()
    server = ServerSftpFinto(radice, chiave).avvia()
    monkeypatch.setenv("TAROT_BACKUP_CHIAVE_SSH", str(file_chiave))
    monkeypatch.setenv("TAROT_BACKUP_PASSWORD", "")
    get_settings.cache_clear()
    yield server
    server.ferma()
    get_settings.cache_clear()


@pytest.fixture
def admin(client, principal_admin):
    client.identita.principal = principal_admin
    return client


def _dest(nas, **campi):
    return backup.Destinazione(host="127.0.0.1", porta=nas.porta, utente="nuspy", cartella="/backup/tarots", **campi)


async def _configura(session, nas, *, attivo=True, conserva=7, fidati=True):
    riga = await backup.impostazioni(session)
    riga.attivo, riga.host, riga.porta, riga.utente = attivo, "127.0.0.1", nas.porta, "nuspy"
    riga.cartella, riga.conserva = "/backup/tarots", conserva
    riga.impronta_host = backup.impronta(nas.chiave_host) if fidati else None
    await session.commit()


def _copie(nas):
    return sorted(p.name for p in (nas.radice / "backup" / "tarots").iterdir())


# ---- la prova e la chiave dell'host -------------------------------------------------------------------------


async def test_la_prova_mostra_la_chiave_del_nas_e_la_fa_accettare(admin, nas):
    r = await admin.put("/admin/backup/impostazioni", json={
        "attivo": False, "host": "127.0.0.1", "porta": nas.porta, "utente": "nuspy", "cartella": "/backup/tarots", "conserva": 7,
    })
    assert r.status_code == 200, r.text
    prova = (await admin.post("/admin/backup/prova", json={})).json()
    assert prova["riuscita"] is True and prova["accettata"] is False
    assert prova["impronta"] == backup.impronta(nas.chiave_host)
    assert (nas.radice / "backup" / "tarots").is_dir() and _copie(nas) == []  # cartella creata, file di prova tolto
    fidata = (await admin.post("/admin/backup/prova", json={"fidati": True})).json()
    assert fidata["accettata"] is True
    stato = (await admin.get("/admin/backup")).json()
    assert stato["impostazioni"]["impronta_host"] == prova["impronta"] and stato["credenziale"]["chiave_ssh"] is True
    assert [e["tipo"] for e in stato["esecuzioni"]] == ["prova", "prova"]
    # cambiare NAS fa dimenticare la chiave accettata
    await admin.put("/admin/backup/impostazioni", json={
        "attivo": False, "host": "127.0.0.2", "porta": nas.porta, "utente": "nuspy", "cartella": "/backup/tarots", "conserva": 7,
    })
    assert (await admin.get("/admin/backup")).json()["impostazioni"]["impronta_host"] is None


async def test_senza_chiave_accettata_o_con_una_chiave_diversa_nessun_dato_parte(session, session_factory, nas):
    await _configura(session, nas, fidati=False)
    r = await backup.esegui_backup(session_factory, manuale=True, url_db=URL_TEST)
    assert r.esito == "errore" and "non è ancora stata accettata" in r.dettaglio
    riga = await backup.impostazioni(session)
    riga.impronta_host = "SHA256:" + "A" * 43
    await session.commit()
    r = await backup.esegui_backup(session_factory, manuale=True, url_db=URL_TEST)
    assert r.esito == "errore" and "è cambiata" in r.dettaglio
    assert not (nas.radice / "backup" / "tarots").exists()


async def test_una_credenziale_sbagliata_si_dice(session, nas, monkeypatch, tmp_path):
    import paramiko

    altra = tmp_path / "altra"
    paramiko.RSAKey.generate(2048).write_private_key_file(str(altra))
    monkeypatch.setenv("TAROT_BACKUP_CHIAVE_SSH", str(altra))
    get_settings.cache_clear()
    with pytest.raises(backup.ErroreBackup, match="rifiutato l'accesso"):
        backup.prova_collegamento(_dest(nas))


# ---- il backup -----------------------------------------------------------------------------------------------


async def test_il_backup_carica_verifica_e_tiene_solo_le_ultime_copie(session, session_factory, nas, monkeypatch):
    await _configura(session, nas, conserva=2)
    orologio = iter(datetime(2026, 10, 1, 2, 30, tzinfo=timezone.utc) + timedelta(days=i) for i in range(10))
    nome_vero = backup._nome_copia
    monkeypatch.setattr(backup, "_nome_copia", lambda tipo, quando: nome_vero(tipo, next(orologio)))
    esiti = [await backup.esegui_backup(session_factory, url_db=URL_TEST) for _ in range(3)]
    assert [e.esito for e in esiti] == ["ok", "ok", "ok"], [e.dettaglio for e in esiti]
    assert _copie(nas) == [
        "tarots-20261002-023000.dump", "tarots-20261002-023000.dump.sha256",
        "tarots-20261003-023000.dump", "tarots-20261003-023000.dump.sha256",
    ]
    assert esiti[2].eliminati == ["tarots-20261001-023000.dump"]
    ultimo = nas.radice / "backup" / "tarots" / esiti[2].file
    assert ultimo.stat().st_size == esiti[2].byte and backup.sha256_di(ultimo) == esiti[2].sha256
    assert ultimo.read_bytes()[:5] == b"PGDMP"


async def test_due_copie_nello_stesso_secondo_non_si_sovrascrivono(session, session_factory, nas, monkeypatch):
    await _configura(session, nas)
    fermo = datetime(2026, 10, 1, 2, 30, tzinfo=timezone.utc)
    nome_vero = backup._nome_copia
    monkeypatch.setattr(backup, "_nome_copia", lambda tipo, quando: nome_vero(tipo, fermo))
    nomi = [(await backup.esegui_backup(session_factory, manuale=True, url_db=URL_TEST)).file for _ in range(3)]
    assert nomi == ["tarots-20261001-023000.dump", "tarots-20261001-023000-2.dump", "tarots-20261001-023000-3.dump"]
    elenco = [c.nome for c in backup.elenco_copie(_dest(nas, impronta_host=backup.impronta(nas.chiave_host)))]
    assert elenco == ["tarots-20261001-023000-3.dump", "tarots-20261001-023000-2.dump", "tarots-20261001-023000.dump"]


async def test_il_backup_notturno_spento_si_salta(session, session_factory, nas):
    await _configura(session, nas, attivo=False)
    r = await backup.esegui_backup(session_factory, url_db=URL_TEST)
    assert r.esito == "saltato"
    r = await backup.esegui_backup(session_factory, manuale=True, url_db=URL_TEST)
    assert r.esito == "ok"


async def test_esegui_ora_e_l_elenco_delle_copie_dalla_console(admin, session, nas, monkeypatch):
    monkeypatch.setenv("TAROT_DATABASE_URL", URL_TEST)
    get_settings.cache_clear()
    await _configura(session, nas)
    assert (await admin.post("/admin/backup/esegui")).status_code == 202
    stato = (await admin.get("/admin/backup")).json()
    assert stato["esecuzioni"][0]["tipo"] == "backup" and stato["esecuzioni"][0]["esito"] == "ok", stato["esecuzioni"][0]
    copie = (await admin.get("/admin/backup/copie")).json()["copie"]
    assert len(copie) == 1 and copie[0]["con_sha256"] and copie[0]["sicurezza"] is False


async def test_solo_l_amministratore_e_la_conferma_scritta(client, admin, nas):
    client.identita.principal = None
    from tarot_core.auth.keycloak import Principal

    client.identita.principal = Principal(subject="utente-normale", roles={"user"})
    assert (await client.get("/admin/backup")).status_code == 403
    assert (await client.post("/admin/backup/ripristina", json={"file": "tarots-20261001-023000.dump", "conferma": "tarots"})).status_code == 403


async def test_il_ripristino_vuole_la_parola_e_un_nome_valido(admin, nas):
    assert (await admin.post("/admin/backup/ripristina", json={"file": "tarots-20261001-023000.dump", "conferma": "si"})).status_code == 422
    assert (await admin.post("/admin/backup/ripristina", json={"file": "../etc/passwd", "conferma": "tarots"})).status_code == 422


# ---- il ripristino -------------------------------------------------------------------------------------------


@pytest.fixture
def db_temporaneo():
    """Un database a parte da ripristinare: quello dei test resta intatto."""
    import psycopg

    base = make_url(URL_TEST)
    nome = "tarot_test_ripristino"
    amministrativo = base.set(drivername="postgresql", database="postgres").render_as_string(hide_password=False)
    with psycopg.connect(amministrativo, autocommit=True) as c:
        c.execute(f"DROP DATABASE IF EXISTS {nome} WITH (FORCE)")
        c.execute(f"CREATE DATABASE {nome}")
    url = base.set(database=nome).render_as_string(hide_password=False)
    diretto = base.set(drivername="postgresql", database=nome).render_as_string(hide_password=False)
    with psycopg.connect(diretto, autocommit=True) as c:
        c.execute("CREATE TABLE segno (valore text)")
        c.execute("INSERT INTO segno VALUES ('prima')")
    yield url, diretto
    with psycopg.connect(amministrativo, autocommit=True) as c:
        c.execute(f"DROP DATABASE IF EXISTS {nome} WITH (FORCE)")


def _segno(diretto):
    import psycopg

    with psycopg.connect(diretto) as c:
        return c.execute("SELECT valore FROM segno").fetchone()[0]


def _cambia_segno(diretto, valore):
    import psycopg

    with psycopg.connect(diretto, autocommit=True) as c:
        c.execute("UPDATE segno SET valore = %s", (valore,))


async def test_il_ripristino_fa_prima_la_copia_di_sicurezza_e_riporta_il_database(session, session_factory, nas, db_temporaneo):
    url, diretto = db_temporaneo
    await _configura(session, nas)
    copia = await backup.esegui_backup(session_factory, manuale=True, url_db=url)
    assert copia.esito == "ok"
    _cambia_segno(diretto, "dopo")

    stato = await backup.ripristina(session_factory, copia.file, actor_id=None, url_db=url)
    assert stato["esito"] == "ok", stato
    assert _segno(diretto) == "prima"
    sicurezze = [n for n in _copie(nas) if n.startswith("tarots-sicurezza-") and n.endswith(".dump")]
    assert len(sicurezze) == 1
    # la copia di sicurezza contiene lo stato di prima del ripristino: «dopo»
    stato = await backup.ripristina(session_factory, sicurezze[0], actor_id=None, url_db=url)
    assert stato["esito"] == "ok" and _segno(diretto) == "dopo"
    righe = (await session.execute(select(BackupEsecuzione).where(BackupEsecuzione.tipo == "ripristino"))).scalars().all()
    assert {r.esito for r in righe} == {"ok"} and len(righe) == 2


async def test_una_copia_rovinata_non_si_ripristina_e_il_database_resta_com_era(session, session_factory, nas, db_temporaneo):
    url, diretto = db_temporaneo
    await _configura(session, nas)
    copia = await backup.esegui_backup(session_factory, manuale=True, url_db=url)
    _cambia_segno(diretto, "dopo")
    (nas.radice / "backup" / "tarots" / f"{copia.file}.sha256").write_text("0" * 64 + "  x\n")
    stato = await backup.ripristina(session_factory, copia.file, actor_id=None, url_db=url)
    assert stato["esito"] == "errore" and "sha256" in stato["dettaglio"]
    assert _segno(diretto) == "dopo"
    righe = (await session.execute(
        select(BackupEsecuzione).where(BackupEsecuzione.tipo == "ripristino", BackupEsecuzione.esito == "errore")
    )).scalars().all()
    assert len(righe) == 1
    # e una copia che non esiste
    stato = await backup.ripristina(session_factory, "tarots-19990101-000000.dump", actor_id=None, url_db=url)
    assert stato["esito"] == "errore" and "non è sul NAS" in stato["dettaglio"]


async def test_lo_strumento_del_cronjob(session, session_factory, nas, monkeypatch):
    await _configura(session, nas)
    monkeypatch.setenv("TAROT_DATABASE_URL", URL_TEST)
    get_settings.cache_clear()
    r = await backup.esegui_backup(session_factory)
    assert r.esito == "ok" and (await session.execute(text("select count(*) from backup_esecuzioni"))).scalar_one() >= 1
