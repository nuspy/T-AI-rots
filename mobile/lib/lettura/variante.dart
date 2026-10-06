/// v9.5, la prova delle due versioni della lettura (90/10), come lo smistatore del sito (`frontend/proxy.ts`): `/read`
/// non è una pagina ma sceglie fra `/read-chat` (tutta in chat) e `/read-classic` (la classica), tenendo i parametri.
///
/// La scelta resta legata alla persona: sul dispositivo (in [Archivio], come il cookie `tarots_lettura` del sito) e,
/// con un account, nel profilo (`variante_lettura`, fissata dal server alla prima lettura): la pagina della lettura
/// riallinea il dispositivo al profilo. La quota della chat arriva dalla console (`lettura_chat_percentuale`).
library;

import 'dart:async';
import 'dart:math' as math;

import '../archivio.dart';
import '../rotte/percorsi.dart';

/// La chiave nell'archivio.
const String chiaveVarianteLettura = 'tarots_lettura';

/// Le due versioni, coi nomi del server e delle statistiche.
abstract final class VarianteLettura {
  /// Tutta in chat.
  static const String chat = 'chat';

  /// La classica.
  static const String classica = 'classica';

  /// Vero per un nome valido.
  static bool valida(String? v) => v == chat || v == classica;

  /// Il percorso della versione [v].
  static String percorso(String v) => v == chat ? R.letturaChat : R.letturaClassica;
}

/// La versione di questo dispositivo: quella salvata, o una sorteggiata con la quota [percentualeChat] (0–100) e
/// salvata subito, così resta la stessa alle aperture seguenti.
String varianteDelDispositivo(Archivio archivio, int percentualeChat, {math.Random? caso}) {
  final salvata = archivio.leggi(chiaveVarianteLettura);
  if (VarianteLettura.valida(salvata)) return salvata!;
  final quota = percentualeChat.clamp(0, 100);
  final scelta = (caso ?? math.Random()).nextInt(100) < quota ? VarianteLettura.chat : VarianteLettura.classica;
  unawaited(archivio.scrivi(chiaveVarianteLettura, scelta));
  return scelta;
}

/// `/read?…` → `/read-chat?…` o `/read-classic?…`; `null` per ogni altro percorso.
String? smistaLettura(Uri uri, Archivio archivio, int percentualeChat, {math.Random? caso}) {
  final percorso = uri.path.replaceAll(RegExp(r'/$'), '');
  if (percorso != R.leggi) return null;
  final verso = VarianteLettura.percorso(varianteDelDispositivo(archivio, percentualeChat, caso: caso));
  return uri.hasQuery ? '$verso?${uri.query}' : verso;
}
