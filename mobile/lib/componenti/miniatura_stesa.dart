/// La stesa in miniatura (`frontend/v2/lettura/miniatura.tsx`): le sue posizioni vere, in scala, in ottone su prugna
/// (il fondo lo mette chi la usa, come `.spread-mini`); le posizioni calcolate in verderame. Il riquadro è 100×64.
library;

import 'dart:math' as math;

import 'package:flutter/widgets.dart';

import '../modelli/carta.dart';
import '../tema/tema.dart';

/// La miniatura di una stesa (decorativa: `aria-hidden`).
class MiniaturaStesa extends StatelessWidget {
  /// La miniatura della [stesa].
  const MiniaturaStesa({super.key, required this.stesa});

  /// La stesa.
  final Stesa stesa;

  @override
  Widget build(BuildContext context) => ExcludeSemantics(
    child: AspectRatio(aspectRatio: 100 / 64, child: CustomPaint(painter: _Miniatura(stesa))),
  );
}

class _Miniatura extends CustomPainter {
  _Miniatura(this.stesa);

  final Stesa stesa;

  @override
  void paint(Canvas canvas, Size size) {
    // `viewBox="0 0 100 64"`, adattato al riquadro (`preserveAspectRatio` predefinito: centrato, senza deformare).
    final scala = math.min(size.width / 100, size.height / 64);
    canvas.translate((size.width - 100 * scala) / 2, (size.height - 64 * scala) / 2);
    canvas.scale(scala);
    final w = stesa.posizioni.length > 8 ? 6.0 : 9.0;
    final h = w * 1.6;
    final bordo = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = .6
      ..color = Token.brassPale;
    for (final p in stesa.posizioni) {
      final cx = p.x * 100;
      final cy = p.y * 64;
      canvas.save();
      if (p.rotazione != 0) {
        canvas.translate(cx, cy);
        canvas.rotate(p.rotazione * math.pi / 180);
        canvas.translate(-cx, -cy);
      }
      final r = Rect.fromCenter(center: Offset(cx, cy), width: w, height: h);
      canvas.drawRect(r, Paint()..color = p.calcolata ? const Color(0x8C19706F) : const Color(0x47D6B66D));
      canvas.drawRect(r, bordo);
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(_Miniatura vecchia) => vecchia.stesa != stesa;
}
