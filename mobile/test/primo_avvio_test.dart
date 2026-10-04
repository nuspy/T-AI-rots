// Il primo avvio dentro l'app intera: il foglio dei consensi, poi l'età, poi la pagina libera. Senza Material sopra
// (l'app non ne ha): un componente che lo richiedesse si romperebbe qui, non sul telefono.

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/analytics/tracciato.dart';
import 'package:tarots/app.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/consensi/consensi.dart';
import 'package:tarots/consensi/eta.dart';
import 'package:tarots/consensi/primo_avvio.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';

void main() {
  testWidgets('consensi, poi età, poi la pagina', (tester) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(390, 844);
    addTearDown(tester.view.reset);
    final archivio = ArchivioMemoria({'lingua': 'en'});
    final rete = apiDaFixture();
    // Il server finto registra le scelte e restituisce lo stato, come `POST /consensi`.
    rete.risposte['POST /consensi'] = (r) => RispostaFinta.json({
      for (final s in ((r.data as Map)['scelte'] as List).cast<Map<Object?, Object?>>()) s['tipo']: s['valore'],
    });
    rete.risposte['/consenso'] = (_) => RispostaFinta.json(<String, Object?>{});
    rete.risposte['/eta-minima'] = (_) => RispostaFinta.json({'anni': 14});
    final c = ProviderContainer(
      overrides: sostituzioni(lingua: 'en', autenticata: false, rete: rete, memoria: archivio),
      retry: (_, _) => null,
    );
    addTearDown(c.dispose);
    await tester.pumpWidget(UncontrolledProviderScope(container: c, child: const TarotsApp()));
    await assesta(tester);

    expect(find.byType(FoglioConsensi), findsOneWidget);
    await tester.tap(find.text('Choose'));
    await tester.pump();
    expect(find.text('Google Analytics'), findsOneWidget);
    await tester.tap(find.text('App statistics'));
    await tester.pump();
    // Aperte le categorie il foglio scorre (sta sopra la barra dell'oracolo): il comando si porta in vista.
    await tester.ensureVisible(find.text('Save my choices'));
    await tester.pump();
    await tester.tap(find.text('Save my choices'));
    await assesta(tester);
    expect(c.read(consensiProvider).valori, {'statistiche': 'accettato', 'google_analytics': 'rifiutato'});
    expect(tester.takeException(), isNull);

    expect(find.byType(DialogoEta), findsOneWidget);
    expect(find.text('I am at least 14 years old'), findsOneWidget);
    await tester.tap(find.text('I am at least 14 years old'));
    await tester.pump();
    await tester.tap(find.text('Confirm'));
    await assesta(tester);
    expect(archivio.leggi(chiaveEta), '14');
    expect(find.byType(DialogoEta), findsNothing);
    expect(tester.takeException(), isNull);
    // L'osservatore (livello base sempre acceso, esteso con le statistiche accettate) si spegne prima della fine:
    // niente timer pendenti.
    c.read(lanternaProvider).spegni();
  });
}
