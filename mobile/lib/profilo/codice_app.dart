/// «Hai già un account sul sito?» (Fase 6): l'altra metà di «Hai un codice dall'app?» del profilo del sito
/// (`frontend/v2/componenti/accessi-collegati.tsx`).
///
/// Nell'app si entra solo con Google (Android) o con Apple (iPhone). Con «Nascondi la mia email» di Apple, o con un
/// social diverso da quello usato sul sito, l'app crea un account nuovo. Qui si crea un codice (`POST
/// /me/collega/codice`): scritto nel profilo del sito entro dieci minuti, l'accesso dell'app passa all'account del sito
/// con ciò che c'era. Da quel momento il refresh token dell'app non vale più: la sessione si interrompe e l'app propone
/// di rientrare ([AvvisoSessione]), e si arriva nell'account vecchio.
library;

import 'dart:async';

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../tema/tema.dart';
import 'comuni.dart';

const Map<String, String> _nomi = {'apple': 'Apple', 'google': 'Google'};

/// La sezione del profilo.
class SezioneCodiceApp extends ConsumerStatefulWidget {
  /// La sezione.
  const SezioneCodiceApp({super.key});

  @override
  ConsumerState<SezioneCodiceApp> createState() => _SezioneCodiceAppState();
}

class _SezioneCodiceAppState extends ConsumerState<SezioneCodiceApp> {
  CodiceCollegamento? _codice;
  String? _errore;
  bool _inCorso = false;
  bool _copiato = false;

  Future<void> _crea() async {
    final t = context.t;
    setState(() {
      _inCorso = true;
      _errore = null;
      _copiato = false;
    });
    try {
      final c = await ref.read(apiProvider).creaCodiceCollegamento();
      if (mounted) setState(() => _codice = c);
    } on ErroreApi catch (e) {
      final d = e.dettaglio;
      final provider = d is Map && d['provider'] is List
          ? (d['provider'] as List).map((p) => _nomi['$p'] ?? '$p').join(', ')
          : '';
      final testi = t.profiloAccCodiceErrori(provider: provider);
      if (mounted) setState(() => _errore = testi[e.codice] ?? (e.stato == 401 ? e.messaggio(t) : testi['generico']));
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final nascosta = emailNascosta(ref.watch(sessioneProvider.select((s) => s.email)));
    final c = _codice;
    final scade = DateTime.tryParse(c?.scadeIl ?? '');
    return Sezione(
      id: 'accessi',
      titolo: t.app_codice_titolo,
      children: [
        if (nascosta) Avviso(t.app_codice_relay, sopra: 0),
        TestoPiccolo(t.app_codice_testo, sopra: nascosta ? 12.8 : 0),
        if (c != null) ...[
          Semantics(
            label: c.codice.split('').join(' '),
            // `.invite-code`: grande, serif, spaziato; si copia col bottone accanto.
            child: Text(c.codice, style: Stile.serif(28.8, colore: Token.plum, em: .12)),
          ),
          if (scade != null) TestoPiccolo(t.app_codice_valido(ora(scade, lingua)), tenue: true, sopra: 6.4),
        ],
        FilaBottoni(
          children: [
            if (c != null)
              Bottone(
                _copiato ? t.comune_copiato : t.comune_copia,
                piccolo: true,
                alTocco: () async {
                  await Clipboard.setData(ClipboardData(text: c.codice));
                  if (mounted) setState(() => _copiato = true);
                },
              ),
            Bottone(
              c == null ? t.app_codice_crea : t.app_codice_nuovo,
              piccolo: true,
              variante: c == null ? Variante.prugna : Variante.quieto,
              an: 'collega_codice',
              alTocco: _inCorso ? null : () => unawaited(_crea()),
            ),
          ],
        ),
        if (_errore != null) Errore(_errore!),
      ],
    );
  }
}

/// L'avviso della sessione interrotta (il refresh token non vale più): spiega e propone di rientrare.
class AvvisoSessione extends ConsumerWidget {
  /// Sopra [child].
  const AvvisoSessione({super.key, required this.child});

  /// L'app.
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final interrotta = ref.watch(sessioneProvider.select((s) => s.interrotta));
    if (!interrotta) return child;
    final t = context.t;
    final sessione = ref.read(sessioneProvider.notifier);
    return Stack(
      children: [
        child,
        FinestraModale(
          titolo: t.app_sessione_spostata_titolo,
          alChiudi: sessione.avvisoLetto,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(t.app_sessione_spostata, style: Stile.sans(16, colore: Token.ink)),
              ),
              FilaBottoni(
                children: [
                  Bottone(
                    t.app_sessione_entra,
                    variante: Variante.ottone,
                    alTocco: () {
                      sessione.avvisoLetto();
                      unawaited(entraDa(ref));
                    },
                  ),
                  Bottone(t.comune_chiudi, variante: Variante.quieto, alTocco: sessione.avvisoLetto),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}
