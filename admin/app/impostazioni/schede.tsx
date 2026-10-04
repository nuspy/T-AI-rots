"use client";

import { Fila, type Voce } from "../schede-comuni";

/* I sotto-tab di Impostazioni (v9, Fase 2c): le regole del sito, la posta in uscita, i dati del titolare per
 * l'informativa privacy. Posta e titolare stanno qui e non in sezioni proprie perché sono impostazioni del sito
 * intero (servono a utenti, admin e informativa), da toccare una volta e poi dimenticare. */
const SCHEDE: Voce[] = [
  { href: "/impostazioni", etichetta: "Generali" },
  { href: "/impostazioni/posta", etichetta: "Posta in uscita" },
  { href: "/impostazioni/titolare", etichetta: "Dati del titolare" },
];

export function Schede() {
  return <Fila voci={SCHEDE} etichetta="Sezioni delle impostazioni" />;
}
