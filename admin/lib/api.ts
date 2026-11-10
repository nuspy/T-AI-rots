/* Il client della console.
 *
 * Tutte le rotte stanno sotto `/admin` e pretendono il ruolo: un 403 qui non
 * è un guasto da nascondere ma un'informazione — significa che il token
 * dell'utente non porta `admin`, e va detto invece di mostrare una pagina
 * vuota che sembra un errore di caricamento.
 *
 * Il token vuoto vuol dire «autenticazione spenta»: la richiesta parte senza
 * `Authorization`, e il backend di sviluppo la attribuisce al suo utente
 * amministratore. Un `Bearer ` senza niente dopo, invece, un backend vero lo
 * rifiuterebbe come token malformato — per questo l'intestazione manca del
 * tutto invece di restare vuota.
 */

export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";

export class ErroreApi extends Error {
  constructor(
    message: string,
    readonly stato: number,
    readonly dettaglio?: string,
  ) {
    super(message);
  }
}

function intestazioni(token: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function chiamata<T>(
  token: string,
  percorso: string,
  opzioni: RequestInit = {},
): Promise<T> {
  return leggi<T>(
    await fetch(`${API}${percorso}`, {
      ...opzioni,
      headers: {
        ...intestazioni(token),
        "Content-Type": "application/json",
        ...(opzioni.headers ?? {}),
      },
    }),
  );
}

/* FastAPI risponde ai 422 con un elenco di errori per campo, non con una
 * frase: se ne prende il primo messaggio, che è quello che serve a chi ha
 * sbagliato il modulo. */
function spiegazione(corpo: unknown): string | undefined {
  const detail = (corpo as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length) {
    const primo = detail[0] as { msg?: string; loc?: unknown[] };
    const campo = Array.isArray(primo.loc) ? primo.loc[primo.loc.length - 1] : undefined;
    return primo.msg ? (campo ? `${String(campo)}: ${primo.msg}` : primo.msg) : undefined;
  }
  return undefined;
}

async function leggi<T>(risposta: Response): Promise<T> {
  if (!risposta.ok) {
    await errore(risposta);
  }

  if (risposta.status === 204) return undefined as T;
  return risposta.json() as Promise<T>;
}

async function errore(risposta: Response): Promise<never> {
  let dettaglio: string | undefined;
  try {
    dettaglio = spiegazione(await risposta.json());
  } catch {
    /* il corpo non era JSON: il codice di stato basta */
  }
  throw new ErroreApi(
    /* Il 403 generico è il ruolo che manca; quando il servizio spiega un
     * rifiuto più preciso, vale la sua spiegazione. */
    risposta.status === 403 && !dettaglio
      ? "Il tuo account non ha il ruolo di amministratore."
      : risposta.status === 401
        ? "La sessione è scaduta."
        : (dettaglio ?? "Richiesta non riuscita."),
    risposta.status,
    dettaglio,
  );
}

export function interrogazione(parametri: Record<string, string | number | undefined>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(parametri)) {
    if (v !== undefined && v !== "") q.set(k, String(v));
  }
  const testo = q.toString();
  return testo ? `?${testo}` : "";
}

/* ---- forme ---- */

export interface Conteggi {
  letture: number;
  completate: number;
  utenti_attivi: number;
  nuovi_utenti: number;
  crediti_consumati: number;
  crediti_venduti: number;
  /** Centesimi, come ogni importo che arriva dal backend. */
  ricavi: number;
  guardia_interventi: number;
  crisi: number;
}

export interface Statistiche {
  giorni: number;
  attuale: Conteggi;
  precedente: Conteggi;
  serie: { giorno: string; letture: number }[];
  per_stesa: { stesa: string; letture: number }[];
  carte: { carta: string; uscite: number }[];
  feedback: Partial<Record<"si" | "in_parte" | "no", number>>;
  consumo: Partial<Record<"credito" | "quota" | "omaggio", number>>;
  abbonamenti: Record<string, number>;
}

export interface Utente {
  id: number;
  email: string | null;
  display_name: string | null;
  locale: string | null;
  attivo: boolean;
  creato: string | null;
  referral_code: string | null;
  invitato_da: number | null;
  saldo: number;
  /** Lo slug del piano in corso, o `null` per chi non ne ha. */
  piano: string | null;
}

