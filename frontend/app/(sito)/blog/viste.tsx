"use client";

/* Le viste dell'elenco del blog: ingresso, sezione, etichetta. Ricevono i dati già letti dal server. */

import Link from "@/app/(sito)/componenti/link";
import type {
  ArticoloBreve, DettaglioSezione, EtichettaConConteggio, NodoSezione,
} from "@/lib/blog";
import { nomeStesa } from "@/lib/i18n";
import { useLingua } from "@/lib/lingua";
import { indirizzo } from "@/lib/percorsi";
import type { Carta, Stesa } from "@/lib/api";
import { Faccia } from "../componenti/carta";
import { Involucro } from "../componenti/testata";
import { nomeCarta } from "@/lib/i18n";
import { AlberoSezioni, Briciole, Paginazione, SchedaArticolo } from "./componenti/elementi";
import stili from "./blog.module.css";
import stiliPagine from "../pagine.module.css";
import stiliStese from "../stese/stese.module.css";

function Ricerca({ q }: { q: string }) {
  const { t, lingua } = useLingua();
  return (
    <form className={stili.ricerca} action={indirizzo(lingua, "/blog")} method="get" role="search">
      <input type="search" name="q" defaultValue={q} placeholder={t.blog_cerca_segnaposto} aria-label={t.blog_cerca}
        maxLength={100} />
      <button type="submit">{t.blog_cerca_vai}</button>
    </form>
  );
}

function Laterale({ albero, etichette, corrente }: { albero: NodoSezione[]; etichette: EtichettaConConteggio[]; corrente?: string }) {
  const { t, lingua } = useLingua();
  return (
    <aside className={stili.laterale} aria-label={t.blog_sezioni}>
      <div>
        <h2>{t.blog_sezioni}</h2>
        <AlberoSezioni nodi={albero} corrente={corrente} />
      </div>
      {etichette.length > 0 && (
        <div>
          <h2>{t.blog_etichette}</h2>
          <ul className={stili.etichette}>
            {etichette.slice(0, 24).map((e) => (
              <li key={e.slug}><Link href={`/blog/tag/${e.slug}`} className={stili.etichetta}>{e.nome} <small>({e.n})</small></Link></li>
            ))}
          </ul>
        </div>
      )}
      <p><a href={indirizzo(lingua, "/blog/feed.xml")}>{t.blog_rss}</a></p>
    </aside>
  );
}

export function VistaBlog({
  q, pagina, pagine, totale, inEvidenza, articoli, albero, etichette,
}: {
  q: string;
  pagina: number;
  pagine: number;
  totale: number;
  inEvidenza: ArticoloBreve | null;
  articoli: ArticoloBreve[];
  albero: NodoSezione[];
  etichette: EtichettaConConteggio[];
}) {
  const { t } = useLingua();
  return (
    <Involucro pubblica larga>
      <div className={stili.pagina} style={{ maxWidth: 1180, margin: "0 auto", width: "100%" }}>
        <header className={stili.intestazione}>
          <h1>{t.blog_titolo}</h1>
          <p>{t.blog_sottotitolo}</p>
        </header>
        <Ricerca q={q} />
        <div className={stili.corpo}>
          <div>
            {q && <p role="status">{t.blog_risultati_per(q, totale)}</p>}
            {inEvidenza && (
              <section aria-label={t.blog_in_evidenza} style={{ marginBottom: 18 }}>
                <SchedaArticolo articolo={inEvidenza} grande />
              </section>
            )}
            {articoli.length > 0 ? (
              <section aria-label={t.blog_ultimi}>
                {!q && <h2 style={{ margin: "0 0 14px", fontSize: "1.3rem" }}>{t.blog_ultimi}</h2>}
                <div className={stili.griglia}>
                  {articoli.map((a) => <SchedaArticolo key={a.slug} articolo={a} />)}
                </div>
              </section>
            ) : (
              !inEvidenza && <p className={stili.vuoto}>{q ? t.blog_nessun_risultato : t.blog_nessun_articolo}</p>
            )}
            <Paginazione pagina={pagina} pagine={pagine} base="/blog" parametri={{ q }} />
          </div>
          <Laterale albero={albero} etichette={etichette} />
        </div>
      </div>
    </Involucro>
  );
}

