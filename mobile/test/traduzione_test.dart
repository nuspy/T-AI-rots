// v9.5, la traduzione dei contenuti sul telefono (ML Kit): il markdown resta intero (collegamenti, scorciatoie,
// immagini), l'articolo si legge tradotto col riquadro che lo dice e torna all'originale, la lingua di lettura si
// sceglie al primo avvio solo dove il telefono sa tradurre (in inglese non si scarica nulla).

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/archivio.dart';
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

  testWidgets('al primo avvio si sceglie la lingua di lettura, e il modello si scarica', (tester) async {
    final motore = MotoreFinto();
    final app = await montaApp(tester, rotta: '/', larghezza: 390, altezza: 844, motore: motore);
    await assesta(tester);
    expect(find.byType(DialogoLinguaContenuti), findsOneWidget);
    // In cima l'interfaccia (inglese); si cerca e si sceglie il magiaro.
    await tester.enterText(find.byType(EditableText).last, 'magy');
    await tester.pump();
    await tester.tap(find.text('Magyar'));
    await tester.pump();
    await tester.ensureVisible(find.text('Continue'));
    await tester.tap(find.text('Continue'));
    await assesta(tester);
    expect(motore.scaricati, ['hu']);
    expect(find.byType(DialogoLinguaContenuti), findsNothing);
    expect(app.read(archivioProvider).leggi(chiaveLinguaContenuti), 'hu');
    finisciScena();
  });

  testWidgets('dove il telefono non sa tradurre, il primo avvio non chiede nulla', (tester) async {
    await montaApp(tester, rotta: '/', larghezza: 390, altezza: 844);
    await assesta(tester);
    expect(find.byType(DialogoLinguaContenuti), findsNothing);
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
