/// L'avvio: le preferenze e il cookie jar su disco, l'orientamento, le licenze dei caratteri, Firebase (se c'è),
/// poi l'app.
///
/// **Orientamento**: il telefono resta in verticale, l'iPad (e i tablet Android) ruotano in tutte le direzioni. La
/// versione mobile del sito è disegnata e misurata in verticale fra 320 e 430 px (la testata su una riga, il rito, i
/// dialoghi): un telefono in orizzontale avrebbe 360–430 px di altezza utile per una pagina larga come un tablet, e il
/// tavolo del rito non ci sta. L'iPad invece è un piccolo computer: Apple chiede tutte le orientazioni per Split View
/// e Slide Over, e le sue larghezze (768–1366 px) cadono nelle forme «tablet» e «computer» del CSS.
library;

import 'dart:async';

import 'package:cookie_jar/cookie_jar.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'analytics/firebase.dart';
import 'api/api.dart';
import 'app.dart';
import 'archivio.dart';

/// Il lato corto (in px logici) da cui un dispositivo è un tablet: la stessa soglia di Android (`sw600dp`).
const double latoTablet = 600;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Telefono in verticale, tablet libero.
  final vista = WidgetsBinding.instance.platformDispatcher.views.first;
  final lato = (vista.physicalSize / vista.devicePixelRatio).shortestSide;
  await SystemChrome.setPreferredOrientations(lato >= latoTablet ? const [] : const [DeviceOrientation.portraitUp]);
  // Da bordo a bordo: la testata scura va sotto la barra di stato, il piede sopra la barra dei gesti (safe area).
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);

  // Le licenze dei caratteri (SIL OFL 1.1) nella pagina delle licenze.
  LicenseRegistry.addLicense(() async* {
    for (final (pacchetto, file) in [
      ('DM Sans', 'assets/fonts/OFL-DMSans.txt'),
      ('Libre Baskerville', 'assets/fonts/OFL-LibreBaskerville.txt'),
    ]) {
      yield LicenseEntryWithLineBreaks([pacchetto], await rootBundle.loadString(file));
    }
  });

  final preferenze = await SharedPreferences.getInstance();
  // Il cookie `tarots_anon` della lettura anonima resta su disco, come nel browser.
  final cartella = await getApplicationSupportDirectory();
  final cookie = PersistCookieJar(storage: FileStorage('${cartella.path}/cookie/'));

  final statistiche = StatisticheFirebase();
  unawaited(statistiche.avvia());

  runApp(
    ProviderScope(
      // Come il sito (`useCarica`): una lettura che non riesce mostra l'errore, non si ripete da sola.
      retry: (tentativo, errore) => null,
      overrides: [
        archivioProvider.overrideWithValue(ArchivioPreferenze(preferenze)),
        cookieJarProvider.overrideWithValue(cookie),
        statisticheGoogleProvider.overrideWithValue(statistiche),
      ],
      child: const TarotsApp(),
    ),
  );
}
