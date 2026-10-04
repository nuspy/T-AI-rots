// La mia storia, una lettura della storia, la lettura condivisa, le proprie carte e il pannello di condivisione, alle
// misure delle catture del sito (360×800, 390×844, iPad 1024×1366), con le risposte vere dell'API locale
// (test/fixtures/storia/) e la sessione di sviluppo. Sul sito: `/my-story` (dentro e fuori), `/my-story/<id>`,
// `/shared/<token>`, `/physical-reading`, e «Share» nella pagina della lettura.
//
//   flutter test --update-goldens --tags golden test/golden/storia_test.dart
@Tags(['golden'])
library;

import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';
import 'package:tarots/componenti/carta.dart';
import 'package:tarots/lettura/immagine_condivisione.dart';
import 'package:tarots/modelli/account.dart';

import '../aiuti/finti.dart';
import '../aiuti/scena.dart';

const List<(double, double)> misure = [(360, 800), (390, 844), (1024, 1366)];
const String idLettura = '5d487f6e-90c3-4e22-9ace-9846f245e594';
const String tokenCondivisa = 'VggWitVxx6ikgoa1S_ldRg';

AdattatoreFinto rete({Uint8List? anteprima}) {
  final r = apiDaFixture();
  r.risposte.addAll({
    '/me/readings': (_) => RispostaFinta.fixture('storia/letture.json'),
    '/me/readings/$idLettura': (_) => RispostaFinta.fixture('storia/lettura.json'),
    '/me/memories': (_) => RispostaFinta.fixture('storia/memorie.json'),
    '/shared/$tokenCondivisa': (_) => RispostaFinta.fixture('storia/condivisa.json'),
    '/spreads': (_) => RispostaFinta.fixture('storia/stese.json'),
    '/cards': (_) => RispostaFinta.fixture('storia/carte.json'),
    'POST /me/readings/$idLettura/share': (_) => RispostaFinta.json({'share_token': tokenCondivisa, 'share_text': null}),
    if (anteprima != null)
      'PUT /me/readings/$idLettura/share-image': (_) => RispostaFinta(
        200,
        pezzi: [anteprima],
        intestazioni: const {
          'content-type': ['image/png'],
        },
      ),
  });
  return r;
}

/// L'immagine che il server restituirebbe: qui la stessa composta dall'app (il server la riduce a 400×300 WebP).
Future<Uint8List> anteprima(WidgetTester tester) async {
  await tester.runAsync(caricaCaratteri);
  final png = await tester.runAsync(() async {
    final d = LetturaCondivisa.fromJson(
      jsonDecode(File('test/fixtures/storia/condivisa.json').readAsStringSync()) as Map<String, Object?>,
    );
    final immagini = await caricaCarte(d.cards, (f) => FileImage(fileCarta(f)), (id) => percorsoCarta(d.mazzo, id));
    return componiImmagine(d, immagini);
  });
  return png!;
}

void main() {
  for (final (w, h) in misure) {
    final nome = w.toInt();

    testWidgets('storia $nome', (tester) async {
      await montaApp(tester, rotta: '/my-story', larghezza: w, altezza: h, rete: rete());
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/storia_$nome.png');
    });

    testWidgets('storia senza account $nome', (tester) async {
      await montaApp(tester, rotta: '/my-story', larghezza: w, altezza: h, rete: rete(), autenticata: false);
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/storia_fuori_$nome.png');
    });

    testWidgets('lettura della storia $nome', (tester) async {
      await montaApp(tester, rotta: '/my-story/$idLettura', larghezza: w, altezza: h, rete: rete());
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/storia_lettura_$nome.png');
    });

    testWidgets('lettura condivisa $nome', (tester) async {
      await montaApp(tester, rotta: '/shared/$tokenCondivisa', larghezza: w, altezza: h, rete: rete());
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/condivisa_$nome.png');
    });

    testWidgets('le proprie carte $nome', (tester) async {
      await montaApp(tester, rotta: '/physical-reading', larghezza: w, altezza: h, rete: rete());
      await paginaIntera(tester, w);
      await fotografa(find.byType(TarotsApp), 'goldens/fisica_$nome.png');
    });

    testWidgets('pannello di condivisione $nome', (tester) async {
      final png = await anteprima(tester);
      await montaApp(tester, rotta: '/my-story/$idLettura', larghezza: w, altezza: h, rete: rete(anteprima: png));
      await tester.ensureVisible(find.text('Share'));
      await tester.tap(find.text('Share'));
      for (var i = 0; i < 6; i++) {
        await assesta(tester);
      }
      await fotografa(find.byType(TarotsApp), 'goldens/condivisione_$nome.png');
    });
  }
}
