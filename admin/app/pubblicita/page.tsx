"use client";

/* Advertisements → Spazi: l'interruttore generale, quale fornitore riempie gli spazi, i tre banner uno per uno, le
 * pagine escluse, e un'anteprima di dove compaiono. Vale per qualunque fornitore; i parametri di ciascuno stanno nel
 * suo sotto-tab (oggi Google Ads). */

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  NOMI_POSIZIONE, POSIZIONI, salvaGenerale, statoPubblicita, type Generale, type Posizione, type StatoPubblicita,
} from "@/lib/pubblicita";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./pubblicita.module.css";

const SPIEGAZIONE: Record<Posizione, string> = {
  terzo: "Dopo circa un terzo del contenuto.",
  due_terzi: "Dopo circa due terzi del contenuto.",
  fine: "Alla fine del contenuto, prima della parte che chiude la pagina (domande, invito finale, diario, piede).",
};

/* Dove sta ciascuno spazio, pagina per pagina: lo stesso ordine dei modelli del sito (`frontend/v2/pagine`). */
const PAGINE: { nome: string; dove: string }[] = [
  { nome: "Home", dove: "dopo il rito · dopo le carte fisiche · dopo il diario, prima di domande e invito finale" },
  { nome: "Le 78 carte", dove: "dopo il primo terzo della griglia · dopo il secondo · in fondo alla griglia" },
  { nome: "Una carta", dove: "nel testo dopo i significati · dopo rovesciata e ambiti · dopo la scheda, prima del diario" },
  { nome: "Le stese", dove: "dopo le standard · dopo quelle di compatibilità · dopo quelle di coppia" },
  { nome: "Una stesa", dove: "dopo lo schema · dopo le regole · dopo le altre stese, prima del diario" },
  { nome: "Carta del giorno, Esplora", dove: "dopo la carta (o le voci) · dentro il diario · in fondo" },
  { nome: "Blog: elenco, sezione, etichetta", dove: "fra i blocchi della colonna (in evidenza, ultimi, scelti a caso) · prima del ponte verso la lettura" },
  { nome: "Blog: articolo", dove: "nel testo a un terzo · nel testo a due terzi · dopo il testo, prima del ponte" },
  { nome: "Mazzi, un mazzo, Prezzi", dove: "fra i blocchi della pagina · la fine prima della nota di chiusura" },
  { nome: "Lettura condivisa", dove: "dopo il tavolo · prima dell'invito finale (il responso non si interrompe)" },
  { nome: "Lettura con carte fisiche", dove: "solo alla fine (lo strumento non si interrompe)" },
];

const MAI = "La lettura (/read), il profilo, la mia storia, il negozio e il carrello, i pagamenti, la privacy, il voto, l'accesso e la vecchia versione (/old) non hanno spazi.";

