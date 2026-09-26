/* Una versione breve del responso, per l'immagine da condividere e per la
 * descrizione dell'anteprima del link. Funzioni pure: girano sia nel browser sia sul
 * server (`generateMetadata` della pagina pubblica). */

/** Una versione breve del responso: le prime frasi della sezione finale (la
 *  tendenza), senza la formattazione Markdown. Il titolo della sezione lo scrive il
 *  modello nella lingua della risposta, quindi non lo si cerca per nome: si prende
 *  l'ultima sezione e se ne toglie la prima riga. */
export function sintesiDelResponso(responso: string | null, massimo: number): string {
  if (!responso) return "";
  const sezioni = responso.split(/^##\s+/m);
  const corpo = sezioni.length > 1 ? sezioni[sezioni.length - 1].split("\n").slice(1).join("\n") : responso;
  const pulito = corpo
    .replace(/^\s*[-*+>]\s+/gm, "")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/[#*_`~]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  if (!pulito) return "";
  const frasi = pulito.split(/(?<=[.!?。！？…])\s+/).filter(Boolean);
  let sintesi = "";
  for (const f of frasi) {
    const prova = sintesi ? `${sintesi} ${f}` : f;
    if (prova.length > massimo) break;
    sintesi = prova;
  }
  if (sintesi) return sintesi;
  /* Anche la prima frase è troppo lunga: si taglia a una parola. */
  const tagliata = pulito.slice(0, massimo);
  return `${tagliata.slice(0, Math.max(tagliata.lastIndexOf(" "), massimo * 0.6)).trimEnd()}…`;
}
