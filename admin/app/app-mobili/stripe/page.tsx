"use client";

/* App mobili → Pulsante Stripe: se e come l'app mostra il pulsante per pagare con Stripe, per piattaforma e paese.
 * Le regole degli store cambiano per paese e nel tempo: per questo è una tabella e non un'impostazione sola.
 * Senza regole vale «nascosto» ovunque; «*» vale per i paesi senza una regola propria. */

import { useState } from "react";
import {
  NOMI_MODALITA, SPIEGA_MODALITA, eliminaPolitica, impostaPolitica,
  type ModalitaStripe, type Piattaforma, type PoliticaStripe,
} from "@/lib/app-mobili";
import comuni from "../../comuni.module.css";
import stili from "../app-mobili.module.css";
import { Campo, Caricamento, Messaggi, Scelta, useAppMobili } from "../comuni";

const NOMI_PIATTAFORMA: Record<Piattaforma, string> = { android: "Android", ios: "iOS" };

/** La stessa risoluzione del backend: il paese, poi «*», poi nascosto. */
function risolvi(regole: PoliticaStripe[], piattaforma: Piattaforma, paese: string): { modalita: ModalitaStripe; da: string } {
  const p = regole.filter((r) => r.piattaforma === piattaforma);
  const regola = p.find((r) => r.paese === paese.toUpperCase()) ?? p.find((r) => r.paese === "*");
  return regola ? { modalita: regola.modalita, da: regola.paese === "*" ? "regola «*»" : `regola ${regola.paese}` }
    : { modalita: "nascosto", da: "nessuna regola" };
}

