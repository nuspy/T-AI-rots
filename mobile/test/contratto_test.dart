// Il contratto fra l'app e il backend.
//
// Due fonti:
// - `test/fixtures/openapi.json`, generato dall'applicazione FastAPI senza avviarla (`tool/genera_openapi.py`): ogni
//   endpoint che l'app chiama esiste col metodo giusto, e i corpi che l'app manda rispettano gli schemi (campi,
//   pattern, limiti). Le risposte del backend sono quasi tutte `Dict[str, Any]` (non tipizzate nello schema);
// - le risposte vere dell'API locale salvate in `test/fixtures/*.json`: i modelli scritti a mano le leggono senza
//   perdere campi che l'app usa.
// `/e` e `/e/dimentica` (lanterna) sono fuori dallo schema (`include_in_schema=False`): li copre `lanterna_test.dart`.

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/consensi/consensi.dart';
import 'package:tarots/modelli/account.dart';
import 'package:tarots/modelli/carta.dart';
import 'package:tarots/modelli/notifiche.dart';
import 'package:tarots/modelli/pubblici.dart';
import 'package:tarots/modelli/store.dart';
import 'package:tarots/pagine/blog.dart' show sceltePerPagina;

/// Gli endpoint che l'app chiama (`lib/api/api.dart`), come compaiono nello schema.
const List<(String, String)> endpointApp = [
  ('get', '/cards'),
  ('get', '/cards/{card_id}'),
  ('get', '/spreads'),
  ('get', '/spreads/{spread_id}'),
  ('get', '/daily-card/today'),
  ('get', '/impostazioni-pubbliche'),
  ('get', '/eta-minima'),
  ('get', '/blog/nove'),
  // Il diario (v9.4: elenchi a pagine anche per carta e stesa, sezioni ricche).
  ('get', '/blog/posts'),
  ('get', '/blog/posts/{slug}'),
  ('get', '/blog/sections'),
  ('get', '/blog/sections/{slug}'),
  ('get', '/blog/tags'),
  ('get', '/decks'),
  ('get', '/me/daily-card'),
  ('get', '/me/profile'),
  ('get', '/me/readings'),
  ('get', '/me/readings/{reading_id}'),
  ('get', '/me/billing'),
  ('get', '/consenso'),
  ('post', '/consensi'),
  ('post', '/me/eta'),
  ('post', '/readings/{reading_id}/reveal/{posizione}'),
  ('post', '/readings/{reading_id}/synthesis'),
  // Fase 9: gli acquisti negli store, le notifiche, i collegamenti verificati.
  ('get', '/billing/store/catalogo'),
  ('post', '/billing/store/google/verifica'),
  ('post', '/billing/store/apple/verifica'),
  ('post', '/me/dispositivi'),
  ('delete', '/me/dispositivi'),
  ('get', '/me/preferenze-notifica'),
  ('put', '/me/preferenze-notifica'),
  ('put', '/me/fuso-orario'),
  ('post', '/notifiche/aperta'),
  ('get', '/app/collegamenti/assetlinks.json'),
  ('get', '/app/collegamenti/apple-app-site-association'),
];

Map<String, Object?> leggi(String nome) =>
    jsonDecode(File('test/fixtures/$nome').readAsStringSync()) as Map<String, Object?>;

