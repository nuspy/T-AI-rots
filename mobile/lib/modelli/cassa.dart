/// La cassa: piani e pacchetti, il conto, i movimenti dei crediti, i mazzi del negozio, gli ordini e il preventivo del
/// carrello, gli abbonamenti della Fase 2b (rinnovo, conguaglio, prova, limite superato) e i codici sconto (Fase 2d).
///
/// Scritti a mano come `Piano`, `Conto`, `Mazzo`, `Ordine`, `Preventivo` di `frontend/lib/api.ts`, `AbbonamentoDettaglio`,
/// `Conguaglio`, `LimiteSuperato` di `frontend/lib/abbonamenti.ts`, `CouponPubblico` e `VoceCoupon` di
/// `frontend/v2/lib/coupon.ts`. Gli importi sono in centesimi, come nell'API.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'cassa.freezed.dart';
part 'cassa.g.dart';

/* ---- piani e conto ---------------------------------------------------------------------------------------------- */

/// Un prezzo con e senza rinnovo automatico (Fase 2b).
@freezed
abstract class PrezzoRinnovo with _$PrezzoRinnovo {
  /// `{listino, con_rinnovo, sconto}`.
  const factory PrezzoRinnovo({required int listino, required int conRinnovo, @Default(0) num sconto}) =
      _PrezzoRinnovo;

  /// Dal JSON dell'API.
  factory PrezzoRinnovo.fromJson(Map<String, dynamic> json) => _$PrezzoRinnovoFromJson(json);
}

/// I prezzi di un abbonamento: mensile, annuale (se c'è) e l'annuale della prova.
@freezed
abstract class PrezziPiano with _$PrezziPiano {
  /// I prezzi.
  const factory PrezziPiano({required PrezzoRinnovo mensile, PrezzoRinnovo? annuale, int? provaAnnuale}) =
      _PrezziPiano;

  /// Dal JSON dell'API.
  factory PrezziPiano.fromJson(Map<String, dynamic> json) => _$PrezziPianoFromJson(json);
}

/// `GET /plans`: un abbonamento o un pacchetto di crediti.
@freezed
abstract class Piano with _$Piano {
  /// Un piano.
  const factory Piano({
    required String slug,
    required String nome,

    /// `abbonamento` o `pacchetto`.
    required String tipo,
    String? descrizione,
    @Default('EUR') String valuta,
    @Default(0) int prezzoMensile,
    @Default(0) int prezzoAnnuale,
    @Default(0) int creditiPerPeriodo,
    @Default(<String, num>{}) Map<String, num> limiti,
    int? livello,
    PrezziPiano? prezzi,
  }) = _Piano;

  const Piano._();

  /// Dal JSON dell'API.
  factory Piano.fromJson(Map<String, dynamic> json) => _$PianoFromJson(json);

  /// Un pacchetto di crediti (una tantum).
  bool get pacchetto => tipo == 'pacchetto';
}

/// L'abbonamento in breve, nel conto.
@freezed
abstract class AbbonamentoBreve with _$AbbonamentoBreve {
  /// L'abbonamento.
  const factory AbbonamentoBreve({
    required String id,
    required String piano,
    required String nome,
    required String stato,
    required String periodoInizio,
    required String periodoFine,
    String? disdettoIl,
    bool? annuale,
    bool? rinnovoAutomatico,

    /// Fase 9: chi incassa (`stripe`, `google_play`, `app_store`…) e se è un abbonamento di uno store.
    String? provider,
    @Default(false) bool store,
  }) = _AbbonamentoBreve;

  /// Dal JSON dell'API.
  factory AbbonamentoBreve.fromJson(Map<String, dynamic> json) => _$AbbonamentoBreveFromJson(json);
}

/// I diritti del piano corrente.
@freezed
abstract class Diritti with _$Diritti {
  /// I diritti.
  const factory Diritti({
    required String piano,
    required String nome,
    @Default(<String, num>{}) Map<String, num> limiti,
    @Default(false) bool predefiniti,
  }) = _Diritti;

  /// Dal JSON dell'API.
  factory Diritti.fromJson(Map<String, dynamic> json) => _$DirittiFromJson(json);
}

/// L'uso di un limite: usati, limite, restanti.
@freezed
abstract class UsoLimite with _$UsoLimite {
  /// L'uso.
  const factory UsoLimite({@Default(0) int usati, int? limite, int? restanti}) = _UsoLimite;

  /// Dal JSON dell'API.
  factory UsoLimite.fromJson(Map<String, dynamic> json) => _$UsoLimiteFromJson(json);
}

