// La lingua dell'app (9/10/2026): al primo avvio si chiede per prima (prima di consensi ed età), in un dialogo con
// l'elenco che scorre nel suo riquadro e «Accetta» sempre in vista; la lingua di lettura la segue (il modello si
// scarica lì); in testata il codice («EN») anche sul telefono; all'accesso vince la lingua scelta nell'account.

import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/componenti/modale.dart';
import 'package:tarots/componenti/premibile.dart';
import 'package:tarots/componenti/testata.dart';
import 'package:tarots/consensi/consensi.dart';
import 'package:tarots/consensi/eta.dart';
import 'package:tarots/consensi/primo_avvio.dart';
import 'package:tarots/l10n/testi.dart';
import 'package:tarots/lettura/variante.dart';
import 'package:tarots/lingua/lingua.dart';
import 'package:tarots/lingua/lingua_profilo.dart';
import 'package:tarots/lingua/scelta_lingua_app.dart';
import 'package:tarots/traduzione/lingua_contenuti.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';
import 'traduzione_test.dart' show MotoreFinto;

Future<ProviderContainer> _monta(
  WidgetTester tester, {
  required ArchivioMemoria archivio,
  double larghezza = 360,
  double altezza = 640,
  bool autenticata = false,
  AdattatoreFinto? rete,
  MotoreFinto? motore,
}) async {
  await tester.runAsync(caricaCaratteri);
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = Size(larghezza, altezza);
  addTearDown(tester.view.reset);
  final c = ProviderContainer(
    overrides: sostituzioni(lingua: 'en', autenticata: autenticata, rete: rete, memoria: archivio, motore: motore),
    retry: (_, _) => null,
  );
  addTearDown(c.dispose);
  await tester.pumpWidget(UncontrolledProviderScope(container: c, child: const TarotsApp()));
  await assesta(tester);
  return c;
}

/// Le scelte del primo avvio già fatte, salvo quelle che il test toglie.
Map<String, String> _fatto() => {
  'lingua': 'en',
  chiaveConsensi: const StatoConsensi(valori: {'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'}).inJson(),
  chiaveEta: '16',
  chiaveVarianteLettura: VarianteLettura.classica,
};

