/// L'app intera per i test a schermo (golden): dati dalle risposte salvate dell'API locale, immagini delle carte da
/// `frontend/public/cards/`, caratteri veri, nessuna rete, nessun Firebase, primo avvio già fatto.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:cookie_jar/cookie_jar.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:flutter_test/flutter_test.dart';
import 'package:material_ui/material_ui.dart';
import 'package:tarots/acquisti/negozio.dart';
import 'package:tarots/analytics/firebase.dart';
import 'package:tarots/analytics/lanterna.dart';
import 'package:tarots/analytics/tracciato.dart';
import 'package:tarots/api/api.dart';
import 'package:tarots/api/client.dart';
import 'package:tarots/app.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/auth/configurazione.dart';
import 'package:tarots/auth/sessione.dart';
import 'package:tarots/componenti/carta.dart';
import 'package:tarots/componenti/diario.dart';
import 'package:tarots/componenti/oracolo.dart';
import 'package:tarots/consensi/consensi.dart';
import 'package:tarots/consensi/eta.dart';
import 'package:tarots/notifiche/fuso.dart';
import 'package:tarots/notifiche/push.dart';
import 'package:tarots/rotte/router.dart';

import 'finti.dart';

bool _caricati = false;

/// I caratteri dell'app (dagli asset) e, come ripiego per i simboli (✦ ♁ ☌) e le scritture che DM Sans e Libre
/// Baskerville non hanno, quelli di Windows che usa anche Edge nelle catture del sito.
Future<void> caricaCaratteri() async {
  if (_caricati) return;
  _caricati = true;
  Future<void> famiglia(String nome, List<String> asset) async {
    final l = FontLoader(nome);
    for (final a in asset) {
      l.addFont(rootBundle.load(a));
    }
    await l.load();
  }

  await famiglia('DM Sans', [
    for (final p in ['Regular', 'Medium', 'SemiBold', 'Bold']) 'assets/fonts/DMSans-$p.ttf',
  ]);
  await famiglia('Libre Baskerville', [
    for (final p in ['Regular', 'Italic', 'Bold', 'BoldItalic']) 'assets/fonts/LibreBaskerville-$p.ttf',
  ]);
  Future<void> sistema(String nome, String file) async {
    final f = File('C:/Windows/Fonts/$file');
    if (!f.existsSync()) return;
    final l = FontLoader(nome)..addFont(f.readAsBytes().then(ByteData.sublistView));
    await l.load();
  }

  await sistema('Arial', 'arial.ttf');
  await sistema('Georgia', 'georgia.ttf');
  await sistema('sans-serif', 'seguisym.ttf');
  await sistema('serif', 'seguisym.ttf');
}

/// Le risposte dell'API locale salvate in `test/fixtures/`.
AdattatoreFinto apiDaFixture() => AdattatoreFinto({
  '/impostazioni-pubbliche': (_) => RispostaFinta.fixture('impostazioni.json'),
  '/daily-card/today': (_) => RispostaFinta.fixture('carta_oggi.json'),
  '/me/daily-card': (_) => RispostaFinta.fixture('carta_del_giorno.json'),
  '/me/billing': (_) => RispostaFinta.fixture('conto.json'),
  '/me/profile': (_) => RispostaFinta.fixture('profilo.json'),
  '/blog/nove': (_) => RispostaFinta.fixture('nove.json'),
  '/decks': (_) => RispostaFinta.json(_mazzi()),
  '/consenso': (_) => RispostaFinta.json({'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'}),
  '/eta-minima': (_) => RispostaFinta.json({'anni': 16}),
  // Nessun silenzio (0 minuti): niente timer dell'oracolo che resti in sospeso alla fine di un test.
  '/impostazioni-chat': (_) => RispostaFinta.json({'proattiva_minuti_inattivita': 0, 'proattiva_max_per_visita': 3}),
  // Lo storico vuoto e nessuna apertura proattiva: la barra dell'oracolo mostra «dock_vuoto», come il sito senza chat.
  '/chat/proattiva': (_) => RispostaFinta.json({'turni': <Object?>[]}),
  'POST /chat/proattiva/avvio': (_) => RispostaFinta.json({'turno': null}, stato: 201),
  // Il banner della prova spento (come il backend locale senza la console «Abbonamenti» accesa).
  '/abbonamenti/pubblico': (_) => RispostaFinta.json({'banner_prova': false, 'prova_disponibile': true}),
  // Fase 9: le preferenze delle notifiche (quelle predefinite della console), un browser già iscritto.
  '/me/preferenze-notifica': (_) => RispostaFinta.fixture('preferenze_notifica.json'),
});

