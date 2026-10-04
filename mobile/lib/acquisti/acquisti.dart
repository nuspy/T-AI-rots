/// Gli acquisti nell'app (Fase 9): il catalogo dello store, l'acquisto, la verifica sul server, il ripristino.
///
/// **L'ordine conta.** Un acquisto che arriva dallo store (nuovo o ripristinato) si manda **prima** al server
/// (`POST /billing/store/google/verifica` o `apple/verifica`), che lo rilegge dallo store, controlla che sia di questo
/// account (`app_account_token`) e accredita una volta sola; **solo dopo** l'app lo chiude presso lo store:
/// - Apple: `Transaction.finish` sempre, dopo una verifica riuscita;
/// - Google: niente, se il server l'ha già confermato (consumato il pacchetto, riconosciuto l'abbonamento); altrimenti
///   l'app consuma o riconosce da sé. Un acquisto che il server non ha potuto registrare **non** si chiude: Google lo
///   rimborsa da solo dopo tre giorni, Apple lo ridà all'avvio successivo e si riprova.
///
/// **In attesa** (Google `PENDING`: un pagamento in contanti; Apple «Chiedi di acquistare»): niente crediti e niente
/// chiusura, un avviso chiaro; quando lo store lo incassa, l'acquisto torna come `purchased` (o arriva la notifica allo
/// server, che accredita da sé).
///
/// **Senza account** non si compra (la pagina fa entrare prima). Un acquisto che arriva prima dell'accesso (all'avvio)
/// aspetta l'accesso; uno che il server non ha potuto verificare (rete assente, store che non risponde) si riprova
/// all'accesso e quando l'app torna in primo piano. All'avvio, su Android, si riprendono anche gli acquisti che lo
/// store ha e l'app non ha chiuso.
///
/// Gli errori diventano un [EsitoAcquisto] (i testi nella lingua dell'app sono in [testoEsito]).
library;

import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:in_app_purchase/in_app_purchase.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../cassa/pagamento.dart' show apriFuori;
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/store.dart';
import '../profilo/dati_account.dart' show mioAbbonamentoProvider;
import 'negozio.dart';

/// Com'è andata, per il messaggio da mostrare.
enum EsitoAcquisto {
  /// Accreditato.
  fatto,

  /// In attesa del pagamento presso lo store.
  inAttesa,

  /// Chi compra ha chiuso la finestra dello store.
  annullato,

  /// Il ripristino ha trovato acquisti, ora registrati.
  ripristinati,

  /// Il ripristino non ha trovato niente.
  nienteDaRipristinare,

  /// L'acquisto è di un altro account.
  errAccount,

  /// Il server non ha potuto registrarlo (store che non risponde, prodotto non collegato in console): si riprova.
  errRegistrazione,

  /// Il server non si raggiunge: si riprova.
  errRete,

  /// Lo store non conferma l'acquisto (firma, token sconosciuto).
  errNonValido,

  /// Lo store dice che è già posseduto.
  errPosseduto,

  /// Qualunque altro errore.
  errGenerico,

  /// Lo store non risponde su questo telefono.
  nonDisponibile,
}

/// Lo stato degli acquisti per le pagine.
@immutable
class StatoAcquisti {
  /// Uno stato.
  const StatoAcquisti({this.inCorso = false, this.esito, this.piano, this.pacchetto = false});

  /// Un acquisto o un ripristino è aperto (i bottoni si spengono).
  final bool inCorso;

  /// L'ultimo esito da mostrare.
  final EsitoAcquisto? esito;

  /// Il nome del piano dell'ultimo acquisto riuscito.
  final String? piano;

  /// L'ultimo acquisto riuscito era un pacchetto di crediti.
  final bool pacchetto;

  /// Una copia con [inCorso] diverso.
  StatoAcquisti conInCorso(bool valore) => StatoAcquisti(inCorso: valore, esito: esito, piano: piano, pacchetto: pacchetto);

  @override
  bool operator ==(Object other) =>
      other is StatoAcquisti &&
      other.inCorso == inCorso &&
      other.esito == esito &&
      other.piano == piano &&
      other.pacchetto == pacchetto;

  @override
  int get hashCode => Object.hash(inCorso, esito, piano, pacchetto);
}

