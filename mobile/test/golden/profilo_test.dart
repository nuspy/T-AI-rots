// Le pagine dell'account alle misure delle catture del sito (360×800, 390×844, 1024×1366): il profilo con un
// abbonamento a pagamento (e quello comprato nello store), la conferma dello spegnimento del rinnovo, la privacy,
// l'eliminazione dell'account. Dati: le fixture di `test/fixtures/profilo/` (vedi `test/profilo_test.dart`).
//
//   flutter test --update-goldens --tags golden test/golden/profilo_test.dart
//
// Sul sito, le stesse pagine: `/profile`, `/privacy`, `/account/elimina` (sessione di sviluppo, API aggiornata).
@Tags(['golden'])
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';

import '../aiuti/scena.dart';
import '../profilo_test.dart' show reteProfilo;

const List<(double, double)> misure = [(360, 800), (390, 844), (1024, 1366)];

void main() {
  for (final (w, h) in misure) {
    final nome = w.toInt();

    testWidgets('profilo $nome', (tester) async {
      await montaApp(tester, rotta: '/profile', larghezza: w, altezza: h, rete: reteProfilo());
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/profilo_$nome.png');
    });

    testWidgets('privacy $nome', (tester) async {
      await montaApp(tester, rotta: '/privacy', larghezza: w, altezza: h, rete: reteProfilo());
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/privacy_$nome.png');
    });

    testWidgets('elimina account $nome', (tester) async {
      await montaApp(tester, rotta: '/account/elimina', larghezza: w, altezza: h, rete: reteProfilo());
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/elimina_$nome.png');
    });
  }

  testWidgets('profilo con l\'abbonamento dello store 390', (tester) async {
    await montaApp(tester, rotta: '/profile', larghezza: 390, altezza: 844, rete: reteProfilo(abbonamento: 'store'));
    await paginaIntera(tester, 390);
    await fotografa(find.byType(TarotsApp), 'goldens/profilo_store_390.png');
  });

  testWidgets('conferma dello spegnimento del rinnovo 390', (tester) async {
    await montaApp(tester, rotta: '/profile', larghezza: 390, altezza: 844, rete: reteProfilo());
    final interruttore = find.text('Renew automatically');
    await tester.ensureVisible(interruttore);
    await tester.pump();
    await tester.tap(interruttore);
    await assesta(tester);
    await fotografa(find.byType(TarotsApp), 'goldens/profilo_rinnovo_390.png');
  });
}
