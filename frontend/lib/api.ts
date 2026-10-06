/* Il client dell'API.
 *
 * Lo schema viene da Personalities: `leggi()` traduce gli errori nel motivo
 * che il server manda, e lo streaming si legge dal corpo di `fetch` invece
 * che con `EventSource`, che non porta intestazioni — quindi non porta il
 * token — e non fa POST.
 */

import { dizionario, type Lingua } from "./i18n";

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";

/* La lingua dell'interfaccia, per i messaggi d'errore che nascono fuori dai
 * componenti: la imposta `ProviderLingua` a ogni cambio. */
let linguaMessaggi: Lingua = "it";
export const impostaLinguaMessaggi = (l: Lingua) => {
  linguaMessaggi = l;
};

/* La v2 (`app/(v2)`) ha un dizionario suo, separato da quello del sito: i due messaggi d'errore che nascono qui
 * li prende da lì. I due siti non convivono mai nella stessa pagina (layout radice diversi, si passa dall'uno
 * all'altro ricaricando), quindi un valore globale basta. `null` torna al dizionario del sito. */
let messaggiPropri: { sessione: string; richiesta: string } | null = null;
export const impostaMessaggiErrore = (m: { sessione: string; richiesta: string } | null) => {
  messaggiPropri = m;
};

/* ---- tipi del dominio ---- */

export interface LetteraEbraica {
  nome: string;
  glifo: string;
  valore: number;
}

export interface Carta {
  id: string;
  arcano: "maggiore" | "minore";
  numero: number | null;
  numero_romano: string | null;
  seme: string | null;
  rango: string | null;
  nome_thoth: string;
  titolo_thoth: string | null;
  nome_it: string;
  /* Il nome nelle altre lingue: `en` sempre, poi quelle con nomi propri. */
  nomi?: Record<string, string>;
  /* Le pagine pubbliche chiedono i testi in una lingua (`?lang=`): `nome` e `slug` sono in quella lingua, `slugs`
   * porta l'indirizzo in ciascuna, e le `*_label` sono i termini tradotti (Air, Wands, Major Arcana…). */
  lang?: "it" | "en";
  nome?: string;
  slug?: string;
  slugs?: Record<string, string>;
  elemento_label?: string | null;
  seme_label?: string | null;
  rango_label?: string | null;
  arcano_label?: string | null;
  lettera_ebraica: LetteraEbraica | null;
  elemento: string;
  astrologia: string;
  parole_chiave: string[];
  colori: string[];
  /* Solo nella scheda completa. */
  percorso?: number | null;
  collega?: string[] | null;
  sefira?: string | null;
  significati?: Record<string, string>;
  dritto?: string;
  rovescio?: string;
  ambiti?: Record<string, string>;
  nota_crowley?: string;
}

/* Di chi parla una posizione nelle letture di compatibilità e di coppia. */
export type Soggetto = "tu" | "partner" | "coppia" | "strada-a" | "strada-b";

export interface Posizione {
  n: number;
  nome: string;
  nome_en: string;
  nomi?: Record<string, string>;
  /* Solo nelle stese speciali. */
  soggetto?: Soggetto;
  significato: string;
  domanda: string;
  x: number;
  y: number;
  rotazione: number;
  calcolata: boolean;
}

/* Il tipo di lettura: la standard e le due speciali. */
/* `lavoro` (lavoro e affari) si svolge come la standard: nessun dato del partner. */
export type Categoria = "standard" | "lavoro" | "compatibilita" | "coppia";
export type Stile = "tradizionale" | "moderna" | "tendenza";

export interface Stesa {
  id: string;
  nome: string;
  nome_en: string;
  nomi?: Record<string, string>;
  /* Come per le carte: lingua dei testi, indirizzo in ciascuna lingua, termini tradotti. */
  lang?: "it" | "en";
  slug?: string;
  slugs?: Record<string, string>;
  mazzo_label?: string | null;
  categoria_label?: string | null;
  stile_label?: string | null;
  categoria: Categoria;
  /* I temi per cui una stesa standard si propone anche altrove: `["lavoro"]` la mette anche fra quelle
   * di «Lavoro e affari» (`/spreads?tema=lavoro` le restituisce già insieme a quelle di categoria `lavoro`). */
  temi?: string[];
  /* Solo nelle stese speciali e in quelle di lavoro. */
  stile: Stile | null;
  /* La larghezza di una carta come frazione del tavolo (e sul tavolo 1:1 dei
   * telefoni): sta nei dati della stesa, non nel codice del tavolo. */
  larghezza: number | null;
  larghezza_stretto: number | null;
  forma: "standard" | "quadrata";
  mazzo: "maggiori" | "completo";
  carte_da_scegliere: number;
  origine: string;
  descrizione: string;
  posizioni: Posizione[];
  regole: string[];
  coppie: [number, number, string][];
  sintesi_wirth: boolean;
  /* v9.4 (assenti da un'API più vecchia): l'illustrazione della stesa (`{url, mini, alt}` relativi all'API) e la
   * tradizione in poche parole, nella lingua dei testi e per lingua (`tradizioni.hu`…). */
  immagine?: { url: string; mini?: string | null; alt: string } | null;
  tradizione?: string | null;
  tradizioni?: Record<string, string>;
}

export interface Dignita {
  elemento: string;
  punteggio: number;
  giudizio: string;
  relazioni: { posizione: number; elemento: string; relazione: string }[];
}

export interface CartaPosata {
  posizione: number;
  calcolata: boolean;
  rivelata: boolean;
  carta?: Carta;
  rovescio?: boolean;
  interpretazione?: string | null;
}

export type StatoLettura =
  | "intervista" | "ventaglio" | "scelta" | "rivelazione" | "sintesi" | "completata" | "annullata";

/* I dati di una persona nelle letture speciali. Il cognome c'è solo qui e nello
 * storico: all'intelligenza artificiale non arriva mai. */
export type Genere = "donna" | "uomo" | "non_binario" | "altro" | "non_dice";

export interface PersonaSalvata {
  nome: string;
  cognome: string | null;
  genere: Genere;
  genere_altro: string | null;
  trans: boolean;
  nascita: string;
}

export interface PersoneLettura {
  v: number;
  tu: { genere: Genere | null; genere_altro: string | null; trans: boolean; nascita: string };
  partner: PersonaSalvata;
}

export interface SegnoCalcolato {
  codice: string;
  elemento: string;
  modalita: string;
  cuspide: boolean;
  vicino: string | null;
}

