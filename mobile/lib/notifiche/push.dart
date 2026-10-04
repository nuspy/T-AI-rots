/// Le notifiche push sul telefono (Fase 9): Firebase Cloud Messaging per riceverle (anche su iPhone: FCM le passa ad
/// APNs), `flutter_local_notifications` per mostrarle quando l'app è aperta (su Android FCM non le mostra da sé) e
/// per i due canali Android (`servizio`, `promozioni`: il backend sceglie il canale, la persona può spegnere le
/// promozioni dalle impostazioni del telefono senza perdere la carta del giorno).
///
/// [ServizioPush] è ciò che il resto dell'app ne vede; [ServizioPushFirebase] è quello vero, [ServizioPushSpento]
/// quello dei test e di un'app senza Firebase configurato (mancano `google-services.json` e
/// `GoogleService-Info.plist`): l'app funziona lo stesso, col push spento e un messaggio nel log.
///
/// **Il permesso non si chiede mai all'avvio**: l'inizializzazione non chiede niente (su iOS
/// `DarwinInitializationSettings` con le richieste spente, e la generazione automatica del token FCM è spenta nel
/// manifesto e nell'Info.plist); lo chiede [ServizioPush.chiediPermesso], dopo un sì della persona.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;

import 'package:dio/dio.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/firebase.dart' show avviaFirebase;
import '../cassa/pagamento.dart' show apriFuori;

/// Una notifica ricevuta: titolo e testo, l'immagine grande, il canale Android e i dati del backend (`link`, `invio`,
/// `firma`, `tipo`: `notifiche/invio.py`).
@immutable
class MessaggioPush {
  /// Una notifica.
  const MessaggioPush({this.titolo, this.corpo, this.immagine, this.canale = 'servizio', this.dati = const {}});

  /// Da un messaggio di FCM.
  factory MessaggioPush.daRemoto(RemoteMessage m) => MessaggioPush(
    titolo: m.notification?.title,
    corpo: m.notification?.body,
    immagine: m.notification?.android?.imageUrl ?? m.notification?.apple?.imageUrl,
    canale: m.notification?.android?.channelId ?? 'servizio',
    dati: {for (final e in m.data.entries) e.key: '${e.value}'},
  );

  /// Dal `payload` di una notifica locale (i dati in JSON).
  factory MessaggioPush.daPayload(String? payload) {
    try {
      final d = jsonDecode(payload ?? '{}');
      return MessaggioPush(dati: d is Map ? {for (final e in d.entries) '${e.key}': '${e.value}'} : const {});
    } on FormatException {
      return const MessaggioPush();
    }
  }

  /// Il titolo.
  final String? titolo;

  /// Il testo.
  final String? corpo;

  /// L'immagine grande (https), se c'è.
  final String? immagine;

  /// Il canale Android (`servizio` o `promozioni`).
  final String canale;

  /// I dati del backend.
  final Map<String, String> dati;

  /// Il percorso del sito da aprire (`/daily-card`).
  String get link => dati['link'] ?? '/';
}

/// Il permesso di mostrare notifiche.
enum PermessoPush {
  /// Concesso (anche «provvisorio» su iOS).
  concesso,

  /// Negato: si riaccende solo dalle impostazioni del telefono.
  negato,

  /// Mai chiesto.
  nonChiesto,
}

/// I nomi dei canali Android nella lingua dell'app (si vedono nelle impostazioni del telefono).
typedef NomiCanali = ({String servizio, String servizioTesto, String promozioni, String promozioniTesto});

/// Le notifiche push del telefono.
abstract interface class ServizioPush {
  /// Inizializza (una volta). Falso se le notifiche non ci sono (Firebase non configurato).
  Future<bool> avvia();

  /// I canali Android coi nomi nella lingua dell'app (rifarli aggiorna i nomi).
  Future<void> canali(NomiCanali nomi);

  /// Il permesso attuale, senza chiedere niente.
  Future<PermessoPush> permesso();

  /// Chiede il permesso (solo dopo un sì della persona).
  Future<PermessoPush> chiediPermesso();

  /// Il token FCM di questo telefono (lo genera, se serve).
  Future<String?> token();

