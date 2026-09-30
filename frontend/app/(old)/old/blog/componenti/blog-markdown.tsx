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
 * Un riferimento che non esiste nel catalogo resta testo: mai un collegamento rotto.
 *
 * `[[video:youtube:ID]]`, da solo su una riga, diventa un video incorporato (YouTube, dominio
 * "-nocookie" per non piazzare cookie prima di un'interazione). Non si ospita video propri: niente
 * infrastruttura di archiviazione video nel progetto, un link a un video già pubblicato basta ed è
 * molto più leggero. Solo YouTube per ora, l'id è validato dal formato (lettere/cifre/`-`/`_`) prima di
 * finire nell'`iframe`, che resta comunque `sandbox`-ato: mai HTML scritto dall'autore, sempre generato
 * da qui. */

import { Fragment } from "react";
import Link from "@/app/(old)/old/componenti/link";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { ESTENSIONE } from "../../componenti/carta";
import { urlMedia } from "@/lib/blog";
import stili from "../blog.module.css";

export interface Riferimenti {
  /* Nome di ogni forma con cui il testo può citare una carta o una stesa: l'id (`maj-17`) e gli slug in ogni lingua. */
  carte: Record<string, string>;
  stese: Record<string, string>;
  articoli: Record<string, string>;
  /* Da ogni forma all'id canonico della carta: serve all'immagine (`/cards/maj-17.webp`). */
  idCarte?: Record<string, string>;
}

/* Le scorciatoie si scrivono in italiano (`[[carta:maj-17]]`) o in inglese (`[[card:the-star]]`): stessa cosa. Il
 * riferimento è un id o uno slug in qualunque lingua; il server manda i nomi per ogni forma (`Riferimenti`). */
const BLOCCO = /^[ \t]*\[\[(carta|card|stesa|spread|articolo|post):([a-z0-9-]+)\]\][ \t]*$/;
const IN_LINEA = /\[\[(carta|card|stesa|spread|articolo|post):([a-z0-9-]+)\]\]/g;
const BLOCCO_VIDEO = /^[ \t]*\[\[video:youtube:([A-Za-z0-9_-]{6,20})\]\][ \t]*$/;

type Tipo = "carta" | "stesa" | "articolo";
const CANONICO: Record<string, Tipo> = { carta: "carta", card: "carta", stesa: "stesa", spread: "stesa", articolo: "articolo", post: "articolo" };
const PERCORSO = { carta: "/carte", stesa: "/stese", articolo: "/blog" } as const;

function nomeDi(tipo: Tipo, id: string, rif: Riferimenti): string | undefined {
  return tipo === "carta" ? rif.carte[id] : tipo === "stesa" ? rif.stese[id] : rif.articoli[id];
}

/* Le scorciatoie in linea diventano collegamenti Markdown (o si tolgono, se il riferimento non esiste). */
function inLinea(testo: string, rif: Riferimenti): string {
  return testo.replace(IN_LINEA, (_m, scritto: string, id: string) => {
    const tipo = CANONICO[scritto];
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
  tipo, id, idCarta, nome, etichette,
}: {
  tipo: Tipo;
  id: string;
  idCarta?: string;
  nome: string;
  etichette: EtichetteTipo;
}) {
  return (
    <Link href={`${PERCORSO[tipo]}/${id}`} className={stili.schedaIncorporata}>
      {tipo === "carta" && (
        // eslint-disable-next-line @next/next/no-img-element -- la carta vera, piccola (`id` può essere uno slug: `idCarta`)
        <img src={`/cards/${idCarta ?? id}.${ESTENSIONE}`} alt="" width={72} height={128} loading="lazy" />
      )}
      <span>
        <small>{etichette[tipo]}</small>
        <strong>{nome}</strong>
      </span>
    </Link>
  );
}

function VideoIncorporato({ id }: { id: string }) {
  return (
    <div className={stili.videoIncorporato}>
      <iframe
        src={`https://www.youtube-nocookie.com/embed/${id}`}
        title="Video"
        loading="lazy"
        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerPolicy="strict-origin-when-cross-origin"
        sandbox="allow-scripts allow-same-origin allow-presentation"
        allowFullScreen
      />
    </div>
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
  const pezzi: ({ md: string } | { tipo: Tipo; id: string; idCarta?: string; nome: string } | { video: string })[] = [];
  let corrente: string[] = [];
  const chiudi = () => {
    if (corrente.length) pezzi.push({ md: corrente.join("\n") });
    corrente = [];
  };
  for (const riga of righe) {
    const mVideo = BLOCCO_VIDEO.exec(riga);
    if (mVideo) {
      chiudi();
      pezzi.push({ video: mVideo[1] });
      continue;
    }
    const m = BLOCCO.exec(riga);
    const tipo = m ? CANONICO[m[1]] : undefined;
    const nome = m && tipo ? nomeDi(tipo, m[2], riferimenti) : undefined;
    if (m && tipo && nome) {
      chiudi();
      pezzi.push({ tipo, id: m[2], idCarta: riferimenti.idCarte?.[m[2]], nome });
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
        ) : "video" in p ? (
          <VideoIncorporato key={i} id={p.video} />
        ) : (
          <Fragment key={i}><Scheda tipo={p.tipo} id={p.id} idCarta={p.idCarta} nome={p.nome} etichette={etichette} /></Fragment>
        ),
      )}
    </div>
  );
}