/// Il testo di un esito, col nome dello [store].
String testoEsito(AppLocalizations t, EsitoAcquisto e, String store, {String? piano, bool pacchetto = false}) =>
    switch (e) {
      EsitoAcquisto.fatto =>
        pacchetto ? t.prezzi_pagato_pacchetto(piano ?? '') : t.prezzi_pagato_piano(piano ?? ''),
      EsitoAcquisto.inAttesa => t.app_store_in_attesa(store),
      EsitoAcquisto.annullato => t.app_store_annullato,
      EsitoAcquisto.ripristinati => t.app_store_ripristinati,
      EsitoAcquisto.nienteDaRipristinare => t.app_store_niente_da_ripristinare,
      EsitoAcquisto.errAccount => t.app_store_err_account,
      EsitoAcquisto.errRegistrazione => t.app_store_err_registrazione,
      EsitoAcquisto.errRete => t.app_store_err_rete,
      EsitoAcquisto.errNonValido => t.app_store_err_non_valido(store),
      EsitoAcquisto.errPosseduto => t.app_store_err_posseduto,
      EsitoAcquisto.errGenerico => t.app_store_err_generico,
      EsitoAcquisto.nonDisponibile => t.app_store_non_disponibile(store),
    };

/// Vero per un esito buono (verde), falso per un errore (rosso); `null` per un avviso neutro.
bool? esitoBuono(EsitoAcquisto e) => switch (e) {
  EsitoAcquisto.fatto || EsitoAcquisto.ripristinati => true,
  EsitoAcquisto.inAttesa || EsitoAcquisto.annullato || EsitoAcquisto.nienteDaRipristinare => null,
  _ => false,
};

/// L'esito di un errore del server sulla verifica (i motivi di `billing/store/comune.py` e dei moduli degli store).
EsitoAcquisto esitoDaErroreApi(ErroreApi e) {
  if (e.stato == 0) return EsitoAcquisto.errRete;
  return switch (e.codice) {
    'account_diverso' => EsitoAcquisto.errAccount,
    'acquisto_non_trovato' || 'firma_non_valida' || 'altra_app' || 'ambiente_non_valido' => EsitoAcquisto.errNonValido,
    'utente_sconosciuto' ||
    'prodotto_sconosciuto' ||
    'tipo_diverso' ||
    'tipo_non_gestito' ||
    'non_configurato' ||
    'credenziali' ||
    'store_non_risponde' ||
    'richiesta_rifiutata' => EsitoAcquisto.errRegistrazione,
    _ => e.stato >= 500 ? EsitoAcquisto.errRegistrazione : EsitoAcquisto.errGenerico,
  };
}

/// Vero se vale la pena riprovare la verifica più tardi (rete, store o server momentaneamente giù).
bool daRiprovare(ErroreApi e) => e.stato == 0 || e.stato == 401 || e.stato >= 500;

/// L'esito di un errore dello store (`IAPError`, o l'eccezione di un acquisto che non si apre).
EsitoAcquisto esitoDaErroreStore(String? codice, String? messaggio) {
  final testo = '${codice ?? ''} ${messaggio ?? ''}'.toLowerCase();
  if (testo.contains('itemalreadyowned') || testo.contains('duplicate')) return EsitoAcquisto.errPosseduto;
  if (testo.contains('usercanceled') || testo.contains('cancel')) return EsitoAcquisto.annullato;
  if (testo.contains('billingunavailable') ||
      testo.contains('serviceunavailable') ||
      testo.contains('servicedisconnected') ||
      testo.contains('networkerror') ||
      testo.contains('itemunavailable')) {
    return EsitoAcquisto.nonDisponibile;
  }
  return EsitoAcquisto.errGenerico;
}

/// Il catalogo dello store per questo telefono: i prodotti, il pulsante Stripe per il paese dello store e, con un
/// account, il token dell'account. `null` dove non si compra negli store.
final catalogoStoreProvider = FutureProvider<CatalogoStore?>((ref) async {
  final negozio = ref.watch(negozioProvider);
  if (negozio == null) return null;
  ref.watch(sessioneProvider.select((s) => s.autenticata));
  final lingua = ref.watch(linguaProvider);
  final paese = await negozio.paese();
  return ref.read(apiProvider).catalogoStore(negozio.piattaforma, paese: paese, lingua: lingua);
});

