/// Lo store del telefono (Fase 9): **Google Play** su Android, **App Store** su iPhone e iPad, attraverso il pacchetto
/// ufficiale `in_app_purchase` (Play Billing; StoreKit 2 su iOS).
///
/// [Negozio] è ciò che il resto dell'app ne vede: disponibilità, paese dello store, prodotti coi prezzi localizzati,
/// acquisto, completamento, ripristino, gestione degli abbonamenti. Parla con lo store attraverso
/// `InAppPurchasePlatform` — l'interfaccia sostituibile del pacchetto: i test le danno uno store finto, l'app quello
/// vero registrato da `InAppPurchase.instance`.
///
/// Le differenze fra i due store stanno nelle due sottoclassi:
/// - [NegozioGoogle]: un abbonamento ha più **base plan** (mensile, annuale, annuale «prova») e offerte (la prova
///   gratuita): il catalogo del sito dice quale (`prodotti_store`: `abbonamento:base_plan`); l'account si passa come
///   `obfuscatedAccountId`; i pacchetti **non** si consumano da soli (`autoConsume: false`): li consuma il server dopo
///   l'accredito, e l'app solo se il server non c'è riuscito; il cambio di abbonamento passa da
///   `ChangeSubscriptionParam` (upgrade col conguaglio di Google, downgrade alla scadenza);
/// - [NegozioApple]: l'account è l'`appAccountToken` di StoreKit 2; Apple gestisce upgrade e downgrade nello stesso
///   gruppo; «Gestisci» apre `showManageSubscriptions` (un canale verso `AppDelegate.swift`) o, se non riesce, la pagina
///   degli abbonamenti dell'App Store.
library;

import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:in_app_purchase_android/billing_client_wrappers.dart';
import 'package:in_app_purchase_android/in_app_purchase_android.dart';
import 'package:in_app_purchase_platform_interface/in_app_purchase_platform_interface.dart';

import '../cassa/pagamento.dart' show apriFuori, schemaApp;
import '../config.dart';
import '../modelli/store.dart';

/// Un prodotto dello store pronto da mostrare e da comprare: il prodotto del catalogo del sito e i dettagli dello
/// store (Google: già quelli del base plan e dell'offerta giusti).
@immutable
class OffertaStore {
  /// Un'offerta.
  const OffertaStore({required this.prodotto, required this.dettagli, required this.prezzo, this.provaGratuita = false});

  /// Il prodotto del catalogo (`GET /billing/store/catalogo`), col suo piano.
  final ProdottoStore prodotto;

  /// I dettagli dello store, da passare all'acquisto.
  final ProductDetails dettagli;

  /// Il prezzo localizzato dello store (`4,99 €`, `$4.99`): per un abbonamento quello ricorrente, dopo la prova.
  final String prezzo;

  /// Lo store offre la prova gratuita su questo prodotto (Google: l'offerta c'è solo per chi ne ha diritto).
  final bool provaGratuita;

  /// Lo slug del piano che accredita.
  String get piano => prodotto.piano.slug;

  /// Vero per un pacchetto di crediti.
  bool get consumabile => prodotto.tipo == 'consumabile';
}

/// Lo store del telefono, visto dall'app.
abstract class Negozio {
  /// Sullo store [iap] (quello vero, o uno finto nei test).
  Negozio(this.iap);

  /// L'interfaccia di `in_app_purchase`.
  final InAppPurchasePlatform iap;

  /// `android` o `ios`, come il catalogo del sito.
  String get piattaforma;

  /// Il nome dello store, come lo vede chi usa l'app.
  String get nome;

  /// Gli acquisti che arrivano dallo store: nuovi, in attesa, ripristinati, annullati, in errore.
  Stream<List<PurchaseDetails>> get aggiornamenti => iap.purchaseStream;

