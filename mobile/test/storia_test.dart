// La storia, il dettaglio di una lettura, la lettura condivisa, le proprie carte, la condivisione (immagine 800×600)
// e la stampa in PDF, con le risposte vere dell'API locale salvate in test/fixtures/storia/.

import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:tarots/componenti/carta.dart';
import 'package:tarots/l10n/testi.dart';
import 'package:tarots/lettura/immagine_condivisione.dart';
import 'package:tarots/lettura/stampa.dart';
import 'package:tarots/modelli/account.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';

const String idLettura = '5d487f6e-90c3-4e22-9ace-9846f245e594';
const String tokenCondivisa = 'VggWitVxx6ikgoa1S_ldRg';

Map<String, Object?> json(String nome) =>
    jsonDecode(File('test/fixtures/storia/$nome').readAsStringSync()) as Map<String, Object?>;

/// Le risposte dell'API per le pagine della storia.
AdattatoreFinto reteStoria() {
  final r = apiDaFixture();
  r.risposte.addAll({
    '/me/readings': (_) => RispostaFinta.fixture('storia/letture.json'),
    '/me/readings/$idLettura': (_) => RispostaFinta.fixture('storia/lettura.json'),
    '/me/memories': (_) => RispostaFinta.fixture('storia/memorie.json'),
    '/shared/$tokenCondivisa': (_) => RispostaFinta.fixture('storia/condivisa.json'),
    '/spreads': (_) => RispostaFinta.fixture('storia/stese.json'),
    '/cards': (_) => RispostaFinta.fixture('storia/carte.json'),
    'POST /me/readings/$idLettura/feedback': (_) => RispostaFinta.json({'feedback': 'si'}),
  });
  return r;
}

/// L'app su [rotta], con le ombre di flutter_test come le vuole il controllo finale (qui non si fotografa).
Future<void> monta(
  WidgetTester tester, {
  required String rotta,
  required double larghezza,
  required double altezza,
  required AdattatoreFinto rete,
  bool autenticata = true,
}) async {
  await montaApp(tester, rotta: rotta, larghezza: larghezza, altezza: altezza, rete: rete, autenticata: autenticata);
  debugDisableShadows = true;
}

