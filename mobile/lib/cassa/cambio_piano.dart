/// Il cambio di piano (`frontend/v2/componenti/cambio-piano.tsx`, Fase 2b), in un dialogo. Un upgrade parte subito e
/// si paga col conguaglio, in tre righe che chiunque può rifare a mano: il valore residuo dell'abbonamento
/// (sottratto), il nuovo abbonamento (con lo sconto del rinnovo automatico, se scelto), il totale; il pagamento si apre
/// nel browser (`pagamentoInSospesoProvider`). Un downgrade si programma per la fine del periodo già pagato. Gli
/// abbonamenti degli store non passano di qui: lì decide lo store.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'pagamento.dart';

/// Apre il dialogo del cambio verso [piano] (mensile o [annuale]); [alFatto] dopo un downgrade programmato.
Future<void> apriCambioPiano(
  BuildContext context, {
  required Piano piano,
  required bool annuale,
  required num scontoRinnovo,
  VoidCallback? alFatto,
}) => apriModale<void>(
  context,
  titolo: context.t.abbonamento_cambio_titolo(piano.nome),
  costruisci: (context) => CambioPiano(piano: piano, annuale: annuale, scontoRinnovo: scontoRinnovo, alFatto: alFatto),
);

/// Il contenuto del dialogo.
class CambioPiano extends ConsumerStatefulWidget {
  /// Il cambio verso [piano].
  const CambioPiano({super.key, required this.piano, required this.annuale, required this.scontoRinnovo, this.alFatto});

  /// Il piano nuovo.
  final Piano piano;

  /// Annuale.
  final bool annuale;

  /// Lo sconto del rinnovo automatico, in percento.
  final num scontoRinnovo;

  /// Dopo un downgrade programmato.
  final VoidCallback? alFatto;

  @override
  ConsumerState<CambioPiano> createState() => _CambioPianoState();
}

class _CambioPianoState extends ConsumerState<CambioPiano> {
  bool _rinnovo = true;
  Conguaglio? _conto;
  String? _errore;
  bool _inCorso = false;
  String? _fatto;
  int _richiesta = 0;

  @override
  void initState() {
    super.initState();
    unawaited(_anteprima());
  }

  Future<void> _anteprima() async {
    final n = ++_richiesta;
    try {
      final c = await ref
          .read(apiProvider)
          .anteprimaCambio(
            widget.piano.slug,
            annuale: widget.annuale,
            rinnovo: _rinnovo,
            lingua: ref.read(linguaProvider),
          );
      if (!mounted || n != _richiesta) return;
      setState(() {
        _conto = c;
        _errore = null;
      });
    } on ErroreApi catch (e) {
      if (!mounted || n != _richiesta) return;
      setState(() {
        _conto = null;
        _errore = e.messaggio(context.t);
      });
    }
  }

