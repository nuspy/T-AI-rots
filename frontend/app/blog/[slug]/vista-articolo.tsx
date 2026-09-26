"use client";

/* La pagina di un articolo: percorso, titolo, firma, immagine, testo, argomenti citati, condivisione,
 * articoli affini, precedente e successivo. Tutto già scritto dal server. */

import Link from "next/link";
import { SITE_URL } from "@/lib/condivisione";
import { dataLeggibile, urlMedia, type ArticoloBlog } from "@/lib/blog";
import { useLingua } from "@/lib/lingua";
import { ESTENSIONE } from "../../componenti/carta";
import { Involucro } from "../../componenti/testata";
import { BlogMarkdown, type Riferimenti } from "../componenti/blog-markdown";
import { CondividiArticolo } from "../componenti/condividi-articolo";
import { Briciole, JsonLd, RigaMeta, SchedaArticolo } from "../componenti/elementi";
import stili from "../blog.module.css";

export function VistaArticolo({ articolo: a, riferimenti }: { articolo: ArticoloBlog; riferimenti: Riferimenti }) {
  const { t, locale } = useLingua();
  const url = `${SITE_URL}/blog/${a.slug}`;
  const immagine = urlMedia(a.immagine?.url);
  const voci = [
    { href: "/blog", nome: t.blog_blog },
    ...a.briciole.map((b) => ({ href: `/blog/sezione/${b.slug}`, nome: b.nome })),
    { href: `/blog/${a.slug}`, nome: a.titolo },
  ];
  const { carte, stese } = a.collegamenti;
  const cita = carte.length + stese.length > 0;

  const dati = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: a.titolo,
    description: a.seo_descrizione,
    image: immagine ? [immagine] : undefined,
    datePublished: a.pubblicato_il ?? undefined,
    dateModified: a.aggiornato_il ?? a.pubblicato_il ?? undefined,
    author: { "@type": "Person", name: a.autore.nome },
    publisher: { "@type": "Organization", name: "T·AI·rots", url: SITE_URL },
    mainEntityOfPage: url,
    inLanguage: a.lang,
    keywords: a.tags.map((x) => x.nome).join(", ") || undefined,
  };
  const briciole = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: voci.map((v, i) => ({
      "@type": "ListItem", position: i + 1, name: v.nome, item: `${SITE_URL}${v.href}`,
    })),
  };

  return (
    <Involucro pubblica larga>
      <article className={stili.articolo}>
        <div>
          <Briciole voci={voci} />
          <header style={{ display: "grid", gap: 14 }}>
            <h1>{a.titolo}</h1>
            {a.sottotitolo && <p className={stili.sottotitoloArticolo}>{a.sottotitolo}</p>}
            <RigaMeta articolo={a} />
            {a.aggiornato_il && a.pubblicato_il && a.aggiornato_il.slice(0, 10) !== a.pubblicato_il.slice(0, 10) && (
              <span className={stili.meta}>{t.blog_aggiornato(dataLeggibile(a.aggiornato_il, locale))}</span>
            )}
          </header>
        </div>

        {immagine && (
          // eslint-disable-next-line @next/next/no-img-element -- immagine dell'articolo, con le misure vere
          <img
            className={stili.immagineArticolo}
            src={immagine}
            alt={a.immagine?.alt ?? ""}
            width={a.immagine?.larghezza ?? 1200}
            height={a.immagine?.altezza ?? 675}
            fetchPriority="high"
          />
        )}

        <BlogMarkdown
          testo={a.testo}
          riferimenti={riferimenti}
          etichette={{ carta: t.blog_tipo_carta, stesa: t.blog_tipo_stesa, articolo: t.blog_tipo_articolo }}
        />

        {a.tags.length > 0 && (
          <ul className={stili.etichette} aria-label={t.blog_etichette}>
            {a.tags.map((e) => (
              <li key={e.slug}><Link href={`/blog/tag/${e.slug}`} className={stili.etichetta}>#{e.nome}</Link></li>
            ))}
          </ul>
        )}

        {cita && (
          <section className={stili.blocco} aria-label={t.blog_si_parla_di}>
            <h2>{t.blog_si_parla_di}</h2>
            <ul className={stili.etichette}>
              {carte.map((c) => (
                <li key={c.id}>
                  <Link href={`/carte/${c.id}`} className={stili.chip}>
                    {/* eslint-disable-next-line @next/next/no-img-element -- la carta, piccola */}
                    <img src={`/cards/${c.id}.${ESTENSIONE}`} alt="" width={30} height={53} loading="lazy" />
                    {c.nome_it}
                  </Link>
                </li>
              ))}
              {stese.map((s) => (
                <li key={s.id}>
                  <Link href={`/stese/${s.id}`} className={`${stili.chip} ${stili.chipSenzaImmagine}`}>▦ {s.nome}</Link>
                </li>
              ))}
            </ul>
          </section>
        )}

        <CondividiArticolo url={url} titolo={a.titolo} />

        {a.correlati.length > 0 && (
          <section className={stili.blocco} aria-label={t.blog_correlati}>
            <h2>{t.blog_correlati}</h2>
            <div className={stili.griglia}>
              {a.correlati.map((x) => <SchedaArticolo key={x.slug} articolo={x} />)}
            </div>
          </section>
        )}

        {(a.precedente || a.successivo) && (
          <nav className={stili.vicini} aria-label={t.blog_articoli_sezione}>
            {a.precedente ? (
              <Link href={`/blog/${a.precedente.slug}`} className={`pannello ${stili.vicino}`} rel="prev">
                <small>← {t.blog_precedente}</small><strong>{a.precedente.titolo}</strong>
              </Link>
            ) : <span />}
            {a.successivo ? (
              <Link href={`/blog/${a.successivo.slug}`} className={`pannello ${stili.vicino}`} rel="next">
                <small>{t.blog_successivo} →</small><strong>{a.successivo.titolo}</strong>
              </Link>
            ) : <span />}
          </nav>
        )}
      </article>
      <JsonLd dati={dati} />
      <JsonLd dati={briciole} />
    </Involucro>
  );
}
