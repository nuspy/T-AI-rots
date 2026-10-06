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
  letture_accesso: "Solo per ragioni di sicurezza (per esempio per gestire una segnalazione di abuso o una richiesta di aiuto), gli amministratori di TAROTS chat possono leggere le tue letture, le conversazioni, ciò che il lettore ricorda e i dati del tuo profilo. Ogni accesso richiede un motivo dichiarato e resta registrato.",
  ai_titolo: "Come si usa l'AI",
  ai_testo: "Un'intelligenza artificiale interpreta le carte nel contesto della tua domanda e delle tue parole. I nomi non arrivano mai al fornitore dell'AI: riceve un segnaposto («Persona_1») e tu leggi il nome vero; il cognome dell'altra persona non parte mai. L'AI non conosce il futuro, e nessuna lettura è una previsione. A ogni richiesta chiediamo al fornitore di non conservare le risposte: i tuoi testi non restano da lui per addestrare i suoi modelli.",

  custode_titolo: "Chi è responsabile dei tuoi dati",
  // I dati del titolare vengono dalla console (Impostazioni → Dati del titolare): i {segnaposto} li riempie la pagina,
  // e un campo vuoto mostra la frase neutra accanto.
  custode_testo: "Il titolare del trattamento dei dati personali raccolti da TAROTS chat (https://tarots.chat) è {titolare}.",
  custode_testo_senza_nome: "Il titolare del trattamento dei dati personali raccolti da TAROTS chat (https://tarots.chat) si contatta all'indirizzo per la privacy qui sotto.",
  custode_indirizzo: "Indirizzo postale: {indirizzo}.",
  custode_indirizzo_vuoto: "Indirizzo postale: disponibile su richiesta al contatto per la privacy.",
  custode_codice: "Codice fiscale o partita IVA: {codice}.",
  custode_email: "Contatto per la privacy: {email}",
  custode_email_vuoto: "Contatto per la privacy: in aggiornamento; intanto puoi esercitare i tuoi diritti dal tuo account.",
  custode_dpo: "Responsabile della protezione dei dati (DPO): {dpo}.",
  custode_dpo_no: "Non è stato nominato un responsabile della protezione dei dati (DPO).",

  scelte_titolo: "Le tue scelte su questo browser",
  scelte_testo: "Tutto ciò che vedi qui sotto resta spento finché non lo accendi, e puoi cambiarlo qui quando vuoi. I cookie tecnici (l'accesso, la lettura gratuita senza account, il ricordo di queste scelte) non chiedono consenso: senza, il sito non funziona.",
  scelte_account: "Le scelte che riguardano il tuo account — le tue parole per le statistiche, i dati particolari, le promozioni — stanno nel tuo account.",
  scelte_account_cta: "Privacy e consensi",

  finalita_titolo: "Che cosa usiamo, perché, e con quale base giuridica",
  finalita_intro: "Ogni uso dei tuoi dati ha la sua finalità e la sua base giuridica secondo il GDPR:",
  finalita: [
    { cosa: "Account e profilo", perche: "Per darti un account, conservare le tue letture e le tue carte personali, e farti entrare (anche con un social).", base: "Base: il contratto che chiedi (art. 6.1.b GDPR)." },
    { cosa: "Letture, intervista, memoria e chat", perche: "Per leggerti le carte con un'AI e ricordare ciò che aiuta nelle letture successive.", base: "Base: contratto; per i dati particolari, il tuo consenso esplicito (art. 9.2.a)." },
    { cosa: "La lettura gratuita senza account", perche: "Per farti provare una lettura prima di iscriverti.", base: "Base: misure precontrattuali che chiedi tu (art. 6.1.b)." },
    { cosa: "Pagamenti, crediti, ordini e spedizioni", perche: "Per vendere crediti, piani e mazzi, e tenere la contabilità che la legge chiede.", base: "Base: contratto e obblighi di legge (art. 6.1.b e 6.1.c)." },
    { cosa: "Sicurezza e registro", perche: "Per proteggere gli account e il servizio, e sapere chi ha fatto cosa. Gli indirizzi IP si conservano solo accorciati, con un'impronta cifrata.", base: "Base: legittimo interesse (art. 6.1.f)." },
    { cosa: "Statistiche anonime", perche: "Per contare le visite senza cookie e senza salvare nulla nel tuo browser.", base: "Base: legittimo interesse." },
    { cosa: "Statistiche collegate al tuo account", perche: "Per capire da quali canali arrivano gli iscritti e che cosa porta a un acquisto.", base: "Base: legittimo interesse; puoi opporti dal tuo account (art. 21)." },
    { cosa: "Statistiche del sito con l'identificativo del browser", perche: "Per riconoscere il tuo browser quando torni.", base: "Base: il tuo consenso (art. 6.1.a)." },
    { cosa: "Google Analytics", perche: "Per misurare come viene usato il sito.", base: "Base: il tuo consenso." },
    { cosa: "Pubblicità", perche: "Per mostrare annunci di Google AdSense in pochi spazi segnalati, solo se sono accesi.", base: "Base: il tuo consenso." },
    { cosa: "Le tue parole per statistiche e spunti del blog", perche: "Per capire, in forma anonima e aggregata, quali temi stanno a cuore alle persone (senza mai citare nessuno). Non ancora attivo.", base: "Base: il tuo consenso, separato e facoltativo." },
    { cosa: "Promozioni", perche: "Offerte e novità con le notifiche, quando arriveranno.", base: "Base: il tuo consenso." },
    { cosa: "Età minima", perche: "Per verificare che tu abbia l'età per usare il servizio da solo.", base: "Base: obbligo di legge (art. 8 GDPR) e contratto." },
  ],

  art9_titolo: "Dati particolari",
  art9_testo: "Alcune cose che puoi raccontarci sono categorie particolari di dati: essere una persona trans, la tua salute. La casella «persona trans» e i ricordi sulla tua salute si usano solo con il tuo consenso esplicito, che dai nel punto in cui spunti la casella e che puoi revocare quando vuoi dal tuo account: allora la casella si svuota e quei ricordi si cancellano. Senza, non arrivano mai all'AI.",
  art9_crisi: "Se scrivi di volerti fare del male, la lettura si ferma e ti mostriamo subito dove trovare aiuto. Contiamo solo che è successo, senza collegarlo a te.",

  stat_titolo: "Statistiche di utilizzo",
  stat_anonime: "Misuriamo in forma anonima come viene usato il sito: pagine visitate, da dove arriva la visita (motore di ricerca, social, campagna), tipo di dispositivo e browser, paese e città approssimativi. Senza cookie e senza salvare nulla nel tuo browser. L'indirizzo IP serve solo nel momento della visita, per stimare paese e città e per calcolare un'impronta che cambia ogni giorno: non viene mai conservato.",
  stat_account: "Se hai un account e hai fatto l'accesso, le visite sono collegate al tuo account, sulla base del nostro legittimo interesse a capire come migliorare il servizio (per esempio da quale canale arrivano gli iscritti e cosa porta a un acquisto). Puoi opporti in qualsiasi momento dal tuo account: da allora le visite non vengono più collegate e il legame con quelle passate viene cancellato.",
  stat_esteso: "Se accendi «Statistiche del sito», riconosciamo anche il tuo browser quando torni nei giorni successivi, con un identificativo casuale conservato nel tuo browser. Se rifiuti o cambi idea, l'identificativo viene dimenticato anche dai nostri server.",
  stat_google: "Se accendi «Google Analytics», usiamo anche Google Analytics 4, un servizio di Google Ireland Ltd., che imposta i suoi cookie (_ga) per contare le visite e capire come viene usato il sito. Si carica solo dopo il tuo consenso (Google Consent Mode), con i segnali Google e la personalizzazione degli annunci disattivati; Google Analytics 4 non conserva gli indirizzi IP. Google può trattare i dati negli Stati Uniti nell'ambito dell'EU-US Data Privacy Framework. Se rifiuti o revochi il consenso, Google Analytics si ferma e i suoi cookie vengono cancellati.",
  stat_conservazione: "Visite ed eventi dettagliati si conservano per 25 mesi; dopo restano solo totali giornalieri anonimi. Le analisi automatiche e le esportazioni usano solo dati aggregati.",
  stat_geo: "Geolocalizzazione IP:",
  pubblicita_titolo: "Pubblicità",
  pubblicita_testo: "Alcune pagine possono mostrare fino a tre spazi segnalati come «Pubblicità», riempiti da Google AdSense, un servizio di Google Ireland Ltd. Gli annunci si caricano solo se accetti qui o nel banner: Google imposta allora i suoi cookie (come __gads e __gpi) per servire gli annunci, limitare quante volte li vedi e misurarli, e può trattare i dati negli Stati Uniti nell'ambito dell'EU-US Data Privacy Framework. Gli annunci non sono personalizzati, salvo che questa pagina dica altrimenti. Se rifiuti, gli spazi non compaiono e da Google AdSense non si carica nulla.",

  social_titolo: "Entrare con un social",
  social_account: "Un account per persona: se entri con Google, Facebook, Apple, GitHub o LinkedIn con la stessa email di un account che esiste già, è lo stesso account, con le stesse letture e gli stessi crediti.",
  social_cosa: "Da quell'account riceviamo ciò che ci condivide: nome e cognome, email, foto del profilo, lingua e — solo se lo permetti nella schermata del provider — data di nascita, genere e città. Li usiamo solo per riempire i campi del tuo account ancora vuoti, mai sopra ciò che hai scritto tu.",
  social_perche: "Perché: dalla data di nascita vengono le tue carte personali (la carta dell'anima e quella dell'anno) e il genere serve a pronomi e concordanze nelle letture di coppia; nome, lingua e foto ti evitano di riscriverli. Base giuridica: il servizio che chiedi, e la tua scelta nella schermata del provider.",
  social_posizione: "Posizione attuale: paese e città, dal social se li condivide, altrimenti stimati a ogni accesso dal tuo indirizzo IP con un database che sta sul nostro server (l'indirizzo non si salva e niente va a terzi). Ci aiuta ad adattare il servizio.",
  social_controllo: "Dal tuo account vedi da dove viene ogni dato, lo correggi o lo cancelli, fermi l'importazione o la posizione, o cancelli in un colpo tutto ciò che è arrivato dai social. I social collegati si gestiscono dalle impostazioni dell'account («Account collegati»).",
  social_cta: "Gestisci i tuoi dati",

  responsabili_titolo: "Chi altro tratta i tuoi dati, e dove",
  responsabili_intro: "Non vendiamo i tuoi dati e non li condividiamo con partner. Questi fornitori li trattano per conto nostro, o come titolari autonomi quando scegli di usarli:",
  responsabili: [
    { chi: "Hosting", cosa: "il nostro server e il database. Fornitore e luogo: {hosting}." },
    { chi: "Fornitori dell'AI", cosa: "i fornitori dei modelli linguistici che configuriamo ricevono il testo della domanda, dell'intervista e della chat — con i nomi sostituiti da un segnaposto e mai il cognome — solo per scrivere la lettura. Fornitori attuali e paesi: {fornitori_ai}." },
    { chi: "Google", cosa: "Google Analytics e AdSense (solo col tuo consenso) e l'accesso con Google (Google Ireland Ltd., i dati possono andare negli Stati Uniti)." },
    { chi: "Accesso con i social", cosa: "Apple, Facebook (Meta), GitHub e LinkedIn, solo se scegli di entrare con loro: sono titolari autonomi del tuo account presso di loro." },
    { chi: "Pagamenti", cosa: "Stripe, per i pagamenti con carta (Stripe Payments Europe, i dati possono andare negli Stati Uniti). Il numero della carta non lo vediamo mai." },
    { chi: "Notifiche dell'app", cosa: "Firebase Cloud Messaging (Google), per le notifiche dell'app, quando arriveranno." },
    { chi: "Email e backup", cosa: "la posta che scrivi a un indirizzo @tarots.chat passa dal servizio di inoltro di Namecheap (Stati Uniti) e arriva in una casella Gmail del titolare (Google); le email che ti mandiamo partono dal nostro server, ospitato da Hivelocity a Londra; i backup stanno in un nostro archivio in Italia, senza terzi." },
  ],
  hosting_vuoto: "un fornitore vincolato da un accordo sul trattamento dei dati",
  fornitori_ai_vuoto: "nessuno attivo in questo momento",
  fornitori_ai_proprio: "su un nostro server, nessun terzo",
  trasferimenti: "Quando i dati escono dallo Spazio economico europeo ci basiamo su una decisione di adeguatezza della Commissione europea (il Regno Unito; gli Stati Uniti per le aziende certificate nell'EU-US Data Privacy Framework) o sulle clausole contrattuali tipo della Commissione.",

  conservazione_titolo: "Per quanto tempo li conserviamo",
  conservazione: [
    "Account, letture, memoria e chat: finché non li cancelli tu, o non cancelli l'account. Non c'è una scadenza automatica: possiamo cancellare noi dati vecchi, per esempio le letture gratuite senza account e le chat datate.",
    "La lettura gratuita senza account: finché non la cancelliamo; se ti iscrivi, entra nel tuo account.",
    "Statistiche dettagliate delle visite: 25 mesi, poi restano solo totali giornalieri anonimi.",
    "Le tue scelte sui consensi: per il tempo necessario a dimostrarle.",
    "Documenti contabili (pagamenti, crediti, ordini): per il tempo che la legge chiede (in Italia, dieci anni). Se cancelli l'account, restano staccati dalla tua identità.",
    "Backup: i dati cancellati spariscono dai backup man mano che ruotano, entro circa una settimana.",
  ],

  diritti_titolo: "I tuoi diritti",
  diritti_testo: "Puoi chiedere di accedere ai tuoi dati, correggerli, cancellarli, riceverli in un formato portabile, limitarne l'uso o opporti, e revocare qualsiasi consenso in qualsiasi momento — senza toccare ciò che è stato fatto prima.",
  diritti_come: "Quasi tutto puoi farlo da solo: scaricare i tuoi dati e cancellare l'account dalla pagina del tuo account, e cambiare ogni consenso lì o in questa pagina. Per tutto il resto scrivi al contatto per la privacy qui sopra: rispondiamo entro un mese.",
  diritti_cta_dati: "I tuoi dati e i consensi",
  diritti_cta_elimina: "Elimina l'account",
  garante_titolo: "Reclami",
  garante_testo: "Se ritieni che i tuoi dati siano trattati in modo illecito, puoi proporre reclamo al Garante per la protezione dei dati personali (www.garanteprivacy.it) o all'autorità del paese in cui vivi o lavori.",

  eta_titolo: "Età minima",
  eta_testo: "TAROTS chat è per chi ha almeno 16 anni; 14 in Italia e in Spagna, 15 in Francia — l'età in cui la legge ti permette di usare da solo i servizi online. Te la chiediamo prima della prima lettura. Se la data di nascita nel tuo account è sotto il minimo, letture e chat si fermano.",

  versione: "Versione 3 — 3 ottobre 2026.",
};
