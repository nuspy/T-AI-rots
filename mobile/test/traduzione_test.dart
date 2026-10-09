// v9.5, la traduzione dei contenuti sul telefono (ML Kit): il markdown resta intero (collegamenti, scorciatoie,
// immagini), l'articolo si legge tradotto col riquadro che lo dice e torna all'originale; la lingua di lettura segue
// quella dell'app, e una diversa scelta dal piè di pagina resta (in inglese non si scarica nulla).

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/componenti/bottoni.dart';
import 'package:tarots/componenti/modale.dart';
import 'package:tarots/componenti/premibile.dart';
import 'package:tarots/lingua/lingua.dart';
import 'package:tarots/traduzione/lingua_contenuti.dart';
import 'package:tarots/traduzione/motore.dart';
import 'package:tarots/traduzione/scelta_lingua.dart';
import 'package:tarots/traduzione/testo_protetto.dart';

import 'aiuti/scena.dart';
import 'fixtures/prezzi/rete.dart';

/// Un motore finto: «traduce» mettendo `‹hu›` davanti, ricorda cosa ha scaricato e cosa gli si è chiesto.
class MotoreFinto implements MotoreTraduzione {
  final List<String> scaricati = [];
  final List<String> frasi = [];
  bool scaricaRiesce = true;

  @override
  bool get disponibile => true;

  @override
  Future<bool> modelloPresente(String lingua) async => scaricati.contains(lingua);

  @override
  Future<bool> scarica(String lingua) async {
    if (!scaricaRiesce) return false;
    scaricati.add(lingua);
    return true;
  }

  @override
  Future<String> traduci(String testo, {required String da, required String a}) async {
    frasi.add(testo);
    return '‹$a› $testo';
  }
}

Future<String> _finta(String f) async => '‹hu› $f';

/// Le ombre come le vuole il controllo finale di flutter_test (montaApp le accende per i golden).
void finisciScena() => debugDisableShadows = true;

