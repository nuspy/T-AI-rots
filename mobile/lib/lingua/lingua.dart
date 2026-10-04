/// La lingua dell'interfaccia: le stesse quindici lingue del sito (`frontend/lib/i18n/lingue.ts`), nello stesso
/// ordine del selettore.
///
/// Chi decide, nell'ordine: la scelta salvata (chiave `lingua`, come nel browser), la lingua del telefono,
/// l'inglese. La lingua della LETTURA è un'altra cosa (quella del quesito, decisa dal server), come nel sito.
library;

import 'dart:ui' show Locale, PlatformDispatcher, TextDirection;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../archivio.dart';
import '../l10n/liste.g.dart' show lingueTradotte;

/// Una lingua del selettore.
typedef DatiLingua = ({String codice, String nome, String locale, bool rtl});

/// Le quindici lingue, nell'ordine del selettore del sito.
const List<DatiLingua> lingue = [
  (codice: 'it', nome: 'Italiano', locale: 'it-IT', rtl: false),
  (codice: 'hu', nome: 'Magyar', locale: 'hu-HU', rtl: false),
  (codice: 'en', nome: 'English', locale: 'en-GB', rtl: false),
  (codice: 'de', nome: 'Deutsch', locale: 'de-DE', rtl: false),
  (codice: 'ru', nome: 'Русский', locale: 'ru-RU', rtl: false),
  (codice: 'uk', nome: 'Українська', locale: 'uk-UA', rtl: false),
  (codice: 'fr', nome: 'Français', locale: 'fr-FR', rtl: false),
  (codice: 'es', nome: 'Español', locale: 'es-ES', rtl: false),
  (codice: 'pt', nome: 'Português', locale: 'pt-PT', rtl: false),
  (codice: 'ro', nome: 'Română', locale: 'ro-RO', rtl: false),
  (codice: 'pl', nome: 'Polski', locale: 'pl-PL', rtl: false),
  (codice: 'zh', nome: '中文', locale: 'zh-CN', rtl: false),
  (codice: 'hi', nome: 'हिन्दी', locale: 'hi-IN', rtl: false),
  (codice: 'ko', nome: '한국어', locale: 'ko-KR', rtl: false),
  (codice: 'ar', nome: 'العربية', locale: 'ar', rtl: true),
];

/// La lingua predefinita.
const String predefinita = 'en';

/// Un codice qualunque («pt-BR», «ZH_cn», «hu») come lingua supportata, o `null`.
String? comeLingua(String? codice) {
  final base = (codice ?? '').trim().toLowerCase().replaceAll('_', '-').split('-').first;
  return lingue.any((l) => l.codice == base) ? base : null;
}

/// La prima lingua del telefono fra quelle supportate; l'inglese se nessuna lo è.
String linguaDelSistema(List<Locale> preferite) => linguaSupportataDelSistema(preferite) ?? predefinita;

/// La prima lingua del telefono che l'app ha, o null (allora l'ultimo indizio è il paese, `/lingua-suggerita`).
String? linguaSupportataDelSistema(List<Locale> preferite) {
  for (final p in preferite) {
    final l = comeLingua(p.languageCode);
    if (l != null) return l;
  }
  return null;
}

/// I dati di una lingua.
DatiLingua datiLingua(String codice) => lingue.firstWhere((l) => l.codice == codice, orElse: () => lingue[2]);

/// La lingua dei contenuti (carte, stese): esistono in italiano e in inglese, le altre lingue leggono l'inglese.
String linguaContenuti(String lingua) => lingua == 'it' ? 'it' : 'en';

/// Il verso del testo: destra→sinistra solo per una lingua che lo vuole e che è tradotta davvero (come nel sito).
TextDirection versoDi(String lingua) =>
    datiLingua(lingua).rtl && lingueTradotte.contains(lingua) ? TextDirection.rtl : TextDirection.ltr;

/// La chiave della scelta salvata: la stessa del sito.
const String chiaveLingua = 'lingua';

/// La lingua corrente dell'interfaccia.
class LinguaNotifier extends Notifier<String> {
  @override
  String build() {
    final salvata = comeLingua(ref.read(archivioProvider).leggi(chiaveLingua));
    return salvata ?? linguaDelSistema(PlatformDispatcher.instance.locales);
  }

  /// Vero se la lingua è una scelta salvata (non un indizio del telefono o del paese).
  bool get scelta => comeLingua(ref.read(archivioProvider).leggi(chiaveLingua)) != null;

  /// Applica la lingua suggerita dal paese, senza ricordarla come scelta: solo se nessuno ha ancora scelto.
  void applicaSuggerita(String lingua) {
    final l = comeLingua(lingua);
    if (l != null && !scelta) state = l;
  }

  /// Sceglie [lingua] e la ricorda.
  Future<void> imposta(String lingua) async {
    final l = comeLingua(lingua);
    if (l == null) return;
    state = l;
    await ref.read(archivioProvider).scrivi(chiaveLingua, l);
  }
}

/// La lingua dell'interfaccia.
final linguaProvider = NotifierProvider<LinguaNotifier, String>(LinguaNotifier.new);
