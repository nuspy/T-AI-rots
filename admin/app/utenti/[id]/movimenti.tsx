"use client";

import { stornaMovimento, type Movimento, type UtenteDettaglio } from "@/lib/api";
import { quandoCompleto } from "@/lib/formato";
import { useAzione } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "./dettaglio.module.css";

/* I movimenti dei crediti di un utente, con l'origine di ciascuno (v9).
 *
 * Canale (sito, app, console, sistema) e fornitore (Stripe, gli store, il
 * simulatore, interno) dicono di quale incasso è figlia una riga; il
 * riferimento è l'incasso presso il fornitore, da cercare nella sua dashboard.
 * Su un acquisto o un rinnovo pagato c'è «Storna»: registra un rimborso o una
 * contestazione che il webhook non ha collegato. Non rimborsa il denaro. */

const MOTIVI: Record<string, string> = {
  accredito_piano: "Rinnovo del piano",
  acquisto: "Acquisto",
  consumo: "Lettura",
  rimborso: "Rimborso lettura",
  rettifica: "Rettifica manuale",
  scadenza: "Scadenza",
  omaggio: "Omaggio",
  storno: "Storno",
  storno_annullato: "Storno annullato",
};

const CANALI: Record<string, string> = {
  web: "sito",
  android: "Android",
  ios: "iOS",
  console: "console",
  sistema: "sistema",
};

const FORNITORI: Record<string, string> = {
  stripe: "Stripe",
  google_play: "Google Play",
  app_store: "App Store",
  mock: "simulato",
  interno: "interno",
};

/* L'incasso di una riga come lo cita il suo storno: il riferimento del fornitore, o la riga stessa se non ne ha. */
const incasso = (m: Movimento) => `${m.provider ?? ""}:${m.riferimento ?? `voce:${m.id}`}`;

export function Movimenti({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  // Gli incassi già stornati (fra le righe mostrate): niente pulsante, il backend risponderebbe 409.
  const stornati = new Set(utente.movimenti.filter((m) => m.reason === "storno").map(incasso));
  const stornabile = (m: Movimento) =>
    m.id !== null &&
    m.delta > 0 &&
    (m.reason === "acquisto" || m.reason === "accredito_piano") &&
    !stornati.has(incasso(m));

  const storna = async (m: Movimento) => {
    const motivo = window.prompt(
      `Stornare ${m.delta} crediti (${MOTIVI[m.reason] ?? m.reason})? Il denaro NON viene rimborsato: questo registra ` +
        "un rimborso o una contestazione già avvenuti presso il fornitore. Il saldo può andare sotto zero.\n\nMotivo:",
    );
    if (motivo === null) return;
    if (motivo.trim().length < 3) {
      window.alert("Serve un motivo di almeno tre caratteri.");
      return;
    }
    const fatto = await esegui((t) => stornaMovimento(t, utente.id, m.id as number, motivo.trim()));
    if (fatto) ricarica();
  };

  return (
    <section className={stili.sezione}>
      <h2 className={stili.sezioneTitolo}>Movimenti dei crediti</h2>
      <p className={comuni.riquadroNota}>
        Gli ultimi cinquanta, dal più recente. Il registro non si corregge:
        un errore si ripara con una rettifica che lo compensa.
      </p>
      {errore && <p className={comuni.errore}>{errore}</p>}
      {utente.movimenti.length === 0 ? (
        <div className={comuni.vuoto}>Nessun movimento.</div>
      ) : (
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th>Quando</th>
                <th>Motivo</th>
                <th className={comuni.numero}>Crediti</th>
                <th>Origine</th>
                <th>Nota</th>
                <th>Lettura</th>
                <th aria-label="Azioni" />
              </tr>
            </thead>
            <tbody>
              {utente.movimenti.map((m, i) => (
                <tr key={m.id ?? `${m.quando}-${i}`}>
                  <td className={comuni.mono}>{quandoCompleto(m.quando)}</td>
                  <td>{MOTIVI[m.reason] ?? m.reason}</td>
                  <td className={`${comuni.numero} ${m.delta > 0 ? comuni.positivo : comuni.negativo}`}>
                    {m.delta > 0 ? `+${m.delta}` : `−${Math.abs(m.delta)}`}
                  </td>
                  <td>
                    {m.canale ? CANALI[m.canale] ?? m.canale : "—"}
                    {m.provider && m.provider !== "interno" && <> · {FORNITORI[m.provider] ?? m.provider}</>}
                    {m.riferimento && (
                      <div className={`${comuni.campoAiuto} ${comuni.mono}`} title={m.riferimento}>
                        {m.riferimento.length > 24 ? `${m.riferimento.slice(0, 24)}…` : m.riferimento}
                      </div>
                    )}
                  </td>
                  <td>{m.note ?? <span className={comuni.campoAiuto}>—</span>}</td>
                  {/* Solo l'identificativo: la lettura è dell'utente, e la
                      console non la apre. */}
                  <td className={comuni.mono}>{m.reading_id ? m.reading_id.slice(0, 8) : "—"}</td>
                  <td>
                    {stornabile(m) && (
                      <button
                        type="button"
                        className={comuni.secondaria}
                        onClick={() => storna(m)}
                        disabled={inCorso}
                        aria-label={`Storna ${m.delta} crediti del ${quandoCompleto(m.quando)}`}
                      >
                        Storna
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
