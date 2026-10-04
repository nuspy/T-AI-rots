/// Le preferenze locali dell'app (lingua, consensi, età confermata, identificativo delle statistiche): poche stringhe
/// in `shared_preferences`. I segreti (il refresh token) stanno altrove, in `flutter_secure_storage` (`auth/`).
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Un archivio chiave → testo. Si legge in modo sincrono (i valori sono già in memoria), si scrive in modo asincrono.
abstract interface class Archivio {
  /// Il valore salvato, o `null`.
  String? leggi(String chiave);

  /// Salva [valore], o lo toglie se è `null`.
  Future<void> scrivi(String chiave, String? valore);
}

/// L'archivio vero, su `shared_preferences` (già caricato in memoria all'avvio).
class ArchivioPreferenze implements Archivio {
  /// Su [preferenze] già caricate con `SharedPreferences.getInstance()`.
  ArchivioPreferenze(this._preferenze);

  final SharedPreferences _preferenze;

  @override
  String? leggi(String chiave) => _preferenze.getString(chiave);

  @override
  Future<void> scrivi(String chiave, String? valore) async {
    if (valore == null) {
      await _preferenze.remove(chiave);
    } else {
      await _preferenze.setString(chiave, valore);
    }
  }
}

/// Un archivio in memoria: per i test, e come ripiego se le preferenze non si possono aprire.
class ArchivioMemoria implements Archivio {
  /// Con i valori [iniziali], se ce ne sono.
  ArchivioMemoria([Map<String, String>? iniziali]) : valori = {...?iniziali};

  /// I valori salvati: i test li leggono.
  final Map<String, String> valori;

  @override
  String? leggi(String chiave) => valori[chiave];

  @override
  Future<void> scrivi(String chiave, String? valore) async {
    if (valore == null) {
      valori.remove(chiave);
    } else {
      valori[chiave] = valore;
    }
  }
}

/// L'archivio dell'app: `main.dart` lo sostituisce con quello vero, i test con uno in memoria.
final archivioProvider = Provider<Archivio>((ref) => ArchivioMemoria());
