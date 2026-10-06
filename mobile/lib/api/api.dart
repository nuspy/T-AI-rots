/// Le chiamate all'API che l'app usa, con i modelli tipizzati (`lib/modelli/`). Le stesse di `frontend/lib/api.ts`
/// e `frontend/lib/privacy.ts`, con gli stessi percorsi.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;
import 'dart:typed_data';
import 'dart:ui' show PlatformDispatcher;

import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/sessione.dart';
import '../config.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../modelli/blog.dart';
import '../modelli/carta.dart';
import '../modelli/cassa.dart';
import '../modelli/notifiche.dart';
import '../modelli/privacy.dart';
import '../modelli/pubblici.dart';
import '../modelli/store.dart';
import '../modelli/voto.dart';
import 'client.dart';
import 'errori.dart';
import 'sse.dart';

/// Il codice per spostare l'accesso dell'app sull'account del sito.
typedef CodiceCollegamento = ({String codice, String? scadeIl, int validitaMinuti, List<String> provider});

/// Una scelta di consenso: tipo (`statistiche`, `google_analytics`…) e valore (`accettato`, `rifiutato`).
typedef SceltaConsenso = ({String tipo, String valore});

/// L'API.
class Api {
  /// Su un client già configurato ([creaDio]).
  Api(this._dio);

  final Dio _dio;

  /// Il client sottostante (per i test).
  Dio get dio => _dio;

  ErroreApi _errore(DioException e) {
    final r = e.response;
    if (r == null) return const ErroreApi(0);
    Object? corpo = r.data;
    if (corpo is String) {
      try {
        corpo = jsonDecode(corpo);
      } on FormatException {
        corpo = null;
      }
    }
    return ErroreApi.daCorpo(r.statusCode ?? 0, corpo);
  }

  Future<T> _chiama<T>(
    String metodo,
    String percorso,
    T Function(Object? dati) leggi, {
    Map<String, Object?>? query,
    Object? corpo,
    bool pubblica = false,
  }) async {
    try {
      final r = await _dio.request<Object?>(
        percorso,
        data: corpo,
        queryParameters: query,
        options: Options(method: metodo, extra: {if (pubblica) Extra.senzaToken: true}),
      );
      return leggi(r.data);
    } on DioException catch (e) {
      throw _errore(e);
    }
  }

  static Map<String, Object?> _mappa(Object? d) => (d ?? const <String, Object?>{}) as Map<String, Object?>;
  static List<Map<String, Object?>> _elenco(Object? d) => (d! as List<Object?>).cast<Map<String, Object?>>();

  /* ---- pubblico ---- */

  /// `GET /cards?lang=`: le 78 carte.
  Future<List<Carta>> carte(String lingua) => _chiama(
    'GET',
    '/cards',
    (d) => _elenco(d).map(Carta.fromJson).toList(),
    query: {'lang': linguaContenuti(lingua)},
    pubblica: true,
  );

  /// `GET /cards/{id}?lang=`: la scheda completa di una carta (per id o slug).
  Future<Carta> carta(String id, String lingua) => _chiama(
    'GET',
    '/cards/${Uri.encodeComponent(id)}',
    (d) => Carta.fromJson(_mappa(d)),
    query: {'lang': linguaContenuti(lingua)},
    pubblica: true,
  );

  /// `GET /spreads?lang=`: le stese, eventualmente di una categoria.
  Future<List<Stesa>> stese(String lingua, {String? categoria}) => _chiama(
    'GET',
    '/spreads',
    (d) => _elenco(d).map(Stesa.fromJson).toList(),
    query: {'lang': linguaContenuti(lingua), 'categoria': ?categoria},
    pubblica: true,
  );

  /// `GET /spreads/{id}?lang=`.
  Future<Stesa> stesa(String id, String lingua) => _chiama(
    'GET',
    '/spreads/${Uri.encodeComponent(id)}',
    (d) => Stesa.fromJson(_mappa(d)),
    query: {'lang': linguaContenuti(lingua)},
    pubblica: true,
  );

  /// `GET /daily-card/today?lang=`: la carta di oggi per tutti.
  Future<CartaOggi> cartaDiOggi(String lingua) => _chiama(
    'GET',
    '/daily-card/today',
    (d) => CartaOggi.fromJson(_mappa(d)),
    query: {'lang': linguaContenuti(lingua)},
    pubblica: true,
  );

  /// `GET /impostazioni-pubbliche`.
  Future<ImpostazioniPubbliche> impostazioniPubbliche() =>
      _chiama('GET', '/impostazioni-pubbliche', (d) => ImpostazioniPubbliche.fromJson(_mappa(d)), pubblica: true);

  /// `GET /lingua-suggerita`: la lingua del paese dell'IP (null se il paese non dice niente).
  Future<String?> linguaSuggerita() =>
      _chiama('GET', '/lingua-suggerita', (d) => _mappa(d)['lingua'] as String?, pubblica: true);

  /// `GET /eta-minima`: l'età minima per il paese stimato.
  Future<EtaMinima> etaMinima() => _chiama('GET', '/eta-minima', (d) => EtaMinima.fromJson(_mappa(d)));

  /// `GET /blog/nove`: i nove articoli di una pagina (contesto: `carta`, `stesa`, `sezione`, `articolo`, `tag`).
  Future<Nove> nove({Map<String, String> contesto = const {}}) =>
      _chiama('GET', '/blog/nove', (d) => Nove.fromJson(_mappa(d)), query: contesto, pubblica: true);

  /// `GET /decks?lang=`: lo slug del mazzo predefinito (o del primo).
  Future<String?> slugMazzoPredefinito(String lingua) => _chiama(
    'GET',
    '/decks',
    (d) {
      final mazzi = _elenco(d);
      if (mazzi.isEmpty) return null;
      final scelto = mazzi.firstWhere((m) => m['predefinito'] == true, orElse: () => mazzi.first);
      return scelto['slug'] as String?;
    },
    query: {'lang': lingua},
    pubblica: true,
  );

