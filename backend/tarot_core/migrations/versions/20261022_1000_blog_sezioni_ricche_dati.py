"""blog v9.4, i dati: Minor Arcana per seme e per numero, il soggetto degli articoli, gli articoli su una carta nella
sua sezione

Revision ID: e2a4b6c8d0f3
Revises: d1f3a5c7e9b2
Creata: 2026-10-05

Solo dati, **idempotente** (rilanciata non crea doppioni e non sposta niente due volte):

1. **Minor Arcana** (slug `minor-arcana`, se c'è: su un database nuovo l'albero lo scrive il seed) diventa due gruppi:
   - il contenitore `by-suit` («By suit»), in cui si spostano le sezioni dei semi (tipo `carte` con filtro `seme`)
     che oggi stanno direttamente sotto Minor Arcana, con i loro slug (`wands`, `cups`, `swords`, `disks`);
   - il contenitore `by-number` («By number») con 14 sezioni `carte` filtro `rango`: `aces`, `twos`… `tens`,
     `princesses`, `princes`, `queens`, `knights`. Uno slug già occupato non si tocca.
2. **Il soggetto** di ogni articolo che non ce l'ha, ricavato da titolo e parola chiave con la regola di oggi
   (`tarot_core.tarot.soggetto.calcola`). Qui si importa il codice, a differenza delle altre migrazioni: la regola
   (il catalogo dei nomi di carte e stese) è troppo lunga per copiarla, e una volta applicata il risultato sta nel
   database; su un database nuovo non ci sono articoli.
3. **Gli articoli su una carta** vanno nella sezione di quella carta (Major Arcana, o il seme dentro «By suit»), ma
   **solo se oggi stanno in una sezione generica**. La regola:
   - generica = nessuna sezione, oppure `learn-tarot`, `thoth-tarot`, `symbolism` (i temi «il tarocco in generale»,
     di cui la carta è un caso più preciso);
   - tematica = tutte le altre (`love`, `relationships`, `career`, `spirituality`, `tarot-journal` e ogni sezione
     creata dalla console): lì l'articolo resta, perché il tema dice di più della carta («The Lovers in a love
     reading» sta bene in Love). Neanche gli articoli già in una sezione di carte o di stese si spostano.

**Il registro.** Ciò che cambia (sezioni create e spostate, soggetti scritti, articoli spostati con la sezione di
prima) va in `audit_log`, azione `blog.v94.sezioni_e_soggetti`, attore nullo. **Il downgrade** legge l'ultima di
quelle righe e rimette le cose com'erano, dove ancora possibile: gli articoli tornano nella sezione di prima (se
stanno ancora dove li aveva messi), i soggetti scritti qui si cancellano (se nessuno li ha cambiati), i semi tornano
sotto Minor Arcana, e le sezioni create qui si cancellano (un articolo finito lì dopo resta senza sezione).
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e2a4b6c8d0f3"
down_revision: Union[str, None] = "d1f3a5c7e9b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AZIONE = "blog.v94.sezioni_e_soggetti"

#: Scritti qui e non importati dal seed: una migrazione non deve cambiare se domani cambia il codice.
PER_SEME = ("by-suit", "By suit", "The four suits, one element each: Wands, Cups, Swords and Disks.")
PER_NUMERO = ("by-number", "By number",
              "The same number or court card across the four suits: the Aces, the Twos… the Knights.")
GRADI = (
    ("aces", "Aces", "asso", "The roots of the four elements: the seed of each suit."),
    ("twos", "Twos", "due", "The first movement of each element: dominion, love, peace, change."),
    ("threes", "Threes", "tre", "The element takes form: virtue, abundance, sorrow, work."),
    ("fours", "Fours", "quattro", "Order and stability in each suit."),
    ("fives", "Fives", "cinque", "Disruption and challenge in each suit."),
    ("sixes", "Sixes", "sei", "Balance regained: the harmony of each element."),
    ("sevens", "Sevens", "sette", "The test of each element: valour, debauch, futility, failure."),
    ("eights", "Eights", "otto", "Movement and method in each suit."),
    ("nines", "Nines", "nove", "The element at its fullest, for better or worse."),
    ("tens", "Tens", "dieci", "The end of each cycle: the element brought to its limit."),
    ("princesses", "Princesses", "principessa", "The earthy part of each element; the Pages of other decks."),
    ("princes", "Princes", "principe", "The airy part of each element, in motion."),
    ("queens", "Queens", "regina", "The watery part of each element: receptive and reflective."),
    ("knights", "Knights", "cavaliere", "The fiery part of each element: swift and decisive."),
)
SEMI = ("bastoni", "coppe", "spade", "dischi")
DESCRIZIONE_MINORI_VECCHIA = "The fifty-six cards of everyday life, divided into four suits."
DESCRIZIONE_MINORI_NUOVA = "The fifty-six cards of everyday life, by suit and by number."
#: Le sezioni «il tarocco in generale»: un articolo su una carta che sta qui va nella sezione della carta.
SEZIONI_GENERICHE = ("learn-tarot", "thoth-tarot", "symbolism")


def _id_sezione(conn, slug: str) -> Optional[int]:
    return conn.execute(sa.text("SELECT id FROM blog_sections WHERE slug = :s"), {"s": slug}).scalar()


def _crea_sezione(conn, *, slug: str, nome: str, descrizione: str, tipo: str, padre: int, ordine: int,
                  filtro: Optional[Dict[str, Any]] = None) -> int:
    return conn.execute(sa.text(
        "INSERT INTO blog_sections (slug, nome, descrizione, tipo, filtro, parent_id, ordine, visibile, created_at, "
        "updated_at) VALUES (:slug, :nome, :descrizione, :tipo, CAST(:filtro AS jsonb), :padre, :ordine, true, now(), "
        "now()) RETURNING id"
    ), {"slug": slug, "nome": nome, "descrizione": descrizione, "tipo": tipo,
        "filtro": json.dumps(filtro) if filtro is not None else None, "padre": padre, "ordine": ordine}).scalar()


def _albero(conn, traccia: Dict[str, Any]) -> None:
    minori = _id_sezione(conn, "minor-arcana")
    if minori is None:
        return
    per_seme = _id_sezione(conn, PER_SEME[0])
    if per_seme is None:
        per_seme = _crea_sezione(conn, slug=PER_SEME[0], nome=PER_SEME[1], descrizione=PER_SEME[2], tipo="contenitore",
                                 padre=minori, ordine=0)
        traccia["sezioni_create"].append(per_seme)
    semi = conn.execute(sa.text(
        "SELECT id FROM blog_sections WHERE parent_id = :minori AND tipo = 'carte' AND filtro->>'seme' = ANY(:semi)"
    ), {"minori": minori, "semi": list(SEMI)}).scalars().all()
    for sid in semi:
        conn.execute(sa.text("UPDATE blog_sections SET parent_id = :p, updated_at = now() WHERE id = :id"),
                     {"p": per_seme, "id": sid})
        traccia["semi_spostati"][str(sid)] = minori
    per_numero = _id_sezione(conn, PER_NUMERO[0])
    if per_numero is None:
        per_numero = _crea_sezione(conn, slug=PER_NUMERO[0], nome=PER_NUMERO[1], descrizione=PER_NUMERO[2],
                                   tipo="contenitore", padre=minori, ordine=1)
        traccia["sezioni_create"].append(per_numero)
    for ordine, (slug, nome, rango, descrizione) in enumerate(GRADI):
        if _id_sezione(conn, slug) is None:
            traccia["sezioni_create"].append(_crea_sezione(
                conn, slug=slug, nome=nome, descrizione=descrizione, tipo="carte", padre=per_numero, ordine=ordine,
                filtro={"rango": rango},
            ))
    cambiata = conn.execute(sa.text(
        "UPDATE blog_sections SET descrizione = :nuova, updated_at = now() WHERE id = :id AND descrizione = :vecchia"
    ), {"nuova": DESCRIZIONE_MINORI_NUOVA, "vecchia": DESCRIZIONE_MINORI_VECCHIA, "id": minori}).rowcount
    traccia["descrizione_minori"] = bool(cambiata)


def _soggetti(conn, traccia: Dict[str, Any]) -> None:
    from tarot_core.tarot import soggetto

    righe = conn.execute(sa.text(
        "SELECT id, titolo, seo_parola_chiave FROM blog_posts WHERE soggetto_tipo IS NULL"
    )).all()
    for r in righe:
        trovato = soggetto.calcola(r.titolo, r.seo_parola_chiave)
        if trovato is None:
            continue
        conn.execute(sa.text("UPDATE blog_posts SET soggetto_tipo = :t, soggetto_ref = :r WHERE id = :id"),
                     {"t": trovato[0], "r": trovato[1], "id": r.id})
        traccia["soggetti"][str(r.id)] = list(trovato)


def _sezione_della_carta(conn, card_id: str) -> Optional[int]:
    if card_id.startswith("maj-"):
        filtro = {"arcano": "maggiore"}
    else:
        seme = card_id.split("-", 1)[0]
        if seme not in SEMI:
            return None
        filtro = {"seme": seme}
    return conn.execute(sa.text(
        "SELECT id FROM blog_sections WHERE tipo = 'carte' AND filtro = CAST(:f AS jsonb) "
        "ORDER BY visibile DESC, ordine, id LIMIT 1"
    ), {"f": json.dumps(filtro)}).scalar()


def _articoli_nella_sezione_della_carta(conn, traccia: Dict[str, Any]) -> None:
    righe = conn.execute(sa.text(
        "SELECT p.id, p.soggetto_ref, p.sezione_id FROM blog_posts p LEFT JOIN blog_sections s ON s.id = p.sezione_id "
        "WHERE p.soggetto_tipo = 'carta' AND (p.sezione_id IS NULL OR s.slug = ANY(:generiche))"
    ), {"generiche": list(SEZIONI_GENERICHE)}).all()
    for r in righe:
        destinazione = _sezione_della_carta(conn, r.soggetto_ref)
        if destinazione is None or destinazione == r.sezione_id:
            continue
        conn.execute(sa.text("UPDATE blog_posts SET sezione_id = :s WHERE id = :id"), {"s": destinazione, "id": r.id})
        traccia["articoli_spostati"][str(r.id)] = {"prima": r.sezione_id, "dopo": destinazione}


def applica(conn) -> Dict[str, Any]:
    """Tutto il lavoro, su una connessione: la migrazione e i test la chiamano. Restituisce la traccia."""
    traccia: Dict[str, Any] = {
        "sezioni_create": [], "semi_spostati": {}, "descrizione_minori": False, "soggetti": {}, "articoli_spostati": {},
    }
    _albero(conn, traccia)
    _soggetti(conn, traccia)
    _articoli_nella_sezione_della_carta(conn, traccia)
    if any(traccia[k] for k in traccia):
        conn.execute(sa.text(
            "INSERT INTO audit_log (actor_id, action, target_type, target_id, before, after, created_at) "
            "VALUES (NULL, :azione, 'blog', 'v9.4', NULL, CAST(:dopo AS jsonb), now())"
        ), {"azione": AZIONE, "dopo": json.dumps(traccia)})
    return traccia


def annulla(conn) -> Optional[Dict[str, Any]]:
    """Il contrario di `applica`, dall'ultima traccia nel registro; None se non c'è."""
    riga = conn.execute(sa.text(
        "SELECT id, after FROM audit_log WHERE action = :azione ORDER BY id DESC LIMIT 1"
    ), {"azione": AZIONE}).first()
    if riga is None or not riga.after:
        return None
    traccia = riga.after if isinstance(riga.after, dict) else json.loads(riga.after)
    for post_id, mossa in (traccia.get("articoli_spostati") or {}).items():
        conn.execute(sa.text("UPDATE blog_posts SET sezione_id = :prima WHERE id = CAST(:id AS uuid) AND sezione_id = :dopo"),
                     {"prima": mossa["prima"], "dopo": mossa["dopo"], "id": post_id})
    for post_id, (tipo, rif) in (traccia.get("soggetti") or {}).items():
        conn.execute(sa.text(
            "UPDATE blog_posts SET soggetto_tipo = NULL, soggetto_ref = NULL "
            "WHERE id = CAST(:id AS uuid) AND soggetto_tipo = :t AND soggetto_ref = :r"
        ), {"id": post_id, "t": tipo, "r": rif})
    for sid, padre in (traccia.get("semi_spostati") or {}).items():
        conn.execute(sa.text("UPDATE blog_sections SET parent_id = :p, updated_at = now() WHERE id = :id"),
                     {"p": padre, "id": int(sid)})
    create: List[int] = list(traccia.get("sezioni_create") or [])
    if create:
        # Prima i figli: le sezioni dei gradi, poi i contenitori (l'ordine di creazione al contrario).
        for sid in reversed(create):
            conn.execute(sa.text("UPDATE blog_sections SET parent_id = NULL WHERE parent_id = :id AND NOT (id = ANY(:create))"),
                         {"id": sid, "create": create})
            conn.execute(sa.text("DELETE FROM blog_sections WHERE id = :id"), {"id": sid})
    if traccia.get("descrizione_minori"):
        conn.execute(sa.text(
            "UPDATE blog_sections SET descrizione = :vecchia, updated_at = now() WHERE slug = 'minor-arcana' "
            "AND descrizione = :nuova"
        ), {"nuova": DESCRIZIONE_MINORI_NUOVA, "vecchia": DESCRIZIONE_MINORI_VECCHIA})
    conn.execute(sa.text(
        "INSERT INTO audit_log (actor_id, action, target_type, target_id, before, after, created_at) "
        "VALUES (NULL, :azione, 'blog', 'v9.4', CAST(:prima AS jsonb), NULL, now())"
    ), {"azione": AZIONE + ".annulla", "prima": json.dumps(traccia)})
    # La traccia è consumata: un secondo downgrade (dopo un altro upgrade) userà quella nuova.
    conn.execute(sa.text("UPDATE audit_log SET action = :fatta WHERE id = :id"),
                 {"fatta": AZIONE + ".annullata", "id": riga.id})
    return traccia


def upgrade() -> None:
    applica(op.get_bind())


def downgrade() -> None:
    annulla(op.get_bind())
