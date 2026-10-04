/// I bottoni e i collegamenti del sito: `.button` (prugna), `.button-brass`, `.button-quiet`, `.button-light`,
/// `.button-small`, e i collegamenti sottolineati d'ottone (`.minor-cta a`, `a.inline`).
library;

import 'package:flutter/widgets.dart';

import '../rotte/navigazione.dart';
import '../tema/tema.dart';
import 'premibile.dart';

/// Le varianti di `.button`.
enum Variante {
  /// `.button`: prugna, testo bianco.
  prugna,

  /// `.button-brass`: ottone, testo scuro.
  ottone,

  /// `.button-quiet`: trasparente, testo prugna, bordo sottile.
  quieto,

  /// `.button-light`: trasparente su fondo scuro.
  chiaro,

  /// `.button-danger`.
  pericolo,
}

/// Un `.button`: va a [href] o chiama [alTocco].
class Bottone extends StatelessWidget {
  /// Un bottone.
  const Bottone(
    this.testo, {
    super.key,
    this.href,
    this.alTocco,
    this.variante = Variante.prugna,
    this.piccolo = false,
    this.pieno = false,
    this.an,
    this.anProprieta = const {},
  });

  /// L'etichetta.
  final String testo;

  /// Dove porta (un percorso del sito).
  final String? href;

  /// Cosa fa, se non porta da nessuna parte.
  final VoidCallback? alTocco;

  /// La variante.
  final Variante variante;

  /// `.button-small`.
  final bool piccolo;

  /// A tutta larghezza (`width: 100%`).
  final bool pieno;

  /// L'evento delle statistiche (`data-an`).
  final String? an;

  /// Le proprietà dell'evento (`data-an-*`).
  final Map<String, String> anProprieta;

  ({Color fondo, Color fondoPremuto, Color testo, Color bordo}) get _colori => switch (variante) {
    Variante.prugna => (
      fondo: Token.plum,
      fondoPremuto: const Color(0xFF572064),
      testo: const Color(0xFFFFFFFF),
      bordo: const Color(0x00000000),
    ),
    Variante.ottone => (
      fondo: Token.brass,
      fondoPremuto: const Color(0xFFC69543),
      testo: Colori.testoOttone,
      bordo: Colori.bordoOttone,
    ),
    Variante.quieto => (
      fondo: const Color(0x00000000),
      fondoPremuto: const Color(0x0F3C1846),
      testo: Token.plum,
      bordo: Token.line,
    ),
    Variante.chiaro => (
      fondo: const Color(0x00000000),
      fondoPremuto: const Color(0x14FFFFFF),
      testo: const Color(0xFFFFF7E8),
      bordo: const Color(0x8CD6B66D),
    ),
    Variante.pericolo => (
      fondo: const Color(0x00000000),
      fondoPremuto: const Color(0x129B2C2C),
      testo: Token.danger,
      bordo: const Color(0x669B2C2C),
    ),
  };

  @override
  Widget build(BuildContext context) {
    final c = _colori;
    final azione = alTocco ?? (href == null ? null : () => vai(context, href!));
    return Premibile(
      alTocco: azione,
      collegamento: href != null && alTocco == null,
      an: an,
      anProprieta: anProprieta,
      raggioFuoco: Token.raggio,
      // `button:disabled { opacity: .55 }`: tutto il bottone, fondo compreso.
      costruisci: (context, premuto) => Opacity(
        opacity: azione == null ? .55 : 1,
        child: AnimatedContainer(
          duration: Token.durataTransizione,
          constraints: BoxConstraints(
            minHeight: piccolo ? Token.altezzaBottonePiccolo : Token.altezzaBottone,
            minWidth: pieno ? double.infinity : 0,
          ),
          padding: piccolo
              ? const EdgeInsets.symmetric(horizontal: 12.8, vertical: 8)
              : const EdgeInsets.symmetric(horizontal: 17.6, vertical: 11.52),
          decoration: BoxDecoration(
            color: premuto ? c.fondoPremuto : c.fondo,
            border: Border.all(color: c.bordo),
            borderRadius: BorderRadius.circular(Token.raggio),
          ),
          child: Center(
            widthFactor: pieno ? null : 1,
            heightFactor: 1,
            child: Text(
              testo,
              textAlign: TextAlign.center,
              style: Stile.bottone(px: piccolo ? 12.8 : 14.08).copyWith(color: c.testo),
            ),
          ),
        ),
      ),
    );
  }
}

