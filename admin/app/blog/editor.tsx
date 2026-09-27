"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  articoli,
  articolo as leggiArticolo,
  cambiaStato,
  carteEStese,
  creaArticolo,
  eliminaArticolo,
  etichette,
  FAQ_DOMANDA_MAX,
  FAQ_MAX,
  FAQ_RISPOSTA_MAX,
  markdownImmagine,
  modificaArticolo,
  PAROLE_CHIAVE_MAX,
  revisioni,
  ripristina,
  sezioni,
  traduciArticolo,
  urlMedia,
  type Articolo,
  type CampiArticolo,
  type DatiControlloSeo,
  type DomandaFrequente,
  type Immagine,
  type StatoArticolo,
} from "@/lib/blog";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import { etichettaStato, sezioniInOrdine } from "./aiuti";
import { Anteprima } from "./anteprima";
import stili from "./blog.module.css";
import { PannelloSeo } from "./pannello-seo";
import { SelettoreImmagine } from "./selettore-immagine";

/* L'editor di un articolo, nuovo o esistente.
 *
 * Scrivere e leggere stanno nella stessa pagina: «Scrivi» è il Markdown con una barra di comandi,
 * «Anteprima» è l'articolo com'è sul sito (senza eseguire HTML). Un articolo non è mai a metà: si
 * salva quando si preme un pulsante, e finché non lo si fa la pagina avvisa a chi prova a chiuderla.
 * Ogni salvataggio che cambia titolo o testo conserva la versione di prima (le ultime venti), che si
 * può ripristinare da qui.
 *
 * Il salvataggio passa dallo stesso punto della pubblicazione via REST (`BlogRepository.salva`): slug,
 * versioni, collegamenti interni e tempo di lettura sono quelli, non una copia.
 */

/* Il sito pubblica in inglese (canonico) e in italiano: gli elenchi del blog mostrano gli articoli di queste due.
 * Le altre lingue restano raggiungibili dall'indirizzo dell'articolo ma non compaiono negli elenchi. */
const LINGUE = [
  ["en", "English"], ["it", "Italiano"], ["hu", "Magyar"], ["de", "Deutsch"], ["fr", "Français"],
  ["es", "Español"], ["pt", "Português"], ["ru", "Русский"], ["uk", "Українська"], ["ro", "Română"],
  ["pl", "Polski"], ["zh", "中文"], ["hi", "हिन्दी"], ["ko", "한국어"], ["ar", "العربية"],
] as const;

/* Sotto queste misure un risultato di ricerca non si tronca. Sono indicazioni, non limiti: il server
 * accetta di più (200 e 320). */
const TITOLO_SEO_IDEALE = 60;
const DESCRIZIONE_SEO_IDEALE = 160;
const MAX_ETICHETTE = 10;

interface Forma {
  titolo: string;
  sottotitolo: string;
  testo: string;
  slug: string;
  lang: string;
  sezioneId: string;
  immagineId: string | null;
  immagineUrl: string | null;
  immagineAlt: string;
  tags: string[];
  inEvidenza: boolean;
  commentiAperti: boolean;
  seoTitolo: string;
  seoDescrizione: string;
  /** La parola chiave principale e le secondarie (separate da virgole: si dividono al salvataggio). */
  parolaChiave: string;
  paroleSecondarie: string;
  noindex: boolean;
  canonical: string;
  faq: DomandaFrequente[];
  stato: StatoArticolo;
  /** Il valore di un `<input type="datetime-local">`: ora locale, senza fuso. */
  pubblicatoIl: string;
}

const VUOTA: Forma = {
  titolo: "", sottotitolo: "", testo: "", slug: "", lang: "en", sezioneId: "", immagineId: null,
  immagineUrl: null, immagineAlt: "", tags: [], inEvidenza: false, commentiAperti: true, seoTitolo: "",
  seoDescrizione: "", parolaChiave: "", paroleSecondarie: "", noindex: false, canonical: "", faq: [],
  stato: "bozza", pubblicatoIl: "",
};

const due = (n: number) => String(n).padStart(2, "0");

/** Un istante ISO → il valore di un campo `datetime-local` (nell'ora del browser). */
function inCampo(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return `${d.getFullYear()}-${due(d.getMonth() + 1)}-${due(d.getDate())}T${due(d.getHours())}:${due(d.getMinutes())}`;
}

function daArticolo(a: Articolo): Forma {
  return {
    titolo: a.titolo, sottotitolo: a.sottotitolo ?? "", testo: a.testo ?? "", slug: a.slug, lang: a.lang,
    sezioneId: a.sezione_id === null ? "" : String(a.sezione_id), immagineId: a.immagine_id,
    immagineUrl: a.immagine, immagineAlt: a.immagine_alt ?? "", tags: a.tags, inEvidenza: a.in_evidenza,
    commentiAperti: a.commenti_aperti, seoTitolo: a.seo_titolo ?? "", seoDescrizione: a.seo_descrizione ?? "",
    parolaChiave: a.seo_parola_chiave ?? "", paroleSecondarie: a.seo_parole_chiave.join(", "), noindex: a.noindex,
    canonical: a.canonical_url ?? "", faq: a.faq.map((f) => ({ domanda: f.domanda, risposta: f.risposta })),
    stato: a.stato, pubblicatoIl: inCampo(a.pubblicato_il),
  };
}

