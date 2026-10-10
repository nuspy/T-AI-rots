/// Il router dell'app (`go_router`): **gli stessi percorsi del sito** (`frontend/v2/lib/percorsi.ts`, coi nomi delle
/// cartelle), così un collegamento al sito apre la stessa pagina nell'app e le statistiche coincidono.
///
/// - Un indirizzo pubblico che arriva da fuori (`/card-of-the-day`, `/it/carta-del-giorno`, i vecchi `/carte/x`) si
///   traduce nella rotta interna con `interno()` (lo stesso codice del proxy del sito, `indirizzi.dart`).
/// - A ogni cambio di rotta: la rotta corrente per la testata e i crediti, la pagina vista per lanterna (col
///   percorso che il sito manderebbe, `pubblico()`) e per Firebase.
/// - Un deep link dell'app (`chat.tarots.app://ritorno/…`, il ritorno da un pagamento) apre il suo percorso.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../analytics/firebase.dart';
import '../analytics/tracciato.dart';
import '../archivio.dart';
import '../cassa/pagamento.dart' show eRitornoApp;
import '../componenti/pagina.dart';
import '../dati/dati.dart' show impostazioniProvider;
import '../dati/inviti.dart';
import '../lettura/variante.dart';
import '../lingua/lingua.dart';
import '../pagine/blog.dart';
import '../pagine/carte.dart';
import '../pagine/condivisa.dart';
import '../pagine/elimina_account.dart';
import '../pagine/errori.dart';
import '../pagine/fisica.dart';
import '../pagine/giorno.dart';
import '../pagine/home.dart';
import '../pagine/lettura.dart';
import '../pagine/lettura_dettaglio.dart';
import '../pagine/mazzi.dart';
import '../pagine/negozio.dart';
import '../pagine/prezzi.dart';
import '../pagine/privacy.dart';
import '../pagine/profilo.dart';
import '../pagine/prova.dart';
import '../pagine/stese.dart';
import '../pagine/storia.dart';
import '../pagine/termini.dart';
import '../pagine/voto.dart';
import 'indirizzi.dart';
import 'percorsi.dart';
import 'percorso.dart';

/// Una rotta: la pagina costruita dallo stato (parametri del percorso e della query), senza transizione (nel sito
/// il cambio di pagina è istantaneo).
GoRoute _rotta(String percorso, Widget Function(GoRouterState stato) pagina) => GoRoute(
  path: percorso,
  pageBuilder: (context, stato) => NoTransitionPage(key: stato.pageKey, child: pagina(stato)),
);

String _p(GoRouterState stato, String nome) => stato.pathParameters[nome] ?? '';

/// Le rotte, nell'ordine di `R`.
List<RouteBase> rotte() => [
  ShellRoute(
    builder: (context, stato, figlio) => Guscio(child: figlio),
    routes: [
      _rotta(R.home, (_) => const Home()),
      // v9.5: `/read` smista (vedi `redirect`); la sua pagina resta solo come ripiego, la classica.
      _rotta(R.leggi, (s) => PaginaLettura(key: ValueKey(s.uri.toString()), parametri: s.uri.queryParameters)),
      _rotta(
        R.letturaChat,
        (s) => PaginaLettura(key: ValueKey(s.uri.toString()), parametri: s.uri.queryParameters, inChat: true),
      ),
      _rotta(
        R.letturaClassica,
        (s) => PaginaLettura(key: ValueKey(s.uri.toString()), parametri: s.uri.queryParameters),
      ),
      _rotta(R.fisica, (s) => LetturaFisica(parametri: s.uri.queryParameters)),
      _rotta(R.storia, (_) => const Storia()),
      _rotta('${R.storia}/:id', (s) => DettaglioLettura(id: _p(s, 'id'))),
      _rotta(R.condivise, (_) => const Errore404()),
      _rotta('${R.condivise}/:token', (s) => PaginaCondivisa(token: _p(s, 'token'))),
      _rotta(R.giorno, (_) => const Giorno()),
      _rotta(R.carte, (_) => const Carte()),
      _rotta('${R.carte}/:id', (s) => DettaglioCarta(id: _p(s, 'id'), parametri: s.uri.queryParameters)),
      _rotta(R.stese, (_) => const Stese()),
      _rotta('${R.stese}/:id', (s) => DettaglioStesa(id: _p(s, 'id'), parametri: s.uri.queryParameters)),
      _rotta(R.mazzi, (_) => const Mazzi()),
      _rotta('${R.mazzi}/:slug', (s) => DettaglioMazzo(slug: _p(s, 'slug'))),
      _rotta(R.voto, (_) => const Voto()),
      _rotta(R.negozio, (_) => const Negozio()),
      _rotta(R.carrello, (s) => PaginaCarrello(parametri: s.uri.queryParameters)),
      _rotta(R.prezzi, (s) => Prezzi(parametri: s.uri.queryParameters)),
      _rotta(R.prova, (s) => PaginaProva(parametri: s.uri.queryParameters)),
      _rotta(R.esplora, (_) => const Esplora()),
      _rotta(R.blog, (s) => Blog(parametri: s.uri.queryParameters)),
      _rotta('${R.blog}/sezione/:slug', (s) => BlogSezione(slug: _p(s, 'slug'), parametri: s.uri.queryParameters)),
      _rotta('${R.blog}/tag/:slug', (s) => BlogTag(slug: _p(s, 'slug'), parametri: s.uri.queryParameters)),
      _rotta('${R.blog}/:slug', (s) => Articolo(slug: _p(s, 'slug'))),
      _rotta(R.profilo, (s) => PaginaProfilo(parametri: s.uri.queryParameters)),
      _rotta(R.privacy, (_) => const PaginaPrivacy()),
      _rotta(R.termini, (_) => const PaginaTermini()),
      _rotta(R.elimina, (_) => const EliminaAccount()),
    ],
  ),
];

