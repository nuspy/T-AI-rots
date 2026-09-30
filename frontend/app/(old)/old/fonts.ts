/* Le tre voci tipografiche del sito (v1), in un modulo solo: le usano il layout radice e il 404 globale
 * (`app/global-not-found.tsx`), che non passa dal layout e deve dichiararle da sé.
 *
 * Cinzel per i titoli, lapidaria come un'iscrizione; Cormorant per la voce dell'oracolo; IBM Plex Sans per
 * l'interfaccia, che deve restare leggibile anche quando tutto il resto è atmosfera.
 * `latin-ext` per ő, ű, ł, ș, ă…: senza, l'ungherese, il polacco e il rumeno ripiegherebbero sul carattere di
 * sistema a metà parola. Il cirillico (russo, ucraino) c'è in Cormorant e in IBM Plex, non in Cinzel: nei titoli
 * ripiega sul serif di sistema. Cinese, hindi, coreano e arabo usano il carattere di sistema (vedi `globals.css`). */

import { Cinzel, Cormorant_Garamond, IBM_Plex_Sans } from "next/font/google";

const titoli = Cinzel({ subsets: ["latin", "latin-ext"], variable: "--font-titoli", weight: ["400", "600", "700"] });
const oracolo = Cormorant_Garamond({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-oracolo",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});
const interfaccia = IBM_Plex_Sans({ subsets: ["latin", "latin-ext", "cyrillic"], variable: "--font-ui", weight: ["400", "500", "600"] });

export const classiFont = `${titoli.variable} ${oracolo.variable} ${interfaccia.variable}`;
