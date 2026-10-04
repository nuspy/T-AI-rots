// Il rito di lettura alle misure delle catture del sito (360×800, 390×844, iPad 1024×1366), con le risposte vere
// dell'API locale (test/fixtures/lettura/). Le fasi si raggiungono come nel sito riprendendo una lettura (`?id=`):
// la preparazione, l'intervista, il ventaglio della scelta (sul telefono nel dialogo scuro del rito) e la lettura
// completata col tavolo, le carte svelate e il responso. Sul sito: `/read?spread=tre-carte` e `/read?id=<id>` con
// una lettura nello stesso stato.
//
//   flutter test --update-goldens --tags golden test/golden/lettura_test.dart
@Tags(['golden'])
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';

import '../aiuti/finti.dart';
import '../aiuti/scena.dart';

const List<(double, double)> misure = [(360, 800), (390, 844), (1024, 1366)];
const String idLettura = 'f2b57ff0-1519-49b6-a8a5-980ccbf3035d';

Map<String, Object?> completa() =>
    jsonDecode(File('test/fixtures/lettura/lettura_completa.json').readAsStringSync()) as Map<String, Object?>;

/// La lettura salvata in uno stato del rito.
Map<String, Object?> inStato(String stato) {
  final l = completa();
  switch (stato) {
    case 'intervista':
      l
        ..['status'] = 'intervista'
        ..['interview'] = (l['interview']! as List<Object?>).take(3).toList()
        ..['context_summary'] = null
        ..['cards'] = <Object?>[]
        ..['picked_slots'] = <Object?>[]
        ..['slot_count'] = null
        ..['synthesis'] = null;
    case 'scelta':
      l
        ..['status'] = 'scelta'
        ..['cards'] = <Object?>[]
        ..['picked_slots'] = <Object?>[]
        ..['synthesis'] = null;
  }
  return l;
}

AdattatoreFinto rete(String stato) {
  final r = apiDaFixture();
  r.risposte.addAll({
    '/spreads': (_) => RispostaFinta.fixture('lettura/stese_en.json'),
    '/me/decks': (_) => RispostaFinta.json({
      'deck_ids': [1],
    }),
    '/me/readings/$idLettura': (_) => RispostaFinta.json(inStato(stato)),
  });
  return r;
}

void main() {
  for (final (w, h) in misure) {
    final nome = w.toInt();
    for (final (stato, rotta) in [
      ('preparazione', '/read?spread=tre-carte'),
      ('intervista', '/read?id=$idLettura'),
      ('scelta', '/read?id=$idLettura'),
      ('completata', '/read?id=$idLettura'),
    ]) {
      testWidgets('lettura $stato $nome', (tester) async {
        await montaApp(tester, rotta: rotta, larghezza: w, altezza: h, rete: rete(stato));
        await assesta(tester);
        await paginaIntera(tester, w);
        await fotografa(find.byType(TarotsApp), 'goldens/lettura_${stato}_$nome.png');
      });
    }
  }
}
