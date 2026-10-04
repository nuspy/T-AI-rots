"use client";

/* I mazzi nella v2 (specifica v2, §10): una casa per più mazzi. Quelli disponibili arrivano dall'API; quelli in
 * sviluppo sono dichiarati come tali, mai presentati come disponibili. Ogni mazzo ha la sua pagina: il linguaggio
 * delle immagini, la biblioteca, la lettura, l'edizione fisica. */

import { useRouter } from "next/navigation";
import { euro, urlPdfGratuito, votoHome, type Mazzo } from "@/lib/api";
import { f } from "@/v2/i18n";
import { CampioniVoto } from "@/v2/componenti/campioni-voto";
import { ImmagineCarta } from "@/v2/componenti/carta";
import LinkV2 from "@/v2/componenti/link";
import { ConPubblicita } from "@/v2/componenti/pubblicita";
import { useCarrello } from "@/v2/lib/carrello";
import { useLingua } from "@/v2/lib/lingua";
import { R, indirizzoV2 } from "@/v2/lib/percorsi";
import { useCarica } from "@/v2/lib/usa";
import { P, useMazzi } from "@/v2/lib/dati";

/* Le immagini di un mazzo: il predefinito (Thoth) nella cartella piatta, gli altri nella propria. */
const cartellaDi = (m: Mazzo) => (m.predefinito ? null : m.slug);
const CAMPIONE = ["maj-00", "maj-02", "maj-06", "maj-09", "maj-17", "maj-19"];

export function Mazzi() {
  const { t } = useLingua();
  const k = t.mazzi;
  const mazzi = useMazzi();
  const disponibili = (mazzi.dati ?? []).filter((m) => m.predefinito || m.attivo_ora);
  /* Gli spazi pubblicitari (spenti per default) fra i blocchi: i mazzi disponibili e quelli in sviluppo. */
  return (
    <>
      {mazzi.errore && <section className="band band-tight"><p className="error">{mazzi.errore}</p></section>}
      <ConPubblicita>
        {disponibili.map((m, i) => (
          <section key={m.id} className="band band-tight deck-layout">
            <div className="deck-spread" aria-hidden="true">
              {[CAMPIONE[i % 2 ? 1 : 0], "maj-06", "maj-19"].map((id) => <ImmagineCarta key={id} id={id} alt="" mazzo={cartellaDi(m)} />)}
            </div>
            <div>
              <span className="available">{k.disponibile}</span>
              <h2 className="section-title">{m.nome}</h2>
              <p className="section-intro">{m.descrizione ?? (m.predefinito ? k.thoth_intro : "")}</p>
              {m.predefinito && <p className="small muted">{k.incluso}</p>}
              <LinkV2 className="button" href={R.mazzo(m.slug)}>{f(k.entra, { mazzo: m.nome })}</LinkV2>
            </div>
          </section>
        ))}
        <section key="in-sviluppo" className="band band-tight">
          <p className="eyebrow">{k.in_sviluppo}</p>
          <div className="difference-grid even">
            {k.futuri.map((x) => (
              <article key={x.nome} className="difference">
                <span aria-hidden="true">{x.simbolo}</span>
                <h3>{x.nome}</h3>
                <p><span className="available planned" style={{ margin: "0 0 .6rem", display: "inline-flex", fontSize: ".66rem" }}>{k.pianificato}</span></p>
                <p>{k.futuro_testo}</p>
              </article>
            ))}
          </div>
          <div className="share-band" style={{ marginTop: ".7rem" }}>
            <div><h2 className="section-title" style={{ fontSize: "clamp(1.5rem, 2.6vw, 2.2rem)" }}>{k.voto_titolo}</h2><p>{k.voto_testo}</p></div>
            <div><LinkV2 className="button button-quiet" href={R.voto}>{k.voto_cta}</LinkV2></div>
          </div>
        </section>
      </ConPubblicita>
    </>
  );
}

