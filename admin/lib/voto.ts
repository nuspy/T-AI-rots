/* Vota il prossimo mazzo (v7, Fase K): tornate, candidati, carte di prova, accettazione dei
 * vincitori. Stesso principio dei mazzi (`mazzi.ts`): l'artwork resta un file separato, qui si
 * gestiscono solo la tornata e i suoi candidati. */

import { chiamata } from "./api";

export type StatoTornata = "aperta" | "chiusa";

export interface Tornata {
  id: string;
  stato: StatoTornata;
  aperta_il: string;
  /** La scadenza dichiarata alla creazione: passata quella, la tornata si chiude da sola. */
  chiude_il: string | null;
  chiusa_il: string | null;
}

export interface CampioneCandidato {
  etichetta: string | null;
  url: string;
}

export interface Candidato {
  id: string;
  nome: string;
  descrizione: string | null;
  campioni: CampioneCandidato[];
  voti: number;
  accettato: boolean;
  deck_id: number | null;
  /** `null` finché il candidato è solo una proposta in riserva, non ancora scelta per una tornata. */
  round_id: string | null;
}

export const tornate = (t: string) => chiamata<Tornata[]>(t, "/admin/voto/tornate");

/** «Tornate elettorali»: si scelgono i candidati fra le proposte in riserva e si dichiara la
 * scadenza — non se ne creano di nuovi al volo qui, vedi `creaProposta`. */
export const creaTornata = (t: string, candidateIds: string[], chiudeIl: string) =>
  chiamata<Tornata>(t, "/admin/voto/tornate", {
    method: "POST", body: JSON.stringify({ candidate_ids: candidateIds, chiude_il: chiudeIl }),
  });

export const chiudiTornata = (t: string, roundId: string) =>
  chiamata<{ id: string; stato: StatoTornata }>(t, `/admin/voto/tornate/${roundId}/chiudi`, { method: "POST" });

export const candidatiDiTornata = (t: string, roundId: string) =>
  chiamata<Candidato[]>(t, `/admin/voto/tornate/${roundId}/candidati`);

/** La riserva: proposte già inserite (con eventuali carte di prova) ma non ancora scelte per
 * nessuna tornata — da qui si scelgono i candidati alla creazione di una nuova tornata. */
export const proposteDisponibili = (t: string) => chiamata<Candidato[]>(t, "/admin/voto/candidati/disponibili");

export const creaProposta = (t: string, corpo: { nome: string; descrizione?: string }) =>
  chiamata<Candidato>(t, "/admin/voto/candidati", { method: "POST", body: JSON.stringify(corpo) });

export const modificaCandidato = (t: string, candidateId: string, corpo: { nome?: string; descrizione?: string }) =>
  chiamata<Candidato>(t, `/admin/voto/candidati/${candidateId}`, { method: "PUT", body: JSON.stringify(corpo) });

export const eliminaCandidato = (t: string, candidateId: string) =>
  chiamata<void>(t, `/admin/voto/candidati/${candidateId}`, { method: "DELETE" });

/** Il body è l'immagine grezza, non JSON — stesso pattern di `caricaArtwork` in `mazzi.ts`. */
export const caricaCampione = (t: string, candidateId: string, etichetta: string, file: File) =>
  chiamata<{ etichetta: string; url: string }>(
    t, `/admin/voto/candidati/${candidateId}/campioni?etichetta=${encodeURIComponent(etichetta)}`,
    { method: "POST", body: file, headers: { "Content-Type": file.type || "image/webp" } },
  );

export const accettaVincitori = (t: string, roundId: string, candidateIds: string[]) =>
  chiamata<{ deck_ids: string[]; tornata_chiusa: boolean }>(t, `/admin/voto/tornate/${roundId}/accetta`, {
    method: "POST", body: JSON.stringify({ candidate_ids: candidateIds }),
  });

/** Crea (o recupera, se già fatto) il mazzo reale di un candidato — vincitore o no: l'admin può
 * voler realizzare anche un mazzo che non ha vinto la votazione. Nessuna generazione automatica
 * dell'artwork: solo il record `Deck`, da completare con la pipeline `crea-mazzo-tarocchi`. */
export const generaMazzoDaCandidato = (t: string, candidateId: string) =>
  chiamata<{ deck_id: number; slug: string }>(t, `/admin/voto/candidati/${candidateId}/genera-mazzo`, { method: "POST" });

/* ---- suggerimenti degli iscritti ("suggerisci tema mazzo") ---- */

export type StatoSuggerimento = "nuovo" | "usato" | "scartato";

export interface Suggerimento {
  id: string;
  user_id: number;
  testo: string;
  stato: StatoSuggerimento;
  candidate_id: string | null;
  creato_il: string;
}

/** Solo quelli ancora da rivedere: una volta trasformati o scartati escono dalla coda. */
export const suggerimenti = (t: string) => chiamata<Suggerimento[]>(t, "/admin/voto/suggerimenti");

/** Trasforma il suggerimento in una proposta vera nella riserva — nome e descrizione partono dal
 * testo libero, si rifiniscono dopo con `modificaCandidato` come ogni altra proposta. */
export const trasformaSuggerimento = (t: string, suggestionId: string) =>
  chiamata<Candidato>(t, `/admin/voto/suggerimenti/${suggestionId}/trasforma`, { method: "POST" });

export const scartaSuggerimento = (t: string, suggestionId: string) =>
  chiamata<Suggerimento>(t, `/admin/voto/suggerimenti/${suggestionId}/scarta`, { method: "POST" });
