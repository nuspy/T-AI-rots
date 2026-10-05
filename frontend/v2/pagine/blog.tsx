"use client";

/* Il diario (il blog) nella v2: un grafo di contenuti, non una lista di post (specifica v2, §14). Ogni articolo
 * porta a una carta, una stesa, un mazzo, e infine a una domanda. I dati vengono dall'API del blog; ogni
 * collegamento resta dentro la v2. Include «Explore», il punto d'ingresso del grafo.
 *
 * Gli spazi pubblicitari (spenti per default): negli elenchi fra i blocchi della colonna (`ConPubblicita`), prima del
 * ponte verso la lettura; nell'articolo dentro il testo a un terzo e a due terzi, e alla fine prima del ponte. */

import { Fragment, Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { leggiApi, type Carta, type Stesa } from "@/lib/api";
import { dataLeggibile, urlMedia, type ArticoloBreve, type NodoSezione } from "@/lib/blog";
import { f, plurale } from "@/v2/i18n";
import { BlogMarkdownV2, type Riferimenti } from "@/v2/componenti/blog-markdown";
import { ImmagineCarta } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { ConPubblicita, Pubblicita, usePubblicitaVisibile } from "@/v2/componenti/pubblicita";
import { P, PER_PAGINA_BLOG, articoli, articolo, etichette, sezione, sezioni } from "@/v2/lib/dati";
import { linguaPubblica } from "@/lib/indirizzi";
import { urlPubblico } from "@/lib/seo";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";
import { nomeDi } from "./carte";

const PER_PAGINA = PER_PAGINA_BLOG;

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
 *  a caso fra quelli attinenti alla pagina, ciascuno col link alla sezione da cui viene. `vuoto` si mostra se il
 *  diario non ha ancora articoli. */
export function DiarioNove({
  contesto = {}, eyebrow, titolo, vuoto = null, inMezzo = null,
}: {
  contesto?: { carta?: string; stesa?: string; sezione?: string; articolo?: string };
  eyebrow?: string;
  titolo?: string;
  vuoto?: React.ReactNode;
  /** Fra i recenti e gli attinenti: uno spazio pubblicitario nelle pagine corte, dove il diario è metà del contenuto. */
  inMezzo?: React.ReactNode;
}) {
  const { t } = useLingua();
  const b = t.blog;
  const percorso = P.nove(contesto);
  const nove = useCarica(() => leggiApi<Nove>(percorso), [percorso], { pubblico: true, iniziale: percorso });
  const recenti = nove.dati?.recenti ?? [];
  const scelti = nove.dati?.scelti ?? [];
  if (!recenti.length && !scelti.length) return vuoto ? <>{vuoto}</> : null;
  return (
    <section className="band band-tight diario-nove" aria-labelledby="titolo-nove">
      <div className="section-head">
        <div>
          <p className="eyebrow">{eyebrow ?? b.nove_eyebrow}</p>
          <h2 id="titolo-nove" className="section-title">{titolo ?? b.nove_titolo}</h2>
        </div>
        <LinkV2 className="button button-quiet" href={R.blog}>{b.nove_ultimi}</LinkV2>
      </div>
      <div className="content-grid">{recenti.map((a) => <Tessera key={a.slug} a={a} />)}</div>
      {scelti.length > 0 && inMezzo}
      {scelti.length > 0 && (
        <>
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
        </>
      )}
    </section>
  );
}

function Pagine({ pagina, pagine, base, q }: { pagina: number; pagine: number; base: string; q?: string }) {
  const { t } = useLingua();
  if (pagine <= 1) return null;
  const href = (p: number) => {
    const s = new URLSearchParams();
    if (q) s.set("q", q);
    if (p > 1) s.set("page", String(p));
    const qs = s.toString();
    return qs ? `${base}?${qs}` : base;
  };
  return (
    <nav className="pager" aria-label={f(t.blog.pagina, { p: pagina, n: pagine })}>
      {pagina > 1 ? <LinkV2 className="button button-quiet button-small" href={href(pagina - 1)} rel="prev">{t.blog.piu_recenti}</LinkV2> : <span />}
      <span className="small muted">{f(t.blog.pagina, { p: pagina, n: pagine })}</span>
      {pagina < pagine ? <LinkV2 className="button button-quiet button-small" href={href(pagina + 1)} rel="next">{t.blog.meno_recenti}</LinkV2> : <span />}
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
function SceltiACaso({ percorso }: { percorso: string }) {
  const { t } = useLingua();
  const b = t.blog;
  const nove = useCarica(() => leggiApi<Nove>(percorso), [percorso], { pubblico: true, iniziale: percorso });
  const scelti = nove.dati?.scelti ?? [];
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
  const pagina = Math.max(1, Number(parametri.get("page") ?? 1) || 1);
  const [testo, setTesto] = useState(q);
  const elenco = useCarica(() => articoli(lingua, { q, pagina, per_pagina: PER_PAGINA }), [lingua, q, pagina], { pubblico: true, iniziale: P.articoli(lingua, { q, pagina, per_pagina: PER_PAGINA }) });
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
                {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} base={R.blog} q={q} />}
              </Fragment>
            )}
            {!q && pagina === 1 && <SceltiACaso key="caso" percorso={P.nove({ recenti: PER_PAGINA, scelti: 10 })} />}
          </ConPubblicita>
          {elenco.dati && lista.length === 0 && <Pagine pagina={pagina} pagine={elenco.dati.pagine} base={R.blog} q={q} />}
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
  const parametri = useSearchParams();
  const pagina = Math.max(1, Number(parametri.get("page") ?? 1) || 1);
  const s = useCarica(() => sezione(slug, lingua), [slug, lingua], { pubblico: true, iniziale: P.sezione(slug, lingua) });
  const elenco = useCarica(() => articoli(lingua, { sezione: slug, pagina, per_pagina: PER_PAGINA }), [slug, lingua, pagina], { pubblico: true, iniziale: P.articoli(lingua, { sezione: slug, pagina, per_pagina: PER_PAGINA }) });
  if (s.errore) return <section className="band band-tight"><p className="notice">{b.vuoto}</p></section>;
  if (!s.dati) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const d = s.dati;
  const lista = elenco.dati?.articoli ?? [];
  return (
    <>
      <section className="subhero subhero-compact">
        <nav aria-label={b.percorso} className="small muted" style={{ marginBottom: "1rem" }}>
          <LinkV2 className="inline" href={R.blog}>{b.eyebrow}</LinkV2>
          {d.briciole.filter((x) => x.slug !== d.slug).map((x) => <span key={x.slug}> · <LinkV2 className="inline" href={R.blogSezione(x.slug)}>{x.nome}</LinkV2></span>)}
        </nav>
        <h1 className="display">{d.nome}</h1>
        {d.descrizione && <p className="section-intro">{d.descrizione}</p>}
      </section>
      <section className="band band-tight story-grid journal-layout">
        <div>
          <ConPubblicita dentro>
            {d.figli.length > 0 && (
              <section key="figli" className="sezioni-box" aria-labelledby="titolo-sottosezioni">
                <h2 id="titolo-sottosezioni">{b.sottosezioni}</h2>
                <Albero nodi={d.figli} />
              </section>
            )}
            {d.tipo === "carte" && (
              <Fragment key="carte">
                <p className="eyebrow" style={{ marginTop: ".5rem" }}>{b.carte_sezione}</p>
                <div className="cards-grid">
                  {(d.elementi as unknown as Carta[]).map((c) => (
                    <LinkV2 key={c.id} className="card-tile" href={R.carta(c.slug ?? c.id)}>
                      <ImmagineCarta id={c.id} alt="" mazzo={null} /><span>{nomeDi(c, lingua)}</span>
                    </LinkV2>
                  ))}
                </div>
              </Fragment>
            )}
            {d.tipo === "stese" && (
              <Fragment key="stese">
                <p className="eyebrow" style={{ marginTop: ".5rem" }}>{b.stese_sezione}</p>
                <ul className="chips">
                  {(d.elementi as unknown as Stesa[]).map((x) => <li key={x.id}><LinkV2 className="chip" href={R.stesa(x.slug ?? x.id)}>{x.nome}</LinkV2></li>)}
                </ul>
              </Fragment>
            )}
            {lista.length > 0 && (
              <Fragment key="lista">
                <p className="eyebrow" style={{ marginTop: ".65rem" }}>{b.articoli}</p>
                <div className="journal-grid">{lista.map((a) => <Tessera key={a.slug} a={a} />)}</div>
                {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} base={R.blogSezione(slug)} />}
              </Fragment>
            )}
            {pagina === 1 && <SceltiACaso key="caso" percorso={P.nove({ sezione: slug, recenti: PER_PAGINA, scelti: 10, completa: false })} />}
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
  const parametri = useSearchParams();
  const pagina = Math.max(1, Number(parametri.get("page") ?? 1) || 1);
  const tag = useCarica(etichette, [], { pubblico: true, iniziale: P.etichette() });
  const elenco = useCarica(() => articoli(lingua, { tag: slug, pagina, per_pagina: PER_PAGINA }), [slug, lingua, pagina], { pubblico: true, iniziale: P.articoli(lingua, { tag: slug, pagina, per_pagina: PER_PAGINA }) });
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
              {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} base={R.blogTag(slug)} />}
            </Fragment>
            {pagina === 1 && <SceltiACaso key="caso" percorso={P.nove({ tag: slug, recenti: PER_PAGINA, scelti: 10, completa: false })} />}
          </ConPubblicita>
          <Ponte />
        </div>
        <Laterale />
      </section>
    </>
  );
}