/* La compatibilità zodiacale come codici: l'interfaccia li traduce. */
export interface Compatibilita {
  segni: { tu: SegnoCalcolato; partner: SegnoCalcolato };
  distanza: number;
  aspetto: string;
  relazione_elementi: string;
  stessa_modalita: boolean;
  armonia: string;
  carta_coppia: Carta;
  carta_anima_tu: Carta;
  carta_anima_partner: Carta;
}

export interface Lettura {
  id: string;
  /* La cartella delle immagini del mazzo della lettura; `null` = il predefinito (v8.5). */
  mazzo?: string | null;
  spread_id: string;
  stesa: string;
  stesa_nomi: Record<string, string>;
  categoria: Categoria;
  stile: Stile | null;
  persone: PersoneLettura | null;
  compatibilita: Compatibilita | null;
  question: string;
  status: StatoLettura;
  lang: string;
  consumo: string;
  created_at: string;
  completed_at: string | null;
  feedback: "si" | "in_parte" | "no" | null;
  shared: boolean;
  /* "Interpreta i miei tarocchi" (v5): il mazzo è fisico, già estratto — le carte si vedono scoperte
   * da subito, indipendentemente dal ritmo di rivelazione dell'interpretazione. */
  manuale: boolean;
  context_summary: string | null;
  interview: { ruolo: "oracolo" | "utente"; testo: string; ordine: number }[];
  cards: CartaPosata[];
  slot_count: number | null;
  picked_slots: number[];
  commitment: string | null;
  deck_salt: string | null;
  synthesis: string | null;
  guard_outcome: string | null;
  share_token: string | null;
  /* Il testo personalizzato del post, come l'ha scritto chi ha condiviso. */
  share_text: string | null;
  feedback_note: string | null;
  disclaimer: string;
  dignita: Record<string, Dignita>;
  stesa_dati: Stesa;
}

export interface LetturaBreve {
  id: string;
  /* La cartella delle immagini del mazzo della lettura; `null` = il predefinito (v8.5). */
  mazzo?: string | null;
  spread_id: string;
  stesa: string;
  stesa_nomi: Record<string, string>;
  categoria: Categoria;
  stile: Stile | null;
  partner_nome: string | null;
  question: string;
  status: StatoLettura;
  created_at: string;
  completed_at: string | null;
  feedback: string | null;
  shared: boolean;
  carte: string[];
}

export interface Piano {
  slug: string;
  nome: string;
  tipo: "abbonamento" | "pacchetto";
  descrizione: string | null;
  valuta: string;
  prezzo_mensile: number;
  prezzo_annuale: number;
  crediti_per_periodo: number;
  limiti: Record<string, number>;
  /* v9, Fase 2b: il livello (decide upgrade o downgrade) e i prezzi con e senza rinnovo automatico. */
  livello?: number;
  prezzi?: {
    mensile: { listino: number; con_rinnovo: number; sconto: number };
    annuale: { listino: number; con_rinnovo: number; sconto: number } | null;
    prova_annuale: number | null;
  };
}

export interface Conto {
  abbonamento: {
    id: string;
    piano: string;
    nome: string;
    stato: string;
    periodo_inizio: string;
    periodo_fine: string;
    disdetto_il: string | null;
    /* v9, Fase 2b (il resto in `lib/abbonamenti.ts`, `AbbonamentoDettaglio`). */
    annuale?: boolean;
    rinnovo_automatico?: boolean;
  } | null;
  diritti: { piano: string; nome: string; limiti: Record<string, number>; predefiniti: boolean };
  saldo: number;
  uso: Record<string, { usati: number; limite: number | null; restanti: number | null }>;
  limiti_attivi: boolean;
  /* v9, Fase 2b: un abbonamento a pagamento con letture comprese (oltre il limite: condono o consenso al credito), e
   * se la prova gratuita è ancora possibile (il banner della prova lo legge da qui). */
  letture_comprese?: boolean;
  prova?: { idonea: boolean; motivo: string | null };
}

export interface Movimento {
  delta: number;
  reason: string;
  quando: string;
  note: string | null;
  reading_id: string | null;
}

/** Un mazzo del negozio (v5, Fase B): il predefinito (Thoth) è sempre posseduto, senza sblocco. */
export interface Mazzo {
  id: number;
  slug: string;
  nome: string;
  descrizione: string | null;
  predefinito: boolean;
  attivo: boolean;
  attivo_ora: boolean;
  attivazione_da: string | null;
  attivazione_fino: string | null;
  prezzo_digitale: number | null;
  prezzo_digitale_scontato: number | null;
  /* v8.5: l'offerta può valere anche sul PDF e sulla scatola. */
  prezzo_stampa_scontato?: number | null;
  prezzo_fisico_scontato?: number | null;
  offerta_formati?: TipoVoceOrdine[];
  offerta_attiva: boolean;
  offerta_valido_fino: string | null;
  prezzo_stampa: number | null;
  prezzo_fisico: number | null;
  richiede_spedizione: boolean;
  valuta: string;
  rank: number;
}

export type TipoVoceOrdine = "digitale" | "pdf" | "fisico";

export interface VoceCarrelloInvio {
  deck_id: number;
  tipo: TipoVoceOrdine;
  quantita?: number;
}

export interface RigaOrdine {
  id: number;
  tipo: TipoVoceOrdine;
  deck_id: number;
  /* Il mazzo della riga (v8.5): il nome da mostrare. */
  mazzo?: { nome: string; slug: string } | null;
  quantita: number;
  prezzo_pieno_unitario: number;
  prezzo_finale_unitario: number;
  stato_evasione: string | null;
}

export interface Ordine {
  id: string;
  status: string;
  importo_totale: number;
  sconto_scaglioni: number;
  valuta: string;
  righe: RigaOrdine[];
  indirizzo_spedizione: Record<string, string | null> | null;
  creato: string | null;
  completato: string | null;
}

/* Il contatore delle condivisioni: una condivisione è «verificata» quando, dopo
 * che hai usato un pulsante di condivisione, qualcun altro apre il tuo link. */
export interface Condivisioni {
  verificate: number;
  premi: number;
  /* Quante condivisioni verificate mancano alla prossima lettura in omaggio. */
  prossimo_tra: number;
  iscrizioni: number;
  soglia: number;
  crediti_iscrizione: number;
}

