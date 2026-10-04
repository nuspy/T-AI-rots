"use client";

/* I mazzi in vendita (v5, Fase B): prezzi, finestra di attivazione stagionale, offerta a tempo, e le immagini.
 * Le immagini (pulsante «Immagini» di ogni mazzo) hanno due strade separate: «Immagini del mazzo nel sito» (ZIP o
 * cartella, online subito, `immagini.tsx`) e l'«Archivio ZIP da scaricare» (Fase I: lo ZIP conservato così com'è,
 * da estrarre a mano nel frontend; non mette niente online). */

import { useId, useState } from "react";
import { PannelloImmagini } from "./immagini";
import {
  caricaArtwork, creaMazzo, eliminaArtwork, eliminaMazzo, elencoArtwork, impostaOfferta,
  mazzi as leggiMazzi, modificaMazzo, rimuoviOfferta, scaricaArtwork,
  type ArtworkUpload, type FormatoOfferta, type Mazzo, type NuovoMazzo, type TipoOfferta,
} from "@/lib/mazzi";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";
import { Traduzioni, diverse, type Testi } from "../traduzioni";

function soldi(centesimi: number | null, valuta = "EUR"): string {
  if (centesimi === null) return "—";
  return (centesimi / 100).toLocaleString("it-IT", { style: "currency", currency: valuta });
}

const VUOTO: NuovoMazzo = { slug: "", nome: "", prezzo_digitale: undefined };

/* Lo slug: l'identificativo del mazzo negli indirizzi e nei file. Le stesse regole del server
 * (`admin_mazzi.py::SLUG_MAZZO`): minuscole, cifre, trattini singoli fra le parole, da 2 a 40 caratteri. */
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function problemaSlug(slug: string): string | null {
  if (!slug) return null;
  if (slug.length < 2 || slug.length > 40) return "Da 2 a 40 caratteri.";
  if (/[A-Z]/.test(slug)) return "Solo lettere minuscole.";
  if (!SLUG.test(slug)) return "Solo lettere minuscole senza accenti, numeri e trattini fra le parole (niente spazi, «_», trattini doppi o all'inizio/alla fine).";
  return null;
}

/** Uno slug proposto dal nome: «Mazzo di Halloween 2026» → `mazzo-di-halloween-2026`. */
function slugDa(nome: string): string {
  return nome.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40).replace(/-+$/, "");
}

