"use client";

/* Le immagini di un mazzo nel sito: uno ZIP o una cartella con le 78 carte e il dorso. Il server riconosce i file
 * (il nome senza estensione è l'id della carta, come per `tools/installa_mazzo.py`), controlla che ci sia tutto, li
 * converte in WebP alla misura web e li conserva: il sito li mostra subito, senza rilascio.
 *
 * - ZIP: una richiesta sola, con l'avanzamento dell'invio; poi il server scompatta e pubblica.
 * - Cartella (scelta o trascinata): la console la controlla prima di caricare (cosa manca, cosa avanza, i
 *   doppioni), poi manda le immagini una per volta nella bozza — tre alla volta, con la barra — e alla fine chiede
 *   di pubblicarle. Il sito non vede mai un mazzo a metà: o la serie nuova completa, o quella di prima.
 *
 * Separato dall'«Archivio ZIP da scaricare» (Fase I) che sta sotto: quello conserva lo ZIP così com'è per
 * installarlo a mano come file del sito, e non mette niente online. */

import { useRef, useState, type DragEvent } from "react";
import {
  ErroreImmagini, caricaFileImmagine, caricaZipImmagini, eliminaImmagini, pubblicaBozzaImmagini, riconosciFile,
  scartaBozzaImmagini, statoImmagini, urlCartaMazzo, type RiepilogoImmagini, type StatoImmagini,
} from "@/lib/mazzi";
import { useDati, useToken } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./immagini.module.css";

interface FileScelto {
  percorso: string;
  file: File;
}

interface Avanzamento {
  testo: string;
  /** `null`: si aspetta il server, durata sconosciuta (barra indeterminata). */
  valore: number | null;
  massimo: number;
}

const IN_PARALLELO = 3;
const ANTEPRIME = ["maj-00", "maj-06", "maj-17", "dorso"];

export function PannelloImmagini({ slug, predefinito }: { slug: string; predefinito: boolean }) {
  if (predefinito) {
    return (
      <p className={comuni.riquadroNota}>
        Il mazzo predefinito (il Thoth) usa le immagini del sito, in <code>frontend/public/cards/</code>: non si
        caricano da qui.
      </p>
    );
  }
  return <Caricamento slug={slug} />;
}

function comeErrore(e: unknown): ErroreImmagini {
  if (e instanceof ErroreImmagini) return e;
  return new ErroreImmagini(e instanceof Error ? e.message : "Il caricamento non è riuscito.", 0);
}

/** I file di una cartella trascinata: le voci si leggono una cartella alla volta (`readEntries` ne dà a blocchi). */
async function leggiVoce(voce: FileSystemEntry, uscita: FileScelto[]): Promise<void> {
  if (voce.isFile) {
    const file = await new Promise<File>((ok, ko) => (voce as FileSystemFileEntry).file(ok, ko));
    uscita.push({ percorso: voce.fullPath.replace(/^\/+/, ""), file });
    return;
  }
  if (!voce.isDirectory) return;
  const lettore = (voce as FileSystemDirectoryEntry).createReader();
  for (;;) {
    const blocco = await new Promise<FileSystemEntry[]>((ok, ko) => lettore.readEntries(ok, ko));
    if (blocco.length === 0) return;
    for (const figlia of blocco) await leggiVoce(figlia, uscita);
  }
}

