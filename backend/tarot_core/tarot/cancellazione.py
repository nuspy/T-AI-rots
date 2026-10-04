"""La cancellazione dell'account chiesta dalla persona (GDPR art. 17; Google Play e Apple la esigono).

**Tre momenti.**

1. **La richiesta** (`POST /me/cancellazione`, con una riconferma esplicita): da subito l'account è chiuso —
   `deleted_at` e `cancellazione_richiesta_il` — e le sessioni in Keycloak si chiudono (`KeycloakAdmin.chiudi_sessioni`:
   le sessioni del browser e i token offline del sito e della console). L'utente in Keycloak **non** si cancella e
   non si disattiva ancora: è ciò che permette di ripensarci.
2. **Il ripensamento** (30 giorni, `GIORNI_RIPENSAMENTO`): chi rientra con le stesse credenziali trova l'account
   «in cancellazione» (`UserRepository.ensure` → `User.in_cancellazione`; ogni endpoint normale risponde 409
   `account_in_cancellazione`) e può annullarla (`POST /me/cancellazione/annulla`) o scaricare i suoi dati. Annullare
   riapre l'account esattamente com'era: niente è stato ancora toccato.
3. **L'esecuzione** (`esegui()`, dal CronJob notturno `tarots-cancellazioni` → `tools/cancellazioni.py`, o a mano
   dalla console «Conservazione dati»): l'utente in Keycloak si cancella e i dati personali con lui.

**Cosa si cancella e cosa resta.** Si cancellano le letture (con colloquio, carte e immagini di condivisione), le
memorie, la chat, le carte del giorno, i consensi correnti, gli indirizzi, l'avatar, i temi suggeriti per i mazzi; le
statistiche perdono il legame con l'account (come con l'opposizione, `lanterna.eventi.imposta_opposizione`). Resta
la **contabilità** — registro dei crediti, abbonamenti, pagamenti, ordini, coupon usati, mazzi sbloccati — che la
legge chiede di conservare (in Italia dieci anni, art. 2220 c.c.): la riga utente non si cancella ma si
**pseudonimizza** con la stessa tecnica di `unione_account.separa()` (una `keycloak_sub` che non corrisponde più a
nessuno, ogni campo anagrafico vuoto). Degli ordini resta il paese di spedizione (serve all'IVA), non l'indirizzo.
Restano anche il registro (`audit_log`, con gli IP già troncati) e lo storico dei consensi: sono la prova di ciò che è
stato fatto, legati ormai solo allo pseudonimo.

**Apple.** Chi è entrato con «Accedi con Apple» dovrebbe vedere revocato anche il token presso Apple
(`appleid.apple.com/auth/revoke`), come chiedono le regole dell'App Store: arriva con l'accesso nativo (Fase 6).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.chat_models import ChatProattivaTurno
from ..domain.consent_models import UserConsent
from ..domain.memory_models import MemoriaStato, UserMemory
from ..domain.models import DailyCard, Reading, User
from ..domain.ordini_models import IndirizzoSpedizione, Ordine
from ..domain.repositories import AuditRepository
from ..domain.voting_models import DeckSuggestion
from .lingue import in_lingua

logger = logging.getLogger(__name__)

#: I giorni in cui la cancellazione si può ancora annullare.
GIORNI_RIPENSAMENTO = 30

#: Il prefisso della `keycloak_sub` di un account cancellato: non corrisponde più a nessun utente di Keycloak (come
#: `unione_account.PREFISSO_SEPARATO`).
PREFISSO_CANCELLATO = "cancellato:"

IN_CANCELLAZIONE = {
    "it": "Hai chiesto di cancellare questo account. Puoi ancora annullare la richiesta fino al {data}.",
    "en": "You asked to delete this account. You can still cancel the request until {data}.",
    "hu": "Kérted a fiók törlését. A kérést {data}-ig még visszavonhatod.",
    "ru": "Ты попросил удалить этот аккаунт. Ты ещё можешь отменить запрос до {data}.",
    "uk": "Ти попросив видалити цей акаунт. Ти ще можеш скасувати запит до {data}.",
    "es": "Pediste eliminar esta cuenta. Todavía puedes anular la solicitud hasta el {data}.",
}


def definitiva_il(user: User) -> Optional[datetime]:
    """Da quando la cancellazione non si può più annullare."""
    if user.cancellazione_richiesta_il is None:
        return None
    return user.cancellazione_richiesta_il + timedelta(days=GIORNI_RIPENSAMENTO)


def stato_json(user: User) -> Dict[str, Any]:
    fine = definitiva_il(user)
    return {
        "richiesta_il": user.cancellazione_richiesta_il.isoformat() if user.cancellazione_richiesta_il else None,
        "definitiva_il": fine.isoformat() if fine else None,
        "eseguita_il": user.cancellazione_eseguita_il.isoformat() if user.cancellazione_eseguita_il else None,
        "annullabile": bool(fine) and user.cancellazione_eseguita_il is None,
        "giorni_ripensamento": GIORNI_RIPENSAMENTO,
    }


def dettaglio_in_cancellazione(user: User) -> Dict[str, Any]:
    """Il corpo del 409 che ricevono gli endpoint normali durante il ripensamento."""
    fine = definitiva_il(user)
    data = fine.date().isoformat() if fine else ""
    return {
        "motivo": "account_in_cancellazione",
        "messaggio": in_lingua(IN_CANCELLAZIONE, user.locale or "it").replace("{data}", data),
        **stato_json(user),
    }


async def richiedi(session: AsyncSession, user: User, *, ip: Optional[str], keycloak: Any) -> Dict[str, Any]:
    """Chiude l'account adesso e apre i 30 giorni di ripensamento. Non fa commit: lo fa chi chiama.

    Le sessioni Keycloak si chiudono qui; se Keycloak non risponde la richiesta vale lo stesso (l'account è comunque
    chiuso per questo sito: ogni token ancora vivo trova la riga «in cancellazione»), e l'esito lo dice."""
    adesso = utcnow()
    user.deleted_at = adesso
    user.cancellazione_richiesta_il = adesso
    user.cancellazione_eseguita_il = None
    sessioni_chiuse = await _chiudi_sessioni(keycloak, user.keycloak_sub)
    await AuditRepository(session).record(
        action="account.cancellazione_richiesta", actor_id=user.id, target_type="user", target_id=str(user.id),
        after={"definitiva_il": definitiva_il(user).isoformat(), "sessioni_chiuse": sessioni_chiuse},
        ip=ip,
    )
    return {**stato_json(user), "sessioni_chiuse": sessioni_chiuse}


