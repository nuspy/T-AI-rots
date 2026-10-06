/// v9.5, la traduzione automatica dei contenuti sul telefono (Google ML Kit, `google_mlkit_translation`): un modello per
/// lingua (circa 30 MB), scaricato una volta e poi usato senza rete. Il testo non esce dal telefono. Gli articoli, le
/// carte e le stese esistono in inglese (carte e stese anche in italiano): li si traduce nella lingua di lettura scelta
/// al primo avvio (`lingua_contenuti.dart`). In inglese non si scarica nulla.
///
/// [MotoreTraduzione] è l'interfaccia; [MotoreMlKit] quello vero (Android e iOS), [MotoreSpento] quello dove ML Kit
/// non c'è (i test, il desktop): non traduce e lo dice, e le pagine mostrano l'originale.
library;

import 'dart:io' show Platform;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mlkit_translation/google_mlkit_translation.dart';

/// Il motore della traduzione.
abstract interface class MotoreTraduzione {
  /// Vero se il telefono sa tradurre.
  bool get disponibile;

  /// Vero se il modello della lingua [lingua] è già sul telefono.
  Future<bool> modelloPresente(String lingua);

  /// Scarica il modello di [lingua] (anche senza Wi-Fi); falso se non riesce.
  Future<bool> scarica(String lingua);

  /// Traduce [testo] da [da] ad [a] (i due modelli devono esserci).
  Future<String> traduci(String testo, {required String da, required String a});
}

/// Le lingue di ML Kit (codici BCP-47 brevi), nell'ordine del pacchetto.
List<String> get lingueMlKit => [for (final l in TranslateLanguage.values) l.bcpCode];

/// Il motore vero, su ML Kit.
class MotoreMlKit implements MotoreTraduzione {
  final OnDeviceTranslatorModelManager _modelli = OnDeviceTranslatorModelManager();
  final Map<String, OnDeviceTranslator> _traduttori = {};

  @override
  bool get disponibile => true;

  @override
  Future<bool> modelloPresente(String lingua) => _modelli.isModelDownloaded(lingua);

  @override
  Future<bool> scarica(String lingua) async {
    if (await _modelli.isModelDownloaded(lingua)) return true;
    return _modelli.downloadModel(lingua, isWifiRequired: false);
  }

  @override
  Future<String> traduci(String testo, {required String da, required String a}) {
    final sorgente = TranslateLanguage.values.where((l) => l.bcpCode == da).firstOrNull;
    final meta = TranslateLanguage.values.where((l) => l.bcpCode == a).firstOrNull;
    if (sorgente == null || meta == null) return Future.value(testo);
    final traduttore = _traduttori.putIfAbsent(
      '$da>$a',
      () => OnDeviceTranslator(sourceLanguage: sorgente, targetLanguage: meta),
    );
    return traduttore.translateText(testo);
  }
}

/// Dove ML Kit non c'è: niente traduzione.
class MotoreSpento implements MotoreTraduzione {
  /// Il motore spento.
  const MotoreSpento();

  @override
  bool get disponibile => false;

  @override
  Future<bool> modelloPresente(String lingua) async => lingua == 'en';

  @override
  Future<bool> scarica(String lingua) async => lingua == 'en';

  @override
  Future<String> traduci(String testo, {required String da, required String a}) async => testo;
}

/// Il motore dell'app: ML Kit su Android e iOS, spento altrove (i test lo sostituiscono).
final motoreTraduzioneProvider = Provider<MotoreTraduzione>(
  (ref) => Platform.isAndroid || Platform.isIOS ? MotoreMlKit() : const MotoreSpento(),
);
