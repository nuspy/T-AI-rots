/// I moduli e i riquadri del sito (v2.css, «forms» e «panels, chips, lists»), per tutte le schermate:
///
/// - [CampoTesto]: `.field` con l'etichetta sopra, il campo bianco (`input`, o `textarea` alta almeno 110 px), la nota
///   piccola sotto; anche su fondo scuro (`.dark .field`);
/// - [CampoScelta]: il `<select>` del sito, che sul telefono apre un elenco: qui un dialogo con le voci;
/// - [Casella]: `.check` (la casella con `accent-color: var(--verdigris)`), con titolo in grassetto e spiegazione
///   (`.cookie-voce`) o solo testo;
/// - [Interruttore]: `.interruttore` (la levetta del rinnovo automatico, `role=switch`);
/// - [Pillola]: `.chip`, premibile e acceso (`aria-pressed`);
/// - [Avviso], [Errore], [Successo]: `.notice` (anche `.notice.dark`), `.error`, `.success`;
/// - [Pannello]: `.panel`, con il titolo serif.
library;

import 'dart:async';

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';

import '../tema/tema.dart';
import 'modale.dart';
import 'premibile.dart';
import 'testi.dart';

/// `.field > span`: l'etichetta di un campo (`.84rem`, 600); sul fondo scuro chiara.
TextStyle stileEtichettaCampo({bool scuro = false}) =>
    Stile.sans(13.44, peso: FontWeight.w600, colore: scuro ? const Color(0xFFF6ECDD) : Token.ink, altezza: 1.6);

/// `.field small`.
TextStyle stileNotaCampo({bool scuro = false}) =>
    Stile.sans(12.8, colore: scuro ? const Color(0xFFD5C4DA) : Token.inkSoft, altezza: 1.6);

/// Un campo di testo del sito (`.field`).
class CampoTesto extends StatefulWidget {
  /// Un campo.
  const CampoTesto({
    super.key,
    this.etichetta,
    this.nota,
    this.controllore,
    this.segnaposto,
    this.righe = 1,
    this.minimoRighe,
    this.tastiera,
    this.azione,
    this.alInvio,
    this.alCambio,
    this.nascosto = false,
    this.lunghezzaMassima,
    this.attivo = true,
    this.scuro = false,
    this.maiuscole = false,
    this.fuoco,
    this.autofocus = false,
    this.formattatori = const [],
    this.semantica,
    this.margineSotto = 16,
  });

  /// `.field > span`.
  final String? etichetta;

  /// `.field small`, sotto il campo.
  final String? nota;

  /// Il testo.
  final TextEditingController? controllore;

  /// Il `placeholder`.
  final String? segnaposto;

  /// Le righe al massimo (1: `input`; più di una o `null`: `textarea`, che cresce col testo).
  final int? righe;

  /// Le righe al minimo per un `textarea` (`min-height: 110px` del sito: 4 righe).
  final int? minimoRighe;

  /// La tastiera (`type="email"`, `type="date"`…).
  final TextInputType? tastiera;

  /// Il tasto d'invio della tastiera.
  final TextInputAction? azione;

  /// Il tasto d'invio premuto.
  final ValueChanged<String>? alInvio;

  /// Il testo è cambiato.
  final ValueChanged<String>? alCambio;

  /// `type="password"`.
  final bool nascosto;

  /// `maxLength`.
  final int? lunghezzaMassima;

  /// `disabled` (falso).
  final bool attivo;

  /// Sul fondo prugna (`.dark .field`).
  final bool scuro;

  /// `text-transform: uppercase` (i codici).
  final bool maiuscole;

  /// Il fuoco, se lo gestisce chi usa il campo.
  final FocusNode? fuoco;

  /// `autofocus`.
  final bool autofocus;

  /// Filtri sull'immissione.
  final List<TextInputFormatter> formattatori;

  /// L'etichetta per i lettori di schermo, se non c'è quella visibile (`aria-label`).
  final String? semantica;

  /// `.field { margin: 0 0 1rem }`.
  final double margineSotto;

  @override
  State<CampoTesto> createState() => _CampoTestoState();
}

class _CampoTestoState extends State<CampoTesto> {
  TextEditingController? _proprio;
  FocusNode? _fuocoProprio;

