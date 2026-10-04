"use client";

import { useState } from "react";
import { catalogo } from "@/lib/api";
import { centesimiDa, importoPerCampo, quandoCompleto, soldi } from "@/lib/formato";
import {
  coupons, creaCoupon, durataCoupon, eliminaCoupon, modificaCoupon, riscattiDi, valoreCoupon,
  type Coupon, type ModificaCoupon, type NuovoCoupon, type Riscatto, type TipoCoupon,
} from "@/lib/offerte";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./coupon.module.css";
import { CifreResoconto, Copia, fineGiorno, inizioGiorno, validita } from "./pezzi";
import { CampiRegole, CampoCampagna, SceltaPiani, regoleDaInviare, type Regole } from "./regole";

/* Coupon di sconto e codici regalo (la scheda «Coupon»; i lotti e le campagne hanno la loro).
 *
 * **Sconto** (percentuale o importo fisso): si applica al pagamento. Su un abbonamento vale sul primo pagamento, sui
 * primi N o per sempre (Fase 2d), e si somma o no allo sconto del rinnovo automatico e della prova: non cumulabile
 * (di default) vale il più alto per l'utente. Un abbonamento non si azzera, un pacchetto sì (a zero i crediti arrivano
 * subito, senza pagare). **Codice regalo** (crediti): chi lo riscatta dal profilo riceve crediti senza pagare.
 *
 * Ogni coupon ha il suo link (`/pricing?coupon=CODICE`, `/it/piano?coupon=CODICE`): applica il codice da solo e lo
 * conserva fino al pagamento, anche dopo la registrazione. Un coupon già usato non si elimina né cambia valore,
 * durata o cumulo — i conti passati devono restare leggibili —: si disattiva.
 */

const TIPI: Record<TipoCoupon, { nome: string; aiuto: string }> = {
  percentuale: { nome: "Sconto in percentuale", aiuto: "Da 1 a 100, sul listino." },
  importo: { nome: "Sconto di un importo", aiuto: "In euro. Non scende sotto zero." },
  crediti: { nome: "Codice regalo in crediti", aiuto: "Chi lo riscatta riceve questi crediti, senza pagare." },
};

const perCampo = (iso: string | null) => {
  if (!iso) return "";
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

/* I coupon singoli con le loro cifre (fuori dal componente: un'identità stabile, o `useDati` ricaricherebbe sempre). */
const couponSingoli = (t: string) => coupons(t);

export default function PaginaCoupon() {
  const elenco = useDati(couponSingoli);
  const piani = useDati(catalogo);
  const [nuovo, setNuovo] = useState(false);
  const scelte = (piani.dati ?? []).map((p) => ({ slug: p.slug, nome: p.nome }));
  const campagne = [...new Set((elenco.dati ?? []).map((c) => c.campagna).filter((c): c is string => !!c))].sort();

  return (
    <>
      <div className={stili.comandi} style={{ marginBottom: "1.25rem" }}>
        <button className={comuni.primaria} type="button" aria-expanded={nuovo} onClick={() => setNuovo(!nuovo)}>
          {nuovo ? "Chiudi" : "Nuovo coupon"}
        </button>
      </div>

      {nuovo && (
        <NuovoCouponForm
          piani={scelte}
          campagne={campagne}
          chiudi={() => setNuovo(false)}
          creato={() => elenco.ricarica()}
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
            <Voce key={c.id} coupon={c} piani={scelte} campagne={campagne} ricarica={elenco.ricarica} />
          ))}
        </ul>
      )}
    </>
  );
}

