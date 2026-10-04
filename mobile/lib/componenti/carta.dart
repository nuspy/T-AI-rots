/// Le carte, come `frontend/v2/componenti/carta.tsx`:
/// - [ImmagineCarta]: l'immagine di una carta (o del dorso), 9:16, con lo spazio già riservato (niente salti mentre
///   arriva). Le immagini vengono dal sito (`/cards/<id>.webp`), le stesse che vede il browser;
/// - [CartaV2]: dorso, faccia e il giro fra i due (0,9 s), con il rovescio girato di 180°, il bagliore d'ottone della
///   carta che aspetta di essere girata, e il nome al posto dell'immagine se l'immagine manca;
/// - [MazzoAttivo]: la cartella delle immagini (`lib/mazzo-attivo.tsx` del sito): il Thoth sta in `/cards/`, gli altri
///   mazzi in `/cards/<slug>/`. Lo si mette attorno a una lettura fatta con un altro mazzo.
library;

import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config.dart';
import '../modelli/carta.dart';
import '../tema/tema.dart';
import 'premibile.dart';

/// Da dove vengono le immagini delle carte: il sito. I test le prendono da `frontend/public/cards/`.
final immagineCartaProvider = Provider<ImageProvider Function(String id)>(
  (ref) =>
      (id) => NetworkImage('${Config.sitoUrl}/cards/$id.webp'),
);

/// Il mazzo attivo: la sottocartella delle immagini (`null`: il Thoth, in `/cards/`).
class MazzoAttivo extends InheritedWidget {
  /// Il mazzo [slug] per le carte dentro [child].
  const MazzoAttivo({super.key, required this.slug, required super.child});

  /// La cartella del mazzo, o `null` per il predefinito.
  final String? slug;

  /// Il mazzo attivo sopra [context].
  static String? di(BuildContext context) => context.dependOnInheritedWidgetOfExactType<MazzoAttivo>()?.slug;

  @override
  bool updateShouldNotify(MazzoAttivo vecchio) => vecchio.slug != slug;
}

/// Il nome del file di una carta nel mazzo [slug] (`percorsoCarta()` del sito): `maj-06` o `<slug>/maj-06`. Anche il
/// dorso è quello del mazzo (`/cards/lovers/dorso.webp`), come `Dorso` del sito.
String percorsoCarta(String? slug, String id) => slug == null || slug.isEmpty ? id : '$slug/$id';

/// L'ombra delle carte: `box-shadow: 0 12px 22px rgba(32,16,38,.32)`.
const BoxShadow ombraCarta = BoxShadow(color: Color(0x52201026), offset: Offset(0, 12), blurRadius: 22);

/// L'immagine di una carta, 9:16.
class ImmagineCarta extends ConsumerWidget {
  /// La carta [id] (`maj-06`, `dorso`); [mazzo] sceglie un mazzo diverso da quello attivo (`''`: il Thoth).
  const ImmagineCarta(this.id, {super.key, this.alt = '', this.adatta = BoxFit.cover, this.mazzo});

  /// L'identificativo (il nome del file).
  final String id;

  /// Il testo alternativo (vuoto: decorativa).
  final String alt;

  /// Come riempire il riquadro.
  final BoxFit adatta;

  /// Un mazzo diverso da quello attivo (le pagine dei mazzi).
  final String? mazzo;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final immagine = Image(
      image: ref.watch(immagineCartaProvider)(percorsoCarta(mazzo ?? MazzoAttivo.di(context), id)),
      fit: adatta,
      excludeFromSemantics: alt.isEmpty,
      semanticLabel: alt.isEmpty ? null : alt,
      gaplessPlayback: true,
      errorBuilder: (context, errore, traccia) => const ColoredBox(color: Token.plum),
    );
    return AspectRatio(aspectRatio: 9 / 16, child: immagine);
  }
}

/// Una carta da girare.
class CartaV2 extends StatefulWidget {
  /// Una carta larga [larghezza].
  const CartaV2({
    super.key,
    required this.carta,
    required this.rivelata,
    required this.larghezza,
    required this.nome,
    this.rovescio = false,
    this.brilla = false,
    this.alTocco,
    this.etichetta,
  });

  /// La carta (assente: solo il dorso).
  final Carta? carta;

  /// Girata a faccia in su.
  final bool rivelata;

  /// La larghezza in px logici.
  final double larghezza;

  /// Il nome della carta nella lingua dell'interfaccia (testo alternativo e ripiego senza immagine).
  final String nome;

  /// Rovesciata.
  final bool rovescio;

  /// Il bagliore d'ottone della carta che aspetta.
  final bool brilla;

