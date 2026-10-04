/// Dove sta il refresh token: nella cassaforte del sistema (Keychain su iOS, Keystore su Android) con
/// `flutter_secure_storage`, mai nelle preferenze in chiaro. Il token d'accesso resta solo in memoria.
library;

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Leggere, salvare e cancellare il refresh token.
abstract interface class Cassaforte {
  /// Il refresh token salvato, o `null`.
  Future<String?> leggi();

  /// Salva [refreshToken], o lo cancella se è `null`.
  Future<void> salva(String? refreshToken);
}

/// La cassaforte del sistema.
class CassaforteSistema implements Cassaforte {
  /// Con il plugin (sostituibile nei test).
  CassaforteSistema([FlutterSecureStorage? archivio]) : _archivio = archivio ?? const FlutterSecureStorage();

  static const String _chiave = 'tarots.refresh_token';
  final FlutterSecureStorage _archivio;

  @override
  Future<String?> leggi() => _archivio.read(key: _chiave);

  @override
  Future<void> salva(String? refreshToken) =>
      refreshToken == null ? _archivio.delete(key: _chiave) : _archivio.write(key: _chiave, value: refreshToken);
}

/// Una cassaforte in memoria, per i test.
class CassaforteMemoria implements Cassaforte {
  /// Con un token già salvato, se serve.
  CassaforteMemoria([this.valore]);

  /// Il token salvato.
  String? valore;

  @override
  Future<String?> leggi() async => valore;

  @override
  Future<void> salva(String? refreshToken) async => valore = refreshToken;
}
