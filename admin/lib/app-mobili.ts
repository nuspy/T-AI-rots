/* «App mobili» (v9, Fase 3): account sviluppatore e pagamenti di Google Play e Apple, prodotti degli store collegati
 * ai piani, politica del pulsante Stripe, appunti di Codemagic.
 *
 * I segreti (il JSON del service account per la Play Developer API, la chiave .p8 della App Store Server API) entrano
 * e non tornano: la console vede solo se ci sono e come riconoscerli. */

import { chiamata } from "./api";

export type Piattaforma = "android" | "ios";
export type TipoAccount = "personale" | "organizzazione";
export type StatoTestChiuso = "non_iniziato" | "in_corso" | "completato" | "non_richiesto";
export type Ambiente = "sandbox" | "production";
export type StatoAccordi = "non_firmati" | "in_attesa" | "attivi";
export type ModalitaStripe = "nascosto" | "link_esterno" | "entitlement_ue" | "scelta_utente";
export type TipoProdotto = "consumabile" | "abbonamento";
export type StatoFiscale = "non_inviate" | "inviate" | "accettate";
export type TipoProfilo = "individuale" | "azienda";

export const NOMI_TIPO_ACCOUNT: Record<TipoAccount, string> = {
  personale: "Personale",
  organizzazione: "Organizzazione (con D-U-N-S)",
};
export const NOMI_TEST_CHIUSO: Record<StatoTestChiuso, string> = {
  non_iniziato: "Non iniziato",
  in_corso: "In corso",
  completato: "Completato",
  non_richiesto: "Non richiesto (organizzazione o account vecchio)",
};
export const NOMI_AMBIENTE: Record<Ambiente, string> = { sandbox: "Sandbox (prove)", production: "Produzione" };
export const NOMI_ACCORDI: Record<StatoAccordi, string> = {
  non_firmati: "Non firmati",
  in_attesa: "In attesa (banca o fisco da completare)",
  attivi: "Attivi",
};
export const NOMI_MODALITA: Record<ModalitaStripe, string> = {
  nascosto: "Nascosto",
  link_esterno: "Link esterno al sito",
  entitlement_ue: "Entitlement UE (SEE)",
  scelta_utente: "Scelta dell'utente (solo Google)",
};
export const SPIEGA_MODALITA: Record<ModalitaStripe, string> = {
  nascosto: "Nessun pulsante: si compra solo con lo store. È il predefinito e l'unico sicuro ovunque.",
  link_esterno:
    "Un collegamento per pagare sul sito. Apple lo ammette negli Stati Uniti; Google con i programmi per le offerte esterne, dove esistono.",
  entitlement_ue:
    "Nello Spazio economico europeo, con l'autorizzazione dello store (Apple «External Purchase Link Entitlement», Google «fatturazione alternativa»). Solo per un paese del SEE.",
  scelta_utente:
    "Store e Stripe affiancati, sceglie l'utente (Google «User Choice Billing»). Su Apple non esiste.",
};
export const NOMI_STATO_FISCALE: Record<StatoFiscale, string> = {
  non_inviate: "Non inviate",
  inviate: "Inviate",
  accettate: "Accettate",
};
export const NOMI_TIPO_PROFILO: Record<TipoProfilo, string> = { individuale: "Individuale", azienda: "Azienda" };

export interface PagamentiStore {
  id_profilo: string;
  beneficiario: string;
  tipo_profilo: TipoProfilo;
  paese: string;
  valuta: string;
  banca: string;
  conto_ultime4: string;
  stato_fiscale: StatoFiscale;
  note: string;
}

export interface ParametriAndroid {
  package_name: string;
  id_sviluppatore: string;
  email_account: string;
  tipo_account: TipoAccount;
  test_chiuso: StatoTestChiuso;
  /** `AAAA-MM-GG` o `null`. */
  test_chiuso_dal: string | null;
  pubsub_topic: string;
  rtdn_audience: string;
  rtdn_email: string;
  versione_minima: string;
  versione_ultima: string;
  commissione_ridotta: boolean;
  /** Fase 10: le impronte SHA-256 dei certificati di firma (`AB:CD:…`), per `/.well-known/assetlinks.json`. */
  impronte_sha256: string[];
  note: string;
}

export interface ParametriIos {
  bundle_id: string;
  team_id: string;
  apple_app_id: string;
  email_account: string;
  tipo_account: TipoAccount;
  key_id: string;
  issuer_id: string;
  ambiente: Ambiente;
  versione_minima: string;
  versione_ultima: string;
  ipad: boolean;
  accordi_paid_apps: StatoAccordi;
  small_business: boolean;
  note: string;
}

export interface ParametriCodemagic {
  team: string;
  app_id: string;
  email_account: string;
  chiave_asc_caricata: boolean;
  chiave_asc_key_id: string;
  keystore_caricato: boolean;
  note: string;
}

export interface EsitoVerifica {
  ok?: boolean;
  messaggio?: string;
}

interface Base<P> {
  parametri: P;
  verificato_il: string | null;
  esito_verifica: EsitoVerifica;
  link_console: string;
}

