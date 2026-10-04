/// I pezzi che il rito usa in più punti: i nomi di carte, stese e posizioni nella lingua della lettura
/// (`frontend/lib/i18n/nomi.ts`), le due colonne alte uguali di `.read-layout`, il respiro dei bottoni (`.pulsa`), il
/// cursore che lampeggia (`.cursore`), le virgolette di `<q>` e il volo delle carte dal ventaglio al tavolo (il
/// `layoutId` di framer-motion).
library;

import 'dart:math' as math;

import 'package:flutter/physics.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';

import '../componenti/carta.dart';
import '../modelli/carta.dart';
import '../tema/tema.dart';

/* ---- i nomi ------------------------------------------------------------------------------------------------------ */

/// Il nome di una carta nella lingua [lingua] (`nomeCarta()` del sito).
String nomeCarta(Carta c, String lingua) {
  if (lingua == 'it') return c.nomeIt;
  return c.nomi[lingua] ?? c.nomi['en'] ?? c.nomeThoth;
}

/// Il nome di una stesa nella lingua [lingua] (`nomeStesa()` del sito).
String nomeStesa(Stesa s, String lingua) {
  if (lingua == 'it') return s.lang == 'it' || s.lang == null ? s.nome : (s.nomi?['it'] ?? s.nome);
  return s.nomi?[lingua] ?? s.nomi?['en'] ?? s.nomeEn;
}

/// Il nome di una posizione nella lingua [lingua] (`nomePosizione()` del sito).
String nomePosizione(Posizione p, String lingua) {
  if (lingua == 'it') return p.nome;
  return p.nomi?[lingua] ?? p.nomi?['en'] ?? p.nomeEn;
}

/// La lingua dei nomi di carte, stese e posizioni (`LinguaNomi` del sito): quella della lettura, che può non essere
/// quella dell'interfaccia (la lingua del quesito la decide il server).
class LinguaNomi extends InheritedWidget {
  /// La lingua [lingua] per [child] (`null`: quella dell'interfaccia).
  const LinguaNomi({super.key, required this.lingua, required super.child});

  /// La lingua dei nomi.
  final String? lingua;

  /// La lingua dei nomi sopra [context], se qualcuno l'ha fissata.
  static String? di(BuildContext context) => context.dependOnInheritedWidgetOfExactType<LinguaNomi>()?.lingua;

  @override
  bool updateShouldNotify(LinguaNomi vecchia) => vecchia.lingua != lingua;
}

/// Le virgolette che il browser mette attorno a `<q>` nella lingua della pagina.
(String, String) virgolette(String lingua) => switch (lingua) {
  'it' || 'ru' || 'uk' || 'es' || 'fr' || 'pt' => ('«', '»'),
  'de' => ('„', '“'),
  'hu' || 'pl' || 'ro' => ('„', '”'),
  'zh' || 'ko' || 'hi' || 'ar' || _ => ('“', '”'),
};

/* ---- le due colonne alte uguali (`.read-layout`) ---------------------------------------------------------------- */

/// `.read-layout`: due pannelli affiancati, separati e bordati da una riga sottile (`gap: 1px; background:
/// var(--line); border: 1px solid var(--line)`), con i pesi `.9fr 1.1fr` e alti uguali (la griglia li allunga);
/// sul telefono uno sotto l'altro. Al contrario di `IntrinsicHeight`, i figli possono misurarsi con `LayoutBuilder`.
class PannelliLettura extends StatelessWidget {
  /// I due pannelli [sinistra] e [destra]; [primaDestra] mette il secondo per primo sul telefono (`.inRito`).
  const PannelliLettura({super.key, required this.sinistra, required this.destra, this.primaDestra = false});

  /// La conversazione.
  final Widget sinistra;

  /// Il rito.
  final Widget destra;

  /// Sul telefono il pannello del rito viene prima (`.inRito > :last-child { order: -1 }`).
  final bool primaDestra;

  @override
  Widget build(BuildContext context) {
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final Widget contenuto;
    if (telefono) {
      final pannelli = primaDestra ? [destra, sinistra] : [sinistra, destra];
      contenuto = Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [pannelli[0], const SizedBox(height: 1), pannelli[1]],
      );
    } else {
      contenuto = _ColonneUguali(pesi: const [9, 11], children: [sinistra, destra]);
    }
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Token.line,
        border: Border.all(color: Token.line),
      ),
      child: Padding(padding: const EdgeInsets.all(0), child: contenuto),
    );
  }
}

class _ColonneUguali extends MultiChildRenderObjectWidget {
  const _ColonneUguali({required this.pesi, required super.children});

  final List<int> pesi;

  @override
  _RenderColonne createRenderObject(BuildContext context) => _RenderColonne(pesi);

  @override
  void updateRenderObject(BuildContext context, _RenderColonne r) => r.pesi = pesi;
}

class _DatiColonna extends ContainerBoxParentData<RenderBox> {}

