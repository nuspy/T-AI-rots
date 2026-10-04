/// L'età minima (GDPR, Fase 1), come `privacy-accesso.tsx` del sito: «ho almeno N anni», con N per il paese
/// (14 in Italia e Spagna, 15 in Francia, 16 altrove; `GET /eta-minima`).
///
/// Nell'app si chiede al primo avvio, dopo i consensi. La conferma si ricorda sul telefono (la lettura anonima la
/// manda al server con `eta_confermata`, come il sito) e, per chi ha un account, va al server con `POST /me/eta` e
/// l'origine `android`/`ios`. «Non ora» chiude il dialogo per questa volta: si ripresenta al prossimo avvio e prima
/// di una lettura (Fase 8).
library;

import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import 'consensi.dart';

/// L'età minima quando il server non la sa dire (fuori rete, backend vecchio): la più alta, come `anni ?? 16` del sito.
const int etaMinimaPredefinita = 16;

/// La chiave dell'archivio: gli anni confermati.
const String chiaveEta = 'eta.confermata';

/// Lo stato della conferma.
@immutable
class StatoEta {
  /// Uno stato.
  const StatoEta({this.anniConfermati, this.rimandata = false});

  /// Gli anni confermati («ho almeno N anni»), o `null`.
  final int? anniConfermati;

  /// «Non ora» in questa sessione dell'app.
  final bool rimandata;

  /// Vero se va chiesta.
  bool daChiedere(int anniMinimi) => !rimandata && (anniConfermati == null || anniConfermati! < anniMinimi);

  @override
  bool operator ==(Object other) =>
      other is StatoEta && other.anniConfermati == anniConfermati && other.rimandata == rimandata;

  @override
  int get hashCode => Object.hash(anniConfermati, rimandata);
}

/// L'età minima per questo telefono (paese stimato dal server).
final etaMinimaProvider = FutureProvider<int>((ref) async {
  try {
    return (await ref.read(apiProvider).etaMinima()).anni;
  } on ErroreApi {
    return etaMinimaPredefinita;
  }
});

/// La conferma dell'età.
class Eta extends Notifier<StatoEta> {
  @override
  StatoEta build() => StatoEta(anniConfermati: int.tryParse(ref.read(archivioProvider).leggi(chiaveEta) ?? ''));

  /// «Ho almeno [anni] anni».
  Future<void> conferma(int anni) async {
    state = StatoEta(anniConfermati: anni);
    await ref.read(archivioProvider).scrivi(chiaveEta, '$anni');
    final sessione = ref.read(sessioneProvider);
    if (!sessione.autenticata) return;
    try {
      await ref.read(apiProvider).confermaEta(anni, origine: origineApp());
    } on ErroreApi catch (e) {
      // Come il sito: un errore chiude il dialogo; il server richiederà la conferma alla prima lettura.
      debugPrint('Conferma dell\'età non registrata dal server (${e.stato}).');
    }
  }

  /// «Non ora».
  void rimanda() => state = StatoEta(anniConfermati: state.anniConfermati, rimandata: true);
}

/// La conferma dell'età.
final etaProvider = NotifierProvider<Eta, StatoEta>(Eta.new);
