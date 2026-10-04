// Le schermate dell'app alle stesse misure delle catture del sito (confronto/cattura_sito.py): 360×800 e 390×844
// (telefoni), 1024×1366 (iPad). Testata, home e carta del giorno, con i dati dell'API locale salvati in
// test/fixtures e la sessione di sviluppo (come il sito locale, con l'autenticazione spenta).
//
//   flutter test --update-goldens --tags golden     rigenera le immagini (test/golden/goldens/)
//
// Le immagini dipendono dai caratteri di ripiego del sistema (quelli di Windows, come Edge nelle catture del sito):
// su un altro sistema si escludono (`--exclude-tags golden`).
@Tags(['golden'])
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';
import 'package:tarots/componenti/testata.dart';
import 'package:tarots/l10n/testi.dart';
import 'package:tarots/lingua/lingua.dart';

import '../aiuti/scena.dart';

const List<(double, double)> misure = [(360, 800), (390, 844), (1024, 1366)];

void main() {
  for (final (w, h) in misure) {
    final nome = w.toInt();

    testWidgets('home $nome', (tester) async {
      await montaApp(tester, rotta: '/', larghezza: w, altezza: h);
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/home_$nome.png');
    });

    testWidgets('carta del giorno $nome', (tester) async {
      await montaApp(tester, rotta: '/daily-card', larghezza: w, altezza: h);
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/giorno_$nome.png');
    });

    for (final lingua in w < 1000 ? ['en', 'it', 'hu', 'ru', 'uk', 'es'] : ['en', 'it']) {
      testWidgets('testata $nome $lingua', (tester) async {
        await montaApp(tester, rotta: '/daily-card', larghezza: w, altezza: h, lingua: lingua);
        await fotografa(find.byType(Testata), 'goldens/testata_${nome}_$lingua.png');
      });
    }
  }

  // La riga unica della testata, in tutte le lingue e alle larghezze dei telefoni (il sito l'ha misurata fra 320 e
  // 430 px in sei lingue): nessuna voce va a capo oltre le due righe e niente esce dal bordo.
  for (final w in [320.0, 360.0, 390.0, 430.0]) {
    testWidgets('testata su una riga a ${w.toInt()} px in tutte le lingue', (tester) async {
      for (final l in lingue) {
        await montaApp(tester, rotta: '/daily-card', larghezza: w, lingua: l.codice);
        final testata = tester.getSize(find.byType(Testata));
        expect(testata.height, lessThanOrEqualTo(57), reason: '${l.codice}: la testata deve restare su una riga');
        final riga = find.descendant(of: find.byType(Testata), matching: find.byType(Row)).first;
        expect(tester.getSize(riga).width, lessThanOrEqualTo(w - 8 + .5), reason: '${l.codice}: esce dal bordo');
        final t = AppLocalizations.of(tester.element(find.byType(Testata)));
        expect(t.localeName, l.codice);
      }
      debugDisableShadows = true;
    });
  }
}
