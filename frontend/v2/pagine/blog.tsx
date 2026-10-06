"use client";

/* Il diario (il blog) nella v2: un grafo di contenuti, non una lista di post (specifica v2, §14). Ogni articolo
 * porta a una carta, una stesa, un mazzo, e infine a una domanda. I dati vengono dall'API del blog; ogni
 * collegamento resta dentro la v2. Include «Explore», il punto d'ingresso del grafo.
 *
 * Gli spazi pubblicitari (spenti per default): negli elenchi fra i blocchi della colonna (`ConPubblicita`), prima del
 * ponte verso la lettura; nell'articolo dentro il testo a un terzo e a due terzi, e alla fine prima del ponte. */

import { Fragment, Suspense, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { leggiApi, type Carta } from "@/lib/api";
import {
  dataLeggibile, urlMedia, type ArticoloBreve, type ElementoStesa, type ElencoArticoli, type NodoSezione,
} from "@/lib/blog";
import { nomeStesaDaNomi } from "@/lib/i18n/nomi";
import { f, plurale, type Lingua } from "@/v2/i18n";
import { BlogMarkdownV2, type Riferimenti } from "@/v2/componenti/blog-markdown";
import { ImmagineCarta } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { ConPubblicita, Pubblicita, usePubblicitaVisibile } from "@/v2/componenti/pubblicita";
import { MiniaturaStesa } from "@/v2/lettura/miniatura";
import {
  P, PER_PAGINA_BLOG, SCELTE_PER_PAGINA, articoli, articolo, etichette, linguaContenuti, numeroPagina, perPagina,
  recentiDiario, sezione, sezioni,
} from "@/v2/lib/dati";
import { linguaPubblica } from "@/lib/indirizzi";
import { urlPubblico } from "@/lib/seo";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useCarica, usePubblico } from "@/v2/lib/usa";
import { useTraduzione } from "@/v2/lib/usa-traduzione";
import { AvvisoTraduzione } from "@/v2/componenti/avviso-traduzione";
import { nomeDi } from "./carte";

/** La pagina e gli articoli per pagina dall'indirizzo (`?page=`, `?per=`): solo nelle pagine del Journal e negli
 *  elenchi completi delle pagine di carte e stese. */
function usePaginazione() {
  const parametri = useSearchParams();
  return { pagina: numeroPagina(parametri.get("page")), per: perPagina(parametri.get("per")) };
}

export function Tessera({ a, grande = false }: { a: ArticoloBreve; grande?: boolean }) {
  const { t } = useLingua();
  return (
    <LinkV2 className={`article ${grande ? "article-featured" : ""}`} href={R.articolo(a.slug)}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={urlMedia(a.immagine?.mini ?? a.immagine?.url) ?? "/cards/maj-06.webp"} alt="" loading="lazy" />
      <small>{a.sezione?.nome ?? a.tags[0]?.nome ?? t.blog.eyebrow}</small>
      <h3>{a.titolo}</h3>
      {grande && a.estratto && <p>{a.estratto}</p>}
      <p>{f(t.blog.min, { n: a.tempo_lettura })}</p>
    </LinkV2>
  );
}

export interface Nove {
  recenti: ArticoloBreve[];
  scelti: ArticoloBreve[];
}

/** I nove articoli di ogni pagina (v8.5): i 3 più recenti, col link all'elenco in ordine cronologico, e 6 scelti
 *  fra quelli attinenti alla pagina, ciascuno col link alla sezione da cui viene. `vuoto` si mostra se il diario non
 *  ha ancora articoli.
 *
 *  `ordine` (v9.4): nelle pagine di un articolo, di una carta e di una stesa le scelte sono per pertinenza (l'articolo
 *  su quella carta prima di tutto) e vengono **prima** degli ultimi articoli (`"scelti"`); altrove (home, Explore,
 *  carta del giorno) restano dopo (`"recenti"`, il predefinito). `lang` tiene solo gli articoli in quella lingua. */
export function DiarioNove({
  contesto = {}, eyebrow, titolo, vuoto = null, inMezzo = null, ordine = "recenti", lang,
}: {
  contesto?: { carta?: string; stesa?: string; sezione?: string; articolo?: string };
  eyebrow?: string;
  titolo?: string;
  vuoto?: React.ReactNode;
  /** Fra i due gruppi: uno spazio pubblicitario nelle pagine corte, dove il diario è metà del contenuto. */
  inMezzo?: React.ReactNode;
  ordine?: "recenti" | "scelti";
  lang?: string;
}) {
  const { t } = useLingua();
  const b = t.blog;
  const percorso = P.nove({ ...contesto, lang });
  const nove = useCarica(() => leggiApi<Nove>(percorso), [percorso], { pubblico: true, iniziale: percorso });
  const recenti = nove.dati?.recenti ?? [];
  const scelti = nove.dati?.scelti ?? [];
  if (!recenti.length && !scelti.length) return vuoto ? <>{vuoto}</> : null;
  const gruppoScelti = scelti.length > 0 && (
    <Fragment key="scelti">
      <h3 className="diario-nove-sotto">{b.nove_attinenti}</h3>
      <div className="content-grid">
        {scelti.map((a) => (
          <div key={a.slug} className="diario-nove-voce">
            <Tessera a={a} />
            {a.sezione && (
              <LinkV2 className="inline small" href={R.blogSezione(a.sezione.slug)}>{f(b.nove_sezione, { sezione: a.sezione.nome })}</LinkV2>
            )}
          </div>
        ))}
      </div>
    </Fragment>
  );
  const gruppoRecenti = recenti.length > 0 && (
    <Fragment key="recenti">
      {/* Prima delle scelte bastano il titolo della fascia e il pulsante; dopo, un titolo come quello delle scelte. */}
      {ordine === "scelti" && scelti.length > 0 && <h3 className="diario-nove-sotto">{b.ultimi}</h3>}
      <div className="content-grid">{recenti.map((a) => <Tessera key={a.slug} a={a} />)}</div>
    </Fragment>
  );
  const [primo, secondo] = ordine === "scelti" ? [gruppoScelti, gruppoRecenti] : [gruppoRecenti, gruppoScelti];
  return (
    <section className="band band-tight diario-nove" aria-labelledby="titolo-nove">
      <div className="section-head">
        <div>
          <p className="eyebrow">{eyebrow ?? b.nove_eyebrow}</p>
          <h2 id="titolo-nove" className="section-title">{titolo ?? b.nove_titolo}</h2>
        </div>
        <LinkV2 className="button button-quiet" href={R.blog}>{b.nove_ultimi}</LinkV2>
      </div>
      {primo}
      {primo && secondo && inMezzo}
      {secondo}
    </section>
  );
}