  /* ---- account ---- */

  /// `GET /me/daily-card`: la carta personale di oggi, sul giorno **locale** del [fuso] del telefono (che il server
  /// salva), come `cartaDelGiornoLocale` del sito.
  Future<CartaDelGiorno> cartaDelGiorno({String? fuso}) => _chiama(
    'GET',
    '/me/daily-card',
    (d) => CartaDelGiorno.fromJson(_mappa(d)),
    query: fuso == null ? null : {'fuso': fuso},
  );

  /// `GET /me/profile`.
  Future<Profilo> profilo() => _chiama('GET', '/me/profile', (d) => Profilo.fromJson(_mappa(d)));

  /// `GET /me/readings`.
  Future<ElencoLetture> letture() => _chiama('GET', '/me/readings', (d) => ElencoLetture.fromJson(_mappa(d)));

  /// `GET /me/readings/{id}`.
  Future<Lettura> lettura(String id) =>
      _chiama('GET', '/me/readings/${Uri.encodeComponent(id)}', (d) => Lettura.fromJson(_mappa(d)));

  /// `GET /me/billing`: il saldo dei crediti (per la testata).
  Future<int?> saldo() => _chiama('GET', '/me/billing', (d) {
    final s = _mappa(d)['saldo'];
    return s is num ? s.toInt() : null;
  });

  /* ---- Fase 8: le schermate ---------------------------------------------------------------------------------- */

  /// Una chiamata che risponde con byte (un PDF, l'archivio dei propri dati), con il nome del file se il server lo dice.
  Future<({Uint8List byte, String? nome})> _byte(String percorso, {Map<String, Object?>? query}) async {
    try {
      final r = await _dio.get<List<int>>(
        percorso,
        queryParameters: query,
        options: Options(responseType: ResponseType.bytes, headers: {'Accept': '*/*'}),
      );
      final disposizione = r.headers.value('content-disposition') ?? '';
      final nome = RegExp('filename="([^"]+)"').firstMatch(disposizione)?.group(1);
      return (byte: Uint8List.fromList(r.data ?? const []), nome: nome);
    } on DioException catch (e) {
      throw await _erroreByte(e);
    }
  }

  /// Un errore di una risposta a byte: il corpo si rilegge come JSON per avere il motivo.
  Future<ErroreApi> _erroreByte(DioException e) async {
    final r = e.response;
    if (r == null) return const ErroreApi(0);
    Object? corpo;
    final dati = r.data;
    if (dati is List<int>) {
      try {
        corpo = jsonDecode(utf8.decode(dati));
      } on FormatException {
        corpo = null;
      }
    } else {
      corpo = dati;
    }
    return ErroreApi.daCorpo(r.statusCode ?? 0, corpo);
  }

  /// Un'immagine mandata come corpo della richiesta (`PUT`): l'avatar, l'immagine di condivisione.
  Future<Response<T>> _immagine<T>(String percorso, Uint8List byte, String tipo, {ResponseType? risposta}) async {
    try {
      return await _dio.put<T>(
        percorso,
        data: Stream<List<int>>.value(byte),
        options: Options(
          contentType: tipo,
          responseType: risposta,
          headers: {Headers.contentLengthHeader: byte.length},
        ),
      );
    } on DioException catch (e) {
      throw await _erroreByte(e);
    }
  }

  /* -- mazzi, stese, carte: le versioni intere -- */

  /// `GET /decks?lang=`: i mazzi, nella lingua della pagina.
  Future<List<Mazzo>> mazzi(String lingua) =>
      _chiama('GET', '/decks', (d) => _elenco(d).map(Mazzo.fromJson).toList(), query: {'lang': lingua}, pubblica: true);

  /// `GET /decks/{slug}?lang=`.
  Future<Mazzo> mazzo(String slug, String lingua) => _chiama(
    'GET',
    '/decks/${Uri.encodeComponent(slug)}',
    (d) => Mazzo.fromJson(_mappa(d)),
    query: {'lang': lingua},
    pubblica: true,
  );

  /// `GET /me/decks`: gli id dei mazzi che si possono già leggere.
  Future<List<int>> mieiMazzi() => _chiama('GET', '/me/decks', (d) {
    final ids = _mappa(d)['deck_ids'];
    return ids is List ? ids.whereType<num>().map((n) => n.toInt()).toList() : <int>[];
  });

  /// `GET /disclaimer?lang=`: l'avvertenza nella lingua.
  Future<String> disclaimer(String lingua) =>
      _chiama('GET', '/disclaimer', (d) => '${_mappa(d)['testo'] ?? ''}', query: {'lang': lingua}, pubblica: true);

  /* -- il rito -- */

  /// `POST /readings`: apre una lettura (con account).
  Future<Apertura> apriLettura({
    required String spreadId,
    required String domanda,
    required String lingua,
    Map<String, Object?>? partner,
    bool ricordaPartner = false,
    List<({int posizione, String cardId})>? carteManuali,
    String? mazzo,
    String? oltreLimite,
    String variante = 'classica',
  }) => _chiama(
    'POST',
    '/readings',
    (d) => Apertura.fromJson(_mappa(d)),
    corpo: {
      'spread_id': spreadId,
      'question': domanda,
      'lang': lingua,
      if (partner != null) ...{'partner': partner, 'ricorda_partner': ricordaPartner},
      if (carteManuali != null)
        'manual_cards': [
          for (final c in carteManuali) {'posizione': c.posizione, 'card_id': c.cardId},
        ],
      'deck_id': ?mazzo,
      'oltre_limite': ?oltreLimite,
      // v9.5: da dove nasce e con quale versione (prova 90/10), per confrontare gli abbandoni.
      'variante': variante,
      'piattaforma': _piattaforma,
    },
  );

