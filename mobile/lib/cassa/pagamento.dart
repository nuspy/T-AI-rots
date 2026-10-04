/// I pagamenti con carta nell'app: la pagina di pagamento (Stripe, o il simulatore del backend in sviluppo) si apre
/// **nel browser di sistema**, e dopo il pagamento si torna all'app. Dalla Fase 9 nell'app si compra nello store
/// (`acquisti/`): la carta resta per il carrello del negozio fisico e, dove il catalogo dello store la ammette, per
/// crediti e abbonamenti.
///
/// - **iPhone e iPad**: il ritorno è un deep link dell'app, `chat.tarots.app://ritorno/<percorso>?checkout=<id>` (il
///   backend ammette solo gli schemi di `ritorno_schemi_app`; Stripe torna solo a indirizzi web, quindi passa da
///   `/billing/ritorno-app`). go_router lo riceve come `/<percorso>?checkout=<id>`.
/// - **Android**: lo schema `chat.tarots.app` è già di flutter_appauth (il ritorno dell'accesso,
///   `chat.tarots.app:/oauth2redirect`, senza host): un secondo filtro sullo stesso schema fa scegliere ogni volta fra
///   due «TAROTS chat» (provato sull'emulatore). Il ritorno è quindi la pagina del sito
///   (`https://tarots.chat/pricing?checkout=<id>`), che è un **App Link** (Fase 10: filtro `autoVerify` nel manifesto
///   e `/.well-known/assetlinks.json` con le impronte dalla console): Android la apre direttamente nell'app. Se il
///   browser non la passa all'app (Chrome lo fa solo per una navigazione partita da un tocco), mostra l'esito del sito
///   e l'app, tornata in primo piano, va da sé alla pagina di ritorno.
/// - In tutti i casi la pagina (prezzi, prova, carrello, profilo) chiede al server com'è andata (`GET
///   /me/checkout/{id}`): non si fida dell'indirizzo, come il sito. Se il ritorno non arriva (il browser chiuso a
///   metà), al ritorno in primo piano l'app va comunque alla pagina di ritorno: il pagamento in sospeso è ricordato
///   in [pagamentoInSospesoProvider].
/// - Gli abbonamenti comprati negli store si gestiscono nello store (`apriGestioneStore` in `acquisti/acquisti.dart`).
library;

import 'dart:async';
import 'dart:io' show Platform;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

/// Lo schema dell'app (`ritorno_schemi_app` del backend, Info.plist, AndroidManifest).
const String schemaApp = 'chat.tarots.app';

/// L'indirizzo di ritorno di un pagamento per la pagina [percorso] dell'app (un percorso interno: `/pricing`): il deep
/// link su iOS, la pagina del sito su Android (vedi sopra; il backend la completa col suo indirizzo pubblico).
String ritornoApp(String percorso, {bool? ios}) => (ios ?? Platform.isIOS) ? '$schemaApp://ritorno$percorso' : percorso;

/// Vero se [uri] è un ritorno dell'app (il deep link di un pagamento).
bool eRitornoApp(Uri uri) => uri.scheme == schemaApp && uri.host == 'ritorno';

/// Apre [url] fuori dall'app (il browser di sistema, o l'app che lo gestisce: lo store, la posta).
Future<bool> apriFuori(String url) async {
  final uri = Uri.tryParse(url);
  if (uri == null) return false;
  try {
    return await launchUrl(uri, mode: LaunchMode.externalApplication);
  } on Object catch (e) {
    debugPrint('Indirizzo non aperto ($url): $e');
    return false;
  }
}

/// Il pagamento aperto nel browser e non ancora tornato: dove andare al ritorno (`/pricing?checkout=…`).
class PagamentoInSospeso extends Notifier<String?> {
  @override
  String? build() => null;

  /// Apre la pagina di pagamento [url] e ricorda dove tornare ([ritorno], col suo `?checkout=`).
  Future<bool> apri(String url, {required String ritorno}) async {
    state = ritorno;
    final aperto = await apriFuori(url);
    if (!aperto) state = null;
    return aperto;
  }

  /// La pagina di ritorno l'ha preso in carico (col deep link o al ritorno in primo piano).
  void concluso() => state = null;
}

/// Il pagamento in sospeso.
final pagamentoInSospesoProvider = NotifierProvider<PagamentoInSospeso, String?>(PagamentoInSospeso.new);

