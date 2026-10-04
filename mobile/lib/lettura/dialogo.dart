/// La conversazione con il lettore (`frontend/v2/lettura/dialogo.tsx`): le domande dell'intervista e le risposte. Si
/// scorre solo dentro il riquadro, mai la pagina: una battuta nuova del lettore si porta in vista dal suo inizio (e si
/// scrive a macchina, due lettere ogni 18 ms), la propria in fondo.
library;

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

import '../componenti/bottoni.dart';
import '../componenti/campi.dart' show Puntini;
import '../l10n/testi.dart';
import '../tema/tema.dart';
import 'comuni.dart';

/// Chi parla.
enum Autore {
  /// Il lettore.
  oracolo,

  /// Chi consulta.
  utente,

  /// Un messaggio del sistema (la crisi).
  sistema,
}

/// Una battuta (`Battuta` del sito).
@immutable
class Battuta {
  /// Una battuta.
  const Battuta({required this.id, required this.autore, required this.testo, this.titolo, this.macchina = false});

  /// Unica nella conversazione.
  final String id;

  /// Chi parla.
  final Autore autore;

  /// Il testo.
  final String testo;

  /// Un titolo al posto del nome di chi parla («✦»).
  final String? titolo;

  /// Le battute nuove del lettore si scrivono a macchina; quelle riprese dallo storico no.
  final bool macchina;
}

/// La conversazione.
class Dialogo extends StatefulWidget {
  /// La conversazione con le [battute].
  const Dialogo({
    super.key,
    required this.battute,
    required this.attesa,
    required this.inputAttivo,
    required this.alRispondi,
    this.alBasta,
    this.puoiFermarti = false,
  });

  /// Le battute.
  final List<Battuta> battute;

  /// Il lettore sta pensando.
  final bool attesa;

  /// Il campo della risposta (solo durante l'intervista).
  final bool inputAttivo;

  /// Una risposta.
  final ValueChanged<String> alRispondi;

  /// «Basta con le domande» (v8.5): chiude l'intervista; attivo solo dopo il minimo di domande.
  final VoidCallback? alBasta;

  /// Il minimo di domande è raggiunto.
  final bool puoiFermarti;

  @override
  State<Dialogo> createState() => _DialogoState();
}

class _DialogoState extends State<Dialogo> {
  final ScrollController _scorri = ScrollController();
  final TextEditingController _testo = TextEditingController();
  final Map<String, GlobalKey> _chiavi = {};
  String? _ultima;

  @override
  void initState() {
    super.initState();
    _testo.addListener(() => setState(() {}));
    _ultima = widget.battute.lastOrNull?.id;
    WidgetsBinding.instance.addPostFrameCallback((_) => _inFondo(animato: false));
  }

