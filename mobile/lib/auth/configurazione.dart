/// La configurazione dell'accesso: Keycloak con il client pubblico `tarot-mobile` (PKCE), e il social giusto per
/// ciascuna piattaforma con `kc_idp_hint` — **Google su Android, Apple su iOS** (decisione dell'operatore, 3/10).
///
/// Il client `tarot-mobile` lo crea la Fase 6 (realm e generatore): finché non c'è, l'accesso non si può provare dal
/// vivo; il modulo è pronto e i test lo verificano con dipendenze finte.
library;

import '../config.dart';

/// Il sistema operativo, per scegliere il social.
enum Piattaforma {
  /// Android: si entra con Google.
  android,

  /// iPhone e iPad: si entra con Apple.
  ios,
}

/// Come raggiungere Keycloak e con quale social.
class ConfigAccesso {
  /// Una configurazione.
  const ConfigAccesso({
    required this.issuer,
    required this.clientId,
    required this.redirect,
    required this.scope,
    required this.idpHint,
    this.insicuro = false,
  });

  /// La configurazione dell'app per [piattaforma], o `null` se Keycloak non è configurato (`KEYCLOAK_URL` vuoto).
  static ConfigAccesso? per(Piattaforma piattaforma) {
    if (Config.keycloakUrl.isEmpty) return null;
    final base = Config.keycloakUrl.endsWith('/')
        ? Config.keycloakUrl.substring(0, Config.keycloakUrl.length - 1)
        : Config.keycloakUrl;
    return ConfigAccesso(
      issuer: '$base/realms/${Config.keycloakRealm}',
      clientId: Config.keycloakClient,
      redirect: redirectApp,
      scope: scopeApp,
      idpHint: piattaforma == Piattaforma.android ? 'google' : 'apple',
      insicuro: Config.keycloakInsicuro,
    );
  }

  /// Lo schema dell'app (`chat.tarots.app`, uguale all'id): AndroidManifest e Info.plist lo dichiarano.
  static const String redirectApp = 'chat.tarots.app:/oauth2redirect';

  /// `offline_access`: il refresh token sopravvive alla chiusura dell'app (come la sessione ripresa del sito).
  static const List<String> scopeApp = ['openid', 'profile', 'email', 'offline_access'];

  /// L'emittente: `https://auth.tarots.chat/realms/tarots`.
  final String issuer;

  /// `tarot-mobile`.
  final String clientId;

  /// Dove Keycloak rimanda dopo l'accesso.
  final String redirect;

  /// Gli scope chiesti.
  final List<String> scope;

  /// `google` o `apple`: Keycloak salta la sua pagina e va dritto al social.
  final String idpHint;

  /// Keycloak in http (solo sviluppo).
  final bool insicuro;

  /// L'indirizzo per revocare un token (il logout vero, come nel sito).
  String get revoca => '$issuer/protocol/openid-connect/revoke';
}
