/// Il client HTTP dell'API (`dio`), con ciò che `chiama()` di `frontend/lib/api.ts` fa nel browser:
///
/// - **base URL** da `--dart-define=API_URL=…` ([Config.apiUrl]);
/// - **`Accept-Language`** con la lingua dell'interfaccia, a ogni richiesta;
/// - **Bearer**: il token d'accesso della sessione, rinnovato se sta per scadere; dopo un 401 si rinnova una volta e
///   si ripete la richiesta, poi l'errore passa (la sessione è finita);
/// - **cookie jar persistente**: il cookie `tarots_anon` della lettura anonima (e dei consensi senza account) resta
///   su disco fra un avvio e l'altro, come nel browser con `credentials: "include"`.
library;

import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';

import '../auth/sessione.dart';

/// Le chiavi di `RequestOptions.extra` che il client capisce.
abstract final class Extra {
  /// Una richiesta da mandare senza token anche se c'è una sessione (le pagine pubbliche).
  static const String senzaToken = 'tarots.senzaToken';

  /// Una richiesta già ripetuta dopo un 401: non si ripete una seconda volta.
  static const String ripetuta = 'tarots.ripetuta';
}

/// L'agente dell'app per le statistiche (`lanterna` riconosce sistema e dispositivo dall'agente): `Android` e
/// `Mobile`, oppure `iPhone`/`iPad`, come i browser di quei dispositivi.
String agenteApp({required bool ios, required bool tablet, required String versione}) {
  final sistema = ios
      ? (tablet ? 'iPad; CPU OS like Mac OS X' : 'iPhone; CPU iPhone OS like Mac OS X')
      : (tablet ? 'Linux; Android; Tablet' : 'Linux; Android; Mobile');
  return 'Mozilla/5.0 ($sistema) TAROTSchat/$versione';
}

/// Lingua, agente e token su ogni richiesta.
class IntestazioniApi extends Interceptor {
  /// Con la lingua corrente (letta a ogni richiesta), la sessione e l'agente.
  IntestazioniApi({required this.lingua, required this.fonte, required this.agente});

  /// La lingua dell'interfaccia, letta al momento della richiesta.
  final String Function() lingua;

  /// Da dove viene il token.
  final FonteToken fonte;

  /// L'agente (`User-Agent`).
  final String agente;

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    options.headers['Accept-Language'] = lingua();
    options.headers['User-Agent'] = agente;
    if (options.extra[Extra.senzaToken] != true && !options.headers.containsKey('Authorization')) {
      final token = await fonte.token();
      if (token != null) options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
}

/// Un 401 su una richiesta con token: si rinnova il token una volta e si ripete. Dieci richieste scadute insieme
/// fanno un solo rinnovo perché la sessione ne tiene uno in corso alla volta (`Sessione.rinnova`). Non è un
/// `QueuedInterceptor`: la richiesta ripetuta ripasserebbe dalla stessa coda e la bloccherebbe.
class RinnovoSu401 extends Interceptor {
  /// Su [dio] (per ripetere la richiesta) con la sessione.
  RinnovoSu401(this.dio, this.fonte);

  /// Il client da cui ripetere.
  final Dio dio;

  /// La sessione.
  final FonteToken fonte;

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final richiesta = err.requestOptions;
    final conToken = richiesta.headers.containsKey('Authorization');
    if (err.response?.statusCode != 401 || !conToken || richiesta.extra[Extra.ripetuta] == true) {
      handler.next(err);
      return;
    }
    final nuovo = await fonte.rinnova();
    if (nuovo == null) {
      handler.next(err);
      return;
    }
    try {
      final risposta = await dio.fetch<Object?>(
        richiesta.copyWith(
          headers: {...richiesta.headers, 'Authorization': 'Bearer $nuovo'},
          extra: {...richiesta.extra, Extra.ripetuta: true},
        ),
      );
      handler.resolve(risposta);
    } on DioException catch (e) {
      handler.next(e);
    }
  }
}

/// Il client dell'API.
Dio creaDio({
  required String base,
  required String Function() lingua,
  required FonteToken fonte,
  required CookieJar cookie,
  required String agente,
  HttpClientAdapter? adattatore,
}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: base,
      connectTimeout: const Duration(seconds: 15),
      // Lo streaming della sintesi manda un `battito` ogni pochi secondi: un minuto e mezzo di silenzio è un guasto.
      receiveTimeout: const Duration(seconds: 90),
      headers: {'Accept': 'application/json'},
    ),
  );
  if (adattatore != null) dio.httpClientAdapter = adattatore;
  dio.interceptors.addAll([
    CookieManager(cookie),
    IntestazioniApi(lingua: lingua, fonte: fonte, agente: agente),
    RinnovoSu401(dio, fonte),
  ]);
  return dio;
}
