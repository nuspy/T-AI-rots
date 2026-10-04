/// Ciò che il rito restituisce: le carte svelate una per una (`frontend/v2/lettura/carte-svelate.tsx`), le fasi
/// dell'interpretazione mentre arriva e l'interpretazione stessa (`responso.tsx`), col Markdown minimo del responso
/// (`frontend/lib/markdown.tsx`: titoli `##`, paragrafi, elenchi, grassetto e corsivo).
library;

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/bottoni.dart';
import '../componenti/campi.dart' show Avviso, Puntini;
import '../componenti/carta.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/carta.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'comuni.dart';
import 'tavolo.dart';

/* ---- le carte svelate -------------------------------------------------------------------------------------------- */

/// Le carte svelate (v8.5): una per una, con la loro spiegazione, prima dell'interpretazione dell'insieme. Mentre le
/// carte si girano la spiegazione arriva in streaming; la carta in arrivo ha il cursore. Dalla v8.6 le carte si
/// girano tutte insieme e il lettore le legge con una chiamata sola: mentre legge, un solo avviso d'attesa per tutte.
class CarteSvelate extends ConsumerWidget {
  /// Le carte [posate] della [stesa]; [attiva] mentre si girano; [lettoreLegge] mentre il lettore le legge.
  const CarteSvelate({
    super.key,
    required this.stesa,
    required this.posate,
    required this.attiva,
    this.lettoreLegge = false,
  });

  /// La stesa.
  final Stesa stesa;

  /// Le carte.
  final List<Posata> posate;

  /// Le carte si stanno girando.
  final bool attiva;

