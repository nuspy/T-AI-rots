"use client";

/* La preparazione di una lettura, nelle due colonne della v2: a sinistra la conversazione che comincia (la
 * domanda, il tipo di lettura, le persone, la forma della stesa), a destra la console del rito che mostra la
 * stesa scelta e l'invito a cominciare. */

import type { Categoria, Stesa, Stile } from "@/lib/api";
import { nomePosizione, nomeStesa } from "@/lib/i18n/nomi";
import { plurale } from "@/v2/i18n";
import { useLingua } from "@/v2/lib/lingua";
import { MiniaturaStesa } from "./miniatura";
import stili from "./lettura.module.css";

const ORDINE_STILI: Stile[] = ["tradizionale", "moderna", "tendenza"];
const CATEGORIE: Categoria[] = ["standard", "compatibilita", "coppia"];

export function SceltaTipo({ categoria, onScegli }: { categoria: Categoria; onScegli: (c: Categoria) => void }) {
  const { t } = useLingua();
  const l = t.lettura;
  return (
    <>
      <h3 className={stili.passo}>{l.tipo_titolo}</h3>
      <div className={stili.tipi} role="group" aria-label={l.tipo_titolo}>
        {CATEGORIE.map((c) => (
          <button key={c} type="button" className={stili.tipo} aria-pressed={c === categoria} onClick={() => onScegli(c)}>
            <b>{l.tipi[c].nome}</b>
            <span>{l.tipi[c].testo}</span>
          </button>
        ))}
      </div>
    </>
  );
}

export function SceltaStesa({
  stese, scelta, onScegli, conStili, conTitolo = true,
}: {
  stese: Stesa[];
  scelta: string | null;
  onScegli: (id: string) => void;
  conStili: boolean;
  /** Senza, quando la pagina ha già il suo titolo per la scelta. */
  conTitolo?: boolean;
}) {
  const { t, lingua } = useLingua();
  const l = t.lettura;
  const selezionata = stese.find((s) => s.id === scelta);
  const offerti = ORDINE_STILI.filter((s) => stese.some((x) => x.stile === s));
  const stileAttivo: Stile | null = conStili ? (selezionata?.stile ?? offerti[0] ?? null) : null;
  const visibili = conStili ? stese.filter((s) => s.stile === stileAttivo) : stese;
  return (
    <>
      {conTitolo && <h3 className={stili.passo}>{l.stesa_titolo}</h3>}
      {conStili && (
        <>
          <div className={stili.stili} role="group">
            {offerti.map((s) => (
              <button key={s} type="button" className="chip" aria-pressed={s === stileAttivo}
                onClick={() => { const prima = stese.find((x) => x.stile === s); if (prima) onScegli(prima.id); }}>
                {l.stili[s].nome}
              </button>
            ))}
          </div>
          {stileAttivo && <p className="muted small">{l.stili[stileAttivo].testo}</p>}
        </>
      )}
      <div className={stili.stese}>
        {visibili.map((s) => (
          <button key={s.id} type="button" className={stili.stesa} aria-pressed={s.id === scelta} onClick={() => onScegli(s.id)}>
            <MiniaturaStesa stesa={s} className={stili.miniatura} />
            <b>{nomeStesa(s, lingua)}</b>
            <small>{plurale(s.posizioni.length, l.n_carte)} · {s.mazzo === "maggiori" ? l.maggiori : l.completo}</small>
          </button>
        ))}
      </div>
    </>
  );
}

/** La stesa scelta, nella console scura: disegno, descrizione, posizioni. */
export function StesaNellaConsole({ stesa }: { stesa: Stesa }) {
  const { t, lingua } = useLingua();
  return (
    <div className={stili.stesaScelta}>
      <MiniaturaStesa stesa={stesa} className={stili.miniatura} />
      <p className="console-status">{plurale(stesa.posizioni.length, t.lettura.n_carte)}</p>
      <h3>{nomeStesa(stesa, lingua)}</h3>
      <p>{stesa.descrizione}</p>
      {stesa.origine && <p className={stili.origine}>{stesa.origine}</p>}
      <ol className={stili.posizioniElenco} aria-label={t.lettura.posizioni}>
        {stesa.posizioni.map((p) => <li key={p.n}>{nomePosizione(p, lingua)}</li>)}
      </ol>
    </div>
  );
}
