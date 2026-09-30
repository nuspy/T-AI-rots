/* La biblioteca delle carte e la pagina di una carta. */

import type { carte as Base } from "../en/carte";

export const carte: typeof Base = {
  meta_titolo: "Le carte dei Tarocchi di Thoth",
  meta_descrizione: "Le 78 carte dei Tarocchi di Thoth: immagini, corrispondenze e significati, ognuna una porta verso una domanda.",
  eyebrow: "Le carte dei Tarocchi di Thoth",
  titolo: "Guarda la carta prima di chiederle di parlare.",
  intro: "Ogni carta unisce un'immagine, un sistema di corrispondenze e significati su più livelli. Il suo ruolo in una lettura dipende comunque dalla posizione, dalle carte vicine e dalla tua domanda.",
  filtri: { tutte: "Tutte", maggiori: "Arcani Maggiori", bastoni: "Bastoni", coppe: "Coppe", spade: "Spade", dischi: "Dischi" } as Record<string, string>,
  filtri_aria: "Filtra le carte",
  n_carte: { uno: "1 carta", molti: "{n} carte" },

  carta_eyebrow: "Tarocchi di Thoth · {arcano}",
  carta_riflessione: "Un punto di partenza per riflettere",
  carta_domanda: "Che cosa ti chiede di guardare {carta}?",
  carta_nota: "Il significato cambia con la posizione, le carte vicine e la tua domanda. Prendi ciò che segue come un linguaggio, non come un verdetto.",
  dritta: "Dritta",
  rovesciata: "Rovesciata",
  rovesciata_nota: "Nella tradizione di Thoth una carta rovesciata si legge attraverso la sua dignità con le carte vicine: è il suo lato d'ombra.",
  livelli: { essoterico: "A prima vista", psicologico: "Dentro di te", iniziatico: "Sul cammino", ombra: "L'ombra" } as Record<string, string>,
  ambiti_titolo: "In amore, nel lavoro, nello spirito",
  ambiti: { amore: "Amore", lavoro: "Lavoro", spirito: "Spirito" } as Record<string, string>,
  corrispondenze: "Corrispondenze",
  sentiero: "sentiero {n}",
  crowley: "La nota di Crowley",
  parole: "Parole chiave",
  cta_leggi: "Leggi questa carta in un rito",
  cta_fisica: "Pescala dal tuo mazzo",
  articoli_su: "Dal diario",
  precedente: "Carta precedente",
  successiva: "Carta successiva",
  torna: "Torna alle carte",
  non_trovata: "Questa carta non è nella biblioteca.",
};
