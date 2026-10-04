"""Collegare un accesso social all'account che la persona ha già (v9, Fase 6).

Il problema. Su iPhone si entra solo con Apple, su Android solo con Google; l'unione per email (passo
`tarots-unione-sicura`) ritrova l'account del sito quando l'email è la stessa. Con «Nascondi la mia email» Apple dà un
indirizzo `…@privaterelay.appleid.com` che non corrisponde a niente: al primo accesso dall'iPhone nasce un account
nuovo e vuoto, e la storia della persona resta sull'altro. Due rimedi:

**a) «Collega il tuo Apple ID» (o Google) dal profilo del sito**, prima di entrare dall'app. È il *client-initiated
account linking* di Keycloak (`/realms/{realm}/broker/{alias}/link`), che Keycloak 26.0 supporta: il sito apre
quell'indirizzo, la persona entra con Apple e Keycloak collega l'identità all'utente della sessione. Verificato su un
Keycloak 26.0.8: collega e torna al sito; senza la sessione di Keycloak nel browser torna con
`link_error=not_logged_in`; un'identità già di un altro utente si ferma su una pagina d'errore di Keycloak (il tema ne
spiega il rimedio). L'azione `kc_action=idp_link` non esiste ancora in 26.0 (Keycloak risponde 400), e la «console
dell'account» farebbe uscire la persona dal sito. Il collegamento vuole:

- un `hash` = base64url(SHA-256(nonce + id della sessione + client + alias)), che il backend calcola dal claim `sid`
  del token (`url_collegamento`);
- la sessione di Keycloak **nel browser** con lo stesso id: per questo il sito, prima, rifà un passaggio da Keycloak
  (istantaneo se la sessione c'è) e solo al ritorno chiede l'indirizzo;
- il ruolo `manage-account` (o `manage-account-links`) del client `account`, che i ruoli predefiniti del realm danno
  a tutti.

**b) Il codice monouso**, quando l'account nell'app è già nato: l'app lo mostra («Hai già un account sul sito?») e la
persona lo scrive nel profilo del sito, dentro l'account vecchio. Allora (`usa_codice`):

1. le identità social dell'account nuovo passano in Keycloak all'account vecchio (prima tolte, poi aggiunte: Keycloak
   non ammette due utenti con la stessa identità; a metà strada un errore rimette tutto com'era);
2. ciò che l'account nuovo aveva già (letture, memorie, crediti, ordini, mazzi, dispositivi…) passa al vecchio;
3. l'account nuovo si **separa** come in `unione_account.separa()` (riga disattivata, mai cancellata) e in Keycloak
   si chiudono le sue sessioni e lo si disattiva: l'app, al prossimo rinnovo, rientra con Apple e trova l'account vecchio.

Lo stesso codice serve a chi passa dall'iPhone ad Android (o viceversa): l'account nato con Google nell'app consegna
Google all'account nato con Apple, e da lì entrambi i pulsanti portano allo stesso posto.

**Sicurezza.** Servono entrambe le sessioni: chi crea il codice è dentro l'account che cede le identità, chi lo usa è
dentro quello che le riceve. Il codice ha 8 caratteri da un alfabeto di 32 (40 bit), vale 10 minuti, una volta sola,
e del database se ne salva solo l'impronta; i tentativi sbagliati sono al massimo `TENTATIVI_ORA` all'ora per account.
"""
from __future__ import annotations

import base64
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError
from ..domain.accesso_nativo_models import CodiceCollegamento
from ..domain.base import utcnow
from ..domain.models import AuditLog, Reading, User
from . import unione_account

#: Senza I, O, 0 e 1: si confondono quando si ricopiano a mano dal telefono.
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
LUNGHEZZA = 8
VALIDITA = timedelta(minutes=10)
TENTATIVI_ORA = 10
#: I social che il profilo propone di collegare: quelli delle app (Google su Android, Apple su iOS).
COLLEGABILI = ("google", "apple")


class ErroreCollegamento(Exception):
    """`motivo`: la chiave che il sito traduce; `stato`: il codice HTTP."""

    def __init__(self, motivo: str, stato: int, **dettagli: Any) -> None:
        super().__init__(motivo)
        self.motivo = motivo
        self.stato = stato
        self.dettagli = dettagli


# ---- a) il collegamento avviato dal sito ---------------------------------------------------------------------------


def url_collegamento(
    *, base_keycloak: str, realm: str, alias: str, client_id: str, sessione: str, ritorno: str,
    nonce: Optional[str] = None,
) -> str:
    """L'indirizzo del *client-initiated account linking* di Keycloak: il browser ci va con la sua sessione."""
    nonce = nonce or str(uuid.uuid4())
    impronta = hashlib.sha256(f"{nonce}{sessione}{client_id}{alias}".encode("utf-8")).digest()
    return f"{base_keycloak.rstrip('/')}/realms/{realm}/broker/{alias}/link?" + urlencode({
        "client_id": client_id, "redirect_uri": ritorno, "nonce": nonce,
        "hash": base64.urlsafe_b64encode(impronta).rstrip(b"=").decode("ascii"),
    })