  /// v9.5: la piattaforma dell'app, come nelle statistiche (`android` o `ios`).
  static String get _piattaforma => Platform.isIOS ? 'ios' : 'android';

  /// `POST /readings/anonime`: la lettura gratuita senza account (il cookie `tarots_anon` la ricorda); [etaAnni] è
  /// l'età minima confermata («ho almeno N anni»), senza la quale il server risponde 403 `eta_da_confermare`.
  Future<Apertura> apriLetturaAnonima({
    required String spreadId,
    required String domanda,
    required String lingua,
    int? etaAnni,
    String variante = 'classica',
  }) => _chiama(
    'POST',
    '/readings/anonime',
    (d) => Apertura.fromJson(_mappa(d)),
    corpo: {
      'spread_id': spreadId,
      'question': domanda,
      'lang': lingua,
      if (etaAnni != null) ...{'eta_confermata': true, 'eta_anni': etaAnni},
      'variante': variante,
      'piattaforma': _piattaforma,
    },
  );

  /// `POST /readings/{id}/interview`: una risposta, l'inizio (risposta assente) o «basta così» ([basta]).
  ///
  /// v9.5: dopo una risposta il server non fa subito un'altra domanda (`continua: false`) e risponde `scelta`; [altra]
  /// chiede un'altra domanda anche oltre il minimo («Voglio rispondere a un'altra domanda»).
  Future<PassoIntervista> rispondi(String id, String? risposta, {bool basta = false, bool altra = false}) => _chiama(
    'POST',
    '/readings/${Uri.encodeComponent(id)}/interview',
    (d) => PassoIntervista.fromJson(_mappa(d)),
    corpo: basta
        ? {'basta': true}
        : {
            if (risposta != null && risposta.isNotEmpty) 'risposta': risposta,
            'continua': false,
            if (altra) 'altra': true,
          },
  );

  /// `POST /readings/{id}/addition` (v9.5): «Voglio dire qualcosa di libero». Il testo entra nell'interpretazione;
  /// `crisi` e `messaggio` come nell'intervista.
  Future<({bool crisi, String? messaggio})> aggiungiAllIntervista(String id, String testo) =>
      _chiama('POST', '/readings/${Uri.encodeComponent(id)}/addition', (d) {
        final m = _mappa(d);
        return (crisi: m['crisi'] == true, messaggio: m['messaggio'] as String?);
      }, corpo: {'testo': testo});

  /// `POST /readings/{id}/fan`: mescola e taglia (il [taglio] è dove si è toccato il mazzo, da 0 a 1).
  Future<Ventaglio> apriVentaglio(String id, {double? taglio}) => _chiama(
    'POST',
    '/readings/${Uri.encodeComponent(id)}/fan',
    (d) => Ventaglio.fromJson(_mappa(d)),
    corpo: taglio == null ? null : {'taglio': taglio},
  );

  /// `POST /readings/{id}/pick`: sceglie la carta del posto [slot] del ventaglio.
  Future<Scelta> scegliCarta(String id, int slot) => _chiama(
    'POST',
    '/readings/${Uri.encodeComponent(id)}/pick',
    (d) => Scelta.fromJson(_mappa(d)),
    corpo: {'slot': slot},
  );

  /// `DELETE /me/readings/{id}`.
  Future<void> cancellaLettura(String id) => _chiama('DELETE', '/me/readings/${Uri.encodeComponent(id)}', (_) {});

  /// `POST /me/readings/{id}/feedback`: com'è andata (`si`, `in_parte`, `no`) e una nota.
  Future<String?> annotaLettura(String id, String esito, {String? nota}) => _chiama(
    'POST',
    '/me/readings/${Uri.encodeComponent(id)}/feedback',
    (d) => _mappa(d)['feedback'] as String?,
    corpo: {'esito': esito, 'nota': ?nota},
  );

  /// `POST /me/readings/{id}/share`: accende o spegne il collegamento pubblico; [testo] assente lascia quello scritto.
  Future<StatoCondivisione> condividiLettura(String id, {required bool attiva, String? testo}) => _chiama(
    'POST',
    '/me/readings/${Uri.encodeComponent(id)}/share',
    (d) => StatoCondivisione.fromJson(_mappa(d)),
    corpo: {'attiva': attiva, 'testo': ?testo},
  );

  /// `PUT /me/readings/{id}/share-image`: l'immagine composta dall'app (PNG 800×600); il server la riscrive in WebP
  /// 400×300 e la restituisce.
  Future<Uint8List> caricaImmagineCondivisione(String id, Uint8List png) async {
    final r = await _immagine<List<int>>(
      '/me/readings/${Uri.encodeComponent(id)}/share-image',
      png,
      'image/png',
      risposta: ResponseType.bytes,
    );
    return Uint8List.fromList(r.data ?? const []);
  }

  /// `POST /me/readings/{id}/share-click`: un pulsante di condivisione usato, con l'identificativo di chi condivide.
  Future<Condivisioni?> registraClicCondivisione(String id, String canale, String visitatore) =>
      _chiama('POST', '/me/readings/${Uri.encodeComponent(id)}/share-click', (d) {
        final c = _mappa(d)['contatore'];
        return c is Map<String, Object?> ? Condivisioni.fromJson(c) : null;
      }, corpo: {'canale': canale, 'visitor': visitatore});

  /// `GET /shared/{token}`: una lettura condivisa.
  Future<LetturaCondivisa> letturaCondivisa(String token) => _chiama(
    'GET',
    '/shared/${Uri.encodeComponent(token)}',
    (d) => LetturaCondivisa.fromJson(_mappa(d)),
    pubblica: true,
  );

  /// `POST /shared/{token}/visit`: chi ha aperto il collegamento (dopo qualche secondo). Non solleva mai.
  Future<void> registraVisita(String token, String visitatore) async {
    try {
      await _chiama('POST', '/shared/${Uri.encodeComponent(token)}/visit', (_) {}, corpo: {'visitor': visitatore});
    } on ErroreApi {
      // una visita non contata non disturba chi legge
    }
  }