export interface Movimento {
  /** L'id della riga del registro (v9): serve allo storno a mano. */
  id: number | null;
  delta: number;
  reason: string;
  quando: string;
  note: string | null;
  reading_id: string | null;
  /** Da dove arriva (web, android, ios, console, sistema) e chi ha incassato (stripe, google_play, app_store, mock, interno). */
  canale?: string;
  provider?: string;
  /** L'incasso presso il fornitore (PaymentIntent, fattura, transazione dello store). */
  riferimento?: string | null;
  scade?: string | null;
}

export type StatoPagamento = "aperto" | "pagato" | "annullato" | "scaduto";

export interface Pagamento {
  id: string;
  user_id: number;
  piano: string;
  nome: string;
  tipo: "abbonamento" | "pacchetto";
  annuale: boolean;
  stato: StatoPagamento;
  fornitore: string;
  /** Centesimi. */
  importo: number;
  valuta: string;
  /** v9, Fase 4: un acquisto di prova degli store (tester, App Review): accredita ma non entra nei ricavi. */
  sandbox?: boolean;
  creato: string | null;
  completato: string | null;
}

/** v9, Fase 4: un acquisto fatto in un'app (Google Play o App Store), come l'ha confermato lo store. */
export interface AcquistoStore {
  id: number;
  piattaforma: "android" | "ios";
  store: string;
  product_id: string;
  tipo: "consumabile" | "abbonamento";
  transazione: string;
  transazione_originale: string | null;
  ordine: string | null;
  stato: "in_attesa" | "accreditato" | "rimborsato" | "revocato" | "scaduto";
  ambiente: "sandbox" | "production";
  confermato: boolean;
  prova: boolean;
  /** Pagato anche se l'utente ha già un altro abbonamento: va detto all'utente di disdirlo nello store. */
  doppio: boolean;
  /** Centesimi nella valuta dello store, quando lo store lo dice (Apple sì, Google no). */
  importo: number | null;
  valuta: string | null;
  paese: string | null;
  acquistato_il: string | null;
  scade_il: string | null;
  revocato_il: string | null;
  creato_il: string | null;
}

export interface UtenteDettaglio extends Omit<Utente, "piano"> {
  abbonamento: {
    piano: string;
    nome: string;
    stato: string;
    fine: string;
  } | null;
  letture: Record<string, number>;
  movimenti: Movimento[];
  pagamenti: Pagamento[];
  /** v9, Fase 4: gli acquisti nelle app. */
  acquisti_store?: AcquistoStore[];
  /** La scheda anagrafica, con la provenienza dei campi presi dai social e la posizione attuale. */
  anagrafica?: {
    nome: string | null;
    cognome: string | null;
    nascita: string | null;
    genere: string | null;
    genere_altro: string | null;
    posizione: { paese: string | null; citta: string | null; fonte: string | null; il: string | null } | null;
    dati_social: {
      campi?: Record<string, { da: string; il: string }>;
      ultimo?: { il: string; provider: string[]; compilati: string[] };
    };
    importa_social: boolean;
    rileva_posizione: boolean;
  };
}

export interface Piano {
  id: number;
  slug: string;
  nome: string;
  tipo: "abbonamento" | "pacchetto";
  descrizione: string | null;
  /** Le traduzioni (v8.5): lingua → testo. */
  nomi?: Record<string, string>;
  descrizioni?: Record<string, string>;
  /** Centesimi. */
  prezzo_mensile: number | null;
  /** Centesimi. */
  prezzo_annuale: number | null;
  crediti: number | null;
  limiti: { letture_al_giorno?: number } & Record<string, unknown>;
  attivo: boolean;
  rango: number;
  abbonati: number;
  /** Abbonamenti (di ogni stato) più pagamenti: a zero il piano si può eliminare, altrimenti solo disattivare. */
  usi: number;
}

/** I campi che il backend accetta: nomi inglesi, importi in centesimi. */
export interface ModificaPiano {
  name?: string;
  description?: string;
  price_monthly?: number;
  price_yearly?: number;
  credits_per_period?: number;
  /** −1 significa «illimitate». */
  letture_al_giorno?: number;
  /** I limiti della Fase 2b (v9): −1 significa «nessun limite». */
  letture_alla_settimana?: number;
  letture_al_mese?: number;
  letture_totali?: number;
  active?: boolean;
  /** L'ordine di presentazione: più basso, più in alto. */
  rank?: number;
  /** Sostituiscono per intero le traduzioni; una lingua vuota si toglie. */
  nomi?: Record<string, string>;
  descrizioni?: Record<string, string>;
}

