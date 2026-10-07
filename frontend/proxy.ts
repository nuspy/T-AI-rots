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

/* ---- v9.5: la prova della lettura in chat ----
 * `/read` (e `/it/read`) non è più una pagina: qui si sceglie la variante e si manda a `/read-chat` o `/read-classic`
 * con tutti i parametri (la domanda della home o dell'oracolo, la carta, la stesa, il mazzo, `?id=`…). Così ogni
 * link verso la lettura, interno o esterno (notifiche, email, QR, vecchi preferiti), segue la regola senza saperlo.
 * La scelta resta nel cookie per un anno; per chi ha un account la pagina la allinea a quella del profilo (la stessa
 * su tutti i dispositivi). Lo smistamento avviene prima della pagina: niente salti, nessuna pagina vista di `/read`. */
export const COOKIE_VARIANTE = "tarots_lettura";
const UN_ANNO = 365 * 24 * 60 * 60;
let percentuale: { valore: number; scade: number } | null = null;

/** Quante persone su cento ricevono la lettura in chat: dalla console (impostazioni pubbliche), ricordato 5 minuti;
 *  se l'API non risponde, 90. */
async function percentualeChat(): Promise<number> {
  if (percentuale && percentuale.scade > Date.now()) return percentuale.valore;
  let valore = percentuale?.valore ?? 90;
  try {
    const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";
    const r = await fetch(`${api}/impostazioni-pubbliche`, { signal: AbortSignal.timeout(1500) });
    if (r.ok) {
      const d = (await r.json()) as { lettura_chat_percentuale?: number };
      if (typeof d.lettura_chat_percentuale === "number") valore = d.lettura_chat_percentuale;
    }
  } catch {
    /* si tiene l'ultimo valore noto */
  }
  percentuale = { valore, scade: Date.now() + 5 * 60_000 };
  return valore;
}

async function smistaLettura(richiesta: NextRequest, lingua: string): Promise<NextResponse> {
  /* `?anteprima=chat|classica`: la versione scelta da un admin nel menu di «Inizia una lettura». Si mostra quella,
   * senza toccare il cookie (la prova resta com'era); il parametro resta, così la pagina non si riallinea al profilo. */
  const anteprima = richiesta.nextUrl.searchParams.get("anteprima");
  if (anteprima === "chat" || anteprima === "classica") {
    const url = richiesta.nextUrl.clone();
    url.pathname = `${lingua === "it" ? "/it" : ""}${anteprima === "chat" ? "/read-chat" : "/read-classic"}`;
    return NextResponse.redirect(url, 307);
  }
  const salvata = richiesta.cookies.get(COOKIE_VARIANTE)?.value;
  const variante = salvata === "chat" || salvata === "classica"
    ? salvata
    : Math.random() * 100 < (await percentualeChat()) ? "chat" : "classica";
  const url = richiesta.nextUrl.clone();
  url.pathname = `${lingua === "it" ? "/it" : ""}${variante === "chat" ? "/read-chat" : "/read-classic"}`;
  const risposta = NextResponse.redirect(url, 307);
  risposta.cookies.set(COOKIE_VARIANTE, variante, { maxAge: UN_ANNO, path: "/", sameSite: "lax" });
  return risposta;
}

export async function proxy(richiesta: NextRequest) {
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
  if (!nellaV1 && interno === "/read") return smistaLettura(richiesta, lingua);

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
