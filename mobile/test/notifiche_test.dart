// Le notifiche (Fase 9) con Firebase finto (`ServizioPush` sostituito) e l'API finta: il permesso solo dopo un sì, la
// registrazione del token con piattaforma, lingua, fuso e versione, il token nuovo, l'uscita che toglie il
// dispositivo, il tocco che apre la pagina giusta e segna l'apertura, l'app senza Firebase, l'invito dopo la carta del
// giorno e la sezione del profilo.

import 'dart:async';
import 'dart:convert';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/auth/sessione.dart';
import 'package:tarots/notifiche/notifiche.dart';
import 'package:tarots/notifiche/push.dart';
import 'package:tarots/rotte/router.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';

/// Firebase finto.
class PushFinto implements ServizioPush {
  PushFinto({this.disponibile = true, this.risposta = PermessoPush.concesso});

  bool disponibile;
  PermessoPush risposta;
  PermessoPush attuale = PermessoPush.nonChiesto;
  int richiestePermesso = 0;
  String valore = 'token-fcm-1234567890-abcdefghij';
  bool cancellato = false;
  NomiCanali? canaliCreati;
  MessaggioPush? daIniziale;
  // ignore: close_sinks, vive quanto il test
  final StreamController<String> nuovi = StreamController<String>.broadcast();
  // ignore: close_sinks, vive quanto il test
  final StreamController<MessaggioPush> tocchi = StreamController<MessaggioPush>.broadcast();

  @override
  Future<bool> avvia() async => disponibile;

  @override
  Future<void> canali(NomiCanali nomi) async => canaliCreati = nomi;

  @override
  Future<PermessoPush> permesso() async => attuale;

  @override
  Future<PermessoPush> chiediPermesso() async {
    richiestePermesso++;
    return attuale = risposta;
  }

  @override
  Future<String?> token() async => cancellato ? null : valore;

  @override
  Stream<String> get tokenNuovi => nuovi.stream;

  @override
  Future<void> cancellaToken() async => cancellato = true;

  @override
  Stream<MessaggioPush> get toccate => tocchi.stream;

  @override
  Future<MessaggioPush?> iniziale() async => daIniziale;

  @override
  Future<bool> apriImpostazioni() async => true;
}

AdattatoreFinto reteNotifiche() {
  final rete = apiDaFixture();
  rete.risposte.addAll({
    'POST /me/dispositivi': (_) => RispostaFinta.json({'id': 7, 'canale': 'fcm', 'piattaforma': 'android', 'attivo': true}),
    'DELETE /me/dispositivi': (_) => RispostaFinta(204),
    'POST /notifiche/aperta': (_) => RispostaFinta(204),
    'PUT /me/fuso-orario': (_) => RispostaFinta.json({'fuso_orario': 'Europe/Rome'}),
    'PUT /me/preferenze-notifica': (_) => RispostaFinta.fixture('preferenze_notifica.json'),
  });
  return rete;
}

/// Aspetta [f] facendo girare l'app (le risposte finte in tempo vero, i microtask nel tempo finto del test): i futuri
/// dei provider nascono nella zona del test e non si completano dentro `runAsync`.
Future<T> aspetta<T>(WidgetTester tester, Future<T> f) async {
  var fatto = false;
  late T valore;
  unawaited(f.then((v) {
    valore = v;
    fatto = true;
  }));
  for (var giro = 0; giro < 50 && !fatto; giro++) {
    await assesta(tester);
  }
  expect(fatto, isTrue, reason: 'non è finito');
  return valore;
}

List<Map<String, Object?>> corpi(AdattatoreFinto rete, String metodo, String percorso) => [
  for (final (i, r) in rete.richieste.indexed)
    if (r.method == metodo && r.uri.path == percorso) jsonDecode(rete.corpi[i]!) as Map<String, Object?>,
];