/** I numeri da mostrare: la prima e l'ultima pagina, la corrente con `vicine` pagine per lato; `null` è un salto
 *  («…»). Un salto di una pagina sola si scrive col suo numero. */
function finestra(pagina: number, pagine: number, vicine: number): (number | null)[] {
  const scelte = new Set([1, pagine]);
  for (let k = pagina - vicine; k <= pagina + vicine; k++) if (k >= 1 && k <= pagine) scelte.add(k);
  const ordinate = [...scelte].sort((x, y) => x - y);
  const fuori: (number | null)[] = [];
  ordinate.forEach((k, i) => {
    const salto = i > 0 ? k - ordinate[i - 1] : 1;
    if (salto === 2) fuori.push(k - 1);
    else if (salto > 2) fuori.push(null);
    fuori.push(k);
  });
  return fuori;
}

/** La paginazione degli elenchi del Journal e degli elenchi completi di carte e stese (v9.4): precedente e
 *  successiva, i numeri con la prima e l'ultima pagina, e la scelta di 10 / 25 / 50 articoli per pagina (`?per=`,
 *  conservata in ogni link; 25 non si scrive). Due righe di numeri: più ampia sul computer, più corta sul telefono
 *  (la prima, la corrente, l'ultima), così non si scorre mai di lato. `ancora` riporta all'elenco dopo il clic. */
