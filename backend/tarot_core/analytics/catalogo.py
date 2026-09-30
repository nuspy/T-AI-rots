"""Il catalogo delle interrogazioni di TAROTS chat (v8): cosa si può chiedere, e a quali tabelle.

Sei sorgenti. Tre sono di `lanterna` (visite, eventi, il riepilogo giornaliero per la storia lunga);
tre sono le tabelle di business, che restano la verità su letture e soldi (utenti, letture,
acquisti, ordini) e si arricchiscono con l'attribuzione di `an_utenti` (primo canale e campagna).

Regole:
- mai contenuti: né la domanda di una lettura, né il testo, né email o nomi;
- il campo «trans» del profilo non entra in nessuna dimensione;
- il genere libero (`gender_custom`) diventa «altro»;
- età, genere, città sono dimensioni **personali**: soglia k per AI ed export.
"""
from __future__ import annotations

from sqlalchemy import DateTime, Integer, Numeric, String, and_, case, cast, exists, func, literal, or_, select

from lanterna.interroga import Dimensione, Misura, Sorgente

from ..domain.analytics_models import TABELLE
from ..domain.billing_models import PaymentCheckout, Plan
from ..domain.models import Reading, User
from ..domain.ordini_models import Ordine

S = TABELLE.sessioni
E = TABELLE.eventi
U = TABELLE.utenti
G = TABELLE.giornaliero
UT = User.__table__
R = Reading.__table__
C = PaymentCheckout.__table__
P = Plan.__table__
O = Ordine.__table__

ND = "(n.d.)"


def arrotonda(espressione, cifre: int):
    """`round` con le cifre esiste in PostgreSQL solo per `numeric`, non per `double precision`."""
    return func.round(cast(espressione, Numeric), cifre)


def _nd(espressione):
    return func.coalesce(espressione, literal(ND))


def fascia_eta(nascita, riferimento=None):
    """Fasce d'età all'istante della riga (o adesso)."""
    anni = func.date_part("year", func.age(riferimento if riferimento is not None else func.now(), nascita))
    return case(
        (nascita.is_(None), literal(ND)),
        (anni < 18, literal("<18")),
        (anni < 25, literal("18-24")),
        (anni < 35, literal("25-34")),
        (anni < 45, literal("35-44")),
        (anni < 55, literal("45-54")),
        (anni < 65, literal("55-64")),
        else_=literal("65+"),
    )


def genere(colonna):
    return case(
        (colonna.in_(["uomo", "donna"]), colonna),
        (colonna.is_(None), literal(ND)),
        else_=literal("altro"),
    )


# ---- dimensioni riusate --------------------------------------------------------------------

def _dim_attribuzione(u=U):
    return {
        "primo_canale": Dimensione("Primo canale", lambda: _nd(u.c.primo_canale), descrizione="Canale del primo contatto"),
        "prima_campagna": Dimensione("Prima campagna", lambda: _nd(u.c.prima_campagna)),
        "prima_sorgente": Dimensione("Prima sorgente UTM", lambda: _nd(u.c.prima_sorgente)),
        "primo_referrer": Dimensione("Primo sito di provenienza", lambda: _nd(u.c.primo_referrer_dominio)),
    }


def _dim_persona(ut=UT, riferimento=None):
    return {
        "fascia_eta": Dimensione("Fascia d'età", lambda: fascia_eta(ut.c.birth_date, riferimento), personale=True),
        "genere": Dimensione("Genere", lambda: genere(ut.c.gender), personale=True),
        "lingua_account": Dimensione("Lingua dell'account", lambda: _nd(ut.c.locale)),
        "invitato": Dimensione("Arrivato con un invito", lambda: case((ut.c.referred_by.is_not(None), literal("sì")), else_=literal("no"))),
    }


# ---- ritorni --------------------------------------------------------------------------------------
#
# Senza cookie un ritorno si riconosce solo in due casi: l'account (chi ha fatto l'accesso) o
# l'identificativo esteso (chi ha accettato i cookie). Per tutti gli altri il tipo di visitatore è
# «non noto», e lo si dice invece di contarli come nuovi.


def _stesso_visitatore(s2):
    return or_(
        and_(S.c.utente_id.is_not(None), s2.c.utente_id == S.c.utente_id),
        and_(S.c.visitatore_esteso.is_not(None), s2.c.visitatore_esteso == S.c.visitatore_esteso),
    )


