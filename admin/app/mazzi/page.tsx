"use client";

/* I mazzi in vendita (v5, Fase B): prezzi, finestra di attivazione stagionale, offerta a tempo.
 * L'artwork resta fuori da qui: file statici nel frontend, un mazzo nuovo richiede un build+deploy. */

import { useState } from "react";
import {
  caricaArtwork, creaMazzo, eliminaArtwork, eliminaMazzo, elencoArtwork, impostaOfferta,
  mazzi as leggiMazzi, modificaMazzo, rimuoviOfferta, scaricaArtwork,
  type ArtworkUpload, type Mazzo, type NuovoMazzo, type TipoOfferta,
} from "@/lib/mazzi";
import { useAzione, useDati } from "@/lib/usa";
import comuni from "../comuni.module.css";

function soldi(centesimi: number | null, valuta = "EUR"): string {
  if (centesimi === null) return "—";
  return (centesimi / 100).toLocaleString("it-IT", { style: "currency", currency: valuta });
}

const VUOTO: NuovoMazzo = { slug: "", nome: "", prezzo_digitale: undefined };

export default function Mazzi() {
  const { dati, errore, inCorso, ricarica } = useDati(leggiMazzi);
  const { esegui, inCorso: inAzione, errore: erroreAzione } = useAzione();
  const [nuovo, setNuovo] = useState<NuovoMazzo>(VUOTO);

  const crea = async () => {
    if (!nuovo.slug.trim() || !nuovo.nome.trim()) return;
    const fatto = await esegui((t) => creaMazzo(t, {
      ...nuovo, slug: nuovo.slug.trim(), nome: nuovo.nome.trim(),
      prezzo_digitale: nuovo.prezzo_digitale || undefined,
    }));
    if (fatto) { setNuovo(VUOTO); ricarica(); }
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
            Prezzi e disponibilità dei mazzi in vendita. La grafica non si carica qui: vive come file
            nel frontend (un mazzo nuovo richiede un rilascio). Un mazzo già posseduto da qualcuno o
            già usato in una lettura non si elimina: si disattiva.
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
            <label className={comuni.campoEtichetta} htmlFor="nuovo-slug">Slug</label>
            <input id="nuovo-slug" className={comuni.ingresso} value={nuovo.slug}
              onChange={(e) => setNuovo((n) => ({ ...n, slug: e.target.value }))} placeholder="halloween-2026" />
          </div>
          <div className={comuni.campo}>
            <label className={comuni.campoEtichetta} htmlFor="nuovo-nome">Nome</label>
            <input id="nuovo-nome" className={comuni.ingresso} value={nuovo.nome}
              onChange={(e) => setNuovo((n) => ({ ...n, nome: e.target.value }))} placeholder="Mazzo di Halloween" />
          </div>
          <div className={comuni.campo}>
            <label className={comuni.campoEtichetta} htmlFor="nuovo-prezzo">Prezzo digitale (€)</label>
            <input id="nuovo-prezzo" className={comuni.ingresso} type="number" min={0} step={0.01}
              value={nuovo.prezzo_digitale ? nuovo.prezzo_digitale / 100 : ""}
              onChange={(e) => setNuovo((n) => ({ ...n, prezzo_digitale: e.target.value ? Math.round(Number(e.target.value) * 100) : undefined }))} />
          </div>
          <button type="button" className={comuni.primaria} disabled={inAzione || !nuovo.slug.trim() || !nuovo.nome.trim()} onClick={crea}>
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
  const [validoFino, setValidoFino] = useState("");

  const salvaOfferta = async () => {
    const v = Number(valore);
    if (!v || v <= 0) return;
    const fatto = await esegui((t) => impostaOfferta(t, mazzo.slug, {
      tipo, valore: tipo === "percentuale" ? v : Math.round(v * 100),
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
          <div className={comuni.mono}>{mazzo.slug}</div>
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
          {mazzo.offerta_attiva && (
            <div className={comuni.positivo}>{soldi(mazzo.prezzo_digitale_scontato, mazzo.valuta)}</div>
          )}
        </td>
        <td><PrezzoInline valore={mazzo.prezzo_stampa} bloccato={bloccato} onSalva={(t) => onPrezzo("prezzo_stampa", t)} /></td>
        <td><PrezzoInline valore={mazzo.prezzo_fisico} bloccato={bloccato} onSalva={(t) => onPrezzo("prezzo_fisico", t)} /></td>
        <td>
          {mazzo.prezzo_digitale === null ? (
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
            onClick={() => setArtworkAperto((a) => !a)}>
            Artwork
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
              <input className={comuni.ingresso} type="datetime-local" value={validoFino} onChange={(e) => setValidoFino(e.target.value)} />
              <button type="button" className={comuni.primaria} disabled={inCorso} onClick={salvaOfferta}>Salva</button>
            </div>
          </td>
        </tr>
      )}
      {artworkAperto && (
        <tr>
          <td colSpan={7}>
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
    <div>
      <p className={comuni.sottotitolo}>
        Carica uno ZIP con tutte le 78 carte + il dorso (stesso nome file = id carta, come produce
        <code> resize_cards.py</code>). Dopo il caricamento, scarica lo ZIP e estrailo in{" "}
        <code>frontend/public/cards/{slug}/</code> prima del prossimo rilascio.
      </p>
      {(erroreLettura || errore) && <p className={comuni.errore}>{erroreLettura ?? errore}</p>}
      <div className={comuni.riga}>
        <input type="file" accept=".zip" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <button type="button" className={comuni.primaria} disabled={!file || inCorso} onClick={carica}>
          Carica
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
