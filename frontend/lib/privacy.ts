/* La privacy dell'account (GDPR, Fase 1): i consensi granulari, l'età minima, l'esportazione dei dati, la
 * cancellazione dell'account, la chat da cancellare. Le chiamate stanno qui e non in `lib/api.ts` per tenere quel
 * file più corto: usano lo stesso `chiama` (stessi errori, stesso cookie anonimo). */

import { API, ErroreApi, chiama, type TipoConsenso, type ValoreConsenso } from "./api";

/** La versione dell'informativa con le categorie granulari: va nello storico con ogni scelta fatta su questo testo. */
export const VERSIONE_CONSENSI = "v3";

/** Le categorie che si scelgono oggi, nell'ordine in cui si mostrano. */
export const CATEGORIE = [
  "statistiche", "google_analytics", "pubblicita", "testi_statistiche", "dati_particolari", "marketing",
] as const;
export type Categoria = (typeof CATEGORIE)[number];

export type StatoConsensi = Record<Categoria, ValoreConsenso | null> & { cookie?: ValoreConsenso | null };

/** Più scelte in una volta («accetta tutto», «rifiuta tutto», «scegli»): o tutte o nessuna. */
export const registraConsensi = (
  token: string | null, scelte: Partial<Record<TipoConsenso, ValoreConsenso>>, versione: string = VERSIONE_CONSENSI,
) =>
  chiama<StatoConsensi>(token, "/consensi", {
    method: "POST",
    body: {
      scelte: Object.entries(scelte).map(([tipo, valore]) => ({ tipo, valore })),
      versione_informativa: versione,
      origine: "web",
    },
  });

export interface StatoEta {
  anni: number;
  paese: string | null;
  confermata_il: string | null;
  da_confermare: boolean;
  sotto_eta: boolean;
}

export interface StatoCancellazione {
  richiesta_il: string | null;
  definitiva_il: string | null;
  eseguita_il: string | null;
  annullabile: boolean;
  giorni_ripensamento: number;
  sessioni_chiuse?: boolean;
}

export interface StatoPrivacy {
  eta: StatoEta;
  esportazione: { ultima_il: string | null; prossima_dal: string | null };
  consensi: Partial<Record<TipoConsenso, { valore: ValoreConsenso; versione: string; il: string | null }>>;
  cancellazione: StatoCancellazione;
}

export const leggiPrivacy = (token: string | null) => chiama<StatoPrivacy>(token, "/me/privacy");

/** L'età minima per chi non ha (ancora) un account: per il paese stimato dall'IP. */
export const leggiEtaMinima = () => chiama<{ anni: number; paese: string | null }>(null, "/eta-minima");

export const confermaEta = (token: string | null, anni: number) =>
  chiama<StatoEta>(token, "/me/eta", { method: "POST", body: { anni, origine: "web" } });

export const statoCancellazione = (token: string | null) => chiama<StatoCancellazione>(token, "/me/cancellazione");

export const chiediCancellazione = (token: string | null) =>
  chiama<StatoCancellazione>(token, "/me/cancellazione", { method: "POST", body: { conferma: true } });

export const annullaCancellazione = (token: string | null) =>
  chiama<StatoCancellazione>(token, "/me/cancellazione/annulla", { method: "POST" });

export const cancellaChat = (token: string | null) => chiama<void>(token, "/chat/proattiva", { method: "DELETE" });

export const cancellaTurnoChat = (token: string | null, id: string) =>
  chiama<void>(token, `/chat/proattiva/${encodeURIComponent(id)}`, { method: "DELETE" });

/** Il dettaglio di un 409 `account_in_cancellazione`, se l'errore è quello. */
export function inCancellazione(e: unknown): StatoCancellazione | null {
  if (!(e instanceof ErroreApi) || e.stato !== 409) return null;
  const d = e.dettaglio as ({ motivo?: string } & StatoCancellazione) | undefined;
  return d?.motivo === "account_in_cancellazione" ? d : null;
}

/** I motivi dell'età: da confermare (con gli anni da chiedere) o insufficiente. */
export function motivoEta(e: unknown): { motivo: "eta_da_confermare" | "eta_insufficiente"; anni: number } | null {
  if (!(e instanceof ErroreApi) || (e.stato !== 403 && e.stato !== 422)) return null;
  const d = e.dettaglio as { motivo?: string; anni?: number } | undefined;
  if (d?.motivo === "eta_da_confermare" || d?.motivo === "eta_insufficiente") return { motivo: d.motivo, anni: d.anni ?? 16 };
  return null;
}

/** L'archivio ZIP dei propri dati: si scarica come file. Una volta ogni 24 ore (poi 429 con la data). */
export async function scaricaEsportazione(token: string | null): Promise<{ ok: true } | { ok: false; prossimaDal: string | null }> {
  const risposta = await fetch(`${API}/me/esportazione`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    credentials: "include",
  });
  if (risposta.status === 429) {
    let prossima: string | null = null;
    try {
      prossima = (await risposta.json())?.detail?.prossima_dal ?? null;
    } catch {
      /* il corpo non era JSON */
    }
    return { ok: false, prossimaDal: prossima };
  }
  if (!risposta.ok) throw new ErroreApi(String(risposta.status), risposta.status);
  const blob = await risposta.blob();
  const nome = /filename="([^"]+)"/.exec(risposta.headers.get("content-disposition") ?? "")?.[1] ?? "tarots-chat-dati.zip";
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nome;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 10_000);
  return { ok: true };
}
