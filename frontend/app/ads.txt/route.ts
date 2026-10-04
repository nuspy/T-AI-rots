/* `/ads.txt`: chi può vendere annunci su questo sito (IAB Tech Lab). La riga di Google AdSense nasce dall'ID editore
 * impostato in console (Advertisements → Google Ads) e la scrive l'API (`/ads.txt`): qui la si serve alla radice del
 * sito, dove Google la cerca per verificare il sito. Senza ID editore: 404. Se l'API non risponde: 503, non 404 —
 * un 404 durante un disservizio farebbe credere a Google che il file non esista più. */

import { API_INTERNA } from "@/lib/server-api";

export const dynamic = "force-dynamic";

const TESTO = { "Content-Type": "text/plain; charset=utf-8" };

export async function GET() {
  let risposta: Response;
  try {
    risposta = await fetch(`${API_INTERNA}/ads.txt`, { cache: "no-store", signal: AbortSignal.timeout(5000) });
  } catch {
    return new Response("", { status: 503, headers: { ...TESTO, "Retry-After": "300" } });
  }
  if (risposta.status === 404) {
    return new Response("", { status: 404, headers: { ...TESTO, "Cache-Control": "public, max-age=60" } });
  }
  if (!risposta.ok) return new Response("", { status: 503, headers: { ...TESTO, "Retry-After": "300" } });
  return new Response(await risposta.text(), { headers: { ...TESTO, "Cache-Control": "public, max-age=300" } });
}
