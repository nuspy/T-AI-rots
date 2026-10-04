"use client";

/* Vota il prossimo mazzo, nella v2: un voto per persona e per tornata, sostituibile finché la tornata è aperta; le
 * percentuali solo dopo aver votato (come nel sito e sul server). Chi non è entrato vede l'ultimo risultato e
 * l'invito ad accedere. */

import { useState } from "react";
import { statoVotoMazzi, suggerisciTemaMazzo, votaMazzo, type CandidatoVoto } from "@/lib/api";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import { CampioniVoto } from "@/v2/componenti/campioni-voto";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";
import { RiepilogoVoto } from "./mazzi";

export function Voto() {
  const { t } = useLingua();
  const k = t.mazzi;
  const sessione = useSessione();
  return (
    <>
      <section className="subhero subhero-compact">
        <p className="eyebrow">{k.voto_eyebrow}</p>
        <h1 className="display">{k.voto_titolo_pagina}</h1>
        <p className="section-intro">{k.voto_intro}</p>
      </section>
      <section className="band band-tight">
        {!sessione.pronta ? null : sessione.autenticata ? <Votazione /> : (
          <div className="story-grid">
            <div className="panel">
              <p>{k.voto_fuori}</p>
              <button type="button" className="button" onClick={() => sessione.entra(R.voto)}>{k.voto_entra}</button>
            </div>
            <RiepilogoVoto />
          </div>
        )}
      </section>
    </>
  );
}

function Votazione() {
  const { t } = useLingua();
  const k = t.mazzi;
  const stato = useCarica(statoVotoMazzi);
  const { esegui, inCorso, errore } = useAzione();
  const [votatoOra, setVotatoOra] = useState<string | null>(null);
  if (stato.errore) return <p className="error">{stato.errore}</p>;
  const s = stato.dati;
  if (!s) return <p className="muted">{t.comune.carica}</p>;
  const mio = votatoOra ?? s.mio_voto;

  const vota = async (id: string) => {
    const r = await esegui((tok) => votaMazzo(tok, id));
    if (r) { setVotatoOra(id); stato.ricarica(); }
  };

  return (
    <>
      {s.tornata ? (
        <>
          {mio && <p className="success" role="status">{k.voto_grazie}</p>}
          <div className="pricing-grid" style={{ marginTop: ".5rem" }}>
            {s.candidati.map((c) => <Candidato key={c.id} c={c} mio={mio} inCorso={inCorso} onVota={() => vota(c.id)} />)}
          </div>
          {mio && <p className="small muted">{k.voto_cambia}</p>}
          {errore && <p className="error">{errore}</p>}
        </>
      ) : <p className="notice">{k.voto_nessuna}</p>}

      {s.vincitori_precedenti && s.vincitori_precedenti.length > 0 && (
        <div className="panel" style={{ marginTop: ".7rem" }}>
          <h2>{k.voto_vincitori}</h2>
          <ul className="list-plain">
            {s.vincitori_precedenti.map((v) => (
              <li key={v.nome} className="memory-entry"><h3>{v.nome}</h3><p className="small">{f(k.voto_percentuale, { n: v.percentuale })}</p></li>
            ))}
          </ul>
        </div>
      )}
      <Suggerisci />
    </>
  );
}

function Candidato({ c, mio, inCorso, onVota }: { c: CandidatoVoto; mio: string | null; inCorso: boolean; onVota: () => void }) {
  const { t } = useLingua();
  const k = t.mazzi;
  const qui = mio === c.id;
  return (
    <article className={`plan ${qui ? "featured" : ""}`}>
      <h3>{c.nome}</h3>
      {c.descrizione && <p>{c.descrizione}</p>}
      <CampioniVoto nome={c.nome} campioni={c.campioni} />
      {c.percentuale !== null && (
        <>
          <div className="stat-bar" aria-hidden="true"><span style={{ width: `${c.percentuale}%` }} /></div>
          <p className="small">{f(k.voto_percentuale, { n: c.percentuale })}</p>
        </>
      )}
      <button type="button" className={`button ${qui ? "button-brass" : "button-quiet"}`} disabled={inCorso || qui} onClick={onVota}>
        {qui ? k.voto_votato : k.voto_bottone}
      </button>
    </article>
  );
}

function Suggerisci() {
  const { t } = useLingua();
  const k = t.mazzi;
  const { esegui, inCorso, errore } = useAzione();
  const [testo, setTesto] = useState("");
  const [inviato, setInviato] = useState(false);
  return (
    <div className="panel" style={{ marginTop: ".7rem" }}>
      <h2>{k.suggerisci_titolo}</h2>
      <p className="small">{k.suggerisci_testo}</p>
      <label className="field">
        <span className="sr-only">{k.suggerisci_titolo}</span>
        <textarea value={testo} maxLength={1000} placeholder={k.suggerisci_segnaposto} dir="auto"
          onChange={(e) => { setTesto(e.target.value); setInviato(false); }} />
      </label>
      <button type="button" className="button button-quiet" disabled={inCorso || testo.trim().length < 3} onClick={async () => {
        const r = await esegui((tok) => suggerisciTemaMazzo(tok, testo.trim()));
        if (r) { setTesto(""); setInviato(true); }
      }}>{k.suggerisci_invia}</button>
      {inviato && <p className="success" role="status">{k.suggerisci_grazie}</p>}
      {errore && <p className="error">{errore}</p>}
    </div>
  );
}
