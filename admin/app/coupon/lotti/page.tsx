"use client";

/* Lotti di codici monouso (v9, Fase 2d): «genera N codici» con un prefisso, ognuno usabile una volta sola, con le
 * stesse regole di sconto e la campagna del lotto. Si esportano in CSV (codice, stato, usato il, link) per mandarli uno
 * per persona — una newsletter, un influencer, un evento. Un lotto si disattiva tutto insieme; i codici usati restano
 * nel resoconto. */

import { useState } from "react";
import { catalogo } from "@/lib/api";
import { centesimiDa, giorno, soldi } from "@/lib/formato";
import {
  attivaLotto, coupons, creaLotto, durataCoupon, lotti, scaricaLotto, valoreCoupon,
  type Coupon, type Lotto, type NuovoLotto, type TipoCoupon,
} from "@/lib/offerte";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../coupon.module.css";
import { Copia, fineGiorno, inizioGiorno, validita } from "../pezzi";
import { CampiRegole, CampoCampagna, SceltaPiani, regoleDaInviare, type Regole } from "../regole";

const MASSIMO = 5000;

export default function PaginaLotti() {
  const elenco = useDati(lotti);
  const piani = useDati(catalogo);
  const [nuovo, setNuovo] = useState(false);
  const scelte = (piani.dati ?? []).map((p) => ({ slug: p.slug, nome: p.nome }));
  const campagne = [...new Set((elenco.dati ?? []).map((l) => l.campagna).filter((c): c is string => !!c))].sort();

  return (
    <>
      <div className={stili.comandi} style={{ marginBottom: "1.25rem" }}>
        <button className={comuni.primaria} type="button" aria-expanded={nuovo} onClick={() => setNuovo(!nuovo)}>
          {nuovo ? "Chiudi" : "Genera codici"}
        </button>
      </div>
      {nuovo && <NuovoLottoForm piani={scelte} campagne={campagne} chiudi={() => setNuovo(false)} creato={elenco.ricarica} />}

      {elenco.errore && <p className={comuni.errore}>{elenco.errore}</p>}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {elenco.dati && elenco.dati.length === 0 && (
        <div className={comuni.vuoto}>Nessun lotto ancora: genera dei codici monouso per una campagna.</div>
      )}
      {elenco.dati && elenco.dati.length > 0 && (
        <ul className={`${stili.elenco} ${elenco.inCorso ? comuni.inRicarica : ""}`} aria-label="Lotti">
          {elenco.dati.map((l) => <VoceLotto key={l.id} lotto={l} piani={scelte} ricarica={elenco.ricarica} />)}
        </ul>
      )}
    </>
  );
}

