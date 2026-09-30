"use client";

/* Il diario (il blog) nella v2: un grafo di contenuti, non una lista di post (specifica v2, §14). Ogni articolo
 * porta a una carta, una stesa, un mazzo, e infine a una domanda. I dati vengono dall'API del blog; ogni
 * collegamento resta dentro la v2. Include «Explore», il punto d'ingresso del grafo. */

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import type { Carta, Stesa } from "@/lib/api";
import { dataLeggibile, urlMedia, type ArticoloBreve, type NodoSezione } from "@/lib/blog";
import { SITE_URL } from "@/lib/condivisione";
import { f, plurale } from "@/v2/i18n";
import { BlogMarkdownV2, type Riferimenti } from "@/v2/componenti/blog-markdown";
import { ImmagineCarta } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { articoli, articolo, etichette, sezione, sezioni } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";
import { nomeDi } from "./carte";

const PER_PAGINA = 12;

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

function Albero({ nodi, corrente }: { nodi: NodoSezione[]; corrente?: string }) {
  return (
    <ul className="list-plain tree">
      {nodi.map((n) => (
        <li key={n.id}>
          <LinkV2 href={R.blogSezione(n.slug)} aria-current={n.slug === corrente ? "page" : undefined}>
            {n.nome} <small className="muted">({n.n_articoli})</small>
          </LinkV2>
          {n.figli.length > 0 && <Albero nodi={n.figli} corrente={corrente} />}
        </li>
      ))}
    </ul>
  );
}

function Laterale({ corrente }: { corrente?: string }) {
  const { t } = useLingua();
  const albero = useCarica(sezioni, [], { pubblico: true });
  const tag = useCarica(etichette, [], { pubblico: true });
  return (
    <aside className="story-sidebar" aria-label={t.blog.sezioni}>
      <h2>{t.blog.sezioni}</h2>
      {albero.dati && <Albero nodi={albero.dati} corrente={corrente} />}
      {(tag.dati ?? []).length > 0 && (
        <>
          <h2 style={{ marginTop: "1.6rem" }}>{t.blog.etichette}</h2>
          <ul className="chips">
            {(tag.dati ?? []).slice(0, 24).map((e) => <li key={e.slug}><LinkV2 className="chip" href={R.blogTag(e.slug)}>{e.nome}</LinkV2></li>)}
          </ul>
        </>
      )}
    </aside>
  );
}

