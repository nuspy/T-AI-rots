/// I consensi dell'app (GDPR, Fase 1): le stesse categorie e gli stessi testi del banner del sito
/// (`frontend/v2/componenti/banner-cookie.tsx`), registrati con `POST /consensi` e origine `android`/`ios`.
///
/// - **`statistiche`**: le statistiche interne (lanterna) e il loro identificativo;
/// - **`google_analytics`**: Firebase Analytics (GA4).
/// La pubblicità non c'è nell'app al lancio (decisione dell'operatore): la sua categoria non si chiede.
///
/// La scelta vale subito sul telefono (si salva in locale prima della rete), poi si manda al server; se il server non
/// risponde resta «da sincronizzare» e si riprova al prossimo avvio. Al cambio di sessione si rilegge lo stato del
/// server (`GET /consenso`), come il sito: le scelte di un account non sono quelle dell'anonimo di prima.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../archivio.dart';

/// La versione dell'informativa con le categorie granulari (`VERSIONE_CONSENSI` del sito).
const String versioneConsensi = 'v3';

/// Le categorie che l'app chiede al primo avvio, nell'ordine del banner.
const List<String> categorieApp = ['statistiche', 'google_analytics'];

/// L'origine delle scelte fatte nell'app.
String origineApp() => Platform.isIOS ? 'ios' : 'android';

/// Lo stato dei consensi.
@immutable
class StatoConsensi {
  /// Uno stato.
  const StatoConsensi({this.valori = const {}, this.daSincronizzare = false});

  /// Tipo → `accettato`, `rifiutato`, o assente se mai scelto.
  final Map<String, String> valori;

  /// Scelte fatte sul telefono che il server non ha ancora ricevuto.
  final bool daSincronizzare;

  /// Vero se una categoria dell'app non è mai stata scelta: si mostra la richiesta.
  bool get daChiedere => categorieApp.any((c) => !valori.containsKey(c));

  /// Vero se [tipo] è accettato.
  bool accettato(String tipo) => valori[tipo] == 'accettato';

  /// In JSON per l'archivio.
  String inJson() => jsonEncode({'valori': valori, 'sospesi': daSincronizzare});

  /// Dall'archivio.
  static StatoConsensi daJson(String? testo) {
    if (testo == null) return const StatoConsensi();
    try {
      final d = jsonDecode(testo);
      if (d is! Map) return const StatoConsensi();
      final valori = <String, String>{};
      final v = d['valori'];
      if (v is Map) {
        for (final e in v.entries) {
          if (e.key is String && (e.value == 'accettato' || e.value == 'rifiutato')) {
            valori[e.key as String] = e.value as String;
          }
        }
      }
      return StatoConsensi(valori: valori, daSincronizzare: d['sospesi'] == true);
    } on FormatException {
      return const StatoConsensi();
    }
  }

  @override
  bool operator ==(Object other) =>
      other is StatoConsensi && mapEquals(other.valori, valori) && other.daSincronizzare == daSincronizzare;

  @override
  int get hashCode => Object.hash(Object.hashAll(valori.entries.map((e) => '${e.key}=${e.value}')), daSincronizzare);
}

/// La chiave dell'archivio.
const String chiaveConsensi = 'consensi.$versioneConsensi';

/// I consensi.
class Consensi extends Notifier<StatoConsensi> {
  @override
  StatoConsensi build() => StatoConsensi.daJson(ref.read(archivioProvider).leggi(chiaveConsensi));

  Future<void> _salva(StatoConsensi s) async {
    state = s;
    await ref.read(archivioProvider).scrivi(chiaveConsensi, s.inJson());
  }

  /// Registra le [scelte] (tipo → `accettato`/`rifiutato`): valgono subito, poi vanno al server.
  Future<void> scegli(Map<String, String> scelte) async {
    await _salva(StatoConsensi(valori: {...state.valori, ...scelte}, daSincronizzare: true));
    await _invia(scelte);
  }

  Future<bool> _invia(Map<String, String> scelte) async {
    try {
      final server = await ref
          .read(apiProvider)
          .registraConsensi(
            [for (final e in scelte.entries) (tipo: e.key, valore: e.value)],
            versione: versioneConsensi,
            origine: origineApp(),
          );
      final valori = {...state.valori};
      for (final c in categorieApp) {
        final v = server[c];
        if (v != null) valori[c] = v;
      }
      await _salva(StatoConsensi(valori: valori));
      return true;
    } on ErroreApi catch (e) {
      debugPrint('Consensi non sincronizzati (${e.stato}): si riprova al prossimo avvio.');
      return false;
    }
  }

  /// All'avvio e al cambio di sessione: manda le scelte rimaste sul telefono, oppure rilegge quelle del server per
  /// le categorie mai scelte qui (chi entra con un account le ritrova).
  Future<void> sincronizza() async {
    final locali = {
      for (final c in categorieApp)
        if (state.valori[c] != null) c: state.valori[c]!,
    };
    if (state.daSincronizzare && locali.isNotEmpty) {
      await _invia(locali);
      return;
    }
    try {
      final server = await ref.read(apiProvider).consensi();
      final valori = {...state.valori};
      var cambiati = false;
      for (final c in categorieApp) {
        final v = server[c];
        if (v != null && valori[c] != v) {
          valori[c] = v;
          cambiati = true;
        }
      }
      if (cambiati) await _salva(StatoConsensi(valori: valori, daSincronizzare: state.daSincronizzare));
    } on ErroreApi {
      // fuori rete: restano le scelte del telefono
    }
  }
}

/// I consensi dell'app.
final consensiProvider = NotifierProvider<Consensi, StatoConsensi>(Consensi.new);
