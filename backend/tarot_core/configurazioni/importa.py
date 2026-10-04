"""La copia una tantum dall'ambiente del server al database, al primo avvio (v9, Fase 2c).

Prima della Fase 2c la posta, le chiavi di Stripe, il fornitore di pagamento e la credenziale del NAS stavano
nell'ambiente (Secret di Kubernetes). Perché l'operatore non debba riscriverle in console — la password della posta
non la conosce nemmeno («compila tu», 3/10) — l'API, partendo, le copia nel database **una volta sola**, cifrate:

- solo se in database quella configurazione è **vuota** e l'ambiente ha il valore;
- una voce copiata (o trovata già piena) si segna in `importazioni_ambiente` e non si ricopia più: da lì vale la
  console, anche se poi l'operatore la svuota;
- ogni copia si scrive nell'audit («importato dall'ambiente»), mai con i valori;
- con più repliche che partono insieme: un lock di transazione di PostgreSQL (`pg_advisory_xact_lock`) mette in fila
  le importazioni, e la chiave primaria di `importazioni_ambiente` impedisce comunque una seconda copia.
"""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings import Settings, get_settings

logger = logging.getLogger(__name__)

#: La chiave del lock di PostgreSQL che mette in fila le importazioni di più repliche (un numero qualunque, fisso).
LOCK_IMPORTAZIONE = 720261018


async def _gia_fatta(session: AsyncSession, voce: str) -> bool:
    from ..domain.configurazioni_models import ImportazioneAmbiente

    return await session.get(ImportazioneAmbiente, voce) is not None


async def _segna(session: AsyncSession, voce: str, esito: str) -> bool:
    """Segna la voce; `False` se qualcun altro l'ha già segnata (allora non si copia niente)."""
    from ..domain.configurazioni_models import ImportazioneAmbiente

    risultato = await session.execute(
        insert(ImportazioneAmbiente).values(voce=voce, esito=esito)
        .on_conflict_do_nothing(index_elements=["voce"]).returning(ImportazioneAmbiente.voce)
    )
    return risultato.scalar_one_or_none() is not None


async def _audit(session: AsyncSession, voce: str, campi: List[str]) -> None:
    from ..domain.repositories import AuditRepository

    await AuditRepository(session).record(
        action="configurazioni.importato_dall_ambiente", target_type="configurazione", target_id=voce,
        after={"campi": campi, "nota": "importato dall'ambiente al primo avvio"},
    )


async def _smtp(session: AsyncSession, s: Settings) -> Optional[str]:
    from ..domain.configurazioni_models import ConfigSmtp
    from ..llm.cifratura import cifra

    if await _gia_fatta(session, "smtp") or not s.smtp_host.strip():
        return None
    riga = await session.get(ConfigSmtp, 1)
    if riga is not None and riga.host.strip():
        await _segna(session, "smtp", "gia_in_console")
        return None
    if not await _segna(session, "smtp", "importato"):
        return None
    if riga is None:
        riga = ConfigSmtp(id=1)
        session.add(riga)
    riga.host, riga.porta, riga.sicurezza = s.smtp_host.strip(), s.smtp_porta, "ssl" if s.smtp_ssl else "starttls"
    riga.utente, riga.mittente = s.smtp_utente, s.smtp_mittente
    riga.password_cifrata = cifra(s.smtp_password)
    campi = ["host", "porta", "sicurezza", "utente", "mittente"] + (["password"] if s.smtp_password else [])
    await _audit(session, "smtp", campi)
    return "smtp"


async def _stripe_chiavi(session: AsyncSession, s: Settings) -> Optional[str]:
    from ..domain.configurazioni_models import ConfigStripe
    from ..llm.cifratura import cifra
    from .correnti import modalita_della_chiave

    if await _gia_fatta(session, "stripe_chiavi") or not s.stripe_secret_key.strip():
        return None
    riga = await session.get(ConfigStripe, 1)
    if riga is not None and riga.chiave_segreta_cifrata:
        await _segna(session, "stripe_chiavi", "gia_in_console")
        return None
    if not await _segna(session, "stripe_chiavi", "importato"):
        return None
    if riga is None:
        riga = ConfigStripe(id=1)
        session.add(riga)
    chiave = s.stripe_secret_key.strip()
    riga.chiave_segreta_cifrata = cifra(chiave)
    riga.modalita = modalita_della_chiave(chiave)
    riga.segreto_webhook_cifrato = cifra(s.stripe_webhook_secret)
    await _audit(session, "stripe_chiavi", ["chiave_segreta"] + (["segreto_webhook"] if s.stripe_webhook_secret else []))
    return "stripe_chiavi"


