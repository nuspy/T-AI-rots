/// Il bigliettino d'invito (`componiBigliettinoV2` di `frontend/v2/lettura/immagine-condivisione.ts`): un PNG 1000×700
/// disegnato sul telefono (fondo prugna, anelli d'ottone, il marchio, il motto, l'omaggio, il codice in un riquadro
/// chiaro, il dominio), da salvare o condividere col foglio del telefono. Nessun server: come nel sito.
library;

import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/painting.dart';

import '../tema/tema.dart';

/// Le misure del bigliettino.
const ui.Size misuraBigliettino = ui.Size(1000, 700);

const Color _prugna = Color(0xFF3C1846);
const Color _prugnaScuro = Color(0xFF201026);
const Color _ottone = Color(0xFFB28336);
const Color _ottoneChiaro = Color(0xFFD6B66D);
const Color _carta = Color(0xFFF4EFE5);

/// Il dominio scritto in fondo.
const String dominioBigliettino = 'tarots.chat';

TextPainter _testo(
  String testo,
  TextStyle stile, {
  double? larghezza,
  int? righe,
  TextAlign allinea = TextAlign.center,
}) => TextPainter(
  text: TextSpan(text: testo, style: stile),
  textDirection: TextDirection.ltr,
  textAlign: allinea,
  maxLines: righe,
  ellipsis: righe == null ? null : '…',
)..layout(maxWidth: larghezza ?? double.infinity);

/// Disegna il testo [p] centrato in [x], con la linea di base in [y] (`fillText` del canvas).
void _centrato(Canvas g, TextPainter p, double x, double y) {
  final base = p.computeDistanceToActualBaseline(TextBaseline.alphabetic);
  p.paint(g, Offset(x - p.width / 2, y - base));
}

/// Il fondo prugna, più chiaro a sinistra del centro, e la cornice d'ottone sottile.
void _fondo(Canvas g, double w, double h) {
  final centro = Offset(w * .5, h * .5);
  final raggio = math.max(w, h) * .75;
  g.drawRect(
    Offset.zero & ui.Size(w, h),
    Paint()
      ..shader = ui.Gradient.radial(
        centro,
        raggio,
        const [Color(0xFF572064), _prugna, _prugnaScuro],
        const [0, .55, 1],
        TileMode.clamp,
        null,
        Offset(w * .34, h * .5),
        30,
      ),
  );
  final m = (math.min(w, h) * .035).roundToDouble();
  g.drawRect(
    Rect.fromLTWH(m, m, w - 2 * m, h - 2 * m),
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5
      ..color = const Color(0xBFD6B66D),
  );
}

/// Il motivo ad anello del tavolo del rito.
void _anelli(Canvas g, double cx, double cy, double raggio) {
  for (var i = 0; i < 5; i++) {
    g.drawCircle(
      Offset(cx, cy),
      raggio * (.42 + i * .16),
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = i == 0 ? 1.6 : 1
        ..color = _ottoneChiaro.withValues(alpha: .22 - i * .035),
    );
  }
}

/// Il marchio: la losanga col «✦», «TAROTS» e «chat» in corsivo d'ottone, centrato in [x] con la base in [y].
void _marchio(Canvas g, double x, double y, double d) {
  final tarots = _testo('TAROTS ', TextStyle(fontFamily: Token.serif.first, fontSize: d, color: _carta));
  final chat = _testo(
    'chat',
    TextStyle(fontFamily: Token.serif.first, fontSize: d, fontStyle: FontStyle.italic, color: _ottoneChiaro),
  );
  final segno = d * 1.1;
  final totale = segno + d * .5 + tarots.width + chat.width;
  final x0 = x - totale / 2;
  final cy = y - d * .35;
  final hx = segno * .42;
  final hy = segno * .55;
  final c = x0 + segno / 2;
  final losanga = Path()
    ..moveTo(c, cy - hy)
    ..lineTo(c + hx, cy - hy * .64)
    ..lineTo(c + hx, cy + hy * .64)
    ..lineTo(c, cy + hy)
    ..lineTo(c - hx, cy + hy * .64)
    ..lineTo(c - hx, cy - hy * .64)
    ..close();
  g.drawPath(
    losanga,
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.4
      ..color = _ottoneChiaro,
  );
  final stella = _testo('✦', TextStyle(fontFamily: Token.serif.first, fontSize: d * .62, color: _ottoneChiaro));
  stella.paint(g, Offset(c - stella.width / 2, cy + 1 - stella.height / 2));
  final base = tarots.computeDistanceToActualBaseline(TextBaseline.alphabetic);
  tarots.paint(g, Offset(x0 + segno + d * .5, y - base));
  chat.paint(g, Offset(x0 + segno + d * .5 + tarots.width, y - base));
}

/// Il bigliettino col [codice], il motto [claim] e l'[omaggio] («5 letture in regalo»), in PNG.
Future<Uint8List?> componiBigliettino(String codice, String claim, String omaggio) async {
  final w = misuraBigliettino.width;
  final h = misuraBigliettino.height;
  final registro = ui.PictureRecorder();
  final g = Canvas(registro);
  _fondo(g, w, h);
  _anelli(g, w / 2, h / 2, h * .62);
  _marchio(g, w / 2, 132, 40);

  // Il motto: due righe al massimo, larghe 760, ogni 42 px (la prima base a 250).
  final motto = _testo(
    claim,
    TextStyle(
      fontFamily: Token.serif.first,
      fontSize: 32,
      fontStyle: FontStyle.italic,
      color: _carta,
      height: 42 / 32,
      leadingDistribution: TextLeadingDistribution.even,
    ),
    larghezza: w - 240,
    righe: 2,
  );
  final primaBase = motto.computeDistanceToActualBaseline(TextBaseline.alphabetic);
  motto.paint(g, Offset((w - motto.width) / 2, 250 - primaBase));

  _centrato(
    g,
    _testo(
      omaggio,
      TextStyle(fontFamily: Token.sans.first, fontSize: 30, fontWeight: FontWeight.w600, color: _ottoneChiaro),
    ),
    w / 2,
    380,
  );

  const tw = 440.0;
  final riquadro = RRect.fromRectAndRadius(Rect.fromLTWH(w / 2 - tw / 2, 430, tw, 104), const Radius.circular(4));
  g.drawRRect(riquadro, Paint()..color = _carta);
  g.drawRRect(
    riquadro,
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3
      ..color = _ottone,
  );
  _centrato(
    g,
    _testo(codice, TextStyle(fontFamily: Token.sans.first, fontSize: 50, fontWeight: FontWeight.w700, color: _prugna)),
    w / 2,
    500,
  );
  _centrato(
    g,
    _testo(
      dominioBigliettino,
      TextStyle(fontFamily: Token.sans.first, fontSize: 24, fontWeight: FontWeight.w600, color: _ottoneChiaro),
    ),
    w / 2,
    h - 64,
  );
  final immagine = await registro.endRecording().toImage(w.toInt(), h.toInt());
  final dati = await immagine.toByteData(format: ui.ImageByteFormat.png);
  immagine.dispose();
  return dati?.buffer.asUint8List();
}
