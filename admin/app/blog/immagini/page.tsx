"use client";

import { useState } from "react";
import { ErroreApi } from "@/lib/api";
import { caricaImmagine, eliminaImmagine, immagini, markdownImmagine, urlMedia, type Immagine } from "@/lib/blog";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../blog.module.css";
import { Schede } from "../schede";

/* La libreria delle immagini del blog.
 *
 * Ogni immagine caricata — PNG, JPEG o WebP, fino a 8 MB — il server la orienta, la porta a 1600 px di
 * larghezza al massimo e la riscrive in WebP senza metadati (la posizione di uno scatto non deve finire online).
 * Vive nel database, non in una cartella: un solo posto da salvare e da ripristinare.
 *
 * Un'immagine usata da un articolo o da una sezione non si elimina: il server risponde 409 e dice quante volte. */

export default function Immagini() {
  const elenco = useDati(immagini);
  const { esegui, inCorso, errore } = useAzione();
  const [copiata, setCopiata] = useState<string | null>(null);
  const [daEliminare, setDaEliminare] = useState<string | null>(null);
  const [inUso, setInUso] = useState<string | null>(null);
  const [caricate, setCaricate] = useState<string | null>(null);

  const carica = async (files: FileList) => {
    setCaricate(null);
    let riuscite = 0;
    for (const file of Array.from(files)) {
      if (await esegui((t) => caricaImmagine(t, file))) riuscite += 1;
      else break;
    }
    if (riuscite) setCaricate(riuscite === 1 ? "1 immagine caricata." : `${riuscite} immagini caricate.`);
    elenco.ricarica();
  };

  const copia = async (i: Immagine) => {
    try {
      await navigator.clipboard.writeText(markdownImmagine(i));
      setCopiata(i.id);
    } catch {
      /* Gli appunti possono essere negati (pagina non sicura, permesso rifiutato): resta il testo da selezionare. */
      setCopiata(null);
    }
  };

  const elimina = async (i: Immagine) => {
    setInUso(null);
    const fatto = await esegui(async (t) => {
      try {
        await eliminaImmagine(t, i.id);
        return true;
      } catch (e) {
        if (e instanceof ErroreApi && e.stato === 409) {
          setInUso(i.id);
          return false;
        }
        throw e;
      }
    });
    if (fatto) {
      setDaEliminare(null);
      elenco.ricarica();
    }
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Blog · Immagini</h1>
          <p className={comuni.sottotitolo}>
            Le immagini degli articoli e delle sezioni. Per metterne una nel testo si copia il suo Markdown e lo si
            incolla; per la copertina la si sceglie dall&apos;editor.
          </p>
        </div>
        <label className={stili.scegliFile}>
          {inCorso ? "Caricamento…" : "Carica immagini"}
          <input
            type="file"
            multiple
            accept="image/png,image/jpeg,image/webp"
            disabled={inCorso}
            onChange={(e) => {
              const files = e.target.files;
              if (files && files.length) void carica(files);
              e.target.value = "";
            }}
          />
        </label>
      </div>

      <Schede />

      {errore && (
        <p className={comuni.errore} role="alert">
          {errore}
        </p>
      )}
      {caricate && !errore && (
        <p className={comuni.esito} role="status">
          {caricate}
        </p>
      )}
      {elenco.errore && <p className={comuni.errore}>{elenco.errore}</p>}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {elenco.dati && elenco.dati.length === 0 && <div className={comuni.vuoto}>Nessuna immagine. Caricane una.</div>}

      {elenco.dati && elenco.dati.length > 0 && (
        <ul className={`${stili.griglia} ${elenco.inCorso ? comuni.inRicarica : ""}`} aria-label="Immagini">
          {elenco.dati.map((i) => (
            <li key={i.id} className={stili.miniatura}>
              {/* eslint-disable-next-line @next/next/no-img-element -- miniatura dalla libreria */}
              <img src={urlMedia(i.url) ?? ""} alt="" loading="lazy" />
              <div className={stili.miniaturaSotto}>
                <span>
                  {i.larghezza}×{i.altezza} · {quandoCompleto(i.creata)}
                </span>
                <div>
                  <button type="button" onClick={() => copia(i)}>
                    {copiata === i.id ? "Copiato" : "Copia Markdown"}
                  </button>
                  {daEliminare === i.id ? (
                    <>
                      <button type="button" style={{ color: "var(--allarme)" }} disabled={inCorso} onClick={() => elimina(i)}>
                        Sì, elimina
                      </button>
                      <button type="button" onClick={() => setDaEliminare(null)}>
                        Annulla
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      style={{ color: "var(--allarme)" }}
                      disabled={inCorso}
                      onClick={() => {
                        setInUso(null);
                        setDaEliminare(i.id);
                      }}
                    >
                      Elimina
                    </button>
                  )}
                </div>
                {inUso === i.id && (
                  <span role="alert" style={{ color: "var(--allarme)", fontFamily: "var(--interfaccia)" }}>
                    In uso da un articolo, da una sezione o da una stesa: prima toglila da lì.
                  </span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
