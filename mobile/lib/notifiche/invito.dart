/// L'invito alle notifiche dopo aver girato la carta del giorno (`InvitoNotifiche` del sito): una domanda cortese
/// («vuoi che te la ricordiamo ogni mattina?»). Solo con un sì il telefono chiede il permesso; un «non ora» lo fa
/// tacere per un mese. Non compare se le notifiche ci sono già, se il permesso è negato o se l'app non le ha.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../l10n/testi.dart';
import '../tema/tema.dart';
import 'notifiche.dart';
import 'push.dart';

/// `.invito-notifiche`.
class InvitoNotifiche extends ConsumerStatefulWidget {
  /// L'invito.
  const InvitoNotifiche({super.key});

  @override
  ConsumerState<InvitoNotifiche> createState() => _InvitoNotificheState();
}

class _InvitoNotificheState extends ConsumerState<InvitoNotifiche> {
  bool _visibile = true;
  bool _inCorso = false;
  EsitoAttivazione? _esito;

  Future<void> _si() async {
    setState(() => _inCorso = true);
    final esito = await ref.read(notificheProvider.notifier).attiva();
    if (!mounted) return;
    if (esito == EsitoAttivazione.negato) unawaited(ref.read(notificheProvider.notifier).invitoChiuso(DateTime.now()));
    setState(() {
      _inCorso = false;
      _esito = esito;
    });
  }

  void _no() {
    unawaited(ref.read(notificheProvider.notifier).invitoChiuso(DateTime.now()));
    setState(() => _visibile = false);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final stato = ref.watch(notificheProvider);
    final autenticata = ref.watch(sessioneProvider.select((s) => s.autenticata));
    if (_esito == EsitoAttivazione.attive) {
      return Padding(padding: const EdgeInsets.only(top: 19.2), child: Successo(t.notifiche_invito_fatto, sopra: 0));
    }
    final mostra =
        _visibile &&
        autenticata &&
        stato.disponibili &&
        !stato.attive &&
        stato.permesso != PermessoPush.negato &&
        ref.read(notificheProvider.notifier).invitoDaMostrare(DateTime.now());
    if (!mostra && _esito == null) return const SizedBox.shrink();
    final errore = switch (_esito) {
      EsitoAttivazione.negato => t.app_push_negato,
      EsitoAttivazione.errore => t.notifiche_errore,
      EsitoAttivazione.nonSupportato => t.app_push_non_disponibile,
      _ => null,
    };
    return Semantics(
      container: true,
      label: t.notifiche_invito_titolo,
      child: Container(
        margin: const EdgeInsets.only(top: 19.2),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14.4),
        decoration: const BoxDecoration(
          color: Color(0xFFFFF8E8),
          border: Border(left: BorderSide(color: Token.brass, width: 3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 4.8),
              child: Text(t.notifiche_invito_titolo, style: Stile.serif(18.4, colore: Token.ink)),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 9.6),
              child: Text(t.notifiche_invito_testo, style: stilePiccolo()),
            ),
            FilaBottoni(
              children: [
                if (_esito == null)
                  Bottone(
                    _inCorso ? t.notifiche_attivazione : t.notifiche_invito_si,
                    piccolo: true,
                    an: 'notifiche_invito_si',
                    alTocco: _inCorso ? null : () => unawaited(_si()),
                  ),
                Bottone(
                  t.notifiche_invito_no,
                  variante: Variante.quieto,
                  piccolo: true,
                  an: 'notifiche_invito_no',
                  alTocco: _no,
                ),
              ],
            ),
            if (errore != null) Errore(errore, sopra: 9.6),
          ],
        ),
      ),
    );
  }
}
