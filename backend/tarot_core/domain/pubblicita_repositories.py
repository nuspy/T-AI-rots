"""Gli spazi pubblicitari: lettura (con creazione al bisogno), scrittura con audit, e le viste per console e sito.

Due livelli, come in `config_models`:

- le **impostazioni generali** (`ImpostazioniPubblicita`, una riga): l'interruttore, il fornitore che riempie gli
  spazi, le caselle dei tre banner, le pagine escluse;
- i **fornitori** (`PubblicitaFornitore`, una riga ciascuno): i parametri pubblici e i dati dell'iscrizione.

Il catalogo dei fornitori (`FORNITORI`) è chiuso e sta qui: aggiungerne uno vuol dire dargli una voce nel catalogo,
la sua validazione dei parametri e la sua vista pubblica, e un sotto-tab nella console. Le tabelle non cambiano.

**Cosa esce verso il sito** (`vista_pubblica`): solo l'interruttore effettivo, le posizioni accese con il loro slot
e formato, le pagine escluse e i parametri di visualizzazione del fornitore. I dati di registrazione e i dettagli dei
pagamenti (in fondo al file) non escono mai.
"""
from __future__ import annotations

import copy
import re
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .config_models import ImpostazioniPubblicita, PubblicitaFornitore
from .repositories import AuditRepository

ID_RIGA = 1

#: Le tre posizioni di ogni pagina, nell'ordine in cui compaiono.
POSIZIONI = ("terzo", "due_terzi", "fine")

#: I formati di un annuncio AdSense (`data-ad-format`). `auto` lascia scegliere a Google la misura migliore.
FORMATI = ("auto", "rectangle", "horizontal", "vertical")

#: A che punto è l'iscrizione ad AdSense: solo un promemoria per chi amministra, non cambia il comportamento.
STATI_REGISTRAZIONE = ("non_iniziata", "ads_txt_verificato", "in_revisione", "approvato", "rifiutato")

#: I fornitori che sanno riempire gli spazi. Oggi solo Google AdSense; affiliazioni e spazi diretti verranno qui.
FORNITORI: Dict[str, Dict[str, str]] = {
    "google": {"etichetta": "Google AdSense"},
}

#: `ca-pub-` e le cifre dell'account (16 oggi; si accetta un intervallo per non rifiutare un formato futuro).
EDITORE = re.compile(r"^ca-pub-\d{10,20}$")
#: L'ID di un'unità pubblicitaria: solo cifre (10 oggi).
SLOT = re.compile(r"^\d{6,20}$")
#: La riga di `ads.txt` per AdSense: `f08c47fec0942fa0` è l'ID di certificazione TAG di Google, uguale per tutti.
RIGA_ADS_TXT = "google.com, {pub}, DIRECT, f08c47fec0942fa0"

POSIZIONI_PREDEFINITE = {p: True for p in POSIZIONI}


def parametri_predefiniti_google() -> Dict[str, Any]:
    return {
        "editore": "",
        "slot": {p: "" for p in POSIZIONI},
        "formato": {p: "auto" for p in POSIZIONI},
        #: `data-full-width-responsive`: sul telefono l'annuncio può prendere tutta la larghezza.
        "responsive": True,
        #: `data-adtest="on"`: annunci di prova, non conteggiati (per le prove in locale).
        "prova": False,
        #: Annunci personalizzati. Spento: si chiedono annunci non personalizzati anche a chi ha acconsentito.
        "personalizzati": False,
    }


def registrazione_predefinita() -> Dict[str, Any]:
    return {
        "email": "",
        "titolare": "",
        "id_cliente": "",
        "data_iscrizione": None,
        "stato": "non_iniziata",
        "note": "",
    }


class ErrorePubblicita(ValueError):
    """Un valore che la console non può salvare (formato sbagliato, accensione senza ID editore)."""


# ---- lettura ---------------------------------------------------------------------------------------


async def generali(session: AsyncSession) -> ImpostazioniPubblicita:
    """La riga generale, creata spenta se manca."""
    riga = await session.get(ImpostazioniPubblicita, ID_RIGA)
    if riga is None:
        riga = ImpostazioniPubblicita(
            id=ID_RIGA, attiva=False, fornitore="google", posizioni=dict(POSIZIONI_PREDEFINITE), pagine_escluse=[],
        )
        session.add(riga)
        await session.flush()
    return riga


