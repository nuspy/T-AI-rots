/// L'accesso ai testi dell'app (generati dai dizionari della v2) da qualunque widget: `context.t.comune_entra`.
library;

import 'package:flutter/widgets.dart';

import 'generato/app_localizations.dart';

export 'generato/app_localizations.dart';
export 'liste.g.dart';

/// I testi della lingua corrente.
extension Testi on BuildContext {
  /// Il dizionario (`t` del sito).
  AppLocalizations get t => AppLocalizations.of(this);
}