void main() {
  test('il link di una notifica: la rotta dell\'app (anche dagli indirizzi pubblici), fuori gli altri siti', () {
    expect(destinazioneNotifica('/daily-card'), '/daily-card');
    expect(destinazioneNotifica('/card-of-the-day'), '/daily-card');
    expect(destinazioneNotifica('/it/carta-del-giorno?da=notifica'), '/daily-card?da=notifica');
    expect(destinazioneNotifica('https://tarots.chat/it/piano'), '/pricing');
    expect(destinazioneNotifica(''), '/');
    expect(destinazioneNotifica('https://example.com/x'), isNull);
  });

  testWidgets('il permesso si chiede solo al sì; poi il token va al server con lingua, fuso e versione', (tester) async {
    final push = PushFinto();
    final rete = reteNotifiche();
    final c = await montaApp(tester, rotta: '/', larghezza: 390, rete: rete, push: push, lingua: 'it');
    // All'avvio niente permesso chiesto e niente token mandato; i canali Android coi nomi nella lingua dell'app.
    expect(push.richiestePermesso, 0);
    expect(corpi(rete, 'POST', '/me/dispositivi'), isEmpty);
    expect(push.canaliCreati?.servizio, 'Carta del giorno e promemoria');
    expect(c.read(notificheProvider).disponibili, isTrue);

    final esito = await aspetta(tester, c.read(notificheProvider.notifier).attiva());
    expect(esito, EsitoAttivazione.attive);
    expect(push.richiestePermesso, 1);
    final corpo = corpi(rete, 'POST', '/me/dispositivi').single;
    expect(corpo['canale'], 'fcm');
    expect(corpo['piattaforma'], 'android');
    expect(corpo['token'], push.valore);
    expect(corpo['lingua'], 'it');
    expect(corpo['versione_app'], '1.0.0');
    expect(c.read(archivioProvider).leggi(chiaveNotificheAttive), '1');

    // Un token nuovo va al server da solo.
    push.nuovi.add('token-fcm-nuovo-0987654321-zyxwv');
    await assesta(tester);
    expect(corpi(rete, 'POST', '/me/dispositivi').last['token'], 'token-fcm-nuovo-0987654321-zyxwv');

    // All'uscita: il dispositivo si toglie dal server con la sessione ancora valida, il token si cancella.
    await aspetta(tester, c.read(primaDiUscireProvider).esegui());
    expect(corpi(rete, 'DELETE', '/me/dispositivi').single, {'canale': 'fcm', 'token': 'token-fcm-nuovo-0987654321-zyxwv'});
    expect(push.cancellato, isTrue);
    expect(c.read(archivioProvider).leggi(chiaveNotificheAttive), isNull);
    expect(c.read(notificheProvider).attive, isFalse);
    debugDisableShadows = true;
  });

  testWidgets('permesso negato: niente token al server', (tester) async {
    final push = PushFinto(risposta: PermessoPush.negato);
    final rete = reteNotifiche();
    final c = await montaApp(tester, rotta: '/', larghezza: 390, rete: rete, push: push);
    final esito = await aspetta(tester, c.read(notificheProvider.notifier).attiva());
    expect(esito, EsitoAttivazione.negato);
    expect(corpi(rete, 'POST', '/me/dispositivi'), isEmpty);
    expect(c.read(notificheProvider).permesso, PermessoPush.negato);
    debugDisableShadows = true;
  });

  testWidgets('senza Firebase l\'app funziona: notifiche non disponibili, nessuna richiesta', (tester) async {
    final rete = reteNotifiche();
    final c = await montaApp(tester, rotta: '/', larghezza: 390, rete: rete, push: PushFinto(disponibile: false));
    expect(c.read(notificheProvider).pronte, isTrue);
    expect(c.read(notificheProvider).disponibili, isFalse);
    final esito = await aspetta(tester, c.read(notificheProvider.notifier).attiva());
    expect(esito, EsitoAttivazione.nonSupportato);
    expect(corpi(rete, 'POST', '/me/dispositivi'), isEmpty);
    debugDisableShadows = true;
  });

  testWidgets('il tocco apre la pagina del link e segna l\'apertura con la firma', (tester) async {
    final push = PushFinto();
    final rete = reteNotifiche();
    final c = await montaApp(tester, rotta: '/', larghezza: 390, rete: rete, push: push);
    push.tocchi.add(
      const MessaggioPush(dati: {'link': '/card-of-the-day', 'invio': '7a1c4f9e-0000-4000-8000-000000000001', 'firma': 'abcdef1234'}),
    );
    await assesta(tester);
    expect(uriVisibile(c.read(routerProvider).routerDelegate.currentConfiguration).path, '/daily-card');
    expect(corpi(rete, 'POST', '/notifiche/aperta').single, {
      'invio': '7a1c4f9e-0000-4000-8000-000000000001',
      'firma': 'abcdef1234',
    });
    debugDisableShadows = true;
  });

  testWidgets('l\'app aperta da una notifica va alla sua pagina', (tester) async {
    final push = PushFinto()..daIniziale = const MessaggioPush(dati: {'link': '/profile'});
    final c = await montaApp(tester, rotta: '/', larghezza: 390, rete: reteNotifiche(), push: push);
    expect(uriVisibile(c.read(routerProvider).routerDelegate.currentConfiguration).path, '/profile');
    debugDisableShadows = true;
  });

  testWidgets('l\'invito dopo la carta del giorno: «sì» chiede il permesso, «non ora» lo fa tacere un mese', (tester) async {
    final push = PushFinto();
    final rete = reteNotifiche();
    final c = await montaApp(tester, rotta: '/daily-card', larghezza: 390, rete: rete, push: push);
    // Prima di girare la carta l'invito non c'è.
    expect(find.text('Shall we remind you every morning?', skipOffstage: false), findsNothing);
    final gira = find.text('Turn the card', skipOffstage: false).last;
    await tester.ensureVisible(gira);
    await tester.pump();
    await tester.tap(gira);
    await assesta(tester);
    final titolo = find.text('Shall we remind you every morning?', skipOffstage: false);
    expect(titolo, findsOneWidget);
    expect(push.richiestePermesso, 0);
    final no = find.text('Not now', skipOffstage: false);
    await tester.ensureVisible(no);
    await tester.pump();
    await tester.tap(no);
    await assesta(tester);
    expect(titolo, findsNothing);
    expect(push.richiestePermesso, 0);
    final n = c.read(notificheProvider.notifier);
    expect(n.invitoDaMostrare(DateTime.now()), isFalse);
    expect(n.invitoDaMostrare(DateTime.now().add(const Duration(days: 31))), isTrue);
    debugDisableShadows = true;
  });

  testWidgets('la sezione «Notifiche» del profilo: accende da qui, con le preferenze del sito', (tester) async {
    final push = PushFinto();
    final rete = reteNotifiche();
    await montaApp(tester, rotta: '/profile', larghezza: 390, rete: rete, push: push);
    expect(find.text('Notifications are off on this device.', skipOffstage: false), findsOneWidget);
    expect(find.text('Card of the day', skipOffstage: false), findsWidgets);
    expect(find.text('08:30', skipOffstage: false), findsOneWidget);
    expect(find.text('Notifications are also on for 1 other device.', skipOffstage: false), findsOneWidget);
    final attiva = find.text('Turn on notifications here', skipOffstage: false);
    await tester.ensureVisible(attiva);
    await tester.pump();
    await tester.tap(attiva);
    await assesta(tester);
    expect(push.richiestePermesso, 1);
    expect(find.text('Notifications are on on this device.', skipOffstage: false), findsOneWidget);
    // Una preferenza va al server.
    final promemoria = find.text('Reminders', skipOffstage: false);
    await tester.ensureVisible(promemoria);
    await tester.pump();
    await tester.tap(promemoria);
    await assesta(tester);
    expect(corpi(rete, 'PUT', '/me/preferenze-notifica').single, {'promemoria': false});
    debugDisableShadows = true;
  });
}
