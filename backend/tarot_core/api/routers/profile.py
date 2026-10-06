"""Il profilo di chi consulta: data di nascita, genere, carte personali, il
partner ricordato, inviti, carta del giorno, e i dati presi dai social con la
posizione attuale (`POST /me/profilo-social`, vedi `tarot/profilo_social.py`)."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import uuid
from datetime import date, datetime, timedelta
from typing import Annotated, Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query, Request, Response, status
from lanterna.rete import ip_client
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...analytics import eventi as analytics
from ...auth.dependencies import CurrentPrincipal, CurrentUser, DbSession, accogli
from ...auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError, PasswordRifiutata
from ...billing.credits import RegistroCrediti
from ...domain import consent_repositories, deck_repositories, indirizzi_repositories, memoria_repositories
from ...domain.base import utcnow
from ...domain.blog_models import MediaImage
from ...domain.memory_models import UserMemory
from ...domain.models import DailyCard, User
from ...domain.ordini_models import IndirizzoSpedizione
from ...domain.repositories import AuditRepository, UserRepository, nuovo_codice_invito
from ...llm.base import supporta_embedding
from ...llm.compiti import Compito
from ...settings import get_settings
from ...tarot import blog as regole_blog
from ...tarot import eta_minima, profilo_social, unione_account
from ...tarot.lingue import in_lingua
from ...tarot.pseudonimi import nomi_utente
from ...tarot.lingue import LINGUE
from ...tarot.numerologia import carta_dell_anima, carta_dell_anno
from ...tarot.persone import LUNGHEZZA_GENERE_ALTRO, mancanti, pulisci
from ..deps import get_conoscenza, provider_per
from .blog import nome_pubblico, url_immagine
from .condivisione import contatore
from .privacy import ETA_INSUFFICIENTE

router = APIRouter(prefix="/me", tags=["profilo"])
logger = logging.getLogger(__name__)

#: Le lingue del realm di Keycloak (`supportedLocales` di `deploy/keycloak/realm-tarots*.json`, e del tema `tarots`).
LINGUE_KEYCLOAK = ("en", "it", "hu", "ru", "uk", "es")

#: Il giorno della carta del giorno è quello italiano: «oggi» per chi la
#: apre, non per il server.
FUSO = ZoneInfo("Europe/Rome")


class ModificaProfilo(BaseModel):
    birth_date: Optional[date] = None
    #: Una delle lingue del sito.
    locale: Optional[str] = Field(default=None, pattern="^(" + "|".join(LINGUE) + ")$")
    #: La scheda anagrafica. Vuoto = cancellato.
    nome: Optional[str] = Field(default=None, max_length=100)
    cognome: Optional[str] = Field(default=None, max_length=100)
    #: La posizione attuale corretta a mano: da lì in poi l'accesso non la sovrascrive. Entrambi vuoti = cancellata,
    #: e si torna al rilevamento automatico (se acceso).
    posizione_paese: Optional[str] = Field(default=None, pattern="^([A-Za-z]{2})?$")
    posizione_citta: Optional[str] = Field(default=None, max_length=100)
    #: Prendere dai social, all'accesso, i dati che mancano nella scheda.
    importa_social: Optional[bool] = None
    #: Rilevare la posizione attuale all'accesso. Spento, quella salvata si cancella.
    rileva_posizione: Optional[bool] = None
    #: Il genere dichiarato. «non_dice» (preferisco non dirlo) è una risposta valida.
    gender: Optional[str] = Field(default=None, pattern="^(donna|uomo|non_binario|altro|non_dice)$")
    #: Il testo libero di «altro»: si azzera se il genere non è «altro».
    gender_custom: Optional[str] = Field(default=None, max_length=40)
    #: La casella facoltativa «persona trans», separata dal genere.
    is_trans: Optional[bool] = None
    #: Il promemoria della verifica in due passaggi all'accesso: `false` = «non mostrare più».
    promemoria_2fa: Optional[bool] = None
    #: Come ti presenti nei commenti del blog. Vuoto = si usa il primo nome.
    nome_pubblico: Optional[str] = Field(default=None, max_length=60)
    #: v7: il registro delle risposte. `esoterico` (default) non cambia nulla; `quotidiano`
    #: evita termini tecnici esoterici non spiegati.
    registro_linguistico: Optional[str] = Field(default=None, pattern="^(esoterico|quotidiano)$")
    #: v7, Fase J: il mazzo di default per le nuove letture. `0` (non un id vero) azzera la scelta
    #: e torna al predefinito globale — `None` qui significa invece "non toccare questo campo",
    #: come per gli altri campi opzionali di questo schema.
    mazzo_predefinito_id: Optional[int] = None


class RispostaUnione(BaseModel):
    #: `mia`: l'account che c'era con questa email era della persona. `non_mia`: no, e si separa.
    scelta: str = Field(pattern="^(mia|non_mia)$")
    #: Facoltativa: la password per entrare anche con l'email (quella di prima, se la ricorda, o una nuova).
    password: Optional[str] = Field(default=None, min_length=1, max_length=128)


class Invito(BaseModel):
    codice: str = Field(min_length=4, max_length=16)


def _oggi() -> date:
    return datetime.now(FUSO).date()


async def _profilo_json(user: User, session) -> Dict[str, Any]:
    conoscenza = get_conoscenza()
    dati: Dict[str, Any] = {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "locale": user.locale,
        # Fase 2d: quando la lingua è stata scelta dal sito (vuoto: mai; allora vale quella del browser all'accesso).
        "locale_scelta_il": user.locale_scelta_il.isoformat() if user.locale_scelta_il else None,
        # v9.5: la versione della lettura di questa persona (prova 90/10), la stessa su tutti i dispositivi.
        "variante_lettura": user.variante_lettura,
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "gender": user.gender,
        "gender_custom": user.gender_custom,
        "is_trans": user.is_trans,
        "promemoria_2fa": user.promemoria_2fa,
        "nome_pubblico": user.nome_pubblico,
        "nome_mostrato": nome_pubblico(user),
        "registro_linguistico": user.registro_linguistico,
        "mazzo_predefinito_id": user.mazzo_predefinito_id,
        "avatar": url_immagine(user.avatar_id),
        "nome": user.nome,
        "cognome": user.cognome,
        "posizione": profilo_social.posizione_json(user),
        # Da dove vengono i campi presi da un social (provider e data), per mostrarlo accanto al campo.
        "dati_social": (user.dati_social or {}).get("campi") or {},
        "importa_social": user.importa_social,
        "rileva_posizione": user.rileva_posizione,
        # Il partner ricordato ha il cognome: si mostra solo al proprietario.
        "partner_ricordato": user.partner_ricordato,
        # L'età minima (GDPR, Fase 1): il sito chiede la conferma al primo accesso se `da_confermare`.
        "eta": eta_minima.stato_json(user),
        # Cosa manca nella scheda per le letture di compatibilità e di coppia.
        "relazioni": {"completo": not mancanti(user), "mancanti": mancanti(user)},
        "referral_code": user.referral_code,
        "invitato": user.referred_by is not None,
        # Il contatore delle condivisioni accertate e dei premi (vedi condivisione.py).
        "condivisioni": await contatore(session, user),
        "carta_anima": None,
        "carta_anno": None,
    }
    if user.birth_date:
        dati["carta_anima"] = conoscenza.carta_pubblica(
            conoscenza.maggiore(carta_dell_anima(user.birth_date))["id"], completa=True,
        )
        dati["carta_anno"] = conoscenza.carta_pubblica(
            conoscenza.maggiore(carta_dell_anno(user.birth_date, _oggi().year))["id"], completa=True,
        )
    return dati


@router.get("/profile")
async def profilo(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if not user.referral_code:
        user.referral_code = nuovo_codice_invito()
        await session.commit()
    return await _profilo_json(user, session)


class PreferenzaStatistiche(BaseModel):
    opposizione: bool


@router.get("/statistiche")
async def preferenza_statistiche(user: CurrentUser, session: DbSession) -> Dict[str, bool]:
    """Il legame fra le visite e l'account (v8, analytics): attivo salvo opposizione (art. 21)."""
    from lanterna.eventi import opposizione

    from ...domain.analytics_models import TABELLE

    return {"opposizione": await opposizione(session, TABELLE, user.id)}


