"use client";

/* Dove si fermano le letture (v9.5). Non dagli eventi ma dal database delle letture: vale per TUTTE le letture aperte
 * nel periodo, anche quelle di chi non ha accettato le statistiche e quelle di prima della v9.5. L'imbuto dice quante
 * arrivano a ogni passo e quante se ne perdono; sotto, dove si fermano con il dettaglio (dopo quante risposte
 * dell'intervista, con quante carte scelte, quante rivelate). Gli anonimi a parte: per loro «completata» è
 * l'anteprima, e conta quanti poi passano a un account. */

import { useCallback, useState } from "react";
import {
  calcolaLettureFerme, type GruppoLetture, type PiattaformaAnalisi, type VarianteLettura,
} from "@/lib/analytics";
import { useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Barre, Tessera, percento } from "../../grafici";
import grafici from "../../grafici.module.css";
import stili from "../../statistiche.module.css";
import { formatta } from "../comuni";

const GRUPPI: [GruppoLetture, string][] = [["iscritti", "Iscritti"], ["anonimi", "Anonimi"], ["tutti", "Tutti"]];
/* v9.5: la prova 90/10 fra la lettura classica e quella in chat (le letture di prima della prova sono classiche). */
const VISTE: [VarianteLettura | "confronto", string][] = [
  ["tutte", "Tutte le versioni"], ["classica", "Classica"], ["chat", "In chat"], ["confronto", "Confronta classica e chat"],
];

function Pulsanti<T extends string>({ voci, valore, imposta, etichetta }: {
  voci: [T, string][]; valore: T; imposta: (v: T) => void; etichetta: string;
}) {
  return (
    <div role="group" aria-label={etichetta} style={{ display: "flex", flexWrap: "wrap", gap: ".5rem", margin: ".6rem 0 1rem" }}>
      {voci.map(([v, nome]) => (
        <button key={v} type="button" aria-pressed={valore === v} style={{ minHeight: 44 }}
                className={valore === v ? comuni.primaria : comuni.secondaria} onClick={() => imposta(v)}>
          {nome}
        </button>
      ))}
    </div>
  );
}

export function LettureFerme({ da, a, piattaforma = "tutte" }: { da: string; a: string; piattaforma?: PiattaformaAnalisi }) {
  const [gruppo, setGruppo] = useState<GruppoLetture>("iscritti");
  const [vista, setVista] = useState<VarianteLettura | "confronto">("tutte");
  return (
    <section style={{ marginTop: "2rem" }} aria-labelledby="letture-ferme">
      <h2 id="letture-ferme" className={comuni.titolo} style={{ fontSize: "1.3rem" }}>Dove si fermano le letture</h2>
      <p className={comuni.sottotitolo}>
        Dal database delle letture: tutte quelle aperte nel periodo, anche di chi non ha accettato le statistiche.
        Una lettura si apre quando la domanda e la stesa sono inviate.
      </p>
      <Pulsanti voci={GRUPPI} valore={gruppo} imposta={setGruppo} etichetta="Gruppo" />
      <Pulsanti voci={VISTE} valore={vista} imposta={setVista} etichetta="Versione della lettura" />
      {vista === "confronto"
        ? <Confronto da={da} a={a} gruppo={gruppo} piattaforma={piattaforma} />
        : <Studio da={da} a={a} gruppo={gruppo} variante={vista} piattaforma={piattaforma} />}
    </section>
  );
}

/* Classica e chat fianco a fianco: per ogni passo la quota di letture che ci arriva. */
function Confronto({ da, a, gruppo, piattaforma }: { da: string; a: string; gruppo: GruppoLetture; piattaforma: PiattaformaAnalisi }) {
  const classica = useDati(useCallback((t: string) => calcolaLettureFerme(t, { da, a, gruppo, variante: "classica", piattaforma }), [da, a, gruppo, piattaforma]));
  const chat = useDati(useCallback((t: string) => calcolaLettureFerme(t, { da, a, gruppo, variante: "chat", piattaforma }), [da, a, gruppo, piattaforma]));
  if (classica.errore || chat.errore) return <p className={comuni.errore} role="alert">{classica.errore ?? chat.errore}</p>;
  if (!classica.dati || !chat.dati) return <p className={comuni.caricamento}>Caricamento…</p>;
  const c = classica.dati;
  const h = chat.dati;
  return (
    <>
      <div className={grafici.tessere}>
        <Tessera etichetta="Classica: arrivate in fondo" valore={c.imbuto[c.imbuto.length - 1]?.letture ?? 0}
                 nota={`${percento(c.imbuto[c.imbuto.length - 1]?.quota ?? null, 1)} di ${formatta(c.letture)} aperte`} />
        <Tessera etichetta="Chat: arrivate in fondo" valore={h.imbuto[h.imbuto.length - 1]?.letture ?? 0}
                 nota={`${percento(h.imbuto[h.imbuto.length - 1]?.quota ?? null, 1)} di ${formatta(h.letture)} aperte`} />
      </div>
      <div className={comuni.contenitoreTabella}>
        <table className={comuni.tabella}>
          <thead><tr><th>Passo</th><th>Classica</th><th>Chat</th></tr></thead>
          <tbody>
            {c.imbuto.map((p, i) => (
              <tr key={p.passo}>
                <td>{p.etichetta}</td>
                <td>{formatta(p.letture)} · {percento(p.quota, 1)}</td>
                <td>{formatta(h.imbuto[i]?.letture)} · {percento(h.imbuto[i]?.quota ?? null, 1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function Studio({ da, a, gruppo, variante, piattaforma }: {
  da: string; a: string; gruppo: GruppoLetture; variante: VarianteLettura; piattaforma: PiattaformaAnalisi;
}) {
  const esito = useDati(useCallback(
    (t: string) => calcolaLettureFerme(t, { da, a, gruppo, variante, piattaforma }), [da, a, gruppo, variante, piattaforma],
  ));
  const d = esito.dati;

  return (
    <>
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
    </>
  );
}
