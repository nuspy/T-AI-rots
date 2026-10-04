/// Il mazzo del rito (`frontend/v2/lettura/ventaglio.tsx`): la mescolata che si interrompe, il taglio, il ventaglio.
/// La geometria è quella del sito: archi di al più 26 carte, il taglio come frazione del mazzo, gli slot già assegnati
/// dal server prima che il ventaglio si apra. Le animazioni hanno le durate e le curve di framer-motion.
library;

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/physics.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

import '../componenti/carta.dart';
import '../componenti/premibile.dart';
import '../l10n/testi.dart';
import 'comuni.dart';

/// Le carte di un arco del ventaglio.
const int cartePerArco = 26;

/// Le carte del mazzo che si taglia.
const int carteDelTaglio = 22;

/// La molla delle carte del ventaglio: `{ type: "spring", stiffness: 140, damping: 18 }`.
const SpringDescription mollaVentaglio = SpringDescription(mass: 1, stiffness: 140, damping: 18);

/// `ease-in-out` di framer-motion (`[0.42, 0, 0.58, 1]`).
const Cubic easeInOut = Cubic(.42, 0, .58, 1);

/// Il ventaglio delle carte coperte (`.ventaglioGruppi`): un arco ogni 26 carte, 28 px fra un arco e l'altro.
class Ventaglio extends StatelessWidget {
  /// [quante] carte, senza quelle già [scelte]; [attivo] finché ne mancano da scegliere.
  const Ventaglio({
    super.key,
    required this.quante,
    required this.scelte,
    required this.attivo,
    required this.alScegli,
  });

  /// Le carte del mazzo.
  final int quante;

  /// Gli slot già scelti (non ci sono più).
  final Set<int> scelte;

  /// Si può ancora scegliere.
  final bool attivo;

  /// Una carta scelta.
  final ValueChanged<int> alScegli;