async def fornitore(session: AsyncSession, nome: str) -> PubblicitaFornitore:
    """La riga di un fornitore del catalogo, creata coi valori predefiniti se manca."""
    if nome not in FORNITORI:
        raise ErrorePubblicita(f"Fornitore sconosciuto: {nome}")
    riga = await session.get(PubblicitaFornitore, nome)
    if riga is None:
        riga = PubblicitaFornitore(
            fornitore=nome, parametri=parametri_predefiniti_google(), registrazione=registrazione_predefinita(),
        )
        session.add(riga)
        await session.flush()
    return riga


def _parametri_google(riga: Optional[PubblicitaFornitore]) -> Dict[str, Any]:
    """I parametri completi: quelli salvati sopra i predefiniti (una chiave nuova non rompe una riga vecchia)."""
    base = parametri_predefiniti_google()
    salvati = (riga.parametri if riga else None) or {}
    for chiave, valore in salvati.items():
        if chiave in ("slot", "formato") and isinstance(valore, dict):
            base[chiave].update({p: valore[p] for p in POSIZIONI if p in valore})
        elif chiave in base:
            base[chiave] = valore
    return base


def _registrazione(riga: Optional[PubblicitaFornitore]) -> Dict[str, Any]:
    base = registrazione_predefinita()
    base.update({k: v for k, v in ((riga.registrazione if riga else None) or {}).items() if k in base})
    return base


def _posizioni(riga: ImpostazioniPubblicita) -> Dict[str, bool]:
    salvate = riga.posizioni or {}
    return {p: bool(salvate.get(p, True)) for p in POSIZIONI}


def google_pronto(parametri: Dict[str, Any]) -> bool:
    """AdSense può riempire gli spazi: c'è un ID editore valido."""
    return bool(EDITORE.match(parametri.get("editore") or ""))


def ads_txt(parametri: Dict[str, Any]) -> Optional[str]:
    """Il contenuto di `ads.txt`, o `None` senza ID editore. Vale anche a pubblicità spenta: Google lo controlla
    durante la verifica del sito, prima che gli spazi si accendano."""
    editore = parametri.get("editore") or ""
    if not EDITORE.match(editore):
        return None
    return RIGA_ADS_TXT.format(pub=editore.removeprefix("ca-")) + "\n"


def vista_generale(riga: ImpostazioniPubblicita) -> Dict[str, Any]:
    return {
        "attiva": riga.attiva,
        "fornitore": riga.fornitore,
        "posizioni": _posizioni(riga),
        "pagine_escluse": list(riga.pagine_escluse or []),
    }


def vista_google(riga: Optional[PubblicitaFornitore]) -> Dict[str, Any]:
    parametri = _parametri_google(riga)
    return {
        "etichetta": FORNITORI["google"]["etichetta"],
        "parametri": parametri,
        "registrazione": _registrazione(riga),
        "pagamenti": _pagamenti(riga),
        "pronto": google_pronto(parametri),
        "ads_txt": ads_txt(parametri),
    }


def vista_pubblica(gen: ImpostazioniPubblicita, google: Optional[PubblicitaFornitore]) -> Dict[str, Any]:
    """Ciò che serve al sito, e nient'altro. Spenta (`{"attiva": false}`) se l'interruttore è giù, se il fornitore
    non è pronto o se nessuna posizione accesa ha il suo slot."""
    spenta: Dict[str, Any] = {"attiva": False}
    if not gen.attiva or gen.fornitore != "google":
        return spenta
    parametri = _parametri_google(google)
    if not google_pronto(parametri):
        return spenta
    caselle = _posizioni(gen)
    posizioni = {
        p: {"slot": parametri["slot"][p], "formato": parametri["formato"].get(p) or "auto"}
        for p in POSIZIONI
        if caselle[p] and SLOT.match(parametri["slot"].get(p) or "")
    }
    if not posizioni:
        return spenta
    return {
        "attiva": True,
        "fornitore": "google",
        "posizioni": posizioni,
        "pagine_escluse": list(gen.pagine_escluse or []),
        "google": {
            "editore": parametri["editore"],
            "responsive": bool(parametri["responsive"]),
            "prova": bool(parametri["prova"]),
            "personalizzati": bool(parametri["personalizzati"]),
        },
    }


