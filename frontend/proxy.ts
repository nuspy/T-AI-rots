/* Il proxy: da indirizzo visibile a pagina, e la lingua.
 *
 * `/cards/the-star` è la pagina `app/carte/[id]`, in inglese; `/it/carte/la-stella` è la stessa pagina in
 * italiano; il vecchio `/carte/…` senza prefisso porta all'italiano con un reindirizzamento permanente. La
 * corrispondenza sta in `lib/percorsi.ts`.
 *
 * La lingua e il fatto che la pagina sia pubblica viaggiano in due intestazioni della richiesta (`x-lang`,
 * `x-pubblica`): il layout le legge per scrivere `<html lang>` e per far partire l'interfaccia nella lingua
 * dell'indirizzo — già sul server, così chi guarda l'HTML (un motore di ricerca) trova il testo giusto. */

import { NextResponse, type NextRequest } from "next/server";
import { risolvi } from "./lib/percorsi";

export function proxy(richiesta: NextRequest) {
  const { pathname } = richiesta.nextUrl;
  const r = risolvi(pathname);

  if (r.reindirizza) {
    const url = richiesta.nextUrl.clone();
    url.pathname = r.reindirizza;
    return NextResponse.redirect(url, 308);
  }

  const intestazioni = new Headers(richiesta.headers);
  intestazioni.set("x-lang", r.lingua);
  intestazioni.set("x-pubblica", r.pubblica ? "1" : "0");

  if (r.interno !== pathname) {
    const destinazione = richiesta.nextUrl.clone();
    destinazione.pathname = r.interno;
    return NextResponse.rewrite(destinazione, { request: { headers: intestazioni } });
  }
  return NextResponse.next({ request: { headers: intestazioni } });
}

/* Ovunque tranne i file statici. `feed.xml` è un'eccezione: è un percorso del sito, in due lingue. */
export const config = {
  matcher: [
    "/((?!_next/|.*\\.(?:png|jpe?g|gif|webp|avif|svg|ico|css|js|map|txt|woff2?|json|xml|webmanifest)$).*)",
    "/blog/feed.xml",
    "/it/blog/feed.xml",
  ],
};
