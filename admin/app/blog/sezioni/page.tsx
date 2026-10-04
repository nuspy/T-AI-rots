"use client";

import { useCallback, useMemo, useState } from "react";
import {
  creaSezione,
  eliminaSezione,
  modificaSezione,
  riordinaSezioni,
  sezioni,
  urlMedia,
  type CampiSezione,
  type Immagine,
  type Sezione,
  type TipoSezione,
} from "@/lib/blog";
import { ErroreApi } from "@/lib/api";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../../comuni.module.css";
import stili from "../blog.module.css";
import { SelettoreImmagine } from "../selettore-immagine";
import { Schede } from "../schede";

/* L'albero delle sezioni del blog.
 *
 * Una sezione ha un **tipo**: `articoli` raccoglie articoli scritti a mano; `carte` e `stese` elencano da sole
 * il catalogo (le ventidue carte dei maggiori, le stese di coppia…) secondo un filtro; `contenitore` riunisce le
 * sotto-sezioni e mostra gli articoli di tutte. Un articolo sta solo in una sezione di tipo «articoli».
 *
 * Si sposta con i pulsanti — su, giù, dentro, fuori — e non trascinando: il trascinamento non c'è sul telefono
 * e non lo si può fare con la tastiera, mentre un pulsante sì, da tutti e due.
 *
 * Nascondere una sezione nasconde anche ciò che contiene: il sito non mostra una sotto-sezione visibile sotto un
 * padre nascosto, e non ne mostra gli articoli.
 */

const TIPI: { valore: TipoSezione; etichetta: string; aiuto: string }[] = [
  { valore: "articoli", etichetta: "Articoli", aiuto: "Articoli scritti a mano." },
  { valore: "contenitore", etichetta: "Contenitore", aiuto: "Riunisce sotto-sezioni e gli articoli di tutte." },
  { valore: "carte", etichetta: "Carte", aiuto: "Elenca da sola le carte del catalogo." },
  { valore: "stese", etichetta: "Stese", aiuto: "Elenca da sola le stese del catalogo." },
];

const FILTRI: Record<"carte" | "stese", { valore: string; etichetta: string }[]> = {
  carte: [
    { valore: "", etichetta: "Tutte le carte" },
    { valore: "arcano:maggiore", etichetta: "Arcani maggiori" },
    { valore: "arcano:minore", etichetta: "Arcani minori" },
    { valore: "seme:bastoni", etichetta: "Bastoni" },
    { valore: "seme:coppe", etichetta: "Coppe" },
    { valore: "seme:spade", etichetta: "Spade" },
    { valore: "seme:dischi", etichetta: "Dischi" },
  ],
  stese: [
    { valore: "", etichetta: "Tutte le stese" },
    { valore: "categoria:standard", etichetta: "Standard" },
    { valore: "categoria:lavoro", etichetta: "Lavoro e affari" },
    { valore: "tema:lavoro", etichetta: "Per il lavoro (lavoro e affari + standard adatte)" },
    { valore: "categoria:compatibilita", etichetta: "Compatibilità" },
    { valore: "categoria:coppia", etichetta: "Coppia" },
  ],
};

const filtroInValore = (f: Record<string, string> | null): string => {
  const voce = Object.entries(f ?? {})[0];
  return voce ? `${voce[0]}:${voce[1]}` : "";
};
const valoreInFiltro = (v: string): Record<string, string> | null => {
  if (!v) return null;
  const [chiave, valore] = v.split(":");
  return { [chiave]: valore };
};

interface Nodo {
  sezione: Sezione;
  figli: Nodo[];
}

function costruisci(tutte: Sezione[]): Nodo[] {
  const nodi = new Map(tutte.map((s) => [s.id, { sezione: s, figli: [] as Nodo[] }]));
  const radici: Nodo[] = [];
  for (const n of nodi.values()) {
    const padre = n.sezione.parent_id === null ? undefined : nodi.get(n.sezione.parent_id);
    (padre ? padre.figli : radici).push(n);
  }
  const ordina = (lista: Nodo[]) => {
    lista.sort((a, b) => a.sezione.ordine - b.sezione.ordine || a.sezione.nome.localeCompare(b.sezione.nome));
    lista.forEach((n) => ordina(n.figli));
  };
  ordina(radici);
  return radici;
}

