"use client";

import { Fila, type Voce } from "../schede-comuni";

/* I sotto-tab di Notifications: i messaggi scritti a mano, quelli automatici, i numeri, la configurazione. */
const SCHEDE: Voce[] = [
  { href: "/notifiche", etichetta: "Campagne" },
  { href: "/notifiche/automatiche", etichetta: "Automatiche" },
  { href: "/notifiche/consegne", etichetta: "Consegne e aperture" },
  { href: "/notifiche/impostazioni", etichetta: "Impostazioni" },
];

export function Schede() {
  return <Fila voci={SCHEDE} etichetta="Sezioni delle notifiche" />;
}
