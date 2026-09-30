/* Il sito (la v2, dalla v8.5): il layout radice di tutte le pagine tranne `/old` (la v1, col suo layout). Da qui non
 * si eredita niente della v1: si passa dall'una all'altra ricaricando la pagina. */

import type { Metadata, Viewport } from "next";
import { SITE_URL } from "@/lib/condivisione";
import { linguaPagina } from "@/lib/lingua-server";
import { NOME_MARCHIO } from "@/lib/marchio";
import { ProvidersV2 } from "@/v2/componenti/providers";
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
  const lingua = await linguaPagina();
  return (
    <html lang={lingua} className={classiFontV2}>
      <body>
        <ProvidersV2 linguaIniziale={lingua}>{children}</ProvidersV2>
      </body>
    </html>
  );
}
