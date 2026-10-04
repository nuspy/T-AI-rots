// GENERATO da frontend/scripts/genera-token.mjs da frontend/app/(v2)/v2.css: non modificare a mano.
// Per cambiare un colore o una misura si cambia il CSS del sito e si rilancia lo script.

// ignore_for_file: lines_longer_than_80_chars

import 'package:flutter/widgets.dart';

/// Una misura che cresce con la larghezza della finestra: `clamp(minimo, vw, massimo)` del CSS.
@immutable
class MisuraFluida {
  /// Il valore più piccolo, in px logici.
  final double minimo;

  /// La percentuale della larghezza della finestra (`4vw` → 4).
  final double vw;

  /// Il valore più grande, in px logici.
  final double massimo;

  /// `clamp(minimo, vw, massimo)`.
  const MisuraFluida({required this.minimo, required this.vw, required this.massimo});

  /// Il valore per una finestra larga [larghezza] px logici.
  double per(double larghezza) => (larghezza * vw / 100).clamp(minimo, massimo);
}

/// I valori del CSS della v2: variabili di `:root`, punti di rottura e misure ricorrenti.
abstract final class Token {
  /// `--paper: #f4efe5`
  static const Color paper = Color(0xFFF4EFE5);

  /// `--paper-deep: #e9dfcc`
  static const Color paperDeep = Color(0xFFE9DFCC);

  /// `--paper-light: #fffaf1`
  static const Color paperLight = Color(0xFFFFFAF1);

  /// `--ink: #20162b`
  static const Color ink = Color(0xFF20162B);

  /// `--ink-soft: #55455d`
  static const Color inkSoft = Color(0xFF55455D);

  /// `--plum: #3c1846`
  static const Color plum = Color(0xFF3C1846);

  /// `--plum-deep: #201026`
  static const Color plumDeep = Color(0xFF201026);

  /// `--brass: #b28336`
  static const Color brass = Color(0xFFB28336);

  /// `--brass-pale: #d6b66d`
  static const Color brassPale = Color(0xFFD6B66D);

  /// `--verdigris: #19706f`
  static const Color verdigris = Color(0xFF19706F);

  /// `--mist: #d8e7df`
  static const Color mist = Color(0xFFD8E7DF);

  /// `--danger: #9b2c2c`
  static const Color danger = Color(0xFF9B2C2C);

  /// `--line: rgba(60, 24, 70, .18)`
  static const Color line = Color(0x2E3C1846);

  /// `--serif`: la prima famiglia è nei font dell'app, le altre sono il ripiego del sito.
  static const List<String> serif = ['Libre Baskerville', 'Georgia', 'serif'];

  /// `--sans`: la prima famiglia è nei font dell'app, le altre sono il ripiego del sito.
  static const List<String> sans = ['DM Sans', 'Arial', 'sans-serif'];

  /// `--gutter: clamp(.8rem, 4vw, 3.6rem)`
  static const MisuraFluida gutter = MisuraFluida(minimo: 12.8, vw: 4.0, massimo: 57.6);

  /// I punti di rottura del CSS (`@media (max-width: Npx)`), dal più stretto.
  static const List<double> puntiDiRottura = [339.0, 430.0, 480.0, 560.0, 760.0, 1000.0, 1100.0];

  /// `.button { border-radius: 3px }`
  static const double raggio = 3.0;

  /// `.chip { border-radius: 999px }`
  static const double raggioPillola = 999.0;

  /// `.button { transition: transform .18s ease, background .18s ease, box-shadow .18s ease }`
  static const Duration durataTransizione = Duration(milliseconds: 180);

  /// `.button { min-height: 47px }`
  static const double altezzaBottone = 47.0;

  /// `.button-small { min-height: 44px }`
  static const double altezzaBottonePiccolo = 44.0;

  /// `body { font: 400 16px/1.6 var(--sans) }`
  static const double corpo = 16.0;

  /// `body { font: 400 16px/1.6 var(--sans) }`
  static const double interlinea = 1.6;

  /// `.band { max-width: 1200px }`
  static const double larghezzaBanda = 1200.0;

  /// `.hero { max-width: 1320px }`
  static const double larghezzaEroe = 1320.0;

  /// `.site-header { min-height: 76px }`
  static const double altezzaTestata = 76.0;

  /// `@media (max-width: 760px) .site-header { min-height: 56px }`
  static const double altezzaTestataTelefono = 56.0;

  /// `@media (max-width: 760px) .primary-nav .nav-breve { font-size: 8px }`
  static const double etichettaTestataTelefono = 8.0;

  /// `@media (max-width: 339px) .primary-nav .nav-breve { font-size: 7px }`
  static const double etichettaTestataStretta = 7.0;

  /// `@media (max-width: 760px) .primary-nav .nav-icona { width: 20px }`
  static const double iconaTestataTelefono = 20.0;

  /// `.hdr-icon { min-height: 48px }`
  static const double bersaglioMinimo = 48.0;

  /// `@media (max-width: 760px) .header-actions .hdr-icon { min-height: 44px }`
  static const double bersaglioTestataTelefono = 44.0;

  /// `.dialog { border-top: 3px solid var(--brass) }`
  static const double bordoModale = 3.0;

  /// `.dialog { width: min(560px, 100%) }`
  static const double larghezzaModale = 560.0;
}
