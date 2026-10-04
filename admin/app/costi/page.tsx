"use client";

/* Costi delle inferenze. Ogni chiamata a un modello lascia una riga nel registro dei consumi (compito, token in
 * ingresso, in cache, in uscita e di ragionamento): qui si vedono per compito, per giorno e per lettura, e si
 * traducono in dollari con un listino a scelta. I listini — il fornitore in uso e quelli che si valutano — si
 * scrivono in fondo alla pagina. */

import { useMemo, useState } from "react";
import {
  costi, creaListino, eliminaListino, modificaListino, nomeFase,
  type Costi, type Listino, type NuovoListino, type RigaLetture,
} from "@/lib/costi";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./costi.module.css";

const PERIODI = [7, 14, 30, 90];

const intero = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 0 });

function token(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toLocaleString("it-IT", { maximumFractionDigits: 2 })} M`;
  if (n >= 10_000) return `${(n / 1000).toLocaleString("it-IT", { maximumFractionDigits: 1 })} k`;
  return intero.format(Math.round(n));
}

function dollari(n: number | undefined): string {
  if (n == null) return "—";
  if (n === 0) return "$0";
  if (n < 0.01) return `$${n.toLocaleString("en-US", { maximumSignificantDigits: 2 })}`;
  return `$${n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function percento(parte: number, totale: number): string {
  return totale > 0 ? `${Math.round((parte / totale) * 100)}%` : "—";
}

export default function PaginaCosti() {
  const [giorni, setGiorni] = useState(14);
  const [scelto, setScelto] = useState<string | null>(null);
  const dati = useDati((t) => costi(t, giorni), [giorni]);
  const d = dati.dati;
  const listino = scelto ?? d?.listini[0]?.nome ?? "";

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Costi</h1>
          <p className={comuni.sottotitolo}>
            Quanti token consuma ogni chiamata ai modelli — il ragionamento conta come uscita — e quanto costa con
            ciascun listino. La cache di un listino in valutazione vale solo per la parte stabile del prompt.
          </p>
        </div>
      </div>

      <div className={comuni.filtri} role="group" aria-label="Periodo">
        {PERIODI.map((g) => (
          <button key={g} type="button" className={g === giorni ? comuni.filtroScelto : comuni.filtro}
            aria-pressed={g === giorni} onClick={() => setGiorni(g)}>
            Ultimi {g} giorni
          </button>
        ))}
      </div>
      {d && d.listini.length > 0 && (
        <div className={comuni.filtri} role="group" aria-label="Listino">
          {d.listini.map((l) => (
            <button key={l.id} type="button" className={l.nome === listino ? comuni.filtroScelto : comuni.filtro}
              aria-pressed={l.nome === listino} onClick={() => setScelto(l.nome)}>
              {l.nome}{l.attuale ? " · in uso" : ""}
            </button>
          ))}
        </div>
      )}

      {dati.errore && <p className={comuni.errore} role="alert">{dati.errore}</p>}
      {!d && dati.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}

      {d && (
        <div className={dati.inCorso ? comuni.inRicarica : undefined}>
          {d.totali.chiamate === 0 ? (
            <div className={comuni.vuoto}>
              Nessuna chiamata registrata negli ultimi {d.giorni} giorni. Il registro parte con questa versione: le
              letture di prima non ci sono.
            </div>
          ) : (
            <Riepilogo d={d} listino={listino} />
          )}
          <Listini listini={d.listini} onCambiati={dati.ricarica} />
        </div>
      )}
    </>
  );
}

