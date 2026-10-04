// Le statistiche interne: il porting di lanterna-osservatore (formato dei lotti, page view, engagement, consenso).

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/analytics/lanterna.dart';

void main() {
  late List<Map<String, Object?>> lotti;
  late DateTime ora;
  late Lanterna l;

  List<Map<String, Object?>> eventi() => [
    for (final lotto in lotti) ...(lotto['eventi']! as List<Object?>).cast<Map<String, Object?>>(),
  ];

  setUp(() {
    lotti = [];
    ora = DateTime(2026, 10, 3, 12);
    l = Lanterna(
      invia: (corpo) async => lotti.add(corpo),
      lingua: () => 'it',
      piattaforma: 'android',
      adesso: () => ora,
      intervallo: const Duration(hours: 1),
    );
  });

  tearDown(() => l.spegni());

  test('senza il consenso statistiche parte il livello base, come nel sito: senza identificativo', () async {
    l.pagina('/it');
    l.traccia('question_submitted', {'entry': 'hero'});
    await l.svuota();
    expect(l.inCoda, 0);
    expect(l.estesa, isFalse);
    expect(lotti.single.containsKey('id'), isFalse);
    expect(eventi().map((e) => e['n']), ['page_view', 'question_submitted']);
  });

  test('col consenso: il lotto ha il formato di lanterna e porta l\'identificativo', () async {
    l.pagina('/card-of-the-day', utm: {'utm_source': 'newsletter', 'altro': 'x'});
    l.estendi('id-prova');
    ora = ora.add(const Duration(seconds: 2));
    await l.svuota();
    expect(lotti.single['v'], 1);
    expect(lotti.single['lingua'], 'it');
    expect(lotti.single['id'], 'id-prova');
    final e = eventi().single;
    expect(e['n'], 'page_view');
    expect(e['p'], '/card-of-the-day');
    expect(e['dt'], 2000);
    expect(e['x'], {'piattaforma': 'android'});
  });

  test('page_view a ogni cambio di rotta (non due volte la stessa), con gli utm', () async {
    l.estendi('id');
    l.pagina('/', utm: {'utm_source': 'x', 'utm_medium': ''});
    l.pagina('/');
    l.pagina('/cards');
    await l.svuota();
    final viste = eventi().where((e) => e['n'] == 'page_view').toList();
    expect(viste.map((e) => e['p']), ['/', '/cards']);
    expect(viste.first['u'], {'utm_source': 'x'});
    expect(viste.last.containsKey('u'), isFalse);
  });

  test('engagement: il tempo attivo fra le interazioni e lo scorrimento, al cambio di pagina', () async {
    l.estendi('id');
    l.pagina('/');
    for (var i = 0; i < 4; i++) {
      ora = ora.add(const Duration(seconds: 5));
      l.scorrimento(.25 * (i + 1));
    }
    // 40 secondi senza toccare nulla: non contano.
    ora = ora.add(const Duration(seconds: 40));
    l.pagina('/cards');
    await l.svuota();
    final eng = eventi().firstWhere((e) => e['n'] == 'engagement');
    expect(eng['p'], '/');
    expect(eng['d'], 20000);
    expect(eng['x'], {'scroll': 100, 'piattaforma': 'android'});
  });

  test('alla pausa dell\'app si chiude la pagina e si manda tutto', () async {
    l.estendi('id');
    l.pagina('/');
    ora = ora.add(const Duration(seconds: 3));
    l.interazione();
    await l.inPausa();
    expect(eventi().map((e) => e['n']), ['page_view', 'engagement']);
    expect(l.inCoda, 0);
  });

  test('lotti da 20, e un lotto parte da solo a 10 eventi', () async {
    l.estendi('id');
    l.pagina('/');
    for (var i = 0; i < 25; i++) {
      l.traccia('tema', {'tema': 'amore'});
    }
    await l.svuota();
    expect(lotti.every((lotto) => (lotto['eventi']! as List<Object?>).length <= 20), isTrue);
    expect(eventi().length, 26);
  });

  test('nomi non validi e percorsi esclusi si scartano', () async {
    l.estendi('id');
    l.pagina('/admin/utenti');
    l.traccia('Non Valido');
    l.pagina('/');
    l.traccia('cta_testata');
    await l.svuota();
    expect(eventi().map((e) => '${e['n']} ${e['p']}'), ['page_view /', 'cta_testata /']);
  });

  test('revocato il consenso gli eventi continuano senza identificativo, anche quelli già in coda', () async {
    l.estendi('id');
    l.pagina('/');
    l.riduci();
    await l.svuota();
    expect(lotti.single.containsKey('id'), isFalse);
    expect(eventi().single['n'], 'page_view');
  });

  test('spegnere (l\'app si chiude) butta la coda e non manda più niente', () async {
    l.pagina('/');
    l.spegni();
    l.pagina('/cards');
    await l.svuota();
    expect(lotti, isEmpty);
  });

  test('un invio che fallisce non solleva errori', () async {
    final rotta = Lanterna(invia: (_) => Future.error(StateError('rete')), lingua: () => 'en', piattaforma: 'ios')
      ..estendi('id')
      ..pagina('/');
    await rotta.svuota();
    rotta.spegni();
  });

  test('l\'identificativo è casuale, 32 cifre esadecimali', () {
    final a = nuovoIdentificativo();
    expect(a, matches(RegExp(r'^[0-9a-f]{32}$')));
    expect(nuovoIdentificativo(), isNot(a));
  });
}
