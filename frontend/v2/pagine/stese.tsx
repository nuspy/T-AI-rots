"use client";

/* Le stese nella v2: una forma che aiuta la domanda a dispiegarsi. L'elenco porta alla lettura con quella stesa
 * (`/v2/read?spread=…`); la pagina di una stesa mostra lo schema sul tavolo, le posizioni, come leggerla.
 *
 * Gli spazi pubblicitari (spenti per default): nell'elenco dopo ogni gruppo di stese; nella pagina di una stesa dopo
 * lo schema, dopo le regole e dopo le altre stese, prima del diario. */

import { useRef } from "react";
import { elencaStese, type Categoria, type Stesa, type Stile } from "@/lib/api";
import { urlMedia } from "@/lib/blog";
import { nomePosizione, nomeStesa } from "@/lib/i18n/nomi";
import { f, plurale } from "@/v2/i18n";
import { AvvisoTraduzione } from "@/v2/componenti/avviso-traduzione";
import LinkV2 from "@/v2/componenti/link";
import { Pubblicita } from "@/v2/componenti/pubblicita";
import { MiniaturaStesa } from "@/v2/lettura/miniatura";
import { Tavolo } from "@/v2/lettura/tavolo";
import { P, linguaContenuti } from "@/v2/lib/dati";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";
import { useTraduzione } from "@/v2/lib/usa-traduzione";
import { ArticoliSu, DiarioNove } from "./blog";

const ORDINE_STILI: Stile[] = ["tradizionale", "moderna", "tendenza"];

function nomeSt(s: Stesa, lingua: string) {
  return s.lang === linguaContenuti(lingua) ? s.nome : nomeStesa(s, lingua as Parameters<typeof nomeStesa>[1]);
}

function Tessera({ stesa }: { stesa: Stesa }) {
  const { t, lingua } = useLingua();
  const k = t.stese;
  // v9.4: l'illustrazione della stesa, se c'è, con lo schema sovrapposto in una lastra prugna; altrimenti lo schema.
  const illustrazione = urlMedia(stesa.immagine?.mini ?? stesa.immagine?.url);
  return (
    <LinkV2 className="difference" href={R.stesa(stesa.slug ?? stesa.id)}>
      {illustrazione ? (
        <span className="spread-illustrata">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={illustrazione} alt="" loading="lazy" width={480} height={300} />
          <span className="scheda-stesa-schema"><MiniaturaStesa stesa={stesa} /></span>
        </span>
      ) : <MiniaturaStesa stesa={stesa} className="spread-mini" />}
      <h3>{nomeSt(stesa, lingua)}</h3>
      <p>{plurale(stesa.posizioni.length, t.lettura.n_carte)} · {stesa.mazzo === "maggiori" ? k.maggiori : k.completo}</p>
    </LinkV2>
  );
}

export function ElencoStese() {
  const { t, lingua } = useLingua();
  const k = t.stese;
  const stese = useCarica(() => elencaStese(undefined, linguaContenuti(lingua)), [lingua], { pubblico: true, iniziale: P.stese(lingua) });
  const per = (c: Categoria) => (stese.dati ?? []).filter((s) => s.categoria === c);
  const gruppo = (c: Categoria, titolo: string, testo: string) => (
    <section className="band band-tight" aria-labelledby={`stese-${c}`}>
      <h2 id={`stese-${c}`} className="section-title">{titolo}</h2>
      <p className="section-intro">{testo}</p>
      {c === "standard" ? (
        <div className="difference-grid even">
          {per(c).map((s) => <Tessera key={s.id} stesa={s} />)}
          <LinkV2 className="difference" href={R.fisica}>
            <span aria-hidden="true">✋</span><h3>{k.fisica}</h3><p>{k.fisica_testo}</p>
          </LinkV2>
        </div>
      ) : (
        ORDINE_STILI.map((stile) => {
          const elenco = per(c).filter((s) => s.stile === stile);
          if (!elenco.length) return null;
          return (
            <div key={stile} style={{ marginTop: ".55rem" }}>
              <p className="eyebrow">{t.lettura.stili[stile].nome} · {t.lettura.stili[stile].testo}</p>
              <div className="difference-grid even">{elenco.map((s) => <Tessera key={s.id} stesa={s} />)}</div>
            </div>
          );
        })
      )}
    </section>
  );
  if (stese.errore) return <section className="band band-tight"><p className="error">{stese.errore}</p></section>;
  return (
    <>
      {gruppo("standard", k.standard, k.standard_testo)}
      <Pubblicita posizione="terzo" />
      {gruppo("compatibilita", k.compat, k.compat_testo)}
      <Pubblicita posizione="due_terzi" />
      {gruppo("coppia", k.coppia, k.coppia_testo)}
      <Pubblicita posizione="fine" />
    </>
  );
}

