// I prezzi (con e senza il codice), la prova e il diario (indice, sezione, articolo, Esplora) alle stesse misure delle
// catture del sito (360×800, 390×844, 1024×1366), a pagina intera, con le risposte vere salvate dall'API.
//
//   flutter test --update-goldens --tags golden test/golden/prezzi_blog_test.dart
//
// Le URL del sito equivalenti: /pricing, /pricing?coupon=LUNA30, /trial, /blog, /blog/sezione/learn-tarot,
// /blog/how-to-read-tarot-cards, /explore, e (v9.4) /blog/sezione/tarot-spreads, /blog/sezione/minor-arcana (sessione di
// sviluppo, lingua inglese).
@Tags(['golden'])
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';

import '../aiuti/scena.dart';
import '../fixtures/prezzi/rete.dart';

const List<(double, double)> misure = [(360, 800), (390, 844), (1024, 1366)];

const List<(String, String)> schermate = [
  ('prezzi', '/pricing'),
  ('prezzi_coupon', '/pricing?coupon=LUNA30'),
  ('prova', '/trial'),
  ('blog', '/blog'),
  ('blog_sezione', '/blog/sezione/learn-tarot'),
  // v9.4: le stese come schede ricche, Minor Arcana coi contenitori «By suit» e «By number».
  ('blog_stese', '/blog/sezione/tarot-spreads'),
  ('blog_minori', '/blog/sezione/minor-arcana'),
  ('articolo', '/blog/how-to-read-tarot-cards'),
  ('esplora', '/explore'),
];

void main() {
  for (final (w, h) in misure) {
    for (final (nome, rotta) in schermate) {
      testWidgets('$nome ${w.toInt()}', (tester) async {
        await montaApp(tester, rotta: rotta, larghezza: w, altezza: h, rete: retePrezziDiario());
        await paginaIntera(tester, w);
        await fotografa(find.byType(TarotsApp), 'goldens/${nome}_${w.toInt()}.png');
      });
    }
  }

  // Il testo ricco dell'articolo (direttive, tabella, figura, scheda, video): solo sul telefono.
  testWidgets('articolo ricco 390', (tester) async {
    await montaApp(tester, rotta: '/blog/ricco', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    await paginaIntera(tester, 390);
    await fotografa(find.byType(TarotsApp), 'goldens/articolo_ricco_390.png');
  });
}
