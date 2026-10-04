/// L'immagine di una lettura condivisa (`frontend/v2/lettura/immagine-condivisione.ts`): 800×600 disegnati
/// nell'app, mandati in PNG (`PUT /me/readings/{id}/share-image`), ridotti dal server a un WebP 400×300 che è l'anteprima
/// nei social. Contiene solo ciò che la pagina pubblica mostra già (`LetturaCondivisa`): le carte uscite nelle loro
/// posizioni sul fondo prugna col motivo ad anello del tavolo del rito, il marchio, il nome della stesa, le parole di
/// chi condivide, il simbolo al posto del nome dell'altra persona, la domanda, una sintesi del responso, l'indirizzo.
///
/// Il disegno è un [CustomPainter] ([PittoreCondivisione]): lo stesso pittore va in un widget dietro un
/// `RepaintBoundary` ([ImmagineCondivisione], per vederlo) e su una tela fuori dallo schermo per il PNG
/// ([componiImmagine]), così il file non dipende da un fotogramma a schermo. Misure, colori, caratteri e geometria
/// sono quelli del sito, punto per punto.
///
/// Qui stanno anche i nomi di carte, stese e posizioni nella lingua della lettura (`lib/i18n/nomi.ts`) e la sintesi
/// breve del responso (`lib/sintesi.ts`), che servono anche alle altre pagine della storia.
library;

import 'dart:async';
import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/widgets.dart';

import '../componenti/icone.dart' show tracciato;
import '../config.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../modelli/carta.dart';

/// Ciò che si disegna (il doppio di ciò che si pubblica).
const Size misuraImmagine = Size(800, 600);

/// Ciò che il server salva e restituisce.
const Size misuraFinale = Size(400, 300);

/* La tavolozza della v2. */
const Color _prugna = Color(0xFF3C1846);
const Color _prugnaScuro = Color(0xFF201026);
const Color _ottone = Color(0xFFB28336);
const Color _ottoneChiaro = Color(0xFFD6B66D);
const Color _carta = Color(0xFFF4EFE5);
const Color _corniceCarta = Color(0xFFF5E6BF);
const Color _tenue = Color(0xFFD9CADE);

const List<String> _serif = ['Georgia', 'serif'];
const List<String> _sans = ['Arial', 'sans-serif'];

/// Il dominio del sito pubblico (`DOMINIO` del sito).
String get dominio => Uri.tryParse(Config.sitoPubblico)?.host ?? 'tarots.chat';

/* ---- i nomi nella lingua della lettura (`lib/i18n/nomi.ts`) ------------------------------------------------------- */

/// Il nome di una carta (`nomeCarta`): l'italiano dai campi originali, le altre lingue da `nomi`, poi l'inglese.
String nomeCartaIn(Carta carta, String lingua) {
  if (lingua == 'it') return carta.nomeIt;
  return carta.nomi[lingua] ?? carta.nomi['en'] ?? carta.nomeThoth;
}

/// Il nome di una stesa (`nomeStesa`).
String nomeStesaIn(Stesa stesa, String lingua) {
  if (lingua == 'it') return stesa.nome;
  return stesa.nomi?[lingua] ?? stesa.nomi?['en'] ?? stesa.nomeEn;
}

/// Il nome di una stesa dai soli campi dello storico (`nomeStesaDaNomi`).
String nomeStesaDaNomi(String nome, Map<String, String> nomi, String lingua) {
  if (lingua == 'it') return nome;
  return nomi[lingua] ?? nomi['en'] ?? nome;
}

/// Il nome di una posizione (`nomePosizione`).
String nomePosizioneIn(Posizione posizione, String lingua) {
  if (lingua == 'it') return posizione.nome;
  return posizione.nomi?[lingua] ?? posizione.nomi?['en'] ?? posizione.nomeEn;
}

/// La lingua dei nomi di una lettura: quella del quesito, se l'app la conosce, altrimenti quella dell'interfaccia.
String linguaLettura(String? lang, String interfaccia) => comeLingua(lang) ?? interfaccia;

