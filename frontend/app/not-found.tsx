/* La pagina che si vede quando l'indirizzo non esiste: lo stesso vestito del sito, non la pagina bianca di
 * Next.js, con qualche collegamento per ripartire invece del solo «torna alla home». Componente server: la
 * lingua si legge dall'intestazione che il proxy scrive (`lib/lingua-server.ts`), come le altre pagine
 * pubbliche; `Link` sceglie da sé l'indirizzo giusto lato client, come ovunque nel sito. */

import Link from "./componenti/link";
import { Involucro } from "./componenti/testata";
import { dizionario } from "@/lib/i18n";
import { linguaPagina } from "@/lib/lingua-server";
import stili from "./errore.module.css";

export default async function NonTrovata() {
  const lingua = await linguaPagina();
  const t = dizionario(lingua);
  const voci = [
    { href: "/", etichetta: t.marchio },
    { href: "/leggi", etichetta: t.nav_leggi },
    { href: "/carte", etichetta: t.nav_carte },
    { href: "/stese", etichetta: t.nav_stese },
    { href: "/blog", etichetta: t.nav_blog },
  ];
  return (
    <Involucro pubblica titolo={t.errore_404_titolo} sottotitolo={t.errore_404_testo}>
      <div className={`pannello ${stili.suggerimenti}`}>
        {voci.map((v) => (
          <Link key={v.href} href={v.href} className="bottone-secondario">{v.etichetta}</Link>
        ))}
      </div>
    </Involucro>
  );
}
