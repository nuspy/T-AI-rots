/// Lo store finto per i test degli acquisti (Fase 9): un'implementazione di `InAppPurchasePlatform` — l'interfaccia
/// sostituibile del pacchetto `in_app_purchase` — che ricorda ciò che l'app le chiede e manda gli acquisti che il test
/// decide. I prodotti e gli acquisti di Google sono quelli veri del plugin (`GooglePlayProductDetails`,
/// `GooglePlayPurchaseDetails`), costruiti dai loro wrapper: si prova anche la scelta del base plan.
library;

import 'dart:async';

import 'package:in_app_purchase_android/billing_client_wrappers.dart';
import 'package:in_app_purchase_android/in_app_purchase_android.dart';
import 'package:in_app_purchase_platform_interface/in_app_purchase_platform_interface.dart';
import 'package:tarots/acquisti/negozio.dart';

/// Lo store finto.
class PiattaformaFinta extends InAppPurchasePlatform {
  /// Con i prodotti che lo store conosce e il [registro] condiviso col test (per l'ordine delle chiamate).
  PiattaformaFinta({this.prodotti = const [], List<String>? registro, this.disponibile = true})
    : registro = registro ?? [];

  /// I prodotti dello store.
  List<ProductDetails> prodotti;

  /// Lo store risponde.
  bool disponibile;

  /// Ciò che è successo, in ordine (`compra:…`, `completa:…`, `ripristina`).
  final List<String> registro;

  /// I parametri degli acquisti aperti.
  final List<PurchaseParam> acquisti = [];

  /// Se l'ultimo acquisto era un consumabile con `autoConsume`.
  final List<bool> autoConsumo = [];

  /// Gli acquisti completati.
  final List<PurchaseDetails> completati = [];

  /// Ciò che il ripristino manda.
  List<PurchaseDetails> daRipristinare = const [];

  final StreamController<List<PurchaseDetails>> _flusso = StreamController<List<PurchaseDetails>>.broadcast();

  /// Lo store manda [acquisti] all'app.
  void manda(List<PurchaseDetails> acquisti) => _flusso.add(acquisti);

  @override
  Stream<List<PurchaseDetails>> get purchaseStream => _flusso.stream;

  @override
  Future<bool> isAvailable() async => disponibile;

  @override
  Future<String> countryCode() async => 'IT';

  @override
  Future<ProductDetailsResponse> queryProductDetails(Set<String> identifiers) async => ProductDetailsResponse(
    productDetails: prodotti.where((p) => identifiers.contains(p.id)).toList(),
    notFoundIDs: identifiers.where((id) => prodotti.every((p) => p.id != id)).toList(),
  );

  @override
  Future<bool> buyNonConsumable({required PurchaseParam purchaseParam}) async {
    registro.add('compra:${purchaseParam.productDetails.id}');
    acquisti.add(purchaseParam);
    return true;
  }

  @override
  Future<bool> buyConsumable({required PurchaseParam purchaseParam, bool autoConsume = true}) async {
    autoConsumo.add(autoConsume);
    return buyNonConsumable(purchaseParam: purchaseParam);
  }

  @override
  Future<void> completePurchase(PurchaseDetails purchase) async {
    registro.add('completa:${purchase.productID}');
    completati.add(purchase);
  }

  @override
  Future<void> restorePurchases({String? applicationUserName}) async {
    registro.add('ripristina');
    if (daRipristinare.isNotEmpty) _flusso.add(daRipristinare);
  }
}

/// Google Play sullo store finto: il consumo e gli acquisti posseduti (che il plugin chiede al BillingClient) li tiene
/// il test.
class NegozioGoogleFinto extends NegozioGoogle {
  /// Sullo store finto.
  NegozioGoogleFinto(PiattaformaFinta super.iap);

  PiattaformaFinta get _finta => iap as PiattaformaFinta;

  /// Gli acquisti posseduti (abbonamenti attivi, pacchetti non consumati).
  List<PurchaseDetails> possedutiFinti = const [];

