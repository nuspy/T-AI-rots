/* Ciò che le pagine del blog si dividono: come si scrive uno stato, come si ordina l'albero delle sezioni.
 * Sta fuori da `page.tsx` perché un file di pagina può esportare solo la pagina. */

import type { Articolo, Sezione } from "@/lib/blog";
import comuni from "../comuni.module.css";

export function etichettaStato(a: Pick<Articolo, "stato" | "programmato">): { testo: string; classe: string } {
  if (a.stato === "pubblicato" && a.programmato) return { testo: "programmato", classe: comuni.neutro };
  if (a.stato === "pubblicato") return { testo: "pubblicato", classe: comuni.positivo };
  if (a.stato === "archiviato") return { testo: "archiviato", classe: comuni.spento };
  return { testo: "bozza", classe: comuni.neutro };
}

/** Le sezioni in ordine d'albero, con il nome del percorso («Articoli › Amore»). */
export function sezioniInOrdine(tutte: Sezione[]): { sezione: Sezione; livello: number; percorso: string }[] {
  const perPadre = new Map<number | null, Sezione[]>();
  for (const s of tutte) {
    const lista = perPadre.get(s.parent_id) ?? [];
    lista.push(s);
    perPadre.set(s.parent_id, lista);
  }
  const uscita: { sezione: Sezione; livello: number; percorso: string }[] = [];
  const visita = (padre: number | null, livello: number, prefisso: string) => {
    for (const s of (perPadre.get(padre) ?? []).sort((a, b) => a.ordine - b.ordine || a.nome.localeCompare(b.nome))) {
      const percorso = prefisso ? `${prefisso} › ${s.nome}` : s.nome;
      uscita.push({ sezione: s, livello, percorso });
      visita(s.id, livello + 1, percorso);
    }
  };
  visita(null, 0, "");
  return uscita;
}