  /// I token nuovi (FCM li cambia ogni tanto).
  Stream<String> get tokenNuovi;

  /// Cancella il token: questo telefono non riceve più niente finché non se ne chiede uno nuovo.
  Future<void> cancellaToken();

  /// Le notifiche toccate (con l'app aperta o in secondo piano).
  Stream<MessaggioPush> get toccate;

  /// La notifica toccata che ha aperto l'app, se c'è.
  Future<MessaggioPush?> iniziale();

  /// Apre le impostazioni delle notifiche dell'app nel telefono.
  Future<bool> apriImpostazioni();
}

/// Le notifiche spente: i test, e l'app senza Firebase.
class ServizioPushSpento implements ServizioPush {
  @override
  Future<bool> avvia() async => false;

  @override
  Future<void> canali(NomiCanali nomi) async {}

  @override
  Future<PermessoPush> permesso() async => PermessoPush.nonChiesto;

  @override
  Future<PermessoPush> chiediPermesso() async => PermessoPush.nonChiesto;

  @override
  Future<String?> token() async => null;

  @override
  Stream<String> get tokenNuovi => const Stream.empty();

  @override
  Future<void> cancellaToken() async {}

  @override
  Stream<MessaggioPush> get toccate => const Stream.empty();

  @override
  Future<MessaggioPush?> iniziale() async => null;

  @override
  Future<bool> apriImpostazioni() async => false;
}

/// Il canale verso `MainActivity.kt` per aprire le impostazioni delle notifiche dell'app (Android: non c'è un
/// indirizzo per farlo; su iOS basta `app-settings:`).
const MethodChannel canaleImpostazioni = MethodChannel('chat.tarots.app/impostazioni');

/// Firebase Cloud Messaging e le notifiche locali.
class ServizioPushFirebase implements ServizioPush {
  final FlutterLocalNotificationsPlugin _locali = FlutterLocalNotificationsPlugin();
  final StreamController<MessaggioPush> _toccate = StreamController<MessaggioPush>.broadcast();
  Future<bool>? _avvio;
  MessaggioPush? _daLocale;

  FirebaseMessaging get _fcm => FirebaseMessaging.instance;

  @override
  Future<bool> avvia() => _avvio ??= _avvia();

  Future<bool> _avvia() async {
    if (!await avviaFirebase()) {
      debugPrint('Notifiche spente: Firebase non è configurato (vedi mobile/LEGGIMI.md, «Attivare le notifiche»).');
      return false;
    }
    try {
      await _locali.initialize(
        settings: const InitializationSettings(
          android: AndroidInitializationSettings('@drawable/ic_notifica'),
          // Nessuna richiesta all'avvio: il permesso si chiede in due tempi (dopo la carta del giorno o dal profilo).
          iOS: DarwinInitializationSettings(
            requestAlertPermission: false,
            requestBadgePermission: false,
            requestSoundPermission: false,
          ),
        ),
        onDidReceiveNotificationResponse: (r) => _toccate.add(MessaggioPush.daPayload(r.payload)),
      );
      final lancio = await _locali.getNotificationAppLaunchDetails();
      if (lancio?.didNotificationLaunchApp ?? false) {
        _daLocale = MessaggioPush.daPayload(lancio!.notificationResponse?.payload);
      }
      // Su iPhone le notifiche con l'app aperta le mostra iOS; su Android le mostra l'app.
      await _fcm.setForegroundNotificationPresentationOptions(alert: true, badge: true, sound: true);
      FirebaseMessaging.onMessage.listen((m) {
        if (Platform.isAndroid && m.notification != null) unawaited(_mostra(MessaggioPush.daRemoto(m)));
      });
      FirebaseMessaging.onMessageOpenedApp.listen((m) => _toccate.add(MessaggioPush.daRemoto(m)));
      return true;
    } on Object catch (e) {
      debugPrint('Notifiche non avviate: $e');
      return false;
    }
  }

  @override
  Future<void> canali(NomiCanali nomi) async {
    final android = _locali.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
    if (android == null) return;
    await android.createNotificationChannel(
      AndroidNotificationChannel('servizio', nomi.servizio, description: nomi.servizioTesto),
    );
    await android.createNotificationChannel(
      AndroidNotificationChannel(
        'promozioni',
        nomi.promozioni,
        description: nomi.promozioniTesto,
        importance: Importance.low,
      ),
    );
  }

