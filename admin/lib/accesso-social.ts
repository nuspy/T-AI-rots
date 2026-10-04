/* L'accesso con i social: i provider che la console sa configurare su Keycloak.
 *
 * Il segreto si manda e basta: il backend lo gira a Keycloak e non lo salva, e indietro torna solo
 * `segreto_impostato` (sì/no). Un `client_secret` vuoto in una modifica vuol dire «tieni quello che c'è». */

import { chiamata } from "./api";

export interface ProviderSociale {
  alias: string;
  nome: string;
  /** Falso per Instagram: è nel catalogo solo per spiegare perché non si accende (`nota`). */
  disponibile: boolean;
  nota: string;
  guida: string[];
  /** Dove si creano le credenziali presso il provider. */
  console: string;
  /** Da registrare presso il provider come indirizzo di ritorno. */
  uri_reindirizzamento: string;
  /** Il provider esiste nel realm (anche spento). */
  presente: boolean;
  abilitato: boolean;
  client_id: string;
  segreto_impostato: boolean;
  /** L'email del provider è garantita: si può unire in automatico all'account con la stessa email (non X, Microsoft). */
  unione_possibile: boolean;
  /** Il provider usa il flusso che unisce gli account. */
  unione_automatica: boolean;
  /** Il backend legge il profilo dal provider, e Keycloak ne conserva il token (`storeToken`). */
  legge_profilo: boolean;
  token_conservato: boolean;
  /** Ci sono ambiti «sensibili» (data di nascita, sesso, città) che si possono chiedere, e se sono chiesti. */
  dati_estesi_disponibili: boolean;
  dati_estesi: boolean;
  nota_estesi: string;
  /** Solo nella risposta a un salvataggio: perché l'unione non è stata attivata (un ruolo che manca in Keycloak). */
  avviso?: string | null;
}

export interface AccessoSociale {
  keycloak_raggiungibile: boolean;
  errore: string | null;
  provider: ProviderSociale[];
  unione: {
    flusso: string;
    /** `null` se Keycloak non ha risposto. */
    flusso_presente: boolean | null;
    /** Tutti i provider presenti con l'email garantita usano il flusso. */
    completa: boolean;
  };
}

export interface ModificaProvider {
  abilitato: boolean;
  client_id: string;
  client_secret: string;
  /** Chiedere anche gli ambiti sensibili; assente = lascia com'è. */
  dati_estesi?: boolean;
}

/** Account dell'app con la stessa email ma identità Keycloak diverse (nati prima dell'unione automatica). */
export interface GruppoDoppio {
  email: string;
  utenti: {
    id: number;
    email: string | null;
    display_name: string | null;
    keycloak_sub: string;
    attivo: boolean;
    creato: string | null;
    letture: number;
  }[];
}

export const accessoSociale = (t: string) => chiamata<AccessoSociale>(t, "/admin/accesso-social");

export const salvaProvider = (t: string, alias: string, corpo: ModificaProvider) =>
  chiamata<ProviderSociale>(t, `/admin/accesso-social/${encodeURIComponent(alias)}`, {
    method: "PUT",
    body: JSON.stringify(corpo),
  });

/** Crea (se manca) il flusso che unisce gli account e lo assegna a tutti i provider presenti con l'email garantita. */
export const applicaUnione = (t: string) =>
  chiamata<AccessoSociale & { provider_aggiornati: string[] }>(t, "/admin/accesso-social/unione", { method: "POST" });

export const accountDoppi = (t: string) =>
  chiamata<{ gruppi: GruppoDoppio[] }>(t, "/admin/accesso-social/doppioni");

/* ---- Apple: il segreto firmato dal sito (v9, Fase 6) ---- */

/** Ciò che la console sa del segreto di Apple: mai la chiave, solo se c'è e la sua impronta. */
export interface SegretoApple {
  team_id: string;
  /** Il Team ID scritto in «App mobili → iOS», proposto se qui manca (è lo stesso account sviluppatore). */
  team_id_suggerito: string;
  key_id: string;
  services_id: string;
  chiave: { presente: boolean; impronta: string | null; illeggibile: boolean };
  /** Team ID, Key ID, Services ID e chiave ci sono tutti: il segreto si può firmare. */
  completa: boolean;
  segreto: {
    generato_il: string | null;
    scade_il: string | null;
    giorni_rimasti: number | null;
    scaduto: boolean;
    da_rinnovare: boolean;
  };
  esito: { ok?: boolean; messaggio?: string; il?: string; avviso?: string };
  durata_giorni: number;
  rinnova_entro_giorni: number;
  /** Solo nella risposta a un salvataggio o a un rinnovo. */
  applicato?: { scade_il: string; abilitato: boolean; avviso: string | null } | null;
}

export interface ModificaSegretoApple {
  team_id?: string;
  key_id?: string;
  services_id?: string;
  /** Il contenuto del file .p8; assente = resta quella di prima. */
  chiave_p8?: string;
  abilitato?: boolean;
}

export const segretoApple = (t: string) => chiamata<SegretoApple>(t, "/admin/accesso-social/apple/segreto");

export const salvaSegretoApple = (t: string, corpo: ModificaSegretoApple) =>
  chiamata<SegretoApple>(t, "/admin/accesso-social/apple/segreto", { method: "PUT", body: JSON.stringify(corpo) });

export const rinnovaSegretoApple = (t: string) =>
  chiamata<SegretoApple>(t, "/admin/accesso-social/apple/segreto/rinnova", { method: "POST" });
