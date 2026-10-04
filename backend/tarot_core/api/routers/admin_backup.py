"""La console del backup sul NAS (v8.3): destinazione, credenziale (v9, Fase 2c: chiave SSH o password, cifrate),
prova del collegamento, backup subito, copie sul NAS, storico, e il ripristino di una copia (con la copia di
sicurezza prima). Solo il ruolo admin.

Backup e ripristino durano secondi o minuti: partono dopo la risposta (`BackgroundTasks`), e la console segue lo
stato (`GET /admin/backup` e `GET /admin/backup/ripristino`).
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...domain.backup_models import BackupEsecuzione
from ...domain.base import utcnow
from ...domain.repositories import AuditRepository
from ...domain.session import get_session_factory
from ...tarot import backup

router = APIRouter(prefix="/admin/backup", tags=["backup"], dependencies=[Depends(require_role("admin"))])

#: La parola da scrivere per confermare un ripristino: il nome del database.
CONFERMA = "tarots"


def _impostazioni_json(r) -> Dict[str, Any]:
    return {
        "attivo": r.attivo, "host": r.host, "porta": r.porta, "utente": r.utente, "cartella": r.cartella,
        "conserva": r.conserva, "impronta_host": r.impronta_host,
    }


@router.get("")
async def stato(session: DbSession) -> Dict[str, Any]:
    riga = await backup.impostazioni(session)
    await session.commit()
    return {
        "impostazioni": _impostazioni_json(riga),
        "credenziale": backup.credenziale(riga),
        "esecuzioni": [backup.esecuzione_json(e) for e in await backup.ultime_esecuzioni(session)],
        "ripristino": backup.stato_json(),
    }


class ImpostazioniIn(BaseModel):
    attivo: bool
    host: str = Field(max_length=255)
    porta: int = Field(ge=1, le=65535)
    utente: str = Field(max_length=120)
    cartella: str = Field(max_length=500)
    conserva: int = Field(ge=1, le=60)


@router.put("/impostazioni")
async def salva_impostazioni(payload: ImpostazioniIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    riga = await backup.impostazioni(session)
    prima = _impostazioni_json(riga)
    host, cartella = payload.host.strip(), payload.cartella.strip()
    if payload.attivo and not (host and payload.utente.strip() and cartella):
        raise HTTPException(status_code=422, detail="Per accendere il backup servono host, utente e cartella.")
    # Un altro NAS è un'altra chiave: quella accettata non vale più.
    if (host, payload.porta) != (riga.host, riga.porta):
        riga.impronta_host = None
    riga.attivo, riga.host, riga.porta = payload.attivo, host, payload.porta
    riga.utente, riga.cartella, riga.conserva = payload.utente.strip(), cartella, payload.conserva
    riga.updated_by = user.id
    await AuditRepository(session).record(
        action="backup.impostazioni", actor_id=user.id, target_type="impostazioni_backup", target_id="1",
        before=prima, after=_impostazioni_json(riga),
    )
    await session.commit()
    return _impostazioni_json(riga)


class CredenzialeIn(BaseModel):
    """La credenziale del NAS dalla console (v9, Fase 2c). Un campo vuoto lascia com'è; `togli` cancella entrambe
    (si torna al Secret montato, se c'è)."""

    chiave_ssh: str = Field(default="", max_length=20_000)
    password: str = Field(default="", max_length=500)
    togli: bool = False


@router.put("/credenziale")
async def salva_credenziale(payload: CredenzialeIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    from ...llm.cifratura import cifra

    riga = await backup.impostazioni(session)
    prima = backup.credenziale(riga)
    campi = []
    if payload.togli:
        riga.chiave_ssh_cifrata = riga.password_cifrata = None
        riga.chiave_ssh_tipo = riga.chiave_ssh_impronta = None
        campi = ["chiave_ssh", "password"]
    else:
        if payload.chiave_ssh.strip():
            try:
                tipo, impronta = backup.descrivi_chiave(payload.chiave_ssh)
            except backup.ErroreBackup as exc:
                raise HTTPException(status_code=422, detail=f"Chiave SSH: {exc}.") from exc
            riga.chiave_ssh_cifrata = cifra(payload.chiave_ssh.strip().replace("\r\n", "\n"))
            riga.chiave_ssh_tipo, riga.chiave_ssh_impronta = tipo, impronta
            campi.append("chiave_ssh")
        if payload.password:
            riga.password_cifrata = cifra(payload.password)
            campi.append("password")
        if not campi:
            raise HTTPException(status_code=422, detail="Scegli un file di chiave, incollala, o scrivi una password.")
    riga.updated_by = user.id
    # Nell'audit solo quali campi e l'impronta pubblica della chiave: mai la chiave né la password.
    await AuditRepository(session).record(
        action="backup.credenziale", actor_id=user.id, target_type="impostazioni_backup", target_id="1",
        before={"origine": prima["origine"], "chiave_impronta": prima["chiave_impronta"]},
        after={"campi": campi, "tolta": payload.togli, "chiave_impronta": riga.chiave_ssh_impronta},
    )
    await session.commit()
    return backup.credenziale(riga)


class ProvaIn(BaseModel):
    #: Vero: se il collegamento riesce, la chiave dell'host vista adesso diventa quella accettata.
    fidati: bool = False


@router.post("/prova")
async def prova(payload: ProvaIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    riga = await backup.impostazioni(session)
    dest = backup.destinazione_di(riga)
    esecuzione = BackupEsecuzione(tipo="prova", manuale=True, actor_id=user.id)
    try:
        esito = await asyncio.to_thread(backup.prova_collegamento, dest)
    except backup.ErroreBackup as exc:
        esecuzione.esito, esecuzione.dettaglio, esecuzione.finita_il = "errore", str(exc), utcnow()
        session.add(esecuzione)
        await session.commit()
        return {"riuscita": False, "dettaglio": str(exc)}
    if payload.fidati and not esito["accettata"]:
        prima = riga.impronta_host
        riga.impronta_host = esito["impronta"]
        esito["accettata"] = True
        await AuditRepository(session).record(
            action="backup.chiave_host", actor_id=user.id, target_type="impostazioni_backup", target_id="1",
            before={"impronta_host": prima}, after={"impronta_host": esito["impronta"]},
        )
    esecuzione.esito, esecuzione.finita_il = "ok", utcnow()
    esecuzione.dettaglio = f"collegamento e scrittura riusciti in {esito['millisecondi']} ms; chiave {esito['impronta']}"
    session.add(esecuzione)
    await session.commit()
    return {"riuscita": True, **esito}


@router.post("/esegui", status_code=status.HTTP_202_ACCEPTED)
async def esegui_ora(
    user: CurrentUser, compiti: BackgroundTasks, fabbrica=Depends(get_session_factory),
) -> Dict[str, Any]:
    """Un backup subito, anche se quello notturno è spento. Parte dopo la risposta: lo storico ne mostra l'esito."""
    compiti.add_task(backup.esegui_backup, fabbrica, manuale=True, actor_id=user.id)
    return {"avviato": True}


@router.get("/copie")
async def copie(session: DbSession) -> Dict[str, Any]:
    dest = backup.destinazione_di(await backup.impostazioni(session))
    await session.commit()
    try:
        elenco = await asyncio.to_thread(backup.elenco_copie, dest)
    except backup.ErroreBackup as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"copie": [
        {"nome": c.nome, "byte": c.byte, "data": c.modificata.isoformat(), "sicurezza": c.sicurezza, "con_sha256": c.con_sha256}
        for c in elenco
    ]}


class RipristinoIn(BaseModel):
    file: str = Field(max_length=255)
    #: Il nome del database, scritto a mano: un ripristino si fa sapendo cosa si fa.
    conferma: str


@router.post("/ripristina", status_code=status.HTTP_202_ACCEPTED)
async def ripristina(
    payload: RipristinoIn, user: CurrentUser, session: DbSession, compiti: BackgroundTasks,
    fabbrica=Depends(get_session_factory),
) -> Dict[str, Any]:
    if payload.conferma.strip() != CONFERMA:
        raise HTTPException(status_code=422, detail=f"Per confermare scrivi «{CONFERMA}».")
    if not backup.NOME_COPIA.match(payload.file):
        raise HTTPException(status_code=422, detail="Nome di copia non valido.")
    if backup.STATO.in_corso:
        raise HTTPException(status_code=409, detail="C'è già un ripristino in corso.")
    await AuditRepository(session).record(
        action="backup.ripristino_avviato", actor_id=user.id, target_type="database", target_id=payload.file,
    )
    await session.commit()
    compiti.add_task(_ripristina, fabbrica, payload.file, user.id)
    return {"avviato": True, "file": payload.file}


async def _ripristina(fabbrica, nome: str, actor_id: int) -> None:
    try:
        await backup.ripristina(fabbrica, nome, actor_id=actor_id)
    except backup.ErroreBackup:
        pass  # già nello stato e nel registro


@router.get("/ripristino")
async def stato_ripristino() -> Dict[str, Any]:
    return backup.stato_json()