/// Se la prova gratuita è ancora possibile.
@freezed
abstract class IdoneitaProva with _$IdoneitaProva {
  /// `{idonea, motivo, usata_il}`.
  const factory IdoneitaProva({required bool idonea, String? motivo, String? usataIl}) = _IdoneitaProva;

  /// Dal JSON dell'API.
  factory IdoneitaProva.fromJson(Map<String, dynamic> json) => _$IdoneitaProvaFromJson(json);
}

/// `GET /me/billing`: il conto.
@freezed
abstract class Conto with _$Conto {
  /// Il conto.
  const factory Conto({
    AbbonamentoBreve? abbonamento,
    Diritti? diritti,
    @Default(0) int saldo,
    @Default(<String, UsoLimite>{}) Map<String, UsoLimite> uso,
    @Default(false) bool limitiAttivi,
    bool? lettureComprese,
    IdoneitaProva? prova,
  }) = _Conto;

  /// Dal JSON dell'API.
  factory Conto.fromJson(Map<String, dynamic> json) => _$ContoFromJson(json);
}

/// Un movimento dei crediti (`GET /me/credits`).
@freezed
abstract class Movimento with _$Movimento {
  /// Un movimento.
  const factory Movimento({
    required int delta,
    required String reason,
    required String quando,
    String? note,
    String? readingId,
  }) = _Movimento;

  /// Dal JSON dell'API.
  factory Movimento.fromJson(Map<String, dynamic> json) => _$MovimentoFromJson(json);
}

/// `GET /me/credits`.
@freezed
abstract class Movimenti with _$Movimenti {
  /// Il saldo e i movimenti.
  const factory Movimenti({@Default(0) int saldo, @Default(<Movimento>[]) List<Movimento> movimenti}) = _Movimenti;

  /// Dal JSON dell'API.
  factory Movimenti.fromJson(Map<String, dynamic> json) => _$MovimentiFromJson(json);
}

/// `POST /me/checkout`, `POST /me/prova`: dove pagare.
@freezed
abstract class Checkout with _$Checkout {
  /// Un pagamento aperto.
  const factory Checkout({
    required String checkoutId,
    required String url,
    @Default(0) int importo,
    int? sconto,
    @Default('EUR') String valuta,
    @Default(false) bool gratis,
  }) = _Checkout;

  /// Dal JSON dell'API.
  factory Checkout.fromJson(Map<String, dynamic> json) => _$CheckoutFromJson(json);
}

/// `GET /me/checkout/{id}`: com'è andata.
@freezed
abstract class StatoCheckout with _$StatoCheckout {
  /// Lo stato.
  const factory StatoCheckout({
    required String checkoutId,
    required String stato,
    required String piano,
    required String nome,
    required String tipo,
    bool? prova,
    bool? cambio,
    String? esito,
  }) = _StatoCheckout;

  /// Dal JSON dell'API.
  factory StatoCheckout.fromJson(Map<String, dynamic> json) => _$StatoCheckoutFromJson(json);
}

/* ---- abbonamenti (Fase 2b) ---------------------------------------------------------------------------------------- */

/// Il piano che parte alla prossima scadenza (un downgrade).
@freezed
abstract class PianoSuccessivo with _$PianoSuccessivo {
  /// `{piano, nome, annuale, dal}`.
  const factory PianoSuccessivo({
    required String piano,
    required String nome,
    @Default(false) bool annuale,
    required String dal,
  }) = _PianoSuccessivo;

  /// Dal JSON dell'API.
  factory PianoSuccessivo.fromJson(Map<String, dynamic> json) => _$PianoSuccessivoFromJson(json);
}

/// Il codice sconto che continua sui rinnovi (Fase 2d).
@freezed
abstract class CouponAbbonamento with _$CouponAbbonamento {
  /// Il codice.
  const factory CouponAbbonamento({
    required String codice,
    required String tipo,
    required num valore,
    @Default(false) bool cumulabile,
    @Default(0) num sconto,
    @Default(false) bool perSempre,
    int? rinnoviRimasti,
  }) = _CouponAbbonamento;

  /// Dal JSON dell'API.
  factory CouponAbbonamento.fromJson(Map<String, dynamic> json) => _$CouponAbbonamentoFromJson(json);
}