export interface Profilo {
  id: number;
  email: string | null;
  display_name: string | null;
  locale: string;
  /* v9, Fase 2d: quando la lingua è stata scelta dal sito (menu o profilo); `null` = mai. */
  locale_scelta_il?: string | null;
  birth_date: string | null;
  gender: Genere | null;
  gender_custom: string | null;
  is_trans: boolean;
  /* Il promemoria della verifica in due passaggi all'accesso; `false` = «non mostrare più». */
  promemoria_2fa: boolean;
  /* Come ti presenti nei commenti del blog (`null` = il primo nome) e il nome che si vede davvero. */
  nome_pubblico: string | null;
  /* v7: "esoterico" (default) non cambia nulla; "quotidiano" evita termini tecnici non spiegati. */
  registro_linguistico: "esoterico" | "quotidiano";
  /* v7, Fase J: null = il mazzo predefinito globale. */
  mazzo_predefinito_id: number | null;
  nome_mostrato: string;
  /* L'immagine personale: percorso relativo dell'API (vedi `urlMedia`). */
  avatar: string | null;
  /* Con il cognome: si mostra solo al proprietario. */
  partner_ricordato: PersonaSalvata | null;
  relazioni: { completo: boolean; mancanti: ("genere" | "nascita")[] };
  referral_code: string | null;
  invitato: boolean;
  condivisioni: Condivisioni;
  carta_anima: Carta | null;
  carta_anno: Carta | null;
  /* La scheda anagrafica: la compila la persona o, se vuota, il social con cui entra (mai sopra un valore). */
  nome?: string | null;
  cognome?: string | null;
  /* Dove si trova adesso: dal social o dall'IP all'accesso; `fonte` "utente" se l'ha corretta lei. */
  posizione?: PosizioneAttuale | null;
  /* Da dove vengono i campi presi dai social: campo → provider ("google", "facebook", "account", "utente") e data. */
  dati_social?: Record<string, { da: string; il: string }>;
  importa_social?: boolean;
  rileva_posizione?: boolean;
}

export interface PosizioneAttuale {
  paese: string | null;
  citta: string | null;
  fonte: string | null;
  il: string | null;
}

/* Ciò che `POST /me/profilo-social` ha fatto: i campi compilati, i social letti, la posizione aggiornata. */
export interface EsitoProfiloSocial {
  compilati: string[];
  provider: string[];
  posizione: PosizioneAttuale | null;
  /* Keycloak ha appena unito questo accesso a un account con l'email mai verificata: va chiesto se era suo. */
  unione?: boolean;
}

/* `GET /me/unione`: l'account che c'era con la stessa email, mai verificato. Keycloak gli ha tolto i vecchi accessi
 * (`credenziali`: password, otp…; `social`: gli alias dei social non fidati); `contenuto` dice cosa c'era dentro. */
export interface UnioneDaConfermare {
  id: string;
  il: string;
  creato_il: string | null;
  credenziali: string[];
  social: string[];
  contenuto: {
    letture: number;
    memorie: number;
    ordini: number;
    acquisti: number;
    crediti: number;
    vuoto: boolean;
    iscritto_il: string | null;
  };
}

export interface CartaDelGiorno {
  giorno: string;
  carta: Carta;
  rovescio: boolean;
  testo: string;
  serie: number;
}

/* Il simbolo grafico con cui una lettura condivisa rappresenta l'altra persona. */
export type Simbolo = "venere" | "marte" | "mercurio" | "stella";

/* Ciò che chiunque vede di una lettura condivisa. Nelle letture speciali il
 * nome dell'altra persona è già stato sostituito dal server con `partner_frase`. */
export interface LetturaCondivisa {
  question: string;
  mazzo?: string | null;
  lang: string;
  stesa: Stesa | null;
  categoria: Categoria;
  speciale: boolean;
  partner_simbolo: Simbolo | null;
  partner_frase: string | null;
  cards: CartaPosata[];
  synthesis: string | null;
  share_text: string | null;
  /* Se l'immagine (WebP 400×300) è stata caricata: serve all'anteprima nei social. */
  immagine: boolean;
  created_at: string;
  disclaimer: string;
}

/* ---- errori e chiamate ---- */

export class ErroreApi extends Error {
  constructor(message: string, readonly stato: number, readonly dettaglio?: unknown) {
    super(message);
  }
}

function intestazioni(token: string | null): HeadersInit {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (token) h.Authorization = `Bearer ${token}`;
  return h;
}

async function leggi<T>(risposta: Response): Promise<T> {
  if (!risposta.ok) {
    /* Il motivo del server, quando c'è: per 402 e 409 è proprio ciò che serve
     * all'utente — «non hai crediti», «le carte si rivelano in ordine». Un
     * messaggio generico lo trasformerebbe in un guasto apparente. */
    let motivo: string | undefined;
    let dettaglio: unknown;
    try {
      const corpo = await risposta.json();
      dettaglio = corpo?.detail;
      motivo =
        typeof corpo?.detail === "string"
          ? corpo.detail
          : typeof corpo?.detail?.messaggio === "string"
            ? corpo.detail.messaggio
            : undefined;
    } catch {
      /* il corpo non era JSON: restano i codici */
    }
    const d = dizionario(linguaMessaggi);
    const m = messaggiPropri ?? { sessione: d.err_sessione, richiesta: d.err_richiesta };
    throw new ErroreApi(
      risposta.status === 401 ? m.sessione : (motivo ?? m.richiesta),
      risposta.status,
      dettaglio,
    );
  }
  if (risposta.status === 204) return undefined as T;
  return risposta.json() as Promise<T>;
}

export async function chiama<T>(
  token: string | null,
  percorso: string,
  init: { method?: string; body?: unknown } = {},
): Promise<T> {
  return leggi<T>(
    await fetch(`${API}${percorso}`, {
      method: init.method ?? "GET",
      headers: intestazioni(token),
      body: init.body === undefined ? undefined : JSON.stringify(init.body),
      /* Il cookie anti-abuso della lettura anonima (v6, Fase F, `tarots_anon`) viaggia solo così:
       * frontend e API sono domini diversi in produzione, e senza `include` il browser non lo
       * manderebbe né lo accetterebbe da una risposta. Nessun altro cookie esiste in questo
       * progetto, quindi non c'è nulla da escludere mandandolo su ogni chiamata. */
      credentials: "include",
    }),
  );
}

/* ---- pubblico ---- */

/** Una lettura pubblica qualunque, per percorso (le pagine della v2 la usano con `usePubblico`, che prende i dati
 *  già letti dal server quando il percorso è lo stesso). */
export const leggiApi = <T>(percorso: string) => chiama<T>(null, percorso);

