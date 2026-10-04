/// Andare a un indirizzo del sito dall'interno dell'app, come `LinkV2` del sito.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'ancore.dart';
import 'indirizzi.dart';
import 'router.dart' show uriVisibile;

/// Apre [href] (un percorso interno, anche coi nomi della v1 o in italiano): una pagina nuova sopra quella corrente,
/// così il gesto «indietro» torna dov'eri, come nel browser. L'ancora (`#invito`) porta in vista la sezione con
/// quell'`id` ([Ancora]); sulla stessa pagina basta l'ancora.
void vai(BuildContext context, String href) {
  final parti = href.split('#');
  final senzaAncora = parti.first;
  final ancora = parti.length > 1 ? parti[1] : null;
  final uri = Uri.parse(senzaAncora.isEmpty ? '/' : senzaAncora);
  final percorso = interno(uri.path.isEmpty ? '/' : uri.path);
  final destinazione = uri.hasQuery ? '$percorso?${uri.query}' : percorso;
  final router = GoRouter.of(context);
  ProviderScope.containerOf(context, listen: false).read(ancoraProvider.notifier).imposta(percorso, ancora);
  if (uriVisibile(router.routerDelegate.currentConfiguration).toString() == destinazione) return;
  unawaited(router.push<void>(destinazione));
}
