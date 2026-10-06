"use client";

/* La traduzione automatica sul dispositivo (v9.5).
 *
 * Usa la Translator API di Chrome (da Chrome 138, solo desktop: Windows, macOS, Linux, ChromeOS): modelli piccoli,
 * uno per coppia di lingue, scaricati da Chrome la prima volta e poi usati senza rete. Niente server, niente costi,
 * il testo non esce dal computer. Dove l'API non c'è (Firefox, Safari, Chrome su Android e iOS) non succede nulla.
 *
 * Si traduce il testo GIÀ MOSTRATO dentro una o più radici del DOM, un blocco alla volta (paragrafo, titolo, voce di
 * elenco, cella…): il blocco si manda come una frase sola, con i suoi elementi in linea (link, grassetti) segnati da
 * etichette numerate `<1>…</1>`; se la traduzione le restituisce nello stesso ordine, ogni pezzo torna nel suo nodo di
 * testo e i link restano dove sono. Altrimenti il blocco si traduce nodo per nodo. Si cambia solo il valore dei nodi
 * di testo (mai la struttura), così React continua a riconoscere il suo albero; se React cambia un testo, un
 * MutationObserver lo ritraduce. `ripristina()` rimette gli originali.
 *
 * Questo file è uguale in `admin/lib/traduzione-auto.ts` (la console lo usa in attesa dei suoi dizionari):
 * `npm run controlla-traduzione` nel sito verifica che le due copie coincidano. */

export type Disponibilita = "unavailable" | "downloadable" | "downloading" | "available";

interface ApiTraduttore {
  translate(testo: string): Promise<string>;
  destroy?: () => void;
}
interface FabbricaTraduttori {
  availability(o: { sourceLanguage: string; targetLanguage: string }): Promise<Disponibilita>;
  create(o: {
    sourceLanguage: string;
    targetLanguage: string;
    monitor?: (m: EventTarget) => void;
  }): Promise<ApiTraduttore>;
}
interface FabbricaRilevatori {
  availability(): Promise<Disponibilita>;
  create(): Promise<{ detect(t: string): Promise<{ detectedLanguage: string; confidence: number }[]> }>;
}

function fabbrica(): FabbricaTraduttori | null {
  if (typeof self === "undefined" || !("Translator" in self)) return null;
  return (self as unknown as { Translator: FabbricaTraduttori }).Translator;
}

/** Vero se il browser ha la Translator API (Chrome desktop 138+). */
export function supportata(): boolean {
  return fabbrica() !== null;
}

/** La parte principale di un codice di lingua: «en-US» → «en». */
export const base = (lingua: string) => lingua.toLowerCase().split(/[-_]/)[0];

export async function disponibilita(da: string, a: string): Promise<Disponibilita> {
  const f = fabbrica();
  if (!f || base(da) === base(a)) return "unavailable";
  try {
    return await f.availability({ sourceLanguage: base(da), targetLanguage: base(a) });
  } catch {
    return "unavailable";
  }
}

const traduttori = new Map<string, Promise<ApiTraduttore>>();

/** Il traduttore di una coppia di lingue, uno solo per pagina. Se il modello va scaricato, Chrome pretende che la
 * chiamata nasca da un gesto dell'utente (un clic): altrimenti rifiuta, e qui si dimentica il tentativo. */
export function traduttore(da: string, a: string, avanzamento?: (percento: number) => void): Promise<ApiTraduttore> {
  const chiave = `${base(da)}>${base(a)}`;
  let p = traduttori.get(chiave);
  if (!p) {
    const f = fabbrica();
    if (!f) return Promise.reject(new Error("Translator API assente"));
    p = f.create({
      sourceLanguage: base(da),
      targetLanguage: base(a),
      monitor(m) {
        m.addEventListener("downloadprogress", (e) => {
          const caricato = (e as ProgressEvent).loaded;
          avanzamento?.(Math.round((caricato <= 1 ? caricato * 100 : caricato)));
        });
      },
    });
    p.catch(() => traduttori.delete(chiave));
    traduttori.set(chiave, p);
  }
  return p;
}

