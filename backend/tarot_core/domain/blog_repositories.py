"""Accesso ai dati del blog: elenchi pubblici, salvataggio degli articoli, albero delle sezioni.

Una regola sola decide cosa vede il pubblico: `BlogRepository.pubblico()`. Sta qui e non nei
router perché l'hanno da ripetere l'elenco, la pagina di un articolo, le pagine di una
carta, il feed e la mappa del sito: se ognuno la riscrivesse, prima o poi una bozza
comparirebbe da qualche parte.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import Select, and_, case, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..tarot import blog as regole
from ..tarot import blog_seo
from ..tarot import soggetto as regole_soggetto
from .base import utcnow
from .blog_models import (
    TIPI_SEZIONE_CON_ARTICOLI, BlogPost, BlogPostLink, BlogPostRevision, BlogPostTag, BlogSection, BlogTag, MediaImage,
)

MAX_REVISIONI = 20
#: I campi che non ammettono `null`: un `null` inviato dalla console vuol dire «lascia com'è».
NON_NULLI = {"titolo", "testo", "lang", "in_evidenza", "commenti_aperti", "noindex"}


class ErroreBlog(ValueError):
    """Un dato del blog non valido: il messaggio si mostra a chi ha sbagliato."""


def condizione_pubblica(sezioni_visibili: Iterable[int], adesso: Optional[datetime] = None):
    """La condizione SQL di un articolo che il pubblico può vedere: pubblicato, con la data di
    pubblicazione già arrivata (un articolo programmato compare da quel momento), e non in una
    sezione nascosta — né in una dentro una nascosta: `sezioni_visibili` sono gli id delle sezioni
    che il pubblico vede davvero (`BlogRepository.sezioni()`)."""
    adesso = adesso or utcnow()
    return and_(
        BlogPost.stato == "pubblicato",
        BlogPost.pubblicato_il.is_not(None),
        BlogPost.pubblicato_il <= adesso,
        or_(BlogPost.sezione_id.is_(None), BlogPost.sezione_id.in_(list(sezioni_visibili) or [-1])),
    )


async def assicura_miniatura(img: MediaImage) -> None:
    """Crea la miniatura di un'immagine se non l'ha ancora (le miniature servono agli elenchi del blog). Si chiama a
    ogni caricamento e ogni volta che un'immagine viene assegnata a un articolo o a una sezione: così un'immagine
    riusata o caricata prima delle miniature la riceve comunque. Gli avatar non ne hanno bisogno. Idempotente."""
    if img.mini_webp is not None or img.uso == "avatar":
        return
    import asyncio

    img.mini_webp, img.mini_larghezza, img.mini_altezza = await asyncio.to_thread(regole.miniatura, img.webp)


class BlogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ---- sezioni ------------------------------------------------------------------

    async def sezioni(self, *, solo_visibili: bool = True) -> List[BlogSection]:
        q = select(BlogSection).order_by(BlogSection.ordine, BlogSection.nome)
        if solo_visibili:
            q = q.where(BlogSection.visibile.is_(True))
        tutte = list((await self._session.execute(q)).scalars())
        if not solo_visibili:
            return tutte
        # Una sezione dentro una nascosta è nascosta anche lei.
        per_id = {s.id: s for s in tutte}
        return [s for s in tutte if self._antenati_visibili(s, per_id)]

    @staticmethod
    def _antenati_visibili(sezione: BlogSection, per_id: Dict[int, BlogSection]) -> bool:
        corrente, visti = sezione, set()
        while corrente.parent_id is not None:
            if corrente.id in visti:
                return False
            visti.add(corrente.id)
            padre = per_id.get(corrente.parent_id)
            if padre is None:
                return False
            corrente = padre
        return True

    async def sezione_per_slug(self, slug: str) -> Optional[BlogSection]:
        return (await self._session.execute(select(BlogSection).where(BlogSection.slug == slug))).scalar_one_or_none()

    async def sezione(self, sezione_id: int) -> Optional[BlogSection]:
        return await self._session.get(BlogSection, sezione_id)

    @staticmethod
    def discendenti(sezione_id: int, sezioni: Sequence[BlogSection]) -> List[int]:
        """Gli id della sezione e di tutte quelle sotto di essa."""
        figli: Dict[Optional[int], List[int]] = {}
        for s in sezioni:
            figli.setdefault(s.parent_id, []).append(s.id)
        risultato, coda = [], [sezione_id]
        while coda:
            corrente = coda.pop()
            if corrente in risultato:
                continue
            risultato.append(corrente)
            coda.extend(figli.get(corrente, []))
        return risultato

    @staticmethod
    def percorso(sezione: Optional[BlogSection], per_id: Dict[int, BlogSection]) -> List[BlogSection]:
        """Dalla radice alla sezione, per le briciole di pane."""
        catena: List[BlogSection] = []
        visti = set()
        while sezione is not None and sezione.id not in visti:
            visti.add(sezione.id)
            catena.append(sezione)
            sezione = per_id.get(sezione.parent_id) if sezione.parent_id is not None else None
        return list(reversed(catena))

    async def valida_albero(self, sezione_id: int, nuovo_padre: Optional[int]) -> None:
        """Una sezione non può stare dentro sé stessa né dentro una sua discendente."""
        if nuovo_padre is None:
            return
        tutte = await self.sezioni(solo_visibili=False)
        if nuovo_padre in self.discendenti(sezione_id, tutte):
            raise ErroreBlog("una sezione non può stare dentro sé stessa o dentro una sua sotto-sezione")
        if not any(s.id == nuovo_padre for s in tutte):
            raise ErroreBlog("la sezione padre non esiste")

    async def slug_sezione_libero(self, base: str, escludi_id: Optional[int] = None) -> str:
        q = select(BlogSection.slug)
        if escludi_id is not None:
            q = q.where(BlogSection.id != escludi_id)
        return regole.slug_libero(base, (await self._session.execute(q)).scalars().all())

    # ---- articoli: lettura ---------------------------------------------------------

    async def pubblico(self):
        """La condizione di visibilità pubblica (vedi `condizione_pubblica`)."""
        return condizione_pubblica(s.id for s in await self.sezioni())

    async def _base(self, *, pubblico: bool) -> Select:
        q = select(BlogPost)
        return q.where(await self.pubblico()) if pubblico else q

    async def per_slug(self, slug: str, *, pubblico: bool = True) -> Optional[BlogPost]:
        q = (await self._base(pubblico=pubblico)).where(BlogPost.slug == slug)
        return (await self._session.execute(q)).scalar_one_or_none()

    async def per_id(self, post_id: uuid.UUID) -> Optional[BlogPost]:
        return await self._session.get(BlogPost, post_id)

    async def elenco(
        self, *, pubblico: bool = True, sezioni: Optional[Iterable[int]] = None, tag: Optional[str] = None,
        testo: str = "", lang: Optional[str] = None, evidenza: Optional[bool] = None, stato: Optional[str] = None,
        autore_id: Optional[int] = None, pagina: int = 1, per_pagina: int = 12,
        riferimento: Optional[Tuple[str, str]] = None,
    ) -> Tuple[List[BlogPost], int]:
        """Gli articoli, dal più recente. Con `riferimento=("carta", "maj-10")` (o una stesa) quelli che hanno quella
        carta come **soggetto**, per primi, e poi quelli che la **citano** (v9.4)."""
        q = await self._base(pubblico=pubblico)
        sul_soggetto = None
        if riferimento is not None:
            tipo, rif = riferimento
            sul_soggetto = and_(BlogPost.soggetto_tipo == tipo, BlogPost.soggetto_ref == rif)
            q = q.where(or_(sul_soggetto, BlogPost.id.in_(
                select(BlogPostLink.post_id).where(BlogPostLink.tipo == tipo, BlogPostLink.riferimento == rif)
            )))
        if sezioni is not None:
            q = q.where(BlogPost.sezione_id.in_(list(sezioni)))
        if tag:
            q = q.where(BlogPost.id.in_(
                select(BlogPostTag.post_id).join(BlogTag, BlogTag.id == BlogPostTag.tag_id).where(BlogTag.slug == tag)
            ))
        if testo.strip():
            like = f"%{_escape_like(testo.strip())}%"
            q = q.where(or_(
                BlogPost.titolo.ilike(like, escape="\\"), BlogPost.sottotitolo.ilike(like, escape="\\"),
                BlogPost.testo.ilike(like, escape="\\"),
            ))
        if lang:
            q = q.where(BlogPost.lang == lang)
        if evidenza is not None:
            q = q.where(BlogPost.in_evidenza.is_(evidenza))
        if stato:
            q = q.where(BlogPost.stato == stato)
        if autore_id is not None:
            q = q.where(BlogPost.autore_id == autore_id)
        totale = int((await self._session.execute(select(func.count()).select_from(q.subquery()))).scalar_one())
        ordine = (BlogPost.pubblicato_il.desc().nulls_last(), BlogPost.created_at.desc()) if pubblico else (
            BlogPost.updated_at.desc(),
        )
        if sul_soggetto is not None:
            ordine = (case((sul_soggetto, 0), else_=1), *ordine)
        q = q.order_by(*ordine).limit(per_pagina).offset((max(pagina, 1) - 1) * per_pagina)
        return list((await self._session.execute(q)).scalars()), totale

    async def conteggi_per_sezione(self) -> Dict[int, int]:
        q = (
            select(BlogPost.sezione_id, func.count()).where(await self.pubblico(), BlogPost.sezione_id.is_not(None))
            .group_by(BlogPost.sezione_id)
        )
        return {sid: n for sid, n in (await self._session.execute(q)).all()}

    async def tag_con_conteggi(self) -> List[Tuple[BlogTag, int]]:
        q = (
            select(BlogTag, func.count(BlogPost.id))
            .join(BlogPostTag, BlogPostTag.tag_id == BlogTag.id)
            .join(BlogPost, BlogPost.id == BlogPostTag.post_id)
            .where(await self.pubblico())
            .group_by(BlogTag.id)
            .order_by(func.count(BlogPost.id).desc(), BlogTag.nome)
        )
        return [(t, int(n)) for t, n in (await self._session.execute(q)).all()]

    async def per_riferimento(
        self, tipo: str, riferimento: str, limite: int = 6, *, lang: Optional[str] = None,
    ) -> List[BlogPost]:
        """Gli articoli che citano una carta, una stesa o un altro articolo."""
        q = (
            select(BlogPost)
            .join(BlogPostLink, BlogPostLink.post_id == BlogPost.id)
            .where(BlogPostLink.tipo == tipo, BlogPostLink.riferimento == riferimento, await self.pubblico())
        )
        if lang:
            q = q.where(BlogPost.lang == lang)
        q = q.order_by(BlogPost.pubblicato_il.desc().nulls_last()).limit(limite)
        return list((await self._session.execute(q)).scalars())

    async def per_soggetto(
        self, tipo: str, riferimento: str, limite: int = 60, *, lang: Optional[str] = None,
    ) -> List[BlogPost]:
        """Gli articoli pubblici il cui soggetto è quella carta o quella stesa (v9.4), dal più recente."""
        q = select(BlogPost).where(
            BlogPost.soggetto_tipo == tipo, BlogPost.soggetto_ref == riferimento, await self.pubblico(),
        )
        if lang:
            q = q.where(BlogPost.lang == lang)
        q = q.order_by(BlogPost.pubblicato_il.desc().nulls_last()).limit(limite)
        return list((await self._session.execute(q)).scalars())

    async def collegamenti(self, post: BlogPost) -> List[BlogPostLink]:
        q = select(BlogPostLink).where(BlogPostLink.post_id == post.id).order_by(BlogPostLink.id)
        return list((await self._session.execute(q)).scalars())

    async def correlati(self, post: BlogPost, limite: int = 3) -> List[BlogPost]:
        """Altri articoli affini: stesse etichette, stessa sezione, stesse carte citate."""
        punteggio = await self.punteggi_correlati(post)
        if not punteggio:
            return []
        q = select(BlogPost).where(BlogPost.id.in_(list(punteggio)), await self.pubblico())
        trovati = list((await self._session.execute(q)).scalars())
        trovati.sort(key=lambda p: (-punteggio[p.id], -(p.pubblicato_il.timestamp() if p.pubblicato_il else 0)))
        return trovati[:limite]

    async def punteggi_correlati(self, post: BlogPost) -> Dict[uuid.UUID, int]:
        """Quanto un altro articolo è affine a questo (id → punti, anche di articoli non pubblici: chi li usa filtra):
        3 per etichetta in comune, 2 per la stessa sezione, 2 per ogni carta o stesa citata da entrambi."""
        etichette = [t.id for t in post.tags]
        collegamenti = [(c.tipo, c.riferimento) for c in await self.collegamenti(post) if c.tipo != "articolo"]
        punteggio: Dict[uuid.UUID, int] = {}

        async def somma(q: Select, peso: int) -> None:
            for (pid,) in (await self._session.execute(q)).all():
                punteggio[pid] = punteggio.get(pid, 0) + peso

        if etichette:
            await somma(
                select(BlogPostTag.post_id).where(BlogPostTag.tag_id.in_(etichette), BlogPostTag.post_id != post.id), 3,
            )
        if post.sezione_id is not None:
            await somma(select(BlogPost.id).where(BlogPost.sezione_id == post.sezione_id, BlogPost.id != post.id), 2)
        for tipo, rif in collegamenti:
            await somma(
                select(BlogPostLink.post_id).where(
                    BlogPostLink.tipo == tipo, BlogPostLink.riferimento == rif, BlogPostLink.post_id != post.id,
                ), 2,
            )
        return punteggio

    async def vicini(self, post: BlogPost) -> Tuple[Optional[BlogPost], Optional[BlogPost]]:
        """L'articolo precedente e il successivo, per data, nella stessa sezione (se ha una)."""
        if post.pubblicato_il is None:
            return None, None
        base = await self.pubblico()
        if post.sezione_id is not None:
            base = and_(base, BlogPost.sezione_id == post.sezione_id)
        prec = (await self._session.execute(
            select(BlogPost).where(base, BlogPost.pubblicato_il < post.pubblicato_il)
            .order_by(BlogPost.pubblicato_il.desc()).limit(1)
        )).scalar_one_or_none()
        succ = (await self._session.execute(
            select(BlogPost).where(base, BlogPost.pubblicato_il > post.pubblicato_il)
            .order_by(BlogPost.pubblicato_il.asc()).limit(1)
        )).scalar_one_or_none()
        return prec, succ

    async def slug_pubblici(self) -> List[Tuple[str, datetime, str, bool]]:
        """`(slug, aggiornato, lingua, noindex)` di ogni articolo pubblico: per la mappa del sito."""
        q = (
            select(BlogPost.slug, BlogPost.updated_at, BlogPost.lang, BlogPost.noindex)
            .where(await self.pubblico()).order_by(BlogPost.pubblicato_il.desc())
        )
        return [(s, d, lingua, bool(n)) for s, d, lingua, n in (await self._session.execute(q)).all()]

    async def lingue_per_sezione_e_tag(self) -> Tuple[Dict[int, set], Dict[str, set]]:
        """Le lingue degli articoli indicizzabili di ogni sezione (per id) e di ogni etichetta (per slug).

        Serve alla mappa del sito: una pagina di sezione o di etichetta senza articoli in una lingua è vuota in
        quella lingua, e una pagina vuota non va indicata ai motori di ricerca."""
        condizione = and_(await self.pubblico(), BlogPost.noindex.is_(False))
        per_sezione: Dict[int, set] = {}
        q = select(BlogPost.sezione_id, BlogPost.lang).where(condizione, BlogPost.sezione_id.is_not(None)).distinct()
        for sid, lingua in (await self._session.execute(q)).all():
            per_sezione.setdefault(sid, set()).add(lingua)
        per_tag: Dict[str, set] = {}
        q = (
            select(BlogTag.slug, BlogPost.lang)
            .join(BlogPostTag, BlogPostTag.tag_id == BlogTag.id)
            .join(BlogPost, BlogPost.id == BlogPostTag.post_id)
            .where(condizione).distinct()
        )
        for slug, lingua in (await self._session.execute(q)).all():
            per_tag.setdefault(slug, set()).add(lingua)
        return per_sezione, per_tag

    # ---- articoli: scrittura --------------------------------------------------------

    async def _tag(self, nomi: Sequence[str]) -> List[BlogTag]:
        risultato: List[BlogTag] = []
        visti = set()
        for nome in nomi[:10]:
            slug, nome_pulito = regole.normalizza_etichetta(nome)
            if not slug or slug in visti:
                continue
            visti.add(slug)
            tag = (await self._session.execute(select(BlogTag).where(BlogTag.slug == slug))).scalar_one_or_none()
            if tag is None:
                tag = BlogTag(slug=slug, nome=nome_pulito)
                self._session.add(tag)
                await self._session.flush()
            risultato.append(tag)
        return risultato

    async def slug_articolo_libero(self, base: str, escludi_id: Optional[uuid.UUID] = None) -> str:
        q = select(BlogPost.slug)
        if escludi_id is not None:
            q = q.where(BlogPost.id != escludi_id)
        return regole.slug_libero(base, (await self._session.execute(q)).scalars().all(), massimo=160)

    async def _controlla_riferimenti(self, dati: Dict[str, Any]) -> None:
        sezione_id = dati.get("sezione_id")
        if sezione_id is not None:
            sezione = await self.sezione(sezione_id)
            if sezione is None:
                raise ErroreBlog("la sezione non esiste")
            if sezione.tipo not in TIPI_SEZIONE_CON_ARTICOLI:
                raise ErroreBlog("gli articoli stanno nelle sezioni di tipo «articoli», «carte» o «stese», non in un contenitore")
        immagine_id = dati.get("immagine_id")
        if immagine_id is not None:
            img = await self._session.get(MediaImage, immagine_id)
            if img is None:
                raise ErroreBlog("l'immagine non esiste")
            # Anche un'immagine riusata da un altro articolo, o caricata prima delle miniature, ne esce con la sua.
            await assicura_miniatura(img)

    async def salva(
        self, post: Optional[BlogPost], dati: Dict[str, Any], *, autore_id: Optional[int],
        tag: Optional[Sequence[str]] = None, chiave_id: Optional[int] = None,
    ) -> BlogPost:
        """Crea o aggiorna un articolo. `dati` contiene solo i campi da scrivere.

        Alla modifica del testo o del titolo si conserva la versione precedente. Ogni salvataggio
        ricalcola il tempo di lettura, l'elenco dei collegamenti interni e la data di pubblicazione
        (un articolo che diventa `pubblicato` senza data parte da adesso). Un articolo senza soggetto lo riceve da
        titolo e parola chiave, e uno su una carta senza sezione va nella sezione della carta (`_soggetto_e_sezione`).
        """
        await self._controlla_riferimenti(dati)
        nuovo = post is None
        if nuovo:
            titolo = (dati.get("titolo") or "").strip()
            if not titolo:
                raise ErroreBlog("serve un titolo")
            post = BlogPost(titolo=titolo, slug="", testo="", autore_id=autore_id, tags=[], creato_da_chiave_id=chiave_id)
            post.id = uuid.uuid4()
            self._session.add(post)
        else:
            precedente = (post.titolo, post.sottotitolo, post.testo)

        for campo in (
            "titolo", "sottotitolo", "testo", "lang", "immagine_id", "immagine_alt", "sezione_id", "in_evidenza",
            "commenti_aperti", "seo_titolo", "seo_descrizione", "seo_parola_chiave", "noindex", "canonical_url",
            "tradotto_da_id",
        ):
            if campo in dati:
                valore = dati[campo]
                if valore is None and campo in NON_NULLI:
                    continue
                if campo == "canonical_url":
                    try:
                        valore = blog_seo.valida_canonical(valore)
                    except blog_seo.DatoSeoNonValido as exc:
                        raise ErroreBlog(str(exc)) from exc
                if isinstance(valore, str):
                    valore = valore.strip()
                    if campo in ("sottotitolo", "immagine_alt", "seo_titolo", "seo_descrizione", "seo_parola_chiave") and not valore:
                        valore = None
                setattr(post, campo, valore)
        # Liste: pulite e limitate. `None` vuol dire «lascia com'è».
        try:
            if dati.get("faq") is not None:
                post.faq = blog_seo.pulisci_faq(dati["faq"])
            if dati.get("seo_parole_chiave") is not None:
                post.seo_parole_chiave = blog_seo.pulisci_parole_chiave(dati["seo_parole_chiave"])
        except blog_seo.DatoSeoNonValido as exc:
            raise ErroreBlog(str(exc)) from exc
        if not (post.titolo or "").strip():
            raise ErroreBlog("serve un titolo")

        await self._soggetto_e_sezione(post, dati)

        if "stato" in dati:
            post.stato = dati["stato"]
        if "pubblicato_il" in dati:
            post.pubblicato_il = dati["pubblicato_il"]
        if post.stato == "pubblicato" and post.pubblicato_il is None:
            post.pubblicato_il = utcnow()

        slug_richiesto = dati.get("slug")
        if slug_richiesto:
            post.slug = await self.slug_articolo_libero(slug_richiesto, post.id)
        elif not post.slug:
            post.slug = await self.slug_articolo_libero(post.titolo, post.id)

        post.tempo_lettura = regole.tempo_lettura(post.testo)
        await self._session.flush()

        if tag is not None:
            post.tags = await self._tag(tag)

        if not nuovo and precedente != (post.titolo, post.sottotitolo, post.testo):
            await self._archivia_versione(post, precedente, autore_id)
        await self._sincronizza_collegamenti(post)
        await self._session.flush()
        return post

    async def _soggetto_e_sezione(self, post: BlogPost, dati: Dict[str, Any]) -> None:
        """Il soggetto dell'articolo e, per una carta, la sua sezione (v9.4).

        - `dati["soggetto"]` presente: è quello indicato a mano, `{"tipo": "carta"|"stesa", "ref": id o slug}`, o
          `None` per «nessun soggetto» (in questo salvataggio non si ricalcola);
        - assente, con l'articolo senza soggetto: si ricava da titolo e parola chiave (`tarot/soggetto.calcola`);
        - un articolo su una carta che resta senza sezione va nella sezione di quella carta (`sezione_della_carta`).
        """
        if "soggetto" in dati:
            valore = dati["soggetto"] or {}
            try:
                scelto = regole_soggetto.normalizza(valore.get("tipo"), valore.get("ref"))
            except regole_soggetto.SoggettoNonValido as exc:
                raise ErroreBlog(str(exc)) from exc
            post.soggetto_tipo, post.soggetto_ref = scelto or (None, None)
        elif post.soggetto_tipo is None:
            calcolato = regole_soggetto.calcola(post.titolo, post.seo_parola_chiave)
            if calcolato is not None:
                post.soggetto_tipo, post.soggetto_ref = calcolato
        if post.sezione_id is None and post.soggetto_tipo == "carta" and post.soggetto_ref:
            post.sezione_id = await self.sezione_della_carta(post.soggetto_ref)

    async def sezione_della_carta(self, card_id: str) -> Optional[int]:
        """La sezione «carte» di una carta: quella dei maggiori (`{"arcano": "maggiore"}`) o quella del suo seme
        (`{"seme": "coppe"}`, dentro «By suit»). Prima le visibili, poi in ordine; None se non c'è."""
        from ..tarot.conoscenza import condivisa

        carta = condivisa().carte.get(card_id)
        if carta is None:
            return None
        cercato = {"arcano": "maggiore"} if carta["arcano"] == "maggiore" else {"seme": carta.get("seme")}
        candidate = [
            s for s in await self.sezioni(solo_visibili=False)
            if s.tipo == "carte" and dict(s.filtro or {}) == cercato
        ]
        if not candidate:
            return None
        visibili = {s.id for s in await self.sezioni()}
        candidate.sort(key=lambda s: (s.id not in visibili, s.ordine, s.id))
        return candidate[0].id

    async def _archivia_versione(self, post: BlogPost, versione: Tuple[str, Optional[str], str], autore_id: Optional[int]) -> None:
        titolo, sottotitolo, testo = versione
        self._session.add(BlogPostRevision(post_id=post.id, titolo=titolo, sottotitolo=sottotitolo, testo=testo, autore_id=autore_id))
        await self._session.flush()
        vecchie = (await self._session.execute(
            select(BlogPostRevision.id).where(BlogPostRevision.post_id == post.id).order_by(BlogPostRevision.id.desc()).offset(MAX_REVISIONI)
        )).scalars().all()
        if vecchie:
            await self._session.execute(delete(BlogPostRevision).where(BlogPostRevision.id.in_(vecchie)))

    async def revisioni(self, post: BlogPost) -> List[BlogPostRevision]:
        q = select(BlogPostRevision).where(BlogPostRevision.post_id == post.id).order_by(BlogPostRevision.id.desc())
        return list((await self._session.execute(q)).scalars())

    async def _sincronizza_collegamenti(self, post: BlogPost) -> None:
        voci = [
            (tipo, rif)
            for tipo, rif in regole.estrai_collegamenti(post.testo, host=_host_del_sito(), risolvi=regole.risolvi_riferimento)
            if not (tipo == "articolo" and rif == post.slug)
        ]
        await self._session.execute(delete(BlogPostLink).where(BlogPostLink.post_id == post.id))
        for tipo, rif in voci:
            self._session.add(BlogPostLink(post_id=post.id, tipo=tipo, riferimento=rif))

    async def elimina(self, post: BlogPost) -> None:
        await self._session.delete(post)


def _host_del_sito() -> Optional[str]:
    """Il dominio del sito, per riconoscere i collegamenti assoluti che sono interni."""
    from urllib.parse import urlparse

    from ..settings import get_settings

    return urlparse(get_settings().web_public_url or "").netloc or None


def _escape_like(testo: str) -> str:
    return testo.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