Object? _mazzi() => jsonDecode(File('test/fixtures/mazzi.json').readAsStringSync());

/// Il percorso di una carta del sito sul disco.
File fileCarta(String id) => File('../frontend/public/cards/$id.webp');

/// Le sostituzioni dei servizi per l'app di prova.
List<Override> sostituzioni({
  required String lingua,
  bool autenticata = true,
  AdattatoreFinto? rete,
  ArchivioMemoria? memoria,
  ConfigAccesso? accesso,
  Negozio? negozio,
  ServizioPush? push,
}) {
  final archivio =
      memoria ??
      ArchivioMemoria({
        'lingua': lingua,
        chiaveConsensi: const StatoConsensi(valori: {'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'})
            .inJson(),
        chiaveEta: '16',
      });
  final adattatore = rete ?? apiDaFixture();
  return [
    archivioProvider.overrideWithValue(archivio),
    authDisattivataProvider.overrideWithValue(autenticata),
    configAccessoProvider.overrideWithValue(accesso),
    statisticheGoogleProvider.overrideWithValue(StatisticheGoogleSpente()),
    cookieJarProvider.overrideWithValue(CookieJar()),
    dioProvider.overrideWith(
      (ref) => creaDio(
        base: 'http://api.prova',
        lingua: () => lingua,
        fonte: FonteFinta(),
        cookie: CookieJar(),
        agente: 'prova',
        adattatore: adattatore,
      ),
    ),
    immagineCartaProvider.overrideWithValue((id) => FileImage(fileCarta(id))),
    temaOracoloProvider.overrideWithValue(0),
    // Le statistiche interne senza invio periodico: nessun timer resta in sospeso alla fine di un test.
    lanternaProvider.overrideWith(
      (ref) => Lanterna(invia: (_) async {}, lingua: () => lingua, piattaforma: 'android', temporizzata: false),
    ),
    rintoccoProvider.overrideWithValue(() async {}),
    // Fase 9: niente store, niente Firebase, niente fuso del telefono (i test non hanno i plugin).
    negozioProvider.overrideWithValue(negozio),
    servizioPushProvider.overrideWithValue(push ?? ServizioPushSpento()),
    leggiFusoProvider.overrideWithValue(() async => null),
    immagineMediaProvider.overrideWithValue((p) => FileImage(fileCarta('maj-06'))),
  ];
}

/// Monta l'app sulla rotta [rotta], larga [larghezza] e alta [altezza], e aspetta dati e immagini.
Future<ProviderContainer> montaApp(
  WidgetTester tester, {
  required String rotta,
  required double larghezza,
  double altezza = 800,
  String lingua = 'en',
  bool autenticata = true,
  AdattatoreFinto? rete,
  Negozio? negozio,
  ServizioPush? push,
}) async {
  // I file veri (caratteri di sistema) si leggono fuori dal tempo finto del test.
  await tester.runAsync(caricaCaratteri);
  await precaricaCarte(tester);
  tester.platformDispatcher.accessibilityFeaturesTestValue = const FakeAccessibilityFeatures(disableAnimations: true);
  addTearDown(tester.platformDispatcher.clearAccessibilityFeaturesTestValue);
  // Le ombre vere (flutter_test le disegna piene per default): il confronto col sito le vuole sfumate.
  // Si rimette com'era in [fotografa]: flutter_test controlla, prima della fine del test, che sia tornato vero.
  debugDisableShadows = false;
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = Size(larghezza, altezza);
  addTearDown(tester.view.reset);
  final contenitore = ProviderContainer(
    overrides: sostituzioni(lingua: lingua, autenticata: autenticata, rete: rete, negozio: negozio, push: push),
    retry: (_, _) => null,
  );
  addTearDown(contenitore.dispose);
  await tester.pumpWidget(UncontrolledProviderScope(container: contenitore, child: const TarotsApp()));
  if (rotta != '/') contenitore.read(routerProvider).go(rotta);
  await assesta(tester);
  return contenitore;
}