function Caricamento({ slug }: { slug: string }) {
  const token = useToken();
  const { dati: stato, errore: erroreLettura, ricarica } = useDati((t) => statoImmagini(t, slug), [slug]);
  const [avanzamento, setAvanzamento] = useState<Avanzamento | null>(null);
  const [errore, setErrore] = useState<ErroreImmagini | null>(null);
  const [riepilogo, setRiepilogo] = useState<RiepilogoImmagini | null>(null);
  const [sopra, setSopra] = useState(false);
  const inputZip = useRef<HTMLInputElement>(null);
  const inputCartella = useRef<HTMLInputElement>(null);
  const occupato = avanzamento !== null;
  const idZip = `zip-${slug}`;
  const idCartella = `cartella-${slug}`;

  const avvia = async (lavoro: (t: string) => Promise<StatoImmagini>) => {
    if (token === null || occupato) return;
    setErrore(null);
    setRiepilogo(null);
    try {
      const esito = await lavoro(token);
      setRiepilogo(esito.riepilogo ?? null);
    } catch (e) {
      setErrore(comeErrore(e));
    } finally {
      setAvanzamento(null);
      ricarica();
    }
  };

  const caricaZip = (file: File) => avvia((t) => {
    setAvanzamento({ testo: `Invio di ${file.name}…`, valore: 0, massimo: 1 });
    return caricaZipImmagini(t, slug, file, (frazione) => setAvanzamento(
      frazione < 1
        ? { testo: `Invio di ${file.name}: ${Math.round(frazione * 100)}%`, valore: frazione, massimo: 1 }
        : { testo: "Il server scompatta lo ZIP, controlla le carte e le converte…", valore: null, massimo: 1 },
    ));
  });

  const caricaCartella = (file: FileScelto[]) => {
    if (!stato || occupato) return;
    setRiepilogo(null);
    const attesi = stato.ids_attesi;
    const r = riconosciFile(file.map((f) => f.percorso), new Set(attesi));
    const mancanti = attesi.filter((id) => !r.scelti.has(id));
    if (mancanti.length > 0 || r.doppioni.size > 0) {
      const parti = [
        mancanti.length > 0 ? `mancano ${mancanti.length} file su ${attesi.length}` : "",
        r.doppioni.size > 0 ? `${r.doppioni.size} carte compaiono più volte` : "",
      ].filter(Boolean);
      setErrore(new ErroreImmagini(
        `La cartella non è completa: ${parti.join(", ")}. Non ho caricato niente.`, 0, mancanti, r.avanzano,
        [...r.doppioni].map(([id, percorsi]) => `${id}: ${percorsi.join(", ")}`),
      ));
      return;
    }
    void avvia(async (t) => {
      const scelti = [...r.scelti.values()].map((i) => file[i]);
      setAvanzamento({ testo: `Caricate 0 di ${scelti.length} immagini`, valore: 0, massimo: scelti.length });
      await scartaBozzaImmagini(t, slug);
      const coda = [...scelti];
      let fatti = 0;
      let fermo = false;
      const lavoratore = async () => {
        while (!fermo && coda.length > 0) {
          const prossimo = coda.shift()!;
          try {
            await caricaFileImmagine(t, slug, prossimo.percorso, prossimo.file);
          } catch (e) {
            fermo = true;
            throw e;
          }
          fatti += 1;
          setAvanzamento({ testo: `Caricate ${fatti} di ${scelti.length} immagini`, valore: fatti, massimo: scelti.length });
        }
      };
      await Promise.all(Array.from({ length: IN_PARALLELO }, lavoratore));
      setAvanzamento({ testo: "Pubblicazione delle immagini…", valore: null, massimo: 1 });
      const esito = await pubblicaBozzaImmagini(t, slug);
      return { ...esito, riepilogo: { installate: esito.pubblicate, avanzano: r.avanzano, ignorati: r.ignorati.length } };
    });
  };

  const scegliCartella = (elenco: FileList | null) => {
    if (!elenco || elenco.length === 0) return;
    caricaCartella([...elenco].map((f) => ({ percorso: f.webkitRelativePath || f.name, file: f })));
    if (inputCartella.current) inputCartella.current.value = "";
  };

  const scegliZip = (elenco: FileList | null) => {
    const file = elenco?.[0];
    if (file) void caricaZip(file);
    if (inputZip.current) inputZip.current.value = "";
  };

  const lascia = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setSopra(false);
    if (occupato) return;
    /* Le voci si prendono subito: dopo il primo `await` il browser non le dà più. */
    const voci = [...e.dataTransfer.items]
      .map((i) => (i.kind === "file" ? i.webkitGetAsEntry?.() ?? null : null))
      .filter((v): v is FileSystemEntry => v !== null);
    const soli = [...e.dataTransfer.files];
    if (soli.length === 1 && voci.length <= 1 && soli[0].name.toLowerCase().endsWith(".zip")) {
      void caricaZip(soli[0]);
      return;
    }
    if (voci.length === 0) {
      caricaCartella(soli.map((f) => ({ percorso: f.name, file: f })));
      return;
    }
    const raccolti: FileScelto[] = [];
    try {
      for (const voce of voci) await leggiVoce(voce, raccolti);
    } catch {
      setErrore(new ErroreImmagini("Non riesco a leggere la cartella trascinata: prova con «Scegli una cartella».", 0));
      return;
    }
    caricaCartella(raccolti);
  };

  const togli = () => {
    if (!window.confirm(`Togliere dal sito le immagini caricate per «${slug}»? Il mazzo tornerà ai file del sito, se ne ha.`)) return;
    void avvia(async (t) => {
      setAvanzamento({ testo: "Rimozione…", valore: null, massimo: 1 });
      await eliminaImmagini(t, slug);
      return statoImmagini(t, slug);
    });
  };

  const scartaBozza = () => avvia(async (t) => {
    setAvanzamento({ testo: "Pulizia della bozza…", valore: null, massimo: 1 });
    await scartaBozzaImmagini(t, slug);
    return statoImmagini(t, slug);
  });

  return (
    <section className={stili.sezione} aria-labelledby={`immagini-${slug}`}>
      <h3 className={stili.titolo} id={`immagini-${slug}`}>Immagini del mazzo nel sito</h3>
      <p className={comuni.riquadroNota}>
        Le 78 carte e il dorso, in un unico ZIP o in una cartella. Il nome di ogni file è l&apos;id della carta
        (<code>maj-00.webp</code>, <code>bastoni-06.png</code>, …, <code>dorso.webp</code>); PNG, JPEG o WebP.
        Le immagini si convertono in WebP alla misura del sito (360×640) e sono online subito, senza rilascio. Si
        ignorano le cartelle che cominciano con <code>_</code> (come <code>_staging</code>); se una carta c&apos;è
        due volte, vince la copia nella cartella <code>Web</code>.
      </p>

      {erroreLettura && <p className={comuni.errore}>{erroreLettura}</p>}
      {stato && (
        stato.versione ? (
          <div>
            <p className={comuni.positivo}>
              {stato.pubblicate} di {stato.attese} immagini nel sito · versione <code>{stato.versione}</code>
            </p>
            <div className={stili.anteprime}>
              {ANTEPRIME.map((id) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img key={id} src={urlCartaMazzo(slug, id, stato.versione!)} alt={id} width={54} height={96} loading="lazy" />
              ))}
            </div>
          </div>
        ) : (
          <p className={comuni.spento}>
            Nessuna immagine caricata da qui: il sito usa i file in <code>frontend/public/cards/{slug}/</code>, se ci sono.
          </p>
        )
      )}
      {stato && stato.bozza > 0 && !occupato && (
        <div className={stili.azioni}>
          <span className={comuni.riquadroNota}>
            C&apos;è un caricamento di cartella interrotto ({stato.bozza} file in bozza, non visibili sul sito):
            ricaricare la cartella ricomincia da capo.
          </span>
          <button type="button" className={comuni.secondaria} onClick={scartaBozza}>Scarta la bozza</button>
        </div>
      )}

      <div className={stili.strade}>
        <div className={stili.strada}>
          <strong>Uno ZIP</strong>
          <p>Fino a 300 MB. Le carte possono stare anche in una sottocartella dello ZIP.</p>
          <input id={idZip} ref={inputZip} className={stili.nascosto} type="file" accept=".zip,application/zip"
            disabled={occupato || !stato} onChange={(e) => scegliZip(e.target.files)} />
          <label htmlFor={idZip} className={stili.pulsante}>Carica lo ZIP…</label>
        </div>
        <div className={stili.strada}>
          <strong>Una cartella</strong>
          <p>Tutti i file della cartella scelta, anche nelle sottocartelle: si caricano uno per volta, con la barra.</p>
          <input id={idCartella} ref={inputCartella} className={stili.nascosto} type="file" multiple
            disabled={occupato || !stato} onChange={(e) => scegliCartella(e.target.files)}
            {...{ webkitdirectory: "", directory: "" }} />
          <label htmlFor={idCartella} className={stili.pulsante}>Scegli una cartella…</label>
        </div>
      </div>

      <div
        className={`${stili.trascina} ${sopra ? stili.trascinaAttiva : ""}`}
        onDragOver={(e) => { e.preventDefault(); if (!occupato) setSopra(true); }}
        onDragLeave={() => setSopra(false)}
        onDrop={lascia}
      >
        Oppure trascina qui la cartella del mazzo (o lo ZIP).
      </div>

      {avanzamento && (
        <div role="status" aria-live="polite">
          <p className={comuni.riquadroNota}>{avanzamento.testo}</p>
          {avanzamento.valore === null ? (
            <progress className={stili.barra} aria-label={avanzamento.testo} />
          ) : (
            <progress className={stili.barra} value={avanzamento.valore} max={avanzamento.massimo} aria-label={avanzamento.testo} />
          )}
        </div>
      )}

      {errore && <Rifiuto errore={errore} />}

      {riepilogo && (
        <div role="status" className={comuni.riquadroNota}>
          <p className={comuni.positivo}>
            Fatto: {riepilogo.installate} immagini pubblicate, già visibili sul sito.
          </p>
          {riepilogo.ignorati > 0 && (
            <p>Ignorati {riepilogo.ignorati} file che non sono immagini del mazzo (file di sistema, cartelle con «_», altri formati).</p>
          )}
          {riepilogo.avanzano.length > 0 && (
            <>
              <p>Avanzano {riepilogo.avanzano.length} immagini che non sono carte (non caricate):</p>
              <ul className={stili.elenco}>{riepilogo.avanzano.map((p) => <li key={p}>{p}</li>)}</ul>
            </>
          )}
        </div>
      )}

      {stato?.versione && (
        <div className={stili.azioni}>
          <button type="button" className={comuni.distruttiva} disabled={occupato} onClick={togli}>
            Togli le immagini dal sito
          </button>
        </div>
      )}
    </section>
  );
}

function Rifiuto({ errore }: { errore: ErroreImmagini }) {
  return (
    <div role="alert">
      <p className={comuni.errore}>{errore.message}</p>
      {errore.mancanti.length > 0 && (
        <>
          <p className={comuni.riquadroNota}>Mancano ({errore.mancanti.length}):</p>
          <ul className={stili.elenco}>{errore.mancanti.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
      {errore.doppioni.length > 0 && (
        <>
          <p className={comuni.riquadroNota}>Doppioni (tieni una sola copia, o mettine una in una cartella «Web»):</p>
          <ul className={stili.elenco}>{errore.doppioni.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
      {errore.avanzano.length > 0 && (
        <>
          <p className={comuni.riquadroNota}>Avanzano, non sono carte ({errore.avanzano.length}):</p>
          <ul className={stili.elenco}>{errore.avanzano.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
      {errore.rifiutati.length > 0 && (
        <>
          <p className={comuni.riquadroNota}>Percorsi non ammessi:</p>
          <ul className={stili.elenco}>{errore.rifiutati.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
    </div>
  );
}
