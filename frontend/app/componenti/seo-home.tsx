import type { Carta, Stesa } from "@/lib/api";
import type { ArticoloBreve } from "@/lib/blog";
import type { LinguaPubblica } from "@/lib/percorsi";
import { HOME } from "@/lib/seo-testi";
import Link from "./link";
import stili from "./seo-home.module.css";

/* Il testo della soglia per chi cerca: come funziona una lettura, perché il Tarocco di Thoth, i collegamenti a
 * carte, stese e articoli, e le domande più frequenti. Scritto dal server, nella lingua dell'indirizzo, sotto la
 * parte animata: chi guarda solo la soglia non lo nota, chi scorre trova risposte. Tutti i collegamenti sono a
 * indirizzi canonici (con lo slug), così i motori di ricerca seguono i link interni senza reindirizzamenti. */

export function SezioniSeo({
  lingua, carte, stese, articoli,
}: {
  lingua: LinguaPubblica;
  carte: Carta[];
  stese: Stesa[];
  articoli: ArticoloBreve[];
}) {
  const maggiori = carte.filter((c) => c.arcano === "maggiore");
  const domande = HOME.domande(lingua);
  return (
    <div className={stili.sezioni} lang={lingua}>
      {/* «Come funziona» è già in soglia.tsx, come infografica: qui sarebbe un doppione dello stesso testo. */}

      <section aria-labelledby="home-esplora">
        <h2 id="home-esplora">{HOME.h2Esplora(lingua)}</h2>
        <div className={stili.colonne}>
          <div>
            <h3>{lingua === "it" ? "Gli Arcani maggiori" : "The Major Arcana"}</h3>
            <div className={stili.mattonelleTesto}>
              {maggiori.map((c) => (
                <Link key={c.id} href={`/carte/${c.slug ?? c.id}`} className={stili.mattonellaTesto}>
                  {c.nome ?? c.nome_it}
                </Link>
              ))}
            </div>
            <p><Link href="/carte">{lingua === "it" ? "Tutte le 78 carte" : "All 78 cards"} →</Link></p>
          </div>
          <div>
            <h3>{lingua === "it" ? "Le stese" : "Tarot spreads"}</h3>
            <div className={stili.mattonelleTesto}>
              {stese.map((s) => (
                <Link key={s.id} href={`/stese/${s.slug ?? s.id}`} className={stili.mattonellaTesto}>{s.nome}</Link>
              ))}
            </div>
            <p><Link href="/stese">{lingua === "it" ? "Tutte le stese" : "All spreads"} →</Link></p>
          </div>
        </div>
      </section>

      {articoli.length > 0 && (
        <section aria-labelledby="home-blog">
          <h2 id="home-blog">{lingua === "it" ? "Dal blog" : "From the blog"}</h2>
          <ul className={stili.articoli}>
            {articoli.map((a) => (
              <li key={a.slug} className="pannello">
                <Link href={`/blog/${a.slug}`}><strong>{a.titolo}</strong></Link>
                {a.estratto && <p>{a.estratto}</p>}
              </li>
            ))}
          </ul>
          <p><Link href="/blog">{lingua === "it" ? "Tutti gli articoli" : "All articles"} →</Link></p>
        </section>
      )}

      <section aria-labelledby="home-domande">
        <h2 id="home-domande">{HOME.h2Domande(lingua)}</h2>
        <div className={stili.domande}>
          {domande.map((d) => (
            <details key={d.d}>
              <summary>{d.d}</summary>
              <p>{d.r}</p>
            </details>
          ))}
        </div>
      </section>
    </div>
  );
}
