/// Il tema dell'app: i valori di `token.g.dart` (generati da `v2.css`) e gli stili di testo del sito, regola per
/// regola. Ogni stile dice da quale selettore viene; le misure in `rem` sono ×16, quelle in `em` di spaziatura sono
/// moltiplicate per la dimensione del carattere, come fa il browser.
library;

import 'package:flutter/widgets.dart';
import 'package:material_ui/material_ui.dart' show ColorScheme, ThemeData, VisualDensity;

import 'token.g.dart';

export 'token.g.dart';

/// Le larghezze dei punti di rottura del CSS (`Token.puntiDiRottura`), con un nome.
abstract final class Rottura {
  /// Un punto di rottura che il CSS deve avere: se il sito lo togliesse, l'app se ne accorge all'avvio (e nei test),
  /// invece di prendere in silenzio quello vicino.
  static double _punto(double px) => Token.puntiDiRottura.firstWhere(
    (p) => p == px,
    orElse: () => throw StateError('v2.css non ha più @media (max-width: ${px}px): aggiornare lib/tema/tema.dart'),
  );

  /// `@media (max-width: 339px)`: telefoni molto vecchi.
  static final double minima = _punto(339);

  /// `@media (max-width: 430px)`.
  static final double stretta = _punto(430);

  /// `@media (max-width: 560px)`.
  static final double piccola = _punto(560);

  /// `@media (max-width: 760px)`: il telefono.
  static final double telefono = _punto(760);

  /// `@media (max-width: 1000px)`.
  static final double media = _punto(1000);

  /// `@media (max-width: 1100px)`: la testata va su due righe.
  static final double larga = _punto(1100);
}

/// Le domande che il CSS fa alla larghezza della finestra.
extension Misure on double {
  /// `@media (max-width: 760px)`.
  bool get telefono => this <= Rottura.telefono;

  /// `@media (max-width: 560px)`.
  bool get piccolo => this <= Rottura.piccola;

  /// `@media (max-width: 430px)`.
  bool get stretto => this <= Rottura.stretta;

  /// `@media (max-width: 1000px)`.
  bool get medio => this <= Rottura.media;

  /// `@media (max-width: 1100px)`.
  bool get largoMedio => this <= Rottura.larga;

  /// `clamp(min, Nvw, max)` per questa larghezza.
  double clampVw(double minimo, double vw, double massimo) => (this * vw / 100).clamp(minimo, massimo);

  /// `var(--gutter)`.
  double get gutter => Token.gutter.per(this);
}

/// I colori che il CSS scrive direttamente nelle regole (non in `:root`), con il selettore da cui vengono.
abstract final class Colori {
  /// `.site-header { color }`.
  static const Color testataTesto = Color(0xFFFFF8EB);

  /// `.site-header { background: rgba(32,16,38,.94) }`.
  static const Color testataFondo = Color(0xF0201026);

  /// `.site-header { border-bottom: 1px solid rgba(244,239,229,.16) }`.
  static const Color testataBordo = Color(0x29F4EFE5);

  /// `.primary-nav a { color }`.
  static const Color voceMenu = Color(0xFFE9DECD);

  /// `.hdr-icon { color }`.
  static const Color iconaTestata = Color(0xFFF3E8D8);

  /// `.button-brass { color }`, `.hdr-badge { color }`.
  static const Color testoOttone = Color(0xFF1D1520);

  /// `.button-brass { border-color }`.
  static const Color bordoOttone = Color(0xFFD5B160);

  /// `.question-form { background }`, `.plan { background }`.
  static const Color carta = Color(0xFFFFFAF0);

  /// `.question-form { border: 1px solid rgba(178,131,54,.55) }`.
  static const Color bordoDomanda = Color(0x8CB28336);

  /// `.question-form input::placeholder`.
  static const Color segnaposto = Color(0xFF806C79);

  /// `.experience, .funnel … .eyebrow` sul prugna: un verderame più chiaro.
  static const Color eyebrowScuro = Color(0xFF8FD0C9);

  /// `.experience { color }`.
  static const Color testoEsperienza = Color(0xFFF5ECDC);

  /// `.experience .section-title`, `.declaration h3`…
  static const Color titoloChiaro = Color(0xFFFFF7E8);

  /// `.experience .section-intro`, `.demo-caption`.
  static const Color introScura = Color(0xFFCDBFD3);

  /// `.demo-copy, .demo-ritual { background }`.
  static const Color fondoDemo = Color(0xFF28152F);

  /// `.site-footer { color }`.
  static const Color piede = Color(0xFFD7C7DB);

  /// `.site-footer p, .site-footer li`.
  static const Color piedeTenue = Color(0xFFBBAEC1);

  /// `.site-footer h2`.
  static const Color piedeTitolo = Color(0xFFFFF5E4);

  /// La cornice crema delle carte (`#f5e6bf`).
  static const Color cornice = Color(0xFFF5E6BF);

  /// `.notice { background }`.
  static const Color avviso = Color(0xFFFFF8E8);

