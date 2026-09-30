"use client";

/* Il mazzo attivo (v7, Fase H): quale sottocartella di `public/cards/` usare per l'artwork.
 *
 * `null` (il default, fuori da qualunque provider) = percorso piatto `/cards/<id>.webp`, esattamente
 * il comportamento di sempre — retrocompatibile al 100% col mazzo Toth esistente, che non ha e non
 * avrà mai una sottocartella. Un mazzo diverso porta uno slug, e `carta.tsx` costruisce il percorso
 * come `/cards/<slug>/<id>.webp`. Il provider si monta dove serve scegliere un mazzo (la lettura,
 * Fase J) — altrove il contesto resta `null` e nulla cambia. */

import { createContext, useContext } from "react";

const ContestoMazzoAttivo = createContext<string | null>(null);

export function ProviderMazzoAttivo({ slug, children }: { slug: string | null; children: React.ReactNode }) {
  return <ContestoMazzoAttivo.Provider value={slug}>{children}</ContestoMazzoAttivo.Provider>;
}

export function useMazzoAttivo(): string | null {
  return useContext(ContestoMazzoAttivo);
}

/** Il percorso di un file dell'artwork, piatto o nella sottocartella del mazzo attivo. */
export function percorsoCarta(slug: string | null, nomeFile: string): string {
  return slug ? `/cards/${slug}/${nomeFile}` : `/cards/${nomeFile}`;
}