/* ---- la sintesi breve del responso (`lib/sintesi.ts`) -------------------------------------------------------------- */

/// Le prime frasi della sezione finale del responso, senza la formattazione Markdown, entro [massimo] caratteri.
String sintesiDelResponso(String? responso, int massimo) {
  if (responso == null || responso.isEmpty) return '';
  final sezioni = responso.split(RegExp(r'^##\s+', multiLine: true));
  final corpo = sezioni.length > 1 ? sezioni.last.split('\n').skip(1).join('\n') : responso;
  final pulito = corpo
      .replaceAll(RegExp(r'^\s*[-*+>]\s+', multiLine: true), '')
      .replaceAllMapped(RegExp(r'\[([^\]]+)\]\([^)]*\)'), (m) => m[1]!)
      .replaceAll(RegExp(r'[#*_`~]'), '')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();
  if (pulito.isEmpty) return '';
  final frasi = pulito.split(RegExp(r'(?<=[.!?。！？…])\s+')).where((f) => f.isNotEmpty);
  var sintesi = '';
  for (final f in frasi) {
    final prova = sintesi.isEmpty ? f : '$sintesi $f';
    if (prova.length > massimo) break;
    sintesi = prova;
  }
  if (sintesi.isNotEmpty) return sintesi;
  final tagliata = pulito.substring(0, math.min(massimo, pulito.length));
  final spazio = tagliata.lastIndexOf(' ');
  final fine = math.max(spazio, (massimo * .6).floor()).clamp(0, tagliata.length);
  return '${tagliata.substring(0, fine).trimRight()}…';
}

/* ---- i simboli dell'altra persona (`lib/simboli.ts`) ---------------------------------------------------------------- */

/// Il lato del quadrato su cui sono tracciati i simboli.
const double latoSimbolo = 64;

String _cerchio(double cx, double cy, double r) =>
    'M ${cx + r} $cy A $r $r 0 1 0 ${cx - r} $cy A $r $r 0 1 0 ${cx + r} $cy';

/// I tracciati dei simboli: Venere, Marte, Mercurio per donna, uomo e non binario; la stella per gli altri.
final Map<String, String> percorsiSimboli = {
  'venere': '${_cerchio(32, 22, 14)} M 32 36 L 32 58 M 22 48 L 42 48',
  'marte': '${_cerchio(26, 38, 14)} M 36 28 L 54 10 M 40 10 L 54 10 L 54 24',
  'mercurio': '${_cerchio(32, 34, 11)} M 23 14 A 9 9 0 0 0 41 14 M 32 45 L 32 62 M 24 54 L 40 54',
  'stella': 'M 32 4 L 38 26 L 60 32 L 38 38 L 32 60 L 26 38 L 4 32 L 26 26 Z',
};

/// Il simbolo per il nome che manda il server (`simboloDi`).
String simboloDi(String? nome) => nome == 'venere' || nome == 'marte' || nome == 'mercurio' ? nome! : 'stella';

/// Il simbolo dell'altra persona, a solo contorno d'ottone (la stella anche piena, appena).
class SimboloPartner extends StatelessWidget {
  /// Il simbolo [nome], largo [lato].
  const SimboloPartner({super.key, required this.nome, this.lato = 28, this.tratto = 3.2});

  /// `venere`, `marte`, `mercurio`, altro (stella).
  final String? nome;

  /// Il lato.
  final double lato;

  /// Lo spessore del tratto nel quadrato di 64.
  final double tratto;

  @override
  Widget build(BuildContext context) => ExcludeSemantics(
    child: CustomPaint(size: Size.square(lato), painter: _PittoreSimbolo(simboloDi(nome), tratto)),
  );
}

class _PittoreSimbolo extends CustomPainter {
  _PittoreSimbolo(this.simbolo, this.tratto);