  /// `POST /me/share-signup`: chi si è iscritto arrivando da un collegamento condiviso.
  Future<bool> attribuisciIscrizione(String token, String visitatore) => _chiama(
    'POST',
    '/me/share-signup',
    (d) => _mappa(d)['attribuita'] == true,
    corpo: {'token': token, 'visitor': visitatore},
  );

  /// L'indirizzo dell'immagine di una lettura condivisa.
  static String urlImmagineCondivisa(String token) =>
      '${Config.apiUrl}/shared/${Uri.encodeComponent(token)}/image.webp';

  /* -- cassa -- */

  /// `GET /plans?lang=`: abbonamenti e pacchetti.
  Future<List<Piano>> piani(String lingua) =>
      _chiama('GET', '/plans', (d) => _elenco(d).map(Piano.fromJson).toList(), query: {'lang': lingua}, pubblica: true);

  /// `GET /me/billing?lang=`: il conto.
  Future<Conto> conto(String lingua) =>
      _chiama('GET', '/me/billing', (d) => Conto.fromJson(_mappa(d)), query: {'lang': lingua});

  /// `GET /me/credits`: i movimenti dei crediti.
  Future<Movimenti> movimenti() => _chiama('GET', '/me/credits', (d) => Movimenti.fromJson(_mappa(d)));

  /// `POST /me/checkout`: il pagamento di un pacchetto o di un abbonamento ([rinnovo]: col rinnovo automatico).
  Future<Checkout> apriPagamento(
    String piano, {
    bool annuale = false,
    bool? rinnovo,
    String? ritorno,
    String? coupon,
  }) => _chiama(
    'POST',
    '/me/checkout',
    (d) => Checkout.fromJson(_mappa(d)),
    corpo: {'piano': piano, 'annuale': annuale, 'rinnovo': ?rinnovo, 'ritorno': ?ritorno, 'coupon': ?coupon},
  );

  /// `GET /me/checkout/{id}`: com'è andato un pagamento (la pagina di ritorno lo chiede, non si fida dell'indirizzo).
  Future<StatoCheckout> statoPagamento(String id) =>
      _chiama('GET', '/me/checkout/${Uri.encodeComponent(id)}', (d) => StatoCheckout.fromJson(_mappa(d)));

  /// `POST /me/subscription`: un abbonamento gratuito.
  Future<void> abbonaGratis(String piano) => _chiama('POST', '/me/subscription', (_) {}, corpo: {'piano': piano});

  /// `POST /me/coupon/riscatta`: un codice regalo, i crediti arrivano subito.
  Future<Riscatto> riscattaCodice(String codice) =>
      _chiama('POST', '/me/coupon/riscatta', (d) => Riscatto.fromJson(_mappa(d)), corpo: {'codice': codice});

  /// `POST /coupon/anteprima`: un codice sconto su tutte le offerte (anche senza account).
  Future<AnteprimaCouponPubblica> anteprimaCoupon(String codice) => _chiama(
    'POST',
    '/coupon/anteprima',
    (d) => AnteprimaCouponPubblica.fromJson(_mappa(d)),
    corpo: {'codice': codice},
  );

  /// `GET /abbonamenti/pubblico`: il banner e i numeri della prova.
  Future<ImpostazioniAbbonamenti> impostazioniAbbonamenti() =>
      _chiama('GET', '/abbonamenti/pubblico', (d) => ImpostazioniAbbonamenti.fromJson(_mappa(d)), pubblica: true);

  /// `GET /me/abbonamento?lang=`.
  Future<MioAbbonamento> mioAbbonamento(String lingua) =>
      _chiama('GET', '/me/abbonamento', (d) => MioAbbonamento.fromJson(_mappa(d)), query: {'lang': lingua});

  /// `POST /me/abbonamento/rinnovo`: accende o spegne il rinnovo automatico.
  Future<AbbonamentoDettaglio> impostaRinnovo({required bool attivo, required String lingua}) => _chiama(
    'POST',
    '/me/abbonamento/rinnovo',
    (d) => AbbonamentoDettaglio.fromJson(_mappa(_mappa(d)['abbonamento'])),
    query: {'lang': lingua},
    corpo: {'attivo': attivo},
  );

  /// `POST /me/abbonamento/cambio/anteprima`: le tre righe del conguaglio.
  Future<Conguaglio> anteprimaCambio(
    String piano, {
    required bool annuale,
    required bool rinnovo,
    required String lingua,
  }) => _chiama(
    'POST',
    '/me/abbonamento/cambio/anteprima',
    (d) => Conguaglio.fromJson(_mappa(d)),
    query: {'lang': lingua},
    corpo: {'piano': piano, 'annuale': annuale, 'rinnovo': rinnovo},
  );

  /// `POST /me/abbonamento/cambio`: l'upgrade (da pagare) o il downgrade (alla scadenza).
  Future<EsitoCambio> cambiaPiano(
    String piano, {
    required bool annuale,
    required bool rinnovo,
    required String lingua,
    String? ritorno,
  }) => _chiama(
    'POST',
    '/me/abbonamento/cambio',
    (d) => EsitoCambio.fromJson(_mappa(d)),
    query: {'lang': lingua},
    corpo: {'piano': piano, 'annuale': annuale, 'rinnovo': rinnovo, 'ritorno': ?ritorno},
  );

  /// `DELETE /me/abbonamento/cambio`: annulla il downgrade programmato.
  Future<AbbonamentoDettaglio> annullaCambio(String lingua) => _chiama(
    'DELETE',
    '/me/abbonamento/cambio',
    (d) => AbbonamentoDettaglio.fromJson(_mappa(_mappa(d)['abbonamento'])),
    query: {'lang': lingua},
  );

