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
export type Categoria = "standard" | "compatibilita" | "coppia";
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
  /* Solo nelle stese speciali. */
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
  } | null;
  diritti: { piano: string; nome: string; limiti: Record<string, number>; predefiniti: boolean };
  saldo: number;
  uso: Record<string, { usati: number; limite: number | null; restanti: number | null }>;
  limiti_attivi: boolean;
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
  tipo: TipoVoceOrdine;
  deck_id: number;
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
  birth_date: string | null;
  gender: Genere | null;
  gender_custom: string | null;
  is_trans: boolean;
  /* Il promemoria della verifica in due passaggi all'accesso; `false` = «non mostrare più». */
  promemoria_2fa: boolean;
  /* Come ti presenti nei commenti del blog (`null` = il primo nome) e il nome che si vede davvero. */
  nome_pubblico: string | null;
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
    const t = dizionario(linguaMessaggi);
    throw new ErroreApi(
      risposta.status === 401 ? t.err_sessione : (motivo ?? t.err_richiesta),
      risposta.status,
      dettaglio,
    );
  }
  if (risposta.status === 204) return undefined as T;
  return risposta.json() as Promise<T>;
}

async function chiama<T>(
  token: string | null,
  percorso: string,
  init: { method?: string; body?: unknown } = {},
): Promise<T> {
  return leggi<T>(
    await fetch(`${API}${percorso}`, {
      method: init.method ?? "GET",
      headers: intestazioni(token),
      body: init.body === undefined ? undefined : JSON.stringify(init.body),
    }),
  );
}

/* ---- pubblico ---- */

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
export const elencaMazzi = () => chiama<Mazzo[]>(null, "/decks");
export const leggiMazzo = (slug: string) => chiama<Mazzo>(null, `/decks/${slug}`);

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
    },
  });

export interface PassoIntervista {
  completa: boolean;
  domanda?: string;
  ordine?: number;
  riassunto?: string;
  crisi?: boolean;
  messaggio?: string;
}

export const rispondi = (token: string | null, id: string, risposta: string | null) =>
  chiama<PassoIntervista>(token, `/readings/${id}/interview`, {
    method: "POST",
    body: risposta ? { risposta } : {},
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

export type EventoRivelazione =
  | { tipo: "carta"; posizione: number; carta: Carta; rovescio: boolean; calcolata: boolean; doppia_valenza: boolean; dignita: Dignita | null }
  | { tipo: "token"; testo: string }
  | { tipo: "sostituisci"; testo: string }
  | { tipo: "errore"; messaggio: string }
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
      saldo: number;
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

export async function* sintesi(
  token: string | null, id: string, segnale?: AbortSignal,
): AsyncGenerator<EventoSintesi> {
  for await (const { nome, dati } of flusso(token, `/readings/${id}/synthesis`, segnale)) {
    yield { tipo: nome, ...dati } as EventoSintesi;
  }
}

/* ---- cassa e profilo ---- */

export const elencaPiani = () => chiama<Piano[]>(null, "/plans");
export const leggiConto = (token: string | null) => chiama<Conto>(token, "/me/billing");
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
  chiama<{ checkout_id: string; stato: string; piano: string; nome: string; tipo: string }>(token, `/me/checkout/${id}`);
export const abbonaGratis = (token: string | null, piano: string) =>
  chiama<unknown>(token, "/me/subscription", { method: "POST", body: { piano } });
export const disdici = (token: string | null) =>
  chiama<unknown>(token, "/me/subscription/cancel", { method: "POST" });

/* ---- negozio mazzi (v5, Fase B3) ---- */

/** Gli id dei mazzi che l'utente può già leggere (predefiniti + sblocchi acquistati). */
export const mieiMazzi = (token: string | null) =>
  chiama<{ deck_ids: number[] }>(token, "/me/decks");

export const apriOrdine = (token: string | null, voci: VoceCarrelloInvio[], ritorno?: string) =>
  chiama<{ url: string } & Ordine>(token, "/orders", { method: "POST", body: { voci, ritorno } });

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
  },
) => chiama<Profilo>(token, "/me/profile", { method: "PATCH", body: dati });
/* L'avatar: l'immagine come corpo della richiesta; il server la ritaglia e la riscrive in WebP. */
export async function caricaAvatar(token: string | null, file: File): Promise<{ avatar: string }> {
  const h: Record<string, string> = { "Content-Type": file.type || "image/png" };
  if (token) h.Authorization = `Bearer ${token}`;
  return leggi<{ avatar: string }>(await fetch(`${API}/me/avatar`, { method: "PUT", headers: h, body: file }));
}
export const togliAvatar = (token: string | null) => chiama<void>(token, "/me/avatar", { method: "DELETE" });
export const cancellaPartner = (token: string | null) => chiama<void>(token, "/me/partner", { method: "DELETE" });
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
}

export const impostazioniPubbliche = () => chiama<ImpostazioniPubbliche>(null, "/impostazioni-pubbliche");

export function euro(centesimi: number, valuta = "EUR", locale = "it-IT"): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency: valuta }).format(centesimi / 100);
}
