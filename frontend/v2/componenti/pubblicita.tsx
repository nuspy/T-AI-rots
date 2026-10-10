"use client";

/* Gli spazi pubblicitari del sito: tre per pagina («terzo», «due_terzi», «fine»), accesi dalla console
 * (Advertisements → Google Ads) e **spenti per default**.
 *
 * - Spenta, o senza consenso, `Pubblicita` non rende nulla: nessuno spazio, nessuno script. Il sito resta com'era.
 * - Il consenso agli annunci è un consenso a sé (`pubblicita` in `/consenso`), chiesto dal banner dei cookie solo
 *   quando gli spazi sono accesi. Lo script di AdSense si scarica una volta sola, e solo dopo aver riletto dal server
 *   un «accettato».
 * - Niente salti di pagina: chi ha accettato porta un cookie del sito (`COOKIE_PUBBLICITA`) che il layout legge sul
 *   server, così l'HTML esce già con lo spazio riservato (altezza minima per formato, in `v2.css`). Chi accetta dal
 *   banner vede comparire gli spazi subito dopo il tocco: un cambio dopo un gesto non conta nel CLS.
 * - La posizione «a un terzo» si decide nei modelli delle pagine (o con `ConPubblicita`, che conta i blocchi), mai
 *   spostando il DOM fuori da React.
 *
 * Nell'Unione europea, nel Regno Unito e in Svizzera Google chiede per AdSense una CMP certificata TCF: il banner
 * del sito non lo è. Dal 10/10/2026, con la pubblicità accesa, si carica il CMP di Google («Privacy e messaggi» di
 * AdSense, TCF 2.2, già tradotto): dove il TCF si applica (`gdprApplies`) è lui a chiedere il consenso agli annunci, e
 * il banner del sito non fa più quella domanda; altrove resta il consenso del sito. Se il CMP non c'è (messaggio non
 * pubblicato in AdSense, script bloccato) dopo 5 s vale il consenso del sito. */

import { usePathname } from "next/navigation";
import {
  Children, Fragment, createContext, isValidElement, useContext, useEffect, useId, useRef, useSyncExternalStore,
} from "react";
import { leggiConsenso, type ValoreConsenso } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { useLingua } from "@/v2/lib/lingua";
import {
  COOKIE_PUBBLICITA, SPENTA, esclusa, posizioniPer, type ImpostazioniPubblicita, type Posizione, type SpazioPubblicita,
} from "@/v2/lib/pubblicita";

/** I dati che il CMP passa a chi ascolta (`__tcfapi('addEventListener', 2, …)`): solo i campi che servono qui. */
interface DatiTcf {
  gdprApplies?: boolean;
  eventStatus?: "tcloaded" | "cmpuishown" | "useractioncomplete";
}

declare global {
  interface Window {
    adsbygoogle?: unknown[] & { requestNonPersonalizedAds?: number };
    __tcfapi?: (comando: string, versione: number, richiamo: (dati: DatiTcf | null, ok: boolean) => void) => void;
    googlefc?: { callbackQueue?: unknown[]; showRevocationMessage?: () => void };
  }
}

export interface StatoInizialePubblicita {
  impostazioni: ImpostazioniPubblicita;
  /** Il cookie del sito dice che questo browser aveva accettato gli annunci: si riserva lo spazio già sul server. */
  ricordo: boolean;
}

const Contesto = createContext<StatoInizialePubblicita>({ impostazioni: SPENTA, ricordo: false });

/* ---- il consenso agli annunci, condiviso fra banner, pagina privacy e spazi ---- */

/** `undefined`: non ancora letto dal server; `null`: mai deciso. */
let consenso: ValoreConsenso | null | undefined = undefined;
const ascoltatori = new Set<() => void>();

function imposta(valore: ValoreConsenso | null): void {
  consenso = valore;
  ascoltatori.forEach((f) => f());
}

function iscriviti(f: () => void): () => void {
  ascoltatori.add(f);
  return () => ascoltatori.delete(f);
}

