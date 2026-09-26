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
};

/** La forma di un dizionario completo. */
export type Dizionario = typeof it;

/** Un dizionario tradotto a metà: le chiavi che mancano ricadono sull'inglese. */
export type Parziale = Partial<Dizionario>;

export type Chiave = keyof Dizionario;
