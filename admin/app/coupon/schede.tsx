"use client";

import { Fila, type Voce } from "../schede-comuni";

/* I sotto-tab dei coupon (v9, Fase 2d): i coupon singoli, i lotti di codici monouso, il resoconto per campagna. */
const SCHEDE: Voce[] = [
  { href: "/coupon", etichetta: "Coupon" },
  { href: "/coupon/lotti", etichetta: "Lotti" },
  { href: "/coupon/campagne", etichetta: "Campagne e resoconto" },
];

export function Schede() {
  return <Fila voci={SCHEDE} etichetta="Sezioni dei coupon" />;
}