/// Un indirizzo che arriva da fuori → la rotta interna (`null`: è già una rotta). Un deep link dell'app
/// (`chat.tarots.app://ritorno/pricing?checkout=…`, il ritorno da un pagamento) diventa il suo percorso.
String? reindirizza(Uri uri) {
  final percorso = uri.path.isEmpty ? '/' : uri.path;
  if (eRitornoApp(uri)) {
    final verso = interno(percorso);
    return uri.hasQuery ? '$verso?${uri.query}' : verso;
  }
  final destinazione = interno(percorso);
  if (destinazione == percorso) return null;
  return uri.hasQuery ? '$destinazione?${uri.query}' : destinazione;
}

/// L'indirizzo della pagina che si vede. `RouteMatchList.uri` è quello della base: una pagina aperta con `push` (ogni
/// collegamento, `vai()`) sta dentro la shell come `ImperativeRouteMatch`, col suo indirizzo, e l'indirizzo della base
/// non cambia. Si scende fino all'ultima pagina, come la barra degli indirizzi del browser.
Uri uriVisibile(RouteMatchList lista) {
  var uri = lista.uri;
  RouteMatchBase? m = lista.matches.lastOrNull;
  while (m != null) {
    if (m is ImperativeRouteMatch) {
      uri = m.matches.uri;
      m = m.matches.matches.lastOrNull;
    } else if (m is ShellRouteMatch) {
      m = m.matches.lastOrNull;
    } else {
      break;
    }
  }
  return uri;
}

/// Il router dell'app.
final routerProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    initialLocation: R.home,
    routes: rotte(),
    redirect: (context, stato) {
      final verso = reindirizza(stato.uri);
      final percentuale = ref.read(impostazioniProvider).value?.letturaChatPercentuale ?? 90;
      // v9.5: `/read` sceglie la versione della lettura (prova 90/10), anche dopo la traduzione di un indirizzo.
      return smistaLettura(Uri.parse(verso ?? stato.uri.toString()), ref.read(archivioProvider), percentuale) ?? verso;
    },
    errorPageBuilder: (context, stato) => NoTransitionPage(
      key: stato.pageKey,
      child: const Guscio(child: Errore404()),
    ),
  );

  void cambiata() {
    final uri = uriVisibile(router.routerDelegate.currentConfiguration);
    // Un invito nell'indirizzo (`?invito=CODICE`) si ricorda fino alla registrazione, come la home del sito.
    final invito = uri.queryParameters['invito'];
    if (invito != null && invito.trim().isNotEmpty) unawaited(salvaInvito(ref.read(archivioProvider), invito));
    ref.read(percorsoProvider.notifier).cambia(Uri(path: uri.path.isEmpty ? '/' : uri.path));
    final visibile = pubblico(linguaPubblica(ref.read(linguaProvider)), uri.path.isEmpty ? '/' : uri.path);
    ref.read(lanternaProvider).pagina(visibile, utm: uri.queryParameters);
    unawaited(ref.read(statisticheGoogleProvider).schermata(visibile));
  }

  router.routerDelegate.addListener(cambiata);
  ref.onDispose(() {
    router.routerDelegate.removeListener(cambiata);
    router.dispose();
  });
  return router;
});
