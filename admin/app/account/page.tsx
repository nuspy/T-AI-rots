"use client";

/* Account (v9, Fase 3): tutti i servizi esterni che chiedono un account, in un posto solo. Per ognuno lo stato
 * (letto senza chiamare nessuno), i passi, **solo il primo link** della procedura del fornitore, dove sta il segreto,
 * i costi, «Gestisci» verso la sezione dove si imposta e «Verifica» dove c'è una prova gratuita. Le impostazioni
 * restano nelle sezioni competenti: qui si guarda e si parte. */

import Link from "next/link";
import { useState } from "react";
import {
  NOMI_STATO, SEGNO_DOVE, SEGNO_STATO, elencoServizi, verificaServizio,
  type ElencoServizi, type ServizioEsterno, type StatoServizio,
} from "@/lib/account-esterni";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./account.module.css";

function Badge({ stato }: { stato: StatoServizio }) {
  return (
    <span className={`${stili.badge} ${stili[stato]}`}>
      <span aria-hidden="true">{SEGNO_STATO[stato]}</span>
      {NOMI_STATO[stato]}
    </span>
  );
}

function host(url: string): string {
  try {
    return new URL(url).host.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function Scheda({ s, onVerificato }: { s: ServizioEsterno; onVerificato: (s: ServizioEsterno) => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [esito, setEsito] = useState<{ stato: StatoServizio; dettaglio: string } | null>(null);
  const titolo = `servizio-${s.id}`;

  const verifica = async () => {
    const r = await esegui((t) => verificaServizio(t, s.id));
    if (r) {
      setEsito(r.esito);
      onVerificato(r.servizio);
    }
  };

  return (
    <li className={stili.scheda} aria-labelledby={titolo}>
      <div className={stili.testa}>
        <h3 id={titolo} className={stili.nome}>{s.nome}</h3>
        <Badge stato={s.stato} />
      </div>
      {s.dettaglio && <p className={stili.dettaglio}>{s.dettaglio}</p>}
      <p className={`${stili.dove} ${stili[`dove_${s.dove}`] ?? ""}`}>
        <span aria-hidden="true">{SEGNO_DOVE[s.dove]} </span>
        {s.dove === "console" && s.sezione ? (
          <>Si imposta in console: <Link href={s.sezione}>{s.sezione.replace(/^\//, "").replace(/\//g, " → ")}</Link></>
        ) : s.dove === "server" ? (
          <>Si imposta sul server (uno dei tre segreti che restano lì)</>
        ) : (
          s.dove_testo
        )}
      </p>
      <p className={stili.meta}>
        {s.fase && <span className={comuni.etichetta}>{s.fase}</span>}
        <span>Costi: {s.costi}</span>
      </p>
      <details className={stili.passi}>
        <summary>Come fare</summary>
        <ol>{s.come_fare.map((p) => <li key={p}>{p}</li>)}</ol>
        <p><strong>Dove sta il segreto:</strong> {s.dove_sta_il_segreto}</p>
        {s.nota && <p>{s.nota}</p>}
      </details>
      {esito && (
        <p className={`${stili.esitoVerifica} ${stili[esito.stato]}`} role="status">
          <span aria-hidden="true">{SEGNO_STATO[esito.stato]} </span>
          Verifica: {NOMI_STATO[esito.stato].toLowerCase()}. <span className={stili.dettaglio}>{esito.dettaglio}</span>
        </p>
      )}
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      <div className={stili.azioni}>
        {s.primo_link && (
          <a className={stili.primoLink} href={s.primo_link} target="_blank" rel="noopener noreferrer">
            Inizia da {host(s.primo_link)} <span aria-hidden="true">↗</span>
            <span className={stili.soloLettori}> (si apre in una nuova scheda)</span>
          </a>
        )}
        {s.sezione && (
          <Link className={stili.gestisci} href={s.sezione}>
            Gestisci<span className={stili.soloLettori}> {s.nome}</span>
          </Link>
        )}
        {s.verificabile && (
          <button type="button" className={comuni.secondaria} onClick={verifica} disabled={inCorso}>
            {inCorso ? "Verifica…" : "Verifica"}
            <span className={stili.soloLettori}> {s.nome}</span>
          </button>
        )}
      </div>
    </li>
  );
}

export default function Account() {
  const stato = useDati(elencoServizi);
  const [aggiornati, setAggiornati] = useState<Record<string, ServizioEsterno>>({});
  const [filtro, setFiltro] = useState<StatoServizio | null>(null);
  const dati: ElencoServizi | null = stato.dati;

  const servizi = (dati?.servizi ?? []).map((s) => aggiornati[s.id] ?? s);
  const visibili = filtro ? servizi.filter((s) => s.stato === filtro) : servizi;
  const conteggi = servizi.reduce<Partial<Record<StatoServizio, number>>>(
    (acc, s) => ({ ...acc, [s.stato]: (acc[s.stato] ?? 0) + 1 }), {});

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Account</h1>
          <p className={comuni.sottotitolo}>
            Tutti i servizi esterni che chiedono un account: a che punto sono, come si fa, da dove si comincia. Lo
            stato si legge senza chiamare nessuno; «Verifica» fa una prova vera, sempre gratuita. Le impostazioni
            restano nelle sezioni: «Gestisci» porta lì.
          </p>
        </div>
      </div>

      {stato.errore && <p className={comuni.errore} role="alert">{stato.errore}</p>}
      {!dati && !stato.errore && <p className={comuni.caricamento}>Caricamento…</p>}

      {dati && (
        <>
          <div className={comuni.filtri} role="group" aria-label="Filtra per stato">
            <button type="button" className={filtro === null ? comuni.filtroScelto : comuni.filtro}
              aria-pressed={filtro === null} onClick={() => setFiltro(null)}>
              Tutti ({servizi.length})
            </button>
            {dati.stati.filter((st) => conteggi[st]).map((st) => (
              <button key={st} type="button" className={filtro === st ? comuni.filtroScelto : comuni.filtro}
                aria-pressed={filtro === st} onClick={() => setFiltro(filtro === st ? null : st)}>
                <span aria-hidden="true">{SEGNO_STATO[st]} </span>{NOMI_STATO[st]} ({conteggi[st]})
              </button>
            ))}
          </div>

          {dati.categorie.map((categoria) => {
            const voci = visibili.filter((s) => s.categoria === categoria);
            if (!voci.length) return null;
            const id = `categoria-${categoria.replace(/\W+/g, "-")}`;
            return (
              <section key={categoria} className={stili.categoria} aria-labelledby={id}>
                <h2 id={id} className={stili.categoriaTitolo}>{categoria}</h2>
                <ul className={stili.griglia}>
                  {voci.map((s) => (
                    <Scheda key={s.id} s={s} onVerificato={(nuovo) => setAggiornati((a) => ({ ...a, [nuovo.id]: nuovo }))} />
                  ))}
                </ul>
              </section>
            );
          })}
          {visibili.length === 0 && <p className={comuni.vuoto}>Nessun servizio in questo stato.</p>}
        </>
      )}
    </>
  );
}