function VoceLotto({ lotto: l, piani, ricarica }: {
  lotto: Lotto; piani: { slug: string; nome: string }[]; ricarica: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [codici, setCodici] = useState<Coupon[] | null>(null);
  const attivo = l.attivi > 0;
  const r = l.regole;

  const commuta = async () => {
    if (await esegui((t) => attivaLotto(t, l.id, !attivo))) ricarica();
  };
  const esporta = () => esegui((t) => scaricaLotto(t, l));
  const mostra = async () => {
    if (codici) return setCodici(null);
    const c = await esegui((t) => coupons(t, l.id));
    if (c) setCodici(c);
  };

  return (
    <li className={attivo ? stili.voce : stili.voceSpenta}>
      <div className={stili.testata}>
        <div>
          <h2 className={stili.titoloScheda}>{l.prefisso}-…</h2>
          <div className={comuni.mono}>{l.campagna ?? "senza campagna"}</div>
        </div>
        {r && <div className={stili.valore}>{valoreCoupon(r, (n) => soldi(n))}</div>}
      </div>
      {l.descrizione && <p className={stili.descrizione}>{l.descrizione}</p>}
      <dl className={stili.dati}>
        <dt>Codici</dt>
        <dd>{l.quantita}: {l.usati} usati, {l.attivi} attivi</dd>
        {r && (
          <>
            <dt>Valido</dt>
            <dd>{validita(r)}</dd>
            {r.tipo !== "crediti" && (
              <>
                <dt>Vale per</dt>
                <dd>{r.piani.length ? r.piani.map((s) => piani.find((p) => p.slug === s)?.nome ?? s).join(", ") : "tutte le offerte"}</dd>
                <dt>Abbonamenti</dt>
                <dd>{durataCoupon(r)}; {r.cumulabile ? "cumulabile" : "non cumulabile"}</dd>
              </>
            )}
          </>
        )}
        <dt>Creato</dt>
        <dd>{giorno(l.creato)}</dd>
      </dl>
      <div className={stili.comandi}>
        <button type="button" className={comuni.primaria} onClick={esporta} disabled={inCorso}>Esporta CSV</button>
        <button type="button" className={comuni.secondaria} onClick={mostra} aria-expanded={codici !== null} disabled={inCorso}>
          {codici ? "Nascondi i codici" : "Vedi i codici"}
        </button>
        <button type="button" className={comuni.secondaria} onClick={commuta} disabled={inCorso}>
          {attivo ? "Disattiva il lotto" : "Riattiva il lotto"}
        </button>
      </div>
      {errore && <p className={comuni.errore}>{errore}</p>}
      {codici && (
        <div className={stili.usi}>
          <ul aria-label={`Codici del lotto ${l.prefisso}`}>
            {codici.map((c) => (
              <li key={c.id}>
                <span className={comuni.mono}>{c.codice}</span>
                <span>{c.riscatti > 0 ? "usato" : c.attivo ? "libero" : "disattivato"}</span>
                <span>{c.link ? <Copia testo={c.link.en} etichetta="Link" descrizione={`Copia il link di ${c.codice}`} /> : null}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </li>
  );
}

function NuovoLottoForm({ piani, campagne, chiudi, creato }: {
  piani: { slug: string; nome: string }[]; campagne: string[]; chiudi: () => void; creato: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [prefisso, setPrefisso] = useState("");
  const [quantita, setQuantita] = useState("100");
  const [campagna, setCampagna] = useState("");
  const [descrizione, setDescrizione] = useState("");
  const [tipo, setTipo] = useState<TipoCoupon>("percentuale");
  const [valore, setValore] = useState("");
  const [scelti, setScelti] = useState<string[]>([]);
  const [primo, setPrimo] = useState(false);
  const [dal, setDal] = useState("");
  const [fino, setFino] = useState("");
  const [regole, setRegole] = useState<Regole>({ durata: "una_volta", periodi: "3", cumulabile: false });
  const [problema, setProblema] = useState<string | null>(null);
  const [fatto, setFatto] = useState<Lotto | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    const n = Number(quantita);
    if (!Number.isInteger(n) || n < 1 || n > MASSIMO) return setProblema(`Da 1 a ${MASSIMO} codici per lotto.`);
    const v = tipo === "importo" ? centesimiDa(valore) : Number(valore);
    if (v === null || !Number.isFinite(v) || v < 1) return setProblema("Il valore non è valido.");
    if (tipo === "percentuale" && (v > 100 || !Number.isInteger(v))) return setProblema("Una percentuale è un intero da 1 a 100.");
    const corpo: NuovoLotto = {
      prefisso: prefisso.trim(), quantita: n, campagna: campagna.trim(), tipo, valore: v,
      valido_dal: inizioGiorno(dal), valido_fino: fineGiorno(fino),
    };
    if (descrizione.trim()) corpo.description = descrizione.trim();
    if (tipo !== "crediti") {
      corpo.piani = scelti;
      corpo.solo_primo_acquisto = primo;
      const r = regoleDaInviare(regole);
      if (!r) return setProblema("«Per N pagamenti» vuole un numero da 2 a 36.");
      Object.assign(corpo, r);
    }
    const lotto = await esegui((t) => creaLotto(t, corpo));
    if (lotto) {
      setFatto(lotto);
      creato();
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="nuovo-lotto">
      <h2 id="nuovo-lotto" className={comuni.riquadroTitolo}>Genera codici monouso</h2>
      <form onSubmit={invia} className={stili.modulo}>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Prefisso</span>
            <input className={comuni.ingresso} value={prefisso} required maxLength={20} autoCapitalize="characters"
              onChange={(e) => setPrefisso(e.target.value.toUpperCase())} placeholder="NEWS" />
            <span className={comuni.campoAiuto}>I codici saranno PREFISSO-XXXXXXXX (8 caratteri leggibili).</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Quanti codici</span>
            <input className={comuni.ingresso} type="number" min={1} max={MASSIMO} inputMode="numeric" value={quantita}
              onChange={(e) => setQuantita(e.target.value)} />
            <span className={comuni.campoAiuto}>Ognuno si usa una volta sola. Al massimo {MASSIMO}.</span>
          </label>
        </div>
        <CampoCampagna valore={campagna} cambia={setCampagna} suggerite={campagne} obbligatoria />
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Descrizione (solo per te)</span>
          <input className={comuni.ingresso} value={descrizione} maxLength={500} onChange={(e) => setDescrizione(e.target.value)} />
        </label>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Che cos&apos;è</span>
            <select className={comuni.selezione} value={tipo} onChange={(e) => setTipo(e.target.value as TipoCoupon)}>
              <option value="percentuale">Sconto in percentuale</option>
              <option value="importo">Sconto di un importo</option>
              <option value="crediti">Codice regalo in crediti</option>
            </select>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>{tipo === "percentuale" ? "Sconto (%)" : tipo === "importo" ? "Sconto (€)" : "Crediti"}</span>
            <input className={comuni.ingresso} inputMode="decimal" value={valore} required onChange={(e) => setValore(e.target.value)} />
          </label>
        </div>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Valido dal</span>
            <input className={comuni.ingresso} type="date" value={dal} onChange={(e) => setDal(e.target.value)} />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Fino al (compreso)</span>
            <input className={comuni.ingresso} type="date" value={fino} onChange={(e) => setFino(e.target.value)} />
          </label>
        </div>
        {tipo !== "crediti" && (
          <>
            <SceltaPiani piani={piani} scelti={scelti} cambia={setScelti} />
            <CampiRegole regole={regole} cambia={setRegole} />
            <label className={stili.spunta}>
              <input type="checkbox" checked={primo} onChange={(e) => setPrimo(e.target.checked)} />
              Solo sul primo acquisto
            </label>
          </>
        )}
        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {fatto && (
          <p className={comuni.esito} role="status">
            Generati {fatto.quantita} codici {fatto.prefisso}-… per «{fatto.campagna}»: esportali in CSV dall&apos;elenco.
          </p>
        )}
        <div className={stili.comandi}>
          <button className={comuni.primaria} type="submit" disabled={inCorso}>Genera</button>
          <button className={comuni.secondaria} type="button" onClick={chiudi} disabled={inCorso}>Chiudi</button>
        </div>
      </form>
    </section>
  );
}
