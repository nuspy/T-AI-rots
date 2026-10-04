/// Le statistiche Google (GA4 attraverso Firebase Analytics), separate da quelle interne come nel sito: consenso
/// proprio (`google_analytics`), spente finché non arriva.
///
/// **Firebase non è ancora configurato** (mancano `android/app/google-services.json` e
/// `ios/Runner/GoogleService-Info.plist`): l'app compila e funziona lo stesso, l'inizializzazione fallisce con un
/// messaggio chiaro nel log e tutto resta spento. Come attivarlo: `mobile/LEGGIMI.md`, «Attivare Firebase».
///
/// Anche con Firebase configurato, la raccolta è spenta dal manifesto e dall'Info.plist
/// (`firebase_analytics_collection_enabled=false`) e si accende solo col consenso; niente identificativi pubblicitari
/// (né AD_ID né IDFA), niente schermate automatiche: le schermate si mandano a mano con il percorso del sito.
library;

import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

Future<bool>? _firebase;

/// Firebase, inizializzato una volta sola per tutta l'app (statistiche Google e notifiche, Fase 9). Falso se mancano
/// `google-services.json` / `GoogleService-Info.plist`: allora statistiche Google e notifiche restano spente.
Future<bool> avviaFirebase() => _firebase ??= () async {
  try {
    await Firebase.initializeApp();
    return true;
  } on Object catch (e) {
    debugPrint(
      'Firebase inattivo: mancano google-services.json (Android) o GoogleService-Info.plist (iOS), quindi le '
      'statistiche Google e le notifiche restano spente (le statistiche interne funzionano). Vedi mobile/LEGGIMI.md, '
      '«Attivare Firebase». Dettaglio: $e',
    );
    return false;
  }
}();

/// Le statistiche Google dell'app.
abstract interface class StatisticheGoogle {
  /// Prova a inizializzare Firebase (una volta, all'avvio).
  Future<void> avvia();

  /// Il consenso `google_analytics`: accende o spegne la raccolta.
  Future<void> consenso({required bool accettato});

  /// Una schermata, col percorso del sito.
  Future<void> schermata(String percorso);

  /// Un evento.
  Future<void> evento(String nome, [Map<String, Object>? parametri]);
}

/// Firebase Analytics.
class StatisticheFirebase implements StatisticheGoogle {
  FirebaseAnalytics? _analytics;
  bool _consenso = false;

  /// Vero se Firebase è inizializzato.
  bool get attiva => _analytics != null;

  @override
  Future<void> avvia() async {
    if (!await avviaFirebase()) return;
    try {
      final a = FirebaseAnalytics.instance;
      await a.setAnalyticsCollectionEnabled(false);
      await a.setConsent(
        analyticsStorageConsentGranted: false,
        adStorageConsentGranted: false,
        adUserDataConsentGranted: false,
        adPersonalizationSignalsConsentGranted: false,
      );
      _analytics = a;
      debugPrint('Firebase Analytics pronto: la raccolta parte solo col consenso «google_analytics».');
      if (_consenso) await consenso(accettato: true);
    } on Object catch (e) {
      debugPrint('Firebase Analytics non avviato: $e');
    }
  }

  @override
  Future<void> consenso({required bool accettato}) async {
    _consenso = accettato;
    final a = _analytics;
    if (a == null) return;
    await a.setConsent(
      analyticsStorageConsentGranted: accettato,
      adStorageConsentGranted: false,
      adUserDataConsentGranted: false,
      adPersonalizationSignalsConsentGranted: false,
    );
    await a.setAnalyticsCollectionEnabled(accettato);
  }

  @override
  Future<void> schermata(String percorso) async {
    final a = _analytics;
    if (a == null || !_consenso) return;
    await a.logScreenView(screenName: percorso, screenClass: 'TAROTSchat');
  }

  @override
  Future<void> evento(String nome, [Map<String, Object>? parametri]) async {
    final a = _analytics;
    if (a == null || !_consenso) return;
    await a.logEvent(name: nome, parameters: parametri);
  }
}

/// Le statistiche Google spente: nei test e dove Firebase non serve.
class StatisticheGoogleSpente implements StatisticheGoogle {
  @override
  Future<void> avvia() async {}

  @override
  Future<void> consenso({required bool accettato}) async {}

  @override
  Future<void> schermata(String percorso) async {}

  @override
  Future<void> evento(String nome, [Map<String, Object>? parametri]) async {}
}

/// Le statistiche Google dell'app (spente nei test).
final statisticheGoogleProvider = Provider<StatisticheGoogle>((ref) => StatisticheFirebase());