  TextEditingController get _testo => widget.controllore ?? (_proprio ??= TextEditingController());
  FocusNode get _fuoco => widget.fuoco ?? (_fuocoProprio ??= FocusNode());
  final GlobalKey<EditableTextState> _campo = GlobalKey(debugLabel: 'campo');

  @override
  void initState() {
    super.initState();
    _fuoco.addListener(_ridisegna);
  }

  void _ridisegna() => setState(() {});

  @override
  void dispose() {
    _fuoco.removeListener(_ridisegna);
    _proprio?.dispose();
    _fuocoProprio?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final multi = widget.righe == null || widget.righe! > 1;
    final stile = Stile.sans(16, colore: Token.ink, altezza: 1.5);
    final minimo = multi ? (widget.minimoRighe ?? 4) : 1;
    final campo = Container(
      constraints: BoxConstraints(minHeight: multi ? 110 : Token.altezzaBottone),
      padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 11.2),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        border: Border.all(color: Token.line),
      ),
      foregroundDecoration: _fuoco.hasFocus
          ? BoxDecoration(border: Border.all(color: Token.verdigris, width: 2))
          : null,
      alignment: multi ? Alignment.topLeft : Alignment.centerLeft,
      child: Stack(
        alignment: multi ? AlignmentDirectional.topStart : AlignmentDirectional.centerStart,
        children: [
          if (widget.segnaposto != null)
            ValueListenableBuilder(
              valueListenable: _testo,
              builder: (context, valore, _) => valore.text.isEmpty
                  ? IgnorePointer(
                      child: Text(
                        widget.segnaposto!,
                        maxLines: multi ? null : 1,
                        overflow: multi ? null : TextOverflow.ellipsis,
                        style: stile.copyWith(color: Colori.segnaposto),
                      ),
                    )
                  : const SizedBox.shrink(),
            ),
          EditableText(
            key: _campo,
            controller: _testo,
            focusNode: _fuoco,
            autofocus: widget.autofocus,
            readOnly: !widget.attivo,
            style: widget.attivo ? stile : stile.copyWith(color: Token.inkSoft),
            cursorColor: Token.ink,
            backgroundCursorColor: Token.inkSoft,
            selectionColor: const Color(0x4019706F),
            maxLines: multi ? widget.righe : 1,
            minLines: multi ? minimo : null,
            keyboardType: widget.tastiera ?? (multi ? TextInputType.multiline : TextInputType.text),
            textInputAction: widget.azione ?? (multi ? TextInputAction.newline : TextInputAction.done),
            obscureText: widget.nascosto,
            textCapitalization: widget.maiuscole ? TextCapitalization.characters : TextCapitalization.sentences,
            onSubmitted: widget.alInvio,
            onChanged: widget.alCambio,
            inputFormatters: [
              if (widget.lunghezzaMassima != null) LengthLimitingTextInputFormatter(widget.lunghezzaMassima),
              if (widget.maiuscole) const _Maiuscole(),
              ...widget.formattatori,
            ],
          ),
        ],
      ),
    );
    return Padding(
      padding: EdgeInsets.only(bottom: widget.margineSotto),
      child: Semantics(
        textField: true,
        label: widget.etichetta ?? widget.semantica,
        child: Opacity(
          opacity: widget.attivo ? 1 : .55,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (widget.etichetta != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 5.6),
                  child: ExcludeSemantics(
                    child: Text(widget.etichetta!, style: stileEtichettaCampo(scuro: widget.scuro)),
                  ),
                ),
              GestureDetector(onTap: () => mostraTastiera(_fuoco, _campo), child: campo),
              if (widget.nota != null)
                Padding(
                  padding: const EdgeInsets.only(top: 5.6),
                  child: Text(widget.nota!, style: stileNotaCampo(scuro: widget.scuro)),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Maiuscole extends TextInputFormatter {
  const _Maiuscole();

  @override
  TextEditingValue formatEditUpdate(TextEditingValue vecchio, TextEditingValue nuovo) =>
      nuovo.copyWith(text: nuovo.text.toUpperCase());
}

/// Il `<select>` del sito: la casella col valore e «▾»; al tocco, l'elenco in un dialogo.
class CampoScelta<T> extends StatelessWidget {
  /// Una scelta fra le [voci] (valore → testo).
  const CampoScelta({
    super.key,
    required this.etichetta,
    required this.voci,
    required this.valore,
    required this.alCambio,
    this.nota,
    this.scuro = false,
    this.attivo = true,
    this.margineSotto = 16,
  });

  /// L'etichetta sopra (anche il titolo del dialogo).
  final String etichetta;

  /// Le voci, nell'ordine.
  final List<(T, String)> voci;

  /// Il valore scelto.
  final T valore;

  /// Una scelta fatta.
  final ValueChanged<T> alCambio;

  /// La nota sotto.
  final String? nota;

  /// Sul fondo scuro.
  final bool scuro;

  /// Attivo.
  final bool attivo;

  /// Il margine sotto.
  final double margineSotto;

  Future<void> _apri(BuildContext context) async {
    final scelta = await apriModale<(T,)>(
      context,
      titolo: etichetta,
      costruisci: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final (v, testo) in voci)
            Premibile(
              alTocco: () => Navigator.of(context).pop((v,)),
              selezionato: v == valore,
              costruisci: (context, premuto) => Container(
                constraints: const BoxConstraints(minHeight: 48),
                alignment: AlignmentDirectional.centerStart,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: v == valore ? Token.plum : (premuto ? Token.mist : null),
                  border: const Border(bottom: BorderSide(color: Token.line)),
                ),
                child: Text(testo, style: Stile.sans(16, colore: v == valore ? const Color(0xFFFFF7E8) : Token.ink)),
              ),
            ),
        ],
      ),
    );
    if (scelta != null) alCambio(scelta.$1);
  }

  @override
  Widget build(BuildContext context) {
    final testo = voci.where((v) => v.$1 == valore).map((v) => v.$2).firstOrNull ?? '';
    return Padding(
      padding: EdgeInsets.only(bottom: margineSotto),
      child: Opacity(
        opacity: attivo ? 1 : .55,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 5.6),
              child: Text(etichetta, style: stileEtichettaCampo(scuro: scuro)),
            ),
            Premibile(
              alTocco: attivo ? () => unawaited(_apri(context)) : null,
              etichetta: '$etichetta: $testo',
              costruisci: (context, premuto) => Container(
                constraints: const BoxConstraints(minHeight: Token.altezzaBottone),
                padding: const EdgeInsets.fromLTRB(12.8, 11.2, 12.8, 11.2),
                decoration: BoxDecoration(
                  color: premuto ? const Color(0xFFF7F3EC) : const Color(0xFFFFFFFF),
                  border: Border.all(color: Token.line),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(testo, style: Stile.sans(16, colore: Token.ink, altezza: 1.5)),
                    ),
                    Text('▾', style: Stile.sans(12, colore: Token.inkSoft)),
                  ],
                ),
              ),
            ),
            if (nota != null)
              Padding(
                padding: const EdgeInsets.only(top: 5.6),
                child: Text(nota!, style: stileNotaCampo(scuro: scuro)),
              ),
          ],
        ),
      ),
    );
  }
}

