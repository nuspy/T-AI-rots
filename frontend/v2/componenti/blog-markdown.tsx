"use client";

/* Il testo di un articolo nella v2: lo stesso Markdown sicuro del sito (`app/(sito)/blog/componenti/blog-markdown.tsx`:
 * niente HTML eseguito, immagini solo relative o https, video YouTube «nocookie» in una sandbox), con due differenze:
 * le scorciatoie `[[carta:…]]`, `[[stesa:…]]`, `[[articolo:…]]` portano alle pagine della v2, e ogni collegamento
 * interno scritto nel testo verso il sito si traduce nella pagina v2 corrispondente (`inV2`). */

import { Fragment } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkDirective from "remark-directive";
import remarkGfm from "remark-gfm";
import { urlMedia } from "@/lib/blog";
import { direttiveBlog } from "@/v2/lib/direttive-blog";
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
/* Un video su una riga da sola: YouTube (in modalità «nocookie») o Vimeo (con `dnt=1`, senza tracciamento). */
const BLOCCO_VIDEO = /^[ \t]*\[\[video:(youtube|vimeo):([A-Za-z0-9_-]{6,20})\]\][ \t]*$/;
const urlVideo = (fonte: string, id: string) =>
  fonte === "vimeo" ? `https://player.vimeo.com/video/${id}?dnt=1` : `https://www.youtube-nocookie.com/embed/${id}`;

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
  img: ({ src, alt, title }) => {
    const s = typeof src === "string" ? src : "";
    if (!(s.startsWith("/") || s.startsWith("https://"))) return null;
    const url = s.startsWith("/blog/media/") ? (urlMedia(s) ?? s) : s;
    // eslint-disable-next-line @next/next/no-img-element -- immagini di un articolo, di misure sconosciute
    const immagine = <img src={url} alt={alt ?? ""} loading="lazy" />;
    /* Il titolo dell'immagine (`![alt](url "didascalia")`) diventa la didascalia. `span` e non `figure`: l'immagine
     * sta dentro un paragrafo, dove un `figure` non è permesso. */
    return title ? <span className="md-figura">{immagine}<span className="md-didascalia">{title}</span></span> : immagine;
  },
  table: ({ children }) => <div className={stili.tabella}><table>{children}</table></div>,
};

/* Un inizio di blocco prima del quale si può inserire qualcosa senza rompere il Markdown: un titolo, o una riga che non
 * apre né continua un elenco, una citazione, una tabella, una direttiva, un'immagine o un riferimento. */
const INIZIO_SICURO = /^(#{1,6}\s|[^\s\-*+>|:![\d])/;

/** Un pezzo di Markdown tagliato dove un inserto non rompe nulla: righe vuote fuori dai blocchi di codice e dalle
 *  direttive (`:::`), prima di un inizio sicuro. Riunire i pezzi ridà esattamente il testo. */
function blocchiSicuri(md: string): string[] {
  const righe = md.split("\n");
  const fuori: string[] = [];
  let corrente: string[] = [];
  let recinto = false;
  let direttive = 0;
  righe.forEach((riga, i) => {
    if (/^\s*(```|~~~)/.test(riga)) recinto = !recinto;
    else if (!recinto && /^\s*:::+\s*\S/.test(riga)) direttive++;
    else if (!recinto && /^\s*:::+\s*$/.test(riga)) direttive = Math.max(0, direttive - 1);
    corrente.push(riga);
    const prossima = righe[i + 1];
    if (riga.trim() === "" && !recinto && direttive === 0 && prossima !== undefined && INIZIO_SICURO.test(prossima)
        && corrente.some((x) => x.trim() !== "")) {
      fuori.push(corrente.join("\n"));
      corrente = [];
    }
  });
  if (corrente.length) fuori.push(corrente.join("\n"));
  return fuori;
}

/** Gli spazi da inserire nel testo, a circa un terzo e due terzi della sua lunghezza (gli spazi pubblicitari). */
export interface InsertiTesto { terzo?: React.ReactNode; due_terzi?: React.ReactNode }

export function BlogMarkdownV2({
  testo, riferimenti, etichette, inserti,
}: { testo: string; riferimenti: Riferimenti; etichette: EtichetteTipo; inserti?: InsertiTesto }) {
  const pezzi: ({ md: string } | { tipo: Tipo; id: string; idCarta?: string; nome: string } | { video: string })[] = [];
  let corrente: string[] = [];
  const chiudi = () => { if (corrente.length) pezzi.push({ md: corrente.join("\n") }); corrente = []; };
  for (const riga of testo.split("\n")) {
    const v = BLOCCO_VIDEO.exec(riga);
    if (v) { chiudi(); pezzi.push({ video: urlVideo(v[1], v[2]) }); continue; }
    const m = BLOCCO.exec(riga);
    const tipo = m ? CANONICO[m[1]] : undefined;
    const nome = m && tipo ? nomeDi(tipo, m[2], riferimenti) : undefined;
    if (m && tipo && nome) { chiudi(); pezzi.push({ tipo, id: m[2], idCarta: riferimenti.idCarte?.[m[2]], nome }); }
    else corrente.push(riga);
  }
  chiudi();

  /* Con degli inserti, il Markdown si taglia nei punti sicuri e gli inserti vanno prima del primo blocco che comincia
   * dopo un terzo (e dopo due terzi) della lunghezza. Senza, i pezzi restano quelli di sempre. */
  const unita: typeof pezzi = inserti
    ? pezzi.flatMap((p): typeof pezzi => ("md" in p ? blocchiSicuri(p.md).map((md) => ({ md })) : [p]))
    : pezzi;
  const prima = new Map<number, React.ReactNode>();
  if (inserti) {
    const pesi = unita.map((u) => ("md" in u ? u.md.length : 200));
    const totale = pesi.reduce((a, b) => a + b, 0);
    let fin = 0;
    let terzo = false;
    for (let i = 1; i < unita.length; i++) {
      fin += pesi[i - 1];
      if (!terzo && fin >= totale / 3) {
        prima.set(i, inserti.terzo);
        terzo = true;
      } else if (terzo && fin >= (2 * totale) / 3) {
        prima.set(i, inserti.due_terzi);
        break;
      }
    }
  }

  return (
    <div className={stili.testo} dir="auto">
      {unita.map((p, i) => (
        <Fragment key={i}>
          {prima.get(i)}
          {"md" in p ? (
            <ReactMarkdown remarkPlugins={[remarkGfm, remarkDirective, direttiveBlog]} components={componenti}>{inLinea(p.md, riferimenti)}</ReactMarkdown>
          ) : "video" in p ? (
            <div className={stili.video}>
              <iframe src={p.video} title="Video" loading="lazy"
                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerPolicy="strict-origin-when-cross-origin" sandbox="allow-scripts allow-same-origin allow-presentation" allowFullScreen />
            </div>
          ) : (
            <LinkV2 href={indirizzo(p.tipo, p.id)} className={stili.scheda}>
              {p.tipo === "carta" && (
                // eslint-disable-next-line @next/next/no-img-element -- la carta vera, piccola
                <img src={`/cards/${p.idCarta ?? p.id}.webp`} alt="" width={72} height={128} loading="lazy" />
              )}
              <span><small>{etichette[p.tipo]}</small><strong>{p.nome}</strong></span>
            </LinkV2>
          )}
        </Fragment>
      ))}
    </div>
  );
}