  @override
  Widget build(BuildContext context) {
    final gruppi = math.max(1, (quante / cartePerArco).ceil());
    return Semantics(
      label: context.t.lettura_ventaglio_aria,
      container: true,
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            for (var g = 0; g < gruppi; g++) ...[
              if (g > 0) const SizedBox(height: 28),
              _Arco(
                inizio: g * cartePerArco,
                quante: math.min(quante, (g + 1) * cartePerArco) - g * cartePerArco,
                scelte: scelte,
                attivo: attivo,
                alScegli: alScegli,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Arco extends StatefulWidget {
  const _Arco({
    required this.inizio,
    required this.quante,
    required this.scelte,
    required this.attivo,
    required this.alScegli,
  });

  final int inizio;
  final int quante;
  final Set<int> scelte;
  final bool attivo;
  final ValueChanged<int> alScegli;

  @override
  State<_Arco> createState() => _ArcoState();
}

class _ArcoState extends State<_Arco> {
  int? _sopra;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final volo = AmbitoVolo.di(context);
    return LayoutBuilder(
      builder: (context, vincoli) {
        final w = vincoli.maxWidth;
        final quante = widget.quante;
        final apertura = quante > 30 ? 118.0 : 84.0;
        final mezza = apertura / 2 * math.pi / 180;
        final corda = w * .92;
        final raggio = corda / 2 / math.sin(mezza);
        final lc = math.min(quante > 30 ? 64.0 : 88.0, math.max(30.0, corda / quante * (quante > 30 ? 3.2 : 1.9)));
        final hc = lc * 16 / 9;
        final freccia = raggio * (1 - math.cos(mezza));
        final carte = <(int, Widget)>[];
        for (var i = 0; i < quante; i++) {
          final slot = widget.inizio + i;
          if (widget.scelte.contains(slot)) continue;
          final angolo = -apertura / 2 + apertura * i / math.max(1, quante - 1);
          carte.add((
            _sopra == i ? quante + 1 : i,
            Positioned(
              key: ValueKey(slot),
              left: w / 2 - lc / 2,
              top: 30,
              width: lc,
              height: hc,
              child: Transform.rotate(
                angle: angolo * math.pi / 180,
                // `transform-origin: 50% <raggio>px`: il perno sta sotto la carta, al centro dell'arco.
                origin: Offset(0, raggio - hc / 2),
                child: _CartaVentaglio(
                  key: volo?.chiaveSlot(slot, angolo),
                  ritardo: Duration(milliseconds: math.min(1200, i * 12)),
                  attivo: widget.attivo,
                  sopra: _sopra == i,
                  etichetta: t.lettura_carta_n(slot + 1),
                  alFuoco: (v) => setState(() => _sopra = v ? i : (_sopra == i ? null : _sopra)),
                  alTocco: () => widget.alScegli(slot),
                ),
              ),
            ),
          ));
        }
        carte.sort((a, b) => a.$1.compareTo(b.$1));
        return SizedBox(
          height: freccia + hc + 40,
          child: Stack(clipBehavior: Clip.none, children: [for (final c in carte) c.$2]),
        );
      },
    );
  }
}

/// `.ventaglioCarta`: il dorso con la cornice crema; entra dal basso con la molla (in ritardo di 12 ms per carta) e,
/// toccato o col fuoco, si alza (`y: -22, scale: 1.06`).
class _CartaVentaglio extends StatefulWidget {
  const _CartaVentaglio({
    super.key,
    required this.ritardo,
    required this.attivo,
    required this.sopra,
    required this.etichetta,
    required this.alFuoco,
    required this.alTocco,
  });

  final Duration ritardo;
  final bool attivo;
  final bool sopra;
  final String etichetta;
  final ValueChanged<bool> alFuoco;
  final VoidCallback alTocco;

  @override
  State<_CartaVentaglio> createState() => _CartaVentaglioState();
}

class _CartaVentaglioState extends State<_CartaVentaglio> with TickerProviderStateMixin {
  late final AnimationController _entrata = AnimationController.unbounded(vsync: this);
  late final AnimationController _alza = AnimationController.unbounded(vsync: this);
  Timer? _attesa;
  bool _avviata = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_avviata) return;
    _avviata = true;
    if (MediaQuery.disableAnimationsOf(context)) {
      _entrata.value = 1;
      return;
    }
    _attesa = Timer(widget.ritardo, () {
      if (mounted) unawaited(_entrata.animateWith(SpringSimulation(mollaVentaglio, 0, 1, 0)));
    });
  }

  /// Si alza (`y: -22, scale: 1.06`) mentre la si preme o ha il fuoco, con la stessa molla.
  void _alzaSe(bool su) {
    final verso = su && widget.attivo ? 1.0 : 0.0;
    if (_meta == verso) return;
    _meta = verso;
    if (MediaQuery.disableAnimationsOf(context)) {
      _alza.value = verso;
    } else {
      unawaited(_alza.animateWith(SpringSimulation(mollaVentaglio, _alza.value, verso, _alza.velocity)));
    }
    widget.alFuoco(su);
  }

  double _meta = 0;

  @override
  void dispose() {
    _attesa?.cancel();
    _entrata.dispose();
    _alza.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Premibile(
      alTocco: widget.attivo ? widget.alTocco : null,
      etichetta: widget.etichetta,
      costruisci: (context, premuto) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted) _alzaSe(premuto || widget.sopra);
        });
        return AnimatedBuilder(
          animation: Listenable.merge([_entrata, _alza]),
          builder: (context, figlio) {
            final e = _entrata.value;
            final a = _alza.value;
            return Opacity(
              opacity: e.clamp(0, 1),
              child: Transform.translate(
                offset: Offset(0, 60 * (1 - e) - 22 * a),
                child: Transform.scale(scale: 1 + .06 * a, child: figlio),
              ),
            );
          },
          child: Container(
            decoration: BoxDecoration(
              border: Border.all(
                color: widget.sopra && widget.attivo ? const Color(0xFFD6B66D) : const Color(0xFFEAD9B2),
                width: 2,
              ),
              boxShadow: [
                widget.sopra && widget.attivo
                    ? const BoxShadow(color: Color(0x66000000), offset: Offset(0, 14), blurRadius: 22)
                    : const BoxShadow(color: Color(0x57000000), offset: Offset(0, 10), blurRadius: 18),
              ],
            ),
            clipBehavior: Clip.hardEdge,
            child: const ImmagineCarta('dorso'),
          ),
        );
      },
    );
  }
}

/// `.mescolamento`: nove dorsi che si dividono e si ricompongono (1,6 s, ease-in-out fra un fotogramma chiave e
/// l'altro, sfasati di 50 ms) finché non si tocca il mazzo.
class Mescolamento extends StatefulWidget {
  /// La mescolata; [alFerma] quando la si interrompe.
  const Mescolamento({super.key, required this.alFerma});