async def _stripe_provider(session: AsyncSession, s: Settings) -> Optional[str]:
    from ..domain.configurazioni_models import ConfigStripe

    # Solo un fornitore scritto davvero nell'ambiente (non il predefinito di sviluppo), e mai il simulatore in
    # produzione.
    if "billing_provider" not in s.model_fields_set or await _gia_fatta(session, "stripe_provider"):
        return None
    if s.billing_provider not in ("disattivato", "mock", "stripe") or (s.billing_provider == "mock" and s.environment == "prod"):
        return None
    riga = await session.get(ConfigStripe, 1)
    if riga is not None and riga.provider:
        await _segna(session, "stripe_provider", "gia_in_console")
        return None
    if not await _segna(session, "stripe_provider", "importato"):
        return None
    if riga is None:
        riga = ConfigStripe(id=1)
        session.add(riga)
    riga.provider = s.billing_provider
    await _audit(session, "stripe_provider", ["provider"])
    return "stripe_provider"


async def _backup(session: AsyncSession, s: Settings) -> Optional[str]:
    from ..llm.cifratura import cifra
    from ..tarot import backup

    if await _gia_fatta(session, "backup_credenziale"):
        return None
    chiave: Optional[str] = None
    if s.backup_chiave_ssh and os.path.isfile(s.backup_chiave_ssh):
        try:
            with open(s.backup_chiave_ssh, encoding="utf-8") as f:
                chiave = f.read().strip() or None
        except (OSError, UnicodeDecodeError) as exc:
            logger.warning("La chiave SSH del backup montata non si legge (%s): non si importa", type(exc).__name__)
    password = s.backup_password or None
    if not (chiave or password):
        return None
    riga = await backup.impostazioni(session)
    if riga.chiave_ssh_cifrata or riga.password_cifrata:
        await _segna(session, "backup_credenziale", "gia_in_console")
        return None
    descrizione = None
    if chiave:
        try:
            descrizione = backup.descrivi_chiave(chiave)
        except backup.ErroreBackup as exc:
            logger.warning("La chiave SSH del backup montata non è valida (%s): non si importa", exc)
            chiave = None
    if not (chiave or password):
        return None
    if not await _segna(session, "backup_credenziale", "importato"):
        return None
    campi: List[str] = []
    if chiave and descrizione:
        riga.chiave_ssh_cifrata = cifra(chiave)
        riga.chiave_ssh_tipo, riga.chiave_ssh_impronta = descrizione
        campi.append("chiave_ssh")
    if password:
        riga.password_cifrata = cifra(password)
        campi.append("password")
    await _audit(session, "backup_credenziale", campi)
    return "backup_credenziale"


async def dall_ambiente(session: AsyncSession, settings: Optional[Settings] = None) -> List[str]:
    """Copia ciò che serve; restituisce le voci copiate. Non fa il commit (lo fa chi chiama, e libera il lock)."""
    s = settings or get_settings()
    await session.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": LOCK_IMPORTAZIONE})
    copiate: List[str] = []
    passi: Dict[str, object] = {
        "smtp": _smtp, "stripe_chiavi": _stripe_chiavi, "stripe_provider": _stripe_provider, "backup": _backup,
    }
    for nome, passo in passi.items():
        try:
            async with session.begin_nested():
                voce = await passo(session, s)  # type: ignore[operator]
        except Exception:  # noqa: BLE001 — una voce che non si importa non deve fermare l'avvio dell'API
            logger.exception("Importazione dall'ambiente di «%s» non riuscita", nome)
            continue
        if voce:
            copiate.append(voce)
            logger.info("Configurazione «%s» importata dall'ambiente nel database (da ora vale la console)", voce)
    return copiate
