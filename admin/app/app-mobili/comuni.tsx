"use client";

/* I pezzi che le pagine di «App mobili» condividono: lo stato caricato una volta con l'esito delle azioni, i campi
 * del modulo, il valore da copiare, il caricamento di un file segreto, l'esito della verifica e gli appunti del
 * profilo pagamenti (gli stessi su Android e iOS). */

import { useEffect, useId, useState } from "react";
import { quandoCompleto } from "@/lib/formato";
import {
  NOMI_STATO_FISCALE, NOMI_TIPO_PROFILO, statoAppMobili,
  type EsitoVerifica, type PagamentiStore, type StatoAppMobili, type StatoFiscale, type TipoProfilo, type UltimaNotifica,
} from "@/lib/app-mobili";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./app-mobili.module.css";

/** Lo stato della sezione, aggiornato da ogni azione (le risposte portano lo stato intero), e l'esito da annunciare. */
export function useAppMobili() {
  const stato = useDati(statoAppMobili);
  const { esegui, inCorso, errore } = useAzione();
  const [ultimo, setUltimo] = useState<StatoAppMobili | null>(null);
  const [esito, setEsito] = useState<string | null>(null);

  useEffect(() => {
    if (!esito) return;
    const t = window.setTimeout(() => setEsito(null), 4000);
    return () => window.clearTimeout(t);
  }, [esito]);

  const azione = async (f: (t: string) => Promise<StatoAppMobili>, messaggio: string) => {
    const r = await esegui(f);
    if (r) {
      setUltimo(r);
      setEsito(messaggio);
    }
    return r;
  };

  return { dati: ultimo ?? stato.dati, erroreCaricamento: stato.errore, azione, inCorso, errore, esito };
}

export function Messaggi({ errore, esito }: { errore: string | null; esito: string | null }) {
  return (
    <>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
      <p className={comuni.esito} role="status" hidden={!esito}>{esito}</p>
    </>
  );
}

export function Caricamento({ errore }: { errore: string | null }) {
  return errore ? <p className={comuni.errore} role="alert">{errore}</p> : <p className={comuni.caricamento}>Caricamento…</p>;
}

interface CampoProps {
  etichetta: string;
  valore: string;
  cambia: (v: string) => void;
  aiuto?: React.ReactNode;
  segnaposto?: string;
  tipo?: "text" | "email" | "date";
  modo?: "text" | "numeric" | "email" | "url";
  massimo?: number;
  mono?: boolean;
}

export function Campo({ etichetta, valore, cambia, aiuto, segnaposto, tipo = "text", modo, massimo, mono }: CampoProps) {
  const id = useId();
  return (
    <label className={comuni.campo}>
      <span className={comuni.campoEtichetta}>{etichetta}</span>
      <input
        className={comuni.ingresso}
        style={mono ? { fontFamily: "var(--apparato)" } : undefined}
        type={tipo}
        value={valore}
        onChange={(e) => cambia(e.target.value)}
        placeholder={segnaposto}
        inputMode={modo}
        maxLength={massimo}
        autoComplete="off"
        spellCheck={false}
        aria-describedby={aiuto ? `${id}-aiuto` : undefined}
      />
      {aiuto && <span id={`${id}-aiuto`} className={comuni.campoAiuto}>{aiuto}</span>}
    </label>
  );
}

export function Scelta<T extends string>({ etichetta, valore, cambia, nomi, aiuto }: {
  etichetta: string;
  valore: T;
  cambia: (v: T) => void;
  nomi: Record<T, string>;
  aiuto?: React.ReactNode;
}) {
  return (
    <label className={comuni.campo}>
      <span className={comuni.campoEtichetta}>{etichetta}</span>
      <select className={comuni.selezione} value={valore} onChange={(e) => cambia(e.target.value as T)}>
        {(Object.keys(nomi) as T[]).map((k) => <option key={k} value={k}>{nomi[k]}</option>)}
      </select>
      {aiuto && <span className={comuni.campoAiuto}>{aiuto}</span>}
    </label>
  );
}

export function Casella({ etichetta, valore, cambia, aiuto }: {
  etichetta: string;
  valore: boolean;
  cambia: (v: boolean) => void;
  aiuto?: React.ReactNode;
}) {
  return (
    <label className={stili.casella}>
      <input type="checkbox" checked={valore} onChange={(e) => cambia(e.target.checked)} />
      <span>
        {etichetta}
        {aiuto && <small>{aiuto}</small>}
      </span>
    </label>
  );
}

