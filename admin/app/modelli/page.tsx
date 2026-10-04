"use client";

import { useState } from "react";
import {
  aggiornaCompito,
  assegnaModello,
  LIVELLI_RAGIONAMENTO,
  modelliECompiti,
  nomeLivello,
  type CompitoAssegnato,
  type LivelloRagionamento,
  type ModelloConfigurato,
  type ModificaCompito,
} from "@/lib/api";
import {
  creaFornitore, eliminaFornitore, fornitori, modificaFornitore, provaFornitore,
  type EsitoProva, type Fornitore, type ModificaFornitore, type NuovoFornitore, type TipoFornitore,
} from "@/lib/fornitori";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import stili from "./modelli.module.css";

/* Chi serve quale compito, e i fornitori fra cui scegliere.
 *
 * I fornitori si configurano qui: indirizzo, modello e chiave. La chiave non torna mai in chiaro — un fornitore
 * la porta solo per rispondere «ce l'ho» o «non ce l'ho» — e appena se ne aggiunge, modifica o elimina uno, il
 * servizio lo rilegge subito: nessun riavvio, nessuna variabile d'ambiente da toccare.
 *
 * Il ragionamento di ogni compito si legge com'è davvero: anche quello che il compito eredita dal fornitore, che
 * prima non si vedeva (l'oracolo e la memoria ragionavano senza che la casella lo dicesse).
 */

const RICADUTA = "";

/* Un compito che ragiona perché lo eredita dal fornitore: è quello che costa senza che nessuno l'abbia scelto. */
const ereditaAcceso = (c: CompitoAssegnato) => c.ragiona_effettivo && c.ragiona_origine === "fornitore";

export default function Modelli() {
  const { dati, errore, inCorso, ricarica } = useDati(modelliECompiti);
  const { esegui, inCorso: inAzione, errore: erroreAzione } = useAzione();
  const fornitoriDati = useDati(fornitori);

  const cambia = async (compito: string, scelto: string) => {
    const fatto = await esegui((t) =>
      assegnaModello(t, compito, scelto === RICADUTA ? null : scelto),
    );
    if (fatto) {
      ricarica();
      fornitoriDati.ricarica();
    }
  };

  /* Una modifica alle impostazioni di un compito. Senza assegnazione propria il compito la riceve qui, sul fornitore
   * che già usa, e il livello resta quello che era (eredita) se non è proprio il livello a cambiare. */
  const aggiorna = async (c: CompitoAssegnato, campi: Omit<ModificaCompito, "modello">) => {
    const corpo: ModificaCompito = { modello: c.assegnato ?? c.in_uso, ...campi };
    if (!c.assegnato && !("livello" in campi)) corpo.livello = null;
    if (await esegui((t) => aggiornaCompito(t, c.compito, corpo))) ricarica();
  };

  const ricaricaTutto = () => {
    ricarica();
    fornitoriDati.ricarica();
  };

  const ereditati = dati?.compiti.filter(ereditaAcceso) ?? [];

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Modelli</h1>
          <p className={comuni.sottotitolo}>
            Una lettura interroga un modello più volte, per lavori diversi.
            Le domande dell&apos;intervista e l&apos;interpretazione di ogni
            carta vogliono un modello rapido; il responso finale il migliore
            che ci si possa permettere; la guardia che lo verifica un modello{" "}
            <em>diverso da quello che l&apos;ha scritto</em>.
          </p>
        </div>
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {erroreAzione && <p className={comuni.errore}>{erroreAzione}</p>}
      {inCorso && !dati && <p className={comuni.caricamento}>Caricamento…</p>}

      {dati && !dati.configurato && (
        <div className={comuni.errore} role="alert">
          <strong>Nessun modello di intelligenza artificiale è configurato.</strong>{" "}
          Finché non ne aggiungi uno le letture non partono: il servizio
          risponde «non pronto» senza addebitare nulla e non usa testi di
          ripiego. Aggiungilo qui sotto, in <strong>Fornitori</strong>, poi
          assegnalo ai compiti.
        </div>
      )}
      {dati?.finto && (
        <p className={comuni.errore} role="status">
          Modello finto attivo (<code>TAROT_LLM_FINTO</code>): le letture usano
          testi fissi, uguali per tutti. Solo per sviluppo e test.
        </p>
      )}
      {ereditati.length > 0 && (
        <div className={stili.allerta} role="status">
          <strong>Attenzione: {ereditati.length === 1 ? "un compito ragiona" : `${ereditati.length} compiti ragionano`} senza che nessuno l&apos;abbia scelto.</strong>{" "}
          Lo ereditano dal fornitore che usano, e ogni risposta costa molti più token (spesso dieci volte tanto):{" "}
          {ereditati.map((c) => `${c.label} (da ${c.in_uso}, livello ${nomeLivello(c.livello_effettivo).toLowerCase()})`).join("; ")}.
          Se non serve, scegli «Nessuno» nel loro menu del ragionamento.
        </div>
      )}

      {dati && (
        <div className={stili.compiti}>
          {dati.compiti.map((c) => (
            <Scheda
              key={c.compito}
              compito={c}
              modelli={dati.modelli}
              bloccato={inAzione}
              onCambia={(scelto) => cambia(c.compito, scelto)}
              onAggiorna={(campi) => aggiorna(c, campi)}
            />
          ))}
        </div>
      )}

      <SezioneFornitori
        dati={fornitoriDati.dati}
        errore={fornitoriDati.errore}
        inCorso={fornitoriDati.inCorso}
        ricarica={ricaricaTutto}
      />
    </>
  );
}