export default function Mazzi() {
  const { dati, errore, inCorso, ricarica } = useDati(leggiMazzi);
  const { esegui, inCorso: inAzione, errore: erroreAzione } = useAzione();
  const [nuovo, setNuovo] = useState<NuovoMazzo>(VUOTO);
  /* Finché lo slug non si tocca a mano, segue il nome. */
  const [slugAMano, setSlugAMano] = useState(false);
  const aiutoSlug = useId();
  const erroreSlug = problemaSlug(nuovo.slug.trim());

  const crea = async () => {
    if (!nuovo.slug.trim() || !nuovo.nome.trim() || erroreSlug) return;
    const fatto = await esegui((t) => creaMazzo(t, {
      ...nuovo, slug: nuovo.slug.trim(), nome: nuovo.nome.trim(),
      prezzo_digitale: nuovo.prezzo_digitale || undefined,
    }));
    if (fatto) { setNuovo(VUOTO); setSlugAMano(false); ricarica(); }
  };

  const salvaPrezzo = async (m: Mazzo, campo: "prezzo_digitale" | "prezzo_stampa" | "prezzo_fisico", testo: string) => {
    const valore = testo.trim() === "" ? null : Math.round(Number(testo) * 100);
    if (valore !== null && Number.isNaN(valore)) return;
    if ((await esegui((t) => modificaMazzo(t, m.slug, { [campo]: valore }))) !== null) ricarica();
  };

  const cambiaAttivo = async (m: Mazzo, attivo: boolean) => {
    if ((await esegui((t) => modificaMazzo(t, m.slug, { attivo }))) !== null) ricarica();
  };

  const elimina = async (m: Mazzo) => {
    if ((await esegui((t) => eliminaMazzo(t, m.slug))) !== null) ricarica();
  };

  return (
    <>
      <div className={comuni.intestazione}>
        <div>
          <h1 className={comuni.titolo}>Mazzi</h1>
          <p className={comuni.sottotitolo}>
            Prezzi, disponibilità e immagini dei mazzi in vendita. Le immagini di un mazzo nuovo si caricano
            dal pulsante «Immagini» (uno ZIP o una cartella con le 78 carte e il dorso) e sono online subito,
            senza rilascio. Un mazzo già posseduto da qualcuno o già usato in una lettura non si elimina: si
            disattiva.
          </p>
        </div>
      </div>

      {errore && <p className={comuni.errore}>{errore}</p>}
      {erroreAzione && <p className={comuni.errore}>{erroreAzione}</p>}
      {inCorso && !dati && <p className={comuni.caricamento}>Caricamento…</p>}

      <div className={comuni.riquadro}>
        <h2 className={comuni.riquadroTitolo}>Nuovo mazzo</h2>
        <div className={comuni.riga}>
          <div className={comuni.campo}>
            <label className={comuni.campoEtichetta} htmlFor="nuovo-nome">Nome</label>
            <input id="nuovo-nome" className={comuni.ingresso} value={nuovo.nome}
              onChange={(e) => {
                const nome = e.target.value;
                setNuovo((n) => ({ ...n, nome, slug: slugAMano ? n.slug : slugDa(nome) }));
              }} placeholder="Mazzo di Halloween" />
          </div>
          <div className={comuni.campo}>
            <label className={comuni.campoEtichetta} htmlFor="nuovo-slug">Slug (identificativo nell&apos;indirizzo)</label>
            <input id="nuovo-slug" className={comuni.ingresso} value={nuovo.slug} maxLength={40}
              autoCapitalize="none" autoCorrect="off" spellCheck={false} inputMode="url"
              aria-invalid={erroreSlug ? true : undefined} aria-describedby={aiutoSlug}
              onChange={(e) => { setSlugAMano(true); setNuovo((n) => ({ ...n, slug: e.target.value })); }}
              placeholder="halloween-2026" />
            <span id={aiutoSlug} className={comuni.campoAiuto}>
              {erroreSlug && <strong className={comuni.negativo} role="alert">{erroreSlug} </strong>}
              Lo slug è il nome del mazzo negli indirizzi e nei file: per esempio{" "}
              <code>/decks/{nuovo.slug.trim() || "thoth"}</code> e <code>/cards/{nuovo.slug.trim() || "thoth"}/maj-00.webp</code>.
              Solo lettere minuscole, numeri e trattini (es. <code>halloween-2026</code>). Si propone da solo dal nome.
              Non si cambia dopo la creazione: indirizzi, letture e ordini già fatti lo usano.
            </span>
          </div>
          <div className={comuni.campo}>
            <label className={comuni.campoEtichetta} htmlFor="nuovo-prezzo">Prezzo digitale (€)</label>
            <input id="nuovo-prezzo" className={comuni.ingresso} type="number" min={0} step={0.01}
              value={nuovo.prezzo_digitale ? nuovo.prezzo_digitale / 100 : ""}
              onChange={(e) => setNuovo((n) => ({ ...n, prezzo_digitale: e.target.value ? Math.round(Number(e.target.value) * 100) : undefined }))} />
          </div>
          <button type="button" className={comuni.primaria} disabled={inAzione || !nuovo.slug.trim() || !nuovo.nome.trim() || Boolean(erroreSlug)} onClick={crea}>
            Crea
          </button>
        </div>
      </div>

      {dati && dati.length === 0 && <p className={comuni.vuoto}>Nessun mazzo ancora.</p>}

      {dati && dati.length > 0 && (
        <div className={comuni.contenitoreTabella}>
          <table className={comuni.tabella}>
            <thead>
              <tr>
                <th>Mazzo</th>
                <th>Attivo</th>
                <th>Digitale</th>
                <th>Stampa</th>
                <th>Fisico</th>
                <th>Offerta</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {dati.map((m) => (
                <RigaMazzo
                  key={m.slug} mazzo={m} bloccato={inAzione}
                  onAttivo={(v) => cambiaAttivo(m, v)}
                  onPrezzo={(campo, testo) => salvaPrezzo(m, campo, testo)}
                  onElimina={() => elimina(m)}
                  onOfferta={ricarica}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function RigaMazzo({
  mazzo, bloccato, onAttivo, onPrezzo, onElimina, onOfferta,
}: {
  mazzo: Mazzo;
  bloccato: boolean;
  onAttivo: (v: boolean) => void;
  onPrezzo: (campo: "prezzo_digitale" | "prezzo_stampa" | "prezzo_fisico", testo: string) => void;
  onElimina: () => void;
  onOfferta: () => void;
}) {
  const { esegui, inCorso, errore } = useAzione();
  const [offertaAperta, setOffertaAperta] = useState(false);
  const [artworkAperto, setArtworkAperto] = useState(false);
  const [tipo, setTipo] = useState<TipoOfferta>("percentuale");
  const [valore, setValore] = useState("");
  const [validoDal, setValidoDal] = useState("");
  const [validoFino, setValidoFino] = useState("");
  const [dettagliAperti, setDettagliAperti] = useState(false);
  /* Si propongono i formati che hanno un prezzo. */
  const [formati, setFormati] = useState<FormatoOfferta[]>(() => (
    (["digitale", "pdf", "fisico"] as FormatoOfferta[]).filter((f) => prezzoDi(mazzo, f) !== null)
  ));

  const salvaOfferta = async () => {
    const v = Number(valore);
    if (!v || v <= 0 || formati.length === 0) return;
    const fatto = await esegui((t) => impostaOfferta(t, mazzo.slug, {
      tipo, valore: tipo === "percentuale" ? v : Math.round(v * 100), formati,
      valido_dal: validoDal ? new Date(validoDal).toISOString() : null,
      valido_fino: validoFino ? new Date(validoFino).toISOString() : null,
    }));
    if (fatto) { setOffertaAperta(false); onOfferta(); }
  };

  const togliOfferta = async () => {
    if ((await esegui((t) => rimuoviOfferta(t, mazzo.slug))) !== null) onOfferta();
  };

  return (
    <>
      <tr>
        <td>
          <strong>{mazzo.nome}</strong>{" "}
          {mazzo.predefinito && <span className={comuni.etichetta}>predefinito</span>}
          <div className={comuni.mono}>slug: {mazzo.slug}</div>
          {mazzo.immagini_versione && <span className={comuni.etichetta}>immagini caricate</span>}
        </td>
        <td>
          <label>
            <input type="checkbox" checked={mazzo.attivo} disabled={bloccato || mazzo.predefinito}
              onChange={(e) => onAttivo(e.target.checked)} />
          </label>
          {!mazzo.attivo_ora && mazzo.attivo && <div className={comuni.spento}>fuori finestra</div>}
        </td>
        <td>
          <PrezzoInline valore={mazzo.prezzo_digitale} bloccato={bloccato} onSalva={(t) => onPrezzo("prezzo_digitale", t)} />
          {mazzo.prezzo_digitale_scontato != null && (
            <div className={comuni.positivo}>{soldi(mazzo.prezzo_digitale_scontato, mazzo.valuta)}</div>
          )}
        </td>
        <td>
          <PrezzoInline valore={mazzo.prezzo_stampa} bloccato={bloccato} onSalva={(t) => onPrezzo("prezzo_stampa", t)} />
          {mazzo.prezzo_stampa_scontato != null && <div className={comuni.positivo}>{soldi(mazzo.prezzo_stampa_scontato, mazzo.valuta)}</div>}
        </td>
        <td>
          <PrezzoInline valore={mazzo.prezzo_fisico} bloccato={bloccato} onSalva={(t) => onPrezzo("prezzo_fisico", t)} />
          {mazzo.prezzo_fisico_scontato != null && <div className={comuni.positivo}>{soldi(mazzo.prezzo_fisico_scontato, mazzo.valuta)}</div>}
        </td>
        <td>
          {mazzo.prezzo_digitale === null && mazzo.prezzo_stampa === null && mazzo.prezzo_fisico === null ? (
            <span className={comuni.spento}>senza prezzo</span>
          ) : mazzo.offerta_attiva ? (
            <button type="button" className={comuni.secondaria} disabled={inCorso} onClick={togliOfferta}>Togli</button>
          ) : (
            <button type="button" className={comuni.secondaria} disabled={inCorso} onClick={() => setOffertaAperta((a) => !a)}>
              Imposta
            </button>
          )}
        </td>
        <td>
          <button type="button" className={comuni.secondaria} disabled={bloccato}
            onClick={() => setDettagliAperti((a) => !a)}>
            Dettagli
          </button>{" "}
          <button type="button" className={comuni.secondaria} disabled={bloccato} aria-expanded={artworkAperto}
            onClick={() => setArtworkAperto((a) => !a)}>
            Immagini
          </button>
          {!mazzo.predefinito && (
            <button type="button" className={comuni.distruttiva} disabled={bloccato} onClick={onElimina}>Elimina</button>
          )}
        </td>
      </tr>
      {offertaAperta && (
        <tr>
          <td colSpan={7}>
            {errore && <p className={comuni.errore}>{errore}</p>}
            <div className={comuni.riga}>
              <select className={comuni.selezione} value={tipo} onChange={(e) => setTipo(e.target.value as TipoOfferta)}>
                <option value="percentuale">% percentuale</option>
                <option value="importo">€ importo fisso</option>
              </select>
              <input className={comuni.ingresso} type="number" min={0} step={tipo === "percentuale" ? 1 : 0.01}
                value={valore} onChange={(e) => setValore(e.target.value)} placeholder={tipo === "percentuale" ? "20" : "5.00"} />
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Dal (vuoto: subito)</span>
                <input className={comuni.ingresso} type="datetime-local" value={validoDal} onChange={(e) => setValidoDal(e.target.value)} />
              </label>
              <label className={comuni.campo}>
                <span className={comuni.campoEtichetta}>Fino a (vuoto: senza scadenza)</span>
                <input className={comuni.ingresso} type="datetime-local" value={validoFino} onChange={(e) => setValidoFino(e.target.value)} />
              </label>
              <fieldset className={comuni.campo} style={{ border: 0, padding: 0, margin: 0 }}>
                <legend className={comuni.campoEtichetta}>Su quali prodotti</legend>
                {(["digitale", "pdf", "fisico"] as FormatoOfferta[]).map((f) => (
                  <label key={f} style={{ display: "inline-flex", gap: ".35rem", marginRight: ".8rem", alignItems: "center", minHeight: 44 }}>
                    <input type="checkbox" checked={formati.includes(f)} disabled={prezzoDi(mazzo, f) === null}
                      onChange={(e) => setFormati((x) => (e.target.checked ? [...x, f] : x.filter((y) => y !== f)))} />
                    {NOMI_FORMATO[f]}
                  </label>
                ))}
              </fieldset>
              <button type="button" className={comuni.primaria} disabled={inCorso || formati.length === 0} onClick={salvaOfferta}>Salva</button>
            </div>
          </td>
        </tr>
      )}
      {dettagliAperti && (
        <tr>
          <td colSpan={7}>
            <DettagliMazzo mazzo={mazzo} onSalvato={() => { setDettagliAperti(false); onOfferta(); }} />
          </td>
        </tr>
      )}
      {artworkAperto && (
        <tr>
          <td colSpan={7}>
            <PannelloImmagini slug={mazzo.slug} predefinito={mazzo.predefinito} />
            <PannelloArtwork slug={mazzo.slug} />
          </td>
        </tr>
      )}
    </>
  );
}

/** v7, Fase I: carica, scarica ed elimina lo ZIP di artwork in staging per un mazzo. Automatizza
 * solo la ricezione/validazione — l'estrazione in `frontend/public/cards/<slug>/` e il rilascio
 * restano un passo manuale, per scelta esplicita (l'artwork resta un file statico nell'immagine). */
function PannelloArtwork({ slug }: { slug: string }) {
  const { dati, errore: erroreLettura, inCorso: caricamento, ricarica } = useDati(
    (t) => elencoArtwork(t, slug), [slug],
  );
  const { esegui, inCorso, errore } = useAzione();
  const [file, setFile] = useState<File | null>(null);

  const carica = async () => {
    if (!file) return;
    if ((await esegui((t) => caricaArtwork(t, slug, file))) !== null) {
      setFile(null);
      ricarica();
    }
  };

  const scarica = async (uploadId: string) => {
    await esegui((t) => scaricaArtwork(t, slug, uploadId));
  };

  const elimina = async (uploadId: string) => {
    if ((await esegui((t) => eliminaArtwork(t, slug, uploadId))) !== null) ricarica();
  };

  return (
    <details style={{ marginTop: "1rem", paddingTop: "1rem", borderTop: "1px solid var(--filo)" }}>
      <summary style={{ cursor: "pointer", minHeight: 44, display: "flex", alignItems: "center" }}>
        Archivio ZIP da scaricare (vecchio metodo: installazione come file, serve un rilascio)
      </summary>
      <p className={comuni.sottotitolo}>
        <strong>Non mette le immagini nel sito.</strong> Conserva lo ZIP così com&apos;è (78 carte + dorso, nome file =
        id carta, come produce <code>resize_cards.py</code>), per riscaricarlo ed estrarlo a mano in{" "}
        <code>frontend/public/cards/{slug}/</code> prima di un rilascio. Per mettere online il mazzo subito usa
        «Immagini del mazzo nel sito», qui sopra. I file nel frontend, se ci sono, hanno la precedenza sulle immagini
        caricate dalla console.
      </p>
      {(erroreLettura || errore) && <p className={comuni.errore}>{erroreLettura ?? errore}</p>}
      <div className={comuni.riga}>
        <input type="file" accept=".zip" aria-label="ZIP da conservare nell'archivio" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button type="button" className={comuni.secondaria} disabled={!file || inCorso} onClick={carica}>
          Conserva nell&apos;archivio
        </button>
      </div>
      {caricamento && <p>Caricamento…</p>}
      {dati && dati.length === 0 && <p className={comuni.spento}>Nessun upload in attesa.</p>}
      {dati && dati.length > 0 && (
        <ul>
          {dati.map((u: ArtworkUpload) => (
            <li key={u.id}>
              {u.file_count} file — {new Date(u.creato_il).toLocaleString("it-IT")}{" "}
              <button type="button" className={comuni.secondaria} disabled={inCorso} onClick={() => scarica(u.id)}>
                Scarica
              </button>{" "}
              <button type="button" className={comuni.distruttiva} disabled={inCorso} onClick={() => elimina(u.id)}>
                Elimina
              </button>
            </li>
          ))}
        </ul>
      )}
    </details>
  );
}

const NOMI_FORMATO: Record<FormatoOfferta, string> = { digitale: "digitale", pdf: "PDF da stampare", fisico: "scatola fisica" };

function prezzoDi(m: Mazzo, f: FormatoOfferta): number | null {
  return f === "digitale" ? m.prezzo_digitale : f === "pdf" ? m.prezzo_stampa : m.prezzo_fisico;
}

/** Da `2026-10-01T08:00:00+00:00` al valore di un `datetime-local` nell'ora locale. */
function perCampo(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const z = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}T${z(d.getHours())}:${z(d.getMinutes())}`;
}

/** v8.5: descrizione, finestra di attivazione (stagionale), ordine nel negozio e spedizione. */
function DettagliMazzo({ mazzo, onSalvato }: { mazzo: Mazzo; onSalvato: () => void }) {
  const { esegui, inCorso, errore } = useAzione();
  const [descrizione, setDescrizione] = useState(mazzo.descrizione ?? "");
  const [da, setDa] = useState(perCampo(mazzo.attivazione_da));
  const [fino, setFino] = useState(perCampo(mazzo.attivazione_fino));
  const [rank, setRank] = useState(String(mazzo.rank));
  const [spedizione, setSpedizione] = useState(mazzo.richiede_spedizione);
  const [nomiT, setNomiT] = useState<Testi>(mazzo.nomi ?? {});
  const [descrizioniT, setDescrizioniT] = useState<Testi>(mazzo.descrizioni ?? {});

  const salva = async () => {
    const fatto = await esegui((t) => modificaMazzo(t, mazzo.slug, {
      descrizione: descrizione.trim() || null,
      attivazione_da: da ? new Date(da).toISOString() : null,
      attivazione_fino: fino ? new Date(fino).toISOString() : null,
      rank: Number(rank) || 0,
      richiede_spedizione: spedizione,
      ...(diverse(nomiT, mazzo.nomi ?? {}) ? { nomi: nomiT } : {}),
      ...(diverse(descrizioniT, mazzo.descrizioni ?? {}) ? { descrizioni: descrizioniT } : {}),
    }));
    if (fatto) onSalvato();
  };

  return (
    <div>
      {errore && <p className={comuni.errore}>{errore}</p>}
      <div className={comuni.riga} style={{ flexWrap: "wrap", alignItems: "flex-end" }}>
        <label className={comuni.campo} style={{ flex: "1 1 320px" }}>
          <span className={comuni.campoEtichetta}>Descrizione (nel negozio)</span>
          <textarea className={comuni.ingresso} rows={3} maxLength={2000} value={descrizione} onChange={(e) => setDescrizione(e.target.value)} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>In vendita dal</span>
          <input className={comuni.ingresso} type="datetime-local" value={da} onChange={(e) => setDa(e.target.value)} />
          <span className={comuni.campoAiuto}>Vuoto: da subito.</span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Fino a</span>
          <input className={comuni.ingresso} type="datetime-local" value={fino} onChange={(e) => setFino(e.target.value)} />
          <span className={comuni.campoAiuto}>Vuoto: senza scadenza (un mazzo stagionale sparisce da solo).</span>
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>Ordine nel negozio</span>
          <input className={comuni.ingresso} type="number" value={rank} onChange={(e) => setRank(e.target.value)} style={{ width: 90 }} />
          <span className={comuni.campoAiuto}>Più basso, prima.</span>
        </label>
        <label className={comuni.campo} style={{ flexDirection: "row", gap: ".5rem", alignItems: "center" }}>
          <input type="checkbox" checked={spedizione} onChange={(e) => setSpedizione(e.target.checked)} />
          <span>La scatola fisica si spedisce (serve un indirizzo)</span>
        </label>
        <button type="button" className={comuni.primaria} disabled={inCorso} onClick={salva}>Salva</button>
      </div>
      <Traduzioni nomi={nomiT} descrizioni={descrizioniT} onNomi={setNomiT} onDescrizioni={setDescrizioniT}
        massimoDescrizione={2000} />
    </div>
  );
}

function PrezzoInline({ valore, bloccato, onSalva }: { valore: number | null; bloccato: boolean; onSalva: (testo: string) => void }) {
  const [testo, setTesto] = useState(valore !== null ? String(valore / 100) : "");
  return (
    <input
      className={comuni.ingresso}
      style={{ width: 90 }}
      type="number"
      min={0}
      step={0.01}
      value={testo}
      disabled={bloccato}
      onChange={(e) => setTesto(e.target.value)}
      onBlur={() => onSalva(testo)}
    />
  );
}