void main() {
  final schema = leggi('openapi.json');
  final percorsi = schema['paths']! as Map<String, Object?>;
  final componenti = (schema['components']! as Map<String, Object?>)['schemas']! as Map<String, Object?>;

  Map<String, Object?> operazione(String metodo, String percorso) =>
      (percorsi[percorso]! as Map<String, Object?>)[metodo]! as Map<String, Object?>;

  Map<String, Object?> corpo(String metodo, String percorso) {
    final rb = operazione(metodo, percorso)['requestBody']! as Map<String, Object?>;
    final rif = (((rb['content']! as Map)['application/json']! as Map)['schema']! as Map)[r'$ref']! as String;
    return componenti[rif.split('/').last]! as Map<String, Object?>;
  }

  Map<String, Object?> proprieta(Map<String, Object?> s, String nome) =>
      (s['properties']! as Map<String, Object?>)[nome]! as Map<String, Object?>;

  test('ogni endpoint dell\'app esiste nel backend col metodo giusto', () {
    final mancanti = [
      for (final (m, p) in endpointApp)
        if (!(percorsi[p] as Map<String, Object?>? ?? {}).containsKey(m)) '${m.toUpperCase()} $p',
    ];
    expect(mancanti, isEmpty);
  });

  test('le letture pubbliche accettano ?lang= (carte, stese, carta di oggi)', () {
    for (final p in ['/cards', '/cards/{card_id}', '/spreads', '/spreads/{spread_id}', '/daily-card/today']) {
      final parametri = (operazione('get', p)['parameters'] as List<Object?>? ?? []).cast<Map<String, Object?>>();
      expect(parametri.map((x) => x['name']), contains('lang'), reason: p);
    }
  });

  test('v9.4: GET /blog/posts accetta carta e stesa, e ogni scelta per pagina (10/25/50); /blog/nove i recenti', () {
    Map<String, Object?> parametro(String percorso, String nome) =>
        ((operazione('get', percorso)['parameters']! as List<Object?>).cast<Map<String, Object?>>().firstWhere(
                  (x) => x['name'] == nome,
                )['schema']
                as Map<String, Object?>?) ??
        const {};
    // `Optional[str]` con un pattern: `{anyOf: [{type: string, pattern}, {type: null}]}`.
    String pattern(Map<String, Object?> s) =>
        (s['anyOf']! as List<Object?>).cast<Map<String, Object?>>().firstWhere((x) => x['pattern'] != null)['pattern']!
            as String;
    for (final (nome, esempio) in [('carta', 'maj-17'), ('stesa', 'croce-celtica')]) {
      expect(RegExp(pattern(parametro('/blog/posts', nome))).hasMatch(esempio), isTrue, reason: nome);
    }
    final per = parametro('/blog/posts', 'per_pagina');
    for (final n in sceltePerPagina) {
      expect(n, inInclusiveRange((per['minimum']! as num).toInt(), (per['maximum']! as num).toInt()));
    }
    final recenti = parametro('/blog/nove', 'recenti');
    expect(sceltePerPagina.map((n) => n.clamp(0, 12)), everyElement(lessThanOrEqualTo(recenti['maximum']! as num)));
  });

  test('POST /consensi: le scelte dell\'app rispettano lo schema (origine android/ios, categorie, versione)', () {
    final s = corpo('post', '/consensi');
    expect(s['required'], containsAll(['scelte', 'versione_informativa']));
    final origine = RegExp(proprieta(s, 'origine')['pattern']! as String);
    expect(origine.hasMatch('android'), isTrue);
    expect(origine.hasMatch('ios'), isTrue);
    final versione = proprieta(s, 'versione_informativa');
    expect(versioneConsensi.length, inInclusiveRange(versione['minLength']! as int, versione['maxLength']! as int));
    final rif = ((proprieta(s, 'scelte')['items']! as Map)[r'$ref']! as String).split('/').last;
    final scelta = componenti[rif]! as Map<String, Object?>;
    final tipo = RegExp(proprieta(scelta, 'tipo')['pattern']! as String);
    final valore = RegExp(proprieta(scelta, 'valore')['pattern']! as String);
    for (final c in categorieApp) {
      expect(tipo.hasMatch(c), isTrue, reason: c);
    }
    expect(valore.hasMatch('accettato') && valore.hasMatch('rifiutato'), isTrue);
    expect(categorieApp.length, lessThanOrEqualTo(proprieta(s, 'scelte')['maxItems']! as int));
  });

  test('POST /me/eta: anni ammessi (14–16 nei paesi europei) e origine dell\'app', () {
    final s = corpo('post', '/me/eta');
    final anni = proprieta(s, 'anni');
    for (final a in [14, 15, 16]) {
      expect(a, inInclusiveRange((anni['minimum']! as num).toInt(), (anni['maximum']! as num).toInt()));
    }
    expect(RegExp(proprieta(s, 'origine')['pattern']! as String).hasMatch('ios'), isTrue);
  });

  test('Fase 9: la verifica degli acquisti riceve ciò che manda l\'app', () {
    final google = corpo('post', '/billing/store/google/verifica');
    expect(google['required'], containsAll(['productId', 'purchaseToken']));
    final apple = corpo('post', '/billing/store/apple/verifica');
    expect(apple['required'], contains('signedTransaction'));
    final catalogo = (operazione('get', '/billing/store/catalogo')['parameters']! as List<Object?>)
        .cast<Map<String, Object?>>()
        .map((x) => x['name']);
    expect(catalogo, containsAll(['piattaforma', 'paese_store', 'lang']));
  });

  test('Fase 9: il dispositivo delle notifiche (FCM, android/ios, lingua, fuso, versione)', () {
    final s = corpo('post', '/me/dispositivi');
    final nomi = (s['properties']! as Map<String, Object?>).keys;
    expect(nomi, containsAll(['canale', 'piattaforma', 'token', 'lingua', 'fuso_orario', 'versione_app']));
    String elenco(Map<String, Object?> p) => jsonEncode(p);
    expect(elenco(proprieta(s, 'canale')), contains('fcm'));
    expect(elenco(proprieta(s, 'piattaforma')), allOf(contains('android'), contains('ios')));
    final via = corpo('delete', '/me/dispositivi');
    expect((via['properties']! as Map<String, Object?>).keys, containsAll(['canale', 'token']));
    final aperta = corpo('post', '/notifiche/aperta');
    expect(aperta['required'], containsAll(['invio', 'firma']));
  });

  group('i modelli leggono le risposte vere dell\'API', () {
    test('carta (scheda completa)', () {
      final c = Carta.fromJson(leggi('carta.json'));
      expect(c.id, 'maj-06');
      expect(c.letteraEbraica, isNotNull);
      expect(c.ambiti, isNotEmpty);
      expect(c.nomeIn('en'), c.nome);
      expect(c.nomeIn('it'), c.nomeIt);
    });

    test('elenco delle carte in italiano: 78, ognuna col suo nome', () {
      final elenco = (jsonDecode(File('test/fixtures/carte_it.json').readAsStringSync()) as List<Object?>)
          .cast<Map<String, Object?>>()
          .map(Carta.fromJson)
          .toList();
      expect(elenco.length, 78);
      expect(elenco.every((c) => c.nomeIn('it').isNotEmpty), isTrue);
    });

    test('stesa', () {
      final s = Stesa.fromJson(leggi('stesa.json'));
      expect(s.posizioni.length, greaterThan(1));
      expect(s.carteDaScegliere, greaterThan(0));
    });

    test('carta di oggi e carta del giorno personale', () {
      final oggi = CartaOggi.fromJson(leggi('carta_oggi.json'));
      expect(oggi.testo, isNotEmpty);
      final mia = CartaDelGiorno.fromJson(leggi('carta_del_giorno.json'));
      expect(mia.serie, isNonNegative);
      expect(DateTime.tryParse(mia.giorno), isNotNull);
    });

    test('impostazioni pubbliche, profilo, storico, lettura, nove articoli', () {
      expect(ImpostazioniPubbliche.fromJson(leggi('impostazioni.json')).creditiIscrizione, isPositive);
      final p = Profilo.fromJson(leggi('profilo.json'));
      expect(p.id, isPositive);
      expect(p.nomeMostrato, isNotEmpty);
      final storico = ElencoLetture.fromJson(leggi('letture.json'));
      expect(storico.letture.length, lessThanOrEqualTo(storico.totale));
      final l = Lettura.fromJson(leggi('lettura.json'));
      expect(l.cards, isNotEmpty);
      expect(l.stesaDati?.posizioni, isNotEmpty);
      expect(l.dignita, isNotEmpty);
      final nove = Nove.fromJson(leggi('nove.json'));
      expect(nove.recenti, isNotEmpty);
    });

    test('Fase 9: preferenze delle notifiche e catalogo dello store', () {
      final p = PreferenzeNotifica.fromJson(leggi('preferenze_notifica.json'));
      expect(p.oraCarta, '08:30');
      expect(p.dispositivi.single.canale, 'webpush');
      final c = CatalogoStore.fromJson(leggi('catalogo_store.json'));
      expect(c.prodotti, isNotEmpty);
      expect(c.prodotti.map((x) => x.piano.slug), everyElement(isNotEmpty));
      expect(c.appAccountToken, isNotNull);
    });
  });
}