/* «amore, tarocchi di Thoth» → ["amore", "tarocchi di Thoth"], senza vuoti né doppioni. */
function paroleDa(testo: string): string[] {
  const viste = new Set<string>();
  return testo
    .split(",")
    .map((v) => v.replace(/\s+/g, " ").trim())
    .filter((v) => v && !viste.has(v.toLowerCase()) && viste.add(v.toLowerCase()))
    .slice(0, PAROLE_CHIAVE_MAX);
}

/* Una domanda senza risposta (o viceversa) non si salva: il server la scarterebbe. */
const faqCompleta = (faq: DomandaFrequente[]): DomandaFrequente[] =>
  faq
    .map((f) => ({ domanda: f.domanda.trim(), risposta: f.risposta.trim() }))
    .filter((f) => f.domanda && f.risposta);

function inCorpo(f: Forma): CampiArticolo {
  return {
    titolo: f.titolo.trim(),
    sottotitolo: f.sottotitolo.trim() || null,
    testo: f.testo,
    /* Vuoto = «scegli tu»: a un articolo nuovo lo slug lo deriva il server dal titolo. */
    slug: f.slug.trim() || undefined,
    lang: f.lang,
    sezione_id: f.sezioneId ? Number(f.sezioneId) : null,
    immagine_id: f.immagineId,
    immagine_alt: f.immagineAlt.trim() || null,
    tags: f.tags,
    in_evidenza: f.inEvidenza,
    commenti_aperti: f.commentiAperti,
    seo_titolo: f.seoTitolo.trim() || null,
    seo_descrizione: f.seoDescrizione.trim() || null,
    seo_parola_chiave: f.parolaChiave.trim() || null,
    seo_parole_chiave: paroleDa(f.paroleSecondarie),
    noindex: f.noindex,
    canonical_url: f.canonical.trim() || null,
    faq: faqCompleta(f.faq),
    stato: f.stato,
    pubblicato_il: f.pubblicatoIl ? new Date(f.pubblicatoIl).toISOString() : null,
  };
}

/* Il testo di un articolo senza Markdown: per l'anteprima del risultato di ricerca. */
function semplice(md: string): string {
  return md
    .replace(/\[\[[^\]]*\]\]/g, " ")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/[#>*_`|-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function Editor({ id }: { id?: string }) {
  const caricato = useDati(
    useCallback((t: string) => (id ? leggiArticolo(t, id) : Promise.resolve(null)), [id]),
  );

  if (id && !caricato.dati) {
    return caricato.errore ? (
      <>
        <p className={comuni.errore} role="alert">
          {caricato.errore}
        </p>
        <Link href="/blog">← Tutti gli articoli</Link>
      </>
    ) : (
      <p className={comuni.caricamento}>Caricamento…</p>
    );
  }
  return <Modulo iniziale={caricato.dati} />;
}