/** La lingua di un testo con la Language Detector API (stessa disponibilità della traduzione), o null. */
export async function rilevaLingua(testo: string): Promise<string | null> {
  if (typeof self === "undefined" || !("LanguageDetector" in self)) return null;
  try {
    const f = (self as unknown as { LanguageDetector: FabbricaRilevatori }).LanguageDetector;
    if ((await f.availability()) === "unavailable") return null;
    const esiti = await (await f.create()).detect(testo.slice(0, 2000));
    const primo = esiti[0];
    return primo && primo.confidence >= 0.5 && primo.detectedLanguage !== "und" ? base(primo.detectedLanguage) : null;
  } catch {
    return null;
  }
}

// ---- la memoria delle traduzioni ------------------------------------------------------------------------------

const MEMORIA = "tarots_traduzioni_v1";
const TETTO_MEMORIA = 1500;
let memoria: Map<string, string> | null = null;

function leggiMemoria(): Map<string, string> {
  if (memoria) return memoria;
  memoria = new Map();
  try {
    const salvata = JSON.parse(window.localStorage.getItem(MEMORIA) ?? "[]") as [string, string][];
    for (const [k, v] of salvata) memoria.set(k, v);
  } catch {
    /* archiviazione non disponibile: si traduce di nuovo */
  }
  return memoria;
}

let salvataggio: ReturnType<typeof setTimeout> | null = null;
function ricorda(chiave: string, valore: string): void {
  const m = leggiMemoria();
  m.delete(chiave);
  m.set(chiave, valore);
  while (m.size > TETTO_MEMORIA) m.delete(m.keys().next().value as string);
  if (salvataggio) clearTimeout(salvataggio);
  salvataggio = setTimeout(() => {
    try {
      window.localStorage.setItem(MEMORIA, JSON.stringify([...m]));
    } catch {
      /* piena o non disponibile: resta in memoria per questa pagina */
    }
  }, 800);
}

// ---- il DOM ---------------------------------------------------------------------------------------------------

const BLOCCHI = "p,li,h1,h2,h3,h4,h5,h6,summary,dt,dd,td,th,figcaption,blockquote,label,legend,caption,button,option";
const MAI = "script,style,code,pre,kbd,samp,textarea,input,select,svg,math,[translate=no],.notranslate,[data-no-trad]";
const IN_LINEA = new Set(["A", "STRONG", "EM", "B", "I", "SPAN", "U", "SMALL", "MARK", "SUB", "SUP", "ABBR", "CITE",
  "Q", "S", "DEL", "INS", "TIME", "BDI"]);
const ATTRIBUTI = ["placeholder", "title", "aria-label", "alt"];
const LETTERE = /\p{L}/u;

interface Nodo {
  originale: string;
  tradotto: string;
}

/** Traduce e tiene tradotte una o più radici del DOM, finché non si chiama `ripristina()`. */
export class TraduzionePagina {
  private testi = new Map<Text, Nodo>();
  private attributi = new Map<Element, Record<string, Nodo>>();
  private osservatore: MutationObserver | null = null;
  private inScrittura = false;
  private coda = new Set<Element>();
  private timer: ReturnType<typeof setTimeout> | null = null;
  private fermata = false;
  private lingueRadici = new Map<HTMLElement, string | null>();

  constructor(
    private radici: HTMLElement[],
    private da: string,
    private a: string,
    private api: ApiTraduttore,
  ) {}

  /** Traduce tutto quello che c'è e poi segue i cambiamenti. */
  async avvia(): Promise<void> {
    for (const r of this.radici) {
      this.lingueRadici.set(r, r.getAttribute("lang"));
      r.setAttribute("lang", base(this.a));
    }
    for (const r of this.radici) await this.traduciSotto(r);
    if (this.fermata || typeof MutationObserver === "undefined") return;
    this.osservatore = new MutationObserver((cambi) => this.cambiati(cambi));
    for (const r of this.radici) {
      this.osservatore.observe(r, {
        subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRIBUTI,
      });
    }
  }

