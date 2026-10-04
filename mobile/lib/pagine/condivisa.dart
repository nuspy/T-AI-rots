/// Una lettura condivisa (`frontend/v2/pagine/condivisa.tsx`): ogni condivisione è una porta d'ingresso. Chi apre il
/// collegamento vede le parole di chi ha condiviso, la domanda, le carte e l'interpretazione — mai il nome, mai il
/// colloquio — e l'invito a cominciare la propria lettura, gratuita.
///
/// Come nel sito: dopo qualche secondo con l'app in primo piano la visita si conta (è ciò che rende «verificata» una
/// condivisione), e il collegamento si ricorda (`ricordaOrigine`) per attribuire un'eventuale iscrizione a chi l'ha
/// condiviso. Niente spazi pubblicitari.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/visitatore.dart';
import '../api/api.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/carta.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../dati/inviti.dart';
import '../l10n/testi.dart';
import '../lettura/comuni.dart' show LinguaNomi;
import '../lettura/immagine_condivisione.dart';
import '../lettura/tavolo.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'lettura_dettaglio.dart';

/// Dopo quanti secondi di lettura la visita si conta.
const int secondiDiLettura = 4;

/// I crediti d'iscrizione quando il server non li dice (`CREDITI_ISCRIZIONE`).
const int creditiIscrizionePredefiniti = 5;

/// La lettura condivisa [token].
final letturaCondivisaProvider = FutureProvider.autoDispose.family<LetturaCondivisa, String>(
  (ref, token) => ref.read(apiProvider).letturaCondivisa(token),
);

/// La pagina.
class PaginaCondivisa extends ConsumerStatefulWidget {
  /// La lettura [token].
  const PaginaCondivisa({super.key, required this.token});

  /// Il collegamento.
  final String token;

  @override
  ConsumerState<PaginaCondivisa> createState() => _PaginaCondivisaState();
}

class _PaginaCondivisaState extends ConsumerState<PaginaCondivisa> {
  Timer? _visita;
  bool _avviata = false;

  @override
  void dispose() {
    _visita?.cancel();
    super.dispose();
  }

  /// La lettura c'è: si ricorda il collegamento e, dopo qualche secondo in primo piano, si conta la visita.
  void _avvia() {
    if (_avviata) return;
    _avviata = true;
    unawaited(ricordaOrigine(ref.read(archivioProvider), widget.token));
    _visita = Timer(const Duration(seconds: secondiDiLettura), () {
      final stato = WidgetsBinding.instance.lifecycleState;
      if (!mounted || (stato != null && stato != AppLifecycleState.resumed)) return;
      unawaited(ref.read(apiProvider).registraVisita(widget.token, ref.read(visitatoreProvider)()));
    });
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lettura = ref.watch(letturaCondivisaProvider(widget.token));
    if (lettura.hasError && !lettura.hasValue) return const Pagina(sezioni: [_NonTrovata()]);
    final d = lettura.value;
    if (d == null || d.stesa == null) {
      return Pagina(sezioni: [StatoFascia(errore: d == null ? null : Exception(t.comune_err_generico))]);
    }
    WidgetsBinding.instance.addPostFrameCallback((_) => _avvia());
    final ll = linguaLettura(d.lang, ref.watch(linguaProvider));
    final invitoN = ref.watch(impostazioniProvider).value?.creditiIscrizione ?? creditiIscrizionePredefiniti;
    return MazzoAttivo(
      slug: d.mazzo,
      child: LinguaNomi(
        lingua: ll,
        child: Pagina(
          sezioni: [
            _Apertura(testo: d.shareText, lingua: ll),
            _Lettura(d: d, lingua: ll),
            _Invito(n: invitoN),
          ],
        ),
      ),
    );
  }
}

/// `.subhero.subhero-compact` con `.static-share`: le parole di chi ha condiviso, sul prugna.
class _Apertura extends StatelessWidget {
  const _Apertura({required this.testo, required this.lingua});

