// Gli acquisti negli store (Fase 9) con lo store finto (`InAppPurchasePlatform` sostituito, `aiuti/store_finto.dart`)
// e l'API finta: la verifica sul server **prima** di chiudere l'acquisto, gli acquisti in attesa, il ripristino, gli
// errori, il token dell'account passato allo store, la scelta del base plan di Google. Nessuno store vero.

import 'dart:convert';

import 'package:cookie_jar/cookie_jar.dart';
import 'package:flutter/widgets.dart' show Locale;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:in_app_purchase_android/billing_client_wrappers.dart';
import 'package:in_app_purchase_android/in_app_purchase_android.dart';
import 'package:in_app_purchase_platform_interface/in_app_purchase_platform_interface.dart';
import 'package:tarots/acquisti/acquisti.dart';
import 'package:tarots/acquisti/negozio.dart';
import 'package:tarots/analytics/firebase.dart';
import 'package:tarots/api/api.dart';
import 'package:tarots/api/client.dart';
import 'package:tarots/api/errori.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/auth/sessione.dart';
import 'package:tarots/l10n/testi.dart';
import 'package:tarots/modelli/store.dart';
import 'package:tarots/notifiche/fuso.dart';
import 'package:tarots/notifiche/push.dart';

import 'aiuti/finti.dart';
import 'aiuti/store_finto.dart';

/// La risposta del server a una verifica: l'acquisto nello [stato] dato, già confermato allo store o no.
Map<String, Object?> verificato(String productId, {String tipo = 'consumabile', String stato = 'accreditato', bool confermato = true}) => {
  'esito': 'pagamento registrato',
  'acquisto': {
    'id': 1,
    'piattaforma': 'android',
    'product_id': productId,
    'tipo': tipo,
    'transazione': 'GPA.1234-5678',
    'stato': stato,
    'ambiente': 'sandbox',
    'confermato': confermato,
  },
  'saldo': 12,
  'abbonamento': null,
};

/// La scena: il catalogo vero catturato dall'API locale, lo store finto, l'API finta con [verifica].
({ProviderContainer c, PiattaformaFinta store, AdattatoreFinto rete, List<String> registro}) scena({
  required RispostaFinta Function() verifica,
  bool apple = false,
  bool autenticata = true,
}) {
  final registro = <String>[];
  final store = PiattaformaFinta(registro: registro);
  final negozio = apple ? NegozioApple(store) : NegozioGoogleFinto(store);
  final rete = AdattatoreFinto({
    '/billing/store/catalogo': (_) => RispostaFinta.fixture(apple ? 'catalogo_store_ios.json' : 'catalogo_store.json'),
    '/me/billing': (_) => RispostaFinta.fixture('conto.json'),
    'POST /billing/store/google/verifica': (_) {
      registro.add('verifica');
      return verifica();
    },
    'POST /billing/store/apple/verifica': (_) {
      registro.add('verifica');
      return verifica();
    },
  });
  final c = ProviderContainer(
    overrides: [
      archivioProvider.overrideWithValue(ArchivioMemoria({'lingua': 'en'})),
      authDisattivataProvider.overrideWithValue(autenticata),
      configAccessoProvider.overrideWithValue(null),
      statisticheGoogleProvider.overrideWithValue(StatisticheGoogleSpente()),
      servizioPushProvider.overrideWithValue(ServizioPushSpento()),
      leggiFusoProvider.overrideWithValue(() async => null),
      negozioProvider.overrideWithValue(negozio),
      dioProvider.overrideWith(
        (ref) => creaDio(
          base: 'http://api.prova',
          lingua: () => 'en',
          fonte: FonteFinta(),
          cookie: CookieJar(),
          agente: 'prova',
          adattatore: rete,
        ),
      ),
    ],
    retry: (_, _) => null,
  );
  addTearDown(c.dispose);
  c.listen(acquistiProvider, (_, _) {});
  return (c: c, store: store, rete: rete, registro: registro);
}

/// Lascia girare i microtask (l'ascolto dello store, la coda degli acquisti).
Future<void> giro(ProviderContainer c) async {
  for (var i = 0; i < 3; i++) {
    await Future<void>.delayed(Duration.zero);
  }
  await c.read(acquistiProvider.notifier).inPari();
}

