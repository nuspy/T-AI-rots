"use client";

/* I pezzi che il blog ripete ovunque: avatar, scheda di un articolo, briciole di pane,
 * albero delle sezioni, paginazione, dati strutturati. */

import Link from "@/app/(sito)/componenti/link";
import { dataLeggibile, urlMedia, type ArticoloBreve, type AutoreBlog, type NodoSezione } from "@/lib/blog";
import { useLingua } from "@/lib/lingua";
import stili from "../blog.module.css";

export function Avatar({ autore }: { autore: AutoreBlog }) {
  const src = urlMedia(autore.avatar);
  return src ? (
    // eslint-disable-next-line @next/next/no-img-element -- avatar di 256 px già ridotto dal server
    <img className={stili.avatar} src={src} alt="" width={28} height={28} loading="lazy" />
  ) : (
    <span className={stili.iniziale} aria-hidden="true">{(autore.nome[0] ?? "?").toUpperCase()}</span>
  );
}

export function RigaMeta({ articolo }: { articolo: ArticoloBreve }) {
  const { t, locale } = useLingua();
  return (
    <div className={stili.meta}>
      <span className={stili.autore}>
        <Avatar autore={articolo.autore} />
        {t.blog_di(articolo.autore.nome)}
      </span>
      {articolo.pubblicato_il && (
        <time dateTime={articolo.pubblicato_il}>{dataLeggibile(articolo.pubblicato_il, locale)}</time>
      )}
      <span>{t.blog_min_lettura(articolo.tempo_lettura)}</span>
    </div>
  );
}

export function SchedaArticolo({ articolo, grande = false }: { articolo: ArticoloBreve; grande?: boolean }) {
  // Negli elenchi la miniatura; la scheda grande in evidenza tiene l'immagine intera.
  const immagine = urlMedia((grande ? null : articolo.immagine?.mini) ?? articolo.immagine?.url);
  return (
    <Link
      href={`/blog/${articolo.slug}`}
      className={`pannello ${stili.scheda} ${grande ? stili.inEvidenza : ""}`}
    >
      {immagine ? (
        // eslint-disable-next-line @next/next/no-img-element -- immagine già ridotta dal server
        <img className={stili.schedaImmagine} src={immagine} alt={articolo.immagine?.alt ?? ""} width={800}
          height={450} loading={grande ? "eager" : "lazy"} />
      ) : (
        <div className={stili.segnaposto} aria-hidden="true">✦</div>
      )}
      <div className={stili.schedaCorpo}>
        {articolo.sezione && <span className={stili.sezionePillola}>{articolo.sezione.nome}</span>}
        <h3>{articolo.titolo}</h3>
        <p>{articolo.sottotitolo || articolo.estratto}</p>
        <RigaMeta articolo={articolo} />
      </div>
    </Link>
  );
}

export function Briciole({ voci }: { voci: { href: string; nome: string }[] }) {
  const { t } = useLingua();
  return (
    <nav aria-label={t.blog_percorso}>
      <ol className={stili.briciole}>
        {voci.map((v, i) => (
          <li key={v.href}>
            {i === voci.length - 1 ? <span aria-current="page">{v.nome}</span> : <Link href={v.href}>{v.nome}</Link>}
          </li>
        ))}
      </ol>
    </nav>
  );
}

const SEGNO_TIPO = { articoli: "", contenitore: "", carte: "◈", stese: "▦" } as const;

export function AlberoSezioni({ nodi, corrente }: { nodi: NodoSezione[]; corrente?: string }) {
  return (
    <ul className={stili.albero}>
      {nodi.map((n) => (
        <li key={n.slug}>
          <Link href={`/blog/sezione/${n.slug}`} aria-current={n.slug === corrente ? "page" : undefined}>
            <span>
              {SEGNO_TIPO[n.tipo] && <span className={stili.tipoSezione} aria-hidden="true">{SEGNO_TIPO[n.tipo]}</span>}
              {n.nome}
            </span>
            {(n.n_articoli > 0 || n.n_elementi) && <small>{n.n_elementi ?? n.n_articoli}</small>}
          </Link>
          {n.figli.length > 0 && <AlberoSezioni nodi={n.figli} corrente={corrente} />}
        </li>
      ))}
    </ul>
  );
}

export function Paginazione({
  pagina, pagine, base, parametri = {},
}: {
  pagina: number;
  pagine: number;
  /* Il percorso della pagina, senza query. */
  base: string;
  /* Gli altri parametri da conservare nel collegamento (per esempio la ricerca). */
  parametri?: Record<string, string | undefined>;
}) {
  const { t } = useLingua();
  if (pagine <= 1) return null;
  const href = (p: number) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(parametri)) if (v) q.set(k, v);
    if (p > 1) q.set("pagina", String(p));
    const s = q.toString();
    return s ? `${base}?${s}` : base;
  };
  return (
    <nav className={stili.paginazione} aria-label={t.blog_pagina_di(pagina, pagine)}>
      {pagina > 1 ? <Link href={href(pagina - 1)} rel="prev">{t.blog_indietro}</Link> : <span aria-disabled="true">{t.blog_indietro}</span>}
      <span>{t.blog_pagina_di(pagina, pagine)}</span>
      {pagina < pagine ? <Link href={href(pagina + 1)} rel="next">{t.blog_avanti}</Link> : <span aria-disabled="true">{t.blog_avanti}</span>}
    </nav>
  );
}

/** Dati strutturati (JSON-LD): `<` diventa `<`, perché un titolo scritto da un autore non possa
 *  chiudere il tag `<script>` (vedi la guida JSON-LD di Next). */
export function JsonLd({ dati }: { dati: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(dati).replace(/</g, "\\u003c") }}
    />
  );
}