/// Decodifica in anticipo, in tempo vero, le immagini delle carte del sito: restano nella cache delle immagini e i
/// widget le trovano pronte (decodificate dentro il tempo finto del test non finirebbero mai).
///
/// Le immagini si chiedono con lo stesso percorso che usano i widget ([fileCarta], con `/`): `listSync` su Windows
/// darebbe la barra rovesciata e la chiave della cache non coinciderebbe. La cache si allarga per tenerle tutte.
Future<void> precaricaCarte(WidgetTester tester) async {
  final cache = tester.binding.imageCache;
  if (cache.maximumSize < 2000) {
    final prima = (cache.maximumSize, cache.maximumSizeBytes);
    cache
      ..maximumSize = 2000
      ..maximumSizeBytes = 1 << 30;
    addTearDown(() {
      cache
        ..maximumSize = prima.$1
        ..maximumSizeBytes = prima.$2;
    });
  }
  await tester.runAsync(() async {
    final nomi = Directory('../frontend/public/cards')
        .listSync()
        .whereType<File>()
        .map((f) => f.uri.pathSegments.last)
        .where((n) => n.endsWith('.webp'))
        .map((n) => n.substring(0, n.length - 5));
    for (final nome in nomi) {
      final pronta = Completer<void>();
      FileImage(fileCarta(nome))
          .resolve(ImageConfiguration.empty)
          .addListener(
            ImageStreamListener(
              (_, _) => pronta.isCompleted ? null : pronta.complete(),
              onError: (_, _) => pronta.isCompleted ? null : pronta.complete(),
            ),
          );
      await pronta.future;
    }
  });
}

/// Lascia arrivare le risposte finte (in tempo vero) e ridisegna.
Future<void> assesta(WidgetTester tester) async {
  for (var giro = 0; giro < 4; giro++) {
    await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 30)));
    await tester.pump(const Duration(milliseconds: 100));
  }
}

/// Allunga la finestra fino a far stare tutta la pagina (per le catture a pagina intera, come quelle del sito).
Future<void> paginaIntera(WidgetTester tester, double larghezza) async {
  for (var giro = 0; giro < 3; giro++) {
    final scorrevoli = find.byType(Scrollable).evaluate().map((e) => (e as StatefulElement).state as ScrollableState);
    final pagina = scorrevoli
        .where((s) => s.position.axis == Axis.vertical)
        .fold<ScrollableState?>(
          null,
          (migliore, s) =>
              migliore == null || s.position.maxScrollExtent > migliore.position.maxScrollExtent ? s : migliore,
        );
    final extra = pagina?.position.maxScrollExtent ?? 0;
    if (extra < 1) return;
    tester.view.physicalSize = Size(larghezza, tester.view.physicalSize.height + extra);
    await tester.pump();
    await assesta(tester);
  }
}

/// Confronta [cosa] con l'immagine [file] e rimette le ombre di flutter_test come le vuole il controllo finale.
Future<void> fotografa(Finder cosa, String file) async {
  try {
    await expectLater(cosa, matchesGoldenFile(file));
  } finally {
    debugDisableShadows = true;
  }
}
