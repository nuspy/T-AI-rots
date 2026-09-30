/* Metodo e privacy. I contenuti legali sono quelli del sito (stesso titolare, stesse scelte, stessa politica sulle
 * statistiche); la v2 aggiunge, con parole semplici, che cosa ricorda il lettore e come si usa l'AI. */

import type { privacy as Base } from "../en/privacy";

export const privacy: typeof Base = {
  meta_titolo: "Metodo e privacy",
  meta_descrizione: "Che cosa si conserva, perché, e come decidi tu: letture, memoria, statistiche e cookie.",
  eyebrow: "Metodo e privacy",
  titolo: "Mistico non vuol dire opaco.",
  intro: "Che cosa si conserva, perché, e come decidi tu. Le stesse regole valgono per ogni pagina di TAROTS chat.",

  letture_titolo: "Le tue letture e la tua memoria",
  letture_testo: "Le letture si conservano nel tuo account perché tu possa tornarci. Ciò che il tuo lettore ricorda nasce dalle tue letture e conversazioni, e puoi rivederlo, modificarlo o cancellarlo in qualsiasi momento da La mia storia. Eliminare una lettura la cancella per sempre.",
  letture_cta: "Gestisci ciò che viene ricordato",
  ai_titolo: "Come si usa l'AI",
  ai_testo: "Un'intelligenza artificiale interpreta le carte nel contesto della tua domanda e delle tue parole. Nelle letture su due persone, il cognome dell'altra persona non arriva mai all'AI. L'AI non conosce il futuro, e nessuna lettura è una previsione.",

  custode_titolo: "Custode del trattamento dati",
  custode_testo: "Il custode del trattamento dei dati personali raccolti da TAROTS chat è Andrea Taini.",
  partner_titolo: "Condivisione dati con i partner",
  partner_testo: "Puoi scegliere se autorizzare la condivisione dei tuoi dati con i nostri partner. Questa scelta è separata da quella sui cookie e puoi cambiarla in qualsiasi momento da questa pagina.",
  partner_si: "Autorizzo",
  partner_no: "Non autorizzo",
  partner_stato_si: "Hai autorizzato la condivisione dei dati con i partner.",
  partner_stato_no: "Non hai autorizzato la condivisione dei dati con i partner.",
  stat_titolo: "Statistiche di utilizzo",
  stat_anonime: "Misuriamo in forma anonima come viene usato il sito: pagine visitate, da dove arriva la visita (motore di ricerca, social, campagna), tipo di dispositivo e browser, paese e città approssimativi. Senza cookie e senza salvare nulla nel tuo browser. L'indirizzo IP serve solo nel momento della visita, per stimare paese e città e per calcolare un'impronta che cambia ogni giorno: non viene mai conservato.",
  stat_account: "Se hai un account e hai fatto l'accesso, le visite sono collegate al tuo account, sulla base del nostro legittimo interesse a capire come migliorare il servizio (per esempio da quale canale arrivano gli iscritti e cosa porta a un acquisto). Puoi opporti in qualsiasi momento dal tuo account: da allora le visite non vengono più collegate e il legame con quelle passate viene cancellato.",
  stat_esteso: "Se accetti nel banner dei cookie («It's fine»), riconosciamo anche il tuo browser quando torni nei giorni successivi, con un identificativo casuale. Se rifiuti o cambi idea, l'identificativo viene dimenticato anche dai nostri server.",
  stat_conservazione: "Visite ed eventi dettagliati si conservano per 25 mesi; dopo restano solo totali giornalieri anonimi. Le analisi automatiche e le esportazioni usano solo dati aggregati.",
  stat_geo: "Geolocalizzazione IP:",
  cookie_titolo: "La tua scelta sui cookie",
  cookie_si: "Accetto",
  cookie_no: "Non accetto",
  cookie_stato_si: "Hai accettato: il tuo browser viene riconosciuto quando torni.",
  cookie_stato_no: "Non hai accettato: le visite restano anonime e l'identificativo del browser è stato dimenticato.",
};
