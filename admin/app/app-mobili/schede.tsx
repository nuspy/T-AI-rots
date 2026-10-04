"use client";

import { Fila, type Voce } from "../schede-comuni";

/* I sotto-tab di App mobili: una piattaforma per scheda, poi ciò che vale per entrambe (prodotti, pulsante Stripe) e
 * la build (Codemagic). */
const SCHEDE: Voce[] = [
  { href: "/app-mobili", etichetta: "Android" },
  { href: "/app-mobili/ios", etichetta: "iOS" },
  { href: "/app-mobili/prodotti", etichetta: "Prodotti" },
  { href: "/app-mobili/stripe", etichetta: "Pulsante Stripe" },
  { href: "/app-mobili/codemagic", etichetta: "Codemagic" },
];

export function Schede() {
  return <Fila voci={SCHEDE} etichetta="Sezioni delle app mobili" />;
}
