"use client";

import { useState } from "react";
import { catalogo } from "@/lib/api";
import { centesimiDa, importoPerCampo, quandoCompleto, soldi } from "@/lib/formato";
import {
  coupons, creaCoupon, eliminaCoupon, modificaCoupon, riscattiDi, valoreCoupon,
  type Coupon, type ModificaCoupon, type NuovoCoupon, type Riscatto, type TipoCoupon,
} from "@/lib/offerte";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./coupon.module.css";

/* Coupon di sconto e codici regalo.
 *
 * **Sconto** (percentuale o importo fisso): si applica al pagamento, sul primo pagamento; un abbonamento si rinnova a
 * prezzo pieno e non si può azzerare, un pacchetto sì (a zero i crediti arrivano subito, senza pagare).
 * **Codice regalo** (crediti): chi lo riscatta dal profilo riceve crediti senza pagare.
 *
 * Un coupon già usato non si elimina né cambia valore — i conti passati devono restare leggibili —: si disattiva.
 */

const TIPI: Record<TipoCoupon, { nome: string; aiuto: string }> = {
  percentuale: { nome: "Sconto in percentuale", aiuto: "Da 1 a 100. Sul primo pagamento." },
  importo: { nome: "Sconto di un importo", aiuto: "In euro, sul primo pagamento. Non scende sotto zero." },
  crediti: { nome: "Codice regalo in crediti", aiuto: "Chi lo riscatta riceve questi crediti, senza pagare." },
};

/* Una data «a giorno» → l'istante ISO: l'inizio del giorno per «dal», la fine per «fino». */
const inizioGiorno = (d: string) => (d ? new Date(`${d}T00:00:00`).toISOString() : null);
const fineGiorno = (d: string) => (d ? new Date(`${d}T23:59:59`).toISOString() : null);
const perCampo = (iso: string | null) => {
  if (!iso) return "";
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

function validita(c: Coupon): string {
  const dal = c.valido_dal ? new Date(c.valido_dal).toLocaleDateString("it-IT") : null;
  const fino = c.valido_fino ? new Date(c.valido_fino).toLocaleDateString("it-IT") : null;
  if (dal && fino) return `${dal} – ${fino}`;
  if (fino) return `fino al ${fino}`;
  if (dal) return `dal ${dal}`;
  return "sempre";
}

export default function PaginaCoupon() {
  const elenco = useDati(coupons);
  const piani = useDati(catalogo);
  const [nuovo, setNuovo] = useState(false);

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Coupon e codici regalo</h1>
          <p className={comuni.sottotitolo}>
            Gli sconti si applicano al primo pagamento; i codici regalo danno crediti a chi li riscatta. Un coupon già
            usato non si elimina: si disattiva.
          </p>
        </div>
      </div>

      <div className={stili.comandi} style={{ marginBottom: "1.25rem" }}>
        <button className={comuni.primaria} type="button" aria-expanded={nuovo} onClick={() => setNuovo(!nuovo)}>
          {nuovo ? "Chiudi" : "Nuovo coupon"}
        </button>
      </div>

      {nuovo && (
        <NuovoCouponForm
          piani={(piani.dati ?? []).map((p) => ({ slug: p.slug, nome: p.nome }))}
          chiudi={() => setNuovo(false)}
          creato={() => {
            setNuovo(false);
            elenco.ricarica();
          }}
        />
      )}

      {elenco.errore && <p className={comuni.errore}>{elenco.errore}</p>}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {elenco.dati && elenco.dati.length === 0 && (
        <div className={comuni.vuoto}>Nessun coupon ancora: creane uno per uno sconto o un codice regalo.</div>
      )}

      {elenco.dati && elenco.dati.length > 0 && (
        <ul className={`${stili.elenco} ${elenco.inCorso ? comuni.inRicarica : ""}`} aria-label="Coupon">
          {elenco.dati.map((c) => (
            <Voce key={c.id} coupon={c} piani={(piani.dati ?? []).map((p) => ({ slug: p.slug, nome: p.nome }))} ricarica={elenco.ricarica} />
          ))}
        </ul>
      )}
    </>
  );
}

