/* La verifica in due passaggi (app di autenticazione, codice a 6 cifre).
 *
 * È di Keycloak, non del sito: il sito non conserva niente e non vede i codici.
 * Il realm ha già il flusso giusto (`deploy/keycloak/README.md`): chi ha configurato
 * l'OTP lo usa a ogni accesso, gli altri no; agli amministratori è obbligatorio.
 * Qui c'è ciò che serve per **proporlo**:
 *
 *  - attivarlo: l'azione «Configure OTP» di Keycloak lanciata dall'app (parametro
 *    `kc_action=CONFIGURE_TOTP` della richiesta di accesso, vedi `Sessione.attiva2fa`):
 *    Keycloak mostra il QR code, chiede il primo codice e torna al sito;
 *  - sapere se è attivo: l'API dell'account di Keycloak (`/account/credentials`), che
 *    risponde al token dell'utente stesso. Se non risponde (token senza il ruolo
 *    dell'account, rete) lo stato è «ignota» e l'interfaccia lo dice, invece di
 *    indovinare. */

export const URL_REALM = `${
  process.env.NEXT_PUBLIC_KEYCLOAK_URL ?? "http://localhost:8080"
}/realms/${process.env.NEXT_PUBLIC_KEYCLOAK_REALM ?? "tarots"}`;

/* La console dell'account di Keycloak: da lì si aggiungono e si tolgono i dispositivi. */
export const URL_ACCOUNT = `${URL_REALM}/account/`;

export type Stato2fa = "attiva" | "spenta" | "ignota";

interface ContenitoreCredenziali {
  type?: string;
  userCredentialMetadatas?: unknown[];
}

export async function leggiStato2fa(token: string | null): Promise<Stato2fa> {
  if (!token) return "ignota";
  try {
    const risposta = await fetch(`${URL_REALM}/account/credentials`, {
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
    });
    if (!risposta.ok) return "ignota";
    const contenitori = (await risposta.json()) as ContenitoreCredenziali[];
    const otp = Array.isArray(contenitori) ? contenitori.find((c) => c.type === "otp") : undefined;
    if (!otp) return "ignota";
    return (otp.userCredentialMetadatas?.length ?? 0) > 0 ? "attiva" : "spenta";
  } catch {
    return "ignota";
  }
}
