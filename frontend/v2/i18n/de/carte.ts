/* COPIA DELL'INGLESE — da tradurre. Rigenerata da copia-inglese.mjs finché questa riga resta qui. */
/* The card library and a single card. */

export const carte = {
  meta_titolo: "Thoth Tarot card library",
  meta_descrizione: "The 78 cards of the Thoth Tarot: images, correspondences and meanings, each a way into a question.",
  eyebrow: "Thoth Tarot card library",
  titolo: "See the card before you ask it to speak.",
  intro: "Each card joins an image, a set of correspondences and meanings on several levels. Its role in a reading still depends on the position, the cards around it and your question.",
  filtri: { tutte: "All", maggiori: "Major Arcana", bastoni: "Wands", coppe: "Cups", spade: "Swords", dischi: "Disks" } as Record<string, string>,
  filtri_aria: "Filter the cards",
  n_carte: { uno: "1 card", molti: "{n} cards" },

  /* one card */
  carta_eyebrow: "Thoth Tarot · {arcano}",
  carta_riflessione: "A reflective starting point",
  carta_domanda: "What is {carta} asking you to look at?",
  carta_nota: "Meaning changes with the position, the surrounding cards and your question. Take what follows as a language, not a verdict.",
  dritta: "Upright",
  rovesciata: "Reversed",
  rovesciata_nota: "In the Thoth tradition a reversed card is read through its dignity with the neighbouring cards; this is its shadow side.",
  livelli: { essoterico: "At first sight", psicologico: "Within you", iniziatico: "On the path", ombra: "The shadow" } as Record<string, string>,
  ambiti_titolo: "In love, work and spirit",
  ambiti: { amore: "Love", lavoro: "Work", spirito: "Spirit" } as Record<string, string>,
  corrispondenze: "Correspondences",
  sentiero: "path {n}",
  crowley: "Crowley's note",
  parole: "Key words",
  cta_leggi: "Read this card in a ritual",
  cta_fisica: "Draw it from your own deck",
  articoli_su: "From the journal",
  precedente: "Previous card",
  successiva: "Next card",
  torna: "Back to the library",
  non_trovata: "This card is not in the library.",
};
