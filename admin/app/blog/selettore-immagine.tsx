"use client";

import { useState } from "react";
import { caricaImmagine, immagini, urlMedia, type Immagine } from "@/lib/blog";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./blog.module.css";

/* Sceglie un'immagine dalla libreria del blog, o ne carica una nuova sul posto.
 *
 * Serve in due punti: la copertina di un articolo e un'immagine dentro il testo. Il
 * chiamante riceve l'immagine scelta e decide che farne. Il caricamento è lo stesso della
 * libreria: il server la riscrive in WebP, quindi qui non si controlla il formato oltre a
 * ciò che `accept` suggerisce. */
export function SelettoreImmagine({
  scelta,
  alScelta,
  chiudi,
}: {
  scelta?: string | null;
  alScelta: (i: Immagine) => void;
  chiudi: () => void;
}) {
  const libreria = useDati(immagini);
  const { esegui, inCorso, errore } = useAzione();
  const [carica, setCarica] = useState(false);

  const nuova = async (file: File) => {
    setCarica(true);
    const i = await esegui((t) => caricaImmagine(t, file));
    setCarica(false);
    if (i) alScelta(i);
  };

  return (
    <div className={stili.selettore} role="dialog" aria-label="Scegli un'immagine">
      <div className={comuni.riga}>
        <label className={stili.scegliFile}>
          {carica ? "Caricamento…" : "Carica un'immagine"}
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp"
            disabled={inCorso}
            onChange={(e) => {
              const file = e.target.files?.[0];
              e.target.value = "";
              if (file) void nuova(file);
            }}
          />
        </label>
        <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={chiudi}>
          Chiudi
        </button>
      </div>
      {errore && (
        <p className={comuni.errore} role="alert">
          {errore}
        </p>
      )}
      {libreria.errore && <p className={comuni.errore}>{libreria.errore}</p>}
      {!libreria.dati && libreria.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {libreria.dati && libreria.dati.length === 0 && <p className={comuni.vuoto}>La libreria è vuota.</p>}
      {libreria.dati && libreria.dati.length > 0 && (
        <ul className={stili.griglia}>
          {libreria.dati.map((i) => (
            <li key={i.id}>
              <button
                type="button"
                className={`${stili.scelta} ${scelta === i.id ? stili.sceltaAttiva : ""}`}
                aria-label={`Immagine ${i.larghezza}×${i.altezza}`}
                aria-pressed={scelta === i.id}
                onClick={() => alScelta(i)}
              >
                {/* eslint-disable-next-line @next/next/no-img-element -- miniatura dalla libreria */}
                <img src={urlMedia(i.url) ?? ""} alt="" loading="lazy" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
