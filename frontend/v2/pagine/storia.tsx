"use client";

/* La mia storia: le letture tenute (il filo), e ciò che il lettore ricorda — visibile e gestibile (specifica v2,
 * §7). Chi non è entrato legge che cosa si ricorda, perché, e chi decide. */

import { useEffect, useState } from "react";
import { useOsservatore, useTraccia } from "lanterna-osservatore/react";
import {
  cancellaLettura, elencaLetture, elencaMemorie, eliminaMemoria, eliminaMemorieSelezionate, eliminaTutteLeMemorie,
  modificaMemoria, type LetturaBreve, type Memoria,
} from "@/lib/api";
import { nomeStesaDaNomi } from "@/lib/i18n/nomi";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import LinkV2 from "@/v2/componenti/link";
import { Modale } from "@/v2/componenti/modale";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useAzione, useCarica } from "@/v2/lib/usa";

export function Storia() {
  const sessione = useSessione();
  if (!sessione.pronta) return null;
  return sessione.autenticata ? <StoriaDentro /> : <StoriaFuori />;
}

function StoriaFuori() {
  const { t } = useLingua();
  const s = t.storia;
  const sessione = useSessione();
  return (
    <section className="band band-tight story-grid">
      <aside className="story-sidebar">
        <h2>{s.cosa_titolo}</h2>
        <ul className="memory-list" style={{ margin: "0 0 1.4rem" }}>
          {s.cosa.map((c) => <li key={c.titolo}><strong>{c.titolo}</strong><span>{c.testo}</span></li>)}
        </ul>
        <h2>{s.perche_titolo}</h2>
        <p className="small">{s.perche_testo}</p>
      </aside>
      <section className="story-main">
        <div className="memory-card">
          <span className="memory-label">{t.home.memoria_etichetta}</span>
          <p>{t.home.memoria_citazione}</p>
          <footer>{t.home.memoria_piede}</footer>
        </div>
        <h2 style={{ marginTop: ".9rem" }}>{s.fuori_titolo}</h2>
        <p className="section-intro">{s.fuori_testo}</p>
        <div className="button-row">
          <button type="button" className="button" onClick={() => sessione.entra(R.storia)}>{s.fuori_entra}</button>
          <LinkV2 className="button button-brass" href={R.leggi}>{s.fuori_inizia}</LinkV2>
        </div>
      </section>
    </section>
  );
}

function StoriaDentro() {
  const { t } = useLingua();
  const s = t.storia;
  const traccia = useTraccia();
  const osservatore = useOsservatore();
  /* Una volta, appena l'osservatore c'è (prima l'evento andrebbe perso). */
  useEffect(() => { if (osservatore) traccia("memory_viewed"); }, [osservatore, traccia]);
  return (
    <section className="band band-tight story-grid">
      <aside className="story-sidebar">
        <Memorie />
        <h2 style={{ marginTop: ".65rem" }}>{s.perche_titolo}</h2>
        <p className="small">{s.perche_testo}</p>
      </aside>
      <section className="story-main" aria-labelledby="titolo-filo">
        <h2 id="titolo-filo">{s.letture_titolo}</h2>
        <Letture />
      </section>
    </section>
  );
}

