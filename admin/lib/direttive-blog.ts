/* Il testo ricco del blog (v8.5): colore e dimensione di una parola o di una frase, e il sottolineato, con una
 * sintassi sicura che non lascia passare né HTML né colori liberi. Solo le classi della tavolozza della v2.
 *
 *   :testo[una frase]{colore=ottone}          :text[a phrase]{color=brass}
 *   :testo[più grande]{dimensione=grande}     :text[bigger]{size=large}
 *   :testo[entrambe]{colore=prugna dimensione=titolo}
 *   :sottolineato[da ricordare]               :underline[to remember]
 *
 * Colori: ottone (brass), prugna (plum), verderame (verdigris), tenue (muted). Dimensioni: piccolo (small), grande
 * (large), titolo (title). Un valore sconosciuto si ignora; una direttiva sconosciuta torna testo com'era scritto,
 * così un «:» nel testo non fa sparire niente.
 *
 * STESSO FILE in `frontend/v2/lib/direttive-blog.ts` (il sito): cambiarli insieme. Il server toglie la
 * sintassi dagli estratti e dai controlli SEO (`tarot/blog.py`, `testo_semplice`). */

import type { Plugin } from "unified";
import { visit } from "unist-util-visit";

const COLORI: Record<string, string> = {
  ottone: "ottone", brass: "ottone", prugna: "prugna", plum: "prugna",
  verderame: "verderame", verdigris: "verderame", tenue: "tenue", muted: "tenue",
};
const DIMENSIONI: Record<string, string> = {
  piccolo: "piccolo", small: "piccolo", grande: "grande", large: "grande", titolo: "titolo", title: "titolo",
};

interface Nodo {
  type: string;
  name?: string;
  attributes?: Record<string, string | null | undefined> | null;
  children?: Nodo[];
  value?: string;
  data?: { hName?: string; hProperties?: Record<string, unknown> };
}

const DIRETTIVE = new Set(["textDirective", "leafDirective", "containerDirective"]);

export const direttiveBlog: Plugin = () => (albero) => {
  visit(albero as never, (nodo: Nodo, indice: number | undefined, genitore: Nodo | undefined) => {
    if (!DIRETTIVE.has(nodo.type)) return;
    const nome = nodo.name ?? "";
    const a = nodo.attributes ?? {};
    if (nodo.type === "textDirective" && (nome === "testo" || nome === "text")) {
      const colore = COLORI[String(a.colore ?? a.color ?? "")];
      const dimensione = DIMENSIONI[String(a.dimensione ?? a.size ?? "")];
      const classi = [colore && `md-colore-${colore}`, dimensione && `md-dim-${dimensione}`].filter(Boolean);
      nodo.data = { hName: "span", hProperties: classi.length ? { className: classi } : {} };
      return;
    }
    if (nodo.type === "textDirective" && (nome === "sottolineato" || nome === "underline")) {
      nodo.data = { hName: "u", hProperties: {} };
      return;
    }
    /* Sconosciuta: torna testo com'era scritta (`:nome[contenuto]`); su una riga da sola resta un paragrafo. */
    if (!genitore?.children || indice === undefined) return;
    const prefisso = nodo.type === "textDirective" ? ":" : nodo.type === "leafDirective" ? "::" : ":::";
    const figli = nodo.children ?? [];
    const testo: Nodo[] = figli.length
      ? [{ type: "text", value: `${prefisso}${nome}[` }, ...figli, { type: "text", value: "]" }]
      : [{ type: "text", value: `${prefisso}${nome}` }];
    genitore.children.splice(indice, 1, ...(nodo.type === "textDirective" ? testo : [{ type: "paragraph", children: testo }]));
    return indice + 1;
  });
};