export const elencaStese = (categoria?: Categoria, lang?: string) => {
  const p = new URLSearchParams();
  if (categoria) p.set("categoria", categoria);
  if (lang) p.set("lang", lang);
  const q = p.toString();
  return chiama<Stesa[]>(null, q ? `/spreads?${q}` : "/spreads");
};
export const elencaCarte = (lang?: string) =>
  chiama<Carta[]>(null, lang ? `/cards?lang=${encodeURIComponent(lang)}` : "/cards");
export const leggiCarta = (id: string, lang?: string) =>
  chiama<Carta>(null, lang ? `/cards/${encodeURIComponent(id)}?lang=${encodeURIComponent(lang)}` : `/cards/${encodeURIComponent(id)}`);
export const leggiCondivisa = (token: string) =>
  chiama<LetturaCondivisa>(null, `/shared/${encodeURIComponent(token)}`);
/* `lang` (v8.5): nome e descrizione nella lingua della pagina, con ripiego sull'inglese. */
export const elencaMazzi = (lang?: string) => chiama<Mazzo[]>(null, lang ? `/decks?lang=${lang}` : "/decks");
export const leggiMazzo = (slug: string) => chiama<Mazzo>(null, `/decks/${slug}`);
/* v7, Fase J: gli id dei mazzi che l'utente può già leggere — per proporre nel selettore solo
 * quelli posseduti (più i gratuiti, cioè senza prezzo digitale, già filtrabili lato chiamante). */
export const elencaMieiMazzi = (token: string | null) =>
  chiama<{ deck_ids: number[] }>(token, "/me/decks");

export const leggiDisclaimer = (lang: string) =>
  chiama<{ testo: string }>(null, `/disclaimer?lang=${lang}`);

/* ---- letture ---- */

export interface Apertura {
  id?: string;
  status?: StatoLettura;
  categoria?: Categoria;
  /* La lingua del quesito, ricavata dal server: quella di domande e responso. */
  lang?: string;
  consumo?: string;
  disclaimer?: string;
  stesa?: Stesa;
  saldo?: number;
  crisi?: boolean;
  messaggio?: string;
}

/* L'altra persona di una lettura di compatibilità o di coppia, come la vuole il server. */
export interface PartnerInvio {
  nome: string;
  cognome?: string;
  genere: Genere;
  genere_altro?: string;
  trans: boolean;
  nascita: string;
}

export interface CartaManualeInvio {
  posizione: number;
  cardId: string;
}

export interface OpzioniApertura {
  spreadId: string;
  domanda: string;
  lang: string;
  /* Solo per le letture speciali. */
  partner?: PartnerInvio;
  /* «Ricorda»: il server salva il partner nel profilo. */
  ricordaPartner?: boolean;
  /* "Interpreta i miei tarocchi" (v5): una carta per ogni posizione non calcolata della stesa, già
   * estratta a mano — con questo campo la lettura salta ventaglio/scelta. */
  manualCards?: CartaManualeInvio[];
  /* Lo slug di un mazzo posseduto (v8.5): la lettura lo ricorda per le immagini. Assente: il predefinito. */
  mazzo?: string | null;
  /* Oltre un limite dell'abbonamento (v9, Fase 2b): il consenso dato nel dialogo — un condono o un credito. */
  oltreLimite?: "condono" | "credito";
  /* v9.5: la versione della lettura (prova 90/10). */
  variante?: "classica" | "chat";
}

export const apriLettura = (token: string | null, o: OpzioniApertura) =>
  chiama<Apertura>(token, "/readings", {
    method: "POST",
    body: {
      spread_id: o.spreadId,
      question: o.domanda,
      lang: o.lang,
      ...(o.partner ? { partner: o.partner, ricorda_partner: !!o.ricordaPartner } : {}),
      ...(o.manualCards ? { manual_cards: o.manualCards.map((c) => ({ posizione: c.posizione, card_id: c.cardId })) } : {}),
      ...(o.mazzo ? { deck_id: o.mazzo } : {}),
      ...(o.oltreLimite ? { oltre_limite: o.oltreLimite } : {}),
      /* v9.5: da dove nasce e con quale versione (prova 90/10): per confrontare gli abbandoni. */
      piattaforma: "web",
      ...(o.variante ? { variante: o.variante } : {}),
    },
  });

/* La lettura gratuita per chi non ha un account (v6, Fase F): solo standard, nessun dato di una
 * seconda persona. Usa gli stessi endpoint di sempre con `token=null` da lì in poi — il cookie
 * anti-abuso (`credentials: "include"`, sopra) fa il resto. Un 409 significa "già usata: registrati". */
/* `etaAnni` (GDPR, Fase 1): l'età minima che la persona ha confermato di avere («ho almeno N anni»); senza, il server
 * risponde 403 `eta_da_confermare` con gli anni da chiedere. */
export const apriLetturaAnonima = (
  spreadId: string, domanda: string, lang: string, etaAnni?: number, variante?: "classica" | "chat",
) =>
  chiama<Apertura>(null, "/readings/anonime", {
    method: "POST",
    body: {
      spread_id: spreadId, question: domanda, lang, ...(etaAnni ? { eta_confermata: true, eta_anni: etaAnni } : {}),
      piattaforma: "web", ...(variante ? { variante } : {}),
    },
  });

export interface PassoIntervista {
  completa: boolean;
  domanda?: string;
  ordine?: number;
  riassunto?: string;
  crisi?: boolean;
  messaggio?: string;
  /** v8.5: il minimo di domande è raggiunto, chi consulta può fermarsi qui («No, basta così»). */
  facoltativa?: boolean;
  /** v9.5: risposta salvata senza domanda successiva: chi legge sceglie con i pulsanti. */
  scelta?: boolean;
  /** v9.5: domande già poste dall'oracolo, e minimo e massimo in vigore. */
  poste?: number;
  min_domande?: number;
  max_domande?: number;
}

/* `basta` (v8.5): chiude l'intervista dopo il minimo di domande e passa alle carte. */
/* v9.5: `continua: false` salva la risposta senza chiedere subito la domanda successiva (si sceglie poi con i
 * pulsanti); `altra: true` chiede un'altra domanda. Senza opzioni, come prima (la v1 e le app già installate). */
export const rispondi = (
  token: string | null, id: string, risposta: string | null, basta = false,
  opzioni: { continua?: boolean; altra?: boolean } = {},
) =>
  chiama<PassoIntervista>(token, `/readings/${id}/interview`, {
    method: "POST",
    body: basta ? { basta: true } : {
      ...(risposta ? { risposta } : {}),
      ...(opzioni.continua === false ? { continua: false } : {}),
      ...(opzioni.altra ? { altra: true } : {}),
    },
  });

