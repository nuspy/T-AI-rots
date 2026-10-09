/// Il primo avvio, prima di tutto (9/10/2026): la lingua dell'app, fra le quindici del sito. Si chiede finché nessuno
/// l'ha scelta (né qui, né dal selettore, né dal profilo dell'account), prima dei consensi e dell'età, così anche quelli
/// arrivano nella lingua giusta.
///
/// Il titolo, poi l'elenco «IT · Italiano» in un riquadro che scorre da sé (con già segnata la lingua del telefono, o
/// quella suggerita dal paese), e sotto il riquadro «Accetta», sempre in vista. I testi del dialogo seguono la lingua
/// segnata. Accettare è come scegliere dal selettore (`scegliLingua`: si ricorda, e con un account va nel profilo).
///
/// La lingua di lettura dei contenuti segue quella dell'app: se non è l'inglese e il telefono sa tradurre, il suo
/// modello (circa 30 MB) si scarica qui, come faceva la vecchia domanda a parte; se non riesce, si va avanti lo stesso
/// e si riprova quando si apre un contenuto.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/modale.dart';
import '../componenti/selettore_lingua.dart';
import '../l10n/testi.dart';
import '../tema/tema.dart';
import '../traduzione/lingua_contenuti.dart';
import '../traduzione/motore.dart';
import 'lingua.dart';
import 'lingua_profilo.dart';

/// Il dialogo del primo avvio (sopra l'app, senza ✕: si chiude scegliendo).
class DialogoLinguaApp extends ConsumerStatefulWidget {
  /// Il dialogo.
  const DialogoLinguaApp({super.key});

  @override
  ConsumerState<DialogoLinguaApp> createState() => _DialogoLinguaAppState();
}

class _DialogoLinguaAppState extends ConsumerState<DialogoLinguaApp> {
  /// La lingua toccata; finché non se ne tocca una vale quella corrente (telefono o paese, che può arrivare dopo).
  String? _scelta;
  bool _scarico = false;
  bool _errore = false;
  final GlobalKey _chiaveScelta = GlobalKey(debugLabel: 'lingua-scelta');

  String get _segnata => _scelta ?? ref.read(linguaProvider);

  Future<void> _accetta() async {
    final lingua = _segnata;
    // La lingua di lettura la segue (se non se n'è scelta un'altra): il modello si scarica prima di chiudere.
    final propria = ref.read(linguaContenutiProvider) != ref.read(linguaProvider);
    final motore = ref.read(motoreTraduzioneProvider);
    if (!_errore && !propria && lingua != 'en' && motore.disponibile && lingueMlKit.contains(lingua)) {
      setState(() {
        _scarico = true;
        _errore = false;
      });
      var riuscito = false;
      try {
        riuscito = await motore.scarica(lingua);
      } on Object {
        riuscito = false;
      }
      if (!mounted) return;
      if (!riuscito) {
        // Dopo un errore il pulsante tiene la scelta: il modello si riscarica alla prima pagina tradotta.
        setState(() {
          _scarico = false;
          _errore = true;
        });
        return;
      }
    }
    await scegliLingua(ref, lingua);
  }

  @override
  Widget build(BuildContext context) {
    final corrente = ref.watch(linguaProvider);
    final segnata = _scelta ?? corrente;
    // I testi nella lingua segnata: chi non legge quella del telefono vede subito la sua.
    final t = lookupAppLocalizations(Locale(segnata));
    final Widget comandi;
    if (_scarico) {
      comandi = Semantics(
        liveRegion: true,
        child: Row(
          children: [
            const Puntini(colore: Token.brass),
            const SizedBox(width: 9.6),
            Expanded(
              child: Text(t.app_lingua_scarico(datiLingua(segnata).nome), style: Stile.sans(14.4, altezza: 1.5)),
            ),
          ],
        ),
      );
    } else {
      comandi = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_errore) ...[Errore(t.app_lingua_errore, sopra: 0), const SizedBox(height: 12)],
          ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 48),
            child: Bottone(
              _errore ? t.app_lingua_continua : t.app_lingua_app_accetta,
              variante: Variante.prugna,
              pieno: true,
              an: 'lingua_app',
              anProprieta: {'lingua': segnata},
              alTocco: () => unawaited(_accetta()),
            ),
          ),
        ],
      );
    }
    return FinestraModale(
      titolo: t.app_lingua_app_titolo,
      scorre: false,
      child: RiquadroElenco(
        etichetta: t.comune_aria_lingua,
        selezionata: _chiaveScelta,
        voci: [
          for (final l in lingue)
            VoceLingua(
              key: l.codice == segnata ? _chiaveScelta : ValueKey(l.codice),
              lingua: l,
              scelta: l.codice == segnata,
              alTocco: _scarico
                  ? null
                  : () => setState(() {
                      _scelta = l.codice;
                      _errore = false;
                    }),
            ),
        ],
        comandi: comandi,
      ),
    );
  }
}