function forme(id: string, slugs: Record<string, string>) {
  return [id, ...Object.values(slugs)];
}

export function ArticoloDiario({ slug }: { slug: string }) {
  const { t, locale } = useLingua();
  const b = t.blog;
  const a = useCarica(() => articolo(slug), [slug], { pubblico: true, iniziale: P.articolo(slug) });
  const [copiato, setCopiato] = useState(false);
  /* Gli spazi pubblicitari dentro il testo (a un terzo e a due terzi): il testo si taglia solo se se ne vede uno. */
  const conInserti = usePubblicitaVisibile(["terzo", "due_terzi"]);
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
        <h1 className="display" style={{ maxWidth: "22ch" }}>{x.titolo}</h1>
        {x.sottotitolo && <p className="section-intro">{x.sottotitolo}</p>}
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
        <BlogMarkdownV2 testo={x.testo} riferimenti={rif} etichette={{ carta: b.tipo_carta, stesa: b.tipo_stesa, articolo: b.tipo_articolo }}
          inserti={conInserti ? { terzo: <Pubblicita posizione="terzo" dentro />, due_terzi: <Pubblicita posizione="due_terzi" dentro /> } : undefined} />

        {x.faq.length > 0 && (
          <div className="faq-list" style={{ maxWidth: "68ch", marginTop: ".85rem" }}>
            <p className="eyebrow">{b.domande}</p>
            {x.faq.map((q) => <details key={q.domanda} className="faq-item"><summary>{q.domanda}</summary><p>{q.risposta}</p></details>)}
          </div>
        )}

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
      <DiarioNove contesto={{ articolo: x.slug }} />
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