  /// Quanto aspettare lo store prima di dire che non risponde: senza Play Store (un emulatore, un telefono senza i
  /// servizi di Google) il BillingClient può non rispondere mai, e la pagina non deve restare vuota.
  static const Duration pazienza = Duration(seconds: 6);

  /// Se lo store risponde (su un telefono senza Play Store, o senza account, no).
  Future<bool> disponibile() async {
    try {
      return await iap.isAvailable().timeout(pazienza);
    } on Object catch (e) {
      debugPrint('Store non disponibile: $e');
      return false;
    }
  }

  /// Il paese dello store (Google alpha-2, Apple alpha-3): decide il pulsante Stripe e i prezzi.
  Future<String?> paese() async {
    try {
      final c = await iap.countryCode().timeout(pazienza);
      return c.isEmpty ? null : c;
    } on Object catch (e) {
      debugPrint('Paese dello store non letto: $e');
      return null;
    }
  }

  /// I prodotti del catalogo che lo store conosce, coi suoi prezzi. Un prodotto che lo store non ha (non ancora creato
  /// o non attivo) non c'è.
  Future<List<OffertaStore>> offerte(List<ProdottoStore> prodotti) async {
    final id = prodotti.map((p) => p.productId).toSet();
    if (id.isEmpty) return const [];
    final r = await iap.queryProductDetails(id).timeout(pazienza);
    if (r.error != null) debugPrint('Prodotti dello store: ${r.error!.code} ${r.error!.message}');
    if (r.notFoundIDs.isNotEmpty) debugPrint('Prodotti che lo store non conosce: ${r.notFoundIDs.join(', ')}');
    return abbina(prodotti, r.productDetails);
  }

  /// Dal catalogo del sito e dai dettagli dello store, le offerte.
  @visibleForTesting
  List<OffertaStore> abbina(List<ProdottoStore> prodotti, List<ProductDetails> dettagli);

  /// Apre l'acquisto di [offerta] per l'account [token] (`app_account_token` del catalogo). [daSostituire]: Google, il
  /// vecchio abbonamento dello stesso store ([upgrade]: col conguaglio subito, altrimenti alla scadenza). L'esito
  /// arriva da [aggiornamenti]; `false` se lo store non ha nemmeno aperto la finestra.
  Future<bool> compra(OffertaStore offerta, {String? token, PurchaseDetails? daSostituire, bool upgrade = true});

  /// Chiude l'acquisto presso lo store (Apple: `Transaction.finish`; Google: conferma). Solo **dopo** la verifica.
  Future<void> completa(PurchaseDetails acquisto) => iap.completePurchase(acquisto);

  /// Consuma un pacchetto (Google; Apple lo fa con [completa]). Solo dopo l'accredito, se il server non l'ha già fatto.
  Future<void> consuma(PurchaseDetails acquisto) => completa(acquisto);

  /// Ripristina gli acquisti: arrivano da [aggiornamenti] come `restored`.
  Future<void> ripristina() => iap.restorePurchases();

  /// Gli acquisti che lo store ha e che l'app non ha ancora chiuso (Google: non confermati; Apple: li ridà da sé).
  Future<List<PurchaseDetails>> nonCompletati() async => const [];

  /// Gli acquisti posseduti (Google: abbonamenti attivi e pacchetti non consumati; Apple: niente, non serve).
  Future<List<PurchaseDetails>> posseduti() async => const [];

  /// Il dato che il server verifica: Google il purchase token, Apple la transazione firmata (JWS).
  String datoDaVerificare(PurchaseDetails acquisto) => acquisto.verificationData.serverVerificationData;

  /// Apre la gestione degli abbonamenti dello store (disdetta, cambio, pagamento), su [productId] se si sa.
  Future<bool> gestisciAbbonamenti({String? productId});
}

/// Google Play.
class NegozioGoogle extends Negozio {
  /// Su [iap].
  NegozioGoogle(super.iap);

  @override
  String get piattaforma => 'android';

  @override
  String get nome => 'Google Play';

