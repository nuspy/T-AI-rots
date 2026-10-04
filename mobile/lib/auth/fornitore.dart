/// Chi parla con Keycloak: l'interfaccia ([FornitoreOAuth]) e la versione vera con `flutter_appauth`.
///
/// L'interfaccia esiste per i test (un fornitore finto, senza browser né Keycloak) e per tenere `flutter_appauth`
/// in un solo file.
library;

import 'package:dio/dio.dart';
import 'package:flutter_appauth/flutter_appauth.dart';

import 'configurazione.dart';

/// I token di una sessione.
class Credenziali {
  /// I token ricevuti da Keycloak.
  const Credenziali({required this.accessToken, required this.scadenza, this.refreshToken, this.idToken});

  /// Il token d'accesso (Bearer).
  final String accessToken;

  /// Quando scade il token d'accesso.
  final DateTime scadenza;

  /// Il refresh token (offline): va nella cassaforte del sistema.
  final String? refreshToken;

  /// L'id token: serve al logout.
  final String? idToken;

  /// Vero se il token d'accesso scade entro [margine].
  bool scadeEntro(Duration margine, DateTime adesso) => !scadenza.isAfter(adesso.add(margine));
}

/// L'accesso non è riuscito o è stato annullato.
class ErroreAccesso implements Exception {
  /// Con il motivo.
  const ErroreAccesso(this.motivo, {this.annullato = false});

  /// Il motivo, per i log.
  final String motivo;

  /// Chi accedeva ha chiuso la pagina del social.
  final bool annullato;

  @override
  String toString() => 'ErroreAccesso($motivo)';
}

/// Le tre operazioni con Keycloak.
abstract interface class FornitoreOAuth {
  /// Apre la pagina del social (`kc_idp_hint`) nel browser di sistema e scambia il codice con i token (PKCE).
  Future<Credenziali> entra(ConfigAccesso config, {String? lingua});

  /// Un token d'accesso nuovo dal refresh token.
  Future<Credenziali> rinnova(ConfigAccesso config, String refreshToken);

  /// Revoca il refresh token e chiude la sessione di Keycloak. Non solleva: si esce comunque.
  Future<void> esci(ConfigAccesso config, {String? refreshToken, String? idToken});
}

/// Il fornitore vero: `flutter_appauth` (AppAuth-Android e AppAuth-iOS).
class FornitoreAppAuth implements FornitoreOAuth {
  /// Con il plugin e un client HTTP per la revoca.
  FornitoreAppAuth({FlutterAppAuth? appAuth, Dio? http})
    : _appAuth = appAuth ?? const FlutterAppAuth(),
      _http = http ?? Dio();

  final FlutterAppAuth _appAuth;
  final Dio _http;

  Credenziali _da(TokenResponse r, {String? refreshPrecedente}) {
    final accesso = r.accessToken;
    if (accesso == null) throw const ErroreAccesso('Keycloak non ha mandato il token d\'accesso');
    return Credenziali(
      accessToken: accesso,
      scadenza: r.accessTokenExpirationDateTime ?? DateTime.now().add(const Duration(minutes: 5)),
      refreshToken: r.refreshToken ?? refreshPrecedente,
      idToken: r.idToken,
    );
  }

  @override
  Future<Credenziali> entra(ConfigAccesso config, {String? lingua}) async {
    try {
      final r = await _appAuth.authorizeAndExchangeCode(
        AuthorizationTokenRequest(
          config.clientId,
          config.redirect,
          issuer: config.issuer,
          scopes: config.scope,
          allowInsecureConnections: config.insicuro,
          additionalParameters: {'kc_idp_hint': config.idpHint, 'ui_locales': ?lingua},
        ),
      );
      return _da(r);
    } on FlutterAppAuthUserCancelledException {
      throw const ErroreAccesso('accesso annullato', annullato: true);
    } on FlutterAppAuthPlatformException catch (e) {
      throw ErroreAccesso('accesso non riuscito: ${e.code}');
    }
  }

  @override
  Future<Credenziali> rinnova(ConfigAccesso config, String refreshToken) async {
    try {
      final r = await _appAuth.token(
        TokenRequest(
          config.clientId,
          config.redirect,
          issuer: config.issuer,
          refreshToken: refreshToken,
          scopes: config.scope,
          allowInsecureConnections: config.insicuro,
        ),
      );
      return _da(r, refreshPrecedente: refreshToken);
    } on FlutterAppAuthPlatformException catch (e) {
      throw ErroreAccesso('rinnovo non riuscito: ${e.code}');
    }
  }

  @override
  Future<void> esci(ConfigAccesso config, {String? refreshToken, String? idToken}) async {
    // Prima la revoca del token offline (come il sito): chiudere la sessione di Keycloak non lo tocca.
    if (refreshToken != null) {
      try {
        await _http.post<void>(
          config.revoca,
          data: {'client_id': config.clientId, 'token': refreshToken, 'token_type_hint': 'refresh_token'},
          options: Options(contentType: Headers.formUrlEncodedContentType),
        );
      } on DioException {
        // Rete assente: meglio fuori con un token orfano che bloccati dentro.
      }
    }
    try {
      await _appAuth.endSession(
        EndSessionRequest(
          idTokenHint: idToken,
          postLogoutRedirectUrl: config.redirect,
          issuer: config.issuer,
          allowInsecureConnections: config.insicuro,
        ),
      );
    } on FlutterAppAuthPlatformException {
      // La pagina di uscita chiusa a metà: i token locali si cancellano comunque.
    }
  }
}
