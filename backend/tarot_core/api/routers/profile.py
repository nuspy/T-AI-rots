"""Il profilo di chi consulta: data di nascita, genere, carte personali, il
partner ricordato, inviti, carta del giorno."""
from __future__ import annotations

import asyncio
import hashlib
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from ...auth.dependencies import CurrentUser, DbSession
from ...billing.credits import RegistroCrediti
from ...domain import deck_repositories, indirizzi_repositories, memoria_repositories
from ...domain.base import utcnow
from ...domain.blog_models import MediaImage
from ...domain.memory_models import UserMemory
from ...domain.models import DailyCard, User
from ...domain.ordini_models import IndirizzoSpedizione
from ...domain.repositories import AuditRepository, nuovo_codice_invito
from ...llm.base import supporta_embedding
from ...llm.compiti import Compito
from ...tarot import blog as regole_blog
from ...tarot.numerologia import carta_dell_anima, carta_dell_anno
from ...tarot.persone import LUNGHEZZA_GENERE_ALTRO, mancanti, pulisci
from ..deps import get_conoscenza, provider_per
from .blog import nome_pubblico, url_immagine
from .condivisione import contatore

router = APIRouter(prefix="/me", tags=["profilo"])

#: Il giorno della carta del giorno è quello italiano: «oggi» per chi la
#: apre, non per il server.
FUSO = ZoneInfo("Europe/Rome")


class ModificaProfilo(BaseModel):
    birth_date: Optional[date] = None
    locale: Optional[str] = Field(default=None, pattern="^(it|en)$")
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
        # Il partner ricordato ha il cognome: si mostra solo al proprietario.
        "partner_ricordato": user.partner_ricordato,
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


@router.patch("/profile")
async def modifica(payload: ModificaProfilo, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    if payload.birth_date is not None:
        if payload.birth_date > _oggi() or payload.birth_date.year < 1900:
            raise HTTPException(status_code=400, detail="Data di nascita non valida")
        user.birth_date = payload.birth_date
    if payload.locale:
        user.locale = payload.locale
    if payload.gender is not None:
        if payload.gender == "altro":
            testo = pulisci(payload.gender_custom, LUNGHEZZA_GENERE_ALTRO)
            if not testo:
                raise HTTPException(status_code=400, detail="Con «altro» scrivi come ti definisci")
            user.gender_custom = testo
        else:
            user.gender_custom = None
        user.gender = payload.gender
    if payload.is_trans is not None:
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
        await registro.accredita(user.id, complemento, reason="omaggio", note=f"invito {codice}")
    if totale_invitato > 0:
        await registro.accredita(invitante.id, totale_invitato, reason="omaggio", note=f"invito riscattato da {user.id}")
    await AuditRepository(session).record(
        action="referral.redeem", actor_id=user.id, target_type="user", target_id=str(invitante.id),
    )
    await session.commit()
    return {"crediti": totale_invitato, "saldo": await registro.saldo(user.id)}


@router.get("/daily-card")
async def carta_del_giorno(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    """La carta del giorno: gratuita, un Arcano maggiore, la stessa per tutto
    il giorno.

    Non serve un modello: il testo è il significato del mazzo nella sua
    lettura del giorno. È un rito quotidiano, e deve costare zero a chi lo
    offre per poter essere di tutti.
    """
    oggi = _oggi()
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
    giorno = oggi
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
    ids: List[uuid.UUID] = Field(default_factory=list)
    tutte: bool = False


def _memoria_json(m: UserMemory) -> Dict[str, Any]:
    return {
        "id": str(m.id), "contenuto": m.contenuto, "tipo": m.tipo,
        "campo_attinenza": m.campo_attinenza, "fonte": m.fonte,
        "aggiornata": m.updated_at.isoformat() if m.updated_at else None,
    }


@router.get("/memories")
async def memorie(user: CurrentUser, session: DbSession) -> Dict[str, List[Dict[str, Any]]]:
    return {"memorie": [_memoria_json(m) for m in await memoria_repositories.elenca(session, user.id)]}


@router.patch("/memories/{memoria_id}")
async def modifica_memoria(
    memoria_id: uuid.UUID, payload: MemoriaMod, user: CurrentUser, session: DbSession,
) -> Dict[str, Any]:
    """Modifica una memoria. Se il contenuto cambia, l'embedding si ricalcola: altrimenti il
    retrieval futuro cercherebbe sul vettore vecchio con un testo nuovo — un disallineamento
    silenzioso che nessun test noterebbe finché qualcuno non si accorge che non torna più fuori."""
    memoria = await memoria_repositories.per_id(session, user.id, memoria_id)
    if memoria is None:
        raise HTTPException(status_code=404, detail="Memoria non trovata")

    contenuto_nuovo = (payload.contenuto or "").strip()
    if contenuto_nuovo and contenuto_nuovo != memoria.contenuto:
        provider_embed = provider_per(Compito.EMBEDDING)
        if supporta_embedding(provider_embed):
            memoria.embedding = (await provider_embed.embed([contenuto_nuovo]))[0]
        memoria.contenuto = contenuto_nuovo
    campo_nuovo = (payload.campo_attinenza or "").strip()
    if campo_nuovo:
        memoria.campo_attinenza = campo_nuovo
    await session.commit()
    await session.refresh(memoria)  # `updated_at` è calcolato dal DB (onupdate): va riletto, non solo committato
    return _memoria_json(memoria)


@router.delete("/memories/{memoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_memoria(memoria_id: uuid.UUID, user: CurrentUser, session: DbSession) -> Response:
    trovata = await memoria_repositories.elimina(session, user.id, memoria_id)
    if not trovata:
        raise HTTPException(status_code=404, detail="Memoria non trovata")
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/memories", status_code=status.HTTP_204_NO_CONTENT)
async def elimina_memorie(payload: MemorieDaEliminare, user: CurrentUser, session: DbSession) -> Response:
    """Cancellazione multipla: `tutte` prevale su `ids` se entrambi sono valorizzati — un client
    che li manda insieme intende «tutte», non un sottoinsieme ambiguo."""
    if payload.tutte:
        await memoria_repositories.elimina_tutte(session, user.id)
    elif payload.ids:
        await memoria_repositories.elimina_molte(session, user.id, payload.ids)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