function ricorda(accettato: boolean): void {
  const sicuro = window.location.protocol === "https:" ? "; Secure" : "";
  document.cookie = accettato
    ? `${COOKIE_PUBBLICITA}=1; Path=/; Max-Age=31536000; SameSite=Lax${sicuro}`
    : `${COOKIE_PUBBLICITA}=; Path=/; Max-Age=0; SameSite=Lax${sicuro}`;
}

/* ---- il CMP di Google (TCF 2.2), per UE, Regno Unito e Svizzera ---- */

/** `applica`: `undefined` finché non si sa, `true` se il consenso agli annunci lo chiede il CMP, `false` se lo chiede il
 *  sito. `pronto`: il CMP ha la scelta di chi guarda (o sa che non c'è da chiedere), gli annunci possono partire. */
export interface StatoTcf { applica: boolean | undefined; pronto: boolean }

const TCF_INIZIALE: StatoTcf = { applica: undefined, pronto: false };
let tcf: StatoTcf = TCF_INIZIALE;
let cmpCaricato = false;

function impostaTcf(nuovo: StatoTcf): void {
  if (nuovo.applica === tcf.applica && nuovo.pronto === tcf.pronto) return;
  tcf = nuovo;
  ascoltatori.forEach((f) => f());
}

/* Lo snippet di «Privacy e messaggi» di AdSense: lo script del CMP e l'iframe `googlefcPresent`, poi l'ascolto del
 * TCF. Una volta sola per pagina. */
function caricaCmp(editore: string): void {
  if (cmpCaricato) return;
  cmpCaricato = true;
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://fundingchoicesmessages.google.com/i/${encodeURIComponent(editore.replace(/^ca-/, ""))}?ers=1`;
  document.head.appendChild(script);
  const segnala = () => {
    if ((window.frames as unknown as Record<string, unknown>).googlefcPresent) return;
    if (!document.body) { window.setTimeout(segnala, 0); return; }
    const cornice = document.createElement("iframe");
    cornice.style.cssText = "width:0;height:0;border:none;z-index:-1000;left:-1000px;top:-1000px;display:none";
    cornice.name = "googlefcPresent";
    document.body.appendChild(cornice);
  };
  segnala();
  const inizio = Date.now();
  const ascolta = () => {
    const api = window.__tcfapi;
    if (typeof api === "function") {
      api("addEventListener", 2, (dati, ok) => {
        if (!ok || !dati) return;
        const applica = dati.gdprApplies === true;
        impostaTcf({ applica, pronto: !applica || dati.eventStatus === "tcloaded" || dati.eventStatus === "useractioncomplete" });
      });
      return;
    }
    /* Niente CMP dopo 5 s: vale il consenso del sito. */
    if (Date.now() - inizio > 5000) impostaTcf({ applica: false, pronto: true });
    else window.setTimeout(ascolta, 200);
  };
  ascolta();
}

/** Riapre il messaggio del CMP di Google, per cambiare la scelta sugli annunci (pagina privacy). */
export function cambiaSceltaAnnunciGoogle(): void {
  const fc = (window.googlefc = window.googlefc || {});
  (fc.callbackQueue = fc.callbackQueue || []).push(() => window.googlefc?.showRevocationMessage?.());
}

/** Le impostazioni degli spazi, il consenso di chi guarda e se a chiederlo è il CMP di Google (banner, privacy). */
export function usePubblicita(): { attiva: boolean; consenso: ValoreConsenso | null | undefined; tcf: StatoTcf } {
  const { impostazioni } = useContext(Contesto);
  const valore = useSyncExternalStore(iscriviti, () => consenso, () => undefined);
  const statoTcf = useSyncExternalStore(iscriviti, () => tcf, () => TCF_INIZIALE);
  return { attiva: impostazioni.attiva, consenso: valore, tcf: statoTcf };
}

/** Da chiamare dopo aver registrato la scelta sugli annunci (banner o pagina privacy): vale subito, senza ricaricare. */
export function annunciaConsensoPubblicita(valore: ValoreConsenso): void {
  ricorda(valore === "accettato");
  imposta(valore);
  if (valore === "rifiutato") spegni();
}

/* ---- AdSense ---- */