/** Un valore da incollare altrove (un URL da dare allo store), con il pulsante per copiarlo. */
export function Copia({ valore, etichetta }: { valore: string; etichetta: string }) {
  const [copiato, setCopiato] = useState(false);
  const copia = async () => {
    try {
      await navigator.clipboard.writeText(valore);
      setCopiato(true);
      window.setTimeout(() => setCopiato(false), 2500);
    } catch {
      /* senza appunti (pagina non sicura): il valore resta selezionabile a mano */
    }
  };
  return (
    <div className={stili.copia}>
      <span className={stili.copiaValore}>{valore}</span>
      <button type="button" className={`${comuni.secondaria} ${stili.tocco}`} onClick={copia} aria-label={`Copia ${etichetta}`}>
        {copiato ? "Copiato" : "Copia"}
      </button>
      <span className={stili.soloLettori} role="status">{copiato ? `${etichetta} copiato negli appunti` : ""}</span>
    </div>
  );
}

/** Un collegamento a un sito esterno: si apre in una nuova scheda, e lo dice. `blocco`: su una riga sua, alto 44px
 *  per il tocco; senza, resta in linea nel testo. */
export function Esterno({ href, children, blocco = false }: { href: string; children: React.ReactNode; blocco?: boolean }) {
  return (
    <a className={`${stili.collegamentoEsterno} ${blocco ? stili.collegamentoBlocco : ""}`} href={href}
      target="_blank" rel="noopener noreferrer">
      {children}
      <span aria-hidden="true"> ↗</span>
      <span className={stili.soloLettori}> (si apre in una nuova scheda)</span>
    </a>
  );
}

/** Il caricamento di un file segreto: si legge nel browser, parte una volta, non torna più. */
export function CaricaSegreto({ etichetta, accetta, presente, descrizione, carica, togli, inCorso }: {
  etichetta: string;
  accetta: string;
  presente: boolean;
  descrizione: React.ReactNode;
  carica: (testo: string) => void;
  togli: () => void;
  inCorso: boolean;
}) {
  const id = useId();
  const leggi = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const scelto = e.target.files?.[0];
    if (!scelto) return;
    carica(await scelto.text());
    e.target.value = "";
  };
  return (
    <div className={stili.segreto}>
      <p style={{ margin: "0 0 0.5rem" }}>
        <span className={`${comuni.stato} ${presente ? comuni.positivo : comuni.neutro}`}>
          {presente ? "✓ presente" : "○ non caricato"}
        </span>{" "}
        {descrizione}
      </p>
      <label htmlFor={id} className={comuni.campoEtichetta}>{presente ? `Sostituisci ${etichetta}` : `Carica ${etichetta}`}</label>
      <div className={stili.azioni} style={{ margin: "0.3rem 0 0" }}>
        <input id={id} className={stili.file} type="file" accept={accetta} onChange={leggi} disabled={inCorso} />
        {presente && (
          <button type="button" className={`${comuni.distruttiva} ${stili.tocco}`} onClick={togli} disabled={inCorso}>
            Togli
          </button>
        )}
      </div>
      <p className={comuni.campoAiuto} style={{ margin: "0.4rem 0 0" }}>
        Si salva cifrato e non si rilegge più da qui: per cambiarlo, carica il file nuovo.
      </p>
    </div>
  );
}

export function EsitoUltimaVerifica({ esito, quando }: { esito: EsitoVerifica; quando: string | null }) {
  if (esito.ok === undefined) {
    return <p className={comuni.riquadroNota}>Mai verificato.</p>;
  }
  const [segno, parola, classe] = esito.ok ? ["✓", "riuscita", comuni.positivo] : ["✗", "non riuscita", comuni.negativo];
  return (
    <div className={stili.esito} role="status">
      <span className={`${stili.esitoSegno} ${classe}`} aria-hidden="true">{segno}</span>
      <span>
        <strong>Verifica {parola}</strong>
        {quando && <span className={comuni.mono}> · {quandoCompleto(quando)}</span>}
      </span>
      <span className={stili.esitoTesto}>{esito.messaggio}</span>
    </div>
  );
}

/** Fase 4: l'ultima notifica arrivata dallo store. È la prova che il collegamento funziona: se dopo un acquisto di
 *  prova qui non cambia niente, lo store non riesce a raggiungere il sito (indirizzo sbagliato, push non autenticato). */
export function UltimaNotificaStore({ notifica }: { notifica?: UltimaNotifica }) {
  if (!notifica?.il) {
    return (
      <p className={comuni.riquadroNota} role="status">
        <strong>Ultima notifica ricevuta:</strong> nessuna, finora. Arriva dopo il primo acquisto (anche di prova) o la
        notifica di prova dello store.
      </p>
    );
  }
  const problema = (notifica.esito ?? "").startsWith("non registrata");
  return (
    <div className={stili.esito} role="status">
      <span className={`${stili.esitoSegno} ${problema ? comuni.negativo : comuni.positivo}`} aria-hidden="true">
        {problema ? "!" : "✓"}
      </span>
      <span>
        <strong>Ultima notifica ricevuta</strong>
        <span className={comuni.mono}> · {quandoCompleto(notifica.il)}</span>
      </span>
      <span className={stili.esitoTesto}>
        <span className={comuni.mono}>{notifica.tipo}</span>
        {notifica.ambiente ? ` (${notifica.ambiente === "sandbox" ? "prova, sandbox" : "produzione"})` : ""}
        {notifica.esito ? ` — ${notifica.esito}` : ""}
      </span>
    </div>
  );
}

