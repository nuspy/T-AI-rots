/* Il sito (la v2, dalla v8.5): il layout radice di tutte le pagine tranne `/old` (la v1, col suo layout). Da qui non
 * si eredita niente della v1: si passa dall'una all'altra ricaricando la pagina. */

import type { Metadata, Viewport } from "next";
import { cookies } from "next/headers";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { leggiDalServer } from "@/lib/server-api";
import { ProvidersV2 } from "@/v2/componenti/providers";
import { COOKIE_PUBBLICITA, PERCORSO_PUBBLICITA, SPENTA, type ImpostazioniPubblicita } from "@/v2/lib/pubblicita";
import { PERCORSO_PUBBLICO_ABBONAMENTI, type ImpostazioniPubblicheAbbonamenti } from "@/lib/abbonamenti";
import { ProvaIniziale, SCRIPT_BANNER_PROVA } from "@/v2/lib/prova";
import { SCRIPT_TESTO } from "@/v2/lib/testo-script";
import { classiFontV2 } from "./fonts";
import "./v2.css";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: `${NOME_MARCHIO} — a living Tarot ritual`, template: `%s · ${NOME_MARCHIO}` },
  description: "A living Tarot ritual with guided interpretation and a reader who remembers your story.",
  applicationName: NOME_MARCHIO,
};

export const viewport: Viewport = {
  themeColor: "#201026",
  colorScheme: "light",
  viewportFit: "cover",
};

export default async function LayoutV2({ children }: { children: React.ReactNode }) {
  /* Gli spazi pubblicitari (spenti per default) e il promemoria del consenso agli annunci: letti qui perché l'HTML
   * esca già con lo spazio riservato a chi li vedrà (`v2/componenti/pubblicita.tsx`). */
  const [lingua, pubblicita, biscotti, prova] = await Promise.all([
    linguaPagina(),
    leggiDalServer<ImpostazioniPubblicita>(PERCORSO_PUBBLICITA, { secondi: 60 }),
    cookies(),
    /* La prova gratuita (v9, Fase 2b): il banner esce già nell'HTML, senza spostare la pagina comparendo dopo. */
    leggiDalServer<ImpostazioniPubblicheAbbonamenti>(PERCORSO_PUBBLICO_ABBONAMENTI, { secondi: 60 }),
  ]);
  const statoPubblicita = {
    impostazioni: pubblicita ?? SPENTA,
    ricordo: biscotti.get(COOKIE_PUBBLICITA)?.value === "1",
  };
  return (
    /* `suppressHydrationWarning`: lo script del banner della prova può mettere `data-prova-nascosta` su <html>
     * prima che React arrivi (chi l'ha chiuso non lo vede nemmeno per un istante). */
    <html lang={lingua} className={classiFontV2} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: SCRIPT_BANNER_PROVA }} />
        {/* La dimensione del testo scelta con A− / A+ (`v2/lib/testo.tsx`), prima del disegno. */}
        <script dangerouslySetInnerHTML={{ __html: SCRIPT_TESTO }} />
      </head>
      <body suppressHydrationWarning>
        <ProvidersV2 linguaIniziale={lingua} pubblicita={statoPubblicita}>
          <ProvaIniziale valore={prova}>{children}</ProvaIniziale>
        </ProvidersV2>
      </body>
    </html>
  );
}