@router.put("/statistiche")
async def modifica_statistiche(payload: PreferenzaStatistiche, user: CurrentUser, session: DbSession) -> Dict[str, bool]:
    """Opposizione o ritiro dell'opposizione. Con l'opposizione il legame con le visite passate si
    cancella subito (restano solo conteggi anonimi); ritirarla non lo ricrea."""
    from lanterna.eventi import imposta_opposizione

    from ...domain.analytics_models import TABELLE

    await imposta_opposizione(session, TABELLE, user.id, payload.opposizione)
    await AuditRepository(session).record(
        action="analytics.opposizione", actor_id=user.id, target_type="user", target_id=str(user.id),
        after={"opposizione": payload.opposizione},
    )
    await session.commit()
    return {"opposizione": payload.opposizione}


async def lingua_in_keycloak(sub: str, lingua: str) -> None:
    """v9, Fase 6: la lingua scelta va anche nell'attributo `locale` dell'utente in Keycloak, così le email che
    manda Keycloak (verifica dell'indirizzo, password dimenticata) arrivano nella lingua giusta. Dopo la risposta e
    senza mai far fallire niente: se Keycloak non risponde, il profilo è comunque salvato e la prossima scelta
    riprova. Il realm ha sei lingue (`LINGUE_KEYCLOAK`): per le altre del sito vale l'inglese, la sua predefinita."""
    if not get_settings().keycloak_client_secret or not sub or sub.startswith(unione_account.PREFISSO_SEPARATO):
        return  # sviluppo senza Keycloak, o una riga che non corrisponde più a un utente
    try:
        await KeycloakAdmin().imposta_lingua(sub, lingua if lingua in LINGUE_KEYCLOAK else "en")
    except KeycloakAdminError as exc:
        logger.warning("Lingua non aggiornata in Keycloak: %s", exc)
    except Exception:  # noqa: BLE001 — un compito in sottofondo non deve mai rompersi in silenzio peggio di così
        logger.exception("Lingua non aggiornata in Keycloak")