/** v9, Fase 4: l'ultima notifica arrivata dallo store (RTDN di Google, Server Notifications V2 di Apple). */
export interface UltimaNotifica {
  il: string | null;
  tipo?: string;
  ambiente?: Ambiente | null;
  esito?: string;
}

export interface ConfigAndroid extends Base<ParametriAndroid> {
  segreti: {
    service_account: { presente: boolean; client_email: string | null; project_id: string | null; chiave_fine: string | null };
  };
  pagamenti: PagamentiStore;
  link_store: string | null;
  url_rtdn: string;
  ultima_notifica?: UltimaNotifica;
}

export interface ConfigIos extends Base<ParametriIos> {
  segreti: { chiave_p8: { presente: boolean; impronta: string | null } };
  pagamenti: PagamentiStore;
  link_store: string | null;
  url_notifiche: string;
  ultima_notifica?: UltimaNotifica;
}

export type ConfigCodemagic = Base<ParametriCodemagic>;

export interface ProdottoStore {
  id: number;
  piattaforma: Piattaforma;
  product_id: string;
  plan_id: number;
  piano: { slug: string; nome: string; tipo: string; attivo: boolean } | null;
  tipo: TipoProdotto;
  /** Fase 4, solo abbonamenti: l'annuale (altrimenti il mensile) e il prodotto «prova» (annuale a metà prezzo). */
  annuale: boolean;
  prova: boolean;
  attivo: boolean;
  note: string;
}

export interface PoliticaStripe {
  id: number;
  piattaforma: Piattaforma;
  /** ISO 3166-1 alpha-2, o `*` per tutti gli altri paesi. */
  paese: string;
  modalita: ModalitaStripe;
  avviso: string;
}

export interface Piano {
  id: number;
  slug: string;
  nome: string;
  tipo: "abbonamento" | "pacchetto";
  attivo: boolean;
  /** Senza prezzo: non si vende negli store. */
  gratuito: boolean;
}

export interface StatoAppMobili {
  android: ConfigAndroid;
  ios: ConfigIos;
  codemagic: ConfigCodemagic;
  prodotti: ProdottoStore[];
  politica_stripe: PoliticaStripe[];
  piani: Piano[];
  catalogo: { modalita_stripe: ModalitaStripe[]; see: string[] };
}

export const statoAppMobili = (t: string) => chiamata<StatoAppMobili>(t, "/admin/app-mobili");

export const salvaAndroid = (
  t: string,
  corpo: { parametri?: Partial<ParametriAndroid>; service_account_json?: string; pagamenti?: Partial<PagamentiStore> },
) => chiamata<StatoAppMobili>(t, "/admin/app-mobili/android", { method: "PUT", body: JSON.stringify(corpo) });

export const salvaIos = (
  t: string,
  corpo: { parametri?: Partial<ParametriIos>; chiave_p8?: string; pagamenti?: Partial<PagamentiStore> },
) => chiamata<StatoAppMobili>(t, "/admin/app-mobili/ios", { method: "PUT", body: JSON.stringify(corpo) });

export const salvaCodemagic = (t: string, corpo: Partial<ParametriCodemagic>) =>
  chiamata<StatoAppMobili>(t, "/admin/app-mobili/codemagic", { method: "PUT", body: JSON.stringify(corpo) });

export const verificaStore = (t: string, piattaforma: Piattaforma) =>
  chiamata<StatoAppMobili>(t, `/admin/app-mobili/${piattaforma}/verifica`, { method: "POST" });

export const creaProdotto = (
  t: string,
  corpo: { piattaforma: Piattaforma; product_id: string; plan_id: number; annuale?: boolean; prova?: boolean; note?: string },
) => chiamata<StatoAppMobili>(t, "/admin/app-mobili/prodotti", { method: "POST", body: JSON.stringify(corpo) });

export const modificaProdotto = (
  t: string, id: number, corpo: { plan_id?: number; annuale?: boolean; prova?: boolean; attivo?: boolean; note?: string },
) =>
  chiamata<StatoAppMobili>(t, `/admin/app-mobili/prodotti/${id}`, { method: "PUT", body: JSON.stringify(corpo) });

export const eliminaProdotto = (t: string, id: number) =>
  chiamata<StatoAppMobili>(t, `/admin/app-mobili/prodotti/${id}`, { method: "DELETE" });

export const impostaPolitica = (
  t: string,
  corpo: { piattaforma: Piattaforma; paese: string; modalita: ModalitaStripe; avviso: string },
) => chiamata<StatoAppMobili>(t, "/admin/app-mobili/politica-stripe", { method: "PUT", body: JSON.stringify(corpo) });

export const eliminaPolitica = (t: string, id: number) =>
  chiamata<StatoAppMobili>(t, `/admin/app-mobili/politica-stripe/${id}`, { method: "DELETE" });

/** v9, Fase 6: crea in Keycloak il client delle app (`tarot-mobile`) se manca. Idempotente. */
export const preparaAccessoApp = (t: string) =>
  chiamata<{ creato: boolean; client_id: string; redirect: string; messaggio: string }>(
    t, "/admin/app-mobili/accesso", { method: "POST" },
  );
