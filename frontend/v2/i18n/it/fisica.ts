/* Le proprie carte: si pesca con il proprio mazzo, si posano le carte, il lettore interpreta. */

import type { fisica as Base } from "../en/fisica";

export const fisica: typeof Base = {
  meta_titolo: "Leggi le tue carte fisiche",
  meta_descrizione: "Pesca le carte dal tuo mazzo di Tarocchi, disponile in una stesa e ricevi un'interpretazione guidata.",
  eyebrow: "Tarocchi fisici",
  titolo: "Le tue mani pescano le carte. Il lettore ti aiuta ad ascoltarne il disegno.",
  intro: "Scegli la stesa che hai usato, indica le carte che hai davvero pescato, poi aggiungi la tua domanda. Nulla viene estratto di nuovo: la lettura parte dal tuo tavolo.",

  passo_1: "1 · Posa le carte",
  stesa_titolo: "Quale stesa hai disposto?",
  cambia_stesa: "Scegli un'altra stesa",
  posiziona: "Tocca ogni posizione e indica la carta che hai trovato lì.",
  aggiungi: "Indica",
  modifica: "Cambia",
  mancano: "Mancano ancora {n} posizioni",
  manca_una: "Manca ancora una posizione",
  pronte: "Ogni carta è al suo posto.",

  passo_2: "2 · Dalle una domanda",
  domanda_titolo: "Che cosa vuoi che le carte ti aiutino a guardare?",
  domanda_segnaposto: "Scrivi la tua domanda con parole tue…",
  domanda_testo: "L'estrazione fisica resta tua. L'interpretazione comincia quando dai un nome a ciò che vuoi capire.",
  interpreta: "Interpreta le mie carte",
  serve_account: "Per interpretare le tue carte serve un account gratuito: il tuo tavolo e la tua domanda restano qui mentre accedi.",
  entra: "Accedi per continuare",

  seme_titolo: "{posizione}: quale seme?",
  carta_titolo: "{posizione}: quale carta?",
  semi: { maggiori: "Arcani Maggiori", bastoni: "Bastoni", coppe: "Coppe", spade: "Spade", dischi: "Dischi" },
  conferma: "Posa questa carta",
  gia_posata: "già sul tavolo",
};