/* v9.5: «vuoi aggiungere qualcosa?» dopo l'ultima domanda, prima delle carte. Con un segnale di crisi il server
 * ferma la lettura e risponde come l'intervista (`crisi`, `messaggio`). */
export const aggiungiAllIntervista = (token: string | null, id: string, testo: string) =>
  chiama<{ aggiunto?: boolean; crisi?: boolean; messaggio?: string }>(token, `/readings/${id}/addition`, {
    method: "POST",
    body: { testo },
  });

/* `taglio`: dove chi consulta ha cliccato per tagliare il mazzo, da 0 a 1. */
export const apriVentaglio = (token: string | null, id: string, taglio?: number) =>
  chiama<{ slot_count: number; commitment: string; da_scegliere: number; picked_slots: number[] }>(
    token, `/readings/${id}/fan`,
    { method: "POST", body: taglio === undefined ? undefined : { taglio } },
  );

export const scegliCarta = (token: string | null, id: string, slot: number) =>
  chiama<{ posizione: number; slot: number; tutte_scelte: boolean; posizioni_calcolate: number[] }>(
    token, `/readings/${id}/pick`, { method: "POST", body: { slot } },
  );

export const leggiLettura = (token: string | null, id: string) => chiama<Lettura>(token, `/me/readings/${id}`);
export const elencaLetture = (token: string | null) =>
  chiama<{ totale: number; letture: LetturaBreve[] }>(token, "/me/readings");
export const cancellaLettura = (token: string | null, id: string) =>
  chiama<void>(token, `/me/readings/${id}`, { method: "DELETE" });
export const annotaLettura = (token: string | null, id: string, esito: string, nota?: string) =>
  chiama<{ feedback: string }>(token, `/me/readings/${id}/feedback`, { method: "POST", body: { esito, nota } });
/* `testo` assente lascia com'è il testo già scritto; una stringa vuota lo toglie. */
export const condividiLettura = (token: string | null, id: string, attiva: boolean, testo?: string) =>
  chiama<{ share_token: string | null; share_text: string | null }>(token, `/me/readings/${id}/share`, {
    method: "POST",
    body: testo === undefined ? { attiva } : { attiva, testo },
  });

export type CanaleCondivisione = "instagram" | "facebook" | "tiktok" | "x" | "email" | "link" | "nativo";

/* L'immagine composta dal browser (PNG 800×600): il server la ricontrolla e la riscrive
 * in WebP 400×300 molto compresso, e risponde con quel WebP — l'immagine che si
 * mostra in anteprima e che i social riceveranno. */
export async function caricaImmagineCondivisione(token: string | null, id: string, png: Blob): Promise<Blob> {
  const h: Record<string, string> = { "Content-Type": "image/png" };
  if (token) h.Authorization = `Bearer ${token}`;
  const risposta = await fetch(`${API}/me/readings/${id}/share-image`, { method: "PUT", headers: h, body: png });
  if (!risposta.ok) return leggi<Blob>(risposta);
  return risposta.blob();
}

export const registraClicCondivisione = (
  token: string | null, id: string, canale: CanaleCondivisione, visitor: string,
) =>
  chiama<{ contatore: Condivisioni }>(token, `/me/readings/${id}/share-click`, {
    method: "POST", body: { canale, visitor },
  });

/* Chi ha aperto il link: la pagina lo dice dopo qualche secondo. `keepalive`
 * fa partire la richiesta anche se la scheda si chiude subito dopo. */
export const registraVisita = (linkToken: string, visitor: string) =>
  fetch(`${API}/shared/${encodeURIComponent(linkToken)}/visit`, {
    method: "POST", headers: intestazioni(null), body: JSON.stringify({ visitor }), keepalive: true,
  }).then(() => undefined, () => undefined);

export const attribuisciIscrizione = (token: string | null, linkToken: string, visitor: string) =>
  chiama<{ attribuita: boolean; motivo?: string }>(token, "/me/share-signup", {
    method: "POST", body: { token: linkToken, visitor },
  });

/* L'indirizzo dell'immagine di una lettura condivisa: quello che i social leggono. */
export const urlImmagineCondivisa = (linkToken: string) =>
  `${API}/shared/${encodeURIComponent(linkToken)}/image.webp`;

/* ---- lo streaming ---- */

/* `posizione` su token, sostituisci ed errore c'è solo nello svelamento di tutte le carte (`rivelaTutte`): lì un
 * flusso porta i testi di più carte. `fase` (`lettura`: il lettore sta leggendo le carte) e `battito` arrivano mentre
 * la chiamata unica lavora. */
export type EventoRivelazione =
  | { tipo: "carta"; posizione: number; carta: Carta; rovescio: boolean; calcolata: boolean; doppia_valenza: boolean; dignita: Dignita | null }
  | { tipo: "token"; testo: string; posizione?: number }
  | { tipo: "sostituisci"; testo: string; posizione?: number }
  | { tipo: "errore"; messaggio: string; posizione?: number }
  | { tipo: "fase"; fase: string }
  | { tipo: "battito" }
  | { tipo: "fine"; posizione: number; interpretazione: string; ultima: boolean };

export type EventoSintesi =
  | { tipo: "fase"; fase: string; guardia?: string }
  | { tipo: "battito" }
  | { tipo: "token"; testo: string }
  | { tipo: "errore"; messaggio: string }
  | {
      tipo: "fine";
      disclaimer: string;
      guardia: string;
      commitment: string;
      deck_salt: string;
      saldo: number | null;
      /* v6, Fase F: vero per un visitatore anonimo — il "testo" ricevuto è l'anteprima, mai il
       * responso vero, e il client deve mostrare l'invito a registrarsi invece del risultato. */
      anonimo?: boolean;
    };

async function* flusso(
  token: string | null,
  percorso: string,
  segnale?: AbortSignal,
): AsyncGenerator<{ nome: string; dati: Record<string, unknown> }> {
  const risposta = await fetch(`${API}${percorso}`, {
    method: "POST",
    headers: intestazioni(token),
    signal: segnale,
    credentials: "include", // il cookie tarots_anon (v6, Fase F): vedi la nota in chiama()
  });
  if (!risposta.ok || !risposta.body) {
    await leggi(risposta);
    return;
  }

  const lettore = risposta.body.getReader();
  const decodificatore = new TextDecoder();
  let avanzo = "";
  while (true) {
    const { done, value } = await lettore.read();
    if (done) break;
    /* `stream: true` perché un carattere multibyte può essere spezzato fra due
     * pacchetti: senza, una lettera accentata a cavallo del confine diventa
     * il carattere di sostituzione. Con l'italiano succede spesso. */
    avanzo += decodificatore.decode(value, { stream: true });
    const blocchi = avanzo.split("\n\n");
    avanzo = blocchi.pop() ?? "";
    for (const blocco of blocchi) {
      let nome = "";
      let dati = "";
      for (const riga of blocco.split("\n")) {
        if (riga.startsWith("event:")) nome = riga.slice(6).trim();
        else if (riga.startsWith("data:")) dati += riga.slice(5).trim();
      }
      if (nome) yield { nome, dati: dati ? JSON.parse(dati) : {} };
    }
  }
}

