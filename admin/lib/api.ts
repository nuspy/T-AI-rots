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

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";

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

async function chiamata<T>(
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

function interrogazione(parametri: Record<string, string | number | undefined>): string {
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
  delta: number;
  reason: string;
  quando: string;
  note: string | null;
  reading_id: string | null;
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
  creato: string | null;
  completato: string | null;
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
}

export interface Piano {
  id: number;
  slug: string;
  nome: string;
  tipo: "abbonamento" | "pacchetto";
  descrizione: string | null;
  /** Centesimi. */
  prezzo_mensile: number | null;
  /** Centesimi. */
  prezzo_annuale: number | null;
  crediti: number | null;
  limiti: { letture_al_giorno?: number } & Record<string, unknown>;
  attivo: boolean;
  rango: number;
  abbonati: number;
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
  active?: boolean;
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
  in_uso: string;
  senza_filtri: boolean;
}

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

/* ---- pagamenti e catalogo ---- */

export const elencoPagamenti = (
  t: string,
  filtri: { stato?: string; limite?: number; offset?: number } = {},
) =>
  chiamata<{ totale: number; incassato: number; pagamenti: Pagamento[] }>(
    t,
    `/admin/payments${interrogazione(filtri)}`,
  );

export const catalogo = (t: string) => chiamata<Piano[]>(t, "/admin/plans");

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
  const risposta = await fetch(`${API}/admin/reports/${tipo}.csv?giorni=${giorni}`, {
    headers: intestazioni(t),
  });
  if (!risposta.ok) await errore(risposta);

  const disposizione = risposta.headers.get("Content-Disposition") ?? "";
  const nome =
    /filename="?([^";]+)"?/.exec(disposizione)?.[1] ??
    `${tipo}-${giorni}g.csv`;

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
  filtri: { azione?: string; target_type?: string; limite?: number } = {},
) => chiamata<VoceRegistro[]>(t, `/admin/audit${interrogazione(filtri)}`);

/* ---- i modelli e i compiti ---- */

export const modelliECompiti = (t: string) =>
  chiamata<{ modelli: ModelloConfigurato[]; compiti: CompitoAssegnato[] }>(
    t, "/admin/models",
  );

export const assegnaModello = (
  t: string,
  compito: string,
  modello: string | null,
) =>
  chiamata<{ compiti: CompitoAssegnato[] }>(t, `/admin/models/${compito}`, {
    method: "PUT",
    body: JSON.stringify({ modello }),
  });