/// `.check`: la casella del browser con `accent-color: var(--verdigris)` (20×20) e il testo accanto; tutta la riga
/// si tocca (è il `<label>`). Con [testo] è `.cookie-voce`: il titolo in grassetto e la spiegazione piccola sotto.
class Casella extends StatelessWidget {
  /// Una casella.
  const Casella({
    super.key,
    required this.valore,
    required this.alCambio,
    required this.titolo,
    this.testo,
    this.grassetto,
    this.scuro = false,
    this.attiva = true,
    this.stileTitolo,
  });

  /// Spuntata.
  final bool valore;

  /// Il nuovo valore.
  final ValueChanged<bool> alCambio;

  /// Il testo accanto.
  final String titolo;

  /// La spiegazione sotto (`small`).
  final String? testo;

  /// Il titolo in grassetto (predefinito: se c'è la spiegazione).
  final bool? grassetto;

  /// Sul fondo scuro.
  final bool scuro;

  /// Attiva.
  final bool attiva;

  /// Uno stile diverso per il titolo.
  final TextStyle? stileTitolo;

  @override
  Widget build(BuildContext context) {
    final colore = scuro ? const Color(0xFFF6ECDD) : Token.ink;
    return MergeSemantics(
      child: Opacity(
        opacity: attiva ? 1 : .55,
        child: Premibile(
          alTocco: attiva ? () => alCambio(!valore) : null,
          pulsante: false,
          costruisci: (context, premuto) => ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 44),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 9.6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 2.4),
                    child: Semantics(
                      checked: valore,
                      child: SizedBox(width: 20, height: 20, child: CustomPaint(painter: Casellina(valore))),
                    ),
                  ),
                  const SizedBox(width: 9.6),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          titolo,
                          style:
                              stileTitolo ??
                              Stile.sans(
                                14.4,
                                peso: (grassetto ?? testo != null) ? FontWeight.w700 : FontWeight.w400,
                                colore: colore,
                                altezza: 1.6,
                              ),
                        ),
                        if (testo != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 2.4),
                            child: Text(
                              testo!,
                              style: Stile.sans(
                                12.8,
                                colore: scuro ? const Color(0xFFD5C4DA) : Token.inkSoft,
                                altezza: 1.45,
                              ),
                            ),
                          ),
                      ],
                    ),
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