export function SchedaMazzo({ slug }: { slug: string }) {
  const { t } = useLingua();
  const k = t.mazzi;
  const mazzi = useMazzi();
  if (mazzi.errore) return <section className="band band-tight"><p className="error">{mazzi.errore}</p></section>;
  if (!mazzi.dati) return <section className="band band-tight"><p className="muted">{t.comune.carica}</p></section>;
  const m = mazzi.dati.find((x) => x.slug === slug);
  if (!m) {
    return (
      <section className="band band-tight">
        <p className="section-intro">{k.non_trovato}</p>
        <LinkV2 className="button button-quiet" href={R.mazzi}>{t.comune.nav_mazzi}</LinkV2>
      </section>
    );
  }
  const cartella = cartellaDi(m);
  const leggiQui = m.predefinito ? `${R.leggi}?deck=${m.slug}` : `${R.leggi}?deck=${m.slug}&source=deck`;
  return (
    <>
      <section className="subhero subhero-compact">
        <span className="available">{k.disponibile}</span>
        <p className="eyebrow">{f(k.mazzo_eyebrow, { mazzo: m.nome })}</p>
        <h1 className="display">{m.predefinito ? k.thoth_titolo : m.nome}</h1>
        <p className="section-intro">{m.predefinito ? k.thoth_intro : (m.descrizione ?? k.altro_titolo)}</p>
      </section>
      {/* Gli spazi pubblicitari (spenti per default): dopo la presentazione e dopo il campione delle carte. */}
      <ConPubblicita>
        <section key="mazzo" className="band band-tight deck-layout">
          <div className="deck-spread" aria-hidden="true">
            {["maj-02", "maj-06", "maj-17"].map((id) => <ImmagineCarta key={id} id={id} alt="" mazzo={cartella} />)}
          </div>
          <div>
            <h2 className="section-title">{k.slogan}</h2>
            <p className="section-intro">{k.slogan_testo}</p>
            <div className="minor-cta">
              <LinkV2 href={leggiQui} data-an="deck_viewed" data-an-mazzo={m.slug}>{k.cta_leggi}</LinkV2>
              <LinkV2 href={R.carte}>{k.cta_carte}</LinkV2>
              <LinkV2 href={`${R.fisica}?deck=${m.slug}`}>{k.cta_fisica}</LinkV2>
              <LinkV2 href={R.negozio}>{k.cta_negozio}</LinkV2>
            </div>
            <StampaMazzo mazzo={m} />
          </div>
        </section>
        <section key="campione" className="band band-tight">
          <p className="eyebrow">{k.campione}</p>
          <div className="cards-grid">
            {CAMPIONE.map((id) => (
              <LinkV2 key={id} className="card-tile" href={R.carta(id)}>
                <ImmagineCarta id={id} alt="" mazzo={cartella} />
              </LinkV2>
            ))}
          </div>
        </section>
      </ConPubblicita>
    </>
  );
}

/** Il riquadro pubblico del voto (chi non ha un account): l'ultimo risultato, e l'invito ad accedere. */
export function RiepilogoVoto() {
  const { t } = useLingua();
  const k = t.mazzi;
  const riepilogo = useCarica(votoHome, [], { pubblico: true, iniziale: P.voto() });
  const r = riepilogo.dati?.risultato_recente;
  if (!r || r.candidati.length === 0) return null;
  return (
    <div className="panel">
      <h2>{k.voto_ultimo}</h2>
      <ul className="list-plain">
        {r.candidati.map((c) => (
          <li key={c.nome} className="memory-entry">
            <h3>{c.nome}</h3>
            <CampioniVoto nome={c.nome} campioni={c.campioni} />
            <div className="stat-bar" role="img" aria-label={f(k.voto_percentuale, { n: c.percentuale })}>
              <span style={{ width: `${c.percentuale}%` }} />
            </div>
            <p className="small">{f(k.voto_percentuale, { n: c.percentuale })}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** «Stampa i tuoi Tarocchi» (v8.5): il PDF da stampare nel carrello, poi al carrello. Gratuito, si scarica subito;
 * senza prezzo non si propone. */
function StampaMazzo({ mazzo }: { mazzo: Mazzo }) {
  const { t, locale, prefissoIt } = useLingua();
  const k = t.mazzi;
  const carrello = useCarrello();
  const router = useRouter();
  if (mazzo.prezzo_stampa == null) return null;
  if (mazzo.prezzo_stampa === 0) {
    return (
      <a className="button button-brass" style={{ marginTop: ".5rem" }} href={urlPdfGratuito(mazzo.slug)} download data-an="deck_pdf_viewed">
        {k.stampa_cta} · {t.negozio.pdf_gratis}
      </a>
    );
  }
  const prezzo = mazzo.prezzo_stampa_scontato ?? mazzo.prezzo_stampa;
  return (
    <button type="button" className="button button-brass" style={{ marginTop: ".5rem" }}
      data-an="carrello_aggiunto" data-an-mazzo={mazzo.slug} data-an-tipo="pdf"
      onClick={() => { carrello.aggiungi(mazzo.id, "pdf"); router.push(indirizzoV2(R.carrello, prefissoIt)); }}>
      {k.stampa_cta} · {euro(prezzo, mazzo.valuta, locale)}
    </button>
  );
}
