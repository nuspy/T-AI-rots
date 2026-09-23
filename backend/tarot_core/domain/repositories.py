"""Accesso ai dati, con l'isolamento fra utenti incorporato.

**Il punto di questo modulo è che il filtro per proprietario non sia opzionale.**
Un endpoint che chiede «la lettura con questo id» non può ricevere quella di un
altro utente, e il modo per garantirlo non è ricordarsi la `WHERE` in ogni
router: è non avere, in nessun punto del codice, un metodo che restituisca una
lettura senza sapere di chi la sta cercando.

Per questo i metodi di `ReadingRepository` prendono l'utente come primo
argomento e non hanno alternativa.
"""
from __future__ import annotations

import logging
import secrets
import uuid
from typing import TYPE_CHECKING, Optional, Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import utcnow
from .models import AuditLog, Reading, User

if TYPE_CHECKING:  # pragma: no cover
    # Solo per l'annotazione: importarlo davvero chiuderebbe un anello —
    # `auth` dipende da questo modulo per sincronizzare l'utente.
    from ..auth.keycloak import Principal

logger = logging.getLogger(__name__)

#: Le lettere dei codici invito: niente 0/O e 1/I, che si confondono a voce.
_ALFABETO_INVITI = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def nuovo_codice_invito() -> str:
    return "".join(secrets.choice(_ALFABETO_INVITI) for _ in range(8))


class UserRepository:
    """Gli utenti, sincronizzati da ciò che afferma Keycloak."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_subject(self, subject: str) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(User.keycloak_sub == subject)
        )
        return result.scalar_one_or_none()

    async def ensure(self, principal: "Principal") -> User:
        """L'utente corrispondente al token, creandolo alla prima comparsa.

        Non esiste una «registrazione» separata: chi supera la verifica del
        token ha già un account, e questa riga è solo il posto dove appendere
        le sue letture. Aspettare un passaggio esplicito di creazione
        significherebbe solo un modo in più di trovarsi autenticati e senza
        profilo.

        I campi anagrafici si riallineano a ogni accesso perché la verità su
        email e nome sta in Keycloak: se l'utente li cambia lì, una copia
        locale che non si aggiorna diventa una seconda verità, sbagliata.
        """
        utente = await self.get_by_subject(principal.subject)

        if utente is None:
            utente = User(
                keycloak_sub=principal.subject,
                email=principal.email,
                display_name=principal.display_name,
                locale=principal.locale,
                referral_code=nuovo_codice_invito(),
            )
            self._session.add(utente)
            await self._session.flush()
            logger.info("Primo accesso di %s: utente creato", principal.subject[:8])
            # Marcato e non dedotto da `created_at`: chi chiama deve poter
            # fare qualcosa *una volta sola* alla nascita dell'account —
            # aprire il piano gratuito — e «creato da poco» non è la stessa
            # cosa di «creato adesso da me».
            utente.appena_creato = True
            return utente

        utente.appena_creato = False

        if utente.deleted_at is not None:
            # Riattivare in silenzio nasconderebbe che l'account era stato
            # chiuso. Chi ha il potere di riaprirlo lo fa da console, e resta
            # scritto nel registro.
            raise PermissionError("account disattivato")

        utente.email = principal.email or utente.email
        utente.display_name = principal.display_name or utente.display_name
        utente.locale = principal.locale or utente.locale
        return utente


class ReadingRepository:
    """Le letture di un utente. Ogni metodo parte dal proprietario."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, owner: User, **campi) -> Reading:
        lettura = Reading(owner_id=owner.id, **campi)
        self._session.add(lettura)
        await self._session.flush()
        return lettura

    async def get(self, owner: User, reading_id: uuid.UUID) -> Optional[Reading]:
        return (await self._session.execute(
            select(Reading).where(Reading.id == reading_id, Reading.owner_id == owner.id)
        )).scalar_one_or_none()

    async def get_for_update(self, owner: User, reading_id: uuid.UUID) -> Optional[Reading]:
        """La lettura, bloccata fino al commit.

        Due clic ravvicinati sulla stessa carta arrivano come due richieste:
        senza il lock entrambe troverebbero libera la stessa posizione.
        """
        return (await self._session.execute(
            select(Reading)
            .where(Reading.id == reading_id, Reading.owner_id == owner.id)
            .with_for_update()
        )).scalar_one_or_none()

    async def list_recent(
        self, owner: User, *, limite: int = 50, prima_di: Optional[uuid.UUID] = None,
    ) -> Sequence[Reading]:
        query = (
            select(Reading)
            .where(Reading.owner_id == owner.id)
            .order_by(desc(Reading.created_at))
            .limit(limite)
        )
        return (await self._session.execute(query)).scalars().all()

    async def count(self, owner: User) -> int:
        return int(await self._session.scalar(
            select(func.count()).select_from(Reading).where(Reading.owner_id == owner.id)
        ) or 0)

    async def delete(self, owner: User, reading_id: uuid.UUID) -> bool:
        """Cancella davvero, in cascata. Vero se c'era."""
        lettura = await self.get(owner, reading_id)
        if lettura is None:
            return False
        await self._session.delete(lettura)
        await self._session.flush()
        return True

    async def by_share_token(self, token: str) -> Optional[Reading]:
        """L'unica lettura raggiungibile senza proprietario: quella che
        l'utente ha scelto di condividere, per il token che ha pubblicato."""
        return (await self._session.execute(
            select(Reading).where(Reading.share_token == token)
        )).scalar_one_or_none()


class AuditRepository:
    """Il registro. Solo scrittura e lettura, mai modifica."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        action: str,
        actor_id: Optional[int] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        before: Optional[dict] = None,
        after: Optional[dict] = None,
        ip: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> AuditLog:
        voce = AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            before=before,
            after=after,
            ip=ip,
            correlation_id=correlation_id,
            created_at=utcnow(),
        )
        self._session.add(voce)
        return voce

    async def for_target(
        self, target_type: str, target_id: str, *, limit: int = 100
    ) -> Sequence[AuditLog]:
        result = await self._session.execute(
            select(AuditLog)
            .where(
                AuditLog.target_type == target_type,
                AuditLog.target_id == str(target_id),
            )
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        return result.scalars().all()