/** Gli id di una sezione e di tutte quelle che le stanno sotto. */
function discendenti(nodo: Nodo): Set<number> {
  const ids = new Set<number>([nodo.sezione.id]);
  for (const f of nodo.figli) discendenti(f).forEach((i) => ids.add(i));
  return ids;
}

export default function Sezioni() {
  const elenco = useDati(sezioni);
  const { esegui, inCorso, errore } = useAzione();
  const [modificando, setModificando] = useState<number | "nuova" | null>(null);
  const [eliminando, setEliminando] = useState<Sezione | null>(null);
  const [problemaElimina, setProblemaElimina] = useState<string | null>(null);

  const radici = useMemo(() => costruisci(elenco.dati ?? []), [elenco.dati]);

  /* Trova i fratelli di una sezione (quelle con lo stesso padre), già in ordine. */
  const fratelliDi = useCallback(
    (padre: number | null): Sezione[] => {
      const visita = (lista: Nodo[]): Sezione[] | null => {
        if (padre === null) return lista.map((n) => n.sezione);
        for (const n of lista) {
          if (n.sezione.id === padre) return n.figli.map((f) => f.sezione);
          const dentro = visita(n.figli);
          if (dentro) return dentro;
        }
        return null;
      };
      return visita(radici) ?? [];
    },
    [radici],
  );

  const applica = async (voci: { id: number; parent_id: number | null; ordine: number }[]) => {
    if ((await esegui((t) => riordinaSezioni(t, voci))) !== null) elenco.ricarica();
  };

  /* I fratelli si riscrivono tutti con ordini 0..n−1: gli ordini di partenza possono avere buchi o
   * valori uguali, e uno scambio fra due numeri uguali non cambierebbe niente. */
  const sposta = (s: Sezione, verso: -1 | 1) => {
    const fratelli = fratelliDi(s.parent_id);
    const i = fratelli.findIndex((f) => f.id === s.id);
    const j = i + verso;
    if (i < 0 || j < 0 || j >= fratelli.length) return;
    const nuovo = [...fratelli];
    [nuovo[i], nuovo[j]] = [nuovo[j], nuovo[i]];
    void applica(nuovo.map((f, ordine) => ({ id: f.id, parent_id: s.parent_id, ordine })));
  };

  /* «Dentro»: diventa l'ultima figlia della sezione che la precede. */
  const dentro = (s: Sezione) => {
    const fratelli = fratelliDi(s.parent_id);
    const i = fratelli.findIndex((f) => f.id === s.id);
    if (i <= 0) return;
    const nuovoPadre = fratelli[i - 1];
    const figli = fratelliDi(nuovoPadre.id);
    void applica([
      ...fratelli.filter((f) => f.id !== s.id).map((f, ordine) => ({ id: f.id, parent_id: s.parent_id, ordine })),
      { id: s.id, parent_id: nuovoPadre.id, ordine: figli.length },
    ]);
  };

  /* «Fuori»: sale di un livello, subito dopo il padre che lascia. */
  const fuori = (s: Sezione) => {
    if (s.parent_id === null) return;
    const tutte = elenco.dati ?? [];
    const padre = tutte.find((x) => x.id === s.parent_id);
    if (!padre) return;
    const livello = fratelliDi(padre.parent_id).filter((f) => f.id !== s.id);
    const posizione = livello.findIndex((f) => f.id === padre.id) + 1;
    livello.splice(posizione, 0, s);
    void applica(livello.map((f, ordine) => ({ id: f.id, parent_id: padre.parent_id, ordine })));
  };

  const mostraNascondi = async (s: Sezione) => {
    if (await esegui((t) => modificaSezione(t, s.id, { visibile: !s.visibile }))) elenco.ricarica();
  };

  const elimina = async (s: Sezione, forza: boolean) => {
    setProblemaElimina(null);
    const fatto = await esegui(async (t) => {
      try {
        await eliminaSezione(t, s.id, forza);
        return true;
      } catch (e) {
        /* Un 409 non è un guasto: dice che la sezione non è vuota, e la scelta di forzare tocca a chi amministra. */
        if (e instanceof ErroreApi && e.stato === 409) {
          setProblemaElimina(
            "Contiene degli articoli o delle sotto-sezioni. Eliminandola gli articoli restano, senza sezione, e le sotto-sezioni salgono alla radice.",
          );
          return false;
        }
        throw e;
      }
    });
    if (fatto) {
      setEliminando(null);
      elenco.ricarica();
    }
  };

  const disegna = (lista: Nodo[]) => (
    <ul className={stili.albero}>
      {lista.map((n, indice) => {
        const s = n.sezione;
        return (
          <li key={s.id} className={stili.nodo}>
            <div className={`${stili.nodoRiga} ${s.visibile ? "" : stili.nodoNascosto}`}>
              <div className={stili.nodoNome}>
                {s.nome}
                <small>
                  /{s.slug} · {s.tipo}
                  {s.tipo === "articoli" || s.tipo === "contenitore" ? ` · ${s.n_articoli} articoli` : ""}
                  {s.visibile ? "" : " · nascosta"}
                </small>
              </div>
              <div className={stili.nodoAzioni} role="group" aria-label={`Azioni per ${s.nome}`}>
                <button type="button" disabled={inCorso || indice === 0} onClick={() => sposta(s, -1)} aria-label={`Sposta ${s.nome} su`} title="Su">
                  ↑
                </button>
                <button type="button" disabled={inCorso || indice === lista.length - 1} onClick={() => sposta(s, 1)} aria-label={`Sposta ${s.nome} giù`} title="Giù">
                  ↓
                </button>
                <button type="button" disabled={inCorso || indice === 0} onClick={() => dentro(s)} aria-label={`Metti ${s.nome} dentro la sezione precedente`} title="Dentro la precedente">
                  →
                </button>
                <button type="button" disabled={inCorso || s.parent_id === null} onClick={() => fuori(s)} aria-label={`Porta ${s.nome} un livello più in alto`} title="Un livello su">
                  ←
                </button>
                <button type="button" disabled={inCorso} onClick={() => mostraNascondi(s)}>
                  {s.visibile ? "Nascondi" : "Mostra"}
                </button>
                <button type="button" disabled={inCorso} onClick={() => setModificando(modificando === s.id ? null : s.id)} aria-expanded={modificando === s.id}>
                  Modifica
                </button>
                <button
                  type="button"
                  disabled={inCorso}
                  style={{ color: "var(--allarme)" }}
                  onClick={() => {
                    setProblemaElimina(null);
                    setEliminando(eliminando?.id === s.id ? null : s);
                  }}
                >
                  Elimina
                </button>
              </div>
            </div>

            {eliminando?.id === s.id && (
              <div className={stili.modulo} role="alert">
                <p style={{ marginTop: 0 }}>
                  Eliminare <strong>{s.nome}</strong>?
                  {problemaElimina && <span> {problemaElimina}</span>}
                </p>
                <div className={stili.azioniModulo}>
                  <button type="button" className={comuni.distruttiva} style={{ height: 44 }} disabled={inCorso} onClick={() => elimina(s, problemaElimina !== null)}>
                    {problemaElimina ? "Elimina lo stesso" : "Sì, elimina"}
                  </button>
                  <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setEliminando(null)}>
                    Annulla
                  </button>
                </div>
              </div>
            )}

            {modificando === s.id && (
              <ModuloSezione
                key={s.id}
                iniziale={s}
                tutte={elenco.dati ?? []}
                albero={radici}
                chiudi={() => setModificando(null)}
                salvato={() => {
                  setModificando(null);
                  elenco.ricarica();
                }}
              />
            )}

            {n.figli.length > 0 && disegna(n.figli)}
          </li>
        );
      })}
    </ul>
  );

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Blog · Sezioni</h1>
          <p className={comuni.sottotitolo}>
            L&apos;albero delle sezioni: carte, stese e articoli stanno nella stessa struttura, così ogni articolo può
            collegarsi a una carta o a una stesa. Una sezione nascosta nasconde anche ciò che contiene.
          </p>
        </div>
        <button className={comuni.primaria} style={{ height: 44 }} onClick={() => setModificando(modificando === "nuova" ? null : "nuova")} aria-expanded={modificando === "nuova"}>
          Nuova sezione
        </button>
      </div>

      <Schede />

      {modificando === "nuova" && (
        <ModuloSezione
          iniziale={null}
          tutte={elenco.dati ?? []}
          albero={radici}
          chiudi={() => setModificando(null)}
          salvato={() => {
            setModificando(null);
            elenco.ricarica();
          }}
        />
      )}

      {(elenco.errore || errore) && (
        <p className={comuni.errore} role="alert">
          {errore ?? elenco.errore}
        </p>
      )}
      {!elenco.dati && elenco.inCorso && <p className={comuni.caricamento}>Caricamento…</p>}
      {elenco.dati && radici.length === 0 && <div className={comuni.vuoto}>Nessuna sezione. Creane una con «Nuova sezione».</div>}
      {radici.length > 0 && <div className={elenco.inCorso ? comuni.inRicarica : undefined}>{disegna(radici)}</div>}
    </>
  );
}