function Modulo({ iniziale }: { iniziale: Articolo | null }) {
  const router = useRouter();
  const { esegui, inCorso, errore } = useAzione();

  const [articoloSalvato, setArticoloSalvato] = useState<Articolo | null>(iniziale);
  const [forma, setForma] = useState<Forma>(iniziale ? daArticolo(iniziale) : VUOTA);
  const [salvata, setSalvata] = useState<Forma>(iniziale ? daArticolo(iniziale) : VUOTA);
  const [vista, setVista] = useState<"scrivi" | "anteprima">("scrivi");
  const [pannello, setPannello] = useState<null | "immagine" | "copertina" | "riferimento">(null);
  const [esito, setEsito] = useState<string | null>(null);
  const [eliminando, setEliminando] = useState(false);
  const [nuovaEtichetta, setNuovaEtichetta] = useState("");
  const [tipoRif, setTipoRif] = useState<"carta" | "stesa" | "articolo">("carta");
  const [idRif, setIdRif] = useState("");
  const area = useRef<HTMLTextAreaElement>(null);

  /* «Adesso» per decidere se il pulsante dice «Pubblica» o «Programma»: si aggiorna ogni mezzo minuto, così
   * un articolo lasciato aperto non resta programmato quando la sua ora è già passata. */
  const [adesso, setAdesso] = useState(() => Date.now());
  useEffect(() => {
    const giro = setInterval(() => setAdesso(Date.now()), 30_000);
    return () => clearInterval(giro);
  }, []);

  const modificato = JSON.stringify(forma) !== JSON.stringify(salvata);
  const nuovo = articoloSalvato === null;

  const imposta = <K extends keyof Forma>(campo: K, valore: Forma[K]) => {
    setForma((f) => ({ ...f, [campo]: valore }));
    setEsito(null);
  };

  /* Chi chiude la scheda con modifiche non salvate deve saperlo. */
  useEffect(() => {
    if (!modificato) return;
    const avvisa = (e: BeforeUnloadEvent) => e.preventDefault();
    window.addEventListener("beforeunload", avvisa);
    return () => window.removeEventListener("beforeunload", avvisa);
  }, [modificato]);

  const catalogo = useDati(carteEStese);
  const tutteLeSezioni = useDati(sezioni);
  const etichetteNote = useDati(etichette);
  const pubblicati = useDati(
    useCallback((t: string) => articoli(t, { stato: "pubblicato", per_pagina: 100 }), []),
  );
  const versioni = useDati(
    useCallback((t: string) => (articoloSalvato ? revisioni(t, articoloSalvato.id) : Promise.resolve([])), [articoloSalvato]),
  );

  const albero = useMemo(
    () => sezioniInOrdine(tutteLeSezioni.dati ?? []).filter((v) => v.sezione.tipo === "articoli"),
    [tutteLeSezioni.dati],
  );
  const riferimenti = useMemo(
    () => ({
      carta: catalogo.dati?.carte ?? [],
      stesa: catalogo.dati?.stese ?? [],
      articolo: (pubblicati.dati?.articoli ?? [])
        .filter((a) => a.id !== articoloSalvato?.id)
        .map((a) => ({ id: a.slug, nome: a.titolo })),
    }),
    [catalogo.dati, pubblicati.dati, articoloSalvato],
  );

  /* ---- salvataggio ---- */

  const salva = async (cambia?: Partial<Forma>): Promise<Articolo | null> => {
    const daScrivere = { ...forma, ...cambia };
    if (!daScrivere.titolo.trim()) {
      setEsito(null);
      setVista("scrivi");
      return null;
    }
    setEsito(null);
    const risposta = await esegui((t) =>
      articoloSalvato
        ? modificaArticolo(t, articoloSalvato.id, inCorpo(daScrivere))
        : creaArticolo(t, inCorpo(daScrivere)),
    );
    if (!risposta) return null;
    const scritta = daArticolo(risposta);
    setArticoloSalvato(risposta);
    setForma(scritta);
    setSalvata(scritta);
    setEsito(
      risposta.stato === "pubblicato"
        ? risposta.programmato ? "Salvato: uscirà alla data indicata." : "Salvato e pubblicato."
        : "Salvato.",
    );
    versioni.ricarica();
    if (nuovo) router.replace(`/blog/${risposta.id}`);
    return risposta;
  };

  const pubblica = () => void salva({ stato: "pubblicato" });

  const cambiaSoloStato = async (azione: "bozza" | "archivia") => {
    if (!articoloSalvato) return;
    if (modificato && !(await salva())) return;
    const r = await esegui((t) => cambiaStato(t, articoloSalvato.id, azione));
    if (r) {
      const scritta = daArticolo(r);
      setArticoloSalvato(r);
      setForma(scritta);
      setSalvata(scritta);
      setEsito(azione === "bozza" ? "Riportato a bozza." : "Archiviato.");
    }
  };

  const elimina = async () => {
    if (!articoloSalvato) return;
    if ((await esegui((t) => eliminaArticolo(t, articoloSalvato.id))) !== null) {
      setSalvata(forma);
      router.push("/blog");
    }
  };

  const [linguaTraduzione, setLinguaTraduzione] = useState("");

  const generaTraduzione = async () => {
    if (!articoloSalvato) return;
    const lang = linguaTraduzione.trim().toLowerCase();
    if (!lang) return;
    const r = await esegui((t) => traduciArticolo(t, articoloSalvato.id, lang));
    if (r) {
      setArticoloSalvato({
        ...articoloSalvato,
        traduzioni: [...articoloSalvato.traduzioni, { id: r.id, lang: r.lang, slug: r.slug, stato: r.stato }],
      });
      setLinguaTraduzione("");
      setEsito(`Bozza tradotta creata (${r.lang}): da rivedere prima di pubblicarla.`);
    }
  };

  const ripristinaVersione = async (revisione: number) => {
    if (!articoloSalvato) return;
    const r = await esegui((t) => ripristina(t, articoloSalvato.id, revisione));
    if (r) {
      const scritta = daArticolo(r);
      setArticoloSalvato(r);
      setForma(scritta);
      setSalvata(scritta);
      setEsito("Versione ripristinata (quella di prima resta nell'elenco).");
      versioni.ricarica();
    }
  };

  /* ---- il testo ---- */

  /* Applica una trasformazione alla selezione e rimette il cursore dove serve. */
  const modificaTesto = (
    trasforma: (prima: string, scelto: string, dopo: string) => { testo: string; da: number; a: number },
  ) => {
    const el = area.current;
    const inizio = el?.selectionStart ?? forma.testo.length;
    const fine = el?.selectionEnd ?? forma.testo.length;
    const r = trasforma(forma.testo.slice(0, inizio), forma.testo.slice(inizio, fine), forma.testo.slice(fine));
    imposta("testo", r.testo);
    requestAnimationFrame(() => {
      el?.focus();
      el?.setSelectionRange(r.da, r.a);
    });
  };

  const avvolgi = (prefisso: string, suffisso: string, segnaposto: string) =>
    modificaTesto((prima, scelto, dopo) => {
      const dentro = scelto || segnaposto;
      return {
        testo: `${prima}${prefisso}${dentro}${suffisso}${dopo}`,
        da: prima.length + prefisso.length,
        a: prima.length + prefisso.length + dentro.length,
      };
    });

  /* Un prefisso all'inizio di ogni riga toccata dalla selezione (titoli, elenchi, citazioni). */
  const perRiga = (prefisso: string) =>
    modificaTesto((prima, scelto, dopo) => {
      const inizioRiga = prima.lastIndexOf("\n") + 1;
      const testoRighe = (prima.slice(inizioRiga) + scelto).split("\n").map((r) => prefisso + r).join("\n");
      const nuovaPrima = prima.slice(0, inizioRiga);
      return {
        testo: nuovaPrima + testoRighe + dopo,
        da: nuovaPrima.length + prefisso.length,
        a: nuovaPrima.length + testoRighe.length,
      };
    });

  const inserisci = (blocco: string) =>
    modificaTesto((prima, _scelto, dopo) => {
      const testo = `${prima}${prima && !prima.endsWith("\n\n") ? (prima.endsWith("\n") ? "\n" : "\n\n") : ""}${blocco}\n\n${dopo}`;
      const posizione = testo.length - dopo.length;
      return { testo, da: posizione, a: posizione };
    });

  const scelgoImmagineNelTesto = (i: Immagine) => {
    inserisci(markdownImmagine(i, forma.immagineAlt));
    setPannello(null);
  };

  const scelgoCopertina = (i: Immagine) => {
    setForma((f) => ({ ...f, immagineId: i.id, immagineUrl: i.url }));
    setPannello(null);
  };

  const opzioniRif = riferimenti[tipoRif];
  const rifScelto = opzioniRif.find((o) => o.id === idRif) ?? opzioniRif[0];

  /* ---- etichette ---- */

  const aggiungiEtichetta = (nome: string) => {
    const pulito = nome.replace(/[,;]+/g, " ").replace(/\s+/g, " ").trim().slice(0, 80);
    if (!pulito || forma.tags.length >= MAX_ETICHETTE) return;
    if (forma.tags.some((t) => t.toLowerCase() === pulito.toLowerCase())) return;
    imposta("tags", [...forma.tags, pulito]);
    setNuovaEtichetta("");
  };

  const suggerite = (etichetteNote.dati ?? [])
    .filter((e) => !forma.tags.some((t) => t.toLowerCase() === e.nome.toLowerCase()))
    .sort((a, b) => b.n - a.n)
    .slice(0, 10);

  /* ---- i numeri ---- */

  const parole = forma.testo.trim() ? forma.testo.trim().split(/\s+/).length : 0;
  const titoloSeo = forma.seoTitolo.trim() || forma.titolo.trim();
  const descrizioneSeo = forma.seoDescrizione.trim() || semplice(forma.testo).slice(0, DESCRIZIONE_SEO_IDEALE);
  const stato = articoloSalvato ? etichettaStato(articoloSalvato) : null;
  const dataFutura = forma.pubblicatoIl !== "" && new Date(forma.pubblicatoIl).getTime() > adesso;
  const senzaTitolo = !forma.titolo.trim();
  /* Ciò che il server controlla: l'articolo com'è adesso, anche non salvato. */
  const datiSeo: DatiControlloSeo = {
    titolo: forma.titolo.trim(),
    sottotitolo: forma.sottotitolo.trim() || null,
    testo: forma.testo,
    slug: forma.slug.trim(),
    seo_titolo: forma.seoTitolo.trim() || null,
    seo_descrizione: forma.seoDescrizione.trim() || null,
    seo_parola_chiave: forma.parolaChiave.trim() || null,
    immagine_presente: forma.immagineId !== null,
    immagine_alt: forma.immagineAlt.trim() || null,
    tags: forma.tags,
    faq: faqCompleta(forma.faq),
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <p style={{ margin: 0, fontSize: "0.8125rem" }}>
            <Link href="/blog">← Tutti gli articoli</Link>
          </p>
          <h1 className={comuni.titolo}>{nuovo ? "Nuovo articolo" : "Modifica articolo"}</h1>
          {stato && articoloSalvato && (
            <p className={comuni.sottotitolo}>
              <span className={`${comuni.stato} ${stato.classe}`}>{stato.testo}</span> · creato{" "}
              {quandoCompleto(articoloSalvato.creato)}, modificato {quandoCompleto(articoloSalvato.aggiornato)} ·{" "}
              {articoloSalvato.tempo_lettura} min di lettura
            </p>
          )}
        </div>
      </div>

      {errore && (
        <p className={comuni.errore} role="alert">
          {errore}
        </p>
      )}
      {esito && !errore && (
        <p className={comuni.esito} role="status">
          {esito}
        </p>
      )}

      <div className={stili.editor}>
        {/* ---- colonna principale: scrivere ---- */}
        <div className={stili.colonna}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Titolo</span>
            <input
              className={`${comuni.ingresso} ${stili.titoloGrande}`}
              value={forma.titolo}
              maxLength={200}
              aria-required="true"
              aria-invalid={senzaTitolo && esito === null && modificato ? true : undefined}
              onChange={(e) => imposta("titolo", e.target.value)}
              placeholder="Il titolo dell'articolo"
            />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Sottotitolo</span>
            <input
              className={comuni.ingresso}
              value={forma.sottotitolo}
              maxLength={300}
              onChange={(e) => imposta("sottotitolo", e.target.value)}
              placeholder="Facoltativo: una riga che spiega di che cosa si parla"
            />
          </label>

          <div>
            <div className={stili.commutatore} role="group" aria-label="Vista del testo">
              <button type="button" aria-pressed={vista === "scrivi"} onClick={() => setVista("scrivi")}>
                Scrivi
              </button>
              <button type="button" aria-pressed={vista === "anteprima"} onClick={() => setVista("anteprima")}>
                Anteprima
              </button>
            </div>
          </div>

          {vista === "scrivi" ? (
            <div>
              <div className={stili.strumenti} role="toolbar" aria-label="Formattazione">
                <button type="button" className={stili.strumento} title="Grassetto" onClick={() => avvolgi("**", "**", "grassetto")}>
                  <strong>G</strong>
                </button>
                <button type="button" className={stili.strumento} title="Corsivo" onClick={() => avvolgi("*", "*", "corsivo")}>
                  <em>C</em>
                </button>
                <button type="button" className={stili.strumento} title="Titolo di sezione" onClick={() => perRiga("## ")}>
                  Titolo
                </button>
                <button type="button" className={stili.strumento} title="Sottotitolo di sezione" onClick={() => perRiga("### ")}>
                  Sotto
                </button>
                <button type="button" className={stili.strumento} title="Elenco puntato" onClick={() => perRiga("- ")}>
                  Elenco
                </button>
                <button type="button" className={stili.strumento} title="Citazione" onClick={() => perRiga("> ")}>
                  Citazione
                </button>
                <button type="button" className={stili.strumento} title="Collegamento" onClick={() => avvolgi("[", "](https://)", "testo del link")}>
                  Link
                </button>
                <button
                  type="button"
                  className={stili.strumento}
                  aria-expanded={pannello === "immagine"}
                  onClick={() => setPannello(pannello === "immagine" ? null : "immagine")}
                >
                  Immagine
                </button>
                <button
                  type="button"
                  className={stili.strumento}
                  aria-expanded={pannello === "riferimento"}
                  title="Una carta, una stesa o un altro articolo"
                  onClick={() => setPannello(pannello === "riferimento" ? null : "riferimento")}
                >
                  Carta / stesa / articolo
                </button>
              </div>

              {pannello === "immagine" && (
                <SelettoreImmagine alScelta={scelgoImmagineNelTesto} chiudi={() => setPannello(null)} />
              )}

              {pannello === "riferimento" && (
                <div className={stili.selettore} role="dialog" aria-label="Inserisci un riferimento">
                  <p className={comuni.riquadroNota}>
                    Da sola su una riga diventa una scheda (con l&apos;immagine, se è una carta); dentro una frase, un
                    collegamento. Un riferimento che non esiste sparisce dal sito senza avvisare.
                  </p>
                  <div className={comuni.riga}>
                    <label className={comuni.campo}>
                      <span className={comuni.campoEtichetta}>Che cosa</span>
                      <select
                        className={comuni.selezione}
                        value={tipoRif}
                        onChange={(e) => {
                          setTipoRif(e.target.value as typeof tipoRif);
                          setIdRif("");
                        }}
                      >
                        <option value="carta">Una carta</option>
                        <option value="stesa">Una stesa</option>
                        <option value="articolo">Un articolo</option>
                      </select>
                    </label>
                    <label className={comuni.campo}>
                      <span className={comuni.campoEtichetta}>Quale</span>
                      <select className={comuni.selezione} value={rifScelto?.id ?? ""} onChange={(e) => setIdRif(e.target.value)}>
                        {opzioniRif.length === 0 && <option value="">Nessuna voce</option>}
                        {opzioniRif.map((o) => (
                          <option key={o.id} value={o.id}>
                            {o.nome}
                          </option>
                        ))}
                      </select>
                    </label>
                    <button
                      type="button"
                      className={comuni.primaria}
                      style={{ height: 44, marginBottom: "0.9rem" }}
                      disabled={!rifScelto}
                      onClick={() => {
                        if (!rifScelto) return;
                        inserisci(`[[${tipoRif}:${rifScelto.id}]]`);
                        setPannello(null);
                      }}
                    >
                      Inserisci
                    </button>
                  </div>
                </div>
              )}

              <label className={comuni.campo} style={{ marginBottom: 0 }}>
                <span className={comuni.campoEtichetta}>Testo (Markdown)</span>
                <textarea
                  ref={area}
                  className={`${comuni.area} ${stili.testoArea}`}
                  value={forma.testo}
                  maxLength={200000}
                  spellCheck
                  onChange={(e) => imposta("testo", e.target.value)}
                  placeholder="Scrivi qui. ## per un titolo di sezione, **grassetto**, *corsivo*, - per gli elenchi."
                />
              </label>
              <p className={stili.contatori}>
                <span>{parole} parole</span>
                <span>≈ {Math.max(1, Math.round(parole / 200))} min di lettura</span>
                <span>{forma.testo.length} / 200000 caratteri</span>
              </p>
            </div>
          ) : (
            <Anteprima
              titolo={forma.titolo}
              sottotitolo={forma.sottotitolo}
              testo={forma.testo}
              catalogo={{ carte: riferimenti.carta, stese: riferimenti.stesa }}
            />
          )}
        </div>

        {/* ---- colonna laterale: pubblicazione e metadati ---- */}
        <aside className={stili.colonna} aria-label="Impostazioni dell'articolo">
          <section className={stili.pannello} aria-labelledby="pubblicazione">
            <h2 id="pubblicazione" className={stili.pannelloTitolo}>
              Pubblicazione
            </h2>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Stato</span>
              <select
                className={comuni.selezione}
                value={forma.stato}
                onChange={(e) => imposta("stato", e.target.value as StatoArticolo)}
              >
                <option value="bozza">Bozza (solo in console)</option>
                <option value="pubblicato">Pubblicato</option>
                <option value="archiviato">Archiviato (non più visibile)</option>
              </select>
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Data di pubblicazione</span>
              <input
                className={comuni.ingresso}
                type="datetime-local"
                value={forma.pubblicatoIl}
                onChange={(e) => imposta("pubblicatoIl", e.target.value)}
              />
              <span className={comuni.campoAiuto}>
                Vuota: parte da adesso. Una data futura, con lo stato «Pubblicato», programma l&apos;uscita.
              </span>
            </label>
            <label className={stili.interruttore}>
              <input type="checkbox" checked={forma.inEvidenza} onChange={(e) => imposta("inEvidenza", e.target.checked)} />
              In evidenza in cima al blog
            </label>
            <label className={stili.interruttore}>
              <input type="checkbox" checked={forma.commentiAperti} onChange={(e) => imposta("commentiAperti", e.target.checked)} />
              Commenti aperti
            </label>
          </section>

          <section className={stili.pannello} aria-labelledby="posizione">
            <h2 id="posizione" className={stili.pannelloTitolo}>
              Sezione e lingua
            </h2>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Sezione</span>
              <select className={comuni.selezione} value={forma.sezioneId} onChange={(e) => imposta("sezioneId", e.target.value)}>
                <option value="">Senza sezione</option>
                {albero.map((v) => (
                  <option key={v.sezione.id} value={v.sezione.id}>
                    {"— ".repeat(v.livello)}
                    {v.sezione.nome}
                    {v.sezione.visibile ? "" : " (nascosta)"}
                  </option>
                ))}
              </select>
              <span className={comuni.campoAiuto}>Gli articoli stanno nelle sezioni di tipo «articoli».</span>
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Lingua dell&apos;articolo</span>
              <select className={comuni.selezione} value={forma.lang} onChange={(e) => imposta("lang", e.target.value)}>
                {LINGUE.map(([codice, nome]) => (
                  <option key={codice} value={codice}>
                    {nome}
                  </option>
                ))}
              </select>
              <span className={comuni.campoAiuto}>
                Il sito è in inglese (lingua principale per i motori di ricerca) e in italiano: l&apos;articolo sta
                nell&apos;indirizzo della sua lingua.
              </span>
            </label>
          </section>

          <section className={stili.pannello} aria-labelledby="copertina">
            <h2 id="copertina" className={stili.pannelloTitolo}>
              Immagine di copertina
            </h2>
            {forma.immagineUrl ? (
              // eslint-disable-next-line @next/next/no-img-element -- copertina dalla libreria
              <img className={stili.copertinaAnteprima} src={urlMedia(forma.immagineUrl) ?? ""} alt={forma.immagineAlt} />
            ) : (
              <p className={comuni.riquadroNota}>Nessuna copertina: sul sito l&apos;articolo comparirà senza immagine.</p>
            )}
            <div className={comuni.riga} style={{ marginBottom: "0.9rem" }}>
              <button
                type="button"
                className={comuni.secondaria}
                style={{ height: 44 }}
                aria-expanded={pannello === "copertina"}
                onClick={() => setPannello(pannello === "copertina" ? null : "copertina")}
              >
                {forma.immagineUrl ? "Cambia" : "Scegli o carica"}
              </button>
              {forma.immagineUrl && (
                <button
                  type="button"
                  className={comuni.secondaria}
                  style={{ height: 44 }}
                  onClick={() => setForma((f) => ({ ...f, immagineId: null, immagineUrl: null }))}
                >
                  Togli
                </button>
              )}
            </div>
            {pannello === "copertina" && (
              <SelettoreImmagine scelta={forma.immagineId} alScelta={scelgoCopertina} chiudi={() => setPannello(null)} />
            )}
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Testo alternativo</span>
              <input
                className={comuni.ingresso}
                value={forma.immagineAlt}
                maxLength={200}
                onChange={(e) => imposta("immagineAlt", e.target.value)}
                placeholder="Che cosa mostra l'immagine"
              />
              <span className={comuni.campoAiuto}>Lo leggono i lettori di schermo e i motori di ricerca.</span>
            </label>
          </section>

          <section className={stili.pannello} aria-labelledby="etichette">
            <h2 id="etichette" className={stili.pannelloTitolo}>
              Etichette
            </h2>
            {forma.tags.length > 0 && (
              <ul className={stili.chips} aria-label="Etichette dell'articolo" style={{ listStyle: "none", padding: 0 }}>
                {forma.tags.map((t) => (
                  <li key={t} className={stili.chip}>
                    {t}
                    <button type="button" aria-label={`Togli l'etichetta ${t}`} onClick={() => imposta("tags", forma.tags.filter((x) => x !== t))}>
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className={comuni.riga}>
              <label className={comuni.campo} style={{ marginBottom: "0.9rem" }}>
                <span className={comuni.campoEtichetta}>Aggiungi</span>
                <input
                  className={comuni.ingresso}
                  value={nuovaEtichetta}
                  maxLength={80}
                  disabled={forma.tags.length >= MAX_ETICHETTE}
                  onChange={(e) => setNuovaEtichetta(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === ",") {
                      e.preventDefault();
                      aggiungiEtichetta(nuovaEtichetta);
                    }
                  }}
                  placeholder={forma.tags.length >= MAX_ETICHETTE ? `Al massimo ${MAX_ETICHETTE}` : "Invio o virgola per aggiungere"}
                />
              </label>
              <button
                type="button"
                className={comuni.secondaria}
                style={{ height: 44, marginBottom: "0.9rem" }}
                disabled={!nuovaEtichetta.trim() || forma.tags.length >= MAX_ETICHETTE}
                onClick={() => aggiungiEtichetta(nuovaEtichetta)}
              >
                Aggiungi
              </button>
            </div>
            {suggerite.length > 0 && forma.tags.length < MAX_ETICHETTE && (
              <div className={stili.suggerimenti} aria-label="Etichette già usate">
                {suggerite.map((e) => (
                  <button key={e.id} type="button" className={stili.suggerimento} onClick={() => aggiungiEtichetta(e.nome)}>
                    + {e.nome}
                  </button>
                ))}
              </div>
            )}
          </section>

          <PannelloSeo dati={datiSeo} />

          <section className={stili.pannello} aria-labelledby="seo">
            <h2 id="seo" className={stili.pannelloTitolo}>
              Motori di ricerca
            </h2>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Parola chiave principale</span>
              <input
                className={comuni.ingresso}
                value={forma.parolaChiave}
                maxLength={120}
                onChange={(e) => imposta("parolaChiave", e.target.value)}
                placeholder="La frase con cui vuoi essere trovato, per esempio «the tower tarot meaning»"
              />
              <span className={comuni.campoAiuto}>
                Una sola, nella lingua dell&apos;articolo. Il controllo verifica che stia nel titolo, nella descrizione, nel
                primo paragrafo e in un titolo di sezione — senza ripeterla a sproposito.
              </span>
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Parole chiave secondarie</span>
              <input
                className={comuni.ingresso}
                value={forma.paroleSecondarie}
                onChange={(e) => imposta("paroleSecondarie", e.target.value)}
                placeholder="Separate da virgole (al massimo dieci)"
              />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Indirizzo (slug)</span>
              <input
                className={comuni.ingresso}
                value={forma.slug}
                maxLength={160}
                onChange={(e) => imposta("slug", e.target.value)}
                placeholder={nuovo ? "Vuoto: lo ricava dal titolo" : ""}
              />
              <span className={comuni.campoAiuto}>
                Cambiarlo cambia l&apos;indirizzo pubblico: i vecchi collegamenti smettono di funzionare.
              </span>
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>
                Titolo per i motori{" "}
                <span className={`${stili.conta} ${forma.seoTitolo.length > TITOLO_SEO_IDEALE ? stili.contaTroppo : ""}`}>
                  {forma.seoTitolo.length}/{TITOLO_SEO_IDEALE}
                </span>
              </span>
              <input
                className={comuni.ingresso}
                value={forma.seoTitolo}
                maxLength={200}
                onChange={(e) => imposta("seoTitolo", e.target.value)}
                placeholder="Vuoto: usa il titolo dell'articolo"
              />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>
                Descrizione{" "}
                <span className={`${stili.conta} ${forma.seoDescrizione.length > DESCRIZIONE_SEO_IDEALE ? stili.contaTroppo : ""}`}>
                  {forma.seoDescrizione.length}/{DESCRIZIONE_SEO_IDEALE}
                </span>
              </span>
              <textarea
                className={comuni.area}
                style={{ minHeight: "5rem", fontFamily: "inherit", fontSize: "1rem" }}
                value={forma.seoDescrizione}
                maxLength={320}
                onChange={(e) => imposta("seoDescrizione", e.target.value)}
                placeholder="Vuoto: le prime parole del testo"
              />
            </label>
            <div className={comuni.riquadroNota} aria-label="Come apparirà in un risultato di ricerca" style={{ marginBottom: "0.9rem" }}>
              <div style={{ color: "var(--rubrica)", fontSize: "1rem" }}>
                {(titoloSeo || "Titolo dell'articolo").slice(0, 70)}
              </div>
              <div className={comuni.mono}>
                {forma.lang === "it" ? "/it" : ""}/blog/{forma.slug || "…"}
              </div>
              <div>{descrizioneSeo || "La descrizione comparirà qui."}</div>
            </div>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Indirizzo canonico</span>
              <input
                className={comuni.ingresso}
                type="url"
                inputMode="url"
                value={forma.canonical}
                maxLength={500}
                onChange={(e) => imposta("canonical", e.target.value)}
                placeholder="Vuoto: la pagina è l'originale"
              />
              <span className={comuni.campoAiuto}>
                Solo se questo testo è già pubblicato altrove: l&apos;indirizzo https della versione originale. Un motore di
                ricerca la preferirà a questa.
              </span>
            </label>
            <label className={stili.interruttore}>
              <input type="checkbox" checked={forma.noindex} onChange={(e) => imposta("noindex", e.target.checked)} />
              Non indicizzare (resta leggibile, ma fuori dai motori di ricerca e dalla mappa del sito)
            </label>
          </section>

          <section className={stili.pannello} aria-labelledby="faq">
            <h2 id="faq" className={stili.pannelloTitolo}>
              Domande frequenti
            </h2>
            <p className={comuni.riquadroNota}>
              Compaiono in fondo all&apos;articolo e diventano dati strutturati FAQ: possono uscire come risposte
              espandibili nei risultati di ricerca. Scrivi domande vere, con risposte brevi.
            </p>
            {forma.faq.length > 0 && (
              <ul className={stili.domandeFaq} aria-label="Domande frequenti dell'articolo">
                {forma.faq.map((f, i) => (
                  <li key={i} className={stili.domandaFaq}>
                    <label className={comuni.campo}>
                      <span className={comuni.campoEtichetta}>Domanda {i + 1}</span>
                      <input
                        className={comuni.ingresso}
                        value={f.domanda}
                        maxLength={FAQ_DOMANDA_MAX}
                        onChange={(e) => imposta("faq", forma.faq.map((x, k) => (k === i ? { ...x, domanda: e.target.value } : x)))}
                      />
                    </label>
                    <label className={comuni.campo}>
                      <span className={comuni.campoEtichetta}>Risposta</span>
                      <textarea
                        className={comuni.area}
                        style={{ minHeight: "5rem", fontFamily: "inherit", fontSize: "1rem" }}
                        value={f.risposta}
                        maxLength={FAQ_RISPOSTA_MAX}
                        onChange={(e) => imposta("faq", forma.faq.map((x, k) => (k === i ? { ...x, risposta: e.target.value } : x)))}
                      />
                    </label>
                    <button
                      type="button"
                      className={comuni.secondaria}
                      style={{ height: 44, marginBottom: "0.9rem" }}
                      onClick={() => imposta("faq", forma.faq.filter((_, k) => k !== i))}
                    >
                      Togli la domanda {i + 1}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <button
              type="button"
              className={comuni.secondaria}
              style={{ height: 44, marginBottom: "0.9rem" }}
              disabled={forma.faq.length >= FAQ_MAX}
              onClick={() => imposta("faq", [...forma.faq, { domanda: "", risposta: "" }])}
            >
              {forma.faq.length >= FAQ_MAX ? `Al massimo ${FAQ_MAX}` : "Aggiungi una domanda"}
            </button>
          </section>

          {!nuovo && articoloSalvato && (
            <section className={stili.pannello} aria-labelledby="traduzioni">
              <h2 id="traduzioni" className={stili.pannelloTitolo}>
                Traduzioni (v5)
              </h2>
              <p className={comuni.riquadroNota}>
                Generata dal modello, sempre come bozza nuova da rivedere prima di pubblicare — non tocca
                questo articolo. Richiede un modello LLM configurato e funzionante.
              </p>
              {articoloSalvato.tradotto_da_id && (
                <p className={comuni.riquadroNota}>Questo articolo è a sua volta una traduzione generata.</p>
              )}
              {articoloSalvato.traduzioni.length > 0 && (
                <ul className={stili.versioni}>
                  {articoloSalvato.traduzioni.map((t) => (
                    <li key={t.id} className={stili.versione}>
                      <span className={stili.versioneTitolo}>{t.lang}</span>
                      <span>{t.stato}</span>
                      <Link href={`/blog/${t.id}`} className={comuni.secondaria} style={{ height: 44, display: "inline-flex", alignItems: "center", padding: "0 1rem" }}>
                        Apri
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
              <div className={stili.azioniModulo}>
                <input
                  type="text"
                  value={linguaTraduzione}
                  onChange={(e) => setLinguaTraduzione(e.target.value)}
                  placeholder="es. hu"
                  maxLength={5}
                  style={{ width: 100 }}
                  aria-label="Codice della lingua di arrivo"
                />
                <button
                  type="button"
                  className={comuni.secondaria}
                  style={{ height: 44 }}
                  disabled={inCorso || !linguaTraduzione.trim() || modificato}
                  title={modificato ? "Salva prima le modifiche" : undefined}
                  onClick={generaTraduzione}
                >
                  Genera traduzione
                </button>
              </div>
            </section>
          )}

          {!nuovo && (
            <section className={stili.pannello} aria-labelledby="versioni">
              <h2 id="versioni" className={stili.pannelloTitolo}>
                Versioni precedenti
              </h2>
              {versioni.dati && versioni.dati.length > 0 ? (
                <ul className={stili.versioni}>
                  {versioni.dati.map((v) => (
                    <li key={v.id} className={stili.versione}>
                      <span className={stili.versioneTitolo}>{v.titolo}</span>
                      <span>
                        {quandoCompleto(v.quando)} · {v.testo.split(/\s+/).filter(Boolean).length} parole
                      </span>
                      <button
                        type="button"
                        className={comuni.secondaria}
                        style={{ height: 44 }}
                        disabled={inCorso || modificato}
                        title={modificato ? "Salva prima le modifiche" : undefined}
                        onClick={() => ripristinaVersione(v.id)}
                      >
                        Ripristina
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className={comuni.riquadroNota}>
                  Nessuna: si conserva la versione di prima a ogni modifica del titolo o del testo (le ultime venti).
                </p>
              )}
            </section>
          )}

          {!nuovo && (
            <section className={stili.pannello} aria-labelledby="zona">
              <h2 id="zona" className={stili.pannelloTitolo}>
                Altre azioni
              </h2>
              <div className={stili.azioniModulo}>
                {articoloSalvato?.stato === "pubblicato" && (
                  <button type="button" className={comuni.secondaria} style={{ height: 44 }} disabled={inCorso} onClick={() => cambiaSoloStato("bozza")}>
                    Riporta a bozza
                  </button>
                )}
                {articoloSalvato?.stato !== "archiviato" && (
                  <button type="button" className={comuni.secondaria} style={{ height: 44 }} disabled={inCorso} onClick={() => cambiaSoloStato("archivia")}>
                    Archivia
                  </button>
                )}
                {eliminando ? (
                  <span className={stili.conferma} role="alert">
                    Eliminare per sempre?
                    <button type="button" className={comuni.distruttiva} style={{ height: 44 }} disabled={inCorso} onClick={elimina}>
                      Sì, elimina
                    </button>
                    <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setEliminando(false)}>
                      Annulla
                    </button>
                  </span>
                ) : (
                  <button type="button" className={comuni.distruttiva} style={{ height: 44 }} disabled={inCorso} onClick={() => setEliminando(true)}>
                    Elimina
                  </button>
                )}
              </div>
            </section>
          )}
        </aside>
      </div>

      {/* ---- la barra dei comandi resta in vista: si salva senza tornare in cima ---- */}
      <div className={stili.barraAzioni}>
        <span className={`${comuni.stato} ${modificato ? comuni.negativo : comuni.neutro} ${stili.stato}`} role="status">
          {inCorso ? "Salvataggio…" : modificato ? "Modifiche non salvate" : nuovo ? "Non ancora salvato" : "Tutto salvato"}
        </span>
        <button
          type="button"
          className={comuni.secondaria}
          style={{ height: 44 }}
          disabled={inCorso || senzaTitolo || (!modificato && !nuovo)}
          onClick={() => void salva()}
        >
          Salva
        </button>
        {forma.stato !== "pubblicato" && (
          <button type="button" className={comuni.primaria} style={{ height: 44 }} disabled={inCorso || senzaTitolo} onClick={pubblica}>
            {dataFutura ? "Programma" : "Pubblica"}
          </button>
        )}
      </div>
    </>
  );
}
