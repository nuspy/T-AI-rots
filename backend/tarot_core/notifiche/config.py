"""La configurazione delle notifiche (v9, Fase 5): quello che sta in console e i segreti che nessuno sceglie.

- **Firebase.** L'operatore carica dalla console il JSON di un service account del progetto Firebase dell'app; si
  salva cifrato (`llm/cifratura.py`) e non torna più indietro: la console vede solo progetto, email e l'esito della
  prova. Con quel JSON si ottiene il token OAuth per FCM HTTP v1 (`notifiche/fcm.py`).
- **VAPID.** La coppia di chiavi del Web Push si genera da sola al primo bisogno (P-256): la privata si salva cifrata
  in `segreti_sistema` (`vapid_privata`), la pubblica in chiaro in `config_notifiche` e si dà ai browser. Non si
  rigenera mai da sola: cambiarla renderebbe inutili tutte le sottoscrizioni dei browser.
- **La firma dei link.** Il link di apertura (dal service worker) e quello di disiscrizione in un clic portano un
  HMAC con un segreto interno (`notifiche_firma`, anch'esso generato e cifrato): nessuno può segnare come aperta la
  notifica di un altro, né disiscrivere qualcuno indovinando un numero.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
from datetime import datetime, time
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.base import utcnow
from ..domain.notifiche_models import TIPI_AUTOMATICI, ConfigNotifiche

logger = logging.getLogger(__name__)

#: Le lingue in cui la console e i predefiniti scrivono le notifiche (le stesse delle email).
LINGUE = ("en", "it", "hu", "ru", "uk", "es")
#: Il fuso di chi non ne ha uno: lo stesso di prima della Fase 5 per la carta del giorno.
FUSO_PREDEFINITO = "Europe/Rome"
SCOPE_FCM = "https://www.googleapis.com/auth/firebase.messaging"


# ---- la riga della console --------------------------------------------------------------------------------------


async def config(session: AsyncSession) -> ConfigNotifiche:
    """La configurazione (singleton), creata con i predefiniti se manca."""
    riga = await session.get(ConfigNotifiche, 1)
    if riga is None:
        await session.execute(insert(ConfigNotifiche).values(id=1).on_conflict_do_nothing(index_elements=["id"]))
        await session.flush()
        riga = await session.get(ConfigNotifiche, 1)
    assert riga is not None
    return riga


# ---- i segreti interni (VAPID, firma) ---------------------------------------------------------------------------


async def _segreto(session: AsyncSession, nome: str, genera) -> str:
    """Un segreto interno: letto da `segreti_sistema`, o generato con `genera()` e salvato cifrato (la prima replica
    che scrive vince: le altre rileggono il suo). Stringa vuota se non si decifra più (chiave master cambiata)."""
    from ..domain.configurazioni_models import SegretoSistema
    from ..llm.cifratura import cifra, decifra

    riga = await session.get(SegretoSistema, nome)
    if riga is None:
        await session.execute(insert(SegretoSistema).values(
            nome=nome, valore_cifrato=cifra(genera()), origine="generato",
        ).on_conflict_do_nothing(index_elements=["nome"]))
        await session.flush()
        riga = (await session.execute(
            select(SegretoSistema).where(SegretoSistema.nome == nome).execution_options(populate_existing=True)
        )).scalar_one()
        logger.info("Segreto interno «%s» generato e salvato cifrato", nome)
    valore = decifra(riga.valore_cifrato)
    if not valore:
        logger.error("Il segreto interno «%s» non si decifra con la chiave master attuale", nome)
    return valore


def _b64(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).rstrip(b"=").decode("ascii")


def _nuova_privata_vapid() -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    chiave = ec.generate_private_key(ec.SECP256R1())
    return chiave.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption(),
    ).decode("ascii")


def pubblica_da_privata(pem: str) -> str:
    """La chiave pubblica VAPID come la vuole `PushManager.subscribe` (`applicationServerKey`): il punto non compresso
    (65 byte) in base64url senza `=`."""
    from cryptography.hazmat.primitives import serialization

    privata = serialization.load_pem_private_key(pem.encode("ascii"), password=None)
    grezza = privata.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint,
    )
    return _b64(grezza)


async def chiavi_vapid(session: AsyncSession) -> Tuple[str, str]:
    """(privata PEM, pubblica base64url), generate al primo bisogno. Non fa il commit. ("", "") se la privata non si
    decifra più: il Web Push resta spento finché qualcuno non decide (rigenerarla vuol dire perdere i browser)."""
    riga = await config(session)
    privata = await _segreto(session, "vapid_privata", _nuova_privata_vapid)
    if not privata:
        return "", ""
    pubblica = pubblica_da_privata(privata)
    if riga.vapid_pubblica != pubblica:
        riga.vapid_pubblica = pubblica
        riga.vapid_creata_il = riga.vapid_creata_il or utcnow()
        await session.flush()
    return privata, pubblica


async def chiave_firma(session: AsyncSession) -> bytes:
    valore = await _segreto(session, "notifiche_firma", lambda: secrets.token_urlsafe(48))
    # Senza segreto (chiave master cambiata) nessuna firma è valida: meglio un link che non funziona che uno falsificabile.
    return valore.encode("utf-8") if valore else secrets.token_bytes(32)


def firma(chiave: bytes, testo: str) -> str:
    return _b64(hmac.new(chiave, testo.encode("utf-8"), hashlib.sha256).digest()[:18])


def firma_valida(chiave: bytes, testo: str, data: str) -> bool:
    return hmac.compare_digest(firma(chiave, testo), data or "")


AMBITI_DISISCRIZIONE = ("promozioni", "tutte")


def token_disiscrizione(chiave: bytes, user_id: int, ambito: str) -> str:
    """`<utente>.<ambito>.<firma>`: il link «non mandarmi più» funziona senza accesso, e solo per quella persona."""
    assert ambito in AMBITI_DISISCRIZIONE
    corpo = f"{user_id}.{ambito}"
    return f"{corpo}.{firma(chiave, 'disiscrivi:' + corpo)}"


def leggi_token_disiscrizione(chiave: bytes, token: str) -> Optional[Tuple[int, str]]:
    parti = (token or "").split(".")
    if len(parti) != 3 or not parti[0].isdigit() or parti[1] not in AMBITI_DISISCRIZIONE:
        return None
    corpo = f"{parti[0]}.{parti[1]}"
    if not firma_valida(chiave, "disiscrivi:" + corpo, parti[2]):
        return None
    return int(parti[0]), parti[1]


# ---- Firebase ---------------------------------------------------------------------------------------------------


def credenziali_firebase(riga: Optional[ConfigNotifiche]):
    """Le credenziali del service account di Firebase (`tarot.google.Credenziali`), o `None` se non c'è o non si
    decifra."""
    from ..llm.cifratura import decifra
    from ..tarot import google

    if riga is None or not riga.firebase_cifrato:
        return None
    testo = decifra(riga.firebase_cifrato)
    if not testo:
        return None
    try:
        return google.Credenziali(info=json.loads(testo), origine="console")
    except ValueError:
        return None


def salva_firebase(riga: ConfigNotifiche, testo: str, *, autore_id: Optional[int]) -> Dict[str, Any]:
    """Controlla e salva cifrato il JSON del service account. Solleva `ValueError` con un messaggio per l'operatore."""
    from ..llm.cifratura import cifra
    from ..tarot import google

    try:
        info = google.leggi_service_account(testo)
    except google.ErroreGoogle as exc:
        raise ValueError(str(exc)) from exc
    riga.firebase_cifrato = cifra(json.dumps(info))
    riga.firebase_progetto = str(info.get("project_id") or "")[:120] or None
    riga.firebase_email = str(info.get("client_email") or "")[:320] or None
    riga.firebase_caricato_il = utcnow()
    riga.firebase_prova_il = None
    riga.firebase_esito = {}
    riga.updated_by = autore_id
    return {"progetto": riga.firebase_progetto, "email": riga.firebase_email}


