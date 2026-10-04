"use client";

/* Advertisements → Google Ads: i parametri di AdSense (ID editore, un'unità pubblicitaria per ciascuno dei tre spazi
 * col suo formato, larghezza piena sul telefono, modalità di prova, annunci personalizzati), i dati dell'iscrizione
 * (restano qui: il sito non li riceve), `ads.txt` e la guida in passi, dall'iscrizione all'accensione. */

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  NOMI_FORMATO, NOMI_POSIZIONE, NOMI_STATO, POSIZIONI, salvaGoogle, statoPubblicita,
  type Formato, type ParametriGoogle, type RegistrazioneGoogle, type StatoPubblicita, type StatoRegistrazione,
} from "@/lib/pubblicita";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import integrazioni from "../../integrazioni.module.css";
import stili from "../pubblicita.module.css";

const FORMATI = Object.keys(NOMI_FORMATO) as Formato[];
const STATI = Object.keys(NOMI_STATO) as StatoRegistrazione[];

export default function GoogleAds() {
  const stato = useDati(statoPubblicita);
  const { esegui, inCorso, errore } = useAzione();
  const [ultimo, setUltimo] = useState<StatoPubblicita | null>(null);
  const [parametri, setParametri] = useState<ParametriGoogle | null>(null);
  const [registrazione, setRegistrazione] = useState<RegistrazioneGoogle | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  const dati = ultimo ?? stato.dati;

  useEffect(() => {
    if (!esito) return;
    const t = window.setTimeout(() => setEsito(null), 4000);
    return () => window.clearTimeout(t);
  }, [esito]);

  if (!dati) {
    return stato.errore ? <p className={comuni.errore} role="alert">{stato.errore}</p> : <p className={comuni.caricamento}>Caricamento…</p>;
  }

  const google = dati.fornitori.google;
  const p = parametri ?? google.parametri;
  const r = registrazione ?? google.registrazione;
  const cambia = (parziale: Partial<ParametriGoogle>) => setParametri({ ...p, ...parziale });
  const cambiaReg = (parziale: Partial<RegistrazioneGoogle>) => setRegistrazione({ ...r, ...parziale });

  const salva = async (corpo: Parameters<typeof salvaGoogle>[1], messaggio: string, dopo: () => void) => {
    const nuovo = await esegui((t) => salvaGoogle(t, corpo));
    if (nuovo) {
      setUltimo(nuovo);
      dopo();
      setEsito(messaggio);
    }
  };

  return (
    <>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {esito && <p className={comuni.esito} role="status">{esito}</p>}

      <p className={comuni.avviso}>
        <strong>Spazi {dati.pubblico.attiva ? "accesi" : "spenti"}.</strong>{" "}
        L&apos;interruttore e i tre banner stanno in <Link href="/pubblicita" className={comuni.collegamento}>Spazi</Link>;
        qui si dice ad AdSense che cosa mostrare.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void salva({ parametri: p }, "Parametri di AdSense salvati.", () => setParametri(null));
        }}
      >
        <section className={comuni.riquadro} aria-labelledby="titolo-account">
          <h2 id="titolo-account" className={comuni.riquadroTitolo}>
            Account AdSense
            <span className={`${comuni.stato} ${google.pronto ? comuni.positivo : comuni.neutro}`}>
              {google.pronto ? "ID editore valido" : "manca l'ID editore"}
            </span>
          </h2>
          <label className={comuni.campo} style={{ maxWidth: "28rem" }}>
            <span className={comuni.campoEtichetta}>ID editore</span>
            <input
              className={comuni.ingresso}
              value={p.editore}
              onChange={(e) => cambia({ editore: e.target.value })}
              placeholder="ca-pub-0000000000000000"
              autoComplete="off"
              spellCheck={false}
              inputMode="text"
            />
            <span className={comuni.campoAiuto}>AdSense → Account → Impostazioni → Informazioni account. Anche «pub-…» va bene.</span>
          </label>
        </section>

        <section className={comuni.riquadro} aria-labelledby="titolo-unita">
          <h2 id="titolo-unita" className={comuni.riquadroTitolo}>Unità pubblicitarie</h2>
          <p className={comuni.riquadroNota}>
            Un&apos;unità «Annunci display» per spazio (AdSense → Annunci → Per unità pubblicitaria): l&apos;ID slot è il
            numero in <code>data-ad-slot</code>. Lo spazio riserva l&apos;altezza del formato, così la pagina non salta.
          </p>
          <div className={stili.griglia}>
            {POSIZIONI.map((posizione) => (
              <fieldset key={posizione} className={stili.posizione}>
                <legend className={stili.posizioneTitolo}>{NOMI_POSIZIONE[posizione]}</legend>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>ID slot</span>
                  <input
                    className={comuni.ingresso}
                    value={p.slot[posizione]}
                    onChange={(e) => cambia({ slot: { ...p.slot, [posizione]: e.target.value } })}
                    placeholder="1234567890"
                    inputMode="numeric"
                    autoComplete="off"
                  />
                </label>
                <label className={comuni.campo}>
                  <span className={comuni.campoEtichetta}>Formato</span>
                  <select
                    className={comuni.selezione}
                    value={p.formato[posizione]}
                    onChange={(e) => cambia({ formato: { ...p.formato, [posizione]: e.target.value as Formato } })}
                  >
                    {FORMATI.map((f) => <option key={f} value={f}>{NOMI_FORMATO[f]}</option>)}
                  </select>
                </label>
              </fieldset>
            ))}
          </div>
        </section>

        <section className={comuni.riquadro} aria-labelledby="titolo-vista">
          <h2 id="titolo-vista" className={comuni.riquadroTitolo}>Visualizzazione</h2>
          <label className={stili.casella}>
            <input type="checkbox" checked={p.responsive} onChange={(e) => cambia({ responsive: e.target.checked })} />
            <span>
              Larghezza piena sul telefono
              <small><code>data-full-width-responsive</code>: sugli schermi stretti l&apos;annuncio può prendere tutta la larghezza.</small>
            </span>
          </label>
          <label className={stili.casella}>
            <input type="checkbox" checked={p.prova} onChange={(e) => cambia({ prova: e.target.checked })} />
            <span>
              Modalità di prova
              <small><code>data-adtest=&quot;on&quot;</code>: annunci di prova, non conteggiati né pagati. Per le prove in locale; spegnila in produzione.</small>
            </span>
          </label>
          <label className={stili.casella}>
            <input type="checkbox" checked={p.personalizzati} onChange={(e) => cambia({ personalizzati: e.target.checked })} />
            <span>
              Annunci personalizzati
              <small>
                Spento: si chiedono annunci non personalizzati anche a chi ha acconsentito. Acceso richiede la CMP
                certificata (vedi la guida, passo 5) e un aggiornamento della pagina privacy, che oggi dice che gli
                annunci non sono personalizzati.
              </small>
            </span>
          </label>
        </section>

        <div className={stili.azioni} style={{ marginBottom: "1.25rem" }}>
          <button type="submit" className={comuni.primaria} disabled={inCorso || parametri === null}>
            {inCorso ? "Salvataggio…" : "Salva i parametri"}
          </button>
          {parametri !== null && (
            <button type="button" className={comuni.secondaria} disabled={inCorso} onClick={() => setParametri(null)}>
              Annulla le modifiche
            </button>
          )}
        </div>
      </form>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void salva({ registrazione: r }, "Dati di registrazione salvati.", () => setRegistrazione(null));
        }}
      >
        <section className={comuni.riquadro} aria-labelledby="titolo-registrazione">
          <h2 id="titolo-registrazione" className={comuni.riquadroTitolo}>
            Dati di registrazione
            <span className={`${comuni.stato} ${r.stato === "approvato" ? comuni.positivo : r.stato === "rifiutato" ? comuni.negativo : comuni.neutro}`}>
              {NOMI_STATO[r.stato]}
            </span>
          </h2>
          <p className={comuni.riquadroNota}>
            Un promemoria dell&apos;iscrizione ad AdSense. Restano nella console: il sito non li riceve e non cambiano
            come si comportano gli spazi.
          </p>
          <div className={comuni.riga}>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Email dell&apos;account</span>
              <input className={comuni.ingresso} type="email" value={r.email} onChange={(e) => cambiaReg({ email: e.target.value })} autoComplete="off" />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Titolare</span>
              <input className={comuni.ingresso} value={r.titolare} onChange={(e) => cambiaReg({ titolare: e.target.value })} autoComplete="off" />
            </label>
          </div>
          <div className={comuni.riga}>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>ID cliente AdSense (se c&apos;è)</span>
              <input className={comuni.ingresso} value={r.id_cliente} onChange={(e) => cambiaReg({ id_cliente: e.target.value })} autoComplete="off" />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Data d&apos;iscrizione</span>
              <input className={comuni.ingresso} type="date" value={r.data_iscrizione ?? ""} onChange={(e) => cambiaReg({ data_iscrizione: e.target.value || null })} />
            </label>
            <label className={comuni.campo}>
              <span className={comuni.campoEtichetta}>Stato della verifica</span>
              <select className={comuni.selezione} value={r.stato} onChange={(e) => cambiaReg({ stato: e.target.value as StatoRegistrazione })}>
                {STATI.map((s) => <option key={s} value={s}>{NOMI_STATO[s]}</option>)}
              </select>
            </label>
          </div>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Note</span>
            <textarea className={comuni.area} style={{ minHeight: "6rem", fontFamily: "inherit" }} value={r.note} onChange={(e) => cambiaReg({ note: e.target.value })} />
          </label>
          <div className={stili.azioni}>
            <button type="submit" className={comuni.primaria} disabled={inCorso || registrazione === null}>
              Salva i dati di registrazione
            </button>
          </div>
        </section>
      </form>

      <section className={comuni.riquadro} aria-labelledby="titolo-ads-txt">
        <h2 id="titolo-ads-txt" className={comuni.riquadroTitolo}>
          ads.txt
          <span className={`${comuni.stato} ${google.ads_txt ? comuni.positivo : comuni.neutro}`}>
            {google.ads_txt ? "pubblicato" : "vuoto (404)"}
          </span>
        </h2>
        <p className={comuni.riquadroNota}>
          Il sito lo serve da solo alla radice (<code>https://tarots.chat/ads.txt</code>) appena c&apos;è l&apos;ID
          editore, anche a pubblicità spenta: Google lo controlla durante la verifica.
        </p>
        <code className={stili.codice}>{google.ads_txt ?? "— nessun ID editore —"}</code>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-guida">
        <h2 id="titolo-guida" className={comuni.riquadroTitolo}>Guida: da zero agli annunci</h2>
        <ol className={integrazioni.passi}>
          <li className={integrazioni.passo}>
            <h3 className={integrazioni.passoTitolo}>Iscriviti ad AdSense</h3>
            <p className={integrazioni.passoTesto}>
              Su <a className={comuni.collegamento} href="https://adsense.google.com/start/" target="_blank" rel="noopener noreferrer">adsense.google.com</a>{" "}
              con l&apos;account Google dell&apos;attività: aggiungi il sito <code>tarots.chat</code>, i dati di pagamento e
              l&apos;indirizzo. Annota email, titolare e data qui sopra in «Dati di registrazione».
            </p>
          </li>
          <li className={integrazioni.passo}>
            <h3 className={integrazioni.passoTitolo}>Incolla l&apos;ID editore e verifica il sito con ads.txt</h3>
            <p className={integrazioni.passoTesto}>
              Copia l&apos;ID <code>ca-pub-…</code> in «Account AdSense» e salva: <code>/ads.txt</code> si pubblica da
              solo. In AdSense → Siti scegli la verifica con «snippet ads.txt» (non serve incollare codice nelle
              pagine). Quando Google lo trova, metti lo stato su «ads.txt verificato».
            </p>
          </li>
          <li className={integrazioni.passo}>
            <h3 className={integrazioni.passoTitolo}>Chiedi la revisione e aspetta l&apos;approvazione</h3>
            <p className={integrazioni.passoTesto}>
              In AdSense → Siti → «Richiedi revisione». Di solito ci vogliono da qualche giorno a qualche settimana; lo
              stato in «Dati di registrazione» è solo un promemoria (Google scrive l&apos;esito per email e nel pannello).
            </p>
          </li>
          <li className={integrazioni.passo}>
            <h3 className={integrazioni.passoTitolo}>Crea tre unità pubblicitarie</h3>
            <p className={integrazioni.passoTesto}>
              AdSense → Annunci → Per unità pubblicitaria → Annunci display, adattabili: una per «a un terzo», una per «a
              due terzi», una per «alla fine» (così i rapporti le distinguono). Copia ciascun <code>data-ad-slot</code>{" "}
              nel suo campo e scegli il formato.
            </p>
          </li>
          <li className={integrazioni.passo}>
            <h3 className={integrazioni.passoTitolo}>Unione europea, Regno Unito e Svizzera: una CMP certificata TCF</h3>
            <p className={integrazioni.passoTesto}>
              Per chi visita da questi paesi Google chiede che il consenso sia raccolto da una piattaforma di gestione
              del consenso (CMP) certificata Google e integrata con il TCF di IAB: senza, lì gli annunci non escono (o
              escono solo «limitati»). Il banner del sito chiede il consenso agli annunci, ma <strong>non è una CMP
              TCF</strong>. La strada più semplice è il messaggio «Normative europee» di AdSense (Privacy e messaggi),
              gratuito; in alternativa una CMP certificata di terzi. Va integrata nel sito prima di accendere gli
              spazi per il pubblico europeo: non è ancora fatto.
            </p>
          </li>
          <li className={integrazioni.passo}>
            <h3 className={integrazioni.passoTitolo}>Prova, poi accendi</h3>
            <p className={integrazioni.passoTesto}>
              Con «Modalità di prova» attiva accendi gli spazi in <Link href="/pubblicita" className={comuni.collegamento}>Spazi</Link>,
              accetta gli annunci nel banner del sito e controlla le pagine anche dal telefono. Poi spegni la modalità
              di prova: da quel momento gli annunci sono veri. Ogni banner si può spegnere da solo.
            </p>
          </li>
        </ol>
      </section>
    </>
  );
}