export async function* rivela(
  token: string | null, id: string, posizione: number, segnale?: AbortSignal,
): AsyncGenerator<EventoRivelazione> {
  for await (const { nome, dati } of flusso(token, `/readings/${id}/reveal/${posizione}`, segnale)) {
    yield { tipo: nome, ...dati } as EventoRivelazione;
  }
}

/** Tutte le carte ancora coperte, interpretate con una chiamata sola: prima un `carta` per ognuna, poi `fase`
 * `lettura` e i battiti, poi per ogni posizione il testo (`token` con `posizione`) e la sua `fine`. */
export async function* rivelaTutte(
  token: string | null, id: string, segnale?: AbortSignal,
): AsyncGenerator<EventoRivelazione> {
  for await (const { nome, dati } of flusso(token, `/readings/${id}/reveal-all`, segnale)) {
    yield { tipo: nome, ...dati } as EventoRivelazione;
  }
}

export async function* sintesi(
  token: string | null, id: string, segnale?: AbortSignal,
): AsyncGenerator<EventoSintesi> {
  for await (const { nome, dati } of flusso(token, `/readings/${id}/synthesis`, segnale)) {
    yield { tipo: nome, ...dati } as EventoSintesi;
  }
}

/* ---- cassa e profilo ---- */

export const elencaPiani = (lang?: string) => chiama<Piano[]>(null, lang ? `/plans?lang=${lang}` : "/plans");
export const leggiConto = (token: string | null, lang?: string) =>
  chiama<Conto>(token, lang ? `/me/billing?lang=${lang}` : "/me/billing");
export const leggiMovimenti = (token: string | null) =>
  chiama<{ saldo: number; movimenti: Movimento[] }>(token, "/me/credits");
export const apriPagamento = (token: string | null, piano: string, annuale: boolean, ritorno?: string, coupon?: string) =>
  chiama<{ checkout_id: string; url: string; importo: number; sconto?: number; valuta: string; gratis?: boolean }>(
    token, "/me/checkout", { method: "POST", body: { piano, annuale, ritorno, coupon } },
  );

/** Quanto costa un'offerta con un codice sconto. Un codice che non vale risponde 422 con `dettaglio.motivo`. */
export interface AnteprimaCoupon {
  codice: string;
  tipo: string;
  listino: number;
  sconto: number;
  importo: number;
  valuta: string;
  gratis: boolean;
}
export const anteprimaCoupon = (token: string | null, codice: string, piano: string, annuale = false) =>
  chiama<AnteprimaCoupon>(token, "/me/coupon/anteprima", { method: "POST", body: { codice, piano, annuale } });

/** Un codice regalo: i crediti arrivano subito. */
export const riscattaCodice = (token: string | null, codice: string) =>
  chiama<{ crediti: number; saldo: number }>(token, "/me/coupon/riscatta", { method: "POST", body: { codice } });

/** Il motivo stabile per cui un codice non vale (`coupon_scaduto`, …), se l'errore ne porta uno. */
export function motivoCodice(e: unknown): string | null {
  if (e instanceof ErroreApi) {
    const d = e.dettaglio as { motivo?: unknown } | undefined;
    if (d && typeof d.motivo === "string") return d.motivo;
  }
  return null;
}
export const statoPagamento = (token: string | null, id: string) =>
  chiama<{
    checkout_id: string; stato: string; piano: string; nome: string; tipo: string;
    /* v9, Fase 2b: una prova, un cambio di piano, e perché una prova non è partita (`carta_gia_usata`…). */
    prova?: boolean; cambio?: boolean; esito?: string | null;
  }>(token, `/me/checkout/${id}`);
export const abbonaGratis = (token: string | null, piano: string) =>
  chiama<unknown>(token, "/me/subscription", { method: "POST", body: { piano } });
export const disdici = (token: string | null) =>
  chiama<unknown>(token, "/me/subscription/cancel", { method: "POST" });

/* ---- negozio mazzi (v5, Fase B3) ---- */

/** Gli id dei mazzi che l'utente può già leggere (predefiniti + sblocchi acquistati). */
export const mieiMazzi = (token: string | null) =>
  chiama<{ deck_ids: number[] }>(token, "/me/decks");

/* `url` nullo e `pagamento_attivo` falso: i pagamenti non sono ancora attivi, l'ordine resta registrato in attesa. */
export const apriOrdine = (token: string | null, voci: VoceCarrelloInvio[], ritorno?: string, indirizzoId?: string) =>
  chiama<{ url: string | null; pagamento_attivo?: boolean } & Ordine>(
    token, "/orders", { method: "POST", body: { voci, ritorno, indirizzo_id: indirizzoId } },
  );

/** Il prezzo di un carrello secondo il server (righe, sconto per mazzo, sconto a scaglioni, totale): anche senza
 *  account, nulla viene scritto. Un formato che il mazzo non offre risponde 422. */
export interface Preventivo {
  righe: { deck_id: number; tipo: TipoVoceOrdine; quantita: number; prezzo_pieno_unitario: number; prezzo_finale_unitario: number }[];
  subtotale: number;
  scaglione_percentuale: number;
  sconto_scaglioni: number;
  totale: number;
  richiede_indirizzo: boolean;
  pagamento_attivo: boolean;
}
export const preventivoCarrello = (voci: VoceCarrelloInvio[]) =>
  chiama<Preventivo>(null, "/shop/quote", { method: "POST", body: { voci } });

export const elencaOrdini = (token: string | null) =>
  chiama<{ ordini: Ordine[] }>(token, "/me/orders");

export const leggiOrdine = (token: string | null, id: string) =>
  chiama<Ordine>(token, `/me/orders/${id}`);

/** Il PDF "Stampa i tuoi Tarocchi" gratuito di un mazzo (solo se il suo `prezzo_stampa` è zero): un
 * indirizzo diretto, per un semplice `<a href>` — nessuna autenticazione richiesta. */
