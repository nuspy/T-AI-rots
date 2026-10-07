/* Ciò che si chiede una volta sola prima della prima lettura, e poi si ricorda in un cookie per un anno:
 *
 * - l'età minima confermata («ho almeno N anni»): chi non ha un account la manda da sé con ogni lettura anonima, chi
 *   ce l'ha la porta nel profilo senza un altro dialogo se il server la chiede (es. dopo essere entrato);
 * - l'avvertenza accettata (i tarocchi non hanno validità scientifica, con la casella «ho capito»): il dialogo non si
 *   riapre più. Il testo resta comunque nella lettura salvata. */

const UN_ANNO = 365 * 24 * 60 * 60;
export const COOKIE_ETA = "tarots_eta";
export const COOKIE_AVVERTENZA = "tarots_avvertenza";

function leggi(nome: string): string | null {
  if (typeof document === "undefined") return null;
  const riga = document.cookie.split("; ").find((c) => c.startsWith(`${nome}=`));
  return riga ? decodeURIComponent(riga.slice(nome.length + 1)) : null;
}

function scrivi(nome: string, valore: string) {
  document.cookie = `${nome}=${encodeURIComponent(valore)}; Path=/; Max-Age=${UN_ANNO}; SameSite=Lax`;
}

/** Gli anni confermati («ho almeno N anni»), o null. */
export function etaConfermata(): number | null {
  const n = Number(leggi(COOKIE_ETA));
  return Number.isInteger(n) && n > 0 ? n : null;
}

export function ricordaEta(anni: number) {
  if ((etaConfermata() ?? 0) < anni) scrivi(COOKIE_ETA, String(anni));
}

export const avvertenzaAccettata = (): boolean => leggi(COOKIE_AVVERTENZA) === "1";

export const ricordaAvvertenza = () => scrivi(COOKIE_AVVERTENZA, "1");