def togli_firebase(riga: ConfigNotifiche, *, autore_id: Optional[int]) -> None:
    riga.firebase_cifrato = None
    riga.firebase_progetto = None
    riga.firebase_email = None
    riga.firebase_caricato_il = None
    riga.firebase_prova_il = None
    riga.firebase_esito = {}
    riga.updated_by = autore_id


# ---- fusi e orari -----------------------------------------------------------------------------------------------


def valida_fuso(nome: Optional[str]) -> Optional[str]:
    """Il nome IANA se esiste (`Europe/Rome`, `America/Argentina/Buenos_Aires`), altrimenti `None`."""
    nome = (nome or "").strip()
    if not nome or len(nome) > 64 or nome.startswith(("/", ".")) or ".." in nome:
        return None
    try:
        ZoneInfo(nome)
    except (ZoneInfoNotFoundError, ValueError):
        return None
    return nome


def fuso_di(user: Any) -> ZoneInfo:
    """Il fuso della persona, o quello predefinito."""
    return ZoneInfo(valida_fuso(getattr(user, "fuso_orario", None)) or FUSO_PREDEFINITO)


def ora_testo(valore: Optional[time]) -> Optional[str]:
    return valore.strftime("%H:%M") if valore else None


def ora_da_testo(valore: Optional[str]) -> Optional[time]:
    if not valore:
        return None
    ore, minuti = valore.split(":")[:2]
    return time(int(ore), int(minuti))