export const urlPdfGratuito = (slug: string) => `${API}/decks/${slug}/pdf`;

/** Lo stesso PDF, ma per una riga "pdf" di un ordine già pagato: richiede il token, quindi un
 * `<a href>` non basta — il chiamante crea un object URL dal Blob per avviare il download. */
export async function scaricaPdfOrdine(token: string | null, ordineId: string, deckId: number): Promise<Blob> {
  const risposta = await fetch(`${API}/me/orders/${ordineId}/pdf/${deckId}`, { headers: intestazioni(token) });
  if (!risposta.ok) return leggi<Blob>(risposta);
  return risposta.blob();
}

export const leggiProfilo = (token: string | null) => chiama<Profilo>(token, "/me/profile");
export const aggiornaProfilo = (
  token: string | null,
  dati: {
    birth_date?: string | null;
    locale?: string;
    gender?: Genere;
    gender_custom?: string | null;
    is_trans?: boolean;
    promemoria_2fa?: boolean;
    nome_pubblico?: string;
    registro_linguistico?: "esoterico" | "quotidiano";
    /* `0` azzera la scelta e torna al predefinito globale. */
    mazzo_predefinito_id?: number;
    /* Vuoto = cancellato. */
    nome?: string;
    cognome?: string;
    /* La posizione corretta a mano (paese ISO a due lettere); entrambi vuoti = di nuovo automatica. */
    posizione_paese?: string;
    posizione_citta?: string;
    importa_social?: boolean;
    rileva_posizione?: boolean;
  },
) => chiama<Profilo>(token, "/me/profile", { method: "PATCH", body: dati });
/* Dopo ogni accesso: i campi vuoti della scheda dai social collegati, e la posizione attuale. Idempotente. */
export const importaProfiloSocial = (token: string | null) =>
  chiama<EsitoProfiloSocial>(token, "/me/profilo-social", { method: "POST" });
/* La domanda «l'account che c'era con la tua email era tuo?», se c'è. */
export const unioneDaConfermare = (token: string | null) =>
  chiama<{ unione: UnioneDaConfermare | null }>(token, "/me/unione");
/* La risposta, con la password facoltativa (un rifiuto della politica torna come 422 `{password: chiave}`). */
export const rispondiUnione = (token: string | null, scelta: "mia" | "non_mia", password?: string) =>
  chiama<{ scelta: string; password: boolean; nuovo_account: boolean }>(token, "/me/unione", {
    method: "POST", body: { scelta, ...(password ? { password } : {}) },
  });
/* Cancella i dati presi dai social (non quelli corretti a mano) e la posizione, e spegne importazione e rilevamento. */
export const dimenticaDatiSocial = (token: string | null) =>
  chiama<void>(token, "/me/dati-social", { method: "DELETE" });
/* L'avatar: l'immagine come corpo della richiesta; il server la ritaglia e la riscrive in WebP. */
export async function caricaAvatar(token: string | null, file: File): Promise<{ avatar: string }> {
  const h: Record<string, string> = { "Content-Type": file.type || "image/png" };
  if (token) h.Authorization = `Bearer ${token}`;
  return leggi<{ avatar: string }>(await fetch(`${API}/me/avatar`, { method: "PUT", headers: h, body: file }));
}
export const togliAvatar = (token: string | null) => chiama<void>(token, "/me/avatar", { method: "DELETE" });
export const cancellaPartner = (token: string | null) => chiama<void>(token, "/me/partner", { method: "DELETE" });

/* ---- indirizzi di spedizione (v5, Fase B5) ---- */

export interface Indirizzo {
  id: string;
  nome: string;
  via: string;
  citta: string;
  cap: string;
  provincia: string | null;
  paese: string;
  telefono: string | null;
  predefinito: boolean;
}

export interface IndirizzoInvio {
  nome: string;
  via: string;
  citta: string;
  cap: string;
  provincia?: string;
  paese: string;
  telefono?: string;
  predefinito?: boolean;
}

export const elencaIndirizzi = (token: string | null) =>
  chiama<{ indirizzi: Indirizzo[] }>(token, "/me/addresses");
export const creaIndirizzo = (token: string | null, dati: IndirizzoInvio) =>
  chiama<Indirizzo>(token, "/me/addresses", { method: "POST", body: dati });
export const modificaIndirizzo = (token: string | null, id: string, dati: Partial<IndirizzoInvio>) =>
  chiama<Indirizzo>(token, `/me/addresses/${id}`, { method: "PATCH", body: dati });
export const eliminaIndirizzo = (token: string | null, id: string) =>
  chiama<void>(token, `/me/addresses/${id}`, { method: "DELETE" });
/* ---- chat proattiva (v6, Fase E) ---- */

export interface PropostaLettura {
  argomento: string;
  categoria: Categoria;
}

export interface TurnoChat {
  id: string;
  ruolo: "ai" | "utente";
  testo: string;
  proposta: PropostaLettura | null;
  creato: string | null;
}

export const impostazioniChat = (token: string | null) =>
  chiama<{ proattiva_minuti_inattivita: number; proattiva_max_per_visita?: number }>(token, "/impostazioni-chat");
export const storicoChat = (token: string | null) =>
  chiama<{ turni: TurnoChat[] }>(token, "/chat/proattiva");
export const avviaChat = (token: string | null) =>
  chiama<{ turno: TurnoChat | null }>(token, "/chat/proattiva/avvio", { method: "POST" });
export const inviaMessaggioChat = (token: string | null, testo: string) =>
  chiama<{ turno: TurnoChat | null }>(token, "/chat/proattiva/messaggio", { method: "POST", body: { testo } });

/* ---- memoria (v6, Fase D) ---- */

export type TipoMemoria = "stabile" | "variabile";

/* Le categorie dello stato sintetico della memoria: un fatto duraturo, una domanda fatta, una situazione del momento. */
export type CategoriaMemoria = "stabile" | "tema" | "volatile";

export interface Memoria {
  id: string;
  contenuto: string;
  tipo: TipoMemoria;
  campo_attinenza: string;
  fonte: string;
  aggiornata: string | null;
  categoria?: CategoriaMemoria;
  /* Il giorno in cui si dimentica da sola se nessuna lettura la conferma; `null`: resta finché non la cancelli. */
  scade?: string | null;
}

export const elencaMemorie = (token: string | null) =>
  chiama<{ memorie: Memoria[] }>(token, "/me/memories");
