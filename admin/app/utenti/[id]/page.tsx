"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useState } from "react";
import {
  catalogo,
  dettaglioUtente,
  impostaAttivo,
  rettificaCrediti,
  type UtenteDettaglio,
} from "@/lib/api";
import { regalaCrediti } from "@/lib/offerte";
import { giorno, quandoCompleto } from "@/lib/formato";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import { TabellaPagamenti } from "../../pagamenti/tabella";
import stili from "./dettaglio.module.css";
import { AcquistiStore } from "./acquisti-store";
import { Movimenti } from "./movimenti";

/* Un utente, visto da chi amministra.
 *
 * Si vede il conto — saldo, abbonamento, movimenti, pagamenti — e quante
 * letture ha fatto, mai che cosa ha chiesto. Si può sospendere l'account,
 * regalare crediti, rettificare il saldo e stornare un incasso (`movimenti.tsx`).
 * Tutto finisce nel registro, con chi l'ha fatto.
 */

const STATI_LETTURA: Record<string, string> = {
  completata: "completate",
};

export default function DettaglioUtente() {
  const { id } = useParams<{ id: string }>();
  const numero = Number(id);

  const { dati, errore, inCorso, ricarica } = useDati(
    useCallback((t: string) => dettaglioUtente(t, numero), [numero]),
  );

  if (!Number.isInteger(numero)) {
    return <p className={comuni.errore}>Identificativo non valido.</p>;
  }

  return (
    <>
      <p className={stili.briciole}>
        <Link href="/utenti" className={comuni.collegamento}>
          ← Utenti
        </Link>
      </p>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {!dati && inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {dati && <Scheda utente={dati} ricarica={ricarica} />}
    </>
  );
}

function Scheda({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const letture = Object.entries(utente.letture).sort(([, a], [, b]) => b - a);
  const totaleLetture = letture.reduce((s, [, n]) => s + n, 0);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>
            {utente.display_name || utente.email || `Utente #${utente.id}`}
          </h1>
          <p className={comuni.sottotitolo}>
            <span className={comuni.mono}>#{utente.id}</span>
            {utente.email && <> · {utente.email}</>}
            {" · "}iscritto il {giorno(utente.creato)}
            {utente.locale && <> · lingua {utente.locale}</>}
          </p>
        </div>
        <Attivazione utente={utente} ricarica={ricarica} />
      </div>

      <div className={stili.sommario}>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Saldo</div>
          <div className={`${stili.voceValore} ${utente.saldo < 0 ? comuni.negativo : ""}`}>
            {utente.saldo} <small>crediti</small>
          </div>
        </div>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Abbonamento</div>
          {utente.abbonamento ? (
            <>
              <div className={stili.voceValore}>{utente.abbonamento.nome}</div>
              <div className={comuni.campoAiuto}>
                {utente.abbonamento.stato} · fino al {giorno(utente.abbonamento.fine)}
              </div>
            </>
          ) : (
            <div className={stili.voceValore}>—</div>
          )}
        </div>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Letture</div>
          <div className={stili.voceValore}>{totaleLetture}</div>
          {letture.length > 0 && (
            <div className={comuni.campoAiuto}>
              {letture.map(([s, n]) => `${n} ${STATI_LETTURA[s] ?? s}`).join(" · ")}
            </div>
          )}
        </div>
        <div className={stili.voce}>
          <div className={stili.voceEtichetta}>Invito</div>
          <div className={`${stili.voceValore} ${comuni.mono}`}>{utente.referral_code ?? "—"}</div>
          {utente.invitato_da !== null && (
            <div className={comuni.campoAiuto}>
              invitato da{" "}
              <Link href={`/utenti/${utente.invitato_da}`} className={comuni.collegamento}>
                #{utente.invitato_da}
              </Link>
            </div>
          )}
        </div>
      </div>

      <Anagrafica utente={utente} />
      <Regalo utente={utente} ricarica={ricarica} />
      <Rettifica utente={utente} ricarica={ricarica} />

      <Movimenti utente={utente} ricarica={ricarica} />

      <section className={stili.sezione}>
        <h2 className={stili.sezioneTitolo}>Pagamenti</h2>
        {utente.pagamenti.length === 0 ? (
          <div className={comuni.vuoto}>Nessun pagamento.</div>
        ) : (
          <TabellaPagamenti pagamenti={utente.pagamenti} senzaUtente />
        )}
      </section>

      <AcquistiStore acquisti={utente.acquisti_store ?? []} />
    </>
  );
}

/* Sospendere e riattivare.
 *
 * Una conferma prima di sospendere, nessuna prima di riattivare: il primo
 * gesto chiude fuori una persona, il secondo la lascia rientrare. */
function Attivazione({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();

  const cambia = async () => {
    if (
      utente.attivo &&
      !window.confirm(
        "Disattivare l'account? L'utente non potrà più accedere finché non verrà riattivato.",
      )
    ) {
      return;
    }
    const fatto = await esegui((t) => impostaAttivo(t, utente.id, !utente.attivo));
    if (fatto) ricarica();
  };

  return (
    <div className={stili.attivazione}>
      <span className={`${comuni.stato} ${utente.attivo ? comuni.positivo : comuni.spento}`}>
        {utente.attivo ? "attivo" : "disattivato"}
      </span>
      <button
        className={utente.attivo ? comuni.distruttiva : comuni.secondaria}
        onClick={cambia}
        disabled={inCorso}
      >
        {utente.attivo ? "Disattiva" : "Riattiva"}
      </button>
      {errore && <p className={comuni.errore}>{errore}</p>}
    </div>
  );
}

/* La rettifica del saldo.
 *
 * Il motivo è obbligatorio, e non per burocrazia: sei mesi dopo, una riga
 * «+10» senza spiegazione è indistinguibile da un errore, e nessuno sa più
 * perché quel saldo è cambiato. */
function Rettifica({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [delta, setDelta] = useState("");
  const [motivo, setMotivo] = useState("");
  const [esito, setEsito] = useState<string | null>(null);

  const numero = Number(delta);
  const valido =
    delta.trim() !== "" && Number.isInteger(numero) && numero !== 0 && motivo.trim().length >= 3;

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valido) return;
    setEsito(null);
    const fatto = await esegui((t) =>
      rettificaCrediti(t, utente.id, { delta: numero, motivo: motivo.trim() }),
    );
    if (fatto) {
      setEsito(
        `${fatto.delta > 0 ? "Accreditati" : "Tolti"} ${Math.abs(fatto.delta)} crediti: saldo ora ${fatto.saldo}.`,
      );
      setDelta("");
      setMotivo("");
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro}>
      <h2 className={comuni.riquadroTitolo}>Rettifica dei crediti</h2>
      <p className={comuni.riquadroNota}>
        Un numero positivo accredita, uno negativo toglie. Diventa una riga nuova
        del registro con il motivo scritto qui, e resta nel registro delle
        operazioni con il tuo nome.
      </p>
      <form className={comuni.riga} onSubmit={invia}>
        <label className={comuni.campo} style={{ flex: "0 1 9rem" }}>
          <span className={comuni.campoEtichetta}>Crediti</span>
          <input
            className={comuni.ingresso}
            type="number"
            step={1}
            inputMode="numeric"
            value={delta}
            onChange={(e) => setDelta(e.target.value)}
            placeholder="es. 5 o −3"
            required
          />
        </label>
        <label className={comuni.campo} style={{ flex: "1 1 20rem" }}>
          <span className={comuni.campoEtichetta}>Motivo (obbligatorio)</span>
          <input
            className={comuni.ingresso}
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            placeholder="es. rimborso per lettura interrotta da un guasto"
            minLength={3}
            maxLength={500}
            required
          />
        </label>
        <button
          className={comuni.primaria}
          type="submit"
          disabled={!valido || inCorso}
          style={{ marginBottom: "0.9rem" }}
        >
          Applica
        </button>
      </form>
      {errore && <p className={comuni.errore}>{errore}</p>}
      {esito && <p className={comuni.esito}>{esito}</p>}
    </section>
  );
}

/* Un regalo di crediti: un pacchetto del catalogo o una quantità. Compare nel registro dell'utente come «Omaggio»,
 * con la nota scritta qui, e nel registro delle operazioni con il tuo nome. A differenza della rettifica non serve a
 * correggere un errore: serve a dare. */
function Regalo({ utente, ricarica }: { utente: UtenteDettaglio; ricarica: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const piani = useDati(catalogo);
  const pacchetti = (piani.dati ?? []).filter((p) => p.tipo === "pacchetto" && p.attivo);
  const [modo, setModo] = useState<"pacchetto" | "quantita">("pacchetto");
  const [scelto, setScelto] = useState("");
  const [quanti, setQuanti] = useState("");
  const [nota, setNota] = useState("");
  const [esito, setEsito] = useState<string | null>(null);

  const numero = Number(quanti);
  const pacchettoScelto = scelto || pacchetti[0]?.slug || "";
  const valido = modo === "pacchetto" ? pacchettoScelto !== "" : Number.isInteger(numero) && numero >= 1;

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valido) return;
    setEsito(null);
    const fatto = await esegui((t) =>
      regalaCrediti(t, utente.id, {
        ...(modo === "pacchetto" ? { piano: pacchettoScelto } : { crediti: numero }),
        ...(nota.trim() ? { nota: nota.trim() } : {}),
      }),
    );
    if (fatto) {
      setEsito(`Regalati ${fatto.crediti} crediti: saldo ora ${fatto.saldo}.`);
      setQuanti("");
      setNota("");
      ricarica();
    }
  };

  return (
    <section className={comuni.riquadro}>
      <h2 className={comuni.riquadroTitolo}>Regala crediti</h2>
      <p className={comuni.riquadroNota}>
        Un pacchetto del catalogo o una quantità a scelta. I crediti arrivano subito, come «Omaggio», senza pagamento.
      </p>
      <form onSubmit={invia}>
        <div className={comuni.riga}>
          <label className={comuni.campo} style={{ flex: "0 1 14rem" }}>
            <span className={comuni.campoEtichetta}>Cosa</span>
            <select className={comuni.selezione} value={modo} onChange={(e) => setModo(e.target.value as typeof modo)}>
              <option value="pacchetto">Un pacchetto</option>
              <option value="quantita">Una quantità</option>
            </select>
          </label>
          {modo === "pacchetto" ? (
            <label className={comuni.campo} style={{ flex: "1 1 14rem" }}>
              <span className={comuni.campoEtichetta}>Pacchetto</span>
              <select className={comuni.selezione} value={pacchettoScelto} onChange={(e) => setScelto(e.target.value)}>
                {pacchetti.length === 0 && <option value="">Nessun pacchetto in vendita</option>}
                {pacchetti.map((p) => (
                  <option key={p.slug} value={p.slug}>
                    {p.nome} ({p.crediti} crediti)
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <label className={comuni.campo} style={{ flex: "0 1 9rem" }}>
              <span className={comuni.campoEtichetta}>Crediti</span>
              <input
                className={comuni.ingresso}
                type="number"
                min={1}
                step={1}
                inputMode="numeric"
                value={quanti}
                onChange={(e) => setQuanti(e.target.value)}
                required
              />
            </label>
          )}
          <label className={comuni.campo} style={{ flex: "1 1 16rem" }}>
            <span className={comuni.campoEtichetta}>Nota (facoltativa)</span>
            <input
              className={comuni.ingresso}
              value={nota}
              maxLength={200}
              onChange={(e) => setNota(e.target.value)}
              placeholder="es. grazie per la segnalazione"
            />
          </label>
          <button className={comuni.primaria} type="submit" disabled={!valido || inCorso} style={{ marginBottom: "0.9rem" }}>
            Regala
          </button>
        </div>
      </form>
      {errore && <p className={comuni.errore}>{errore}</p>}
      {esito && <p className={comuni.esito}>{esito}</p>}
    </section>
  );
}

/* La scheda anagrafica: ciò che la persona ha scritto o che è arrivato dai social (solo nei campi vuoti), con la
 * provenienza di ciascun campo, e la posizione attuale (dal social o dall'IP all'accesso, o corretta a mano). */
function Anagrafica({ utente }: { utente: UtenteDettaglio }) {
  const a = utente.anagrafica;
  if (!a) return null;
  const campi = a.dati_social.campi ?? {};
  const origine = (campo: string) => {
    const voce = campi[campo];
    if (!voce) return null;
    return voce.da === "utente" ? "scritto dalla persona" : voce.da === "account" ? "dall'iscrizione" : `da ${voce.da}, ${giorno(voce.il)}`;
  };
  const righe: [string, string | null, string][] = [
    ["Nome", a.nome, "nome"],
    ["Cognome", a.cognome, "cognome"],
    ["Data di nascita", a.nascita ? giorno(a.nascita) : null, "birth_date"],
    ["Genere", a.genere === "altro" ? `altro (${a.genere_altro ?? ""})` : a.genere, "gender"],
    ["Lingua", utente.locale, "locale"],
  ];
  const pos = a.posizione;
  return (
    <section className={stili.sezione}>
      <h2 className={stili.sezioneTitolo}>Scheda anagrafica</h2>
      <p className={comuni.riquadroNota}>
        I social riempiono solo i campi vuoti, all&apos;accesso; la persona li corregge dal profilo.
        {" "}Importazione dai social {a.importa_social ? "accesa" : "spenta"}, rilevamento della posizione {a.rileva_posizione ? "acceso" : "spento"}.
        {a.dati_social.ultimo && <> Ultimo accesso con lettura dei social: {quandoCompleto(a.dati_social.ultimo.il)}{a.dati_social.ultimo.provider.length ? ` (${a.dati_social.ultimo.provider.join(", ")})` : ""}.</>}
      </p>
      <div className={comuni.contenitoreTabella}>
        <table className={comuni.tabella}>
          <thead><tr><th>Campo</th><th>Valore</th><th>Provenienza</th></tr></thead>
          <tbody>
            {righe.map(([etichetta, valore, campo]) => (
              <tr key={campo}><td>{etichetta}</td><td>{valore || "—"}</td><td>{origine(campo) ?? "—"}</td></tr>
            ))}
            {campi.avatar && <tr><td>Immagine</td><td>foto del profilo social</td><td>{origine("avatar")}</td></tr>}
            <tr>
              <td>Posizione attuale</td>
              <td>{pos ? [pos.citta, pos.paese].filter(Boolean).join(", ") : "—"}</td>
              <td>{pos ? `${pos.fonte === "ip" ? "dall'IP" : pos.fonte === "utente" ? "corretta dalla persona" : `da ${pos.fonte}`}, ${giorno(pos.il)}` : "—"}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
