/// Il genere e la casella «persona trans» (`CampiGenere` e `CasellaTrans` di `frontend/v2/lettura/persone.tsx`), per la
/// sezione «Genere» del profilo.
///
/// «Persona trans» è un dato dell'art. 9 GDPR (Fase 1): si usa solo col consenso esplicito `dati_particolari`.
/// Spuntando la casella senza il consenso si apre sotto una richiesta breve (`.consenso-inline`); «Non ora» lascia la
/// casella vuota. Togliere la spunta non chiede niente.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/errori.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../consensi/consensi.dart';
import '../l10n/testi.dart';
import '../tema/tema.dart';
import 'comuni.dart';
import 'dati_account.dart';

/// I generi, nell'ordine del sito.
const List<String> generi = ['donna', 'uomo', 'non_binario', 'altro', 'non_dice'];

/// Il genere, la sua descrizione libera e la casella «persona trans».
class CampiGenere extends StatelessWidget {
  /// I campi.
  const CampiGenere({
    super.key,
    required this.genere,
    required this.altro,
    required this.trans,
    required this.alGenere,
    required this.alAltro,
    required this.alTrans,
  });

  /// Il genere scelto (vuoto: nessuno).
  final String genere;

  /// La descrizione di «altro».
  final TextEditingController altro;

  /// La casella.
  final bool trans;

  /// Il genere cambiato.
  final ValueChanged<String> alGenere;

  /// La descrizione cambiata.
  final ValueChanged<String> alAltro;

  /// La casella cambiata.
  final ValueChanged<bool> alTrans;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    final scelta = CampoScelta<String>(
      etichetta: t.lettura_persone_genere,
      voci: [('', t.lettura_persone_genere_scegli), for (final g in generi) (g, t.letturaGeneri[g] ?? g)],
      valore: genere,
      alCambio: alGenere,
    );
    final descrizione = CampoTesto(
      etichetta: t.lettura_persone_genere_altro,
      controllore: altro,
      lunghezzaMassima: 30,
      alCambio: alAltro,
    );
    // `.form-grid`: due colonne (`gap: 0 1rem`) oltre 760 px, una sotto.
    final griglia = genere != 'altro'
        ? scelta
        : w.telefono
        ? Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [scelta, descrizione])
        : Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(child: scelta),
              const SizedBox(width: 16),
              Expanded(child: descrizione),
            ],
          );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        griglia,
        CasellaTrans(trans: trans, alTrans: alTrans),
      ],
    );
  }
}

/// La casella «persona trans» col consenso ai dati particolari chiesto al momento.
class CasellaTrans extends ConsumerStatefulWidget {
  /// La casella.
  const CasellaTrans({super.key, required this.trans, required this.alTrans});

  /// Spuntata.
  final bool trans;

  /// Il nuovo valore.
  final ValueChanged<bool> alTrans;

  @override
  ConsumerState<CasellaTrans> createState() => _CasellaTransState();
}

class _CasellaTransState extends ConsumerState<CasellaTrans> {
  bool _chiede = false;
  bool _inCorso = false;
  bool _errore = false;

  bool get _dato {
    if (ref.watch(consensiProvider).accettato('dati_particolari')) return true;
    return ref.watch(consensiAccountProvider).value?['dati_particolari'] == 'accettato';
  }

  Future<void> _acconsenti() async {
    setState(() {
      _inCorso = true;
      _errore = false;
    });
    try {
      await ref.read(consensiProvider.notifier).scegli({'dati_particolari': 'accettato'});
      ref.invalidate(consensiAccountProvider);
      if (!mounted) return;
      setState(() => _chiede = false);
      widget.alTrans(true);
    } on ErroreApi {
      if (mounted) setState(() => _errore = true);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final dato = _dato;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Casella(
          valore: widget.trans,
          titolo: t.lettura_persone_trans,
          alCambio: (v) {
            if (v && !dato) {
              setState(() => _chiede = true);
              return;
            }
            setState(() => _chiede = false);
            widget.alTrans(v);
          },
        ),
        if (_chiede)
          Semantics(
            container: true,
            label: t.lettura_art9_titolo,
            child: Container(
              margin: const EdgeInsets.fromLTRB(30.4, 0, 0, 12.8),
              padding: const EdgeInsets.symmetric(horizontal: 14.4, vertical: 11.2),
              decoration: const BoxDecoration(
                color: Color(0xFFF3F7F2),
                border: Border(left: BorderSide(color: Token.verdigris, width: 3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: TestoConGrassetto(grassetto: '${t.lettura_art9_titolo}. ', resto: t.lettura_art9_testo),
                  ),
                  FilaBottoni(
                    children: [
                      Bottone(
                        t.lettura_art9_si,
                        piccolo: true,
                        alTocco: _inCorso ? null : () => unawaited(_acconsenti()),
                      ),
                      Bottone(
                        t.lettura_art9_no,
                        piccolo: true,
                        variante: Variante.quieto,
                        alTocco: () => setState(() => _chiede = false),
                      ),
                    ],
                  ),
                  if (_errore) Errore(t.comune_err_operazione),
                ],
              ),
            ),
          ),
      ],
    );
  }
}
