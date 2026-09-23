/* Il client dell'API.
 *
 * Lo schema viene da Personalities: `leggi()` traduce gli errori nel motivo
 * che il server manda, e lo streaming si legge dal corpo di `fetch` invece
 * che con `EventSource`, che non porta intestazioni — quindi non porta il
 * token — e non fa POST.
 */

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";

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

export interface Posizione {
  n: number;
  nome: string;
  nome_en: string;
  significato: string;
  domanda: string;
  x: number;
  y: number;
  rotazione: number;
  calcolata: boolean;
}

export interface Stesa {
  id: string;
  nome: string;
  nome_en: string;
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

export interface Lettura {
  id: string;
  spread_id: string;
  stesa: string;
  question: string;
  status: StatoLettura;
  lang: string;
  consumo: string;
  created_at: string;
  completed_at: string | null;
  feedback: "si" | "in_parte" | "no" | null;
  shared: boolean;
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
  feedback_note: string | null;
  disclaimer: string;
  dignita: Record<string, Dignita>;
  stesa_dati: Stesa;
}

export interface LetturaBreve {
  id: string;
  spread_id: string;
  stesa: string;
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

export interface Profilo {
  id: number;
  email: string | null;
  display_name: string | null;
  locale: string;
  birth_date: string | null;
  referral_code: string | null;
  invitato: boolean;
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

export interface LetturaCondivisa {
  question: string;
  stesa: Stesa | null;
  cards: CartaPosata[];
  synthesis: string | null;
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
    throw new ErroreApi(
      risposta.status === 401 ? "La sessione è scaduta." : (motivo ?? "Richiesta non riuscita."),
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

export const elencaStese = () => chiama<Stesa[]>(null, "/spreads");
export const elencaCarte = () => chiama<Carta[]>(null, "/cards");
export const leggiCarta = (id: string) => chiama<Carta>(null, `/cards/${encodeURIComponent(id)}`);
export const leggiCondivisa = (token: string) =>
  chiama<LetturaCondivisa>(null, `/shared/${encodeURIComponent(token)}`);
export const leggiDisclaimer = (lang: string) =>
  chiama<{ testo: string }>(null, `/disclaimer?lang=${lang}`);

/* ---- letture ---- */

export interface Apertura {
  id?: string;
  status?: StatoLettura;
  consumo?: string;
  disclaimer?: string;
  stesa?: Stesa;
  saldo?: number;
  crisi?: boolean;
  messaggio?: string;
}

export const apriLettura = (token: string | null, spreadId: string, domanda: string, lang: string) =>
  chiama<Apertura>(token, "/readings", { method: "POST", body: { spread_id: spreadId, question: domanda, lang } });

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

export const apriVentaglio = (token: string | null, id: string) =>
  chiama<{ slot_count: number; commitment: string; da_scegliere: number; picked_slots: number[] }>(
    token, `/readings/${id}/fan`, { method: "POST" },
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
export const condividiLettura = (token: string | null, id: string, attiva: boolean) =>
  chiama<{ share_token: string | null }>(token, `/me/readings/${id}/share`, { method: "POST", body: { attiva } });

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
export const apriPagamento = (token: string | null, piano: string, annuale: boolean, ritorno?: string) =>
  chiama<{ checkout_id: string; url: string; importo: number; valuta: string }>(token, "/me/checkout", {
    method: "POST",
    body: { piano, annuale, ritorno },
  });
export const statoPagamento = (token: string | null, id: string) =>
  chiama<{ checkout_id: string; stato: string; piano: string; nome: string; tipo: string }>(token, `/me/checkout/${id}`);
export const abbonaGratis = (token: string | null, piano: string) =>
  chiama<unknown>(token, "/me/subscription", { method: "POST", body: { piano } });
export const disdici = (token: string | null) =>
  chiama<unknown>(token, "/me/subscription/cancel", { method: "POST" });

export const leggiProfilo = (token: string | null) => chiama<Profilo>(token, "/me/profile");
export const aggiornaProfilo = (token: string | null, dati: { birth_date?: string | null; locale?: string }) =>
  chiama<Profilo>(token, "/me/profile", { method: "PATCH", body: dati });
export const riscattaInvito = (token: string | null, codice: string) =>
  chiama<{ crediti: number; saldo: number }>(token, "/me/referral", { method: "POST", body: { codice } });
export const cartaDelGiorno = (token: string | null) => chiama<CartaDelGiorno>(token, "/me/daily-card");

export function euro(centesimi: number, valuta = "EUR"): string {
  return new Intl.NumberFormat("it-IT", { style: "currency", currency: valuta }).format(centesimi / 100);
}
