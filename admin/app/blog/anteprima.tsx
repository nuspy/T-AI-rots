"use client";

import ReactMarkdown, { type Components } from "react-markdown";
import remarkDirective from "remark-directive";
import remarkGfm from "remark-gfm";
import { API } from "@/lib/api";
import { direttiveBlog } from "@/lib/direttive-blog";
import type { Riferimento } from "@/lib/blog";
import stili from "./blog.module.css";

/* L'anteprima di un articolo: come si legge sul sito, o abbastanza da accorgersi di un errore.
 *
 * Vale la regola del sito: il Markdown si rende **senza eseguire HTML** (nessun `rehype-raw`), le
 * immagini si accettano solo relative o `https`, i collegamenti esterni si aprono in una scheda nuova. Le
 * scorciatoie `[[carta:maj-17]]`, `[[stesa:croce-celtica]]` e `[[articolo:slug]]` qui diventano un
 * riquadro col nome — o col nome in rosso se la carta o la stesa non esistono: sul sito un riferimento
 * sbagliato sparisce in silenzio, ed è meglio accorgersene prima di pubblicare. */

const SCORCIATOIA = /\[\[(carta|stesa|articolo):([a-z0-9-]+)\]\]/g;
/* Un video su una riga da sola: sul sito un riquadro YouTube o Vimeo; qui un segnaposto col suo indirizzo. */
const VIDEO = /^[ \t]*\[\[video:(youtube|vimeo):([A-Za-z0-9_-]{6,20})\]\][ \t]*$/gm;

export interface Catalogo {
  carte: Riferimento[];
  stese: Riferimento[];
}

/* Le scorciatoie diventano collegamenti a un'àncora speciale: la resa del riquadro sta in `componenti.a`. */
function conRiferimenti(testo: string, catalogo: Catalogo): string {
  const nomi = {
    carta: new Map(catalogo.carte.map((c) => [c.id, c.nome])),
    stesa: new Map(catalogo.stese.map((s) => [s.id, s.nome])),
  };
  const conVideo = testo.replace(VIDEO, (_m, fonte: string, id: string) =>
    `[▶ video ${fonte === "vimeo" ? "Vimeo" : "YouTube"} · ${id}](${fonte === "vimeo" ? `https://vimeo.com/${id}` : `https://www.youtube.com/watch?v=${id}`})`);
  return conVideo.replace(SCORCIATOIA, (_m, tipo: "carta" | "stesa" | "articolo", id: string) => {
    const nome = tipo === "articolo" ? id : nomi[tipo].get(id);
    const etichetta = nome ? `${tipo} · ${nome}` : `${tipo} · ${id} (non esiste)`;
    return `[${etichetta.replace(/[[\]]/g, "")}](#rif-${nome ? "ok" : "no"})`;
  });
}

/* Un percorso relativo dell'API (`/blog/media/…`) sta sull'API, non sulla console. */
function sorgente(src: string): string | null {
  if (src.startsWith("/blog/media/")) return `${API}${src}`;
  if (src.startsWith("https://") || src.startsWith("/")) return src;
  return null;
}

const componenti: Components = {
  h1: ({ children }) => <h2>{children}</h2>,
  a: ({ href, children }) => {
    if (href === "#rif-ok") return <span className={stili.riferimento}>{children}</span>;
    if (href === "#rif-no") {
      return (
        <span className={stili.riferimento} style={{ color: "var(--allarme)", borderColor: "var(--allarme)" }}>
          {children}
        </span>
      );
    }
    if (!href) return <>{children}</>;
    return (
      <a href={href} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    );
  },
  img: ({ src, alt, title }) => {
    const s = typeof src === "string" ? sorgente(src) : null;
    if (!s) return null;
    // eslint-disable-next-line @next/next/no-img-element -- anteprima di un'immagine di misura sconosciuta
    const immagine = <img src={s} alt={alt ?? ""} />;
    return title ? <span className="md-figura">{immagine}<span className="md-didascalia">{title}</span></span> : immagine;
  },
  table: ({ children }) => (
    <div className={stili.tabellaAnteprima}>
      <table>{children}</table>
    </div>
  ),
};

export function Anteprima({
  titolo,
  sottotitolo,
  testo,
  catalogo,
}: {
  titolo: string;
  sottotitolo: string;
  testo: string;
  catalogo: Catalogo;
}) {
  return (
    <article className={stili.anteprima} aria-label="Anteprima dell'articolo" dir="auto">
      <h1 className={stili.anteprimaTitolo}>{titolo || "Senza titolo"}</h1>
      {sottotitolo && <p className={stili.anteprimaSotto}>{sottotitolo}</p>}
      {testo.trim() ? (
        <ReactMarkdown remarkPlugins={[remarkGfm, remarkDirective, direttiveBlog]} components={componenti}>
          {conRiferimenti(testo, catalogo)}
        </ReactMarkdown>
      ) : (
        <p style={{ color: "var(--inchiostro-debole)" }}>Il testo è ancora vuoto.</p>
      )}
    </article>
  );
}