  final String simbolo;
  final double tratto;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(size.width / latoSimbolo);
    canvas.drawPath(
      tracciato(percorsiSimboli[simbolo]!),
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = tratto
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round
        ..color = _ottoneChiaro,
    );
  }

  @override
  bool shouldRepaint(_PittoreSimbolo vecchio) => vecchio.simbolo != simbolo;
}

/* ---- la geometria del tavolo (`lib/geometria-tavolo.ts`) ---------------------------------------------------------- */

/// La larghezza di una carta come frazione del tavolo: nei dati della stesa, 0,1 se manca.
double _larghezzaBase(Stesa stesa) => stesa.larghezza ?? .1;

/// Le carte sono il 20% più grandi rispetto al tavolo, coi centri dove stavano.
const double _scalaCarte = 1.2;

/* ---- gli strumenti di disegno ------------------------------------------------------------------------------------- */

/// Un testo su una riga, con la linea di base a [y] e l'allineamento [allinea] rispetto a [x].
void _scrivi(Canvas g, String testo, TextStyle stile, double x, double y, {TextAlign allinea = TextAlign.left}) {
  final p = TextPainter(
    text: TextSpan(text: testo, style: stile),
    textDirection: TextDirection.ltr,
    maxLines: 1,
  )..layout();
  final base = p.computeDistanceToActualBaseline(TextBaseline.alphabetic);
  final dx = switch (allinea) {
    TextAlign.center => x - p.width / 2,
    TextAlign.right => x - p.width,
    _ => x,
  };
  p.paint(g, Offset(dx, y - base));
  p.dispose();
}

/// Un testo a capo entro [larghezza], al più [massimo] righe (l'ultima coi puntini se il testo continua), con la
/// prima linea di base a [y] e [riga] fra una linea e l'altra (`paragrafo` del sito). Restituisce la quota sotto
/// l'ultima riga.
double _paragrafo(
  Canvas g,
  String testo,
  TextStyle stile,
  double x,
  double y,
  double larghezza,
  double riga,
  int massimo, {
  TextDirection verso = TextDirection.ltr,
}) {
  if (testo.isEmpty) return y;
  final p = TextPainter(
    text: TextSpan(
      text: testo,
      style: stile.copyWith(height: riga / (stile.fontSize ?? 16)),
    ),
    textDirection: verso,
    maxLines: massimo,
    ellipsis: '…',
  )..layout(maxWidth: larghezza);
  final righe = p.computeLineMetrics();
  if (righe.isEmpty) {
    p.dispose();
    return y;
  }
  p.paint(g, Offset(x, y - righe.first.baseline));
  p.dispose();
  return y + righe.length * riga;
}

RRect _rettangolo(double x, double y, double w, double h, double r) =>
    RRect.fromRectAndRadius(Rect.fromLTWH(x, y, w, h), Radius.circular(r));

/// Il fondo prugna, più chiaro a sinistra del centro, e la cornice d'ottone sottile.
void _fondo(Canvas g, double w, double h) {
  final sfumatura = ui.Gradient.radial(
    Offset(w * .5, h * .5),
    math.max(w, h) * .75,
    const [Color(0xFF572064), _prugna, _prugnaScuro],
    const [0, .55, 1],
    TileMode.clamp,
    null,
    Offset(w * .34, h * .5),
    30,
  );
  g.drawRect(Rect.fromLTWH(0, 0, w, h), Paint()..shader = sfumatura);
  final m = (math.min(w, h) * .035).roundToDouble();
  g.drawRect(
    Rect.fromLTWH(m, m, w - 2 * m, h - 2 * m),
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5
      ..color = const Color(0xBFD6B66D),
  );
}

/// Il motivo ad anello del tavolo del rito: cerchi concentrici d'ottone, appena accennati.
void _anelli(Canvas g, Offset centro, double raggio) {
  for (var i = 0; i < 5; i++) {
    g.drawCircle(
      centro,
      raggio * (.42 + i * .16),
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = i == 0 ? 1.6 : 1
        ..color = _ottoneChiaro.withValues(alpha: .22 - i * .035),
    );
  }
}