def _visita_precedente():
    s2 = S.alias("precedente")
    return select(func.max(s2.c.inizio)).where(_stesso_visitatore(s2), s2.c.inizio < S.c.inizio).scalar_subquery()


def _di_ritorno():
    s2 = S.alias("precedente")
    return exists().where(_stesso_visitatore(s2), s2.c.inizio < S.c.inizio)


def _tipo_visitatore():
    return case(
        (_di_ritorno(), literal("di ritorno")),
        (or_(S.c.utente_id.is_not(None), S.c.visitatore_esteso.is_not(None)), literal("nuovo")),
        else_=literal("non noto (senza cookie né accesso)"),
    )


VISITE = Sorgente(
    etichetta="Visite",
    descrizione="Una riga per sessione (30 minuti di inattività la chiudono). «Visitatori» somma gli "
    "univoci di ogni giorno: senza cookie, lo stesso browser in due giorni conta due volte.",
    da=lambda: S,
    tempo=lambda: S.c.inizio,
    persone=lambda: func.count(func.distinct(S.c.visitatore_giorno)),
    misure={
        "sessioni": Misura("Sessioni", lambda: func.count()),
        "visitatori": Misura("Visitatori (univoci giornalieri)", lambda: func.count(func.distinct(S.c.visitatore_giorno))),
        "utenti": Misura("Utenti registrati", lambda: func.count(func.distinct(S.c.utente_id))),
        "pagine": Misura("Pagine viste", lambda: func.coalesce(func.sum(S.c.pagine), 0)),
        "pagine_per_sessione": Misura("Pagine per sessione", lambda: arrotonda(func.avg(S.c.pagine), 2), "decimale"),
        "tempo_medio": Misura("Tempo attivo medio", lambda: arrotonda(func.avg(S.c.tempo_attivo_ms) / 1000.0, 1), "secondi"),
        "tasso_coinvolgimento": Misura(
            "Sessioni coinvolte", lambda: arrotonda(func.avg(cast(S.c.coinvolta, Integer)), 4), "percento",
            "Più di una pagina, o 10 secondi attivi, o un'azione",
        ),
        "rimbalzo": Misura("Rimbalzo", lambda: arrotonda(1 - func.avg(cast(S.c.coinvolta, Integer)), 4), "percento"),
        "sessioni_estese": Misura(
            "Sessioni col consenso", lambda: func.count(S.c.visitatore_esteso),
            descrizione="Il campione su cui si misurano i ritorni",
        ),
        "sessioni_di_ritorno": Misura(
            "Sessioni di ritorno", lambda: func.count().filter(_di_ritorno()),
            descrizione="Di chi era già venuto (riconoscibile solo con l'accesso o i cookie accettati)",
        ),
        "giorni_tra_visite": Misura(
            "Giorni medi dalla visita precedente",
            lambda: arrotonda(func.avg(func.extract("epoch", S.c.inizio - _visita_precedente()) / 86400.0), 1),
            "decimale", "Solo per i ritorni riconoscibili",
        ),
    },
    dimensioni={
        "tipo_visitatore": Dimensione("Nuovo o di ritorno", _tipo_visitatore),
        "canale": Dimensione("Canale", lambda: S.c.canale),
        "referrer": Dimensione("Sito di provenienza", lambda: _nd(S.c.referrer_dominio)),
        "campagna": Dimensione("Campagna", lambda: _nd(S.c.utm_campagna)),
        "sorgente_utm": Dimensione("Sorgente UTM", lambda: _nd(S.c.utm_sorgente)),
        "mezzo_utm": Dimensione("Mezzo UTM", lambda: _nd(S.c.utm_mezzo)),
        "contenuto_utm": Dimensione("Contenuto UTM", lambda: _nd(S.c.utm_contenuto)),
        "paese": Dimensione("Paese", lambda: _nd(S.c.paese)),
        "regione": Dimensione("Regione", lambda: _nd(S.c.regione)),
        "citta": Dimensione("Città", lambda: _nd(S.c.citta), personale=True, descrizione="Stima dall'IP, spesso del fornitore"),
        "dispositivo": Dimensione("Dispositivo", lambda: S.c.dispositivo),
        "browser": Dimensione("Browser", lambda: S.c.browser),
        "so": Dimensione("Sistema operativo", lambda: S.c.so),
        "lingua": Dimensione("Lingua", lambda: _nd(S.c.lingua)),
        "ingresso": Dimensione("Pagina d'ingresso", lambda: _nd(S.c.ingresso)),
        "uscita": Dimensione("Pagina d'uscita", lambda: _nd(S.c.uscita)),
        "registrato": Dimensione("Registrato", lambda: case((S.c.utente_id.is_not(None), literal("sì")), else_=literal("no"))),
    },
)

