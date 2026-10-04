// I consensi del primo avvio (stesse categorie del banner del sito) e la conferma dell'età.

import 'dart:convert';

import 'package:cookie_jar/cookie_jar.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/api/api.dart';
import 'package:tarots/api/client.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/auth/sessione.dart';
import 'package:tarots/consensi/consensi.dart';
import 'package:tarots/consensi/eta.dart';

import 'aiuti/finti.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  late AdattatoreFinto rete;
  late ArchivioMemoria archivio;

  ProviderContainer contenitore({bool autenticata = false}) {
    final c = ProviderContainer(
      overrides: [
        archivioProvider.overrideWithValue(archivio),
        authDisattivataProvider.overrideWithValue(autenticata),
        configAccessoProvider.overrideWithValue(null),
        apiProvider.overrideWithValue(
          Api(
            creaDio(
              base: 'http://api.prova',
              lingua: () => 'it',
              fonte: FonteFinta(),
              cookie: CookieJar(),
              agente: 'prova',
              adattatore: rete,
            ),
          ),
        ),
      ],
    );
    addTearDown(c.dispose);
    return c;
  }

  setUp(() {
    archivio = ArchivioMemoria();
    rete = AdattatoreFinto({
      'POST /consensi': (r) =>
          RispostaFinta.json({'statistiche': 'accettato', 'google_analytics': 'rifiutato', 'pubblicita': null}),
      'GET /consenso': (_) => RispostaFinta.json({'statistiche': 'rifiutato', 'google_analytics': null}),
      'GET /eta-minima': (_) => RispostaFinta.json({'anni': 14, 'paese': 'IT'}),
      'POST /me/eta': (_) => RispostaFinta.json({'anni': 14}),
    });
  });

  test('al primo avvio si chiedono statistiche e Google Analytics (la pubblicità no)', () {
    final c = contenitore();
    expect(categorieApp, ['statistiche', 'google_analytics']);
    expect(c.read(consensiProvider).daChiedere, isTrue);
  });

  test('la scelta vale subito, va al server con origine e versione, e si ricorda', () async {
    final c = contenitore();
    await c.read(consensiProvider.notifier).scegli({'statistiche': 'accettato', 'google_analytics': 'rifiutato'});
    final stato = c.read(consensiProvider);
    expect(stato.daChiedere, isFalse);
    expect(stato.accettato('statistiche'), isTrue);
    expect(stato.daSincronizzare, isFalse);
    final corpo = jsonDecode(rete.corpi.last!) as Map<String, Object?>;
    expect(corpo['origine'], 'android');
    expect(corpo['versione_informativa'], versioneConsensi);
    expect(corpo['scelte'], [
      {'tipo': 'statistiche', 'valore': 'accettato'},
      {'tipo': 'google_analytics', 'valore': 'rifiutato'},
    ]);
    // Un nuovo avvio ritrova le scelte.
    expect(StatoConsensi.daJson(archivio.leggi(chiaveConsensi)).accettato('statistiche'), isTrue);
  });

  test('fuori rete la scelta resta sul telefono e si manda al prossimo avvio', () async {
    rete.risposte['POST /consensi'] = (_) => RispostaFinta.json({'detail': 'giù'}, stato: 503);
    final c = contenitore();
    await c.read(consensiProvider.notifier).scegli({'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'});
    expect(c.read(consensiProvider).daSincronizzare, isTrue);
    expect(c.read(consensiProvider).daChiedere, isFalse, reason: 'la richiesta non ricompare');

    rete.risposte['POST /consensi'] = (_) =>
        RispostaFinta.json({'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'});
    final dopo = contenitore();
    await dopo.read(consensiProvider.notifier).sincronizza();
    expect(dopo.read(consensiProvider).daSincronizzare, isFalse);
    expect(rete.richieste.where((r) => r.uri.path == '/consensi').length, 2);
  });

  test('senza scelte locali si adotta quella del server (chi entra con un account la ritrova)', () async {
    final c = contenitore();
    await c.read(consensiProvider.notifier).sincronizza();
    expect(c.read(consensiProvider).valori, {'statistiche': 'rifiutato'});
    expect(c.read(consensiProvider).daChiedere, isTrue, reason: 'google_analytics non è ancora scelto');
  });

  group('età minima', () {
    test('l\'età del paese viene dal server; senza risposta vale 16', () async {
      final c = contenitore();
      expect(await c.read(etaMinimaProvider.future), 14);
      rete.risposte.remove('GET /eta-minima');
      final senza = contenitore();
      expect(await senza.read(etaMinimaProvider.future), etaMinimaPredefinita);
    });

    test('«ho almeno N anni» si ricorda; con un account va al server con l\'origine', () async {
      final c = contenitore(autenticata: true);
      expect(c.read(etaProvider).daChiedere(14), isTrue);
      await c.read(etaProvider.notifier).conferma(14);
      expect(c.read(etaProvider).daChiedere(14), isFalse);
      expect(archivio.leggi(chiaveEta), '14');
      expect(jsonDecode(rete.corpi.last!), {'anni': 14, 'origine': 'android'});
    });

    test('senza account non si chiama il server; «Not now» rimanda solo per questa volta', () async {
      final c = contenitore();
      c.read(etaProvider.notifier).rimanda();
      expect(c.read(etaProvider).daChiedere(16), isFalse);
      expect(contenitore().read(etaProvider).daChiedere(16), isTrue);
      await c.read(etaProvider.notifier).conferma(16);
      expect(rete.richieste.where((r) => r.uri.path == '/me/eta'), isEmpty);
    });
  });
}
