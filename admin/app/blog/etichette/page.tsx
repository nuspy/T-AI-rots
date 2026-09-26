"use client";

import { useState } from "react";
import { eliminaEtichetta, etichette, rinominaEtichetta, type Etichetta } from "@/lib/blog";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../blog.module.css";
import { Schede } from "../schede";

/* Le etichette (tag) del blog.
 *
 * Nascono da sole scrivendole in un articolo. Qui si sistemano: si corregge un nome (l'indirizzo pubblico
 * `/blog/tag/…` cambia con lui) e si eliminano quelle che non servono più — un'etichetta eliminata sparisce dagli
 * articoli che la portavano, che restano dove sono.
 *
 * Due etichette non possono avere lo stesso nome: se lo si prova, il server risponde 409 e lo dice. Per unirne
 * due basta rinominare una nell'altra dopo aver cambiato gli articoli. */

export default function Etichette() {
  const elenco = useDati(etichette);
  const { esegui, inCorso, errore } = useAzione();
  const [modificando, setModificando] = useState<number | null>(null);
  const [nome, setNome] = useState("");
  const [daEliminare, setDaEliminare] = useState<number | null>(null);

  const salva = async (e: Etichetta) => {
    if (await esegui((t) => rinominaEtichetta(t, e.id, nome.trim()))) {
      setModificando(null);
      elenco.ricarica();
    }
  };

  const elimina = async (e: Etichetta) => {
    if ((await esegui((t) => eliminaEtichetta(t, e.id))) !== null) {
      setDaEliminare(null);
      elenco.ricarica();
    }
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Blog · Etichette</h1>
          <p className={comuni.sottotitolo}>
            Le etichette nascono scrivendole in un articolo. Qui si correggono e si eliminano; eliminandone una, gli
            articoli restano.
          </p>
        </div>
      </div>

      <Schede />

      {(errore || elenco.errore) && (
        <p className={comuni.errore} role="alert">
          {errore ?? elenco.errore}
        </p>
      )}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {elenco.dati && elenco.dati.length === 0 && (
        <div className={comuni.vuoto}>Nessuna etichetta ancora: si creano scrivendole in un articolo.</div>
      )}

      {elenco.dati && elenco.dati.length > 0 && (
        <ul className={`${stili.elenco} ${elenco.inCorso ? comuni.inRicarica : ""}`} aria-label="Etichette" style={{ marginBottom: "1rem" }}>
          {elenco.dati.map((e) => (
            <li key={e.id} className={stili.voce} style={{ gridTemplateColumns: "minmax(0, 1fr)" }}>
              {modificando === e.id ? (
                <form
                  className={comuni.riga}
                  onSubmit={(ev) => {
                    ev.preventDefault();
                    void salva(e);
                  }}
                >
                  <label className={comuni.campo} style={{ marginBottom: 0 }}>
                    <span className={comuni.campoEtichetta}>Nome</span>
                    <input className={comuni.ingresso} value={nome} maxLength={80} autoFocus onChange={(ev) => setNome(ev.target.value)} />
                  </label>
                  <button type="submit" className={comuni.primaria} style={{ height: 44 }} disabled={inCorso || !nome.trim() || nome.trim() === e.nome}>
                    Salva
                  </button>
                  <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setModificando(null)}>
                    Annulla
                  </button>
                </form>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem 1rem", alignItems: "center" }}>
                  <div className={stili.voceTesto} style={{ flex: "1 1 12rem" }}>
                    <strong>{e.nome}</strong>
                    <p className={stili.dettagli}>
                      <span className={comuni.mono}>/blog/tag/{e.slug}</span>
                      <span>{e.n === 1 ? "1 articolo" : `${e.n} articoli`}</span>
                    </p>
                  </div>
                  <button
                    type="button"
                    className={comuni.secondaria}
                    style={{ height: 44 }}
                    disabled={inCorso}
                    onClick={() => {
                      setNome(e.nome);
                      setDaEliminare(null);
                      setModificando(e.id);
                    }}
                  >
                    Rinomina
                  </button>
                  {daEliminare === e.id ? (
                    <span className={stili.conferma} role="alert">
                      Eliminare l&apos;etichetta?
                      <button type="button" className={comuni.distruttiva} style={{ height: 44 }} disabled={inCorso} onClick={() => elimina(e)}>
                        Sì, elimina
                      </button>
                      <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setDaEliminare(null)}>
                        Annulla
                      </button>
                    </span>
                  ) : (
                    <button
                      type="button"
                      className={comuni.distruttiva}
                      style={{ height: 44 }}
                      disabled={inCorso}
                      onClick={() => {
                        setModificando(null);
                        setDaEliminare(e.id);
                      }}
                    >
                      Elimina
                    </button>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
