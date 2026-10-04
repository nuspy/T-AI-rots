/// Ciò che si tocca: un'area che risponde al tocco, alla tastiera (Invio e Spazio) e ai lettori di schermo, con
/// l'anello del fuoco del sito (`:focus-visible { outline: 3px solid var(--verdigris); outline-offset: 3px }`) solo
/// quando si naviga con la tastiera, e lo stato «premuto» al posto dell'`:hover` del sito.
library;

import 'package:flutter/widgets.dart';

import '../analytics/tracciato.dart';
import '../tema/tema.dart';

/// Un'area premibile.
class Premibile extends StatefulWidget {
  /// Un'area che chiama [alTocco]; [costruisci] riceve lo stato premuto per disegnarsi.
  const Premibile({
    super.key,
    required this.alTocco,
    required this.costruisci,
    this.etichetta,
    this.pulsante = true,
    this.collegamento = false,
    this.selezionato = false,
    this.an,
    this.anProprieta = const {},
    this.raggioFuoco = 0,
  });

  /// Cosa fare al tocco (`null`: disattivato).
  final VoidCallback? alTocco;

  /// Il contenuto, secondo lo stato premuto.
  final Widget Function(BuildContext context, bool premuto) costruisci;

  /// L'etichetta per i lettori di schermo (`aria-label`), se diversa dal testo visibile.
  final String? etichetta;

  /// Un pulsante (`<button>`).
  final bool pulsante;

  /// Un collegamento (`<a>`).
  final bool collegamento;

  /// La pagina corrente (`aria-current="page"`).
  final bool selezionato;

  /// Il nome dell'evento delle statistiche, come `data-an` (vedi [Tracciato]).
  final String? an;

  /// Le proprietà dell'evento, come `data-an-*`.
  final Map<String, String> anProprieta;

  /// Il raggio dell'anello del fuoco.
  final double raggioFuoco;

  @override
  State<Premibile> createState() => _PremibileState();
}

class _PremibileState extends State<Premibile> {
  bool _premuto = false;
  bool _fuoco = false;

  void _attiva() => widget.alTocco?.call();

  @override
  Widget build(BuildContext context) {
    final attivo = widget.alTocco != null;
    Widget contenuto = widget.costruisci(context, _premuto && attivo);
    if (_fuoco && FocusManager.instance.highlightMode == FocusHighlightMode.traditional) {
      contenuto = CustomPaint(foregroundPainter: _Anello(widget.raggioFuoco), child: contenuto);
    }
    Widget risultato = Semantics(
      button: widget.pulsante && !widget.collegamento,
      link: widget.collegamento,
      enabled: attivo,
      selected: widget.selezionato,
      label: widget.etichetta,
      excludeSemantics: widget.etichetta != null,
      onTap: attivo ? _attiva : null,
      child: FocusableActionDetector(
        enabled: attivo,
        onShowFocusHighlight: (v) => setState(() => _fuoco = v),
        actions: {ActivateIntent: CallbackAction<ActivateIntent>(onInvoke: (_) => _attiva())},
        mouseCursor: attivo ? SystemMouseCursors.click : SystemMouseCursors.basic,
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapDown: attivo ? (_) => setState(() => _premuto = true) : null,
          onTapUp: attivo ? (_) => setState(() => _premuto = false) : null,
          onTapCancel: attivo ? () => setState(() => _premuto = false) : null,
          onTap: attivo ? _attiva : null,
          child: contenuto,
        ),
      ),
    );
    if (widget.an != null) risultato = Tracciato(an: widget.an!, proprieta: widget.anProprieta, child: risultato);
    return risultato;
  }
}

/// L'anello del fuoco: 3 px di verderame a 3 px dal bordo, fuori dal riquadro (non sposta niente).
class _Anello extends CustomPainter {
  _Anello(this.raggio);

  final double raggio;

  @override
  void paint(Canvas canvas, Size size) {
    final r = RRect.fromRectAndRadius((Offset.zero & size).inflate(4.5), Radius.circular(raggio + 4.5));
    canvas.drawRRect(
      r,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3
        ..color = Token.verdigris,
    );
  }

  @override
  bool shouldRepaint(_Anello vecchio) => vecchio.raggio != raggio;
}