function Voce({
  coupon: c, piani, ricarica,
}: {
  coupon: Coupon;
  piani: { slug: string; nome: string }[];
  ricarica: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [modifica, setModifica] = useState(false);
  const [usi, setUsi] = useState<Riscatto[] | null>(null);
  const [conferma, setConferma] = useState(false);
  const [copiato, setCopiato] = useState(false);

  const commuta = async () => {
    if (await esegui((t) => modificaCoupon(t, c.id, { attivo: !c.attivo }))) ricarica();
  };
  const elimina = async () => {
    if ((await esegui((t) => eliminaCoupon(t, c.id))) !== null) ricarica();
  };
  const mostraUsi = async () => {
    if (usi) return setUsi(null);
    const r = await esegui((t) => riscattiDi(t, c.id));
    if (r) setUsi(r.riscatti);
  };
  const copia = async () => {
    try {
      await navigator.clipboard.writeText(c.codice);
      setCopiato(true);
    } catch {
      setCopiato(false);
    }
  };

  const nomiPiani = c.piani.map((s) => piani.find((p) => p.slug === s)?.nome ?? s);

  return (
    <li className={c.attivo ? stili.voce : stili.voceSpenta}>
      <div className={stili.testata}>
        <div>
          <strong className={stili.codice}>{c.codice}</strong>{" "}
          <button type="button" className={stili.copia} onClick={copia} aria-label={`Copia il codice ${c.codice}`}>
            {copiato ? "Copiato" : "Copia"}
          </button>
          <div className={comuni.mono}>{TIPI[c.tipo].nome}</div>
        </div>
        <div className={stili.valore}>{valoreCoupon(c, (n) => soldi(n))}</div>
      </div>
      {c.descrizione && <p className={stili.descrizione}>{c.descrizione}</p>}
      <dl className={stili.dati}>
        <dt>Valido</dt>
        <dd>{validita(c)}</dd>
        <dt>Usi</dt>
        <dd>
          {c.riscatti}
          {c.max_riscatti !== null ? ` / ${c.max_riscatti}` : ""}, al massimo {c.max_per_utente} a persona
        </dd>
        {c.tipo !== "crediti" && (
          <>
            <dt>Vale per</dt>
            <dd>{nomiPiani.length ? nomiPiani.join(", ") : "tutte le offerte"}</dd>
            {c.solo_primo_acquisto && (
              <>
                <dt>Condizione</dt>
                <dd>solo sul primo acquisto</dd>
              </>
            )}
          </>
        )}
        <dt>Stato</dt>
        <dd className={c.attivo ? comuni.positivo : comuni.spento}>{c.attivo ? "attivo" : "disattivato"}</dd>
      </dl>

      {modifica ? (
        <ModuloModifica
          coupon={c}
          piani={piani}
          chiudi={() => setModifica(false)}
          salvato={() => {
            setModifica(false);
            ricarica();
          }}
        />
      ) : (
        <div className={stili.comandi}>
          <button type="button" className={comuni.secondaria} onClick={commuta} disabled={inCorso}>
            {c.attivo ? "Disattiva" : "Riattiva"}
          </button>
          <button type="button" className={comuni.secondaria} onClick={() => setModifica(true)}>
            Modifica
          </button>
          <button type="button" className={comuni.secondaria} onClick={mostraUsi} aria-expanded={usi !== null}>
            {usi ? "Nascondi gli usi" : "Chi lo ha usato"}
          </button>
          {c.riscatti === 0 &&
            (conferma ? (
              <>
                <button type="button" className={comuni.distruttiva} onClick={elimina} disabled={inCorso}>
                  Sì, elimina
                </button>
                <button type="button" className={comuni.secondaria} onClick={() => setConferma(false)}>
                  Annulla
                </button>
              </>
            ) : (
              <button type="button" className={comuni.distruttiva} onClick={() => setConferma(true)}>
                Elimina
              </button>
            ))}
        </div>
      )}
      {errore && <p className={comuni.errore}>{errore}</p>}
      {usi && (
        <div className={stili.usi}>
          {usi.length === 0 ? (
            <p className={comuni.riquadroNota}>Nessuno lo ha ancora usato.</p>
          ) : (
            <ul>
              {usi.map((u) => (
                <li key={u.id}>
                  <span>{u.email}</span>
                  <span>{u.crediti ? `${u.crediti} crediti` : `sconto ${soldi(u.sconto)}`}</span>
                  <span>{quandoCompleto(u.quando)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </li>
  );
}

/* Ciò che si può cambiare di un coupon: le regole d'uso. Il tipo e — dopo il primo uso — il valore restano com'erano. */
function ModuloModifica({
  coupon: c, piani, chiudi, salvato,
}: {
  coupon: Coupon;
  piani: { slug: string; nome: string }[];
  chiudi: () => void;
  salvato: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [descrizione, setDescrizione] = useState(c.descrizione ?? "");
  const [dal, setDal] = useState(perCampo(c.valido_dal));
  const [fino, setFino] = useState(perCampo(c.valido_fino));
  const [massimo, setMassimo] = useState(c.max_riscatti === null ? "" : String(c.max_riscatti));
  const [perUtente, setPerUtente] = useState(String(c.max_per_utente));
  const [scelti, setScelti] = useState<string[]>(c.piani);
  const [primo, setPrimo] = useState(c.solo_primo_acquisto);
  const [valore, setValore] = useState(c.tipo === "importo" ? importoPerCampo(c.valore) : String(c.valore));
  const [problema, setProblema] = useState<string | null>(null);
  const modificabile = c.riscatti === 0;

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    const corpo: ModificaCoupon = {
      description: descrizione.trim(),
      valido_dal: inizioGiorno(dal),
      valido_fino: fineGiorno(fino),
      max_per_utente: Number(perUtente) || 1,
    };
    corpo.max_riscatti = massimo.trim() === "" ? null : Number(massimo);        // vuoto: senza tetto
    if (c.tipo !== "crediti") {
      corpo.piani = scelti;
      corpo.solo_primo_acquisto = primo;
    }
    if (modificabile) {
      const v = c.tipo === "importo" ? centesimiDa(valore) : Number(valore);
      if (v === null || !Number.isFinite(v) || v < 1) return setProblema("Il valore non è valido.");
      if (v !== c.valore) corpo.valore = v;
    }
    if (await esegui((t) => modificaCoupon(t, c.id, corpo))) salvato();
  };

  return (
    <form onSubmit={invia} className={stili.modulo}>
      {modificabile && (
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>
            {c.tipo === "percentuale" ? "Percentuale" : c.tipo === "importo" ? "Sconto (€)" : "Crediti"}
          </span>
          <input className={comuni.ingresso} inputMode="decimal" value={valore} onChange={(e) => setValore(e.target.value)} />
        </label>
      )}
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Descrizione</span>
        <input className={comuni.ingresso} value={descrizione} maxLength={500} onChange={(e) => setDescrizione(e.target.value)} />
      </label>
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
      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Usi in tutto</span>
          <input className={comuni.ingresso} type="number" min={1} value={massimo} onChange={(e) => setMassimo(e.target.value)} placeholder="senza tetto" />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Usi a persona</span>
          <input className={comuni.ingresso} type="number" min={1} max={100} value={perUtente} onChange={(e) => setPerUtente(e.target.value)} />
        </label>
      </div>
      {c.tipo !== "crediti" && (
        <>
          <SceltaPiani piani={piani} scelti={scelti} cambia={setScelti} />
          <label className={stili.spunta}>
            <input type="checkbox" checked={primo} onChange={(e) => setPrimo(e.target.checked)} />
            Solo sul primo acquisto
          </label>
        </>
      )}
      {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
      <div className={stili.comandi}>
        <button className={comuni.primaria} type="submit" disabled={inCorso}>
          Salva
        </button>
        <button className={comuni.secondaria} type="button" onClick={chiudi} disabled={inCorso}>
          Annulla
        </button>
      </div>
    </form>
  );
}

function SceltaPiani({
  piani, scelti, cambia,
}: {
  piani: { slug: string; nome: string }[];
  scelti: string[];
  cambia: (v: string[]) => void;
}) {
  return (
    <fieldset className={stili.gruppo}>
      <legend className={comuni.campoEtichetta}>Vale per</legend>
      <div className={stili.sceltePiani}>
        {piani.map((p) => (
          <label key={p.slug} className={stili.spunta}>
            <input
              type="checkbox"
              checked={scelti.includes(p.slug)}
              onChange={(e) => cambia(e.target.checked ? [...scelti, p.slug] : scelti.filter((s) => s !== p.slug))}
            />
            {p.nome}
          </label>
        ))}
      </div>
      <span className={comuni.campoAiuto}>Nessuna spunta: tutte le offerte.</span>
    </fieldset>
  );
}

function NuovoCouponForm({
  piani, chiudi, creato,
}: {
  piani: { slug: string; nome: string }[];
  chiudi: () => void;
  creato: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [tipo, setTipo] = useState<TipoCoupon>("percentuale");
  const [codice, setCodice] = useState("");
  const [descrizione, setDescrizione] = useState("");
  const [valore, setValore] = useState("");
  const [scelti, setScelti] = useState<string[]>([]);
  const [primo, setPrimo] = useState(false);
  const [dal, setDal] = useState("");
  const [fino, setFino] = useState("");
  const [massimo, setMassimo] = useState("");
  const [perUtente, setPerUtente] = useState("1");
  const [problema, setProblema] = useState<string | null>(null);
  const [nuovoCodice, setNuovoCodice] = useState<string | null>(null);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    const v = tipo === "importo" ? centesimiDa(valore) : Number(valore);
    if (v === null || !Number.isFinite(v) || v < 1) return setProblema("Il valore non è valido.");
    if (tipo === "percentuale" && (v > 100 || !Number.isInteger(v))) return setProblema("Una percentuale è un intero da 1 a 100.");
    if (tipo === "crediti" && !Number.isInteger(v)) return setProblema("I crediti sono un intero.");
    const corpo: NuovoCoupon = { tipo, valore: v, max_per_utente: Number(perUtente) || 1 };
    if (codice.trim()) corpo.code = codice.trim();
    if (descrizione.trim()) corpo.description = descrizione.trim();
    if (tipo !== "crediti") {
      corpo.piani = scelti;
      corpo.solo_primo_acquisto = primo;
    }
    if (dal) corpo.valido_dal = inizioGiorno(dal);
    if (fino) corpo.valido_fino = fineGiorno(fino);
    if (massimo.trim() !== "") corpo.max_riscatti = Number(massimo);
    const fatto = await esegui((t) => creaCoupon(t, corpo));
    if (fatto) {
      setNuovoCodice(fatto.codice);
      creato();
    }
  };

  return (
    <section className={comuni.riquadro} aria-labelledby="nuovo-coupon">
      <h2 id="nuovo-coupon" className={comuni.riquadroTitolo}>
        Nuovo coupon
      </h2>
      <form onSubmit={invia} className={stili.modulo}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Che cos&apos;è</span>
          <select className={comuni.selezione} value={tipo} onChange={(e) => setTipo(e.target.value as TipoCoupon)}>
            {(Object.keys(TIPI) as TipoCoupon[]).map((t) => (
              <option key={t} value={t}>
                {TIPI[t].nome}
              </option>
            ))}
          </select>
          <span className={comuni.campoAiuto}>{TIPI[tipo].aiuto}</span>
        </label>
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>
              {tipo === "percentuale" ? "Sconto (%)" : tipo === "importo" ? "Sconto (€)" : "Crediti"}
            </span>
            <input
              className={comuni.ingresso}
              inputMode="decimal"
              value={valore}
              required
              onChange={(e) => setValore(e.target.value)}
              placeholder={tipo === "percentuale" ? "20" : tipo === "importo" ? "5,00" : "10"}
            />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Codice</span>
            <input
              className={comuni.ingresso}
              value={codice}
              maxLength={40}
              onChange={(e) => setCodice(e.target.value.toUpperCase())}
              placeholder="vuoto: lo scelgo io"
            />
            <span className={comuni.campoAiuto}>Maiuscole, cifre e trattini. Vuoto: 8 caratteri casuali leggibili.</span>
          </label>
        </div>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Descrizione (solo per te)</span>
          <input className={comuni.ingresso} value={descrizione} maxLength={500} onChange={(e) => setDescrizione(e.target.value)} placeholder="es. Newsletter di ottobre" />
        </label>
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
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Usi in tutto</span>
            <input className={comuni.ingresso} type="number" min={1} value={massimo} onChange={(e) => setMassimo(e.target.value)} placeholder="senza tetto" />
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Usi a persona</span>
            <input className={comuni.ingresso} type="number" min={1} max={100} value={perUtente} onChange={(e) => setPerUtente(e.target.value)} />
          </label>
        </div>
        {tipo !== "crediti" && (
          <>
            <SceltaPiani piani={piani} scelti={scelti} cambia={setScelti} />
            <label className={stili.spunta}>
              <input type="checkbox" checked={primo} onChange={(e) => setPrimo(e.target.checked)} />
              Solo sul primo acquisto
            </label>
          </>
        )}
        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {nuovoCodice && <p className={comuni.esito}>Creato: {nuovoCodice}</p>}
        <div className={stili.comandi}>
          <button className={comuni.primaria} type="submit" disabled={inCorso}>
            Crea il coupon
          </button>
          <button className={comuni.secondaria} type="button" onClick={chiudi} disabled={inCorso}>
            Annulla
          </button>
        </div>
      </form>
    </section>
  );
}