void main() {
  group('il markdown resta intero', () {
    test('collegamenti: si traduce solo il testo, l\'indirizzo resta', () async {
      final r = await traduciRiga('Read [the Tower](/cards/maj-16) today.', _finta);
      expect(r, contains('[‹hu› the Tower](/cards/maj-16)'));
      expect(r, startsWith('‹hu› Read'));
    });

    test('scorciatoie, immagini, codice e indirizzi non si toccano', () async {
      const riga = 'See [[card:the-tower]] and ![a moon](/media/1.jpg), `code` at https://tarots.chat/x';
      final r = await traduciRiga(riga, _finta);
      expect(r, contains('[[card:the-tower]]'));
      expect(r, contains('![a moon](/media/1.jpg)'));
      expect(r, contains('`code`'));
      expect(r, contains('https://tarots.chat/x'));
    });

    test('il prefisso markdown resta davanti', () async {
      expect(await traduciRiga('## A title', _finta), '## ‹hu› A title');
      expect(await traduciRiga('- an item', _finta), '- ‹hu› an item');
    });

    test('se la traduzione perde un segnaposto, la riga resta com\'era', () async {
      const riga = 'Open [[card:the-sun]] now';
      expect(await traduciRiga(riga, (f) async => 'something else'), riga);
    });

    test('codice, tabelle e righe vuote restano; il resto riga per riga', () async {
      const testo = 'First line\n\n```\nnot this\n```\n| a | b |\nLast line';
      final r = await traduciMarkdown(testo, _finta);
      expect(r, '‹hu› First line\n\n```\nnot this\n```\n| a | b |\n‹hu› Last line');
    });
  });

  testWidgets('un articolo si legge tradotto, e torna all\'originale', (tester) async {
    final motore = MotoreFinto();
    await montaApp(
      tester,
      rotta: '/blog/how-to-read-tarot-cards',
      larghezza: 390,
      altezza: 844,
      rete: retePrezziDiario(),
      linguaContenuti: 'hu',
      motore: motore,
    );
    await assesta(tester);
    expect(motore.scaricati, contains('hu'));
    expect(find.textContaining('‹hu› How to Read Tarot Cards'), findsWidgets);
    expect(find.text('Translated automatically on your device from English.'), findsOneWidget);

    await tester.ensureVisible(find.text('Show the original (English)'));
    await tester.tap(find.text('Show the original (English)'));
    await assesta(tester);
    expect(find.textContaining('‹hu› How to Read Tarot Cards'), findsNothing);
    expect(find.text('Translate into Magyar'), findsOneWidget);
    expect(tester.takeException(), isNull);
    finisciScena();
  });

  testWidgets('in inglese non si traduce e non si scarica nulla', (tester) async {
    final motore = MotoreFinto();
    await montaApp(
      tester,
      rotta: '/blog/how-to-read-tarot-cards',
      larghezza: 390,
      altezza: 844,
      rete: retePrezziDiario(),
      linguaContenuti: 'en',
      motore: motore,
    );
    await assesta(tester);
    expect(motore.scaricati, isEmpty);
    expect(motore.frasi, isEmpty);
    expect(find.text('Translated automatically on your device from English.'), findsNothing);
    finisciScena();
  });

  testWidgets('la lingua di lettura segue l\'app, senza una domanda a parte al primo avvio', (tester) async {
    final motore = MotoreFinto();
    final app = await montaApp(tester, rotta: '/', larghezza: 390, altezza: 844, lingua: 'hu', motore: motore);
    await assesta(tester);
    expect(find.byType(SceltaLinguaContenuti), findsNothing);
    expect(app.read(linguaContenutiProvider), 'hu');
    expect(app.read(archivioProvider).leggi(chiaveLinguaContenuti), isNull);
    finisciScena();
  });

  testWidgets(
    'dal piè di pagina un\'altra lingua di lettura: resta, e non segue più l\'app; il pulsante resta in vista',
    (tester) async {
      final motore = MotoreFinto();
      final app = await montaApp(tester, rotta: '/', larghezza: 360, altezza: 640, motore: motore);
      await assesta(tester);
      final voce = find.byType(VoceLinguaContenuti);
      await tester.ensureVisible(voce);
      await tester.pump();
      await tester.tap(voce);
      await assesta(tester);
      // L'elenco scorre nel suo riquadro, «Continua» resta sotto, dentro lo schermo.
      expect(find.byType(RiquadroElenco), findsOneWidget);
      final continua = tester.getRect(find.text('Continue'));
      expect(continua.bottom, lessThanOrEqualTo(640));
      expect(
        tester.getRect(find.ancestor(of: find.text('Continue'), matching: find.byType(Bottone))).height,
        greaterThanOrEqualTo(48),
      );
      await tester.enterText(find.byType(EditableText).last, 'deutsch');
      await tester.pump();
      await tester.tap(find.text('Deutsch'));
      await tester.pump();
      await tester.tap(find.text('Continue'));
      await assesta(tester);
      expect(motore.scaricati, ['de']);
      expect(app.read(archivioProvider).leggi(chiaveLinguaContenuti), 'de');
      // L'app cambia lingua: la lettura resta in tedesco.
      await app.read(linguaProvider.notifier).imposta('it');
      await assesta(tester);
      expect(app.read(linguaContenutiProvider), 'de');
      // Scegliere di nuovo la lingua dell'app torna a seguirla.
      app.read(linguaContenutiProvider.notifier).scegli('it');
      expect(app.read(archivioProvider).leggi(chiaveLinguaContenuti), isNull);
      await app.read(linguaProvider.notifier).imposta('en');
      await assesta(tester);
      expect(app.read(linguaContenutiProvider), 'en');
      expect(tester.takeException(), isNull);
      finisciScena();
    },
  );

  testWidgets('dove il telefono non sa tradurre, la voce del piè di pagina non c\'è', (tester) async {
    await montaApp(tester, rotta: '/', larghezza: 390, altezza: 844);
    await assesta(tester);
    expect(find.byType(VoceLinguaContenuti), findsOneWidget);
    expect(find.descendant(of: find.byType(VoceLinguaContenuti), matching: find.byType(Premibile)), findsNothing);
    finisciScena();
  });

  test('l\'elenco: l\'interfaccia e l\'inglese in cima, poi tutte le lingue di ML Kit', () {
    final l = ordineLingue('hu');
    expect(l.take(2), ['hu', 'en']);
    expect(l.toSet(), lingueMlKit.toSet());
    expect(l.length, greaterThan(50));
    for (final c in lingueMlKit) {
      expect(nomiLingue.containsKey(c), isTrue, reason: 'manca il nome di $c');
    }
  });
}
