/// I testi del sito con le due cose del CSS che Flutter non ha da sé:
/// - **`text-wrap: balance`** (titoli, eyebrow, note): le righe di un titolo hanno lunghezze simili, niente parola
///   sola sull'ultima riga. [TestoBilanciato] cerca la larghezza più stretta che tiene lo stesso numero di righe,
///   come fa il browser (fino a sei righe, come Chromium);
/// - **`max-width: Nch`**: [larghezzaCh] misura la cifra «0» nel carattere dello stile, come il browser.
library;

import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';

import '../tema/tema.dart';

/// La larghezza di `1ch` nello stile [s]: la larghezza della cifra «0».
double larghezzaCh(TextStyle s, TextScaler scala) {
  final p = TextPainter(
    // `ch` è l'avanzamento della cifra, senza la spaziatura fra le lettere.
    text: TextSpan(text: '0', style: s.copyWith(letterSpacing: 0)),
    textDirection: TextDirection.ltr,
    textScaler: scala,
  )..layout();
  final w = p.width;
  p.dispose();
  return w;
}

/// Un testo (anche composto, come il titolo della home con la parte in corsivo) con le righe bilanciate.
///
/// Un oggetto di disegno suo (non un `LayoutBuilder`): così sa dare le misure intrinseche e si può mettere nelle
/// righe di una griglia che allunga le celle (`IntrinsicHeight`).
class TestoBilanciato extends StatelessWidget {
  /// Un testo semplice.
  TestoBilanciato(String testo, {super.key, required TextStyle stile, this.maxCh, this.allinea = TextAlign.start})
    : span = TextSpan(text: testo, style: stile);

  /// Un testo composto.
  const TestoBilanciato.ricco(this.span, {super.key, this.maxCh, this.allinea = TextAlign.start});

  /// Il testo.
  final TextSpan span;

  /// `max-width` in `ch` (della dimensione dello stile principale), se c'è.
  final double? maxCh;

  /// L'allineamento.
  final TextAlign allinea;

  @override
  Widget build(BuildContext context) {
    final scala = MediaQuery.textScalerOf(context);
    return _Bilancia(
      span: span,
      scala: scala,
      verso: Directionality.of(context),
      allinea: allinea,
      maxCh: maxCh,
      curato: false,
      child: Text.rich(span, textAlign: allinea, textScaler: scala),
    );
  }
}

/// Un paragrafo (`<p>`) con `text-wrap: pretty`, come i paragrafi del sito: l'ultima riga non resta con una parola
/// sola, se basta stringere un po' le righe sopra (senza aggiungerne). Si usa come `Text`.
class Paragrafo extends StatelessWidget {
  /// Un paragrafo.
  const Paragrafo(this.testo, {super.key, this.style, this.textAlign = TextAlign.start});

  /// Il testo.
  final String testo;

  /// Lo stile (unito a quello di base, come `Text`).
  final TextStyle? style;

  /// L'allineamento.
  final TextAlign textAlign;

  @override
  Widget build(BuildContext context) {
    final scala = MediaQuery.textScalerOf(context);
    final span = TextSpan(text: testo, style: DefaultTextStyle.of(context).style.merge(style));
    return _Bilancia(
      span: span,
      scala: scala,
      verso: Directionality.of(context),
      allinea: textAlign,
      maxCh: null,
      curato: true,
      child: Text.rich(span, textAlign: textAlign, textScaler: scala),
    );
  }
}

class _Bilancia extends SingleChildRenderObjectWidget {
  const _Bilancia({
    required this.span,
    required this.scala,
    required this.verso,
    required this.allinea,
    required this.maxCh,
    required this.curato,
    required super.child,
  });

  final TextSpan span;
  final TextScaler scala;
  final TextDirection verso;
  final TextAlign allinea;
  final double? maxCh;
  final bool curato;

  @override
  _RenderBilancia createRenderObject(BuildContext context) =>
      _RenderBilancia(span, scala, verso, allinea, maxCh, curato: curato);

  @override
  void updateRenderObject(BuildContext context, _RenderBilancia r) {
    r
      ..span = span
      ..scala = scala
      ..verso = verso
      ..allinea = allinea
      ..maxCh = maxCh
      ..curato = curato
      ..markNeedsLayout();
  }
}