@router.patch("/profile")
async def modifica(
    payload: ModificaProfilo, user: CurrentUser, session: DbSession, compiti: BackgroundTasks,
) -> Dict[str, Any]:
    if payload.birth_date is not None:
        if payload.birth_date > _oggi() or payload.birth_date.year < 1900:
            raise HTTPException(status_code=400, detail="Data di nascita non valida")
        if eta_minima.sotto_eta(payload.birth_date, user.posizione_paese):
            # GDPR, Fase 1: una data di nascita sotto l'età minima non si salva, e la conferma dell'età data prima
            # non vale più (la data dice il contrario): letture e chat si fermano finché non si chiarisce.
            anni = eta_minima.anni_minimi(user.posizione_paese)
            user.eta_confermata_il = None
            user.eta_confermata_anni = None
            await AuditRepository(session).record(
                action="account.eta_contraddetta", actor_id=user.id, target_type="user", target_id=str(user.id),
                after={"anni_minimi": anni},
            )
            await session.commit()
            raise HTTPException(status_code=422, detail={
                "motivo": "eta_insufficiente", "anni": anni,
                "messaggio": in_lingua(ETA_INSUFFICIENTE, user.locale).replace("{anni}", str(anni)),
            })
        user.birth_date = payload.birth_date
        profilo_social.dimentica_campo(user, "birth_date")
    if payload.locale:
        user.locale = payload.locale
        # Fase 2d: scelta dal sito (menu o profilo). Da qui il claim del token non la riscrive, e fra due
        # dispositivi vince la più recente (`frontend/v2/lib/lingua-profilo.ts`).
        user.locale_scelta_il = utcnow()
        profilo_social.dimentica_campo(user, "locale")
        compiti.add_task(lingua_in_keycloak, user.keycloak_sub, payload.locale)
    for campo in ("nome", "cognome"):
        valore = getattr(payload, campo)
        if valore is not None:
            setattr(user, campo, pulisci(valore, 100) or None)
            profilo_social.dimentica_campo(user, campo)
    if payload.posizione_paese is not None or payload.posizione_citta is not None:
        paese = (payload.posizione_paese or "").upper() or None
        citta = pulisci(payload.posizione_citta, 100) or None
        user.posizione_paese, user.posizione_citta = paese, citta
        user.posizione_fonte = "utente" if (paese or citta) else None
        user.posizione_il = utcnow() if (paese or citta) else None
    if payload.importa_social is not None:
        user.importa_social = payload.importa_social
    if payload.rileva_posizione is not None:
        user.rileva_posizione = payload.rileva_posizione
        if not payload.rileva_posizione and user.posizione_fonte != "utente":
            user.posizione_paese = user.posizione_citta = user.posizione_fonte = None
            user.posizione_il = None
    if payload.gender is not None:
        profilo_social.dimentica_campo(user, "gender")
        if payload.gender == "altro":
            testo = pulisci(payload.gender_custom, LUNGHEZZA_GENERE_ALTRO)
            if not testo:
                raise HTTPException(status_code=400, detail="Con «altro» scrivi come ti definisci")
            user.gender_custom = testo
        else:
            user.gender_custom = None
        user.gender = payload.gender
    if payload.is_trans is not None:
        # «Persona trans» è un dato dell'art. 9 GDPR: si salva solo con il consenso `dati_particolari` (il sito lo
        # chiede accanto alla casella). Toglierla si può sempre; una casella già spuntata prima della Fase 1 si può
        # rimandare uguale (il sito la rimanda insieme al genere) — al modello comunque non arriva senza consenso.
        if (
            payload.is_trans and not user.is_trans
            and not await consent_repositories.accettato(session, user.id, "dati_particolari")
        ):
            raise HTTPException(status_code=409, detail={"motivo": "consenso_dati_particolari"})
        user.is_trans = payload.is_trans
    if payload.promemoria_2fa is not None:
        user.promemoria_2fa = payload.promemoria_2fa
    if payload.nome_pubblico is not None:
        user.nome_pubblico = pulisci(payload.nome_pubblico, 60) or None
    if payload.registro_linguistico is not None:
        user.registro_linguistico = payload.registro_linguistico
    if payload.mazzo_predefinito_id is not None:
        if payload.mazzo_predefinito_id == 0:
            user.mazzo_predefinito_id = None
        else:
            mazzo = await deck_repositories.per_id(session, payload.mazzo_predefinito_id)
            if mazzo is None or not await deck_repositories.possiede(session, user.id, mazzo):
                raise HTTPException(status_code=400, detail="Mazzo non posseduto o inesistente")
            user.mazzo_predefinito_id = mazzo.id
    await session.commit()
    return await _profilo_json(user, session)