export default function PulsanteStripe() {
  const { dati, erroreCaricamento, azione, inCorso, errore, esito } = useAppMobili();
  const [nuova, setNuova] = useState<{ piattaforma: Piattaforma; paese: string; modalita: ModalitaStripe; avviso: string }>({
    piattaforma: "ios", paese: "", modalita: "nascosto", avviso: "",
  });
  const [prova, setProva] = useState<{ piattaforma: Piattaforma; paese: string }>({ piattaforma: "ios", paese: "IT" });

  if (!dati) return <Caricamento errore={erroreCaricamento} />;

  const paeseValido = nuova.paese === "*" || /^[A-Z]{2}$/.test(nuova.paese);
  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!paeseValido) return;
    const r = await azione((t) => impostaPolitica(t, nuova), `Regola ${NOMI_PIATTAFORMA[nuova.piattaforma]} ${nuova.paese} salvata.`);
    if (r) setNuova({ ...nuova, paese: "", avviso: "" });
  };
  const risultato = risolvi(dati.politica_stripe, prova.piattaforma, prova.paese);

  return (
    <>
      <Messaggi errore={errore} esito={esito} />

      <section className={comuni.riquadro} aria-labelledby="titolo-modi">
        <h2 id="titolo-modi" className={comuni.riquadroTitolo}>Le modalità</h2>
        <ul className={stili.passi}>
          {dati.catalogo.modalita_stripe.map((m) => (
            <li key={m}><strong>{NOMI_MODALITA[m]}</strong>: {SPIEGA_MODALITA[m]}</li>
          ))}
        </ul>
        <p className={comuni.riquadroNota} style={{ margin: 0 }}>
          Prima di accendere un pulsante, controlla le regole in vigore dello store per quel paese: chi sbaglia rischia
          il rifiuto dell&apos;app o la sospensione. Il paese è quello dello store dell&apos;utente.
        </p>
      </section>

      {(["android", "ios"] as Piattaforma[]).map((piattaforma) => {
        const regole = dati.politica_stripe.filter((r) => r.piattaforma === piattaforma);
        return (
          <section key={piattaforma} className={comuni.riquadro} aria-labelledby={`titolo-${piattaforma}`}>
            <h2 id={`titolo-${piattaforma}`} className={comuni.riquadroTitolo}>{NOMI_PIATTAFORMA[piattaforma]}</h2>
            {!regole.some((r) => r.paese === "*") && (
              <p className={comuni.riquadroNota}>Tutti i paesi senza una regola: <strong>nascosto</strong> (predefinito).</p>
            )}
            {regole.length > 0 && (
              <ul className={stili.elenco}>
                {regole.map((r) => (
                  <li key={r.id} className={stili.voce}>
                    <span className={stili.voceTitolo}>{r.paese === "*" ? "* (tutti gli altri paesi)" : r.paese}</span>
                    <span className={stili.voceRiga}>
                      <span className={`${comuni.stato} ${r.modalita === "nascosto" ? comuni.neutro : comuni.positivo}`}>
                        {r.modalita === "nascosto" ? "– " : "● "}{NOMI_MODALITA[r.modalita]}
                      </span>
                      {r.avviso && <span>«{r.avviso}»</span>}
                    </span>
                    <span className={stili.voceAzioni}>
                      <button type="button" className={comuni.secondaria} disabled={inCorso}
                        onClick={() => setNuova({ piattaforma: r.piattaforma, paese: r.paese, modalita: r.modalita, avviso: r.avviso })}>
                        Modifica
                      </button>
                      <button type="button" className={comuni.distruttiva} disabled={inCorso}
                        onClick={() => void azione((t) => eliminaPolitica(t, r.id), `Regola ${r.paese} tolta: torna a valere «*» o nascosto.`)}>
                        Togli
                      </button>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </section>
        );
      })}

      <form className={comuni.riquadro} onSubmit={salva} aria-labelledby="titolo-regola">
        <h2 id="titolo-regola" className={comuni.riquadroTitolo}>Aggiungi o cambia una regola</h2>
        <div className={comuni.riga}>
          <Scelta<Piattaforma> etichetta="Piattaforma" valore={nuova.piattaforma} nomi={NOMI_PIATTAFORMA}
            cambia={(v) => setNuova({ ...nuova, piattaforma: v })} />
          <Campo etichetta="Paese" valore={nuova.paese} massimo={2} segnaposto="US, IT o *" mono
            cambia={(v) => setNuova({ ...nuova, paese: v.toUpperCase() })}
            aiuto="Codice ISO di due lettere, o «*» per tutti i paesi senza una regola propria." />
          <Scelta<ModalitaStripe> etichetta="Modalità" valore={nuova.modalita} nomi={NOMI_MODALITA}
            cambia={(v) => setNuova({ ...nuova, modalita: v })} />
        </div>
        <Campo etichetta="Avviso accanto al pulsante" valore={nuova.avviso} massimo={500}
          cambia={(v) => setNuova({ ...nuova, avviso: v })}
          aiuto="Il testo che le regole dello store chiedono (per esempio che l'acquisto avviene fuori dall'app)." />
        <div className={stili.azioni}>
          <button type="submit" className={comuni.primaria} disabled={inCorso || !paeseValido}>Salva la regola</button>
        </div>
      </form>

      <section className={comuni.riquadro} aria-labelledby="titolo-prova">
        <h2 id="titolo-prova" className={comuni.riquadroTitolo}>Cosa vede un utente</h2>
        <div className={comuni.riga}>
          <Scelta<Piattaforma> etichetta="Piattaforma" valore={prova.piattaforma} nomi={NOMI_PIATTAFORMA}
            cambia={(v) => setProva({ ...prova, piattaforma: v })} />
          <Campo etichetta="Paese dello store" valore={prova.paese} massimo={2} mono
            cambia={(v) => setProva({ ...prova, paese: v.toUpperCase() })} />
        </div>
        <p role="status" style={{ margin: 0 }}>
          <strong>{NOMI_MODALITA[risultato.modalita]}</strong>{" "}
          <span className={comuni.mono}>({risultato.da})</span>
        </p>
      </section>
    </>
  );
}