export const modificaMemoria = (token: string | null, id: string, dati: { contenuto?: string; campo_attinenza?: string }) =>
  chiama<Memoria>(token, `/me/memories/${id}`, { method: "PATCH", body: dati });
export const eliminaMemoria = (token: string | null, id: string) =>
  chiama<void>(token, `/me/memories/${id}`, { method: "DELETE" });
export const eliminaMemorieSelezionate = (token: string | null, ids: string[]) =>
  chiama<void>(token, "/me/memories", { method: "DELETE", body: { ids } });
export const eliminaTutteLeMemorie = (token: string | null) =>
  chiama<void>(token, "/me/memories", { method: "DELETE", body: { tutte: true } });

export const riscattaInvito = (token: string | null, codice: string) =>
  chiama<{ crediti: number; saldo: number }>(token, "/me/referral", { method: "POST", body: { codice } });
/** La carta del giorno per tutti (`GET /daily-card/today`): senza account, uguale per chiunque nello stesso giorno. */
export interface CartaOggi {
  giorno: string;
  carta: Carta;
  testo: string;
}

export const cartaDiOggi = (lingua: string) => chiama<CartaOggi>(null, `/daily-card/today?lang=${lingua}`);
export const cartaDelGiorno = (token: string | null) => chiama<CartaDelGiorno>(token, "/me/daily-card");

/** I numeri del regalo d'iscrizione e del referral: pubblici, nessun dato sensibile — servono a mostrare cifre
 * vere nella home e nel profilo, invece di un testo fisso che l'amministrazione potrebbe aver cambiato. */
export interface ImpostazioniPubbliche {
  crediti_iscrizione: number;
  crediti_invito: number;
  commissione_referral_percentuale: number;
  /** v9.5: minimo e massimo delle domande dell'intervista (quali scelte mostrare alla riapertura). */
  intervista_min_domande?: number;
  intervista_max_domande?: number;
}

export const impostazioniPubbliche = () => chiama<ImpostazioniPubbliche>(null, "/impostazioni-pubbliche");

/* ---- consenso GDPR (v7, Fase G) ---- */

/* GDPR, Fase 1: le categorie granulari. `cookie` resta solo per il vecchio sito sotto /old (vale per statistiche e
 * Google Analytics insieme); `condivisione_dati_partner` non si sceglie più (non c'è nessuna condivisione). */
export type TipoConsenso =
  | "statistiche" | "google_analytics" | "pubblicita" | "testi_statistiche" | "dati_particolari" | "marketing" | "cookie";
export type ValoreConsenso = "accettato" | "rifiutato";

/* La versione del testo informativo mostrato: cambiarla in futuro (nuova informativa) fa
 * ricomparire il banner anche a chi aveva già scelto sulla versione precedente. */
export const VERSIONE_INFORMATIVA = "v1";

export const leggiConsenso = (token: string | null) =>
  chiama<Record<TipoConsenso, ValoreConsenso | null>>(token, "/consenso");

/* `versione`: il testo che questa persona ha davvero visto. La v2 del sito passa la sua (v8.6: l'informativa che
 * nomina Google Analytics, `VERSIONE_INFORMATIVA_V2` in `v2/componenti/contatore-google.tsx`); la v1 resta sulla sua. */
export const registraConsenso = (
  token: string | null,
  tipo: TipoConsenso,
  valore: ValoreConsenso,
  versione: string = VERSIONE_INFORMATIVA,
) =>
  chiama<{ esito: string }>(token, "/consenso", {
    method: "POST",
    body: { tipo, valore, versione_informativa: versione },
  });

/* v8.6: se questa persona ha acconsentito a Google Analytics (un «accettato» sull'informativa che lo nomina), e se
 * aveva accettato un testo precedente e va richiesto. */
export const statoConsensoGoogle = (token: string | null) =>
  chiama<{ attivo: boolean; da_rinnovare: boolean }>(token, "/consenso-google");

/* ---- statistiche di utilizzo (v8): opposizione al legame visite-account ---- */

export const leggiPreferenzaStatistiche = (token: string | null) =>
  chiama<{ opposizione: boolean }>(token, "/me/statistiche");

export const impostaPreferenzaStatistiche = (token: string | null, opposizione: boolean) =>
  chiama<{ opposizione: boolean }>(token, "/me/statistiche", { method: "PUT", body: { opposizione } });

/* ---- vota il prossimo mazzo (v7, Fase K) ---- */

export interface CampioneVoto {
  etichetta: string | null;
  /* Percorsi relativi dell'API (`urlMedia`): la grande per l'ingrandimento, la miniatura per l'elenco. */
  url: string | null;
  mini?: string | null;
}

export interface CandidatoVoto {
  id: string;
  nome: string;
  descrizione: string | null;
  campioni: CampioneVoto[];
  /* `null` finché l'utente non ha votato in questa tornata: le percentuali non si mostrano prima,
   * per non influenzare il voto. */
  percentuale: number | null;
}

export interface VincitorePrecedente {
  nome: string;
  percentuale: number;
}

export interface StatoVoto {
  tornata: { id: string } | null;
  mio_voto: string | null;
  candidati: CandidatoVoto[];
  vincitori_precedenti: VincitorePrecedente[] | null;
}

export const statoVotoMazzi = (token: string | null) => chiama<StatoVoto>(token, "/voto/mazzi");
export const votaMazzo = (token: string | null, candidateId: string) =>
  chiama<{ esito: string }>(token, `/voto/mazzi/${candidateId}`, { method: "POST" });

/* «Tornate elettorali»: il riepilogo per la home page, pubblico (nessun account richiesto) — ogni
 * candidato dell'ultima tornata chiusa, non solo il vincitore, per il riquadro con le miniature
 * ingrandibili in home. */
export interface CandidatoRisultato {
  nome: string;
  percentuale: number;
  campioni: CampioneVoto[];
}

export interface RisultatoRecente {
  chiusa_il: string | null;
  candidati: CandidatoRisultato[];
}

export interface VotoHome {
  voto_aperto: boolean;
  risultato_recente: RisultatoRecente | null;
}

export const votoHome = () => chiama<VotoHome>(null, "/voto/home");

/** "Suggerisci tema mazzo": un iscritto propone liberamente un tema in testo libero. */
export const suggerisciTemaMazzo = (token: string | null, testo: string) =>
  chiama<{ esito: string }>(token, "/voto/suggerimenti", { method: "POST", body: { testo } });

export function euro(centesimi: number, valuta = "EUR", locale = "it-IT"): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency: valuta }).format(centesimi / 100);
}
