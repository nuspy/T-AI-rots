"use client";

/* Il testo di un articolo nella v2: lo stesso Markdown sicuro del sito (`app/(sito)/blog/componenti/blog-markdown.tsx`:
 * niente HTML eseguito, immagini solo relative o https, video YouTube «nocookie» in una sandbox), con due differenze:
 * le scorciatoie `[[carta:…]]`, `[[stesa:…]]`, `[[articolo:…]]` portano alle pagine della v2, e ogni collegamento
 * interno scritto nel testo verso il sito si traduce nella pagina v2 corrispondente (`inV2`). */

import { Fragment } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { urlMedia } from "@/lib/blog";
import { R, inV2 } from "@/v2/lib/percorsi";
import LinkV2 from "./link";
import stili from "./blog.module.css";

export interface Riferimenti {
  carte: Record<string, string>;
  stese: Record<string, string>;
  articoli: Record<string, string>;
  idCarte?: Record<string, string>;
}

const BLOCCO = /^[ \t]*\[\[(carta|card|stesa|spread|articolo|post):([a-z0-9-]+)\]\][ \t]*$/;
const IN_LINEA = /\[\[(carta|card|stesa|spread|articolo|post):([a-z0-9-]+)\]\]/g;
const BLOCCO_VIDEO = /^[ \t]*\[\[video:youtube:([A-Za-z0-9_-]{6,20})\]\][ \t]*$/;

type Tipo = "carta" | "stesa" | "articolo";
const CANONICO: Record<string, Tipo> = { carta: "carta", card: "carta", stesa: "stesa", spread: "stesa", articolo: "articolo", post: "articolo" };
const indirizzo = (tipo: Tipo, id: string) => (tipo === "carta" ? R.carta(id) : tipo === "stesa" ? R.stesa(id) : R.articolo(id));
const nomeDi = (tipo: Tipo, id: string, rif: Riferimenti) =>
  tipo === "carta" ? rif.carte[id] : tipo === "stesa" ? rif.stese[id] : rif.articoli[id];

function inLinea(testo: string, rif: Riferimenti): string {
  return testo.replace(IN_LINEA, (_m, scritto: string, id: string) => {
    const tipo = CANONICO[scritto];
    const nome = nomeDi(tipo, id, rif);
    return nome ? `[${nome.replace(/[[\]]/g, "")}](${indirizzo(tipo, id)})` : "";
  });
}

export interface EtichetteTipo { carta: string; stesa: string; articolo: string }

const componenti: Components = {
  h1: ({ children }) => <h2>{children}</h2>,
  a: ({ href, children }) => {
    if (!href) return <>{children}</>;
    if (href.startsWith("/")) return <LinkV2 href={inV2(href)}>{children}</LinkV2>;
    if (href.startsWith("#")) return <a href={href}>{children}</a>;
    return <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>;
  },
  img: ({ src, alt }) => {
    const s = typeof src === "string" ? src : "";
    if (!(s.startsWith("/") || s.startsWith("https://"))) return null;
    const url = s.startsWith("/blog/media/") ? (urlMedia(s) ?? s) : s;
    // eslint-disable-next-line @next/next/no-img-element -- immagini di un articolo, di misure sconosciute
    return <img src={url} alt={alt ?? ""} loading="lazy" />;
  },
  table: ({ children }) => <div className={stili.tabella}><table>{children}</table></div>,
};

export function BlogMarkdownV2({ testo, riferimenti, etichette }: { testo: string; riferimenti: Riferimenti; etichette: EtichetteTipo }) {
  const pezzi: ({ md: string } | { tipo: Tipo; id: string; idCarta?: string; nome: string } | { video: string })[] = [];
  let corrente: string[] = [];
  const chiudi = () => { if (corrente.length) pezzi.push({ md: corrente.join("\n") }); corrente = []; };
  for (const riga of testo.split("\n")) {
    const v = BLOCCO_VIDEO.exec(riga);
    if (v) { chiudi(); pezzi.push({ video: v[1] }); continue; }
    const m = BLOCCO.exec(riga);
    const tipo = m ? CANONICO[m[1]] : undefined;
    const nome = m && tipo ? nomeDi(tipo, m[2], riferimenti) : undefined;
    if (m && tipo && nome) { chiudi(); pezzi.push({ tipo, id: m[2], idCarta: riferimenti.idCarte?.[m[2]], nome }); }
    else corrente.push(riga);
  }
  chiudi();

  return (
    <div className={stili.testo} dir="auto">
      {pezzi.map((p, i) =>
        "md" in p ? (
          <ReactMarkdown key={i} remarkPlugins={[remarkGfm]} components={componenti}>{inLinea(p.md, riferimenti)}</ReactMarkdown>
        ) : "video" in p ? (
          <div key={i} className={stili.video}>
            <iframe src={`https://www.youtube-nocookie.com/embed/${p.video}`} title="Video" loading="lazy"
              allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              referrerPolicy="strict-origin-when-cross-origin" sandbox="allow-scripts allow-same-origin allow-presentation" allowFullScreen />
          </div>
        ) : (
          <Fragment key={i}>
            <LinkV2 href={indirizzo(p.tipo, p.id)} className={stili.scheda}>
              {p.tipo === "carta" && (
                // eslint-disable-next-line @next/next/no-img-element -- la carta vera, piccola
                <img src={`/cards/${p.idCarta ?? p.id}.webp`} alt="" width={72} height={128} loading="lazy" />
              )}
              <span><small>{etichette[p.tipo]}</small><strong>{p.nome}</strong></span>
            </LinkV2>
          </Fragment>
        ),
      )}
    </div>
  );
}
