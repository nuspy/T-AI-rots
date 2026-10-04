// Il client dell'API: lingua, Bearer, rinnovo dopo un 401, errori del server, cookie jar persistente.

import 'dart:io';

import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/api/api.dart';
import 'package:tarots/api/client.dart';
import 'package:tarots/api/errori.dart';

import 'aiuti/finti.dart';

void main() {
  late AdattatoreFinto rete;
  late FonteFinta sessione;
  late CookieJar cookie;
  var lingua = 'it';

  Api crea() => Api(
    creaDio(
      base: 'http://api.prova',
      lingua: () => lingua,
      fonte: sessione,
      cookie: cookie,
      agente: agenteApp(ios: false, tablet: false, versione: '1.0.0'),
      adattatore: rete,
    ),
  );

  setUp(() {
    lingua = 'it';
    sessione = FonteFinta(attuale: 'vecchio', nuovo: 'nuovo');
    cookie = CookieJar();
    rete = AdattatoreFinto({
      '/impostazioni-pubbliche': (_) => RispostaFinta.fixture('impostazioni.json'),
      '/daily-card/today': (_) => RispostaFinta.fixture('carta_oggi.json'),
      '/me/profile': (r) => r.headers['Authorization'] == 'Bearer nuovo'
          ? RispostaFinta.fixture('profilo.json')
          : RispostaFinta.json({'detail': 'token scaduto'}, stato: 401),
      '/me/daily-card': (_) => RispostaFinta.json({'detail': 'token scaduto'}, stato: 401),
      '/me/billing': (_) => RispostaFinta.json({
        'detail': {'motivo': 'crediti', 'messaggio': 'Non hai crediti'},
      }, stato: 402),
    });
  });

  test('ogni richiesta porta la lingua corrente, l\'agente e il Bearer', () async {
    final api = crea();
    await api.saldo().catchError((Object _) => null);
    lingua = 'hu';
    await api.saldo().catchError((Object _) => null);
    expect(rete.richieste[0].headers['Accept-Language'], 'it');
    expect(rete.richieste[1].headers['Accept-Language'], 'hu');
    expect(rete.richieste[0].headers['Authorization'], 'Bearer vecchio');
    expect(rete.richieste[0].headers['User-Agent'], contains('Android'));
    expect(rete.richieste[0].headers['User-Agent'], contains('Mobile'));
  });

  test('le letture pubbliche non mandano il token', () async {
    final oggi = await crea().cartaDiOggi('hu');
    expect(oggi.carta.id, isNotEmpty);
    final r = rete.richieste.single;
    expect(r.headers.containsKey('Authorization'), isFalse);
    expect(r.uri.queryParameters['lang'], 'en', reason: 'le lingue senza contenuti propri leggono l\'inglese');
  });

  test('dopo un 401 rinnova il token una volta sola e ripete la richiesta', () async {
    final profilo = await crea().profilo();
    expect(profilo.id, isPositive);
    expect(sessione.rinnovi, 1);
    expect(rete.richieste.map((r) => r.headers['Authorization']), ['Bearer vecchio', 'Bearer nuovo']);
  });

  test('se anche dopo il rinnovo è 401, l\'errore passa (niente giri infiniti)', () async {
    await expectLater(crea().cartaDelGiorno(), throwsA(isA<ErroreApi>().having((e) => e.stato, 'stato', 401)));
    expect(sessione.rinnovi, 1);
    expect(rete.richieste.length, 2);
  });

  test('se il rinnovo non riesce, la sessione è finita: 401', () async {
    sessione.nuovo = null;
    await expectLater(crea().profilo(), throwsA(isA<ErroreApi>().having((e) => e.stato, 'stato', 401)));
    expect(rete.richieste.length, 1);
  });

  test('il motivo del server arriva a chi mostra l\'errore', () async {
    await expectLater(
      crea().saldo(),
      throwsA(
        isA<ErroreApi>()
            .having((e) => e.stato, 'stato', 402)
            .having((e) => e.motivo, 'motivo', 'Non hai crediti')
            .having((e) => e.codice, 'codice', 'crediti'),
      ),
    );
  });

  test('una rete assente è un ErroreApi con stato 0', () async {
    final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:9', connectTimeout: const Duration(seconds: 2)));
    await expectLater(Api(dio).impostazioniPubbliche(), throwsA(isA<ErroreApi>().having((e) => e.stato, 'stato', 0)));
  });

  group('cookie tarots_anon', () {
    test('il cookie della lettura anonima torna nelle richieste successive', () async {
      rete.risposte['POST /consensi'] = (_) => RispostaFinta.json(
        {'statistiche': 'accettato'},
        intestazioni: {
          'set-cookie': ['tarots_anon=abc123; Max-Age=31536000; Path=/; HttpOnly; SameSite=lax'],
        },
      );
      final api = crea();
      await api.registraConsensi([(tipo: 'statistiche', valore: 'accettato')], versione: 'v3', origine: 'android');
      await api.impostazioniPubbliche();
      expect(rete.richieste.last.headers['cookie'], contains('tarots_anon=abc123'));
    });

    test('su disco resta fra un avvio e l\'altro (PersistCookieJar)', () async {
      final cartella = await Directory.systemTemp.createTemp('tarots_cookie');
      addTearDown(() => cartella.delete(recursive: true));
      final uri = Uri.parse('http://api.prova/consensi');
      final primo = PersistCookieJar(storage: FileStorage('${cartella.path}/'));
      await primo.saveFromResponse(uri, [Cookie('tarots_anon', 'xyz')..maxAge = 3600]);
      // Un altro «avvio»: un jar nuovo sulla stessa cartella.
      final secondo = PersistCookieJar(storage: FileStorage('${cartella.path}/'));
      final letti = await secondo.loadForRequest(Uri.parse('http://api.prova/readings/anonime'));
      expect(letti.map((c) => '${c.name}=${c.value}'), contains('tarots_anon=xyz'));
    });
  });

  test('il corpo dei consensi ha l\'origine dell\'app', () async {
    rete.risposte['POST /consensi'] = (_) => RispostaFinta.json({'statistiche': 'rifiutato'});
    await crea().registraConsensi([(tipo: 'statistiche', valore: 'rifiutato')], versione: 'v3', origine: 'ios');
    expect(rete.corpi.last, contains('"origine":"ios"'));
    expect(rete.corpi.last, contains('"versione_informativa":"v3"'));
  });
}