/// L'abbonamento per intero (`GET /me/abbonamento`).
@freezed
abstract class AbbonamentoDettaglio with _$AbbonamentoDettaglio {
  /// L'abbonamento.
  const factory AbbonamentoDettaglio({
    required String id,
    required String piano,
    required String nome,

    /// `in_prova`, `attivo`, `in_sospeso`, `sospeso`, `disdetto`, `scaduto`.
    required String stato,
    required String provider,
    @Default(false) bool store,
    String? gestioneStore,
    @Default(false) bool gratuito,
    @Default(false) bool annuale,
    @Default(false) bool prova,
    required String periodoInizio,
    required String periodoFine,
    String? disdettoIl,
    @Default(false) bool rinnovoAutomatico,
    int? listino,
    int? importoPeriodo,
    @Default(0) num scontoRicorrente,
    int? prossimoRinnovo,
    @Default('EUR') String valuta,
    @Default(false) bool fatturaAperta,
    String? pagamentoFallitoIl,
    String? fineTolleranza,
    PianoSuccessivo? pianoSuccessivo,
    CouponAbbonamento? coupon,
  }) = _AbbonamentoDettaglio;

  /// Dal JSON dell'API.
  factory AbbonamentoDettaglio.fromJson(Map<String, dynamic> json) => _$AbbonamentoDettaglioFromJson(json);
}

/// `GET /abbonamenti/pubblico`: il banner della prova e i numeri della prova.
@freezed
abstract class ImpostazioniAbbonamenti with _$ImpostazioniAbbonamenti {
  /// Le impostazioni pubbliche.
  const factory ImpostazioniAbbonamenti({
    @Default(false) bool bannerProva,
    @Default(false) bool provaDisponibile,
    @Default(14) int giorniProva,
    @Default(50) num scontoProva,
    @Default(20) num scontoRinnovo,
    @Default(2) int condoniPerPeriodo,
    @Default(2) int giorniPromemoriaProva,
    @Default(7) int giorniTolleranza,
  }) = _ImpostazioniAbbonamenti;

  /// Dal JSON dell'API.
  factory ImpostazioniAbbonamenti.fromJson(Map<String, dynamic> json) => _$ImpostazioniAbbonamentiFromJson(json);
}

/// I numeri dell'abbonamento che il profilo mostra.
@freezed
abstract class NumeriAbbonamento with _$NumeriAbbonamento {
  /// `{sconto_rinnovo, sconto_prova, giorni_prova, giorni_tolleranza}`.
  const factory NumeriAbbonamento({
    @Default(20) num scontoRinnovo,
    @Default(50) num scontoProva,
    @Default(14) int giorniProva,
    @Default(7) int giorniTolleranza,
  }) = _NumeriAbbonamento;

  /// Dal JSON dell'API.
  factory NumeriAbbonamento.fromJson(Map<String, dynamic> json) => _$NumeriAbbonamentoFromJson(json);
}

/// `GET /me/abbonamento`.
@freezed
abstract class MioAbbonamento with _$MioAbbonamento {
  /// Il mio abbonamento.
  const factory MioAbbonamento({
    AbbonamentoDettaglio? abbonamento,
    required IdoneitaProva prova,
    @Default(NumeriAbbonamento()) NumeriAbbonamento impostazioni,
    @Default(0) int saldo,
  }) = _MioAbbonamento;

  /// Dal JSON dell'API.
  factory MioAbbonamento.fromJson(Map<String, dynamic> json) => _$MioAbbonamentoFromJson(json);
}

/// Le tre righe del conguaglio (e il conto di un downgrade).
@freezed
abstract class Conguaglio with _$Conguaglio {
  /// Il conguaglio.
  const factory Conguaglio({
    /// `upgrade` o `downgrade`.
    required String tipo,
    required String piano,
    required String nome,
    @Default(false) bool annuale,
    @Default(false) bool rinnovo,
    @Default(0) int listino,
    @Default(0) num scontoRinnovo,
    @Default(0) int nuovo,
    @Default(0) int residuo,
    @Default(0) int totale,
    @Default(0) int pagato,
    @Default(0) int giorniRimasti,
    @Default(0) int giorniPeriodo,
    required String decorre,
    @Default('EUR') String valuta,
  }) = _Conguaglio;

  /// Dal JSON dell'API.
  factory Conguaglio.fromJson(Map<String, dynamic> json) => _$ConguaglioFromJson(json);
}

/// `POST /me/abbonamento/cambio`: l'upgrade da pagare (`url`) o il downgrade programmato.
@freezed
abstract class EsitoCambio with _$EsitoCambio {
  /// L'esito.
  const factory EsitoCambio({
    required String tipo,
    required Conguaglio conguaglio,
    String? url,
    int? importo,
    AbbonamentoDettaglio? abbonamento,
  }) = _EsitoCambio;

  /// Dal JSON dell'API.
  factory EsitoCambio.fromJson(Map<String, dynamic> json) => _$EsitoCambioFromJson(json);
}

