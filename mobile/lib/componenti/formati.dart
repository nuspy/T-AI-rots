/// I formati dei numeri e delle date, come il sito: `euro()` di `frontend/lib/api.ts` (`Intl.NumberFormat` con la
/// valuta) e le date nella lingua dell'interfaccia (`toLocaleDateString(locale, …)`), con le stesse convenzioni.
library;

import 'package:intl/intl.dart';

import '../lingua/lingua.dart';

/// Il locale di `intl` per la lingua [lingua] (`it` → `it_IT`).
String localeIntl(String lingua) => datiLingua(lingua).locale.replaceAll('-', '_');

/// Un importo in centesimi nella valuta (`euro(centesimi, valuta, locale)` del sito): «19,90 €», «€19.90».
String euro(num centesimi, String lingua, {String valuta = 'EUR'}) {
  final f = NumberFormat.simpleCurrency(locale: localeIntl(lingua), name: valuta);
  return f.format(centesimi / 100);
}

/// Una data ISO come «3 ottobre 2026» (`dateStyle: "long"`); il testo così com'è se non si legge.
String dataLunga(String? iso, String lingua, {bool utc = false}) {
  final d = DateTime.tryParse(iso ?? '');
  if (d == null) return iso ?? '';
  return DateFormat.yMMMMd(localeIntl(lingua)).format(utc ? d.toUtc() : d.toLocal());
}

/// Una data ISO come «3 ott 2026» (`dateStyle: "medium"`).
String dataMedia(String? iso, String lingua) {
  final d = DateTime.tryParse(iso ?? '');
  if (d == null) return iso ?? '';
  return DateFormat.yMMMd(localeIntl(lingua)).format(d.toLocal());
}

/// Giorno, mese e ora (`{ day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" }`): «3 ottobre, 14:30».
String dataOra(String? iso, String lingua) {
  final d = DateTime.tryParse(iso ?? '');
  if (d == null) return iso ?? '';
  final l = localeIntl(lingua);
  return '${DateFormat.MMMMd(l).format(d.toLocal())}, ${DateFormat.Hm(l).format(d.toLocal())}';
}

/// Un numero con i separatori della lingua («1.234»).
String numero(num n, String lingua) => NumberFormat.decimalPattern(localeIntl(lingua)).format(n);

/// L'ora («14:30») nella lingua [lingua], nell'ora del telefono.
String ora(DateTime d, String lingua) => DateFormat.Hm(localeIntl(lingua)).format(d.toLocal());
