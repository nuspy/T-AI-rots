"use client";

/* Le pagine d'errore della v2: la pagina che non esiste e l'interruzione imprevista. Dicono cosa è successo e
 * dove andare, con la voce della v2; nessun collegamento porta al sito. */

import LinkV2 from "@/v2/componenti/link";
import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";

function Uscite() {
  const { t } = useLingua();
  return (
    <div className="button-row" style={{ marginTop: ".55rem" }}>
      <LinkV2 className="button button-brass" href={R.leggi}>{t.home.cta_gratis}</LinkV2>
      <LinkV2 className="button button-quiet" href={R.home}>{t.comune.e_home}</LinkV2>
      <LinkV2 className="button button-quiet" href={R.esplora}>{t.comune.nav_esplora}</LinkV2>
    </div>
  );
}

export function NonTrovataV2() {
  const { t } = useLingua();
  const c = t.comune;
  return (
    <section className="subhero">
      <p className="eyebrow">{c.e404_eyebrow}</p>
      <h1 className="display">{c.e404_titolo}</h1>
      <p className="section-intro">{c.e404_testo}</p>
      <Uscite />
    </section>
  );
}

export function ErroreV2({ onRiprova }: { onRiprova: () => void }) {
  const { t } = useLingua();
  const c = t.comune;
  return (
    <section className="subhero" role="alert">
      <p className="eyebrow">{c.e500_eyebrow}</p>
      <h1 className="display">{c.e500_titolo}</h1>
      <p className="section-intro">{c.e500_testo}</p>
      <div className="button-row" style={{ marginTop: ".55rem" }}>
        <button type="button" className="button" onClick={onRiprova}>{c.riprova}</button>
      </div>
      <Uscite />
    </section>
  );
}