def in_silenzio(adesso_locale: datetime, dal: Optional[time], al: Optional[time]) -> bool:
    """Se `adesso_locale` cade nelle ore di silenzio, anche a cavallo della mezzanotte (22:00 → 08:00)."""
    if dal is None or al is None or dal == al:
        return False
    ora = adesso_locale.time().replace(tzinfo=None)
    if dal < al:
        return dal <= ora < al
    return ora >= dal or ora < al


# ---- le automatiche: predefiniti --------------------------------------------------------------------------------

#: Le automatiche come partono: attive (tranne i crediti in scadenza: dalla v9 i crediti comprati non scadono, e
#: restano solo quelli di piano dei piani vecchi), con l'ora locale d'invio (`None`: appena serve, fuori dal
#: silenzio; la carta del giorno usa l'ora scelta dalla persona) e la pagina dove porta il tocco.
PREDEFINITE: Dict[str, Dict[str, Any]] = {
    "carta_giorno": {"attiva": True, "ora": None, "link": "/daily-card"},
    "serie_in_pericolo": {"attiva": True, "ora": "20:00", "link": "/daily-card"},
    "crediti_in_scadenza": {"attiva": False, "ora": "18:00", "link": "/read"},
    "benvenuto": {"attiva": True, "ora": "11:00", "link": "/daily-card"},
    "rinnovo_fallito": {"attiva": True, "ora": None, "link": "/profile"},
    "promemoria_prova": {"attiva": True, "ora": None, "link": "/trial"},
}

