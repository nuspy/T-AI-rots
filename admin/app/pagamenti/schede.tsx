"use client";

import { Fila, type Voce } from "../schede-comuni";

/* I sotto-tab di Pagamenti (v9, Fase 2c): i passaggi alla cassa, e chi incassa (Stripe, configurato da qui). */
const SCHEDE: Voce[] = [
  { href: "/pagamenti", etichetta: "Pagamenti" },
  { href: "/pagamenti/stripe", etichetta: "Stripe" },
];

export function Schede() {
  return <Fila voci={SCHEDE} etichetta="Sezioni dei pagamenti" />;
}