/* Le carte o le stese di una sezione «carte» / «stese»: rimandano alle loro pagine. */
function ElementiCatalogo({ sezione }: { sezione: DettaglioSezione }) {
  const { t, lingua } = useLingua();
  if (sezione.tipo === "carte") {
    const carte = sezione.elementi as unknown as Carta[];
    return (
      <section aria-label={t.blog_carte_sezione}>
        <div className={stiliPagine.griglaCarte}>
          {carte.map((c) => (
            <Link key={c.id} href={`/carte/${c.slug ?? c.id}`} className={stiliPagine.cartaLink}>
              <div style={{ width: "100%", aspectRatio: "9 / 16", borderRadius: 8, overflow: "hidden" }}>
                <Faccia carta={c} />
              </div>
              {nomeCarta(c, lingua)}
            </Link>
          ))}
        </div>
      </section>
    );
  }
  const stese = sezione.elementi as unknown as Stesa[];
  return (
    <section aria-label={t.blog_stese_sezione}>
      <div className={stiliStese.griglia}>
        {stese.map((s) => (
          <Link key={s.id} href={`/stese/${s.slug ?? s.id}`} className={`pannello ${stiliStese.tessera}`}>
            <strong className={stiliStese.nome}>{nomeStesa(s, lingua)}</strong>
            <span className={stiliStese.meta}>{t.stesa_n_carte(s.posizioni.length)}</span>
            <p className={stiliStese.descrizione}>{s.descrizione}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}

export function VistaSezione({
  sezione, articoli, pagina, pagine, albero, etichette,
}: {
  sezione: DettaglioSezione;
  articoli: ArticoloBreve[];
  pagina: number;
  pagine: number;
  albero: NodoSezione[];
  etichette: EtichettaConConteggio[];
}) {
  const { t } = useLingua();
  const voci = [
    { href: "/blog", nome: t.blog_blog },
    ...sezione.briciole.map((b) => ({ href: `/blog/sezione/${b.slug}`, nome: b.nome })),
  ];
  return (
    <Involucro pubblica larga>
      <div className={stili.pagina} style={{ maxWidth: 1180, margin: "0 auto", width: "100%" }}>
        <div>
          <Briciole voci={voci} />
          <header className={stili.intestazione}>
            <h1>{sezione.nome}</h1>
            {sezione.descrizione && <p>{sezione.descrizione}</p>}
          </header>
        </div>
        <div className={stili.corpo}>
          <div style={{ display: "grid", gap: 28 }}>
            {sezione.figli.length > 0 && (
              <section aria-label={t.blog_sottosezioni}>
                <h2 style={{ margin: "0 0 10px", fontSize: "1.2rem" }}>{t.blog_sottosezioni}</h2>
                <AlberoSezioni nodi={sezione.figli} />
              </section>
            )}
            {(sezione.tipo === "carte" || sezione.tipo === "stese") && <ElementiCatalogo sezione={sezione} />}
            {articoli.length > 0 && (
              <section aria-label={t.blog_articoli_sezione}>
                <h2 style={{ margin: "0 0 14px", fontSize: "1.3rem" }}>{t.blog_articoli_sezione}</h2>
                <div className={stili.griglia}>
                  {articoli.map((a) => <SchedaArticolo key={a.slug} articolo={a} />)}
                </div>
                <Paginazione pagina={pagina} pagine={pagine} base={`/blog/sezione/${sezione.slug}`} />
              </section>
            )}
            {articoli.length === 0 && sezione.tipo !== "carte" && sezione.tipo !== "stese" && sezione.figli.length === 0 && (
              <p className={stili.vuoto}>{t.blog_nessun_articolo}</p>
            )}
          </div>
          <div className={stili.lateraleSoloDesktop}>
            <Laterale albero={albero} etichette={etichette} corrente={sezione.slug} />
          </div>
        </div>
      </div>
    </Involucro>
  );
}

export function VistaEtichetta({
  etichetta, slug, articoli, pagina, pagine, albero, etichette,
}: {
  etichetta: string;
  slug: string;
  articoli: ArticoloBreve[];
  pagina: number;
  pagine: number;
  albero: NodoSezione[];
  etichette: EtichettaConConteggio[];
}) {
  const { t } = useLingua();
  return (
    <Involucro pubblica larga>
      <div className={stili.pagina} style={{ maxWidth: 1180, margin: "0 auto", width: "100%" }}>
        <div>
          <Briciole voci={[{ href: "/blog", nome: t.blog_blog }, { href: "#", nome: `#${etichetta}` }]} />
          <header className={stili.intestazione}><h1>{etichetta}</h1></header>
        </div>
        <div className={stili.corpo}>
          <div>
            {articoli.length > 0 ? (
              <div className={stili.griglia}>{articoli.map((a) => <SchedaArticolo key={a.slug} articolo={a} />)}</div>
            ) : (
              <p className={stili.vuoto}>{t.blog_nessun_articolo}</p>
            )}
            <Paginazione pagina={pagina} pagine={pagine} base={`/blog/tag/${slug}`} />
          </div>
          <Laterale albero={albero} etichette={etichette} />
        </div>
      </div>
    </Involucro>
  );
}
