/// La conversazione con il lettore (`frontend/v2/lettura/dialogo.tsx`): le domande dell'intervista e le risposte. Si
/// scorre solo dentro il riquadro, mai la pagina: una battuta nuova del lettore si porta in vista dal suo inizio (e si
/// scrive a macchina, due lettere ogni 18 ms), la propria in fondo. Nella lettura in chat (v9.5, `fluido`) il
/// riquadro non c'è: la conversazione scorre con la pagina, che decide lei quando seguirla.
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

/// Un pulsante sotto il campo dell'intervista: manda il testo scritto e dice cosa viene dopo («Invia, basta con le
/// domande», «Invia e fammi un'altra domanda», «Invia e voglio dire una cosa»). Con il campo vuoto vale
/// [etichettaVuoto] (senza «Invia»); se manca, il pulsante aspetta che si scriva qualcosa.
@immutable
class InvioDialogo {
  /// Un invio.
  const InvioDialogo({
    required this.chiave,
    required this.etichetta,
    required this.alInvio,
    this.etichettaVuoto,
    this.primaria = false,
  });

  /// Il nome dell'invio (`basta`, `altra`, `dire`): anche per le statistiche dei clic (`intervista_<chiave>`).
  final String chiave;

  /// Il testo, con qualcosa scritto nel campo.
  final String etichetta;

  /// Il testo a campo vuoto; null = il pulsante aspetta che si scriva.
  final String? etichettaVuoto;

  /// Cosa fa, col testo scritto (vuoto se non si è scritto nulla).
  final ValueChanged<String> alInvio;

  /// Il pulsante principale (ottone).
  final bool primaria;
}

/// La conversazione.
class Dialogo extends StatefulWidget {
  /// La conversazione con le [battute].
  const Dialogo({
    super.key,
    required this.battute,
    required this.attesa,
    required this.inputAttivo,
    this.invii = const [],
    this.libero = false,
    this.fluido = false,
    this.alNovita,
  });

  /// Le battute.
  final List<Battuta> battute;

  /// Il lettore sta pensando.
  final bool attesa;

  /// Il campo c'è per tutta l'intervista, finché non si passa alle carte.
  final bool inputAttivo;

  /// I pulsanti sotto il campo, già scelti da chi chiama (sempre visibili, dalla prima domanda).
  final List<InvioDialogo> invii;

  /// v9.5: il campo è per il testo libero, non per una risposta.
  final bool libero;

  /// v9.5, la lettura in chat: niente riquadro con lo scorrimento interno, la conversazione scorre con la pagina, e
  /// a ogni novità si chiama [alNovita] (la pagina decide se scorrere).
  final bool fluido;

  /// Con [fluido]: una battuta nuova ([allInizio] vero: va mostrata dal suo inizio) o il campo con gli invii
  /// (falso: in vista).
  final void Function(BuildContext contesto, {required bool allInizio})? alNovita;

  @override
  State<Dialogo> createState() => _DialogoState();
}

class _DialogoState extends State<Dialogo> {
  final ScrollController _scorri = ScrollController();
  final TextEditingController _testo = TextEditingController();
  final Map<String, GlobalKey> _chiavi = {};
  final GlobalKey _chiaveScelte = GlobalKey(debugLabel: 'scelte');
  String? _ultima;

  @override
  void initState() {
    super.initState();
    _testo.addListener(() => setState(() {}));
    _ultima = widget.battute.lastOrNull?.id;
    if (!widget.fluido) WidgetsBinding.instance.addPostFrameCallback((_) => _inFondo(animato: false));
  }