/// La casella disegnata: bordo grigio quando è vuota, verderame pieno con la spunta bianca quando è scelta.
class Casellina extends CustomPainter {
  /// Spuntata o no.
  const Casellina(this.scelta);

  /// Spuntata.
  final bool scelta;

  @override
  void paint(Canvas canvas, Size size) {
    final r = RRect.fromRectAndRadius((Offset.zero & size).deflate(1), const Radius.circular(3));
    if (!scelta) {
      canvas.drawRRect(r, Paint()..color = const Color(0xFFFFFFFF));
      canvas.drawRRect(
        r,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.5
          ..color = const Color(0xFF767676),
      );
      return;
    }
    canvas.drawRRect(r, Paint()..color = Token.verdigris);
    final spunta = Path()
      ..moveTo(size.width * .25, size.height * .52)
      ..lineTo(size.width * .43, size.height * .7)
      ..lineTo(size.width * .76, size.height * .32);
    canvas.drawPath(
      spunta,
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.2
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round
        ..color = const Color(0xFFFFFFFF),
    );
  }

  @override
  bool shouldRepaint(Casellina vecchia) => vecchia.scelta != scelta;
}

/// `.interruttore`: una levetta 46×26 (verderame quando è accesa, il pallino si sposta di 20 px in .18 s), con il
/// testo accanto e 44 px di tocco.
class Interruttore extends StatelessWidget {
  /// Una levetta.
  const Interruttore({super.key, required this.valore, required this.alCambio, required this.titolo, this.testo});

  /// Accesa.
  final bool valore;

  /// Il nuovo valore (`null`: disattivata).
  final ValueChanged<bool>? alCambio;

  /// Il testo accanto.
  final String titolo;

  /// Una spiegazione piccola sotto il titolo (`.abbonamenti-comandi .interruttore small`).
  final String? testo;