/// Le offerte dello store (i prodotti del catalogo che lo store conosce, coi prezzi localizzati), o `null` dove non
/// si compra negli store. `disponibile` è falso se lo store non risponde.
final offerteStoreProvider = FutureProvider<({CatalogoStore catalogo, List<OffertaStore> offerte, bool disponibile})?>(
  (ref) async {
    final negozio = ref.watch(negozioProvider);
    final catalogo = await ref.watch(catalogoStoreProvider.future);
    if (negozio == null || catalogo == null) return null;
    final disponibile = await negozio.disponibile();
    var offerte = const <OffertaStore>[];
    if (disponibile) {
      try {
        offerte = await negozio.offerte(catalogo.prodotti);
      } on Object catch (e) {
        debugPrint('Prodotti dello store non letti: $e');
      }
    }
    return (catalogo: catalogo, offerte: offerte, disponibile: disponibile);
  },
);

/// Gli acquisti nell'app.
class Acquisti extends Notifier<StatoAcquisti> {
  StreamSubscription<List<PurchaseDetails>>? _ascolto;

  /// Gli acquisti da verificare appena si può (dopo l'accesso, al ritorno della rete).
  final List<PurchaseDetails> _daVerificare = [];

  /// Gli acquisti si trattano uno alla volta, nell'ordine in cui arrivano.
  Future<void> _coda = Future<void>.value();
  bool _ripristino = false;
  int _ripristinati = 0;

  /// Quanto aspettare, dopo la richiesta di ripristino, che lo store mandi gli acquisti (i test la accorciano).
  @visibleForTesting
  static Duration attesaRipristino = const Duration(milliseconds: 1500);

  Negozio? get _negozio => ref.read(negozioProvider);

  @override
  StatoAcquisti build() {
    final negozio = ref.watch(negozioProvider);
    if (negozio != null) {
      _ascolto = negozio.aggiornamenti.listen(
        (elenco) {
          for (final p in elenco) {
            _accoda(() => _tratta(p));
          }
        },
        onError: (Object e) => debugPrint('Acquisti dello store: $e'),
      );
      // All'accesso (e all'avvio con la sessione già aperta): ciò che aspettava.
      ref.listen(sessioneProvider.select((s) => s.autenticata), (prima, ora) {
        if (ora) unawaited(Future<void>.microtask(riprova));
      }, fireImmediately: true);
    }
    ref.onDispose(() => _ascolto?.cancel());
    return const StatoAcquisti();
  }

  void _accoda(Future<void> Function() lavoro) {
    _coda = _coda.then((_) => lavoro()).catchError((Object e) => debugPrint('Acquisto non trattato: $e'));
  }

  /// Aspetta che gli acquisti arrivati finora siano trattati (per i test e per il ripristino).
  Future<void> inPari() => _coda;

  void _mostra(EsitoAcquisto? esito, {bool inCorso = false, String? piano, bool pacchetto = false}) {
    state = StatoAcquisti(inCorso: inCorso, esito: esito, piano: piano, pacchetto: pacchetto);
  }

  /// L'esito è stato letto (o la pagina è cambiata).
  void letto() {
    if (state.esito != null) state = StatoAcquisti(inCorso: state.inCorso);
  }

  /// Riprova le verifiche rimaste in sospeso e, su Android, gli acquisti che lo store ha e l'app non ha chiuso.
  Future<void> riprova() async {
    final negozio = _negozio;
    if (negozio == null || !ref.read(sessioneProvider).autenticata) return;
    final rimasti = [..._daVerificare];
    _daVerificare.clear();
    List<PurchaseDetails> aperti = const [];
    try {
      aperti = await negozio.nonCompletati();
    } on Object catch (e) {
      debugPrint('Acquisti non chiusi non letti: $e');
    }
    final visti = <String>{};
    for (final p in [...rimasti, ...aperti]) {
      if (!visti.add(negozio.datoDaVerificare(p))) continue;
      _accoda(() => _verifica(p, silenzioso: true));
    }
    await _coda;
  }

  Future<void> _tratta(PurchaseDetails p) async {
    final negozio = _negozio;
    if (negozio == null) return;
    switch (p.status) {
      case PurchaseStatus.pending:
        // Niente crediti e niente chiusura finché lo store non incassa.
        _mostra(EsitoAcquisto.inAttesa);
      case PurchaseStatus.canceled:
        await _chiudiSenzaCrediti(negozio, p);
        if (state.inCorso) _mostra(EsitoAcquisto.annullato);
      case PurchaseStatus.error:
        await _chiudiSenzaCrediti(negozio, p);
        _mostra(esitoDaErroreStore(p.error?.code, '${p.error?.message} ${p.error?.details ?? ''}'));
      case PurchaseStatus.purchased:
      case PurchaseStatus.restored:
        await _verifica(p, silenzioso: p.status == PurchaseStatus.restored);
    }
  }