  static PermessoPush _permesso(AuthorizationStatus s) => switch (s) {
    AuthorizationStatus.authorized || AuthorizationStatus.provisional => PermessoPush.concesso,
    AuthorizationStatus.denied || AuthorizationStatus.deniedPermanently => PermessoPush.negato,
    AuthorizationStatus.notDetermined => PermessoPush.nonChiesto,
  };

  @override
  Future<PermessoPush> permesso() async => _permesso((await _fcm.getNotificationSettings()).authorizationStatus);

  @override
  Future<PermessoPush> chiediPermesso() async => _permesso((await _fcm.requestPermission()).authorizationStatus);

  @override
  Future<String?> token() async {
    await _fcm.setAutoInitEnabled(true);
    if (Platform.isIOS && await _fcm.getAPNSToken() == null) {
      // Su iPhone il token FCM arriva dopo quello di APNs: un attimo di pazienza.
      await Future<void>.delayed(const Duration(seconds: 2));
      if (await _fcm.getAPNSToken() == null) return null;
    }
    return _fcm.getToken();
  }

  @override
  Stream<String> get tokenNuovi => _fcm.onTokenRefresh;

  @override
  Future<void> cancellaToken() async {
    await _fcm.deleteToken();
    await _fcm.setAutoInitEnabled(false);
  }

  @override
  Stream<MessaggioPush> get toccate => _toccate.stream;

  @override
  Future<MessaggioPush?> iniziale() async {
    final remoto = await _fcm.getInitialMessage();
    if (remoto != null) return MessaggioPush.daRemoto(remoto);
    final locale = _daLocale;
    _daLocale = null;
    return locale;
  }

  /// Mostra una notifica arrivata con l'app aperta (Android), con l'immagine grande se c'è.
  Future<void> _mostra(MessaggioPush m) async {
    StyleInformation? stile;
    final immagine = m.immagine;
    if (immagine != null && immagine.startsWith('https://')) {
      try {
        final r = await Dio().get<List<int>>(
          immagine,
          options: Options(responseType: ResponseType.bytes, receiveTimeout: const Duration(seconds: 8)),
        );
        final byte = r.data;
        if (byte != null && byte.isNotEmpty) {
          final bitmap = ByteArrayAndroidBitmap(Uint8List.fromList(byte));
          stile = BigPictureStyleInformation(bitmap, contentTitle: m.titolo, summaryText: m.corpo, largeIcon: bitmap);
        }
      } on Object catch (e) {
        debugPrint('Immagine della notifica non scaricata: $e');
      }
    }
    final promozione = m.canale == 'promozioni';
    await _locali.show(
      id: (m.dati['invio'] ?? '${DateTime.now().millisecondsSinceEpoch}').hashCode & 0x7fffffff,
      title: m.titolo,
      body: m.corpo,
      payload: jsonEncode(m.dati),
      notificationDetails: NotificationDetails(
        android: AndroidNotificationDetails(
          promozione ? 'promozioni' : 'servizio',
          promozione ? 'Offers' : 'Card of the day',
          icon: '@drawable/ic_notifica',
          importance: promozione ? Importance.low : Importance.defaultImportance,
          styleInformation: stile ?? BigTextStyleInformation(m.corpo ?? ''),
        ),
      ),
    );
  }

  @override
  Future<bool> apriImpostazioni() async {
    if (Platform.isIOS) return apriFuori('app-settings:');
    try {
      return await canaleImpostazioni.invokeMethod<bool>('notifiche') ?? false;
    } on Object catch (e) {
      debugPrint('Impostazioni delle notifiche non aperte: $e');
      return false;
    }
  }
}

/// Le notifiche push del telefono (spente nei test e dove non ci sono Android o iOS).
final servizioPushProvider = Provider<ServizioPush>((ref) {
  if (kIsWeb || !(Platform.isAndroid || Platform.isIOS)) return ServizioPushSpento();
  return ServizioPushFirebase();
});
