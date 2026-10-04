"use client";

import { Fila, type Voce } from "../schede-comuni";

/* I sotto-tab di Abbonamenti: l'elenco, poi le regole. */
const SCHEDE: Voce[] = [
  { href: "/abbonamenti", etichetta: "Elenco" },
  { href: "/abbonamenti/impostazioni", etichetta: "Impostazioni" },
];

export function Schede() {
  return <Fila voci={SCHEDE} etichetta="Sezioni degli abbonamenti" />;
}