  /// Apple vuole chiusa anche una transazione fallita o annullata (StoreKit 1); su Google non c'è niente da chiudere.
  Future<void> _chiudiSenzaCrediti(Negozio negozio, PurchaseDetails p) async {
    if (negozio.piattaforma != 'ios' || !p.pendingCompletePurchase) return;
    try {
      await negozio.completa(p);
    } on Object catch (e) {
      debugPrint('Transazione non chiusa: $e');
    }
  }

  Future<void> _verifica(PurchaseDetails p, {required bool silenzioso}) async {
    final negozio = _negozio;
    if (negozio == null) return;
    final dato = negozio.datoDaVerificare(p);
    if (dato.isEmpty) return;
    if (!ref.read(sessioneProvider).autenticata) {
      _ricorda(negozio, p);
      return;
    }
    final api = ref.read(apiProvider);
    final lingua = ref.read(linguaProvider);
    final EsitoVerificaStore r;
    try {
      r = negozio.piattaforma == 'ios'
          ? await api.verificaApple(dato, lingua: lingua)
          : await api.verificaGoogle(p.productID, dato, lingua: lingua);
    } on ErroreApi catch (e) {
      debugPrint('Verifica dell\'acquisto ${p.productID} non riuscita: $e');
      if (daRiprovare(e)) _ricorda(negozio, p);
      if (!silenzioso) _mostra(e.stato == 401 ? EsitoAcquisto.errRete : esitoDaErroreApi(e));
      return;
    }
    if (r.acquisto.stato == 'in_attesa') {
      if (!silenzioso) _mostra(EsitoAcquisto.inAttesa);
      return;
    }
    await _chiudi(negozio, p, r.acquisto);
    _aggiornaConto();
    if (_ripristino) {
      _ripristinati++;
    } else if (!silenzioso) {
      final piano = _pianoDi(p.productID);
      _mostra(EsitoAcquisto.fatto, piano: piano?.nome ?? p.productID, pacchetto: r.acquisto.tipo == 'consumabile');
    }
  }

  void _ricorda(Negozio negozio, PurchaseDetails p) {
    final dato = negozio.datoDaVerificare(p);
    if (_daVerificare.every((x) => negozio.datoDaVerificare(x) != dato)) _daVerificare.add(p);
  }

  /// Chiude l'acquisto presso lo store **dopo** la verifica. Se non riesce, ci pensa il server (Google: la conferma
  /// notturna) o lo store lo ridà (Apple): niente errore per chi compra, i crediti sono già arrivati.
  Future<void> _chiudi(Negozio negozio, PurchaseDetails p, AcquistoRegistrato a) async {
    try {
      if (negozio.piattaforma == 'ios') {
        await negozio.completa(p);
      } else if (!a.confermato) {
        await (a.tipo == 'consumabile' ? negozio.consuma(p) : negozio.completa(p));
      }
    } on Object catch (e) {
      debugPrint('Acquisto ${p.productID} verificato ma non chiuso presso lo store: $e');
    }
  }

  void _aggiornaConto() {
    ref.invalidate(contoProvider);
    ref.invalidate(saldoProvider);
    ref.invalidate(mioAbbonamentoProvider);
  }

  PianoStore? _pianoDi(String productId) =>
      ref.read(catalogoStoreProvider).value?.prodotti.where((x) => x.productId == productId).firstOrNull?.piano;

  /// Compra [offerta]. L'esito arriva dallo store e poi dal server: lo stato lo dice.
  Future<void> compra(OffertaStore offerta) async {
    final negozio = _negozio;
    if (negozio == null || state.inCorso) return;
    _mostra(null, inCorso: true);
    try {
      final catalogo = await ref.read(catalogoStoreProvider.future);
      PurchaseDetails? vecchio;
      var upgrade = true;
      if (!offerta.consumabile && negozio.piattaforma == 'android') {
        (vecchio, upgrade) = await _daSostituire(negozio, catalogo, offerta);
      }
      final aperto = await negozio.compra(
        offerta,
        token: catalogo?.appAccountToken,
        daSostituire: vecchio,
        upgrade: upgrade,
      ).timeout(Negozio.pazienza * 2);
      if (!aperto) _mostra(EsitoAcquisto.errGenerico);
    } on TimeoutException {
      _mostra(EsitoAcquisto.nonDisponibile);
    } on InAppPurchaseException catch (e) {
      _mostra(esitoDaErroreStore(e.code, e.message));
    } on PlatformException catch (e) {
      _mostra(esitoDaErroreStore(e.code, e.message));
    } on ErroreApi catch (e) {
      _mostra(esitoDaErroreApi(e));
    }
  }