  @override
  Widget build(BuildContext context) {
    final attivo = alCambio != null;
    final ridotto = MediaQuery.disableAnimationsOf(context);
    final durata = ridotto ? Duration.zero : Token.durataTransizione;
    return Semantics(
      toggled: valore,
      enabled: attivo,
      label: titolo,
      excludeSemantics: true,
      onTap: attivo ? () => alCambio!(!valore) : null,
      child: Premibile(
        alTocco: attivo ? () => alCambio!(!valore) : null,
        pulsante: false,
        costruisci: (context, premuto) => Padding(
          padding: const EdgeInsets.symmetric(vertical: 4.8),
          child: ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 44),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Opacity(
                  opacity: attivo ? 1 : .55,
                  child: AnimatedContainer(
                    duration: durata,
                    curve: Curves.ease,
                    width: 46,
                    height: 26,
                    decoration: BoxDecoration(
                      color: valore ? Token.verdigris : const Color(0xFFE3DACE),
                      border: Border.all(color: valore ? Token.verdigris : Token.inkSoft),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: AnimatedAlign(
                      duration: durata,
                      curve: Curves.ease,
                      alignment: valore ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.all(2),
                        width: 20,
                        height: 20,
                        decoration: const BoxDecoration(
                          color: Color(0xFFFFFFFF),
                          shape: BoxShape.circle,
                          boxShadow: [BoxShadow(color: Color(0x59201026), offset: Offset(0, 1), blurRadius: 3)],
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 11.2),
                Flexible(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(titolo, style: Stile.sans(16, colore: Token.ink, altezza: 1.4)),
                      if (testo != null) Text(testo!, style: Stile.sans(12.8, colore: Token.inkSoft, altezza: 1.4)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// `.chip`: una pillola alta 44 px; accesa (`aria-pressed`, `aria-current`) prugna con il testo chiaro.
class Pillola extends StatelessWidget {
  /// Una pillola.
  const Pillola(this.testo, {super.key, this.alTocco, this.acceso = false, this.an, this.anProprieta = const {}});

  /// Il testo.
  final String testo;

  /// Al tocco (assente: solo un'etichetta).
  final VoidCallback? alTocco;

  /// Accesa.
  final bool acceso;

  /// L'evento delle statistiche.
  final String? an;

  /// Le proprietà dell'evento.
  final Map<String, String> anProprieta;

  @override
  Widget build(BuildContext context) {
    Widget pillola(bool premuto) => Container(
      constraints: const BoxConstraints(minHeight: 44),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5.6),
      decoration: BoxDecoration(
        color: acceso ? Token.plum : (premuto ? const Color(0x0F3C1846) : null),
        border: Border.all(color: acceso ? Token.plum : Token.line),
        borderRadius: BorderRadius.circular(Token.raggioPillola),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(testo, style: Stile.sans(13.12, colore: acceso ? const Color(0xFFFFF7E8) : Token.inkSoft, altezza: 1.6)),
        ],
      ),
    );
    if (alTocco == null) return pillola(false);
    return Premibile(
      alTocco: alTocco,
      selezionato: acceso,
      an: an,
      anProprieta: anProprieta,
      raggioFuoco: 22,
      costruisci: (context, premuto) => pillola(premuto),
    );
  }
}

/// `.chips`: le pillole in fila, che vanno a capo (`gap: .5rem`).
class Pillole extends StatelessWidget {
  /// Le pillole.
  const Pillole({super.key, required this.children});

  /// Le pillole.
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Wrap(spacing: 8, runSpacing: 8, children: children);
}

/// Un riquadro con la riga a sinistra: `.notice` (ottone), `.error` (rosso), `.success` (verderame).
class _Riquadro extends StatelessWidget {
  const _Riquadro({
    required this.child,
    required this.fondo,
    required this.linea,
    required this.colore,
    this.sopra = 16,
  });

  final Widget child;
  final Color fondo;
  final Color linea;
  final Color colore;
  final double sopra;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.only(top: sopra),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
      decoration: BoxDecoration(
        color: fondo,
        border: Border(left: BorderSide(color: linea, width: 3)),
      ),
      child: DefaultTextStyle.merge(
        style: Stile.sans(14.4, colore: colore, altezza: 1.6),
        child: child,
      ),
    );
  }
}

/// `.notice` (e `.notice.dark` sul prugna).
class Avviso extends StatelessWidget {
  /// Un avviso col [testo], o con un contenuto qualunque ([figlio]).
  const Avviso(this.testo, {super.key, this.scuro = false, this.sopra = 16, this.figlio, this.linea});

  /// Il testo.
  final String? testo;

  /// `.notice.dark`.
  final bool scuro;

  /// Il margine sopra (`margin-top: 1rem`).
  final double sopra;

  /// Un contenuto al posto del testo.
  final Widget? figlio;

  /// Un colore diverso per la riga (`.notice-pagamento`: rosso).
  final Color? linea;

  @override
  Widget build(BuildContext context) => _Riquadro(
    fondo: scuro ? const Color(0x0FFFFFFF) : Colori.avviso,
    linea: linea ?? Token.brass,
    colore: scuro ? const Color(0xFFEADBE9) : Token.inkSoft,
    sopra: sopra,
    child: figlio ?? Paragrafo(testo ?? ''),
  );
}

/// `.error`, con `role="alert"`.
class Errore extends StatelessWidget {
  /// Un errore.
  const Errore(this.testo, {super.key, this.sopra = 16});

  /// Il messaggio.
  final String testo;

  /// Il margine sopra.
  final double sopra;

  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: true,
    child: _Riquadro(
      fondo: Colori.fondoErrore,
      linea: Token.danger,
      colore: Token.danger,
      sopra: sopra,
      child: Paragrafo(testo),
    ),
  );
}

/// `.success`.
class Successo extends StatelessWidget {
  /// Un esito riuscito.
  const Successo(this.testo, {super.key, this.sopra = 16});

  /// Il messaggio.
  final String testo;

  /// Il margine sopra.
  final double sopra;

  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: true,
    child: _Riquadro(
      fondo: const Color(0xFFE7F2EE),
      linea: Token.verdigris,
      colore: const Color(0xFF0F4D4C),
      sopra: sopra,
      child: Paragrafo(testo),
    ),
  );
}

/// `.panel`: il riquadro chiaro col bordo sottile (`padding: clamp(1.1rem, 3vw, 1.8rem)` di lato,
/// `clamp(.6rem, 1.5vw, .9rem)` sopra e sotto), con il titolo serif (`h2`/`h3`: 1.35rem).
class Pannello extends StatelessWidget {
  /// Un pannello.
  const Pannello({super.key, this.titolo, required this.child, this.sotto = 0, this.colore = Token.paperLight});

  /// Il titolo.
  final String? titolo;

  /// Il contenuto.
  final Widget child;

  /// Lo spazio sotto (fra un pannello e l'altro, `.panel + .panel { margin-top: .5rem }`).
  final double sotto;

  /// Il fondo.
  final Color colore;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    return Container(
      margin: EdgeInsets.only(bottom: sotto),
      padding: EdgeInsets.symmetric(horizontal: w.clampVw(17.6, 3, 28.8), vertical: w.clampVw(9.6, 1.5, 14.4)),
      decoration: BoxDecoration(
        color: colore,
        border: Border.all(color: Token.line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (titolo != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 9.6),
              child: Semantics(header: true, child: TestoBilanciato(titolo!, stile: Stile.serif(21.6))),
            ),
          child,
        ],
      ),
    );
  }
}

/// `.panel h3`: un sottotitolo dentro un pannello (`font: 400 1.1rem var(--serif); margin: .5rem 0 .5rem`).
class TitoloPannello extends StatelessWidget {
  /// Un sottotitolo.
  const TitoloPannello(this.testo, {super.key});

  /// Il testo.
  final String testo;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(top: 8, bottom: 8),
    child: Semantics(header: true, child: TestoBilanciato(testo, stile: Stile.serif(17.6))),
  );
}

/// `.small.muted`: il testo piccolo e tenue.
TextStyle stilePiccolo({Color colore = Token.inkSoft}) => Stile.sans(13.44, colore: colore, altezza: 1.6);

/// La rotellina dell'attesa del sito (`.typing`): tre puntini d'ottone che pulsano (1,2 s, sfasati di .15 s).
class Puntini extends StatefulWidget {
  /// I puntini.
  const Puntini({super.key, this.etichetta, this.colore = Token.brassPale});

