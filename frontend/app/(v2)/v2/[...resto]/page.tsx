/* Ogni indirizzo sconosciuto sotto `/v2` finisce qui, e da qui nella pagina «non trovata» della v2 (non in quella
 * del sito, `app/global-not-found.tsx`). */

import { notFound } from "next/navigation";

export default function Sconosciuta() {
  notFound();
}