  Future<void> _conferma() async {
    final conto = _conto;
    if (conto == null) return;
    final t = context.t;
    final lingua = ref.read(linguaProvider);
    setState(() {
      _inCorso = true;
      _errore = null;
    });
    try {
      final r = await ref
          .read(apiProvider)
          .cambiaPiano(
            widget.piano.slug,
            annuale: widget.annuale,
            rinnovo: _rinnovo,
            lingua: lingua,
            ritorno: ritornoApp(R.prezzi),
          );
      if (r.tipo == 'upgrade' && r.url != null) {
        await ref.read(pagamentoInSospesoProvider.notifier).apri(r.url!, ritorno: R.prezzi);
        if (mounted) Navigator.of(context).pop();
        return;
      }
      if (!mounted) return;
      setState(() => _fatto = t.abbonamento_cambio_programmato(dataLunga(r.conguaglio.decorre, lingua)));
      widget.alFatto?.call();
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _errore = e.messaggio(t));
    } finally {
      if (mounted) setState(() => _inCorso = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final conto = _conto;
    String soldi(int c) => euro(c, lingua, valuta: conto?.valuta ?? widget.piano.valuta);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (conto?.tipo == 'upgrade') ...[
          Semantics(
            liveRegion: true,
            child: Conguaglio3Righe(
              righe: [
                (
                  titolo: t.abbonamento_cambio_residuo,
                  nota: t.abbonamento_cambio_residuo_nota(
                    conto!.giorniRimasti,
                    conto.giorniPeriodo,
                    soldi(conto.pagato),
                  ),
                  importo: '−${soldi(conto.residuo)}',
                ),
                (
                  titolo: conto.rinnovo ? t.abbonamento_cambio_nuovo_rinnovo : t.abbonamento_cambio_nuovo,
                  nota: conto.rinnovo
                      ? t.abbonamento_cambio_nuovo_nota(soldi(conto.listino), widget.scontoRinnovo)
                      : null,
                  importo: soldi(conto.nuovo),
                ),
              ],
              totale: (titolo: t.abbonamento_cambio_totale, importo: soldi(conto.totale)),
            ),
          ),
          Text(conto.totale == 0 ? t.abbonamento_cambio_zero : t.abbonamento_cambio_subito, style: stilePiccolo()),
        ],
        if (conto?.tipo == 'downgrade')
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(
              t.abbonamento_cambio_downgrade(dataLunga(conto!.decorre, lingua), soldi(conto.totale)),
              style: Stile.sans(16, colore: Token.ink, altezza: 1.6),
            ),
          ),
        if (conto != null)
          Interruttore(
            valore: _rinnovo,
            titolo: t.abbonamento_cambio_rinnovo(widget.scontoRinnovo),
            alCambio: (v) {
              setState(() => _rinnovo = v);
              unawaited(_anteprima());
            },
          ),
        if (_fatto != null) Successo(_fatto!),
        if (_errore != null) Errore(_errore!),
        const SizedBox(height: 16),
        FilaBottoni(
          children: [
            if (_fatto == null && conto != null)
              Bottone(
                conto.tipo == 'upgrade'
                    ? t.abbonamento_cambio_paga(soldi(conto.totale))
                    : t.abbonamento_cambio_programma,
                variante: Variante.ottone,
                an: 'cambio_conferma',
                alTocco: _inCorso
                    ? null
                    : () {
                        ref.read(lanternaProvider).traccia('cambio_conferma');
                        unawaited(_conferma());
                      },
              ),
            Bottone(t.comune_chiudi, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop()),
          ],
        ),
      ],
    );
  }
}

/// `.conguaglio`: le righe con l'importo allineato a destra e il totale in evidenza (`dl` del sito).
class Conguaglio3Righe extends StatelessWidget {
  /// Le [righe] e il [totale].
  const Conguaglio3Righe({super.key, required this.righe, required this.totale});

  /// Le righe: titolo, nota piccola, importo.
  final List<({String titolo, String? nota, String importo})> righe;

  /// Il totale.
  final ({String titolo, String importo}) totale;

  @override
  Widget build(BuildContext context) {
    Widget riga({
      required Widget dt,
      required String dd,
      required TextStyle stileDd,
      Color? fondo,
      bool bordo = true,
    }) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
      decoration: BoxDecoration(
        color: fondo,
        border: bordo ? const Border(top: BorderSide(color: Token.line)) : null,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.baseline,
        textBaseline: TextBaseline.alphabetic,
        children: [
          Expanded(child: dt),
          const SizedBox(width: 16),
          Text(dd, softWrap: false, style: stileDd),
        ],
      ),
    );
    final cifre = [const FontFeature.tabularFigures()];
    return Container(
      margin: const EdgeInsets.only(bottom: 12.8),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        border: Border.all(color: Token.line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final (i, r) in righe.indexed)
            riga(
              bordo: i > 0,
              dt: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    r.titolo,
                    style: Stile.sans(16, peso: FontWeight.w600, colore: Token.ink, altezza: 1.6),
                  ),
                  if (r.nota != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 2.4),
                      child: Text(r.nota!, style: Stile.sans(12.8, colore: Token.inkSoft, altezza: 1.6)),
                    ),
                ],
              ),
              dd: r.importo,
              stileDd: Stile.serif(20, colore: Token.ink).copyWith(fontFeatures: cifre),
            ),
          riga(
            fondo: Token.paperDeep,
            dt: Text(
              totale.titolo,
              style: Stile.sans(16.8, peso: FontWeight.w600, colore: Token.ink, altezza: 1.6),
            ),
            dd: totale.importo,
            stileDd: Stile.serif(25.6, colore: Token.ink).copyWith(fontWeight: FontWeight.w700, fontFeatures: cifre),
          ),
        ],
      ),
    );
  }
}
