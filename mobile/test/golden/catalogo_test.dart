// Il catalogo alle misure delle catture del sito (360×800, 390×844, 1024×1366): la biblioteca e una carta, le stese
// e una stesa, i mazzi e il Thoth, il voto, il negozio, il carrello con un PDF, la pagina che non c'è. Dati: le
// fixture di `test/fixtures/catalogo/` (vedi `test/catalogo_test.dart`), la sessione di sviluppo.
//
//   flutter test --update-goldens --tags golden test/golden/catalogo_test.dart
//
// Sul sito, le stesse pagine: `/cards`, `/cards/the-star`, `/spreads`, `/spreads/three-card`, `/decks`,
// `/decks/thoth`, `/vote`, `/shop`, `/cart` (col PDF del Thoth nel carrello), `/non-esiste`.
@Tags(['golden'])
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';
import 'package:tarots/dati/dati.dart';

import '../aiuti/scena.dart';
import '../catalogo_test.dart' show reteCatalogo;

const List<(double, double)> misure = [(360, 800), (390, 844), (1024, 1366)];

const List<(String, String)> pagine = [
  ('carte', '/cards'),
  ('carta', '/cards/the-star'),
  ('stese', '/spreads'),
  ('stesa', '/spreads/three-card'),
  ('mazzi', '/decks'),
  ('mazzo', '/decks/thoth'),
  ('voto', '/vote'),
  ('negozio', '/shop'),
  ('pagina_404', '/non-esiste'),
];

/// La biblioteca mostra tutte le 78 carte: la cache delle immagini (100 MB) non le terrebbe tutte decodificate, e le
/// ultime precaricate scaccerebbero le prime. Si allarga solo per questi test.
void cacheGrande(WidgetTester tester) {
  final cache = tester.binding.imageCache;
  final prima = (cache.maximumSize, cache.maximumSizeBytes);
  cache
    ..maximumSize = 2000
    ..maximumSizeBytes = 1 << 30;
  addTearDown(() {
    cache
      ..maximumSize = prima.$1
      ..maximumSizeBytes = prima.$2;
  });
}

/// Aspetta, in tempo vero, che tutte le immagini della pagina siano decodificate (le 78 carte della biblioteca non
/// finiscono tutte nei pochi giri di `assesta`).
Future<void> attendiImmagini(WidgetTester tester) async {
  final elementi = find.byType(Image).evaluate().toList();
  await tester.runAsync(() async {
    for (final e in elementi) {
      await precacheImage((e.widget as Image).image, e);
    }
  });
  await tester.pump();
}

void main() {
  for (final (w, h) in misure) {
    final nome = w.toInt();

    for (final (file, rotta) in pagine) {
      testWidgets('$file $nome', (tester) async {
        cacheGrande(tester);
        await montaApp(tester, rotta: rotta, larghezza: w, altezza: h, rete: reteCatalogo());
        await paginaIntera(tester, w);
        await attendiImmagini(tester);
        await fotografa(find.byType(TarotsApp), 'goldens/${file}_$nome.png');
      });
    }

    testWidgets('carrello $nome', (tester) async {
      cacheGrande(tester);
      final c = await montaApp(tester, rotta: '/cart', larghezza: w, altezza: h, rete: reteCatalogo());
      c.read(carrelloProvider.notifier).aggiungi(1, 'pdf');
      await assesta(tester);
      // Il preventivo parte dopo un quarto di secondo (come nel sito, mentre si premono i +/−).
      await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 300)));
      await assesta(tester);
      await paginaIntera(tester, w);
      await attendiImmagini(tester);
      await fotografa(find.byType(TarotsApp), 'goldens/carrello_$nome.png');
    });
  }
}
