"use client";

import { useLingua } from "@/v2/lib/lingua";
import { R } from "@/v2/lib/percorsi";
import LinkV2 from "./link";
import { SelettoreLingua } from "./testata";

export function Piede() {
  const { t } = useLingua();
  const c = t.comune;
  const colonne: { titolo: string; voci: [string, string][] }[] = [
    { titolo: c.piede_leggi, voci: [[R.leggi, c.piede_leggi_gratis], [R.fisica, c.piede_tue_carte], [R.giorno, c.piede_giorno], [R.storia, c.piede_storia]] },
    { titolo: c.piede_esplora, voci: [[R.mazzi, c.piede_mazzi], [R.carte, c.piede_carte], [R.stese, c.piede_stese], [R.blog, c.piede_diario], [R.voto, c.piede_voto]] },
    { titolo: c.piede_info, voci: [[R.prezzi, c.piede_prezzi], [R.negozio, c.piede_negozio], [R.privacy, c.piede_privacy]] },
  ];
  return (
    <footer className="site-footer">
      <section>
        <LinkV2 className="brand" href={R.home} aria-label={c.aria_home}>
          <span className="brand-mark" aria-hidden="true">✦</span>
          <span>TAROTS <em>chat</em></span>
        </LinkV2>
        <p>{c.piede_motto}</p>
        <div className="footer-lang"><SelettoreLingua /></div>
      </section>
      {colonne.map((col) => (
        <section key={col.titolo}>
          <h2>{col.titolo}</h2>
          <ul>
            {col.voci.map(([href, testo]) => <li key={href}><LinkV2 href={href}>{testo}</LinkV2></li>)}
          </ul>
        </section>
      ))}
      <p className="footer-note">{c.piede_avvertenza}</p>
    </footer>
  );
}