async def annulla(session: AsyncSession, user: User, *, ip: Optional[str]) -> Dict[str, Any]:
    """Riapre l'account: nei 30 giorni niente è stato toccato, quindi torna com'era."""
    if user.cancellazione_richiesta_il is None or user.cancellazione_eseguita_il is not None:
        raise ValueError("nessuna cancellazione da annullare")
    richiesta = user.cancellazione_richiesta_il
    user.deleted_at = None
    user.cancellazione_richiesta_il = None
    user.in_cancellazione = False
    await AuditRepository(session).record(
        action="account.cancellazione_annullata", actor_id=user.id, target_type="user", target_id=str(user.id),
        before={"richiesta_il": richiesta.isoformat()}, ip=ip,
    )
    return stato_json(user)


async def _chiudi_sessioni(keycloak: Any, sub: str) -> bool:
    if keycloak is None or sub.startswith((PREFISSO_CANCELLATO, "separato:", "dev-")):
        return False
    try:
        await keycloak.chiudi_sessioni(sub)
        return True
    except Exception:  # noqa: BLE001 - la richiesta di cancellazione vale anche se Keycloak non risponde
        logger.warning("Sessioni Keycloak non chiuse per la cancellazione di %s", sub[:8], exc_info=True)
        return False


async def da_eseguire(session: AsyncSession, *, adesso: Optional[datetime] = None) -> List[User]:
    """Gli account il cui ripensamento è finito e che non sono ancora stati cancellati."""
    limite = (adesso or utcnow()) - timedelta(days=GIORNI_RIPENSAMENTO)
    return list((await session.execute(
        select(User)
        .where(
            User.cancellazione_richiesta_il.is_not(None),
            User.cancellazione_richiesta_il <= limite,
            User.cancellazione_eseguita_il.is_(None),
        )
        .order_by(User.cancellazione_richiesta_il)
    )).scalars())


