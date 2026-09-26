/* Il testo di un articolo: Markdown, reso senza eseguire HTML.
 *
 * `react-markdown` non interpreta l'HTML scritto nel testo (senza `rehype-raw` resta testo), quindi
 * un `<script>` in un articolo non fa niente. Tocca a noi decidere cosa diventano i collegamenti e
 * le immagini: i collegamenti interni sono `Link` del sito, quelli esterni si aprono in una scheda
 * nuova con `rel` prudente; le immagini si accettano solo relative o `https`.
 *
 * Le scorciatoie `[[carta:maj-17]]`, `[[stesa:croce-celtica]]`, `[[articolo:slug]]`:
 *  - da sole su una riga diventano una scheda (con l'immagine, se è una carta);
 *  - dentro una frase diventano un collegamento con il nome della carta, della stesa o dell'articolo.
 * Un riferimento che non esiste nel catalogo resta testo: mai un collegamento rotto. */

import { Fragment } from "react";
import Link from "next/link";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { ESTENSIONE } from "../../componenti/carta";
import { urlMedia } from "@/lib/blog";
import stili from "../blog.module.css";

export interface Riferimenti {
  carte: Record<string, string>;
  stese: Record<string, string>;
  articoli: Record<string, string>;
}

const BLOCCO = /^[ \t]*\[\[(carta|stesa|articolo):([a-z0-9-]+)\]\][ \t]*$/;
const IN_LINEA = /\[\[(carta|stesa|articolo):([a-z0-9-]+)\]\]/g;

const PERCORSO = { carta: "/carte", stesa: "/stese", articolo: "/blog" } as const;

function nomeDi(tipo: "carta" | "stesa" | "articolo", id: string, rif: Riferimenti): string | undefined {
  return tipo === "carta" ? rif.carte[id] : tipo === "stesa" ? rif.stese[id] : rif.articoli[id];
}

/* Le scorciatoie in linea diventano collegamenti Markdown (o si tolgono, se il riferimento non esiste). */
function inLinea(testo: string, rif: Riferimenti): string {
  return testo.replace(IN_LINEA, (_m, tipo: "carta" | "stesa" | "articolo", id: string) => {
    const nome = nomeDi(tipo, id, rif);
    return nome ? `[${nome.replace(/[[\]]/g, "")}](${PERCORSO[tipo]}/${id})` : "";
  });
}

export interface EtichetteTipo {
  carta: string;
  stesa: string;
  articolo: string;
}

function Scheda({
  tipo, id, nome, etichette,
}: {
  tipo: "carta" | "stesa" | "articolo";
  id: string;
  nome: string;
  etichette: EtichetteTipo;
}) {
  return (
    <Link href={`${PERCORSO[tipo]}/${id}`} className={stili.schedaIncorporata}>
      {tipo === "carta" && (
        // eslint-disable-next-line @next/next/no-img-element -- la carta vera, piccola
        <img src={`/cards/${id}.${ESTENSIONE}`} alt="" width={72} height={128} loading="lazy" />
      )}
      <span>
        <small>{etichette[tipo]}</small>
        <strong>{nome}</strong>
      </span>
    </Link>
  );
}

const componenti: Components = {
  h1: ({ children }) => <h2>{children}</h2>,
  a: ({ href, children }) => {
    if (!href) return <>{children}</>;
    if (href.startsWith("/")) return <Link href={href}>{children}</Link>;
    if (href.startsWith("#")) return <a href={href}>{children}</a>;
    return <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>;
  },
  img: ({ src, alt }) => {
    const s = typeof src === "string" ? src : "";
    if (!(s.startsWith("/") || s.startsWith("https://"))) return null;
    /* Le immagini della libreria si scrivono con il percorso relativo dell'API (`/blog/media/…`), così il testo
     * non dipende dall'host: qui diventano l'indirizzo vero. */
    const indirizzo = s.startsWith("/blog/media/") ? (urlMedia(s) ?? s) : s;
    // eslint-disable-next-line @next/next/no-img-element -- immagini di un articolo, di misure sconosciute
    return <img src={indirizzo} alt={alt ?? ""} loading="lazy" />;
  },
  /* Le tabelle larghe scorrono dentro il loro riquadro, non allargano la pagina. */
  table: ({ children }) => <div className={stili.tabella}><table>{children}</table></div>,
};

export function BlogMarkdown({
  testo, riferimenti, etichette,
}: {
  testo: string;
  riferimenti: Riferimenti;
  etichette: EtichetteTipo;
}) {
  /* Si spezza il testo alle scorciatoie «da sole su una riga»: ciò che sta in mezzo è Markdown. */
  const righe = testo.split("\n");
  const pezzi: ({ md: string } | { tipo: "carta" | "stesa" | "articolo"; id: string; nome: string })[] = [];
  let corrente: string[] = [];
  const chiudi = () => {
    if (corrente.length) pezzi.push({ md: corrente.join("\n") });
    corrente = [];
  };
  for (const riga of righe) {
    const m = BLOCCO.exec(riga);
    const nome = m ? nomeDi(m[1] as "carta" | "stesa" | "articolo", m[2], riferimenti) : undefined;
    if (m && nome) {
      chiudi();
      pezzi.push({ tipo: m[1] as "carta" | "stesa" | "articolo", id: m[2], nome });
    } else {
      corrente.push(riga);
    }
  }
  chiudi();

  return (
    <div className={stili.testo} dir="auto">
      {pezzi.map((p, i) =>
        "md" in p ? (
          <ReactMarkdown key={i} remarkPlugins={[remarkGfm]} components={componenti}>
            {inLinea(p.md, riferimenti)}
          </ReactMarkdown>
        ) : (
          <Fragment key={i}><Scheda tipo={p.tipo} id={p.id} nome={p.nome} etichette={etichette} /></Fragment>
        ),
      )}
    </div>
  );
}
