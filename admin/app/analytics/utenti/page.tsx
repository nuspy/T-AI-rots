"use client";

/* Utenti (v8): chi si iscrive, da dove arriva, quanto vale ogni campagna.
 *
 * Età e genere vengono dal profilo (facoltativi: molti «n.d.»); canale e campagna dal primo contatto
 * registrato dagli analytics, quindi solo per chi si è iscritto dopo il loro rilascio e non si è opposto.
 * Il campo «trans» del profilo non entra mai in queste statistiche.
 */

import comuni from "../../comuni.module.css";
import { Barre, Colonne, Tessera } from "../../grafici";
import grafici from "../../grafici.module.css";
import stili from "../../statistiche.module.css";
import { FiltriPeriodo, barreDa, etichettaPeriodo, formatta, serie, useApprofondisci, usePeriodo, useRisultato, useSegni } from "../comuni";
import { BottoniEsporta } from "../esporta";
import { PannelloAI } from "../pannello-ai";

const FASCE = ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+", "(n.d.)"];

export default function Utenti() {
  const { giorni, da, a, imposta } = usePeriodo();
  const segni = useSegni(da, a);
  const approfondisci = useApprofondisci(giorni);
  const base = { da, a, sorgente: "utenti" };

  const totali = useRisultato({ ...base, misure: ["utenti", "eta_media", "attivi_30g", "visite_prima"], confronto: "precedente" });
  const andamento = useRisultato({ ...base, misure: ["utenti"], granularita: "giorno", limite: 400 });
  const per = (d: string) => ({ ...base, misure: ["utenti"], dimensioni: [d], limite: 12 });
  const eta = useRisultato(per("fascia_eta"));
  const genere = useRisultato(per("genere"));
  const canale = useRisultato(per("primo_canale"));
  const campagna = useRisultato(per("prima_campagna"));
  const lingua = useRisultato(per("lingua_account"));
  const paese = useRisultato(per("paese"));
  const visitePrima = useRisultato(per("visite_prima_fascia"));
  const incrocio = useRisultato({ ...base, misure: ["utenti"], dimensioni: ["fascia_eta", "genere"], limite: 100 });
  const valoreCampagne = useRisultato({
    da, a, sorgente: "acquisti", misure: ["ricavi", "clienti", "acquisti"], dimensioni: ["prima_campagna"], limite: 20,
  });

  const t = totali.dati?.totali;
  const p = totali.dati?.confronto?.totali;
  const tocca = (d: string) => (v: string) => approfondisci("utenti", ["utenti", "eta_media"], d, v, d === "fascia_eta" ? "genere" : "fascia_eta");

  // Età × genere come tabella a doppia entrata: più leggibile di un grafico a gruppi su un telefono.
  const generi = Array.from(new Set((incrocio.dati?.righe ?? []).map((r) => String(r.genere)))).sort();
  const cella = (f: string, g: string) =>
    incrocio.dati?.righe.find((r) => r.fascia_eta === f && r.genere === g)?.utenti ?? 0;

  // Valore per campagna: iscritti nel periodo e ricavi nel periodo, per campagna d'origine.
  const iscrittiPer = new Map((campagna.dati?.righe ?? []).map((r) => [String(r.prima_campagna), Number(r.utenti)]));
  const campagneValore = (valoreCampagne.dati?.righe ?? []).map((r) => {
    const nome = String(r.prima_campagna);
    const iscritti = iscrittiPer.get(nome) ?? null;
    return { nome, ricavi: Number(r.ricavi), clienti: Number(r.clienti), iscritti, perIscritto: iscritti ? Number(r.ricavi) / iscritti : null };
  });

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Utenti</h1>
          <p className={comuni.sottotitolo}>
            Iscritti nel periodo: età, genere, canale e campagna d&apos;origine. Età e genere sono facoltativi nel profilo;
            canale e campagna esistono per chi si è iscritto dopo il rilascio degli analytics.
          </p>
        </div>
      </div>
      <FiltriPeriodo giorni={giorni} imposta={imposta} />
      {totali.errore && <p className={comuni.errore} role="alert">{totali.errore}</p>}
      {!totali.dati && totali.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {t && (
        <div className={totali.inCorso ? comuni.inRicarica : undefined}>
          <div className={grafici.tessere}>
            <Tessera etichetta="Nuovi iscritti" valore={Number(t.utenti)} precedente={p ? Number(p.utenti) : null} />
            <Tessera etichetta="Età media" valore={t.eta_media === null ? null : Number(t.eta_media)}
              formato={(n) => formatta(n, "decimale")} nota="di chi l'ha indicata" />
            <Tessera etichetta="Ancora attivi" valore={Number(t.attivi_30g)} nota="di questi iscritti, visti negli ultimi 30 giorni" />
            <Tessera etichetta="Visite prima di iscriversi" valore={t.visite_prima === null ? null : Number(t.visite_prima)}
              formato={(n) => formatta(n, "decimale")} nota="media, solo per chi ha accettato i cookie" />
          </div>

          <Colonne segni={segni} titolo="Iscritti al giorno" descrizione={`${etichettaPeriodo(giorni)}, giorni italiani.`}
            unita="iscritti" punti={serie(andamento.dati?.righe, "utenti", da, a)} />

          <div className={stili.coppie}>
            <Barre titolo="Fasce d'età" unita="iscritti" onScegli={tocca("fascia_eta")}
              barre={FASCE.map((f) => ({ chiave: f, etichetta: f, valore: Number(eta.dati?.righe.find((r) => r.fascia_eta === f)?.utenti ?? 0) }))
                .filter((b) => b.valore > 0)} />
            <Barre titolo="Genere" unita="iscritti" barre={barreDa(genere.dati, "genere", "utenti")} onScegli={tocca("genere")} />
            <Barre titolo="Primo canale" descrizione="Da dove sono arrivati la prima volta." unita="iscritti"
              barre={barreDa(canale.dati, "primo_canale", "utenti")} onScegli={tocca("primo_canale")} />
            <Barre titolo="Prima campagna" unita="iscritti" barre={barreDa(campagna.dati, "prima_campagna", "utenti")}
              onScegli={tocca("prima_campagna")} />
            <Barre titolo="Paese" descrizione="Dall'IP dell'ultima visita con l'accesso fatto." unita="iscritti"
              barre={barreDa(paese.dati, "paese", "utenti")} onScegli={tocca("paese")} />
            <Barre titolo="Dopo quante visite si iscrivono" descrizione="Solo per chi aveva accettato i cookie prima di iscriversi."
              unita="iscritti" barre={barreDa(visitePrima.dati, "visite_prima_fascia", "utenti")}
              colonneTabella={[{ titolo: "quota", valori: (visitePrima.dati?.righe ?? []).map((r) => formatta(Number(r.utenti) / Math.max(1, Number(visitePrima.dati?.totali.utenti ?? 1)), "percento")) }]} />
            <Barre titolo="Lingua dell'account" unita="iscritti" barre={barreDa(lingua.dati, "lingua_account", "utenti")} />
          </div>

          <section className={comuni.riquadro} aria-labelledby="titolo-eta-genere">
            <h2 id="titolo-eta-genere" className={comuni.riquadroTitolo}>Età × genere</h2>
            {generi.length === 0 ? (
              <p className={comuni.vuoto}>Nessun iscritto nel periodo.</p>
            ) : (
              <div className={comuni.contenitoreTabella}>
                <table className={comuni.tabella}>
                  <thead>
                    <tr><th>Fascia</th>{generi.map((g) => <th key={g} className={comuni.numero}>{g}</th>)}</tr>
                  </thead>
                  <tbody>
                    {FASCE.map((f) => (
                      <tr key={f}><td>{f}</td>{generi.map((g) => <td key={g} className={comuni.numero}>{formatta(Number(cella(f, g)))}</td>)}</tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className={comuni.riquadro} aria-labelledby="titolo-campagne">
            <h2 id="titolo-campagne" className={comuni.riquadroTitolo}>Quanto vale ogni campagna</h2>
            <p className={comuni.riquadroNota}>
              Ricavi del periodo per campagna d&apos;origine del cliente, e la media per iscritto del periodo (i ricavi
              possono venire da iscritti di periodi precedenti).
            </p>
            {campagneValore.length === 0 ? (
              <p className={comuni.vuoto}>Nessun acquisto nel periodo.</p>
            ) : (
              <div className={comuni.contenitoreTabella}>
                <table className={comuni.tabella}>
                  <thead>
                    <tr><th>Campagna</th><th className={comuni.numero}>Ricavi</th><th className={comuni.numero}>Clienti</th>
                      <th className={comuni.numero}>Iscritti</th><th className={comuni.numero}>Per iscritto</th></tr>
                  </thead>
                  <tbody>
                    {campagneValore.map((c) => (
                      <tr key={c.nome}>
                        <td>{c.nome}</td>
                        <td className={comuni.numero}>{formatta(c.ricavi, "euro")}</td>
                        <td className={comuni.numero}>{formatta(c.clienti)}</td>
                        <td className={comuni.numero}>{formatta(c.iscritti)}</td>
                        <td className={comuni.numero}>{formatta(c.perIscritto, "euro")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      )}
      <BottoniEsporta collezione="utenti" giorni={giorni} />
      <PannelloAI sezione="utenti" titolo="Utenti" giorni={giorni} />
    </>
  );
}