/* Cosa dice la scheda sul ragionamento in uso, in parole. */
function statoRagionamento(c: CompitoAssegnato): string {
  const stato = c.ragiona_effettivo ? "acceso" : "spento";
  const livello = c.ragiona_effettivo && c.livello_effettivo ? `, livello${nomeLivello(c.livello_effettivo).toLowerCase()}` : "";
  if (c.ragiona_origine === "compito") return `${stato[0].toUpperCase()}${stato.slice(1)}${livello} — scelto per questo compito.`;
  if (c.ragiona_origine === "parametri") return `${stato[0].toUpperCase()}${stato.slice(1)} — deciso dai parametri scritti a mano su questo compito.`;
  if (c.ragiona_origine === "codice") return "Spento — lo decide il servizio: questa chiamata non ha bisogno di ragionare.";
  if (c.ragiona_origine === "predefinito") return `${stato[0].toUpperCase()}${stato.slice(1)}${livello} — il predefinito di questo compito, finché non ne scegli un altro.`;
  return `${stato[0].toUpperCase()}${stato.slice(1)}${livello} — ereditato dal fornitore ${c.in_uso}.`;
}

function Scheda({
  compito,
  modelli,
  bloccato,
  onCambia,
  onAggiorna,
}: {
  compito: CompitoAssegnato;
  modelli: ModelloConfigurato[];
  bloccato: boolean;
  onCambia: (scelto: string) => void;
  onAggiorna: (campi: Omit<ModificaCompito, "modello">) => void;
}) {
  const id = `compito-${compito.compito}`;
  const idLivello = `${id}-livello`;
  const idStato = `${id}-stato`;
  const nessunModello = modelli.length === 0;
  const fornitoreLivello = compito.livello_fornitore ? nomeLivello(compito.livello_fornitore).toLowerCase() : null;

  return (
    <section className={stili.scheda}>
      <h2 className={stili.schedaTitolo}>{compito.label}</h2>
      <p className={stili.schedaNota}>{compito.descrizione}</p>

      <label className={stili.etichetta} htmlFor={id}>
        Modello
      </label>
      <select
        id={id}
        className={stili.scelta}
        value={compito.assegnato ?? RICADUTA}
        disabled={bloccato}
        onChange={(e) => onCambia(e.target.value)}
      >
        {/* Distinta da «assegnato al predefinito»: si comportano uguale oggi
            e diversamente domani, quando il predefinito cambia. */}
        <option value={RICADUTA}>
          {compito.segue ? `Nessuna scelta — usa il modello della ${compito.segue}` : "Nessuna scelta — segue il predefinito"}
        </option>
        {modelli.map((m) => (
          <option key={m.nome} value={m.nome}>
            {m.nome}
          </option>
        ))}
      </select>

      <label className={stili.etichetta} htmlFor={idLivello} style={{ marginTop: "0.8rem" }}>
        Ragionamento
      </label>
      <select
        id={idLivello}
        className={stili.scelta}
        aria-describedby={idStato}
        value={compito.livello ?? RICADUTA}
        disabled={bloccato || nessunModello || compito.ragiona_origine === "codice"}
        onChange={(e) => onAggiorna({ livello: (e.target.value || null) as LivelloRagionamento | null })}
      >
        <option value={RICADUTA}>
          {compito.livello_predefinito
            ? `Predefinito del compito (${nomeLivello(compito.livello_predefinito).toLowerCase()})`
            : `Eredita dal fornitore${fornitoreLivello ? ` (${fornitoreLivello})` : ""}`}
        </option>
        {LIVELLI_RAGIONAMENTO.map((l) => (
          <option key={l.valore} value={l.valore}>{l.nome}</option>
        ))}
      </select>
      <p id={idStato} className={compito.ragiona_effettivo ? stili.statoAcceso : stili.inUso}>
        {statoRagionamento(compito)}
      </p>
      {ereditaAcceso(compito) && (
        <p className={stili.avviso}>
          Ragiona perché lo eredita dal fornitore: costa di più senza che sia stato scelto. Se non serve, scegli «Nessuno».
        </p>
      )}
      {!compito.ragiona_spegnibile && compito.ragiona_effettivo && (
        <p className={stili.avviso}>
          Questo fornitore non dice come spegnere il ragionamento: scegli un livello per il compito perché si spenga davvero.
        </p>
      )}

      <AltreImpostazioni compito={compito} bloccato={bloccato || nessunModello} onAggiorna={onAggiorna} />

      <p className={stili.inUso}>
        In uso: <strong>{compito.in_uso}</strong>
        {compito.senza_filtri && (
          <>
            {" — "}
            <span className={stili.avviso}>
              modello senza filtri: non rifiuta nulla
            </span>
          </>
        )}
      </p>
    </section>
  );
}