/// `GET /me/abbonamento/pagamento`: dove sistemare il pagamento.
@freezed
abstract class PagamentoDaSistemare with _$PagamentoDaSistemare {
  /// `{provider, store, url, gia_pagata}`.
  const factory PagamentoDaSistemare({
    required String provider,
    @Default(false) bool store,
    String? url,
    @Default(false) bool giaPagata,
  }) = _PagamentoDaSistemare;

  /// Dal JSON dell'API.
  factory PagamentoDaSistemare.fromJson(Map<String, dynamic> json) => _$PagamentoDaSistemareFromJson(json);
}

/// Il corpo dell'errore 402 `limite_superato` di `POST /readings`.
@freezed
abstract class LimiteSuperato with _$LimiteSuperato {
  /// Il limite superato.
  const factory LimiteSuperato({
    /// `letture_al_giorno`, `letture_alla_settimana`, `letture_al_mese`, `letture_totali`.
    required String limite,
    @Default(0) int valore,
    @Default(0) int usate,
    @Default(0) int lettureFatte,
    String? siLibera,
    @Default(0) int condoniRimasti,
    @Default(0) int condoniPerPeriodo,
    @Default(0) int saldo,

    /// `condono`, `credito`, `acquisto`.
    required String scelta,
  }) = _LimiteSuperato;

  /// Dal JSON dell'API.
  factory LimiteSuperato.fromJson(Map<String, dynamic> json) => _$LimiteSuperatoFromJson(json);
}

/* ---- codici sconto (Fase 2d) --------------------------------------------------------------------------------------- */

/// Il codice sconto in chiaro (`POST /coupon/anteprima`).
@freezed
abstract class CouponPubblico with _$CouponPubblico {
  /// Il codice.
  const factory CouponPubblico({
    required String codice,

    /// `percentuale` o `importo`.
    required String tipo,
    required num valore,

    /// `una_volta`, `periodi`, `sempre`.
    required String durata,
    int? periodi,
    @Default(false) bool cumulabile,
    @Default(<String>[]) List<String> piani,
    String? validoFino,
  }) = _CouponPubblico;

  /// Dal JSON dell'API.
  factory CouponPubblico.fromJson(Map<String, dynamic> json) => _$CouponPubblicoFromJson(json);
}

/// Un'offerta con il coupon: il prezzo, oppure perché il codice non vale lì (`motivo`).
@freezed
abstract class VoceCoupon with _$VoceCoupon {
  /// Una voce.
  const factory VoceCoupon({
    required String piano,
    @Default(false) bool annuale,
    @Default(false) bool rinnovo,
    @Default(false) bool prova,
    String? motivo,
    int? listino,
    num? scontoBase,
    num? scontoCoupon,
    num? sconto,
    int? importo,
    int? risparmio,
    String? vince,
    bool? applicato,
    bool? cumulabile,
    num? scontoRicorrente,
    int? rinnoviCoupon,
    String? nota,
  }) = _VoceCoupon;

  /// Dal JSON dell'API.
  factory VoceCoupon.fromJson(Map<String, dynamic> json) => _$VoceCouponFromJson(json);
}

/// `POST /coupon/anteprima`: il codice e le offerte.
@freezed
abstract class AnteprimaCouponPubblica with _$AnteprimaCouponPubblica {
  /// L'anteprima.
  const factory AnteprimaCouponPubblica({
    required CouponPubblico coupon,
    @Default(<VoceCoupon>[]) List<VoceCoupon> offerte,
  }) = _AnteprimaCouponPubblica;

  const AnteprimaCouponPubblica._();

  /// Dal JSON dell'API.
  factory AnteprimaCouponPubblica.fromJson(Map<String, dynamic> json) => _$AnteprimaCouponPubblicaFromJson(json);

  /// La variante che la pagina mostra (`voceCoupon()` del sito).
  VoceCoupon? voce(String piano, {required bool annuale, required bool rinnovo, bool prova = false}) =>
      offerte.where((o) => o.piano == piano && o.annuale == annuale && o.rinnovo == rinnovo && o.prova == prova).firstOrNull;
}

/// `POST /me/coupon/riscatta`: un codice regalo.
@freezed
abstract class Riscatto with _$Riscatto {
  /// `{crediti, saldo}`.
  const factory Riscatto({@Default(0) int crediti, @Default(0) int saldo}) = _Riscatto;

  /// Dal JSON dell'API.
  factory Riscatto.fromJson(Map<String, dynamic> json) => _$RiscattoFromJson(json);
}

/* ---- negozio (mazzi, carrello, ordini) ------------------------------------------------------------------------------ */

