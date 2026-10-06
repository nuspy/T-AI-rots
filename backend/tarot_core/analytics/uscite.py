"""Le uscite (v8.6): da quale pagina finisce la visita e, se è una pagina di lettura, a che punto della lettura.

**La pagina d'uscita** è l'ultima pagina vista della sessione: `lanterna` la scrive in `an_sessioni.uscita` a ogni
lotto che contiene una pagina vista. L'osservatore del browser manda l'ultimo lotto anche quando la scheda si
nasconde o la pagina si chiude (`visibilitychange`/`pagehide`, con `fetch(…, {keepalive: true})`, l'equivalente di
`sendBeacon` che porta anche il token): l'uscita è quella vera anche per chi chiude la scheda a metà.

**L'ultima azione** di una lettura è l'ultimo evento della sessione sulla pagina d'uscita, dopo l'ultima volta che ci
si è entrati: la fase della lettura (`lettura_fase`, con la fase), un gesto (mescola, taglia, sceglie, rivela),
il paywall, una condivisione… Pagine viste, tempo attivo ed elementi visti non sono azioni. Una sessione senza
nessuna azione su quella pagina è «solo vista»: è entrata ed è uscita senza toccare nulla.

Solo conteggi di sessioni per pagina: nessuna dimensione personale, nessuna soglia da applicare.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from lanterna.interroga import limiti
from sqlalchemy import and_, case, func, literal, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.analytics_models import TABELLE

FUSO = "Europe/Rome"
ND = "(n.d.)"
SOLO_VISTA = "(nessuna azione)"

#: Le pagine di lettura, con gli indirizzi di oggi e quelli di prima (lo storico della v1 sotto `/old`, l'anteprima
#: `/v2`): la lettura guidata e quella col mazzo fisico, in inglese e in italiano.
PAGINE_LETTURA = (
    "/read", "/it/read", "/v2/read", "/it/v2/read",
    "/physical-reading", "/it/physical-reading", "/v2/physical-reading", "/it/v2/physical-reading",
    "/leggi", "/it/leggi", "/old/leggi", "/old/it/leggi",
    "/interpreta", "/it/interpreta", "/old/interpreta", "/old/it/interpreta",
)

#: Gli eventi che non sono azioni di chi legge.
NON_AZIONI = ("page_view", "engagement", "vista")

#: Le azioni con un nome leggibile; le altre si mostrano col loro nome.
ETICHETTE: Dict[str, str] = {
    SOLO_VISTA: "Nessuna azione: è entrato ed è uscito",
    # v2 (lettura guidata)
    "lettura_fase:preparazione": "Fase: domanda e stesa",
    "lettura_fase:intervista": "Fase: intervista",
    "lettura_fase:taglio": "Fase: mescola e taglia",
    "lettura_fase:scelta": "Fase: scelta delle carte",
    "lettura_fase:rivelazione": "Fase: rivelazione",
    "lettura_fase:completata": "Fase: interpretazione (completata)",
    "lettura_fase:stesa": "Fase: scelta della stesa (v1)",
    "question_started": "Ha iniziato a scrivere la domanda",
    "question_submitted": "Ha inviato la domanda",
    "reading_entry": "Arrivato da un link alla lettura",
    "qr_entry": "Arrivato dal QR",
    "reading_started": "Ha aperto la lettura",
    "shuffle_started": "Mescola",
    "shuffle_interrupted": "Ha interrotto il mescolamento",
    "deck_cut": "Ha tagliato il mazzo",
    "card_drawn": "Ha scelto una carta",
    "card_revealed": "Ha rivelato una carta",
    "reading_completed": "Lettura completata",
    "interview_addition": "Ha aggiunto qualcosa dopo l'intervista",
    "interview_addition_skipped": "Non ha aggiunto nulla: è passato alle carte",
    "paywall_viewed": "Ha visto il paywall (crediti finiti)",
    "signup_started": "È andato a iscriversi",
    "share_completed": "Ha condiviso",
    "physical_reading_started": "Lettura col mazzo fisico avviata",
    "link_esterno": "Ha aperto un link esterno",
}


#: Gli eventi della lettura che portano un numero (v9.5): la domanda dell'intervista, la carta scelta o rivelata.
#: L'azione diventa «nome:n» («card_revealed:3»), con l'etichetta di `NUMERATE`.
CON_NUMERO = ("interview_question", "interview_answered", "interview_skipped", "card_drawn", "card_revealed")
NUMERATE: Dict[str, str] = {
    "interview_question": "Intervista: ha ricevuto la domanda {n}",
    "interview_answered": "Intervista: ha risposto alla domanda {n}",
    "interview_skipped": "Intervista: ha chiesto di fermarsi dopo {n} risposte",
    "card_drawn": "Ha scelto la carta {n}",
    "card_revealed": "Ha rivelato la carta in posizione {n}",
}


def e_lettura(percorso: Optional[str]) -> bool:
    if not percorso:
        return False
    p = percorso.rstrip("/") or "/"
    return any(p == base or p.startswith(base + "/") for base in PAGINE_LETTURA)


def _condizione_lettura(colonna):
    return or_(*[or_(colonna == base, colonna.like(base + "/%")) for base in PAGINE_LETTURA])


def etichetta(azione: str) -> str:
    nome, _, n = azione.partition(":")
    if nome in NUMERATE and n:
        return NUMERATE[nome].format(n=n)
    return ETICHETTE.get(azione, azione.replace("lettura_fase:", "Fase: ") if azione.startswith("lettura_fase:") else azione)


async def uscite(session: AsyncSession, da: date, a: date, *, limite: int = 25) -> Dict[str, Any]:
    S, E = TABELLE.sessioni, TABELLE.eventi
    inizio, fine = limiti(da, a, FUSO)
    nel_periodo = and_(S.c.inizio >= inizio, S.c.inizio < fine)

    totale = (await session.execute(select(func.count()).select_from(S).where(nel_periodo))).scalar_one()

    pagina = func.coalesce(S.c.uscita, literal(ND))
    righe = (await session.execute(
        select(
            pagina.label("pagina"),
            func.count().label("uscite"),
            func.count().filter(S.c.pagine <= 1).label("uscite_unica_pagina"),
        )
        .where(nel_periodo).group_by(pagina).order_by(func.count().desc(), pagina).limit(limite)
    )).all()

    # Le visualizzazioni di ciascuna pagina nello stesso periodo: «uscite / visualizzazioni» è il tasso d'uscita.
    percorsi = [r.pagina for r in righe if r.pagina != ND]
    viste: Dict[str, int] = {}
    if percorsi:
        viste = dict((await session.execute(
            select(E.c.percorso, func.count())
            .where(E.c.nome == "page_view", E.c.ts >= inizio, E.c.ts < fine, E.c.percorso.in_(percorsi))
            .group_by(E.c.percorso)
        )).all())

    pagine = [
        {
            "pagina": r.pagina, "uscite": r.uscite, "uscite_unica_pagina": r.uscite_unica_pagina,
            "visualizzazioni": viste.get(r.pagina),
            "tasso_uscita": round(r.uscite / viste[r.pagina], 4) if viste.get(r.pagina) else None,
            "quota": round(r.uscite / totale, 4) if totale else None,
            "lettura": e_lettura(r.pagina),
        }
        for r in righe
    ]

    # L'ultima azione sulla pagina d'uscita, dopo l'ultimo ingresso in quella pagina.
    E2 = E.alias("ingresso")
    ultimo_ingresso = (
        select(func.max(E2.c.ts))
        .where(E2.c.sessione_id == S.c.id, E2.c.nome == "page_view", E2.c.percorso == S.c.uscita)
        .correlate(S)
        .scalar_subquery()
    )
    azione_evento = case(
        (E.c.nome == "lettura_fase", literal("lettura_fase:") + func.coalesce(E.c.proprieta["fase"].astext, literal("?"))),
        # v9.5: dopo quale domanda, a quale carta (il numero, mai il contenuto)
        (and_(E.c.nome.in_(CON_NUMERO), E.c.proprieta["n"].isnot(None)),
         E.c.nome + literal(":") + E.c.proprieta["n"].astext),
        else_=E.c.nome,
    )
    ultima = (
        select(azione_evento.label("azione"))
        .where(
            E.c.sessione_id == S.c.id, E.c.percorso == S.c.uscita, E.c.nome.not_in(NON_AZIONI),
            or_(ultimo_ingresso.is_(None), E.c.ts >= ultimo_ingresso),
        )
        .order_by(E.c.ts.desc(), E.c.id.desc()).limit(1)
        .correlate(S)
        .lateral("ultima")
    )
    azione = func.coalesce(ultima.c.azione, literal(SOLO_VISTA))
    letture = (await session.execute(
        select(S.c.uscita.label("pagina"), azione.label("azione"), func.count().label("sessioni"))
        .select_from(S.outerjoin(ultima, true()))
        .where(nel_periodo, _condizione_lettura(S.c.uscita))
        .group_by(S.c.uscita, azione)
        .order_by(func.count().desc())
    )).all()

    complessive: Dict[str, int] = {}
    per_pagina: Dict[str, Dict[str, int]] = {}
    for r in letture:
        complessive[r.azione] = complessive.get(r.azione, 0) + r.sessioni
        per_pagina.setdefault(r.pagina, {})[r.azione] = r.sessioni

    def _voci(conteggi: Dict[str, int]) -> List[Dict[str, Any]]:
        somma = sum(conteggi.values())
        return [
            {"azione": k, "etichetta": etichetta(k), "sessioni": v, "quota": round(v / somma, 4) if somma else None}
            for k, v in sorted(conteggi.items(), key=lambda x: (-x[1], x[0]))
        ]

    return {
        "da": da.isoformat(), "a": a.isoformat(),
        "sessioni": totale,
        "pagine": pagine,
        "letture": {
            "sessioni": sum(complessive.values()),
            "azioni": _voci(complessive),
            "per_pagina": [
                {"pagina": p, "sessioni": sum(c.values()), "azioni": _voci(c)}
                for p, c in sorted(per_pagina.items(), key=lambda x: -sum(x[1].values()))
            ],
        },
    }
