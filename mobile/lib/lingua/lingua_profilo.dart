/// La lingua del menu e quella del profilo (v9, Fase 2d), come `frontend/v2/lib/lingua-profilo.ts`: **vince l'ultima
/// scelta**.
///
/// - Chi è dentro e cambia lingua dal selettore la cambia anche nel profilo (`PATCH /me/profile`, che segna
///   `locale_scelta_il`): l'oracolo, le email e le notifiche la seguono. Il telefono ricorda quando l'ha scelta
///   (`lingua_il`, la stessa chiave del sito).
/// - **All'accesso** (una volta per persona e per avvio) si confrontano le due scelte: una scelta fatta qui più recente
///   di quella del profilo va nel profilo; se no vince il profilo (l'app passa alla sua lingua); se nessuno ha mai
///   scelto, la lingua in cui si sta leggendo va nel profilo.
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
import 'lingua.dart';

/// Quando la lingua è stata scelta qui (millisecondi): la stessa chiave del sito.
const String chiaveLinguaIl = 'lingua_il';

int? _numero(String? v) {
  final n = int.tryParse(v ?? '');
  return n != null && n > 0 ? n : null;
}

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

/// Il selettore della lingua: l'interfaccia cambia subito, poi la scelta va nel profilo (con un account).
Future<void> scegliLingua(WidgetRef ref, String lingua) async {
  await ref.read(linguaProvider.notifier).imposta(lingua);
  await segnaScelta(ref.read(archivioProvider));
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
    final localeIl = _numero(archivio.leggi(chiaveLinguaIl));
    if (localeIl != null && (profiloIl == null || localeIl > profiloIl)) {
      if (delProfilo != qui) await salva(qui);
    } else if (profiloIl != null && delProfilo != null) {
      await segnaScelta(archivio, profiloIl);
      if (delProfilo != qui) await _ref.read(linguaProvider.notifier).imposta(delProfilo);
    } else if (delProfilo != qui) {
      await salva(qui);
    }
  }
}

final _sincroniaProvider = Provider<SincroniaLingua>(SincroniaLingua.new);

/// Il riallineamento della lingua col profilo (lo chiama l'app quando la sessione è pronta).
final sincroniaLinguaProvider = Provider<SincroniaLingua>((ref) => ref.watch(_sincroniaProvider));
