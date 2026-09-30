/* Le proprie carte: si pesca con il proprio mazzo, si posano le carte, il lettore interpreta. */

import type { fisica as Base } from "../en/fisica";

export const fisica: typeof Base = {
  meta_titolo: "Lee tus cartas físicas",
  meta_descrizione: "Saca las cartas con tu propio mazo de Tarot, colócalas en una tirada y recibe una interpretación guiada.",
  eyebrow: "Modo Tarot físico",
  titolo: "Tus manos sacan las cartas. El lector te ayuda a escuchar el conjunto.",
  intro: "Elige la tirada que has usado, indica las cartas que realmente te han salido y luego añade tu pregunta. No se vuelve a sacar nada: la lectura parte de tu mesa.",

  passo_1: "1 · Coloca las cartas",
  stesa_titolo: "¿Qué tirada has dispuesto?",
  cambia_stesa: "Elegir otra tirada",
  posiziona: "Toca cada posición e indica la carta que has encontrado en ella.",
  aggiungi: "Indicar",
  modifica: "Cambiar",
  mancano: "Faltan {n} posiciones por indicar",
  manca_una: "Falta una posición por indicar",
  pronte: "Cada carta está en su lugar.",

  passo_2: "2 · Dale una pregunta",
  domanda_titolo: "¿Qué quieres que las cartas te ayuden a examinar?",
  domanda_segnaposto: "Escribe tu pregunta con tus propias palabras…",
  domanda_testo: "Tu tirada física sigue siendo tuya. La interpretación empieza cuando nombras lo que quieres entender.",
  interpreta: "Interpretar mis cartas",
  serve_account: "Para interpretar tus propias cartas necesitas una cuenta gratuita: tu mesa y tu pregunta se conservan mientras inicias sesión.",
  entra: "Inicia sesión para continuar",

  seme_titolo: "{posizione}: ¿qué palo?",
  carta_titolo: "{posizione}: ¿qué carta?",
  semi: { maggiori: "Arcanos Mayores", bastoni: "Bastos", coppe: "Copas", spade: "Espadas", dischi: "Discos" },
  conferma: "Colocar esta carta",
  gia_posata: "ya está sobre la mesa",
};