function Ponte() {
  const { t } = useLingua();
  return (
    <div className="share-band" style={{ marginTop: "2.4rem" }}>
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
  const elenco = useCarica(() => articoli(lingua, { q, pagina, per_pagina: PER_PAGINA }), [lingua, q, pagina], { pubblico: true });
  const evidenza = useCarica(() => (q || pagina > 1 ? Promise.resolve(null) : articoli(lingua, { evidenza: "true", per_pagina: 1 })), [lingua, q, pagina], { pubblico: true });
  const primo = evidenza.dati?.articoli[0] ?? null;
  const lista = (elenco.dati?.articoli ?? []).filter((a) => a.slug !== primo?.slug);

  return (
    <section className="band band-tight">
      <form role="search" className="question-form" style={{ marginBottom: "2rem" }} onSubmit={(e) => {
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
          {primo && <div style={{ marginBottom: "1.2rem" }}><Tessera a={primo} grande /></div>}
          {elenco.errore && <p className="error">{elenco.errore}</p>}
          {elenco.dati && lista.length === 0 && !primo && <p className="notice">{q ? b.nessun_risultato : b.vuoto}</p>}
          {lista.length > 0 && (
            <>
              {!q && <p className="eyebrow">{b.ultimi}</p>}
              <div className="journal-grid">{lista.map((a) => <Tessera key={a.slug} a={a} />)}</div>
            </>
          )}
          {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} base={R.blog} q={q} />}
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
  const s = useCarica(() => sezione(slug, lingua), [slug, lingua], { pubblico: true });
  const elenco = useCarica(() => articoli(lingua, { sezione: slug, pagina, per_pagina: PER_PAGINA }), [slug, lingua, pagina], { pubblico: true });
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
          {d.figli.length > 0 && (<><p className="eyebrow">{b.sottosezioni}</p><Albero nodi={d.figli} /></>)}
          {d.tipo === "carte" && (
            <>
              <p className="eyebrow" style={{ marginTop: "1.4rem" }}>{b.carte_sezione}</p>
              <div className="cards-grid">
                {(d.elementi as unknown as Carta[]).map((c) => (
                  <LinkV2 key={c.id} className="card-tile" href={R.carta(c.slug ?? c.id)}>
                    <ImmagineCarta id={c.id} alt="" mazzo={null} /><span>{nomeDi(c, lingua)}</span>
                  </LinkV2>
                ))}
              </div>
            </>
          )}
          {d.tipo === "stese" && (
            <>
              <p className="eyebrow" style={{ marginTop: "1.4rem" }}>{b.stese_sezione}</p>
              <ul className="chips">
                {(d.elementi as unknown as Stesa[]).map((x) => <li key={x.id}><LinkV2 className="chip" href={R.stesa(x.slug ?? x.id)}>{x.nome}</LinkV2></li>)}
              </ul>
            </>
          )}
          {lista.length > 0 && (
            <>
              <p className="eyebrow" style={{ marginTop: "1.8rem" }}>{b.articoli}</p>
              <div className="journal-grid">{lista.map((a) => <Tessera key={a.slug} a={a} />)}</div>
              {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} base={R.blogSezione(slug)} />}
            </>
          )}
          {elenco.dati && lista.length === 0 && d.figli.length === 0 && d.tipo === "articoli" && <p className="notice">{b.vuoto}</p>}
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
  const tag = useCarica(etichette, [], { pubblico: true });
  const elenco = useCarica(() => articoli(lingua, { tag: slug, pagina, per_pagina: PER_PAGINA }), [slug, lingua, pagina], { pubblico: true });
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
          <div className="journal-grid">{lista.map((a) => <Tessera key={a.slug} a={a} />)}</div>
          {elenco.dati && <Pagine pagina={pagina} pagine={elenco.dati.pagine} base={R.blogTag(slug)} />}
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
  const a = useCarica(() => articolo(slug), [slug], { pubblico: true });
  const [copiato, setCopiato] = useState(false);
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
  const url = `${SITE_URL}${R.articolo(x.slug)}`;
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
            style={{ display: "block", width: "100%", maxWidth: 960, height: "auto", marginBottom: "2rem" }} fetchPriority="high" />
        )}
        <BlogMarkdownV2 testo={x.testo} riferimenti={rif} etichette={{ carta: b.tipo_carta, stesa: b.tipo_stesa, articolo: b.tipo_articolo }} />

        {x.faq.length > 0 && (
          <div className="faq-list" style={{ maxWidth: "68ch", marginTop: "2.4rem" }}>
            <p className="eyebrow">{b.domande}</p>
            {x.faq.map((q) => <details key={q.domanda} className="faq-item"><summary>{q.domanda}</summary><p>{q.risposta}</p></details>)}
          </div>
        )}

        {(x.collegamenti.carte.length > 0 || x.collegamenti.stese.length > 0) && (
          <div style={{ marginTop: "2.4rem" }}>
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
        <div className="button-row" style={{ marginTop: "1.6rem" }}>
          <button type="button" className="button button-quiet button-small" onClick={condividi} data-an="share_started" data-an-cosa="articolo">
            {copiato ? b.copiato : b.condividi}
          </button>
        </div>
        <Ponte />

        {x.correlati.length > 0 && (
          <div style={{ marginTop: "3rem" }}>
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
      </section>
    </article>
  );
}

export function Esplora() {
  const { t, lingua } = useLingua();
  const b = t.blog;
  const diario = useCarica(() => articoli(lingua, { per_pagina: 3 }), [lingua], { pubblico: true });
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
      {(diario.dati?.articoli ?? []).length > 0 && (
        <section className="band band-tight">
          <div className="section-head">
            <p className="eyebrow">{b.esplora_ultimi}</p>
            <LinkV2 className="button button-quiet" href={R.blog}>{t.home.diario_cta}</LinkV2>
          </div>
          <div className="content-grid">{diario.dati!.articoli.map((a) => <Tessera key={a.slug} a={a} />)}</div>
        </section>
      )}
    </>
  );
}
