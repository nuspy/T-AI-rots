/// v9.5, la lingua di lettura dei contenuti: quella in cui l'app traduce articoli, carte, stese e mazzi sul telefono
/// (`motore.dart`). Di norma è quella dell'interfaccia (scelta al primo avvio, `lingua/scelta_lingua_app.dart`); dal
/// piè di pagina se ne sceglie un'altra fra tutte le lingue di ML Kit (`scelta_lingua.dart`), che resta sul telefono,
/// nell'archivio: chi legge in ungherese può avere i menu in inglese, e viceversa.
library;

import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../archivio.dart';
import '../lingua/lingua.dart';

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

/// La lingua di lettura (9/10/2026): segue quella dell'interfaccia, senza una domanda a parte al primo avvio. Una
/// lingua diversa scelta dal piè di pagina si ricorda (`lingua_contenuti`: le lingue di ML Kit sono molte più delle
/// quindici dell'app) e da allora non segue più l'interfaccia; scegliere di nuovo quella dell'interfaccia torna a
/// seguirla. Una scelta salvata uguale all'interfaccia (il vecchio primo avvio) vale come «segue».
class LinguaContenuti extends Notifier<String> {
  @override
  String build() {
    final interfaccia = ref.watch(linguaProvider);
    final archivio = ref.read(archivioProvider);
    final salvata = archivio.leggi(chiaveLinguaContenuti);
    if (salvata == null || salvata.isEmpty) return interfaccia;
    if (salvata == interfaccia) {
      unawaited(archivio.scrivi(chiaveLinguaContenuti, null));
      return interfaccia;
    }
    return salvata;
  }

  /// Sceglie [codice]: diversa dall'interfaccia si salva, uguale torna a seguire l'interfaccia.
  void scegli(String codice) {
    final segue = codice == ref.read(linguaProvider);
    state = codice;
    unawaited(ref.read(archivioProvider).scrivi(chiaveLinguaContenuti, segue ? null : codice));
  }
}

/// La lingua di lettura.
final linguaContenutiProvider = NotifierProvider<LinguaContenuti, String>(LinguaContenuti.new);