EVENTI = Sorgente(
    etichetta="Eventi",
    descrizione="Ogni azione misurata: pagine viste, fasi della lettura, click, acquisti. Le proprietà "
    "degli eventi si usano come dimensioni con «prop:<nome>» (es. prop:stesa, prop:fase).",
    da=lambda: E.outerjoin(S, S.c.id == E.c.sessione_id),
    tempo=lambda: E.c.ts,
    persone=lambda: func.count(func.distinct(func.coalesce(cast(E.c.utente_id, String), S.c.visitatore_giorno))),
    proprieta=lambda chiave: _nd(E.c.proprieta[chiave].astext),
    misure={
        "eventi": Misura("Eventi", lambda: func.count()),
        "sessioni": Misura("Sessioni", lambda: func.count(func.distinct(E.c.sessione_id))),
        "utenti": Misura("Utenti registrati", lambda: func.count(func.distinct(E.c.utente_id))),
        "visitatori": Misura("Visitatori (univoci giornalieri)", lambda: func.count(func.distinct(S.c.visitatore_giorno))),
        "valore": Misura("Valore", lambda: func.coalesce(func.sum(E.c.valore_centesimi), 0) / 100.0, "euro"),
        "durata_media": Misura("Durata attiva media", lambda: arrotonda(func.avg(E.c.durata_ms) / 1000.0, 1), "secondi"),
    },
    dimensioni={
        "nome": Dimensione("Evento", lambda: E.c.nome),
        "percorso": Dimensione("Pagina", lambda: _nd(E.c.percorso)),
        "origine": Dimensione("Origine", lambda: E.c.origine),
        "lingua": Dimensione("Lingua", lambda: _nd(func.coalesce(E.c.lingua, S.c.lingua))),
        "canale": Dimensione("Canale", lambda: _nd(S.c.canale)),
        "campagna": Dimensione("Campagna", lambda: _nd(S.c.utm_campagna)),
        "paese": Dimensione("Paese", lambda: _nd(S.c.paese)),
        "dispositivo": Dimensione("Dispositivo", lambda: _nd(S.c.dispositivo)),
        "registrato": Dimensione("Registrato", lambda: case((E.c.utente_id.is_not(None), literal("sì")), else_=literal("no"))),
    },
)

RIEPILOGO = Sorgente(
    etichetta="Riepilogo giornaliero",
    descrizione="Totali anonimi per giorno, conservati per sempre: la storia oltre la conservazione del "
    "dettaglio. Aggiornato ogni notte (il giorno in corso non c'è).",
    da=lambda: G,
    # Mezzanotte italiana del giorno, come istante: confrontabile con i limiti delle interrogazioni.
    tempo=lambda: func.timezone("Europe/Rome", cast(G.c.giorno, DateTime)),
    misure={
        "eventi": Misura("Eventi", lambda: func.coalesce(func.sum(G.c.eventi), 0)),
        "sessioni": Misura("Sessioni (somma per gruppo)", lambda: func.coalesce(func.sum(G.c.sessioni), 0)),
        "visitatori": Misura("Visitatori (somma per gruppo)", lambda: func.coalesce(func.sum(G.c.visitatori), 0)),
        "valore": Misura("Valore", lambda: func.coalesce(func.sum(G.c.valore_centesimi), 0) / 100.0, "euro"),
    },
    dimensioni={
        "nome": Dimensione("Evento", lambda: G.c.nome),
        "percorso": Dimensione("Pagina", lambda: G.c.percorso),
        "canale": Dimensione("Canale", lambda: G.c.canale),
        "campagna": Dimensione("Campagna", lambda: G.c.campagna),
        "paese": Dimensione("Paese", lambda: G.c.paese),
        "dispositivo": Dimensione("Dispositivo", lambda: G.c.dispositivo),
        "lingua": Dimensione("Lingua", lambda: G.c.lingua),
        "registrato": Dimensione("Registrato", lambda: case((G.c.registrato, literal("sì")), else_=literal("no"))),
    },
)

_UTENTI_ATTIVI = and_(UT.c.deleted_at.is_(None))