export function SchedaStesa({ id }: { id: string }) {
  const { t, lingua } = useLingua();
  const k = t.stese;
  const stese = useCarica(() => elencaStese(undefined, linguaContenuti(lingua)), [lingua], { pubblico: true, iniziale: P.stese(lingua) });
  /* v9.5: la stesa esiste in italiano e in inglese; nelle altre lingue si traduce dall'inglese sul dispositivo. I nomi
   * ufficiali delle posizioni e le etichette del sito restano `data-no-trad`. */
  const intro = useRef<HTMLParagraphElement>(null);
  const posizioni = useRef<HTMLOListElement>(null);
  const testo = useRef<HTMLDivElement>(null);
  const traduzione = useTraduzione([intro, posizioni, testo], lingua, {
    sorgente: linguaContenuti(lingua), chiave: stese.dati ? id : undefined,
  });
  if (stese.errore) return <section className="band band-tight"><p className="error">{stese.errore}</p></section>;
  if (!stese.dati) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const s = stese.dati.find((x) => x.id === id || x.slug === id || Object.values(x.slugs ?? {}).includes(id));
  if (!s) {
    return (
      <section className="band band-tight">
        <p className="section-intro">{k.non_trovata_stesa}</p>
        <LinkV2 className="button button-quiet" href={R.stese}>{k.stesa_tutte}</LinkV2>
      </section>
    );
  }
  const nomePos = (n: number) => {
    const p = s.posizioni.find((x) => x.n === n);
    return p ? (s.lang === linguaContenuti(lingua) ? p.nome : nomePosizione(p, lingua)) : String(n);
  };
  const altre = stese.dati.filter((x) => x.categoria === s.categoria && x.id !== s.id).slice(0, 4);
  return (
    <>
      <section className="subhero subhero-compact">
        <p className="eyebrow">{k.stesa_eyebrow} · {plurale(s.posizioni.length, t.lettura.n_carte)}</p>
        <h1 className="display">{nomeSt(s, lingua)}</h1>
        <p ref={intro} lang={linguaContenuti(lingua)} className="section-intro">{s.descrizione}</p>
        <div className="button-row" style={{ marginTop: ".5rem" }}>
          <LinkV2 className="button button-brass" href={`${R.leggi}?spread=${encodeURIComponent(s.id)}&source=spread`}>{k.stesa_cta}</LinkV2>
          <LinkV2 className="button button-quiet" href={R.stese}>{k.stesa_tutte}</LinkV2>
        </div>
      </section>
      <section className="band band-tight">
        <AvvisoTraduzione stato={traduzione} />
        <div className="read-layout">
          <div className="read-panel dark" role="img" aria-label={k.stesa_diagramma}>
            <Tavolo stesa={s} posate={[]} prossima={null} rivelazioneInCorso={false} evidenzia={null} />
          </div>
          <div className="read-panel">
            <h2>{k.stesa_posizioni}</h2>
            <ol ref={posizioni} lang={linguaContenuti(lingua)} className="list-plain">
              {s.posizioni.map((p) => (
                <li key={p.n} className="memory-entry">
                  <small data-no-trad>{f(k.stesa_posizione, { n: p.n })}</small>
                  <h3 data-no-trad>{nomePos(p.n)}</h3>
                  <p>{p.significato}</p>
                  {p.domanda && <p className="small" style={{ fontStyle: "italic" }}>{p.domanda}</p>}
                </li>
              ))}
            </ol>
          </div>
        </div>
        <Pubblicita posizione="terzo" dentro />
        <div ref={testo} lang={linguaContenuti(lingua)} className="prose-block" style={{ marginTop: ".7rem" }}>
          {s.regole.length > 0 && (<><h3 data-no-trad>{k.stesa_come}</h3><ul>{s.regole.map((r, i) => <li key={i}>{r}</li>)}</ul></>)}
          {s.coppie.length > 0 && (
            <>
              <h3 data-no-trad>{k.stesa_coppie}</h3>
              <ul>{s.coppie.map(([a, b, testo]) => <li key={`${a}-${b}`}><b data-no-trad>{nomePos(a)} ↔ {nomePos(b)}.</b> {testo}</li>)}</ul>
            </>
          )}
          {s.origine && (<><h3 data-no-trad>{k.stesa_origine}</h3><p>{s.origine}</p></>)}
        </div>
      </section>
      <Pubblicita posizione="due_terzi" />
      {altre.length > 0 && (
        <>
          <section className="band band-tight">
            <p className="eyebrow">{k.stesa_altre}</p>
            <div className="difference-grid even">{altre.map((x) => <Tessera key={x.id} stesa={x} />)}</div>
          </section>
          {/* La fine dopo le altre stese: senza, cadrebbe subito dopo i due terzi. */}
          <Pubblicita posizione="fine" />
        </>
      )}
      {/* Le scelte per pertinenza prima degli ultimi articoli (v9.4), poi l'elenco completo di quelli su questa stesa. */}
      <DiarioNove contesto={{ stesa: s.id }} ordine="scelti" />
      <ArticoliSu tipo="stesa" id={s.id} nome={nomeSt(s, lingua)} base={R.stesa(s.slug ?? s.id)} />
    </>
  );
}