/// Le carte uscite nelle loro posizioni, ritagliate sul loro ingombro e scalate per entrare in [scatola] (al più
/// [cartaMax] px di larghezza), con la cornice chiara, l'ombra e il numero della posizione d'ottone. Si usa anche per
/// la stampa in PDF (il tavolo della lettura sul foglio).
void disegnaTavolo(
  Canvas g,
  Stesa stesa,
  List<CartaPosata> carte,
  Rect scatola,
  double cartaMax,
  Map<int, ui.Image?> immagini,
  String lingua, {
  bool anelli = true,
}) {
  final posate = carte.where((c) => c.carta != null).toList();
  final quadrato = stesa.forma == 'quadrata';
  const th = 600.0;
  final tw = quadrato ? th : th * 16 / 12;
  final lc = tw * _larghezzaBase(stesa) * _scalaCarte;
  final ac = lc * 16 / 9;
  const margine = 20.0;
  var minX = double.infinity, minY = double.infinity, maxX = -double.infinity, maxY = -double.infinity;
  Posizione? posizioneDi(CartaPosata c) => stesa.posizioni.where((q) => q.n == c.posizione).firstOrNull;
  for (final c in posate) {
    final pos = posizioneDi(c);
    if (pos == null) continue;
    final a = pos.rotazione * math.pi / 180;
    final mx = (math.cos(a).abs() * lc + math.sin(a).abs() * ac) / 2;
    final my = (math.sin(a).abs() * lc + math.cos(a).abs() * ac) / 2;
    minX = math.min(minX, pos.x * tw - mx);
    maxX = math.max(maxX, pos.x * tw + mx);
    minY = math.min(minY, pos.y * th - my);
    maxY = math.max(maxY, pos.y * th + my);
  }
  if (!minX.isFinite) return;
  minX -= margine;
  maxX += margine;
  minY -= margine;
  maxY += margine;
  final s = [scatola.width / (maxX - minX), scatola.height / (maxY - minY), cartaMax / lc].reduce(math.min);
  final ox = scatola.left + (scatola.width - (maxX - minX) * s) / 2 - minX * s;
  final oy = scatola.top + (scatola.height - (maxY - minY) * s) / 2 - minY * s;

  if (anelli) _anelli(g, scatola.center, math.min(scatola.width, scatola.height) * .62);

  final larga = lc * s;
  final alta = ac * s;
  final bordo = math.max(3.0, larga * .035);
  for (final c in posate) {
    final pos = posizioneDi(c);
    if (pos == null) continue;
    final px = ox + pos.x * tw * s;
    final py = oy + pos.y * th * s;
    final giro = (pos.rotazione + ((c.rovescio ?? false) ? 180 : 0)) * math.pi / 180;
    final img = immagini[c.posizione];
    g.save();
    g.translate(px, py);
    g.rotate(giro);
    // `shadowColor: rgba(20,8,26,.55); shadowBlur: 16; shadowOffsetY: 8`.
    g.drawRRect(
      _rettangolo(-larga / 2, -alta / 2 + 8, larga, alta, larga * .05),
      Paint()
        ..color = const Color(0x8C14081A)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8),
    );
    g.drawRRect(_rettangolo(-larga / 2, -alta / 2, larga, alta, larga * .05), Paint()..color = _corniceCarta);
    g.save();
    final dentro = _rettangolo(
      -larga / 2 + bordo,
      -alta / 2 + bordo,
      larga - 2 * bordo,
      alta - 2 * bordo,
      larga * .035,
    );
    g.clipRRect(dentro);
    if (img != null) {
      paintImage(canvas: g, rect: dentro.outerRect, image: img, fit: BoxFit.fill, filterQuality: FilterQuality.medium);
    } else {
      g.drawRect(Rect.fromLTWH(-larga / 2, -alta / 2, larga, alta), Paint()..color = _prugna);
      _scrivi(
        g,
        nomeCartaIn(c.carta!, lingua),
        TextStyle(
          fontFamily: 'Libre Baskerville',
          fontFamilyFallback: _serif,
          fontSize: math.max(12, larga * .12),
          color: _carta,
        ),
        0,
        0,
        allinea: TextAlign.center,
      );
    }
    g.restore();
    g.restore();

    // Il numero della posizione, sull'angolo in alto a sinistra come nella stesa.
    final teta = pos.rotazione * math.pi / 180;
    final bx = px + (-larga / 2) * math.cos(teta) - (-alta / 2) * math.sin(teta);
    final by = py + (-larga / 2) * math.sin(teta) + (-alta / 2) * math.cos(teta);
    final r = math.max(11.0, math.min(16.0, larga * .13));
    g.drawCircle(Offset(bx, by), r, Paint()..color = _ottone);
    final numero = TextPainter(
      text: TextSpan(
        text: '${c.posizione}',
        style: TextStyle(
          fontFamily: 'DM Sans',
          fontFamilyFallback: _sans,
          fontWeight: FontWeight.w700,
          fontSize: (r * 1.05).roundToDouble(),
          color: _prugnaScuro,
          height: 1,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    numero.paint(g, Offset(bx - numero.width / 2, by + 1 - numero.height / 2));
    numero.dispose();
  }
}

/// Il marchio della v2: il segno ✦ nella sua losanga, «TAROTS» e «chat» in corsivo d'ottone, con la linea di base a
/// [y].
void _marchio(Canvas g, double x, double y, double dimensione) {
  TextStyle serif({FontStyle? stile, required Color colore, double? px}) => TextStyle(
    fontFamily: 'Libre Baskerville',
    fontFamilyFallback: _serif,
    fontSize: px ?? dimensione,
    fontStyle: stile,
    color: colore,
    height: 1,
  );
  double larghezza(String t, TextStyle s) {
    final p = TextPainter(
      text: TextSpan(text: t, style: s),
      textDirection: TextDirection.ltr,
    )..layout();
    final w = p.width;
    p.dispose();
    return w;
  }

  const tarots = 'TAROTS ';
  final w1 = larghezza(tarots, serif(colore: _carta));
  final segno = dimensione * 1.1;
  final cy = y - dimensione * .35;
  final hx = segno * .42, hy = segno * .55;
  final cx = x + segno / 2;
  final losanga = Path()
    ..moveTo(cx, cy - hy)
    ..lineTo(cx + hx, cy - hy * .64)
    ..lineTo(cx + hx, cy + hy * .64)
    ..lineTo(cx, cy + hy)
    ..lineTo(cx - hx, cy + hy * .64)
    ..lineTo(cx - hx, cy - hy * .64)
    ..close();
  g.drawPath(
    losanga,
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.4
      ..color = _ottoneChiaro,
  );
  final stella = TextPainter(
    text: TextSpan(
      text: '✦',
      style: serif(colore: _ottoneChiaro, px: dimensione * .62),
    ),
    textDirection: TextDirection.ltr,
  )..layout();
  stella.paint(g, Offset(cx - stella.width / 2, cy + 1 - stella.height / 2));
  stella.dispose();
  _scrivi(g, tarots, serif(colore: _carta), x + segno + dimensione * .5, y);
  _scrivi(g, 'chat', serif(stile: FontStyle.italic, colore: _ottoneChiaro), x + segno + dimensione * .5 + w1, y);
}

void _simbolo(Canvas g, String? nome, Offset centro, double lato) {
  final k = lato / latoSimbolo;
  final quale = simboloDi(nome);
  final percorso = tracciato(percorsiSimboli[quale]!);
  g.save();
  g.translate(centro.dx - lato / 2, centro.dy - lato / 2);
  g.scale(k);
  if (quale == 'stella') g.drawPath(percorso, Paint()..color = const Color(0x29D6B66D));
  g.drawPath(
    percorso,
    Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..color = _ottoneChiaro,
  );
  g.restore();
}

/// Il pittore dell'immagine della lettura condivisa, 800×600 (scalato se il riquadro è diverso).
class PittoreCondivisione extends CustomPainter {
  /// L'immagine di [lettura], con le immagini delle carte già caricate (posizione → immagine).
  PittoreCondivisione(this.lettura, this.immagini);

  /// La lettura condivisa (ciò che la pagina pubblica mostra).
  final LetturaCondivisa lettura;

  /// Le immagini delle carte, per posizione.
  final Map<int, ui.Image?> immagini;

  @override
  void paint(Canvas canvas, Size size) {
    final stesa = lettura.stesa;
    if (stesa == null) return;
    canvas.save();
    canvas.scale(size.width / misuraImmagine.width, size.height / misuraImmagine.height);
    dipingi(canvas);
    canvas.restore();
  }

  /// Il disegno a 800×600.
  void dipingi(Canvas g) {
    final l = lettura;
    final stesa = l.stesa!;
    const w = 800.0, h = 600.0;
    final ll = comeLingua(l.lang) ?? 'it';
    final verso = ll == 'ar' ? TextDirection.rtl : TextDirection.ltr;

    _fondo(g, w, h);
    disegnaTavolo(g, stesa, l.cards, const Rect.fromLTWH(40, 44, 430, h - 88), 128, immagini, ll);

    const colX = 500.0;
    const colW = w - colX - 44;
    _marchio(g, colX, 78, 26);

    _scrivi(
      g,
      nomeStesaIn(stesa, ll).toUpperCase().split('').join(String.fromCharCode(8202)),
      const TextStyle(
        fontFamily: 'DM Sans',
        fontFamilyFallback: _sans,
        fontWeight: FontWeight.w600,
        fontSize: 12,
        color: _ottoneChiaro,
      ),
      colX,
      122,
    );

    var y = 158.0;
    final testo = l.shareText ?? '';
    if (testo.isNotEmpty) {
      y =
          _paragrafo(
            g,
            testo,
            const TextStyle(
              fontFamily: 'Libre Baskerville',
              fontFamilyFallback: _serif,
              fontStyle: FontStyle.italic,
              fontSize: 22,
              color: _carta,
            ),
            colX,
            y,
            colW,
            29,
            2,
            verso: verso,
          ) +
          8;
    }
    if (l.speciale) {
      _simbolo(g, l.partnerSimbolo, Offset(colX + 14, y + 8), 26);
      _scrivi(
        g,
        l.partnerFrase ?? '',
        const TextStyle(
          fontFamily: 'Libre Baskerville',
          fontFamilyFallback: _serif,
          fontStyle: FontStyle.italic,
          fontSize: 17,
          color: _tenue,
        ),
        colX + 36,
        y + 14,
      );
      y += 36;
    }
    g.drawRect(Rect.fromLTWH(colX, y + 6, 36, 2), Paint()..color = _ottoneChiaro);
    y =
        _paragrafo(
          g,
          '«${l.question}»',
          const TextStyle(fontFamily: 'Libre Baskerville', fontFamilyFallback: _serif, fontSize: 20, color: _carta),
          colX,
          y + 36,
          colW,
          27,
          3,
          verso: verso,
        ) +
        10;
    final righe = ((h - 104 - y) / 23).floor().clamp(2, 6);
    _paragrafo(
      g,
      sintesiDelResponso(l.synthesis, 160),
      const TextStyle(fontFamily: 'DM Sans', fontFamilyFallback: _sans, fontSize: 16, color: _tenue),
      colX,
      y + 6,
      colW,
      23,
      righe,
      verso: verso,
    );

    _scrivi(
      g,
      dominio,
      const TextStyle(
        fontFamily: 'DM Sans',
        fontFamilyFallback: _sans,
        fontWeight: FontWeight.w600,
        fontSize: 20,
        color: _ottoneChiaro,
      ),
      colX,
      h - 56,
    );
  }

  @override
  bool shouldRepaint(PittoreCondivisione vecchio) => vecchio.lettura != lettura || vecchio.immagini != immagini;
}

/// L'immagine come widget (dietro un `RepaintBoundary`, come ogni disegno che si esporta): 4:3.
class ImmagineCondivisione extends StatelessWidget {
  /// L'immagine di [lettura].
  const ImmagineCondivisione({super.key, required this.lettura, required this.immagini});

  /// La lettura condivisa.
  final LetturaCondivisa lettura;

  /// Le immagini delle carte, per posizione.
  final Map<int, ui.Image?> immagini;

  @override
  Widget build(BuildContext context) => RepaintBoundary(
    child: AspectRatio(
      aspectRatio: 4 / 3,
      child: CustomPaint(painter: PittoreCondivisione(lettura, immagini)),
    ),
  );
}

/// Carica un'immagine come `ui.Image` (null se manca o non arriva entro dieci secondi).
Future<ui.Image?> caricaImmagine(ImageProvider fornitore) {
  final pronta = Completer<ui.Image?>();
  final flusso = fornitore.resolve(ImageConfiguration.empty);
  late final ImageStreamListener ascolto;
  ascolto = ImageStreamListener(
    (info, _) {
      if (!pronta.isCompleted) pronta.complete(info.image.clone());
      info.dispose();
      flusso.removeListener(ascolto);
    },
    onError: (errore, traccia) {
      if (!pronta.isCompleted) pronta.complete(null);
      flusso.removeListener(ascolto);
    },
  );
  flusso.addListener(ascolto);
  return pronta.future.timeout(const Duration(seconds: 10), onTimeout: () => null);
}

/// Le immagini delle carte di una lettura (nel suo mazzo), per posizione.
Future<Map<int, ui.Image?>> caricaCarte(
  List<CartaPosata> carte,
  ImageProvider Function(String file) fornitore,
  String Function(String id) file,
) async {
  final voci = await Future.wait([
    for (final c in carte.where((c) => c.carta != null))
      caricaImmagine(fornitore(file(c.carta!.id))).then((img) => MapEntry(c.posizione, img)),
  ]);
  return Map.fromEntries(voci);
}

/// L'immagine della lettura condivisa in PNG 800×600, disegnata su una tela fuori dallo schermo con lo stesso pittore
/// del widget; `null` se la lettura non ha la stesa.
Future<Uint8List?> componiImmagine(LetturaCondivisa lettura, Map<int, ui.Image?> immagini) async {
  if (lettura.stesa == null) return null;
  final registro = ui.PictureRecorder();
  final tela = Canvas(registro, Offset.zero & misuraImmagine);
  PittoreCondivisione(lettura, immagini).dipingi(tela);
  final disegno = registro.endRecording();
  final immagine = await disegno.toImage(misuraImmagine.width.toInt(), misuraImmagine.height.toInt());
  disegno.dispose();
  final dati = await immagine.toByteData(format: ui.ImageByteFormat.png);
  immagine.dispose();
  return dati?.buffer.asUint8List();
}

/// Il tavolo di una lettura da solo, in PNG (per la stampa in PDF): le carte sul fondo prugna, largo [larghezza].
Future<Uint8List?> componiTavolo(
  Stesa stesa,
  List<CartaPosata> carte,
  Map<int, ui.Image?> immagini,
  String lingua, {
  double larghezza = 900,
}) async {
  final altezza = larghezza * (stesa.forma == 'quadrata' ? 1 : 12 / 16);
  final registro = ui.PictureRecorder();
  final tela = Canvas(registro, Rect.fromLTWH(0, 0, larghezza, altezza));
  tela.drawRect(Rect.fromLTWH(0, 0, larghezza, altezza), Paint()..color = _prugna);
  disegnaTavolo(
    tela,
    stesa,
    carte,
    Rect.fromLTWH(24, 24, larghezza - 48, altezza - 48),
    larghezza * .22,
    immagini,
    lingua,
  );
  final disegno = registro.endRecording();
  final immagine = await disegno.toImage(larghezza.toInt(), altezza.toInt());
  disegno.dispose();
  final dati = await immagine.toByteData(format: ui.ImageByteFormat.png);
  immagine.dispose();
  return dati?.buffer.asUint8List();
}
