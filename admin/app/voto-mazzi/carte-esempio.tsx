"use client";

/* Le carte d'esempio di una proposta o di un candidato: fino a cinque immagini, mostrate sulla pagina pubblica del
 * voto nell'ordine scelto qui (la prima si vede per prima). Selezione multipla: i file partono uno dopo l'altro, con
 * l'avanzamento; oltre il tetto si caricano i primi e si avvisa. Ogni carta si sposta prima o dopo e si elimina,
 * con pulsanti veri (tastiera, tocco: almeno 44 px). */

import { useRef, useState } from "react";
import {
  MAX_CAMPIONI, caricaCampione, eliminaCampione, riordinaCampioni, urlCampione, type Candidato,
} from "@/lib/voto";
import { ErroreApi } from "@/lib/api";
import { useToken } from "@/lib/usa";
import comuni from "../comuni.module.css";

const PULSANTE: React.CSSProperties = { minHeight: 44, minWidth: 44, height: "auto", padding: "0 .6rem" };

export function CarteEsempio({
  candidato, onCambiata, bloccato,
}: { candidato: Candidato; onCambiata: () => void; bloccato: boolean }) {
  const token = useToken();
  const input = useRef<HTMLInputElement>(null);
  const [lavoro, setLavoro] = useState<string | null>(null);
  const [errore, setErrore] = useState<string | null>(null);
  const [avviso, setAvviso] = useState<string | null>(null);
  const campioni = candidato.campioni;
  const restano = MAX_CAMPIONI - campioni.length;
  const fermo = bloccato || lavoro !== null || token === null;
  const idInput = `campioni-${candidato.id}`;

  const esegui = async (testo: string, azione: (t: string) => Promise<unknown>) => {
    if (token === null) return;
    setLavoro(testo);
    setErrore(null);
    try {
      await azione(token);
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : "L'operazione non è riuscita.");
    } finally {
      setLavoro(null);
      onCambiata();
    }
  };

  const aggiungi = (elenco: FileList | null) => {
    const scelti = [...(elenco ?? [])];
    if (input.current) input.current.value = "";
    if (scelti.length === 0) return;
    const daCaricare = scelti.slice(0, Math.max(restano, 0));
    setAvviso(scelti.length > daCaricare.length
      ? `Al massimo ${MAX_CAMPIONI} carte d'esempio: carico le prime ${daCaricare.length}, le altre ${scelti.length - daCaricare.length} restano fuori.`
      : null);
    if (daCaricare.length === 0) return;
    void esegui(`Caricate 0 di ${daCaricare.length}`, async (t) => {
      for (const [i, file] of daCaricare.entries()) {
        await caricaCampione(t, candidato.id, file);
        setLavoro(`Caricate ${i + 1} di ${daCaricare.length}`);
      }
    });
  };

  const sposta = (da: number, a: number) => {
    const ordine = campioni.map((c) => c.media_id);
    const [preso] = ordine.splice(da, 1);
    ordine.splice(a, 0, preso);
    void esegui("Riordino…", (t) => riordinaCampioni(t, candidato.id, ordine));
  };

  const elimina = (i: number) => {
    if (!window.confirm(`Eliminare la carta d'esempio ${i + 1} di «${candidato.nome}»?`)) return;
    void esegui("Eliminazione…", (t) => eliminaCampione(t, candidato.id, campioni[i].media_id));
  };

  return (
    <div style={{ marginTop: 8 }}>
      <div className={comuni.campoEtichetta}>Carte d&apos;esempio ({campioni.length} di {MAX_CAMPIONI})</div>
      {campioni.length > 0 && (
        <ol style={{ display: "flex", flexWrap: "wrap", gap: 12, listStyle: "none", padding: 0, margin: "6px 0" }}>
          {campioni.map((c, i) => (
            <li key={c.media_id} style={{ display: "grid", gap: 4, justifyItems: "center" }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={urlCampione(c.mini)} alt={c.etichetta ?? `Carta d'esempio ${i + 1}`} width={60} height={107}
                style={{ width: 60, height: "auto", borderRadius: 4, border: "1px solid var(--filo)" }} />
              <div style={{ display: "flex", gap: 4 }}>
                <button type="button" className={comuni.secondaria} style={PULSANTE} disabled={fermo || i === 0}
                  aria-label={`Sposta prima la carta ${i + 1}`} onClick={() => sposta(i, i - 1)}>←</button>
                <button type="button" className={comuni.secondaria} style={PULSANTE} disabled={fermo || i === campioni.length - 1}
                  aria-label={`Sposta dopo la carta ${i + 1}`} onClick={() => sposta(i, i + 1)}>→</button>
                <button type="button" className={comuni.distruttiva} style={PULSANTE} disabled={fermo}
                  aria-label={`Elimina la carta ${i + 1}`} onClick={() => elimina(i)}>✕</button>
              </div>
            </li>
          ))}
        </ol>
      )}
      <div className={comuni.riga} style={{ alignItems: "center" }}>
        <input id={idInput} ref={input} type="file" accept="image/png,image/jpeg,image/webp" multiple
          disabled={fermo || restano <= 0} onChange={(e) => aggiungi(e.target.files)}
          aria-describedby={`${idInput}-aiuto`} style={{ minHeight: 44 }} />
        <span id={`${idInput}-aiuto`} className={comuni.campoAiuto}>
          {restano > 0
            ? `PNG, JPEG o WebP; puoi sceglierne più d'una insieme (ancora ${restano}).`
            : "Hai già cinque carte d'esempio: eliminane una per aggiungerne un'altra."}
        </span>
      </div>
      <div role="status" aria-live="polite">
        {lavoro && <p className={comuni.riquadroNota}>{lavoro}</p>}
        {avviso && <p className={comuni.riquadroNota}>{avviso}</p>}
      </div>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
    </div>
  );
}