  /// `GET /me/abbonamento/pagamento`: dove sistemare il pagamento fallito.
  Future<PagamentoDaSistemare> pagamentoDaSistemare() =>
      _chiama('GET', '/me/abbonamento/pagamento', (d) => PagamentoDaSistemare.fromJson(_mappa(d)));

  /// `POST /me/prova`: la prova gratuita (il metodo di pagamento si registra all'inizio).
  Future<Checkout> iniziaProva(String piano, {String? ritorno, String? coupon}) => _chiama(
    'POST',
    '/me/prova',
    (d) => Checkout.fromJson(_mappa(d)),
    corpo: {'piano': piano, 'ritorno': ?ritorno, 'coupon': ?coupon},
  );

  /* -- acquisti negli store (Fase 9) -- */

  /// `GET /billing/store/catalogo`: i prodotti dello store di [piattaforma] (`android`, `ios`), il pulsante Stripe per
  /// il paese dello store e, con un account, il token dell'account da passare allo store.
  Future<CatalogoStore> catalogoStore(String piattaforma, {String? paese, String? lingua}) => _chiama(
    'GET',
    '/billing/store/catalogo',
    (d) => CatalogoStore.fromJson(_mappa(d)),
    query: {'piattaforma': piattaforma, 'paese_store': ?paese, 'lang': ?lingua},
  );

  /// `POST /billing/store/google/verifica`: il server rilegge l'acquisto da Google, accredita e lo conferma.
  Future<EsitoVerificaStore> verificaGoogle(String productId, String purchaseToken, {String? lingua}) => _chiama(
    'POST',
    '/billing/store/google/verifica',
    (d) => EsitoVerificaStore.fromJson(_mappa(d)),
    query: {'lang': ?lingua},
    corpo: {'productId': productId, 'purchaseToken': purchaseToken},
  );

  /// `POST /billing/store/apple/verifica`: la transazione firmata di StoreKit 2 (`jwsRepresentation`).
  Future<EsitoVerificaStore> verificaApple(String transazioneFirmata, {String? lingua}) => _chiama(
    'POST',
    '/billing/store/apple/verifica',
    (d) => EsitoVerificaStore.fromJson(_mappa(d)),
    query: {'lang': ?lingua},
    corpo: {'signedTransaction': transazioneFirmata},
  );

  /* -- negozio -- */

  /// `POST /shop/quote`: il prezzo del carrello secondo il server (anche senza account).
  Future<Preventivo> preventivo(List<({int deckId, String tipo, int quantita})> voci) => _chiama(
    'POST',
    '/shop/quote',
    (d) => Preventivo.fromJson(_mappa(d)),
    corpo: {
      'voci': [
        for (final v in voci) {'deck_id': v.deckId, 'tipo': v.tipo, 'quantita': v.quantita},
      ],
    },
  );

  /// `POST /orders`: l'ordine del carrello (con l'indirizzo, per le scatole).
  Future<Ordine> apriOrdine(
    List<({int deckId, String tipo, int quantita})> voci, {
    String? ritorno,
    String? indirizzoId,
  }) => _chiama(
    'POST',
    '/orders',
    (d) => Ordine.fromJson(_mappa(d)),
    corpo: {
      'voci': [
        for (final v in voci) {'deck_id': v.deckId, 'tipo': v.tipo, 'quantita': v.quantita},
      ],
      'ritorno': ?ritorno,
      'indirizzo_id': ?indirizzoId,
    },
  );

  /// `GET /me/orders`.
  Future<List<Ordine>> ordini() => _chiama('GET', '/me/orders', (d) {
    final o = _mappa(d)['ordini'];
    return o is List ? o.cast<Map<String, Object?>>().map(Ordine.fromJson).toList() : <Ordine>[];
  });

  /// `GET /me/orders/{id}`.
  Future<Ordine> ordine(String id) =>
      _chiama('GET', '/me/orders/${Uri.encodeComponent(id)}', (d) => Ordine.fromJson(_mappa(d)));

  /// `GET /me/orders/{id}/pdf/{deck}`: il PDF «Stampa i tuoi Tarocchi» di un ordine pagato.
  Future<({Uint8List byte, String? nome})> pdfOrdine(String ordineId, int deckId) =>
      _byte('/me/orders/${Uri.encodeComponent(ordineId)}/pdf/$deckId');

  /// L'indirizzo del PDF gratuito di un mazzo (nessun accesso richiesto).
  static String urlPdfGratuito(String slug) => '${Config.apiUrl}/decks/${Uri.encodeComponent(slug)}/pdf';

  /// `GET /me/addresses`.
  Future<List<Indirizzo>> indirizzi() => _chiama('GET', '/me/addresses', (d) {
    final i = _mappa(d)['indirizzi'];
    return i is List ? i.cast<Map<String, Object?>>().map(Indirizzo.fromJson).toList() : <Indirizzo>[];
  });

  /// `POST /me/addresses`.
  Future<Indirizzo> creaIndirizzo(Map<String, Object?> dati) =>
      _chiama('POST', '/me/addresses', (d) => Indirizzo.fromJson(_mappa(d)), corpo: dati);

  /// `PATCH /me/addresses/{id}`.
  Future<Indirizzo> modificaIndirizzo(String id, Map<String, Object?> dati) =>
      _chiama('PATCH', '/me/addresses/${Uri.encodeComponent(id)}', (d) => Indirizzo.fromJson(_mappa(d)), corpo: dati);

  /// `DELETE /me/addresses/{id}`.
  Future<void> eliminaIndirizzo(String id) => _chiama('DELETE', '/me/addresses/${Uri.encodeComponent(id)}', (_) {});

  /* -- profilo -- */

  /// `PATCH /me/profile`: i campi da cambiare (vuoto = cancellato, come il sito).
  Future<Profilo> aggiornaProfilo(Map<String, Object?> dati) =>
      _chiama('PATCH', '/me/profile', (d) => Profilo.fromJson(_mappa(d)), corpo: dati);

