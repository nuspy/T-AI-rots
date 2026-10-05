"use client";

import { useId, useMemo, useState } from "react";
import type { Riferimento, Soggetto } from "@/lib/blog";
import comuni from "../comuni.module.css";
import stili from "./blog.module.css";

/* Il soggetto di un articolo (v9.4): la carta o la stesa di cui parla.
 *
 * Serve al sito per mettere l'articolo per primo sulla pagina di quella carta o di quella stesa, e per sceglierlo
 * fra gli articoli «da leggere». Quattro scelte:
 * - **Automatico**: non si manda niente e il server cerca il nome di una carta o di una stesa nel titolo, poi nella
 *   parola chiave principale (lo fa solo per un articolo che un soggetto non ce l'ha ancora: chi lo chiede per un
 *   articolo che ne ha uno, se lo vede prima togliere e poi ricalcolare);
 * - **Nessuno**: si manda `null`, e resta senza;
 * - **Una carta**, **Una stesa**: si manda `{tipo, ref}` con l'id scelto dall'elenco.
 *
 * L'elenco si filtra scrivendo: cerca nel nome italiano, in quello inglese, in quello di Thoth e nell'id. */

export type ModoSoggetto = "auto" | "nessuno" | "carta" | "stesa";

const NESSUNA: Riferimento[] = [];

/** Minuscolo e senza accenti: «Più» trova «piu», «Ruota» trova «ruota». */
const normale = (testo: string) =>
  testo
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .trim();

export function SceltaSoggetto({
  modo,
  rif,
  cambia,
  carte,
  stese,
  attuale,
  automatico,
}: {
  modo: ModoSoggetto;
  rif: string;
  cambia: (modo: ModoSoggetto, rif: string) => void;
  carte: Riferimento[];
  stese: Riferimento[];
  /** Il soggetto dell'articolo com'è salvato, o null. */
  attuale: Soggetto | null;
  /** Vero se l'ultimo salvataggio l'ha scelto il server, dal titolo o dalla parola chiave. */
  automatico: boolean;
}) {
  const [cerca, setCerca] = useState("");
  const idElenco = useId();

  const voci = modo === "carta" ? carte : modo === "stesa" ? stese : NESSUNA;
  const scelta = voci.find((v) => v.id === rif) ?? null;
  const trovate = useMemo(() => {
    const testo = normale(cerca);
    if (!testo) return voci;
    return voci.filter((v) => [v.nome, v.id, ...(v.altri ?? [])].some((n) => normale(n).includes(testo)));
  }, [voci, cerca]);

  return (
    <>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Di che cosa parla</span>
        <select
          className={comuni.selezione}
          value={modo}
          onChange={(e) => {
            const nuovo = e.target.value as ModoSoggetto;
            setCerca("");
            /* Tornando sulla carta (o sulla stesa) salvata, la si ritrova già scelta. */
            cambia(nuovo, attuale && attuale.tipo === nuovo ? attuale.ref : "");
          }}
        >
          <option value="auto">Automatico (dal titolo)</option>
          <option value="nessuno">Nessuna carta o stesa</option>
          <option value="carta">Una carta</option>
          <option value="stesa">Una stesa</option>
        </select>
        <span className={comuni.campoAiuto}>
          Il soggetto fa comparire l&apos;articolo per primo sulla pagina di quella carta o di quella stesa.
        </span>
      </label>

      {automatico && attuale && modo === attuale.tipo && rif === attuale.ref && (
        <p className={comuni.riquadroNota} role="status">
          <span className={`${comuni.stato} ${comuni.neutro}`}>scelto in automatico</span> Il sito l&apos;ha trovato
          nel titolo o nella parola chiave. Se non è giusto, cambialo o scegli «Nessuna carta o stesa».
        </p>
      )}

      {modo === "auto" && (
        <p className={comuni.riquadroNota}>
          {attuale
            ? `Al salvataggio «${attuale.nome}» viene tolto e il sito cerca di nuovo una carta o una stesa nel titolo, poi nella parola chiave principale.`
            : "Al salvataggio il sito cerca il nome di una carta o di una stesa nel titolo, poi nella parola chiave principale. Se non lo trova, l'articolo resta senza."}
        </p>
      )}

      {(modo === "carta" || modo === "stesa") && (
        <div>
          <p className={comuni.riquadroNota} style={{ marginBottom: "0.5rem" }} aria-live="polite">
            {scelta ? (
              <>
                Scelta: <strong>{scelta.nome}</strong> <span className={comuni.mono}>({scelta.id})</span>
              </>
            ) : (
              <>{modo === "carta" ? "Scegli una carta dall'elenco." : "Scegli una stesa dall'elenco."} Senza scelta il soggetto non cambia.</>
            )}
          </p>
          <label className={comuni.campo} style={{ marginBottom: "0.5rem" }}>
            <span className={comuni.campoEtichetta}>{modo === "carta" ? "Cerca la carta" : "Cerca la stesa"}</span>
            <input
              className={comuni.ingresso}
              type="search"
              value={cerca}
              aria-controls={idElenco}
              onChange={(e) => setCerca(e.target.value)}
              placeholder={modo === "carta" ? "Nome in italiano o in inglese: «torre», «tower»" : "Per esempio «croce», «celtic»"}
            />
          </label>
          <ul id={idElenco} className={stili.sceltaSoggetto} aria-label={modo === "carta" ? "Carte" : "Stese"}>
            {trovate.length === 0 && <li className={stili.sceltaSoggettoVuota}>Nessuna corrisponde.</li>}
            {trovate.map((v) => (
              <li key={v.id}>
                <button
                  type="button"
                  aria-pressed={v.id === rif}
                  onClick={() => cambia(modo, v.id)}
                >
                  <span>{v.nome}</span>
                  {v.altri?.[0] && v.altri[0] !== v.nome && <small>{v.altri[0]}</small>}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
