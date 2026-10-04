// Le pagine dell'account (profilo, privacy, eliminazione) con l'API finta: le fixture vere dell'API aggiornata
// (`test/fixtures/profilo/`, lette con GET da http://localhost:8108), più qualche stato composto a mano (un abbonamento a
// pagamento, uno dello store, un ordine col PDF, un indirizzo) dalla forma delle risposte del backend.

import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart' show Override;
import 'package:flutter_test/flutter_test.dart';
import 'package:share_plus/share_plus.dart';
import 'package:tarots/app.dart';
import 'package:tarots/componenti/bottoni.dart';
import 'package:tarots/profilo/comuni.dart';
import 'package:tarots/rotte/router.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';

/// L'API finta delle pagine dell'account; [abbonamento] sceglie lo stato dell'abbonamento (`attivo`, `store`, `free`).
AdattatoreFinto reteProfilo({String abbonamento = 'attivo'}) {
  final rete = apiDaFixture();
  RispostaFinta f(String nome) => RispostaFinta.fixture('profilo/$nome.json');
  rete.risposte.addAll({
    '/me/abbonamento': (_) => f(switch (abbonamento) {
      'store' => 'abbonamento_store',
      'free' => 'abbonamento',
      _ => 'abbonamento_attivo',
    }),
    '/me/privacy': (_) => f('privacy_scelta'),
    '/consenso': (_) => f('consenso_scelto'),
    '/privacy/titolare': (_) => f('titolare'),
    '/plans': (_) => f('piani'),
    '/me/orders': (_) => f('ordini_uno'),
    '/me/addresses': (_) => f('indirizzi_uno'),
    '/me/statistiche': (_) => f('statistiche'),
    '/me/decks': (_) => f('miei_mazzi'),
    '/abbonamenti/pubblico': (_) => RispostaFinta.json({'banner_prova': false, 'prova_disponibile': true}),
    'POST /me/abbonamento/rinnovo': (_) => RispostaFinta.json({
      'abbonamento': {
        ...(_json('profilo/abbonamento_attivo.json')['abbonamento']! as Map<String, Object?>),
        'rinnovo_automatico': false,
      },
    }),
    'POST /me/cancellazione': (_) => RispostaFinta.json({
      'richiesta_il': '2026-10-04T10:00:00+02:00',
      'definitiva_il': '2026-11-03T10:00:00+01:00',
      'eseguita_il': null,
      'annullabile': true,
      'giorni_ripensamento': 30,
      'sessioni_chiuse': true,
    }),
  });
  return rete;
}

Map<String, Object?> _json(String nome) =>
    jsonDecode(File('test/fixtures/$nome').readAsStringSync()) as Map<String, Object?>;

/// Monta l'app sulla [rotta] con le [altre] sostituzioni (la condivisione finta).
Future<ProviderContainer> montaAccount(
  WidgetTester tester,
  String rotta, {
  AdattatoreFinto? rete,
  List<Override> altre = const [],
  double larghezza = 390,
  double altezza = 844,
}) async {
  await tester.runAsync(caricaCaratteri);
  tester.platformDispatcher.accessibilityFeaturesTestValue = const FakeAccessibilityFeatures(disableAnimations: true);
  addTearDown(tester.platformDispatcher.clearAccessibilityFeaturesTestValue);
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = Size(larghezza, altezza);
  addTearDown(tester.view.reset);
  final c = ProviderContainer(
    overrides: [...sostituzioni(lingua: 'en', rete: rete ?? reteProfilo()), ...altre],
    retry: (_, _) => null,
  );
  addTearDown(c.dispose);
  await tester.pumpWidget(UncontrolledProviderScope(container: c, child: const TarotsApp()));
  c.read(routerProvider).go(rotta);
  await assesta(tester);
  return c;
}

