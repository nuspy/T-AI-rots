"use client";

/* Calendario e obiettivi (v8).
 *
 * Il calendario segna campagne, rilasci, articoli, cambi di prezzo e fatti esterni: compaiono come ◆ sui
 * grafici, nel rapporto della settimana e fra i dati dell'interpretazione AI.
 * Gli obiettivi dicono cosa conta come risultato: una pagina (uno o più percorsi, uno per lingua) o un
 * evento (con una proprietà facoltativa, es. lettura_fase con fase = completata). */

import { useCallback, useState } from "react";
import {
  creaAnnotazione, creaObiettivo, elencaAnnotazioni, risultatiObiettivi, togliAnnotazione, togliObiettivo,
  type TipoAnnotazione,
} from "@/lib/analytics";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { oggi } from "../comuni";

const TIPI: Record<TipoAnnotazione, string> = {
  campagna: "Campagna", rilascio: "Rilascio del sito", contenuto: "Contenuto pubblicato",
  prezzo: "Cambio di prezzo", esterno: "Fatto esterno", altro: "Altro",
};

const ESEMPI_OBIETTIVI = [
  { nome: "Vede i prezzi", tipo: "pagina" as const, valore: "/pricing,/it/piano", chiave: "", valoreProprieta: "" },
  { nome: "Arriva al responso", tipo: "evento" as const, valore: "lettura_fase", chiave: "fase", valoreProprieta: "completata" },
  { nome: "Acquista", tipo: "evento" as const, valore: "acquisto", chiave: "", valoreProprieta: "" },
];

