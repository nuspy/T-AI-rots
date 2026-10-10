/* Quando una domanda basta per partire (10/10/2026): almeno due parole, prima i pulsanti d'invio restano spenti. Le
 * scritture che non separano le parole (cinese, giapponese) contano i caratteri: ne bastano quattro. La stessa regola
 * nell'app (`mobile/lib/lettura/domanda.dart`). */

/** Se la domanda ha almeno due parole (con almeno una lettera ciascuna), o quattro caratteri in cinese o giapponese. */
export function domandaBasta(testo: string): boolean {
  const pulito = testo.trim();
  if (/[぀-ヿ㐀-鿿]/u.test(pulito)) return [...pulito.replace(/\s/gu, "")].length >= 4;
  return pulito.split(/\s+/u).filter((p) => /\p{L}/u.test(p)).length >= 2;
}
