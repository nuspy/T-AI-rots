/* La carta del giorno. */

import type { giorno as Base } from "../en/giorno";

export const giorno: typeof Base = {
  meta_titolo: "Carta del giorno",
  meta_descrizione: "Una carta dei Tarocchi di Thoth per oggi, gratis e senza account: un piccolo incontro e uno spunto per riflettere.",
  eyebrow: "Carta del giorno",
  titolo: "Un piccolo incontro, senza bisogno di un account.",
  intro: "Una carta per oggi, la stessa per tutti fino a mezzanotte (UTC). Prendi l'immagine come uno spunto per riflettere, non come una promessa.",
  intro_dentro: "La tua carta di oggi, gratuita. Girala quando sei pronta o pronto: tiene il conto dei tuoi giorni di fila.",
  di_tutti: "La carta di oggi",
  tua: "La tua carta di oggi",
  gira: "Gira la carta",
  serie: { uno: "1 giorno di fila", molti: "{n} giorni di fila" },
  domanda: "Se qualcosa di preciso chiede la tua attenzione, portalo in una lettura.",
  cta: "Fai una domanda più ampia",
  significato: "Il significato completo di {carta}",
  personale: "Con un account gratuito la carta viene pescata per te ogni giorno, e la serie dei giorni tiene viva la pratica.",
  entra: "Accedi",
};