/** Gli appunti del profilo pagamenti dello store: del conto, solo le ultime 4 cifre. */
export function AppuntiPagamenti({ pagamenti, salva, inCorso, store, aiutoProfilo }: {
  pagamenti: PagamentiStore;
  salva: (p: Partial<PagamentiStore>) => Promise<unknown>;
  inCorso: boolean;
  store: string;
  aiutoProfilo: React.ReactNode;
}) {
  const [bozza, setBozza] = useState<PagamentiStore | null>(null);
  const p = bozza ?? pagamenti;
  const cambia = (parziale: Partial<PagamentiStore>) => setBozza({ ...p, ...parziale });
  const ultime4Valide = p.conto_ultime4 === "" || /^[0-9A-Za-z]{4}$/.test(p.conto_ultime4);
  const id = useId();

  return (
    <form
      className={comuni.riquadro}
      aria-labelledby={`${id}-titolo`}
      onSubmit={async (e) => {
        e.preventDefault();
        if (!bozza || !ultime4Valide) return;
        if (await salva(bozza)) setBozza(null);
      }}
    >
      <h2 id={`${id}-titolo`} className={comuni.riquadroTitolo}>Profilo pagamenti (appunti)</h2>
      <p className={comuni.riquadroNota}>
        <strong>Solo un promemoria.</strong> Il profilo vero sta in {store}: questi dati non servono a incassare e non
        arrivano all&apos;app. Del conto si tengono solo le ultime 4 cifre; IBAN e numeri di carta interi si rifiutano,
        anche nelle note.
      </p>
      <div className={comuni.riga}>
        <Campo etichetta="ID del profilo" valore={p.id_profilo} cambia={(v) => cambia({ id_profilo: v })} aiuto={aiutoProfilo} mono />
        <Scelta<TipoProfilo> etichetta="Tipo di profilo" valore={p.tipo_profilo} nomi={NOMI_TIPO_PROFILO}
          cambia={(v) => cambia({ tipo_profilo: v })} />
      </div>
      <div className={comuni.riga}>
        <Campo etichetta="Beneficiario" valore={p.beneficiario} cambia={(v) => cambia({ beneficiario: v })} />
        <Campo etichetta="Paese (ISO)" valore={p.paese} massimo={2} segnaposto="IT"
          cambia={(v) => cambia({ paese: v.toUpperCase() })} />
      </div>
      <div className={comuni.riga}>
        <Campo etichetta="Banca" valore={p.banca} cambia={(v) => cambia({ banca: v })} />
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Conto: ultime 4 cifre</span>
          <input
            className={comuni.ingresso}
            value={p.conto_ultime4}
            onChange={(e) => cambia({ conto_ultime4: e.target.value.replace(/[\s-]/g, "").slice(0, 4) })}
            maxLength={4}
            placeholder="1234"
            autoComplete="off"
            aria-invalid={!ultime4Valide}
            aria-describedby={`${id}-ultime4`}
          />
          <span id={`${id}-ultime4`} className={comuni.campoAiuto}>Solo per riconoscere il conto.</span>
        </label>
        <Campo etichetta="Valuta" valore={p.valuta} massimo={3} segnaposto="EUR" cambia={(v) => cambia({ valuta: v.toUpperCase() })} />
      </div>
      <Scelta<StatoFiscale> etichetta="Informazioni fiscali" valore={p.stato_fiscale} nomi={NOMI_STATO_FISCALE}
        cambia={(v) => cambia({ stato_fiscale: v })} />
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Note</span>
        <textarea className={comuni.area} style={{ minHeight: "5rem", fontFamily: "inherit" }} value={p.note}
          onChange={(e) => cambia({ note: e.target.value })} />
      </label>
      <div className={stili.azioni}>
        <button type="submit" className={comuni.primaria} disabled={inCorso || !bozza || !ultime4Valide}>
          {inCorso ? "Salvataggio…" : "Salva gli appunti"}
        </button>
        {bozza && (
          <button type="button" className={comuni.secondaria} onClick={() => setBozza(null)} disabled={inCorso}>
            Annulla le modifiche
          </button>
        )}
      </div>
    </form>
  );
}
