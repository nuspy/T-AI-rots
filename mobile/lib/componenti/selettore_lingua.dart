/// Il selettore della lingua (`SelettoreLingua` del sito, `.lang-select`): una casella col nome della lingua e «▾»;
/// al tocco, l'elenco delle quindici lingue in un dialogo (il `<select>` del telefono fa lo stesso).
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
      alTocco: () => unawaited(_scegli(context, ref)),
      raggioFuoco: Token.raggio,
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: BoxConstraints(minHeight: 44, maxWidth: larghezzaMassima),
        child: Container(
          padding: const EdgeInsets.only(left: 9.6, right: 25.6),
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0x73D6B66D)),
            borderRadius: BorderRadius.circular(Token.raggio),
          ),
          child: Stack(
            alignment: Alignment.centerLeft,
            clipBehavior: Clip.none,
            children: [
              Text(
                datiLingua(lingua).nome,
                maxLines: 1,
                overflow: TextOverflow.clip,
                softWrap: false,
                style: Stile.sans(12.8, colore: colore),
              ),
              Positioned(
                right: -25.6 + 8.8,
                child: Text('▾', style: Stile.sans(11.2, colore: Token.brassPale)),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _scegli(BuildContext context, WidgetRef ref) async {
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
              Premibile(
                alTocco: () => Navigator.of(context).pop(l.codice),
                selezionato: l.codice == corrente,
                costruisci: (context, premuto) => Container(
                  constraints: const BoxConstraints(minHeight: 48),
                  alignment: AlignmentDirectional.centerStart,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: l.codice == corrente ? Token.plum : (premuto ? Token.mist : null),
                    border: const Border(bottom: BorderSide(color: Token.line)),
                  ),
                  child: Text(
                    l.nome,
                    style: Stile.sans(16, colore: l.codice == corrente ? const Color(0xFFFFF7E8) : Token.ink),
                  ),
                ),
              ),
          ],
        );
      },
    );
    if (scelta != null) await scegliLingua(ref, scelta);
  }
}
