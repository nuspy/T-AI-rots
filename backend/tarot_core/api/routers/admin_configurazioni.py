"""Le configurazioni dalla console (v9, Fase 2c): Stripe, posta in uscita, dati del titolare. Solo il ruolo admin.

**I segreti non escono mai.** La chiave segreta di Stripe, il segreto del webhook e la password della posta si
scrivono (cifrati, `llm/cifratura.py`) e non si rileggono: le risposte dicono solo se ci sono, da dove vengono
(console o ambiente del server) e, per Stripe, la modalità ricavata dalla forma della chiave. Nemmeno l'audit li
vede: registra quali campi sono cambiati, mai i valori. Un campo segreto lasciato vuoto in un salvataggio resta
com'era; per toglierlo c'è un comando esplicito.

Dopo ogni salvataggio i valori in memoria di questa replica si ricaricano subito (`correnti.carica`); le altre
repliche li rileggono entro `correnti.ETA_MASSIMA` secondi.

`router_pubblico` dà al sito i dati del titolare per l'informativa (`GET /privacy/titolare`, senza accesso).
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...auth.dependencies import CurrentUser, DbSession, require_role
from ...billing.stripe import EVENTI
from ...configurazioni import correnti, dns, smtp as prova_smtp, stripe_console, titolare
from ...domain.base import utcnow
from ...domain.configurazioni_models import (
    EMAIL_PRIVACY_PREDEFINITA, FORNITORI_PAGAMENTO, HOSTING_PREDEFINITO, ConfigSmtp, ConfigStripe,
)
from ...domain.repositories import AuditRepository
from ...llm.cifratura import cifra, decifra
from ...settings import get_settings

router = APIRouter(
    prefix="/admin/configurazioni", tags=["configurazioni"], dependencies=[Depends(require_role("admin"))],
)
router_pubblico = APIRouter(tags=["privacy"])

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _presenza(valore: str, origine: str) -> Dict[str, Any]:
    return {"impostata": bool(valore), "origine": origine if valore else None}


async def _riga_stripe(session) -> ConfigStripe:
    riga = await session.get(ConfigStripe, 1)
    if riga is None:
        riga = ConfigStripe(id=1)
        session.add(riga)
        await session.flush()
    return riga


async def _riga_smtp(session) -> ConfigSmtp:
    riga = await session.get(ConfigSmtp, 1)
    if riga is None:
        riga = ConfigSmtp(id=1)
        session.add(riga)
        await session.flush()
    return riga


# ---- Stripe -----------------------------------------------------------------------------------------------------


def _stato_stripe(riga: Optional[ConfigStripe]) -> Dict[str, Any]:
    s = get_settings()
    eff = correnti.pagamenti(s)
    chiave_console = decifra(riga.chiave_segreta_cifrata) if riga else ""
    segreto_console = decifra(riga.segreto_webhook_cifrato) if riga else ""
    chiave = chiave_console or s.stripe_secret_key
    return {
        "provider": eff.provider,
        "provider_console": riga.provider if riga else None,
        "provider_ambiente": s.billing_provider,
        "origine_provider": eff.origine_provider,
        "produzione": s.environment == "prod",
        "modalita": (riga.modalita if riga and riga.modalita else None) or correnti.modalita_della_chiave(chiave),
        "chiave_segreta": {
            **_presenza(chiave, "console" if chiave_console else "ambiente"),
            # Solo il tipo di chiave (`sk` segreta o `rk` limitata), mai un pezzo del valore.
            "tipo": chiave[:2] if chiave[:3] in ("sk_", "rk_") else None,
        },
        "chiave_pubblicabile": riga.chiave_pubblicabile if riga and riga.chiave_pubblicabile else None,
        "segreto_webhook": _presenza(
            segreto_console if chiave_console else s.stripe_webhook_secret,
            "console" if chiave_console else "ambiente",
        ),
        "webhook": {
            "url_atteso": stripe_console.url_webhook(),
            "id": riga.webhook_id if riga else None,
            "url": riga.webhook_url if riga else None,
            "registrato_il": riga.webhook_registrato_il.isoformat() if riga and riga.webhook_registrato_il else None,
        },
        "eventi": list(EVENTI),
        "ultima_prova": {
            "quando": riga.ultima_prova_il.isoformat() if riga and riga.ultima_prova_il else None,
            "esito": (riga.esito_prova or None) if riga else None,
        },
    }


@router.get("/stripe")
async def stato_stripe(session: DbSession) -> Dict[str, Any]:
    await correnti.carica(session)
    return _stato_stripe(await session.get(ConfigStripe, 1))


class StripeIn(BaseModel):
    #: Il fornitore attivo; `null` torna a quello dell'ambiente.
    provider: Optional[str] = None
    #: `test` o `live`; `null` la ricava dalla chiave.
    modalita: Optional[str] = None
    #: Vuota: resta quella salvata.
    chiave_segreta: str = Field(default="", max_length=300)
    #: Vuota: resta quella salvata; `-` la toglie.
    chiave_pubblicabile: str = Field(default="", max_length=200)
    #: Toglie chiave segreta e segreto del webhook dalla console (si torna a quelli dell'ambiente, se ci sono).
    togli_chiavi: bool = False


@router.put("/stripe")
async def salva_stripe(payload: StripeIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    s = get_settings()
    riga = await _riga_stripe(session)
    cambiati = []

    if payload.provider is not None and payload.provider not in FORNITORI_PAGAMENTO:
        raise HTTPException(status_code=422, detail="Fornitore sconosciuto: disattivato, mock o stripe.")
    if payload.provider == "mock" and s.environment == "prod":
        raise HTTPException(
            status_code=422,
            detail="In produzione il fornitore simulato non si può scegliere: chiunque attiverebbe i piani senza pagare.",
        )
    if payload.modalita not in (None, "test", "live"):
        raise HTTPException(status_code=422, detail="Modalità: test (prova) o live (reale).")

    chiave = payload.chiave_segreta.strip()
    if chiave:
        if not chiave.startswith(("sk_", "rk_")):
            raise HTTPException(
                status_code=422,
                detail="La chiave segreta comincia con sk_ (segreta) o rk_ (limitata). Quella con pk_ è la pubblicabile.",
            )
        modalita_chiave = correnti.modalita_della_chiave(chiave)
        if modalita_chiave is None:
            raise HTTPException(status_code=422, detail="La chiave non sembra di Stripe (sk_test_…, sk_live_…).")
        if payload.modalita and payload.modalita != modalita_chiave:
            raise HTTPException(
                status_code=422,
                detail=f"La chiave è di {'prova' if modalita_chiave == 'test' else 'produzione'}, ma hai scelto la "
                       f"modalità {'reale' if payload.modalita == 'live' else 'di prova'}.",
            )
        vecchia = decifra(riga.chiave_segreta_cifrata)
        if vecchia and correnti.modalita_della_chiave(vecchia) != modalita_chiave:
            # Gli endpoint del webhook di prova e quelli reali sono separati: il segreto vecchio non vale più.
            riga.segreto_webhook_cifrato, riga.webhook_id, riga.webhook_url, riga.webhook_registrato_il = None, None, None, None
            cambiati.append("webhook (azzerato: modalità cambiata)")
        riga.chiave_segreta_cifrata = cifra(chiave)
        riga.modalita = modalita_chiave
        riga.esito_prova, riga.ultima_prova_il = {}, None
        cambiati.append("chiave_segreta")
    elif payload.modalita and payload.modalita != riga.modalita:
        attuale = correnti.modalita_della_chiave(decifra(riga.chiave_segreta_cifrata) or s.stripe_secret_key)
        if attuale and attuale != payload.modalita:
            raise HTTPException(
                status_code=422,
                detail="Per cambiare modalità incolla la chiave segreta dell'altra modalità (sk_test_… o sk_live_…).",
            )
        riga.modalita = payload.modalita
        cambiati.append("modalita")

    pubblicabile = payload.chiave_pubblicabile.strip()
    if pubblicabile == "-":
        riga.chiave_pubblicabile = None
        cambiati.append("chiave_pubblicabile")
    elif pubblicabile:
        if not pubblicabile.startswith("pk_") or correnti.modalita_della_chiave(pubblicabile) is None:
            raise HTTPException(status_code=422, detail="La chiave pubblicabile comincia con pk_test_ o pk_live_.")
        modalita = riga.modalita or correnti.modalita_della_chiave(decifra(riga.chiave_segreta_cifrata))
        if modalita and correnti.modalita_della_chiave(pubblicabile) != modalita:
            raise HTTPException(status_code=422, detail="La chiave pubblicabile è di un'altra modalità della segreta.")
        riga.chiave_pubblicabile = pubblicabile
        cambiati.append("chiave_pubblicabile")

    if payload.togli_chiavi:
        riga.chiave_segreta_cifrata = riga.segreto_webhook_cifrato = None
        riga.webhook_id = riga.webhook_url = None
        riga.webhook_registrato_il = None
        riga.modalita = None
        cambiati.append("chiavi tolte")

    if "provider" in payload.model_fields_set and payload.provider != riga.provider:
        if payload.provider == "stripe":
            chiave_effettiva = decifra(riga.chiave_segreta_cifrata) or (
                s.stripe_secret_key if not riga.chiave_segreta_cifrata else ""
            )
            if not chiave_effettiva:
                raise HTTPException(status_code=422, detail="Per attivare Stripe serve prima la chiave segreta.")
        prima = riga.provider
        riga.provider = payload.provider
        cambiati.append(f"provider: {prima or 'ambiente'} → {payload.provider or 'ambiente'}")

    riga.updated_by = user.id
    await AuditRepository(session).record(
        action="configurazioni.stripe", actor_id=user.id, target_type="configurazione", target_id="stripe",
        after={"campi": cambiati},
    )
    await session.commit()
    await correnti.carica(session)
    return _stato_stripe(riga)


@router.post("/stripe/prova")
async def prova_stripe(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    riga = await _riga_stripe(session)
    await correnti.carica(session)  # i valori di adesso, anche se salvati da un'altra replica
    chiave = correnti.pagamenti().chiave_segreta
    try:
        esito = await stripe_console.prova_chiave(chiave)
    except stripe_console.ErroreStripeConsole as exc:
        esito = {"ok": False, "messaggio": str(exc)}
    riga.ultima_prova_il, riga.esito_prova = utcnow(), esito
    await AuditRepository(session).record(
        action="configurazioni.stripe_prova", actor_id=user.id, target_type="configurazione", target_id="stripe",
        after={"ok": esito.get("ok")},
    )
    await session.commit()
    return {"esito": esito, "stato": _stato_stripe(riga)}


@router.post("/stripe/webhook")
async def registra_webhook(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    riga = await _riga_stripe(session)
    await correnti.carica(session)
    eff = correnti.pagamenti()
    try:
        esito = await stripe_console.registra_webhook(
            eff.chiave_segreta, webhook_id_noto=riga.webhook_id, segreto_noto=eff.segreto_webhook,
        )
    except stripe_console.ErroreStripeConsole as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if esito["segreto"]:
        riga.segreto_webhook_cifrato = cifra(esito["segreto"])
    elif not riga.segreto_webhook_cifrato and eff.segreto_webhook:
        # Il segreto dell'endpoint era nell'ambiente: lo si copia accanto alla chiave, così la coppia sta insieme.
        riga.segreto_webhook_cifrato = cifra(eff.segreto_webhook)
    if not riga.chiave_segreta_cifrata and eff.chiave_segreta:
        riga.chiave_segreta_cifrata = cifra(eff.chiave_segreta)
        riga.modalita = correnti.modalita_della_chiave(eff.chiave_segreta)
    riga.webhook_id, riga.webhook_url, riga.webhook_registrato_il = esito["id"], esito["url"], utcnow()
    riga.updated_by = user.id
    await AuditRepository(session).record(
        action="configurazioni.stripe_webhook", actor_id=user.id, target_type="configurazione", target_id="stripe",
        after={"azione": esito["azione"], "endpoint": esito["id"], "url": esito["url"],
               "eventi": len(esito["eventi"]), "nuovo_segreto": bool(esito["segreto"])},
    )
    await session.commit()
    await correnti.carica(session)
    return {
        "azione": esito["azione"], "doppioni_tolti": esito["doppioni_tolti"], "eventi": esito["eventi"],
        "stato": _stato_stripe(riga),
    }


# ---- posta in uscita ---------------------------------------------------------------------------------------------


def _stato_smtp(riga: Optional[ConfigSmtp], email_admin: Optional[str]) -> Dict[str, Any]:
    s = get_settings()
    console = riga is not None and bool(riga.host.strip())
    in_uso = correnti.smtp(s)
    return {
        "origine": correnti.origine_smtp(s),
        "console": {
            "host": riga.host if riga else "", "porta": riga.porta if riga else 465,
            "sicurezza": riga.sicurezza if riga else "ssl", "utente": riga.utente if riga else "",
            "password": {"impostata": bool(riga and riga.password_cifrata)},
            "mittente": riga.mittente if riga else "", "nome_mittente": riga.nome_mittente if riga else "TAROTS chat",
            "dkim_selettore": riga.dkim_selettore if riga else "",
            "attiva": console,
        },
        # Dell'ambiente si dice cosa c'è, senza la password.
        "ambiente": {
            "host": s.smtp_host, "porta": s.smtp_porta, "sicurezza": "ssl" if s.smtp_ssl else "starttls",
            "utente": s.smtp_utente, "mittente": s.smtp_mittente, "password": {"impostata": bool(s.smtp_password)},
        },
        "in_uso": {"host": in_uso.host, "porta": in_uso.porta, "mittente": in_uso.mittente,
                   "configurata": in_uso.configurato},
        "dominio": dns.dominio_di(in_uso.mittente),
        "email_admin": email_admin,
        "ultima_prova": {
            "quando": riga.ultima_prova_il.isoformat() if riga and riga.ultima_prova_il else None,
            "esito": (riga.esito_prova or None) if riga else None,
        },
    }


@router.get("/smtp")
async def stato_smtp(user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    await correnti.carica(session)
    return _stato_smtp(await session.get(ConfigSmtp, 1), user.email)


class SmtpIn(BaseModel):
    #: Vuoto: la console smette di decidere e vale l'ambiente.
    host: str = Field(default="", max_length=255)
    porta: int = Field(default=465, ge=1, le=65535)
    sicurezza: str = Field(default="ssl", pattern=r"^(ssl|starttls)$")
    utente: str = Field(default="", max_length=320)
    #: Vuota: resta quella salvata.
    password: str = Field(default="", max_length=500)
    togli_password: bool = False
    mittente: str = Field(default="", max_length=320)
    nome_mittente: str = Field(default="TAROTS chat", max_length=120)
    dkim_selettore: str = Field(default="", max_length=63, pattern=r"^[A-Za-z0-9._-]*$")


@router.put("/smtp")
async def salva_smtp(payload: SmtpIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    host, mittente = payload.host.strip(), payload.mittente.strip()
    if host and not EMAIL.match(mittente):
        raise HTTPException(status_code=422, detail="Il mittente è un indirizzo email (per esempio noreply@tarots.chat).")
    riga = await _riga_smtp(session)
    prima = {k: getattr(riga, k) for k in ("host", "porta", "sicurezza", "utente", "mittente", "nome_mittente", "dkim_selettore")}
    riga.host, riga.porta, riga.sicurezza = host, payload.porta, payload.sicurezza
    riga.utente, riga.mittente = payload.utente.strip(), mittente
    riga.nome_mittente = payload.nome_mittente.strip() or "TAROTS chat"
    riga.dkim_selettore = payload.dkim_selettore.strip()
    campi = [k for k, v in prima.items() if getattr(riga, k) != v]
    s = get_settings()
    if payload.togli_password:
        riga.password_cifrata = None
        campi.append("password tolta")
    elif payload.password:
        riga.password_cifrata = cifra(payload.password)
        campi.append("password")
    elif host and not riga.password_cifrata and s.smtp_password and host == s.smtp_host.strip():
        # Stesso server dell'ambiente e nessuna password scritta: si copia quella del server (l'operatore non la
        # conosce, richiesta del 3/10: «compila tu»).
        riga.password_cifrata = cifra(s.smtp_password)
        campi.append("password (copiata dal server)")
    riga.updated_by = user.id
    await AuditRepository(session).record(
        action="configurazioni.smtp", actor_id=user.id, target_type="configurazione", target_id="smtp",
        after={"campi": campi},
    )
    await session.commit()
    await correnti.carica(session)
    dns.dimentica()
    return _stato_smtp(riga, user.email)


class ProvaSmtpIn(BaseModel):
    destinatario: str = Field(min_length=3, max_length=320)


@router.post("/smtp/prova")
async def prova_posta(payload: ProvaSmtpIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    destinatario = payload.destinatario.strip()
    if not EMAIL.match(destinatario):
        raise HTTPException(status_code=422, detail="Scrivi un indirizzo email valido.")
    await correnti.carica(session)
    esito = await prova_smtp.invia_prova(destinatario)
    riga = await session.get(ConfigSmtp, 1)
    if riga is not None:
        riga.ultima_prova_il, riga.esito_prova = utcnow(), esito
    await AuditRepository(session).record(
        action="configurazioni.smtp_prova", actor_id=user.id, target_type="configurazione", target_id="smtp",
        after={"ok": esito["ok"], "destinatario": destinatario},
    )
    await session.commit()
    return esito


@router.get("/smtp/dns")
async def dns_posta(session: DbSession, forza: bool = False) -> Dict[str, Any]:
    riga = await session.get(ConfigSmtp, 1)
    selettore = riga.dkim_selettore if riga is not None else ""
    return await dns.controlla(dns.dominio_di(correnti.smtp().mittente), selettore, forza=forza)


# ---- dati del titolare -------------------------------------------------------------------------------------------


@router.get("/titolare")
async def leggi_titolare(session: DbSession) -> Dict[str, Any]:
    r = await titolare.riga(session)
    await session.commit()
    return {**titolare.json_admin(r), "fornitori_ai": await titolare.fornitori_ai(session),
            "predefiniti": {"email_privacy": EMAIL_PRIVACY_PREDEFINITA, "hosting": HOSTING_PREDEFINITO}}


class TitolareIn(BaseModel):
    nome: str = Field(default="", max_length=200)
    indirizzo: str = Field(default="", max_length=400)
    codice_fiscale: str = Field(default="", max_length=40)
    email_privacy: str = Field(default="", max_length=320)
    dpo_nominato: bool = False
    dpo_contatto: str = Field(default="", max_length=400)
    hosting: str = Field(default="", max_length=300)


@router.put("/titolare")
async def salva_titolare(payload: TitolareIn, user: CurrentUser, session: DbSession) -> Dict[str, Any]:
    email = payload.email_privacy.strip()
    if email and not EMAIL.match(email):
        raise HTTPException(status_code=422, detail="L'email per la privacy non è un indirizzo valido.")
    if payload.dpo_nominato and not payload.dpo_contatto.strip():
        raise HTTPException(status_code=422, detail="Se il DPO è nominato, scrivi come contattarlo.")
    r = await titolare.riga(session)
    prima = titolare.json_admin(r)
    r.nome, r.indirizzo = payload.nome.strip(), payload.indirizzo.strip()
    r.codice_fiscale = payload.codice_fiscale.strip()
    r.email_privacy = email
    r.dpo_nominato, r.dpo_contatto = payload.dpo_nominato, payload.dpo_contatto.strip()
    r.hosting = payload.hosting.strip()
    r.updated_by = user.id
    dopo = titolare.json_admin(r)
    # Dati pubblici (stanno nell'informativa): nell'audit vanno anche i valori.
    await AuditRepository(session).record(
        action="configurazioni.titolare", actor_id=user.id, target_type="configurazione", target_id="titolare",
        before={k: v for k, v in prima.items() if k != "aggiornato_il"},
        after={k: v for k, v in dopo.items() if k != "aggiornato_il"},
    )
    await session.commit()
    await session.refresh(r)
    return {**titolare.json_admin(r), "fornitori_ai": await titolare.fornitori_ai(session),
            "predefiniti": {"email_privacy": EMAIL_PRIVACY_PREDEFINITA, "hosting": HOSTING_PREDEFINITO}}


@router_pubblico.get("/privacy/titolare")
async def titolare_pubblico(session: DbSession) -> Dict[str, Any]:
    """I dati del titolare per l'informativa del sito, e i fornitori di intelligenza artificiale attivi."""
    return await titolare.json_pubblico(session)
