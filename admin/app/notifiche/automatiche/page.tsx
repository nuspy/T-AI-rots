"use client";

/* Notifications → Automatiche: i messaggi che il sito manda da solo (carta del giorno, serie, benvenuto, prova,
 * rinnovo non riuscito, crediti in scadenza). Ognuna si accende e si spegne, ha la sua ora (dove serve) e i suoi testi
 * nelle sei lingue: una lingua lasciata vuota torna al testo predefinito. */

import { useEffect, useState } from "react";
import { salvaAutomatica, statoNotifiche, traduci, LINGUE, type Automatica, type Lingua, type StatoNotifiche, type Testi } from "@/lib/notifiche";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { Anteprima, Casella, TestiPerLingua } from "../comuni";
import stili from "../notifiche.module.css";

function Voce({ a, salva, inCorso }: {
  a: Automatica;
  salva: (corpo: { attiva?: boolean; ora?: string; testi?: Testi }, messaggio: string) => Promise<unknown>;
  inCorso: boolean;
}) {
  const { esegui } = useAzione();
  const [lingua, setLingua] = useState<Lingua>("it");
  const [testi, setTesti] = useState<Testi | null>(null);
  const [ora, setOra] = useState<string | null>(null);
  const t = testi ?? a.testi;
  const modificata = testi !== null || (ora !== null && ora !== a.ora);

  return (
    <section className={comuni.riquadro} aria-labelledby={`auto-${a.tipo}`}>
      <h2 id={`auto-${a.tipo}`} className={comuni.riquadroTitolo}>
        {a.nome}
        <span className={`${comuni.stato} ${a.attiva ? comuni.positivo : comuni.neutro}`}>{a.attiva ? "● accesa" : "○ spenta"}</span>
      </h2>
      <p className={comuni.riquadroNota}>{a.spiegazione} Porta a <span className={comuni.mono}>{a.link}</span>.</p>
      <Casella etichetta="Accesa" valore={a.attiva} cambia={(v) => void salva({ attiva: v }, v ? `«${a.nome}» accesa.` : `«${a.nome}» spenta.`)} />
      {a.ha_ora && (
        <label className={comuni.campo} style={{ maxWidth: "14rem" }}>
          <span className={comuni.campoEtichetta}>Ora locale di chi riceve</span>
          <input className={comuni.ingresso} type="time" value={ora ?? a.ora ?? ""} onChange={(e) => setOra(e.target.value)} />
          <span className={comuni.campoAiuto}>Parte da quest&apos;ora, entro tre ore, fuori dalle ore di silenzio.</span>
        </label>
      )}
      <details>
        <summary style={{ minHeight: 44, display: "flex", alignItems: "center", cursor: "pointer" }}>
          Testi ({a.personalizzati.length ? `personalizzati: ${a.personalizzati.map((l) => l.toUpperCase()).join(", ")}` : "predefiniti"})
        </summary>
        <div className={stili.griglia} style={{ marginTop: "0.75rem" }}>
          <div>
            <TestiPerLingua testi={t} lingua={lingua} scegli={setLingua} base="it" cambia={(l, x) => setTesti({ ...t, [l]: x })} />
            <div className={stili.azioni}>
              <button type="button" className={comuni.secondaria} disabled={inCorso || !t.it?.titolo}
                onClick={async () => {
                  const r = await esegui((tok) => traduci(tok, "it", t.it!, LINGUE.filter((l) => l !== "it")));
                  if (r) setTesti({ ...t, ...r.testi });
                }}>
                Traduci dall&apos;italiano
              </button>
            </div>
          </div>
          <Anteprima testo={t[lingua]} lingua={lingua} />
        </div>
      </details>
      {modificata && (
        <div className={stili.azioni}>
          <button type="button" className={comuni.primaria} disabled={inCorso}
            onClick={async () => {
              const r = await salva({ ...(ora ? { ora } : {}), ...(testi ? { testi } : {}) }, `«${a.nome}» salvata.`);
              if (r) { setTesti(null); setOra(null); }
            }}>
            Salva
          </button>
          <button type="button" className={comuni.secondaria} disabled={inCorso} onClick={() => { setTesti(null); setOra(null); }}>
            Annulla le modifiche
          </button>
        </div>
      )}
    </section>
  );
}

export default function Automatiche() {
  const caricato = useDati(statoNotifiche);
  const { esegui, inCorso, errore } = useAzione();
  const [ultimo, setUltimo] = useState<StatoNotifiche | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  const dati = ultimo ?? caricato.dati;

  useEffect(() => {
    if (!esito) return;
    const t = window.setTimeout(() => setEsito(null), 4000);
    return () => window.clearTimeout(t);
  }, [esito]);

  if (caricato.errore) return <p className={comuni.errore} role="alert">{caricato.errore}</p>;
  if (!dati) return <p className={comuni.caricamento}>Caricamento…</p>;

  return (
    <>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      <p className={comuni.esito} role="status" hidden={!esito}>{esito}</p>
      <p className={comuni.riquadroNota}>
        Partono da sole, all&apos;ora locale di ciascuno, una volta al giorno al massimo per tipo. La persona le regola dal
        suo profilo («Carta del giorno» e «Promemoria»); i segnaposto fra graffe ({"{n}"}, {"{data}"}…) si riempiono da soli.
      </p>
      {dati.automatiche.map((a) => (
        <Voce key={a.tipo} a={a} inCorso={inCorso} salva={async (corpo, messaggio) => {
          const r = await esegui((t) => salvaAutomatica(t, a.tipo, corpo));
          if (r) { setUltimo(r); setEsito(messaggio); }
          return r;
        }} />
      ))}
    </>
  );
}