class _RenderBilancia extends RenderShiftedBox {
  _RenderBilancia(this.span, this.scala, this.verso, this.allinea, this.maxCh, {required this.curato}) : super(null);

  /// `text-wrap: pretty` invece di `balance`.
  bool curato;

  TextSpan span;
  TextScaler scala;
  TextDirection verso;
  TextAlign allinea;
  double? maxCh;

  double _massima(double disponibile) {
    final stile = span.style;
    if (maxCh == null || stile == null) return disponibile;
    return (larghezzaCh(stile, scala) * maxCh!).clamp(0, disponibile);
  }

  /// `pretty`: la larghezza più ampia, fino a un terzo più stretta, con cui l'ultima riga ha almeno due parole e le
  /// righe restano tante quante erano. Se non c'è, la larghezza piena.
  double _cura(double massima) {
    final testo = span.toPlainText();
    final p = TextPainter(text: span, textDirection: verso, textScaler: scala, textAlign: allinea);
    ({int righe, bool sola}) misura(double w) {
      p.layout(maxWidth: w);
      final righe = p.computeLineMetrics().length;
      final ultima = p.getLineBoundary(TextPosition(offset: testo.length));
      final parole = testo.substring(ultima.start, ultima.end).trim().split(RegExp(r'\s+'));
      return (righe: righe, sola: parole.length < 2);
    }

    final m = misura(massima);
    if (m.righe < 2 || !m.sola) {
      p.dispose();
      return massima;
    }
    for (var w = massima - 4; w >= massima * 2 / 3; w -= 4) {
      final x = misura(w);
      if (x.righe > m.righe) break;
      if (!x.sola) {
        p.dispose();
        return w;
      }
    }
    p.dispose();
    return massima;
  }

  /// La larghezza più stretta che tiene lo stesso numero di righe (fino a sei, come Chromium).
  double _bilancia(double massima) {
    if (!massima.isFinite) return massima;
    if (curato) return _cura(massima);
    final p = TextPainter(text: span, textDirection: verso, textScaler: scala, textAlign: allinea);
    int righe(double w) {
      p.layout(maxWidth: w);
      return p.computeLineMetrics().length;
    }

    final n = righe(massima);
    if (n <= 1 || n > 6) {
      p.dispose();
      return massima;
    }
    var basso = massima / n;
    var alto = massima;
    while (alto - basso > 1) {
      final medio = (basso + alto) / 2;
      if (righe(medio) > n) {
        basso = medio;
      } else {
        alto = medio;
      }
    }
    p.dispose();
    return alto.ceilToDouble().clamp(0, massima);
  }

  @override
  double computeMinIntrinsicWidth(double height) => child?.getMinIntrinsicWidth(height) ?? 0;

  @override
  double computeMaxIntrinsicWidth(double height) => child?.getMaxIntrinsicWidth(height) ?? 0;

  @override
  double computeMinIntrinsicHeight(double width) => child?.getMinIntrinsicHeight(_bilancia(_massima(width))) ?? 0;

  @override
  double computeMaxIntrinsicHeight(double width) => child?.getMaxIntrinsicHeight(_bilancia(_massima(width))) ?? 0;

  @override
  Size computeDryLayout(BoxConstraints constraints) {
    final c = child;
    if (c == null) return constraints.smallest;
    final w = _bilancia(_massima(constraints.maxWidth));
    final s = c.getDryLayout(BoxConstraints(maxWidth: w));
    final larga = allinea == TextAlign.center && constraints.hasBoundedWidth;
    return constraints.constrain(Size(larga ? constraints.maxWidth : s.width, s.height));
  }

  @override
  void performLayout() {
    final c = child;
    if (c == null) {
      size = constraints.smallest;
      return;
    }
    final w = _bilancia(_massima(constraints.maxWidth));
    c.layout(BoxConstraints(maxWidth: w), parentUsesSize: true);
    final larga = allinea == TextAlign.center && constraints.hasBoundedWidth;
    size = constraints.constrain(Size(larga ? constraints.maxWidth : c.size.width, c.size.height));
    (c.parentData! as BoxParentData).offset = Offset(larga ? (size.width - c.size.width) / 2 : 0, 0);
  }
}

