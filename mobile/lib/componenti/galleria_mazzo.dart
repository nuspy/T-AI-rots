/// Le carte di un mazzo prima di comprarlo (`frontend/v2/componenti/galleria-mazzo.tsx`): le 78 miniature per gruppo
/// (Arcani maggiori, poi i quattro semi) in un dialogo largo; le pillole dei gruppi filtrano. Un tocco su una carta la
/// ingrandisce (`.deck-zoom`): un tocco sull'ingrandimento torna alle carte, le frecce ai lati (e quelle della
/// tastiera) passano alla precedente e alla successiva del gruppo mostrato; il titolo del dialogo diventa il nome della
/// carta.
///
/// Anche [ZoomCarte], l'ingrandimento con le frecce, serve ai campioni del voto (`campioni-voto.tsx`).
library;

import 'dart:math' as math;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/carta.dart';
import '../modelli/cassa.dart';
import '../tema/tema.dart';
import 'campi.dart';
import 'carta.dart';
import 'griglia.dart';
import 'modale.dart';
import 'pagina.dart' show messaggioErrore;
import 'premibile.dart';

/// I gruppi della galleria, nell'ordine del sito.
const List<String> gruppiGalleria = ['maggiori', 'bastoni', 'coppe', 'spade', 'dischi'];

String _gruppoDi(Carta c) => c.arcano == 'maggiore' ? 'maggiori' : (c.seme ?? 'maggiori');

/// Le 78 carte (nella lingua dei contenuti) per la galleria.
final carteGalleriaProvider = FutureProvider<List<Carta>>((ref) {
  final lingua = ref.watch(linguaProvider.select(linguaContenuti));
  return ref.read(apiProvider).carte(lingua);
});

/// Apre la galleria del [mazzo].
Future<void> apriGalleriaMazzo(BuildContext context, Mazzo mazzo) {
  return showGeneralDialog<void>(
    context: context,
    barrierDismissible: true,
    barrierLabel: context.t.comune_chiudi,
    barrierColor: const Color(0x00000000),
    transitionDuration: Token.durataTransizione,
    pageBuilder: (context, _, _) => GalleriaMazzo(mazzo: mazzo),
    transitionBuilder: (context, animazione, _, figlio) => FadeTransition(opacity: animazione, child: figlio),
  );
}

/// La galleria (il dialogo largo).
class GalleriaMazzo extends ConsumerStatefulWidget {
  /// La galleria del [mazzo].
  const GalleriaMazzo({super.key, required this.mazzo});

  /// Il mazzo.
  final Mazzo mazzo;

  @override
  ConsumerState<GalleriaMazzo> createState() => _GalleriaMazzoState();
}

class _GalleriaMazzoState extends ConsumerState<GalleriaMazzo> {
  String _filtro = 'tutte';
  int? _zoom;

  /// Le miniature, per riportare in vista l'ultima carta guardata quando si torna alla griglia.
  final Map<String, GlobalKey> _chiavi = {};
  String? _ultima;

  GlobalKey _chiave(String id) => _chiavi.putIfAbsent(id, GlobalKey.new);

  /// Dall'ingrandimento alla griglia (X, tocco fuori, «indietro», tocco sulla carta): la finestra resta aperta e la
  /// carta appena guardata torna in vista.
  void _tornaAlleCarte() {
    setState(() => _zoom = null);
    final id = _ultima;
    if (id == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ctx = _chiavi[id]?.currentContext;
      if (ctx != null && ctx.mounted) Scrollable.ensureVisible(ctx, alignment: .5);
    });
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final carte = ref.watch(carteGalleriaProvider);
    final elenco = [
      for (final c in carte.value ?? const <Carta>[])
        if (_filtro == 'tutte' || _gruppoDi(c) == _filtro) c,
    ];
    // Il Thoth vive in `/cards/`, gli altri mazzi in `/cards/<slug>/`.
    final cartella = widget.mazzo.predefinito ? '' : widget.mazzo.slug;
    final inZoom = _zoom != null && _zoom! < elenco.length ? elenco[_zoom!] : null;
    if (inZoom != null) _ultima = inZoom.id;
    final nomi = t.carteFiltri;
    final w = MediaQuery.sizeOf(context).width;

