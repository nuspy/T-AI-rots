/// Il fuso orario del telefono (IANA: `Europe/Rome`), come `fusoDelBrowser()` del sito: decide il giorno della carta
/// del giorno e l'ora delle notifiche. Lo dà `flutter_timezone`; dove il plugin non c'è (i test) è `null`, e il server
/// usa quello che già conosce (o Roma).
library;

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_timezone/flutter_timezone.dart';

/// Il fuso del telefono, o `null` se non si sa.
Future<String?> fusoDelTelefono() async {
  try {
    final fuso = (await FlutterTimezone.getLocalTimezone()).identifier;
    return fuso.isEmpty ? null : fuso;
  } on Object catch (e) {
    debugPrint('Fuso orario del telefono non letto: $e');
    return null;
  }
}

/// Come leggere il fuso (sostituibile nei test).
final leggiFusoProvider = Provider<Future<String?> Function()>((ref) => fusoDelTelefono);

/// Il fuso del telefono, letto una volta.
final fusoProvider = FutureProvider<String?>((ref) => ref.read(leggiFusoProvider)());
