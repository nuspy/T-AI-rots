/* Le due voci della v2: Libre Baskerville per i titoli e la voce del lettore, DM Sans per l'interfaccia.
 * `latin-ext` per ő, ű dell'ungherese (e per le lingue che si tradurranno). Il cirillico e le scritture non
 * latine ricadono sui caratteri di sistema, come nel sito. */

import { DM_Sans, Libre_Baskerville } from "next/font/google";

const serif = Libre_Baskerville({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "700"],
  style: ["normal", "italic"],
  variable: "--font-v2-serif",
});
const sans = DM_Sans({ subsets: ["latin", "latin-ext"], weight: ["400", "500", "600", "700"], variable: "--font-v2-sans" });

export const classiFontV2 = `${serif.variable} ${sans.variable}`;