    final Widget corpo;
    if (inZoom != null) {
      corpo = ZoomCarte(
        totale: elenco.length,
        indice: _zoom!,
        alCambio: (i) => setState(() => _zoom = i),
        alChiudi: _tornaAlleCarte,
        etichettaChiudi: t.negozio_galleria_torna,
        carta: ImmagineCarta(inZoom.id, alt: inZoom.nomeIn(lingua), mazzo: cartella, adatta: BoxFit.contain),
      );
    } else {
      corpo = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (carte.hasError && !carte.hasValue) Errore(messaggioErrore(carte.error!, t), sopra: 0),
          if (!carte.hasValue && !carte.hasError) Text(t.comune_carica, style: stilePiccolo()),
          if (elenco.isNotEmpty)
            Text('${t.carte_n_carte(elenco.length)} · ${t.negozio_galleria_nota}', style: stilePiccolo()),
          // `.deck-gallery-jump`: le pillole dei gruppi (filtrano, non fanno scorrere).
          Padding(
            padding: const EdgeInsets.only(top: 12, bottom: 16),
            child: Semantics(
              label: t.negozio_galleria_gruppi,
              container: true,
              child: Pillole(
                children: [
                  for (final g in ['tutte', ...gruppiGalleria])
                    Pillola(
                      nomi[g] ?? g,
                      acceso: _filtro == g,
                      alTocco: () => setState(() {
                        _filtro = g;
                        _zoom = null;
                      }),
                    ),
                ],
              ),
            ),
          ),
          for (final g in gruppiGalleria)
            if (elenco.any((c) => _gruppoDi(c) == g))
              Semantics(
                container: true,
                label: nomi[g],
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 20, bottom: 9.6),
                      child: Text(nomi[g] ?? g, style: Stile.serif(18.4, colore: Token.plum)),
                    ),
                    _Miniature(
                      larga: !w.telefono,
                      children: [
                        for (final (i, c) in elenco.indexed)
                          if (_gruppoDi(c) == g)
                            Premibile(
                              key: _chiave(c.id),
                              alTocco: () => setState(() => _zoom = i),
                              etichetta: t.negozio_galleria_ingrandisci(c.nomeIn(lingua)),
                              costruisci: (context, premuto) => AnimatedContainer(
                                duration: const Duration(milliseconds: 150),
                                curve: Curves.ease,
                                transform: Matrix4.translationValues(0, premuto ? -2 : 0, 0),
                                decoration: BoxDecoration(
                                  color: Colori.cornice,
                                  border: Border.all(color: Token.line),
                                  boxShadow: premuto
                                      ? const [
                                          BoxShadow(color: Color(0x38201026), offset: Offset(0, 8), blurRadius: 18),
                                        ]
                                      : null,
                                ),
                                child: ImmagineCarta(c.id, mazzo: cartella),
                              ),
                            ),
                      ],
                    ),
                  ],
                ),
              ),
        ],
      );
    }

    // Il tasto «indietro» con una carta ingrandita torna alle carte, non chiude la finestra.
    return PopScope(
      canPop: inZoom == null,
      onPopInvokedWithResult: (fatto, _) {
        if (!fatto && _zoom != null) _tornaAlleCarte();
      },
      child: Focus(
        autofocus: true,
        onKeyEvent: (_, e) {
          if (_zoom == null || elenco.isEmpty || e is! KeyDownEvent) return KeyEventResult.ignored;
          if (e.logicalKey == LogicalKeyboardKey.arrowRight) {
            setState(() => _zoom = (_zoom! + 1) % elenco.length);
            return KeyEventResult.handled;
          }
          if (e.logicalKey == LogicalKeyboardKey.arrowLeft) {
            setState(() => _zoom = (_zoom! - 1 + elenco.length) % elenco.length);
            return KeyEventResult.handled;
          }
          return KeyEventResult.ignored;
        },
        child: FinestraModale(
          titolo: inZoom != null ? inZoom.nomeIn(lingua) : t.negozio_galleria_titolo(widget.mazzo.nome),
          larga: true,
          // Con una carta ingrandita la X e il tocco fuori tornano alle carte; dalla griglia chiudono la finestra.
          alChiudi: inZoom != null ? _tornaAlleCarte : () => Navigator.of(context).pop(),
          child: corpo,
        ),
      ),
    );
  }
}

/// `.deck-gallery`: `repeat(auto-fill, minmax(84px, 1fr))` con `gap: .6rem`; sul telefono 64 px e `.45rem`.
class _Miniature extends StatelessWidget {
  const _Miniature({required this.larga, required this.children});

