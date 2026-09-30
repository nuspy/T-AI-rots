/* Le misure del tavolo di una lettura che servono anche fuori dal tavolo: all'immagine di condivisione (sito e v2)
 * e al tavolo della v2. Costanti pure, senza React. */

import type { Soggetto, Stesa } from "./api";

/** L'estensione dei file delle carte (`webp` in produzione). */
export const ESTENSIONE = process.env.NEXT_PUBLIC_CARD_EXT ?? "webp";

/* La larghezza di una carta come frazione della larghezza del tavolo sta nei
 * dati della stesa (`larghezza`): dieci carte della Croce Celtica devono stare
 * dove ne stanno tre, e ogni stesa dichiara la sua. Senza, vale 0.1. */
export const larghezzaBase = (stesa: Stesa): number => stesa.larghezza ?? 0.1;

/* Il colore di chi parla una posizione, nelle letture di compatibilità e di
 * coppia. Non è mai l'unico segnale: i nomi delle posizioni dicono già il
 * soggetto, e la legenda sotto il tavolo lo scrive. */
export const COLORE_SOGGETTO: Record<Soggetto, string> = {
  tu: "#d8b45a",
  partner: "#b9a4ff",
  coppia: "#7fd6c2",
  "strada-a": "#f0a37a",
  "strada-b": "#8ec5ff",
};

/* Le carte sono il 20% più grandi di com'erano rispetto al tavolo, con i centri
 * dove stavano: la distanza fra le carte non cambia (è definita dalle
 * coordinate della stesa), si riduce solo lo spazio vuoto fra i bordi. Il
 * tavolo è alto un quinto di più (vedi `.tavolo`), così le carte più grandi non
 * si toccano. */
export const SCALA_CARTE = 1.2;