function Voce({
  coupon: c, piani, campagne, ricarica,
}: {
  coupon: Coupon;
  piani: { slug: string; nome: string }[];
  campagne: string[];
  ricarica: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [modifica, setModifica] = useState(false);
  const [usi, setUsi] = useState<Riscatto[] | null>(null);
  const [conferma, setConferma] = useState(false);

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

  const nomiPiani = c.piani.map((s) => piani.find((p) => p.slug === s)?.nome ?? s);

  return (
    <li className={c.attivo ? stili.voce : stili.voceSpenta}>
      <div className={stili.testata}>
        <div>
          <strong className={stili.codice}>{c.codice}</strong>
          <div className={comuni.mono}>{TIPI[c.tipo].nome}</div>
        </div>
        <div className={stili.valore}>{valoreCoupon(c, (n) => soldi(n))}</div>
      </div>
      <div className={stili.comandi}>
        <Copia testo={c.codice} etichetta="Copia il codice" descrizione={`Copia il codice ${c.codice}`} />
        {c.link && (
          <>
            <Copia testo={c.link.en} etichetta="Copia link" descrizione={`Copia il link che applica ${c.codice} (inglese)`} />
            <Copia testo={c.link.it} etichetta="Link /it" descrizione={`Copia il link che applica ${c.codice} (italiano)`} />
          </>
        )}
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
            <dt>Abbonamenti</dt>
            <dd>{durataCoupon(c)}</dd>
            <dt>Cumulo</dt>
            <dd>{c.cumulabile ? "si somma a rinnovo e prova" : "non cumulabile: vale il più alto"}</dd>
            {c.solo_primo_acquisto && (
              <>
                <dt>Condizione</dt>
                <dd>solo sul primo acquisto</dd>
              </>
            )}
          </>
        )}
        {c.campagna && (
          <>
            <dt>Campagna</dt>
            <dd>{c.campagna}</dd>
          </>
        )}
        <dt>Stato</dt>
        <dd className={c.attivo ? comuni.positivo : comuni.spento}>{c.attivo ? "attivo" : "disattivato"}</dd>
      </dl>
      {c.resoconto && c.resoconto.riscatti + c.resoconto.rinnovi_scontati > 0 && <CifreResoconto r={c.resoconto} />}

      {modifica ? (
        <ModuloModifica
          coupon={c}
          piani={piani}
          campagne={campagne}
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
                  <span>{u.email}{u.rinnovo ? " · rinnovo" : ""}</span>
                  <span>{u.crediti ? `${u.crediti} crediti` : `−${soldi(u.sconto)} · pagato ${soldi(u.importo)}`}</span>
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

/* Ciò che si può cambiare di un coupon: le regole d'uso e la campagna. Il tipo e — dopo il primo uso — valore, durata
 * e cumulo restano com'erano. */
function ModuloModifica({
  coupon: c, piani, campagne, chiudi, salvato,
}: {
  coupon: Coupon;
  piani: { slug: string; nome: string }[];
  campagne: string[];
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
  const [campagna, setCampagna] = useState(c.campagna ?? "");
  const [regole, setRegole] = useState<Regole>({ durata: c.durata, periodi: String(c.periodi ?? 3), cumulabile: c.cumulabile });
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
      campagna: campagna.trim() || null,
    };
    corpo.max_riscatti = massimo.trim() === "" ? null : Number(massimo);        // vuoto: senza tetto
    if (c.tipo !== "crediti") {
      corpo.piani = scelti;
      corpo.solo_primo_acquisto = primo;
      if (modificabile) {
        const r = regoleDaInviare(regole);
        if (!r) return setProblema("«Per N pagamenti» vuole un numero da 2 a 36.");
        Object.assign(corpo, r);
      }
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
      <CampoCampagna valore={campagna} cambia={setCampagna} suggerite={campagne} />
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
          <CampiRegole regole={regole} cambia={setRegole} bloccate={!modificabile} />
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

function NuovoCouponForm({
  piani, campagne, chiudi, creato,
}: {
  piani: { slug: string; nome: string }[];
  campagne: string[];
  chiudi: () => void;
  creato: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [tipo, setTipo] = useState<TipoCoupon>("percentuale");
  const [codice, setCodice] = useState("");
  const [descrizione, setDescrizione] = useState("");
  const [campagna, setCampagna] = useState("");
  const [valore, setValore] = useState("");
  const [scelti, setScelti] = useState<string[]>([]);
  const [primo, setPrimo] = useState(false);
  const [dal, setDal] = useState("");
  const [fino, setFino] = useState("");
  const [massimo, setMassimo] = useState("");
  const [perUtente, setPerUtente] = useState("1");
  const [regole, setRegole] = useState<Regole>({ durata: "una_volta", periodi: "3", cumulabile: false });
  const [problema, setProblema] = useState<string | null>(null);
  const [nuovo, setNuovo] = useState<Coupon | null>(null);

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
    if (campagna.trim()) corpo.campagna = campagna.trim();
    if (tipo !== "crediti") {
      corpo.piani = scelti;
      corpo.solo_primo_acquisto = primo;
      const r = regoleDaInviare(regole);
      if (!r) return setProblema("«Per N pagamenti» vuole un numero da 2 a 36.");
      Object.assign(corpo, r);
    }
    if (dal) corpo.valido_dal = inizioGiorno(dal);
    if (fino) corpo.valido_fino = fineGiorno(fino);
    if (massimo.trim() !== "") corpo.max_riscatti = Number(massimo);
    const fatto = await esegui((t) => creaCoupon(t, corpo));
    if (fatto) {
      setNuovo(fatto);
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
              autoCapitalize="characters"
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
        <CampoCampagna valore={campagna} cambia={setCampagna} suggerite={campagne} />
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
            <CampiRegole regole={regole} cambia={setRegole} />
            <label className={stili.spunta}>
              <input type="checkbox" checked={primo} onChange={(e) => setPrimo(e.target.checked)} />
              Solo sul primo acquisto
            </label>
          </>
        )}
        {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
        {nuovo && (
          <div className={comuni.esito} role="status">
            Creato: <strong>{nuovo.codice}</strong>{" "}
            {nuovo.link && <Copia testo={nuovo.link.en} etichetta="Copia link" descrizione={`Copia il link che applica ${nuovo.codice}`} />}
          </div>
        )}
        <div className={stili.comandi}>
          <button className={comuni.primaria} type="submit" disabled={inCorso}>
            Crea il coupon
          </button>
          <button className={comuni.secondaria} type="button" onClick={chiudi} disabled={inCorso}>
            Chiudi
          </button>
        </div>
      </form>
    </section>
  );
}