UTENTI = Sorgente(
    etichetta="Utenti",
    descrizione="Gli iscritti, per data d'iscrizione. Attribuzione (primo canale, campagna) solo per chi "
    "si è iscritto da quando esistono gli analytics e non si è opposto.",
    da=lambda: UT.outerjoin(U, U.c.utente_id == UT.c.id),
    tempo=lambda: UT.c.created_at,
    dove=lambda: _UTENTI_ATTIVI,
    persone=lambda: func.count(),
    misure={
        "utenti": Misura("Iscritti", lambda: func.count()),
        "eta_media": Misura("Età media", lambda: arrotonda(func.avg(func.date_part("year", func.age(UT.c.birth_date))), 1), "decimale"),
        "attivi_30g": Misura(
            "Attivi negli ultimi 30 giorni",
            lambda: func.count().filter(U.c.ultimo_accesso > func.now() - func.make_interval(0, 0, 0, 30)),
        ),
        "giorni_attivi_medi": Misura("Giorni attivi medi", lambda: arrotonda(func.avg(U.c.giorni_attivi), 1), "decimale"),
        "visite_prima": Misura(
            "Visite prima dell'iscrizione (media)", lambda: arrotonda(func.avg(U.c.visite_prima_registrazione), 1), "decimale",
            "Solo per chi ha dato il consenso del banner prima di iscriversi",
        ),
    },
    dimensioni={
        **_dim_persona(),
        **_dim_attribuzione(),
        "paese": Dimensione(
            "Paese (ultima visita)", lambda: _nd(
                select(S.c.paese).where(S.c.utente_id == UT.c.id, S.c.paese.is_not(None))
                .order_by(S.c.inizio.desc()).limit(1).scalar_subquery()
            ),
            descrizione="Dall'IP dell'ultima visita con l'accesso fatto; n.d. per chi si è opposto",
        ),
        "visite_prima_fascia": Dimensione(
            "Visite prima di iscriversi", lambda: case(
                (U.c.visite_prima_registrazione.is_(None), literal("non noto (senza cookie)")),
                (U.c.visite_prima_registrazione <= 1, literal("1 (al primo arrivo)")),
                (U.c.visite_prima_registrazione <= 3, literal("2-3")),
                (U.c.visite_prima_registrazione <= 9, literal("4-9")),
                else_=literal("10 o più"),
            ),
            descrizione="Solo per chi aveva accettato i cookie prima di iscriversi",
        ),
    },
)

LETTURE = Sorgente(
    etichetta="Letture",
    descrizione="Le letture aperte, per data di apertura. Anonime comprese (senza età e genere).",
    da=lambda: R.outerjoin(UT, UT.c.id == R.c.owner_id).outerjoin(U, U.c.utente_id == R.c.owner_id),
    tempo=lambda: R.c.created_at,
    persone=lambda: func.count(func.distinct(func.coalesce(cast(R.c.owner_id, String), R.c.anon_id))),
    misure={
        "letture": Misura("Letture aperte", lambda: func.count()),
        "completate": Misura("Completate", lambda: func.count().filter(R.c.status == "completata")),
        "tasso_completamento": Misura(
            "Tasso di completamento",
            lambda: arrotonda(func.count().filter(R.c.status == "completata") * 1.0 / func.nullif(func.count(), 0), 4),
            "percento",
        ),
        "lettori": Misura("Lettori (registrati)", lambda: func.count(func.distinct(R.c.owner_id))),
        "avverate": Misura(
            "«Si è avverato» (sì o in parte)", lambda: func.count().filter(R.c.feedback.in_(["si", "in_parte"])),
        ),
        "con_feedback": Misura("Con risposta al «si è avverato?»", lambda: func.count(R.c.feedback)),
    },
    dimensioni={
        "stesa": Dimensione("Stesa", lambda: R.c.spread_id),
        "consumo": Dimensione("Pagata con", lambda: R.c.consumo),
        "lingua": Dimensione("Lingua della lettura", lambda: R.c.lang),
        "stato": Dimensione("Stato", lambda: R.c.status),
        "esito_guardia": Dimensione("Esito del controllo", lambda: _nd(R.c.guard_outcome)),
        "feedback": Dimensione("Si è avverato?", lambda: _nd(R.c.feedback)),
        "manuale": Dimensione("Mazzo fisico", lambda: case((R.c.manuale, literal("sì")), else_=literal("no"))),
        "anonima": Dimensione("Anonima", lambda: case((R.c.owner_id.is_(None), literal("sì")), else_=literal("no"))),
        **_dim_persona(riferimento=R.c.created_at),
        **_dim_attribuzione(),
    },
)