  @override
  void didUpdateWidget(Dialogo vecchio) {
    super.didUpdateWidget(vecchio);
    final ultima = widget.battute.lastOrNull;
    if (ultima != null && ultima.id != _ultima) {
      _ultima = ultima.id;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (ultima.autore == Autore.utente) {
          _inFondo();
        } else {
          _allInizio(ultima.id);
        }
      });
    }
    if (widget.attesa && !vecchio.attesa) WidgetsBinding.instance.addPostFrameCallback((_) => _inFondo());
  }

  @override
  void dispose() {
    _scorri.dispose();
    _testo.dispose();
    super.dispose();
  }

  Duration get _durata => MediaQuery.disableAnimationsOf(context) ? Duration.zero : const Duration(milliseconds: 300);

  void _inFondo({bool animato = true}) {
    if (!mounted || !_scorri.hasClients) return;
    final fine = _scorri.position.maxScrollExtent;
    if (!animato || _durata == Duration.zero) {
      _scorri.jumpTo(fine);
    } else {
      unawaited(_scorri.animateTo(fine, duration: _durata, curve: Curves.ease));
    }
  }

  /// Porta l'inizio della battuta [id] in cima al riquadro (12 px sotto il bordo), anche mentre il testo cresce.
  void _allInizio(String id) {
    final ctx = _chiavi[id]?.currentContext;
    if (!mounted || ctx == null || !_scorri.hasClients) return;
    unawaited(
      Scrollable.ensureVisible(
        ctx,
        duration: _durata,
        curve: Curves.ease,
        alignmentPolicy: ScrollPositionAlignmentPolicy.keepVisibleAtStart,
      ),
    );
  }

  void _invia() {
    final pulito = _testo.text.trim();
    if (pulito.isEmpty) return;
    _testo.clear();
    widget.alRispondi(pulito);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final media = MediaQuery.of(context);
    final stretto = media.size.width <= 640;
    final massima = stretto ? media.size.height * .58 : math.min(media.size.height * .62, 620.0);
    final battute = ConstrainedBox(
      constraints: BoxConstraints(maxHeight: massima),
      child: Semantics(
        liveRegion: true,
        child: ListView(
          controller: _scorri,
          shrinkWrap: true,
          padding: const EdgeInsets.only(right: 4.8),
          children: [
            for (final (i, b) in widget.battute.indexed) ...[
              if (i > 0) const SizedBox(height: 12.8),
              _VoceBattuta(key: _chiavi.putIfAbsent(b.id, GlobalKey.new), battuta: b),
            ],
            if (widget.attesa)
              Padding(
                padding: const EdgeInsets.only(top: 12.8),
                child: Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: Puntini(etichetta: t.lettura_pensa, colore: Token.brass),
                ),
              ),
          ],
        ),
      ),
    );

    final campo = _Risposta(controllore: _testo, segnaposto: t.lettura_risposta_segnaposto, attivo: !widget.attesa);
    final azioni = Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        Bottone(t.lettura_rispondi, alTocco: widget.attesa || _testo.text.trim().isEmpty ? null : _invia),
        if (widget.alBasta != null)
          Bottone(
            t.lettura_basta_domande,
            variante: Variante.quieto,
            an: 'intervista_basta',
            alTocco: widget.attesa || !widget.puoiFermarti ? null : widget.alBasta,
          ),
      ],
    );

    return ConstrainedBox(
      constraints: const BoxConstraints(minHeight: 360),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          battute,
          if (widget.inputAttivo)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: CallbackShortcuts(
                bindings: {
                  const SingleActivator(LogicalKeyboardKey.enter, control: true): _invia,
                  const SingleActivator(LogicalKeyboardKey.enter, meta: true): _invia,
                },
                child: stretto
                    ? Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          campo,
                          const SizedBox(height: 9.6 + 8),
                          azioni,
                        ],
                      )
                    : Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(child: campo),
                          const SizedBox(width: 9.6),
                          Padding(padding: const EdgeInsets.only(top: 8), child: azioni),
                        ],
                      ),
              ),
            ),
        ],
      ),
    );
  }
}

/// `.battuta`: entra dal basso (10 px, .3 s); del lettore in serif su carta, di chi consulta in verderame a destra,
/// del sistema tenue.
class _VoceBattuta extends StatefulWidget {
  const _VoceBattuta({super.key, required this.battuta});

  final Battuta battuta;

  @override
  State<_VoceBattuta> createState() => _VoceBattutaState();
}

