"use client";

/* Le proprie carte (specifica v2, §9): il mazzo è fisico e già estratto. Si sceglie la stesa usata, si dice quale
 * carta c'è in ogni posizione, si scrive la domanda; poi la stessa apertura di sempre (`POST /readings` con
 * `manual_cards`) e la lettura continua nella pagina della lettura, che mostra le carte già scoperte. Nessun
 * modello nuovo: è la funzione «Interpreta i miei tarocchi» del sito.
 *
 * Il tavolo e la domanda si ricordano nella sessione del browser: chi deve entrare nell'account per continuare
 * li ritrova al ritorno. */

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useTraccia } from "lanterna-osservatore/react";
import { ErroreApi, apriLettura, elencaCarte, elencaStese, leggiDisclaimer, type Carta, type Stesa } from "@/lib/api";
import { nomeCarta, nomePosizione, nomeStesa } from "@/lib/i18n/nomi";
import { useSessione } from "@/lib/sessione";
import { f } from "@/v2/i18n";
import { Modale } from "@/v2/componenti/modale";
import { linguaContenuti } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";
import { domandaBasta } from "./domanda";
import { SceltaStesa } from "./preparazione";
import { Tavolo, type Posata } from "./tavolo";
import stili from "./lettura.module.css";

const CHIAVE = "tarots.v2.fisica";
type Seme = "maggiori" | "bastoni" | "coppe" | "spade" | "dischi";
const SEMI: Seme[] = ["maggiori", "bastoni", "coppe", "spade", "dischi"];

interface Bozza { stesaId: string | null; assegnazioni: Record<number, string>; domanda: string }

function leggiBozza(): Bozza | null {
  try {
    const b = JSON.parse(window.sessionStorage.getItem(CHIAVE) ?? "null") as Bozza | null;
    return b && typeof b === "object" ? b : null;
  } catch {
    return null;
  }
}

function DialogoCarta({
  aperta, posizione, carte, occupate, onConferma, onChiudi,
}: {
  aperta: boolean;
  posizione: string;
  carte: Carta[];
  occupate: Set<string>;
  onConferma: (id: string) => void;
  onChiudi: () => void;
}) {
  const { t, lingua } = useLingua();
  const fi = t.fisica;
  const [seme, setSeme] = useState<Seme | null>(null);
  const [scelta, setScelta] = useState<string | null>(null);
  const chiudi = () => { setSeme(null); setScelta(null); onChiudi(); };
  const visibili = seme ? carte.filter((c) => (seme === "maggiori" ? c.arcano === "maggiore" : c.seme === seme)) : [];
  return (
    <Modale aperta={aperta} titolo={f(seme ? fi.carta_titolo : fi.seme_titolo, { posizione })} onChiudi={chiudi}>
      {!seme ? (
        <ul className="list-plain" style={{ display: "grid", gap: ".5rem" }}>
          {SEMI.map((s) => (
            <li key={s}><button type="button" className="button button-quiet" style={{ width: "100%", justifyContent: "flex-start" }}
              onClick={() => setSeme(s)}>{fi.semi[s]}</button></li>
          ))}
        </ul>
      ) : (
        <>
          <ul className="chips" style={{ maxHeight: "50dvh", overflowY: "auto" }}>
            {visibili.map((c) => {
              const occupata = occupate.has(c.id) && scelta !== c.id;
              return (
                <li key={c.id}>
                  <button type="button" className="chip" disabled={occupata} aria-pressed={c.id === scelta}
                    title={occupata ? fi.gia_posata : undefined} onClick={() => setScelta(c.id)}>
                    {nomeCarta(c, lingua)}
                  </button>
                </li>
              );
            })}
          </ul>
          <div className="button-row" style={{ marginTop: "1rem" }}>
            <button type="button" className="button button-quiet" onClick={() => { setSeme(null); setScelta(null); }}>{t.comune.indietro}</button>
            <button type="button" className="button" disabled={!scelta} onClick={() => { if (scelta) { onConferma(scelta); chiudi(); } }}>
              {fi.conferma}
            </button>
          </div>
        </>
      )}
    </Modale>
  );
}

