/// Servizi finti per i test: nessuna rete vera, nessun Keycloak, nessun Firebase, nessun modello.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:tarots/auth/cassaforte.dart';
import 'package:tarots/auth/configurazione.dart';
import 'package:tarots/auth/fornitore.dart';
import 'package:tarots/auth/sessione.dart';

/// Una risposta finta.
class RispostaFinta {
  /// Uno stato, un corpo (testo o pezzi di byte per lo streaming) e le intestazioni.
  RispostaFinta(this.stato, {this.corpo = '', this.pezzi, this.intestazioni = const {}, this.ritardo = Duration.zero});

  /// Dal JSON di un file di `test/fixtures/`.
  factory RispostaFinta.fixture(String nome, {int stato = 200}) =>
      RispostaFinta(stato, corpo: File('test/fixtures/$nome').readAsStringSync(), intestazioni: _json);

  /// Da un oggetto JSON.
  factory RispostaFinta.json(Object? dati, {int stato = 200, Map<String, List<String>> intestazioni = const {}}) =>
      RispostaFinta(stato, corpo: jsonEncode(dati), intestazioni: {..._json, ...intestazioni});

  static const Map<String, List<String>> _json = {
    Headers.contentTypeHeader: ['application/json; charset=utf-8'],
  };

  /// Lo stato HTTP.
  final int stato;

  /// Il corpo intero.
  final String corpo;

  /// Il corpo a pezzi (streaming SSE): se c'è, vince su [corpo].
  final List<List<int>>? pezzi;

  /// Le intestazioni.
  final Map<String, List<String>> intestazioni;

  /// Un'attesa prima di ogni pezzo.
  final Duration ritardo;
}

/// Un adattatore HTTP finto per `dio`: risponde secondo il percorso e ricorda le richieste.
class AdattatoreFinto implements HttpClientAdapter {
  /// Con le risposte per `METODO /percorso` (o solo `/percorso`, qualunque metodo).
  AdattatoreFinto(this.risposte);

  /// Le risposte.
  final Map<String, RispostaFinta Function(RequestOptions r)> risposte;

  /// Le richieste ricevute, in ordine.
  final List<RequestOptions> richieste = [];

  /// I corpi delle richieste, già letti.
  final List<String?> corpi = [];

  /// Vero se una richiesta è stata annullata mentre rispondeva.
  bool annullata = false;

  @override
  Future<ResponseBody> fetch(RequestOptions r, Stream<Uint8List>? corpo, Future<void>? annulla) async {
    richieste.add(r);
    corpi.add(corpo == null ? null : utf8.decode(await corpo.expand((x) => x).toList(), allowMalformed: true));
    final chiave = '${r.method} ${r.uri.path}';
    final f = risposte[chiave] ?? risposte[r.uri.path];
    if (f == null) {
      return ResponseBody.fromString('{"detail":"Not Found"}', 404, headers: RispostaFinta._json);
    }
    final risposta = f(r);
    if (risposta.pezzi != null) {
      final controllore = StreamController<Uint8List>();
      unawaited(
        annulla?.then((_) {
          annullata = true;
          if (!controllore.isClosed) unawaited(controllore.close());
        }),
      );
      unawaited(() async {
        for (final p in risposta.pezzi!) {
          if (risposta.ritardo > Duration.zero) await Future<void>.delayed(risposta.ritardo);
          if (controllore.isClosed) return;
          controllore.add(Uint8List.fromList(p));
        }
        if (!controllore.isClosed) await controllore.close();
      }());
      return ResponseBody(controllore.stream, risposta.stato, headers: risposta.intestazioni);
    }
    return ResponseBody.fromString(risposta.corpo, risposta.stato, headers: risposta.intestazioni);
  }

  @override
  void close({bool force = false}) {}
}

/// Una sessione finta per il client.
class FonteFinta implements FonteToken {
  /// Con un token iniziale e quello che dà il rinnovo.
  FonteFinta({this.attuale, this.nuovo});

  /// Il token attuale.
  String? attuale;

  /// Il token dopo il rinnovo (`null`: il rinnovo fallisce).
  String? nuovo;

  /// Quante volte si è rinnovato.
  int rinnovi = 0;

  @override
  Future<String?> token() async => attuale;

  @override
  Future<String?> rinnova() async {
    rinnovi++;
    attuale = nuovo;
    return nuovo;
  }
}

/// Un Keycloak finto.
class FornitoreFinto implements FornitoreOAuth {
  /// Con le credenziali da dare all'accesso e al rinnovo.
  FornitoreFinto({this.accesso, this.rinnovo, this.errore});

  /// Ciò che dà `entra`.
  Credenziali? accesso;

  /// Ciò che dà `rinnova`.
  Credenziali? rinnovo;

  /// L'errore da sollevare (accesso annullato, refresh scaduto…).
  ErroreAccesso? errore;

  /// Le configurazioni ricevute da `entra` (per controllare il social chiesto).
  final List<ConfigAccesso> entrate = [];

  /// I refresh token ricevuti da `rinnova`.
  final List<String> rinnovati = [];

  /// I refresh token revocati all'uscita.
  final List<String?> revocati = [];

  @override
  Future<Credenziali> entra(ConfigAccesso config, {String? lingua}) async {
    entrate.add(config);
    if (errore != null) throw errore!;
    return accesso!;
  }

  @override
  Future<Credenziali> rinnova(ConfigAccesso config, String refreshToken) async {
    rinnovati.add(refreshToken);
    if (errore != null) throw errore!;
    return rinnovo!;
  }

  @override
  Future<void> esci(ConfigAccesso config, {String? refreshToken, String? idToken}) async {
    revocati.add(refreshToken);
  }
}

/// Una cassaforte finta (in memoria).
CassaforteMemoria cassaforteFinta([String? valore]) => CassaforteMemoria(valore);

/// Un JWT finto (non firmato) con le [rivendicazioni].
String jwtFinto(Map<String, Object?> rivendicazioni) {
  String parte(Object o) => base64Url.encode(utf8.encode(jsonEncode(o))).replaceAll('=', '');
  return '${parte({'alg': 'none'})}.${parte(rivendicazioni)}.firma';
}