/** Un piano nuovo: gli importi in centesimi. Un pacchetto ha un prezzo solo e almeno un credito. */
export interface NuovoPiano {
  slug: string;
  name: string;
  description?: string;
  tipo: "abbonamento" | "pacchetto";
  price_monthly: number;
  price_yearly?: number;
  credits_per_period?: number;
  letture_al_giorno?: number;
  letture_alla_settimana?: number;
  letture_al_mese?: number;
  letture_totali?: number;
  rank?: number;
  active?: boolean;
}

/* ---- ordini (mazzi, v5, Fase B6) ---- */

export type StatoOrdine = "aperto" | "pagato" | "annullato" | "scaduto";
export type TipoRigaOrdine = "digitale" | "pdf" | "fisico";
export type StatoEvasione = "in_attesa" | "spedito" | "consegnato";

export interface RigaOrdine {
  id: number;
  tipo: TipoRigaOrdine;
  deck_id: number;
  /* Il mazzo della riga (v8.5): il nome da mostrare. */
  mazzo?: { nome: string; slug: string } | null;
  quantita: number;
  /** Centesimi. */
  prezzo_pieno_unitario: number;
  /** Centesimi, dopo l'eventuale offerta a tempo sul mazzo. */
  prezzo_finale_unitario: number;
  /** Solo per `tipo === "fisico"`. */
  stato_evasione: StatoEvasione | null;
}

export interface Ordine {
  id: string;
  user_id: number;
  status: StatoOrdine;
  /** Centesimi, dopo lo sconto per-mazzo (già nelle righe) e quello a scaglioni. */
  importo_totale: number;
  /** Centesimi: solo la parte a scaglioni. */
  sconto_scaglioni: number;
  valuta: string;
  righe: RigaOrdine[];
  indirizzo_spedizione: Record<string, string | null> | null;
  creato: string | null;
  completato: string | null;
}

export interface VoceRegistro {
  id: number;
  attore: number | null;
  azione: string;
  tipo: string | null;
  target: string | null;
  prima: Record<string, unknown> | null;
  dopo: Record<string, unknown> | null;
  ip: string | null;
  correlazione: string | null;
  quando: string;
}

export interface ModelloConfigurato {
  nome: string;
  provider: string;
  model: string;
  descrizione: string;
}

export interface CompitoAssegnato {
  compito: string;
  label: string;
  descrizione: string;
  /* Il nome scelto, o `null` quando il compito ricade sul predefinito. Le
   * due cose si comportano uguale oggi e diversamente domani, quando il
   * predefinito cambia: per questo restano distinte. */
  assegnato: string | null;
  /* v7: se questo COMPITO ragiona, a prescindere dal fornitore assegnato. `null` solo per
   * un compito senza assegnazione propria (ricade sul predefinito) — un'assegnazione toccata
   * dalla console ha sempre un valore esplicito, mai `null` (il backlog vuole il reasoning
   * spento per default, non "eredita" per i compiti non ancora toccati). */
  ragiona_override: boolean | null;
  /* Il livello di ragionamento scelto per il compito; `null` = eredita dal fornitore. */
  livello: LivelloRagionamento | null;
  /* Lo stato vero, calcolato dal servizio: il livello in uso (`null` per un fornitore di prima dei livelli), se il
   * modello ragiona davvero e chi l'ha deciso. */
  livello_effettivo: LivelloRagionamento | null;
  livello_fornitore: LivelloRagionamento | null;
  ragiona_effettivo: boolean;
  /* `codice`: spento dal servizio qualunque scelta (l'embedding, l'aggiornamento breve della memoria). */
  ragiona_origine: "compito" | "fornitore" | "parametri" | "codice" | "predefinito";
  ragiona_spegnibile: boolean;
  /* Il livello del compito quando non se ne sceglie uno (l'anteprima: `none`); `null` = eredita dal fornitore. */
  livello_predefinito?: LivelloRagionamento | null;
  /* Senza assegnazione usa il modello di questo compito invece del predefinito (l'anteprima: `sintesi`). */
  segue?: string | null;
  /* Lo schema JSON rigoroso in uso, e se il compito risponde in JSON (altrimenti non si offre). */
  json_schema: boolean;
  schema_possibile: boolean;
  in_uso: string;
  senza_filtri: boolean;
}

export type LivelloRagionamento = "none" | "minimal" | "low" | "medium" | "high" | "xhigh" | "max";