  /// La fase che si ripete di un'offerta (il prezzo dopo la prova): l'ultima.
  static PricingPhaseWrapper? _ricorrente(SubscriptionOfferDetailsWrapper o) => o.pricingPhases.lastOrNull;

  /// Un'offerta con una fase gratuita all'inizio: la prova.
  static bool _conProva(SubscriptionOfferDetailsWrapper o) =>
      o.offerId != null && o.pricingPhases.length > 1 && o.pricingPhases.first.priceAmountMicros == 0;

  static SubscriptionOfferDetailsWrapper? _offerta(GooglePlayProductDetails d) {
    final i = d.subscriptionIndex;
    final elenco = d.productDetails.subscriptionOfferDetails;
    return i == null || elenco == null || i >= elenco.length ? null : elenco[i];
  }

  @override
  List<OffertaStore> abbina(List<ProdottoStore> prodotti, List<ProductDetails> dettagli) {
    final google = dettagli.whereType<GooglePlayProductDetails>().toList();
    final risultato = <OffertaStore>[];
    for (final p in prodotti) {
      final candidati = google.where((d) => d.id == p.productId).toList();
      if (p.tipo == 'consumabile') {
        final d = candidati.where((d) => d.subscriptionIndex == null).firstOrNull;
        if (d != null) risultato.add(OffertaStore(prodotto: p, dettagli: d, prezzo: d.price));
        continue;
      }
      // Le offerte del base plan giusto: per la prova quella con la fase gratuita (Google la dà solo a chi ne ha
      // diritto), altrimenti il base plan senza offerte.
      final delPiano = [
        for (final d in candidati)
          if (_offerta(d) case final o? when p.basePlan == null || o.basePlanId == p.basePlan) (d, o),
      ];
      final scelta = p.prova
          ? (delPiano.where((x) => _conProva(x.$2)).firstOrNull ?? delPiano.where((x) => x.$2.offerId == null).firstOrNull)
          : (delPiano.where((x) => x.$2.offerId == null).firstOrNull ?? delPiano.firstOrNull);
      if (scelta == null) continue;
      final (d, o) = scelta;
      risultato.add(
        OffertaStore(prodotto: p, dettagli: d, prezzo: _ricorrente(o)?.formattedPrice ?? d.price, provaGratuita: _conProva(o)),
      );
    }
    return risultato;
  }

  @override
  Future<bool> compra(OffertaStore offerta, {String? token, PurchaseDetails? daSostituire, bool upgrade = true}) {
    final d = offerta.dettagli;
    final vecchio = daSostituire is GooglePlayPurchaseDetails ? daSostituire : null;
    final parametri = GooglePlayPurchaseParam(
      productDetails: d,
      applicationUserName: token,
      offerToken: d is GooglePlayProductDetails ? d.offerToken : null,
      changeSubscriptionParam: vecchio == null
          ? null
          : ChangeSubscriptionParam(
              oldPurchaseDetails: vecchio,
              // Upgrade: subito, col conguaglio calcolato da Google; downgrade: alla scadenza (Fase 2b).
              replacementMode: upgrade ? ReplacementMode.chargeProratedPrice : ReplacementMode.deferred,
            ),
    );
    // Il pacchetto non si consuma da solo: prima lo accredita il server (che poi lo consuma).
    return offerta.consumabile
        ? iap.buyConsumable(purchaseParam: parametri, autoConsume: false)
        : iap.buyNonConsumable(purchaseParam: parametri);
  }

  InAppPurchaseAndroidPlatformAddition? get _aggiunta {
    final a = InAppPurchasePlatformAddition.instance;
    return a is InAppPurchaseAndroidPlatformAddition ? a : null;
  }

  @override
  Future<void> consuma(PurchaseDetails acquisto) async {
    final r = await _aggiunta?.consumePurchase(acquisto);
    if (r != null && r.responseCode != BillingResponse.ok && r.responseCode != BillingResponse.itemNotOwned) {
      throw InAppPurchaseException(source: 'google_play', code: '${r.responseCode}', message: r.debugMessage);
    }
  }