function Riepilogo({ d, listino }: { d: Costi; listino: string }) {
  const letture = Object.fromEntries(d.letture.map((r) => [r.stato, r])) as Partial<Record<RigaLetture["stato"], RigaLetture>>;
  const t = d.totali;
  const perGiorno = useMemo(() => {
    const somme = new Map<string, { chiamate: number; ingresso: number; uscita: number; ragionamento: number; costo: number }>();
    for (const r of d.per_giorno) {
      const s = somme.get(r.giorno) ?? { chiamate: 0, ingresso: 0, uscita: 0, ragionamento: 0, costo: 0 };
      s.chiamate += r.chiamate; s.ingresso += r.ingresso; s.uscita += r.uscita; s.ragionamento += r.ragionamento;
      s.costo += r.costi[listino] ?? 0;
      somme.set(r.giorno, s);
    }
    return [...somme.entries()].sort(([a], [b]) => b.localeCompare(a));
  }, [d.per_giorno, listino]);
  const massimo = Math.max(...d.per_compito.map((r) => r.costi[listino] ?? 0), 0);

  return (
    <>
      <div className={stili.schede}>
        <Scheda etichetta={`Costo del periodo (${listino})`} valore={dollari(t.costi[listino])}
          nota={`${intero.format(t.chiamate)} chiamate${t.errori ? `, ${t.errori} non riuscite` : ""}`} />
        <Scheda etichetta="Per lettura completata" valore={dollari(letture.completata?.costi_per_lettura[listino])}
          nota={letture.completata ? `${letture.completata.letture} letture, ${token(letture.completata.per_lettura.ingresso)} token in ingresso e ${token(letture.completata.per_lettura.uscita)} in uscita a lettura` : "nessuna nel periodo"} />
        <Scheda etichetta="Per lettura abbandonata" valore={dollari(letture.abbandonata?.costi_per_lettura[listino])}
          nota={letture.abbandonata ? `${letture.abbandonata.letture} letture ferme a metà (comprese quelle ancora in corso)` : "nessuna nel periodo"} />
        <Scheda etichetta="Ragionamento sull'uscita" valore={percento(t.ragionamento, t.uscita)}
          nota={`${token(t.ragionamento)} token di ragionamento su ${token(t.uscita)} in uscita`} />
        <Scheda etichetta="Ingresso in cache" valore={percento(t.cache, t.ingresso)}
          nota={`Riportato dal fornitore. Cacheabile (prefisso stabile): ${percento(t.cacheabile, t.ingresso)}`} />
      </div>
      {t.stimate > 0 && (
        <p className={comuni.campoAiuto}>
          {t.stimate} chiamate senza consumo riportato dal fornitore: i loro token sono stimati dai caratteri
          ({d.caratteri_per_token} per token).
        </p>
      )}

      <section className={stili.sezione} aria-labelledby="titolo-compiti">
        <h2 id="titolo-compiti" className={comuni.riquadroTitolo}>Per compito</h2>
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th scope="col">Compito</th>
                <th scope="col" className={comuni.numero}>Chiamate</th>
                <th scope="col" className={comuni.numero}>Ingresso</th>
                <th scope="col" className={comuni.numero}>Uscita</th>
                <th scope="col" className={comuni.numero}>di cui ragion.</th>
                <th scope="col" className={comuni.numero}>Costo</th>
              </tr>
            </thead>
            <tbody>
              {d.per_compito.map((r) => (
                <tr key={`${r.compito}/${r.fase}`}>
                  <td>
                    {nomeFase(r.compito, r.fase)}
                    {r.errori > 0 && <span className={`${comuni.stato} ${comuni.negativo}`} style={{ marginLeft: ".4rem" }}>{r.errori} non riuscite</span>}
                    <span className={stili.barra} aria-hidden="true">
                      <span className={stili.barraPiena} style={{ width: `${massimo ? ((r.costi[listino] ?? 0) / massimo) * 100 : 0}%` }} />
                    </span>
                  </td>
                  <td className={comuni.numero}>{intero.format(r.chiamate)}</td>
                  <td className={comuni.numero}>{token(r.ingresso)}</td>
                  <td className={comuni.numero}>{token(r.uscita)}</td>
                  <td className={comuni.numero}>{token(r.ragionamento)}</td>
                  <td className={comuni.numero}>{dollari(r.costi[listino])}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className={stili.sezione} aria-labelledby="titolo-letture">
        <h2 id="titolo-letture" className={comuni.riquadroTitolo}>Per lettura</h2>
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th scope="col">Letture</th>
                <th scope="col" className={comuni.numero}>Quante</th>
                <th scope="col" className={comuni.numero}>Chiamate a lettura</th>
                <th scope="col" className={comuni.numero}>Token a lettura</th>
                <th scope="col" className={comuni.numero}>Costo a lettura</th>
                <th scope="col" className={comuni.numero}>Per 1000</th>
              </tr>
            </thead>
            <tbody>
              {d.letture.map((r) => (
                <tr key={r.stato}>
                  <td>{{ completata: "Completate", abbandonata: "Abbandonate o in corso", annullata: "Fermate per crisi", cancellata: "Cancellate" }[r.stato]}</td>
                  <td className={comuni.numero}>{r.letture}</td>
                  <td className={comuni.numero}>{r.per_lettura.chiamate.toLocaleString("it-IT")}</td>
                  <td className={comuni.numero}>{token(r.per_lettura.ingresso)} + {token(r.per_lettura.uscita)}</td>
                  <td className={comuni.numero}>{dollari(r.costi_per_lettura[listino])}</td>
                  <td className={comuni.numero}>{dollari((r.costi_per_lettura[listino] ?? 0) * 1000)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {d.fuori_lettura.length > 0 && (
          <p className={comuni.campoAiuto}>
            Fuori dalle letture:{" "}
            {d.fuori_lettura.map((r) => `${nomeFase(r.compito, r.compito)} ${intero.format(r.chiamate)} chiamate, ${dollari(r.costi[listino])}`).join(" · ")}
          </p>
        )}
      </section>

      <section className={stili.sezione} aria-labelledby="titolo-giorni">
        <h2 id="titolo-giorni" className={comuni.riquadroTitolo}>Per giorno</h2>
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th scope="col">Giorno (UTC)</th>
                <th scope="col" className={comuni.numero}>Chiamate</th>
                <th scope="col" className={comuni.numero}>Ingresso</th>
                <th scope="col" className={comuni.numero}>Uscita</th>
                <th scope="col" className={comuni.numero}>Costo</th>
              </tr>
            </thead>
            <tbody>
              {perGiorno.map(([g, s]) => (
                <tr key={g}>
                  <td className={comuni.mono}>{g}</td>
                  <td className={comuni.numero}>{intero.format(s.chiamate)}</td>
                  <td className={comuni.numero}>{token(s.ingresso)}</td>
                  <td className={comuni.numero}>{token(s.uscita)} <span className={comuni.campoAiuto}>({percento(s.ragionamento, s.uscita)} ragion.)</span></td>
                  <td className={comuni.numero}>{dollari(s.costo)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function Scheda({ etichetta, valore, nota }: { etichetta: string; valore: string; nota?: string }) {
  return (
    <div className={stili.scheda}>
      <p className={stili.schedaEtichetta}>{etichetta}</p>
      <p className={stili.schedaValore}>{valore}</p>
      {nota && <p className={stili.schedaNota}>{nota}</p>}
    </div>
  );
}

const VUOTO: NuovoListino = {
  nome: "", prezzo_ingresso: 0, prezzo_cache: 0, prezzo_uscita: 0, cache_hit: 0, attuale: false, nota: "",
};

/* I listini: un modulo per ciascuno, più uno vuoto per aggiungerne. I prezzi in dollari per milione di token; la
 * cache in percento (si salva fra 0 e 1). */
function Listini({ listini, onCambiati }: { listini: Listino[]; onCambiati: () => void }) {
  const [nuovo, setNuovo] = useState(false);
  return (
    <section className={stili.sezione} aria-labelledby="titolo-listini">
      <div className={comuni.riga} style={{ justifyContent: "space-between", flexWrap: "wrap" }}>
        <h2 id="titolo-listini" className={comuni.riquadroTitolo}>Listini</h2>
        {!nuovo && <button type="button" className={comuni.secondaria} onClick={() => setNuovo(true)}>Aggiungi un listino</button>}
      </div>
      <p className={comuni.campoAiuto}>
        Dollari per milione di token. «Cache hit» è la quota della parte stabile del prompt che si stima trovata in
        cache; per il listino in uso vale invece la cache riportata dal fornitore.
      </p>
      <ul className={stili.listini}>
        {nuovo && (
          <li className={comuni.riquadro}>
            <ModuloListino iniziale={VUOTO} onFatto={() => { setNuovo(false); onCambiati(); }} onAnnulla={() => setNuovo(false)} />
          </li>
        )}
        {listini.map((l) => (
          <li key={l.id} className={comuni.riquadro}>
            <ModuloListino iniziale={l} id={l.id} onFatto={onCambiati} />
          </li>
        ))}
      </ul>
    </section>
  );
}

function ModuloListino({ iniziale, id, onFatto, onAnnulla }: {
  iniziale: NuovoListino; id?: number; onFatto: () => void; onAnnulla?: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [v, setV] = useState({
    nome: iniziale.nome, ingresso: String(iniziale.prezzo_ingresso), cache: String(iniziale.prezzo_cache),
    uscita: String(iniziale.prezzo_uscita), hit: String(Math.round(iniziale.cache_hit * 100)),
    attuale: iniziale.attuale, nota: iniziale.nota,
  });
  const [salvato, setSalvato] = useState(false);
  const numero = (s: string) => Number(s.replace(",", "."));
  const valido = v.nome.trim() !== "" && [v.ingresso, v.cache, v.uscita, v.hit].every((s) => s.trim() !== "" && Number.isFinite(numero(s)) && numero(s) >= 0)
    && numero(v.hit) <= 100;

  const salva = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valido) return;
    const corpo: NuovoListino = {
      nome: v.nome.trim(), prezzo_ingresso: numero(v.ingresso), prezzo_cache: numero(v.cache),
      prezzo_uscita: numero(v.uscita), cache_hit: numero(v.hit) / 100, attuale: v.attuale, nota: v.nota.trim(),
    };
    const r = await esegui((t) => (id == null ? creaListino(t, corpo) : modificaListino(t, id, corpo)));
    if (r) { setSalvato(true); onFatto(); }
  };

  const elimina = async () => {
    if (id == null || !window.confirm(`Eliminare il listino «${iniziale.nome}»?`)) return;
    if ((await esegui((t) => eliminaListino(t, id))) !== null) onFatto();
  };

  const campo = (chiave: "ingresso" | "cache" | "uscita" | "hit", etichetta: string) => (
    <label className={comuni.campo}>
      <span className={comuni.campoEtichetta}>{etichetta}</span>
      <input className={comuni.ingresso} inputMode="decimal" value={v[chiave]}
        onChange={(e) => { setSalvato(false); setV({ ...v, [chiave]: e.target.value }); }} />
    </label>
  );

  return (
    <form onSubmit={salva}>
      <div className={stili.moduloListino}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Nome</span>
          <input className={comuni.ingresso} value={v.nome} maxLength={60}
            onChange={(e) => { setSalvato(false); setV({ ...v, nome: e.target.value }); }} />
        </label>
        {campo("ingresso", "Ingresso $/M")}
        {campo("cache", "In cache $/M")}
        {campo("uscita", "Uscita $/M")}
        {campo("hit", "Cache hit %")}
      </div>
      <label className={comuni.campo} style={{ marginTop: ".75rem" }}>
        <span className={comuni.campoEtichetta}>Nota</span>
        <input className={comuni.ingresso} value={v.nota} maxLength={300}
          onChange={(e) => { setSalvato(false); setV({ ...v, nota: e.target.value }); }} />
      </label>
      <label className={comuni.campo} style={{ flexDirection: "row", alignItems: "center", gap: ".5rem", marginTop: ".75rem", minHeight: 44 }}>
        <input type="checkbox" checked={v.attuale} onChange={(e) => { setSalvato(false); setV({ ...v, attuale: e.target.checked }); }} />
        <span>Fornitore in uso</span>
      </label>
      <div className={stili.azioni}>
        <button className={comuni.primaria} type="submit" disabled={inCorso || !valido}>
          {id == null ? "Aggiungi" : "Salva"}
        </button>
        {onAnnulla && <button type="button" className={comuni.secondaria} onClick={onAnnulla}>Annulla</button>}
        {id != null && <button type="button" className={comuni.distruttiva} onClick={elimina} disabled={inCorso}>Elimina</button>}
        {salvato && !errore && <span className={comuni.esito} role="status">Salvato.</span>}
      </div>
      {errore && <p className={comuni.errore} role="alert">{errore}</p>}
    </form>
  );
}
