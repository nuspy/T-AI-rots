"use client";

import { useState } from "react";
import { registro, type VoceRegistro } from "@/lib/api";
import { useDati } from "@/lib/usa";
import stili from "../comuni.module.css";

/* Il registro delle operazioni.
 *
 * Sola lettura, e non per scelta dell'interfaccia: il backend non espone
 * alcun modo di modificarlo. Un registro che si può correggere non è un
 * registro.
 */

/* I tipi di oggetto noti, per il secondo filtro: ogni valore che il backend scrive davvero (grep su
 * `target_type=`/`tipo=` nelle chiamate di audit). Le azioni invece si ricavano da ciò che è arrivato: cambiano
 * più spesso, e un elenco scritto qui resterebbe indietro. */
const TIPI = [
  "user", "plan", "coupon", "reading", "compito", "llm_provider", "impostazioni_credito",
  "blog_section", "blog_post", "blog_tag", "media_image", "api_key",
];

const LIMITE = 200;

export default function Registro() {
  const [filtro, setFiltro] = useState("");
  const [tipo, setTipo] = useState("");
  const [offset, setOffset] = useState(0);
  const { dati, errore, inCorso } = useDati(
    (t) => registro(t, { azione: filtro, target_type: tipo, limite: LIMITE, offset }),
    [filtro, tipo, offset],
  );
  /* Le pagine si accumulano finché non cambia un filtro: allora si riparte da zero, con la pagina nuova al posto
   * di tutte le precedenti — filtrare non deve mostrare insieme a righe di prima e di dopo il cambio.
   *
   * Aggiustata durante il rendering (non in un effetto): `dati` cambia identità a ogni richiesta completata,
   * anche quando l'offset resta 0 (un filtro cambiato) — confrontarlo con l'ultimo visto, invece di aspettare
   * che cambi l'offset, coglie anche quel caso. È il modo che React stesso consiglia per «aggiustare uno stato
   * quando cambia un valore», al posto di un useEffect che si limiterebbe a copiare una prop in uno stato. */
  const [accumulati, setAccumulati] = useState<VoceRegistro[]>([]);
  const [datiVisti, setDatiVisti] = useState<VoceRegistro[] | null>(null);
  if (dati && dati !== datiVisti) {
    setDatiVisti(dati);
    setAccumulati((prima) => (offset === 0 ? dati : [...prima, ...dati]));
  }

  const cambiaFiltro = (v: string) => {
    setFiltro(v);
    setOffset(0);
  };
  const cambiaTipo = (v: string) => {
    setTipo(v);
    setOffset(0);
  };

  /* L'azione scelta resta nel menu anche quando il filtro l'ha resa l'unica,
   * o sparirebbe l'opzione per tornare indietro. */
  const azioni = [...new Set([...accumulati.map((v) => v.azione), ...(filtro ? [filtro] : [])])].sort();
  const forsePiu = (dati?.length ?? 0) === LIMITE;

  return (
    <>
      <div className={stili.intestazione}>
        <div>
          <h1 className={stili.titolo}>Registro</h1>
          <p className={stili.sottotitolo}>
            Chi ha fatto cosa, a cosa, e com&apos;era prima. Ogni operazione
            amministrativa lascia una riga: la scrittura avviene dentro
            l&apos;operazione stessa, non accanto.
          </p>
        </div>
        <select
          className={stili.selezione}
          value={tipo}
          onChange={(e) => cambiaTipo(e.target.value)}
          aria-label="Filtra per oggetto"
          style={{ maxWidth: "12rem" }}
        >
          <option value="">Ogni oggetto</option>
          {TIPI.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <select
          className={stili.selezione}
          value={filtro}
          onChange={(e) => cambiaFiltro(e.target.value)}
          aria-label="Filtra per azione"
          style={{ maxWidth: "16rem" }}
        >
          <option value="">Tutte le azioni</option>
          {azioni.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </div>

      {errore && <p className={stili.errore}>{errore}</p>}
      {inCorso && accumulati.length === 0 && <p className={stili.caricamento}>Caricamento…</p>}

      {accumulati.length === 0 && !inCorso && (
        <div className={stili.vuoto}>Nessuna operazione registrata.</div>
      )}

      {accumulati.length > 0 && (
        <div className={stili.contenitoreTabella}>
          <table className={stili.tabella}>
            <thead>
              <tr>
                <th>Quando</th>
                <th>Chi</th>
                <th>Azione</th>
                <th>Oggetto</th>
                <th>Cambiamento</th>
                <th>Da</th>
              </tr>
            </thead>
            <tbody>
              {accumulati.map((v) => (
                <tr key={v.id}>
                  <td className={stili.mono}>
                    {new Date(v.quando).toLocaleString("it-IT", {
                      day: "2-digit",
                      month: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </td>
                  <td className={stili.mono}>{v.attore !== null ? `#${v.attore}` : "sistema"}</td>
                  <td className={stili.mono}>{v.azione}</td>
                  <td className={stili.mono}>
                    {v.tipo}
                    {v.target ? ` ${v.target.slice(0, 12)}` : ""}
                  </td>
                  <td>
                    <Cambiamento voce={v} />
                  </td>
                  <td className={stili.mono}>{v.ip ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {forsePiu && (
        <div style={{ textAlign: "center", marginTop: 16 }}>
          <button
            type="button"
            className={stili.secondaria}
            disabled={inCorso}
            onClick={() => setOffset((o) => o + LIMITE)}
          >
            {inCorso ? "Caricamento…" : "Carica altro"}
          </button>
        </div>
      )}
    </>
  );
}

/* Solo i campi cambiati.
 *
 * Mostrare i due stati per intero renderebbe la tabella illeggibile, e la
 * domanda a cui si risponde guardando un registro è «cosa è cambiato», non
 * «com'era tutto».
 */
function Cambiamento({ voce }: { voce: VoceRegistro }) {
  const prima = voce.prima ?? {};
  const dopo = voce.dopo ?? {};
  const chiavi = [...new Set([...Object.keys(prima), ...Object.keys(dopo)])];
  const cambiate = chiavi.filter(
    (k) => JSON.stringify(prima[k]) !== JSON.stringify(dopo[k]),
  );

  if (cambiate.length === 0) {
    return <span className={stili.campoAiuto}>—</span>;
  }

  return (
    <ul style={{ margin: 0, padding: 0, listStyle: "none" }}>
      {cambiate.slice(0, 4).map((k) => (
        <li key={k} className={stili.mono} style={{ fontSize: "0.75rem" }}>
          {k}: {rendi(prima[k])} → {rendi(dopo[k])}
        </li>
      ))}
    </ul>
  );
}

function rendi(valore: unknown): string {
  if (valore === undefined || valore === null) return "—";
  if (typeof valore === "string") {
    return valore.length > 24 ? `${valore.slice(0, 24)}…` : valore;
  }
  return JSON.stringify(valore).slice(0, 30);
}
