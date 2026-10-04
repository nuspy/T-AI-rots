/* I collegamenti verificati fra il sito e le app (v9, Fase 10): `/.well-known/assetlinks.json` (Android App Links) e
 * `/.well-known/apple-app-site-association` (iOS Universal Links). Li scrive l'API dai valori della console «App
 * mobili» (package e impronte dei certificati di firma; Team ID, bundle ID e percorsi): qui si servono alla radice del
 * sito, dove Android e Apple li cercano.
 *
 * Le regole di chi li legge: risposta 200 con `Content-Type: application/json`, **nessun reindirizzamento** (Android e
 * Apple non li seguono), https. Se l'API non risponde: 503 con `Retry-After`, non 404 — un 404 farebbe credere che
 * l'associazione non esista più. */

import { API_INTERNA } from "@/lib/server-api";

const JSON_ = { "Content-Type": "application/json" };

/** Il file dall'API (`/app/collegamenti/<nome>`), così com'è. */
export async function fileCollegamenti(nome: "assetlinks.json" | "apple-app-site-association"): Promise<Response> {
  let risposta: Response;
  try {
    risposta = await fetch(`${API_INTERNA}/app/collegamenti/${nome}`, {
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    return new Response("", { status: 503, headers: { ...JSON_, "Retry-After": "300" } });
  }
  if (!risposta.ok) return new Response("", { status: 503, headers: { ...JSON_, "Retry-After": "300" } });
  return new Response(await risposta.text(), { headers: { ...JSON_, "Cache-Control": "public, max-age=300" } });
}