@router.post("/profilo-social")
async def importa_profilo_social(
    request: Request, user: CurrentUser, principal: CurrentPrincipal, session: DbSession,
    authorization: Annotated[Optional[str], Header()] = None,
) -> Dict[str, Any]:
    """Dopo ogni accesso il sito chiama questo, una volta: i campi vuoti della scheda si riempiono con i dati dei
    social collegati, e la posizione attuale si aggiorna (dal social o dall'IP). Idempotente: un campo già pieno
    non si tocca, e una seconda chiamata non compila niente di nuovo. Non fallisce mai per colpa di un social:
    restituisce cosa ha compilato e da dove."""
    ora = utcnow()
    claims = principal.raw_claims or {}
    token = authorization.split(" ", 1)[1].strip() if authorization and " " in authorization else None
    dati: List[profilo_social.DatiSocial] = []
    if user.importa_social:
        dal_token = profilo_social.dati_dal_token(claims)
        if dal_token:
            dati.append(dal_token)
        if token:
            dati.extend(await profilo_social.leggi_dai_social(get_settings(), token))

    compilati: List[str] = []
    for d in dati:
        compilati.extend(profilo_social.compila(user, d, claims=claims, ora=ora))
    if user.importa_social and user.avatar_id is None and not profilo_social.scelto_dalla_persona(user, "avatar"):
        for d in dati:
            if d.foto and await _avatar_da_foto(session, user, d.foto):
                profilo_social.segna(user, "avatar", d.provider, ora)
                compilati.append("avatar")
                break

    # La posizione attuale: quella che dà il social, se c'è; altrimenti l'IP di questa richiesta, letto nel
    # database geografico locale (nessun servizio esterno, l'IP non si salva).
    dal_social = next((d for d in dati if d.paese or d.citta), None)
    if dal_social is not None:
        posizione = profilo_social.aggiorna_posizione(
            user, paese=dal_social.paese, citta=dal_social.citta, fonte=dal_social.provider, ora=ora,
        )
    else:
        from lanterna.geo import luogo

        dove = luogo(get_settings().analytics_geo or None, ip_client(request))
        posizione = profilo_social.aggiorna_posizione(
            user, paese=dove.paese, citta=dove.citta, fonte="ip", ora=ora,
        )

    provider = sorted({d.provider for d in dati if d.provider != "account"})
    if provider or compilati:
        provenienza = dict(user.dati_social or {})
        provenienza["ultimo"] = {"il": ora.isoformat(), "provider": provider, "compilati": compilati}
        user.dati_social = provenienza
    if compilati:
        await AuditRepository(session).record(
            action="profilo.dati_social", actor_id=user.id, target_type="user", target_id=str(user.id),
            # Quali campi e da dove, mai i valori.
            after={"compilati": compilati, "provider": provider},
        )
    # L'unione da confermare: Keycloak ha appena tolto i vecchi accessi a un account con l'email mai verificata.
    unione = unione_account.registra(user, claims)
    await session.commit()
    return {"compilati": compilati, "provider": provider, "posizione": posizione, "unione": unione is not None}


async def _unione_json(session, user: User) -> Optional[Dict[str, Any]]:
    nota = user.unione_in_attesa
    if not nota:
        return None
    return {**nota, "contenuto": await unione_account.attivita(session, user)}


@router.get("/unione")
async def unione_in_attesa(user: CurrentUser, principal: CurrentPrincipal, session: DbSession) -> Dict[str, Any]:
    """La domanda «l'account che c'era con la tua email era tuo?», se c'è: cosa è stato tolto (password, social non
    fidati) e cosa contiene l'account (letture, memorie, crediti, ordini). `null` se non c'è niente da chiedere."""
    if unione_account.registra(user, principal.raw_claims or {}) is not None:
        await session.commit()
    return {"unione": await _unione_json(session, user)}


@router.post("/unione")
async def rispondi_unione(
    payload: RispostaUnione, request: Request, user: CurrentUser, principal: CurrentPrincipal, session: DbSession,
) -> Dict[str, Any]:
    """La risposta. Prima la password, se c'è (un rifiuto della politica di Keycloak non chiude la domanda); poi:

    - `mia` → l'account resta com'è;
    - `non_mia` → la riga dell'account si separa (disattivata, non cancellata: letture e acquisti di chi l'aveva
      creato restano per la contabilità, ma non sono più della persona) e ne nasce una nuova, come a una prima
      iscrizione.

    La password si può scegliere solo qui, mentre la domanda è aperta: dopo, dalla pagina dell'account di Keycloak."""
    nota = user.unione_in_attesa
    if not nota:
        raise HTTPException(status_code=409, detail="Nessuna unione da confermare")
    if payload.password:
        try:
            await KeycloakAdmin().imposta_password(principal.subject, payload.password)
        except PasswordRifiutata as exc:
            raise HTTPException(status_code=422, detail={"password": exc.chiave}) from exc
        except KeycloakAdminError as exc:
            raise HTTPException(status_code=503, detail="La password non si può impostare adesso") from exc

    contenuto = await unione_account.attivita(session, user)
    persona = user
    separata: Optional[str] = None
    if payload.scelta == "non_mia":
        separata = unione_account.separa(user)
        await session.flush()
        persona = await UserRepository(session).ensure(principal)
        await accogli(session, persona, request)
    unione_account.risolvi(persona, nota)
    await AuditRepository(session).record(
        action="profilo.unione", actor_id=persona.id, target_type="user", target_id=str(persona.id),
        after={
            "scelta": payload.scelta, "password": bool(payload.password), "tolti": unione_account.tolti(nota),
            "contenuto": contenuto, "separata": separata, "riga_separata": user.id if separata else None,
        },
    )
    await session.commit()
    return {"scelta": payload.scelta, "password": bool(payload.password), "nuovo_account": separata is not None}