  /// Google: l'abbonamento di Play che questo sostituisce (lo stesso store non ne vende due insieme) e se è un upgrade
  /// (livello più alto o uguale: subito, col conguaglio) o un downgrade (alla scadenza).
  Future<(PurchaseDetails?, bool)> _daSostituire(Negozio negozio, CatalogoStore? catalogo, OffertaStore offerta) async {
    final abbonamenti = {
      for (final p in catalogo?.prodotti ?? const <ProdottoStore>[])
        if (p.tipo == 'abbonamento') p.productId,
    };
    List<PurchaseDetails> posseduti;
    try {
      posseduti = await negozio.posseduti();
    } on Object {
      posseduti = const [];
    }
    final vecchio = posseduti
        .where((p) => abbonamenti.contains(p.productID) && p.status != PurchaseStatus.pending)
        .firstOrNull;
    if (vecchio == null) return (null, true);
    final attuale = ref.read(contoProvider).value?.abbonamento?.piano;
    final livelloAttuale = catalogo?.prodotti.where((p) => p.piano.slug == attuale).firstOrNull?.piano.livello;
    return (vecchio, livelloAttuale == null || offerta.prodotto.piano.livello >= livelloAttuale);
  }

  /// Ripristina gli acquisti dello store (Apple chiede il bottone; su Android serve dopo un cambio di telefono).
  Future<void> ripristina() async {
    final negozio = _negozio;
    if (negozio == null || state.inCorso) return;
    _mostra(null, inCorso: true);
    _ripristino = true;
    _ripristinati = 0;
    try {
      // Senza store (niente Play Store, nessun account) il ripristino «riesce» senza trovare niente: meglio dirlo.
      if (!await negozio.disponibile()) {
        _mostra(EsitoAcquisto.nonDisponibile);
        return;
      }
      await negozio.ripristina().timeout(Negozio.pazienza * 2);
      await Future<void>.delayed(attesaRipristino);
      await _coda;
      _mostra(_ripristinati > 0 ? EsitoAcquisto.ripristinati : EsitoAcquisto.nienteDaRipristinare);
    } on InAppPurchaseException catch (e) {
      _mostra(esitoDaErroreStore(e.code, e.message));
    } on PlatformException catch (e) {
      _mostra(esitoDaErroreStore(e.code, e.message));
    } on TimeoutException {
      _mostra(EsitoAcquisto.nonDisponibile);
    } finally {
      _ripristino = false;
    }
  }

  /// Apre la gestione degli abbonamenti dello store (Google: sull'abbonamento posseduto, se lo trova).
  Future<bool> gestisci() async {
    final negozio = _negozio;
    if (negozio == null) return false;
    String? productId;
    if (negozio.piattaforma == 'android') {
      final catalogo = ref.read(catalogoStoreProvider).value;
      final abbonamenti = {
        for (final p in catalogo?.prodotti ?? const <ProdottoStore>[])
          if (p.tipo == 'abbonamento') p.productId,
      };
      try {
        productId = (await negozio.posseduti()).map((p) => p.productID).where(abbonamenti.contains).firstOrNull;
      } on Object {
        productId = null;
      }
    }
    return negozio.gestisciAbbonamenti(productId: productId);
  }
}

/// Gli acquisti nell'app.
final acquistiProvider = NotifierProvider<Acquisti, StatoAcquisti>(Acquisti.new);

/// Apre la gestione di un abbonamento dello store [provider] (`google_play`, `app_store`): nello store di questo
/// telefono col deep link ufficiale (Google Play sull'abbonamento, `showManageSubscriptions` di Apple); un abbonamento
/// dell'altro store (comprato su un altro telefono) apre la pagina web di quello store.
Future<bool> apriGestioneStore(WidgetRef ref, String? provider) {
  final negozio = ref.read(negozioProvider);
  final piattaforma = provider == 'app_store' ? 'ios' : 'android';
  if (negozio != null && negozio.piattaforma == piattaforma) return ref.read(acquistiProvider.notifier).gestisci();
  return apriFuori(provider == 'app_store' ? urlGestioneApple : urlGestioneGoogle(null));
}