  /** Rimette i testi originali e smette di seguire la pagina. */
  ripristina(): void {
    this.fermata = true;
    this.osservatore?.disconnect();
    if (this.timer) clearTimeout(this.timer);
    this.scrivi(() => {
      for (const [nodo, s] of this.testi) if (nodo.nodeValue === s.tradotto) nodo.nodeValue = s.originale;
      for (const [el, valori] of this.attributi) {
        for (const [nome, s] of Object.entries(valori)) if (el.getAttribute(nome) === s.tradotto) el.setAttribute(nome, s.originale);
      }
      for (const [r, lang] of this.lingueRadici) {
        if (lang === null) r.removeAttribute("lang");
        else r.setAttribute("lang", lang);
      }
    });
    this.testi.clear();
    this.attributi.clear();
  }

  private scrivi(fn: () => void): void {
    this.inScrittura = true;
    try {
      fn();
    } finally {
      this.osservatore?.takeRecords();
      this.inScrittura = false;
    }
  }

  private async frase(testo: string): Promise<string> {
    const chiave = `${base(this.da)}>${base(this.a)}:${testo}`;
    const m = leggiMemoria();
    const noto = m.get(chiave);
    if (noto !== undefined) return noto;
    const tradotto = await this.api.translate(testo);
    ricorda(chiave, tradotto);
    return tradotto;
  }

  private escluso(n: Node): boolean {
    const el = n instanceof Element ? n : n.parentElement;
    return !el || el.closest(MAI) !== null;
  }

  private async traduciSotto(radice: Element): Promise<void> {
    if (this.fermata || this.escluso(radice)) return;
    const blocchi = [radice, ...radice.querySelectorAll(BLOCCHI)].filter(
      (b) => b.matches(BLOCCHI) && !b.querySelector(BLOCCHI) && !this.escluso(b),
    );
    for (const b of blocchi) {
      if (this.fermata) return;
      await this.traduciBlocco(b);
    }
    // I testi fuori dai blocchi (un <div> con testo dentro, una cella fatta di <span>…): uno per uno.
    const percorso = document.createTreeWalker(radice, NodeFilter.SHOW_TEXT);
    const sciolti: Text[] = [];
    for (let n = percorso.nextNode(); n; n = percorso.nextNode()) {
      const t = n as Text;
      if (!this.testi.has(t) && LETTERE.test(t.nodeValue ?? "") && !this.escluso(t)) sciolti.push(t);
    }
    for (const t of sciolti) {
      if (this.fermata) return;
      await this.traduciNodo(t);
    }
    await this.traduciAttributi(radice);
  }

  /** Un blocco come frase sola, con gli elementi in linea segnati da etichette numerate. */
  private async traduciBlocco(blocco: Element): Promise<void> {
    if (!LETTERE.test(blocco.textContent ?? "")) return;
    const pezzi: Text[][] = [[]];
    const etichette: string[] = [];
    let testo = "";
    let semplice = true;
    let n = 0;
    const visita = (el: Node) => {
      for (const figlio of el.childNodes) {
        if (figlio.nodeType === Node.TEXT_NODE) {
          const t = figlio as Text;
          pezzi[pezzi.length - 1].push(t);
          testo += this.testi.get(t)?.originale ?? t.nodeValue ?? "";
        } else if (figlio instanceof Element && IN_LINEA.has(figlio.tagName) && !figlio.matches(MAI)) {
          const id = ++n;
          etichette.push(`<${id}>`);
          testo += `<${id}>`;
          pezzi.push([]);
          visita(figlio);
          etichette.push(`</${id}>`);
          testo += `</${id}>`;
          pezzi.push([]);
        } else if (figlio.nodeType === Node.ELEMENT_NODE) {
          semplice = false; // un'immagine, un'interruzione, codice: meglio nodo per nodo
        }
      }
    };
    visita(blocco);
    if (!semplice) {
      for (const gruppo of pezzi) for (const t of gruppo) await this.traduciNodo(t);
      return;
    }
    let tradotto: string;
    try {
      tradotto = await this.frase(testo.trim());
    } catch {
      return;
    }
    const trovate = tradotto.match(/<\/?\d+>/g) ?? [];
    const parti = tradotto.split(/<\/?\d+>/);
    if (trovate.join() !== etichette.join() || parti.length !== pezzi.length) {
      for (const gruppo of pezzi) for (const t of gruppo) await this.traduciNodo(t);
      return;
    }
    this.scrivi(() => {
      pezzi.forEach((gruppo, i) => {
        if (!gruppo.length) return;
        const originaleGruppo = gruppo.map((t) => this.testi.get(t)?.originale ?? t.nodeValue ?? "").join("");
        const prima = originaleGruppo.match(/^\s*/)?.[0] ?? "";
        const dopo = originaleGruppo.match(/\s*$/)?.[0] ?? "";
        const parte = parti[i].trim();
        gruppo.forEach((t, j) => {
          const originale = this.testi.get(t)?.originale ?? t.nodeValue ?? "";
          const nuovo = j === 0 ? (parte ? `${prima}${parte}${dopo}` : originaleGruppo) : "";
          this.testi.set(t, { originale, tradotto: nuovo });
          t.nodeValue = nuovo;
        });
      });
    });
  }

