/// Le griglie del CSS (`display: grid; grid-template-columns: repeat(n, 1fr)`): celle in righe, ogni riga alta
/// quanto la cella più alta (le celle si allungano, come `align-items: stretch`), con lo spazio fra colonne e righe.
///
/// Il motivo ricorrente del sito «`gap: 1px; background: var(--line); border: 1px solid var(--line)`» (le tessere
/// separate da una riga sottile) è [Griglia.righe]: lo sfondo della griglia è la riga, le celle hanno il loro fondo.
library;

import 'package:flutter/widgets.dart';

/// Una griglia.
class Griglia extends StatelessWidget {
  /// Una griglia di [colonne] colonne uguali (o coi [pesi] dati, come `1.1fr 1fr 1fr 1fr`).
  const Griglia({
    super.key,
    required this.children,
    this.colonne = 1,
    this.pesi,
    this.spazioColonne = 0,
    this.spazioRighe = 0,
    this.allunga = true,
  }) : linea = null;

  /// Celle separate da una riga di [linea] (gap 1 px, bordo 1 px).
  const Griglia.righe({super.key, required this.children, this.colonne = 1, this.pesi, required Color this.linea})
    : spazioColonne = 1,
      spazioRighe = 1,
      allunga = true;

  /// Le celle, riga per riga.
  final List<Widget> children;

  /// Il numero di colonne.
  final int colonne;

  /// I pesi delle colonne (`fr`), se non sono uguali.
  final List<int>? pesi;

  /// `column-gap`.
  final double spazioColonne;

  /// `row-gap`.
  final double spazioRighe;

  /// Le celle di una riga alte uguali (`align-items: stretch`); falso = in alto (`align-items: start`).
  final bool allunga;

  /// Il colore delle righe fra le celle ([Griglia.righe]).
  final Color? linea;

  @override
  Widget build(BuildContext context) {
    final righe = <Widget>[];
    for (var i = 0; i < children.length; i += colonne) {
      final celle = <Widget>[];
      for (var c = 0; c < colonne; c++) {
        if (c > 0) celle.add(SizedBox(width: spazioColonne));
        final indice = i + c;
        final cella = indice < children.length ? children[indice] : const SizedBox.shrink();
        celle.add(Expanded(flex: pesi?[c] ?? 1, child: cella));
      }
      if (righe.isNotEmpty) righe.add(SizedBox(height: spazioRighe));
      final riga = Row(
        crossAxisAlignment: allunga && colonne > 1 ? CrossAxisAlignment.stretch : CrossAxisAlignment.start,
        children: celle,
      );
      righe.add(allunga && colonne > 1 ? IntrinsicHeight(child: riga) : riga);
    }
    final colonna = Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: righe);
    if (linea == null) return colonna;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: linea,
        border: Border.all(color: linea!),
      ),
      child: Padding(padding: const EdgeInsets.all(1), child: colonna),
    );
  }
}