/// Un mazzo del negozio: il predefinito (Thoth) è sempre posseduto.
@freezed
abstract class Mazzo with _$Mazzo {
  /// Un mazzo.
  const factory Mazzo({
    required int id,
    required String slug,
    required String nome,
    String? descrizione,
    @Default(false) bool predefinito,
    @Default(true) bool attivo,
    @Default(true) bool attivoOra,
    String? attivazioneDa,
    String? attivazioneFino,
    int? prezzoDigitale,
    int? prezzoDigitaleScontato,
    int? prezzoStampaScontato,
    int? prezzoFisicoScontato,
    @Default(<String>[]) List<String> offertaFormati,
    @Default(false) bool offertaAttiva,
    String? offertaValidoFino,
    int? prezzoStampa,
    int? prezzoFisico,
    @Default(false) bool richiedeSpedizione,
    @Default('EUR') String valuta,
    @Default(0) int rank,
  }) = _Mazzo;

  /// Dal JSON dell'API.
  factory Mazzo.fromJson(Map<String, dynamic> json) => _$MazzoFromJson(json);
}

/// Il mazzo di una riga d'ordine.
@freezed
abstract class MazzoRiga with _$MazzoRiga {
  /// `{nome, slug}`.
  const factory MazzoRiga({required String nome, required String slug}) = _MazzoRiga;

  /// Dal JSON dell'API.
  factory MazzoRiga.fromJson(Map<String, dynamic> json) => _$MazzoRigaFromJson(json);
}

/// Una riga di un ordine.
@freezed
abstract class RigaOrdine with _$RigaOrdine {
  /// Una riga.
  const factory RigaOrdine({
    required int id,

    /// `digitale`, `pdf`, `fisico`.
    required String tipo,
    required int deckId,
    MazzoRiga? mazzo,
    @Default(1) int quantita,
    @Default(0) int prezzoPienoUnitario,
    @Default(0) int prezzoFinaleUnitario,
    String? statoEvasione,
  }) = _RigaOrdine;

  /// Dal JSON dell'API.
  factory RigaOrdine.fromJson(Map<String, dynamic> json) => _$RigaOrdineFromJson(json);
}

/// Un ordine del negozio.
@freezed
abstract class Ordine with _$Ordine {
  /// Un ordine.
  const factory Ordine({
    required String id,
    required String status,
    @Default(0) int importoTotale,
    @Default(0) int scontoScaglioni,
    @Default('EUR') String valuta,
    @Default(<RigaOrdine>[]) List<RigaOrdine> righe,
    Map<String, String?>? indirizzoSpedizione,
    String? creato,
    String? completato,

    /// Solo nella risposta di `POST /orders`: dove pagare (`null` se i pagamenti non sono attivi).
    String? url,
    bool? pagamentoAttivo,
  }) = _Ordine;

  /// Dal JSON dell'API.
  factory Ordine.fromJson(Map<String, dynamic> json) => _$OrdineFromJson(json);
}

/// Una riga del preventivo del carrello.
@freezed
abstract class RigaPreventivo with _$RigaPreventivo {
  /// Una riga.
  const factory RigaPreventivo({
    required int deckId,
    required String tipo,
    @Default(1) int quantita,
    @Default(0) int prezzoPienoUnitario,
    @Default(0) int prezzoFinaleUnitario,
  }) = _RigaPreventivo;

  /// Dal JSON dell'API.
  factory RigaPreventivo.fromJson(Map<String, dynamic> json) => _$RigaPreventivoFromJson(json);
}

/// `POST /shop/quote`: il prezzo di un carrello secondo il server.
@freezed
abstract class Preventivo with _$Preventivo {
  /// Il preventivo.
  const factory Preventivo({
    @Default(<RigaPreventivo>[]) List<RigaPreventivo> righe,
    @Default(0) int subtotale,
    @Default(0) num scaglionePercentuale,
    @Default(0) int scontoScaglioni,
    @Default(0) int totale,
    @Default(false) bool richiedeIndirizzo,
    @Default(false) bool pagamentoAttivo,
  }) = _Preventivo;

  /// Dal JSON dell'API.
  factory Preventivo.fromJson(Map<String, dynamic> json) => _$PreventivoFromJson(json);
}

/// Un indirizzo di spedizione.
@freezed
abstract class Indirizzo with _$Indirizzo {
  /// Un indirizzo.
  const factory Indirizzo({
    required String id,
    required String nome,
    required String via,
    required String citta,
    required String cap,
    String? provincia,
    required String paese,
    String? telefono,
    @Default(false) bool predefinito,
  }) = _Indirizzo;

  /// Dal JSON dell'API.
  factory Indirizzo.fromJson(Map<String, dynamic> json) => _$IndirizzoFromJson(json);
}