  @override
  Future<List<PurchaseDetails>> posseduti() async {
    final r = await _aggiunta?.queryPastPurchases().timeout(Negozio.pazienza);
    if (r?.error != null) debugPrint('Acquisti posseduti: ${r!.error!.message}');
    return r?.pastPurchases ?? const [];
  }

  @override
  Future<List<PurchaseDetails>> nonCompletati() async => [
    for (final p in await posseduti())
      if (p.status == PurchaseStatus.purchased && p.pendingCompletePurchase) p,
  ];

  @override
  Future<bool> gestisciAbbonamenti({String? productId}) => apriFuori(urlGestioneGoogle(productId));
}

/// La pagina degli abbonamenti di Google Play, su un abbonamento se si sa quale (il deep link ufficiale).
String urlGestioneGoogle(String? productId) => Uri.https('play.google.com', '/store/account/subscriptions', {
  if (productId != null && productId.isNotEmpty) 'sku': productId,
  'package': schemaApp,
}).toString();

/// La pagina degli abbonamenti dell'App Store (fuori dall'app, se `showManageSubscriptions` non c'è).
const String urlGestioneApple = 'https://apps.apple.com/account/subscriptions';

/// Il canale verso `ios/Runner/AppDelegate.swift` per `AppStore.showManageSubscriptions(in:)` (StoreKit 2): il plugin
/// non lo espone.
const MethodChannel canaleStoreApple = MethodChannel('chat.tarots.app/store');

/// L'App Store (StoreKit 2).
class NegozioApple extends Negozio {
  /// Su [iap].
  NegozioApple(super.iap);

  @override
  String get piattaforma => 'ios';

  @override
  String get nome => 'App Store';

  @override
  List<OffertaStore> abbina(List<ProdottoStore> prodotti, List<ProductDetails> dettagli) => [
    for (final p in prodotti)
      if (dettagli.where((d) => d.id == p.productId).firstOrNull case final d?)
        // La prova (introductory offer) la decide Apple: c'è se il prodotto è quello della prova.
        OffertaStore(prodotto: p, dettagli: d, prezzo: d.price, provaGratuita: p.prova),
  ];

  @override
  Future<bool> compra(OffertaStore offerta, {String? token, PurchaseDetails? daSostituire, bool upgrade = true}) {
    // Su iOS il token dell'account è l'`appAccountToken` (un UUID); upgrade e downgrade nello stesso gruppo li fa Apple.
    final parametri = PurchaseParam(productDetails: offerta.dettagli, applicationUserName: token);
    return offerta.consumabile
        ? iap.buyConsumable(purchaseParam: parametri)
        : iap.buyNonConsumable(purchaseParam: parametri);
  }

  @override
  Future<bool> gestisciAbbonamenti({String? productId}) async {
    try {
      if (await canaleStoreApple.invokeMethod<bool>('gestisciAbbonamenti') ?? false) return true;
    } on Object catch (e) {
      debugPrint('showManageSubscriptions non disponibile: $e');
    }
    return apriFuori(urlGestioneApple);
  }
}

/// Lo store del telefono, o `null` dove non si compra negli store (i test, o una build con
/// `--dart-define=ACQUISTI_STORE=false`, che usa il pagamento web come la Fase 8).
final negozioProvider = Provider<Negozio?>((ref) {
  if (!Config.acquistiStore) return null;
  if (!Platform.isAndroid && !Platform.isIOS) return null;
  // `InAppPurchase.instance` registra l'implementazione della piattaforma (Play Billing o StoreKit 2).
  InAppPurchase.instance;
  final iap = InAppPurchasePlatform.instance;
  return Platform.isIOS ? NegozioApple(iap) : NegozioGoogle(iap);
});
