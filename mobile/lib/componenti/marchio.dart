/// Il marchio del sito (`.brand`): il segno esagonale con la stella e «TAROTS *chat*».
library;

import 'package:flutter/widgets.dart';

import '../tema/tema.dart';

/// `.brand-mark`: un riquadro col bordo d'ottone chiaro ritagliato a esagono
/// (`clip-path: polygon(50% 0, 100% 18%, 100% 82%, 50% 100%, 0 82%, 0 18%)`). Il ritaglio taglia via i bordi in
/// alto e in basso: del bordo restano i due lati verticali, come nel browser. Dentro, «✦».
class SegnoMarchio extends StatelessWidget {
  /// Un segno largo [larghezza] e alto [altezza], con la stella a [px].
  const SegnoMarchio({super.key, required this.larghezza, required this.altezza, required this.px});

  /// Larghezza.
  final double larghezza;

  /// Altezza.
  final double altezza;

  /// La dimensione della stella.
  final double px;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: larghezza,
      height: altezza,
      child: CustomPaint(
        painter: const _Esagono(),
        child: Center(
          child: Text(
            '✦',
            textScaler: TextScaler.noScaling,
            style: Stile.serif(px, colore: Token.brassPale, altezza: 1),
          ),
        ),
      ),
    );
  }
}

class _Esagono extends CustomPainter {
  const _Esagono();

  @override
  void paint(Canvas canvas, Size s) {
    final ritaglio = Path()
      ..moveTo(s.width / 2, 0)
      ..lineTo(s.width, s.height * .18)
      ..lineTo(s.width, s.height * .82)
      ..lineTo(s.width / 2, s.height)
      ..lineTo(0, s.height * .82)
      ..lineTo(0, s.height * .18)
      ..close();
    canvas.save();
    canvas.clipPath(ritaglio);
    canvas.drawRect(
      (Offset.zero & s).deflate(.5),
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1
        ..color = Token.brassPale,
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(_Esagono vecchio) => false;
}

/// «TAROTS *chat*» (`.brand-name`, con `chat` in ottone chiaro).
class NomeMarchio extends StatelessWidget {
  /// Il nome a [px].
  const NomeMarchio({super.key, required this.px, this.colore = Colori.testataTesto});

  /// La dimensione del carattere.
  final double px;

  /// Il colore di «TAROTS».
  final Color colore;

  @override
  Widget build(BuildContext context) {
    final stile = Stile.serif(px, em: .04, colore: colore, altezza: 1.6);
    return Text.rich(
      TextSpan(
        style: stile,
        children: const [
          TextSpan(text: 'TAROTS '),
          TextSpan(
            text: 'chat',
            style: TextStyle(fontStyle: FontStyle.italic, color: Token.brassPale),
          ),
        ],
      ),
      maxLines: 1,
      softWrap: false,
    );
  }
}
