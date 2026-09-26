/* La lingua di una richiesta, letta sul server.
 *
 * Non la decide il browser né una preferenza salvata: la decide l'indirizzo (`/it/…` è italiano, il resto è
 * inglese), e il proxy la scrive in un'intestazione (`proxy.ts`). Le pagine pubbliche la leggono da qui per
 * scegliere i testi, i metadati e le lingue dei dati (`?lang=` dell'API). */

import { headers } from "next/headers";
import type { LinguaPubblica } from "./percorsi";

export async function linguaPagina(): Promise<LinguaPubblica> {
  return (await headers()).get("x-lang") === "it" ? "it" : "en";
}

export async function paginaPubblica(): Promise<boolean> {
  return (await headers()).get("x-pubblica") === "1";
}
