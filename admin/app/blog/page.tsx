"use client";

import Link from "next/link";
import { useCallback, useMemo, useState } from "react";
import {
  articoli,
  cambiaStato,
  eliminaArticolo,
  sezioni,
  urlMedia,
  type Articolo,
  type StatoArticolo,
} from "@/lib/blog";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./blog.module.css";
import { etichettaStato, sezioniInOrdine } from "./aiuti";
import { Schede } from "./schede";

/* Gli articoli del blog, tutti, anche le bozze e quelli programmati.
 *
 * Il pubblico vede solo ciò che è «pubblicato» con la data arrivata e in una sezione visibile; qui si
 * vede tutto, con lo stato scritto a parole. «Programmato» non è uno stato a sé nel database — è
 * `pubblicato` con una data nel futuro — ma per chi amministra è una cosa diversa, e si legge così.
 */

const STATI: { valore: StatoArticolo | ""; etichetta: string }[] = [
  { valore: "", etichetta: "Tutti" },
  { valore: "bozza", etichetta: "Bozze" },
  { valore: "pubblicato", etichetta: "Pubblicati" },
  { valore: "archiviato", etichetta: "Archiviati" },
];

const PER_PAGINA = 20;

export default function Articoli() {
  const [stato, setStato] = useState<StatoArticolo | "">("");
  const [sezioneId, setSezioneId] = useState("");
  const [ricerca, setRicerca] = useState("");
  const [cerca, setCerca] = useState("");
  const [pagina, setPagina] = useState(1);

  const elenco = useDati(
    useCallback(
      (t: string) =>
        articoli(t, {
          stato: stato || undefined,
          sezione_id: sezioneId ? Number(sezioneId) : undefined,
          q: cerca || undefined,
          pagina,
          per_pagina: PER_PAGINA,
        }),
      [stato, sezioneId, cerca, pagina],
    ),
  );
  const tutteLeSezioni = useDati(sezioni);
  const albero = useMemo(() => sezioniInOrdine(tutteLeSezioni.dati ?? []), [tutteLeSezioni.dati]);
  const nomeSezione = useMemo(() => new Map(albero.map((v) => [v.sezione.id, v.percorso])), [albero]);

  const { esegui, inCorso, errore } = useAzione();
  const [daEliminare, setDaEliminare] = useState<string | null>(null);

  const totale = elenco.dati?.totale ?? 0;
  const pagine = Math.max(1, Math.ceil(totale / PER_PAGINA));

  const cambia = async (a: Articolo, azione: "pubblica" | "archivia" | "bozza") => {
    if (await esegui((t) => cambiaStato(t, a.id, azione))) elenco.ricarica();
  };
  const elimina = async (id: string) => {
    if ((await esegui((t) => eliminaArticolo(t, id))) !== null) {
      setDaEliminare(null);
      elenco.ricarica();
    }
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Blog</h1>
          <p className={comuni.sottotitolo}>
            Gli articoli, con le bozze e quelli programmati. Il pubblico vede solo ciò che è pubblicato, con la data
            arrivata, in una sezione visibile.
          </p>
        </div>
        <Link href="/blog/nuovo" className={stili.comandoLink}>
          Nuovo articolo
        </Link>
      </div>

      <Schede />

      <div className={comuni.filtri} role="group" aria-label="Stato">
        {STATI.map((s) => (
          <button
            key={s.valore || "tutti"}
            className={stato === s.valore ? comuni.filtroScelto : comuni.filtro}
            aria-pressed={stato === s.valore}
            onClick={() => {
              setStato(s.valore);
              setPagina(1);
            }}
          >
            {s.etichetta}
          </button>
        ))}
      </div>

      <form
        className={stili.barra}
        role="search"
        onSubmit={(e) => {
          e.preventDefault();
          setCerca(ricerca.trim());
          setPagina(1);
        }}
      >
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Cerca</span>
          <input
            className={comuni.ingresso}
            type="search"
            value={ricerca}
            maxLength={100}
            placeholder="Titolo o testo"
            onChange={(e) => setRicerca(e.target.value)}
          />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Sezione</span>
          <select
            className={comuni.selezione}
            value={sezioneId}
            onChange={(e) => {
              setSezioneId(e.target.value);
              setPagina(1);
            }}
          >
            <option value="">Tutte</option>
            {albero.map((v) => (
              <option key={v.sezione.id} value={v.sezione.id}>
                {"— ".repeat(v.livello)}
                {v.sezione.nome}
              </option>
            ))}
          </select>
        </label>
        <button className={comuni.secondaria} type="submit" style={{ height: 44, marginBottom: "0.9rem" }}>
          Cerca
        </button>
      </form>

      {(elenco.errore || errore) && (
        <p className={comuni.errore} role="alert">
          {errore ?? elenco.errore}
        </p>
      )}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {elenco.dati &&
        (elenco.dati.articoli.length === 0 ? (
          <div className={comuni.vuoto}>
            Nessun articolo{stato || cerca || sezioneId ? " con questi filtri" : " ancora"}.{" "}
            {!stato && !cerca && !sezioneId && <Link href="/blog/nuovo">Scrivi il primo.</Link>}
          </div>
        ) : (
          <ul className={`${stili.elenco} ${elenco.inCorso ? comuni.inRicarica : ""}`} aria-label="Articoli">
            {elenco.dati.articoli.map((a) => {
              const s = etichettaStato(a);
              return (
                <li key={a.id} className={stili.voce}>
                  {a.immagine ? (
                    // eslint-disable-next-line @next/next/no-img-element -- la copertina, già piccola per il browser
                    <img className={stili.copertina} src={urlMedia(a.immagine) ?? ""} alt="" width={72} height={54} />
                  ) : (
                    <span className={stili.senzaCopertina} aria-hidden="true">
                      —
                    </span>
                  )}
                  <div className={stili.voceTesto}>
                    <Link href={`/blog/${a.id}`} className={stili.voceTitolo}>
                      {a.in_evidenza && (
                        <span className={stili.stellina} title="In evidenza" aria-label="In evidenza">
                          ★{" "}
                        </span>
                      )}
                      {a.titolo}
                    </Link>
                    <p className={stili.dettagli}>
                      <span className={`${comuni.stato} ${s.classe}`}>{s.testo}</span>
                      <span>{a.sezione_id ? (nomeSezione.get(a.sezione_id) ?? "—") : "senza sezione"}</span>
                      <span>{a.pubblicato_il ? quandoCompleto(a.pubblicato_il) : `modificato ${quandoCompleto(a.aggiornato)}`}</span>
                      {a.autore && <span>{a.autore.nome}</span>}
                      <span>{a.tempo_lettura} min</span>
                    </p>
                  </div>
                  <div className={stili.azioniVoce}>
                    <Link href={`/blog/${a.id}`} className={comuni.secondaria} style={{ display: "inline-flex", alignItems: "center" }}>
                      Modifica
                    </Link>
                    {a.stato !== "pubblicato" && (
                      <button className={comuni.secondaria} disabled={inCorso} onClick={() => cambia(a, "pubblica")}>
                        Pubblica
                      </button>
                    )}
                    {a.stato === "pubblicato" && (
                      <button className={comuni.secondaria} disabled={inCorso} onClick={() => cambia(a, "bozza")}>
                        Riporta a bozza
                      </button>
                    )}
                    {a.stato !== "archiviato" && (
                      <button className={comuni.secondaria} disabled={inCorso} onClick={() => cambia(a, "archivia")}>
                        Archivia
                      </button>
                    )}
                    {daEliminare === a.id ? (
                      <span className={stili.conferma} role="alert">
                        Eliminare per sempre?
                        <button className={comuni.distruttiva} disabled={inCorso} onClick={() => elimina(a.id)}>
                          Sì, elimina
                        </button>
                        <button className={comuni.secondaria} onClick={() => setDaEliminare(null)}>
                          Annulla
                        </button>
                      </span>
                    ) : (
                      <button className={comuni.distruttiva} disabled={inCorso} onClick={() => setDaEliminare(a.id)}>
                        Elimina
                      </button>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        ))}

      {elenco.dati && totale > PER_PAGINA && (
        <div className={comuni.paginazione}>
          <span>
            Pagina {pagina} di {pagine} · {totale} articoli
          </span>
          <div className={comuni.paginazioneComandi}>
            <button className={comuni.secondaria} disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>
              Precedente
            </button>
            <button className={comuni.secondaria} disabled={pagina >= pagine} onClick={() => setPagina(pagina + 1)}>
              Successiva
            </button>
          </div>
        </div>
      )}
    </>
  );
}
