"use client";

/* I pezzi che le pagine di «Notifications» condividono: l'anteprima della notifica come la vede un telefono, i
 * campi dei testi per lingua (con il contatore dei caratteri), le scelte multiple del filtro. */

import { useId } from "react";
import type { Lingua, Testi, Testo } from "@/lib/notifiche";
import { LINGUE, NOMI_LINGUA } from "@/lib/notifiche";
import comuni from "../comuni.module.css";
import stili from "./notifiche.module.css";

/** Le misure consigliate: oltre, Android e iOS tagliano con i puntini. */
export const TITOLO_CONSIGLIATO = 60;
export const CORPO_CONSIGLIATO = 180;

export function Anteprima({ testo, immagine, promozione, lingua }: {
  testo: Testo | undefined;
  immagine?: string | null;
  promozione?: boolean;
  lingua: Lingua;
}) {
  return (
    <figure className={stili.telefono} style={{ margin: 0 }} aria-label={`Anteprima della notifica in ${NOMI_LINGUA[lingua].toLowerCase()}`}>
      <div className={stili.notifica}>
        <span className={stili.icona} aria-hidden="true">T</span>
        <span className={stili.notificaApp}>TAROTS chat · adesso</span>
        <span className={stili.notificaTitolo}>{testo?.titolo || "Titolo della notifica"}</span>
        <span className={stili.notificaCorpo}>{testo?.corpo || "Il testo della notifica."}</span>
        {immagine && (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img className={stili.notificaImmagine} src={immagine} alt="" loading="lazy" />
        )}
        {promozione && <span className={stili.notificaAzione}>Niente più promozioni</span>}
      </div>
      <figcaption className={comuni.campoAiuto} style={{ marginTop: "0.5rem" }}>
        Indicativa: ogni sistema la disegna a modo suo. Sul sito, le promozioni hanno il pulsante per non riceverne più.
      </figcaption>
    </figure>
  );
}

function Contatore({ n, massimo }: { n: number; massimo: number }) {
  return (
    <span className={`${stili.contatore} ${n > massimo ? stili.contatoreOltre : ""}`}>
      {n}/{massimo}
      {n > massimo && <span className={stili.soloLettori}> (troppo lungo: verrà tagliato su alcuni telefoni)</span>}
    </span>
  );
}

/** Titolo e testo di una lingua, con le schede delle lingue sopra. */
export function TestiPerLingua({ testi, lingua, scegli, cambia, base, segnaposto }: {
  testi: Testi;
  lingua: Lingua;
  scegli: (l: Lingua) => void;
  cambia: (l: Lingua, t: Testo) => void;
  base: Lingua;
  segnaposto?: Partial<Record<Lingua, Testo>>;
}) {
  const id = useId();
  const t = testi[lingua] ?? { titolo: "", corpo: "" };
  return (
    <>
      <ul className={stili.lingue} role="tablist" aria-label="Lingua del testo">
        {LINGUE.map((l) => {
          const vuota = !testi[l]?.titolo || !testi[l]?.corpo;
          return (
            <li key={l} role="presentation">
              <button
                type="button"
                role="tab"
                aria-selected={l === lingua}
                aria-controls={`${id}-pannello`}
                className={l === lingua ? stili.linguaScelta : stili.lingua}
                onClick={() => scegli(l)}
              >
                {l.toUpperCase()}
                {l === base && <span className={stili.vuota}>base</span>}
                {vuota && l !== base && <span className={stili.vuota} aria-label="vuota">○</span>}
              </button>
            </li>
          );
        })}
      </ul>
      <div id={`${id}-pannello`} role="tabpanel" aria-label={NOMI_LINGUA[lingua]}>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>
            Titolo ({NOMI_LINGUA[lingua].toLowerCase()}) <Contatore n={t.titolo.length} massimo={TITOLO_CONSIGLIATO} />
          </span>
          <input className={comuni.ingresso} value={t.titolo} maxLength={120} lang={lingua}
            placeholder={segnaposto?.[lingua]?.titolo}
            onChange={(e) => cambia(lingua, { ...t, titolo: e.target.value })} />
        </label>
        <label className={comuni.campo}>
          <span className={comuni.campoEtichetta}>
            Testo <Contatore n={t.corpo.length} massimo={CORPO_CONSIGLIATO} />
          </span>
          <textarea className={comuni.area} style={{ minHeight: "5.5rem", fontFamily: "inherit", fontSize: "1rem" }}
            value={t.corpo} maxLength={400} lang={lingua} placeholder={segnaposto?.[lingua]?.corpo}
            onChange={(e) => cambia(lingua, { ...t, corpo: e.target.value })} />
        </label>
      </div>
    </>
  );
}

/** Una scelta multipla come fila di caselle alte 44px. */
export function Scelte<T extends string>({ titolo, voci, scelte, cambia, aiuto }: {
  titolo: string;
  voci: { valore: T; nome: string }[];
  scelte: T[];
  cambia: (v: T[]) => void;
  aiuto?: string;
}) {
  return (
    <fieldset className={stili.chips}>
      <legend>{titolo}</legend>
      {voci.map((v) => (
        <label key={v.valore} className={stili.chip}>
          <input
            type="checkbox"
            checked={scelte.includes(v.valore)}
            onChange={(e) => cambia(e.target.checked ? [...scelte, v.valore] : scelte.filter((x) => x !== v.valore))}
          />
          {v.nome}
        </label>
      ))}
      {aiuto && <span className={comuni.campoAiuto} style={{ flexBasis: "100%" }}>{aiuto}</span>}
    </fieldset>
  );
}

export function Casella({ etichetta, valore, cambia, aiuto }: {
  etichetta: string;
  valore: boolean;
  cambia: (v: boolean) => void;
  aiuto?: React.ReactNode;
}) {
  return (
    <label className={stili.casella}>
      <input type="checkbox" checked={valore} onChange={(e) => cambia(e.target.checked)} />
      <span>
        {etichetta}
        {aiuto && <small>{aiuto}</small>}
      </span>
    </label>
  );
}
