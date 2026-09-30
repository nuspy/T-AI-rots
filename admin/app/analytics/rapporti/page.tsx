"use client";

/* Rapporti (v8): l'email della domenica notte (lunedì 0:30) con la settimana appena conclusa.
 * Destinatari, interpretazione AI sì/no, anteprima, invio subito e registro degli invii. */

import { useCallback, useState } from "react";
import {
  aggiungiDestinatario, anteprimaRapporto, controllaAvvisi, inviaRapporto, opzioniRapporto, statoRapporto, togliDestinatario,
} from "@/lib/analytics";
import { quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";

export default function Rapporti() {
  const stato = useDati(statoRapporto);
  const { esegui, inCorso, errore } = useAzione();
  const [email, setEmail] = useState("");
  const [anteprima, setAnteprima] = useState<string | null>(null);
  const [esito, setEsito] = useState<string | null>(null);
  const s = stato.dati;

  const agisci = useCallback(async <T,>(f: (t: string) => Promise<T>) => {
    const r = await esegui(f);
    stato.ricarica();
    return r;
  }, [esegui, stato]);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Rapporto settimanale</h1>
          <p className={comuni.sottotitolo}>
            Ogni lunedì alle 0:30 parte un&apos;email con la settimana appena conclusa: numeri principali, canali, campagne,
            pagine, l&apos;imbuto della lettura e un Excel allegato. Gruppi di meno di 5 persone sono omessi.
          </p>
        </div>
        <button className={comuni.primaria} disabled={inCorso || !s?.destinatari.length}
          onClick={async () => {
            const r = await agisci((t) => inviaRapporto(t));
            if (r) setEsito(r.riuscito ? `Inviato: ${r.dettaglio}.` : `Non inviato: ${r.dettaglio}.`);
          }}>
          {inCorso ? "Invio in corso…" : "Invia ora"}
        </button>
      </div>

      {(stato.errore || errore) && <p className={comuni.errore} role="alert">{errore ?? stato.errore}</p>}
      {esito && <p className={comuni.avviso} role="status">{esito}</p>}
      {!s && stato.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {s && (
        <>
          {!s.smtp_configurato && (
            <p className={comuni.avviso}>
              <strong>Posta non configurata</strong>: servono TAROT_SMTP_HOST e TAROT_SMTP_MITTENTE nel deployment dell&apos;API.
            </p>
          )}

          <section className={comuni.riquadro} aria-labelledby="titolo-destinatari">
            <h2 id="titolo-destinatari" className={comuni.riquadroTitolo}>Destinatari</h2>
            {s.destinatari.length === 0 && <p className={comuni.vuoto}>Nessun destinatario: il rapporto non parte.</p>}
            <ul style={{ listStyle: "none", padding: 0, margin: "0 0 0.75rem", display: "grid", gap: "0.5rem" }}>
              {s.destinatari.map((d) => (
                <li key={d.id} className={comuni.riga}>
                  <span className={comuni.mono} style={{ overflowWrap: "anywhere" }}>{d.email}</span>
                  <button className={comuni.secondaria} disabled={inCorso} onClick={() => agisci((t) => togliDestinatario(t, d.id))}
                    aria-label={`Togli ${d.email}`}>
                    Togli
                  </button>
                </li>
              ))}
            </ul>
            <form className={comuni.riga} onSubmit={async (e) => {
              e.preventDefault();
              if (await agisci((t) => aggiungiDestinatario(t, email))) setEmail("");
            }}>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Nuovo indirizzo</span>
                <input className={comuni.ingresso} type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email" inputMode="email" />
              </label>
              <button className={comuni.secondaria} type="submit" disabled={inCorso || !email}>Aggiungi</button>
            </form>
          </section>

          <section className={comuni.riquadro} aria-labelledby="titolo-opzioni">
            <h2 id="titolo-opzioni" className={comuni.riquadroTitolo}>Opzioni</h2>
            <label className={comuni.riga} style={{ alignItems: "center", minHeight: 48 }}>
              <input type="checkbox" checked={s.opzioni.ai} disabled={inCorso} style={{ width: 24, height: 24 }}
                onChange={(e) => agisci((t) => opzioniRapporto(t, { ...s.opzioni, ai: e.target.checked }))} />
              <span>Nel rapporto, la lettura dei dati del modello (una chiamata a settimana; solo le voci verificate)</span>
            </label>
            <label className={comuni.riga} style={{ alignItems: "center", minHeight: 48 }}>
              <input type="checkbox" checked={s.opzioni.avvisi} disabled={inCorso} style={{ width: 24, height: 24 }}
                onChange={(e) => agisci((t) => opzioniRapporto(t, { ...s.opzioni, avvisi: e.target.checked }))} />
              <span>
                Avvisi automatici: ogni notte, se ieri visite, iscrizioni, letture, acquisti o errori del modello escono dal
                normale dei 28 giorni prima, un&apos;email agli stessi destinatari
              </span>
            </label>
            <button className={comuni.secondaria} disabled={inCorso} onClick={async () => {
              const r = await esegui((t) => controllaAvvisi(t));
              if (r) setEsito(r.avvisi.length ? `Ieri (${r.giorno}): ${r.avvisi.map((a) => a.testo).join(" ")}` : `Ieri (${r.giorno}) tutto nel normale.`);
            }}>
              Controlla ieri adesso (senza inviare)
            </button>
          </section>

          <section className={comuni.riquadro} aria-labelledby="titolo-anteprima">
            <h2 id="titolo-anteprima" className={comuni.riquadroTitolo}>
              Anteprima · settimana dal {s.prossima_settimana.da} al {s.prossima_settimana.a}
            </h2>
            <button className={comuni.secondaria} disabled={inCorso} onClick={async () => {
              const html = await esegui((t) => anteprimaRapporto(t));
              if (html) setAnteprima(html);
            }}>
              {anteprima ? "Aggiorna l'anteprima" : "Mostra l'anteprima"}
            </button>
            {anteprima && (
              /* Isolata: l'HTML del rapporto non esegue script e non tocca la console. */
              <iframe title="Anteprima del rapporto" srcDoc={anteprima} sandbox=""
                style={{ width: "100%", minHeight: 480, border: "1px solid var(--filo)", marginTop: "0.75rem", background: "#fff" }} />
            )}
          </section>

          <h2 className={comuni.riquadroTitolo} style={{ marginTop: "1.5rem" }}>Invii</h2>
          {s.invii.length === 0 ? (
            <div className={comuni.vuoto}>Nessun invio ancora.</div>
          ) : (
            <div className={comuni.contenitoreTabella}>
              <table className={comuni.tabella}>
                <thead><tr><th>Quando</th><th>Settimana</th><th>Esito</th><th>Dettaglio</th></tr></thead>
                <tbody>
                  {s.invii.map((i) => (
                    <tr key={i.id}>
                      <td>{quandoCompleto(i.creato_il)}{i.manuale ? " · a mano" : ""}{i.tipo === "avviso" ? " · avviso" : ""}</td>
                      <td>{i.da} – {i.a}</td>
                      <td><span className={`${comuni.stato} ${i.riuscito ? comuni.positivo : comuni.negativo}`}>{i.riuscito ? "inviato" : "non inviato"}</span></td>
                      <td style={{ overflowWrap: "anywhere" }}>{i.dettaglio}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </>
  );
}