/* I livelli nell'ordine della console, con il nome per chi non è tecnico. */
export const LIVELLI_RAGIONAMENTO: { valore: LivelloRagionamento; nome: string }[] = [
  { valore: "none", nome: "Nessuno (spento)" },
  { valore: "minimal", nome: "Minimo" },
  { valore: "low", nome: "Basso" },
  { valore: "medium", nome: "Medio" },
  { valore: "high", nome: "Alto" },
  { valore: "xhigh", nome: "Molto alto" },
  { valore: "max", nome: "Massimo" },
];

export const nomeLivello = (l: LivelloRagionamento | null | undefined) =>
  LIVELLI_RAGIONAMENTO.find((x) => x.valore === l)?.nome ?? "—";

/* Le impostazioni di un compito da scrivere. Ogni campo presente si scrive (`null` = torna al predefinito / eredita),
 * ogni campo assente non si tocca. `modello` serve sempre: un compito senza assegnazione la riceve qui, sul fornitore
 * che già usa. */
export interface ModificaCompito {
  modello: string;
  livello?: LivelloRagionamento | null;
  json_schema?: boolean | null;
}

export const aggiornaCompito = (t: string, compito: string, corpo: ModificaCompito) =>
  chiamata<{ compiti: CompitoAssegnato[] }>(t, `/admin/models/${compito}`, {
    method: "PUT",
    body: JSON.stringify(corpo),
  });

/* ---- statistiche ---- */

export const leggiStatistiche = (t: string, giorni: number) =>
  chiamata<Statistiche>(t, `/admin/stats?giorni=${giorni}`);

/* ---- utenti ---- */

export const elencoUtenti = (
  t: string,
  filtri: { q?: string; limite?: number; offset?: number } = {},
) =>
  chiamata<{ totale: number; utenti: Utente[] }>(
    t,
    `/admin/users${interrogazione(filtri)}`,
  );

export const dettaglioUtente = (t: string, id: number) =>
  chiamata<UtenteDettaglio>(t, `/admin/users/${id}`);

/* Un account creato a mano: nasce in Keycloak con questa password (definitiva, email già verificata) e subito anche
 * nel database, col piano gratuito. 409 se l'email è già usata, 400 se la password non rispetta la politica del
 * realm. */
export const creaUtente = (
  t: string,
  corpo: { email: string; password: string; nome?: string },
) =>
  chiamata<Omit<Utente, "saldo" | "piano">>(t, `/admin/users`, {
    method: "POST",
    body: JSON.stringify(corpo),
  });