  /// `PUT /me/avatar`: l'immagine del profilo (il server la ritaglia e la riscrive in WebP).
  Future<String?> caricaAvatar(Uint8List byte, String tipo) async {
    final r = await _immagine<Object?>('/me/avatar', byte, tipo);
    final d = r.data;
    return d is Map ? d['avatar'] as String? : null;
  }

  /// `DELETE /me/avatar`.
  Future<void> togliAvatar() => _chiama('DELETE', '/me/avatar', (_) {});

  /// `DELETE /me/partner`: dimentica il partner ricordato.
  Future<void> cancellaPartner() => _chiama('DELETE', '/me/partner', (_) {});

  /// `DELETE /me/dati-social`: cancella i dati presi dai social e la posizione.
  Future<void> dimenticaDatiSocial() => _chiama('DELETE', '/me/dati-social', (_) {});

  /// `POST /me/referral`: il codice d'invito di un'altra persona.
  Future<Riscatto> riscattaInvito(String codice) =>
      _chiama('POST', '/me/referral', (d) => Riscatto.fromJson(_mappa(d)), corpo: {'codice': codice});

  /// `GET /me/statistiche`: l'opposizione al legame fra visite e account.
  Future<bool> opposizioneStatistiche() => _chiama('GET', '/me/statistiche', (d) => _mappa(d)['opposizione'] == true);

  /// `PUT /me/statistiche`.
  Future<bool> impostaOpposizioneStatistiche(bool opposizione) =>
      _chiama('PUT', '/me/statistiche', (d) => _mappa(d)['opposizione'] == true, corpo: {'opposizione': opposizione});

  /// `POST /me/collega/codice` (Fase 6): il codice che sposta l'accesso di questo account dell'app sull'account del sito
  /// (lo si scrive nel profilo del sito entro pochi minuti). 409 `nessuna_identita`: niente da spostare.
  Future<CodiceCollegamento> creaCodiceCollegamento() => _chiama('POST', '/me/collega/codice', (d) {
    final m = _mappa(d);
    final p = m['provider'];
    return (
      codice: '${m['codice'] ?? ''}',
      scadeIl: m['scade_il'] as String?,
      validitaMinuti: m['validita_minuti'] is num ? (m['validita_minuti'] as num).toInt() : 10,
      provider: p is List ? p.map((x) => '$x').toList() : (p == null ? const <String>[] : ['$p']),
    );
  });

  /* -- memoria e chat proattiva -- */

  /// `GET /me/memories`.
  Future<List<Memoria>> memorie() => _chiama('GET', '/me/memories', (d) {
    final m = _mappa(d)['memorie'];
    return m is List ? m.cast<Map<String, Object?>>().map(Memoria.fromJson).toList() : <Memoria>[];
  });

  /// `PATCH /me/memories/{id}`.
  Future<Memoria> modificaMemoria(String id, {String? contenuto, String? campoAttinenza}) => _chiama(
    'PATCH',
    '/me/memories/${Uri.encodeComponent(id)}',
    (d) => Memoria.fromJson(_mappa(d)),
    corpo: {'contenuto': ?contenuto, 'campo_attinenza': ?campoAttinenza},
  );

  /// `DELETE /me/memories/{id}`.
  Future<void> eliminaMemoria(String id) => _chiama('DELETE', '/me/memories/${Uri.encodeComponent(id)}', (_) {});

  /// `DELETE /me/memories`: quelle scelte, o tutte.
  Future<void> eliminaMemorie({List<String>? ids, bool tutte = false}) =>
      _chiama('DELETE', '/me/memories', (_) {}, corpo: tutte ? {'tutte': true} : {'ids': ids ?? const <String>[]});

  /// `GET /impostazioni-chat`.
  Future<ImpostazioniChat> impostazioniChat() =>
      _chiama('GET', '/impostazioni-chat', (d) => ImpostazioniChat.fromJson(_mappa(d)));

  /// `GET /chat/proattiva`: lo storico.
  Future<List<TurnoChat>> storicoChat() => _chiama('GET', '/chat/proattiva', (d) {
    final t = _mappa(d)['turni'];
    return t is List ? t.cast<Map<String, Object?>>().map(TurnoChat.fromJson).toList() : <TurnoChat>[];
  });

  /// `POST /chat/proattiva/avvio`: l'oracolo apre da sé (un'inferenza).
  Future<TurnoChat?> avviaChat() => _chiama('POST', '/chat/proattiva/avvio', (d) {
    final t = _mappa(d)['turno'];
    return t is Map<String, Object?> ? TurnoChat.fromJson(t) : null;
  });

  /// `POST /chat/proattiva/messaggio`.
  Future<TurnoChat?> inviaMessaggioChat(String testo) => _chiama('POST', '/chat/proattiva/messaggio', (d) {
    final t = _mappa(d)['turno'];
    return t is Map<String, Object?> ? TurnoChat.fromJson(t) : null;
  }, corpo: {'testo': testo});

  /// `DELETE /chat/proattiva`: cancella tutta la chat.
  Future<void> cancellaChat() => _chiama('DELETE', '/chat/proattiva', (_) {});

  /// `DELETE /chat/proattiva/{id}`: cancella un turno.
  Future<void> cancellaTurnoChat(String id) => _chiama('DELETE', '/chat/proattiva/${Uri.encodeComponent(id)}', (_) {});

  /* -- privacy dell'account (GDPR, Fase 1) -- */

  /// `GET /me/privacy`.
  Future<StatoPrivacy> privacy() => _chiama('GET', '/me/privacy', (d) => StatoPrivacy.fromJson(_mappa(d)));

  /// `GET /privacy/titolare`: i dati del titolare per l'informativa.
  Future<Titolare> titolare() =>
      _chiama('GET', '/privacy/titolare', (d) => Titolare.fromJson(_mappa(d)), pubblica: true);