  /// `aria-label`.
  final String? etichetta;

  /// Il colore dei puntini.
  final Color colore;

  @override
  State<Puntini> createState() => _PuntiniState();
}

class _PuntiniState extends State<Puntini> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200));

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

  /// `@keyframes pulse { 0%, 80%, 100% { opacity: .25; scale(.8) } 40% { opacity: 1; scale(1) } }`, ease-in-out.
  static double _pulso(double t) {
    final x = t % 1;
    if (x >= .8) return 0;
    final f = x <= .4 ? x / .4 : (.8 - x) / .4;
    return Curves.easeInOut.transform(f);
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: widget.etichetta,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 9.6),
        child: AnimatedBuilder(
          animation: _c,
          builder: (context, _) => Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              for (var i = 0; i < 3; i++) ...[
                if (i > 0) const SizedBox(width: 5),
                Builder(
                  builder: (context) {
                    final p = _pulso(_c.value - i * .125);
                    return Opacity(
                      opacity: .25 + .75 * p,
                      child: Transform.scale(
                        scale: .8 + .2 * p,
                        child: Container(
                          width: 7,
                          height: 7,
                          decoration: BoxDecoration(color: widget.colore, shape: BoxShape.circle),
                        ),
                      ),
                    );
                  },
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Un tocco su un campo di testo: il fuoco e la tastiera. `requestFocus` da solo non basta quando il campo ha già il
/// fuoco ma la tastiera è stata chiusa (tasto Indietro di Android): il campo resta evidenziato e la tastiera non torna.
void mostraTastiera(FocusNode fuoco, GlobalKey<EditableTextState> campo) {
  fuoco.requestFocus();
  campo.currentState?.requestKeyboard();
}
