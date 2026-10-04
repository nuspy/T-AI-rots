/// L'identità anonima di chi usa l'app per le condivisioni (`idVisitatore()` di `frontend/lib/condivisione.ts`): il
/// server distingue chi condivide da chi apre il collegamento e ne conserva solo un'impronta con sale.
///
/// Come nel sito, l'identificativo resta sul telefono solo col consenso `statistiche` (ed è lo stesso del livello
/// esteso delle statistiche, `lanterna.id`); senza, vive quanto l'app aperta e non riconosce nessuno nei giorni dopo.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../app.dart' show chiaveIdStatistiche;
import '../archivio.dart';
import 'lanterna.dart' show nuovoIdentificativo;

String? _soloInMemoria;

/// L'identificativo da mandare con un clic di condivisione o con la visita a una lettura condivisa.
final visitatoreProvider = Provider<String Function()>((ref) {
  final archivio = ref.watch(archivioProvider);
  return () => archivio.leggi(chiaveIdStatistiche) ?? (_soloInMemoria ??= nuovoIdentificativo());
});