  /// `GET /me/esportazione`: l'archivio ZIP dei propri dati. Una volta ogni 24 ore: poi 429 con la data
  /// ([ErroreApi.dettaglio] → `prossima_dal`).
  Future<({Uint8List byte, String? nome})> esportazione() => _byte('/me/esportazione');

  /// `GET /me/cancellazione`.
  Future<StatoCancellazione> statoCancellazione() =>
      _chiama('GET', '/me/cancellazione', (d) => StatoCancellazione.fromJson(_mappa(d)));

  /// `POST /me/cancellazione`: chiede la cancellazione dell'account (30 giorni di ripensamento).
  Future<StatoCancellazione> chiediCancellazione() =>
      _chiama('POST', '/me/cancellazione', (d) => StatoCancellazione.fromJson(_mappa(d)), corpo: {'conferma': true});

  /// `POST /me/cancellazione/annulla`.
  Future<StatoCancellazione> annullaCancellazione() =>
      _chiama('POST', '/me/cancellazione/annulla', (d) => StatoCancellazione.fromJson(_mappa(d)));

  /* -- voto -- */

  /// `GET /voto/mazzi`.
  Future<StatoVoto> statoVoto() => _chiama('GET', '/voto/mazzi', (d) => StatoVoto.fromJson(_mappa(d)));

  /// `POST /voto/mazzi/{id}`.
  Future<void> votaMazzo(String candidato) => _chiama('POST', '/voto/mazzi/${Uri.encodeComponent(candidato)}', (_) {});

  /// `GET /voto/home`.
  Future<VotoHome> votoHome() => _chiama('GET', '/voto/home', (d) => VotoHome.fromJson(_mappa(d)), pubblica: true);

  /// `POST /voto/suggerimenti`: un tema per un mazzo futuro.
  Future<void> suggerisciTemaMazzo(String testo) =>
      _chiama('POST', '/voto/suggerimenti', (_) {}, corpo: {'testo': testo});

  /* -- diario -- */

  /// `GET /blog/posts`: una pagina dell'elenco (`pagina`, `sezione`, `tag`, `q`…).
  Future<ElencoArticoli> articoli([Map<String, String> parametri = const {}]) => _chiama(
    'GET',
    '/blog/posts',
    (d) => ElencoArticoli.fromJson(_mappa(d)),
    query: {
      for (final e in parametri.entries)
        if (e.value.isNotEmpty) e.key: e.value,
    },
    pubblica: true,
  );

  /// `GET /blog/posts?carta=…` o `?stesa=…` (v9.4): l'elenco completo, a pagine, degli articoli su una carta o una
  /// stesa ([tipo] `carta` o `stesa`, [id] l'id o lo slug) — prima quelli che l'hanno come soggetto, poi quelli che la
  /// citano. Una carta o una stesa sconosciuta: 404.
  Future<ElencoArticoli> articoliSuPagine(String tipo, String id, {int pagina = 1, int perPagina = 25}) =>
      articoli({tipo: id, 'pagina': '$pagina', 'per_pagina': '$perPagina'});

  /// `GET /blog/posts/{slug}`.
  Future<ArticoloBlog> articolo(String slug) => _chiama(
    'GET',
    '/blog/posts/${Uri.encodeComponent(slug)}',
    (d) => ArticoloBlog.fromJson(_mappa(d)),
    pubblica: true,
  );

  /// `GET /blog/sections`: l'albero delle sezioni.
  Future<List<NodoSezione>> sezioni() =>
      _chiama('GET', '/blog/sections', (d) => _elenco(d).map(NodoSezione.fromJson).toList(), pubblica: true);

  /// `GET /blog/sections/{slug}?lang=`.
  Future<DettaglioSezione> sezione(String slug, String lingua) => _chiama(
    'GET',
    '/blog/sections/${Uri.encodeComponent(slug)}',
    (d) => DettaglioSezione.fromJson(_mappa(d)),
    query: {'lang': linguaContenuti(lingua)},
    pubblica: true,
  );

  /// `GET /blog/tags`.
  Future<List<EtichettaConConteggio>> etichette() =>
      _chiama('GET', '/blog/tags', (d) => _elenco(d).map(EtichettaConConteggio.fromJson).toList(), pubblica: true);

  /// `GET /blog/links/{carta|stesa}/{id}`: gli articoli che parlano di una carta o di una stesa.
  Future<List<ArticoloBreve>> articoliSu(String tipo, String id) => _chiama(
    'GET',
    '/blog/links/$tipo/${Uri.encodeComponent(id)}',
    (d) => _elenco(d).map(ArticoloBreve.fromJson).toList(),
    pubblica: true,
  );

  /* ---- consensi ed età (GDPR, Fase 1) ---- */

  /// `GET /consenso`: le scelte correnti di questa persona (con o senza account).
  Future<Map<String, String?>> consensi() =>
      _chiama('GET', '/consenso', (d) => _mappa(d).map((k, v) => MapEntry(k, v is String ? v : null)));

  /// `POST /consensi`: più scelte insieme, sullo stesso testo informativo, con l'origine (`android`/`ios`).
  Future<Map<String, String?>> registraConsensi(
    List<SceltaConsenso> scelte, {
    required String versione,
    required String origine,
  }) => _chiama(
    'POST',
    '/consensi',
    (d) => _mappa(d).map((k, v) => MapEntry(k, v is String ? v : null)),
    corpo: {
      'scelte': [
        for (final s in scelte) {'tipo': s.tipo, 'valore': s.valore},
      ],
      'versione_informativa': versione,
      'origine': origine,
    },
  );

  /// `POST /me/eta`: «ho almeno N anni», per chi ha un account.
  Future<void> confermaEta(int anni, {required String origine}) =>
      _chiama('POST', '/me/eta', (_) {}, corpo: {'anni': anni, 'origine': origine});

