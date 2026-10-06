"use client";

/* Dove si fermano le letture (v9.5). Non dagli eventi ma dal database delle letture: vale per TUTTE le letture aperte
 * nel periodo, anche quelle di chi non ha accettato le statistiche e quelle di prima della v9.5. L'imbuto dice quante
 * arrivano a ogni passo e quante se ne perdono; sotto, dove si fermano con il dettaglio (dopo quante risposte
 * dell'intervista, con quante carte scelte, quante rivelate). Gli anonimi a parte: per loro «completata» è
 * l'anteprima, e conta quanti poi passano a un account. */

import { useCallback, useState } from "react";
import { calcolaLettureFerme, type GruppoLetture } from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Barre, Tessera, percento } from "../../grafici";
import grafici from "../../grafici.module.css";
import stili from "../../statistiche.module.css";
import { formatta } from "../comuni";

const GRUPPI: [GruppoLetture, string][] = [["iscritti", "Iscritti"], ["anonimi", "Anonimi"], ["tutti", "Tutti"]];

export function LettureFerme({ da, a }: { da: string; a: string }) {
  const [gruppo, setGruppo] = useState<GruppoLetture>("iscritti");
  const esito = useDati(useCallback((t: string) => calcolaLettureFerme(t, { da, a, gruppo }), [da, a, gruppo]));
  const d = esito.dati;

  return (
    <section style={{ marginTop: "2rem" }} aria-labelledby="letture-ferme">
      <h2 id="letture-ferme" className={comuni.titolo} style={{ fontSize: "1.3rem" }}>Dove si fermano le letture</h2>
      <p className={comuni.sottotitolo}>
        Dal database delle letture: tutte quelle aperte nel periodo, anche di chi non ha accettato le statistiche.
        Una lettura si apre quando la domanda e la stesa sono inviate.
      </p>
      <div role="group" aria-label="Gruppo" style={{ display: "flex", flexWrap: "wrap", gap: ".5rem", margin: ".6rem 0 1rem" }}>
        {GRUPPI.map(([g, nome]) => (
          <button key={g} type="button" aria-pressed={gruppo === g} style={{ minHeight: 44 }}
                  className={gruppo === g ? comuni.primaria : comuni.secondaria} onClick={() => setGruppo(g)}>
            {nome}
          </button>
        ))}
      </div>

      {esito.errore && <p className={comuni.errore} role="alert">{esito.errore}</p>}
      {!d && esito.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {d && d.letture === 0 && <div className={comuni.vuoto}>Nessuna lettura aperta in questo periodo.</div>}

      {d && d.letture > 0 && (
        <div className={esito.inCorso ? comuni.inRicarica : undefined}>
          <div className={grafici.tessere}>
            <Tessera etichetta="Letture aperte" valore={d.letture} nota={d.annullate ? `più ${d.annullate} annullate` : "nel periodo"} />
            <Tessera etichetta="Arrivate in fondo" valore={d.imbuto[d.imbuto.length - 1]?.letture ?? 0}
                     nota={`${percento(d.imbuto[d.imbuto.length - 1]?.quota ?? null, 1)} delle aperte`} />
            {d.anteprima && (
              <Tessera etichetta="Anteprima → account" valore={d.anteprima.passate_a_un_account}
                       nota={`${percento(d.anteprima.quota, 1)} delle ${formatta(d.anteprima.completate)} anteprime`} />
            )}
          </div>

          <div className={stili.coppie}>
            <Barre
              titolo="Fino a dove arrivano"
              descrizione="Letture che raggiungono ogni passo. Accanto: la quota sulle letture aperte."
              unita="letture"
              barre={d.imbuto.map((p) => ({
                chiave: p.passo, etichetta: p.etichetta, valore: p.letture, dettaglio: percento(p.quota, 1),
              }))}
              colonneTabella={[
                { titolo: "perse dal passo prima", valori: d.imbuto.map((p) => formatta(p.perse_dal_passo_prima)) },
                { titolo: "passano al passo", valori: d.imbuto.map((p) => percento(p.tasso_passaggio, 1)) },
              ]}
            />
            <Barre
              titolo="Dove si fermano"
              descrizione="Letture rimaste ferme a ciascun passo (non completate). Accanto: la quota sulle aperte."
              unita="letture"
              barre={d.ferme.filter((f) => f.letture > 0).map((f) => ({
                chiave: f.stato, etichetta: f.etichetta, valore: f.letture, dettaglio: percento(f.quota, 1),
              }))}
            />
          </div>

          <div className={stili.coppie}>
            {d.ferme.filter((f) => f.dettaglio && f.dettaglio.length > 0).map((f) => (
              <Barre
                key={f.stato}
                titolo={f.etichetta}
                descrizione={`${formatta(f.letture)} letture: il punto esatto.`}
                unita="letture"
                barre={f.dettaglio!.map((x) => ({ chiave: x.etichetta, etichetta: x.etichetta, valore: x.letture }))}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