class _RenderColonne extends RenderBox
    with ContainerRenderObjectMixin<RenderBox, _DatiColonna>, RenderBoxContainerDefaultsMixin<RenderBox, _DatiColonna> {
  _RenderColonne(this._pesi);

  List<int> _pesi;
  set pesi(List<int> v) {
    _pesi = v;
    markNeedsLayout();
  }

  @override
  void setupParentData(RenderBox child) {
    if (child.parentData is! _DatiColonna) child.parentData = _DatiColonna();
  }

  @override
  void performLayout() {
    final w = constraints.maxWidth;
    final totale = _pesi.fold(0, (a, b) => a + b);
    final utile = w - (childCount - 1);
    final larghezze = [for (final p in _pesi) utile * p / totale];
    var h = 0.0;
    var i = 0;
    var figlio = firstChild;
    while (figlio != null) {
      figlio.layout(BoxConstraints(minWidth: larghezze[i], maxWidth: larghezze[i]), parentUsesSize: true);
      h = math.max(h, figlio.size.height);
      figlio = childAfter(figlio);
      i++;
    }
    var x = 0.0;
    i = 0;
    figlio = firstChild;
    while (figlio != null) {
      figlio.layout(BoxConstraints.tight(Size(larghezze[i], h)), parentUsesSize: true);
      (figlio.parentData! as _DatiColonna).offset = Offset(x, 0);
      x += larghezze[i] + 1;
      figlio = childAfter(figlio);
      i++;
    }
    size = constraints.constrain(Size(w, h));
  }

  @override
  void paint(PaintingContext context, Offset offset) => defaultPaint(context, offset);

  @override
  bool hitTestChildren(BoxHitTestResult result, {required Offset position}) =>
      defaultHitTestChildren(result, position: position);
}

/* ---- le animazioni che si ripetono ------------------------------------------------------------------------------ */

/// `.pulsa` (`@keyframes respiro`, 2,4 s, ease-in-out): il bottone «respira» da scuro a luminoso, con un alone
/// d'ottone. Fermo col movimento ridotto.
class Respiro extends StatefulWidget {
  /// Attorno al bottone [child].
  const Respiro({super.key, required this.child, this.attivo = true});

  /// Il bottone.
  final Widget child;

  /// Falso: fermo (il bottone è disattivato).
  final bool attivo;

  @override
  State<Respiro> createState() => _RespiroState();
}

class _RespiroState extends State<Respiro> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 2400));

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _aggiorna();
  }

  @override
  void didUpdateWidget(Respiro vecchio) {
    super.didUpdateWidget(vecchio);
    _aggiorna();
  }

  void _aggiorna() {
    final fermo = MediaQuery.disableAnimationsOf(context) || !widget.attivo;
    if (fermo) {
      _c.stop();
      _c.value = 0;
    } else if (!_c.isAnimating) {
      _c.repeat();
    }
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_c.isAnimating) return widget.child;
    return AnimatedBuilder(
      animation: _c,
      builder: (context, figlio) {
        // 0 → 50% → 100%, ease-in-out per tratto: luminosità .82 → 1.18 → .82.
        final x = _c.value;
        final f = Curves.easeInOut.transform(x <= .5 ? x * 2 : (1 - x) * 2);
        final luce = .82 + .36 * f;
        return DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(Token.raggio),
            boxShadow: [BoxShadow(color: Color.fromRGBO(214, 182, 109, .55 * f), blurRadius: 22, spreadRadius: 2)],
          ),
          child: ColorFiltered(
            colorFilter: ColorFilter.matrix([
              luce, 0, 0, 0, 0, //
              0, luce, 0, 0, 0, //
              0, 0, luce, 0, 0, //
              0, 0, 0, 1, 0, //
            ]),
            child: figlio,
          ),
        );
      },
      child: widget.child,
    );
  }
}

/// `.cursore`: «▍» d'ottone che lampeggia (`steps(2)`, 1 s), mentre il testo si scrive.
class Cursore extends StatefulWidget {
  /// Il cursore, alla dimensione del testo [stile].
  const Cursore({super.key, this.stile});

  /// Lo stile del testo accanto.
  final TextStyle? stile;

  @override
  State<Cursore> createState() => _CursoreState();
}

class _CursoreState extends State<Cursore> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(seconds: 1));

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

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: _c,
    builder: (context, _) => Opacity(
      opacity: _c.value < .5 ? 1 : 0,
      child: Text('▍', style: (widget.stile ?? const TextStyle()).copyWith(color: Token.brass)),
    ),
  );
}

/// Lo span del cursore dentro un testo che si scrive.
InlineSpan spanCursore(TextStyle stile) => WidgetSpan(
  alignment: PlaceholderAlignment.baseline,
  baseline: TextBaseline.alphabetic,
  child: Cursore(stile: stile),
);

/* ---- il volo delle carte: dal ventaglio al tavolo ---------------------------------------------------------------- */