function ModuloSezione({
  iniziale,
  tutte,
  albero,
  chiudi,
  salvato,
}: {
  iniziale: Sezione | null;
  tutte: Sezione[];
  albero: Nodo[];
  chiudi: () => void;
  salvato: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [nome, setNome] = useState(iniziale?.nome ?? "");
  const [slug, setSlug] = useState(iniziale?.slug ?? "");
  const [descrizione, setDescrizione] = useState(iniziale?.descrizione ?? "");
  const [tipo, setTipo] = useState<TipoSezione>(iniziale?.tipo ?? "articoli");
  const [filtro, setFiltro] = useState(filtroInValore(iniziale?.filtro ?? null));
  const [padre, setPadre] = useState(iniziale?.parent_id === null || iniziale === null ? "" : String(iniziale.parent_id));
  const [visibile, setVisibile] = useState(iniziale?.visibile ?? true);
  const [seoTitolo, setSeoTitolo] = useState(iniziale?.seo_titolo ?? "");
  const [seoDescrizione, setSeoDescrizione] = useState(iniziale?.seo_descrizione ?? "");
  const [immagine, setImmagine] = useState<{ id: string; url: string } | null>(
    iniziale?.immagine_id && iniziale.immagine ? { id: iniziale.immagine_id, url: iniziale.immagine } : null,
  );
  const [scegli, setScegli] = useState(false);

  /* Una sezione non può stare sotto se stessa né sotto una delle sue discendenti (il server lo rifiuta
   * comunque, ma non ha senso offrirlo). */
  const vietate = useMemo(() => {
    if (!iniziale) return new Set<number>();
    const trova = (lista: Nodo[]): Nodo | null => {
      for (const n of lista) {
        if (n.sezione.id === iniziale.id) return n;
        const d = trova(n.figli);
        if (d) return d;
      }
      return null;
    };
    const nodo = trova(albero);
    return nodo ? discendenti(nodo) : new Set([iniziale.id]);
  }, [iniziale, albero]);

  const candidati = useMemo(() => {
    const uscita: { s: Sezione; livello: number }[] = [];
    const visita = (lista: Nodo[], livello: number) => {
      for (const n of lista) {
        if (vietate.has(n.sezione.id)) continue;
        uscita.push({ s: n.sezione, livello });
        visita(n.figli, livello + 1);
      }
    };
    visita(albero, 0);
    return uscita;
  }, [albero, vietate]);

  const invia = async (e: React.FormEvent) => {
    e.preventDefault();
    const corpo: CampiSezione = {
      nome: nome.trim(),
      slug: slug.trim() || undefined,
      descrizione: descrizione.trim() || null,
      tipo,
      filtro: tipo === "carte" || tipo === "stese" ? valoreInFiltro(filtro) : null,
      parent_id: padre ? Number(padre) : null,
      visibile,
      immagine_id: immagine?.id ?? null,
      seo_titolo: seoTitolo.trim() || null,
      seo_descrizione: seoDescrizione.trim() || null,
    };
    if (!iniziale) corpo.ordine = tutte.filter((s) => s.parent_id === corpo.parent_id).length;
    const fatto = await esegui((t) => (iniziale ? modificaSezione(t, iniziale.id, corpo) : creaSezione(t, corpo)));
    if (fatto) salvato();
  };

  return (
    <form className={stili.modulo} onSubmit={invia} aria-label={iniziale ? `Modifica ${iniziale.nome}` : "Nuova sezione"}>
      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Nome</span>
          <input className={comuni.ingresso} value={nome} maxLength={120} required onChange={(e) => setNome(e.target.value)} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Indirizzo (slug)</span>
          <input className={comuni.ingresso} value={slug} maxLength={80} onChange={(e) => setSlug(e.target.value)} placeholder={iniziale ? "" : "Vuoto: dal nome"} />
        </label>
      </div>

      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Tipo</span>
          <select
            className={comuni.selezione}
            value={tipo}
            onChange={(e) => {
              setTipo(e.target.value as TipoSezione);
              setFiltro("");
            }}
          >
            {TIPI.map((t) => (
              <option key={t.valore} value={t.valore}>
                {t.etichetta}
              </option>
            ))}
          </select>
          <span className={comuni.campoAiuto}>{TIPI.find((t) => t.valore === tipo)?.aiuto}</span>
        </label>
        {(tipo === "carte" || tipo === "stese") && (
          <label className={comuni.campo}>
            <span className={comuni.campoEtichetta}>Che cosa elenca</span>
            <select className={comuni.selezione} value={filtro} onChange={(e) => setFiltro(e.target.value)}>
              {FILTRI[tipo].map((f) => (
                <option key={f.valore} value={f.valore}>
                  {f.etichetta}
                </option>
              ))}
            </select>
          </label>
        )}
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Dentro</span>
          <select className={comuni.selezione} value={padre} onChange={(e) => setPadre(e.target.value)}>
            <option value="">Radice (nessun padre)</option>
            {candidati.map(({ s, livello }) => (
              <option key={s.id} value={s.id}>
                {"— ".repeat(livello)}
                {s.nome}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className={comuni.campo}>
        <span className={comuni.campoEtichetta}>Descrizione</span>
        <textarea
          className={comuni.area}
          style={{ minHeight: "5rem", fontFamily: "inherit", fontSize: "1rem" }}
          value={descrizione}
          maxLength={2000}
          onChange={(e) => setDescrizione(e.target.value)}
        />
      </label>

      <div className={comuni.riga}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Titolo per i motori di ricerca</span>
          <input className={comuni.ingresso} value={seoTitolo} maxLength={200} onChange={(e) => setSeoTitolo(e.target.value)} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Descrizione per i motori (320 al massimo)</span>
          <input className={comuni.ingresso} value={seoDescrizione} maxLength={320} onChange={(e) => setSeoDescrizione(e.target.value)} />
        </label>
      </div>

      <div style={{ marginBottom: "0.9rem" }}>
        <span className={comuni.campoEtichetta}>Immagine</span>
        <div className={comuni.riga} style={{ marginTop: "0.3rem", alignItems: "center" }}>
          {immagine && (
            // eslint-disable-next-line @next/next/no-img-element -- immagine della sezione
            <img src={urlMedia(immagine.url) ?? ""} alt="" width={96} height={72} style={{ objectFit: "cover", flex: "0 0 auto", border: "1px solid var(--filo)" }} />
          )}
          <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setScegli(!scegli)} aria-expanded={scegli}>
            {immagine ? "Cambia" : "Scegli o carica"}
          </button>
          {immagine && (
            <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={() => setImmagine(null)}>
              Togli
            </button>
          )}
        </div>
        {scegli && (
          <div style={{ marginTop: "0.6rem" }}>
            <SelettoreImmagine
              scelta={immagine?.id}
              alScelta={(i: Immagine) => {
                setImmagine({ id: i.id, url: i.url });
                setScegli(false);
              }}
              chiudi={() => setScegli(false)}
            />
          </div>
        )}
      </div>

      <label className={stili.interruttore}>
        <input type="checkbox" checked={visibile} onChange={(e) => setVisibile(e.target.checked)} />
        Visibile sul sito
      </label>

      {errore && (
        <p className={comuni.errore} role="alert">
          {errore}
        </p>
      )}
      <div className={stili.azioniModulo}>
        <button type="submit" className={comuni.primaria} style={{ height: 44 }} disabled={inCorso || !nome.trim()}>
          {iniziale ? "Salva" : "Crea la sezione"}
        </button>
        <button type="button" className={comuni.secondaria} style={{ height: 44 }} onClick={chiudi}>
          Annulla
        </button>
      </div>
    </form>
  );
}
