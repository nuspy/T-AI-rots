/// Il codice d'invito e il collegamento condiviso da cui si arriva (`frontend/lib/inviti.ts`, `lib/condivisione.ts`,
/// `lib/riscatto-invito.tsx`, `lib/attribuzione.tsx` del sito), con le stesse chiavi:
///
/// - `?invito=CODICE` in un indirizzo (la home del sito lo legge, l'app lo legge a ogni rotta) si ricorda fino alla
///   registrazione e si riscatta da solo alla prima sessione (`POST /me/referral`);
/// - chi apre una lettura condivisa ricorda il collegamento per sette giorni (`ricordaOrigine`): se poi si iscrive, chi
///   l'ha condiviso riceve le sue letture in regalo (`POST /me/share-signup`).
/// Un rifiuto del server è definitivo e il ricordo si dimentica; un guasto di rete o del server si ritenta al prossimo
/// accesso.
library;

import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/visitatore.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../archivio.dart';

/// La chiave del codice d'invito (come il sito).
const String chiaveInvito = 'invito';

/// La chiave del collegamento condiviso da cui si arriva (come il sito).
const String chiaveOrigine = 'tarots.origine';

/// Quanto vale il ricordo del collegamento condiviso.
const Duration validitaOrigine = Duration(days: 7);

/// Ricorda il codice d'invito [codice] (in maiuscolo).
Future<void> salvaInvito(Archivio a, String codice) => a.scrivi(chiaveInvito, codice.trim().toUpperCase());

/// Il codice d'invito ricordato, se c'è (il profilo lo propone nel campo «Hai un codice?»).
String? leggiInvito(Archivio a) {
  final c = a.leggi(chiaveInvito);
  return c == null || c.isEmpty ? null : c;
}

/// Ricorda la lettura condivisa [token] appena aperta.
Future<void> ricordaOrigine(Archivio a, String token) =>
    a.scrivi(chiaveOrigine, jsonEncode({'token': token, 'quando': DateTime.now().millisecondsSinceEpoch}));

/// Il collegamento condiviso ricordato, se non è scaduto.
String? leggiOrigine(Archivio a) {
  try {
    final v = jsonDecode(a.leggi(chiaveOrigine) ?? 'null');
    if (v is! Map || v['token'] is! String || v['quando'] is! num) return null;
    final quando = DateTime.fromMillisecondsSinceEpoch((v['quando'] as num).toInt());
    if (DateTime.now().difference(quando) > validitaOrigine) {
      unawaited(a.scrivi(chiaveOrigine, null));
      return null;
    }
    return v['token'] as String;
  } on FormatException {
    return null;
  }
}

/// Alla prima sessione: il riscatto dell'invito e l'attribuzione dell'iscrizione, una volta per avvio.
class RiscattiAutomatici {
  /// Sui provider dell'app.
  RiscattiAutomatici(this._ref);

  final Ref _ref;
  bool _invitoTentato = false;
  bool _origineTentata = false;

  bool _definitivo(ErroreApi e) => e.stato > 0 && e.stato < 500 && e.stato != 401;

  /// C'è una sessione: si prova ciò che è ricordato.
  Future<void> prova() async {
    final a = _ref.read(archivioProvider);
    final api = _ref.read(apiProvider);
    final codice = leggiInvito(a);
    if (codice != null && !_invitoTentato) {
      _invitoTentato = true;
      try {
        await api.riscattaInvito(codice);
        await a.scrivi(chiaveInvito, null);
      } on ErroreApi catch (e) {
        if (_definitivo(e)) {
          await a.scrivi(chiaveInvito, null);
        } else {
          _invitoTentato = false;
        }
      }
    }
    final origine = leggiOrigine(a);
    if (origine != null && !_origineTentata) {
      _origineTentata = true;
      try {
        await api.attribuisciIscrizione(origine, _ref.read(visitatoreProvider)());
        await a.scrivi(chiaveOrigine, null);
      } on ErroreApi catch (e) {
        if (_definitivo(e)) {
          await a.scrivi(chiaveOrigine, null);
        } else {
          _origineTentata = false;
        }
      }
    }
  }
}

/// I riscatti automatici.
final riscattiProvider = Provider<RiscattiAutomatici>(RiscattiAutomatici.new);
