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

from sqlalchemy import desc, func, or_, select
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


def _lingua_del_sito(codice: Optional[str]) -> Optional[str]:
    """Il claim `locale` come lingua del sito (`tarot/lingue.py`): «pt-BR» → «pt»; una lingua che il sito non ha →
    `None` (resta quella di prima). Keycloak offre le stesse lingue, ma un attributo si può scrivere a mano."""
    from ..tarot.lingue import LINGUE

    base = (codice or "").strip().lower().replace("_", "-").split("-")[0]
    return base if base in LINGUE else None


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
                locale=_lingua_del_sito(principal.locale) or "it",
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
        utente.in_cancellazione = False

        if (
            utente.deleted_at is not None
            and utente.cancellazione_richiesta_il is not None
            and utente.cancellazione_eseguita_il is None
        ):
            # La cancellazione chiesta dalla persona, nei 30 giorni di ripensamento (`tarot/cancellazione.py`): può
            # rientrare, ma solo per annullarla (o scaricare i suoi dati). Lo decide `current_user`; qui non si
            # riallinea niente, l'account resta com'era quando l'ha chiusa.
            utente.in_cancellazione = True
            return utente

        if utente.deleted_at is not None:
            # Riattivare in silenzio nasconderebbe che l'account era stato
            # chiuso. Chi ha il potere di riaprirlo lo fa da console, e resta
            # scritto nel registro.
            raise PermissionError("account disattivato")

        utente.email = principal.email or utente.email
        utente.display_name = principal.display_name or utente.display_name
        # La lingua solo se il token la porta davvero (l'attributo `locale` dell'utente in Keycloak): senza, il
        # `Principal` ripiega su «it», e riscriverla a ogni accesso cancellerebbe quella presa dal social o scelta
        # dal profilo. Un `Principal` costruito a mano (sviluppo, test) non ha claim e vale com'è.
        # v9, Fase 2d: e **solo finché la persona non ha scelto dal sito** (menu o profilo, `locale_scelta_il`). Il
        # claim è la lingua della pagina di accesso del giorno della registrazione: riscriverla a ogni richiesta
        # annullerebbe la scelta del menu alla richiesta dopo, e oracolo ed email tornerebbero nella lingua vecchia.
        if utente.locale_scelta_il is None:
            locale_token = principal.raw_claims.get("locale") if principal.raw_claims else principal.locale
            utente.locale = _lingua_del_sito(locale_token) or utente.locale
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

    async def get_flex(
        self, reading_id: uuid.UUID, *, owner: Optional[User], anon_id: Optional[str], lock: bool = False,
    ) -> Optional[Reading]:
        """Come `get`/`get_for_update`, ma per gli endpoint condivisi fra utenti autenticati e
        visitatori anonimi (v6, Fase F): questa lettura è mia se `owner_id` combacia, oppure se non
        ha ancora un proprietario e il suo `anon_id` combacia col cookie di chi chiede.

        Dopo il reclamo alla registrazione `owner_id` non è più nullo: da lì in poi solo la prima
        condizione vale, e il vecchio cookie anonimo smette di dare accesso — corretto, perché la
        lettura è ormai di un utente e passa dal percorso normale.
        """
        condizioni = []
        if owner is not None:
            condizioni.append(Reading.owner_id == owner.id)
        if anon_id:
            condizioni.append((Reading.owner_id.is_(None)) & (Reading.anon_id == anon_id))
        if not condizioni:
            return None
        query = select(Reading).where(Reading.id == reading_id, or_(*condizioni))
        if lock:
            query = query.with_for_update()
        return (await self._session.execute(query)).scalar_one_or_none()

    async def reclama_anonima(self, anon_id: str, owner: User) -> Optional[Reading]:
        """Alla prima registrazione (`current_user()`, `appena_creato`): se il cookie corrisponde a
        una lettura ancora senza proprietario, la assegna. Non rigenera nulla: la sintesi, se già
        c'era, resta quella già calcolata — il client la rilegge per intero dopo la registrazione."""
        lettura = (await self._session.execute(
            select(Reading).where(Reading.anon_id == anon_id, Reading.owner_id.is_(None))
        )).scalar_one_or_none()
        if lettura is not None:
            lettura.owner_id = owner.id
        return lettura

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
        # L'indirizzo non entra mai in chiaro (GDPR, Fase 1): la rete troncata e l'impronta HMAC dell'intero.
        from ..tarot.ip_protetto import proteggi

        ip, ip_hash = proteggi(ip)
        voce = AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            before=before,
            after=after,
            ip=ip,
            ip_hash=ip_hash,
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