# ---- scrittura -------------------------------------------------------------------------------------


def _pulisci_percorso(valore: str) -> str:
    p = valore.strip()
    if not p:
        return ""
    if not p.startswith("/"):
        raise ErrorePubblicita(f"Una pagina esclusa è un indirizzo che comincia con «/»: «{p}»")
    if len(p) > 200 or any(c.isspace() for c in p):
        raise ErrorePubblicita(f"Indirizzo non valido: «{p}»")
    return p.rstrip("/") or "/"


async def aggiorna_generali(
    session: AsyncSession, campi: Dict[str, Any], *, attore_id: int, ip: str | None = None,
) -> ImpostazioniPubblicita:
    """Aggiorna i campi presenti; accendere senza un fornitore pronto è un errore (meglio dirlo subito che
    accendere un interruttore che non fa nulla)."""
    riga = await generali(session)
    prima = vista_generale(riga)

    if campi.get("fornitore") is not None:
        if campi["fornitore"] not in FORNITORI:
            raise ErrorePubblicita(f"Fornitore sconosciuto: {campi['fornitore']}")
        riga.fornitore = campi["fornitore"]
    if campi.get("posizioni") is not None:
        attuali = _posizioni(riga)
        attuali.update({p: bool(v) for p, v in campi["posizioni"].items() if p in POSIZIONI})
        riga.posizioni = attuali
    if campi.get("pagine_escluse") is not None:
        pulite = [x for x in (_pulisci_percorso(v) for v in campi["pagine_escluse"]) if x]
        riga.pagine_escluse = list(dict.fromkeys(pulite))
    if campi.get("attiva") is not None:
        if campi["attiva"]:
            parametri = _parametri_google(await fornitore(session, riga.fornitore))
            if not google_pronto(parametri):
                raise ErrorePubblicita("Per accendere la pubblicità serve prima l'ID editore (ca-pub-…) di AdSense.")
        riga.attiva = bool(campi["attiva"])
    riga.updated_by = attore_id

    dopo = vista_generale(riga)
    if prima != dopo:
        await AuditRepository(session).record(
            action="pubblicita.impostazioni", actor_id=attore_id, target_type="impostazioni_pubblicita",
            target_id=str(ID_RIGA), before=prima, after=dopo, ip=ip,
        )
    return riga


def _testo(valore: Any, massimo: int) -> str:
    return str(valore or "").strip()[:massimo]


async def aggiorna_google(
    session: AsyncSession, parametri: Optional[Dict[str, Any]], registrazione: Optional[Dict[str, Any]], *,
    attore_id: int, ip: str | None = None,
) -> PubblicitaFornitore:
    """Aggiorna i parametri e/o i dati d'iscrizione di AdSense; solo le chiavi presenti."""
    riga = await fornitore(session, "google")
    prima = vista_google(riga)
    nuovi = copy.deepcopy(prima["parametri"])
    reg = copy.deepcopy(prima["registrazione"])

    if parametri:
        if "editore" in parametri and parametri["editore"] is not None:
            editore = parametri["editore"].strip().lower()
            if editore.startswith("pub-"):
                editore = f"ca-{editore}"
            if editore and not EDITORE.match(editore):
                raise ErrorePubblicita(
                    "L'ID editore ha la forma «ca-pub-» seguita da 16 cifre "
                    "(AdSense → Account → Informazioni account).")
            nuovi["editore"] = editore
        for posizione, slot in (parametri.get("slot") or {}).items():
            if posizione not in POSIZIONI or slot is None:
                continue
            slot = str(slot).strip()
            if slot and not SLOT.match(slot):
                raise ErrorePubblicita(
                    f"L'ID dello slot «{posizione}» è un numero (AdSense → Annunci → Per unità pubblicitaria).")
            nuovi["slot"][posizione] = slot
        for posizione, formato in (parametri.get("formato") or {}).items():
            if posizione not in POSIZIONI or formato is None:
                continue
            if formato not in FORMATI:
                raise ErrorePubblicita(f"Formato sconosciuto: {formato}")
            nuovi["formato"][posizione] = formato
        for chiave in ("responsive", "prova", "personalizzati"):
            if parametri.get(chiave) is not None:
                nuovi[chiave] = bool(parametri[chiave])

    if registrazione:
        for chiave, massimo in (("email", 200), ("titolare", 200), ("id_cliente", 60), ("note", 2000)):
            if registrazione.get(chiave) is not None:
                reg[chiave] = _testo(registrazione[chiave], massimo)
        if "data_iscrizione" in registrazione:
            reg["data_iscrizione"] = registrazione["data_iscrizione"] or None
        if registrazione.get("stato") is not None:
            if registrazione["stato"] not in STATI_REGISTRAZIONE:
                raise ErrorePubblicita(f"Stato sconosciuto: {registrazione['stato']}")
            reg["stato"] = registrazione["stato"]

    riga.parametri = nuovi
    #: I dettagli dei pagamenti stanno nella stessa colonna, sotto la loro chiave: salvare l'iscrizione non li tocca.
    riga.registrazione = {**reg, "pagamenti": _pagamenti(riga)}
    riga.updated_by = attore_id
    if (nuovi, reg) != (prima["parametri"], prima["registrazione"]):
        await AuditRepository(session).record(
            action="pubblicita.google", actor_id=attore_id, target_type="pubblicita_fornitore", target_id="google",
            before={"parametri": prima["parametri"], "registrazione": prima["registrazione"]},
            after={"parametri": nuovi, "registrazione": reg}, ip=ip,
        )
    return riga