  private async traduciNodo(t: Text): Promise<void> {
    const originale = this.testi.get(t)?.originale ?? t.nodeValue ?? "";
    if (!LETTERE.test(originale) || this.escluso(t)) return;
    try {
      const parte = await this.frase(originale.trim());
      const prima = originale.match(/^\s*/)?.[0] ?? "";
      const dopo = originale.match(/\s*$/)?.[0] ?? "";
      const nuovo = `${prima}${parte}${dopo}`;
      this.scrivi(() => {
        this.testi.set(t, { originale, tradotto: nuovo });
        t.nodeValue = nuovo;
      });
    } catch {
      /* resta l'originale */
    }
  }

  private async traduciAttributi(radice: Element): Promise<void> {
    const elementi = [radice, ...radice.querySelectorAll(ATTRIBUTI.map((a) => `[${a}]`).join(","))];
    for (const el of elementi) {
      if (this.fermata) return;
      if (el.closest("[translate=no],.notranslate,[data-no-trad]")) continue;
      for (const nome of ATTRIBUTI) {
        const valore = el.getAttribute(nome);
        if (!valore || !LETTERE.test(valore)) continue;
        const noto = this.attributi.get(el)?.[nome];
        if (noto && valore === noto.tradotto) continue;
        try {
          const tradotto = await this.frase(valore);
          this.scrivi(() => {
            this.attributi.set(el, { ...(this.attributi.get(el) ?? {}), [nome]: { originale: valore, tradotto } });
            el.setAttribute(nome, tradotto);
          });
        } catch {
          /* resta l'originale */
        }
      }
    }
  }

  /** React (o altro) ha cambiato la pagina: si ritraduce solo ciò che è cambiato, poco dopo e una volta sola. */
  private cambiati(cambi: MutationRecord[]): void {
    if (this.inScrittura || this.fermata) return;
    for (const c of cambi) {
      if (c.type === "characterData") {
        const t = c.target as Text;
        const s = this.testi.get(t);
        if (s && t.nodeValue === s.tradotto) continue;
        if (s) this.testi.delete(t);
        const blocco = t.parentElement?.closest(BLOCCHI) ?? t.parentElement;
        if (blocco) this.coda.add(blocco);
      } else if (c.type === "childList") {
        for (const n of c.addedNodes) {
          if (n instanceof Element) this.coda.add(n);
          else if (n.parentElement) this.coda.add(n.parentElement.closest(BLOCCHI) ?? n.parentElement);
        }
      } else if (c.type === "attributes" && c.target instanceof Element) {
        this.coda.add(c.target);
      }
    }
    if (!this.coda.size) return;
    if (this.timer) clearTimeout(this.timer);
    this.timer = setTimeout(() => {
      const elementi = [...this.coda].filter((e) => e.isConnected);
      this.coda.clear();
      void (async () => {
        for (const e of elementi) await this.traduciSotto(e);
      })();
    }, 150);
  }
}

// ---- le preferenze --------------------------------------------------------------------------------------------

const AUTOMATICA = "tarots_traduzione_automatica";

/** Falso se la persona ha scelto «non tradurre automaticamente». */
export function automaticaAttiva(): boolean {
  try {
    return window.localStorage.getItem(AUTOMATICA) !== "no";
  } catch {
    return true;
  }
}

export function impostaAutomatica(attiva: boolean): void {
  try {
    if (attiva) window.localStorage.removeItem(AUTOMATICA);
    else window.localStorage.setItem(AUTOMATICA, "no");
  } catch {
    /* niente: resta la scelta di questa pagina */
  }
}
