"use client";

import { useState } from "react";
import { scaricaReport, type TipoReport } from "@/lib/api";
import { useAzione } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./report.module.css";

/* Le esportazioni in CSV, per la contabilità e per chi analizza fuori dalla
 * console.
 *
 * Il file si scarica con una richiesta autenticata e non con un
 * collegamento: un `<a href>` non manda il token, e un token in querystring
 * resterebbe scritto nei log di ogni proxy sulla strada.
 */

const REPORT: { tipo: TipoReport; titolo: string; descrizione: string; periodo: boolean }[] = [
  {
    tipo: "utenti",
    titolo: "Utenti",
    descrizione: "Tutti gli iscritti: email, nome, lingua, stato, data d'iscrizione, chi li ha invitati.",
    periodo: false,
  },
  {
    tipo: "pagamenti",
    titolo: "Pagamenti",
    descrizione: "Ogni passaggio alla cassa nel periodo, con piano, stato e importo in centesimi.",
    periodo: true,
  },
  {
    tipo: "crediti",
    titolo: "Movimenti dei crediti",
    descrizione: "Il registro dei crediti nel periodo: accrediti, consumi, rimborsi, rettifiche con la loro nota.",
    periodo: true,
  },
  {
    tipo: "letture",
    titolo: "Letture",
    descrizione: "Metadati delle letture nel periodo: stesa, stato, come è stata pagata, esito della guardia, giudizio.",
    periodo: true,
  },
];

const PERIODI = [7, 30, 90, 365, 3650];

function periodo(g: number): string {
  if (g === 3650) return "Tutto";
  if (g === 365) return "Ultimo anno";
  return `Ultimi ${g} giorni`;
}

export default function Report() {
  const [giorni, setGiorni] = useState(30);
  const [inScarico, setInScarico] = useState<TipoReport | null>(null);
  const [scaricato, setScaricato] = useState<string | null>(null);
  const { esegui, errore } = useAzione();

  const scarica = async (tipo: TipoReport) => {
    setInScarico(tipo);
    setScaricato(null);
    const nome = await esegui((t) => scaricaReport(t, tipo, giorni));
    setInScarico(null);
    if (nome) setScaricato(nome);
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Report</h1>
          <p className={comuni.sottotitolo}>
            Esportazioni in CSV, in UTF-8 con BOM così Excel legge le lettere
            accentate. Gli importi sono in centesimi, come nel database.
          </p>
        </div>
      </div>

      <p className={comuni.avviso}>
        <strong>Le letture escono senza contenuto.</strong> Il report delle
        letture porta solo metadati — quale stesa, quando, com&apos;è finita —
        e mai la domanda dell&apos;utente, le sue risposte all&apos;intervista o
        il responso. Sono dati intimi, e per amministrare il servizio non
        servono.
      </p>

      <div className={comuni.filtri} role="group" aria-label="Periodo">
        {PERIODI.map((g) => (
          <button
            key={g}
            className={g === giorni ? comuni.filtroScelto : comuni.filtro}
            aria-pressed={g === giorni}
            onClick={() => setGiorni(g)}
          >
            {periodo(g)}
          </button>
        ))}
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {scaricato && <p className={comuni.esito}>Scaricato {scaricato}.</p>}

      <div className={stili.elenco}>
        {REPORT.map((r) => (
          <section key={r.tipo} className={stili.voce}>
            <div>
              <h2 className={stili.voceTitolo}>{r.titolo}</h2>
              <p className={stili.voceNota}>{r.descrizione}</p>
              <p className={stili.vocePeriodo}>
                {r.periodo ? periodo(giorni) : "Sempre completo: il periodo non si applica."}
              </p>
            </div>
            <button
              className={comuni.secondaria}
              onClick={() => scarica(r.tipo)}
              disabled={inScarico !== null}
            >
              {inScarico === r.tipo ? "Preparazione…" : `Scarica ${r.tipo}.csv`}
            </button>
          </section>
        ))}
      </div>
    </>
  );
}