  /// Al tocco (girarla).
  final VoidCallback? alTocco;

  /// L'etichetta per i lettori di schermo.
  final String? etichetta;

  @override
  State<CartaV2> createState() => _CartaV2State();
}

class _CartaV2State extends State<CartaV2> with TickerProviderStateMixin {
  late final AnimationController _giro = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 900),
    value: _girata ? 1 : 0,
  );
  late final AnimationController _bagliore = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 2400),
  );

  bool get _girata => widget.rivelata && widget.carta != null;

  @override
  void initState() {
    super.initState();
    if (widget.brilla) _bagliore.repeat();
  }

  @override
  void didUpdateWidget(CartaV2 vecchia) {
    super.didUpdateWidget(vecchia);
    final ridotto = MediaQuery.disableAnimationsOf(context);
    if (_girata != (vecchia.rivelata && vecchia.carta != null)) {
      if (ridotto) {
        _giro.value = _girata ? 1 : 0;
      } else {
        _giro.animateTo(_girata ? 1 : 0, curve: const Cubic(.2, .7, .2, 1));
      }
    }
    if (widget.brilla && !_bagliore.isAnimating) _bagliore.repeat();
    if (!widget.brilla) _bagliore.stop();
  }

  @override
  void dispose() {
    _giro.dispose();
    _bagliore.dispose();
    super.dispose();
  }

  Widget _lato(Widget figlio, double anello, double alfa) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: widget.brilla ? Token.brassPale : Colori.cornice, width: 2),
        boxShadow: [
          ombraCarta,
          if (widget.brilla)
            BoxShadow(
              color: Token.brassPale.withValues(alpha: alfa),
              spreadRadius: anello,
            ),
        ],
      ),
      clipBehavior: Clip.hardEdge,
      child: figlio,
    );
  }

  @override
  Widget build(BuildContext context) {
    final ridotto = MediaQuery.disableAnimationsOf(context);
    final carta = widget.carta;
    final faccia = carta == null
        ? const SizedBox.shrink()
        : Transform.rotate(
            angle: widget.rovescio ? math.pi : 0,
            child: _Faccia(id: carta.id, nome: widget.nome, larghezza: widget.larghezza),
          );
    final contenuto = SizedBox(
      width: widget.larghezza,
      height: widget.larghezza * 16 / 9,
      child: AnimatedBuilder(
        animation: Listenable.merge([_giro, _bagliore]),
        builder: (context, _) {
          // `@keyframes bagliore`: l'anello d'ottone respira fra 2 e 5 px (fermo a 3 px col movimento ridotto).
          final t = ridotto ? .33 : (1 - math.cos(_bagliore.value * 2 * math.pi)) / 2;
          final anello = 2 + 3 * t;
          final alfa = .45 + .35 * t;
          final angolo = _giro.value * math.pi;
          final mostraFaccia = angolo > math.pi / 2;
          return Transform(
            alignment: Alignment.center,
            transform: Matrix4.identity()
              ..setEntry(3, 2, 1 / 1200)
              ..rotateY(angolo),
            child: mostraFaccia
                ? Transform(
                    alignment: Alignment.center,
                    transform: Matrix4.rotationY(math.pi),
                    child: _lato(faccia, anello, alfa),
                  )
                : _lato(const ImmagineCarta('dorso'), anello, alfa),
          );
        },
      ),
    );
    if (widget.alTocco == null) {
      return Semantics(label: widget.etichetta ?? (_girata ? widget.nome : null), image: true, child: contenuto);
    }
    return Premibile(
      alTocco: widget.alTocco,
      etichetta: widget.etichetta ?? widget.nome,
      costruisci: (context, premuto) => contenuto,
    );
  }
}

class _Faccia extends ConsumerWidget {
  const _Faccia({required this.id, required this.nome, required this.larghezza});

  final String id;
  final String nome;
  final double larghezza;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Image(
      image: ref.watch(immagineCartaProvider)(percorsoCarta(MazzoAttivo.di(context), id)),
      fit: BoxFit.cover,
      semanticLabel: nome,
      gaplessPlayback: true,
      // Se l'immagine manca resta il nome della carta: mai una carta vuota (`.testo` di carta.module.css).
      errorBuilder: (context, errore, traccia) => Container(
        color: Token.plum,
        alignment: Alignment.center,
        padding: const EdgeInsets.all(8),
        child: Text(
          nome,
          textAlign: TextAlign.center,
          style: Stile.serif(larghezza * .1, colore: const Color(0xFFFFF7E8)),
        ),
      ),
    );
  }
}
