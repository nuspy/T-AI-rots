"""I valori in uso in questo processo: prima il database (la console), poi l'ambiente (il ripiego).

Chi li usa — `provider_pagamenti()`, `PagamentiStripe`, l'invio delle email, il rapporto agli admin — è codice
sincrono chiamato da molti punti, e non ha sempre una sessione sottomano: legge un'**istantanea** tenuta in memoria,
non il database. L'istantanea si carica:

- all'avvio dell'API e poi ogni `ETA_MASSIMA` secondi (`avvio.aggiorna_periodicamente`): con più repliche, una
  modifica fatta dalla console su una replica arriva alle altre entro mezzo minuto;
- subito, nella replica che salva dalla console (`carica` dopo il commit);
- dai CronJob e dalle funzioni che hanno già una sessione (`assicura`), prima di usarla.

Senza istantanea (le prove, uno strumento che non l'ha caricata) vale l'ambiente, come prima della Fase 2c.

**Le regole.** Il fornitore di pagamento è quello scelto in console, altrimenti `TAROT_BILLING_PROVIDER`; in
produzione il simulatore non vale mai (diventa `disattivato`). Le chiavi di Stripe vanno in coppia: se la console ha
una chiave segreta, valgono la sua chiave e il suo segreto del webhook, mai mescolati con quelli dell'ambiente (che
potrebbero essere di un altro account). La posta: se la console ha un host, vale tutta la configurazione della
console; altrimenti tutta quella dell'ambiente.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from lanterna import posta as lanterna_posta
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings import Settings, get_settings

#: Ogni quanti secondi l'istantanea si rilegge dal database.
ETA_MASSIMA = 30.0
NOME_MITTENTE_PREDEFINITO = "TAROTS chat"


@dataclass(frozen=True)
class StripeDaConsole:
    provider: Optional[str]
    modalita: Optional[str]
    chiave_segreta: str
    chiave_pubblicabile: str
    segreto_webhook: str


@dataclass(frozen=True)
class SmtpDaConsole:
    host: str
    porta: int
    ssl: bool
    utente: str
    password: str
    mittente: str
    nome_mittente: str


@dataclass(frozen=True)
class Istantanea:
    stripe: Optional[StripeDaConsole]
    smtp: Optional[SmtpDaConsole]
    letta: float


_istantanea: Optional[Istantanea] = None


async def carica(session: AsyncSession) -> Istantanea:
    """Rilegge dal database le configurazioni della console (decifrando i segreti) e le mette in memoria."""
    global _istantanea
    from ..domain.configurazioni_models import ConfigSmtp, ConfigStripe
    from ..llm.cifratura import decifra

    stripe = None
    riga = await session.get(ConfigStripe, 1)
    if riga is not None:
        stripe = StripeDaConsole(
            provider=riga.provider, modalita=riga.modalita,
            chiave_segreta=decifra(riga.chiave_segreta_cifrata), chiave_pubblicabile=riga.chiave_pubblicabile or "",
            segreto_webhook=decifra(riga.segreto_webhook_cifrato),
        )
    smtp = None
    posta = await session.get(ConfigSmtp, 1)
    if posta is not None and posta.host.strip():
        smtp = SmtpDaConsole(
            host=posta.host.strip(), porta=posta.porta, ssl=posta.sicurezza == "ssl", utente=posta.utente,
            password=decifra(posta.password_cifrata), mittente=posta.mittente,
            nome_mittente=posta.nome_mittente or NOME_MITTENTE_PREDEFINITO,
        )
    _istantanea = Istantanea(stripe=stripe, smtp=smtp, letta=time.monotonic())
    return _istantanea


async def assicura(session: AsyncSession, eta_massima: float = ETA_MASSIMA) -> Istantanea:
    """L'istantanea, riletta se manca o è più vecchia di `eta_massima` secondi."""
    if _istantanea is not None and time.monotonic() - _istantanea.letta < eta_massima:
        return _istantanea
    return await carica(session)


def dimentica() -> None:
    """Solo per le prove: si torna all'ambiente."""
    global _istantanea
    _istantanea = None


# ---- pagamenti ------------------------------------------------------------------------------------------------


def modalita_della_chiave(chiave: str) -> Optional[str]:
    """`live` o `test` dalla forma della chiave (segreta, limitata o pubblicabile); `None` se non si riconosce."""
    for prefisso in ("sk_", "rk_", "pk_"):
        if chiave.startswith(prefisso + "live_"):
            return "live"
        if chiave.startswith(prefisso + "test_"):
            return "test"
    return None


@dataclass(frozen=True)
class Pagamenti:
    provider: str
    chiave_segreta: str
    segreto_webhook: str
    chiave_pubblicabile: str
    #: `console` o `ambiente`: da dove viene il fornitore.
    origine_provider: str
    #: `console`, `ambiente` o `nessuna`: da dove vengono le chiavi di Stripe.
    origine_chiavi: str

    @property
    def modalita(self) -> Optional[str]:
        return modalita_della_chiave(self.chiave_segreta)


def pagamenti(settings: Optional[Settings] = None) -> Pagamenti:
    s = settings or get_settings()
    console = _istantanea.stripe if _istantanea is not None else None

    if console is not None and console.provider:
        provider, origine_provider = console.provider, "console"
    else:
        provider, origine_provider = s.billing_provider, "ambiente"
    if provider == "mock" and s.environment == "prod":
        # Il simulatore regalerebbe i piani: in produzione non vale mai, da qualunque parte arrivi.
        provider = "disattivato"

    if console is not None and console.chiave_segreta:
        chiave, segreto, origine = console.chiave_segreta, console.segreto_webhook, "console"
    elif s.stripe_secret_key or s.stripe_webhook_secret:
        chiave, segreto, origine = s.stripe_secret_key, s.stripe_webhook_secret, "ambiente"
    else:
        chiave, segreto, origine = "", "", "nessuna"
    return Pagamenti(
        provider=provider, chiave_segreta=chiave, segreto_webhook=segreto,
        chiave_pubblicabile=console.chiave_pubblicabile if console is not None else "",
        origine_provider=origine_provider, origine_chiavi=origine,
    )


# ---- posta in uscita ------------------------------------------------------------------------------------------


def origine_smtp(settings: Optional[Settings] = None) -> str:
    """`console`, `ambiente` o `nessuna`."""
    if _istantanea is not None and _istantanea.smtp is not None:
        return "console"
    s = settings or get_settings()
    return "ambiente" if s.smtp_host else "nessuna"


def smtp(settings: Optional[Settings] = None) -> lanterna_posta.ConfigSmtp:
    """La configurazione SMTP in uso: l'unica funzione da cui passa chi spedisce email (utenti e admin)."""
    console = _istantanea.smtp if _istantanea is not None else None
    if console is not None:
        return lanterna_posta.ConfigSmtp(
            host=console.host, porta=console.porta, utente=console.utente, password=console.password,
            mittente=console.mittente, nome_mittente=console.nome_mittente, ssl=console.ssl,
        )
    s = settings or get_settings()
    return lanterna_posta.ConfigSmtp(
        host=s.smtp_host, porta=s.smtp_porta, utente=s.smtp_utente, password=s.smtp_password,
        mittente=s.smtp_mittente, nome_mittente=NOME_MITTENTE_PREDEFINITO, ssl=s.smtp_ssl,
    )
