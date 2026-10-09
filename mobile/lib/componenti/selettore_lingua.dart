/// Il selettore della lingua (`SelettoreLingua` del sito, `.lang-select`): una casella col codice della lingua («IT»)
/// e «▾» (sulla testata del telefono, in fondo alla riga, è invece un'icona come le altre col codice sotto); al tocco,
/// l'elenco delle quindici lingue («IT · Italiano») in un dialogo (il `<select>` del telefono fa lo stesso).
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../lingua/lingua_profilo.dart';
import '../tema/tema.dart';
import 'modale.dart';
import 'premibile.dart';

/// La casella della lingua.
class SelettoreLingua extends ConsumerWidget {
  /// Una casella; [colore] è quello del testo (`#f3e8d8` in testata, `#e9decd` nel piede).
  const SelettoreLingua({super.key, this.colore = Colori.iconaTestata, this.larghezzaMassima = 120});

  /// Il colore del testo.
  final Color colore;

  /// `max-width` (7.5rem; 4.6rem sotto i 430 px).
  final double larghezzaMassima;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lingua = ref.watch(linguaProvider);
    final t = context.t;
    return Premibile(
      etichetta: '${t.comune_aria_lingua}: ${datiLingua(lingua).nome}',
      alTocco: () => unawaited(apriSceltaLingua(context, ref)),
      raggioFuoco: Token.raggio,
      costruisci: (context, premuto) => ConstrainedBox(
        // Il codice e la freccia stanno in 44 px; il tocco è alto quanto la testata (48).
        constraints: BoxConstraints(minHeight: 48, minWidth: 44, maxWidth: larghezzaMassima),
        child: Center(
          widthFactor: 1,
          child: Container(
            constraints: const BoxConstraints(minHeight: 32),
            padding: const EdgeInsets.only(left: 6.4, right: 4.8),
            decoration: BoxDecoration(
              color: premuto ? const Color(0x14FFFFFF) : null,
              border: Border.all(color: const Color(0x73D6B66D)),
              borderRadius: BorderRadius.circular(Token.raggio),
            ),
            // Col testo molto ingrandito il codice si stringe nella casella invece di uscirne.
            child: FittedBox(
              fit: BoxFit.scaleDown,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    lingua.toUpperCase(),
                    maxLines: 1,
                    softWrap: false,
                    style: Stile.sans(12.8, peso: FontWeight.w600, colore: colore),
                  ),
                  const SizedBox(width: 3.2),
                  Text('▾', style: Stile.sans(11.2, colore: Token.brassPale)),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// L'elenco delle quindici lingue in un dialogo («IT · Italiano»): la lingua toccata vale subito, e con un account va
/// anche nel profilo (`scegliLingua`). Lo usano la casella e la voce della testata del telefono.
Future<void> apriSceltaLingua(BuildContext context, WidgetRef ref) async {
  final scelta = await apriModale<String>(
    context,
    titolo: context.t.comune_aria_lingua,
    costruisci: (context) {
      final corrente = ref.read(linguaProvider);
      return Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final l in lingue)
            VoceLingua(lingua: l, scelta: l.codice == corrente, alTocco: () => Navigator.of(context).pop(l.codice)),
        ],
      );
    },
  );
  if (scelta != null) await scegliLingua(ref, scelta);
}

/// Una lingua dell'elenco: «IT · Italiano», alta 48 px; la scelta è prugna e ha il segno ✓ (non solo il colore), e
/// per i lettori di schermo è un pulsante d'opzione di un gruppo.
class VoceLingua extends StatelessWidget {
  /// La voce di [lingua].
  const VoceLingua({super.key, required this.lingua, required this.scelta, required this.alTocco});

  /// La lingua.
  final DatiLingua lingua;

  /// È quella scelta.
  final bool scelta;

  /// Il tocco.
  final VoidCallback? alTocco;

  @override
  Widget build(BuildContext context) {
    const chiaro = Color(0xFFFFF7E8);
    return MergeSemantics(
      child: Semantics(
        inMutuallyExclusiveGroup: true,
        checked: scelta,
        child: Premibile(
          alTocco: alTocco,
          selezionato: scelta,
          etichetta: lingua.nome,
          costruisci: (context, premuto) => Container(
            constraints: const BoxConstraints(minHeight: 48),
            alignment: AlignmentDirectional.centerStart,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: scelta ? Token.plum : (premuto ? Token.mist : null),
              border: const Border(bottom: BorderSide(color: Token.line)),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text.rich(
                    TextSpan(
                      children: [
                        TextSpan(
                          text: lingua.codice.toUpperCase(),
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        TextSpan(text: ' · ${lingua.nome}'),
                      ],
                    ),
                    style: Stile.sans(16, altezza: 1.5, colore: scelta ? chiaro : Token.ink),
                  ),
                ),
                if (scelta)
                  Text(
                    '✓',
                    style: Stile.sans(16, peso: FontWeight.w700, colore: chiaro),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