void main() {
  testWidgets('il profilo mostra le sezioni del sito, con l\'abbonamento a pagamento', (tester) async {
    await montaAccount(tester, '/profile');
    for (final testo in [
      'Your details',
      'Subscription',
      'Monthly Basic',
      'Automatic renewal',
      'Your personal cards',
      'Gender',
      'How your reader speaks to you',
      'Invite those you love',
      'DRER3KFW',
      'Your picture and public name',
      'Your orders',
      'Shipping addresses',
      'Ada Lovelace',
      'Usage statistics',
      'Privacy and consents',
      'App statistics',
    ]) {
      expect(find.text(testo, skipOffstage: false), findsWidgets, reason: testo);
    }
    // Niente sezione «Sicurezza» (2FA di Keycloak): nell'app si entra con Google o Apple.
    expect(find.text('Account security', skipOffstage: false), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('spegnere il rinnovo chiede la conferma formale e poi lo spegne', (tester) async {
    final rete = reteProfilo();
    await montaAccount(tester, '/profile', rete: rete);
    final interruttore = find.text('Renew automatically', skipOffstage: false);
    await tester.ensureVisible(interruttore);
    await tester.pump();
    await tester.tap(interruttore);
    await assesta(tester);
    expect(find.text('Turn off automatic renewal?'), findsOneWidget);
    await tester.tap(find.text('Yes, turn off renewal'));
    await assesta(tester);
    expect(rete.richieste.any((r) => r.method == 'POST' && r.uri.path == '/me/abbonamento/rinnovo'), isTrue);
    expect(rete.corpi.whereType<String>().any((c) => c.contains('"attivo":false')), isTrue);
    expect(find.text("Automatic renewal is off. We've sent you a confirmation email.", skipOffstage: false), findsOneWidget);
  });

  testWidgets('un abbonamento dello store rimanda allo store, senza interruttore', (tester) async {
    await montaAccount(tester, '/profile', rete: reteProfilo(abbonamento: 'store'));
    expect(find.textContaining('Google Play', skipOffstage: false), findsWidgets);
    expect(find.text('Renew automatically', skipOffstage: false), findsNothing);
  });

  testWidgets('l\'invito si condivide col foglio del telefono, con il collegamento del sito pubblico', (tester) async {
    final condivisi = <ShareParams>[];
    await montaAccount(
      tester,
      '/profile',
      altre: [condivisioneProvider.overrideWithValue((p) async => condivisi.add(p))],
    );
    final bottone = find.text('Share your invitation', skipOffstage: false);
    await tester.ensureVisible(bottone);
    await tester.pump();
    await tester.tap(bottone);
    await assesta(tester);
    expect(condivisi.single.text, contains('DRER3KFW'));
    expect(condivisi.single.text, contains('https://tarots.chat/?invito=DRER3KFW'));
  });

  testWidgets('eliminare l\'account vuole la casella e la parola, poi dice quando', (tester) async {
    final rete = reteProfilo();
    await montaAccount(tester, '/account/elimina', rete: rete);
    expect(find.text('Delete your account', skipOffstage: false), findsWidgets);
    final casella = find.textContaining('I understand', skipOffstage: false);
    await tester.ensureVisible(casella);
    await tester.pump();
    await tester.tap(casella);
    await tester.pump();
    // La parola, come la scriverebbe chi usa l'app (il campo la porta in maiuscolo).
    tester.widget<EditableText>(find.byType(EditableText, skipOffstage: false).last).controller.text = 'DELETE';
    await tester.pump();
    final elimina = find.text('Delete my account', skipOffstage: false).last;
    await tester.ensureVisible(elimina);
    await tester.pump();
    await tester.tap(elimina);
    await assesta(tester);
    expect(rete.richieste.any((r) => r.method == 'POST' && r.uri.path == '/me/cancellazione'), isTrue);
    expect(find.text('Your account is closed', skipOffstage: false), findsOneWidget);
  });

  testWidgets('la privacy mostra il titolare dalla console e le scelte del telefono', (tester) async {
    await montaAccount(tester, '/privacy');
    expect(find.textContaining('Andrea Taini', skipOffstage: false), findsOneWidget);
    expect(find.text('Your choices on this device', skipOffstage: false), findsOneWidget);
    expect(
      find.byWidgetPredicate((w) => w is TestoSottolineato && w.testo == 'privacy@tarots.chat', skipOffstage: false),
      findsOneWidget,
    );
    // L'hosting compare nel riquadro del titolare e fra i responsabili del trattamento.
    expect(find.textContaining('Hivelocity', skipOffstage: false), findsWidgets);
    expect(find.text('Your choices on this browser', skipOffstage: false), findsNothing);
  });

  testWidgets('senza account il profilo invita a entrare', (tester) async {
    await tester.runAsync(caricaCaratteri);
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(390, 844);
    addTearDown(tester.view.reset);
    final c = ProviderContainer(
      overrides: sostituzioni(lingua: 'en', autenticata: false, rete: reteProfilo()),
      retry: (_, _) => null,
    );
    addTearDown(c.dispose);
    await tester.pumpWidget(UncontrolledProviderScope(container: c, child: const TarotsApp()));
    c.read(routerProvider).go('/profile');
    await assesta(tester);
    expect(find.text('Sign in to manage your account.', skipOffstage: false), findsOneWidget);
  });
}
