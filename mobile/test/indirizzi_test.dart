// Il porting di `frontend/lib/indirizzi.ts`: gli stessi risultati del codice TypeScript del sito, indirizzo per
// indirizzo (i risultati attesi li scrive `tool/indirizzi_attesi.mjs` eseguendo il TypeScript).

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/rotte/indirizzi.dart';
import 'package:tarots/rotte/router.dart';

void main() {
  final attesi = jsonDecode(File('test/fixtures/indirizzi_attesi.json').readAsStringSync()) as Map<String, Object?>;
  Map<String, Object?> sezione(String nome) => attesi[nome]! as Map<String, Object?>;

  test('risolvi() come il proxy del sito', () {
    for (final MapEntry(key: p, value: v) in sezione('risolvi').entries) {
      final atteso = v! as Map<String, Object?>;
      final r = risolvi(p);
      expect(
        {'lingua': r.lingua.name, 'interno': r.interno, 'pubblica': r.pubblica, 'reindirizza': r.reindirizza},
        atteso,
        reason: p,
      );
    }
  });

  test('interno(), pubblico(), normalizza(), indicizzabile()', () {
    for (final MapEntry(key: p, value: v) in sezione('interno').entries) {
      expect(interno(p), v, reason: p);
    }
    for (final MapEntry(key: p, value: v) in sezione('pubblico').entries) {
      final atteso = v! as Map<String, Object?>;
      expect(pubblico(LinguaPubblica.en, p), atteso['en'], reason: 'en $p');
      expect(pubblico(LinguaPubblica.it, p), atteso['it'], reason: 'it $p');
    }
    for (final MapEntry(key: p, value: v) in sezione('normalizza').entries) {
      expect(normalizza(p), v, reason: p);
    }
    for (final MapEntry(key: p, value: v) in sezione('indicizzabile').entries) {
      expect(indicizzabile(p), v, reason: p);
    }
  });

  test('un collegamento del sito porta alla rotta dell\'app, con la query', () {
    expect(reindirizza(Uri.parse('/it/carta-del-giorno')), '/daily-card');
    expect(reindirizza(Uri.parse('/card-of-the-day?utm_source=x')), '/daily-card?utm_source=x');
    expect(reindirizza(Uri.parse('/carte/maj-17')), '/cards/maj-17');
    expect(reindirizza(Uri.parse('/cards/maj-17')), isNull);
    expect(reindirizza(Uri.parse('/')), isNull);
  });

  test('le statistiche ricevono l\'indirizzo che il sito manderebbe', () {
    expect(pubblico(linguaPubblica('en'), '/daily-card'), '/card-of-the-day');
    expect(pubblico(linguaPubblica('hu'), '/daily-card'), '/card-of-the-day');
    expect(pubblico(linguaPubblica('it'), '/daily-card'), '/it/carta-del-giorno');
    expect(pubblico(linguaPubblica('it'), '/'), '/it');
  });
}
