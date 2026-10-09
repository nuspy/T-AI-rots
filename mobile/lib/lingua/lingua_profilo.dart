/// La lingua del menu e quella del profilo (v9, Fase 2d; dal 9/10/2026 **vince l'account**).
///
/// - Chi è dentro e cambia lingua (dal selettore in testata o nel piè di pagina, dal primo avvio, dall'invito a passare
///   alla lingua in cui scrive) la cambia anche nel profilo (`PATCH /me/profile`, che segna `locale_scelta_il`):
///   l'oracolo, le email e le notifiche la seguono. Il telefono ricorda quando l'ha scelta (`lingua_il`, come il sito).
/// - **All'accesso** (una volta per persona e per avvio): se l'account ha una lingua scelta (`locale_scelta_il`), vince
///   quella e l'app ci passa, qualunque cosa si sia scelta qui prima di entrare; se l'account non ha mai scelto, la
///   lingua di qui va nel profilo.
/// - Nessun ciclo: applicare la lingua del profilo non scrive nel profilo.
library;

import 'dart:async';
import 'dart:ui' show PlatformDispatcher;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../modelli/account.dart';
import '../traduzione/lingua_contenuti.dart';
import '../traduzione/motore.dart';
import 'lingua.dart';

/// Quando la lingua è stata scelta qui (millisecondi): la stessa chiave del sito.
const String chiaveLinguaIl = 'lingua_il';

/// Ricorda che la lingua è stata scelta adesso (o al momento [quando]).
Future<void> segnaScelta(Archivio archivio, [int? quando]) =>
    archivio.scrivi(chiaveLinguaIl, '${quando ?? DateTime.now().millisecondsSinceEpoch}');

/// Scrive la lingua nel profilo. Mai un errore visibile: il selettore ha già cambiato l'interfaccia.
Future<void> salvaNelProfilo(Ref ref, String lingua) async {
  try {
    final p = await ref.read(apiProvider).aggiornaProfilo({'locale': lingua});
    final il = DateTime.tryParse(p.localeSceltaIl ?? '');
    if (il != null) await segnaScelta(ref.read(archivioProvider), il.millisecondsSinceEpoch);
  } on ErroreApi {
    // rete o sessione: si riallinea al prossimo accesso
  }
}

/// All'avvio, senza una scelta salvata e senza una lingua del telefono che l'app abbia: l'ultimo indizio è il paese
/// (`/lingua-suggerita`). Non diventa una scelta: il selettore e il profilo valgono sempre di più.
Future<void> suggerisciDalPaese(WidgetRef ref) async {
  final lingua = ref.read(linguaProvider.notifier);
  if (lingua.scelta || linguaSupportataDelSistema(PlatformDispatcher.instance.locales) != null) return;
  try {
    final l = await ref.read(apiProvider).linguaSuggerita();
    if (l != null) lingua.applicaSuggerita(l);
  } on ErroreApi {
    // senza rete resta la lingua di ripiego
  }
}

/// Il selettore della lingua: l'interfaccia cambia subito, poi la scelta va nel profilo (con un account). La lingua di
/// lettura la segue (se non se n'è scelta un'altra): il suo modello di traduzione si scarica in silenzio, così la
/// prossima pagina tradotta è già pronta (se non riesce, si riprova quando si apre un contenuto).
Future<void> scegliLingua(WidgetRef ref, String lingua) async {
  await ref.read(linguaProvider.notifier).imposta(lingua);
  await segnaScelta(ref.read(archivioProvider));
  final motore = ref.read(motoreTraduzioneProvider);
  final contenuti = ref.read(linguaContenutiProvider);
  if (motore.disponibile && contenuti != 'en' && lingueMlKit.contains(contenuti)) {
    unawaited(motore.scarica(contenuti).then((_) {}, onError: (Object _) {}));
  }
  if (ref.read(sessioneProvider).autenticata) await ref.read(_sincroniaProvider).salva(lingua);
}

/// Il riallineamento all'accesso.
class SincroniaLingua {
  /// Sui provider dell'app.
  SincroniaLingua(this._ref);

  final Ref _ref;
  String? _allineata;

  /// Salva [lingua] nel profilo.
  Future<void> salva(String lingua) => salvaNelProfilo(_ref, lingua);

  /// All'accesso: una volta per persona (il nome della sessione fa da soggetto) e per avvio.
  Future<void> allinea() async {
    final sessione = _ref.read(sessioneProvider);
    if (!sessione.pronta || !sessione.autenticata) return;
    final chi = sessione.nome ?? 'sviluppo';
    if (_allineata == chi) return;
    _allineata = chi;
    final api = _ref.read(apiProvider);
    final archivio = _ref.read(archivioProvider);
    final Profilo profilo;
    try {
      profilo = await api.profilo();
    } on ErroreApi {
      _allineata = null;
      return;
    }
    final delProfilo = comeLingua(profilo.locale);
    final qui = _ref.read(linguaProvider);
    final profiloIl = DateTime.tryParse(profilo.localeSceltaIl ?? '')?.millisecondsSinceEpoch;
    if (profiloIl != null && delProfilo != null) {
      // L'account ha scelto: vince lui, qualunque cosa si sia scelta qui prima di entrare.
      await segnaScelta(archivio, profiloIl);
      if (delProfilo != qui) await _ref.read(linguaProvider.notifier).imposta(delProfilo);
    } else {
      // L'account non ha mai scelto: prende la lingua di qui (e da allora la sua scelta c'è).
      await salva(qui);
    }
  }
}

final _sincroniaProvider = Provider<SincroniaLingua>(SincroniaLingua.new);

/// Il riallineamento della lingua col profilo (lo chiama l'app quando la sessione è pronta).
final sincroniaLinguaProvider = Provider<SincroniaLingua>((ref) => ref.watch(_sincroniaProvider));
