/* Una lettura condivisa: la porta d'ingresso di chi riceve il link. */

import type { condivisa as Base } from "../en/condivisa";

export const condivisa: typeof Base = {
  eyebrow: "Egy jóslás, amelyet valaki megosztott veled",
  titolo_predefinito: "Egy kérdés, a kártyák, és amit megnyitottak.",
  nota: "Egy személyes tarot-jóslásból megosztva. Annak neve, aki megosztotta, soha nem jelenik meg.",
  domanda: "A kérdés",
  l_interpretazione: "Az értelmezés",
  invito_titolo: "A saját kérdésed is vár.",
  invito_testo: "Vegyél részt te magad a rituáléban: az első jóslásod ingyenes, és nem kell hozzá fiók. Ha létrehozol egyet, aki ezt a linket küldte neked, {n} ingyenes jóslást kap.",
  inizia: "Kezdd el az ingyenes jóslást",
  iscriviti: "Ingyenes fiók létrehozása",
  giorno: "Vagy húzd ki a mai kártyát",
  non_trovata_titolo: "Ezt a jóslást már nem osztják meg.",
  non_trovata_testo: "Aki megosztotta, talán kikapcsolta a linket. A saját jóslásodat így is elkezdheted.",
};
