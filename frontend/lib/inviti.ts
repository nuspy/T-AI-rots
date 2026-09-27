/* Il codice d'invito nell'indirizzo (`?invito=CODICE`): si ricorda fino alla registrazione, poi si riscatta da
 * solo al primo accesso (`app/componenti/riscatto-invito.tsx`), sullo stesso schema di `lib/condivisione.ts` per
 * l'origine di una condivisione. */

const CHIAVE_INVITO = "invito";

export function salvaInvito(codice: string): void {
  try {
    window.localStorage.setItem(CHIAVE_INVITO, codice.toUpperCase());
  } catch {
    /* archiviazione non disponibile: il codice si scrive a mano in profilo */
  }
}

export function leggiInvito(): string | null {
  try {
    return window.localStorage.getItem(CHIAVE_INVITO);
  } catch {
    return null;
  }
}

export function dimenticaInvito(): void {
  try {
    window.localStorage.removeItem(CHIAVE_INVITO);
  } catch {
    /* niente da fare */
  }
}
