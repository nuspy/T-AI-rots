/* La biblioteca delle carte e la pagina di una carta. */

import type { carte as Base } from "../en/carte";

export const carte: typeof Base = {
  meta_titolo: "Biblioteca de cartas del Tarot Thoth",
  meta_descrizione: "Las 78 cartas del Tarot Thoth: imágenes, correspondencias y significados, cada una una puerta hacia una pregunta.",
  eyebrow: "Biblioteca de cartas del Tarot Thoth",
  titolo: "Mira la carta antes de pedirle que hable.",
  intro: "Cada carta une una imagen, un conjunto de correspondencias y significados en varios niveles. Su papel en una lectura depende siempre de la posición, de las cartas que la rodean y de tu pregunta.",
  filtri: { tutte: "Todas", maggiori: "Arcanos Mayores", bastoni: "Bastos", coppe: "Copas", spade: "Espadas", dischi: "Discos" } as Record<string, string>,
  filtri_aria: "Filtrar las cartas",
  n_carte: { uno: "1 carta", molti: "{n} cartas" },

  carta_eyebrow: "Tarot Thoth · {arcano}",
  carta_riflessione: "Un punto de partida para reflexionar",
  carta_domanda: "¿Qué te está pidiendo mirar {carta}?",
  carta_nota: "El significado cambia según la posición, las cartas que la rodean y tu pregunta. Toma lo que sigue como un lenguaje, no como un veredicto.",
  dritta: "Al derecho",
  rovesciata: "Invertida",
  rovesciata_nota: "En la tradición Thoth, una carta invertida se lee a través de su dignidad con las cartas vecinas; este es su lado de sombra.",
  livelli: { essoterico: "A primera vista", psicologico: "Dentro de ti", iniziatico: "En el camino", ombra: "La sombra" } as Record<string, string>,
  ambiti_titolo: "En el amor, el trabajo y el espíritu",
  ambiti: { amore: "Amor", lavoro: "Trabajo", spirito: "Espíritu" } as Record<string, string>,
  corrispondenze: "Correspondencias",
  sentiero: "sendero {n}",
  crowley: "La nota de Crowley",
  parole: "Palabras clave",
  cta_leggi: "Lee esta carta en un ritual",
  cta_fisica: "Sácala de tu propio mazo",
  articoli_su: "Del diario",
  precedente: "Carta anterior",
  successiva: "Carta siguiente",
  torna: "Volver a la biblioteca",
  non_trovata: "Esta carta no está en la biblioteca.",
};
