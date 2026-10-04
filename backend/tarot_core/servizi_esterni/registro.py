"""Il registro dei servizi esterni (v9, Fase 3): ogni account che il sito usa o userà, in un posto solo.

La console «Account» li raccoglie tutti per vedere a colpo d'occhio cosa c'è, cosa manca e come si fa; i dettagli e
le impostazioni restano nella sezione competente (`sezione`), dove già stavano. Ogni voce dice:

- **`sonda`**: lo stato, letto solo dal database e dall'ambiente, **senza chiamare nessuno** (costo zero, nessuna
  attesa, nessun servizio a pagamento): `da_configurare`, `configurato`, `verificato` (l'ultima prova vera è
  riuscita), `errore` (l'ultima prova è fallita, o un file manca), `manuale` (lo stato sta fuori dal sito e non si
  può leggere), `non_usato`;
- **`verifica`** (facoltativa): una prova vera e gratuita, la stessa del pulsante della sezione competente (l'elenco
  dei modelli dei fornitori LLM, la verifica guidata di Google, la prova di Reddit, la prova del NAS, la lettura da
  Keycloak, le prove degli store);
- **`come_fare`**: i passi, brevi; **`primo_link`**: **solo il primo** indirizzo della procedura del fornitore (le
  pagine successive della stessa procedura le apre il fornitore da sé); **`dove_sta_il_segreto`**; i **costi**.

Un servizio nuovo che chiede un account si aggiunge qui (e il test `test_account_esterni.py` controlla che la sua
sezione esista nella console e che la sonda non sollevi).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings import get_settings

#: Gli stati, nell'ordine in cui la console li riassume.
STATI = ("errore", "da_configurare", "configurato", "verificato", "manuale", "non_usato")

CATEGORIE = (
    "Intelligenza artificiale", "Google", "Accesso", "Social", "Pubblicità", "Pagamenti e store",
    "Email e notifiche", "Infrastruttura", "Strumenti",
)

Stato = Dict[str, str]
Sonda = Callable[[AsyncSession], Awaitable[Stato]]
#: La verifica riceve anche chi la chiede (alcune prove esistenti lo registrano).
Verifica = Callable[[AsyncSession, Any], Awaitable[Stato]]


def stato(nome: str, dettaglio: str = "") -> Stato:
    assert nome in STATI, nome
    return {"stato": nome, "dettaglio": dettaglio}


@dataclass(frozen=True)
class ServizioEsterno:
    id: str
    nome: str
    categoria: str
    #: La pagina della console dove si imposta (`/modelli`); `None` per ciò che vive fuori dalla console.
    sezione: Optional[str]
    sonda: Sonda
    come_fare: Tuple[str, ...]
    #: Il primo indirizzo della procedura del fornitore, e solo quello. `None` se non c'è un fornitore.
    primo_link: Optional[str]
    dove_sta_il_segreto: str
    costi: str
    verifica: Optional[Verifica] = None
    #: La fase del piano v9 in cui il servizio entra davvero (`Fase 5`), se non è ancora in uso.
    fase: Optional[str] = None
    nota: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    #: Dove si imposta (v9, Fase 2c): `console` (la `sezione`), `server` (solo i tre segreti che restano sul server:
    #: password del database, chiave master di cifratura, segreto del client API↔Keycloak), `fornitore` (nell'account
    #: del servizio esterno, fuori dal sito), `automatico` (nulla da fare: lo fa il sito, o sta nel rilascio).
    #: Vuoto: `console` se c'è una sezione, altrimenti `fornitore`.
    dove: str = ""

    @property
    def dove_si_imposta(self) -> str:
        return self.dove or ("console" if self.sezione else "fornitore")


DOVE = {
    "console": "Si imposta in console",
    "server": "Si imposta sul server",
    "fornitore": "Si imposta dal fornitore",
    "automatico": "Automatico: nulla da fare",
}


# ---- sonde e verifiche ------------------------------------------------------------------------------------------


def _esito_passo(esito: Dict[str, Any], passo: str) -> Optional[Dict[str, Any]]:
    v = (esito or {}).get(passo)
    return v if isinstance(v, dict) else None


def _da_esito(passo: Optional[Dict[str, Any]], configurato: Stato) -> Stato:
    """Dall'esito salvato dell'ultima prova: verificato, errore, o (mai provato, o saltato) lo stato di base."""
    if passo is None or passo.get("saltato"):
        return configurato
    return stato("verificato" if passo.get("ok") else "errore", str(passo.get("messaggio") or ""))


# Intelligenza artificiale

async def _sonda_llm(session: AsyncSession) -> Stato:
    from ..domain.llm_repositories import fornitori_correnti

    attivi = [f for f in await fornitori_correnti(session) if f.attivo]
    if attivi:
        nomi = ", ".join(f.nome for f in attivi[:6]) + ("…" if len(attivi) > 6 else "")
        return stato("configurato", f"{len(attivi)} fornitori attivi: {nomi}.")
    if get_settings().modelli:
        return stato("configurato", "Nessun fornitore in console: si usa l'elenco dell'ambiente (TAROT_MODELLI).")
    return stato("da_configurare", "Nessun fornitore attivo: le letture non hanno un modello.")


async def _verifica_llm(session: AsyncSession, _utente) -> Stato:
    from ..api.routers.admin_llm import prova
    from ..domain.llm_repositories import fornitori_correnti

    attivi = [f for f in await fornitori_correnti(session) if f.attivo]
    if not attivi:
        return stato("da_configurare", "Nessun fornitore attivo da provare.")
    esiti = [(f.nome, await prova(f.id, session)) for f in attivi]
    falliti = [f"{nome}: {e.errore}" for nome, e in esiti if not e.ok]
    if falliti:
        return stato("errore", "Non rispondono — " + "; ".join(falliti))
    return stato("verificato", f"Rispondono tutti ({len(esiti)}): elenco dei modelli letto, nessuna generazione.")


# Google

async def _google(session: AsyncSession):
    from ..tarot import google

    riga = await google.config(session)
    return google, riga, google.credenziali_di(riga)


async def _sonda_service_account(session: AsyncSession) -> Stato:
    _, riga, cred = await _google(session)
    if cred is None:
        return stato("da_configurare", "Nessun service account: Search Console e GA4 restano spenti.")
    base = stato("configurato", f"{cred.email} ({'console' if cred.origine == 'console' else 'file montato'}).")
    return _da_esito(_esito_passo(riga.esito_verifica if riga else {}, "credenziali"), base)


async def _sonda_search_console(session: AsyncSession) -> Stato:
    google, riga, cred = await _google(session)
    if cred is None:
        return stato("da_configurare", "Serve prima il service account Google.")
    base = stato("configurato", f"Proprietà {google.proprieta_sc(riga)}: accesso non ancora verificato.")
    return _da_esito(_esito_passo(riga.esito_verifica if riga else {}, "search_console"), base)


async def _sonda_ga4(session: AsyncSession) -> Stato:
    _, riga, cred = await _google(session)
    if not (riga and (riga.ga4_proprieta_id or riga.ga4_misurazione_id)):
        return stato("da_configurare", "Mancano l'ID della proprietà GA4 e l'ID di misurazione (G-…).")
    parti = [f"proprietà {riga.ga4_proprieta_id}" if riga.ga4_proprieta_id else "manca l'ID della proprietà",
             f"contatore {riga.ga4_misurazione_id}" if riga.ga4_misurazione_id else "manca l'ID di misurazione"]
    base = stato("configurato", "; ".join(parti) + ".")
    return _da_esito(_esito_passo(riga.esito_verifica, "ga4") if cred else None, base)


def _verifica_google(passo: str) -> Verifica:
    async def verifica(session: AsyncSession, _utente) -> Stato:
        from ..tarot import google

        passi = await google.verifica(session)
        esito = passi.get(passo) or passi.get("credenziali") or {}
        if esito.get("saltato"):
            return stato("da_configurare", str(esito.get("messaggio") or ""))
        return stato("verificato" if esito.get("ok") else "errore", str(esito.get("messaggio") or ""))

    return verifica


# Accesso

async def _sonda_keycloak(session: AsyncSession) -> Stato:
    s = get_settings()
    if not s.keycloak_client_secret:
        return stato("da_configurare", "Manca il segreto del client tarot-api: la console non può cambiare il login "
                                       "persistente né l'accesso con i social.")
    return stato("configurato", f"Realm {s.keycloak_realm} su {s.keycloak_issuer_url or s.keycloak_url}.")


async def _verifica_keycloak(_session: AsyncSession, _utente) -> Stato:
    from ..auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError

    try:
        provider = await KeycloakAdmin().provider_identita()
    except KeycloakAdminError as exc:
        return stato("errore", str(exc))
    accesi = [p.get("alias") for p in provider if p.get("enabled")]
    return stato("verificato", f"Keycloak risponde: {len(accesi)} accessi social accesi ({', '.join(accesi) or 'nessuno'}).")


async def _sonda_social(_session: AsyncSession) -> Stato:
    return stato("manuale", "Lo stato sta in Keycloak: «Verifica» lo legge.")


async def _sonda_segreto_apple(session: AsyncSession) -> Stato:
    """Apple (v9, Fase 6): il segreto firmato dal sito scade; la sonda dice fino a quando vale, senza Keycloak."""
    from ..domain.accesso_nativo_models import ConfigAccessoApple
    from ..domain.base import utcnow
    from ..tarot import accesso_apple

    r = await session.get(ConfigAccessoApple, 1)
    if r is None or not accesso_apple.completa(r):
        return stato("da_configurare", "Mancano Team ID, Key ID, Services ID o la chiave .p8.")
    if r.segreto_scade_il is None:
        return stato("configurato", "Dati completi, ma il segreto non è ancora stato scritto in Keycloak.")
    scade = r.segreto_scade_il.date().isoformat()
    if (r.esito or {}).get("ok") is False:
        return stato("errore", f"Ultimo rinnovo non riuscito; il segreto in uso scade il {scade}.")
    if r.segreto_scade_il <= utcnow():
        return stato("errore", f"Il segreto è scaduto il {scade}: l'accesso con Apple non funziona.")
    return stato("configurato", f"Segreto valido fino al {scade} (si rinnova da solo ogni mese).")


def _verifica_social(alias: str) -> Verifica:
    async def verifica(_session: AsyncSession, _utente) -> Stato:
        from ..auth.keycloak_admin import KeycloakAdmin, KeycloakAdminError

        try:
            p = await KeycloakAdmin().leggi_provider(alias)
        except KeycloakAdminError as exc:
            return stato("errore", str(exc))
        if p is None:
            return stato("da_configurare", "Non configurato in Keycloak.")
        if not p.get("enabled"):
            return stato("configurato", "Configurato in Keycloak ma spento.")
        return stato("verificato", "Acceso in Keycloak.")

    return verifica


# Social

async def _sonda_reddit(session: AsyncSession) -> Stato:
    from ..tarot import reddit

    riga = await reddit.config(session)
    mancano = reddit.mancanti(riga)
    if riga is None or not riga.client_id:
        return stato("da_configurare", "Nessuna app Reddit configurata.")
    if mancano:
        return stato("da_configurare", "Mancano: " + ", ".join(mancano) + ".")
    base = stato("configurato", f"u/{riga.utente} → r/{riga.subreddit}" + (" (acceso)" if riga.attivo else " (spento)"))
    return _da_esito(_esito_passo(riga.esito_prova, "accesso"), base)


async def _verifica_reddit(session: AsyncSession, _utente) -> Stato:
    from ..tarot import reddit

    passi = await reddit.prova(session)
    accesso = passi.get("accesso") or {}
    destinazione = passi.get("destinazione") or {}
    ok = bool(accesso.get("ok")) and bool(destinazione.get("ok", True))
    testo = " ".join(str(p.get("messaggio") or "") for p in (accesso, destinazione) if p)
    return stato("verificato" if ok else "errore", testo)


# Pubblicità

async def _sonda_adsense(session: AsyncSession) -> Stato:
    from ..domain import pubblicita_repositories as pubblicita
    from ..domain.config_models import PubblicitaFornitore

    riga = await session.get(PubblicitaFornitore, "google")
    vista = pubblicita.vista_google(riga)
    if not vista["pronto"]:
        return stato("da_configurare", "Manca l'ID editore (ca-pub-…).")
    return stato("configurato", f"Editore {vista['parametri']['editore']}; iscrizione: "
                                f"{vista['registrazione']['stato'].replace('_', ' ')}.")


# Pagamenti e store

async def _sonda_stripe(session: AsyncSession) -> Stato:
    from ..configurazioni import correnti
    from ..domain.configurazioni_models import ConfigStripe

    await correnti.assicura(session)
    eff = correnti.pagamenti()
    if not eff.chiave_segreta:
        return stato("da_configurare", "Nessuna chiave di Stripe: incollala in Pagamenti → Stripe "
                                       f"(fornitore attivo: {eff.provider}).")
    modalita = {"live": "reale", "test": "di prova"}.get(eff.modalita or "", "sconosciuta")
    mancano = [] if eff.segreto_webhook else ["il webhook (premi «Registra il webhook»)"]
    if eff.provider != "stripe":
        mancano.append(f"l'attivazione (fornitore attivo: {eff.provider})")
    base = stato("configurato", f"Chiave {modalita} ({'console' if eff.origine_chiavi == 'console' else 'ambiente'})"
                                + (f"; mancano {', '.join(mancano)}." if mancano else "; webhook pronto."))
    riga = await session.get(ConfigStripe, 1)
    esito = riga.esito_prova if riga is not None and riga.esito_prova else None
    if esito is None:
        return base
    if not esito.get("ok"):
        return stato("errore", str(esito.get("messaggio") or ""))
    return stato("verificato" if not mancano else "configurato", f"{esito.get('messaggio')} {base['dettaglio']}".strip())


async def _app(session: AsyncSession, piattaforma: str):
    from ..domain import app_mobili_repositories as app_mobili
    from ..domain.app_mobili_models import ConfigAppMobile

    riga = await session.get(ConfigAppMobile, piattaforma)
    return app_mobili, riga, app_mobili.parametri_di(riga, piattaforma)


async def _sonda_play(session: AsyncSession) -> Stato:
    app_mobili, riga, p = await _app(session, "android")
    if not app_mobili.segreti_di(riga).get("service_account"):
        if p["id_sviluppatore"]:
            return stato("da_configurare", f"Account {p['id_sviluppatore']}: manca il service account per la Play "
                                           "Developer API.")
        return stato("da_configurare", "Account sviluppatore non ancora indicato.")
    base = stato("configurato", f"App {p['package_name']}: credenziali caricate, non ancora verificate.")
    return _da_esito(riga.esito_verifica if riga and riga.esito_verifica else None, base)


async def _sonda_pagamenti_google(session: AsyncSession) -> Stato:
    app_mobili, riga, _ = await _app(session, "android")
    pag = app_mobili.pagamenti_di(riga)
    if not (pag["id_profilo"] or pag["beneficiario"]):
        return stato("da_configurare", "Nessun appunto sul profilo pagamenti.")
    conto = f", conto …{pag['conto_ultime4']}" if pag["conto_ultime4"] else ""
    return stato("configurato", f"Profilo {pag['id_profilo'] or '—'}{conto} (appunti).")


async def _sonda_apple_developer(session: AsyncSession) -> Stato:
    _, _, p = await _app(session, "ios")
    if not p["team_id"]:
        return stato("da_configurare", "Team ID non ancora indicato.")
    return stato("configurato", f"Team {p['team_id']} ({p['tipo_account']}).")


async def _sonda_app_store_connect(session: AsyncSession) -> Stato:
    app_mobili, riga, p = await _app(session, "ios")
    if not (app_mobili.segreti_di(riga).get("chiave_p8") and p["key_id"] and p["issuer_id"]):
        return stato("da_configurare", "Mancano la chiave .p8 della App Store Server API, il Key ID o l'Issuer ID.")
    base = stato("configurato", f"App {p['bundle_id']} ({p['ambiente']}): chiave caricata, non ancora verificata.")
    return _da_esito(riga.esito_verifica if riga and riga.esito_verifica else None, base)


async def _sonda_pagamenti_apple(session: AsyncSession) -> Stato:
    app_mobili, riga, p = await _app(session, "ios")
    pag = app_mobili.pagamenti_di(riga)
    accordi = p["accordi_paid_apps"].replace("_", " ")
    if p["accordi_paid_apps"] != "attivi":
        return stato("da_configurare", f"Accordo Paid Apps: {accordi}. Senza, l'app non vende nulla.")
    conto = f", conto …{pag['conto_ultime4']}" if pag["conto_ultime4"] else ""
    return stato("configurato", f"Accordo Paid Apps attivo{conto}.")


def _verifica_store(piattaforma: str) -> Verifica:
    async def verifica(session: AsyncSession, _utente) -> Stato:
        from ..tarot import store_verifica

        esito = await store_verifica.verifica(session, piattaforma)
        return stato("verificato" if esito.get("ok") else "errore", str(esito.get("messaggio") or ""))

    return verifica


async def _sonda_codemagic(session: AsyncSession) -> Stato:
    _, _, p = await _app(session, "codemagic")
    if not p["app_id"]:
        return stato("da_configurare", "App non ancora collegata a Codemagic.")
    mancano = [n for n, v in (("chiave API di App Store Connect", p["chiave_asc_caricata"]),
                               ("keystore Android", p["keystore_caricato"])) if not v]
    return stato("configurato", f"App {p['app_id']}" + (f"; in Codemagic mancano: {', '.join(mancano)}." if mancano else "."))


async def _config_notifiche(session: AsyncSession):
    from ..domain.notifiche_models import ConfigNotifiche

    return await session.get(ConfigNotifiche, 1)


async def _sonda_firebase(session: AsyncSession) -> Stato:
    riga = await _config_notifiche(session)
    if riga is None or not riga.firebase_cifrato:
        return stato("da_configurare", "Nessun service account di Firebase: le app non ricevono notifiche (il sito sì, "
                                       "con il Web Push).")
    base = stato("configurato", f"Progetto {riga.firebase_progetto} ({riga.firebase_email}): non ancora provato.")
    return _da_esito(riga.firebase_esito if riga.firebase_esito else None, base)


async def _verifica_firebase(session: AsyncSession, _utente) -> Stato:
    from ..api.routers.admin_notifiche import prova_firebase

    esito = await prova_firebase(session)
    await session.commit()
    return stato("verificato" if esito.get("ok") else "errore", str(esito.get("messaggio") or ""))


async def _sonda_apns(session: AsyncSession) -> Stato:
    riga = await _config_notifiche(session)
    if riga is None or not riga.firebase_cifrato:
        return stato("da_configurare", "Prima serve Firebase; poi la chiave APNs si carica in Firebase, non qui.")
    return stato("manuale", "La chiave APNs sta in Firebase: da qui non si vede. Se le notifiche arrivano su Android ma "
                            "non su iPhone, manca lì.")


async def _sonda_vapid(session: AsyncSession) -> Stato:
    riga = await _config_notifiche(session)
    if riga is None or not riga.vapid_pubblica:
        return stato("configurato", "Si generano da sole al primo uso del Web Push (o al primo giro delle notifiche).")
    return stato("configurato", f"Generate il {riga.vapid_creata_il:%d/%m/%Y}, salvate cifrate." if riga.vapid_creata_il
                 else "Generate e salvate cifrate.")


# Email e notifiche

def _riassunto_dns(esito: Dict[str, Any]) -> Tuple[str, bool]:
    """«SPF ✓, DKIM ✗, DMARC ✗» e se mancano record."""
    parti, manca = [], False
    for nome, chiave in (("SPF", "spf"), ("DKIM", "dkim"), ("DMARC", "dmarc")):
        presente = (esito.get(chiave) or {}).get("stato") == "presente"
        manca = manca or not presente
        parti.append(f"{nome} {'presente' if presente else 'assente'}")
    return ", ".join(parti), manca


async def _sonda_smtp(session: AsyncSession) -> Stato:
    from ..configurazioni import correnti, dns
    from ..domain.configurazioni_models import ConfigSmtp

    await correnti.assicura(session)
    config = correnti.smtp()
    if not config.configurato:
        return stato("da_configurare", "Posta in uscita non impostata: in Impostazioni → Posta in uscita servono "
                                       "almeno server e mittente. Senza, email e rapporti non partono.")
    origine = "console" if correnti.origine_smtp() == "console" else "ambiente del server"
    dettaglio = (f"{config.host}:{config.porta} ({'SSL' if config.ssl else 'STARTTLS'}), mittente {config.mittente} "
                 f"({origine})" + ("" if config.password else "; senza password"))
    riga = await session.get(ConfigSmtp, 1)
    ultimo = dns.ultimo(dns.dominio_di(config.mittente), riga.dkim_selettore if riga is not None else "")
    if ultimo is None or ultimo.get("errore"):
        return stato("configurato", f"{dettaglio}. DNS non ancora controllato: premi «Verifica».")
    riassunto, manca = _riassunto_dns(ultimo)
    return stato("configurato" if manca else "verificato", f"{dettaglio}. DNS: {riassunto}.")


async def _verifica_smtp(session: AsyncSession, _utente) -> Stato:
    """La sonda DNS (gratuita): SPF, DKIM e DMARC del dominio del mittente. Nessuna email parte da qui."""
    from ..configurazioni import correnti, dns
    from ..domain.configurazioni_models import ConfigSmtp

    await correnti.carica(session)
    config = correnti.smtp()
    riga = await session.get(ConfigSmtp, 1)
    esito = await dns.controlla(dns.dominio_di(config.mittente), riga.dkim_selettore if riga is not None else "",
                                forza=True)
    if esito.get("errore"):
        return stato("errore", esito["errore"])
    riassunto, manca = _riassunto_dns(esito)
    if manca:
        return stato("configurato", f"DNS di {esito['dominio']}: {riassunto}. Senza DKIM e DMARC molte email "
                                    "finiscono nello spam: vedi Impostazioni → Posta in uscita.")
    return stato("verificato", f"DNS di {esito['dominio']}: {riassunto}.")


async def _sonda_newsletter(_session: AsyncSession) -> Stato:
    return stato("non_usato", "Niente newsletter via email: le novità sono le campagne push di «Notifications».")


# Infrastruttura

async def _sonda_backup(session: AsyncSession) -> Stato:
    from ..domain.backup_models import BackupEsecuzione, ImpostazioniBackup
    from ..tarot import backup

    riga = await session.get(ImpostazioniBackup, 1)
    cred = backup.credenziale(riga)
    if riga is None or not riga.host:
        return stato("da_configurare", "Nessuna destinazione sul NAS.")
    if not cred["configurata"]:
        return stato("da_configurare", "Manca la credenziale del NAS: caricala in Backup (chiave SSH o password).")
    ultima = (await session.execute(
        select(BackupEsecuzione).where(BackupEsecuzione.tipo.in_(("backup", "prova")),
                                       BackupEsecuzione.esito.in_(("ok", "errore")))
        .order_by(BackupEsecuzione.created_at.desc()).limit(1)
    )).scalar_one_or_none()
    base = stato("configurato", f"{riga.utente}@{riga.host}:{riga.porta}{riga.cartella}"
                                + ("" if riga.attivo else " (spento)"))
    if ultima is None:
        return base
    quando = ultima.created_at.strftime("%d/%m/%Y") if ultima.created_at else ""
    if ultima.esito == "ok":
        return stato("verificato", f"{base['dettaglio']}; ultima {ultima.tipo} riuscita il {quando}.")
    return stato("errore", f"Ultima {ultima.tipo} fallita il {quando}: {ultima.dettaglio or ''}".strip())


async def _verifica_backup(session: AsyncSession, utente) -> Stato:
    from ..api.routers.admin_backup import ProvaIn, prova

    esito = await prova(ProvaIn(fidati=False), utente, session)
    if esito.get("riuscita"):
        avviso = "" if esito.get("accettata") else " La chiave dell'host non è ancora accettata: fallo dalla pagina Backup."
        return stato("verificato", f"Collegamento e scrittura riusciti in {esito.get('millisecondi')} ms.{avviso}")
    return stato("errore", str(esito.get("dettaglio") or ""))


async def _sonda_database(session: AsyncSession) -> Stato:
    from sqlalchemy import text
    from sqlalchemy.engine import make_url

    url = make_url(get_settings().database_url)
    versione = (await session.execute(text("SHOW server_version"))).scalar_one()
    return stato("configurato", f"PostgreSQL {versione} su {url.host}:{url.port or 5432}, database {url.database}.")


async def _sonda_chiave_master(_session: AsyncSession) -> Stato:
    s = get_settings()
    if s.llm_provider_key == "pF6wjvqBFeElH8yC0tfWcG6KFZnKDr5s6n4L5EjmMTE=":
        if s.environment == "prod":
            return stato("errore", "È quella di sviluppo: chi legge il database leggerebbe anche le chiavi.")
        return stato("configurato", "Chiave di sviluppo (va bene solo in locale).")
    return stato("configurato", "Impostata sul server: cifra tutte le chiavi e le password salvate dalla console.")


async def _sonda_segreti_interni(session: AsyncSession) -> Stato:
    from ..configurazioni.segreti import SEGRETI
    from ..domain.configurazioni_models import SegretoSistema

    righe = (await session.execute(select(SegretoSistema.nome, SegretoSistema.origine))).all()
    if not righe:
        return stato("configurato", "Si generano al prossimo avvio dell'API.")
    origini = ", ".join(f"{'impronta degli IP' if n == 'ip_hash' else 'sale delle condivisioni'} "
                        f"({'generato' if o == 'generato' else 'dall’ambiente'})" for n, o in sorted(righe))
    return stato("configurato", f"{len(righe)} di {len(SEGRETI)} pronti, cifrati nel database: {origini}.")


async def _sonda_dbip(_session: AsyncSession) -> Stato:
    percorso = get_settings().analytics_geo
    if not percorso:
        return stato("da_configurare", "Nessun file DB-IP: niente paese e città negli analytics.")
    if not os.path.isfile(percorso):
        return stato("errore", f"Il file {percorso} non c'è: l'immagine dell'API va ricostruita con GEO_MESE.")
    return stato("configurato", f"File {percorso}.")


async def _sonda_otlp(_session: AsyncSession) -> Stato:
    s = get_settings()
    if not s.tracing_enabled:
        return stato("non_usato", "Tracce spente (TAROT_TRACING_ENABLED=false).")
    locale = "localhost" in s.otlp_endpoint or "127.0.0.1" in s.otlp_endpoint
    return stato("configurato", f"Tracce verso {s.otlp_endpoint}" + (" (indirizzo locale)." if locale else "."))


async def _sonda_redis(_session: AsyncSession) -> Stato:
    return stato("non_usato", "Nessun codice lo usa: l'impostazione TAROT_REDIS_URL è stata tolta.")


async def _sonda_manuale(_session: AsyncSession) -> Stato:
    return stato("manuale", "Sta fuori dal sito: lo stato non si può leggere da qui.")


# Strumenti

async def _sonda_indexnow(_session: AsyncSession) -> Stato:
    chiave = get_settings().indexnow_chiave
    return (stato("configurato", f"Chiave {chiave[:6]}… (pubblica, servita in /{chiave[:6]}….txt).") if chiave
            else stato("da_configurare", "Nessuna chiave IndexNow: Bing e Yandex non ricevono le notifiche."))


async def _sonda_websub(_session: AsyncSession) -> Stato:
    hub = get_settings().websub_hub
    return stato("configurato", f"Hub {hub}.") if hub else stato("da_configurare", "Nessun hub WebSub.")


async def _sonda_chiavi_rest(session: AsyncSession) -> Stato:
    from ..domain.blog_models import ApiKey

    attive = (await session.execute(
        select(func.count()).select_from(ApiKey).where(ApiKey.attiva.is_(True), ApiKey.revocata_il.is_(None))
    )).scalar_one()
    return (stato("configurato", f"{attive} chiavi attive.") if attive
            else stato("da_configurare", "Nessuna chiave: gli agenti non possono pubblicare sul blog."))


async def _sonda_colab(session: AsyncSession) -> Stato:
    from ..domain.analytics_models import TABELLE
    from ..domain.base import utcnow

    t = TABELLE.token
    validi = (await session.execute(
        select(func.count()).select_from(t).where(t.c.revocato_il.is_(None), t.c.scade_il > utcnow())
    )).scalar_one()
    return (stato("configurato", f"{validi} token validi per i notebook.") if validi
            else stato("manuale", "Nessun token valido: se ne crea uno quando serve un notebook."))


# ---- il registro ------------------------------------------------------------------------------------------------


def _social() -> List[ServizioEsterno]:
    from ..auth.provider_sociali import CATALOGO

    voci = []
    for p in CATALOGO:
        if not p.disponibile:
            continue
        costi = ("Richiede l'Apple Developer Program (99 $ l'anno), lo stesso dell'app iOS." if p.alias == "apple"
                 else "Gratis.")
        voci.append(ServizioEsterno(
            id=f"social_{p.alias}", nome=f"Accesso con {p.nome}", categoria="Accesso", sezione="/accesso-social",
            sonda=_sonda_segreto_apple if p.alias == "apple" else _sonda_social, verifica=_verifica_social(p.alias),
            come_fare=tuple(p.guida) or ("Crea l'app OAuth nella console del fornitore e incolla client id e segreto "
                                         "in «Accesso con i social».",),
            primo_link=p.console,
            dove_sta_il_segreto=(
                "La chiave .p8 cifrata nel database (si imposta in console); il segreto che ne nasce lo firma il sito "
                "e lo scrive in Keycloak." if p.alias == "apple" else
                "In Keycloak: la console lo gira a Keycloak e lo dimentica (non sta nel nostro database)."),
            costi=costi, nota=p.nota,
        ))
    return voci


def _registro() -> List[ServizioEsterno]:
    voci: List[ServizioEsterno] = [
        ServizioEsterno(
            id="llm", nome="Fornitori LLM", categoria="Intelligenza artificiale", sezione="/modelli",
            sonda=_sonda_llm, verifica=_verifica_llm,
            come_fare=(
                "Crea un account dal fornitore scelto (predefinito: NVIDIA NIM) e genera una chiave API.",
                "In «Modelli» aggiungi il fornitore: tipo, indirizzo, modello e chiave.",
                "Assegna il fornitore ai compiti (letture, chat, traduzioni) e premi «Prova».",
            ),
            primo_link="https://build.nvidia.com/",
            dove_sta_il_segreto="Database, cifrata (llm_providers.api_key_cifrata, chiave Fernet nel Secret "
                                "`tarots-secrets` chiave `llm-provider-key`).",
            costi="A consumo per token (il livello gratuito di NVIDIA è solo una prova). «Verifica» legge solo "
                  "l'elenco dei modelli: non genera nulla e non costa.",
        ),
        ServizioEsterno(
            id="google_service_account", nome="Service account Google", categoria="Google", sezione="/analytics/google",
            sonda=_sonda_service_account, verifica=_verifica_google("credenziali"),
            come_fare=(
                "In Google Cloud crea un progetto e un service account, poi una chiave JSON.",
                "Abilita le API «Google Search Console API» e «Google Analytics Data API» nel progetto.",
                "Carica il file JSON in «Configura Google» (SEO o Analytics → Google).",
            ),
            primo_link="https://console.cloud.google.com/iam-admin/serviceaccounts",
            dove_sta_il_segreto="Database, cifrato (config_google); ripiego: file montato "
                                "(TAROT_SEARCH_CONSOLE_CREDENZIALI).",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="search_console", nome="Google Search Console", categoria="Google", sezione="/seo",
            sonda=_sonda_search_console, verifica=_verifica_google("search_console"),
            come_fare=(
                "Aggiungi la proprietà di dominio tarots.chat e verificala con il record TXT nel DNS.",
                "In Impostazioni → Utenti e autorizzazioni aggiungi l'email del service account con permesso «Completo».",
                "«Verifica» controlla l'accesso e invia la sitemap.",
            ),
            primo_link="https://search.google.com/search-console",
            dove_sta_il_segreto="Nessun segreto proprio: usa il service account Google.",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="ga4", nome="Google Analytics 4", categoria="Google", sezione="/analytics/google",
            sonda=_sonda_ga4, verifica=_verifica_google("ga4"),
            come_fare=(
                "Crea una proprietà GA4 e un flusso web per tarots.chat.",
                "Copia l'ID della proprietà (numero) e l'ID di misurazione (G-…) in «Configura Google».",
                "In Gestione accessi alla proprietà aggiungi l'email del service account come «Visualizzatore».",
            ),
            primo_link="https://analytics.google.com/",
            dove_sta_il_segreto="Nessun segreto: gli ID sono pubblici; la lettura usa il service account Google.",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="keycloak", nome="Keycloak (account degli utenti)", categoria="Accesso", sezione="/accesso-social",
            sonda=_sonda_keycloak, verifica=_verifica_keycloak,
            come_fare=(
                "Il realm `tarots` si genera con deploy/keycloak/strumenti (vedi deploy/k8s/LEGGIMI.md).",
                "Il client `tarot-api` ha un account di servizio con i ruoli di realm-management per la console.",
                "Il suo segreto è uno dei tre segreti che restano sul server: Secret `tarots-secrets`, chiave "
                "`api-client-secret` (lo stesso valore lo legge Keycloak). Login social e sessioni si regolano "
                "poi dalla console.",
            ),
            primo_link="https://www.keycloak.org/documentation",
            dove_sta_il_segreto="Sul server: Secret k8s `tarots-secrets`, chiavi `api-client-secret` e "
                                "`keycloak-admin-password`.",
            costi="Gratis (self-hosted sul server).",
            dove="server",
        ),
        *_social(),
        ServizioEsterno(
            id="reddit", nome="Reddit", categoria="Social", sezione="/social",
            sonda=_sonda_reddit, verifica=_verifica_reddit,
            come_fare=(
                "Con l'account che pubblicherà, crea un'app di tipo «script».",
                "In «Social» incolla client id, secret, utente, password e il subreddit.",
                "«Prova» legge account e subreddit senza pubblicare.",
            ),
            primo_link="https://www.reddit.com/prefs/apps",
            dove_sta_il_segreto="Database, cifrati (config_reddit: secret dell'app e password).",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="adsense", nome="Google AdSense", categoria="Pubblicità", sezione="/pubblicita/google",
            sonda=_sonda_adsense,
            come_fare=(
                "Iscriviti ad AdSense con il sito tarots.chat.",
                "Copia l'ID editore (ca-pub-…) e gli slot in «Advertisements → Google Ads»: il sito serve ads.txt da solo.",
                "Attendi l'approvazione di Google, poi accendi gli spazi.",
            ),
            primo_link="https://www.google.com/adsense/start/",
            dove_sta_il_segreto="Nessun segreto: l'ID editore è pubblico; il profilo pagamenti è solo appunti "
                                "(ultime 4 cifre del conto).",
            costi="Gratis: Google trattiene la sua quota sugli annunci.",
        ),
        ServizioEsterno(
            id="stripe", nome="Stripe", categoria="Pagamenti e store", sezione="/pagamenti/stripe",
            sonda=_sonda_stripe,
            come_fare=(
                "Crea l'account Stripe e completa la verifica dell'attività e del conto bancario.",
                "In Stripe → Sviluppatori → Chiavi API copia la chiave segreta (sk_…) e la pubblicabile (pk_…) e "
                "incollale in Pagamenti → Stripe; premi «Prova la chiave».",
                "Premi «Registra il webhook»: l'indirizzo e gli eventi li imposta la console. Poi scegli «Stripe» "
                "come fornitore attivo.",
                "IVA OSS: decidi con il commercialista fra Stripe Tax e la registrazione OSS.",
            ),
            primo_link="https://dashboard.stripe.com/register",
            dove_sta_il_segreto="Database, cifrati (config_stripe: chiave segreta e segreto del webhook); ripiego: "
                                "Secret `tarots-secrets`, copiato da solo in console al primo avvio.",
            costi="Commissione per transazione (vedi il listino Stripe del paese); Stripe Tax a parte. "
                  "«Verifica» non c'è qui: la prova della chiave è in Pagamenti → Stripe (lettura gratuita).",
        ),
        ServizioEsterno(
            id="google_play", nome="Google Play Console", categoria="Pagamenti e store", sezione="/app-mobili",
            sonda=_sonda_play, verifica=_verifica_store("android"),
            come_fare=(
                "Registra l'account sviluppatore (personale o organizzazione con D-U-N-S) e verifica l'identità.",
                "Un account personale nuovo deve fare un test chiuso con 12 tester per 14 giorni prima della produzione.",
                "Crea un service account in Google Cloud, invitalo in Play Console → Utenti e autorizzazioni e "
                "carica il suo JSON in «App mobili → Android».",
            ),
            primo_link="https://play.google.com/console/signup",
            dove_sta_il_segreto="Database, cifrato (config_app_mobili, riga android).",
            costi="25 $ una tantum; commissione del 15% sugli abbonamenti e sul primo milione di dollari l'anno, poi 30%.",
            # Fase 2d: i coupon del sito non valgono negli acquisti di Google Play.
            nota="Codici promozionali: i coupon della console valgono solo sui pagamenti Stripe (sito, o pulsante "
                 "Stripe nell'app). Per gli acquisti con Google Play si creano i codici promozionali di Google, in "
                 "Play Console (https://play.google.com/console/) → l'app → Monetizza → Promozioni.",
        ),
        ServizioEsterno(
            id="google_pagamenti", nome="Profilo pagamenti Google Play", categoria="Pagamenti e store",
            sezione="/app-mobili",
            sonda=_sonda_pagamenti_google,
            come_fare=(
                "In Play Console → Configurazione → Profilo pagamenti crea il profilo commerciante (merchant).",
                "Aggiungi il conto bancario e i dati fiscali; Google fa un piccolo versamento di prova.",
                "Annota in «App mobili → Android» l'ID del profilo e le ultime 4 cifre del conto.",
            ),
            primo_link="https://play.google.com/console/",
            dove_sta_il_segreto="Nessun segreto: solo appunti (ultime 4 cifre del conto).",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="apple_developer", nome="Apple Developer Program", categoria="Pagamenti e store",
            sezione="/app-mobili/ios",
            sonda=_sonda_apple_developer,
            come_fare=(
                "Iscriviti all'Apple Developer Program (come persona o come organizzazione con D-U-N-S).",
                "Annota il Team ID (Account → Membership) in «App mobili → iOS».",
                "Crea l'identificativo dell'app chat.tarots.app con «Sign in with Apple» e «In-App Purchase».",
            ),
            primo_link="https://developer.apple.com/programs/enroll/",
            dove_sta_il_segreto="Nessun segreto qui: l'account è dell'operatore.",
            costi="99 $ l'anno (o l'equivalente locale).",
        ),
        ServizioEsterno(
            id="app_store_connect", nome="App Store Connect e App Store Server API", categoria="Pagamenti e store",
            sezione="/app-mobili/ios",
            sonda=_sonda_app_store_connect, verifica=_verifica_store("ios"),
            come_fare=(
                "Crea l'app in App Store Connect con il bundle ID chat.tarots.app e annota l'Apple ID.",
                "In Utenti e accesso → Integrazioni → Acquisti in-app genera una chiave e scarica il file .p8.",
                "Carica la chiave con Key ID e Issuer ID in «App mobili → iOS» e incolla l'URL delle Server "
                "Notifications V2 nelle informazioni dell'app.",
            ),
            primo_link="https://appstoreconnect.apple.com/",
            dove_sta_il_segreto="Database, cifrata (config_app_mobili, riga ios).",
            # Fase 2d: i coupon del sito non valgono negli acquisti dell'App Store.
            nota="Codici promozionali: i coupon della console valgono solo sui pagamenti Stripe (sito, o pulsante "
                 "Stripe nell'app). Per gli abbonamenti comprati con Apple si creano gli Offer Codes, in App Store "
                 "Connect (https://appstoreconnect.apple.com/) → l'app → Abbonamenti → il gruppo → l'abbonamento → "
                 "Codici offerta.",
            costi="Incluso nell'Apple Developer Program; commissione 15% (Small Business Program) o 30%.",
        ),
        ServizioEsterno(
            id="apple_pagamenti", nome="Accordi, imposte e banche Apple", categoria="Pagamenti e store",
            sezione="/app-mobili/ios",
            sonda=_sonda_pagamenti_apple,
            come_fare=(
                "In App Store Connect firma l'accordo «Paid Apps».",
                "Aggiungi conto bancario e moduli fiscali (W-8BEN o W-8BEN-E fuori dagli USA).",
                "Se il fatturato resta sotto il milione di dollari l'anno, iscriviti allo Small Business Program.",
            ),
            primo_link="https://appstoreconnect.apple.com/",
            dove_sta_il_segreto="Nessun segreto: solo appunti (ultime 4 cifre del conto).",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="codemagic", nome="Codemagic (build delle app)", categoria="Strumenti", sezione="/app-mobili/codemagic",
            sonda=_sonda_codemagic,
            come_fare=(
                "Crea l'account Codemagic e collega il repository dell'app.",
                "In Codemagic carica la chiave API di App Store Connect (firma e TestFlight) e il keystore di upload "
                "Android: restano là, non qui.",
                "Annota team e ID dell'app in «App mobili → Codemagic».",
            ),
            primo_link="https://codemagic.io/signup",
            dove_sta_il_segreto="In Codemagic (chiave API di App Store Connect, keystore); copia del keystore fuori "
                                "dal repo.",
            costi="Piano gratuito con minuti di build limitati al mese; oltre, a consumo.",
        ),
        ServizioEsterno(
            id="firebase", nome="Firebase Cloud Messaging", categoria="Email e notifiche",
            sezione="/notifiche/impostazioni",
            sonda=_sonda_firebase, verifica=_verifica_firebase,
            come_fare=(
                "Crea un progetto Firebase e aggiungi le app Android e iOS (chat.tarots.app); scarica "
                "google-services.json e GoogleService-Info.plist per l'app.",
                "In Impostazioni progetto → Account di servizio → «Genera nuova chiave privata»: scarichi un file JSON.",
                "Caricalo in Notifications → Impostazioni e premi «Prova»: il sito manda un messaggio solo convalidato.",
            ),
            primo_link="https://console.firebase.google.com/",
            dove_sta_il_segreto="Database, cifrato (config_notifiche): la console mostra solo progetto ed email.",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="apns", nome="Apple Push Notification service (APNs)", categoria="Email e notifiche",
            sezione="/notifiche/impostazioni", dove="fornitore",
            sonda=_sonda_apns,
            come_fare=(
                "In Certificates, Identifiers & Profiles → Keys crea una chiave con «Apple Push Notifications service» "
                "e scarica il file .p8 (si scarica una volta sola).",
                "Caricala in Firebase → Impostazioni progetto → Cloud Messaging → app Apple, con Key ID e Team ID.",
                "Il backend non la vede: le notifiche iOS passano da FCM. La spiegazione è in Notifications → "
                "Impostazioni.",
            ),
            primo_link="https://developer.apple.com/account/resources/authkeys/list",
            dove_sta_il_segreto="In Firebase (non nel nostro database).",
            costi="Incluso nell'Apple Developer Program.",
        ),
        ServizioEsterno(
            id="vapid", nome="Chiavi VAPID (Web Push)", categoria="Email e notifiche",
            sezione="/notifiche/impostazioni", dove="automatico",
            sonda=_sonda_vapid,
            come_fare=(
                "Nessun account e nulla da fare: la coppia di chiavi si genera da sola al primo uso e si salva cifrata.",
                "La pubblica si dà al browser quando chiede il permesso; lo stato è in Notifications → Impostazioni.",
            ),
            primo_link="https://datatracker.ietf.org/doc/html/rfc8292",
            dove_sta_il_segreto="Database, cifrata (segreti_sistema, «vapid_privata»): mai mostrata.",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="newsletter", nome="Invio novità (newsletter)", categoria="Email e notifiche", sezione=None,
            sonda=_sonda_newsletter,
            come_fare=(
                "Le novità agli utenti sono le campagne del tab «Notifications»: push nelle app (FCM) e Web Push sul "
                "sito, filtrate per lingua, paese e attività; le promozioni solo a chi ha dato il consenso «marketing».",
                "Per le novità via email servirà un fornitore di invii massivi con disiscrizione a un clic: la posta "
                "del server (Stalwart) è per i messaggi di servizio, non per gli invii di massa.",
            ),
            primo_link=None,
            dove_sta_il_segreto="—",
            costi="Le notifiche push sono gratis; un fornitore email avrebbe il suo listino.",
        ),
        ServizioEsterno(
            id="smtp", nome="Posta in uscita (SMTP)", categoria="Email e notifiche", sezione="/impostazioni/posta",
            sonda=_sonda_smtp, verifica=_verifica_smtp,
            come_fare=(
                "Il server di posta Stalwart (su mail.tadamoo.com, lo stesso di Keycloak) solo spedisce: le email "
                "agli utenti e i rapporti agli admin. La posta in arrivo a @tarots.chat la riceve e la inoltra "
                "Namecheap (vedi «Dominio e DNS»).",
                "In Impostazioni → Posta in uscita: server, porta, sicurezza, utente, password e mittente; poi "
                "«Invia un'email di prova». Al primo avvio la console copia da sola i valori che il server aveva.",
                "Perché le email non finiscano nello spam, nel DNS di tarots.chat servono SPF (c'è), DKIM e DMARC: "
                "«Verifica» li controlla.",
            ),
            primo_link="https://stalw.art/docs/",
            dove_sta_il_segreto="Database, cifrata (config_smtp: la password); ripiego: Secret `tarots-secrets`, "
                                "chiave `smtp-password`.",
            costi="Gratis (self-hosted). «Verifica» legge solo il DNS: nessuna email parte.",
        ),
        ServizioEsterno(
            id="nas_backup", nome="Backup sul NAS (SFTP)", categoria="Infrastruttura", sezione="/backup",
            sonda=_sonda_backup, verifica=_verifica_backup,
            come_fare=(
                "Sul NAS attiva SFTP e crea un utente con una cartella per i backup.",
                "In «Backup» carica la chiave SSH privata (file o incolla) o scrivi la password dell'utente del NAS.",
                "Indica host, porta, utente e cartella, poi «Prova» e accetta la chiave dell'host.",
            ),
            primo_link="https://www.terra-master.com/",
            dove_sta_il_segreto="Database, cifrata con la chiave master che sta solo sul server (il dump sul NAS "
                                "porta solo testo cifrato); ripiego: Secret `tarots-backup`.",
            costi="Gratis (NAS dell'operatore).",
        ),
        ServizioEsterno(
            id="dbip", nome="DB-IP City Lite (paese dall'IP)", categoria="Infrastruttura", sezione=None,
            sonda=_sonda_dbip,
            come_fare=(
                "Nessun account: il file si scarica alla build dell'immagine dell'API (argomento GEO_MESE).",
                "Licenza CC BY 4.0: l'attribuzione a DB-IP resta nell'informativa.",
            ),
            primo_link="https://db-ip.com/db/download/ip-to-city-lite",
            dove_sta_il_segreto="Nessun segreto.",
            costi="Gratis.",
            dove="automatico",
        ),
        ServizioEsterno(
            id="otlp", nome="Tracce OpenTelemetry (OTLP)", categoria="Infrastruttura", sezione=None,
            sonda=_sonda_otlp,
            come_fare=(
                "Serve un collettore OTLP (OpenTelemetry Collector, Jaeger, Tempo…) raggiungibile dall'API.",
                "Imposta TAROT_OTLP_ENDPOINT; senza collettore, TAROT_TRACING_ENABLED=false.",
            ),
            primo_link="https://opentelemetry.io/docs/collector/",
            dove_sta_il_segreto="Nessun segreto (ambiente).",
            costi="Gratis se self-hosted.",
            dove="automatico",
        ),
        ServizioEsterno(
            id="redis", nome="Redis", categoria="Infrastruttura", sezione=None,
            sonda=_sonda_redis,
            come_fare=(
                "Non serve: nessuna parte del sito lo usa (code e cache stanno in PostgreSQL o in memoria).",
                "Se un giorno servirà, si aggiunge con il suo Deployment e un'impostazione nuova.",
            ),
            primo_link="https://redis.io/",
            dove_sta_il_segreto="—",
            costi="—",
            dove="automatico",
        ),
        ServizioEsterno(
            id="database", nome="Database PostgreSQL", categoria="Infrastruttura", sezione=None,
            sonda=_sonda_database,
            come_fare=(
                "Il database sta sul server (k3s). La sua password è uno dei tre segreti che restano sul server: "
                "Secret `tarots-secrets`, chiavi `database-url` (indirizzo con la password) e `db-password`.",
                "Non si imposta dalla console: è la console a vivere nel database.",
            ),
            primo_link="https://www.postgresql.org/docs/current/",
            dove_sta_il_segreto="Sul server: Secret k8s `tarots-secrets`, chiavi `database-url` e `db-password`.",
            costi="Gratis (self-hosted sul server).",
            dove="server",
        ),
        ServizioEsterno(
            id="chiave_master", nome="Chiave master di cifratura", categoria="Infrastruttura", sezione=None,
            sonda=_sonda_chiave_master,
            come_fare=(
                "Una chiave Fernet che cifra tutte le chiavi e le password salvate dalla console (Stripe, posta, NAS, "
                "fornitori LLM, Google, Reddit, store). Sta solo sul server, mai nel database: un dump del database "
                "senza questa chiave non rivela nessun segreto.",
                "Si genera una volta sola (`Fernet.generate_key()`) e va nel Secret `tarots-secrets`, chiave "
                "`llm-provider-key`. Se la si perde o la si cambia, i segreti salvati in console vanno reinseriti.",
            ),
            primo_link="https://cryptography.io/en/latest/fernet/",
            dove_sta_il_segreto="Sul server: Secret k8s `tarots-secrets`, chiave `llm-provider-key`.",
            costi="Gratis.",
            dove="server",
        ),
        ServizioEsterno(
            id="segreti_interni", nome="Segreti interni (impronte degli IP e delle condivisioni)",
            categoria="Infrastruttura", sezione=None,
            sonda=_sonda_segreti_interni,
            come_fare=(
                "Nulla da fare: al primo avvio l'API genera da sola i segreti con cui calcola le impronte degli "
                "indirizzi IP (GDPR) e dei link condivisi, e li conserva cifrati nel database.",
                "Non si mostrano mai. Se il server ne dava già uno (TAROT_IP_HASH_SECRET, TAROT_CONDIVISIONE_SALE), "
                "vale quello, copiato nel database.",
            ),
            primo_link=None,
            dove_sta_il_segreto="Database, cifrati (segreti_sistema).",
            costi="Gratis.",
            dove="automatico",
        ),
        ServizioEsterno(
            id="dns", nome="Namecheap (dominio, DNS e posta in arrivo)", categoria="Infrastruttura", sezione=None,
            sonda=_sonda_manuale,
            come_fare=(
                "Namecheap è il registrar di tarots.chat e ne gestisce il DNS: un record per ogni sottodominio "
                "(niente wildcard) e il record TXT di Google per Search Console.",
                "La posta in arrivo a @tarots.chat la riceve Namecheap (record MX eforward1…5.registrar-servers.com) "
                "e la inoltra: tutte le caselle (*) vanno ad a.taini@gmail.com. Lo imposta l'operatore.",
                "Per cambiare l'inoltro: Domain List → Manage accanto a tarots.chat → Redirect Email → Add Forwarder.",
                "SPF, DKIM e DMARC (per la posta in uscita) si aggiungono qui, in Advanced DNS: lo stato lo mostra "
                "«Posta in uscita».",
                "Rinnovo del dominio: controlla la scadenza e il rinnovo automatico.",
            ),
            primo_link="https://ap.www.namecheap.com/domains/list/",
            dove_sta_il_segreto="Fuori dal sito: l'account Namecheap è dell'operatore.",
            costi="Il rinnovo annuale del dominio; l'inoltro della posta è incluso.",
        ),
        ServizioEsterno(
            id="npm", nome="Nginx Proxy Manager e Let's Encrypt", categoria="Infrastruttura", sezione=None,
            sonda=_sonda_manuale,
            come_fare=(
                "Sul server, Nginx Proxy Manager instrada ogni sottodominio verso il servizio giusto.",
                "Per ogni host chiedi il certificato Let's Encrypt (rinnovo automatico).",
            ),
            primo_link="https://nginxproxymanager.com/guide/",
            dove_sta_il_segreto="Fuori dal repo: l'utente amministratore di NPM sul server.",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="indexnow", nome="IndexNow (Bing, Yandex)", categoria="Strumenti", sezione="/seo",
            sonda=_sonda_indexnow,
            come_fare=(
                "Nessun account: si sceglie una chiave e la si pubblica in https://tarots.chat/<chiave>.txt.",
                "Imposta TAROT_INDEXNOW_CHIAVE; la notifica notturna avvisa i motori.",
            ),
            primo_link="https://www.indexnow.org/",
            dove_sta_il_segreto="Nessun segreto: il protocollo vuole la chiave pubblica (già nel rilascio).",
            costi="Gratis.",
            dove="automatico",
        ),
        ServizioEsterno(
            id="websub", nome="WebSub (feed del blog)", categoria="Strumenti", sezione="/seo",
            sonda=_sonda_websub,
            come_fare=(
                "Nessun account: si usa un hub pubblico (quello di Google).",
                "Imposta TAROT_WEBSUB_HUB con l'indirizzo dell'hub.",
            ),
            primo_link="https://pubsubhubbub.appspot.com/",
            dove_sta_il_segreto="Nessun segreto (già nel rilascio).",
            costi="Gratis.",
            dove="automatico",
        ),
        ServizioEsterno(
            id="litmedia", nome="LitMedia (immagini del blog)", categoria="Strumenti", sezione=None,
            sonda=_sonda_manuale,
            come_fare=(
                "Le immagini del blog le genera la skill «litmedia-skill» degli agenti, non il sito.",
                "La chiave sta nella configurazione della skill sul PC dell'operatore.",
            ),
            primo_link="https://www.litmedia.ai/",
            dove_sta_il_segreto="Fuori dal repo: configurazione della skill dell'operatore.",
            costi="A crediti, per immagine.",
        ),
        ServizioEsterno(
            id="chiavi_rest", nome="Chiavi REST degli agenti", categoria="Strumenti", sezione="/blog/chiavi",
            sonda=_sonda_chiavi_rest,
            come_fare=(
                "In «Blog → Chiavi» crea una chiave con gli ambiti necessari (si vede una volta sola).",
                "Mettila nella configurazione della skill che pubblica; revocala quando non serve più.",
            ),
            primo_link=None,
            dove_sta_il_segreto="Database: solo l'impronta. La chiave in chiaro sta negli agenti che la usano.",
            costi="Gratis.",
        ),
        ServizioEsterno(
            id="colab", nome="Google Colab (studi sugli analytics)", categoria="Strumenti", sezione="/analytics/studi",
            sonda=_sonda_colab,
            come_fare=(
                "In «Analytics → Studi» crea un token con scadenza e ambiti.",
                "Apri il notebook in Colab e incolla il token: esporta i dati e reimporta i risultati firmati.",
            ),
            primo_link="https://colab.research.google.com/",
            dove_sta_il_segreto="Database: solo l'impronta del token.",
            costi="Gratis (piano base di Colab).",
        ),
    ]
    return voci


REGISTRO: Tuple[ServizioEsterno, ...] = tuple(_registro())
PER_ID: Dict[str, ServizioEsterno] = {s.id: s for s in REGISTRO}


async def leggi_stato(session: AsyncSession, servizio: ServizioEsterno) -> Stato:
    """La sonda, protetta: un guasto di una sonda non deve svuotare la pagina."""
    try:
        return await servizio.sonda(session)
    except Exception as exc:  # noqa: BLE001 — la pagina mostra il guasto sulla sua voce
        return stato("errore", f"Lo stato non si legge ({type(exc).__name__}).")


def voce_json(servizio: ServizioEsterno, s: Stato) -> Dict[str, Any]:
    return {
        "id": servizio.id, "nome": servizio.nome, "categoria": servizio.categoria, "sezione": servizio.sezione,
        "stato": s["stato"], "dettaglio": s["dettaglio"], "come_fare": list(servizio.come_fare),
        "primo_link": servizio.primo_link, "dove_sta_il_segreto": servizio.dove_sta_il_segreto,
        "costi": servizio.costi, "verificabile": servizio.verifica is not None, "fase": servizio.fase,
        "nota": servizio.nota, "dove": servizio.dove_si_imposta, "dove_testo": DOVE[servizio.dove_si_imposta],
    }
