/* Come si scrivono importi e date in console.
 *
 * In un posto solo perché si ripetono su ogni pagina, e due formati diversi
 * per la stessa cifra — «12,00 €» qui, «12 €» là — fanno sospettare che i
 * numeri non siano gli stessi.
 */

const euro = new Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR" });

/** Centesimi → «12,90 €». Il backend conta in centesimi, sempre. */
export function soldi(centesimi: number | null | undefined, valuta = "EUR"): string {
  if (centesimi === null || centesimi === undefined) return "—";
  const formato =
    valuta.toUpperCase() === "EUR"
      ? euro
      : new Intl.NumberFormat("it-IT", { style: "currency", currency: valuta.toUpperCase() });
  return formato.format(centesimi / 100);
}

const dataOra = new Intl.DateTimeFormat("it-IT", {
  day: "2-digit",
  month: "2-digit",
  year: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});

const soloData = new Intl.DateTimeFormat("it-IT", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

export function quandoCompleto(iso: string | null | undefined): string {
  return iso ? dataOra.format(new Date(iso)) : "—";
}

export function giorno(iso: string | null | undefined): string {
  return iso ? soloData.format(new Date(iso)) : "—";
}

/** «12,90» → 1290. `null` se non è un importo: meglio rifiutare che
 *  indovinare, quando la cifra è un prezzo. */
export function centesimiDa(testo: string): number | null {
  const pulito = testo.trim().replace(/\s|€/g, "").replace(/\.(?=\d{3}(\D|$))/g, "").replace(",", ".");
  if (pulito === "") return null;
  const valore = Number(pulito);
  if (!Number.isFinite(valore) || valore < 0) return null;
  return Math.round(valore * 100);
}

/** 1290 → «12,90», per riempire un campo che poi si rilegge con `centesimiDa`. */
export function importoPerCampo(centesimi: number | null | undefined): string {
  if (centesimi === null || centesimi === undefined) return "";
  return (centesimi / 100).toFixed(2).replace(".", ",");
}