  final bool larga;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final minimo = larga ? 84.0 : 64.0;
    final spazio = larga ? 9.6 : 7.2;
    return LayoutBuilder(
      builder: (context, vincoli) {
        final colonne = math.max(1, ((vincoli.maxWidth + spazio) / (minimo + spazio)).floor());
        return Griglia(
          colonne: colonne,
          spazioColonne: spazio,
          spazioRighe: spazio,
          allunga: false,
          children: children,
        );
      },
    );
  }
}

/// `.deck-zoom`: la carta grande al centro (`min(360px, 78vw)`, al più alta quanto la finestra meno 14rem) con le
/// frecce color melanzana ai lati (48 px, 44 fino a 560 px); un tocco sulla carta chiude l'ingrandimento.
class ZoomCarte extends StatelessWidget {
  /// L'ingrandimento della [carta] numero [indice] di [totale].
  const ZoomCarte({
    super.key,
    required this.totale,
    required this.indice,
    required this.alCambio,
    required this.alChiudi,
    required this.etichettaChiudi,
    required this.carta,
    this.didascalia,
  });

  /// Quante carte.
  final int totale;

  /// Quale.
  final int indice;

  /// Passa a un'altra.
  final ValueChanged<int> alCambio;

  /// Chiude l'ingrandimento.
  final VoidCallback alChiudi;

  /// L'etichetta del tocco sulla carta.
  final String etichettaChiudi;

  /// L'immagine.
  final Widget carta;

  /// La riga sotto (l'etichetta di un campione del voto).
  final String? didascalia;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final piccolo = w.piccolo;
    final lato = piccolo ? 44.0 : 48.0;
    final larghezza = math.min(360.0, w * .78);
    final altezzaMassima = math.max(160.0, media.size.height - 224);
    Widget freccia(String segno, String etichetta, int verso) => Premibile(
      alTocco: () => alCambio((indice + verso + totale) % totale),
      etichetta: etichetta,
      raggioFuoco: lato / 2,
      costruisci: (context, premuto) => Container(
        width: lato,
        height: lato,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: premuto ? Token.plumDeep : Token.plum,
          shape: BoxShape.circle,
          border: Border.all(color: const Color(0x8CD6B66D)),
          boxShadow: const [BoxShadow(color: Color(0x4D201026), offset: Offset(0, 6), blurRadius: 18)],
        ),
        child: Text(segno, style: Stile.sans(20.8, altezza: 1, colore: const Color(0xFFFFF7E8))),
      ),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            Padding(
              padding: EdgeInsets.symmetric(horizontal: piccolo ? 46.4 : 54.4),
              child: Center(
                child: Premibile(
                  alTocco: alChiudi,
                  etichetta: etichettaChiudi,
                  costruisci: (context, premuto) => ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: larghezza, maxHeight: altezzaMassima),
                    child: DecoratedBox(
                      decoration: const BoxDecoration(
                        boxShadow: [BoxShadow(color: Color(0x47201026), offset: Offset(0, 18), blurRadius: 36)],
                      ),
                      child: carta,
                    ),
                  ),
                ),
              ),
            ),
            if (totale > 1) ...[
              Positioned(left: 0, child: freccia('←', t.negozio_galleria_prec, -1)),
              Positioned(right: 0, child: freccia('→', t.negozio_galleria_succ, 1)),
            ],
          ],
        ),
        if (didascalia != null)
          Padding(
            padding: const EdgeInsets.only(top: 6.4),
            child: Text(didascalia!, textAlign: TextAlign.center, style: stilePiccolo()),
          ),
      ],
    );
  }
}

/// Un'immagine che riempie in larghezza mantenendo il 9:16 (per gli ingrandimenti dei campioni).
class ImmagineNoveSedici extends StatelessWidget {
  /// L'immagine [immagine].
  const ImmagineNoveSedici(this.immagine, {super.key, this.alt});

  /// La sorgente.
  final ImageProvider immagine;

  /// Il testo alternativo.
  final String? alt;

  @override
  Widget build(BuildContext context) => AspectRatio(
    aspectRatio: 9 / 16,
    child: Image(
      image: immagine,
      fit: BoxFit.contain,
      semanticLabel: alt,
      excludeFromSemantics: alt == null,
      errorBuilder: (context, e, s) => const ColoredBox(color: Token.paperDeep),
    ),
  );
}
