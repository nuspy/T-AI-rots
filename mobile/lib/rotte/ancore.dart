/// Le ancore degli indirizzi (`/profile#privacy`, `/privacy#pv-eta`): `vai()` ricorda l'ancora con la pagina, e la
/// sezione con quell'`id` ([Ancora]), quando c'è (anche dopo che i dati sono arrivati), ci fa scorrere la pagina, come
/// il browser con un frammento.
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'percorso.dart';

/// L'ancora in attesa: la pagina (percorso interno) e l'`id`.
class AncoraInAttesa extends Notifier<({String percorso, String id})?> {
  @override
  ({String percorso, String id})? build() => null;

  /// Si va a [percorso] con l'ancora [id] (o senza: `null`).
  void imposta(String percorso, String? id) => state = id == null || id.isEmpty ? null : (percorso: percorso, id: id);

  /// La sezione l'ha raggiunta.
  void raggiunta() => state = null;
}

/// L'ancora in attesa.
final ancoraProvider = NotifierProvider<AncoraInAttesa, ({String percorso, String id})?>(AncoraInAttesa.new);

/// Una sezione con un `id`: se la pagina è stata aperta con `#id`, la si porta in vista.
class Ancora extends ConsumerStatefulWidget {
  /// La sezione [child] con l'[id].
  const Ancora({super.key, required this.id, required this.child});

  /// L'`id` della sezione.
  final String id;

  /// La sezione.
  final Widget child;

  @override
  ConsumerState<Ancora> createState() => _AncoraState();
}

class _AncoraState extends ConsumerState<Ancora> {
  void _forse(({String percorso, String id})? a) {
    if (a == null || a.id != widget.id || a.percorso != ref.read(percorsoProvider).path) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      ref.read(ancoraProvider.notifier).raggiunta();
      final ridotto = MediaQuery.disableAnimationsOf(context);
      Scrollable.ensureVisible(
        context,
        duration: ridotto ? Duration.zero : const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    });
  }

  @override
  void initState() {
    super.initState();
    _forse(ref.read(ancoraProvider));
  }

  @override
  Widget build(BuildContext context) {
    ref.listen(ancoraProvider, (_, a) => _forse(a));
    return widget.child;
  }
}