  /// `POST /e/dimentica`: revocato il consenso `statistiche`, il server dimentica l'identificativo.
  Future<void> dimenticaStatistiche(String id) =>
      _chiama('POST', '/e/dimentica', (_) {}, corpo: jsonEncode({'id': id}), pubblica: true);

  /* ---- notifiche (Fase 9, con l'API della Fase 5) ---- */

  /// `POST /me/dispositivi`: il token FCM di questo telefono, con piattaforma, lingua, fuso e versione dell'app.
  Future<void> registraDispositivo({
    required String token,
    required String piattaforma,
    String? lingua,
    String? fuso,
    String? versione,
  }) => _chiama(
    'POST',
    '/me/dispositivi',
    (_) {},
    corpo: {
      'canale': 'fcm',
      'piattaforma': piattaforma,
      'token': token,
      'lingua': ?lingua,
      'fuso_orario': ?fuso,
      'versione_app': ?versione,
    },
  );

  /// `DELETE /me/dispositivi`: questo telefono non riceve più le notifiche di questo account.
  Future<void> togliDispositivo(String token) =>
      _chiama('DELETE', '/me/dispositivi', (_) {}, corpo: {'canale': 'fcm', 'token': token});

  /// `GET /me/preferenze-notifica`.
  Future<PreferenzeNotifica> preferenzeNotifica() =>
      _chiama('GET', '/me/preferenze-notifica', (d) => PreferenzeNotifica.fromJson(_mappa(d)));

  /// `PUT /me/preferenze-notifica`: solo i campi da cambiare.
  Future<PreferenzeNotifica> salvaPreferenzeNotifica(Map<String, Object?> modifiche) =>
      _chiama('PUT', '/me/preferenze-notifica', (d) => PreferenzeNotifica.fromJson(_mappa(d)), corpo: modifiche);

  /// `PUT /me/fuso-orario`: il fuso del telefono (decide il giorno della carta del giorno).
  Future<void> salvaFuso(String fuso) => _chiama('PUT', '/me/fuso-orario', (_) {}, corpo: {'fuso_orario': fuso});

  /// `POST /notifiche/aperta`: la notifica è stata toccata (la firma dell'invio dice che è proprio questa).
  Future<void> notificaAperta(String invio, String firma) =>
      _chiama('POST', '/notifiche/aperta', (_) {}, corpo: {'invio': invio, 'firma': firma}, pubblica: true);

  /* ---- lo streaming della lettura ---- */

  /// `POST /readings/{id}/reveal/{posizione}`: la carta e la sua interpretazione, a pezzi.
  Stream<EventoLettura> rivela(String id, int posizione) =>
      _flusso('/readings/${Uri.encodeComponent(id)}/reveal/$posizione', Flusso.rivelazione);

  /// `POST /readings/{id}/reveal-all`: tutte le carte coperte insieme, interpretate con una chiamata sola. Prima un
  /// `carta` per ognuna, poi `fase` `lettura` e i battiti, poi per ogni carta il testo (`token` con `posizione`) e la
  /// sua `fine`.
  Stream<EventoLettura> rivelaTutte(String id) =>
      _flusso('/readings/${Uri.encodeComponent(id)}/reveal-all', Flusso.rivelazione);

  /// `POST /readings/{id}/synthesis`: il responso, con le fasi e i battiti.
  Stream<EventoLettura> sintesi(String id) => _flusso('/readings/${Uri.encodeComponent(id)}/synthesis', Flusso.sintesi);

  /// Un flusso SSE. Chiudere l'ascolto annulla la richiesta. Nessun riprova automatico.
  Stream<EventoLettura> _flusso(String percorso, Flusso flusso) async* {
    final annulla = CancelToken();
    try {
      final Response<ResponseBody> r;
      try {
        r = await _dio.post<ResponseBody>(
          percorso,
          cancelToken: annulla,
          options: Options(
            responseType: ResponseType.stream,
            headers: {'Accept': 'text/event-stream'},
            validateStatus: (s) => s != null && s < 400,
          ),
        );
      } on DioException catch (e) {
        throw await _erroreFlusso(e);
      }
      await for (final evento in leggiSse(r.data!.stream)) {
        yield tipizza(evento, flusso);
      }
    } finally {
      if (!annulla.isCancelled) annulla.cancel('ascolto chiuso');
    }
  }

  /// Un errore di un flusso: il corpo è uno stream, si legge per avere il motivo.
  Future<ErroreApi> _erroreFlusso(DioException e) async {
    final r = e.response;
    if (r == null) return const ErroreApi(0);
    final dati = r.data;
    Object? corpo;
    if (dati is ResponseBody) {
      try {
        corpo = jsonDecode(await utf8.decoder.bind(dati.stream).join());
      } on FormatException {
        corpo = null;
      }
    }
    return ErroreApi.daCorpo(r.statusCode ?? 0, corpo);
  }
}

/// Il cookie jar: `main.dart` lo sostituisce con quello su disco (`PersistCookieJar`).
final cookieJarProvider = Provider<CookieJar>((ref) => CookieJar());

/// L'agente dell'app.
final agenteProvider = Provider<String>((ref) {
  final vista = PlatformDispatcher.instance.views.firstOrNull;
  final lato = vista == null ? 0.0 : (vista.physicalSize / vista.devicePixelRatio).shortestSide;
  return agenteApp(ios: Platform.isIOS, tablet: lato >= 600, versione: Config.versione);
});

/// Il client HTTP dell'API.
final dioProvider = Provider<Dio>((ref) {
  return creaDio(
    base: Config.apiUrl,
    lingua: () => ref.read(linguaProvider),
    fonte: ref.read(sessioneProvider.notifier),
    cookie: ref.watch(cookieJarProvider),
    agente: ref.watch(agenteProvider),
  );
});

/// L'API.
final apiProvider = Provider<Api>((ref) => Api(ref.watch(dioProvider)));