/* Lo schema JSON rigoroso: un'impostazione avanzata, chiusa finché non serve, solo per i compiti che rispondono in
 * JSON. */
function AltreImpostazioni({
  compito: c, bloccato, onAggiorna,
}: {
  compito: CompitoAssegnato;
  bloccato: boolean;
  onAggiorna: (campi: Omit<ModificaCompito, "modello">) => void;
}) {
  if (!c.schema_possibile) return null;
  return (
    <details className={stili.altre}>
      <summary className={stili.altreTitolo}>Altre impostazioni</summary>
      <label className={stili.spuntaFornitore}>
        <input
          type="checkbox"
          checked={c.json_schema}
          disabled={bloccato}
          onChange={(e) => onAggiorna({ json_schema: e.target.checked })}
        />
        Risposta vincolata a uno schema rigoroso
      </label>
      <p className={stili.aiuto}>
        Il fornitore è obbligato a rispondere nella forma attesa, e una risposta malformata non può più arrivare. Da
        provare: se il fornitore non lo accetta, il servizio torna da solo al formato di prima e se lo ricorda.
      </p>
    </details>
  );
}

function SezioneFornitori({
  dati, errore, inCorso, ricarica,
}: {
  dati: { fornitori: Fornitore[]; catalogo: TipoFornitore[] } | null;
  errore: string | null;
  inCorso: boolean;
  ricarica: () => void;
}) {
  const [nuovo, setNuovo] = useState(false);

  return (
    <section className={stili.disponibili}>
      <div className={comuni.intestazione} style={{ marginBottom: "0.75rem" }}>
        <div>
          <h2 className={stili.disponibiliTitolo}>Fornitori</h2>
          <p className={stili.disponibiliNota}>
            Indirizzo, modello e chiave di ciascun fornitore. La chiave non si
            rivede mai una volta salvata: si sostituisce, non si consulta.
          </p>
        </div>
        <button className={comuni.primaria} type="button" aria-expanded={nuovo} onClick={() => setNuovo(!nuovo)}>
          {nuovo ? "Chiudi" : "Nuovo fornitore"}
        </button>
      </div>

      {nuovo && dati && (
        <ModuloFornitore
          catalogo={dati.catalogo}
          chiudi={() => setNuovo(false)}
          salvato={() => {
            setNuovo(false);
            ricarica();
          }}
        />
      )}

      {errore && <p className={comuni.errore}>{errore}</p>}
      {!dati && inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {dati && dati.fornitori.length === 0 && (
        <div className={comuni.vuoto}>Nessun fornitore ancora: aggiungine uno.</div>
      )}

      {dati && dati.fornitori.length > 0 && (
        <ul className={`${stili.elencoFornitori} ${inCorso ? comuni.inRicarica : ""}`} aria-label="Fornitori">
          {dati.fornitori.map((f) => (
            <VoceFornitore key={f.id} fornitore={f} catalogo={dati.catalogo} ricarica={ricarica} />
          ))}
        </ul>
      )}
    </section>
  );
}

function VoceFornitore({
  fornitore: f, catalogo, ricarica,
}: {
  fornitore: Fornitore;
  catalogo: TipoFornitore[];
  ricarica: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [modifica, setModifica] = useState(false);
  const [conferma, setConferma] = useState(false);
  const [esito, setEsito] = useState<EsitoProva | null>(null);
  const spec = catalogo.find((c) => c.tipo === f.tipo);

  const commuta = async () => {
    if (await esegui((t) => modificaFornitore(t, f.id, { attivo: !f.attivo }))) ricarica();
  };
  const elimina = async () => {
    if ((await esegui((t) => eliminaFornitore(t, f.id))) !== null) ricarica();
  };
  const prova = async () => {
    setEsito(null);
    const r = await esegui((t) => provaFornitore(t, f.id));
    if (r) setEsito(r);
  };

  return (
    <li className={f.attivo ? stili.fornitoreVoce : stili.fornitoreVoceSpenta}>
      <div className={stili.fornitoreTestata}>
        <div>
          <strong>{f.nome}</strong>
          <div className={comuni.mono}>{spec?.label ?? f.tipo}</div>
        </div>
        {f.senza_filtri && <span className={stili.avviso}>senza filtri</span>}
      </div>
      {f.descrizione && <p className={stili.descrizione}>{f.descrizione}</p>}
      <dl className={stili.fornitoreDati}>
        <dt>Indirizzo</dt>
        <dd className={comuni.mono}>{f.base_url || "—"}</dd>
        <dt>Modello</dt>
        <dd className={comuni.mono}>{f.model || "(quello caricato dal server)"}</dd>
        <dt>Chiave</dt>
        <dd>{f.has_key ? "impostata" : "nessuna"}</dd>
        <dt>Ragionamento</dt>
        <dd>{nomeLivello(f.livello_ragionamento)} (predefinito dei compiti che lo usano)</dd>
        <dt>Stato</dt>
        <dd className={f.attivo ? comuni.positivo : comuni.spento}>{f.attivo ? "attivo" : "disattivato"}</dd>
      </dl>

      {modifica ? (
        <ModuloFornitore
          fornitore={f}
          catalogo={catalogo}
          chiudi={() => setModifica(false)}
          salvato={() => {
            setModifica(false);
            ricarica();
          }}
        />
      ) : (
        <div className={stili.comandiFornitore}>
          <button type="button" className={comuni.secondaria} onClick={prova} disabled={inCorso}>
            Prova la connessione
          </button>
          <button type="button" className={comuni.secondaria} onClick={commuta} disabled={inCorso}>
            {f.attivo ? "Disattiva" : "Riattiva"}
          </button>
          <button type="button" className={comuni.secondaria} onClick={() => setModifica(true)}>
            Modifica
          </button>
          {conferma ? (
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
          )}
        </div>
      )}
      {errore && <p className={comuni.errore}>{errore}</p>}
      {esito && (
        <p className={esito.ok ? comuni.esito : comuni.errore}>
          {esito.ok
            ? `Risponde. Modelli visti: ${esito.modelli.slice(0, 5).join(", ") || "nessuno"}`
            : `Non risponde: ${esito.errore}`}
        </p>
      )}
    </li>
  );
}

/** Un fornitore nuovo o uno esistente: stesso modulo, l'assenza di `fornitore` decide quale. */
function ModuloFornitore({
  fornitore: f, catalogo, chiudi, salvato,
}: {
  fornitore?: Fornitore;
  catalogo: TipoFornitore[];
  chiudi: () => void;
  salvato: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [tipo, setTipo] = useState(f?.tipo ?? catalogo[0]?.tipo ?? "");
  const [nome, setNome] = useState(f?.nome ?? "");
  const [baseUrl, setBaseUrl] = useState(f?.base_url ?? catalogo[0]?.base_url ?? "");
  const [model, setModel] = useState(f?.model ?? "");
  const [apiKey, setApiKey] = useState("");
  const [apiKeyTocca, setApiKeyTocca] = useState(false);
  const [descrizione, setDescrizione] = useState(f?.descrizione ?? "");
  const [livello, setLivello] = useState<LivelloRagionamento>(f?.livello_ragionamento ?? "none");
  const [senzaFiltri, setSenzaFiltri] = useState(f?.senza_filtri ?? false);
  const [problema, setProblema] = useState<string | null>(null);

  const specScelto = catalogo.find((c) => c.tipo === tipo);

  const cambiaTipo = (t: string) => {
    setTipo(t);
    if (!f) setBaseUrl(catalogo.find((c) => c.tipo === t)?.base_url ?? "");
  };

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    setProblema(null);
    if (!f && !nome.trim()) return setProblema("Il nome non può essere vuoto.");

    if (f) {
      const corpo: ModificaFornitore = {
        base_url: baseUrl.trim(), model: model.trim(), descrizione: descrizione.trim(),
        livello_ragionamento: livello, senza_filtri: senzaFiltri,
      };
      if (apiKeyTocca) corpo.api_key = apiKey;
      if (await esegui((t) => modificaFornitore(t, f.id, corpo))) salvato();
    } else {
      const corpo: NuovoFornitore = {
        nome: nome.trim(), tipo, base_url: baseUrl.trim(), model: model.trim(),
        descrizione: descrizione.trim(), livello_ragionamento: livello, senza_filtri: senzaFiltri,
        api_key: apiKey,
      };
      if (await esegui((t) => creaFornitore(t, corpo))) salvato();
    }
  };

  return (
    <form onSubmit={invia} className={stili.fornitoreModulo}>
      {!f && (
        <div className={comuni.riga}>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Nome</span>
            <input className={comuni.ingresso} value={nome} maxLength={60} onChange={(e) => setNome(e.target.value)} placeholder="es. nvidia-veloce" />
            <span className={comuni.campoAiuto}>Come lo vedrai nell&apos;assegnazione dei compiti. Non si cambia dopo.</span>
          </label>
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Tipo</span>
            <select className={comuni.selezione} value={tipo} onChange={(e) => cambiaTipo(e.target.value)}>
              {catalogo.map((c) => (
                <option key={c.tipo} value={c.tipo}>{c.label}</option>
              ))}
            </select>
          </label>
        </div>
      )}
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Indirizzo</span>
        <input className={comuni.ingresso} value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="https://…/v1" />
        {specScelto?.nota && <span className={comuni.campoAiuto}>{specScelto.nota}</span>}
      </label>
      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Modello</span>
          <input className={comuni.ingresso} value={model} onChange={(e) => setModel(e.target.value)} placeholder="vuoto: il primo caricato" />
        </label>
        {(specScelto?.auth ?? "api_key") === "api_key" && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Chiave</span>
            <input
              className={comuni.ingresso}
              type="password"
              autoComplete="new-password"
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value);
                setApiKeyTocca(true);
              }}
              placeholder={f ? (f.has_key ? "invariata" : "nessuna") : ""}
            />
            {f && <span className={comuni.campoAiuto}>Vuota e toccata: la svuota. Non toccata: resta quella di prima.</span>}
          </label>
        )}
      </div>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Descrizione (solo per te)</span>
        <input className={comuni.ingresso} value={descrizione} maxLength={200} onChange={(e) => setDescrizione(e.target.value)} />
      </label>
      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Ragionamento predefinito</span>
        <select className={comuni.selezione} value={livello} onChange={(e) => setLivello(e.target.value as LivelloRagionamento)}>
          {LIVELLI_RAGIONAMENTO.map((l) => (
            <option key={l.valore} value={l.valore}>{l.nome}</option>
          ))}
        </select>
        <span className={comuni.campoAiuto}>
          Quanto pensa il modello prima di rispondere, per i compiti che non scelgono da sé. Più ragionamento vuol dire
          risposte più lente e molti più token pagati.
        </span>
      </label>
      <label className={stili.spuntaFornitore}>
        <input type="checkbox" checked={senzaFiltri} onChange={(e) => setSenzaFiltri(e.target.checked)} />
        Senza filtri (un modello «abliterato»: non rifiuta nulla)
      </label>
      {(problema || errore) && <p className={comuni.errore}>{problema ?? errore}</p>}
      <div className={stili.comandiFornitore}>
        <button className={comuni.primaria} type="submit" disabled={inCorso}>
          {f ? "Salva" : "Crea il fornitore"}
        </button>
        <button className={comuni.secondaria} type="button" onClick={chiudi} disabled={inCorso}>
          Annulla
        </button>
      </div>
    </form>
  );
}