async def _avatar_da_foto(session, user: User, url: str) -> bool:
    """La foto del profilo social come avatar, se la persona non ne ha uno: scaricata dalla CDN del provider e
    riscritta come quelle caricate a mano (256 px, WebP)."""
    dati = await profilo_social.scarica_foto(url)
    if not dati:
        return False
    try:
        webp, larghezza, altezza = await asyncio.to_thread(regole_blog.prepara_avatar, dati)
    except regole_blog.ImmagineNonValida:
        return False
    immagine = MediaImage(uso="avatar", webp=webp, larghezza=larghezza, altezza=altezza, owner_id=user.id)
    session.add(immagine)
    await session.flush()
    user.avatar_id = immagine.id
    return True


@router.delete("/dati-social", status_code=status.HTTP_204_NO_CONTENT)
async def dimentica_dati_social(user: CurrentUser, session: DbSession) -> Response:
    """Cancella ciò che è venuto dai social e non è stato toccato dopo (un campo corretto a mano resta), con la
    posizione attuale, e spegne l'importazione e il rilevamento: al prossimo accesso non tornano."""
    campi = dict((user.dati_social or {}).get("campi") or {})
    for campo, origine in campi.items():
        if (origine or {}).get("da") == "utente":
            continue
        if campo == "birth_date":
            user.birth_date = None
        elif campo == "gender":
            user.gender = user.gender_custom = None
        elif campo in ("nome", "cognome"):
            setattr(user, campo, None)
        elif campo == "avatar" and user.avatar_id is not None:
            immagine = await session.get(MediaImage, user.avatar_id)
            user.avatar_id = None
            await session.flush()
            if immagine is not None and immagine.uso == "avatar" and immagine.owner_id == user.id:
                await session.delete(immagine)
        # La lingua resta: non è mai vuota, e quella presa dal social è comunque una lingua del sito.
    user.dati_social = None
    user.posizione_paese = user.posizione_citta = user.posizione_fonte = None
    user.posizione_il = None
    user.importa_social = False
    user.rileva_posizione = False
    await AuditRepository(session).record(
        action="profilo.dati_social_cancellati", actor_id=user.id, target_type="user", target_id=str(user.id),
        after={"campi": sorted(campi)},
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/partner", status_code=status.HTTP_204_NO_CONTENT)
async def dimentica_partner(user: CurrentUser, session: DbSession) -> Response:
    """Cancella il partner ricordato. Idempotente: senza partner non fa nulla.

    Nel registro entra il fatto, mai i dati del partner: sono di un terzo.
    """
    if user.partner_ricordato is not None:
        user.partner_ricordato = None
        await AuditRepository(session).record(
            action="partner.forget", actor_id=user.id, target_type="user", target_id=str(user.id),
        )
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/referral")
async def riscatta(payload: Invito, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """Riscatta un invito: crediti a chi invita e a chi è invitato.

    Una volta sola per account, e mai col proprio codice. `crediti_invito` è il **totale** che l'invitato deve
    avere dopo il riscatto: chi si iscrive ha già preso il regalo d'iscrizione (`crediti_iscrizione`, accreditato
    al primo accesso), quindi qui gli si dà solo il complemento — «diventano 5», non «diventano 3+5». Chi invita
    non ha preso nessun regalo base, e riceve l'intero `crediti_invito`.
    """
    if user.referred_by is not None:
        raise HTTPException(status_code=409, detail="Hai già usato un invito")
    codice = payload.codice.strip().upper()
    if codice == (user.referral_code or ""):
        raise HTTPException(status_code=400, detail="Non puoi invitare te stesso")
    invitante = (await session.execute(
        select(User).where(User.referral_code == codice, User.deleted_at.is_(None))
    )).scalar_one_or_none()
    if invitante is None:
        raise HTTPException(status_code=404, detail="Codice invito sconosciuto")

    from ...domain.impostazioni_repositories import correnti as impostazioni_correnti

    impostazioni = await impostazioni_correnti(session)
    totale_invitato = impostazioni.crediti_invito
    complemento = max(0, totale_invitato - impostazioni.crediti_iscrizione)

    registro = RegistroCrediti(session)
    user.referred_by = invitante.id
    if complemento > 0:
        await registro.accredita(user.id, complemento, reason="omaggio", note=f"invito {codice}", canale="web")
    if totale_invitato > 0:
        await registro.accredita(invitante.id, totale_invitato, reason="omaggio", note=f"invito riscattato da {user.id}")
    await AuditRepository(session).record(
        action="referral.redeem", actor_id=user.id, target_type="user", target_id=str(invitante.id),
    )
    await analytics.evento(session, analytics.INVITO_RISCATTATO, utente_id=user.id)
    await session.commit()
    return {"crediti": totale_invitato, "saldo": await registro.saldo(user.id)}


@router.get("/daily-card")
async def carta_del_giorno(
    user: CurrentUser, session: DbSession, fuso: Optional[str] = Query(default=None, max_length=64),
) -> Dict[str, Any]:
    """La carta del giorno: gratuita, un Arcano maggiore, la stessa per tutto
    il giorno.

    Non serve un modello: il testo è il significato del mazzo nella sua
    lettura del giorno. È un rito quotidiano, e deve costare zero a chi lo
    offre per poter essere di tutti.

    v9, Fase 5: il giorno è quello **locale** di chi la apre (`users.fuso_orario`; il sito manda il fuso del browser
    in `?fuso=` e si salva); senza fuso resta quello di Roma, come prima.
    """
    from ...notifiche.config import fuso_di, valida_fuso

    fuso_valido = valida_fuso(fuso)
    if fuso_valido and user.fuso_orario != fuso_valido:
        user.fuso_orario = fuso_valido
        await session.commit()
    oggi = datetime.now(fuso_di(user)).date()
    conoscenza = get_conoscenza()
    riga = (await session.execute(
        select(DailyCard).where(DailyCard.user_id == user.id, DailyCard.giorno == oggi)
    )).scalar_one_or_none()
    if riga is None:
        # Deterministica per utente e giorno: se due richieste arrivano
        # insieme, entrambe scelgono la stessa carta.
        seme = hashlib.sha256(f"{user.id}:{oggi.isoformat()}".encode()).digest()
        maggiori = [i for i in conoscenza.ordine if conoscenza.carte[i]["arcano"] == "maggiore"]
        card_id = maggiori[seme[0] % len(maggiori)]
        rovescio = seme[1] % 4 == 0
        carta = conoscenza.carta(card_id)
        riga = DailyCard(
            user_id=user.id, giorno=oggi, card_id=card_id, rovescio=rovescio,
            testo=carta["rovescio"] if rovescio else carta["dritto"], created_at=utcnow(),
        )
        session.add(riga)
        # Solo la prima apertura del giorno: le successive rileggono la stessa carta.
        await analytics.evento(session, analytics.CARTA_DEL_GIORNO, utente_id=user.id)
        try:
            await session.commit()
        except Exception:  # noqa: BLE001 - corsa sull'unicità: rileggiamo
            await session.rollback()
            riga = (await session.execute(
                select(DailyCard).where(DailyCard.user_id == user.id, DailyCard.giorno == oggi)
            )).scalar_one()

    giorni = set((await session.execute(
        select(DailyCard.giorno).where(
            DailyCard.user_id == user.id, DailyCard.giorno >= oggi - timedelta(days=366),
        )
    )).scalars())
    serie = 0
    # Chi si è spostato verso ovest può avere già la carta di «domani» (presa quando da lui era già domani): la serie
    # parte da lì, così il cambio di fuso non la spezza.
    giorno = oggi + timedelta(days=1) if oggi + timedelta(days=1) in giorni else oggi
    while giorno in giorni:
        serie += 1
        giorno -= timedelta(days=1)

    return {
        "giorno": oggi.isoformat(),
        "carta": conoscenza.carta_pubblica(riga.card_id, completa=True),
        "rovescio": riga.rovescio,
        "testo": riga.testo,
        "serie": serie,
    }


@router.put("/avatar")
async def carica_avatar(request: Request, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """La tua immagine personale (avatar): compare accanto ai tuoi commenti. Si ritaglia al centro
    in un quadrato di 256 px e si riscrive in WebP; quella precedente si cancella."""
    if not request.headers.get("content-type", "").startswith("image/"):
        raise HTTPException(status_code=415, detail="Serve un'immagine")
    if int(request.headers.get("content-length") or 0) > regole_blog.MAX_CARICO_IMMAGINE:
        raise HTTPException(status_code=413, detail="Immagine troppo grande")
    try:
        webp, larghezza, altezza = await asyncio.to_thread(regole_blog.prepara_avatar, await request.body())
    except regole_blog.ImmagineNonValida as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    precedente = user.avatar_id
    nuova = MediaImage(uso="avatar", webp=webp, larghezza=larghezza, altezza=altezza, owner_id=user.id)
    session.add(nuova)
    await session.flush()
    user.avatar_id = nuova.id
    profilo_social.dimentica_campo(user, "avatar")
    await session.flush()
    if precedente is not None:
        vecchia = await session.get(MediaImage, precedente)
        if vecchia is not None and vecchia.uso == "avatar" and vecchia.owner_id == user.id:
            await session.delete(vecchia)
    await session.commit()
    return {"avatar": url_immagine(nuova.id)}


@router.delete("/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def togli_avatar(user: CurrentUser, session: DbSession) -> Response:
    if user.avatar_id is not None:
        immagine = await session.get(MediaImage, user.avatar_id)
        user.avatar_id = None
        # Tolta apposta: la foto del social non torna al prossimo accesso.
        profilo_social.dimentica_campo(user, "avatar")
        await session.flush()
        if immagine is not None and immagine.uso == "avatar" and immagine.owner_id == user.id:
            await session.delete(immagine)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- indirizzi di spedizione (v5, Fase B5) --------------------------------------------------------

#: Un profilo non ne accumula all'infinito: oltre questo numero, aggiungerne un altro chiede prima di
#: cancellarne uno — non è una lista della spesa.
TETTO_INDIRIZZI = 10


class IndirizzoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    via: str = Field(min_length=1, max_length=200)
    citta: str = Field(min_length=1, max_length=120)
    cap: str = Field(min_length=1, max_length=20)
    provincia: Optional[str] = Field(default=None, max_length=80)
    paese: str = Field(min_length=2, max_length=2, pattern="^[A-Za-z]{2}$")
    telefono: Optional[str] = Field(default=None, max_length=30)
    predefinito: bool = False


class IndirizzoMod(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=120)
    via: Optional[str] = Field(default=None, min_length=1, max_length=200)
    citta: Optional[str] = Field(default=None, min_length=1, max_length=120)
    cap: Optional[str] = Field(default=None, min_length=1, max_length=20)
    provincia: Optional[str] = Field(default=None, max_length=80)
    paese: Optional[str] = Field(default=None, min_length=2, max_length=2, pattern="^[A-Za-z]{2}$")
    telefono: Optional[str] = Field(default=None, max_length=30)
    predefinito: Optional[bool] = None


def _indirizzo_json(i: IndirizzoSpedizione) -> Dict[str, Any]:
    return {
        "id": str(i.id), "nome": i.nome, "via": i.via, "citta": i.citta, "cap": i.cap,
        "provincia": i.provincia, "paese": i.paese, "telefono": i.telefono, "predefinito": i.predefinito,
    }


@router.get("/addresses")
async def indirizzi(user: CurrentUser, session: DbSession) -> Dict[str, List[Dict[str, Any]]]:
    return {"indirizzi": [_indirizzo_json(i) for i in await indirizzi_repositories.elenca(session, user.id)]}


@router.post("/addresses", status_code=status.HTTP_201_CREATED)
async def crea_indirizzo(payload: IndirizzoIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    esistenti = await indirizzi_repositories.elenca(session, user.id)
    if len(esistenti) >= TETTO_INDIRIZZI:
        raise HTTPException(status_code=422, detail="Hai già troppi indirizzi salvati: eliminane uno prima di aggiungerne un altro.")
    predefinito = payload.predefinito or not esistenti  # il primo indirizzo è predefinito di diritto
    if predefinito:
        await indirizzi_repositories.azzera_predefinito(session, user.id)
    indirizzo = IndirizzoSpedizione(
        user_id=user.id, nome=payload.nome.strip(), via=payload.via.strip(), citta=payload.citta.strip(),
        cap=payload.cap.strip(), provincia=(payload.provincia or "").strip() or None,
        paese=payload.paese.upper(), telefono=(payload.telefono or "").strip() or None, predefinito=predefinito,
    )
    session.add(indirizzo)
    await session.commit()
    return _indirizzo_json(indirizzo)


@router.patch("/addresses/{indirizzo_id}")
async def modifica_indirizzo(
    indirizzo_id: uuid.UUID, payload: IndirizzoMod, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    indirizzo = await indirizzi_repositories.per_id(session, user.id, indirizzo_id)
    if indirizzo is None:
        raise HTTPException(status_code=404, detail="Indirizzo non trovato")
    dati = payload.model_dump(exclude_unset=True)
    if dati.get("predefinito"):
        await indirizzi_repositories.azzera_predefinito(session, user.id, tranne=indirizzo.id)
    for campo, valore in dati.items():
        if campo == "paese" and isinstance(valore, str):
            valore = valore.upper()
        elif isinstance(valore, str) and campo != "predefinito":
            valore = valore.strip() or None
        setattr(indirizzo, campo, valore)
    await session.commit()
    return _indirizzo_json(indirizzo)


@router.delete("/addresses/{indirizzo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_indirizzo(indirizzo_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Response:
    indirizzo = await indirizzi_repositories.per_id(session, user.id, indirizzo_id)
    if indirizzo is None:
        raise HTTPException(status_code=404, detail="Indirizzo non trovato")
    era_predefinito = indirizzo.predefinito
    await session.delete(indirizzo)
    await session.flush()
    if era_predefinito:
        # Un altro, se resta qualcuno, diventa il nuovo predefinito — mai lasciare il profilo senza
        # nessuno quando ce n'è ancora almeno uno disponibile.
        rimasti = await indirizzi_repositories.elenca(session, user.id)
        if rimasti:
            rimasti[0].predefinito = True
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- memoria (v6, Fase D) -----------------------------------------------------------------------


class MemoriaMod(BaseModel):
    contenuto: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    campo_attinenza: Optional[str] = Field(default=None, min_length=1, max_length=40)


class MemorieDaEliminare(BaseModel):
    #: Gli id delle voci dello stato sintetico (brevi) o delle memorie di prima (UUID), anche mescolati.
    ids: List[str] = Field(default_factory=list, max_length=200)
    tutte: bool = False


def _memoria_json(m: UserMemory) -> Dict[str, Any]:
    return {
        "id": str(m.id), "contenuto": m.contenuto, "tipo": m.tipo,
        "campo_attinenza": m.campo_attinenza, "fonte": m.fonte,
        "aggiornata": m.updated_at.isoformat() if m.updated_at else None,
        # Le memorie di prima (con embedding) non si dimenticano da sole.
        "categoria": "stabile" if m.tipo == "stabile" else "volatile", "scade": None,
    }


def _voce_json(v: Dict[str, Any]) -> Dict[str, Any]:
    """Una voce dello stato sintetico nella forma di una memoria, con la categoria e il giorno in cui si dimentica."""
    from ...tarot.stato_memoria import scade_il

    scade = scade_il(v)
    return {
        "id": v["id"], "contenuto": v["testo"], "tipo": "stabile" if v["categoria"] == "stabile" else "variabile",
        "campo_attinenza": v["campo"], "fonte": v["fonte"], "aggiornata": v["visto"], "categoria": v["categoria"],
        "dal": v["dal"], "scade": scade.isoformat() if scade else None,
    }


def _uuid_o_none(valore: str) -> Optional[uuid.UUID]:
    try:
        return uuid.UUID(valore)
    except (ValueError, AttributeError, TypeError):
        return None


@router.get("/memories")
async def memorie(user: CurrentUser, session: DbSession) -> Dict[str, List[Dict[str, Any]]]:
    """Ciò che il lettore ricorda: le voci dello stato sintetico (già ripulite dall'oblio di oggi) e, se ce ne sono
    ancora, le memorie di prima — tutto ciò che può entrare in un prompt si vede qui e si può cancellare."""
    from ...tarot.stato_memoria import per_prompt

    voci = [_voce_json(v) for v in per_prompt(await memoria_repositories.stato_di(session, user.id), date.today())]
    vecchie = [_memoria_json(m) for m in await memoria_repositories.elenca(session, user.id)]
    return {"memorie": voci + vecchie}


async def _modifica_voce(session, user: User, voce_id: str, payload: MemoriaMod) -> Dict[str, Any]:
    voci = await memoria_repositories.stato_di(session, user.id, lock=True)
    voce = next((v for v in voci if v["id"] == voce_id), None)
    if voce is None:
        raise HTTPException(status_code=404, detail="Memoria non trovata")
    if (payload.contenuto or "").strip():
        voce["testo"] = " ".join(payload.contenuto.split())[:240]
    if (payload.campo_attinenza or "").strip():
        voce["campo"] = payload.campo_attinenza.strip().lower()
    # Chi corregge una voce la conferma: riparte la sua vita.
    voce["visto"] = date.today().isoformat()
    from ...tarot.stato_memoria import valida

    await memoria_repositories.salva_stato(session, user.id, valida(voci))
    await session.commit()
    return _voce_json(next(v for v in valida(voci) if v["id"] == voce_id))


@router.patch("/memories/{memoria_id}")
async def modifica_memoria(
    memoria_id: str, payload: MemoriaMod, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Modifica una memoria: una voce dello stato sintetico (id breve) o una memoria di prima (UUID). Per queste, se il
    contenuto cambia, l'embedding si ricalcola: altrimenti il retrieval futuro cercherebbe sul vettore vecchio con un
    testo nuovo — un disallineamento silenzioso che nessun test noterebbe finché qualcuno non si accorge che non torna
    più fuori."""
    memoria_uuid = _uuid_o_none(memoria_id)
    if memoria_uuid is None:
        return await _modifica_voce(session, user, memoria_id, payload)
    memoria = await memoria_repositories.per_id(session, user.id, memoria_uuid)
    if memoria is None:
        raise HTTPException(status_code=404, detail="Memoria non trovata")

    contenuto_nuovo = (payload.contenuto or "").strip()
    if contenuto_nuovo and contenuto_nuovo != memoria.contenuto:
        # Il testo va al fornitore degli embedding senza i nomi della persona (GDPR, Fase 1, `tarot/pseudonimi.py`).
        provider_embed = provider_per(Compito.EMBEDDING, await nomi_utente(session, user))
        if supporta_embedding(provider_embed):
            memoria.embedding = (await provider_embed.embed([contenuto_nuovo]))[0]
        memoria.contenuto = contenuto_nuovo
    campo_nuovo = (payload.campo_attinenza or "").strip()
    if campo_nuovo:
        memoria.campo_attinenza = campo_nuovo
    await session.commit()
    await session.refresh(memoria)  # `updated_at` è calcolato dal DB (onupdate): va riletto, non solo committato
    return _memoria_json(memoria)


async def _togli_voci(session, user: User, ids: List[str]) -> int:
    """Toglie dallo stato sintetico le voci con questi id. Restituisce quante ne ha tolte."""
    if not ids:
        return 0
    voci = await memoria_repositories.stato_di(session, user.id, lock=True)
    rimaste = [v for v in voci if v["id"] not in set(ids)]
    if len(rimaste) != len(voci):
        await memoria_repositories.salva_stato(session, user.id, rimaste)
    return len(voci) - len(rimaste)


@router.delete("/memories/{memoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_memoria(memoria_id: str, user: CurrentUser, session: DbSession) -> Response:
    memoria_uuid = _uuid_o_none(memoria_id)
    if memoria_uuid is None:
        trovata = bool(await _togli_voci(session, user, [memoria_id]))
    else:
        trovata = await memoria_repositories.elimina(session, user.id, memoria_uuid)
    if not trovata:
        raise HTTPException(status_code=404, detail="Memoria non trovata")
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/memories", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_memorie(payload: MemorieDaEliminare, user: CurrentUser, session: DbSession) -> Response:
    """Cancellazione multipla: `tutte` prevale su `ids` se entrambi sono valorizzati — un client
    che li manda insieme intende «tutte», non un sottoinsieme ambiguo. «Tutte» vuol dire lo stato sintetico e le
    memorie di prima."""
    if payload.tutte:
        await memoria_repositories.elimina_tutte(session, user.id)
        await memoria_repositories.elimina_stato(session, user.id)
    elif payload.ids:
        vecchie = [u for u in (_uuid_o_none(i) for i in payload.ids) if u is not None]
        if vecchie:
            await memoria_repositories.elimina_molte(session, user.id, vecchie)
        await _togli_voci(session, user, [i for i in payload.ids if _uuid_o_none(i) is None])
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
