/// Ciò che l'app chiede al primo avvio, sopra la pagina:
///
/// 1. **la lingua dell'app** (9/10/2026, `lingua/scelta_lingua_app.dart`): per prima, così il resto arriva nella lingua
///    scelta; la lingua di lettura dei contenuti (la traduzione sul telefono) la segue, senza una domanda a parte;
/// 2. **i consensi** (il banner del sito, `banner-cookie.tsx`): un foglio in basso con gli stessi tre comandi con lo
///    stesso peso — «Accept all», «Reject all», «Choose» — e, scegliendo, le categorie una per una con la nota sui
///    dati tecnici; finché non si sceglie la pagina resta usabile, come nel sito. Dove il banner parla di cookie e di
///    browser l'app ha testi suoi, sui dati del dispositivo (la sezione `app` dei dizionari, `frontend/v2/i18n/*/app.ts`);
/// 3. **l'età minima** (`privacy-accesso.tsx`): «ho almeno N anni», in un dialogo; «Not now» lo chiude per questa
///    volta.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/modale.dart';
import '../componenti/oracolo.dart' show altezzaOracoloProvider;
import '../componenti/premibile.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../lingua/scelta_lingua_app.dart';
import '../rotte/percorsi.dart';
import '../rotte/router.dart';
import '../tema/tema.dart';
import 'consensi.dart';
import 'eta.dart';

/// Il primo avvio sopra l'app [child].
class PrimoAvvio extends ConsumerWidget {
  /// Sopra [child].
  const PrimoAvvio({super.key, required this.child});

  /// L'app.
  final Widget child;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final consensi = ref.watch(consensiProvider);
    final eta = ref.watch(etaProvider);
    final anni = ref.watch(etaMinimaProvider).value;
    final Widget? sopra;
    if (ref.watch(linguaDaChiedereProvider)) {
      // Per prima la lingua: consensi ed età arrivano poi nella lingua scelta.
      sopra = const DialogoLinguaApp();
    } else if (consensi.daChiedere) {
      // Sopra la barra dell'oracolo, come il banner del sito (`bottom: var(--oracolo-h)`).
      final barra = ref.watch(altezzaOracoloProvider);
      final media = MediaQuery.of(context);
      sopra = Padding(
        padding: EdgeInsets.only(bottom: barra),
        child: MediaQuery(
          // Lo spazio del foglio è quello sopra la barra (che ha già la sua safe area in basso).
          data: media.copyWith(
            size: Size(media.size.width, media.size.height - barra),
            padding: barra > 0 ? media.padding.copyWith(bottom: 0) : media.padding,
          ),
          child: const Align(alignment: Alignment.bottomCenter, child: FoglioConsensi()),
        ),
      );
    } else if (anni != null && eta.daChiedere(anni)) {
      sopra = DialogoEta(anni: anni);
    } else {
      sopra = null;
    }
    return Stack(children: [child, ?sopra]);
  }
}

/// Un collegamento alla privacy dal primo avvio (che sta sopra il navigatore: va al router direttamente).
class _LinkPrivacy extends ConsumerWidget {
  const _LinkPrivacy({required this.testo, required this.stile});

  final String testo;
  final TextStyle stile;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Premibile(
      collegamento: true,
      alTocco: () => unawaited(ref.read(routerProvider).push<void>(R.privacy)),
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 44),
        child: Align(
          alignment: AlignmentDirectional.centerStart,
          widthFactor: 1,
          heightFactor: 1,
          child: TestoSottolineato(testo, stile: stile, colore: premuto ? Token.verdigris : Token.plum),
        ),
      ),
    );
  }
}

/// Il foglio dei consensi.
class FoglioConsensi extends ConsumerStatefulWidget {
  /// Il foglio.
  const FoglioConsensi({super.key});

  @override
  ConsumerState<FoglioConsensi> createState() => _FoglioConsensiState();
}

class _FoglioConsensiState extends ConsumerState<FoglioConsensi> {
  bool _aperto = false;
  bool _inCorso = false;
  final Map<String, bool> _scelte = {};

  bool _acceso(String c) => _scelte[c] ?? ref.read(consensiProvider).accettato(c);