  final String? testo;
  final String lingua;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    final telefono = w.telefono;
    final parole = testo != null && testo!.isNotEmpty ? testo! : t.condivisa_titolo_predefinito;
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: Token.larghezzaBanda),
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.fromLTRB(
            w.gutter,
            telefono ? 16 : w.clampVw(16, 2.1, 25.6),
            w.gutter,
            telefono ? 16 : 14.4,
          ),
          decoration: const BoxDecoration(
            border: Border(bottom: BorderSide(color: Token.line)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Eyebrow(t.condivisa_eyebrow),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 760),
                child: Container(
                  width: double.infinity,
                  color: Token.plum,
                  padding: EdgeInsets.symmetric(horizontal: w.clampVw(20, 4, 32), vertical: w.clampVw(10.4, 2, 16)),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Paragrafo(
                        parole,
                        style: Stile.serif(
                          24.8,
                          stile: FontStyle.italic,
                          altezza: 1.45,
                          colore: const Color(0xFFFFF7E8),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        child: Paragrafo(
                          t.condivisa_nota,
                          style: Stile.sans(16, colore: const Color(0xFFD8C8DB), altezza: 1.6),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// La scena, il tavolo e l'interpretazione.
class _Lettura extends StatelessWidget {
  const _Lettura({required this.d, required this.lingua});

  final LetturaCondivisa d;
  final String lingua;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final stesa = d.stesa!;
    final posate = [for (final c in d.cards) Posata.da(c)];
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          ScenaLettura(
            etichetta: nomeStesaIn(stesa, lingua),
            domanda: d.question,
            lingua: lingua,
            sotto: d.speciale && d.partnerFrase != null
                ? Row(
                    children: [
                      SimboloPartner(nome: d.partnerSimbolo),
                      const SizedBox(width: 6.4),
                      Flexible(
                        child: Text(d.partnerFrase!, style: Stile.sans(16, colore: Token.ink)),
                      ),
                    ],
                  )
                : null,
          ),
          PannelloLettura(
            scuro: true,
            child: Tavolo(stesa: stesa, posate: posate, nomePartner: d.partnerFrase),
          ),
          if (d.synthesis != null && d.synthesis!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 11.2),
              child: RiquadroResponso(
                titolo: t.condivisa_l_interpretazione,
                testo: d.synthesis!,
                avvertenza: d.disclaimer,
              ),
            ),
        ],
      ),
    );
  }
}

/// `.final`: l'invito a cominciare, sul verderame con la grande stella.
class _Invito extends ConsumerWidget {
  const _Invito({required this.n});

  final int n;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    final sessione = ref.watch(sessioneProvider);
    return ClipRect(
      child: ColoredBox(
        color: Token.verdigris,
        child: Stack(
          children: [
            Positioned(
              right: w * .05,
              bottom: -64,
              child: ExcludeSemantics(
                child: Text('✦', style: Stile.serif(240, altezza: 1, colore: const Color(0x40D6B66D))),
              ),
            ),
            Fascia(
              child: Column(
                children: [
                  Semantics(
                    header: true,
                    child: TestoBilanciato(
                      t.condivisa_invito_titolo,
                      stile: Stile.display(w).copyWith(color: const Color(0xFFFFF9EE)),
                      maxCh: 16,
                      allinea: TextAlign.center,
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(top: 24, bottom: 32),
                    child: ConstrainedBox(
                      constraints: BoxConstraints(
                        maxWidth: larghezzaCh(Stile.sans(16), MediaQuery.textScalerOf(context)) * 42,
                      ),
                      child: Paragrafo(
                        t.condivisa_invito_testo(n),
                        textAlign: TextAlign.center,
                        style: Stile.sans(16, colore: const Color(0xFFDCEBE5), altezza: 1.6),
                      ),
                    ),
                  ),
                  Wrap(
                    alignment: WrapAlignment.center,
                    spacing: 9.6,
                    runSpacing: 9.6,
                    children: [
                      Bottone(
                        t.condivisa_inizia,
                        href: '${R.leggi}?source=share',
                        variante: Variante.ottone,
                        an: 'cta_condivisa',
                      ),
                      if (!sessione.autenticata && sessione.pronta)
                        Bottone(
                          t.condivisa_iscriviti,
                          variante: Variante.chiaro,
                          an: 'cta_iscrizione',
                          anProprieta: const {'dove': 'condivisa'},
                          alTocco: () => unawaited(entraDa(ref)),
                        ),
                      Bottone(t.condivisa_giorno, href: R.giorno, variante: Variante.chiaro),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Il collegamento non c'è più (spento da chi l'aveva condiviso).
class _NonTrovata extends StatelessWidget {
  const _NonTrovata();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Eyebrow(t.condivisa_eyebrow),
          Semantics(
            header: true,
            child: TestoBilanciato(
              t.condivisa_non_trovata_titolo,
              stile: Stile.serif(w.clampVw(32, 4, 54.4), altezza: 1.05, em: -.055),
              maxCh: 15,
            ),
          ),
          IntroSezione(t.condivisa_non_trovata_testo),
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Bottone(t.condivisa_inizia, href: '${R.leggi}?source=share', variante: Variante.ottone),
          ),
        ],
      ),
    );
  }
}
