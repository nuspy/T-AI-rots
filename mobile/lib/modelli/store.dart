/// Gli acquisti negli store (Fase 9): il catalogo per l'app (`GET /billing/store/catalogo`) e l'esito della verifica
/// di un acquisto (`POST /billing/store/google/verifica`, `POST /billing/store/apple/verifica`), come li scrive
/// `backend/tarot_core/api/routers/billing_store.py`.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

import 'cassa.dart';

part 'store.freezed.dart';
part 'store.g.dart';

/// Il piano del sito che un prodotto dello store accredita.
@freezed
abstract class PianoStore with _$PianoStore {
  /// `{slug, nome, descrizione, tipo, crediti, limiti, livello}`.
  const factory PianoStore({
    required String slug,
    required String nome,
    String? descrizione,

    /// `pacchetto` o `abbonamento`.
    required String tipo,
    @Default(0) int crediti,
    @Default(<String, num>{}) Map<String, num> limiti,
    @Default(0) int livello,
  }) = _PianoStore;

  /// Dal JSON dell'API.
  factory PianoStore.fromJson(Map<String, dynamic> json) => _$PianoStoreFromJson(json);
}

/// Un prodotto in vendita nello store, collegato in console (App mobili → Prodotti) a un piano del sito.
@freezed
abstract class ProdottoStore with _$ProdottoStore {
  /// Un prodotto.
  const factory ProdottoStore({
    /// L'ID del prodotto nello store (per Google l'abbonamento, senza il base plan).
    required String productId,

    /// Google: il base plan dell'abbonamento (`mensile`, `annuale`, `prova`); Apple: sempre nullo.
    String? basePlan,

    /// `consumabile` (un pacchetto di crediti) o `abbonamento`.
    required String tipo,
    @Default(false) bool annuale,

    /// L'annuale della prova: metà prezzo, con la prova gratuita dello store.
    @Default(false) bool prova,
    required PianoStore piano,
  }) = _ProdottoStore;

  /// Dal JSON dell'API.
  factory ProdottoStore.fromJson(Map<String, dynamic> json) => _$ProdottoStoreFromJson(json);
}

/// Il pulsante per pagare con carta (Stripe) secondo la politica della console per il paese dello store.
@freezed
abstract class PulsanteStripe with _$PulsanteStripe {
  /// `{modalita, avviso, mostra}`.
  const factory PulsanteStripe({
    @Default('nascosto') String modalita,
    String? avviso,
    @Default(false) bool mostra,
  }) = _PulsanteStripe;

  /// Dal JSON dell'API.
  factory PulsanteStripe.fromJson(Map<String, dynamic> json) => _$PulsanteStripeFromJson(json);
}

/// `GET /billing/store/catalogo?piattaforma=&paese_store=`: i prodotti dello store di questa piattaforma, il pulsante
/// Stripe e, con un account, il token da passare allo store (`obfuscatedAccountId`, `appAccountToken`).
@freezed
abstract class CatalogoStore with _$CatalogoStore {
  /// Il catalogo.
  const factory CatalogoStore({
    required String piattaforma,
    String? paese,
    @Default(<ProdottoStore>[]) List<ProdottoStore> prodotti,
    @Default(PulsanteStripe()) PulsanteStripe stripe,
    String? appAccountToken,
  }) = _CatalogoStore;

  /// Dal JSON dell'API.
  factory CatalogoStore.fromJson(Map<String, dynamic> json) => _$CatalogoStoreFromJson(json);
}

/// La riga dell'acquisto dopo la verifica (`acquisto_json` del backend): quello che serve all'app.
@freezed
abstract class AcquistoRegistrato with _$AcquistoRegistrato {
  /// L'acquisto.
  const factory AcquistoRegistrato({
    required String productId,
    required String tipo,

    /// `in_attesa`, `accreditato`, `rimborsato`, `revocato`, `scaduto`.
    required String stato,

    /// Già confermato allo store dal server (Google: consumato o riconosciuto).
    @Default(false) bool confermato,
    @Default('production') String ambiente,
  }) = _AcquistoRegistrato;

  /// Dal JSON dell'API.
  factory AcquistoRegistrato.fromJson(Map<String, dynamic> json) => _$AcquistoRegistratoFromJson(json);
}

/// L'esito della verifica: l'acquisto, il saldo e l'abbonamento aggiornati.
@freezed
abstract class EsitoVerificaStore with _$EsitoVerificaStore {
  /// L'esito.
  const factory EsitoVerificaStore({
    @Default('') String esito,
    required AcquistoRegistrato acquisto,
    @Default(0) int saldo,
    AbbonamentoDettaglio? abbonamento,
  }) = _EsitoVerificaStore;

  /// Dal JSON dell'API.
  factory EsitoVerificaStore.fromJson(Map<String, dynamic> json) => _$EsitoVerificaStoreFromJson(json);
}