  /// Le carte sono girate e il lettore le sta leggendo tutte insieme: un solo avviso, nessun cursore.
  final bool lettoreLegge;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final String ll = LinguaNomi.di(context) ?? ref.watch(linguaProvider);
    final rivelate = [...posate.where((p) => p.rivelata && p.carta != null)]
      ..sort((a, b) => a.posizione.compareTo(b.posizione));
    if (rivelate.isEmpty) return const SizedBox.shrink();
    // Il cursore sta sulla prima carta ancora senza spiegazione (quella che sta arrivando), o sull'ultima.
    final inArrivo = rivelate.where((p) => (p.interpretazione ?? '').isEmpty).firstOrNull ?? rivelate.last;
    final testo = Stile.sans(15.2, altezza: 1.55, colore: Token.inkSoft);
    return Semantics(
      liveRegion: true,
      container: true,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 9.6),
              child: Semantics(header: true, child: Text(t.lettura_carte_svelate, style: Stile.serif(21.6))),
            ),
            if (lettoreLegge)
              Padding(
                padding: const EdgeInsets.only(bottom: 11.2),
                child: Container(
                  constraints: const BoxConstraints(minHeight: 48),
                  padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 9.6),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFFAF1),
                    border: Border.all(color: Token.line),
                  ),
                  child: Row(
                    children: [
                      const ExcludeSemantics(child: Puntini(colore: Token.brass)),
                      const SizedBox(width: 9.6),
                      Expanded(
                        child: Text(
                          t.lettura_lettore_legge,
                          style: Stile.serif(16, altezza: 1.5, stile: FontStyle.italic, colore: Token.inkSoft),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            for (final (i, p) in rivelate.indexed) ...[
              if (i > 0) const SizedBox(height: 11.2),
              Container(
                padding: const EdgeInsets.all(11.2),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFFAF1),
                  border: Border.all(color: Token.line),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 72,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(3),
                        boxShadow: const [BoxShadow(color: Color(0x2E201026), offset: Offset(0, 4), blurRadius: 12)],
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: Transform.rotate(
                        angle: p.rovescio == true ? math.pi : 0,
                        child: ImmagineCarta(p.carta!.id, alt: nomeCarta(p.carta!, ll)),
                      ),
                    ),
                    const SizedBox(width: 12.8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${p.posizione}. ${_nomePosizione(stesa, p.posizione, ll)}'.toUpperCase(),
                            style: Stile.sans(11.52, peso: FontWeight.w700, em: .08, colore: Token.verdigris),
                          ),
                          Padding(
                            padding: const EdgeInsets.only(bottom: 4.8),
                            child: Text(
                              '${nomeCarta(p.carta!, ll)}${p.rovescio == true ? ' · ${t.lettura_rovesciata}' : ''}',
                              style: Stile.serif(17.6),
                            ),
                          ),
                          Text.rich(
                            TextSpan(
                              children: [
                                TextSpan(text: p.interpretazione ?? ''),
                                if (attiva && !lettoreLegge && identical(p, inArrivo)) spanCursore(testo),
                              ],
                            ),
                            style: testo,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  static String _nomePosizione(Stesa s, int n, String lingua) {
    final pos = s.posizioni.where((x) => x.n == n).firstOrNull;
    return pos == null ? '' : nomePosizione(pos, lingua);
  }
}

/* ---- le fasi dell'interpretazione ---------------------------------------------------------------------------------- */

/// Le fasi del responso mentre si prepara (`FaseResponso`): il sigillo che gira (14 s) e la frase della fase.
class FaseResponso extends StatefulWidget {
  /// La fase corrente (`unione`, `guardia`, `revisione`).
  const FaseResponso({super.key, required this.fase});

  /// La fase.
  final String fase;

  @override
  State<FaseResponso> createState() => _FaseResponsoState();
}

class _FaseResponsoState extends State<FaseResponso> with SingleTickerProviderStateMixin {
  late final AnimationController _giro = AnimationController(vsync: this, duration: const Duration(seconds: 14));

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _giro.stop();
    } else if (!_giro.isAnimating) {
      _giro.repeat();
    }
  }

  @override
  void dispose() {
    _giro.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final testo = switch (widget.fase) {
      'guardia' => t.lettura_fasi_guardia,
      'revisione' => t.lettura_fasi_revisione,
      _ => t.lettura_fasi_unione,
    };
    final stile = Stile.serif(17.6, altezza: 1.5, stile: FontStyle.italic, colore: Token.inkSoft);
    return Semantics(
      liveRegion: true,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 32),
        child: Column(
          children: [
            ExcludeSemantics(
              child: RotationTransition(
                turns: _giro,
                child: const SizedBox(width: 84, height: 84, child: CustomPaint(painter: _Sigillo())),
              ),
            ),
            const SizedBox(height: 16),
            AnimatedSwitcher(
              duration: MediaQuery.disableAnimationsOf(context) ? Duration.zero : const Duration(milliseconds: 300),
              transitionBuilder: (figlio, a) => FadeTransition(
                opacity: a,
                child: SlideTransition(
                  position: Tween(begin: const Offset(0, .15), end: Offset.zero).animate(a),
                  child: figlio,
                ),
              ),
              child: ConstrainedBox(
                key: ValueKey(widget.fase),
                constraints: BoxConstraints(maxWidth: larghezzaCh(stile, MediaQuery.textScalerOf(context)) * 36),
                child: Text(testo, textAlign: TextAlign.center, style: stile),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Il sigillo: due cerchi (ottone e verderame tratteggiato) e la stella di due triangoli prugna, su 100×100.
class _Sigillo extends CustomPainter {
  const _Sigillo();

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(size.width / 100);
    canvas.drawCircle(
      const Offset(50, 50),
      46,
      Paint()
        ..style = PaintingStyle.stroke
        ..color = const Color(0x99B28336),
    );
    final tratteggio = Paint()
      ..style = PaintingStyle.stroke
      ..color = const Color(0x8019706F);
    const r = 38.0;
    const circonferenza = 2 * math.pi * r;
    for (var d = 0.0; d < circonferenza; d += 6) {
      canvas.drawArc(Rect.fromCircle(center: const Offset(50, 50), radius: r), d / r, 2 / r, false, tratteggio);
    }
    final stella = Path()
      ..moveTo(50, 12)
      ..lineTo(83, 69)
      ..lineTo(17, 69)
      ..close()
      ..moveTo(50, 88)
      ..lineTo(17, 31)
      ..lineTo(83, 31)
      ..close();
    canvas.drawPath(
      stella,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.3
        ..color = Token.plum,
    );
  }

  @override
  bool shouldRepaint(_Sigillo vecchio) => false;
}

/* ---- il Markdown del responso ------------------------------------------------------------------------------------ */

/// Il Markdown minimo del responso (`Markdown` di `frontend/lib/markdown.tsx`): blocchi separati da righe vuote, `##`
/// e `#` titoli, `-`/`*` elenchi, `**grassetto**` e `*corsivo*`; nient'altro (il testo viene dal modello).
class MarkdownResponso extends StatelessWidget {
  /// Il [testo] nello stile [stile] (`.testo`: serif 1.04rem/1.75), coi titoli [stileTitolo].
  const MarkdownResponso(this.testo, {super.key, required this.stile, required this.stileTitolo});

  /// Il testo.
  final String testo;

  /// I paragrafi.
  final TextStyle stile;

  /// I titoli (`h3`).
  final TextStyle stileTitolo;

  static List<InlineSpan> _inline(String testo) {
    final parti = <InlineSpan>[];
    final re = RegExp(r'(\*\*[^*]+\*\*|\*[^*]+\*)');
    var da = 0;
    for (final m in re.allMatches(testo)) {
      if (m.start > da) parti.add(TextSpan(text: testo.substring(da, m.start)));
      final p = m.group(0)!;
      if (p.startsWith('**')) {
        parti.add(
          TextSpan(
            text: p.substring(2, p.length - 2),
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        );
      } else if (p.length > 2) {
        parti.add(
          TextSpan(
            text: p.substring(1, p.length - 1),
            style: const TextStyle(fontStyle: FontStyle.italic),
          ),
        );
      } else {
        parti.add(TextSpan(text: p));
      }
      da = m.end;
    }
    if (da < testo.length) parti.add(TextSpan(text: testo.substring(da)));
    return parti;
  }

  @override
  Widget build(BuildContext context) {
    final blocchi = <Widget>[];
    for (final grezzo in testo.split(RegExp(r'\n{2,}'))) {
      final righe = grezzo.trim();
      if (righe.isEmpty) continue;
      if (righe.startsWith('## ') || righe.startsWith('# ')) {
        final tutte = righe.split('\n');
        final titolo = tutte.first.replaceFirst(RegExp(r'^#{1,2} '), '');
        blocchi.add(
          Padding(
            padding: EdgeInsets.only(top: blocchi.isEmpty ? 0 : 25.6, bottom: 8),
            child: Semantics(header: true, child: TestoBilanciato(titolo, stile: stileTitolo)),
          ),
        );
        if (righe.startsWith('## ') && tutte.length > 1) {
          blocchi.add(
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Text.rich(TextSpan(children: _inline(tutte.skip(1).join(' '))), style: stile),
            ),
          );
        }
      } else if (RegExp(r'^[-*] ').hasMatch(righe)) {
        blocchi.add(
          Padding(
            padding: const EdgeInsets.only(bottom: 16, left: 19.2),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                for (final r in righe.split('\n'))
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('•  ', style: stile),
                      Expanded(
                        child: Text.rich(
                          TextSpan(children: _inline(r.replaceFirst(RegExp(r'^[-*] '), ''))),
                          style: stile,
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        );
      } else {
        blocchi.add(
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text.rich(TextSpan(children: _inline(righe.replaceAll('\n', ' '))), style: stile),
          ),
        );
      }
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: blocchi);
  }
}

/* ---- il responso ----------------------------------------------------------------------------------------------- */

/// L'interpretazione finale (`Responso`): il testo e ciò che se ne fa dopo. Chi non ha un account vede una prima
/// risposta e l'invito a tenere la lettura intera; chi è dentro condivide, verifica il mazzo, torna alla sua storia.
class Responso extends StatefulWidget {
  /// Il responso della lettura [id].
  const Responso({
    super.key,
    required this.id,
    required this.testo,
    required this.finito,
    required this.disclaimer,
    required this.commitment,
    required this.saldo,
    required this.anonimo,
    required this.omaggi,
    required this.alNuova,
    required this.alRegistrati,
    required this.alCondividi,
    required this.alVai,
    this.alStampa,
  });

  /// La lettura.
  final String id;

  /// Il testo (Markdown minimo).
  final String testo;

  /// Arrivato tutto.
  final bool finito;

  /// L'avvertenza.
  final String disclaimer;

  /// L'impronta del mazzo sigillato.
  final String? commitment;

  /// Il saldo dopo la lettura.
  final int? saldo;

  /// Un visitatore senza account: il testo è l'anteprima.
  final bool anonimo;

  /// Le letture in regalo con un account.
  final int omaggi;

  /// «Fai una nuova domanda».
  final VoidCallback alNuova;

  /// «Ottieni la lettura completa gratis».
  final VoidCallback alRegistrati;

  /// «Condividi questa lettura».
  final VoidCallback alCondividi;

  /// Un collegamento interno.
  final ValueChanged<String> alVai;

  /// «Stampa in PDF», se disponibile.
  final VoidCallback? alStampa;

  @override
  State<Responso> createState() => _ResponsoState();
}

class _ResponsoState extends State<Responso> with SingleTickerProviderStateMixin {
  late final AnimationController _entrata = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 600),
  );
  bool _verifica = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_entrata.value == 0 && !_entrata.isAnimating) {
      if (MediaQuery.disableAnimationsOf(context)) {
        _entrata.value = 1;
      } else {
        unawaited(_entrata.forward());
      }
    }
  }

  @override
  void dispose() {
    _entrata.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    final stile = Stile.serif(16.64, altezza: 1.75, colore: Token.ink);
    final titolo = Stile.serif(w.clampVw(28.8, 3.4, 41.6), altezza: 1.15, em: -.03);
    final contenuto = Container(
      padding: EdgeInsets.all(w.clampVw(22.4, 5, 48)),
      decoration: const BoxDecoration(
        color: Token.paperLight,
        border: Border(
          top: BorderSide(color: Token.brass, width: 3),
          left: BorderSide(color: Token.line),
          right: BorderSide(color: Token.line),
          bottom: BorderSide(color: Token.line),
        ),
        boxShadow: [BoxShadow(color: Color(0x1A3C1846), offset: Offset(0, 24), blurRadius: 50)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Eyebrow('✦'),
          Padding(
            padding: const EdgeInsets.only(bottom: 19.2),
            child: Semantics(
              header: true,
              child: TestoBilanciato(
                widget.anonimo ? t.lettura_anteprima_titolo : t.lettura_il_responso,
                stile: titolo,
              ),
            ),
          ),
          MarkdownResponso(
            widget.testo,
            stile: stile,
            stileTitolo: Stile.serif(20, colore: Token.plum),
          ),
          if (widget.finito && widget.anonimo)
            Container(
              margin: const EdgeInsets.only(top: 22.4),
              padding: const EdgeInsets.all(19.2),
              decoration: const BoxDecoration(
                color: Token.plum,
                boxShadow: [BoxShadow(color: Token.brassPale, offset: Offset(10, 10))],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Paragrafo(t.lettura_anteprima_testo, style: Stile.sans(16, colore: const Color(0xFFE6D8E8))),
                  const SizedBox(height: 16),
                  Paragrafo(
                    t.lettura_anteprima_extra(widget.omaggi),
                    style: Stile.sans(16, colore: const Color(0xFFE6D8E8)),
                  ),
                  const SizedBox(height: 16),
                  Bottone(
                    t.lettura_anteprima_cta,
                    variante: Variante.ottone,
                    an: 'cta_iscrizione',
                    anProprieta: const {'dove': 'anteprima'},
                    alTocco: widget.alRegistrati,
                  ),
                ],
              ),
            ),
          if (widget.finito && !widget.anonimo) ...[
            Container(
              margin: const EdgeInsets.only(top: 22.4),
              padding: const EdgeInsets.only(top: 16),
              decoration: const BoxDecoration(
                border: Border(top: BorderSide(color: Token.line)),
              ),
              child: Text(widget.disclaimer, style: Stile.sans(13.44, colore: Token.inkSoft)),
            ),
            if (widget.commitment != null)
              Padding(
                padding: const EdgeInsets.only(top: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Premibile(
                      alTocco: () => setState(() => _verifica = !_verifica),
                      costruisci: (context, premuto) => ConstrainedBox(
                        constraints: const BoxConstraints(minHeight: 44),
                        child: Align(
                          alignment: AlignmentDirectional.centerStart,
                          widthFactor: 1,
                          heightFactor: 1,
                          child: Text(
                            '${_verifica ? '▾' : '▸'} ${t.lettura_verifica}',
                            style: Stile.sans(13.44, colore: Token.plum),
                          ),
                        ),
                      ),
                    ),
                    if (_verifica) ...[
                      Paragrafo(t.lettura_verifica_testo, style: Stile.sans(13.44, colore: Token.inkSoft)),
                      const SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(9.6),
                        color: Token.paper,
                        child: Text(
                          widget.commitment!,
                          style: const TextStyle(fontFamily: 'monospace', fontSize: 12.16, color: Token.inkSoft),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: FilaBottoni(
                children: [
                  Bottone(t.lettura_condividi, an: 'share_started', alTocco: widget.alCondividi),
                  Bottone(t.lettura_vai_storia, variante: Variante.quieto, href: R.lettura(widget.id)),
                  if (widget.alStampa != null)
                    Bottone(
                      '⎙ ${t.lettura_stampa_pdf}',
                      variante: Variante.quieto,
                      an: 'stampa_pdf',
                      alTocco: widget.alStampa,
                    ),
                  Bottone(t.lettura_nuova, variante: Variante.quieto, alTocco: widget.alNuova),
                ],
              ),
            ),
            if (widget.saldo == 0)
              Avviso(
                null,
                figlio: Wrap(
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Text('${t.lettura_crediti_finiti}. ', style: Stile.sans(14.4, colore: Token.inkSoft)),
                    Collegamento(t.lettura_vedi_prezzi, href: R.prezzi, stile: Stile.sans(14.4)),
                  ],
                ),
              ),
          ],
        ],
      ),
    );
    return AnimatedBuilder(
      animation: _entrata,
      builder: (context, figlio) {
        final v = Curves.easeOut.transform(_entrata.value);
        return Opacity(
          opacity: v,
          child: Transform.translate(offset: Offset(0, 24 * (1 - v)), child: figlio),
        );
      },
      child: Semantics(
        liveRegion: true,
        container: true,
        child: Center(
          child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 860), child: contenuto),
        ),
      ),
    );
  }
}
