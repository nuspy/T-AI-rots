/* Le carte dei mazzi caricati dalla console: `/cards/<slug>/<id>.webp`.
 *
 * I file in `public/` vincono sempre su questa rotta: il Thoth (`/cards/maj-00.webp`) e i mazzi installati come file
 * (`/cards/lovers/maj-00.webp`) non passano mai di qui. Arriva qui soltanto un mazzo che il sito non ha fra i suoi
 * file: allora le immagini stanno nel database e le serve l'API (`GET /decks/{slug}/cards/{id}.webp`), e questa rotta
 * le inoltra con le stesse intestazioni (cache, ETag; il 304 passa com'è). Così ogni pagina, la lettura, la galleria,
 * l'immagine di condivisione e il PDF continuano a chiedere lo stesso indirizzo, e un mazzo nuovo si vede subito,
 * senza ricostruire il sito. */

import { API_INTERNA } from "@/lib/server-api";

const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const FILE = /^[a-z0-9-]{1,30}\.webp$/;
const INOLTRATE = ["content-type", "cache-control", "etag", "x-content-type-options"];

function nonTrovata(): Response {
  return new Response("Not found", { status: 404, headers: { "Cache-Control": "public, max-age=60" } });
}

export async function GET(richiesta: Request, { params }: { params: Promise<{ id: string; file: string }> }) {
  const { id: slug, file } = await params;
  if (!SLUG.test(slug) || slug.length > 40 || !FILE.test(file)) return nonTrovata();

  const versione = new URL(richiesta.url).searchParams.get("v");
  const indirizzo = `${API_INTERNA}/decks/${slug}/cards/${file}${versione ? `?v=${encodeURIComponent(versione)}` : ""}`;
  const daInoltrare = new Headers();
  const etag = richiesta.headers.get("if-none-match");
  if (etag) daInoltrare.set("If-None-Match", etag);

  let risposta: Response;
  try {
    risposta = await fetch(indirizzo, { headers: daInoltrare, cache: "no-store", signal: AbortSignal.timeout(10_000) });
  } catch {
    return new Response("Bad gateway", { status: 502, headers: { "Cache-Control": "no-store" } });
  }
  if (risposta.status === 404) return nonTrovata();
  if (risposta.status !== 200 && risposta.status !== 304) {
    return new Response("Bad gateway", { status: 502, headers: { "Cache-Control": "no-store" } });
  }
  const intestazioni = new Headers();
  for (const nome of INOLTRATE) {
    const valore = risposta.headers.get(nome);
    if (valore) intestazioni.set(nome, valore);
  }
  return new Response(risposta.status === 304 ? null : risposta.body, { status: risposta.status, headers: intestazioni });
}
