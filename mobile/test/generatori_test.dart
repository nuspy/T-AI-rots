// La fonte unica sito → app: gli ARB (dai dizionari della v2) e i token (da v2.css).

import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/l10n/testi.dart';
import 'package:tarots/tema/tema.dart';

Map<String, Object?> arb(String lingua) =>
    jsonDecode(File('lib/l10n/app_$lingua.arb').readAsStringSync()) as Map<String, Object?>;

void main() {
  final lingue = Directory('lib/l10n')
      .listSync()
      .map((f) => RegExp(r'app_(\w+)\.arb$').firstMatch(f.path)?.group(1))
      .whereType<String>()
      .toList();

  test('quindici lingue, tutte con le stesse voci dell\'inglese', () {
    expect(lingue.toSet(), {'en', 'it', 'hu', 'de', 'ru', 'uk', 'fr', 'es', 'pt', 'ro', 'pl', 'zh', 'hi', 'ko', 'ar'});
    final base = arb('en').keys.where((k) => !k.startsWith('@')).toSet();
    for (final l in lingue) {
      expect(arb(l).keys.where((k) => !k.startsWith('@')).toSet(), base, reason: l);
    }
  });

  test('le etichette corte della testata conservano gli a capo dei dizionari', () {
    final en = arb('en');
    expect(en['comune_nav_breve_fisica'], 'Your\ncards');
    expect(en['comune_testata_entra'], 'Sign\nin');
    expect(arb('it')['comune_nav_breve_fisica'], contains('\n'));
  });

  test('segnaposto e plurali diventano ICU, con i segnaposto dichiarati', () {
    final en = arb('en');
    expect(en['comune_testata_crediti_n'], '{n, plural, =1{1 credit} other{{n} credits}}');
    expect((en['@giorno_significato']! as Map)['placeholders'], {
      'carta': {'type': 'Object'},
    });
  });

  testWidgets('le classi generate danno i testi giusti, con plurali e argomenti', (tester) async {
    late AppLocalizations en;
    late AppLocalizations it;
    await tester.pumpWidget(
      Localizations(
        locale: const Locale('en'),
        delegates: const [AppLocalizations.delegate, DefaultWidgetsLocalizations.delegate],
        child: Builder(
          builder: (context) {
            en = AppLocalizations.of(context);
            return const SizedBox();
          },
        ),
      ),
    );
    it = await AppLocalizations.delegate.load(const Locale('it'));
    expect(en.comune_testata_crediti_n(1), '1 credit');
    expect(en.comune_testata_crediti_n(4), '4 credits');
    expect(en.giorno_significato('The Star'), 'The full meaning of The Star');
    expect(it.comune_testata_crediti_n(1), isNot(en.comune_testata_crediti_n(1)));
    expect(en.homeTemi.length, 6);
    expect(en.homeTemi.first.chiave, 'amore');
    expect(lingueTradotte, containsAll(['en', 'it', 'hu']));
  });

  test('i token vengono da v2.css', () {
    final css = File('../frontend/app/(v2)/v2.css').readAsStringSync();
    String variabile(String nome) => RegExp('$nome:\\s*([^;]+);').firstMatch(css)!.group(1)!.trim();
    String esadecimale(Color c) => '#${(c.toARGB32() & 0xFFFFFF).toRadixString(16).padLeft(6, '0')}';
    expect(esadecimale(Token.paper), variabile('--paper'));
    expect(esadecimale(Token.plum), variabile('--plum'));
    expect(esadecimale(Token.brassPale), variabile('--brass-pale'));
    expect(Token.puntiDiRottura, contains(760.0));
    expect(Token.gutter.per(360), 14.4);
    expect(Token.etichettaTestataTelefono, 8);
  });

  test('ARB e token sono aggiornati (lo script di controllo del sito)', () async {
    final esito = await Process.run('node', ['../frontend/scripts/controlla-mobile.mjs']);
    expect(esito.exitCode, 0, reason: '${esito.stdout}${esito.stderr}');
  }, skip: _senzaNode() ? 'node non c\'è: si controlla con node scripts/controlla-mobile.mjs' : false);
}

bool _senzaNode() {
  try {
    return Process.runSync('node', ['--version']).exitCode != 0;
  } on ProcessException {
    return true;
  }
}
