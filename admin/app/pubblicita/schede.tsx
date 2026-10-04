"use client";

import { Fila, type Voce } from "../schede-comuni";

/* I sotto-tab di Advertisements. «Spazi» vale per qualunque fornitore (l'interruttore, i tre banner, le pagine
 * escluse); poi un sotto-tab per fornitore. Un fornitore nuovo (affiliazioni, spazi venduti direttamente) è una voce
 * qui e una pagina sotto `app/pubblicita/<fornitore>`, con le sue chiavi nel backend (`FORNITORI`). */
const SCHEDE: Voce[] = [
  { href: "/pubblicita", etichetta: "Spazi" },
  { href: "/pubblicita/google", etichetta: "Google Ads" },
];

/* Dentro Google Ads: le impostazioni (parametri e iscrizione) e gli appunti sul profilo pagamenti. */
const SCHEDE_GOOGLE: Voce[] = [
  { href: "/pubblicita/google", etichetta: "Impostazioni" },
  { href: "/pubblicita/google/pagamenti", etichetta: "Pagamenti" },
];

export function Schede() {
  return <Fila voci={SCHEDE} etichetta="Sezioni della pubblicità" />;
}

export function SchedeGoogle() {
  return <Fila voci={SCHEDE_GOOGLE} etichetta="Sezioni di Google Ads" piccola />;
}
