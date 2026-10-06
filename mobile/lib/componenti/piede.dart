/// Il piede del sito (`frontend/v2/componenti/piede.tsx`, `.site-footer`): il marchio col motto e la lingua, tre
/// colonne di collegamenti, l'avvertenza. Quattro colonne sul computer, due fino a 760 px, una fino a 430 px.
library;

import 'dart:math' as math;

import 'package:flutter/widgets.dart';

import '../l10n/testi.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import '../traduzione/scelta_lingua.dart';
import 'marchio.dart';
import 'premibile.dart';
import 'selettore_lingua.dart';
import 'testi.dart';

/// Il piede.
class Piede extends StatelessWidget {
  /// Il piede della pagina.
  const Piede({super.key});

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final colonne = [
      (
        titolo: t.comune_piede_leggi,
        voci: [
          (R.leggi, t.comune_piede_leggi_gratis),
          (R.fisica, t.comune_piede_tue_carte),
          (R.giorno, t.comune_piede_giorno),
          (R.storia, t.comune_piede_storia),
        ],
      ),
      (
        titolo: t.comune_piede_esplora,
        voci: [
          (R.mazzi, t.comune_piede_mazzi),
          (R.carte, t.comune_piede_carte),
          (R.stese, t.comune_piede_stese),
          (R.blog, t.comune_piede_diario),
          (R.voto, t.comune_piede_voto),
        ],
      ),
      (
        titolo: t.comune_piede_info,
        voci: [
          (R.prezzi, t.comune_piede_prezzi),
          (R.negozio, t.comune_piede_negozio),
          (R.privacy, t.comune_piede_privacy),
        ],
      ),
    ];
    final tenue = Stile.sans(13.44, colore: Colori.piedeTenue, altezza: 1.6);

    final primo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Premibile(
          alTocco: () => vai(context, R.home),
          collegamento: true,
          etichetta: t.comune_aria_home,
          costruisci: (context, _) => const SizedBox(
            height: 44,
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                SegnoMarchio(larghezza: 33, altezza: 40, px: 16),
                SizedBox(width: 9.6),
                NomeMarchio(px: 16, colore: Colori.piede),
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 13.44),
          child: Paragrafo(t.comune_piede_motto, style: tenue),
        ),
        const Padding(
          padding: EdgeInsets.only(top: 16 - 13.44),
          child: SelettoreLingua(colore: Colori.voceMenu),
        ),
        // v9.5: la lingua in cui il telefono traduce articoli, carte e stese.
        const VoceLinguaContenuti(colore: Colori.voceMenu),
      ],
    );

    Widget colonna(({String titolo, List<(String, String)> voci}) c) => Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Semantics(
            header: true,
            child: Text(c.titolo, style: Stile.serif(16.8, colore: Colori.piedeTitolo)),
          ),
        ),
        for (final (href, testo) in c.voci)
          Premibile(
            alTocco: () => vai(context, href),
            collegamento: true,
            costruisci: (context, premuto) => ConstrainedBox(
              constraints: const BoxConstraints(minHeight: 40),
              child: Align(
                alignment: AlignmentDirectional.centerStart,
                widthFactor: 1,
                heightFactor: 1,
                child: Text(testo, style: tenue.copyWith(color: premuto ? Token.brassPale : Colori.piedeTenue)),
              ),
            ),
          ),
      ],
    );

    final blocchi = [primo, for (final c in colonne) colonna(c)];
    final spazio = w.telefono ? 22.4 : 32.0;
    final Widget griglia;
    if (w.stretto) {
      griglia = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (var i = 0; i < blocchi.length; i++) ...[if (i > 0) SizedBox(height: spazio), blocchi[i]],
        ],
      );
    } else if (w.telefono) {
      griglia = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (var r = 0; r < blocchi.length; r += 2) ...[
            if (r > 0) SizedBox(height: spazio),
            IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: blocchi[r]),
                  SizedBox(width: spazio),
                  Expanded(child: r + 1 < blocchi.length ? blocchi[r + 1] : const SizedBox()),
                ],
              ),
            ),
          ],
        ],
      );
    } else {
      griglia = Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(flex: 15, child: blocchi[0]),
          for (final b in blocchi.skip(1)) ...[SizedBox(width: spazio), Expanded(flex: 10, child: b)],
        ],
      );
    }

    final gutter = w.gutter;
    final verticale = w.telefono ? 16.0 : 20.0;
    return ColoredBox(
      color: Token.plumDeep,
      child: Padding(
        padding: EdgeInsets.fromLTRB(
          math.max(gutter, media.padding.left),
          verticale,
          math.max(gutter, media.padding.right),
          math.max(verticale, media.padding.bottom),
        ),
        child: DefaultTextStyle.merge(
          style: const TextStyle(color: Colori.piede),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              griglia,
              SizedBox(height: spazio),
              Container(
                padding: const EdgeInsets.only(top: 24),
                decoration: const BoxDecoration(
                  border: Border(top: BorderSide(color: Color(0x33D6B66D))),
                ),
                child: Paragrafo(t.comune_piede_avvertenza, style: tenue.copyWith(fontSize: 12.48)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
