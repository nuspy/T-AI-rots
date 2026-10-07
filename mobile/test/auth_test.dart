// L'accesso (Fase 6 per il client Keycloak): non si prova dal vivo, qui con un Keycloak e una cassaforte finti.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/auth/configurazione.dart';
import 'package:tarots/auth/fornitore.dart';
import 'package:tarots/auth/sessione.dart';

import 'aiuti/finti.dart';

ConfigAccesso config(Piattaforma p) => ConfigAccesso(
  issuer: 'https://auth.prova/realms/tarots',
  clientId: 'tarot-mobile',
  redirect: ConfigAccesso.redirectApp,
  scope: ConfigAccesso.scopeApp,
  idpHint: p == Piattaforma.android ? 'google' : 'apple',
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final adesso = DateTime(2026, 10, 3, 12);

  Credenziali credenziali(String accesso, {Duration dura = const Duration(minutes: 5), String? refresh = 'r1'}) =>
      Credenziali(
        accessToken: accesso,
        scadenza: adesso.add(dura),
        refreshToken: refresh,
        idToken: jwtFinto({'given_name': 'Anna'}),
      );

  ProviderContainer contenitore(FornitoreFinto fornitore, {String? refresh, Piattaforma p = Piattaforma.android}) {
    final c = ProviderContainer(
      overrides: [
        authDisattivataProvider.overrideWithValue(false),
        piattaformaProvider.overrideWithValue(p),
        configAccessoProvider.overrideWithValue(config(p)),
        fornitoreOAuthProvider.overrideWithValue(fornitore),
        cassaforteProvider.overrideWithValue(cassaforteFinta(refresh)),
        orologioProvider.overrideWithValue(() => adesso),
      ],
    );
    addTearDown(c.dispose);
    return c;
  }

  test('la configurazione: client tarot-mobile, redirect dello schema dell\'app, offline_access', () {
    final c = config(Piattaforma.android);
    expect(c.clientId, 'tarot-mobile');
    expect(c.redirect, 'chat.tarots.app:/oauth2redirect');
    expect(c.scope, containsAll(['openid', 'offline_access']));
    expect(c.revoca, 'https://auth.prova/realms/tarots/protocol/openid-connect/revoke');
    // Senza KEYCLOAK_URL (questi test non lo passano) l'accesso non è configurato: l'app resta anonima.
    expect(ConfigAccesso.per(Piattaforma.android), isNull);
  });

  test('Android entra con Google, iOS con Apple (kc_idp_hint)', () async {
    for (final (p, atteso) in [(Piattaforma.android, 'google'), (Piattaforma.ios, 'apple')]) {
      final f = FornitoreFinto(accesso: credenziali('a1'));
      final c = contenitore(f, p: p);
      c.read(sessioneProvider);
      await Future<void>.delayed(Duration.zero);
      await c.read(sessioneProvider.notifier).entra();
      expect(f.entrate.single.idpHint, atteso);
      final s = c.read(sessioneProvider);
      expect((s.autenticata, s.nome), (true, 'Anna'));
      expect(await c.read(cassaforteProvider).leggi(), 'r1', reason: 'il refresh token va nella cassaforte');
    }
  });

  test('all\'avvio la sessione riprende dal refresh token salvato', () async {
    final f = FornitoreFinto(rinnovo: credenziali('a2', refresh: 'r2'));
    final c = contenitore(f, refresh: 'r0');
    expect(c.read(sessioneProvider).pronta, isFalse);
    await Future<void>.delayed(Duration.zero);
    await Future<void>.delayed(Duration.zero);
    expect(c.read(sessioneProvider).autenticata, isTrue);
    expect(f.rinnovati, ['r0']);
    expect(await c.read(cassaforteProvider).leggi(), 'r2', reason: 'il refresh token ruotato si salva');
  });

  test('senza refresh token: pronta e anonima', () async {
    final c = contenitore(FornitoreFinto());
    c.read(sessioneProvider);
    await Future<void>.delayed(Duration.zero);
    final s = c.read(sessioneProvider);
    expect((s.pronta, s.autenticata), (true, false));
    expect(await c.read(sessioneProvider.notifier).token(), isNull);
  });

  test('il token che scade entro 30 secondi si rinnova prima della richiesta, una volta sola', () async {
    final f = FornitoreFinto(
      accesso: credenziali('a1', dura: const Duration(seconds: 20)),
      rinnovo: credenziali('a2'),
    );
    final c = contenitore(f);
    c.read(sessioneProvider);
    await Future<void>.delayed(Duration.zero);
    final n = c.read(sessioneProvider.notifier);
    await n.entra();
    final token = await Future.wait([n.token(), n.token(), n.token()]);
    expect(token, ['a2', 'a2', 'a2']);
    expect(f.rinnovati.length, 1);
  });

  test('un refresh token rifiutato chiude la sessione e svuota la cassaforte', () async {
    final f = FornitoreFinto(errore: const ErroreAccesso('invalid_grant'));
    final c = contenitore(f, refresh: 'scaduto');
    c.read(sessioneProvider);
    await Future<void>.delayed(Duration.zero);
    await Future<void>.delayed(Duration.zero);
    expect(c.read(sessioneProvider).autenticata, isFalse);
    expect(await c.read(cassaforteProvider).leggi(), isNull);
  });

  test('l\'accesso annullato non cambia niente', () async {
    final f = FornitoreFinto(errore: const ErroreAccesso('annullato', annullato: true));
    final c = contenitore(f);
    c.read(sessioneProvider);
    await Future<void>.delayed(Duration.zero);
    await expectLater(c.read(sessioneProvider.notifier).entra(), throwsA(isA<ErroreAccesso>()));
    expect(c.read(sessioneProvider).autenticata, isFalse);
  });

  test('uscire revoca il refresh token e lo cancella', () async {
    final f = FornitoreFinto(accesso: credenziali('a1'));
    final c = contenitore(f);
    c.read(sessioneProvider);
    await Future<void>.delayed(Duration.zero);
    await c.read(sessioneProvider.notifier).entra();
    await c.read(sessioneProvider.notifier).esci();
    expect(f.revocati, ['r1']);
    expect(c.read(sessioneProvider).autenticata, isFalse);
    expect(await c.read(cassaforteProvider).leggi(), isNull);
  });

  test('la sessione di sviluppo (AUTH_DISATTIVATA) è dentro senza token', () async {
    final c = ProviderContainer(overrides: [authDisattivataProvider.overrideWithValue(true)]);
    addTearDown(c.dispose);
    expect(c.read(sessioneProvider).autenticata, isTrue);
    expect(await c.read(sessioneProvider.notifier).token(), isNull);
  });

  test('nomeDaToken legge given_name, poi name, e non si rompe', () {
    expect(nomeDaToken(jwtFinto({'given_name': 'Ada', 'name': 'Ada L.'})), 'Ada');
    expect(nomeDaToken(jwtFinto({'name': 'Ada L.'})), 'Ada L.');
    expect(nomeDaToken('non.un.token!'), isNull);
    expect(nomeDaToken(null), isNull);
  });

  test('ruoliDaToken legge realm_access.roles, e non si rompe', () {
    expect(
      ruoliDaToken(
        jwtFinto({
          'realm_access': {
            'roles': ['admin', 'offline_access', 3],
          },
        }),
      ),
      ['admin', 'offline_access'],
    );
    expect(ruoliDaToken(jwtFinto({'name': 'Ada'})), isEmpty);
    expect(ruoliDaToken('non.un.token!'), isEmpty);
    expect(ruoliDaToken(null), isEmpty);
  });
}