export function Calendario() {
  const annotazioni = useDati(useCallback((t: string) => elencaAnnotazioni(t), []));
  const { esegui, inCorso, errore } = useAzione();
  const [giorno, setGiorno] = useState(oggi());
  const [fine, setFine] = useState("");
  const [tipo, setTipo] = useState<TipoAnnotazione>("campagna");
  const [titolo, setTitolo] = useState("");
  const [nota, setNota] = useState("");

  return (
    <section className={comuni.riquadro} aria-labelledby="titolo-calendario">
      <h2 id="titolo-calendario" className={comuni.riquadroTitolo}>Calendario</h2>
      <p className={comuni.riquadroNota}>
        Segna qui campagne, rilasci, articoli, cambi di prezzo: compaiono sui grafici (◆), nel rapporto e nell&apos;analisi AI,
        che così può collegare un cambiamento alla sua causa.
      </p>
      <form className={comuni.riga} onSubmit={async (e) => {
        e.preventDefault();
        const r = await esegui((t) => creaAnnotazione(t, { giorno, fine: fine || null, tipo, titolo, nota: nota || null }));
        if (r) { setTitolo(""); setNota(""); setFine(""); annotazioni.ricarica(); }
      }}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Dal</span>
          <input className={comuni.ingresso} type="date" required value={giorno} onChange={(e) => setGiorno(e.target.value)} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Al (facoltativo)</span>
          <input className={comuni.ingresso} type="date" value={fine} min={giorno} onChange={(e) => setFine(e.target.value)} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Tipo</span>
          <select className={comuni.selezione} value={tipo} onChange={(e) => setTipo(e.target.value as TipoAnnotazione)}>
            {Object.entries(TIPI).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Cosa</span>
          <input className={comuni.ingresso} required maxLength={200} value={titolo} onChange={(e) => setTitolo(e.target.value)}
            placeholder="Campagna Instagram autunno" />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Nota (facoltativa)</span>
          <input className={comuni.ingresso} maxLength={1000} value={nota} onChange={(e) => setNota(e.target.value)} />
        </label>
        <button className={comuni.primaria} type="submit" disabled={inCorso || !titolo.trim()}>Aggiungi</button>
      </form>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {annotazioni.dati && annotazioni.dati.length > 0 && (
        <div className={comuni.contenitoreTabella} style={{ marginTop: "0.75rem" }}>
          <table className={comuni.tabella}>
            <thead><tr><th>Quando</th><th>Tipo</th><th>Cosa</th><th /></tr></thead>
            <tbody>
              {[...annotazioni.dati].reverse().map((a) => (
                <tr key={a.id}>
                  <td>{a.giorno}{a.fine ? ` – ${a.fine}` : ""}</td>
                  <td>{TIPI[a.tipo] ?? a.tipo}</td>
                  <td>{a.titolo}{a.nota ? <span className={comuni.etichetta}> · {a.nota}</span> : null}</td>
                  <td>
                    <button className={comuni.secondaria} disabled={inCorso} aria-label={`Togli ${a.titolo}`}
                      onClick={async () => { await esegui((t) => togliAnnotazione(t, a.id)); annotazioni.ricarica(); }}>
                      Togli
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export function Obiettivi() {
  const obiettivi = useDati(useCallback((t: string) => risultatiObiettivi(t, 30), []));
  const { esegui, inCorso, errore } = useAzione();
  const [nome, setNome] = useState("");
  const [tipo, setTipo] = useState<"evento" | "pagina">("pagina");
  const [valore, setValore] = useState("");
  const [chiave, setChiave] = useState("");
  const [valoreProprieta, setValoreProprieta] = useState("");

  const aggiungi = async (o: { nome: string; tipo: "evento" | "pagina"; valore: string; chiave: string; valoreProprieta: string }) => {
    const proprieta = o.tipo === "evento" && o.chiave ? { [o.chiave]: o.valoreProprieta } : {};
    const r = await esegui((t) => creaObiettivo(t, { nome: o.nome, tipo: o.tipo, valore: o.valore, proprieta }));
    if (r) { setNome(""); setValore(""); setChiave(""); setValoreProprieta(""); obiettivi.ricarica(); }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="titolo-obiettivi-conf">
      <h2 id="titolo-obiettivi-conf" className={comuni.riquadroTitolo}>Obiettivi</h2>
      <p className={comuni.riquadroNota}>
        Cosa conta come risultato. Una <strong>pagina</strong>: uno o più percorsi separati da virgola (una pagina esiste in più
        lingue: <span className={comuni.mono}>/pricing,/it/piano</span>). Un <strong>evento</strong>: il suo nome, con una proprietà
        facoltativa. I risultati sono nel Traffico, nel rapporto e nell&apos;analisi AI.
      </p>
      {obiettivi.dati && obiettivi.dati.obiettivi.length === 0 && (
        <div className={comuni.riga}>
          <span className={comuni.etichetta}>Per cominciare:</span>
          {ESEMPI_OBIETTIVI.map((e) => (
            <button key={e.nome} className={comuni.secondaria} disabled={inCorso} onClick={() => aggiungi(e)}>+ {e.nome}</button>
          ))}
        </div>
      )}
      <form className={comuni.riga} onSubmit={(e) => { e.preventDefault(); aggiungi({ nome, tipo, valore, chiave, valoreProprieta }); }}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Nome</span>
          <input className={comuni.ingresso} required maxLength={120} value={nome} onChange={(e) => setNome(e.target.value)} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Tipo</span>
          <select className={comuni.selezione} value={tipo} onChange={(e) => setTipo(e.target.value as "evento" | "pagina")}>
            <option value="pagina">Pagina</option>
            <option value="evento">Evento</option>
          </select>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>{tipo === "pagina" ? "Percorsi" : "Nome dell'evento"}</span>
          <input className={comuni.ingresso} required maxLength={500} value={valore} onChange={(e) => setValore(e.target.value)}
            placeholder={tipo === "pagina" ? "/pricing,/it/piano" : "lettura_fase"} />
        </label>
        {tipo === "evento" && (
          <>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Proprietà (facoltativa)</span>
              <input className={comuni.ingresso} maxLength={40} value={chiave} placeholder="fase"
                onChange={(e) => setChiave(e.target.value.replace(/[^a-zA-Z0-9_]/g, ""))} />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Valore</span>
              <input className={comuni.ingresso} maxLength={200} value={valoreProprieta} placeholder="completata"
                onChange={(e) => setValoreProprieta(e.target.value)} />
            </label>
          </>
        )}
        <button className={comuni.primaria} type="submit" disabled={inCorso || !nome.trim() || !valore.trim()}>Aggiungi</button>
      </form>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {obiettivi.dati && obiettivi.dati.obiettivi.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0, margin: "0.75rem 0 0", display: "grid", gap: "0.5rem" }}>
          {obiettivi.dati.obiettivi.map((o) => (
            <li key={o.id} className={comuni.riga}>
              <span>
                <strong>{o.nome}</strong> · {o.tipo === "pagina" ? "pagina" : "evento"}{" "}
                <span className={comuni.mono}>{o.valore}{Object.entries(o.proprieta).map(([k, v]) => ` (${k} = ${v})`).join("")}</span>
              </span>
              <button className={comuni.secondaria} disabled={inCorso} aria-label={`Togli ${o.nome}`}
                onClick={async () => { await esegui((t) => togliObiettivo(t, o.id)); obiettivi.ricarica(); }}>
                Togli
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