void main() {
  testWidgets('primo avvio: prima la lingua, con «Accetta» sempre in vista; poi i consensi nella lingua scelta', (
    tester,
  ) async {
    final archivio = ArchivioMemoria({chiaveVarianteLettura: VarianteLettura.classica});
    final motore = MotoreFinto();
    // Il server non ha ancora consensi per questo dispositivo.
    final rete = apiDaFixture()..risposte['/consenso'] = (_) => RispostaFinta.json(<String, Object?>{});
    final c = await _monta(tester, archivio: archivio, motore: motore, rete: rete);

    // La lingua per prima: i consensi aspettano.
    expect(find.byType(DialogoLinguaApp), findsOneWidget);
    expect(find.byType(FoglioConsensi), findsNothing);
    expect(find.text('Choose your language'), findsOneWidget);
    // Segnata quella del telefono; le righe «IT · Italiano».
    expect(find.text('EN · English'), findsOneWidget);
    expect(find.text('IT · Italiano'), findsOneWidget);
    // L'elenco scorre nel suo riquadro; «Accetta» sta sotto, dentro lo schermo (360×640), alto almeno 48 px.
    expect(find.byType(RiquadroElenco), findsOneWidget);
    final accetta = tester.getRect(find.text('Accept'));
    expect(accetta.bottom, lessThanOrEqualTo(640));
    final riquadro = tester.getRect(find.byType(ListView));
    expect(riquadro.bottom, lessThanOrEqualTo(accetta.top));
    expect(
      tester.getSize(find.ancestor(of: find.text('Accept'), matching: find.byType(ConstrainedBox)).first).height,
      greaterThanOrEqualTo(48),
    );
    // Un'opzione d'un gruppo per i lettori di schermo, con lo stato «scelta».
    final semantica = tester.ensureSemantics();
    expect(
      tester.getSemantics(find.text('EN · English')),
      isSemantics(isInMutuallyExclusiveGroup: true, hasCheckedState: true, isChecked: true, isButton: true),
    );
    semantica.dispose();

    // Il magiaro, in fondo all'elenco o quasi: si scorre nel riquadro, il pulsante non si muove.
    await tester.scrollUntilVisible(find.text('HU · Magyar'), 48, scrollable: find.byType(Scrollable).last);
    await tester.tap(find.text('HU · Magyar'));
    await tester.pump();
    expect(tester.getRect(find.text('Elfogadom')).bottom, lessThanOrEqualTo(640));
    // I testi del dialogo seguono la lingua segnata.
    expect(find.text('Válaszd ki a nyelvet'), findsOneWidget);
    await tester.tap(find.text('Elfogadom'));
    await assesta(tester);

    // La lingua è scelta e ricordata; la lingua di lettura la segue, col suo modello scaricato.
    expect(c.read(linguaProvider), 'hu');
    expect(archivio.leggi('lingua'), 'hu');
    expect(archivio.leggi(chiaveLinguaIl), isNotNull);
    expect(c.read(linguaContenutiProvider), 'hu');
    expect(motore.scaricati, contains('hu'));
    expect(find.byType(DialogoLinguaApp), findsNothing);
    // Poi i consensi, in ungherese.
    expect(find.byType(FoglioConsensi), findsOneWidget);
    expect(AppLocalizations.of(tester.element(find.byType(FoglioConsensi))).localeName, 'hu');
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('chi ha già scelto non vede il dialogo', (tester) async {
    await _monta(tester, archivio: ArchivioMemoria(_fatto()));
    expect(find.byType(DialogoLinguaApp), findsNothing);
    debugDisableShadows = true;
  });

  testWidgets('sul telefono la testata mostra il codice della lingua, in fondo, e l\'elenco «IT · Italiano»', (
    tester,
  ) async {
    await _monta(tester, archivio: ArchivioMemoria(_fatto()));
    final codice = find.descendant(of: find.byType(Testata), matching: find.text('EN'));
    expect(codice, findsOneWidget);
    // È l'ultima voce della riga (dopo «Start reading»), alta come le altre voci (44 px).
    final voce = find.ancestor(of: codice, matching: find.byType(Premibile)).first;
    final riga = tester.getRect(find.byType(Testata));
    final casella = tester.getRect(voce);
    expect(casella.right, greaterThan(riga.right - 12));
    expect(casella.height, greaterThanOrEqualTo(44));
    await tester.tap(voce);
    await assesta(tester);
    expect(find.text('IT · Italiano'), findsOneWidget);
    await tester.tap(find.text('IT · Italiano'));
    await assesta(tester);
    expect(find.descendant(of: find.byType(Testata), matching: find.text('IT')), findsOneWidget);
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  group('all\'accesso', () {
    Map<String, Object?> profilo() =>
        jsonDecode(File('test/fixtures/profilo.json').readAsStringSync()) as Map<String, Object?>;

    testWidgets('l\'account ha scelto: vince lui, anche su una scelta più recente fatta qui', (tester) async {
      final rete = apiDaFixture();
      rete.risposte['/me/profile'] = (_) =>
          RispostaFinta.json({...profilo(), 'locale': 'it', 'locale_scelta_il': '2025-01-01T00:00:00Z'});
      final archivio = ArchivioMemoria({..._fatto(), chiaveLinguaIl: '${DateTime.now().millisecondsSinceEpoch}'});
      final c = await _monta(tester, archivio: archivio, autenticata: true, rete: rete, larghezza: 390, altezza: 844);
      await assesta(tester);
      expect(c.read(linguaProvider), 'it');
      expect(rete.richieste.where((r) => r.method == 'PATCH' && r.uri.path == '/me/profile'), isEmpty);
      debugDisableShadows = true;
    });

    testWidgets('l\'account non ha mai scelto: prende la lingua di qui', (tester) async {
      final rete = apiDaFixture();
      rete.risposte['/me/profile'] = (_) =>
          RispostaFinta.json({...profilo(), 'locale': 'en', 'locale_scelta_il': null});
      final c = await _monta(
        tester,
        archivio: ArchivioMemoria({..._fatto(), 'lingua': 'hu'}),
        autenticata: true,
        rete: rete,
        larghezza: 390,
        altezza: 844,
      );
      await assesta(tester);
      expect(c.read(linguaProvider), 'hu');
      final i = rete.richieste.lastIndexWhere((r) => r.method == 'PATCH' && r.uri.path == '/me/profile');
      expect(i, isNot(-1));
      expect(jsonDecode(rete.corpi[i]!), {'locale': 'hu'});
      debugDisableShadows = true;
    });
  });
}