function Letture() {
  const { t, lingua, locale } = useLingua();
  const s = t.storia;
  const letture = useCarica(elencaLetture);
  const { esegui } = useAzione();
  const [daCancellare, setDaCancellare] = useState<LetturaBreve | null>(null);

  if (letture.errore) return <p className="error">{letture.errore}</p>;
  if (!letture.dati) return <p className="muted">{t.comune.carica}</p>;
  if (letture.dati.letture.length === 0) {
    return (
      <div className="panel">
        <p>{s.letture_vuoto}</p>
        <LinkV2 className="button button-brass" href={R.leggi}>{s.letture_inizia}</LinkV2>
      </div>
    );
  }
  const data = (iso: string) => new Date(iso).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" });
  return (
    <>
      {letture.dati.letture.map((l) => {
        const finita = l.status === "completata";
        return (
          <article key={l.id} className="memory-entry">
            <small>
              {l.categoria !== "standard" && `${s.badge[l.categoria] ?? ""} · `}
              {nomeStesaDaNomi(l.stesa, l.stesa_nomi, lingua)}
              {l.partner_nome ? ` · ${f(t.lettura.tu_e, { nome: l.partner_nome })}` : ""} · {data(l.created_at)}
            </small>
            <h3 dir="auto">{l.question}</h3>
            <p>
              {s.stati[l.status] ?? l.status}
              {l.carte.length > 0 && ` · ${l.carte.slice(0, 4).join(", ")}${l.carte.length > 4 ? "…" : ""}`}
              {l.feedback && ` · ${s.esito} ${s.esiti[l.feedback] ?? l.feedback}`}
            </p>
            <div className="button-row" style={{ marginTop: ".6rem" }}>
              <LinkV2 className="button button-quiet button-small" href={finita ? R.lettura(l.id) : `${R.leggi}?id=${l.id}`}>
                {finita ? s.rileggi : s.continua}
              </LinkV2>
              {finita && (
                <LinkV2 className="button button-quiet button-small" data-an="followup_started"
                  href={`${R.leggi}?question=${encodeURIComponent(l.question)}&source=story`}>
                  {s.riprendi_tema}
                </LinkV2>
              )}
              <button type="button" className="button button-danger button-small" onClick={() => setDaCancellare(l)}
                aria-label={`${s.cancella}: ${l.question}`}>
                {s.cancella}
              </button>
            </div>
          </article>
        );
      })}
      <Modale aperta={!!daCancellare} titolo={s.cancella_conferma_titolo} onChiudi={() => setDaCancellare(null)}>
        <p className="prose" dir="auto">«{daCancellare?.question}»</p>
        <p className="prose">{s.cancella_conferma_testo}</p>
        <div className="button-row">
          <button type="button" className="button button-danger" onClick={async () => {
            const id = daCancellare?.id;
            setDaCancellare(null);
            if (id) { await esegui((tok) => cancellaLettura(tok, id)); letture.ricarica(); }
          }}>{s.cancella}</button>
          <button type="button" className="button button-quiet" onClick={() => setDaCancellare(null)}>{t.comune.annulla}</button>
        </div>
      </Modale>
    </>
  );
}

/* La memoria: elenco, modifica in linea, cancellazione singola e multipla con doppia conferma. Il pulsante in fondo
 * è uno solo — «elimina selezionate» se ce n'è almeno una, altrimenti «elimina tutte» — per non lasciare dubbi. */
function Memorie() {
  const { t } = useLingua();
  const s = t.storia;
  const traccia = useTraccia();
  const memorie = useCarica(elencaMemorie);
  const { esegui, inCorso, errore } = useAzione();
  const [selezionate, setSelezionate] = useState<Set<string>>(new Set());
  const [conferma, setConferma] = useState<0 | 1 | 2>(0);
  const [casella, setCasella] = useState(false);
  const elenco = memorie.dati?.memorie ?? [];
  const alcune = selezionate.size > 0;

  const chiudi = () => { setConferma(0); setCasella(false); };
  const cancella = async () => {
    if (alcune) await esegui((tok) => eliminaMemorieSelezionate(tok, [...selezionate]));
    else await esegui((tok) => eliminaTutteLeMemorie(tok));
    traccia("memory_updated", { azione: alcune ? "elimina_alcune" : "elimina_tutte" });
    setSelezionate(new Set());
    chiudi();
    memorie.ricarica();
  };

  return (
    <section aria-labelledby="titolo-memoria">
      <h2 id="titolo-memoria">{s.memoria_titolo}</h2>
      <p className="small">{s.memoria_testo}</p>
      <p className="small muted">{s.memoria_oblio}</p>
      {memorie.errore && <p className="error">{memorie.errore}</p>}
      {memorie.dati && elenco.length === 0 && <p className="small muted">{s.memoria_vuoto}</p>}
      {elenco.length > 0 && (
        <>
          <ul className="list-plain">
            {elenco.map((m) => (
              <RigaMemoria key={m.id} memoria={m} selezionata={selezionate.has(m.id)}
                onSeleziona={() => setSelezionate((p) => { const n = new Set(p); if (n.has(m.id)) n.delete(m.id); else n.add(m.id); return n; })}
                onCambio={() => { traccia("memory_updated", { azione: "modifica" }); memorie.ricarica(); }} />
            ))}
          </ul>
          <button type="button" className="button button-danger button-small" style={{ marginTop: "1rem" }} onClick={() => setConferma(1)}>
            {alcune ? s.elimina_selezionate : s.elimina_tutte}
          </button>
        </>
      )}
      {errore && <p className="error">{errore}</p>}
      <Modale aperta={conferma > 0} titolo={s.conferma_titolo} onChiudi={chiudi}>
        {conferma === 1 ? (
          <>
            <p className="prose">{alcune ? (selezionate.size === 1 ? s.conferma_una : f(s.conferma_n, { n: selezionate.size })) : s.conferma_tutte}</p>
            <div className="button-row">
              <button type="button" className="button" onClick={() => setConferma(2)}>{s.conferma_continua}</button>
              <button type="button" className="button button-quiet" onClick={chiudi}>{s.annulla}</button>
            </div>
          </>
        ) : (
          <>
            <label className="check">
              <input type="checkbox" checked={casella} onChange={(e) => setCasella(e.target.checked)} />
              <span>{s.conferma_casella}</span>
            </label>
            <div className="button-row">
              <button type="button" className="button button-danger" disabled={!casella || inCorso} onClick={cancella}>{s.conferma_elimina}</button>
              <button type="button" className="button button-quiet" onClick={chiudi}>{s.annulla}</button>
            </div>
          </>
        )}
      </Modale>
    </section>
  );
}

