/// I dati delle schermate, come gli hook di `frontend/v2/lib/dati.ts`: ogni lettura è un provider, che le schermate
/// osservano (caricamento, errore, dati).
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../modelli/cassa.dart';
import '../modelli/pubblici.dart';
import '../notifiche/fuso.dart';
import '../rotte/percorso.dart';
import 'carrello.dart';

export 'carrello.dart';

/// Il saldo dei crediti per la testata: si rilegge a ogni cambio di pagina (una lettura consuma crediti), come
/// `useConto([percorso])` del sito. `null` senza sessione o se non si sa.
final saldoProvider = FutureProvider<int?>((ref) async {
  ref.watch(percorsoProvider);
  if (!ref.watch(sessioneProvider.select((s) => s.autenticata))) return null;
  try {
    return await ref.read(apiProvider).saldo();
  } on ErroreApi {
    return null;
  }
});

/// I pezzi nel carrello (il segno sull'icona della testata).
final pezziCarrelloProvider = Provider<int>((ref) => ref.watch(carrelloProvider).fold(0, (s, v) => s + v.quantita));

/// Il conto (saldo, abbonamento, uso dei limiti, prova), nella lingua dell'interfaccia: `useConto()` del sito. Si
/// rilegge a ogni cambio di pagina, come il saldo; `null` senza sessione.
final contoProvider = FutureProvider<Conto?>((ref) async {
  ref.watch(percorsoProvider);
  final lingua = ref.watch(linguaProvider);
  if (!ref.watch(sessioneProvider.select((s) => s.autenticata))) return null;
  return ref.read(apiProvider).conto(lingua);
});

/// Le impostazioni pubbliche degli abbonamenti (il banner e i numeri della prova), una volta per avvio.
final impostazioniAbbonamentiProvider = FutureProvider<ImpostazioniAbbonamenti?>((ref) async {
  try {
    return await ref.read(apiProvider).impostazioniAbbonamenti();
  } on ErroreApi {
    // un backend senza la Fase 2b: niente banner, niente prova
    return null;
  }
});

/// I mazzi del negozio nella lingua dell'interfaccia.
final mazziProvider = FutureProvider<List<Mazzo>>((ref) {
  final lingua = ref.watch(linguaProvider);
  return ref.read(apiProvider).mazzi(lingua);
});

/// Abbonamenti e pacchetti nella lingua dell'interfaccia.
final pianiProvider = FutureProvider<List<Piano>>((ref) {
  final lingua = ref.watch(linguaProvider);
  return ref.read(apiProvider).piani(lingua);
});

/// Il profilo (con un account).
final profiloProvider = FutureProvider<Profilo?>((ref) async {
  if (!ref.watch(sessioneProvider.select((s) => s.autenticata))) return null;
  return ref.read(apiProvider).profilo();
});

/// I numeri del regalo d'iscrizione e dell'invito.
final impostazioniProvider = FutureProvider<ImpostazioniPubbliche>(
  (ref) => ref.read(apiProvider).impostazioniPubbliche(),
);

/// La carta di oggi per tutti, nella lingua dei contenuti.
final cartaOggiProvider = FutureProvider<CartaOggi>((ref) {
  final lingua = ref.watch(linguaProvider.select(linguaContenuti));
  return ref.read(apiProvider).cartaDiOggi(lingua);
});

/// La carta personale di oggi (con un account).
final cartaDelGiornoProvider = FutureProvider<CartaDelGiorno>((ref) async {
  ref.watch(sessioneProvider.select((s) => s.autenticata));
  // Il giorno locale del telefono (Fase 9), come `cartaDelGiornoLocale` del sito.
  final fuso = await ref.watch(fusoProvider.future);
  return ref.read(apiProvider).cartaDelGiorno(fuso: fuso);
});

/// I nove articoli del diario di una pagina (il contesto come stringa di query: `carta=maj-17`, vuota per la home).
final noveProvider = FutureProvider.family<Nove, String>((ref, contesto) {
  ref.watch(linguaProvider);
  return ref.read(apiProvider).nove(contesto: Uri.splitQueryString(contesto));
});

/// Lo slug del mazzo predefinito (il Thoth), per il collegamento della home.
final mazzoPredefinitoProvider = FutureProvider<String?>((ref) {
  final lingua = ref.watch(linguaProvider);
  return ref.read(apiProvider).slugMazzoPredefinito(lingua);
});
