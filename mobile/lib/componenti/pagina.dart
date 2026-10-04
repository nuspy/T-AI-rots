/// La struttura di ogni schermata, come il layout della v2 (`Pagina` di `frontend/v2/componenti/pagina.tsx`): la
/// testata in alto (ferma, come `position: sticky`), sotto la pagina che scorre — il banner della prova, il contenuto,
/// il piede — e in fondo la barra dell'oracolo (ferma, come `position: fixed`; la pagina le lascia il suo spazio come
/// con `--oracolo-h`). Dietro, lo sfondo del sito (`body::before`: due aloni, d'ottone in alto a sinistra e di
/// verderame a destra, fermi mentre la pagina scorre). La tastiera spinge in su pagina e barra, mai la testata.
library;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/errori.dart';
import '../l10n/testi.dart';
import '../rotte/percorso.dart';
import '../tema/tema.dart';
import 'banner_prova.dart';
import 'campi.dart' show Errore;
import 'oracolo.dart';
import 'piede.dart';
import 'testata.dart';

/// Lo sfondo del sito.
class Sfondo extends StatelessWidget {
  /// Dietro [child].
  const Sfondo({super.key, required this.child});

  /// Il contenuto.
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final dimensione = MediaQuery.sizeOf(context);
    final lato = dimensione.shortestSide == 0 ? 1.0 : dimensione.shortestSide;
    // `radial-gradient(circle at 15% 5%, rgba(178,131,54,.12), transparent 22rem)` e
    // `radial-gradient(circle at 85% 35%, rgba(25,112,111,.1), transparent 24rem)`, il tutto a `opacity: .6`.
    return Stack(
      children: [
        const Positioned.fill(child: ColoredBox(color: Token.paper)),
        Positioned.fill(
          child: Opacity(
            opacity: .6,
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(-.7, -.9),
                  radius: 352 / lato,
                  colors: const [Color(0x1FB28336), Color(0x00B28336)],
                ),
              ),
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: RadialGradient(
                    center: const Alignment(.7, -.3),
                    radius: 384 / lato,
                    colors: const [Color(0x1A19706F), Color(0x0019706F)],
                  ),
                ),
              ),
            ),
          ),
        ),
        Positioned.fill(child: child),
      ],
    );
  }
}

/// Il guscio di tutte le schermate: testata, pagina e barra dell'oracolo.
class Guscio extends ConsumerWidget {
  /// Attorno alla pagina [child] (quella della rotta).
  const Guscio({super.key, required this.child});

  /// La pagina.
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final media = MediaQuery.of(context);
    final conOracolo = oracoloVisibile(ref.watch(percorsoProvider).path);
    return AnnotatedRegion<SystemUiOverlayStyle>(
      // La testata è scura: icone chiare nella barra di stato.
      value: SystemUiOverlayStyle.light.copyWith(
        statusBarColor: const Color(0x00000000),
        systemNavigationBarColor: Token.plumDeep,
      ),
      child: Sfondo(
        child: Padding(
          padding: EdgeInsets.only(bottom: media.viewInsets.bottom),
          child: MediaQuery.removeViewInsets(
            context: context,
            removeBottom: true,
            child: Column(
              children: [
                // Ferma mentre la pagina scorre: si ridisegna per conto suo.
                const RepaintBoundary(child: Testata()),
                Expanded(
                  child: MediaQuery.removePadding(
                    context: context,
                    removeTop: true,
                    // Sopra la barra dell'oracolo la safe area in basso è sua: il piede non la conta due volte.
                    removeBottom: conOracolo,
                    child: child,
                  ),
                ),
                const RepaintBoundary(child: Oracolo()),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Una pagina: il banner della prova, le sezioni una sotto l'altra, poi il piede; scorre sotto la testata.
class Pagina extends StatelessWidget {
  /// Una pagina con le [sezioni].
  const Pagina({super.key, required this.sezioni, this.controllore});

  /// Le sezioni, a tutta larghezza.
  final List<Widget> sezioni;

  /// Lo scorrimento (per tornare in cima o per i test).
  final ScrollController? controllore;

  @override
  Widget build(BuildContext context) {
    return DefaultTextStyle(
      style: Stile.corpo,
      child: SingleChildScrollView(
        controller: controllore,
        primary: controllore == null,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [const BannerProva(), ...sezioni, const Piede()],
        ),
      ),
    );
  }
}

/// Una fascia (`.band`): larga al massimo 1200 px, centrata, con il margine laterale del sito (`--gutter`) e
/// l'imbottitura verticale della fascia (`clamp(1.6rem, 3.15vw, 2.8rem)`, 1rem sul telefono; `.band-tight` più
/// stretta). [stretta] è `.band-narrow` (860 px).
class Fascia extends StatelessWidget {
  /// Una fascia.
  const Fascia({super.key, required this.child, this.stretta = false, this.compatta = false, this.colore});

  /// Il contenuto.
  final Widget child;

  /// `.band-narrow`.
  final bool stretta;

  /// `.band-tight`.
  final bool compatta;

  /// Lo sfondo della sezione che la contiene (a tutta larghezza).
  final Color? colore;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final verticale = w.telefono ? 16.0 : (compatta ? w.clampVw(16, 1.75, 22.4) : w.clampVw(25.6, 3.15, 44.8));
    final fascia = Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: stretta ? 860 : Token.larghezzaBanda),
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: w.gutter, vertical: verticale),
          child: child,
        ),
      ),
    );
    return colore == null ? fascia : ColoredBox(color: colore!, child: fascia);
  }
}

/// Il messaggio di un errore per chi usa l'app: il motivo del server, o quello generico (`useCarica` del sito).
String messaggioErrore(Object e, AppLocalizations t) => e is ErroreApi ? e.messaggio(t) : t.comune_err_generico;

/// Una fascia che dice «Caricamento…» (`.muted`) o l'errore (`.error`), mentre i dati della pagina non ci sono.
class StatoFascia extends StatelessWidget {
  /// Il caricamento, o l'[errore] se c'è.
  const StatoFascia({super.key, this.errore, this.compatta = true});

  /// L'errore (assente: si sta caricando).
  final Object? errore;

  /// `.band-tight`.
  final bool compatta;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final e = errore;
    return Fascia(
      compatta: compatta,
      child: e == null
          ? Semantics(
              liveRegion: true,
              child: Text(t.comune_carica, style: Stile.sans(16, colore: Token.inkSoft, altezza: 1.6)),
            )
          : Errore(messaggioErrore(e, t)),
    );
  }
}