  /// `.error { background }`.
  static const Color fondoErrore = Color(0xFFFBEEEE);

  /// `.difference { background }`.
  static const Color differenza = Color(0xFFFFF9ED);

  /// `.physical { background }`.
  static const Color fisico = Color(0xFFF0E7D7);

  /// `.dialog-backdrop { background: rgba(32,16,38,.62) }`.
  static const Color velo = Color(0x9E201026);
}

/// Gli stili di testo del sito.
abstract final class Stile {
  /// `body { font: 400 16px/1.6 var(--sans); color: var(--ink) }`.
  static const TextStyle corpo = TextStyle(
    fontFamily: 'DM Sans',
    fontFamilyFallback: ['Arial', 'sans-serif'],
    fontSize: 16,
    height: 1.6,
    color: Token.ink,
    fontWeight: FontWeight.w400,
    leadingDistribution: TextLeadingDistribution.even,
  );

  /// `var(--serif)` alla dimensione [px].
  ///
  /// Senza [altezza] è l'interlinea `normal` di Libre Baskerville (1.24, misurata in Edge e in Flutter): quella dei
  /// titoli che il CSS scrive con la scorciatoia `font:`. Va scritta: un'altezza nulla erediterebbe l'1.6 del corpo.
  static TextStyle serif(double px, {double? altezza = 1.24, FontStyle? stile, Color? colore, double? em}) => TextStyle(
    fontFamily: 'Libre Baskerville',
    fontFamilyFallback: const ['Georgia', 'serif'],
    fontSize: px,
    height: altezza,
    leadingDistribution: TextLeadingDistribution.even,
    fontStyle: stile,
    fontWeight: FontWeight.w400,
    color: colore,
    letterSpacing: em == null ? null : em * px,
  );

  /// `var(--sans)` alla dimensione [px].
  ///
  /// L'interlinea predefinita è quella di `body` (1.6), che nel CSS si eredita ovunque; chi nel CSS usa la scorciatoia
  /// `font:` senza interlinea torna a `normal` (in Flutter: `altezza: null` in [serif]). Le righe si dividono lo spazio
  /// in più sopra e sotto in parti uguali (`leadingDistribution: even`), come nel browser.
  static TextStyle sans(
    double px, {
    FontWeight peso = FontWeight.w400,
    double? altezza = 1.6,
    Color? colore,
    double? em,
  }) => TextStyle(
    fontFamily: 'DM Sans',
    fontFamilyFallback: const ['Arial', 'sans-serif'],
    fontSize: px,
    fontWeight: peso,
    height: altezza,
    leadingDistribution: TextLeadingDistribution.even,
    color: colore,
    letterSpacing: em == null ? null : em * px,
  );

  /// `.eyebrow { color: var(--verdigris); font-size: .74rem; font-weight: 700; letter-spacing: .1em; uppercase }`.
  static TextStyle eyebrow({Color colore = Token.verdigris}) =>
      sans(11.84, peso: FontWeight.w700, colore: colore, em: .1, altezza: 1.6);

  /// `.display { font: 400 clamp(2.25rem, 5vw, 5.4rem)/1.05 var(--serif); letter-spacing: -.055em }`; sotto i 430 px
  /// `font-size: 2.3rem`.
  static TextStyle display(double larghezza) {
    final px = larghezza.stretto ? 36.8 : larghezza.clampVw(36, 5, 86.4);
    return serif(px, altezza: 1.05, em: -.055);
  }

  /// `.section-title { font: 400 clamp(1.85rem, 3.5vw, 3.5rem)/1.15 var(--serif); letter-spacing: -.04em }`.
  static TextStyle titoloSezione(double larghezza) => serif(larghezza.clampVw(29.6, 3.5, 56), altezza: 1.15, em: -.04);

  /// `.section-intro { color: var(--ink-soft); font-size: 1.06rem }`; sul telefono `1rem`.
  static TextStyle introSezione(double larghezza) =>
      sans(larghezza.telefono ? 16 : 16.96, altezza: 1.6, colore: Token.inkSoft);

  /// `.button { font-weight: 700; font-size: .88rem; line-height: 1.2; letter-spacing: .01em }`.
  static TextStyle bottone({double px = 14.08}) => sans(px, peso: FontWeight.w700, altezza: 1.2, em: .01);
}

/// Il tema Material dell'app: quasi niente di Material si vede (i componenti sono quelli del sito), ma il tema dà
/// il carattere predefinito, il fondo e il colore della selezione del testo.
ThemeData temaApp() {
  return ThemeData(
    useMaterial3: true,
    fontFamily: 'DM Sans',
    scaffoldBackgroundColor: Token.paper,
    canvasColor: Token.paper,
    visualDensity: VisualDensity.standard,
    colorScheme: const ColorScheme.light(
      primary: Token.plum,
      onPrimary: Color(0xFFFFFFFF),
      secondary: Token.brass,
      onSecondary: Colori.testoOttone,
      surface: Token.paper,
      onSurface: Token.ink,
      error: Token.danger,
    ),
  );
}