export default function Spazi() {
  const stato = useDati(statoPubblicita);
  const { esegui, inCorso, errore } = useAzione();
  const [ultimo, setUltimo] = useState<StatoPubblicita | null>(null);
  const [escluse, setEscluse] = useState<string | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  const dati = ultimo ?? stato.dati;

  useEffect(() => {
    if (!esito) return;
    const t = window.setTimeout(() => setEsito(null), 4000);
    return () => window.clearTimeout(t);
  }, [esito]);

  const salva = async (corpo: Partial<Generale>, messaggio: string) => {
    const r = await esegui((t) => salvaGenerale(t, corpo));
    if (r) {
      setUltimo(r);
      setEsito(messaggio);
    }
  };

  if (!dati) {
    return stato.errore ? <p className={comuni.errore} role="alert">{stato.errore}</p> : <p className={comuni.caricamento}>Caricamento…</p>;
  }

  const g = dati.generale;
  const google = dati.fornitori.google;
  const testoEscluse = escluse ?? g.pagine_escluse.join("\n");
  const visibile = (p: Posizione) => !!dati.pubblico.posizioni?.[p];

  return (
    <>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      {esito && <p className={comuni.esito} role="status">{esito}</p>}

      <section className={comuni.riquadro} aria-labelledby="titolo-interruttore">
        <h2 id="titolo-interruttore" className={comuni.riquadroTitolo}>
          Pubblicità sul sito
          <span className={`${comuni.stato} ${dati.pubblico.attiva ? comuni.positivo : comuni.neutro}`}>
            {dati.pubblico.attiva ? "accesa" : "spenta"}
          </span>
        </h2>
        <p className={comuni.riquadroNota}>
          L&apos;interruttore generale. Spenta, il sito non riserva spazi e non carica nessuno script: le pagine sono
          quelle di sempre. Per accenderla serve l&apos;ID editore nel sotto-tab del fornitore.
        </p>
        {!google.pronto && (
          <p className={comuni.avviso}>
            <strong>Manca l&apos;ID editore di AdSense.</strong> Impostalo in{" "}
            <Link href="/pubblicita/google" className={comuni.collegamento}>Google Ads</Link>, poi torna qui ad accendere.
          </p>
        )}
        <label className={stili.casella}>
          <input
            type="checkbox"
            checked={g.attiva}
            disabled={inCorso || (!g.attiva && !google.pronto)}
            onChange={(e) => salva({ attiva: e.target.checked }, e.target.checked ? "Pubblicità accesa." : "Pubblicità spenta.")}
          />
          <span>
            Mostra gli spazi pubblicitari
            <small>Vale per tutti gli spazi accesi qui sotto, nelle pagine non escluse.</small>
          </span>
        </label>
        {g.attiva && !dati.pubblico.attiva && (
          <p className={comuni.avviso}>
            <strong>Accesa, ma il sito non mostra nulla:</strong> nessuno spazio acceso ha il suo ID slot. Aggiungili in{" "}
            <Link href="/pubblicita/google" className={comuni.collegamento}>Google Ads</Link>.
          </p>
        )}
        <div className={comuni.campo} style={{ marginTop: "0.75rem", maxWidth: "24rem" }}>
          <label className={comuni.campoEtichetta} htmlFor="fornitore">Chi riempie gli spazi</label>
          <select
            id="fornitore"
            className={comuni.selezione}
            value={g.fornitore}
            disabled={inCorso || dati.catalogo.fornitori.length < 2}
            onChange={(e) => salva({ fornitore: e.target.value }, "Fornitore cambiato.")}
          >
            {dati.catalogo.fornitori.map((f) => <option key={f.chiave} value={f.chiave}>{f.etichetta}</option>)}
          </select>
          <span className={comuni.campoAiuto}>Oggi solo Google AdSense; affiliazioni e spazi diretti si aggiungeranno qui.</span>
        </div>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-banner">
        <h2 id="titolo-banner" className={comuni.riquadroTitolo}>I tre banner</h2>
        <p className={comuni.riquadroNota}>
          Uno per uno: spegnerne uno non sposta gli altri. Un banner acceso si vede solo se ha il suo ID slot nel
          sotto-tab del fornitore.
        </p>
        {POSIZIONI.map((p) => {
          const slot = google.parametri.slot[p];
          return (
            <label key={p} className={stili.casella}>
              <input
                type="checkbox"
                checked={g.posizioni[p]}
                disabled={inCorso}
                onChange={(e) => salva(
                  { posizioni: { ...g.posizioni, [p]: e.target.checked } },
                  `${NOMI_POSIZIONE[p]}: ${e.target.checked ? "acceso" : "spento"}.`,
                )}
              />
              <span>
                {NOMI_POSIZIONE[p]}{" "}
                <span className={`${comuni.stato} ${visibile(p) ? comuni.positivo : comuni.neutro}`}>
                  {visibile(p) ? "sul sito" : !g.posizioni[p] ? "spento" : !slot ? "manca lo slot" : "non sul sito"}
                </span>
                <small>{SPIEGAZIONE[p]}</small>
              </span>
            </label>
          );
        })}
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-escluse">
        <h2 id="titolo-escluse" className={comuni.riquadroTitolo}>Pagine escluse</h2>
        <p className={comuni.riquadroNota}>
          Un indirizzo per riga, come si vede nel browser (<code>/pricing</code>, <code>/it/prezzi</code>): esclude anche
          le pagine sotto (<code>/blog</code> toglie gli spazi a tutto il blog). {MAI}
        </p>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Indirizzi senza pubblicità</span>
          <textarea
            className={comuni.area}
            style={{ minHeight: "6rem" }}
            value={testoEscluse}
            onChange={(e) => setEscluse(e.target.value)}
            spellCheck={false}
            placeholder={"/pricing\n/it/prezzi"}
          />
        </label>
        <div className={stili.azioni}>
          <button
            className={comuni.primaria}
            disabled={inCorso || escluse === null}
            onClick={async () => {
              await salva({ pagine_escluse: testoEscluse.split("\n").map((r) => r.trim()).filter(Boolean) }, "Pagine escluse salvate.");
              setEscluse(null);
            }}
          >
            Salva le pagine escluse
          </button>
        </div>
      </section>

      <section className={comuni.riquadro} aria-labelledby="titolo-anteprima">
        <h2 id="titolo-anteprima" className={comuni.riquadroTitolo}>Dove compaiono</h2>
        <p className={comuni.riquadroNota}>
          Lo schema di una pagina, con gli spazi come li vede adesso il sito (pieni: mostrati; tratteggiati: spenti o
          senza slot). Sotto, la posizione pagina per pagina.
        </p>
        <div className={stili.pagina} aria-label="Schema di una pagina">
          <div className={stili.blocco}>Inizio del contenuto</div>
          <Spazio p="terzo" visibile={visibile("terzo")} />
          <div className={stili.blocco}>Contenuto</div>
          <Spazio p="due_terzi" visibile={visibile("due_terzi")} />
          <div className={stili.blocco}>Fine del contenuto</div>
          <Spazio p="fine" visibile={visibile("fine")} />
          <div className={stili.chiusura}>Chiusura: domande, invito finale, diario, piede</div>
        </div>
        <ul className={stili.elencoPagine}>
          {PAGINE.map((x) => <li key={x.nome}><strong>{x.nome}</strong><span>{x.dove}</span></li>)}
        </ul>
        <p className={comuni.campoAiuto} style={{ marginTop: "0.75rem" }}>
          Nelle pagine corte uno spazio può mancare: due annunci non stanno mai uno accanto all&apos;altro.
        </p>
      </section>
    </>
  );
}

function Spazio({ p, visibile }: { p: Posizione; visibile: boolean }) {
  return (
    <div className={visibile ? stili.spazio : stili.spazioSpento}>
      Pubblicità · {NOMI_POSIZIONE[p].toLowerCase()}
    </div>
  );
}
