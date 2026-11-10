/// La configurazione dell'app, fissata alla compilazione con `--dart-define` (vedi LEGGIMI.md).
///
/// I valori predefiniti sono quelli dello sviluppo sull'emulatore Android: `10.0.2.2` è il PC che lo ospita, dove
/// girano l'API (:8100) e il sito (:3000). Per un telefono vero nella stessa rete si passa l'indirizzo del PC
/// (`--dart-define=API_URL=http://192.168.1.91:8100`), per la produzione quelli pubblici.
abstract final class Config {
  /// L'API FastAPI (`backend/tarot_core`).
  static const String apiUrl = String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8100');

  /// Il sito: le immagini delle carte (`/cards/<id>.webp`) e le pagine che l'app apre nel browser.
  static const String sitoUrl = String.fromEnvironment('SITO_URL', defaultValue: 'http://10.0.2.2:3000');

  /// Il sito che si vede nei collegamenti condivisi e negli inviti (`SITE_URL` del sito, `NEXT_PUBLIC_SITE_URL`): sempre
  /// quello pubblico, anche in sviluppo, perché i collegamenti escono dal telefono.
  static const String sitoPubblico = String.fromEnvironment('SITO_PUBBLICO', defaultValue: 'https://tarots.chat');

  /// Keycloak (`https://auth.tarots.chat`). Vuoto = accesso non configurato: l'app funziona da anonima.
  static const String keycloakUrl = String.fromEnvironment('KEYCLOAK_URL');

  /// Il realm di Keycloak, lo stesso del sito.
  static const String keycloakRealm = String.fromEnvironment('KEYCLOAK_REALM', defaultValue: 'tarots');

  /// Il client pubblico dell'app (PKCE), creato dalla Fase 6.
  static const String keycloakClient = String.fromEnvironment('KEYCLOAK_CLIENT_ID', defaultValue: 'tarot-mobile');

  /// Lo sviluppo contro un backend con `TAROT_AUTH_DISABLED=true`: come `NEXT_PUBLIC_AUTH_DISABLED` del sito, l'app
  /// si comporta da utente entrato («Sviluppo») senza token, e il backend usa il suo utente di sviluppo.
  static const bool authDisattivata = bool.fromEnvironment('AUTH_DISATTIVATA');

  /// Vero nelle build di sviluppo che parlano con un Keycloak in http (solo in locale).
  static const bool keycloakInsicuro = bool.fromEnvironment('KEYCLOAK_INSICURO');

  /// Fase 9: si compra negli store (Google Play, App Store). Con `false` l'app usa il pagamento web nel browser, come
  /// nella Fase 8 (utile in sviluppo su un emulatore senza Play Store).
  static const bool acquistiStore = bool.fromEnvironment('ACQUISTI_STORE', defaultValue: true);

  /// La versione dell'app che compare nell'agente (`User-Agent`) delle statistiche.
  static const String versione = String.fromEnvironment('VERSIONE_APP', defaultValue: '1.0.0');

  /// Google Play RSA public key per la verifica degli acquisti in-app (Fase 9).
  static const String playPublicKey = String.fromEnvironment('PLAY_PUBLIC_KEY',
      defaultValue: 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzS/RaasS00iwTODrY1sMS2mLY1szh/E7P1kAmR74dntxE9cfvkmQ5akZIx9vw85xI8eZZnPFplphUW1UgiR0tmeT73Qzx1AZbFNGsg+oPWyaI4hIyK9fuZ2cdAdsvdN47XAgQELdlN48Ggz3GUcOydXj7VO6nJsjOuPPcykhXZgyc1aa2i44w00X4MLLOpo+vJvRLdi82nhGvhCbd366IHGUIQycdoGw3mPfOrpCRVjSQn3XRMnoce5rO0DDnhb0iYoba5LUy9I47susi5y/aNk5h6jkc+0Ep7eGE1eQaabWriBNRI8pxjYgFLJVs8S3J9Lf0jn7yos6OGDc5vVkawIDAQAB');
}
