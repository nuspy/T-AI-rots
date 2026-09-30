"use client";

/* Vota il prossimo mazzo (v7, Fase K) e le sue estensioni "tornate elettorali": una riserva di
 * proposte (con le loro carte di prova) da cui si scelgono i candidati quando si apre una nuova
 * tornata, con una scadenza dichiarata — la tornata si chiude da sola quando passa, nessun
 * pulsante da premere. Suggerimenti degli iscritti in coda di revisione, e la possibilità di
 * generare il mazzo reale di un candidato anche se non ha vinto. */

import { useState } from "react";
import {
  accettaVincitori, candidatiDiTornata, caricaCampione, chiudiTornata, creaProposta, creaTornata,
  eliminaCandidato, generaMazzoDaCandidato, modificaCandidato, proposteDisponibili,
  scartaSuggerimento, suggerimenti as leggiSuggerimenti, tornate as leggiTornate,
  trasformaSuggerimento,
  type Candidato, type Suggerimento, type Tornata,
} from "@/lib/voto";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";

export default function VotoMazzi() {
  const { dati: tornate, errore, inCorso, ricarica } = useDati(leggiTornate);
  const [selezionata, setSelezionata] = useState<string | null>(null);

  const tornataAperta = tornate?.find((r) => r.stato === "aperta") ?? null;
  const corrente = selezionata ?? tornataAperta?.id ?? tornate?.[0]?.id ?? null;

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Vota il prossimo mazzo</h1>
          <p className={comuni.sottotitolo}>
            Una riserva di proposte (con le loro carte di prova), le tornate che ne scelgono alcune
            con una scadenza dichiarata — si chiudono da sole, non serve un pulsante — e
            l'accettazione dei vincitori. Un mazzo reale si può generare per qualunque candidato,
            anche se non ha vinto.
          </p>
        </div>
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {inCorso && !tornate && <p className={comuni.caricamento}>Caricamento…</p>}

      <Suggerimenti onTrasformato={ricarica} />
      <Riserva onCambiata={ricarica} />

      <div className={comuni.riquadro}>
        <h2 className={comuni.riquadroTitolo}>Tornate</h2>
        {tornate && tornate.length > 0 && (
          <div className={comuni.contenitoreTabella}>
            <table className={comuni.tabella}>
              <thead>
                <tr><th>Aperta il</th><th>Stato</th><th>Scade il</th><th>Chiusa il</th><th></th></tr>
              </thead>
              <tbody>
                {tornate.map((r) => (
                  <tr key={r.id} className={r.id === corrente ? comuni.filtroScelto : undefined}>
                    <td>{new Date(r.aperta_il).toLocaleString("it-IT")}</td>
                    <td><span className={r.stato === "aperta" ? comuni.positivo : comuni.spento}>{r.stato}</span></td>
                    <td>{r.chiude_il ? new Date(r.chiude_il).toLocaleString("it-IT") : "—"}</td>
                    <td>{r.chiusa_il ? new Date(r.chiusa_il).toLocaleString("it-IT") : "—"}</td>
                    <td>
                      <button type="button" className={comuni.secondaria} onClick={() => setSelezionata(r.id)}>Apri</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {corrente && <Candidati roundId={corrente} tornata={tornate?.find((r) => r.id === corrente) ?? null} onCambioTornate={ricarica} />}
    </>
  );
}

/* ---- suggerimenti degli iscritti ------------------------------------------------------------------ */

function Suggerimenti({ onTrasformato }: { onTrasformato: () => void }) {
  const { dati, errore, inCorso, ricarica } = useDati(leggiSuggerimenti);
  const { esegui, inCorso: inAzione, errore: erroreAzione } = useAzione();

  const trasforma = async (s: Suggerimento) => {
    if ((await esegui((t) => trasformaSuggerimento(t, s.id))) !== null) { ricarica(); onTrasformato(); }
  };

  const scarta = async (s: Suggerimento) => {
    if ((await esegui((t) => scartaSuggerimento(t, s.id))) !== null) ricarica();
  };

  if (!inCorso && dati && dati.length === 0) return null;

  return (
    <div className={comuni.riquadro}>
      <h2 className={comuni.riquadroTitolo}>Suggerimenti degli iscritti</h2>
      <p className={comuni.riquadroNota}>
        Temi proposti liberamente dagli utenti registrati. Trasformarne uno lo aggiunge alla riserva
        di proposte, pronto per essere scelto in una tornata (nome e descrizione si rifiniscono lì).
      </p>
      {(errore || erroreAzione) && <p className={comuni.errore}>{errore ?? erroreAzione}</p>}
      {inCorso && !dati && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && dati.length > 0 && (
        <ul>
          {dati.map((s) => (
            <li key={s.id} className={comuni.riga} style={{ alignItems: "center" }}>
              <span style={{ flex: 1 }}>{s.testo}</span>
              <button type="button" className={comuni.primaria} disabled={inAzione} onClick={() => trasforma(s)}>
                Trasforma in proposta
              </button>
              <button type="button" className={comuni.distruttiva} disabled={inAzione} onClick={() => scarta(s)}>
                Scarta
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* ---- riserva di proposte + creazione della tornata ------------------------------------------------- */

function Riserva({ onCambiata }: { onCambiata: () => void }) {
  const { dati: proposte, errore, inCorso, ricarica } = useDati(proposteDisponibili);
  const { esegui, inCorso: inAzione, errore: erroreAzione } = useAzione();
  const [nome, setNome] = useState("");
  const [descrizione, setDescrizione] = useState("");
  const [selezionate, setSelezionate] = useState<Set<string>>(new Set());
  const [chiudeIl, setChiudeIl] = useState("");

  const aggiungi = async () => {
    if (!nome.trim()) return;
    const fatto = await esegui((t) => creaProposta(t, { nome: nome.trim(), descrizione: descrizione.trim() || undefined }));
    if (fatto) { setNome(""); setDescrizione(""); ricarica(); }
  };

  const elimina = async (id: string) => {
    if ((await esegui((t) => eliminaCandidato(t, id))) !== null) {
      setSelezionate((s) => { const n = new Set(s); n.delete(id); return n; });
      ricarica();
    }
  };

  const commuta = (id: string) => {
    setSelezionate((s) => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id); else n.add(id);
      return n;
    });
  };

  const apriTornata = async () => {
    if (selezionate.size === 0 || !chiudeIl) return;
    const fatta = await esegui((t) => creaTornata(t, [...selezionate], new Date(chiudeIl).toISOString()));
    if (fatta) { setSelezionate(new Set()); setChiudeIl(""); ricarica(); onCambiata(); }
  };

  return (
    <div className={comuni.riquadro}>
      <h2 className={comuni.riquadroTitolo}>Riserva di proposte</h2>
      <p className={comuni.riquadroNota}>
        Prepara qui le proposte (con le loro carte di prova) prima di aprire una tornata: seleziona
        quelle da mettere al voto e dichiara quando la votazione deve chiudersi.
      </p>
      {(errore || erroreAzione) && <p className={comuni.errore}>{errore ?? erroreAzione}</p>}
      {inCorso && !proposte && <p className={comuni.caricamento}>Caricamento…</p>}

      <div className={comuni.riga}>
        <div className={comuni.campo}>
          <label className={comuni.campoEtichetta}>Nome</label>
          <input className={comuni.ingresso} value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Nome del mazzo proposto" />
        </div>
        <div className={comuni.campo}>
          <label className={comuni.campoEtichetta}>Descrizione</label>
          <input className={comuni.ingresso} value={descrizione} onChange={(e) => setDescrizione(e.target.value)} placeholder="Facoltativa" />
        </div>
        <button type="button" className={comuni.primaria} disabled={inAzione || !nome.trim()} onClick={aggiungi}>
          Aggiungi alla riserva
        </button>
      </div>

      {proposte && proposte.length === 0 && <p className={comuni.vuoto}>Nessuna proposta in riserva.</p>}

      {proposte && proposte.length > 0 && (
        <>
          <div className={comuni.contenitoreTabella} style={{ marginTop: 14 }}>
            <table className={comuni.tabella}>
              <thead>
                <tr><th></th><th>Proposta</th><th></th></tr>
              </thead>
              <tbody>
                {proposte.map((p) => (
                  <RigaProposta
                    key={p.id} proposta={p} selezionata={selezionate.has(p.id)} bloccato={inAzione}
                    onCommuta={() => commuta(p.id)} onElimina={() => elimina(p.id)} onCambiata={ricarica}
                  />
                ))}
              </tbody>
            </table>
          </div>

          <div className={comuni.riga} style={{ marginTop: 14 }}>
            <div className={comuni.campo}>
              <label className={comuni.campoEtichetta}>La votazione chiude il</label>
              <input className={comuni.ingresso} type="datetime-local" value={chiudeIl} onChange={(e) => setChiudeIl(e.target.value)} />
            </div>
            <button type="button" className={comuni.primaria} disabled={inAzione || selezionate.size === 0 || !chiudeIl} onClick={apriTornata}>
              Apri tornata con {selezionate.size} selezionat{selezionate.size === 1 ? "a" : "e"}
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function RigaProposta({
  proposta, selezionata, bloccato, onCommuta, onElimina, onCambiata,
}: {
  proposta: Candidato; selezionata: boolean; bloccato: boolean;
  onCommuta: () => void; onElimina: () => void; onCambiata: () => void;
}) {
  return (
    <tr>
      <td><input type="checkbox" checked={selezionata} onChange={onCommuta} /></td>
      <td>
        <CorpoCandidato candidato={proposta} onCambiata={onCambiata} bloccato={bloccato} mostraGeneraMazzo />
      </td>
      <td>
        <button type="button" className={comuni.distruttiva} disabled={bloccato} onClick={onElimina}>Elimina</button>
      </td>
    </tr>
  );
}

/* ---- candidati di una tornata --------------------------------------------------------------------- */

function Candidati({
  roundId, tornata, onCambioTornate,
}: { roundId: string; tornata: Tornata | null; onCambioTornate: () => void }) {
  const { dati: candidati, errore, inCorso, ricarica } = useDati((t) => candidatiDiTornata(t, roundId), [roundId]);
  const { esegui, inCorso: inAzione, errore: erroreAzione } = useAzione();
  const [selezionati, setSelezionati] = useState<Set<string>>(new Set());
  const aperta = tornata?.stato === "aperta";

  const chiudi = async () => {
    if ((await esegui((t) => chiudiTornata(t, roundId))) !== null) { onCambioTornate(); ricarica(); }
  };

  const accetta = async () => {
    if (selezionati.size === 0) return;
    const fatto = await esegui((t) => accettaVincitori(t, roundId, [...selezionati]));
    if (fatto) { setSelezionati(new Set()); onCambioTornate(); ricarica(); }
  };

  const commuta = (id: string) => {
    setSelezionati((s) => {
      const nuovo = new Set(s);
      if (nuovo.has(id)) nuovo.delete(id); else nuovo.add(id);
      return nuovo;
    });
  };

  const totaleVoti = (candidati ?? []).reduce((s, c) => s + c.voti, 0);

  return (
    <div className={comuni.riquadro}>
      <h2 className={comuni.riquadroTitolo}>Candidati della tornata {totaleVoti > 0 && <span className={comuni.riquadroNota}>({totaleVoti} voti totali)</span>}</h2>
      {(errore || erroreAzione) && <p className={comuni.errore}>{errore ?? erroreAzione}</p>}
      {inCorso && !candidati && <p className={comuni.caricamento}>Caricamento…</p>}

      {candidati && candidati.length === 0 && <p className={comuni.vuoto}>Nessun candidato in questa tornata.</p>}

      {candidati && candidati.length > 0 && (
        <div className={comuni.contenitoreTabella} style={{ marginTop: 14 }}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th></th><th>Candidato</th><th>Voti</th><th>%</th><th>Accettato</th><th></th>
              </tr>
            </thead>
            <tbody>
              {candidati.map((c) => (
                <RigaCandidatoTornata
                  key={c.id} candidato={c} totaleVoti={totaleVoti} bloccato={inAzione}
                  selezionato={selezionati.has(c.id)} onCommuta={() => commuta(c.id)} onCambiato={ricarica}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className={comuni.riga} style={{ marginTop: 14 }}>
        {aperta && (
          <>
            <button type="button" className={comuni.primaria} disabled={inAzione || selezionati.size === 0} onClick={accetta}>
              Accetta selezionati ({selezionati.size})
            </button>
            <button type="button" className={comuni.secondaria} disabled={inAzione} onClick={chiudi}>
              Chiudi la tornata senza accettare
            </button>
          </>
        )}
      </div>
    </div>
  );
}

function RigaCandidatoTornata({
  candidato, totaleVoti, bloccato, selezionato, onCommuta, onCambiato,
}: {
  candidato: Candidato; totaleVoti: number; bloccato: boolean; selezionato: boolean;
  onCommuta: () => void; onCambiato: () => void;
}) {
  const percentuale = totaleVoti > 0 ? Math.round((100 * candidato.voti) / totaleVoti) : 0;
  return (
    <tr>
      <td><input type="checkbox" checked={selezionato} disabled={candidato.accettato} onChange={onCommuta} /></td>
      <td><CorpoCandidato candidato={candidato} onCambiata={onCambiato} bloccato={bloccato} mostraGeneraMazzo /></td>
      <td className={comuni.numero}>{candidato.voti}</td>
      <td className={comuni.numero}>{percentuale}%</td>
      <td>{candidato.accettato ? <span className={comuni.positivo}>sì</span> : <span className={comuni.spento}>no</span>}</td>
      <td />
    </tr>
  );
}

/* ---- il corpo comune a una proposta o a un candidato di tornata: nome, descrizione, carte di
 * prova, modifica, upload, e — quando richiesto — "genera mazzo" (vincitore o no). ---- */

function CorpoCandidato({
  candidato, onCambiata, bloccato, mostraGeneraMazzo,
}: { candidato: Candidato; onCambiata: () => void; bloccato: boolean; mostraGeneraMazzo: boolean }) {
  const { esegui, inCorso, errore } = useAzione();
  const [modificaAperta, setModificaAperta] = useState(false);
  const [nome, setNome] = useState(candidato.nome);
  const [descrizione, setDescrizione] = useState(candidato.descrizione ?? "");
  const [etichettaCampione, setEtichettaCampione] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [mazzoGenerato, setMazzoGenerato] = useState<{ slug: string } | null>(null);

  const salva = async () => {
    if (!nome.trim()) return;
    if ((await esegui((t) => modificaCandidato(t, candidato.id, { nome: nome.trim(), descrizione: descrizione.trim() || undefined }))) !== null) {
      setModificaAperta(false);
      onCambiata();
    }
  };

  const carica = async () => {
    if (!file || !etichettaCampione.trim()) return;
    if ((await esegui((t) => caricaCampione(t, candidato.id, etichettaCampione.trim(), file))) !== null) {
      setFile(null);
      setEtichettaCampione("");
      onCambiata();
    }
  };

  const genera = async () => {
    const fatto = await esegui((t) => generaMazzoDaCandidato(t, candidato.id));
    if (fatto) { setMazzoGenerato({ slug: fatto.slug }); onCambiata(); }
  };

  return (
    <div>
      <strong>{candidato.nome}</strong>
      {candidato.descrizione && <div className={comuni.riquadroNota}>{candidato.descrizione}</div>}
      {candidato.campioni.length > 0 && (
        <div className={comuni.riga} style={{ marginTop: 6 }}>
          {candidato.campioni.map((camp, i) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img key={i} src={camp.url} alt={camp.etichetta ?? ""} width={60} style={{ borderRadius: 6 }} />
          ))}
        </div>
      )}
      {errore && <p className={comuni.errore}>{errore}</p>}
      <div className={comuni.riga} style={{ marginTop: 8 }}>
        <button type="button" className={comuni.secondaria} disabled={bloccato} onClick={() => setModificaAperta((a) => !a)}>
          Modifica
        </button>
        {mostraGeneraMazzo && (
          candidato.deck_id ? (
            <span className={comuni.positivo}>Mazzo generato (id {candidato.deck_id})</span>
          ) : (
            <button type="button" className={comuni.secondaria} disabled={bloccato || inCorso} onClick={genera}>
              Genera mazzo
            </button>
          )
        )}
      </div>
      {mazzoGenerato && (
        <p className={comuni.riquadroNota}>
          Creato con slug <code>{mazzoGenerato.slug}</code>: completalo con la pipeline
          <code> crea-mazzo-tarocchi</code> e attivalo dalla pagina Mazzi quando è pronto.
        </p>
      )}
      {modificaAperta && (
        <div style={{ marginTop: 10 }}>
          <div className={comuni.riga}>
            <input className={comuni.ingresso} value={nome} onChange={(e) => setNome(e.target.value)} />
            <input className={comuni.ingresso} value={descrizione} onChange={(e) => setDescrizione(e.target.value)} placeholder="Descrizione" />
            <button type="button" className={comuni.primaria} disabled={inCorso || !nome.trim()} onClick={salva}>Salva</button>
          </div>
          <div className={comuni.riga} style={{ marginTop: 8 }}>
            <input className={comuni.ingresso} value={etichettaCampione} onChange={(e) => setEtichettaCampione(e.target.value)}
              placeholder="Etichetta della carta di prova (es. maj-06)" />
            <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            <button type="button" className={comuni.secondaria} disabled={inCorso || !file || !etichettaCampione.trim()} onClick={carica}>
              Carica carta di prova
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
