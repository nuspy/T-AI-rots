"use client";

import { useEffect, useState } from "react";
import { controlloSeo, type ControlloSeo, type DatiControlloSeo, type RapportoSeo } from "@/lib/blog";
import { ErroreApi } from "@/lib/api";
import { useToken } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./blog.module.css";

/* Il controllo SEO di un articolo, mentre lo si scrive.
 *
 * Il rapporto lo calcola il server (`POST /admin/blog/seo-check`, le stesse regole con cui un agente controlla i
 * suoi articoli via REST): qui si manda l'articolo com'è, anche non salvato, un istante dopo l'ultima modifica.
 * Non misura il posizionamento — non ha dati di ricerca —: dice se l'articolo rispetta le buone pratiche note e
 * cosa migliorare. Un 100 non promette il primo posto. */

const ATTESA_MS = 900;

const GIUDIZIO = {
  ottimo: { testo: "Ottimo", classe: comuni.positivo },
  buono: { testo: "Buono", classe: comuni.neutro },
  da_migliorare: { testo: "Da migliorare", classe: comuni.negativo },
} as const;

/* Il segno dice l'esito anche senza colore. */
const SEGNO = { ok: "✓", avviso: "!", errore: "✕" } as const;
const NOME_ESITO = { ok: "a posto", avviso: "da migliorare", errore: "da correggere" } as const;

const ORDINE = { errore: 0, avviso: 1, ok: 2 } as const;

interface Risposta {
  chiave: string;
  rapporto: RapportoSeo | null;
  errore: string | null;
}

export function PannelloSeo({ dati }: { dati: DatiControlloSeo }) {
  const token = useToken();
  const [risposta, setRisposta] = useState<Risposta | null>(null);
  const chiave = JSON.stringify(dati);
  const vuoto = !dati.titolo.trim() && !dati.testo.trim();

  useEffect(() => {
    if (token === null || vuoto) return;
    let annullato = false;
    const attesa = setTimeout(() => {
      controlloSeo(token, JSON.parse(chiave) as DatiControlloSeo)
        .then((rapporto) => {
          if (!annullato) setRisposta({ chiave, rapporto, errore: null });
        })
        .catch((e: unknown) => {
          if (annullato) return;
          setRisposta((prima) => ({
            chiave,
            rapporto: prima?.rapporto ?? null,
            errore: e instanceof ErroreApi ? e.message : "Il controllo non è riuscito.",
          }));
        });
    }, ATTESA_MS);
    return () => {
      annullato = true;
      clearTimeout(attesa);
    };
  }, [token, chiave, vuoto]);

  const aggiornato = risposta?.chiave === chiave;
  const rapporto = risposta?.rapporto ?? null;
  const dafare = rapporto ? rapporto.controlli.filter((c) => c.esito !== "ok").sort(perOrdine) : [];
  const riusciti = rapporto ? rapporto.controlli.filter((c) => c.esito === "ok") : [];

  return (
    <section className={stili.pannello} aria-labelledby="controllo-seo" aria-busy={!aggiornato && !vuoto}>
      <h2 id="controllo-seo" className={stili.pannelloTitolo}>
        Controllo SEO
      </h2>

      {vuoto && <p className={comuni.riquadroNota}>Scrivi un titolo e un testo: il controllo parte da solo.</p>}

      {risposta?.errore && !vuoto && (
        <p className={comuni.errore} role="alert">
          {risposta.errore}
        </p>
      )}

      {rapporto && !vuoto && (
        <div className={aggiornato ? undefined : comuni.inRicarica}>
          <div className={stili.punteggio}>
            <div
              className={stili.punteggioBarra}
              role="meter"
              aria-label="Punteggio SEO"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={rapporto.punteggio}
              aria-valuetext={`${rapporto.punteggio} su 100: ${GIUDIZIO[rapporto.giudizio].testo}`}
            >
              <span style={{ width: `${rapporto.punteggio}%` }} data-giudizio={rapporto.giudizio} />
            </div>
            <p className={stili.punteggioNumero}>
              <strong>{rapporto.punteggio}</strong>/100{" "}
              <span className={`${comuni.stato} ${GIUDIZIO[rapporto.giudizio].classe}`}>{GIUDIZIO[rapporto.giudizio].testo}</span>
            </p>
          </div>

          <p className={stili.statistiche}>
            <span>{rapporto.statistiche.parole} parole</span>
            <span>{rapporto.statistiche.titoli_h2} titoli di sezione</span>
            <span>{rapporto.statistiche.collegamenti_interni} link interni</span>
            <span>{rapporto.statistiche.faq} domande</span>
          </p>

          {dafare.length > 0 ? (
            <ul className={stili.controlli} aria-label="Cosa migliorare">
              {dafare.map((c) => (
                <RigaControllo key={c.id} controllo={c} />
              ))}
            </ul>
          ) : (
            <p className={comuni.esito}>Tutti i controlli sono a posto.</p>
          )}

          {riusciti.length > 0 && (
            <details className={stili.riusciti}>
              <summary>A posto ({riusciti.length})</summary>
              <ul className={stili.controlli}>
                {riusciti.map((c) => (
                  <RigaControllo key={c.id} controllo={c} />
                ))}
              </ul>
            </details>
          )}
        </div>
      )}

      {!rapporto && !vuoto && !risposta?.errore && <p className={comuni.caricamento}>Controllo in corso…</p>}
    </section>
  );
}

function perOrdine(a: ControlloSeo, b: ControlloSeo): number {
  return ORDINE[a.esito] - ORDINE[b.esito] || b.peso - a.peso;
}

function RigaControllo({ controllo }: { controllo: ControlloSeo }) {
  return (
    <li className={stili.controllo} data-esito={controllo.esito}>
      <span className={stili.controlloSegno} aria-hidden="true">
        {SEGNO[controllo.esito]}
      </span>
      <span>
        <span className={stili.soloLettori}>{NOME_ESITO[controllo.esito]}: </span>
        {controllo.messaggio_it}
      </span>
    </li>
  );
}
