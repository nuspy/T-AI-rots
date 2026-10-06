/// v9.5, la lingua di lettura dei contenuti: quella in cui l'app traduce articoli, carte, stese e mazzi sul telefono
/// (`motore.dart`). Si sceglie al primo avvio fra tutte le lingue di ML Kit (`scelta_lingua.dart`) e si cambia dal
/// piè di pagina; resta sul telefono, nell'archivio. È distinta dalla lingua dell'interfaccia (15 lingue, tradotte a
/// mano): chi legge in ungherese può avere i menu in inglese, e viceversa.
library;

import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../archivio.dart';
import 'motore.dart';

/// La chiave nell'archivio.
const String chiaveLinguaContenuti = 'lingua_contenuti';

/// I nomi delle lingue di ML Kit nella loro lingua (come le si cerca e le si riconosce).
const Map<String, String> nomiLingue = {
  'af': 'Afrikaans',
  'sq': 'Shqip',
  'ar': 'العربية',
  'be': 'Беларуская',
  'bn': 'বাংলা',
  'bg': 'Български',
  'ca': 'Català',
  'zh': '中文',
  'hr': 'Hrvatski',
  'cs': 'Čeština',
  'da': 'Dansk',
  'nl': 'Nederlands',
  'en': 'English',
  'eo': 'Esperanto',
  'et': 'Eesti',
  'fi': 'Suomi',
  'fr': 'Français',
  'gl': 'Galego',
  'ka': 'ქართული',
  'de': 'Deutsch',
  'el': 'Ελληνικά',
  'gu': 'ગુજરાતી',
  'ht': 'Kreyòl ayisyen',
  'he': 'עברית',
  'hi': 'हिन्दी',
  'hu': 'Magyar',
  'is': 'Íslenska',
  'id': 'Bahasa Indonesia',
  'ga': 'Gaeilge',
  'it': 'Italiano',
  'ja': '日本語',
  'kn': 'ಕನ್ನಡ',
  'ko': '한국어',
  'lt': 'Lietuvių',
  'lv': 'Latviešu',
  'mk': 'Македонски',
  'mr': 'मराठी',
  'ms': 'Bahasa Melayu',
  'mt': 'Malti',
  'no': 'Norsk',
  'fa': 'فارسی',
  'pl': 'Polski',
  'pt': 'Português',
  'ro': 'Română',
  'ru': 'Русский',
  'sk': 'Slovenčina',
  'sl': 'Slovenščina',
  'es': 'Español',
  'sw': 'Kiswahili',
  'sv': 'Svenska',
  'tl': 'Tagalog',
  'ta': 'தமிழ்',
  'te': 'తెలుగు',
  'th': 'ไทย',
  'tr': 'Türkçe',
  'uk': 'Українська',
  'ur': 'اردو',
  'vi': 'Tiếng Việt',
  'cy': 'Cymraeg',
};

/// Il nome di una lingua nella sua lingua (il codice, se non è fra quelle note).
String nomeLingua(String codice) => nomiLingue[codice] ?? codice.toUpperCase();

/// La lingua di lettura: `null` finché non la si è scelta (il primo avvio la chiede).
class LinguaContenuti extends Notifier<String?> {
  @override
  String? build() {
    final salvata = ref.read(archivioProvider).leggi(chiaveLinguaContenuti);
    return salvata != null && salvata.isNotEmpty ? salvata : null;
  }

  /// Sceglie [codice] e lo salva.
  void scegli(String codice) {
    state = codice;
    unawaited(ref.read(archivioProvider).scrivi(chiaveLinguaContenuti, codice));
  }
}

/// La lingua di lettura.
final linguaContenutiProvider = NotifierProvider<LinguaContenuti, String?>(LinguaContenuti.new);

/// Vero se il primo avvio deve chiedere la lingua di lettura: solo dove il telefono sa tradurre.
final linguaContenutiDaChiedereProvider = Provider<bool>(
  (ref) => ref.watch(motoreTraduzioneProvider).disponibile && ref.watch(linguaContenutiProvider) == null,
);
