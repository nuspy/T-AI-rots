/// Le icone della testata: gli stessi tracciati SVG del sito (`ICONE` e `ICONE_MENU` in
/// `frontend/v2/componenti/testata.tsx`), 24×24, a tratto, col colore del testo. Si disegnano direttamente
/// (`path_parsing`), senza caricamenti asincroni: l'icona c'è dal primo fotogramma.
library;

import 'package:flutter/widgets.dart';
import 'package:path_parsing/path_parsing.dart';

/// I tracciati delle icone delle azioni (carrello, crediti, profilo, entra).
abstract final class Icone {
  /// Il carrello.
  static const String carrello =
      'M3 4h2l2.2 10.2a1.5 1.5 0 0 0 1.5 1.2h8.6a1.5 1.5 0 0 0 1.5-1.1L21 8H6.2M9.5 20a1 1 0 1 0 0-.01M17.5 20a1 1 0 1 0 0-.01';

  /// I crediti.
  static const String crediti =
      'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM12 7.5l1.3 2.9 3.2.3-2.4 2.1.7 3.1L12 14.3l-2.8 1.6.7-3.1-2.4-2.1 3.2-.3Z';

  /// Il profilo.
  static const String profilo = 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4.5 20.5c.9-3.6 3.9-5.5 7.5-5.5s6.6 1.9 7.5 5.5';

  /// Entra.
  static const String entra = 'M10 17l5-5-5-5M15 12H3M14 4h5a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-5';

  /// La lingua (un globo: sulla testata del telefono, sopra il codice «IT»).
  static const String lingua =
      'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM3.5 9h17M3.5 15h17M12 3c-2.4 2.5-3.6 5.5-3.6 9s1.2 6.5 3.6 9M12 3c2.4 2.5 3.6 5.5 3.6 9s-1.2 6.5-3.6 9';
}

/// Le sezioni del menu.
enum Voce { leggi, fisica, giorno, diario, esplora, storia, negozio }

/// I tracciati delle icone del menu, che sul telefono prendono il posto delle scritte.
const Map<Voce, String> iconeMenu = {
  Voce.leggi: 'M7 3h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2ZM11 7.5l1.1 2.2 2.4.4-1.7 1.7.4 2.4-2.2-1.2-2.2 1.2.4-2.4-1.7-1.7 2.4-.4Z',
  Voce.fisica: 'M3.5 8 10 4.5l5.5 11.5-6.5 3.5ZM13.5 4.5l6 2.5-4 10.5',
  Voce.giorno: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8ZM12 2.5v2M12 19.5v2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M2.5 12h2M19.5 12h2M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4',
  Voce.diario: 'M5 4h9a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3V4ZM5 17a3 3 0 0 1 3-3h9M9 8h5',
  Voce.esplora: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18ZM15.5 8.5l-2 5-5 2 2-5Z',
  Voce.storia: 'M3.5 12a8.5 8.5 0 1 0 2.6-6.1M3 4v4h4M12 7.5V12l3 2',
  Voce.negozio: 'M6 8h12l-1 12H7L6 8ZM9 8V6.5a3 3 0 0 1 6 0V8',
};

/// I tracciati già letti.
final Map<String, Path> _tracciati = {};

class _Scrittore implements PathProxy {
  _Scrittore(this.path);

  final Path path;

  @override
  void moveTo(double x, double y) => path.moveTo(x, y);

  @override
  void lineTo(double x, double y) => path.lineTo(x, y);

  @override
  void cubicTo(double x1, double y1, double x2, double y2, double x3, double y3) =>
      path.cubicTo(x1, y1, x2, y2, x3, y3);

  @override
  void close() => path.close();
}

/// Il tracciato [d] come `Path` nel riquadro 24×24 (letto una volta sola).
Path tracciato(String d) => _tracciati.putIfAbsent(d, () {
  final p = Path();
  writeSvgPathDataToPath(d, _Scrittore(p));
  return p;
});

/// Un'icona a tratto: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
/// stroke-linecap="round" stroke-linejoin="round">`.
class IconaTratto extends StatelessWidget {
  /// Il tracciato [d], largo e alto [misura], del [colore] del testo.
  const IconaTratto(this.d, {super.key, required this.misura, required this.colore});

  /// Il tracciato SVG.
  final String d;

  /// Lato in px logici.
  final double misura;

  /// Il colore del tratto.
  final Color colore;

  @override
  Widget build(BuildContext context) {
    return ExcludeSemantics(
      child: CustomPaint(size: Size.square(misura), painter: _PittoreTratto(tracciato(d), colore)),
    );
  }
}

class _PittoreTratto extends CustomPainter {
  _PittoreTratto(this.path, this.colore);

  final Path path;
  final Color colore;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(size.width / 24);
    canvas.drawPath(
      path,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.7
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round
        ..color = colore,
    );
  }

  @override
  bool shouldRepaint(_PittoreTratto vecchio) => vecchio.path != path || vecchio.colore != colore;
}