function RigaMemoria({
  memoria, selezionata, onSeleziona, onCambio,
}: { memoria: Memoria; selezionata: boolean; onSeleziona: () => void; onCambio: () => void }) {
  const { t, locale } = useLingua();
  const s = t.storia;
  const { esegui, inCorso } = useAzione();
  const [modifica, setModifica] = useState(false);
  const [contenuto, setContenuto] = useState(memoria.contenuto);
  const [campo, setCampo] = useState(memoria.campo_attinenza);
  const tipo = memoria.categoria ? s.categoria[memoria.categoria] : memoria.tipo === "stabile" ? s.tipo_stabile : s.tipo_variabile;
  const scade = memoria.scade
    ? f(s.scade, { data: new Date(memoria.scade).toLocaleDateString(locale, { day: "numeric", month: "long", year: "numeric" }) })
    : "";

  return (
    <li className="memory-entry">
      <small>
        {tipo} · {s.campi[memoria.campo_attinenza] ?? memoria.campo_attinenza}
        {s.fonte[memoria.fonte] ? ` · ${s.fonte[memoria.fonte]}` : ""}
      </small>
      {scade && <p className="small muted" style={{ margin: ".2rem 0 0" }}>{scade}</p>}
      {modifica ? (
        <div style={{ marginTop: ".5rem" }}>
          <label className="field"><span>{s.memoria_titolo}</span>
            <textarea value={contenuto} rows={3} dir="auto" onChange={(e) => setContenuto(e.target.value)} /></label>
          <label className="field"><span>{s.campo}</span>
            {memoria.categoria ? (
              <select value={campo} onChange={(e) => setCampo(e.target.value)}>
                {Object.entries(s.campi).map(([valore, nome]) => <option key={valore} value={valore}>{nome}</option>)}
              </select>
            ) : (
              <input value={campo} dir="auto" onChange={(e) => setCampo(e.target.value)} />
            )}</label>
          <div className="button-row">
            <button type="button" className="button button-small" disabled={inCorso || !contenuto.trim()} onClick={async () => {
              await esegui((tok) => modificaMemoria(tok, memoria.id, { contenuto: contenuto.trim(), campo_attinenza: campo.trim() }));
              setModifica(false);
              onCambio();
            }}>{s.salva}</button>
            <button type="button" className="button button-quiet button-small" onClick={() => {
              setModifica(false); setContenuto(memoria.contenuto); setCampo(memoria.campo_attinenza);
            }}>{s.annulla}</button>
          </div>
        </div>
      ) : (
        <p dir="auto" style={{ margin: ".3rem 0" }}>{memoria.contenuto}</p>
      )}
      <div className="button-row">
        <label className="check" style={{ minHeight: 44, padding: 0 }}>
          <input type="checkbox" checked={selezionata} onChange={onSeleziona} />
          <span className="small">{s.seleziona}</span>
        </label>
        <button type="button" className="button button-quiet button-small" onClick={() => setModifica((v) => !v)}>{s.modifica}</button>
        <button type="button" className="button button-danger button-small" disabled={inCorso}
          onClick={async () => { await esegui((tok) => eliminaMemoria(tok, memoria.id)); onCambio(); }}>{s.elimina}</button>
      </div>
    </li>
  );
}
