"use client";

/* App mobili → Prodotti: ogni prodotto creato in Play Console o in App Store Connect, con il piano del sito che
 * accredita. Un pacchetto di crediti è un prodotto «consumabile», un abbonamento un «abbonamento»; un ID prodotto
 * vale una volta sola per piattaforma. Prezzi e nomi si decidono negli store: qui solo il collegamento. */

import { useState } from "react";
import {
  creaProdotto, eliminaProdotto, modificaProdotto, type Piattaforma, type ProdottoStore,
} from "@/lib/app-mobili";
import comuni from "../../comuni.module.css";
import stili from "../app-mobili.module.css";
import { Campo, Caricamento, Messaggi, useAppMobili } from "../comuni";

const NOMI_PIATTAFORMA: Record<Piattaforma, string> = { android: "Google Play (Android)", ios: "App Store (iOS)" };

/** Fase 4: l'intervallo di un abbonamento venduto nello store. «Prova» è l'annuale a metà prezzo con il periodo gratuito
 *  dello store (Google: offerta di prova sul base plan; Apple: introductory offer). */
type Intervallo = "mensile" | "annuale" | "prova";
const NOMI_INTERVALLO: Record<Intervallo, string> = {
  mensile: "Mensile",
  annuale: "Annuale",
  prova: "Annuale «prova» (metà prezzo, con la prova gratuita)",
};
/** Nell'elenco: corto, perché l'etichetta non va a capo. */
const BREVI_INTERVALLO: Record<Intervallo, string> = { mensile: "mensile", annuale: "annuale", prova: "annuale prova" };
const intervallo = (p:Pick<ProdottoStore, "annuale" | "prova">): Intervallo => (p.prova ? "prova" : p.annuale ? "annuale" : "mensile");

export default function Prodotti() {
  const { dati, erroreCaricamento, azione, inCorso, errore, esito } = useAppMobili();
  const [nuovo, setNuovo] = useState<{
    piattaforma: Piattaforma; product_id: string; plan_id: string; intervallo: Intervallo; note: string;
  }>({ piattaforma: "android", product_id: "", plan_id: "", intervallo: "mensile", note: "" });

  if (!dati) return <Caricamento errore={erroreCaricamento} />;

  const piani = dati.piani.filter((p) => p.attivo && !p.gratuito);
  const abbonamento = piani.find((p) => String(p.id) === nuovo.plan_id)?.tipo === "abbonamento";
  const aggiungi = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuovo.product_id.trim() || !nuovo.plan_id) return;
    const r = await azione((t) => creaProdotto(t, {
      piattaforma: nuovo.piattaforma, product_id: nuovo.product_id.trim(), plan_id: Number(nuovo.plan_id), note: nuovo.note,
      annuale: abbonamento && nuovo.intervallo !== "mensile", prova: abbonamento && nuovo.intervallo === "prova",
    }), `Prodotto ${nuovo.product_id.trim()} aggiunto.`);
    if (r) setNuovo({ ...nuovo, product_id: "", note: "" });
  };

  return (
    <>
      <Messaggi errore={errore} esito={esito} />

      <p className={comuni.avviso}>
        Crea prima il prodotto nello store (stesso ID su Google e Apple, se vuoi), con prezzo e nome; poi collegalo
        qui al piano del sito. Su Google l&apos;ID ha solo minuscole, cifre, «_» e «.». Un prodotto venduto non si
        cancella: si spegne, così gli acquisti vecchi restano leggibili.
      </p>
      <p className={comuni.riquadroNota}>
        Un abbonamento di Google Play ha uno o più <strong>base plan</strong> (le varianti di durata e prezzo dello stesso
        abbonamento): scrivi l&apos;ID dell&apos;abbonamento, due punti e l&apos;ID del base plan, per esempio
        «abbonamento:annuale». Su Apple ogni durata è un prodotto a sé. Per ogni abbonamento scegli se è il mensile,
        l&apos;annuale o l&apos;annuale «prova».
      </p>

      {(["android", "ios"] as Piattaforma[]).map((piattaforma) => {
        const elenco = dati.prodotti.filter((p) => p.piattaforma === piattaforma);
        return (
          <section key={piattaforma} className={comuni.riquadro} aria-labelledby={`titolo-${piattaforma}`}>
            <h2 id={`titolo-${piattaforma}`} className={comuni.riquadroTitolo}>{NOMI_PIATTAFORMA[piattaforma]}</h2>
            {elenco.length === 0 ? (
              <p className={comuni.riquadroNota}>Nessun prodotto collegato.</p>
            ) : (
              <ul className={stili.elenco}>
                {elenco.map((p) => <Prodotto key={p.id} p={p} inCorso={inCorso} azione={azione} />)}
              </ul>
            )}
          </section>
        );
      })}

      <form className={comuni.riquadro} onSubmit={aggiungi} aria-labelledby="titolo-nuovo">
        <h2 id="titolo-nuovo" className={comuni.riquadroTitolo}>Collega un prodotto</h2>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Store</span>
            <select className={comuni.selezione} value={nuovo.piattaforma}
              onChange={(e) => setNuovo({ ...nuovo, piattaforma: e.target.value as Piattaforma })}>
              {(Object.keys(NOMI_PIATTAFORMA) as Piattaforma[]).map((k) => <option key={k} value={k}>{NOMI_PIATTAFORMA[k]}</option>)}
            </select>
          </label>
          <Campo etichetta="ID del prodotto nello store" valore={nuovo.product_id} mono segnaposto="crediti_15"
            cambia={(v) => setNuovo({ ...nuovo, product_id: v })} />
        </div>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Piano del sito</span>
          <select className={comuni.selezione} value={nuovo.plan_id} onChange={(e) => setNuovo({ ...nuovo, plan_id: e.target.value })}>
            <option value="">Scegli…</option>
            {piani.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nome} ({p.tipo === "pacchetto" ? "pacchetto → consumabile" : "abbonamento"})
              </option>
            ))}
          </select>
          <span className={comuni.campoAiuto}>Il tipo del prodotto segue il piano: pacchetto → consumabile, abbonamento → abbonamento.</span>
        </label>
        {abbonamento && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Durata nello store</span>
            <select className={comuni.selezione} value={nuovo.intervallo}
              onChange={(e) => setNuovo({ ...nuovo, intervallo: e.target.value as Intervallo })}>
              {(Object.keys(NOMI_INTERVALLO) as Intervallo[]).map((k) => <option key={k} value={k}>{NOMI_INTERVALLO[k]}</option>)}
            </select>
            <span className={comuni.campoAiuto}>
              Deve corrispondere al prodotto creato nello store: l&apos;app accredita quel periodo del piano.
            </span>
          </label>
        )}
        <Campo etichetta="Note" valore={nuovo.note} cambia={(v) => setNuovo({ ...nuovo, note: v })} />
        <div className={stili.azioni}>
          <button type="submit" className={comuni.primaria} disabled={inCorso || !nuovo.product_id.trim() || !nuovo.plan_id}>
            Collega il prodotto
          </button>
        </div>
      </form>
    </>
  );
}

