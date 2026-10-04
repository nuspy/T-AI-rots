/* Il proxy: da indirizzo visibile a pagina, e la lingua.
 *
 * Il sito è la v2 (`app/(v2)`): `/cards/the-star` è la cartella `app/(v2)/cards/[id]` in inglese, `/it/carte/la-stella`
 * la stessa in italiano, `/card-of-the-day` la cartella `daily-card`; i vecchi indirizzi (`/leggi`, `/s/…`, `/v2/…`,
 * `/carte/…` senza `/it`) portano ai nuovi con un reindirizzamento permanente. La corrispondenza sta in
 * `lib/indirizzi.ts`.
 *
 * La v1 vive sotto `/old` (`app/(old)/old`, mappa in `lib/percorsi.ts`): funziona com'era, ma non si indicizza
 * (`X-Robots-Tag: noindex`).
 *
 * La lingua e il fatto che la pagina sia pubblica viaggiano in due intestazioni della richiesta (`x-lang`,
 * `x-pubblica`): il layout le legge per scrivere `<html lang>` e per far partire l'interfaccia nella lingua
 * dell'indirizzo — già sul server, così chi guarda l'HTML (un motore di ricerca) trova il testo giusto. */

import { NextResponse, type NextRequest } from "next/server";
import { risolvi as risolviSito } from "./lib/indirizzi";
import { VECCHIO, risolvi as risolviVecchio } from "./lib/percorsi";

const NOINDEX = "noindex, nofollow";

export function proxy(richiesta: NextRequest) {
  const { pathname } = richiesta.nextUrl;
  const nellaV1 = pathname === VECCHIO || pathname.startsWith(`${VECCHIO}/`);

  let lingua: string;
  let pubblica: boolean;
  let interno: string;
  let reindirizza: string | null;
  if (nellaV1) {
    const r = risolviVecchio(pathname);
    ({ lingua, pubblica, reindirizza } = r);
    interno = `${VECCHIO}${r.interno === "/" ? "" : r.interno}`;
  } else {
    ({ lingua, pubblica, interno, reindirizza } = risolviSito(pathname));
  }

  if (reindirizza && reindirizza !== pathname) {
    const url = richiesta.nextUrl.clone();
    url.pathname = reindirizza;
    return NextResponse.redirect(url, 308);
  }

  const intestazioni = new Headers(richiesta.headers);
  intestazioni.set("x-lang", lingua);
  intestazioni.set("x-pubblica", pubblica ? "1" : "0");

  let risposta: NextResponse;
  if (interno !== pathname) {
    const destinazione = richiesta.nextUrl.clone();
    destinazione.pathname = interno;
    risposta = NextResponse.rewrite(destinazione, { request: { headers: intestazioni } });
  } else {
    risposta = NextResponse.next({ request: { headers: intestazioni } });
  }
  if (nellaV1) risposta.headers.set("X-Robots-Tag", NOINDEX);
  return risposta;
}

/* Ovunque tranne i file statici e `/.well-known/` (i collegamenti verificati delle app: niente lingua, mai un
 * reindirizzamento). `feed.xml` è un'eccezione: è un percorso del sito, in due lingue. */
export const config = {
  matcher: [
    "/((?!_next/|\\.well-known/|.*\\.(?:png|jpe?g|gif|webp|avif|svg|ico|css|js|map|txt|woff2?|json|xml|webmanifest)$).*)",
    "/blog/feed.xml",
    "/it/blog/feed.xml",
    "/old/blog/feed.xml",
    "/old/it/blog/feed.xml",
  ],
};