  Future<void> _registra(Map<String, String> valori) async {
    setState(() => _inCorso = true);
    try {
      await ref.read(consensiProvider.notifier).scegli(valori);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  Future<void> _tutte(String valore) => _registra({for (final c in categorieApp) c: valore});

  Future<void> _salva() => _registra({for (final c in categorieApp) c: _acceso(c) ? 'accettato' : 'rifiutato'});

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final piccolo = w.piccolo;
    final etichette = {
      'statistiche': (titolo: t.app_consenso_statistiche, testo: t.app_consenso_statistiche_testo),
      'google_analytics': (titolo: t.app_consenso_google, testo: t.app_consenso_google_testo),
    };
    final testo = Stile.sans(13.76, colore: Token.inkSoft, altezza: 1.6);
    final abilitato = !_inCorso;
    VoidCallback? azione(Future<void> Function() f) => abilitato ? () => unawaited(f()) : null;

    final comandi = _aperto
        ? [Bottone(t.comune_consenso_salva, piccolo: true, pieno: piccolo, alTocco: azione(_salva))]
        : [
            Bottone(
              t.comune_consenso_accetta_tutto,
              piccolo: true,
              pieno: piccolo,
              alTocco: azione(() => _tutte('accettato')),
            ),
            Bottone(
              t.comune_consenso_rifiuta_tutto,
              piccolo: true,
              pieno: piccolo,
              alTocco: azione(() => _tutte('rifiutato')),
            ),
            Bottone(
              t.comune_consenso_scegli,
              piccolo: true,
              pieno: piccolo,
              variante: Variante.quieto,
              alTocco: abilitato ? () => setState(() => _aperto = true) : null,
            ),
          ];

    // `.cookie-comandi`: sul telefono due colonne, il terzo comando a tutta larghezza; più largo, una fila.
    final Widget fila;
    if (piccolo && comandi.length == 3) {
      fila = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Expanded(child: comandi[0]),
              const SizedBox(width: 9.6),
              Expanded(child: comandi[1]),
            ],
          ),
          const SizedBox(height: 9.6),
          comandi[2],
        ],
      );
    } else {
      fila = Row(
        children: [
          for (var i = 0; i < comandi.length; i++) ...[
            if (i > 0) const SizedBox(width: 9.6),
            Expanded(child: comandi[i]),
          ],
        ],
      );
    }

    final contenuto = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 6.4),
          child: Semantics(header: true, child: Text(t.app_consensi_titolo, style: Stile.serif(16.8))),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 12.8),
          child: Wrap(
            crossAxisAlignment: WrapCrossAlignment.end,
            children: [
              Text(t.app_consensi_testo, style: testo),
              _LinkPrivacy(testo: '${t.comune_cookie_leggi}.', stile: testo),
            ],
          ),
        ),
        if (_aperto) ...[
          for (final c in categorieApp)
            Casella(
              valore: _acceso(c),
              alCambio: (v) => setState(() => _scelte[c] = v),
              titolo: etichette[c]!.titolo,
              testo: etichette[c]!.testo,
            ),
          Padding(
            padding: const EdgeInsets.only(top: 6.4, bottom: 9.6),
            child: Text(t.app_consenso_tecnici, style: Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6)),
          ),
        ],
        fila,
      ],
    );

    return Semantics(
      scopesRoute: true,
      namesRoute: true,
      label: t.app_consensi_titolo,
      explicitChildNodes: true,
      child: Container(
        width: piccolo ? double.infinity : 440,
        margin: piccolo ? EdgeInsets.zero : EdgeInsets.only(left: 16, bottom: 16 + media.padding.bottom),
        constraints: BoxConstraints(maxHeight: media.size.height - 32 - media.padding.top),
        decoration: BoxDecoration(
          color: Token.paperLight,
          border: Border(
            top: const BorderSide(color: Token.verdigris, width: 3),
            left: piccolo ? BorderSide.none : const BorderSide(color: Token.line),
            right: piccolo ? BorderSide.none : const BorderSide(color: Token.line),
            bottom: piccolo ? BorderSide.none : const BorderSide(color: Token.line),
          ),
          boxShadow: const [BoxShadow(color: Color(0x40201026), offset: Offset(0, 20), blurRadius: 44)],
        ),
        child: SingleChildScrollView(
          padding: piccolo
              ? EdgeInsets.fromLTRB(
                  media.padding.left > 16 ? media.padding.left : 16,
                  16,
                  media.padding.right > 16 ? media.padding.right : 16,
                  media.padding.bottom > 16 ? media.padding.bottom : 16,
                )
              : const EdgeInsets.all(19.2),
          child: DefaultTextStyle(style: Stile.corpo, child: contenuto),
        ),
      ),
    );
  }
}

/// «Ho almeno N anni».
class DialogoEta extends ConsumerStatefulWidget {
  /// Per l'età minima [anni].
  const DialogoEta({super.key, required this.anni});

  /// L'età minima del paese.
  final int anni;

  @override
  ConsumerState<DialogoEta> createState() => _DialogoEtaState();
}

class _DialogoEtaState extends ConsumerState<DialogoEta> {
  bool _spuntata = false;
  bool _inCorso = false;

  Future<void> _conferma() async {
    setState(() => _inCorso = true);
    try {
      await ref.read(etaProvider.notifier).conferma(widget.anni);
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final testo = Stile.sans(16, altezza: 1.6, colore: Token.ink);
    final piccolo = Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6);
    return FinestraModale(
      titolo: t.comune_eta_titolo,
      alChiudi: () => ref.read(etaProvider.notifier).rimanda(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(t.comune_eta_testo(widget.anni), style: testo),
          ),
          Casella(
            valore: _spuntata,
            alCambio: (v) => setState(() => _spuntata = v),
            titolo: t.comune_eta_dichiaro(widget.anni),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 13.44),
            child: Wrap(
              crossAxisAlignment: WrapCrossAlignment.end,
              children: [
                Text('${t.comune_eta_perche} ', style: piccolo),
                _LinkPrivacy(testo: '${t.comune_cookie_leggi}.', stile: piccolo),
              ],
            ),
          ),
          FilaBottoni(
            children: [
              Bottone(t.comune_eta_conferma, alTocco: _spuntata && !_inCorso ? () => unawaited(_conferma()) : null),
              Bottone(
                t.comune_eta_non_ora,
                variante: Variante.quieto,
                alTocco: () => ref.read(etaProvider.notifier).rimanda(),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
