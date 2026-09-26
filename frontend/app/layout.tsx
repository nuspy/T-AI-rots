import type { Metadata, Viewport } from "next";
import { Cinzel, Cormorant_Garamond, IBM_Plex_Sans } from "next/font/google";
import { Providers } from "./providers";
import { Cosmo } from "./componenti/cosmo";
import "./globals.css";

/* Tre voci tipografiche: Cinzel per i titoli, lapidaria come un'iscrizione;
 * Cormorant per la voce dell'oracolo; IBM Plex Sans per l'interfaccia, che
 * deve restare leggibile anche quando tutto il resto è atmosfera. */
/* `latin-ext` per ő, ű, ł, ș, ă…: senza, l'ungherese, il polacco e il rumeno
 * ripiegherebbero sul carattere di sistema a metà parola. Il cirillico (russo,
 * ucraino) c'è in Cormorant e in IBM Plex, non in Cinzel: nei titoli ripiega
 * sul serif di sistema. Cinese, hindi, coreano e arabo usano il carattere di
 * sistema (vedi `globals.css`). */
const titoli = Cinzel({ subsets: ["latin", "latin-ext"], variable: "--font-titoli", weight: ["400", "600", "700"] });
const oracolo = Cormorant_Garamond({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-oracolo",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});
const interfaccia = IBM_Plex_Sans({ subsets: ["latin", "latin-ext", "cyrillic"], variable: "--font-ui", weight: ["400", "500", "600"] });

export const metadata: Metadata = {
  title: { default: "TAROTS chat — Tarocchi di Thoth con l'AI", template: "%s · TAROTS chat" },
  description:
    "Letture dei tarocchi di Thoth guidate da un'intelligenza artificiale: intervista, stese tradizionali, carte rivelate una a una e un responso coerente con la dottrina esoterica.",
  openGraph: { type: "website", siteName: "TAROTS chat" },
};

export const viewport: Viewport = {
  themeColor: "#07050f",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it" className={`${titoli.variable} ${oracolo.variable} ${interfaccia.variable}`}>
      <body>
        <Cosmo />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