export const impostaAttivo = (t: string, id: number, attivo: boolean) =>
  chiamata<Omit<Utente, "saldo" | "piano">>(t, `/admin/users/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ attivo }),
  });

/* Una riga nuova nel registro dei crediti, mai una modifica di quelle che ci
 * sono: il motivo è obbligatorio, e il backend lo rifiuta sotto i tre
 * caratteri. */
export const rettificaCrediti = (
  t: string,
  id: number,
  corpo: { delta: number; motivo: string },
) =>
  chiamata<{ saldo: number; delta: number }>(t, `/admin/users/${id}/credits`, {
    method: "POST",
    body: JSON.stringify(corpo),
  });

/* Lo storno a mano di un incasso (v9): toglie i crediti che aveva dato, con lo stesso riferimento del fornitore.
 * Non rimborsa il denaro: quello si fa presso il fornitore. 409 se è già stornato. */
export const stornaMovimento = (t: string, id: number, voce: number, motivo: string) =>
  chiamata<{ saldo: number; delta: number }>(t, `/admin/users/${id}/credits/${voce}/storno`, {
    method: "POST",
    body: JSON.stringify({ motivo }),
  });

/* ---- pagamenti e catalogo ---- */

export interface ConfigurazionePagamenti {
  /** stripe, mock o disattivato. */
  provider: string;
  /** Solo se le chiavi ci sono, mai i valori. */
  stripe: { chiave_segreta: boolean; segreto_webhook: boolean; modalita: "test" | "live" | null };
  webhook_url: string;
  eventi: string[];
  schemi_app: string[];
}

export const configurazionePagamenti = (t: string) =>
  chiamata<ConfigurazionePagamenti>(t, "/admin/payments/config");

export const elencoPagamenti = (
  t: string,
  filtri: { stato?: string; limite?: number; offset?: number } = {},
) =>
  chiamata<{ totale: number; incassato: number; pagamenti: Pagamento[] }>(
    t,
    `/admin/payments${interrogazione(filtri)}`,
  );

export const elencoOrdini = (
  t: string,
  filtri: { status?: string; limite?: number; offset?: number } = {},
) =>
  chiamata<{ totale: number; incassato: number; ordini: Ordine[] }>(
    t,
    `/admin/orders${interrogazione(filtri)}`,
  );

export const dettaglioOrdine = (t: string, id: string) => chiamata<Ordine>(t, `/admin/orders/${id}`);

/** Solo per una riga `fisico`: le altre non hanno una spedizione da seguire (il backend lo rifiuta). */
export const aggiornaEvasione = (t: string, ordineId: string, rigaId: number, stato_evasione: StatoEvasione) =>
  chiamata<Ordine>(t, `/admin/orders/${ordineId}/righe/${rigaId}`, {
    method: "PATCH", body: JSON.stringify({ stato_evasione }),
  });

export const catalogo = (t: string) => chiamata<Piano[]>(t, "/admin/plans");

export const creaPiano = (t: string, corpo: NuovoPiano) =>
  chiamata<Piano>(t, "/admin/plans", { method: "POST", body: JSON.stringify(corpo) });

/** Solo un piano mai usato; uno usato si disattiva (il backend risponde 409). */
export const eliminaPiano = (t: string, slug: string) =>
  chiamata<void>(t, `/admin/plans/${encodeURIComponent(slug)}`, { method: "DELETE" });

export const modificaPiano = (t: string, slug: string, corpo: ModificaPiano) =>
  chiamata<Piano>(t, `/admin/plans/${encodeURIComponent(slug)}`, {
    method: "PATCH",
    body: JSON.stringify(corpo),
  });

/* ---- report ---- */

export type TipoReport = "utenti" | "pagamenti" | "crediti" | "letture";

/** Scarica un CSV e lo consegna al browser come file.
 *
 * `fetch` e non un collegamento: un `<a href>` non sa mandare l'intestazione
 * `Authorization`, e un token in querystring finisce nei log del proxy. Il
 * file arriva come blob, diventa un indirizzo locale, e un collegamento
 * invisibile lo salva col nome che il backend ha scelto.
 */
export async function scaricaReport(
  t: string,
  tipo: TipoReport,
  giorni: number,
): Promise<string> {
  return scaricaFile(t, `/admin/reports/${tipo}.csv?giorni=${giorni}`, {}, `${tipo}-${giorni}g.csv`);
}

/** Come `scaricaReport`, per qualunque file dell'API (anche con POST e corpo JSON). */
export async function scaricaFile(
  t: string,
  percorso: string,
  opzioni: RequestInit = {},
  nomeRipiego = "file",
): Promise<string> {
  const risposta = await fetch(`${API}${percorso}`, {
    ...opzioni,
    headers: { ...intestazioni(t), "Content-Type": "application/json", ...(opzioni.headers ?? {}) },
  });
  if (!risposta.ok) await errore(risposta);

  const disposizione = risposta.headers.get("Content-Disposition") ?? "";
  const nome = /filename="?([^";]+)"?/.exec(disposizione)?.[1] ?? nomeRipiego;

  const indirizzo = URL.createObjectURL(await risposta.blob());
  try {
    const a = document.createElement("a");
    a.href = indirizzo;
    a.download = nome;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } finally {
    /* Rilasciato al giro dopo: revocarlo subito, in qualche browser,
     * interrompe il salvataggio appena cominciato. */
    setTimeout(() => URL.revokeObjectURL(indirizzo), 0);
  }
  return nome;
}

/* ---- registro ---- */

export const registro = (
  t: string,
  filtri: { azione?: string; target_type?: string; limite?: number; offset?: number } = {},
) => chiamata<VoceRegistro[]>(t, `/admin/audit${interrogazione(filtri)}`);

/* ---- i modelli e i compiti ---- */

export const modelliECompiti = (t: string) =>
  chiamata<{
    /* Falso: nessun modello vero — le letture rispondono 503. */
    configurato: boolean;
    finto: boolean;
    modelli: ModelloConfigurato[];
    compiti: CompitoAssegnato[];
  }>(
    t, "/admin/models",
  );

export const assegnaModello = (
  t: string,
  compito: string,
  modello: string | null,
  /* `undefined` (parametro omesso) = non toccare il reasoning di questa assegnazione, es. quando
   * si cambia solo il modello. Un valore esplicito lo sovrascrive. */
  ragiona?: boolean,
) =>
  chiamata<{ compiti: CompitoAssegnato[] }>(t, `/admin/models/${compito}`, {
    method: "PUT",
    body: JSON.stringify(ragiona === undefined ? { modello } : { modello, ragiona }),
  });