  @override
  void didUpdateWidget(Dialogo vecchio) {
    super.didUpdateWidget(vecchio);
    final ultima = widget.battute.lastOrNull;
    if (ultima != null && ultima.id != _ultima) {
      _ultima = ultima.id;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (widget.fluido) {
          final ctx = _chiavi[ultima.id]?.currentContext;
          if (mounted && ctx != null) widget.alNovita?.call(ctx, allInizio: true);
        } else if (ultima.autore == Autore.utente) {
          _inFondo();
        } else {
          _allInizio(ultima.id);
        }
      });
    }
    final sceltePronte = !widget.attesa && widget.inputAttivo && widget.invii.isNotEmpty;
    final eranoPronte = !vecchio.attesa && vecchio.inputAttivo && vecchio.invii.isNotEmpty;
    if (sceltePronte && !eranoPronte) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!widget.fluido) {
          _inFondo();
        } else {
          final ctx = _chiaveScelte.currentContext;
          if (mounted && ctx != null) widget.alNovita?.call(ctx, allInizio: false);
        }
      });
    }
    if (!widget.fluido && widget.attesa && !vecchio.attesa) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _inFondo());
    }
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

  String get _pulito => _testo.text.trim();

  bool _usabile(InvioDialogo i) => !widget.attesa && (_pulito.isNotEmpty || i.etichettaVuoto != null);

  void _invia(InvioDialogo? i) {
    if (i == null || !_usabile(i)) return;
    final pulito = _pulito;
    _testo.clear();
    i.alInvio(pulito);
  }

  /// Ctrl+Invio: il pulsante principale, se si può usare; altrimenti il primo che si può usare.
  void _predefinito() =>
      _invia(widget.invii.where((i) => i.primaria && _usabile(i)).firstOrNull ?? widget.invii.where(_usabile).firstOrNull);

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final media = MediaQuery.of(context);
    final stretto = media.size.width <= 640;
    final massima = stretto ? media.size.height * .58 : math.min(media.size.height * .62, 620.0);
    final voci = <Widget>[
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
    ];
    final battute = widget.fluido
        ? Semantics(
            liveRegion: true,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: voci,
            ),
          )
        : ConstrainedBox(
            constraints: BoxConstraints(maxHeight: massima),
            child: Semantics(
              liveRegion: true,
              child: ListView(
                controller: _scorri,
                shrinkWrap: true,
                padding: const EdgeInsets.only(right: 4.8),
                children: voci,
              ),
            ),
          );

    final segnaposto = widget.libero ? t.lettura_libero_segnaposto : t.lettura_risposta_segnaposto;
    final campo = _Risposta(
      controllore: _testo,
      segnaposto: segnaposto,
      attivo: !widget.attesa,
      fuocoSubito: widget.libero,
    );
    // I tre invii, sempre visibili sotto il campo: ognuno manda il testo e dice cosa viene dopo. Sul telefono uno
    // per riga, larghi quanto il campo; più largo affiancati.
    final bottoni = [
      for (final i in widget.invii)
        Bottone(
          _pulito.isEmpty && i.etichettaVuoto != null ? i.etichettaVuoto! : i.etichetta,
          variante: i.primaria ? Variante.ottone : Variante.quieto,
          pieno: stretto,
          an: 'intervista_${i.chiave}',
          alTocco: _usabile(i) ? () => _invia(i) : null,
        ),
    ];
    final invii = Semantics(
      container: true,
      label: t.lettura_scelta_titolo,
      child: stretto
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final (k, b) in bottoni.indexed) ...[if (k > 0) const SizedBox(height: 8), b],
              ],
            )
          : Wrap(spacing: 8, runSpacing: 8, children: bottoni),
    );

    return ConstrainedBox(
      constraints: BoxConstraints(minHeight: widget.fluido ? 0 : 360),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          battute,
          if (widget.inputAttivo)
            Padding(
              key: _chiaveScelte,
              padding: const EdgeInsets.only(top: 16),
              child: CallbackShortcuts(
                bindings: {
                  const SingleActivator(LogicalKeyboardKey.enter, control: true): _predefinito,
                  const SingleActivator(LogicalKeyboardKey.enter, meta: true): _predefinito,
                },
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [campo, const SizedBox(height: 9.6 + 8), invii],
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
  const _Risposta({
    required this.controllore,
    required this.segnaposto,
    required this.attivo,
    this.fuocoSubito = false,
  });

  final TextEditingController controllore;
  final String segnaposto;
  final bool attivo;

  /// v9.5: il campo del testo libero prende subito il fuoco (si è appena scelto di scrivere).
  final bool fuocoSubito;

  @override
  State<_Risposta> createState() => _RispostaState();
}

class _RispostaState extends State<_Risposta> {
  final FocusNode _fuoco = FocusNode(debugLabel: 'risposta');

  @override
  void initState() {
    super.initState();
    _fuoco.addListener(() => setState(() {}));
    if (widget.fuocoSubito) WidgetsBinding.instance.addPostFrameCallback((_) => _fuoco.requestFocus());
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
