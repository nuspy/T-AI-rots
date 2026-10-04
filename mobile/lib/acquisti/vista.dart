/// I pezzi comuni delle pagine che vendono nello store (prezzi, prova): l'esito dell'ultimo acquisto e la nota con
/// «Ripristina gli acquisti» (Apple chiede il bottone in ogni app che vende abbonamenti).
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../l10n/testi.dart';
import 'acquisti.dart';
import 'negozio.dart';

/// L'esito dell'ultimo acquisto nello store (verde, neutro o rosso), o niente.
class EsitoAcquistoStore extends ConsumerWidget {
  /// L'esito per lo store [negozio].
  const EsitoAcquistoStore({super.key, required this.negozio});

  /// Lo store (per il nome nei testi).
  final Negozio negozio;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final s = ref.watch(acquistiProvider);
    final e = s.esito;
    if (e == null) {
      return s.inCorso
          ? Semantics(liveRegion: true, child: Avviso(t.app_store_in_corso, sopra: 0))
          : const SizedBox.shrink();
    }
    final testo = testoEsito(t, e, negozio.nome, piano: s.piano, pacchetto: s.pacchetto);
    return switch (esitoBuono(e)) {
      true => Successo(testo, sopra: 0),
      false => Errore(testo, sopra: 0),
      null => Semantics(liveRegion: true, child: Avviso(testo, sopra: 0)),
    };
  }
}

/// «Paghi con Google Play…» e «Ripristina gli acquisti».
class NotaStore extends ConsumerWidget {
  /// La nota per lo store [negozio].
  const NotaStore({super.key, required this.negozio});

  /// Lo store.
  final Negozio negozio;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final inCorso = ref.watch(acquistiProvider.select((s) => s.inCorso));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Text(t.app_store_nota(negozio.nome), style: stilePiccolo()),
        ),
        Bottone(
          t.app_store_ripristina,
          variante: Variante.quieto,
          piccolo: true,
          an: 'store_ripristina',
          alTocco: inCorso
              ? null
              : () => unawaited(() async {
                  // I crediti vanno su un account: senza, prima si entra.
                  if (!ref.read(sessioneProvider).autenticata && !await entraDa(ref)) return;
                  await ref.read(acquistiProvider.notifier).ripristina();
                }()),
        ),
      ],
    );
  }
}
