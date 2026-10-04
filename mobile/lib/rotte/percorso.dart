/// La rotta corrente (il percorso interno, senza query): la testata accende la sua voce, i crediti si rileggono a ogni
/// cambio di pagina, le statistiche contano la pagina. La aggiorna il router (`router.dart`).
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

/// La rotta corrente.
class PercorsoCorrente extends Notifier<Uri> {
  @override
  Uri build() => Uri(path: '/');

  /// La rotta è cambiata.
  void cambia(Uri uri) {
    if (uri.toString() != state.toString()) state = uri;
  }
}

/// La rotta corrente.
final percorsoProvider = NotifierProvider<PercorsoCorrente, Uri>(PercorsoCorrente.new);