  /// La mescolata si ferma.
  final VoidCallback alFerma;

  @override
  State<Mescolamento> createState() => _MescolamentoState();
}

class _MescolamentoState extends State<Mescolamento> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1600));

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _c.stop();
    } else if (!_c.isAnimating) {
      _c.repeat();
    }
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  /// Il valore dei fotogrammi chiave [k] (cinque, a distanza uguale) al tempo [t], ease-in-out per tratto.
  static double _chiavi(List<double> k, double t) {
    final x = t.clamp(0.0, 1.0) * (k.length - 1);
    final i = math.min(k.length - 2, x.floor());
    final f = easeInOut.transform(x - i);
    return k[i] + (k[i + 1] - k[i]) * f;
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Premibile(
      alTocco: widget.alFerma,
      etichetta: t.lettura_ferma,
      an: 'rito',
      anProprieta: const {'passo': 'shuffle_interrupted'},
      costruisci: (context, premuto) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 18),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 10),
          child: SizedBox(
            width: 120,
            height: 120 * 16 / 9,
            child: AnimatedBuilder(
              animation: _c,
              builder: (context, _) => Stack(
                clipBehavior: Clip.none,
                children: [
                  for (var i = 0; i < 9; i++)
                    Builder(
                      builder: (context) {
                        // `delay: i * 0.05` su un ciclo di 1,6 s che si ripete.
                        final tt = ((_c.value * 1600 - i * 50) / 1600) % 1;
                        final segno = i.isOdd ? 1.0 : -1.0;
                        final x = _chiavi([0, segno * (46 + i * 5), 0, -segno * 28, 0], tt);
                        final y = _chiavi([0, -i * 2.0, i * 1.5, -i.toDouble(), 0], tt);
                        final r = _chiavi([0, segno * 8, 0, -segno * 4, 0], tt);
                        return Positioned.fill(
                          child: Transform.translate(
                            offset: Offset(x, y),
                            child: Transform.rotate(
                              angle: r * math.pi / 180,
                              child: Container(
                                decoration: BoxDecoration(
                                  border: Border.all(color: const Color(0xFFF5E6BF), width: 2),
                                  boxShadow: const [
                                    BoxShadow(color: Color(0x66000000), offset: Offset(0, 8), blurRadius: 20),
                                  ],
                                ),
                                clipBehavior: Clip.hardEdge,
                                child: const ImmagineCarta('dorso'),
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Il taglio (`.taglio`): si sceglie il punto in cui dividere il mazzo; le carte dopo il punto si alzano (.18 s),
/// la linea d'ottone segna il punto; al tocco le due metà si scambiano (1 s, ease-in-out) e dopo 1,1 s [alTaglia]
/// riceve la frazione (0–1). Da tastiera: frecce e Invio.
class Taglio extends StatefulWidget {
  /// Il taglio.
  const Taglio({super.key, required this.alTaglia});

  /// Il punto scelto, come frazione del mazzo.
  final ValueChanged<double> alTaglia;

  @override
  State<Taglio> createState() => _TaglioState();
}

class _TaglioState extends State<Taglio> with SingleTickerProviderStateMixin {
  late final AnimationController _scambio = AnimationController(vsync: this, duration: const Duration(seconds: 1));
  final FocusNode _fuoco = FocusNode(debugLabel: 'taglio');
  int? _punto;
  int? _tagliato;
  Timer? _attesa;

  @override
  void dispose() {
    _attesa?.cancel();
    _scambio.dispose();
    _fuoco.dispose();
    super.dispose();
  }

  int _puntoDa(double x, double lc, double passo) =>
      ((x - lc / 2 + passo / 2) / passo).round().clamp(1, carteDelTaglio - 1);

  void _taglia(int p) {
    if (_tagliato != null) return;
    setState(() {
      _punto = p;
      _tagliato = p;
    });
    if (MediaQuery.disableAnimationsOf(context)) {
      _scambio.value = 1;
    } else {
      unawaited(_scambio.forward());
    }
    _attesa = Timer(const Duration(milliseconds: 1100), () => widget.alTaglia(p / carteDelTaglio));
  }

  KeyEventResult _tasto(FocusNode nodo, KeyEvent e) {
    if (_tagliato != null || e is! KeyDownEvent) return KeyEventResult.ignored;
    const n = carteDelTaglio;
    if (e.logicalKey == LogicalKeyboardKey.arrowLeft) {
      setState(() => _punto = math.max(1, (_punto ?? n ~/ 2) - 1));
    } else if (e.logicalKey == LogicalKeyboardKey.arrowRight) {
      setState(() => _punto = math.min(n - 1, (_punto ?? n ~/ 2) + 1));
    } else if (e.logicalKey == LogicalKeyboardKey.enter || e.logicalKey == LogicalKeyboardKey.space) {
      _taglia(_punto ?? (n / 2).round());
    } else {
      return KeyEventResult.ignored;
    }
    return KeyEventResult.handled;
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 720),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8),
          child: LayoutBuilder(
            builder: (context, vincoli) {
              const n = carteDelTaglio;
              final w = vincoli.maxWidth;
              final lc = math.min(88.0, w / 6);
              final passo = (w - lc) / (n - 1);
              final hc = lc * 16 / 9;
              return Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Semantics(
                  button: true,
                  label: t.lettura_taglio_aria,
                  onTap: () => _taglia(_punto ?? (n / 2).round()),
                  child: Focus(
                    focusNode: _fuoco,
                    onKeyEvent: _tasto,
                    child: Listener(
                      onPointerHover: (e) {
                        if (_tagliato == null) setState(() => _punto = _puntoDa(e.localPosition.dx, lc, passo));
                      },
                      onPointerMove: (e) {
                        if (_tagliato == null) setState(() => _punto = _puntoDa(e.localPosition.dx, lc, passo));
                      },
                      child: GestureDetector(
                        behavior: HitTestBehavior.opaque,
                        onTapUp: (d) => _taglia(_puntoDa(d.localPosition.dx, lc, passo)),
                        child: Directionality(
                          textDirection: TextDirection.ltr,
                          child: SizedBox(
                            height: hc + 24,
                            child: AnimatedBuilder(
                              animation: _scambio,
                              builder: (context, _) => Stack(
                                clipBehavior: Clip.none,
                                children: [
                                  for (var i = 0; i < n; i++) _carta(i, lc, hc, passo),
                                  if (_punto != null && _tagliato == null)
                                    Positioned(
                                      left: _punto! * passo - 1,
                                      top: 0,
                                      bottom: 0,
                                      child: const IgnorePointer(
                                        child: Stack(
                                          clipBehavior: Clip.none,
                                          children: [
                                            SizedBox(width: 2, child: ColoredBox(color: Color(0xFFD6B66D))),
                                            Positioned(
                                              top: -8,
                                              left: -7,
                                              child: Text(
                                                '✦',
                                                style: TextStyle(color: Color(0xFFD6B66D), fontSize: 14),
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
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _carta(int i, double lc, double hc, double passo) {
    const n = carteDelTaglio;
    final tg = _tagliato;
    var dx = 0.0;
    var dy = 0.0;
    if (tg != null) {
      final f = easeInOut.transform(_scambio.value);
      dx = (i >= tg ? -tg * passo : (n - tg) * passo) * f;
      // `y: [0, ±28, 0]`: su e giù nello stesso secondo.
      final su = _scambio.value <= .5
          ? easeInOut.transform(_scambio.value * 2)
          : easeInOut.transform((1 - _scambio.value) * 2);
      dy = (i >= tg ? -28 : 28) * su;
    }
    final alzata = tg == null && _punto != null && i >= _punto!;
    return Positioned(
      key: ValueKey(i),
      left: i * passo,
      top: 12,
      width: lc,
      height: hc,
      child: TweenAnimationBuilder<double>(
        tween: Tween(end: alzata ? -10 : 0),
        duration: const Duration(milliseconds: 180),
        curve: easeInOut,
        builder: (context, y, figlio) =>
            Transform.translate(offset: Offset(dx, dy + (tg == null ? y : 0)), child: figlio),
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0xFFF5E6BF)),
            boxShadow: const [BoxShadow(color: Color(0x66000000), offset: Offset(-2, 4), blurRadius: 10)],
          ),
          clipBehavior: Clip.hardEdge,
          child: const ImmagineCarta('dorso'),
        ),
      ),
    );
  }
}