async def leggi_pubblica(session: AsyncSession) -> Dict[str, Any]:
    """La vista del sito, senza scrivere nulla: chi non ha mai aperto la console vede la pubblicità spenta."""
    gen = await session.get(ImpostazioniPubblicita, ID_RIGA)
    if gen is None:
        return {"attiva": False}
    return vista_pubblica(gen, await session.get(PubblicitaFornitore, gen.fornitore))


async def leggi_ads_txt(session: AsyncSession) -> Optional[str]:
    return ads_txt(_parametri_google(await session.get(PubblicitaFornitore, "google")))


# ---- i dettagli dei pagamenti di AdSense (solo appunti della console) --------------------------------------------
#
# Il profilo pagamenti vero sta in AdSense: qui se ne tiene un promemoria per chi amministra, che non serve né a pagare
# né a incassare. Stanno in `pubblicita_fornitori.registrazione["pagamenti"]` (niente colonna nuova, niente
# migrazione): come la registrazione, nessun endpoint pubblico li espone. Del conto si tengono **solo le ultime 4
# cifre**: un IBAN o un numero di carta interi non si salvano da nessuna parte, nemmeno nelle note.

TIPI_PROFILO = ("individuale", "azienda")
METODI_PAGAMENTO = ("bonifico", "bonifico_internazionale", "altro")
STATI_FISCALI = ("non_inviate", "inviate", "accettate")
MODULI_FISCALI = ("W-8BEN", "W-8BEN-E", "W-9", "altro")
STATI_PIN = ("non_ricevuto", "ricevuto", "verificato")

#: Le ultime 4 cifre (o caratteri) del conto: niente di più lungo.
ULTIME_4 = re.compile(r"^[0-9A-Za-z]{4}$")
VALUTA = re.compile(r"^[A-Z]{3}$")
#: Un IBAN intero (due lettere, due cifre di controllo, 11-30 caratteri), anche scritto a gruppi.
IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b", re.IGNORECASE)
#: Un numero di carta o di conto lungo: 13 o più cifre di fila, anche separate da spazi o trattini.
NUMERO_LUNGO = re.compile(r"(?:\d[ -]?){13,}")
#: L'ID del profilo pagamenti di AdSense: 12 cifre a gruppi di 4 (`1234-5678-9012`).
ID_PROFILO = re.compile(r"^\d{4}(?:[- ]?\d{4}){2}$")


def pagamenti_predefiniti() -> Dict[str, Any]:
    return {
        "id_profilo": "",
        "beneficiario": "",
        "tipo_profilo": "individuale",
        "indirizzo": "",
        "metodo": "bonifico",
        "banca": "",
        "conto_ultime4": "",
        "soglia": None,
        "valuta": "EUR",
        "stato_fiscale": "non_inviate",
        "modulo_fiscale": "W-8BEN",
        "stato_pin": "non_ricevuto",
        "ultimo_pagamento": None,
        "note": "",
    }


