/// Le letture dell'account per le pagine del profilo, come gli `useCarica(...)` del sito: ogni provider si rilegge con
/// `ref.invalidate` (il `ricarica()` del sito) e si scarta quando la pagina si chiude.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../auth/sessione.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../modelli/privacy.dart';

bool _dentro(Ref ref) => ref.watch(sessioneProvider.select((s) => s.autenticata));

/// `GET /me/abbonamento?lang=`.
final mioAbbonamentoProvider = FutureProvider.autoDispose<MioAbbonamento?>((ref) async {
  final lingua = ref.watch(linguaProvider);
  if (!_dentro(ref)) return null;
  return ref.read(apiProvider).mioAbbonamento(lingua);
});

/// `GET /me/privacy`: le date dei consensi, l'ultima esportazione, la cancellazione.
final statoPrivacyProvider = FutureProvider.autoDispose<StatoPrivacy?>((ref) async {
  if (!_dentro(ref)) return null;
  return ref.read(apiProvider).privacy();
});

/// `GET /consenso`: tutte le scelte di questa persona (anche quelle che riguardano solo l'account).
final consensiAccountProvider = FutureProvider.autoDispose<Map<String, String?>>((ref) {
  ref.watch(sessioneProvider.select((s) => s.autenticata));
  return ref.read(apiProvider).consensi();
});

/// `GET /me/orders`.
final ordiniProvider = FutureProvider.autoDispose<List<Ordine>>((ref) async {
  if (!_dentro(ref)) return const [];
  return ref.read(apiProvider).ordini();
});

/// `GET /me/addresses`.
final indirizziProvider = FutureProvider.autoDispose<List<Indirizzo>>((ref) async {
  if (!_dentro(ref)) return const [];
  return ref.read(apiProvider).indirizzi();
});

/// `GET /me/statistiche`: l'opposizione al legame fra visite e account.
final opposizioneProvider = FutureProvider.autoDispose<bool?>((ref) async {
  if (!_dentro(ref)) return null;
  return ref.read(apiProvider).opposizioneStatistiche();
});

/// `GET /me/decks`: i mazzi che si possono già leggere.
final mieiMazziProvider = FutureProvider.autoDispose<List<int>>((ref) async {
  if (!_dentro(ref)) return const [];
  return ref.read(apiProvider).mieiMazzi();
});

/// `GET /privacy/titolare` (Fase 2c): `null` se l'API non lo sa ancora dire (la pagina ha il suo ripiego).
final titolareProvider = FutureProvider.autoDispose<Titolare?>((ref) async {
  try {
    return await ref.read(apiProvider).titolare();
  } on Object {
    return null;
  }
});
