// Fase 6 nell'app: «Hai già un account sul sito?» (il codice per spostare l'accesso), la sessione che si interrompe
// quando il codice è stato usato sul sito, il nome chiesto se manca, e l'email nascosta di Apple.

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/auth/configurazione.dart';
import 'package:tarots/auth/fornitore.dart';
import 'package:tarots/auth/sessione.dart';
import 'package:tarots/consensi/consensi.dart';
import 'package:tarots/consensi/eta.dart';
import 'package:tarots/rotte/router.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';
import 'profilo_test.dart' show reteProfilo;

const ConfigAccesso _config = ConfigAccesso(
  issuer: 'https://auth.prova/realms/tarots',
  clientId: 'tarot-mobile',
  redirect: ConfigAccesso.redirectApp,
  scope: ConfigAccesso.scopeApp,
  idpHint: 'apple',
);

Credenziali _credenziali({String email = 'anna@example.com'}) => Credenziali(
  accessToken: jwtFinto({'given_name': 'Anna', 'email': email}),
  scadenza: DateTime.now().add(const Duration(hours: 1)),
  refreshToken: 'r2',
  idToken: jwtFinto({'given_name': 'Anna', 'email': email}),
);

/// L'app con un accesso vero (finto): la sessione riprende dal refresh token, o si interrompe se il fornitore rifiuta.
Future<ProviderContainer> _monta(
  WidgetTester tester, {
  required AdattatoreFinto rete,
  required FornitoreFinto fornitore,
  ArchivioMemoria? archivio,
}) async {
  await tester.runAsync(caricaCaratteri);
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = const Size(390, 844);
  addTearDown(tester.view.reset);
  final c = ProviderContainer(
    overrides: [
      ...sostituzioni(
        lingua: 'en',
        autenticata: false,
        rete: rete,
        accesso: _config,
        memoria:
            archivio ??
            ArchivioMemoria({
              'lingua': 'en',
              chiaveConsensi: const StatoConsensi(valori: {'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'})
                  .inJson(),
              chiaveEta: '16',
            }),
      ),
      fornitoreOAuthProvider.overrideWithValue(fornitore),
      cassaforteProvider.overrideWithValue(cassaforteFinta('r1')),
    ],
    retry: (_, _) => null,
  );
  addTearDown(c.dispose);
  await tester.pumpWidget(UncontrolledProviderScope(container: c, child: const TarotsApp()));
  await assesta(tester);
  return c;
}

void main() {
  test('l\'email del token e quella nascosta di Apple', () {
    expect(emailDaToken(jwtFinto({'email': 'x@privaterelay.appleid.com'})), 'x@privaterelay.appleid.com');
    expect(emailNascosta('x@PrivateRelay.AppleID.com'), isTrue);
    expect(emailNascosta('anna@example.com'), isFalse);
    expect(emailNascosta(null), isFalse);
  });

  testWidgets('il profilo crea il codice per il sito e lo mostra grande', (tester) async {
    final rete = reteProfilo();
    rete.risposte['POST /me/collega/codice'] = (_) => RispostaFinta.json({
      'codice': 'ABCD-EFGH',
      'scade_il': '2026-10-04T10:40:00Z',
      'validita_minuti': 10,
      'provider': ['apple'],
    });
    final c = await _monta(
      tester,
      rete: rete,
      fornitore: FornitoreFinto(rinnovo: _credenziali()),
    );
    expect(c.read(sessioneProvider).autenticata, isTrue);
    c.read(routerProvider).go('/profile');
    await assesta(tester);
    final crea = find.text('Create the code');
    await tester.ensureVisible(crea);
    await tester.pump();
    expect(find.text('Already have an account on the website?'), findsOneWidget);
    await tester.tap(crea);
    await assesta(tester);
    expect(find.text('ABCD-EFGH'), findsOneWidget);
    expect(find.text('Copy'), findsOneWidget);
    expect(find.text('Create a new code'), findsOneWidget);
  });

  testWidgets('niente da spostare: il messaggio del sito', (tester) async {
    final rete = reteProfilo();
    rete.risposte['POST /me/collega/codice'] = (_) => RispostaFinta.json({
      'detail': {'motivo': 'nessuna_identita'},
    }, stato: 409);
    final c = await _monta(
      tester,
      rete: rete,
      fornitore: FornitoreFinto(rinnovo: _credenziali()),
    );
    c.read(routerProvider).go('/profile');
    await assesta(tester);
    final crea = find.text('Create the code');
    await tester.ensureVisible(crea);
    await tester.pump();
    await tester.tap(crea);
    await assesta(tester);
    expect(find.text('The app account has no sign-in to move.'), findsOneWidget);
  });

  testWidgets('il refresh token non vale più (il codice è stato usato sul sito): l\'app propone di rientrare', (
    tester,
  ) async {
    final c = await _monta(
      tester,
      rete: apiDaFixture(),
      fornitore: FornitoreFinto(errore: const ErroreAccesso('invalid_grant')),
    );
    expect(c.read(sessioneProvider).interrotta, isTrue);
    expect(find.text('Sign in again'), findsWidgets);
    await tester.tap(find.text('Close'));
    await tester.pump();
    expect(c.read(sessioneProvider).interrotta, isFalse);
    expect(find.text('Sign in again'), findsNothing);
  });

  testWidgets('con l\'email nascosta di Apple il primo accesso apre il profilo sul codice', (tester) async {
    final archivio = ArchivioMemoria({
      'lingua': 'en',
      chiaveConsensi: const StatoConsensi(valori: {'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'})
          .inJson(),
      chiaveEta: '16',
    });
    final c = await _monta(
      tester,
      rete: reteProfilo(),
      fornitore: FornitoreFinto(rinnovo: _credenziali(email: 'zz@privaterelay.appleid.com')),
      archivio: archivio,
    );
    expect(uriVisibile(c.read(routerProvider).routerDelegate.currentConfiguration).path, '/profile');
    expect(archivio.leggi(chiaveCodiceProposto), 'zz@privaterelay.appleid.com');
    expect(find.textContaining('You signed in with Apple and hid your email', skipOffstage: false), findsOneWidget);
  });
}