def _pagamenti(riga: Optional[PubblicitaFornitore]) -> Dict[str, Any]:
    base = pagamenti_predefiniti()
    salvati = ((riga.registrazione if riga else None) or {}).get("pagamenti") or {}
    base.update({k: v for k, v in salvati.items() if k in base})
    return base


def _senza_numeri_di_conto(campo: str, testo: str) -> str:
    """Rifiuta un testo libero che contiene un IBAN o un numero di carta/conto intero."""
    if IBAN.search(testo) or NUMERO_LUNGO.search(testo):
        raise ErrorePubblicita(
            f"«{campo}» sembra contenere un IBAN o un numero di carta o di conto intero: qui si tengono solo le "
            "ultime 4 cifre, nel loro campo.")
    return testo


def _scelta(valore: Any, ammessi: tuple, nome: str) -> str:
    if valore not in ammessi:
        raise ErrorePubblicita(f"{nome} sconosciuto: {valore}")
    return valore


async def aggiorna_pagamenti_google(
    session: AsyncSession, campi: Dict[str, Any], *, attore_id: int, ip: str | None = None,
) -> PubblicitaFornitore:
    """Aggiorna i dettagli dei pagamenti (solo le chiavi presenti), con audit del prima e del dopo."""
    riga = await fornitore(session, "google")
    prima = _pagamenti(riga)
    nuovi = copy.deepcopy(prima)

    if campi.get("id_profilo") is not None:
        profilo = _testo(campi["id_profilo"], 40)
        if profilo and not ID_PROFILO.match(profilo):
            raise ErrorePubblicita(
                "L'ID del profilo pagamenti ha 12 cifre a gruppi di 4 (AdSense → Pagamenti → Impostazioni).")
        nuovi["id_profilo"] = profilo
    for chiave, massimo, nome in (
        ("beneficiario", 200, "Beneficiario"),
        ("indirizzo", 500, "Indirizzo"), ("banca", 120, "Banca"), ("note", 2000, "Note"),
    ):
        if campi.get(chiave) is not None:
            nuovi[chiave] = _senza_numeri_di_conto(nome, _testo(campi[chiave], massimo))
    if campi.get("conto_ultime4") is not None:
        ultime = re.sub(r"[\s-]", "", str(campi["conto_ultime4"]))
        if ultime and not ULTIME_4.match(ultime):
            raise ErrorePubblicita(
                "Del conto si tengono solo le ultime 4 cifre: un IBAN o un numero di conto interi non si salvano qui.")
        nuovi["conto_ultime4"] = ultime.upper()
    if campi.get("tipo_profilo") is not None:
        nuovi["tipo_profilo"] = _scelta(campi["tipo_profilo"], TIPI_PROFILO, "Tipo di profilo")
    if campi.get("metodo") is not None:
        nuovi["metodo"] = _scelta(campi["metodo"], METODI_PAGAMENTO, "Metodo di pagamento")
    if campi.get("stato_fiscale") is not None:
        nuovi["stato_fiscale"] = _scelta(campi["stato_fiscale"], STATI_FISCALI, "Stato delle informazioni fiscali")
    if campi.get("modulo_fiscale") is not None:
        nuovi["modulo_fiscale"] = _scelta(campi["modulo_fiscale"], MODULI_FISCALI, "Modulo fiscale")
    if campi.get("stato_pin") is not None:
        nuovi["stato_pin"] = _scelta(campi["stato_pin"], STATI_PIN, "Stato del PIN")
    if "soglia" in campi:
        nuovi["soglia"] = campi["soglia"]
    if campi.get("valuta") is not None:
        valuta = str(campi["valuta"]).strip().upper()
        if not VALUTA.match(valuta):
            raise ErrorePubblicita("La valuta è un codice di tre lettere (EUR, USD, GBP…).")
        nuovi["valuta"] = valuta
    if "ultimo_pagamento" in campi:
        nuovi["ultimo_pagamento"] = campi["ultimo_pagamento"] or None

    riga.registrazione = {**_registrazione(riga), "pagamenti": nuovi}
    riga.updated_by = attore_id
    if nuovi != prima:
        await AuditRepository(session).record(
            action="pubblicita.google.pagamenti", actor_id=attore_id, target_type="pubblicita_fornitore",
            target_id="google", before=prima, after=nuovi, ip=ip,
        )
    return riga