/// La molla di framer-motion `{ type: "spring", stiffness: 120, damping: 18 }` (massa 1).
const SpringDescription mollaTavolo = SpringDescription(mass: 1, stiffness: 120, damping: 18);

/// Il registro del volo: ogni carta del ventaglio e ogni posto del tavolo hanno una chiave; scelta una carta, una
/// copia vola dal suo posto nel ventaglio al suo posto sul tavolo (come `layoutId` di framer-motion), mentre la carta
/// del tavolo aspetta nascosta.
class VoloCarte extends ChangeNotifier {
  final Map<int, GlobalKey> _slot = {};
  final Map<int, GlobalKey> _posti = {};
  final Map<int, double> _angoli = {};
  final Set<int> _inVolo = {};

  /// La chiave della carta [slot] del ventaglio (con il suo angolo nell'arco, in gradi).
  GlobalKey chiaveSlot(int slot, double angolo) {
    _angoli[slot] = angolo;
    return _slot.putIfAbsent(slot, () => GlobalKey(debugLabel: 'slot-$slot'));
  }

  /// La chiave del posto [posizione] sul tavolo.
  GlobalKey chiavePosto(int posizione) =>
      _posti.putIfAbsent(posizione, () => GlobalKey(debugLabel: 'posto-$posizione'));

  /// Vero mentre la carta della [posizione] vola verso il tavolo.
  bool inVolo(int posizione) => _inVolo.contains(posizione);

  /// Il rettangolo sullo schermo della carta [slot], prima che sparisca dal ventaglio.
  ({Rect rect, double angolo})? partenza(int slot) {
    final ctx = _slot[slot]?.currentContext;
    final box = ctx?.findRenderObject() as RenderBox?;
    if (box == null || !box.attached || !box.hasSize) return null;
    final centro = box.localToGlobal(box.size.center(Offset.zero));
    return (
      rect: Rect.fromCenter(center: centro, width: box.size.width, height: box.size.height),
      angolo: _angoli[slot] ?? 0,
    );
  }

  /// Fa volare una copia del dorso da [da] al posto [posizione] (appena il tavolo l'ha disposto), sopra tutto.
  Future<void> vola(BuildContext context, int posizione, ({Rect rect, double angolo}) da, double angoloArrivo) async {
    final overlay = Overlay.maybeOf(context, rootOverlay: true);
    if (overlay == null || MediaQuery.disableAnimationsOf(context)) return;
    // Il dorso del mazzo della lettura: sopra tutto non c'è più il `MazzoAttivo` della pagina.
    final mazzo = MazzoAttivo.di(context);
    _inVolo.add(posizione);
    notifyListeners();
    await WidgetsBinding.instance.endOfFrame;
    final box = _posti[posizione]?.currentContext?.findRenderObject() as RenderBox?;
    if (box == null || !box.attached || !box.hasSize) {
      _inVolo.remove(posizione);
      notifyListeners();
      return;
    }
    final arrivo = Rect.fromCenter(
      center: box.localToGlobal(box.size.center(Offset.zero)),
      width: box.size.width,
      height: box.size.height,
    );
    final controllore = AnimationController.unbounded(vsync: overlay);
    final voce = OverlayEntry(
      builder: (context) => AnimatedBuilder(
        animation: controllore,
        builder: (context, _) {
          final t = controllore.value;
          final r = Rect.lerp(da.rect, arrivo, t)!;
          final angolo = (da.angolo + (angoloArrivo - da.angolo) * t) * math.pi / 180;
          return Positioned.fromRect(
            rect: r,
            child: IgnorePointer(
              child: Transform.rotate(angle: angolo, child: _DorsoVolante(mazzo)),
            ),
          );
        },
      ),
    );
    overlay.insert(voce);
    try {
      await controllore.animateWith(SpringSimulation(mollaTavolo, 0, 1, 0));
    } finally {
      voce.remove();
      controllore.dispose();
      _inVolo.remove(posizione);
      notifyListeners();
    }
  }
}

class _DorsoVolante extends StatelessWidget {
  const _DorsoVolante(this.mazzo);

  final String? mazzo;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xFFEAD9B2), width: 2),
        boxShadow: const [BoxShadow(color: Color(0x57000000), offset: Offset(0, 10), blurRadius: 18)],
      ),
      clipBehavior: Clip.hardEdge,
      child: ImmagineCarta('dorso', mazzo: mazzo ?? ''),
    );
  }
}

/// Il registro del volo per i discendenti.
class AmbitoVolo extends InheritedNotifier<VoloCarte> {
  /// Il registro [notifier] per [child].
  const AmbitoVolo({super.key, required VoloCarte super.notifier, required super.child});

  /// Il registro sopra [context], se c'è.
  static VoloCarte? di(BuildContext context) => context.dependOnInheritedWidgetOfExactType<AmbitoVolo>()?.notifier;
}