Map<String, Object?> corpoDi(AdattatoreFinto rete, String percorso) {
  final i = rete.richieste.lastIndexWhere((r) => r.uri.path == percorso);
  return jsonDecode(rete.corpi[i]!) as Map<String, Object?>;
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => Acquisti.attesaRipristino = const Duration(milliseconds: 10));

  group('Google Play', () {
    test('un pacchetto: il token dell\'account va allo store, niente consumo automatico, verifica e poi niente '
        '(il server l\'ha già consumato)', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('crediti_5')));
      s.store.prodotti = [pacchettoGoogle('crediti_5', '€4.99')];
      final offerte = (await s.c.read(offerteStoreProvider.future))!;
      final o = offerte.offerte.singleWhere((o) => o.prodotto.productId == 'crediti_5');
      expect(o.prezzo, '€4.99');
      expect(offerte.catalogo.stripe.mostra, isTrue);

      await s.c.read(acquistiProvider.notifier).compra(o);
      expect(s.store.acquisti.single.applicationUserName, offerte.catalogo.appAccountToken);
      expect(s.store.autoConsumo.single, isFalse, reason: 'il pacchetto lo consuma il server dopo l\'accredito');
      expect(s.c.read(acquistiProvider).inCorso, isTrue);

      s.store.manda([acquistoGoogle('crediti_5', token: 'tok-1')]);
      await giro(s.c);
      expect(corpoDi(s.rete, '/billing/store/google/verifica'), {'productId': 'crediti_5', 'purchaseToken': 'tok-1'});
      expect(s.registro, ['compra:crediti_5', 'verifica']);
      final stato = s.c.read(acquistiProvider);
      expect(stato.esito, EsitoAcquisto.fatto);
      expect(stato.pacchetto, isTrue);
      expect(stato.piano, '5 readings');
    });

    test('se il server non ha potuto confermare, l\'app consuma (pacchetto) o riconosce (abbonamento) DOPO la '
        'verifica', () async {
      var tipo = 'consumabile';
      final s = scena(verifica: () => RispostaFinta.json(verificato('x', tipo: tipo, confermato: false)));
      s.store.manda([acquistoGoogle('crediti_5')]);
      await giro(s.c);
      expect(s.registro, ['verifica', 'consuma:crediti_5']);
      tipo = 'abbonamento';
      s.store.manda([acquistoGoogle('abbonamento_oro', token: 'tok-abb')]);
      await giro(s.c);
      expect(s.registro, ['verifica', 'consuma:crediti_5', 'verifica', 'completa:abbonamento_oro']);
    });

    test('in attesa (PENDING): niente verifica, niente chiusura, un avviso', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('crediti_5')));
      s.store.manda([acquistoGoogle('crediti_5', stato: PurchaseStateWrapper.pending)]);
      await giro(s.c);
      expect(s.registro, isEmpty);
      expect(s.c.read(acquistiProvider).esito, EsitoAcquisto.inAttesa);
      final t = lookupAppLocalizations(const Locale('it'));
      expect(testoEsito(t, EsitoAcquisto.inAttesa, 'Google Play'), contains('Google Play'));
    });

    test('il server lo registra ancora in attesa: non si chiude', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('crediti_5', stato: 'in_attesa', confermato: false)));
      s.store.manda([acquistoGoogle('crediti_5')]);
      await giro(s.c);
      expect(s.registro, ['verifica']);
      expect(s.c.read(acquistiProvider).esito, EsitoAcquisto.inAttesa);
    });

    test('errori chiari, e l\'acquisto non verificato non si chiude', () async {
      final casi = <(RispostaFinta, EsitoAcquisto)>[
        (
          RispostaFinta.json({'detail': {'motivo': 'account_diverso', 'messaggio': 'altro account'}}, stato: 403),
          EsitoAcquisto.errAccount,
        ),
        (
          RispostaFinta.json({'detail': {'motivo': 'prodotto_sconosciuto', 'messaggio': 'non collegato'}}, stato: 422),
          EsitoAcquisto.errRegistrazione,
        ),
        (
          RispostaFinta.json({'detail': {'motivo': 'acquisto_non_trovato', 'messaggio': 'sconosciuto'}}, stato: 404),
          EsitoAcquisto.errNonValido,
        ),
        (
          RispostaFinta.json({'detail': {'motivo': 'store_non_risponde', 'messaggio': 'giù'}}, stato: 503),
          EsitoAcquisto.errRegistrazione,
        ),
      ];
      for (final (risposta, atteso) in casi) {
        final s = scena(verifica: () => risposta);
        s.store.manda([acquistoGoogle('crediti_5')]);
        await giro(s.c);
        expect(s.c.read(acquistiProvider).esito, atteso, reason: risposta.corpo);
        expect(s.registro, ['verifica'], reason: 'nessuna chiusura senza verifica riuscita');
      }
    });

    test('il server non risponde: si riprova (al ritorno in primo piano), poi si chiude', () async {
      var giu = true;
      final s = scena(
        verifica: () => giu
            ? RispostaFinta.json({'detail': {'motivo': 'store_non_risponde', 'messaggio': 'giù'}}, stato: 503)
            : RispostaFinta.json(verificato('abbonamento_oro', tipo: 'abbonamento', confermato: false)),
      );
      s.store.manda([acquistoGoogle('abbonamento_oro')]);
      await giro(s.c);
      expect(s.registro, ['verifica']);
      giu = false;
      await s.c.read(acquistiProvider.notifier).riprova();
      expect(s.registro, ['verifica', 'verifica', 'completa:abbonamento_oro']);
    });

    test('annullato e già posseduto', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('crediti_5')));
      s.store.prodotti = [pacchettoGoogle('crediti_5', '€4.99')];
      final o = (await s.c.read(offerteStoreProvider.future))!.offerte.first;
      await s.c.read(acquistiProvider.notifier).compra(o);
      s.store.manda([acquistoGoogle('crediti_5', status: PurchaseStatus.canceled)]);
      await giro(s.c);
      expect(s.c.read(acquistiProvider).esito, EsitoAcquisto.annullato);
      final errore = acquistoGoogle('crediti_5', status: PurchaseStatus.error)
        ..error = IAPError(source: 'google_play', code: 'purchase_error', message: 'BillingResponse.itemAlreadyOwned');
      s.store.manda([errore]);
      await giro(s.c);
      expect(s.c.read(acquistiProvider).esito, EsitoAcquisto.errPosseduto);
      expect(s.registro.where((r) => r == 'verifica'), isEmpty);
    });

    test('ripristino: ogni acquisto ritrovato passa dal server; senza niente lo dice', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('abbonamento_oro', tipo: 'abbonamento')));
      s.store.daRipristinare = [acquistoGoogle('abbonamento_oro', riconosciuto: true, status: PurchaseStatus.restored)];
      await s.c.read(acquistiProvider.notifier).ripristina();
      expect(s.registro, ['ripristina', 'verifica']);
      expect(s.c.read(acquistiProvider).esito, EsitoAcquisto.ripristinati);
      s.store.daRipristinare = const [];
      await s.c.read(acquistiProvider.notifier).ripristina();
      expect(s.c.read(acquistiProvider).esito, EsitoAcquisto.nienteDaRipristinare);
    });

    test('il base plan giusto: mensile, annuale e la prova con l\'offerta gratuita (prezzo dopo la prova)', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('x')));
      s.store.prodotti = abbonamentoGoogle('abbonamento_oro', [
        offertaGoogle('mensile', [fase('€9.99', 9990000, 'P1M')]),
        offertaGoogle('annuale', [fase('€99.99', 99990000, 'P1Y')]),
        offertaGoogle('prova', [fase('€49.99', 49990000, 'P1Y')]),
        offertaGoogle('prova', [fase('Free', 0, 'P2W', cicli: 1), fase('€49.99', 49990000, 'P1Y')], offerta: 'gratis-14'),
      ]);
      final offerte = (await s.c.read(offerteStoreProvider.future))!.offerte;
      OffertaStore di(String base) => offerte.singleWhere((o) => o.prodotto.basePlan == base);
      expect(di('mensile').prezzo, '€9.99');
      expect(di('annuale').prezzo, '€99.99');
      expect(di('prova').prezzo, '€49.99');
      expect(di('prova').provaGratuita, isTrue);
      expect((di('prova').dettagli as GooglePlayProductDetails).offerToken, 'token-prova-gratis-14');
      expect(di('mensile').provaGratuita, isFalse);
      // Senza l'offerta gratuita (Google non la dà a chi ha già avuto la prova) resta il base plan, senza prova.
      s.store.prodotti = abbonamentoGoogle('abbonamento_oro', [offertaGoogle('prova', [fase('€49.99', 49990000, 'P1Y')])]);
      s.c.invalidate(offerteStoreProvider);
      final senza = (await s.c.read(offerteStoreProvider.future))!.offerte.single;
      expect(senza.provaGratuita, isFalse);

      // L'acquisto passa l'offerta scelta.
      s.store.prodotti = abbonamentoGoogle('abbonamento_oro', [
        offertaGoogle('prova', [fase('Free', 0, 'P2W', cicli: 1), fase('€49.99', 49990000, 'P1Y')], offerta: 'gratis-14'),
      ]);
      s.c.invalidate(offerteStoreProvider);
      final prova = (await s.c.read(offerteStoreProvider.future))!.offerte.single;
      await s.c.read(acquistiProvider.notifier).compra(prova);
      final p = s.store.acquisti.single as GooglePlayPurchaseParam;
      expect(p.offerToken, 'token-prova-gratis-14');
      expect(p.changeSubscriptionParam, isNull);
    });

    test('cambio di abbonamento nello stesso store: il vecchio si sostituisce (upgrade col conguaglio)', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('x')));
      (s.c.read(negozioProvider)! as NegozioGoogleFinto).possedutiFinti = [
        acquistoGoogle('abbonamento_base', riconosciuto: true),
      ];
      s.store.prodotti = abbonamentoGoogle('abbonamento_oro', [offertaGoogle('mensile', [fase('€9.99', 9990000, 'P1M')])]);
      final oro = (await s.c.read(offerteStoreProvider.future))!.offerte.single;
      await s.c.read(acquistiProvider.notifier).compra(oro);
      final p = s.store.acquisti.single as GooglePlayPurchaseParam;
      expect(p.changeSubscriptionParam?.oldPurchaseDetails.productID, 'abbonamento_base');
      expect(p.changeSubscriptionParam?.replacementMode, ReplacementMode.chargeProratedPrice);
    });

    test('«Gestisci» apre Google Play sull\'abbonamento posseduto', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('x')));
      final negozio = s.c.read(negozioProvider)! as NegozioGoogleFinto;
      negozio.possedutiFinti = [acquistoGoogle('abbonamento_oro', riconosciuto: true)];
      await s.c.read(catalogoStoreProvider.future);
      await s.c.read(acquistiProvider.notifier).gestisci();
      expect(negozio.gestioni, ['abbonamento_oro']);
      expect(
        urlGestioneGoogle('abbonamento_oro'),
        'https://play.google.com/store/account/subscriptions?sku=abbonamento_oro&package=chat.tarots.app',
      );
      expect(urlGestioneGoogle(null), 'https://play.google.com/store/account/subscriptions?package=chat.tarots.app');
    });

    test('lo store non risponde: nessuna offerta, la pagina lo dice', () async {
      final s = scena(verifica: () => RispostaFinta.json(verificato('x')));
      s.store.disponibile = false;
      final dati = (await s.c.read(offerteStoreProvider.future))!;
      expect(dati.disponibile, isFalse);
      expect(dati.offerte, isEmpty);
    });
  });

  group('App Store', () {
    test('la transazione firmata va al server, poi si chiude (finish)', () async {
      final s = scena(apple: true, verifica: () => RispostaFinta.json(verificato('chat.tarots.crediti.5', confermato: false)));
      s.store.manda([acquistoApple('chat.tarots.crediti.5', jws: 'jws.della.transazione.firmata')]);
      await giro(s.c);
      expect(corpoDi(s.rete, '/billing/store/apple/verifica'), {'signedTransaction': 'jws.della.transazione.firmata'});
      expect(s.registro, ['verifica', 'completa:chat.tarots.crediti.5']);
    });

    test('il token dell\'account è l\'appAccountToken', () async {
      final s = scena(apple: true, verifica: () => RispostaFinta.json(verificato('x')));
      s.store.prodotti = [ProductDetails(id: 'chat.tarots.oro.anno.prova', title: 'Oro', description: '', price: '49,99 €', rawPrice: 49.99, currencyCode: 'EUR')];
      final catalogo = await s.c.read(catalogoStoreProvider.future);
      final o = (await s.c.read(offerteStoreProvider.future))!.offerte.single;
      expect(o.provaGratuita, isTrue);
      await s.c.read(acquistiProvider.notifier).compra(o);
      expect(s.store.acquisti.single.applicationUserName, catalogo!.appAccountToken);
    });

    test('una verifica rifiutata non chiude la transazione (Apple la ridà)', () async {
      final s = scena(
        apple: true,
        verifica: () => RispostaFinta.json({'detail': {'motivo': 'firma_non_valida', 'messaggio': 'no'}}, stato: 401),
      );
      s.store.manda([acquistoApple('chat.tarots.crediti.5')]);
      await giro(s.c);
      expect(s.registro, ['verifica']);
    });
  });

  test('i motivi del server diventano esiti', () {
    expect(esitoDaErroreApi(const ErroreApi(0)), EsitoAcquisto.errRete);
    expect(esitoDaErroreApi(const ErroreApi(500)), EsitoAcquisto.errRegistrazione);
    expect(esitoDaErroreStore('purchase_error', 'BillingResponse.billingUnavailable'), EsitoAcquisto.nonDisponibile);
    expect(esitoDaErroreStore('purchase_error', 'BillingResponse.userCanceled'), EsitoAcquisto.annullato);
    final t = lookupAppLocalizations(const Locale('en'));
    for (final e in EsitoAcquisto.values) {
      expect(testoEsito(t, e, 'Google Play', piano: 'Gold'), isNotEmpty, reason: '$e');
    }
  });

  test('il catalogo viene dal server con il paese dello store', () async {
    final s = scena(verifica: () => RispostaFinta.json(verificato('x')));
    final CatalogoStore? c = await s.c.read(catalogoStoreProvider.future);
    expect(c!.prodotti.where((p) => p.prova).single.basePlan, 'prova');
    final r = s.rete.richieste.firstWhere((r) => r.uri.path == '/billing/store/catalogo');
    expect(r.uri.queryParameters, containsPair('piattaforma', 'android'));
    expect(r.uri.queryParameters, containsPair('paese_store', 'IT'));
  });
}