/// Una fila di bottoni (`.button-row { display: flex; flex-wrap: wrap; gap: .6rem }`).
class FilaBottoni extends StatelessWidget {
  /// Una fila.
  const FilaBottoni({super.key, required this.children});

  /// I bottoni.
  final List<Widget> children;

  @override
  Widget build(BuildContext context) =>
      Wrap(spacing: 9.6, runSpacing: 9.6, crossAxisAlignment: WrapCrossAlignment.center, children: children);
}

/// Un collegamento sottolineato d'ottone: `.minor-cta a`, `a.inline` (alto almeno 44 px, si tocca bene).
class Collegamento extends StatelessWidget {
  /// Un collegamento a [href].
  const Collegamento(this.testo, {super.key, required this.href, this.stile, this.an, this.anProprieta = const {}});

  /// Il testo.
  final String testo;

  /// Dove porta.
  final String href;

  /// Lo stile del testo (il colore è prugna, la sottolineatura d'ottone).
  final TextStyle? stile;

  /// L'evento delle statistiche (`data-an`).
  final String? an;

  /// Le proprietà dell'evento.
  final Map<String, String> anProprieta;

  @override
  Widget build(BuildContext context) {
    final base = stile ?? Stile.sans(14.08, altezza: 1.6);
    return Premibile(
      alTocco: () => vai(context, href),
      collegamento: true,
      an: an,
      anProprieta: anProprieta,
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 44),
        child: Align(
          alignment: AlignmentDirectional.centerStart,
          widthFactor: 1,
          heightFactor: 1,
          child: TestoSottolineato(testo, stile: base, colore: premuto ? Token.verdigris : Token.plum),
        ),
      ),
    );
  }
}

/// Un testo sottolineato come nel sito: `text-decoration-color: var(--brass); text-underline-offset: 4px` (la linea
/// 4 px sotto la linea di base, una per riga).
class TestoSottolineato extends StatelessWidget {
  /// Un testo sottolineato.
  const TestoSottolineato(
    this.testo, {
    super.key,
    required this.stile,
    this.colore = Token.plum,
    this.linea = Token.brass,
    this.scarto = 4,
  });

  /// Il testo.
  final String testo;

  /// Lo stile.
  final TextStyle stile;

  /// Il colore del testo.
  final Color colore;

  /// Il colore della linea.
  final Color linea;

  /// La distanza della linea dalla linea di base.
  final double scarto;

  @override
  Widget build(BuildContext context) {
    final scala = MediaQuery.textScalerOf(context);
    final verso = Directionality.of(context);
    return LayoutBuilder(
      builder: (context, vincoli) {
        final p = TextPainter(
          text: TextSpan(
            text: testo,
            style: stile.copyWith(color: colore),
          ),
          textDirection: verso,
          textScaler: scala,
        )..layout(maxWidth: vincoli.maxWidth);
        return Semantics(
          label: testo,
          child: CustomPaint(size: p.size, painter: _Sottolineatura(p, linea, scarto)),
        );
      },
    );
  }
}

class _Sottolineatura extends CustomPainter {
  _Sottolineatura(this.testo, this.linea, this.scarto);

  final TextPainter testo;
  final Color linea;
  final double scarto;

  @override
  void paint(Canvas canvas, Size size) {
    testo.paint(canvas, Offset.zero);
    final pennello = Paint()
      ..color = linea
      ..strokeWidth = 1;
    for (final r in testo.computeLineMetrics()) {
      final y = r.baseline + scarto + .5;
      canvas.drawLine(Offset(r.left, y), Offset(r.left + r.width, y), pennello);
    }
  }

  @override
  bool shouldRepaint(_Sottolineatura vecchio) => true;
}