export function Pagine({
  pagina, pagine, totale, base, q, per, ancora,
}: {
  pagina: number; pagine: number; totale: number; base: string; q?: string; per: number; ancora?: string;
}) {
  const { t, prefissoIt } = useLingua();
  const b = t.blog;
  const router = useRouter();
  if (pagine <= 1 && totale <= SCELTE_PER_PAGINA[0]) return null;
  const href = (p: number, n = per) => {
    const s = new URLSearchParams();
    if (q) s.set("q", q);
    if (p > 1) s.set("page", String(p));
    if (n !== PER_PAGINA_BLOG) s.set("per", String(n));
    const qs = s.toString();
    return `${qs ? `${base}?${qs}` : base}${ancora ? `#${ancora}` : ""}`;
  };
  const numeri = (vicine: number, classe: string) => (
    <ol className={`paginatore-numeri ${classe}`}>
      <li>
        {pagina > 1
          ? <LinkV2 className="paginatore-voce paginatore-passo" href={href(pagina - 1)} rel="prev" aria-label={b.pagina_precedente}><span aria-hidden="true">‹</span></LinkV2>
          : <span className="paginatore-voce paginatore-passo" aria-hidden="true">‹</span>}
      </li>
      {finestra(pagina, pagine, vicine).map((n, i) => (n === null ? (
        <li key={`salto-${i}`} className="paginatore-salto" aria-hidden="true">…</li>
      ) : (
        <li key={n}>
          <LinkV2
            className="paginatore-voce" href={href(n)} aria-current={n === pagina ? "page" : undefined}
            aria-label={n === 1 ? `${b.pagina_prima}, ${n}` : n === pagine ? `${b.pagina_ultima}, ${n}` : f(b.pagina_n, { p: n })}
          >{n}</LinkV2>
        </li>
      )))}
      <li>
        {pagina < pagine
          ? <LinkV2 className="paginatore-voce paginatore-passo" href={href(pagina + 1)} rel="next" aria-label={b.pagina_successiva}><span aria-hidden="true">›</span></LinkV2>
          : <span className="paginatore-voce paginatore-passo" aria-hidden="true">›</span>}
      </li>
    </ol>
  );
  return (
    <nav className="paginatore" aria-label={f(b.pagina, { p: pagina, n: pagine })}>
      {pagine > 1 && <>{numeri(2, "paginatore-ampio")}{numeri(0, "paginatore-stretto")}</>}
      <label className="paginatore-per">
        <span>{b.per_pagina}</span>
        <select value={per} onChange={(e) => router.push(indirizzoV2(href(1, Number(e.target.value)), prefissoIt))}>
          {SCELTE_PER_PAGINA.map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
      </label>
    </nav>
  );
}

/** Cosa contiene una sezione, in pastiglie con la loro parola: le carte e le stese del ramo («22 cards», «19 spreads»)
 *  e i suoi articoli con quelli delle sotto-sezioni («6 articles», lo stesso numero che mostra la pagina della
 *  sezione). Un contenitore come «Tarot» le mostra tutte; una sezione di carte o di stese non mostra «0 articles». Con
 *  un'API più vecchia (senza `n_carte`/`n_stese`) carte e stese vengono da `n_elementi`. */
function Conti({ n }: { n: NodoSezione }) {
  const { t } = useLingua();
  const b = t.blog;
  const carte = n.n_carte ?? (n.tipo === "carte" ? n.n_elementi ?? 0 : 0);
  const stese = n.n_stese ?? (n.tipo === "stese" ? n.n_elementi ?? 0 : 0);
  const voci = [
    carte > 0 ? plurale(carte, b.conta_carte) : null,
    stese > 0 ? plurale(stese, b.conta_stese) : null,
    n.n_articoli > 0 || (!carte && !stese) ? plurale(n.n_articoli, b.conta_articoli) : null,
  ].filter((v): v is string => v !== null);
  return <span className="albero-conti">{voci.map((v) => <span key={v} className="albero-conta">{v}</span>)}</span>;
}

/* Le sezioni come un piccolo albero (v8.5): ogni ramo collegato al padre da un tratto d'ottone, cosa contiene in
 * pastiglie (`Conti`), la sezione corrente in prugna. Voci alte 44px: si toccano bene anche sul telefono. */
function Albero({ nodi, corrente, livello = 0 }: { nodi: NodoSezione[]; corrente?: string; livello?: number }) {
  return (
    <ul className={livello === 0 ? "albero-sezioni" : "albero-rami"}>
      {nodi.map((n) => (
        <li key={n.id}>
          <LinkV2 className="albero-voce" href={R.blogSezione(n.slug)} aria-current={n.slug === corrente ? "page" : undefined}>
            <span className="albero-nome">{n.nome}</span>
            <Conti n={n} />
          </LinkV2>
          {n.figli.length > 0 && <Albero nodi={n.figli} corrente={corrente} livello={livello + 1} />}
        </li>
      ))}
    </ul>
  );
}

/** I gradi delle carte minori in numeri romani, per il sigillo delle sezioni «By number» (`aces` → I). */
const ROMANI: Record<string, string> = {
  asso: "I", ace: "I", aces: "I", "1": "I", due: "II", two: "II", twos: "II", "2": "II",
  tre: "III", three: "III", threes: "III", "3": "III", quattro: "IV", four: "IV", fours: "IV", "4": "IV",
  cinque: "V", five: "V", fives: "V", "5": "V", sei: "VI", six: "VI", sixes: "VI", "6": "VI",
  sette: "VII", seven: "VII", sevens: "VII", "7": "VII", otto: "VIII", eight: "VIII", eights: "VIII", "8": "VIII",
  nove: "IX", nine: "IX", nines: "IX", "9": "IX", dieci: "X", ten: "X", tens: "X", "10": "X",
  // Le figure: principessa e principe cominciano con la stessa lettera, il principe ne prende due.
  principe: "Pr", prince: "Pr", princes: "Pr",
};

/** Il segno nel sigillo di una sezione senza immagine: il numero romano di un grado, il quadrato delle stese,
 *  altrimenti l'iniziale del nome. */
function sigla(n: NodoSezione): string {
  const rango = n.filtro?.rango;
  if (rango && ROMANI[String(rango).toLowerCase()]) return ROMANI[String(rango).toLowerCase()];
  if (n.tipo === "stese") return "▦";
  return (n.nome.trim()[0] ?? "✦").toUpperCase();
}

/** Il segnaposto di un'immagine che non c'è ancora: una lastra prugna con un sigillo d'ottone (lo stesso cerchio del
 *  rito in home) e il segno della sezione. Decorativo: il nome sta già nel riquadro. */
function Sigillo({ segno }: { segno: string }) {
  return (
    <span className="sigillo" aria-hidden="true">
      <span className="sigillo-cerchio"><span className="sigillo-segno">{segno}</span></span>
    </span>
  );
}

/** L'alt di un'immagine dentro un link che ha già il nome scritto: vuoto se ripete solo il nome. */
const altUtile = (alt: string | null | undefined, nome: string) => (alt && alt.trim() !== nome.trim() ? alt : "");

/* Le sotto-sezioni come riquadri (v9.4, al posto dell'albero): l'immagine della sezione (o il sigillo), il nome, cosa
 * contiene (`Conti`) e 3 articoli del suo ramo scelti per la giornata. Immagine e nome sono un solo link; gli
 * articoli i loro, alti 44 px. */
function RiquadriSezioni({ nodi }: { nodi: NodoSezione[] }) {
  return (
    <ul className="riquadri-sezioni">
      {nodi.map((n) => {
        const img = urlMedia(n.immagine?.mini ?? n.immagine?.url);
        return (
          <li key={n.id} className="riquadro-sezione">
            <LinkV2 className="riquadro-testa" href={R.blogSezione(n.slug)}>
              <span className="riquadro-immagine">
                {img
                  // eslint-disable-next-line @next/next/no-img-element
                  ? <img src={img} alt={altUtile(n.immagine?.alt, n.nome)} loading="lazy" width={480} height={270} />
                  : <Sigillo segno={sigla(n)} />}
              </span>
              <span className="riquadro-nome">{n.nome}<span className="riquadro-freccia" aria-hidden="true">→</span></span>
            </LinkV2>
            <Conti n={n} />
            {(n.articoli ?? []).length > 0 && (
              <ul className="riquadro-articoli">
                {(n.articoli ?? []).slice(0, 3).map((a) => (
                  <li key={a.slug}><LinkV2 href={R.articolo(a.slug)}>{a.titolo}</LinkV2></li>
                ))}
              </ul>
            )}
          </li>
        );
      })}
    </ul>
  );
}

/* Le stese di una sezione «stese» (v9.4), in schede ricche: l'illustrazione con lo schema della stesa sovrapposto in
 * una lastra prugna (senza illustrazione lo schema occupa tutta la lastra), la tradizione e il numero di carte, il
 * nome, l'introduzione breve, la lettura con quella stesa e il link alla sua pagina. */
function SchedeStese({ elementi }: { elementi: ElementoStesa[] }) {
  const { t, lingua } = useLingua();
  const b = t.blog;
  const nome = (s: ElementoStesa) =>
    s.lang === linguaContenuti(lingua) ? s.nome : nomeStesaDaNomi(s.nome, s.nomi, lingua as Lingua);
  return (
    <ul className="schede-stese">
      {elementi.map((s) => {
        const n = nome(s);
        const img = urlMedia(s.immagine?.mini ?? s.immagine?.url);
        // La tradizione nella lingua della pagina; per una lingua senza traduzione, quella dei testi (l'inglese).
        const tradizione = s.tradizioni?.[lingua] ?? s.tradizioni?.[linguaContenuti(lingua)] ?? s.tradizione;
        const pagina = R.stesa(s.slug ?? s.id);
        return (
          <li key={s.id} className="scheda-stesa">
            <LinkV2 className={`scheda-stesa-lastra ${img ? "con-immagine" : ""}`} href={pagina} tabIndex={-1} aria-hidden="true">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              {img && <img src={img} alt="" loading="lazy" width={480} height={300} />}
              <span className="scheda-stesa-schema"><MiniaturaStesa stesa={s} /></span>
            </LinkV2>
            <div className="scheda-stesa-corpo">
              <p className="scheda-stesa-sopra">
                {[tradizione, plurale(s.n_carte, t.lettura.n_carte)].filter(Boolean).join(" · ")}
              </p>
              <h3><LinkV2 href={pagina}>{n}</LinkV2></h3>
              {s.descrizione_breve && <p className="scheda-stesa-intro">{s.descrizione_breve}</p>}
              <div className="scheda-stesa-azioni">
                <LinkV2 className="button button-brass button-small" href={`${R.leggi}?spread=${encodeURIComponent(s.id)}&source=journal`}>
                  {b.stesa_inizia}
                </LinkV2>
                <LinkV2 className="inline small" href={pagina}>{b.stesa_posizioni}</LinkV2>
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

function Laterale({ corrente }: { corrente?: string }) {
  const { t } = useLingua();
  const albero = useCarica(sezioni, [], { pubblico: true, iniziale: P.sezioni() });
  const tag = useCarica(etichette, [], { pubblico: true, iniziale: P.etichette() });
  return (
    <aside className="journal-aside" aria-label={t.blog.sezioni}>
      <section className="sezioni-box" aria-labelledby="titolo-sezioni">
        <h2 id="titolo-sezioni">{t.blog.sezioni}</h2>
        {albero.dati && <Albero nodi={albero.dati} corrente={corrente} />}
      </section>
      {(tag.dati ?? []).length > 0 && (
        <section className="sezioni-box" aria-labelledby="titolo-etichette">
          <h2 id="titolo-etichette">{t.blog.etichette}</h2>
          <ul className="chips">
            {(tag.dati ?? []).slice(0, 24).map((e) => <li key={e.slug}><LinkV2 className="chip" href={R.blogTag(e.slug)}>{e.nome}</LinkV2></li>)}
          </ul>
        </section>
      )}
    </aside>
  );
}

/** I 10 a caso delle pagine del Diario (v8.5): sotto gli ultimi articoli, solo in prima pagina, ognuno col link alla
 *  sua sezione. Stessa scelta per tutta la giornata (la decide il server). */
function SceltiACaso({ percorso, escludi = [] }: { percorso: string; escludi?: ArticoloBreve[] }) {
  const { t } = useLingua();
  const b = t.blog;
  const nove = useCarica(() => leggiApi<Nove>(percorso), [percorso], { pubblico: true, iniziale: percorso });
  // L'API esclude al più 12 recenti (`recentiDiario`): gli altri articoli della prima pagina si tolgono qui.
  const visti = new Set(escludi.map((a) => a.slug));
  const scelti = (nove.dati?.scelti ?? []).filter((a) => !visti.has(a.slug));
  if (!scelti.length) return null;
  return (
    <section className="journal-a-caso" aria-labelledby="titolo-a-caso">
      <h2 id="titolo-a-caso" className="diario-nove-sotto">{b.a_caso}</h2>
      <div className="journal-grid">
        {scelti.map((a) => (
          <div key={a.slug} className="diario-nove-voce">
            <Tessera a={a} />
            {a.sezione && (
              <LinkV2 className="inline small" href={R.blogSezione(a.sezione.slug)}>{f(b.nove_sezione, { sezione: a.sezione.nome })}</LinkV2>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

function Ponte() {
  const { t } = useLingua();
  return (
    <div className="share-band" style={{ marginTop: ".85rem" }}>
      <div><p className="eyebrow">{t.blog.ponte_titolo}</p><p>{t.blog.ponte_testo}</p></div>
      <div><LinkV2 className="button button-brass" href={`${R.leggi}?source=journal`}>{t.blog.ponte_cta}</LinkV2></div>
    </div>
  );
}

export function Diario() {
  return <Suspense fallback={null}><DiarioContenuto /></Suspense>;
}

function DiarioContenuto() {
  const { t, lingua, prefissoIt } = useLingua();
  const b = t.blog;
  const router = useRouter();
  const parametri = useSearchParams();
  const q = parametri.get("q") ?? "";
  const { pagina, per } = usePaginazione();
  const [testo, setTesto] = useState(q);
  const elenco = useCarica(() => articoli(lingua, { q, pagina, per_pagina: per }), [lingua, q, pagina, per], { pubblico: true, iniziale: P.articoli(lingua, { q, pagina, per_pagina: per }) });
  const evidenza = useCarica(() => (q || pagina > 1 ? Promise.resolve(null) : articoli(lingua, { evidenza: "true", per_pagina: 1 })), [lingua, q, pagina], { pubblico: true, iniziale: q || pagina > 1 ? null : P.articoli(lingua, { evidenza: "true", per_pagina: 1 }) });
  const primo = evidenza.dati?.articoli[0] ?? null;
  const lista = (elenco.dati?.articoli ?? []).filter((a) => a.slug !== primo?.slug);

  return (
    <section className="band band-tight">
      <form role="search" className="question-form" style={{ marginBottom: ".7rem" }} onSubmit={(e) => {
        e.preventDefault();
        const pulito = testo.trim();
        router.push(indirizzoV2(pulito ? `${R.blog}?q=${encodeURIComponent(pulito)}` : R.blog, prefissoIt));
      }}>
        <label className="sr-only" htmlFor="cerca-diario">{b.cerca}</label>
        <input id="cerca-diario" type="search" name="q" value={testo} onChange={(e) => setTesto(e.target.value)} placeholder={b.cerca_segnaposto} maxLength={100} />
        <button type="submit" className="button">{b.cerca_vai}</button>
      </form>
      <div className="story-grid journal-layout">
        <div>
          {q && elenco.dati && <p role="status">{f(plurale(elenco.dati.totale, b.risultati), { q })}</p>}
          {elenco.errore && <p className="error">{elenco.errore}</p>}
          {elenco.dati && lista.length === 0 && !primo && <p className="notice">{q ? b.nessun_risultato : b.vuoto}</p>}
          {/* Gli spazi pubblicitari (spenti per default) fra i blocchi presenti: in evidenza, ultimi, scelti a caso;
              la fine prima del ponte verso la lettura. */}
          <ConPubblicita dentro>
            {primo && <div key="primo" style={{ marginBottom: ".5rem" }}><Tessera a={primo} grande /></div>}
            {lista.length > 0 && (
              <Fragment key="lista">
                {!q && <p className="eyebrow">{b.ultimi}</p>}
                <div className="journal-grid">{lista.map((a) => <Tessera key={a.slug} a={a} />)}</div>
                {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} totale={elenco.dati.totale} base={R.blog} q={q} per={per} />}
              </Fragment>
            )}
            {!q && pagina === 1 && <SceltiACaso key="caso" percorso={P.nove({ recenti: recentiDiario(per), scelti: 10 })} escludi={[...lista, ...(primo ? [primo] : [])]} />}
          </ConPubblicita>
          {elenco.dati && lista.length === 0 && <Pagine pagina={pagina} pagine={elenco.dati.pagine} totale={elenco.dati.totale} base={R.blog} q={q} per={per} />}
          <Ponte />
        </div>
        <Laterale />
      </div>
    </section>
  );
}

export function SezioneDiario({ slug }: { slug: string }) {
  return <Suspense fallback={null}><SezioneContenuto slug={slug} /></Suspense>;
}

function SezioneContenuto({ slug }: { slug: string }) {
  const { t, lingua } = useLingua();
  const b = t.blog;
  const { pagina, per } = usePaginazione();
  const s = useCarica(() => sezione(slug, lingua), [slug, lingua], { pubblico: true, iniziale: P.sezione(slug, lingua) });
  const elenco = useCarica(() => articoli(lingua, { sezione: slug, pagina, per_pagina: per }), [slug, lingua, pagina, per], { pubblico: true, iniziale: P.articoli(lingua, { sezione: slug, pagina, per_pagina: per }) });
  if (s.errore) return <section className="band band-tight"><p className="notice">{b.vuoto}</p></section>;
  if (!s.dati) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const d = s.dati;
  const lista = elenco.dati?.articoli ?? [];
  const carte = d.tipo === "carte" ? (d.elementi as unknown as Carta[]) : [];
  const stese = d.tipo === "stese" ? (d.elementi as unknown as ElementoStesa[]) : [];
  return (
    <>
      <section className="subhero subhero-compact">
        <nav aria-label={b.percorso} className="small muted" style={{ marginBottom: "1rem" }}>
          <LinkV2 className="inline" href={R.blog}>{b.eyebrow}</LinkV2>
          {d.briciole.filter((x) => x.slug !== d.slug).map((x) => <span key={x.slug}> · <LinkV2 className="inline" href={R.blogSezione(x.slug)}>{x.nome}</LinkV2></span>)}
        </nav>
        <h1 className="display">{d.nome}</h1>
        {d.descrizione && <p className="section-intro">{d.descrizione}</p>}
        <div className="sezione-conti"><Conti n={d} /></div>
      </section>
      {/* Il contenuto della sezione a tutta larghezza (v9.4): le sotto-sezioni in riquadri, le carte, le stese. Poi gli
          articoli nella colonna, con le sezioni e le etichette accanto. */}
      {(d.figli.length > 0 || carte.length > 0 || stese.length > 0) && (
        <section className="band band-tight sezione-catalogo">
          {d.figli.length > 0 && (
            <div className="sezione-blocco" aria-labelledby="titolo-sottosezioni">
              <h2 id="titolo-sottosezioni" className="sezione-blocco-titolo">{b.sottosezioni}</h2>
              <RiquadriSezioni nodi={d.figli} />
            </div>
          )}
          {carte.length > 0 && (
            <div className="sezione-blocco" aria-labelledby="titolo-carte-sezione">
              <h2 id="titolo-carte-sezione" className="sezione-blocco-titolo">{b.carte_sezione}</h2>
              <div className="cards-grid cards-grid-sezione">
                {carte.map((c) => (
                  <LinkV2 key={c.id} className="card-tile" href={R.carta(c.slug ?? c.id)}>
                    <ImmagineCarta id={c.id} alt="" mazzo={null} />
                    <span>{nomeDi(c, lingua)}</span>
                    {c.arcano_label && <small>{c.arcano === "maggiore" ? c.numero_romano : c.seme_label}</small>}
                  </LinkV2>
                ))}
              </div>
            </div>
          )}
          {stese.length > 0 && (
            <div className="sezione-blocco" aria-labelledby="titolo-stese-sezione">
              <h2 id="titolo-stese-sezione" className="sezione-blocco-titolo">{b.stese_sezione}</h2>
              <SchedeStese elementi={stese} />
            </div>
          )}
        </section>
      )}
      <section className="band band-tight story-grid journal-layout">
        <div>
          <ConPubblicita dentro>
            {lista.length > 0 && (
              <Fragment key="lista">
                <p className="eyebrow">{b.articoli}</p>
                <div className="journal-grid">{lista.map((a) => <Tessera key={a.slug} a={a} />)}</div>
                {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} totale={elenco.dati.totale} base={R.blogSezione(slug)} per={per} />}
              </Fragment>
            )}
            {pagina === 1 && <SceltiACaso key="caso" percorso={P.nove({ sezione: slug, recenti: recentiDiario(per), scelti: 10, completa: false })} escludi={lista} />}
          </ConPubblicita>
          {/* «Ancora nessun articolo» se il ramo non ha né articoli né carte o stese (un contenitore di sezioni vuote). */}
          {elenco.dati && lista.length === 0 && (d.tipo === "articoli" || d.tipo === "contenitore") && !d.n_carte && !d.n_stese
            && (d.figli.length === 0 || d.n_carte !== undefined) && <p className="notice">{b.vuoto}</p>}
          <Ponte />
        </div>
        <Laterale corrente={slug} />
      </section>
    </>
  );
}

export function EtichettaDiario({ slug }: { slug: string }) {
  return <Suspense fallback={null}><EtichettaContenuto slug={slug} /></Suspense>;
}

function EtichettaContenuto({ slug }: { slug: string }) {
  const { t, lingua } = useLingua();
  const b = t.blog;
  const { pagina, per } = usePaginazione();
  const tag = useCarica(etichette, [], { pubblico: true, iniziale: P.etichette() });
  const elenco = useCarica(() => articoli(lingua, { tag: slug, pagina, per_pagina: per }), [slug, lingua, pagina, per], { pubblico: true, iniziale: P.articoli(lingua, { tag: slug, pagina, per_pagina: per }) });
  const nome = tag.dati?.find((e) => e.slug === slug)?.nome ?? slug;
  const lista = elenco.dati?.articoli ?? [];
  return (
    <>
      <section className="subhero subhero-compact">
        <nav aria-label={b.percorso} className="small muted" style={{ marginBottom: "1rem" }}><LinkV2 className="inline" href={R.blog}>{b.eyebrow}</LinkV2></nav>
        <p className="eyebrow">{b.etichette}</p>
        <h1 className="display">{nome}</h1>
      </section>
      <section className="band band-tight story-grid journal-layout">
        <div>
          {elenco.dati && lista.length === 0 && <p className="notice">{b.vuoto}</p>}
          <ConPubblicita dentro>
            <Fragment key="lista">
              <div className="journal-grid">{lista.map((a) => <Tessera key={a.slug} a={a} />)}</div>
              {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} totale={elenco.dati.totale} base={R.blogTag(slug)} per={per} />}
            </Fragment>
            {pagina === 1 && <SceltiACaso key="caso" percorso={P.nove({ tag: slug, recenti: recentiDiario(per), scelti: 10, completa: false })} escludi={lista} />}
          </ConPubblicita>
          <Ponte />
        </div>
        <Laterale />
      </section>
    </>
  );
}

/** L'elenco completo degli articoli su una carta o una stesa, in fondo alla sua pagina (v9.4): prima quelli che ne
 *  parlano come soggetto, poi quelli che la citano (`GET /blog/posts?carta=` / `?stesa=`), con la paginazione del
 *  Journal. Niente se non ce n'è nessuno. */
export function ArticoliSu(props: { tipo: "carta" | "stesa"; id: string; nome: string; base: string }) {
  return <Suspense fallback={null}><ArticoliSuContenuto {...props} /></Suspense>;
}

function ArticoliSuContenuto({ tipo, id, nome, base }: { tipo: "carta" | "stesa"; id: string; nome: string; base: string }) {
  const { t } = useLingua();
  const b = t.blog;
  const { pagina, per } = usePaginazione();
  const elenco = usePubblico<ElencoArticoli>(P.elencoSu(tipo, id, pagina, per));
  const dati = elenco.dati;
  if (!dati || dati.totale === 0) return null;
  return (
    <section id="articoli-su" className="band band-tight articoli-su" aria-labelledby="titolo-articoli-su">
      <div className="section-head">
        <div>
          <p className="eyebrow">{b.eyebrow}</p>
          <h2 id="titolo-articoli-su" className="section-title">{f(b.articoli_su, { nome })}</h2>
        </div>
        <span className="albero-conta articoli-su-conta">{plurale(dati.totale, b.conta_articoli)}</span>
      </div>
      <div className="journal-grid">{dati.articoli.map((a) => <Tessera key={a.slug} a={a} />)}</div>
      <Pagine pagina={pagina} pagine={dati.pagine} totale={dati.totale} base={base} per={per} ancora="articoli-su" />
    </section>
  );
}

function forme(id: string, slugs: Record<string, string>) {
  return [id, ...Object.values(slugs)];
}

export function ArticoloDiario({ slug }: { slug: string }) {
  const { t, locale, lingua } = useLingua();
  const b = t.blog;
  const a = useCarica(() => articolo(slug), [slug], { pubblico: true, iniziale: P.articolo(slug) });
  const [copiato, setCopiato] = useState(false);
  /* Gli spazi pubblicitari dentro il testo (a un terzo e a due terzi): il testo si taglia solo se se ne vede uno. */
  const conInserti = usePubblicitaVisibile(["terzo", "due_terzi"]);
  /* v9.5: gli articoli sono solo in inglese; dove il browser sa tradurre sul dispositivo, titolo, testo e domande
   * si traducono nella lingua del sito (`AvvisoTraduzione` lo dice e offre l'originale). */
  const testa = useRef<HTMLDivElement>(null);
  const corpo = useRef<HTMLDivElement>(null);
  const traduzione = useTraduzione([testa, corpo], lingua, {
    sorgente: a.dati?.lang ?? null,
    chiave: a.dati ? `${a.dati.slug}:${a.dati.aggiornato_il ?? a.dati.pubblicato_il ?? ""}` : undefined,
  });
  if (a.errore) {
    return (
      <section className="band band-tight">
        <p className="section-intro">{b.non_trovato}</p>
        <LinkV2 className="button button-quiet" href={R.blog}>{b.eyebrow}</LinkV2>
      </section>
    );
  }
  const x = a.dati;
  if (!x) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const rif: Riferimenti = {
    carte: Object.fromEntries(x.collegamenti.carte.flatMap((c) => forme(c.id, c.slugs).map((k) => [k, c.nome]))),
    stese: Object.fromEntries(x.collegamenti.stese.flatMap((s) => forme(s.id, s.slugs).map((k) => [k, s.nome]))),
    articoli: Object.fromEntries(x.collegamenti.articoli.map((y) => [y.slug, y.titolo])),
    idCarte: Object.fromEntries(x.collegamenti.carte.flatMap((c) => forme(c.id, c.slugs).map((k) => [k, c.id]))),
  };
  const immagine = urlMedia(x.immagine?.url);
  const url = urlPubblico(linguaPubblica(x.lang), R.articolo(x.slug));
  const condividi = async () => {
    if (navigator.share) { try { await navigator.share({ title: x.titolo, url }); return; } catch { /* annullato */ } }
    try { await navigator.clipboard.writeText(url); setCopiato(true); } catch { /* niente */ }
  };

  return (
    <article lang={x.lang}>
      <section className="subhero subhero-compact">
        <nav aria-label={b.percorso} className="small muted" style={{ marginBottom: "1rem" }}>
          <LinkV2 className="inline" href={R.blog}>{b.eyebrow}</LinkV2>
          {x.briciole.map((y) => <span key={y.slug}> · <LinkV2 className="inline" href={R.blogSezione(y.slug)}>{y.nome}</LinkV2></span>)}
        </nav>
        <AvvisoTraduzione stato={traduzione} />
        <div ref={testa} lang={x.lang}>
          <h1 className="display" style={{ maxWidth: "22ch" }}>{x.titolo}</h1>
          {x.sottotitolo && <p className="section-intro">{x.sottotitolo}</p>}
        </div>
        <p className="small muted">
          {x.autore.nome && f(b.di, { nome: x.autore.nome })}
          {x.pubblicato_il && ` · ${dataLeggibile(x.pubblicato_il, locale)}`} · {f(b.min, { n: x.tempo_lettura })}
          {x.aggiornato_il && x.pubblicato_il && x.aggiornato_il.slice(0, 10) !== x.pubblicato_il.slice(0, 10) && ` · ${f(b.aggiornato, { data: dataLeggibile(x.aggiornato_il, locale) })}`}
        </p>
      </section>
      <section className="band band-tight">
        {immagine && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={immagine} alt={x.immagine?.alt ?? ""} width={x.immagine?.larghezza ?? 1200} height={x.immagine?.altezza ?? 675}
            style={{ display: "block", width: "100%", maxWidth: 960, height: "auto", marginBottom: ".7rem" }} fetchPriority="high" />
        )}
        <div ref={corpo} lang={x.lang}>
          <BlogMarkdownV2 testo={x.testo} riferimenti={rif} etichette={{ carta: b.tipo_carta, stesa: b.tipo_stesa, articolo: b.tipo_articolo }}
            inserti={conInserti ? { terzo: <Pubblicita posizione="terzo" dentro />, due_terzi: <Pubblicita posizione="due_terzi" dentro /> } : undefined} />

          {x.faq.length > 0 && (
            <div className="faq-list" style={{ maxWidth: "68ch", marginTop: ".85rem" }}>
              <p className="eyebrow" data-no-trad>{b.domande}</p>
              {x.faq.map((q) => <details key={q.domanda} className="faq-item"><summary>{q.domanda}</summary><p>{q.risposta}</p></details>)}
            </div>
          )}
        </div>

        {(x.collegamenti.carte.length > 0 || x.collegamenti.stese.length > 0) && (
          <div style={{ marginTop: ".85rem" }}>
            <p className="eyebrow">{b.si_parla_di}</p>
            <ul className="chips">
              {x.collegamenti.carte.map((c) => <li key={c.id}><LinkV2 className="chip" href={R.carta(c.id)}>✦ {c.nome}</LinkV2></li>)}
              {x.collegamenti.stese.map((s) => <li key={s.id}><LinkV2 className="chip" href={R.stesa(s.id)}>▦ {s.nome}</LinkV2></li>)}
            </ul>
          </div>
        )}
        {x.tags.length > 0 && (
          <ul className="chips" style={{ marginTop: "1rem" }} aria-label={b.etichette}>
            {x.tags.map((e) => <li key={e.slug}><LinkV2 className="chip" href={R.blogTag(e.slug)}>#{e.nome}</LinkV2></li>)}
          </ul>
        )}
        <div className="button-row" style={{ marginTop: ".55rem" }}>
          <button type="button" className="button button-quiet button-small" onClick={condividi} data-an="share_started" data-an-cosa="articolo">
            {copiato ? b.copiato : b.condividi}
          </button>
        </div>
        <Pubblicita posizione="fine" dentro />
        <Ponte />

        {x.correlati.length > 0 && (
          <div style={{ marginTop: "1.05rem" }}>
            <p className="eyebrow">{b.correlati}</p>
            <div className="journal-grid">{x.correlati.slice(0, 3).map((y) => <Tessera key={y.slug} a={y} />)}</div>
          </div>
        )}
        {(x.precedente || x.successivo) && (
          <nav className="pager" aria-label={b.articoli}>
            {x.precedente ? <LinkV2 className="inline" href={R.articolo(x.precedente.slug)} rel="prev">← {x.precedente.titolo}</LinkV2> : <span />}
            {x.successivo ? <LinkV2 className="inline" href={R.articolo(x.successivo.slug)} rel="next">{x.successivo.titolo} →</LinkV2> : <span />}
          </nav>
        )}
        <p className="small muted articolo-copyright">
          {f(b.copyright, { anno: (x.pubblicato_il ?? x.aggiornato_il ?? "").slice(0, 4) })}
        </p>
      </section>
      <DiarioNove contesto={{ articolo: x.slug }} ordine="scelti" lang={x.lang} />
    </article>
  );
}

export function Esplora() {
  const { t } = useLingua();
  const b = t.blog;
  const dove: Record<string, string> = { diario: R.blog, carte: R.carte, stese: R.stese, mazzi: R.mazzi, giorno: R.giorno, fisica: R.fisica };
  return (
    <>
      <section className="subhero subhero-compact">
        <p className="eyebrow">{b.esplora_eyebrow}</p>
        <h1 className="display">{b.esplora_titolo}</h1>
        <p className="section-intro">{b.esplora_intro}</p>
      </section>
      <section className="band band-tight">
        <div className="difference-grid even" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}>
          {b.esplora_voci.map((v) => (
            <LinkV2 key={v.chiave} className="difference" href={dove[v.chiave]}>
              <span aria-hidden="true">{v.simbolo}</span><h3>{v.titolo}</h3><p>{v.testo}</p>
            </LinkV2>
          ))}
        </div>
      </section>
      {/* Pagina corta come la carta del giorno: un terzo dopo le voci, due terzi dentro il diario, la fine dopo. */}
      <Pubblicita posizione="terzo" />
      <DiarioNove eyebrow={b.esplora_ultimi} inMezzo={<Pubblicita posizione="due_terzi" dentro />} />
      <Pubblicita posizione="fine" />
    </>
  );
}