export function LetturaFisica() {
  const { t, lingua, prefissoIt } = useLingua();
  const fi = t.fisica;
  const l = t.lettura;
  const sessione = useSessione();
  const router = useRouter();
  const traccia = useTraccia();
  const stese = useCarica(() => elencaStese("standard", linguaContenuti(lingua)), [lingua], { pubblico: true });
  const carte = useCarica(() => elencaCarte(linguaContenuti(lingua)), [lingua], { pubblico: true });

  const [stesaId, setStesaId] = useState<string | null>(null);
  const [assegnazioni, setAssegnazioni] = useState<Record<number, string>>({});
  const [domanda, setDomanda] = useState("");
  const [attiva, setAttiva] = useState<number | null>(null);
  const [disclaimer, setDisclaimer] = useState<string | null>(null);
  const [mostraDisclaimer, setMostraDisclaimer] = useState(false);
  const [inCorso, setInCorso] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);
  const [ripresa, setRipresa] = useState(false);

  /* La bozza della sessione, una volta dopo il montaggio. */
  useEffect(() => {
    const b = leggiBozza();
    if (b) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setStesaId(b.stesaId);
      setAssegnazioni(b.assegnazioni ?? {});
      setDomanda(b.domanda ?? "");
    }
    setRipresa(true);
    const sorgente = new URLSearchParams(window.location.search).get("source");
    if (sorgente) traccia(sorgente === "qr" ? "qr_entry" : "reading_entry", { sorgente, pagina: "fisica" });
  }, [traccia]);
  useEffect(() => {
    if (!ripresa) return;
    try {
      window.sessionStorage.setItem(CHIAVE, JSON.stringify({ stesaId, assegnazioni, domanda }));
    } catch {
      /* senza memoria di sessione la bozza vale per questa pagina */
    }
  }, [ripresa, stesaId, assegnazioni, domanda]);

  const stesa: Stesa | undefined = useMemo(() => stese.dati?.find((s) => s.id === stesaId), [stese.dati, stesaId]);
  const daRiempire = useMemo(() => (stesa ? stesa.posizioni.filter((p) => !p.calcolata) : []), [stesa]);
  const mancano = daRiempire.filter((p) => !assegnazioni[p.n]).length;
  const occupate = useMemo(() => new Set(Object.values(assegnazioni)), [assegnazioni]);
  const posate: Posata[] = useMemo(
    () => Object.entries(assegnazioni).map(([p, id]) => ({
      posizione: Number(p), slot: null, calcolata: false, rivelata: false,
      carta: (carte.dati ?? []).find((c) => c.id === id),
    })),
    [assegnazioni, carte.dati],
  );
  const nomeAttiva = attiva !== null && stesa ? nomePosizione(stesa.posizioni.find((p) => p.n === attiva)!, lingua) : "";
  const pronta = !!stesa && mancano === 0 && domandaBasta(domanda);

  const scegliStesa = (id: string) => {
    if (id === stesaId) return;
    setStesaId(id);
    setAssegnazioni({});
    traccia("physical_reading_started");
  };

  const chiediInizio = async () => {
    if (!sessione.autenticata) {
      sessione.entra(indirizzoV2(R.fisica, prefissoIt));
      return;
    }
    if (!disclaimer) {
      try { setDisclaimer((await leggiDisclaimer(lingua)).testo); } catch { /* arriva con la lettura */ }
    }
    setMostraDisclaimer(true);
  };

  const apri = async () => {
    if (!stesaId || !pronta) return;
    setMostraDisclaimer(false);
    setInCorso(true);
    setErrore(null);
    try {
      const a = await apriLettura(sessione.token, {
        spreadId: stesaId, domanda: domanda.trim(), lang: lingua,
        manualCards: Object.entries(assegnazioni).map(([p, id]) => ({ posizione: Number(p), cardId: id })),
      });
      traccia("reading_started", { categoria: "manuale" });
      try { window.sessionStorage.removeItem(CHIAVE); } catch { /* niente */ }
      if (a.id) router.replace(indirizzoV2(`${R.leggi}?id=${a.id}`, prefissoIt));
    } catch (e) {
      setErrore(e instanceof ErroreApi ? e.message : l.err_lettura);
      setInCorso(false);
    }
  };

  return (
    <section className="band band-tight">
      <div className="read-layout">
        <section className="read-panel" aria-labelledby="fisica-1">
          <p className="eyebrow">{fi.passo_1}</p>
          {!stesa ? (
            <>
              <h2 id="fisica-1">{fi.stesa_titolo}</h2>
              {stese.dati && <SceltaStesa stese={stese.dati} scelta={stesaId} onScegli={scegliStesa} conStili={false} conTitolo={false} />}
              {stese.errore && <p className="error">{stese.errore}</p>}
            </>
          ) : (
            <>
              <h2 id="fisica-1">{nomeStesa(stesa, lingua)}</h2>
              <p className="muted small">{fi.posiziona}</p>
              <Tavolo stesa={stesa} posate={posate} prossima={null} rivelazioneInCorso={false} evidenzia={null} manuale
                onSelezionaPosizione={setAttiva} testoAggiungi={fi.aggiungi} testoModifica={fi.modifica} />
              <p className={mancano ? "notice" : "success"} role="status">
                {mancano === 0 ? fi.pronte : mancano === 1 ? fi.manca_una : f(fi.mancano, { n: mancano })}
              </p>
              <button type="button" className="button button-quiet button-small" style={{ marginTop: "1rem" }}
                onClick={() => { setStesaId(null); setAssegnazioni({}); }}>{fi.cambia_stesa}</button>
            </>
          )}
        </section>

        <section className="read-panel dark" aria-labelledby="fisica-2">
          <p className="eyebrow">{fi.passo_2}</p>
          <h2 id="fisica-2">{fi.domanda_titolo}</h2>
          <label className="sr-only" htmlFor="domanda-fisica">{fi.domanda_titolo}</label>
          <textarea id="domanda-fisica" className={stili.domanda} rows={5} dir="auto" maxLength={1000}
            placeholder={fi.domanda_segnaposto} value={domanda} onChange={(e) => setDomanda(e.target.value)} />
          <p className={stili.consoleTesto} style={{ textAlign: "left", marginInline: 0 }}>{fi.domanda_testo}</p>
          {sessione.pronta && !sessione.autenticata && <p className="notice dark">{fi.serve_account}</p>}
          <button type="button" className="button button-brass" disabled={!pronta || inCorso} onClick={chiediInizio}>
            {inCorso ? t.comune.carica : sessione.autenticata || !sessione.pronta ? fi.interpreta : fi.entra}
          </button>
          {errore && <p className="error" role="alert">{errore}</p>}
        </section>
      </div>

      <DialogoCarta aperta={attiva !== null} posizione={nomeAttiva} carte={carte.dati ?? []} occupate={occupate}
        onConferma={(id) => { if (attiva !== null) setAssegnazioni((a) => ({ ...a, [attiva]: id })); }}
        onChiudi={() => setAttiva(null)} />
      <Modale aperta={mostraDisclaimer} titolo={l.avviso_titolo} onChiudi={() => setMostraDisclaimer(false)}>
        <p className="prose" dir="auto">{disclaimer ?? ""}</p>
        <div className="button-row">
          <button type="button" className="button button-brass" onClick={apri} autoFocus>{l.avviso_accetta}</button>
        </div>
      </Modale>
    </section>
  );
}