void main() {
  test('la sintesi breve del responso: le frasi della sezione finale, senza Markdown', () {
    const responso = '## Il quadro\n\nPrima parte.\n\n## La tendenza\n\nUna **frase** breve. Un\'altra frase. Una terza.';
    expect(sintesiDelResponso(responso, 40), 'Una frase breve. Un\'altra frase.');
    expect(sintesiDelResponso(null, 40), '');
    expect(sintesiDelResponso('## T\n\n${'parola ' * 40}', 30), endsWith('…'));
  });

  test('i modelli leggono le risposte vere', () {
    final l = Lettura.fromJson(json('lettura.json'));
    expect(l.id, idLettura);
    expect(l.shareToken, tokenCondivisa);
    final c = LetturaCondivisa.fromJson(json('condivisa.json'));
    expect(c.stesa, isNotNull);
    expect(c.cards.where((x) => x.carta != null), isNotEmpty);
  });

  testWidgets('l\'immagine di condivisione è un PNG 800×600', (tester) async {
    await tester.runAsync(caricaCaratteri);
    final png = await tester.runAsync(() async {
      final d = LetturaCondivisa.fromJson(json('condivisa.json'));
      final immagini = await caricaCarte(d.cards, (f) => FileImage(fileCarta(f)), (id) => percorsoCarta(d.mazzo, id));
      expect(immagini.values.whereType<ui.Image>(), isNotEmpty);
      return componiImmagine(d, immagini);
    });
    expect(png, isNotNull);
    final codec = await tester.runAsync(() => ui.instantiateImageCodec(png!));
    final frame = await tester.runAsync(() => codec!.getNextFrame());
    expect(frame!.image.width, 800);
    expect(frame.image.height, 600);
  });

  testWidgets('il PDF della lettura', (tester) async {
    final byte = await tester.runAsync(() async {
      await initializeDateFormatting('en');
      final caratteri = await CaratteriStampa.carica();
      return costruisciPdf(
        Lettura.fromJson(json('lettura.json')),
        t: lookupAppLocalizations(const Locale('en')),
        interfaccia: 'en',
        caratteri: caratteri,
      );
    });
    expect(byte, isNotNull);
    expect(ascii.decode(byte!.sublist(0, 4)), '%PDF');
  });

  testWidgets('la mia storia: le letture e la memoria', (tester) async {
    await monta(tester, rotta: '/my-story', larghezza: 390, altezza: 844, rete: reteStoria());
    expect(find.text('Your recent thread'), findsOneWidget);
    expect(find.text('Values clarity before speed when facing a decision.'), findsOneWidget);
    expect(find.text('Will we have diesel this winter?'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('la mia storia senza account', (tester) async {
    await monta(tester, rotta: '/my-story', larghezza: 390, altezza: 844, rete: reteStoria(), autenticata: false);
    expect(find.text('What is remembered'), findsOneWidget);
    expect(find.text('Start your free reading'), findsWidgets);
  });

  testWidgets('il dettaglio di una lettura: l\'esito si annota', (tester) async {
    final rete = reteStoria();
    await monta(tester, rotta: '/my-story/$idLettura', larghezza: 1024, altezza: 1366, rete: rete);
    expect(find.text('Did it come true?'.toUpperCase()), findsOneWidget);
    expect(find.text('The interpretation'), findsOneWidget);
    await tester.tap(find.text('Yes'));
    await assesta(tester);
    expect(rete.richieste.any((r) => r.uri.path.endsWith('/feedback')), isTrue);
    expect(find.text('Noted.'), findsOneWidget);
  });

  testWidgets('la lettura condivisa: la visita si conta dopo qualche secondo', (tester) async {
    final rete = reteStoria();
    await monta(tester, rotta: '/shared/$tokenCondivisa', larghezza: 390, altezza: 844, rete: rete);
    expect(find.text('Your own question is waiting.'), findsOneWidget);
    await tester.pump(const Duration(seconds: 5));
    await assesta(tester);
    expect(rete.richieste.any((r) => r.uri.path == '/shared/$tokenCondivisa/visit'), isTrue);
  });

  testWidgets('la lettura condivisa che non c\'è più', (tester) async {
    await monta(tester, rotta: '/shared/inesistente', larghezza: 390, altezza: 844, rete: reteStoria());
    expect(find.text('This reading is no longer shared.'), findsOneWidget);
  });

  testWidgets('le proprie carte: si sceglie la stesa e compare il tavolo', (tester) async {
    await monta(tester, rotta: '/physical-reading', larghezza: 390, altezza: 844, rete: reteStoria());
    expect(find.text('Which spread did you lay out?'), findsOneWidget);
    await tester.ensureVisible(find.text('Three cards').first);
    await tester.tap(find.text('Three cards').first);
    await assesta(tester);
    expect(find.text('Choose another spread'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('la condivisione: il collegamento, l\'immagine caricata, i canali', (tester) async {
    final rete = reteStoria();
    final webp = File('../frontend/public/cards/maj-06.webp').readAsBytesSync();
    rete.risposte.addAll({
      'POST /me/readings/$idLettura/share': (_) =>
          RispostaFinta.json({'share_token': tokenCondivisa, 'share_text': 'Ciò che mi hanno detto le carte'}),
      'PUT /me/readings/$idLettura/share-image': (_) => RispostaFinta(
        200,
        pezzi: [webp],
        intestazioni: const {
          'content-type': ['image/webp'],
        },
      ),
    });
    await monta(tester, rotta: '/my-story/$idLettura', larghezza: 390, altezza: 844, rete: rete);
    await tester.ensureVisible(find.text('Share'));
    await tester.tap(find.text('Share'));
    for (var i = 0; i < 6; i++) {
      await assesta(tester);
    }
    expect(find.text('Share this reading'), findsOneWidget);
    expect(rete.richieste.any((r) => r.uri.path.endsWith('/share-image')), isTrue);
    expect(find.text('Ready: choose where to share.'), findsOneWidget);
    expect(find.text('Instagram'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
