"use client";

/* Uscite (v8.6): da quale pagina finisce la visita e, quando è una pagina di lettura, che cosa la persona aveva
 * appena fatto. La pagina d'uscita è l'ultima pagina vista della sessione (l'osservatore manda l'ultimo lotto anche
 * quando la scheda si chiude); l'ultima azione è l'ultimo evento sulla pagina di lettura prima di uscire: la fase, un
 * gesto (mescola, taglia, sceglie, rivela), il paywall… «Nessuna azione» vuol dire entrata e uscita senza toccare
 * nulla. Una barra delle pagine si tocca per aprire l'Esploratore su quelle visite. */

import { useCallback, useState } from "react";
import { calcolaUscite, type AzioneUscita, type PiattaformaAnalisi } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Barre, Tessera, percento } from "../../grafici";
import grafici from "../../grafici.module.css";
import stili from "../../statistiche.module.css";
import { FiltriPeriodo, etichettaPeriodo, formatta, useApprofondisci, usePeriodo } from "../comuni";
import { LettureFerme } from "./letture-ferme";

const barreAzioni = (azioni: AzioneUscita[], quante = 15) =>
  azioni.slice(0, quante).map((a) => ({
    chiave: a.azione,
    etichetta: a.etichetta,
    valore: a.sessioni,
    dettaglio: percento(a.quota, 1),
  }));

export default function Uscite() {
  const { giorni, da, a, imposta } = usePeriodo();
  const approfondisci = useApprofondisci(giorni);
  /* v9.5: sito, Android o iOS (l'app marca ogni evento; il sito dalla v9.5, prima senza marca = sito). */
  const [piattaforma, setPiattaforma] = useState<PiattaformaAnalisi>("tutte");
  const esito = useDati(useCallback((t: string) => calcolaUscite(t, { da, a, limite: 25, piattaforma }), [da, a, piattaforma]));

  const d = esito.dati;
  const letture = d?.letture;
  const soloVista = letture?.azioni.find((x) => x.azione === "(nessuna azione)");
  const vuoto = d && !d.sessioni;

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Uscite</h1>
          <p className={comuni.sottotitolo}>
            L&apos;ultima pagina vista di ogni visita e, per le pagine di lettura, l&apos;ultima cosa fatta prima di
            andarsene. Tocca una pagina per vedere quelle visite nell&apos;Esploratore.
          </p>
        </div>
      </div>
      <FiltriPeriodo giorni={giorni} imposta={imposta} />
      <SceltaPiattaforma valore={piattaforma} imposta={setPiattaforma} />

      {esito.errore && <p className={comuni.errore} role="alert">{esito.errore}</p>}
      {!d && esito.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {vuoto && <div className={comuni.vuoto}>Nessuna visita in questo periodo: allarga il periodo.</div>}

      {d && !vuoto && (
        <div className={esito.inCorso ? comuni.inRicarica : undefined}>
          <div className={grafici.tessere}>
            <Tessera etichetta="Visite" valore={d.sessioni} nota={etichettaPeriodo(giorni).toLowerCase()} />
            <Tessera etichetta="Finite su una lettura" valore={letture?.sessioni ?? 0}
              nota={`${percento(d.sessioni ? (letture?.sessioni ?? 0) / d.sessioni : null, 1)} delle visite`} />
            <Tessera etichetta="Lettura lasciata senza toccare nulla" valore={soloVista?.sessioni ?? 0}
              nota={`${percento(soloVista?.quota ?? (letture?.sessioni ? 0 : null), 1)} di chi esce da una lettura`} />
          </div>

          <div className={stili.coppie}>
            <Barre
              titolo="Pagine d'uscita"
              descrizione="Visite finite su ciascuna pagina. Accanto: il tasso d'uscita (uscite su visualizzazioni della pagina)."
              unita="visite"
              barre={d.pagine.map((p) => ({
                chiave: p.pagina,
                etichetta: p.lettura ? `${p.pagina} · lettura` : p.pagina,
                valore: p.uscite,
                dettaglio: p.tasso_uscita === null ? undefined : `${percento(p.tasso_uscita, 1)} d'uscita`,
              }))}
              colonneTabella={[
                { titolo: "visualizzazioni", valori: d.pagine.map((p) => formatta(p.visualizzazioni)) },
                { titolo: "tasso d'uscita", valori: d.pagine.map((p) => percento(p.tasso_uscita, 1)) },
                { titolo: "visite di una sola pagina", valori: d.pagine.map((p) => formatta(p.uscite_unica_pagina)) },
              ]}
              onScegli={(v) => approfondisci("visite", ["sessioni", "pagine_per_sessione", "tempo_medio"], "uscita", v, "ingresso")}
            />

            {letture && letture.sessioni > 0 ? (
              <Barre
                titolo="Letture: l'ultima azione prima di uscire"
                descrizione="Per le visite finite su una pagina di lettura (guidata o col mazzo fisico, anche la v1 sotto /old)."
                unita="visite"
                barre={barreAzioni(letture.azioni)}
              />
            ) : (
              <div className={comuni.vuoto}>Nessuna visita è finita su una pagina di lettura in questo periodo.</div>
            )}
          </div>

          {letture && letture.per_pagina.length > 1 && (
            <div className={stili.coppie}>
              {letture.per_pagina.slice(0, 6).map((p) => (
                <Barre
                  key={p.pagina}
                  titolo={`Ultima azione su ${p.pagina}`}
                  descrizione={`${formatta(p.sessioni)} visite finite su questa pagina.`}
                  unita="visite"
                  barre={barreAzioni(p.azioni, 10)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      <LettureFerme da={da} a={a} piattaforma={piattaforma} />
    </>
  );
}

const PIATTAFORME: [PiattaformaAnalisi, string][] = [["tutte", "Tutte"], ["web", "Sito"], ["android", "Android"], ["ios", "iOS"]];

function SceltaPiattaforma({ valore, imposta }: { valore: PiattaformaAnalisi; imposta: (p: PiattaformaAnalisi) => void }) {
  return (
    <div role="group" aria-label="Piattaforma" style={{ display: "flex", flexWrap: "wrap", gap: ".5rem", margin: ".2rem 0 1rem" }}>
      {PIATTAFORME.map(([p, nome]) => (
        <button key={p} type="button" aria-pressed={valore === p} style={{ minHeight: 44 }}
                className={valore === p ? comuni.primaria : comuni.secondaria} onClick={() => imposta(p)}>
          {nome}
        </button>
      ))}
    </div>
  );
}