#: I testi predefiniti, in sei lingue (russo e ucraino col «tu»). Segnaposto: `{n}` (giorni di fila, crediti),
#: `{data}`, `{piano}`, `{giorni}`, `{sconto}`.
TESTI_PREDEFINITI: Dict[str, Dict[str, Dict[str, str]]] = {
    "carta_giorno": {
        "en": {"titolo": "Your card of the day", "corpo": "It's ready for you: turn it over and find today's reflection."},
        "it": {"titolo": "La tua carta del giorno", "corpo": "È pronta per te: girala e scopri lo spunto di oggi."},
        "hu": {"titolo": "A napi kártyád", "corpo": "Már vár rád: fordítsd meg, és nézd meg a mai gondolatot."},
        "ru": {"titolo": "Твоя карта дня", "corpo": "Она уже ждёт тебя: переверни её и узнай, о чём сегодня стоит подумать."},
        "uk": {"titolo": "Твоя карта дня", "corpo": "Вона вже чекає на тебе: переверни її й дізнайся, про що сьогодні варто подумати."},
        "es": {"titolo": "Tu carta del día", "corpo": "Ya está lista para ti: dale la vuelta y descubre la reflexión de hoy."},
    },
    "serie_in_pericolo": {
        "en": {"titolo": "Don't break your streak", "corpo": "{n} days in a row: today's card is still waiting for you."},
        "it": {"titolo": "Non interrompere la tua serie", "corpo": "Sono {n} giorni di fila: la carta di oggi ti aspetta ancora."},
        "hu": {"titolo": "Ne szakítsd meg a sorozatod", "corpo": "{n} napja egymás után: a mai kártyád még vár rád."},
        "ru": {"titolo": "Не прерывай свою серию", "corpo": "Дней подряд: {n}. Карта на сегодня всё ещё ждёт тебя."},
        "uk": {"titolo": "Не переривай свою серію", "corpo": "Днів поспіль: {n}. Карта на сьогодні досі чекає на тебе."},
        "es": {"titolo": "No rompas tu racha", "corpo": "Llevas {n} días seguidos: la carta de hoy aún te espera."},
    },
    "crediti_in_scadenza": {
        "en": {"titolo": "Your credits are expiring", "corpo": "{n} credits from your plan expire on {data}: use them for a reading."},
        "it": {"titolo": "Hai crediti in scadenza", "corpo": "{n} crediti del tuo piano scadono il {data}: usali per una lettura."},
        "hu": {"titolo": "Lejáró kreditjeid vannak", "corpo": "A csomagod {n} kreditje lejár ekkor: {data}. Használd fel őket egy olvasásra."},
        "ru": {"titolo": "Твои кредиты скоро сгорят", "corpo": "Кредиты твоего плана ({n}) истекают {data}: используй их для расклада."},
        "uk": {"titolo": "Твої кредити скоро згорять", "corpo": "Кредити твого плану ({n}) спливають {data}: використай їх для розкладу."},
        "es": {"titolo": "Tus créditos van a caducar", "corpo": "{n} créditos de tu plan caducan el {data}: úsalos para una lectura."},
    },
    "benvenuto": {
        "en": {"titolo": "Welcome to TAROTS chat", "corpo": "A free card for you every day. And when a question needs room, the cards are waiting."},
        "it": {"titolo": "Ti diamo il benvenuto", "corpo": "Ogni giorno una carta per te, gratis. E quando una domanda chiede spazio, le carte ti aspettano."},
        "hu": {"titolo": "Üdv a TAROTS chatben", "corpo": "Minden nap egy ingyenes kártya neked. És ha egy kérdés teret kér, a kártyák várnak."},
        "ru": {"titolo": "Добро пожаловать в TAROTS chat", "corpo": "Каждый день бесплатная карта для тебя. А когда вопросу нужно пространство, карты ждут."},
        "uk": {"titolo": "Ласкаво просимо до TAROTS chat", "corpo": "Щодня безкоштовна карта для тебе. А коли питанню потрібен простір, карти чекають."},
        "es": {"titolo": "Te damos la bienvenida a TAROTS chat", "corpo": "Cada día una carta gratis para ti. Y cuando una pregunta necesite espacio, las cartas te esperan."},
    },
    "rinnovo_fallito": {
        "en": {"titolo": "Your payment didn't go through", "corpo": "The renewal of {piano} failed: fix it in a minute. Your readings stay active for now."},
        "it": {"titolo": "Il pagamento non è riuscito", "corpo": "Il rinnovo di {piano} non è andato a buon fine: sistemalo in un minuto. Per ora le tue letture restano attive."},
        "hu": {"titolo": "A fizetés nem sikerült", "corpo": "A(z) {piano} megújítása nem sikerült: egy perc alatt rendezheted. Addig az olvasásaid aktívak maradnak."},
        "ru": {"titolo": "Платёж не прошёл", "corpo": "Продление {piano} не удалось: исправь это за минуту. Пока твои расклады остаются доступны."},
        "uk": {"titolo": "Платіж не пройшов", "corpo": "Подовження {piano} не вдалося: виправ це за хвилину. Поки що твої розклади доступні."},
        "es": {"titolo": "El pago no se ha completado", "corpo": "La renovación de {piano} ha fallado: arréglalo en un minuto. Por ahora tus lecturas siguen activas."},
    },
    "promemoria_prova": {
        "en": {"titolo": "Your trial ends in {giorni} days", "corpo": "On {data} it becomes yearly at {sconto}% off forever. You can cancel from your profile anytime."},
        "it": {"titolo": "La tua prova finisce tra {giorni} giorni", "corpo": "Il {data} diventa annuale con il {sconto}% di sconto per sempre. Puoi disdire dal profilo quando vuoi."},
        "hu": {"titolo": "A próbaidőszakod {giorni} nap múlva véget ér", "corpo": "Ekkor éves előfizetéssé válik, örökre {sconto}% kedvezménnyel: {data}. A profilodban bármikor lemondhatod."},
        "ru": {"titolo": "Пробный период скоро закончится", "corpo": "{data} он станет годовой подпиской со скидкой {sconto}% навсегда. Отменить можно в профиле в любой момент."},
        "uk": {"titolo": "Пробний період скоро закінчиться", "corpo": "{data} він стане річною підпискою зі знижкою {sconto}% назавжди. Скасувати можна в профілі будь-коли."},
        "es": {"titolo": "Tu prueba termina en {giorni} días", "corpo": "El {data} pasa a ser anual con un {sconto}% de descuento para siempre. Puedes cancelarla desde tu perfil cuando quieras."},
    },
}

assert set(PREDEFINITE) == set(TIPI_AUTOMATICI) == set(TESTI_PREDEFINITI)


def automatica(riga: Optional[ConfigNotifiche], tipo: str) -> Dict[str, Any]:
    """Come è impostata un'automatica: i predefiniti, con sopra quello che l'operatore ha cambiato in console. I testi
    si fondono lingua per lingua (una lingua lasciata vuota in console resta quella predefinita)."""
    base = PREDEFINITE[tipo]
    salvata = ((riga.automatiche if riga else None) or {}).get(tipo) or {}
    testi = {lingua: dict(t) for lingua, t in TESTI_PREDEFINITI[tipo].items()}
    for lingua, t in (salvata.get("testi") or {}).items():
        if isinstance(t, dict) and (t.get("titolo") or "").strip() and (t.get("corpo") or "").strip():
            testi[lingua] = {"titolo": t["titolo"].strip(), "corpo": t["corpo"].strip()}
    return {
        "attiva": bool(salvata.get("attiva", base["attiva"])),
        "ora": salvata.get("ora", base["ora"]) if base["ora"] is not None else None,
        "link": base["link"],
        "testi": testi,
        "personalizzati": sorted(x for x in (salvata.get("testi") or {}) if x in testi),
    }