  /// Le gestioni degli abbonamenti aperte (con il productId).
  final List<String?> gestioni = [];

  @override
  Future<void> consuma(PurchaseDetails acquisto) async => _finta.registro.add('consuma:${acquisto.productID}');

  @override
  Future<List<PurchaseDetails>> posseduti() async => possedutiFinti;

  @override
  Future<bool> gestisciAbbonamenti({String? productId}) async {
    gestioni.add(productId);
    return true;
  }
}

/// Un pacchetto di crediti di Google Play.
GooglePlayProductDetails pacchettoGoogle(String id, String prezzo, {int micros = 4990000}) =>
    GooglePlayProductDetails.fromProductDetails(
      ProductDetailsWrapper(
        description: '',
        name: id,
        productId: id,
        productType: ProductType.inapp,
        title: id,
        oneTimePurchaseOfferDetails: OneTimePurchaseOfferDetailsWrapper(
          formattedPrice: prezzo,
          priceAmountMicros: micros,
          priceCurrencyCode: 'EUR',
        ),
      ),
    ).single;

/// Una fase di prezzo di un'offerta di Google.
PricingPhaseWrapper fase(String prezzo, int micros, String periodo, {int cicli = 0}) => PricingPhaseWrapper(
  billingCycleCount: cicli,
  billingPeriod: periodo,
  formattedPrice: prezzo,
  priceAmountMicros: micros,
  priceCurrencyCode: 'EUR',
  recurrenceMode: cicli == 0 ? RecurrenceMode.infiniteRecurring : RecurrenceMode.finiteRecurring,
);

/// Un abbonamento di Google Play con le sue offerte (una per base plan, e le offerte della prova).
List<GooglePlayProductDetails> abbonamentoGoogle(String id, List<SubscriptionOfferDetailsWrapper> offerte) =>
    GooglePlayProductDetails.fromProductDetails(
      ProductDetailsWrapper(
        description: '',
        name: id,
        productId: id,
        productType: ProductType.subs,
        title: id,
        subscriptionOfferDetails: offerte,
      ),
    );

/// Un'offerta di un abbonamento di Google ([offerta] nulla: il base plan da solo).
SubscriptionOfferDetailsWrapper offertaGoogle(String basePlan, List<PricingPhaseWrapper> fasi, {String? offerta}) =>
    SubscriptionOfferDetailsWrapper(
      basePlanId: basePlan,
      offerId: offerta,
      offerTags: const [],
      offerIdToken: 'token-$basePlan-${offerta ?? 'base'}',
      pricingPhases: fasi,
    );

/// Un acquisto di Google Play come lo manda il BillingClient.
GooglePlayPurchaseDetails acquistoGoogle(
  String productId, {
  String token = 'token-acquisto',
  PurchaseStateWrapper stato = PurchaseStateWrapper.purchased,
  bool riconosciuto = false,
  PurchaseStatus? status,
}) {
  final p = GooglePlayPurchaseDetails.fromPurchase(
    PurchaseWrapper(
      orderId: 'GPA.1234-5678',
      packageName: 'chat.tarots.app',
      purchaseTime: 1759574400000,
      purchaseToken: token,
      signature: 'firma',
      products: [productId],
      isAutoRenewing: false,
      originalJson: '{}',
      isAcknowledged: riconosciuto,
      purchaseState: stato,
    ),
  ).single;
  if (status != null) p.status = status;
  return p;
}

/// Un acquisto dell'App Store (StoreKit 2): la transazione firmata nel dato da verificare.
PurchaseDetails acquistoApple(String productId, {String jws = 'eyJhbGciOiJFUzI1NiJ9.transazione.firma'}) =>
    PurchaseDetails(
        purchaseID: '2000000123456789',
        productID: productId,
        verificationData: PurchaseVerificationData(
          localVerificationData: '{}',
          serverVerificationData: jws,
          source: 'app_store',
        ),
        transactionDate: '1759574400000',
        status: PurchaseStatus.purchased,
      )
      ..pendingCompletePurchase = true;