/// `<p class="eyebrow">`: piccolo, maiuscolo, spaziato, verderame; sul telefono con `.6rem` sotto (`1rem` più largo).
class Eyebrow extends StatelessWidget {
  /// Un'eyebrow.
  const Eyebrow(this.testo, {super.key, this.colore = Token.verdigris, this.sotto, this.allinea = TextAlign.start});

  /// Il testo (si mostra in maiuscolo, come `text-transform: uppercase`).
  final String testo;

  /// Il colore.
  final Color colore;

  /// Lo spazio sotto; se manca, quello del CSS per la larghezza corrente.
  final double? sotto;

  /// L'allineamento (centrato nell'ultimo invito della home).
  final TextAlign allinea;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return Padding(
      padding: EdgeInsets.only(bottom: sotto ?? (w.telefono ? 9.6 : 16)),
      child: TestoBilanciato(
        testo.toUpperCase(),
        stile: Stile.eyebrow(colore: colore),
        allinea: allinea,
      ),
    );
  }
}

/// `<h2 class="section-title">`: serif, `max-width: 19ch`, righe bilanciate.
class TitoloSezione extends StatelessWidget {
  /// Un titolo di sezione.
  const TitoloSezione(this.testo, {super.key, this.colore = Token.ink, this.px});

  /// Il testo.
  final String testo;

  /// Il colore (sui fondi scuri, chiaro).
  final Color colore;

  /// Una dimensione diversa da quella della classe (lo stile in linea del sito).
  final double? px;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final base = Stile.titoloSezione(w);
    final stile = px == null ? base.copyWith(color: colore) : Stile.serif(px!, altezza: 1.15, em: -.04, colore: colore);
    return Semantics(header: true, child: TestoBilanciato(testo, stile: stile, maxCh: 19));
  }
}

/// `<p class="section-intro">`.
class IntroSezione extends StatelessWidget {
  /// Un'introduzione.
  const IntroSezione(this.testo, {super.key, this.colore = Token.inkSoft, this.sopra = 8});

  /// Il testo.
  final String testo;

  /// Il colore.
  final Color colore;

  /// Il margine sopra (`.section-intro { margin-top: .5rem }`).
  final double sopra;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final stile = Stile.introSezione(w).copyWith(color: colore);
    final massima = larghezzaCh(stile, MediaQuery.textScalerOf(context)) * 58;
    // Sotto, il margine del paragrafo (1em) resta sul computer; sul telefono `margin-block: .6rem 0`.
    return Padding(
      padding: EdgeInsets.only(top: sopra, bottom: w.telefono ? 0 : stile.fontSize ?? 16),
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: massima),
        child: Paragrafo(testo, style: stile),
      ),
    );
  }
}

/// L'apertura delle pagine interne (`Sottotitolo` del sito, `.subhero`): occhiello, titolo, introduzione, con la
/// riga sotto. [compatta] è `.subhero-compact` (titolo più piccolo, meno spazio).
class Sottotitolo extends StatelessWidget {
  /// Un'apertura.
  const Sottotitolo({
    super.key,
    required this.eyebrow,
    required this.titolo,
    required this.intro,
    this.compatta = false,
    this.figlio,
  });

  /// L'occhiello.
  final String eyebrow;

  /// Il titolo (`<h1 class="display">`).
  final String titolo;

  /// L'introduzione.
  final String intro;

  /// `.subhero-compact`.
  final bool compatta;

  /// Ciò che la pagina mette sotto l'introduzione (`children` di `Sottotitolo` del sito).
  final Widget? figlio;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final telefono = w.telefono;
    final sopra = telefono ? 16.0 : (compatta ? w.clampVw(16, 2.1, 25.6) : w.clampVw(20, 2.8, 39.2));
    final sotto = telefono ? 16.0 : (compatta ? 14.4 : 16.8);
    final display = compatta ? Stile.serif(w.clampVw(32, 4.2, 64), altezza: 1.05, em: -.055) : Stile.display(w);
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: Token.larghezzaBanda),
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.fromLTRB(w.gutter, sopra, w.gutter, sotto),
          decoration: const BoxDecoration(
            border: Border(bottom: BorderSide(color: Token.line)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Eyebrow(eyebrow),
              Semantics(header: true, child: TestoBilanciato(titolo, stile: display, maxCh: 18)),
              IntroSezione(intro),
              ?figlio,
            ],
          ),
        ),
      ),
    );
  }
}