class _VoceBattutaState extends State<_VoceBattuta> with SingleTickerProviderStateMixin {
  late final AnimationController _entrata = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 300),
  );
  Timer? _macchina;
  int _n = 0;

  @override
  void initState() {
    super.initState();
    _n = widget.battuta.macchina ? 0 : widget.battuta.testo.length;
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final ridotto = MediaQuery.disableAnimationsOf(context);
    if (_entrata.value == 0 && !_entrata.isAnimating) {
      if (ridotto) {
        _entrata.value = 1;
      } else {
        unawaited(_entrata.forward());
      }
    }
    if (ridotto) _n = widget.battuta.testo.length;
    if (_n < widget.battuta.testo.length && _macchina == null) {
      _macchina = Timer.periodic(const Duration(milliseconds: 18), (_) {
        if (!mounted) return;
        setState(() => _n = math.min(widget.battuta.testo.length, _n + 2));
        if (_n >= widget.battuta.testo.length) _macchina?.cancel();
      });
    }
  }

  @override
  void dispose() {
    _macchina?.cancel();
    _entrata.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final b = widget.battuta;
    final utente = b.autore == Autore.utente;
    final sistema = b.autore == Autore.sistema;
    final stile = b.autore == Autore.oracolo
        ? Stile.serif(15.68, altezza: 1.65, colore: Token.ink)
        : Stile.sans(
            sistema ? 13.44 : 15.2,
            colore: utente ? const Color(0xFFFFFFFF) : (sistema ? Token.inkSoft : Token.ink),
          );
    final autore =
        b.titolo ??
        (utente
            ? t.lettura_tu
            : b.autore == Autore.oracolo
            ? t.lettura_lettore
            : t.lettura_sistema);
    final scrivendo = _n < b.testo.length;
    final contenuto = Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
      decoration: BoxDecoration(
        color: utente ? Token.verdigris : (sistema ? null : Token.paper),
        border: utente
            ? const Border(right: BorderSide(color: Token.verdigris, width: 2))
            : Border(left: BorderSide(color: sistema ? Token.inkSoft : Token.brass, width: 2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            autore.toUpperCase(),
            style: Stile.sans(
              11.2,
              peso: FontWeight.w700,
              em: .08,
              colore: utente ? const Color(0xFFD8E7DF) : Token.verdigris,
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text.rich(
              TextSpan(
                children: [
                  TextSpan(text: b.testo.substring(0, _n)),
                  if (scrivendo) spanCursore(stile),
                ],
              ),
              style: stile,
            ),
          ),
        ],
      ),
    );
    return AnimatedBuilder(
      animation: _entrata,
      builder: (context, figlio) {
        final v = Curves.easeOut.transform(_entrata.value);
        return Opacity(
          opacity: v,
          child: Transform.translate(offset: Offset(0, 10 * (1 - v)), child: figlio),
        );
      },
      child: Align(
        alignment: utente ? AlignmentDirectional.centerEnd : AlignmentDirectional.centerStart,
        child: FractionallySizedBox(
          widthFactor: sistema ? 1 : null,
          child: LayoutBuilder(
            builder: (context, vincoli) => ConstrainedBox(
              constraints: BoxConstraints(maxWidth: sistema ? vincoli.maxWidth : vincoli.maxWidth * .92),
              child: contenuto,
            ),
          ),
        ),
      ),
    );
  }
}

/// `.risposta textarea`: il campo della risposta (alto almeno 52 px, due righe, cresce col testo).
class _Risposta extends StatefulWidget {
  const _Risposta({required this.controllore, required this.segnaposto, required this.attivo});

  final TextEditingController controllore;
  final String segnaposto;
  final bool attivo;

  @override
  State<_Risposta> createState() => _RispostaState();
}

class _RispostaState extends State<_Risposta> {
  final FocusNode _fuoco = FocusNode(debugLabel: 'risposta');

  @override
  void initState() {
    super.initState();
    _fuoco.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _fuoco.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final stile = Stile.sans(16, altezza: 1.5, colore: widget.attivo ? Token.ink : Token.inkSoft);
    return Semantics(
      textField: true,
      label: widget.segnaposto,
      child: GestureDetector(
        onTap: _fuoco.requestFocus,
        child: Opacity(
          opacity: widget.attivo ? 1 : .55,
          child: Container(
            constraints: const BoxConstraints(minHeight: 52),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFFFFFFF),
              border: Border.all(color: _fuoco.hasFocus ? Token.verdigris : Token.line, width: _fuoco.hasFocus ? 2 : 1),
            ),
            child: Stack(
              children: [
                if (widget.controllore.text.isEmpty)
                  IgnorePointer(
                    child: Text(widget.segnaposto, style: stile.copyWith(color: Colori.segnaposto)),
                  ),
                EditableText(
                  controller: widget.controllore,
                  focusNode: _fuoco,
                  readOnly: !widget.attivo,
                  style: stile,
                  cursorColor: Token.ink,
                  backgroundCursorColor: Token.inkSoft,
                  selectionColor: const Color(0x4019706F),
                  minLines: 2,
                  maxLines: 8,
                  keyboardType: TextInputType.multiline,
                  textInputAction: TextInputAction.newline,
                  textCapitalization: TextCapitalization.sentences,
                  inputFormatters: [LengthLimitingTextInputFormatter(2000)],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
