/// Le pagine che arrivano con la Fase 8: la rotta esiste già (i collegamenti del sito e le statistiche funzionano),
/// la pagina dice dove si è e rimanda al sito finché non c'è.
library;

import 'package:flutter/widgets.dart';

import '../componenti/bottoni.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// Una pagina segnaposto per la rotta [percorso].
class Segnaposto extends StatelessWidget {
  /// Con il [titolo] della pagina (dai dizionari) e il [percorso] della rotta.
  const Segnaposto({super.key, required this.titolo, required this.percorso});

  /// Il titolo.
  final String titolo;

  /// La rotta (si mostra in piccolo: serve a chi prova l'app).
  final String percorso;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    return Pagina(
      sezioni: [
        Fascia(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Eyebrow(t.comune_marchio),
              Semantics(
                header: true,
                child: TestoBilanciato(titolo.replaceAll('\n', ' '), stile: Stile.display(w), maxCh: 18),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Text(percorso, style: Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6)),
              ),
              Bottone(t.comune_e_home, href: R.home, variante: Variante.quieto),
            ],
          ),
        ),
      ],
    );
  }
}