# ---- b) il codice monouso -------------------------------------------------------------------------------------------


def normalizza(codice: str) -> str:
    return "".join(c for c in (codice or "").upper() if c.isalnum())


def impronta(codice: str) -> str:
    return hashlib.sha256(normalizza(codice).encode("ascii", "ignore")).hexdigest()


def nuovo_codice() -> str:
    return "".join(secrets.choice(ALFABETO) for _ in range(LUNGHEZZA))


def mostrato(codice: str) -> str:
    """`ABCD-EFGH`: due gruppi si ricopiano meglio di otto lettere di fila."""
    return f"{codice[:4]}-{codice[4:]}"


async def crea_codice(session: AsyncSession, kc: KeycloakAdmin, user: User, sub: str) -> Dict[str, Any]:
    """Un codice nuovo per l'account `user` (quello che cederà le sue identità). I codici non usati di prima non
    valgono più. Senza un'identità social da cedere non c'è niente da spostare: 409."""
    identita = await kc.identita_federate(sub)
    if not identita:
        raise ErroreCollegamento("nessuna_identita", 409)
    await session.execute(delete(CodiceCollegamento).where(
        CodiceCollegamento.user_id == user.id, CodiceCollegamento.usato_il.is_(None),
    ))
    codice = nuovo_codice()
    ora = utcnow()
    session.add(CodiceCollegamento(user_id=user.id, impronta=impronta(codice), creato_il=ora, scade_il=ora + VALIDITA))
    await session.flush()
    return {
        "codice": mostrato(codice), "scade_il": (ora + VALIDITA).isoformat(),
        "validita_minuti": int(VALIDITA.total_seconds() // 60),
        "provider": sorted({str(i.get("identityProvider")) for i in identita}),
    }


async def tentativi_sbagliati(session: AsyncSession, user_id: int, ora: Optional[datetime] = None) -> int:
    ora = ora or utcnow()
    return int((await session.execute(
        select(func.count()).select_from(AuditLog).where(
            AuditLog.action == "collega.codice_errato", AuditLog.actor_id == user_id,
            AuditLog.created_at > ora - timedelta(hours=1),
        )
    )).scalar_one() or 0)


async def _abbonamento_a_pagamento(session: AsyncSession, user_id: int) -> bool:
    from ..domain.billing_models import STATI_VIVI, Subscription

    return bool((await session.execute(
        select(func.count()).select_from(Subscription).where(
            Subscription.user_id == user_id, Subscription.status.in_(STATI_VIVI), Subscription.provider != "interno",
        )
    )).scalar_one())


async def trasferisci(session: AsyncSession, da: User, a: User) -> Dict[str, int]:
    """Ciò che l'account `da` ha già passa ad `a`. Le tabelle con una riga per persona (consensi, preferenze, carta
    del giorno, voti) restano quelle di `a`: sono scelte sue. Restituisce quante righe per tabella."""
    from ..domain.abbonamenti_models import ProvaGratuita
    from ..domain.acquisti_store_models import AcquistoStore
    from ..domain.billing_models import CouponRedemption, CreditEntry, PaymentCheckout
    from ..domain.chat_models import ChatProattivaTurno
    from ..domain.deck_models import DeckUnlock
    from ..domain.memory_models import UserMemory
    from ..domain.notifiche_models import DispositivoNotifica
    from ..domain.ordini_models import IndirizzoSpedizione, Ordine

    spostati: Dict[str, int] = {}

    async def sposta(nome: str, colonna, *condizioni) -> None:
        esito = await session.execute(
            update(colonna.class_).where(colonna == da.id, *condizioni).values({colonna.key: a.id})
            .execution_options(synchronize_session=False)
        )
        if esito.rowcount:
            spostati[nome] = int(esito.rowcount)

    await sposta("letture", Reading.owner_id)
    await sposta("memorie", UserMemory.owner_id)
    # Lo stato sintetico della memoria è una riga per persona: le voci di `da` si uniscono a quelle di `a`.
    from datetime import date

    from ..domain import memoria_repositories
    from .stato_memoria import dimentica

    voci_da = await memoria_repositories.stato_di(session, da.id, lock=True)
    if voci_da:
        voci_a = await memoria_repositories.stato_di(session, a.id, lock=True)
        gia = {(v["categoria"], v["testo"].strip().lower()) for v in voci_a}
        unite = voci_a + [v for v in voci_da if (v["categoria"], v["testo"].strip().lower()) not in gia]
        await memoria_repositories.salva_stato(session, a.id, dimentica(unite, date.today()))
        await memoria_repositories.elimina_stato(session, da.id)
        spostati["stato_memoria"] = len(voci_da)
    await sposta("chat", ChatProattivaTurno.owner_id)
    await sposta("crediti", CreditEntry.user_id)
    await sposta("ordini", Ordine.user_id)
    # Un solo indirizzo predefinito: se `a` ne ha già uno, quelli che arrivano non lo sono.
    if (await session.execute(select(func.count()).select_from(IndirizzoSpedizione).where(
        IndirizzoSpedizione.user_id == a.id, IndirizzoSpedizione.predefinito.is_(True),
    ))).scalar_one():
        await session.execute(update(IndirizzoSpedizione).where(IndirizzoSpedizione.user_id == da.id)
                              .values(predefinito=False).execution_options(synchronize_session=False))
    await sposta("indirizzi", IndirizzoSpedizione.user_id)
    await sposta("pagamenti", PaymentCheckout.user_id)
    await sposta("coupon", CouponRedemption.user_id)
    await sposta("acquisti_store", AcquistoStore.user_id)
    await sposta("dispositivi", DispositivoNotifica.user_id)
    # I mazzi sbloccati: uno per mazzo e persona.
    gia = select(DeckUnlock.deck_id).where(DeckUnlock.user_id == a.id).scalar_subquery()
    await sposta("mazzi", DeckUnlock.user_id, DeckUnlock.deck_id.not_in(gia))
    # La prova gratuita usata resta usata (una per persona).
    if not (await session.execute(select(func.count()).select_from(ProvaGratuita)
                                  .where(ProvaGratuita.user_id == a.id))).scalar_one():
        await sposta("prova", ProvaGratuita.user_id)
    return spostati


async def usa_codice(
    session: AsyncSession, kc: KeycloakAdmin, ricevente: User, sub_ricevente: str, codice: str,
) -> Dict[str, Any]:
    """Sposta le identità social dell'account che ha creato il codice su `ricevente`, con i suoi dati, e separa
    l'account che le ha cedute. Non fa il commit; un errore lascia la sessione da annullare (`rollback`).

    L'ordine: prima i controlli (codice, conflitti), poi il database (`flush`), infine Keycloak. Se Keycloak fallisce
    a metà si rimette com'era e chi chiama annulla il database: nessuno resta con mezzo spostamento."""
    ora = utcnow()
    if await tentativi_sbagliati(session, ricevente.id, ora) >= TENTATIVI_ORA:
        raise ErroreCollegamento("troppi_tentativi", 429)
    riga = (await session.execute(
        select(CodiceCollegamento).where(CodiceCollegamento.impronta == impronta(codice)).with_for_update()
    )).scalar_one_or_none()
    donatore = await session.get(User, riga.user_id) if riga is not None else None
    if (
        riga is None or riga.usato_il is not None or riga.scade_il <= ora
        or donatore is None or donatore.deleted_at is not None
        or len(normalizza(codice)) != LUNGHEZZA
    ):
        raise ErroreCollegamento("codice_non_valido", 400)
    if donatore.id == ricevente.id:
        raise ErroreCollegamento("stesso_account", 409)
    if await _abbonamento_a_pagamento(session, donatore.id):
        # Un abbonamento pagato (sito o store) non si sposta da solo: lo spostiamo noi, a mano, senza perdere giorni.
        raise ErroreCollegamento("abbonamento_attivo", 409)

    sub_donatore = donatore.keycloak_sub
    da_spostare = await kc.identita_federate(sub_donatore)
    if not da_spostare:
        raise ErroreCollegamento("nessuna_identita", 409)
    gia = {str(i.get("identityProvider")) for i in await kc.identita_federate(sub_ricevente)}
    conflitti = sorted(gia & {str(i.get("identityProvider")) for i in da_spostare})
    if conflitti:
        raise ErroreCollegamento("gia_collegato", 409, provider=conflitti)

    spostati = await trasferisci(session, donatore, ricevente)
    separata = unione_account.separa(donatore)
    riga.usato_il, riga.usato_da = ora, ricevente.id
    await session.flush()

    fatti: List[Dict[str, Any]] = []
    try:
        for identita in da_spostare:
            alias = str(identita["identityProvider"])
            await kc.scollega_identita(sub_donatore, alias)
            fatti.append(identita)
            await kc.collega_identita(sub_ricevente, identita)
    except KeycloakAdminError as exc:
        for identita in fatti:  # si rimette com'era, al meglio
            try:
                await kc.scollega_identita(sub_ricevente, str(identita["identityProvider"]))
                await kc.collega_identita(sub_donatore, identita)
            except KeycloakAdminError:
                pass
        raise ErroreCollegamento("keycloak", 502, errore=str(exc)[:200]) from exc

    return {
        "provider": sorted({str(i["identityProvider"]) for i in da_spostare}),
        "spostati": spostati,
        "donatore_id": donatore.id,
        "sub_donatore": sub_donatore,
        "riga_separata": separata,
    }


async def chiudi_donatore(kc: KeycloakAdmin, sub_donatore: str) -> Optional[str]:
    """Dopo il commit: l'utente che ha ceduto le identità non entra più (sessioni chiuse, token offline dell'app
    revocati, disattivato). Tollerante: le identità sono già spostate, e un utente senza accessi non può entrare
    comunque. Restituisce l'errore, se c'è stato, per il registro."""
    try:
        await kc.chiudi_sessioni(sub_donatore)
        await kc.disattiva_utente(sub_donatore)
    except KeycloakAdminError as exc:
        return str(exc)[:200]
    return None
