/// L'app: il router coi percorsi del sito, i testi dei dizionari della v2, il tema del CSS della v2, e attorno ciò che
/// vale per tutte le schermate (statistiche, primo avvio).
library;

import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart';

import 'acquisti/acquisti.dart';
import 'analytics/firebase.dart';
import 'analytics/lanterna.dart';
import 'analytics/tracciato.dart';
import 'api/api.dart';
import 'api/errori.dart';
import 'archivio.dart';
import 'auth/sessione.dart';
import 'cassa/ritorno.dart';
import 'componenti/dimensione_testo.dart';
import 'consensi/consensi.dart';
import 'consensi/primo_avvio.dart';
import 'dati/inviti.dart';
import 'l10n/testi.dart';
import 'lingua/lingua.dart';
import 'lingua/lingua_profilo.dart';
import 'notifiche/notifiche.dart';
import 'profilo/codice_app.dart' show AvvisoSessione;
import 'rotte/ancore.dart';
import 'rotte/percorsi.dart';
import 'rotte/router.dart';
import 'tema/tema.dart';

/// L'email (di «Nascondi la mia email») per cui il profilo ha già proposto il codice per il sito.
const String chiaveCodiceProposto = 'collega.proposto';

/// La chiave dell'identificativo delle statistiche (il livello esteso): esiste solo col consenso `statistiche`.
const String chiaveIdStatistiche = 'lanterna.id';

/// L'app.
class TarotsApp extends ConsumerStatefulWidget {
  /// L'app.
  const TarotsApp({super.key});

  @override
  ConsumerState<TarotsApp> createState() => _TarotsAppState();
}

class _TarotsAppState extends ConsumerState<TarotsApp> {
  AppLifecycleListener? _ciclo;

  @override
  void dispose() {
    _ciclo?.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    // Fase 9: gli acquisti dello store si ascoltano dall'avvio (Apple ridà subito le transazioni non chiuse; quelli in
    // sospeso si riprovano al ritorno in primo piano); le notifiche si preparano senza chiedere niente.
    Future.microtask(() {
      ref.read(acquistiProvider);
      ref.read(notificheProvider);
    });
    _ciclo = AppLifecycleListener(onResume: () => unawaited(ref.read(acquistiProvider.notifier).riprova()));
    // All'avvio: le scelte già fatte valgono subito, poi si sincronizzano col server.
    Future.microtask(() {
      _applica(null, ref.read(consensiProvider));
      unawaited(ref.read(consensiProvider.notifier).sincronizza());
    });
    // La lingua di chi arriva: scelta salvata, poi quella del telefono, poi il paese (come il sito).
    Future.microtask(() => suggerisciDalPaese(ref));
    // La lingua del profilo e quella del selettore: vince l'ultima scelta (all'accesso, una volta per persona).
    ref.listenManual(sessioneProvider, (prima, ora) {
      if (ora.pronta && ora.autenticata) {
        unawaited(ref.read(sincroniaLinguaProvider).allinea());
        // L'invito e la lettura condivisa da cui si è arrivati, come `RiscattoInvitoAutomatico` e
        // `AttribuzioneCondivisione` del sito.
        unawaited(ref.read(riscattiProvider).prova());
        // Fase 6: al primo accesso con «Nascondi la mia email» di Apple l'account è nuovo anche se c'è quello del sito:
        // una volta per email, il profilo apre «Hai già un account sul sito?».
        final email = ora.email;
        final archivio = ref.read(archivioProvider);
        if (!(prima?.autenticata ?? false) && emailNascosta(email) && archivio.leggi(chiaveCodiceProposto) != email) {
          unawaited(archivio.scrivi(chiaveCodiceProposto, email));
          ref.read(ancoraProvider.notifier).imposta(R.profilo, 'accessi');
          unawaited(ref.read(routerProvider).push<void>(R.profilo));
        }
      }
    }, fireImmediately: true);
  }

  /// Le scelte sui consensi applicate a ciò che ne dipende: il livello esteso di lanterna (`statistiche`: il livello
  /// base va sempre, come nel sito) e Firebase (`google_analytics`).
  void _applica(StatoConsensi? prima, StatoConsensi ora) {
    final archivio = ref.read(archivioProvider);
    final lanterna = ref.read(lanternaProvider);
    if (ora.accettato('statistiche')) {
      var id = archivio.leggi(chiaveIdStatistiche);
      if (id == null) {
        id = nuovoIdentificativo();
        unawaited(archivio.scrivi(chiaveIdStatistiche, id));
      }
      lanterna.estendi(id);
    } else {
      lanterna.riduci();
      final id = archivio.leggi(chiaveIdStatistiche);
      // La revoca fa dimenticare l'identificativo anche al server, come `dimentica()` del sito.
      if (id != null && (prima?.accettato('statistiche') ?? false)) {
        unawaited(
          ref.read(apiProvider).dimenticaStatistiche(id).catchError((Object _) {}, test: (e) => e is ErroreApi),
        );
      }
      if (id != null) unawaited(archivio.scrivi(chiaveIdStatistiche, null));
    }
    unawaited(ref.read(statisticheGoogleProvider).consenso(accettato: ora.accettato('google_analytics')));
  }

  @override
  Widget build(BuildContext context) {
    ref.listen(consensiProvider, _applica);
    // Al cambio di sessione si rileggono i consensi dal server (quelli di un account non sono quelli dell'anonimo).
    ref.listen(sessioneProvider.select((s) => s.autenticata), (prima, ora) {
      if (prima != ora) unawaited(ref.read(consensiProvider.notifier).sincronizza());
    });

    final lingua = ref.watch(linguaProvider);
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'TAROTS chat',
      debugShowCheckedModeBanner: false,
      theme: temaApp(),
      routerConfig: router,
      locale: Locale(lingua),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: const [AppLocalizations.delegate, ...GlobalMaterialLocalizations.delegates],
      builder: (context, figlio) => Directionality(
        textDirection: versoDi(lingua),
        // Il testo di base del sito (`body`): senza, Flutter disegna il testo fuori da Material sottolineato.
        child: DefaultTextStyle(
          style: Stile.corpo,
          // La dimensione del testo scelta con A− / A+ (`componenti/dimensione_testo.dart`).
          child: ScalaTesto(
            child: OsservatoreApp(
              child: PrimoAvvio(
                child: AvvisoSessione(child: RitornoPagamento(child: figlio ?? const SizedBox.shrink())),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
