"""Il backup del database sul NAS, e il ripristino (v8.3).

**Cosa si salva.** Il database `tarots` intero con `pg_dump -Fc`: l'app, lo schema `keycloak` (utenti e accessi) e
le immagini (sono blob in `media_images`, `share_images`). Un file per notte, `tarots-AAAAMMGG-HHMMSS.dump`, con
accanto `<file>.sha256`.

**Dove.** Su SFTP (paramiko), nella cartella scelta dalla console. La chiave dell'host del NAS si accetta una volta
dalla console («Fidati di questa chiave») e poi si controlla a ogni collegamento: un host con un'altra chiave non
riceve il database. La credenziale (chiave SSH privata o password) la monta un Secret, mai nel database.

**Quante copie.** Si tengono le `conserva` più recenti (sette, se la console non dice altro); le più vecchie si
cancellano **solo dopo** un caricamento riuscito e verificato (dimensione sul NAS = dimensione locale). Le copie di
sicurezza fatte prima di un ripristino (`tarots-sicurezza-…`) hanno un conto a parte: se ne tengono tre.

**Il ripristino.** Prima una copia di sicurezza (se fallisce, non si ripristina niente), poi il file scelto si scarica
e si confronta con il suo `.sha256`, poi `pg_restore --clean --if-exists --single-transaction`: o si ripristina
tutto, o niente. `lock_timeout` evita di restare appesi dietro una connessione che tiene una tabella. Il registro
delle esecuzioni sta nello stesso database e torna com'era al momento della copia: le righe della copia di
sicurezza e del ripristino si riscrivono subito dopo. Poi API e Keycloak vanno riavviati (lo dice la console).
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import os
import posixpath
import re
import smtplib
import stat as stat_mod
import subprocess
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional

from sqlalchemy import select
from sqlalchemy.engine import make_url

from ..domain.backup_models import BackupEsecuzione, ImpostazioniBackup
from ..domain.base import utcnow
from ..domain.repositories import AuditRepository
from ..settings import get_settings

logger = logging.getLogger(__name__)

ID_RIGA = 1
#: Le copie di sicurezza fatte prima di un ripristino che si tengono.
CONSERVA_SICUREZZA = 3
#: Il nome di ogni copia: niente altro si legge, si scarica o si cancella dalla cartella del NAS.
NOME_COPIA = re.compile(r"^tarots-(sicurezza-)?(\d{8}-\d{6})\.dump$")
LOCK_TIMEOUT_MS = 60_000
TIMEOUT_SSH = 20


class ErroreBackup(Exception):
    """Un errore da mostrare così com'è in console e nell'avviso email."""


@dataclass
class Destinazione:
    host: str
    porta: int
    utente: str
    cartella: str
    conserva: int = 7
    impronta_host: Optional[str] = None

    def completa(self) -> bool:
        return bool(self.host and self.utente and self.cartella)


@dataclass
class Copia:
    nome: str
    byte: int
    modificata: datetime
    sicurezza: bool
    con_sha256: bool = False


@dataclass
class StatoRipristino:
    """Il ripristino in corso (uno alla volta, nel processo dell'API): la console lo interroga mentre lavora."""

    in_corso: bool = False
    fase: str = ""
    file: Optional[str] = None
    esito: Optional[str] = None
    dettaglio: Optional[str] = None
    iniziato: Optional[datetime] = None
    finito: Optional[datetime] = None
    passi: List[str] = field(default_factory=list)


STATO = StatoRipristino()
_blocco = asyncio.Lock()


# ---- la destinazione ----------------------------------------------------------------------------------------


async def impostazioni(session) -> ImpostazioniBackup:
    riga = await session.get(ImpostazioniBackup, ID_RIGA)
    if riga is None:
        riga = ImpostazioniBackup(id=ID_RIGA)
        session.add(riga)
        await session.flush()
    return riga


def destinazione_di(riga: ImpostazioniBackup) -> Destinazione:
    return Destinazione(
        host=riga.host.strip(), porta=riga.porta, utente=riga.utente.strip(), cartella=riga.cartella.strip(),
        conserva=riga.conserva, impronta_host=riga.impronta_host,
    )


def credenziale() -> Dict[str, Any]:
    """Com'è configurato l'accesso al NAS, senza mai mostrare il segreto."""
    s = get_settings()
    chiave = bool(s.backup_chiave_ssh) and os.path.isfile(s.backup_chiave_ssh)
    return {"chiave_ssh": chiave, "password": bool(s.backup_password), "configurata": chiave or bool(s.backup_password)}


# ---- SFTP --------------------------------------------------------------------------------------------------


def impronta(chiave) -> str:
    """L'impronta di una chiave SSH come la stampa OpenSSH: `SHA256:<base64 senza =>`."""
    return "SHA256:" + base64.b64encode(hashlib.sha256(chiave.asbytes()).digest()).decode().rstrip("=")


def _chiave_privata(percorso: str):
    import paramiko

    try:
        return paramiko.PKey.from_path(percorso)
    except (paramiko.SSHException, OSError, ValueError) as exc:
        raise ErroreBackup(f"la chiave SSH del Secret non si legge ({type(exc).__name__})") from exc


class Archivio:
    """La cartella del NAS, aperta su SFTP. Si usa con `with apri(dest) as archivio:`."""

    def __init__(self, sftp, cartella: str, impronta_vista: str) -> None:
        self._sftp = sftp
        self.cartella = cartella
        self.impronta_vista = impronta_vista

    def _percorso(self, nome: str) -> str:
        return posixpath.join(self.cartella, nome)

    def assicura_cartella(self) -> None:
        parziale = "/" if self.cartella.startswith("/") else ""
        for pezzo in [p for p in self.cartella.split("/") if p]:
            parziale = posixpath.join(parziale, pezzo) if parziale else pezzo
            try:
                self._sftp.stat(parziale)
            except FileNotFoundError:
                self._sftp.mkdir(parziale)

    def carica(self, locale: Path, nome: str) -> int:
        """Carica con un nome provvisorio e poi rinomina: una copia a metà non ha mai il nome di una copia."""
        provvisorio = self._percorso(f".{nome}.parziale")
        self._sftp.put(str(locale), provvisorio)
        try:
            self._sftp.remove(self._percorso(nome))
        except FileNotFoundError:
            pass
        self._sftp.rename(provvisorio, self._percorso(nome))
        return self._sftp.stat(self._percorso(nome)).st_size

    def scrivi_testo(self, nome: str, testo: str) -> None:
        with self._sftp.open(self._percorso(nome), "w") as f:
            f.write(testo.encode("utf-8"))

    def leggi_testo(self, nome: str) -> Optional[str]:
        try:
            with self._sftp.open(self._percorso(nome), "r") as f:
                return f.read().decode("utf-8", "replace")
        except FileNotFoundError:
            return None

    def scarica(self, nome: str, locale: Path) -> None:
        self._sftp.get(self._percorso(nome), str(locale))

    def elimina(self, nome: str) -> None:
        try:
            self._sftp.remove(self._percorso(nome))
        except FileNotFoundError:
            pass

    def elenco(self) -> List[Copia]:
        voci = {a.filename: a for a in self._sftp.listdir_attr(self.cartella)}
        copie = []
        for nome, a in voci.items():
            m = NOME_COPIA.match(nome)
            if not m or not stat_mod.S_ISREG(a.st_mode or 0):
                continue
            copie.append(Copia(
                nome=nome, byte=a.st_size or 0, sicurezza=bool(m.group(1)),
                modificata=datetime.fromtimestamp(a.st_mtime or 0, tz=timezone.utc),
                con_sha256=f"{nome}.sha256" in voci,
            ))
        # Dalla più recente, per data e ora nel nome (non per data di modifica: una copia ricaricata non ringiovanisce).
        return sorted(copie, key=lambda c: NOME_COPIA.match(c.nome).group(2), reverse=True)


@contextmanager
def apri(dest: Destinazione, *, richiedi_impronta: bool = True) -> Iterator[Archivio]:
    """Il collegamento SFTP. Con `richiedi_impronta` la chiave dell'host deve essere quella accettata in console;
    senza (la prova di collegamento) si legge e si restituisce, per farla accettare."""
    import paramiko

    if not dest.completa():
        raise ErroreBackup("destinazione incompleta: servono host, utente e cartella")
    s = get_settings()
    trasporto = None
    try:
        try:
            trasporto = paramiko.Transport((dest.host, dest.porta))
            trasporto.banner_timeout = TIMEOUT_SSH
            trasporto.start_client(timeout=TIMEOUT_SSH)
        except (OSError, paramiko.SSHException) as exc:
            raise ErroreBackup(f"il NAS non risponde su {dest.host}:{dest.porta} ({exc})") from exc
        vista = impronta(trasporto.get_remote_server_key())
        if dest.impronta_host and vista != dest.impronta_host:
            raise ErroreBackup(
                f"la chiave del NAS è cambiata ({vista}, attesa {dest.impronta_host}): nessun dato inviato. "
                "Se il NAS è stato reinstallato, rifai la prova e accetta la chiave nuova."
            )
        if richiedi_impronta and not dest.impronta_host:
            raise ErroreBackup("la chiave del NAS non è ancora stata accettata: fai la prova dalla console")
        try:
            if s.backup_chiave_ssh and os.path.isfile(s.backup_chiave_ssh):
                trasporto.auth_publickey(dest.utente, _chiave_privata(s.backup_chiave_ssh))
            elif s.backup_password:
                trasporto.auth_password(dest.utente, s.backup_password)
            else:
                raise ErroreBackup("manca la credenziale del NAS: il Secret tarots-backup (chiave SSH o password)")
        except paramiko.AuthenticationException as exc:
            raise ErroreBackup(f"il NAS ha rifiutato l'accesso come {dest.utente}") from exc
        sftp = paramiko.SFTPClient.from_transport(trasporto)
        if sftp is None:
            raise ErroreBackup("SFTP non disponibile sul NAS")
        try:
            yield Archivio(sftp, dest.cartella.rstrip("/") or "/", vista)
        finally:
            sftp.close()
    finally:
        if trasporto is not None:
            trasporto.close()


def prova_collegamento(dest: Destinazione) -> Dict[str, Any]:
    """Collegamento, cartella (creata se manca), scrittura e cancellazione di un file di prova. Restituisce
    l'impronta vista, da accettare in console."""
    inizio = time.monotonic()
    with apri(dest, richiedi_impronta=False) as archivio:
        archivio.assicura_cartella()
        nome = f".tarots-prova-{uuid.uuid4().hex[:8]}"
        archivio.scrivi_testo(nome, "prova di scrittura del backup di TAROTS chat\n")
        letto = archivio.leggi_testo(nome)
        archivio.elimina(nome)
        if not letto:
            raise ErroreBackup("il file di prova non si rilegge dal NAS")
        return {
            "impronta": archivio.impronta_vista,
            "accettata": dest.impronta_host == archivio.impronta_vista,
            "copie": len(archivio.elenco()),
            "millisecondi": int((time.monotonic() - inizio) * 1000),
        }


# ---- PostgreSQL --------------------------------------------------------------------------------------------


def _ambiente_pg(url_db: str) -> Dict[str, str]:
    u = make_url(url_db)
    env = dict(os.environ)
    env.update({
        "PGHOST": u.host or "localhost", "PGPORT": str(u.port or 5432), "PGUSER": u.username or "",
        "PGDATABASE": u.database or "", "PGCONNECT_TIMEOUT": "20",
    })
    if u.password:
        env["PGPASSWORD"] = u.password
    return env


def _esegui(comando: List[str], env: Dict[str, str], timeout: int) -> None:
    try:
        esito = subprocess.run(comando, env=env, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise ErroreBackup(f"{comando[0]} non è installato nell'immagine") from exc
    except subprocess.TimeoutExpired as exc:
        raise ErroreBackup(f"{Path(comando[0]).name} non ha finito entro {timeout} s") from exc
    if esito.returncode != 0:
        # Mai la password: PGPASSWORD sta nell'ambiente, non negli argomenti, quindi non compare qui.
        raise ErroreBackup(f"{Path(comando[0]).name} è fallito: {(esito.stderr or esito.stdout).strip()[-800:]}")


def dump(destinazione: Path, url_db: Optional[str] = None) -> None:
    s = get_settings()
    _esegui([s.backup_pg_dump, "-Fc", "-Z", "6", "-f", str(destinazione)], _ambiente_pg(url_db or s.database_url), 3600)


def restore(sorgente: Path, url_db: Optional[str] = None) -> None:
    s = get_settings()
    env = _ambiente_pg(url_db or s.database_url)
    env["PGOPTIONS"] = f"-c lock_timeout={LOCK_TIMEOUT_MS}"
    _esegui([
        s.backup_pg_restore, "--clean", "--if-exists", "--single-transaction", "--no-owner", "--no-acl",
        "-d", env["PGDATABASE"], str(sorgente),
    ], env, 3600)


def sha256_di(percorso: Path) -> str:
    h = hashlib.sha256()
    with percorso.open("rb") as f:
        for pezzo in iter(lambda: f.read(1 << 20), b""):
            h.update(pezzo)
    return h.hexdigest()


# ---- il backup ---------------------------------------------------------------------------------------------


def _nome_copia(tipo: str, quando: datetime) -> str:
    return f"tarots-{'sicurezza-' if tipo == 'sicurezza' else ''}{quando.strftime('%Y%m%d-%H%M%S')}.dump"


def _rotazione(archivio: Archivio, conserva: int) -> List[str]:
    """Le copie oltre le `conserva` più recenti (e le copie di sicurezza oltre le tre più recenti)."""
    eliminati = []
    copie = archivio.elenco()
    for sicurezza, tenere in ((False, conserva), (True, CONSERVA_SICUREZZA)):
        for c in [c for c in copie if c.sicurezza == sicurezza][tenere:]:
            archivio.elimina(c.nome)
            archivio.elimina(f"{c.nome}.sha256")
            eliminati.append(c.nome)
    return eliminati


def _fai_backup(dest: Destinazione, tipo: str, url_db: Optional[str]) -> Dict[str, Any]:
    """Il lavoro vero, sincrono (in un thread): dump, caricamento, verifica, rotazione."""
    nome = _nome_copia(tipo, utcnow())
    with tempfile.TemporaryDirectory(prefix="tarots-backup-") as cartella:
        locale = Path(cartella) / nome
        dump(locale, url_db)
        byte = locale.stat().st_size
        impronta_file = sha256_di(locale)
        with apri(dest) as archivio:
            archivio.assicura_cartella()
            sul_nas = archivio.carica(locale, nome)
            if sul_nas != byte:
                archivio.elimina(nome)
                raise ErroreBackup(f"caricamento incompleto: {sul_nas} byte sul NAS invece di {byte}")
            archivio.scrivi_testo(f"{nome}.sha256", f"{impronta_file}  {nome}\n")
            eliminati = _rotazione(archivio, dest.conserva)
    return {"file": nome, "byte": byte, "sha256": impronta_file, "eliminati": eliminati}


async def esegui_backup(
    fabbrica: Callable[[], Any], *, tipo: str = "backup", manuale: bool = False, actor_id: Optional[int] = None,
    url_db: Optional[str] = None, avvisa: bool = True,
) -> BackupEsecuzione:
    """Un backup completo, registrato. Non solleva: l'esito sta nella riga restituita (staccata dalla sessione)."""
    async with fabbrica() as session:
        riga_imp = await impostazioni(session)
        dest = destinazione_di(riga_imp)
        attivo = riga_imp.attivo
        esecuzione = BackupEsecuzione(tipo=tipo, manuale=manuale, actor_id=actor_id, esito="in_corso")
        if tipo == "backup" and not manuale and not attivo:
            esecuzione.esito, esecuzione.dettaglio, esecuzione.finita_il = "saltato", "backup spento dalla console", utcnow()
        session.add(esecuzione)
        await session.commit()
        await session.refresh(esecuzione)
    if esecuzione.esito == "saltato":
        return esecuzione

    inizio = time.monotonic()
    try:
        risultato = await asyncio.to_thread(_fai_backup, dest, tipo, url_db)
        esito, dettaglio = "ok", None
    except ErroreBackup as exc:
        risultato, esito, dettaglio = {}, "errore", str(exc)
    except Exception as exc:  # noqa: BLE001 — qualunque guasto finisce nel registro, non in un 500 muto
        logger.exception("Backup fallito")
        risultato, esito, dettaglio = {}, "errore", f"{type(exc).__name__}: {exc}"[:2000]

    async with fabbrica() as session:
        riga = await session.get(BackupEsecuzione, esecuzione.id)
        riga.esito = esito
        riga.dettaglio = dettaglio
        riga.durata_secondi = int(time.monotonic() - inizio)
        riga.finita_il = utcnow()
        riga.file = risultato.get("file")
        riga.byte = risultato.get("byte")
        riga.sha256 = risultato.get("sha256")
        riga.eliminati = risultato.get("eliminati", [])
        await session.commit()
        await session.refresh(riga)
        session.expunge(riga)
    logger.info("Backup %s: %s %s", tipo, esito, riga.file or dettaglio)
    if esito == "errore" and avvisa and not manuale:
        await _avvisa(fabbrica, riga)
    return riga


async def _avvisa(fabbrica, riga: BackupEsecuzione) -> None:
    """L'email ai destinatari del rapporto analytics quando il backup notturno fallisce."""
    import html

    from lanterna import posta

    from ..analytics import rapporto

    try:
        async with fabbrica() as session:
            destinatari = await rapporto.destinatari_attivi(session)
        config = rapporto.config_smtp()
        if not config.configurato or not destinatari:
            logger.warning("Backup fallito e nessun avviso possibile (SMTP o destinatari mancanti)")
            return
        console = f"{get_settings().web_public_url.rstrip('/')}/admin/backup"
        corpo = posta.pagina_html(
            "Backup non riuscito", "Il backup notturno del database non è arrivato sul NAS",
            [f"<p>{html.escape(riga.dettaglio or '')}</p>", f'<p>Dettagli e nuovo tentativo: <a href="{console}">{console}</a></p>'],
        )
        testo = f"Backup non riuscito\n\n{riga.dettaglio}\n\n{console}"
        posta.invia(config, [posta.componi(config, d, "TAROTS chat — backup non riuscito", testo, corpo) for d in destinatari])
    except (OSError, smtplib.SMTPException):
        logger.exception("Avviso del backup non inviato")


# ---- le copie e il ripristino -----------------------------------------------------------------------------


def elenco_copie(dest: Destinazione) -> List[Copia]:
    with apri(dest) as archivio:
        return archivio.elenco()


def _scarica_e_verifica(dest: Destinazione, nome: str, locale: Path) -> str:
    with apri(dest) as archivio:
        if nome not in {c.nome for c in archivio.elenco()}:
            raise ErroreBackup(f"la copia {nome} non è sul NAS")
        archivio.scarica(nome, locale)
        atteso = archivio.leggi_testo(f"{nome}.sha256")
    trovato = sha256_di(locale)
    if atteso and atteso.split()[0] != trovato:
        raise ErroreBackup(f"la copia {nome} non corrisponde al suo sha256: file rovinato, ripristino annullato")
    return trovato


def _passo(testo: str) -> None:
    STATO.fase = testo
    STATO.passi.append(f"{utcnow().strftime('%H:%M:%S')} {testo}")


async def ripristina(
    fabbrica: Callable[[], Any], nome: str, *, actor_id: Optional[int], url_db: Optional[str] = None,
) -> Dict[str, Any]:
    """Copia di sicurezza, poi il ripristino di `nome`. Uno alla volta. Restituisce lo stato finale."""
    if not NOME_COPIA.match(nome):
        raise ErroreBackup("nome di copia non valido")
    if _blocco.locked():
        raise ErroreBackup("c'è già un ripristino in corso")
    async with _blocco:
        STATO.__init__(in_corso=True, file=nome, iniziato=utcnow())
        try:
            _passo("copia di sicurezza del database attuale")
            sicurezza = await esegui_backup(fabbrica, tipo="sicurezza", manuale=True, actor_id=actor_id, url_db=url_db, avvisa=False)
            if sicurezza.esito != "ok":
                raise ErroreBackup(f"copia di sicurezza non riuscita, nessun ripristino: {sicurezza.dettaglio}")
            async with fabbrica() as session:
                dest = destinazione_di(await impostazioni(session))
            inizio = time.monotonic()
            with tempfile.TemporaryDirectory(prefix="tarots-ripristino-") as cartella:
                locale = Path(cartella) / nome
                _passo(f"scaricamento e verifica di {nome}")
                impronta_file = await asyncio.to_thread(_scarica_e_verifica, dest, nome, locale)
                _passo("ripristino nel database (tutto o niente)")
                await asyncio.to_thread(restore, locale, url_db)
            durata = int(time.monotonic() - inizio)
            # Il registro ora è quello della copia: si riscrivono la copia di sicurezza e il ripristino.
            async with fabbrica() as session:
                # Ogni copia contiene la propria riga, scritta «in corso» prima del dump: quella della copia appena
                # ripristinata si chiude qui (se ce n'è più d'una non si può sapere quale sia, e restano come sono).
                aperte = list((await session.execute(select(BackupEsecuzione).where(
                    BackupEsecuzione.esito == "in_corso", BackupEsecuzione.tipo.in_(("backup", "sicurezza")),
                ))).scalars())
                if len(aperte) == 1:
                    aperte[0].esito, aperte[0].file = "ok", nome
                    aperte[0].dettaglio = "chiusa dopo il ripristino: è la copia ripristinata"
                # `merge`: se si è ripristinata proprio la copia di sicurezza, la sua riga c'è già.
                await session.merge(BackupEsecuzione(
                    id=sicurezza.id, tipo="sicurezza", manuale=True, esito="ok", file=sicurezza.file, byte=sicurezza.byte,
                    sha256=sicurezza.sha256, durata_secondi=sicurezza.durata_secondi, eliminati=sicurezza.eliminati,
                    finita_il=sicurezza.finita_il, actor_id=None, extra={"prima_del_ripristino": nome},
                ))
                session.add(BackupEsecuzione(
                    tipo="ripristino", manuale=True, esito="ok", file=nome, sha256=impronta_file, durata_secondi=durata,
                    finita_il=utcnow(), actor_id=None, extra={"copia_di_sicurezza": sicurezza.file, "actor_id": actor_id},
                ))
                await AuditRepository(session).record(
                    action="backup.ripristino", actor_id=None, target_type="database", target_id=nome,
                    before={"copia_di_sicurezza": sicurezza.file}, after={"actor_id": actor_id},
                )
                await session.commit()
            _passo("fatto: riavvia API e Keycloak")
            STATO.esito, STATO.dettaglio = "ok", f"ripristinata {nome}; copia di sicurezza {sicurezza.file}"
        except ErroreBackup as exc:
            STATO.esito, STATO.dettaglio = "errore", str(exc)
            await _registra_errore_ripristino(fabbrica, nome, actor_id, str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ripristino fallito")
            STATO.esito, STATO.dettaglio = "errore", f"{type(exc).__name__}: {exc}"[:2000]
            await _registra_errore_ripristino(fabbrica, nome, actor_id, STATO.dettaglio)
        finally:
            STATO.in_corso = False
            STATO.finito = utcnow()
    return stato_json()


async def _registra_errore_ripristino(fabbrica, nome: str, actor_id: Optional[int], dettaglio: str) -> None:
    """Con `--single-transaction` un ripristino fallito non ha cambiato niente: il registro è ancora quello di prima."""
    try:
        async with fabbrica() as session:
            session.add(BackupEsecuzione(
                tipo="ripristino", manuale=True, esito="errore", file=nome, dettaglio=dettaglio, finita_il=utcnow(),
                actor_id=actor_id,
            ))
            await AuditRepository(session).record(
                action="backup.ripristino_fallito", actor_id=actor_id, target_type="database", target_id=nome,
                after={"dettaglio": dettaglio[:500]},
            )
            await session.commit()
    except Exception:  # noqa: BLE001
        logger.exception("Registro del ripristino fallito non scritto")


def stato_json() -> Dict[str, Any]:
    return {
        "in_corso": STATO.in_corso, "fase": STATO.fase, "file": STATO.file, "esito": STATO.esito,
        "dettaglio": STATO.dettaglio, "passi": list(STATO.passi),
        "iniziato": STATO.iniziato.isoformat() if STATO.iniziato else None,
        "finito": STATO.finito.isoformat() if STATO.finito else None,
    }


def esecuzione_json(r: BackupEsecuzione) -> Dict[str, Any]:
    return {
        "id": str(r.id), "tipo": r.tipo, "manuale": r.manuale, "esito": r.esito, "file": r.file, "byte": r.byte,
        "sha256": r.sha256, "durata_secondi": r.durata_secondi, "eliminati": r.eliminati, "dettaglio": r.dettaglio,
        "avviata_il": r.created_at.isoformat() if r.created_at else None,
        "finita_il": r.finita_il.isoformat() if r.finita_il else None,
    }


async def ultime_esecuzioni(session, limite: int = 30) -> List[BackupEsecuzione]:
    q = select(BackupEsecuzione).order_by(BackupEsecuzione.created_at.desc()).limit(limite)
    return list((await session.execute(q)).scalars())