ACQUISTI = Sorgente(
    etichetta="Acquisti",
    descrizione="Pacchetti di crediti e abbonamenti pagati (i rinnovi automatici non sono ancora qui), per "
    "data di pagamento. Importi in euro, dopo gli sconti.",
    da=lambda: C.join(P, P.c.id == C.c.plan_id).join(UT, UT.c.id == C.c.user_id).outerjoin(U, U.c.utente_id == C.c.user_id),
    tempo=lambda: C.c.completed_at,
    dove=lambda: C.c.status == "pagato",
    persone=lambda: func.count(func.distinct(C.c.user_id)),
    misure={
        "acquisti": Misura("Acquisti", lambda: func.count()),
        "ricavi": Misura("Ricavi", lambda: func.coalesce(func.sum(C.c.importo), 0) / 100.0, "euro"),
        "clienti": Misura("Clienti", lambda: func.count(func.distinct(C.c.user_id))),
        "valore_medio": Misura("Valore medio", lambda: arrotonda(func.avg(C.c.importo) / 100.0, 2), "euro"),
        "sconti": Misura("Sconti concessi", lambda: func.coalesce(func.sum(C.c.sconto), 0) / 100.0, "euro"),
    },
    dimensioni={
        "piano": Dimensione("Piano", lambda: P.c.slug),
        "tipo": Dimensione("Tipo", lambda: P.c.tipo),
        "annuale": Dimensione("Annuale", lambda: case((C.c.annuale, literal("sì")), else_=literal("no"))),
        "coupon": Dimensione("Con codice", lambda: case((C.c.coupon_id.is_not(None), literal("sì")), else_=literal("no"))),
        "fornitore": Dimensione("Fornitore di pagamento", lambda: C.c.provider),
        **_dim_persona(riferimento=C.c.completed_at),
        **_dim_attribuzione(),
    },
)

ORDINI = Sorgente(
    etichetta="Ordini del negozio",
    descrizione="Mazzi digitali, PDF e stampe pagati, per data di pagamento.",
    da=lambda: O.join(UT, UT.c.id == O.c.user_id).outerjoin(U, U.c.utente_id == O.c.user_id),
    tempo=lambda: O.c.completed_at,
    dove=lambda: O.c.status == "pagato",
    persone=lambda: func.count(func.distinct(O.c.user_id)),
    misure={
        "ordini": Misura("Ordini", lambda: func.count()),
        "ricavi": Misura("Ricavi", lambda: func.coalesce(func.sum(O.c.importo_totale), 0) / 100.0, "euro"),
        "clienti": Misura("Clienti", lambda: func.count(func.distinct(O.c.user_id))),
        "valore_medio": Misura("Valore medio", lambda: arrotonda(func.avg(O.c.importo_totale) / 100.0, 2), "euro"),
    },
    dimensioni={**_dim_persona(riferimento=O.c.completed_at), **_dim_attribuzione()},
)

CATALOGO = {
    "visite": VISITE,
    "eventi": EVENTI,
    "utenti": UTENTI,
    "letture": LETTURE,
    "acquisti": ACQUISTI,
    "ordini": ORDINI,
    "riepilogo": RIEPILOGO,
}


# ---- coorti -------------------------------------------------------------------------------

def primo_iscrizione():
    return select(UT.c.id.label("k"), UT.c.created_at.label("t0")).where(_UTENTI_ATTIVI)


def attivita_letture():
    return select(R.c.owner_id.label("k"), R.c.created_at.label("t")).where(R.c.owner_id.is_not(None))


def attivita_visite():
    return select(S.c.utente_id.label("k"), S.c.inizio.label("t")).where(S.c.utente_id.is_not(None))


def spesa():
    """Acquisti e ordini pagati, in euro: per le coorti di valore (LTV)."""
    acquisti = select(C.c.user_id.label("k"), C.c.completed_at.label("t"), (C.c.importo / 100.0).label("v")).where(
        C.c.status == "pagato"
    )
    ordini = select(O.c.user_id.label("k"), O.c.completed_at.label("t"), (O.c.importo_totale / 100.0).label("v")).where(
        O.c.status == "pagato"
    )
    return acquisti.union_all(ordini)


COORTI = {
    "letture": ("Iscritti che fanno letture", attivita_letture, False),
    "visite": ("Iscritti che tornano sul sito", attivita_visite, False),
    "spesa": ("Spesa cumulata per iscritto (€)", spesa, True),
}

