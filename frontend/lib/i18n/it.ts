/* L'interfaccia in italiano: è il dizionario di riferimento.
 *
 * Il tipo `Dizionario` viene da qui: una lingua tradotta per intero (`en`,
 * `hu`) deve avere ogni chiave, e il compilatore lo verifica. Una lingua
 * tradotta a metà usa `Parziale` e ricade sull'inglese per le chiavi mancanti.
 *
 * Solo i testi dell'interfaccia stanno qui. I testi lunghi — domande
 * dell'oracolo, interpretazioni, responso, disclaimer — arrivano dal server già
 * nella lingua del quesito.
 */

export const it = {
  marchio: "T·AI·rots",
  motto: "L'oracolo del Tarocco di Thoth, letto da un'intelligenza artificiale.",
  sovratitolo: "Tarocco di Thoth · Aleister Crowley",

  /* navigazione e sessione */
  nav_leggi: "Consulta",
  nav_letture: "Le mie letture",
  nav_giorno: "Carta del giorno",
  nav_carte: "Le carte",
  nav_piano: "Crediti",
  nav_profilo: "Profilo",
  nav_admin: "Admin",
  aria_lingua: "Lingua",
  aria_sezioni: "Sezioni",
  entra: "Entra",
  registrati: "Registrati",
  esci: "Esci",
  verifica_sessione: "Verifica della sessione…",
  serve_account: "Serve un account per consultare le carte.",

  /* scelta della stesa e della domanda */
  inizia: "Inizia la consultazione",
  scegli_stesa: "Scegli la stesa",
  la_tua_domanda: "La tua domanda",
  domanda_segnaposto: "Scrivi ciò che vuoi chiedere alle carte: una domanda, un dubbio, o anche solo «cosa mi riserva il futuro?»",
  maggiori: "22 Arcani maggiori",
  completo: "78 carte",
  carte: "carte",
  accetto: "Ho capito, procediamo",
  disclaimer_titolo: "Prima di cominciare",

  /* colloquio */
  oracolo: "L'oracolo",
  tu: "Tu",
  rispondi: "Rispondi",
  risposta_segnaposto: "Scrivi la tua risposta…",
  oracolo_pensa: "L'oracolo sta pensando",

  /* mazzo, taglio, scelta, rivelazione */
  mescola: "Mescola le carte",
  mescolando: "Le carte si mescolano…",
  ferma_mescolata: "Clicca sul mazzo per fermare la mescolata",
  taglia_mazzo: "Taglia il mazzo",
  taglia_istruzione: "Clicca nel punto in cui vuoi dividere il mazzo",
  riprova: "Riprova",
  scegli_n: (n: number) => (n === 1 ? "Scegli l'ultima carta" : `Scegli ancora ${n} carte`),
  tocca_per_rivelare: "Tocca la carta che brilla per rivelarla",
  rivela: "Rivela",
  carta_coperta: "Carta coperta",
  dritta: "dritta",
  rovesciata: "rovesciata",
  dignita: "Dignità",
  doppia_valenza: "Doppia valenza",
  sintesi_calcolata: "Sintesi calcolata",

  /* responso */
  responso: "Ricevi il responso",
  fase_unione: "Le carte si parlano: sto unendo domanda, colloquio e stesa…",
  fase_guardia: "Il guardiano verifica il responso…",
  fase_revisione: "Il responso viene rivisto con maggiore cura…",
  il_responso: "Il responso",
  nuova_lettura: "Nuova lettura",
  condividi: "Condividi",
  scarica_immagine: "Scarica l'immagine",
  link_copiato: "Link copiato",
  immagine_piede: "Lettura AI · non è una certezza · nessuna base scientifica",
  verifica_mazzo: "Verifica del mazzo",
  verifica_testo: "Le carte erano fissate prima della tua scelta. Hash del mazzo:",

  /* crediti */
  crediti: "crediti",
  credito: "credito",
  compra: "Acquista crediti",
  crediti_finiti: "Hai esaurito i crediti",
  crediti_finiti_testo: "Ogni consultazione usa un credito, oppure una delle letture giornaliere del tuo abbonamento. Scegli un pacchetto o un abbonamento per continuare.",
  chiudi: "Chiudi",

  /* diario e storico */
  si: "Sì",
  in_parte: "In parte",
  no: "No",
  si_e_avverato: "Si è avverato?",
  cancella: "Cancella",
  conferma_cancella: "Cancellare definitivamente questa lettura?",
  nessuna_lettura: "Nessuna lettura ancora. Le carte aspettano la tua prima domanda.",
  letture_sottotitolo: "Ogni lettura resta salvata. Puoi riaprirla, annotare se si è avverata, o cancellarla per sempre.",
  ritira_condivisione: "Ritira la condivisione",
  il_quadro: "Il quadro",
  stati: {
    intervista: "in intervista",
    ventaglio: "pronta da mescolare",
    scelta: "carte da scegliere",
    rivelazione: "carte da rivelare",
    sintesi: "in attesa del responso",
    completata: "completata",
    annullata: "sospesa",
  },

  /* soglia */
  home_come: "Come si svolge una lettura",
  home_passi: [
    ["Domanda", "Scrivi ciò che vuoi sapere: una scelta, un sentimento, o semplicemente il futuro."],
    ["Intervista", "L'oracolo ti fa poche domande per capire il contesto — mai la risposta al tuo quesito."],
    ["Le carte", "Scegli dal ventaglio: le carte sono già assegnate e si girano una a una sul tavolo."],
    ["Il responso", "L'AI unisce domanda, colloquio, stesa, dignità e simboli in una lettura coerente."],
  ],
  home_stese: "Cinque stese della tradizione",
  home_rigore: "Rigore esoterico",
  home_rigore_1:
    "Ogni carta porta le sue vere attribuzioni del Thoth — lettera ebraica, sentiero sull'Albero della Vita, decano, sephira — ed è letta su più livelli. Le carte vicine si modulano a vicenda con le dignità elementali di Crowley; nella croce semplice la sintesi si calcola per somma teosofica, come insegnava Oswald Wirth.",
  home_rigore_2:
    "Il mazzo è mescolato e sigillato con un hash crittografico prima che tu scelga: a fine lettura puoi verificare che nessuna carta sia stata cambiata dopo la tua scelta.",
  home_avvertenza:
    "Una lettura AI, coerente e rigorosa sul piano esoterico. Non è una certezza: mostra il più probabile dei futuri. Non esiste alcuna base scientifica che dimostri la validità delle previsioni dei tarocchi.",

  /* le carte */
  carte_sottotitolo: "Le 78 carte del Tarocco di Thoth con le loro attribuzioni e i significati sui diversi livelli.",
  filtri: {
    tutte: "tutte",
    maggiori: "maggiori",
    bastoni: "bastoni",
    coppe: "coppe",
    spade: "spade",
    dischi: "dischi",
  },
  livelli: {
    essoterico: "Significato essoterico",
    psicologico: "Livello psicologico",
    iniziatico: "Livello iniziatico",
    ombra: "Ombra",
  },
  ambiti: { amore: "amore", lavoro: "lavoro", spirito: "spirito" },
  sentiero: "sentiero",

  /* carta del giorno */
  giorno_sottotitolo: "Un Arcano maggiore per la tua giornata, gratuito. Giralo quando sei pronto.",
  giorni_di_fila: (n: number) => (n === 1 ? "1 giorno" : `${n} giorni di fila`),

  /* crediti e abbonamenti */
  piano_titolo: "Crediti e abbonamenti",
  piano_sottotitolo: "Ogni lettura usa un credito, oppure una delle letture giornaliere del tuo abbonamento. In questa versione i pagamenti sono simulati.",
  pacchetti: "Pacchetti di letture",
  abbonamenti: "Abbonamenti",
  movimenti_recenti: "Movimenti recenti",
  nessun_movimento: "Nessun movimento ancora.",
  motivi: {
    accredito_piano: "Crediti del piano",
    acquisto: "Pacchetto acquistato",
    consumo: "Lettura",
    rimborso: "Rimborso",
    rettifica: "Correzione",
    scadenza: "Scadenza",
    omaggio: "Omaggio",
  },
  il_tuo_saldo: "Il tuo saldo",
  abbonamento: "Abbonamento",
  gratuito: "Gratuito",
  disdetto_fino: (data: string) => `Disdetto: resta attivo fino al ${data}.`,
  si_rinnova: (data: string) => `Si rinnova il ${data}.`,
  letture_di_oggi: "Letture di oggi",
  disdici: "Disdici",
  gratis: "Gratis",
  al_mese: "/ mese",
  crediti_a_lettura: (n: number, prezzo: string) => `${n} crediti · ${prezzo} a lettura`,
  letture_al_giorno: (n: number) => `${n} letture al giorno`,
  carta_giorno_gratuita: "Carta del giorno gratuita",
  il_tuo_piano: "Il tuo piano",
  acquista: "Acquista",
  scegli: "Scegli",
  abbonati: "Abbonati",
  pagamento_pacchetto: (nome: string) => `Pagamento riuscito: i crediti di «${nome}» sono sul tuo saldo.`,
  pagamento_piano: (nome: string) => `Pagamento riuscito: il piano «${nome}» è attivo.`,
  pagamento_non_completato: "Il pagamento non è stato completato.",
  pagamento_non_verificato: "Non è stato possibile verificare il pagamento.",

  /* profilo */
  profilo_carte: "Le tue carte personali",
  profilo_carte_testo:
    "Dalla data di nascita si ricavano, per riduzione teosofica, la carta dell'anima — la lezione di una vita — e la carta del tuo anno personale. Se la indichi, l'oracolo ne terrà conto nelle letture.",
  data_nascita: "Data di nascita",
  salva: "Salva",
  carta_anima: "Carta dell'anima",
  carta_anno: "Carta dell'anno",
  invita_titolo: "Invita chi ami",
  invita_testo: "Per ogni persona che si iscrive con il tuo codice, tu e lei ricevete 3 letture in regalo.",
  invito_testo_condivisione: (codice: string) => `Il mio codice invito: ${codice}`,
  condividi_codice: "Condividi il codice",
  copiato: "Copiato",
  hai_codice: "Hai un codice invito?",
  riscatta: "Riscatta",
  letture_regalo: (n: number) => `Hai ricevuto ${n} letture in regalo.`,

  /* tipo di lettura */
  tipo_titolo: "Che lettura vuoi fare?",
  tipo_standard: "Lettura standard",
  tipo_standard_desc: "Una domanda e una stesa della tradizione: la lettura di sempre.",
  tipo_compat: "Compatibilità con un partner",
  tipo_compat_desc: "Cosa unisce e cosa distingue te e un'altra persona: carte e segni zodiacali a confronto.",
  tipo_coppia: "Relazione di coppia",
  tipo_coppia_desc: "Lo stato del legame che stai vivendo: forze, attriti, consiglio ed esito.",
  badge_compat: "Compatibilità",
  badge_coppia: "Coppia",
  indietro: "Indietro",
  avanti: "Avanti",
  cambia_tipo: "← Cambia tipo di lettura",

  /* le persone */
  persone_titolo: "Le persone",
  persone_partner: "L'altra persona",
  persone_di_te: "Di te",
  persone_di_te_testo: "Per queste letture servono anche alcuni tuoi dati: restano nel tuo profilo e non te li chiediamo più.",
  persone_nome: "Nome",
  persone_cognome: "Cognome (facoltativo)",
  persone_nascita: "Data di nascita",
  persone_genere: "Sesso / genere",
  persone_genere_scegli: "Scegli…",
  persone_genere_altro: "Specifica",
  persone_trans: "Persona trans (facoltativo)",
  persona_trans: "persona trans",
  generi: {
    donna: "Donna",
    uomo: "Uomo",
    non_binario: "Non binario",
    altro: "Altro",
    non_dice: "Preferisco non dirlo",
  },
  persone_ricorda: "Ricorda questi dati per la prossima volta",
  persone_privacy:
    "I dati di un'altra persona restano nel tuo storico: non si condividono, e il cognome non viene mai passato all'intelligenza artificiale. Inseriscili solo se ti senti a tuo agio; puoi cancellare il partner ricordato dal profilo.",
  persone_ripresi: (nome: string) => `Ho ripreso i dati di ${nome}.`,
  persone_dimentica: "Dimentica",
  err_persone_nome: "Scrivi il nome.",
  err_persone_genere: "Scegli un'opzione.",
  err_persone_nascita: "Indica una data di nascita valida.",
  err_persone_altro: "Scrivi come ci si definisce.",
  err_profilo_incompleto: "Completa i dati che mancano per continuare.",

  /* lo stile di stesa */
  stile_titolo: "Scegli lo stile di stesa",
  stile_tradizionale: "Tradizionale",
  stile_moderna: "Moderna",
  stile_tendenza: "Di tendenza",
  stile_tradizionale_desc: "Le stese classiche, quelle che si trovano nei manuali.",
  stile_moderna_desc: "Le stese della cartomanzia contemporanea.",
  stile_tendenza_desc: "Le stese più diffuse ora fra chi legge online.",
  domanda_facoltativa: "La domanda è facoltativa: se la lasci vuota la lettura parte dal tipo che hai scelto.",
  domanda_default_compat: (nome: string) => `Compatibilità con ${nome}`,
  domanda_default_coppia: (nome: string) => `Relazione di coppia con ${nome}`,
  inizia_speciale: "Inizia la lettura",
  tu_e: (nome: string) => `Tu e ${nome}`,

  /* la legenda del tavolo */
  soggetto_tu: "Tu",
  soggetto_partner: "L'altra persona",
  soggetto_coppia: "La relazione",
  soggetto_strada: "Le due strade",
  legenda: "Legenda",

  /* il profilo */
  profilo_genere_titolo: "Sesso / genere",
  profilo_genere_testo:
    "Serve solo alle letture di compatibilità e di coppia, per pronomi e concordanze. «Preferisco non dirlo» è una risposta valida.",
  profilo_partner_titolo: "Partner ricordato",
  profilo_partner_vuoto: "Nessun partner ricordato. Puoi ricordarlo dal modulo di una lettura di compatibilità o di coppia.",
  profilo_partner_cancella: "Cancella",
  profilo_partner_conferma: "Cancellare il partner ricordato?",

  /* storico e dettaglio */
  le_persone: "Le persone",
  compat_zodiacale: "Compatibilità zodiacale",
  compat_avviso: "Solo i segni solari: senza ora e luogo di nascita non ci sono ascendente né luna. È uno sfondo, non un verdetto.",
  segno_di: (nome: string, segno: string) => `${nome}: ${segno}`,
  aspetto_titolo: "Aspetto",
  armonia_titolo: "Armonia",
  elementi_titolo: "Elementi",
  carta_coppia: "Carta della coppia",
  cuspide_di: (segno: string) => `al confine con ${segno}`,
  segni: {
    ariete: "Ariete", toro: "Toro", gemelli: "Gemelli", cancro: "Cancro", leone: "Leone", vergine: "Vergine",
    bilancia: "Bilancia", scorpione: "Scorpione", sagittario: "Sagittario", capricorno: "Capricorno",
    acquario: "Acquario", pesci: "Pesci",
  },
  aspetti: {
    congiunzione: "congiunzione", semisestile: "semisestile", sestile: "sestile", quadrato: "quadrato",
    trigono: "trigono", quinconce: "quinconce", opposizione: "opposizione",
  },
  armonie: { alta: "alta", buona: "buona", mista: "mista", impegnativa: "impegnativa" },
  elementi: { fuoco: "fuoco", terra: "terra", aria: "aria", acqua: "acqua" },
  relazioni_elementi: {
    rafforzata: "stesso elemento", amica: "elementi amici", moderata: "elementi moderati",
    ostile: "elementi in contrasto", neutra: "neutra",
  },

  /* la soglia: le letture speciali */
  home_speciali: "Letture speciali",
  home_speciali_testo: "Due letture pensate per chi vuole capire un legame: con un partner o dentro una coppia.",

  /* errori */
  err_generico: "Qualcosa non ha funzionato.",
  err_operazione: "L'operazione non è riuscita.",
  err_sessione: "La sessione è scaduta.",
  err_richiesta: "Richiesta non riuscita.",
  err_oracolo: "L'oracolo non ha risposto.",
  err_lettura: "La lettura non è partita.",
  err_mazzo: "Il mazzo non si è aperto.",
  err_posa: "La carta non è stata posata.",
  err_giro: "La carta non si è girata.",
  err_responso: "Il responso non è arrivato.",

  /* La condivisione */
  cond_titolo: "Condividi la lettura",
  cond_anteprima: "Anteprima della condivisione",
  cond_testo_etichetta: "Il tuo testo (facoltativo)",
  cond_testo_segnaposto: "Es.: Guarda cosa mi hanno detto le carte ✨",
  cond_testo_aiuto: "Compare sull'immagine e nel post.",
  cond_preparo: "Preparo l'immagine e il link…",
  cond_pronta: "Tutto pronto: scegli dove condividere.",
  cond_errore: "Non sono riuscito a preparare la condivisione.",
  cond_condividi_su: "Condividi su",
  cond_condividi_con: (nome: string) => `Condividi con ${nome}`,
  cond_email: "Email",
  cond_solo_link: "Solo link",
  cond_copiato: "Link copiato negli appunti",
  cond_scaricata: (rete: string) => `Immagine scaricata e testo copiato: caricala su ${rete}.`,
  cond_apri: (rete: string) => `Apri ${rete}`,
  cond_scarica: "Scarica l'immagine",
  cond_premio_titolo: "Condividi e guadagna letture",
  cond_premio_1: (n: number) => `Ogni ${n} condivisioni verificate, 1 lettura in omaggio`,
  cond_premio_2: (n: number) => `Chi si iscrive dal tuo link ti regala ${n} letture gratis (anche con l'iscrizione gratuita)`,
  cond_premio_3: "Nessun limite: più condividi, più letture guadagni",
  cond_contatore: (verificate: number, manca: number) =>
    `${verificate} condivisioni verificate · ${manca === 1 ? "ne manca 1" : `ne mancano ${manca}`} alla prossima lettura in omaggio`,
  cond_verificata_spiega: "Una condivisione è verificata quando qualcun altro apre il tuo link.",
  cond_speciale_nota: "Nelle letture di coppia il nome dell'altra persona non compare: al suo posto un simbolo e la scritta «qualcuno di speciale».",
  cond_link_attivo: "Il link è attivo: chi lo riceve vede la lettura, ma non il tuo nome.",
  cond_disattiva: "Disattiva il link",
  prof_cond_titolo: "Le tue condivisioni",
  prof_cond_testo: (soglia: number, crediti: number) =>
    `Ogni ${soglia} condivisioni verificate ricevi una lettura in omaggio, e chi si iscrive dal tuo link te ne regala ${crediti}. Una condivisione è verificata quando qualcun altro apre il tuo link.`,
  prof_cond_verificate: "Condivisioni verificate",
  prof_cond_premi: "Letture in omaggio ricevute",
  prof_cond_iscritti: "Iscritti dal tuo link",
  prof_cond_prossimo: (n: number) => (n === 1 ? "Ne manca 1 alla prossima lettura in omaggio" : `Ne mancano ${n} alla prossima lettura in omaggio`),
  pub_iscriviti: "Iscriviti gratis",
  pub_invito: (n: number) => `Vuoi la tua lettura? Iscriviti gratis: chi ti ha inviato questo link riceve ${n} letture in regalo.`,

  /* Verifica in due passaggi */
  sic_titolo: "Verifica in due passaggi",
  sic_testo: "Proteggi il tuo account con un codice temporaneo generato da un'app di autenticazione (Google Authenticator, Microsoft Authenticator, FreeOTP). Anche se qualcuno scoprisse la tua password, non potrebbe entrare. È facoltativa.",
  sic_attiva: "Attiva ora",
  sic_piu_tardi: "Più tardi",
  sic_non_mostrare: "Non mostrare più questo promemoria",
  sic_profilo_titolo: "Sicurezza dell'account",
  sic_stato: "Verifica in due passaggi",
  sic_stato_attiva: "Attiva",
  sic_stato_spenta: "Non attiva",
  sic_stato_ignota: "Stato non disponibile: controllalo nel tuo account",
  sic_attiva_2fa: "Attiva la verifica in due passaggi",
  sic_gestisci: "Gestisci nell'account",
  sic_promemoria: "Ricordami di attivarla ad ogni accesso",
};

/** La forma di un dizionario completo. */
export type Dizionario = typeof it;

/** Un dizionario tradotto a metà: le chiavi che mancano ricadono sull'inglese. */
export type Parziale = Partial<Dizionario>;

export type Chiave = keyof Dizionario;