function Prodotto({ p, inCorso, azione }: {
  p: ProdottoStore;
  inCorso: boolean;
  azione: ReturnType<typeof useAppMobili>["azione"];
}) {
  return (
    <li className={`${stili.voce} ${p.attivo ? "" : stili.spenta}`}>
      <span className={stili.voceTitolo}>{p.product_id}</span>
      <span className={stili.voceRiga}>
        <span>{p.piano ? p.piano.nome : `piano ${p.plan_id}`}</span>
        <span className={comuni.etichetta}>{p.tipo === "abbonamento" ? BREVI_INTERVALLO[intervallo(p)] : p.tipo}</span>
        <span className={`${comuni.stato} ${p.attivo ? comuni.positivo : comuni.neutro}`}>
          {p.attivo ? "✓ in vendita" : "– spento"}
        </span>
        {p.piano && !p.piano.attivo && <span className={`${comuni.stato} ${comuni.negativo}`}>piano ritirato</span>}
      </span>
      {p.note && <span className={comuni.campoAiuto}>{p.note}</span>}
      <span className={stili.voceAzioni}>
        <button type="button" className={comuni.secondaria} disabled={inCorso}
          onClick={() => void azione((t) => modificaProdotto(t, p.id, { attivo: !p.attivo }),
            p.attivo ? `${p.product_id} spento.` : `${p.product_id} in vendita.`)}>
          {p.attivo ? "Spegni" : "Rimetti in vendita"}
        </button>
        <button type="button" className={comuni.distruttiva} disabled={inCorso}
          onClick={() => {
            if (window.confirm(`Eliminare il collegamento di ${p.product_id}? Se è già stato venduto, meglio spegnerlo.`)) {
              void azione((t) => eliminaProdotto(t, p.id), `${p.product_id} eliminato.`);
            }
          }}>
          Elimina
        </button>
      </span>
    </li>
  );
}
