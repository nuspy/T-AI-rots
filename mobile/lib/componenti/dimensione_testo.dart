/// La dimensione del testo scelta da chi legge (A− / A+ in alto a destra di ogni pagina, come sul sito,
/// `frontend/v2/lib/testo.tsx`): dipende dal gusto e dal dispositivo. Moltiplica la scala del testo del sistema
/// (Dynamic Type, la dimensione dei caratteri di Android), non la sostituisce. Si ricorda sul dispositivo.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../archivio.dart';
import '../l10n/testi.dart';
import '../tema/tema.dart';
import 'premibile.dart';

/// La chiave nell'archivio (la percentuale).
const String chiaveDimensioneTesto = 'tarots_testo';

/// I passi, in percentuale della scala del sistema (come `PASSI_TESTO` del sito).
const List<int> passiTesto = [70, 80, 90, 100, 110, 120, 130];

/// La percentuale scelta (100 se non c'è).
class DimensioneTestoNotifier extends Notifier<int> {
  @override
  int build() {
    final v = int.tryParse(ref.read(archivioProvider).leggi(chiaveDimensioneTesto) ?? '');
    return passiTesto.contains(v) ? v! : 100;
  }

  /// Un passo più piccolo (-1) o più grande (+1).
  void passo(int verso) {
    final i = passiTesto.indexOf(state);
    final nuovo = passiTesto[(i + verso).clamp(0, passiTesto.length - 1)];
    if (nuovo == state) return;
    state = nuovo;
    unawaited(ref.read(archivioProvider).scrivi(chiaveDimensioneTesto, nuovo == 100 ? null : '$nuovo'));
  }
}

/// La dimensione del testo.
final dimensioneTestoProvider = NotifierProvider<DimensioneTestoNotifier, int>(DimensioneTestoNotifier.new);

/// La scala del sistema per la percentuale scelta.
class ScalaTesto extends ConsumerWidget {
  /// Applica la dimensione scelta al [child] (tutta l'app).
  const ScalaTesto({super.key, required this.child});

  /// L'app.
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final percento = ref.watch(dimensioneTestoProvider);
    if (percento == 100) return child;
    final media = MediaQuery.of(context);
    final sistema = media.textScaler.scale(100) / 100;
    return MediaQuery(
      data: media.copyWith(textScaler: TextScaler.linear(sistema * percento / 100)),
      child: child,
    );
  }
}

/// A− e A+: due pulsanti da 44 px in alto a destra, sopra il primo contenuto della pagina. Le loro lettere non
/// cambiano con la dimensione che regolano.
class DimensioneTesto extends ConsumerWidget {
  /// I due pulsanti.
  const DimensioneTesto({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final percento = ref.watch(dimensioneTestoProvider);
    final i = passiTesto.indexOf(percento);
    final notifier = ref.read(dimensioneTestoProvider.notifier);
    return MediaQuery.withNoTextScaling(
      child: Semantics(
        container: true,
        label: t.comune_testo_gruppo,
        value: t.comune_testo_misura(percento),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _Bottone(segno: '−', etichetta: t.comune_testo_meno, alTocco: i > 0 ? () => notifier.passo(-1) : null),
            const SizedBox(width: 6),
            _Bottone(
              segno: '+',
              etichetta: t.comune_testo_piu,
              alTocco: i < passiTesto.length - 1 ? () => notifier.passo(1) : null,
            ),
          ],
        ),
      ),
    );
  }
}

class _Bottone extends StatelessWidget {
  const _Bottone({required this.segno, required this.etichetta, required this.alTocco});

  final String segno;
  final String etichetta;
  final VoidCallback? alTocco;

  @override
  Widget build(BuildContext context) {
    final attivo = alTocco != null;
    return Premibile(
      alTocco: alTocco,
      pulsante: true,
      etichetta: etichetta,
      raggioFuoco: 999,
      costruisci: (context, premuto) => Opacity(
        opacity: attivo ? 1 : .4,
        child: Container(
          constraints: const BoxConstraints(minWidth: 44, minHeight: 44),
          padding: const EdgeInsets.symmetric(horizontal: 8),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: premuto ? const Color(0xFFF3E8D3) : const Color(0xEBFFFCF5),
            border: Border.all(color: Token.line),
            borderRadius: BorderRadius.circular(999),
            boxShadow: const [BoxShadow(color: Color(0x1F201026), offset: Offset(0, 2), blurRadius: 8)],
          ),
          child: Text.rich(
            TextSpan(
              children: [
                const TextSpan(text: 'A'),
                TextSpan(text: segno, style: Stile.sans(13, peso: FontWeight.w600, colore: Token.ink)),
              ],
            ),
            style: Stile.sans(15, peso: FontWeight.w600, colore: Token.ink),
          ),
        ),
      ),
    );
  }
}