/* Lo stesso frammento di gtag di `contatore-google.tsx`: Consent Mode legge i comandi da `dataLayer`. */
const gtag = function gtag() {
  const w = window as unknown as { dataLayer?: unknown[] };
  w.dataLayer = w.dataLayer || [];
  // eslint-disable-next-line prefer-rest-params
  w.dataLayer.push(arguments);
} as unknown as (...argomenti: unknown[]) => void;

let scriptCaricato = false;

function caricaAdSense(google: NonNullable<ImpostazioniPubblicita["google"]>, daTcf = false): void {
  /* Il consenso di questa persona vale per gli annunci; la personalizzazione solo se la console la accende. Dove
   * decide il CMP (TCF), AdSense legge da sé la sua stringa di consenso: qui non si concede niente. */
  if (!daTcf) {
    gtag("consent", "update", {
      ad_storage: "granted",
      ad_user_data: "granted",
      ad_personalization: google.personalizzati ? "granted" : "denied",
    });
  }
  const coda = (window.adsbygoogle = window.adsbygoogle || []);
  coda.requestNonPersonalizedAds = google.personalizzati ? 0 : 1;
  if (scriptCaricato) return;
  scriptCaricato = true;
  const script = document.createElement("script");
  script.async = true;
  script.crossOrigin = "anonymous";
  script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${encodeURIComponent(google.editore)}`;
  document.head.appendChild(script);
}

/* Revoca: niente più annunci nuovi (gli spazi spariscono con lo stato) e i cookie di AdSense del sito si cancellano. */
function spegni(): void {
  gtag("consent", "update", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
  const host = window.location.hostname;
  const radice = host.split(".").slice(-2).join(".");
  for (const voce of document.cookie.split(";")) {
    const nome = voce.split("=")[0]?.trim();
    if (!nome || !/^(__gads|__gpi|__eoi)$/.test(nome)) continue;
    for (const d of ["", host, `.${host}`, `.${radice}`]) {
      document.cookie = `${nome}=; Max-Age=0; path=/${d ? `; domain=${d}` : ""}`;
    }
  }
}

/* ---- il provider (nei provider della v2) ---- */

/** Porta a tutte le pagine le impostazioni lette dal layout, e rilegge il consenso di chi guarda (solo se gli spazi
 *  sono accesi: spenta la pubblicità, nessuna richiesta in più). */
export function ProviderPubblicita({ iniziale, children }: { iniziale?: StatoInizialePubblicita; children: React.ReactNode }) {
  const valore = iniziale ?? { impostazioni: SPENTA, ricordo: false };
  const attiva = valore.impostazioni.attiva;
  const editore = valore.impostazioni.google?.editore;
  const sessione = useSessione();

  /* Con la pubblicità accesa il CMP di Google si carica per tutti: è lui a sapere se il TCF si applica. */
  useEffect(() => {
    if (attiva && editore) caricaCmp(editore);
  }, [attiva, editore]);

  useEffect(() => {
    if (!attiva || !sessione.pronta) return;
    let annullato = false;
    leggiConsenso(sessione.token)
      .then((c) => {
        if (annullato) return;
        const scelta = c.pubblicita ?? null;
        ricorda(scelta === "accettato");
        imposta(scelta);
      })
      .catch(() => {});
    return () => {
      annullato = true;
    };
  }, [attiva, sessione.pronta, sessione.token]);

  return <Contesto.Provider value={valore}>{children}</Contesto.Provider>;
}

/* ---- gli spazi ---- */

interface SpazioVisibile {
  spazio: SpazioPubblicita;
  google: NonNullable<ImpostazioniPubblicita["google"]>;
  confermato: boolean;
  /** Il consenso lo gestisce il CMP di Google (TCF): AdSense lo legge da sé. */
  daTcf: boolean;
}

/* Gli spazi di questa pagina che si vedono adesso: accesi in console, non esclusi, con il consenso (del sito, o del
 * CMP di Google dove si applica il TCF). */
function useSpazi(): (posizione: Posizione) => SpazioVisibile | null {
  const { impostazioni, ricordo } = useContext(Contesto);
  const valore = useSyncExternalStore(iscriviti, () => consenso, () => undefined);
  const statoTcf = useSyncExternalStore(iscriviti, () => tcf, () => TCF_INIZIALE);
  const percorso = usePathname();
  return (posizione) => {
    const spazio = impostazioni.attiva ? impostazioni.posizioni?.[posizione] : undefined;
    const google = impostazioni.google;
    if (!spazio || !google || esclusa(percorso, impostazioni.pagine_escluse)) return null;
    /* Dove decide il CMP lo spazio c'è appena il CMP ha la scelta; AdSense serve annunci secondo quella. */
    if (statoTcf.applica === true) return statoTcf.pronto ? { spazio, google, confermato: true, daTcf: true } : null;
    /* Si vede con un consenso confermato, o — finché il server non ha risposto — col promemoria del cookie. */
    const confermato = valore === "accettato";
    if (!confermato && !(valore === undefined && ricordo)) return null;
    return { spazio, google, confermato, daTcf: false };
  };
}

/** Vero se almeno uno di questi spazi si vede: per le pagine che cambiano forma solo quando c'è un annuncio da
 *  inserire (il testo di un articolo si taglia solo allora). */
export function usePubblicitaVisibile(posizioni: Posizione[]): boolean {
  const visibile = useSpazi();
  return posizioni.some((p) => visibile(p) !== null);
}

/** Uno spazio pubblicitario. `dentro`: sta dentro una colonna o una fascia che ha già i suoi margini laterali. */
export function Pubblicita({ posizione, dentro = false }: { posizione: Posizione; dentro?: boolean }) {
  const visibile = useSpazi()(posizione);
  if (!visibile) return null;
  return <Annuncio posizione={posizione} {...visibile} dentro={dentro} />;
}

function Annuncio({
  posizione, spazio, google, confermato, daTcf, dentro,
}: {
  posizione: Posizione;
  spazio: SpazioPubblicita;
  google: NonNullable<ImpostazioniPubblicita["google"]>;
  confermato: boolean;
  daTcf: boolean;
  dentro: boolean;
}) {
  const { t } = useLingua();
  const id = useId();
  const ins = useRef<HTMLModElement>(null);

  useEffect(() => {
    if (!confermato) return;
    caricaAdSense(google, daTcf);
    const el = ins.current;
    /* Una richiesta per spazio: il doppio effetto dello sviluppo non deve chiederne due. */
    if (!el || el.dataset.richiesto || el.dataset.adsbygoogleStatus) return;
    el.dataset.richiesto = "1";
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch {
      /* AdSense non ha accettato lo spazio (bloccato, già pieno): resta vuoto, con la sua altezza */
    }
  }, [confermato, daTcf, google]);

  return (
    <aside
      className={`pubblicita pubblicita-${spazio.formato}${dentro ? " pubblicita-dentro" : ""}`}
      aria-labelledby={id}
      data-posizione={posizione}
    >
      <p id={id} className="pubblicita-etichetta">{t.comune.pubblicita_etichetta}</p>
      <ins
        ref={ins}
        className="adsbygoogle"
        style={{ display: "block" }}
        data-ad-client={google.editore}
        data-ad-slot={spazio.slot}
        data-ad-format={spazio.formato}
        data-full-width-responsive={google.responsive ? "true" : "false"}
        {...(google.prova ? { "data-adtest": "on" } : {})}
      />
    </aside>
  );
}

/** Una sequenza di blocchi con gli spazi inseriti a un terzo, a due terzi e alla fine (`posizioniPer`). Per le pagine
 *  il cui contenuto cambia (articoli, piani, mazzi): i blocchi assenti (`null`, `false`) non contano. Spenta la
 *  pubblicità, rende esattamente i blocchi. */
export function ConPubblicita({ children, dentro = false }: { children: React.ReactNode; dentro?: boolean }) {
  const blocchi = Children.toArray(children);
  const dove = posizioniPer(blocchi.length);
  return (
    <>
      {blocchi.map((b, i) => {
        const posizione = dove.get(i + 1);
        return (
          <Fragment key={isValidElement(b) && b.key != null ? b.key : i}>
            {b}
            {posizione && <Pubblicita posizione={posizione} dentro={dentro} />}
          </Fragment>
        );
      })}
    </>
  );
}