async def esegui(
    session: AsyncSession, user: User, *, keycloak: Any, attore_id: Optional[int] = None, motivo: str = "scadenza",
) -> Dict[str, Any]:
    """Cancella l'utente in Keycloak e i dati personali, e pseudonimizza ciò che la contabilità deve tenere. Non fa
    commit: lo fa chi chiama, così un errore a metà non lascia un account mezzo cancellato.

    Se Keycloak non si raggiunge solleva prima di toccare il database: si riproverà al giro dopo (un utente cancellato
    qui ma vivo in Keycloak potrebbe rientrare e ritrovarsi un account nuovo e vuoto, senza sapere perché).
    `motivo`: `scadenza` (il CronJob) o `console` (a mano, da «Conservazione dati")."""
    sub = user.keycloak_sub
    if keycloak is not None and not sub.startswith((PREFISSO_CANCELLATO, "separato:", "dev-")):
        await keycloak.cancella_utente(sub)
        # TODO(Fase 6): chi è entrato con «Accedi con Apple» va anche revocato presso Apple
        # (POST https://appleid.apple.com/auth/revoke con il refresh token dell'identità Apple e il client secret
        # JWT del Services ID): Keycloak non lo fa da solo cancellando l'utente. Serve l'accesso nativo della Fase 6
        # (estensione Apple di Keycloak, `tarot/collega_identita.py`) per avere il token da revocare.

    conteggi: Dict[str, int] = {}

    async def via(nome: str, stmt) -> None:
        esito = await session.execute(stmt)
        conteggi[nome] = int(esito.rowcount or 0)

    uid = user.id
    # L'avatar si stacca dalla riga prima di cancellare le immagini (la FK è `SET NULL`, ma così l'ordine è esplicito).
    user.avatar_id = None
    await session.flush()
    from ..domain.blog_models import MediaImage

    await via("letture", delete(Reading).where(Reading.owner_id == uid))
    await via("memorie", delete(UserMemory).where(UserMemory.owner_id == uid))
    await via("stato_memoria", delete(MemoriaStato).where(MemoriaStato.user_id == uid))
    await via("chat", delete(ChatProattivaTurno).where(ChatProattivaTurno.owner_id == uid))
    await via("carte_del_giorno", delete(DailyCard).where(DailyCard.user_id == uid))
    await via("consensi_correnti", delete(UserConsent).where(UserConsent.user_id == uid))
    await via("indirizzi", delete(IndirizzoSpedizione).where(IndirizzoSpedizione.user_id == uid))
    await via("temi_suggeriti", delete(DeckSuggestion).where(DeckSuggestion.user_id == uid))
    await via("immagini", delete(MediaImage).where(MediaImage.owner_id == uid, MediaImage.uso == "avatar"))
    # v9, Fase 5: i dispositivi delle notifiche, le preferenze e il registro degli invii.
    from ..domain.notifiche_models import DispositivoNotifica, InvioNotifica, PreferenzeNotifica

    await via("notifiche_invii", delete(InvioNotifica).where(InvioNotifica.user_id == uid))
    await via("notifiche_dispositivi", delete(DispositivoNotifica).where(DispositivoNotifica.user_id == uid))
    await via("notifiche_preferenze", delete(PreferenzeNotifica).where(PreferenzeNotifica.user_id == uid))
    user.fuso_orario = None

    # Degli ordini resta ciò che serve alla contabilità e all'IVA (importi, righe, paese), non l'indirizzo.
    ordini = (await session.execute(select(Ordine).where(Ordine.user_id == uid))).scalars().all()
    for ordine in ordini:
        if ordine.indirizzo_spedizione:
            ordine.indirizzo_spedizione = {"paese": (ordine.indirizzo_spedizione or {}).get("paese"), "rimosso": True}
    conteggi["ordini_pseudonimizzati"] = len(ordini)

    # Le statistiche: le visite e gli eventi perdono il legame con l'account, il primo contatto si cancella.
    try:
        from lanterna.eventi import imposta_opposizione

        from ..domain.analytics_models import TABELLE

        async with session.begin_nested():
            await imposta_opposizione(session, TABELLE, uid, True)
    except Exception:  # noqa: BLE001 - le statistiche non devono impedire la cancellazione dei dati veri
        logger.warning("Statistiche non scollegate dall'account %s", uid, exc_info=True)

    # La riga resta, svuotata: tiene insieme la contabilità con uno pseudonimo che non porta a nessuno.
    user.keycloak_sub = f"{PREFISSO_CANCELLATO}{uuid.uuid4().hex}"
    for campo in (
        "email", "display_name", "birth_date", "gender", "gender_custom", "nome_pubblico", "partner_ricordato",
        "referral_code", "nome", "cognome", "posizione_paese", "posizione_citta", "posizione_fonte", "posizione_il",
        "dati_social", "unione_in_attesa", "unione_risolta", "mazzo_predefinito_id", "eta_confermata_il",
        "eta_confermata_anni",
    ):
        setattr(user, campo, None)
    user.is_trans = False
    user.importa_social = False
    user.rileva_posizione = False
    adesso = utcnow()
    user.deleted_at = user.deleted_at or adesso
    user.cancellazione_richiesta_il = user.cancellazione_richiesta_il or adesso
    user.cancellazione_eseguita_il = adesso
    user.in_cancellazione = False

    await AuditRepository(session).record(
        action="account.cancellazione_eseguita", actor_id=attore_id, target_type="user", target_id=str(uid),
        after={"motivo": motivo, "conteggi": conteggi},
    )
    return conteggi


async def esegui_scadute(session_factory, keycloak: Any, *, adesso: Optional[datetime] = None) -> Dict[str, Any]:
    """Il giro notturno: ogni account scaduto in una transazione sua, così un errore su uno non ferma gli altri."""
    eseguite: List[int] = []
    fallite: List[int] = []
    async with session_factory() as sessione:
        ids = [u.id for u in await da_eseguire(sessione, adesso=adesso)]
    for uid in ids:
        async with session_factory() as sessione:
            user = await sessione.get(User, uid)
            if user is None or user.cancellazione_eseguita_il is not None:
                continue
            try:
                await esegui(sessione, user, keycloak=keycloak)
                await sessione.commit()
                eseguite.append(uid)
            except Exception:  # noqa: BLE001 - si riprova al prossimo giro; il motivo resta nei log
                await sessione.rollback()
                logger.exception("Cancellazione dell'account %s non riuscita", uid)
                fallite.append(uid)
    return {"eseguite": eseguite, "fallite": fallite}
