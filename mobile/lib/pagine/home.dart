/// La home (`frontend/v2/pagine/home.tsx`), sezione per sezione nello stesso ordine: la domanda, l'esperienza, i
/// temi, il rito (con la dichiarazione), la memoria, la differenza, i mazzi, le carte fisiche, il metodo, il percorso
/// dal gratuito alla lettura completa, la condivisione, il diario, le domande, l'ultimo invito. Le misure sono quelle
/// di v2.css per la stessa larghezza (telefono fino a 760 px, poi tablet e computer). Gli spazi pubblicitari del sito
/// non ci sono: niente pubblicità nell'app al lancio.
library;

import 'dart:math' as math;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../analytics/tracciato.dart';
import '../componenti/bottoni.dart';
import '../componenti/carta.dart';
import '../componenti/diario.dart';
import '../componenti/griglia.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// La home.
class Home extends ConsumerWidget {
  /// La home.
  const Home({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final omaggi = ref.watch(impostazioniProvider).value;
    final nIscrizione = omaggi?.creditiIscrizione ?? 3;
    final nInvito = omaggi?.creditiInvito ?? 5;
    return Pagina(
      sezioni: [
        const _Eroe(),
        const _Esperienza(),
        const _Temi(),
        const _Rito(),
        const _Memoria(),
        const _Differenza(),
        const _Mazzi(),
        const _Fisico(),
        const _Metodo(),
        _Percorso(nIscrizione: nIscrizione),
        _Condividi(nInvito: nInvito),
        DiarioNove(eyebrow: t.home_diario_eyebrow, titolo: t.home_diario_titolo, vuoto: const _DiarioRiserva()),
        const _Domande(),
        const _Finale(),
      ],
    );
  }
}

double _w(BuildContext context) => MediaQuery.sizeOf(context).width;

/// `.section-head`: eyebrow e titolo (a sinistra), e accanto un collegamento o un'introduzione; sul telefono uno sotto
/// l'altro (`display: block`).
class _TestaSezione extends StatelessWidget {
  const _TestaSezione({required this.eyebrow, required this.titolo, this.lato, this.chiaro = false, this.introTesto});

  final String eyebrow;
  final String titolo;
  final Widget? lato;
  final bool chiaro;

  /// Il testo dell'introduzione accanto al titolo, per dividere lo spazio come il flex del sito.
  final String? introTesto;

  @override
  Widget build(BuildContext context) {
    final w = _w(context);
    final testa = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(eyebrow, colore: chiaro ? Colori.eyebrowScuro : Token.verdigris),
        TitoloSezione(titolo, colore: chiaro ? Colori.titoloChiaro : Token.ink),
      ],
    );
    final Widget corpo;
    if (lato == null) {
      corpo = testa;
    } else if (w.telefono) {
      corpo = Column(crossAxisAlignment: CrossAxisAlignment.start, children: [testa, lato!]);
    } else if (introTesto != null) {
      // `display: flex; justify-content: space-between; gap: .7rem`: le due colonne partono larghe quanto il loro
      // contenuto (il titolo al massimo 19ch, l'introduzione 58ch) e, se non ci stanno, si stringono in proporzione.
      corpo = LayoutBuilder(
        builder: (context, vincoli) {
          final scala = MediaQuery.textScalerOf(context);
          double riga(String s, TextStyle st) {
            final p = TextPainter(
              text: TextSpan(text: s, style: st),
              textDirection: TextDirection.ltr,
              textScaler: scala,
            )..layout();
            final l = p.width;
            p.dispose();
            return l;
          }

          final stTitolo = Stile.titoloSezione(w);
          final stIntro = Stile.introSezione(w);
          final baseTesta = [
            riga(titolo, stTitolo).clamp(0.0, larghezzaCh(stTitolo, scala) * 19),
            riga(eyebrow.toUpperCase(), Stile.eyebrow()),
          ].reduce((a, b) => a > b ? a : b);
          // La base del paragrafo è la sua riga intera (il browser non ci applica `max-width`); il limite di 58ch
          // vale dopo, sulla larghezza che gli resta.
          final baseIntro = riga(introTesto!, stIntro);
          var lt = baseTesta;
          var li = baseIntro;
          final manca = lt + li + 11.2 - vincoli.maxWidth;
          if (manca > 0) {
            lt -= manca * baseTesta / (baseTesta + baseIntro);
            li -= manca * baseIntro / (baseTesta + baseIntro);
          }
          li = li.clamp(0.0, larghezzaCh(stIntro, scala) * 58);
          // Nessuna colonna sotto la sua parola più lunga (`min-width: auto` degli elementi flex).
          final parolaTitolo = titolo.split(' ').map((p) => riga(p, stTitolo)).reduce((a, b) => a > b ? a : b);
          if (lt < parolaTitolo) lt = parolaTitolo.ceilToDouble() + 1;
          return Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              SizedBox(width: lt, child: testa),
              SizedBox(width: li, child: lato),
            ],
          );
        },
      );
    } else {
      corpo = Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(child: testa),
          const SizedBox(width: 11.2),
          Flexible(child: lato!),
        ],
      );
    }
    // `.section-head { margin-bottom: .9rem }`.
    return Padding(padding: const EdgeInsets.only(bottom: 14.4), child: corpo);
  }
}

/* ---- l'eroe: la domanda ----------------------------------------------------------------------------------------- */

class _Eroe extends ConsumerStatefulWidget {
  const _Eroe();

  @override
  ConsumerState<_Eroe> createState() => _EroeState();
}

class _EroeState extends ConsumerState<_Eroe> {
  final _domanda = TextEditingController();
  bool _avviso = false;

  @override
  void dispose() {
    _domanda.dispose();
    super.dispose();
  }

  void _chiedi() {
    final pulita = _domanda.text.trim();
    if (pulita.length < 3) {
      setState(() => _avviso = true);
      return;
    }
    ref.read(lanternaProvider).traccia('question_submitted', {'entry': 'hero'});
    vai(context, '${R.leggi}?question=${Uri.encodeQueryComponent(pulita)}&source=hero');
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final telefono = w.telefono;
    final gutter = w.gutter;
    final display = Stile.display(w);

    final copia = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(t.home_eyebrow),
        Semantics(
          header: true,
          child: TestoBilanciato.ricco(
            TextSpan(
              style: display,
              children: [
                TextSpan(text: t.home_titolo_1),
                TextSpan(
                  text: t.home_titolo_em,
                  style: const TextStyle(color: Token.verdigris, fontStyle: FontStyle.italic),
                ),
                TextSpan(text: t.home_titolo_2),
              ],
            ),
            maxCh: 15,
          ),
        ),
        // `.hero-copy .lede { margin: 1.7rem 0 2rem; font-size: 1.1rem }`; sul telefono `1rem 0 1.2rem`, 1.02rem.
        Padding(
          padding: EdgeInsets.only(top: telefono ? 16 : 27.2, bottom: telefono ? 19.2 : 32),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxWidth: larghezzaCh(Stile.sans(telefono ? 16.32 : 17.6), MediaQuery.textScalerOf(context)) * 46,
            ),
            child: Paragrafo(
              t.home_lede,
              style: Stile.sans(telefono ? 16.32 : 17.6, colore: Token.inkSoft, altezza: 1.6),
            ),
          ),
        ),
        _ModuloDomanda(controllore: _domanda, alInvio: _chiedi, alCambio: () => setState(() => _avviso = false)),
        if (_avviso) Semantics(liveRegion: true, child: _Avviso(t.home_domanda_breve)),
        // `.minor-cta { margin-top: .6rem; gap: .4rem 1rem; font-size: .88rem }`.
        Padding(
          padding: EdgeInsets.only(top: telefono ? 9.6 : 16),
          child: Wrap(
            spacing: 16,
            runSpacing: 6.4,
            children: [
              Collegamento(
                t.home_cta_gratis,
                href: '${R.leggi}?source=hero',
                an: 'hero_cta_click',
                anProprieta: const {'dove': 'gratis'},
              ),
              Collegamento(t.home_cta_fisiche, href: R.fisica),
              Collegamento(t.home_cta_giorno, href: R.giorno),
            ],
          ),
        ),
        // `.trust-strip { margin-top: 1.05rem; padding-top: .5rem; border-top; gap: .6rem 1.2rem; .8rem }`.
        Container(
          width: double.infinity,
          margin: const EdgeInsets.only(top: 16.8),
          padding: const EdgeInsets.only(top: 8),
          decoration: const BoxDecoration(
            border: Border(top: BorderSide(color: Token.line)),
          ),
          child: Wrap(
            spacing: 19.2,
            runSpacing: 9.6,
            children: [
              for (final f in [t.home_fiducia_1, t.home_fiducia_2, t.home_fiducia_3])
                Text.rich(
                  TextSpan(
                    children: [
                      const TextSpan(
                        text: '✦ ',
                        style: TextStyle(color: Token.brass),
                      ),
                      TextSpan(text: f),
                    ],
                  ),
                  style: Stile.sans(12.8, colore: Token.inkSoft, altezza: 1.6),
                ),
            ],
          ),
        ),
      ],
    );

    final oggetto = _OggettoRituale(telefono: telefono, larghezza: w);
    final verticale = telefono ? 16.0 : w.clampVw(19.2, 2.45, 39.2);
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: Token.larghezzaEroe),
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: gutter, vertical: verticale),
          child: telefono
              ? Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [copia, const SizedBox(height: 16), oggetto],
                )
              : Row(
                  children: [
                    Expanded(flex: 92, child: copia),
                    SizedBox(width: w.clampVw(32, 6, 104)),
                    Expanded(flex: 108, child: oggetto),
                  ],
                ),
        ),
      ),
    );
  }
}

/// `.question-form`: il campo e il bottone (uno sotto l'altro sul telefono).
class _ModuloDomanda extends StatelessWidget {
  const _ModuloDomanda({required this.controllore, required this.alInvio, required this.alCambio});

  final TextEditingController controllore;
  final VoidCallback alInvio;
  final VoidCallback alCambio;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final telefono = _w(context).telefono;
    final campo = Semantics(
      textField: true,
      label: t.home_domanda_etichetta,
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 44),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Stack(
            alignment: AlignmentDirectional.centerStart,
            children: [
              ValueListenableBuilder(
                valueListenable: controllore,
                builder: (context, valore, _) => valore.text.isEmpty
                    ? IgnorePointer(
                        child: Text(
                          t.home_domanda_segnaposto,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: Stile.sans(16, colore: Colori.segnaposto, altezza: 1.6),
                        ),
                      )
                    : const SizedBox.shrink(),
              ),
              EditableText(
                controller: controllore,
                focusNode: _fuoco(context),
                style: Stile.sans(16, colore: Token.ink, altezza: 1.6),
                cursorColor: Token.ink,
                backgroundCursorColor: Token.inkSoft,
                maxLines: 1,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => alInvio(),
                onChanged: (_) => alCambio(),
                inputFormatters: const [],
                selectionColor: const Color(0x4019706F),
              ),
            ],
          ),
        ),
      ),
    );
    final bottone = Bottone(
      t.home_domanda_invia,
      variante: Variante.ottone,
      pieno: telefono,
      alTocco: alInvio,
      an: 'hero_cta_click',
      anProprieta: const {'dove': 'domanda'},
    );
    return Container(
      constraints: const BoxConstraints(maxWidth: 580),
      padding: const EdgeInsets.all(8.8),
      decoration: const BoxDecoration(
        color: Colori.carta,
        border: Border.fromBorderSide(BorderSide(color: Colori.bordoDomanda)),
        boxShadow: [BoxShadow(color: Color(0x1F3C1846), offset: Offset(0, 13), blurRadius: 40)],
      ),
      child: telefono
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [campo, const SizedBox(height: 9.6), bottone],
            )
          : Row(
              children: [
                Expanded(child: campo),
                const SizedBox(width: 9.6),
                bottone,
              ],
            ),
    );
  }

  static final Expando<FocusNode> _nodi = Expando();

  FocusNode _fuoco(BuildContext context) => _nodi[controllore] ??= FocusNode(debugLabel: 'domanda-eroe');
}

/// `.notice`: il riquadro con la riga d'ottone a sinistra.
class _Avviso extends StatelessWidget {
  const _Avviso(this.testo);

  final String testo;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12.8),
      decoration: const BoxDecoration(
        color: Colori.avviso,
        border: Border(left: BorderSide(color: Token.brass, width: 3)),
      ),
      child: Paragrafo(testo, style: Stile.sans(14.4, colore: Token.inkSoft, altezza: 1.6)),
    );
  }
}

/// `.ritual-object`: due cerchi (uno fermo con gli aloni, uno che gira piano), la carta degli Amanti inclinata e la
/// nota in prugna.
class _OggettoRituale extends StatefulWidget {
  const _OggettoRituale({required this.telefono, required this.larghezza});

  final bool telefono;
  final double larghezza;

  @override
  State<_OggettoRituale> createState() => _OggettoRitualeState();
}

class _OggettoRitualeState extends State<_OggettoRituale> with SingleTickerProviderStateMixin {
  late final AnimationController _giro = AnimationController(vsync: this, duration: const Duration(seconds: 40));

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context) || !TickerMode.valuesOf(context).enabled) {
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
    final w = widget.larghezza;
    final telefono = widget.telefono;
    // `.hero-card { width: min(238px, 43vw) }`; sul telefono `min(170px, 44vw)`.
    final carta = telefono ? math.min(170.0, w * .44) : math.min(238.0, w * .43);
    final altezzaMinima = telefono ? 260.0 : 400.0;
    return Semantics(
      image: true,
      label: t.home_oggetto_aria,
      child: LayoutBuilder(
        builder: (context, vincoli) {
          final lato = vincoli.maxWidth;
          final cerchio = math.min(490.0, lato * .86);
          final interno = math.min(360.0, lato * .65);
          final altezzaCarta = carta * 16 / 9 + 10;
          return SizedBox(
            height: math.max(altezzaMinima, altezzaCarta),
            child: Stack(
              alignment: Alignment.center,
              clipBehavior: Clip.none,
              children: [
                // `::before`: il cerchio d'ottone con due aloni.
                Container(
                  width: cerchio,
                  height: cerchio,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.fromBorderSide(BorderSide(color: Color(0xB3B28336))),
                    boxShadow: [
                      BoxShadow(color: Color(0x14B28336), spreadRadius: 22),
                      BoxShadow(color: Color(0x0F19706F), spreadRadius: 55),
                    ],
                  ),
                ),
                // `::after`: il cerchio dei raggi, che gira in 40 secondi.
                RotationTransition(
                  turns: _giro,
                  child: CustomPaint(size: Size.square(interno), painter: const _Raggi()),
                ),
                ExcludeSemantics(
                  child: Transform.rotate(
                    angle: 3 * math.pi / 180,
                    child: Container(
                      width: carta,
                      decoration: const BoxDecoration(
                        border: Border.fromBorderSide(BorderSide(color: Colori.cornice, width: 5)),
                        boxShadow: [BoxShadow(color: Color(0x57201026), offset: Offset(0, 28), blurRadius: 24)],
                      ),
                      child: ImmagineCarta('maj-06', alt: t.home_oggetto_carta),
                    ),
                  ),
                ),
                Positioned(
                  right: telefono ? lato * .02 : 0,
                  bottom: telefono
                      ? math.max(altezzaMinima, altezzaCarta) * .02
                      : math.max(altezzaMinima, altezzaCarta) * .07,
                  child: _NotaOrbita(telefono: telefono),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

/// La `conic-gradient` dei raggi: quattro spicchi sottili, ottone e verderame alternati.
class _Raggi extends CustomPainter {
  const _Raggi();

  @override
  void paint(Canvas canvas, Size size) {
    final centro = size.center(Offset.zero);
    final r = size.width / 2;
    // `from 10deg`: lo zero della CSS è in alto, quello di Flutter a destra.
    const inizio = (10 - 90) * math.pi / 180;
    final spicchi = [
      (.07, .08, const Color(0x73B28336)),
      (.25, .26, const Color(0x8019706F)),
      (.50, .51, const Color(0x73B28336)),
      (.75, .76, const Color(0x8019706F)),
    ];
    for (final (da, a, colore) in spicchi) {
      canvas.drawArc(
        Rect.fromCircle(center: centro, radius: r),
        inizio + da * 2 * math.pi,
        (a - da) * 2 * math.pi,
        true,
        Paint()..color = colore,
      );
    }
  }

  @override
  bool shouldRepaint(_Raggi vecchio) => false;
}

/// `.orbit-note`: la nota prugna inclinata.
class _NotaOrbita extends StatelessWidget {
  const _NotaOrbita({required this.telefono});

  final bool telefono;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Transform.rotate(
      angle: -4 * math.pi / 180,
      child: Container(
        constraints: BoxConstraints(maxWidth: telefono ? 180 : 210),
        padding: telefono
            ? const EdgeInsets.symmetric(horizontal: 14.4, vertical: 12)
            : const EdgeInsets.symmetric(horizontal: 18.4, vertical: 16),
        decoration: const BoxDecoration(
          color: Token.plum,
          boxShadow: [BoxShadow(color: Color(0x40201026), offset: Offset(0, 16), blurRadius: 28)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 5.6),
              child: Text(
                t.home_nota_titolo.toUpperCase(),
                style: Stile.sans(10.72, peso: FontWeight.w700, colore: Token.brassPale, em: .08),
              ),
            ),
            // `.orbit-note` è fra i testi bilanciati del CSS (`text-wrap: balance`).
            TestoBilanciato(
              t.home_nota_testo,
              stile: Stile.serif(
                telefono ? 13.6 : 14.72,
                stile: FontStyle.italic,
                altezza: 1.5,
                colore: const Color(0xFFFBF3E5),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/* ---- l'esperienza -------------------------------------------------------------------------------------------- */

class _Esperienza extends StatelessWidget {
  const _Esperienza();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final telefono = w.telefono;
    final imbottitura = EdgeInsets.symmetric(
      horizontal: telefono ? 17.6 : w.clampVw(24, 4, 52),
      vertical: w.clampVw(12, 2, 25.6),
    );
    Widget messaggio(String testo, {bool utente = false}) => Align(
      alignment: utente ? AlignmentDirectional.centerEnd : AlignmentDirectional.centerStart,
      child: FractionallySizedBox(
        widthFactor: telefono ? .94 : .9,
        alignment: utente ? AlignmentDirectional.centerEnd : AlignmentDirectional.centerStart,
        child: Align(
          alignment: utente ? AlignmentDirectional.centerEnd : AlignmentDirectional.centerStart,
          child: Container(
            padding: telefono
                ? const EdgeInsets.symmetric(horizontal: 12, vertical: 9.6)
                : const EdgeInsets.symmetric(horizontal: 16, vertical: 14.4),
            decoration: BoxDecoration(
              color: utente ? const Color(0x2419706F) : const Color(0x0EFFFFFF),
              border: utente
                  ? const Border(right: BorderSide(color: Token.verdigris, width: 2))
                  : const Border(left: BorderSide(color: Token.brass, width: 2)),
            ),
            child: Paragrafo(
              testo,
              style: Stile.sans(telefono ? 14.08 : 14.88, altezza: 1.6, colore: Colori.testoEsperienza),
            ),
          ),
        ),
      ),
    );
    final copia = Container(
      color: Colori.fondoDemo,
      padding: imbottitura,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Eyebrow(t.home_demo_contesto, colore: Colori.eyebrowScuro, sotto: telefono ? 9.6 : 16),
          Semantics(
            label: t.home_demo_esempio,
            container: true,
            child: Padding(
              padding: EdgeInsets.only(top: telefono ? 16 - 9.6 : 32 - 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  messaggio(t.home_demo_1, utente: true),
                  SizedBox(height: telefono ? 9.6 : 16),
                  messaggio(t.home_demo_2),
                  SizedBox(height: telefono ? 9.6 : 16),
                  messaggio(t.home_demo_3, utente: true),
                ],
              ),
            ),
          ),
        ],
      ),
    );
    final dorso = telefono ? 84.0 : 122.0;
    final passo = telefono ? 44.0 : 62.0;
    final rito = Container(
      color: Colori.fondoDemo,
      padding: imbottitura,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Eyebrow(t.home_demo_carte, colore: Colori.eyebrowScuro),
          ExcludeSemantics(
            child: SizedBox(
              height: telefono ? 190 : 330,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  for (final (dx, dy, gradi) in [
                    (-passo, telefono ? 6.0 : 10.0, telefono ? -12.0 : -13.0),
                    (0.0, -12.0, 0.0),
                    (passo, telefono ? 8.0 : 12.0, telefono ? 12.0 : 13.0),
                  ])
                    Transform.translate(
                      offset: Offset(dx, dy),
                      child: Transform.rotate(
                        angle: gradi * math.pi / 180,
                        child: Container(
                          width: dorso,
                          decoration: const BoxDecoration(
                            boxShadow: [BoxShadow(color: Color(0x59000000), offset: Offset(0, 16), blurRadius: 20)],
                          ),
                          child: const ImmagineCarta('dorso'),
                        ),
                      ),
                    ),
                  Positioned(
                    bottom: 8,
                    child: Text(t.home_demo_didascalia, style: Stile.sans(12.16, colore: Colori.introScura)),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
    return ColoredBox(
      color: Token.plumDeep,
      child: Fascia(
        child: DefaultTextStyle.merge(
          style: const TextStyle(color: Colori.testoEsperienza),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _TestaSezione(
                eyebrow: t.home_demo_eyebrow,
                titolo: t.home_demo_titolo,
                chiaro: true,
                lato: IntroSezione(t.home_demo_intro, colore: Colori.introScura),
                introTesto: t.home_demo_intro,
              ),
              DecoratedBox(
                decoration: BoxDecoration(
                  color: const Color(0x47D6B66D),
                  border: Border.all(color: const Color(0x59D6B66D)),
                ),
                child: Padding(
                  padding: EdgeInsets.zero,
                  child: telefono
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [copia, const SizedBox(height: 1), rito],
                        )
                      : IntrinsicHeight(
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Expanded(flex: 8, child: copia),
                              const SizedBox(width: 1),
                              Expanded(flex: 12, child: rito),
                            ],
                          ),
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

/* ---- i temi ---------------------------------------------------------------------------------------------------- */

class _Temi extends StatelessWidget {
  const _Temi();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final colonne = w.telefono ? 2 : (w.medio ? 3 : 6);
    return Fascia(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _TestaSezione(
            eyebrow: t.home_temi_eyebrow,
            titolo: t.home_temi_titolo,
            lato: Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Align(
                alignment: AlignmentDirectional.centerStart,
                child: Bottone(t.home_temi_cta, href: R.leggi, variante: Variante.quieto),
              ),
            ),
          ),
          Griglia.righe(
            colonne: colonne,
            linea: Token.line,
            children: [for (final tema in t.homeTemi) _Tema(tema: tema)],
          ),
        ],
      ),
    );
  }
}

class _Tema extends StatelessWidget {
  const _Tema({required this.tema});

  final ({String chiave, String simbolo, String nome, String nota}) tema;

  @override
  Widget build(BuildContext context) {
    final telefono = _w(context).telefono;
    return Premibile(
      alTocco: () => vai(context, '${R.leggi}?topic=${tema.chiave}'),
      collegamento: true,
      an: 'tema',
      anProprieta: {'tema': tema.chiave},
      costruisci: (context, premuto) {
        final testo = premuto ? const Color(0xFFFFFFFF) : Token.ink;
        final simbolo = Text(tema.simbolo, style: Stile.serif(telefono ? 23.2 : 38.4, altezza: 1, colore: Token.brass));
        final nome = Text(tema.nome, style: Stile.serif(16, altezza: 1.6, colore: testo));
        final nota = Text(tema.nota, style: Stile.sans(13.33, altezza: 1.25, colore: testo));
        return Container(
          color: premuto ? Token.plum : Token.paper,
          padding: telefono ? const EdgeInsets.symmetric(horizontal: 13.6, vertical: 11.2) : const EdgeInsets.all(19.2),
          child: telefono
              ? Row(
                  children: [
                    simbolo,
                    const SizedBox(width: 8.8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [nome, const SizedBox(height: 1.6), nota],
                      ),
                    ),
                  ],
                )
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [simbolo, const SizedBox(height: 8), nome, const SizedBox(height: 8), nota],
                ),
        );
      },
    );
  }
}

/* ---- il rito e la dichiarazione ------------------------------------------------------------------------------- */

class _Rito extends StatelessWidget {
  const _Rito();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final colonne = w.telefono ? 2 : (w.medio ? 3 : 6);
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Eyebrow(t.home_rito_eyebrow),
          TitoloSezione(t.home_rito_titolo),
          const SizedBox(height: 12),
          Griglia(
            colonne: colonne,
            spazioColonne: w.telefono ? 14.4 : 8,
            spazioRighe: w.telefono ? 16 : (w.medio ? 25.6 : 8),
            allunga: false,
            children: [
              for (final (i, p) in t.homeRitoPassi.indexed) _PassoRito(numero: i + 1, titolo: p.titolo, testo: p.testo),
            ],
          ),
          const _Dichiarazione(),
        ],
      ),
    );
  }
}

class _PassoRito extends StatelessWidget {
  const _PassoRito({required this.numero, required this.titolo, required this.testo});

  final int numero;
  final String titolo;
  final String testo;

  @override
  Widget build(BuildContext context) {
    final telefono = _w(context).telefono;
    final titoloStile = Stile.sans(12.16, peso: FontWeight.w700, em: .06, altezza: 1.6);
    return Container(
      padding: EdgeInsets.only(top: telefono ? 10.4 : 19.2, right: telefono ? 0 : 5.6),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Token.brass, width: 2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (telefono)
            Text.rich(
              TextSpan(
                children: [
                  TextSpan(
                    text: '$numero ',
                    style: Stile.serif(17.6, colore: Token.verdigris),
                  ),
                  TextSpan(text: titolo.toUpperCase(), style: titoloStile),
                ],
              ),
            )
          else ...[
            Padding(
              padding: const EdgeInsets.only(bottom: 9.6),
              child: Text('$numero', style: Stile.serif(24, colore: Token.verdigris)),
            ),
            Text(titolo.toUpperCase(), style: titoloStile),
          ],
          Padding(
            padding: EdgeInsets.only(top: telefono ? 4.8 : 8),
            child: Paragrafo(testo, style: Stile.sans(telefono ? 13.44 : 13.6, colore: Token.inkSoft, altezza: 1.6)),
          ),
        ],
      ),
    );
  }
}

/// La dichiarazione del rito (`frontend/v2/componenti/dichiarazione.tsx`, forma intera).
class _Dichiarazione extends StatelessWidget {
  const _Dichiarazione();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final telefono = w.telefono;
    final testa = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(t.home_vero_eyebrow, colore: Token.brassPale),
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: TestoBilanciato(
            t.home_vero_titolo,
            stile: Stile.serif(w.clampVw(30.4, 3.6, 51.2), altezza: 1.1, em: -.04, colore: Colori.titoloChiaro),
            maxCh: 16,
          ),
        ),
        Paragrafo(t.home_vero_testo, style: Stile.sans(16, colore: const Color(0xFFD9CADE), altezza: 1.6)),
      ],
    );
    final fatti = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final f in t.homeVeroFatti)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8),
            decoration: const BoxDecoration(
              border: Border(top: BorderSide(color: Color(0x66D6B66D))),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(bottom: 4.8),
                  child: Text(f.titolo, style: Stile.serif(18.4, colore: Token.brassPale)),
                ),
                Text(f.testo, style: Stile.sans(14.4, colore: const Color(0xFFE6D8E8), altezza: 1.6)),
              ],
            ),
          ),
      ],
    );
    final chiusa = Container(
      padding: const EdgeInsets.only(top: 8),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0x66D6B66D))),
      ),
      child: Text(
        t.home_vero_chiusa,
        style: Stile.serif(17.6, stile: FontStyle.italic, altezza: 1.5, colore: const Color(0xFFFBF3E5)),
      ),
    );
    final orizzontale = telefono ? 19.2 : w.clampVw(22.4, 4, 48);
    final verticale = w.clampVw(12, 2, 24);
    final ombra = telefono ? 8.0 : 14.0;
    return Container(
      // L'ombra piena (box-shadow senza sfocatura) esce dal riquadro senza spostare niente, come nel CSS.
      margin: const EdgeInsets.only(top: 16.8),
      padding: EdgeInsets.symmetric(horizontal: orizzontale, vertical: verticale),
      decoration: BoxDecoration(
        color: Token.plumDeep,
        boxShadow: [BoxShadow(color: const Color(0x59B28336), offset: Offset(ombra, ombra))],
      ),
      child: Semantics(
        label: t.home_vero_eyebrow,
        container: true,
        child: telefono
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [testa, const SizedBox(height: 8.8), fatti, const SizedBox(height: 8.8), chiusa],
              )
            : Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(flex: 10, child: testa),
                      const SizedBox(width: 48),
                      Expanded(flex: 11, child: fatti),
                    ],
                  ),
                  const SizedBox(height: 8.8),
                  chiusa,
                ],
              ),
      ),
    );
  }
}

/* ---- la memoria ------------------------------------------------------------------------------------------------ */

class _Memoria extends StatelessWidget {
  const _Memoria();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final telefono = w.telefono;
    final ombra = telefono ? 9.0 : 15.0;
    final scheda = Container(
      padding: EdgeInsets.symmetric(horizontal: telefono ? 22.4 : 35.2, vertical: 17.6),
      decoration: BoxDecoration(
        color: Token.plum,
        boxShadow: [BoxShadow(color: const Color(0x59B28336), offset: Offset(ombra, ombra))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 11.2),
            child: Text(
              t.home_memoria_etichetta.toUpperCase(),
              style: Stile.sans(11.2, peso: FontWeight.w700, em: .1, colore: Token.brassPale, altezza: 1.6),
            ),
          ),
          ConstrainedBox(
            constraints: BoxConstraints(
              maxWidth: larghezzaCh(Stile.serif(telefono ? 19.2 : 23.2), MediaQuery.textScalerOf(context)) * 28,
            ),
            child: Text(
              t.home_memoria_citazione,
              style: Stile.serif(
                telefono ? 19.2 : 23.2,
                stile: FontStyle.italic,
                altezza: 1.45,
                colore: const Color(0xFFF8F0E1),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(top: 9.6),
            child: Text(t.home_memoria_piede, style: Stile.sans(12.8, colore: const Color(0xFFD5C4DA), altezza: 1.6)),
          ),
        ],
      ),
    );
    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(t.home_memoria_eyebrow),
        TitoloSezione(t.home_memoria_titolo),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (final v in t.homeMemoriaVoci)
                Container(
                  padding: EdgeInsets.symmetric(vertical: telefono ? 9.6 : 13.6),
                  decoration: const BoxDecoration(
                    border: Border(bottom: BorderSide(color: Token.line)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(v.titolo, style: Stile.sans(14.72, peso: FontWeight.w700, altezza: 1.6)),
                      Text(v.testo, style: Stile.sans(13.76, colore: Token.inkSoft, altezza: 1.6)),
                    ],
                  ),
                ),
            ],
          ),
        ),
        Bottone(t.home_memoria_cta, href: R.storia, variante: Variante.quieto),
      ],
    );
    return ColoredBox(
      color: Token.mist,
      child: Fascia(
        child: telefono
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  scheda,
                  SizedBox(height: w.clampVw(11.2, 2.8, 44.8)),
                  testo,
                ],
              )
            : Row(
                children: [
                  Expanded(flex: 9, child: scheda),
                  SizedBox(width: w.clampVw(11.2, 2.8, 44.8)),
                  Expanded(flex: 11, child: testo),
                ],
              ),
      ),
    );
  }
}

/* ---- la differenza --------------------------------------------------------------------------------------------- */

class _Differenza extends StatelessWidget {
  const _Differenza();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final colonne = w.telefono ? 1 : (w.medio ? 2 : 4);
    final voci = t.homeDiff;
    return Fascia(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Eyebrow(t.home_diff_eyebrow),
          Griglia.righe(
            colonne: colonne,
            pesi: colonne == 4 ? const [11, 10, 10, 10] : null,
            linea: Token.line,
            children: [
              for (final (i, d) in voci.indexed)
                _VoceDifferenza(prima: i == 0, simbolo: d.simbolo, titolo: d.titolo, testo: d.testo),
            ],
          ),
        ],
      ),
    );
  }
}

class _VoceDifferenza extends StatelessWidget {
  const _VoceDifferenza({required this.prima, required this.simbolo, required this.titolo, required this.testo});

  final bool prima;
  final String simbolo;
  final String titolo;
  final String testo;

  @override
  Widget build(BuildContext context) {
    final telefono = _w(context).telefono;
    return Container(
      color: prima ? Token.verdigris : Colori.differenza,
      padding: EdgeInsets.symmetric(horizontal: telefono ? 17.6 : 22.4, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 8.8),
            child: Text(
              simbolo,
              textAlign: telefono ? TextAlign.center : TextAlign.start,
              style: Stile.serif(27.2, colore: prima ? Token.brassPale : Token.brass),
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              titolo,
              style: Stile.serif(telefono ? 18.4 : 20.8, colore: prima ? const Color(0xFFFFF7E8) : Token.ink),
            ),
          ),
          Paragrafo(testo, style: Stile.sans(13.92, colore: prima ? Token.mist : Token.inkSoft, altezza: 1.6)),
        ],
      ),
    );
  }
}

/* ---- i mazzi ---------------------------------------------------------------------------------------------------- */

class _Mazzi extends ConsumerWidget {
  const _Mazzi();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final slug = ref.watch(mazzoPredefinitoProvider).value;
    final w = _w(context);
    final telefono = w.telefono;
    final ventaglio = ExcludeSemantics(
      child: SizedBox(
        height: 390,
        child: Stack(
          alignment: Alignment.center,
          children: [
            for (final (id, dx, dy, gradi) in [
              ('maj-17', -86.0, 5.0, -18.0),
              ('maj-02', 86.0, 7.0, 18.0),
              ('maj-06', 0.0, -15.0, 0.0),
            ])
              Transform.translate(
                offset: Offset(dx, dy),
                child: Transform.rotate(
                  angle: gradi * math.pi / 180,
                  child: Container(
                    width: 125,
                    decoration: const BoxDecoration(
                      border: Border.fromBorderSide(BorderSide(color: Colori.cornice, width: 3)),
                      boxShadow: [BoxShadow(color: Color(0x40201026), offset: Offset(0, 16), blurRadius: 26)],
                    ),
                    child: ImmagineCarta(id),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.symmetric(horizontal: 8.8, vertical: 4.48),
          color: Token.verdigris,
          child: Text(
            t.home_mazzi_disponibile.toUpperCase(),
            style: Stile.sans(11.2, peso: FontWeight.w700, em: .07, colore: const Color(0xFFFFF7E8), altezza: 1.6),
          ),
        ),
        Eyebrow(t.home_mazzi_eyebrow),
        TitoloSezione(t.home_mazzi_titolo),
        IntroSezione(t.home_mazzi_intro),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 32),
          child: Semantics(
            label: t.home_mazzi_futuri_aria,
            container: true,
            child: Wrap(
              spacing: 10.4,
              runSpacing: 10.4,
              children: [
                for (final m in t.homeMazziFuturi)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 11.2, vertical: 8),
                    decoration: BoxDecoration(border: Border.all(color: Token.line)),
                    child: Text(m, style: Stile.sans(12.8, colore: Token.inkSoft, altezza: 1.6)),
                  ),
              ],
            ),
          ),
        ),
        FilaBottoni(
          children: [
            Bottone(t.home_mazzi_cta, href: slug == null ? R.mazzi : R.mazzo(slug), variante: Variante.quieto),
            Bottone(t.home_mazzi_voto, href: R.voto, variante: Variante.quieto),
          ],
        ),
      ],
    );
    final spazio = w.clampVw(11.2, 2.1, 28);
    return Fascia(
      child: telefono
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ventaglio,
                SizedBox(height: spazio),
                testo,
              ],
            )
          : Row(
              children: [
                Expanded(flex: 8, child: ventaglio),
                SizedBox(width: spazio),
                Expanded(flex: 12, child: testo),
              ],
            ),
    );
  }
}

/* ---- le carte fisiche ------------------------------------------------------------------------------------------- */

class _Fisico extends StatelessWidget {
  const _Fisico();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final telefono = w.telefono;
    final immagine = telefono ? 86.0 : 105.0;
    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(t.home_fisico_eyebrow),
        TitoloSezione(t.home_fisico_titolo),
        IntroSezione(t.home_fisico_intro),
        Bottone(t.home_fisico_cta, href: R.fisica, an: 'cta_fisica'),
      ],
    );
    final scheda = Container(
      padding: const EdgeInsets.symmetric(horizontal: 25.6, vertical: 12.8),
      decoration: const BoxDecoration(
        color: Token.paperLight,
        border: Border(top: BorderSide(color: Token.verdigris, width: 2)),
        boxShadow: [BoxShadow(color: Color(0x143C1846), offset: Offset(0, 16), blurRadius: 30)],
      ),
      child: Row(
        children: [
          Container(
            width: immagine,
            decoration: const BoxDecoration(
              border: Border.fromBorderSide(BorderSide(color: Token.brassPale, width: 2)),
            ),
            child: ImmagineCarta('maj-09', alt: t.home_fisico_carta_alt),
          ),
          const SizedBox(width: 22.4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(bottom: 6.4),
                  child: Text(t.home_fisico_scheda_titolo, style: Stile.serif(20)),
                ),
                Paragrafo(t.home_fisico_scheda_testo, style: Stile.sans(14.08, colore: Token.inkSoft, altezza: 1.6)),
              ],
            ),
          ),
        ],
      ),
    );
    return ColoredBox(
      color: Colori.fisico,
      child: Fascia(
        child: telefono
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [testo, const SizedBox(height: 16.8), scheda],
              )
            : Row(
                children: [
                  Expanded(child: testo),
                  const SizedBox(width: 16.8),
                  Expanded(child: scheda),
                ],
              ),
      ),
    );
  }
}

/* ---- il metodo -------------------------------------------------------------------------------------------------- */

class _Metodo extends StatelessWidget {
  const _Metodo();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final colonne = w.telefono ? 1 : (w.medio ? 2 : 4);
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Eyebrow(t.home_metodo_eyebrow),
          TitoloSezione(t.home_metodo_titolo),
          const SizedBox(height: 13.6),
          Griglia(
            colonne: colonne,
            spazioColonne: 22.4,
            spazioRighe: 22.4,
            allunga: false,
            children: [
              for (final m in t.homeMetodo)
                Container(
                  padding: const EdgeInsets.only(top: 8),
                  decoration: const BoxDecoration(
                    border: Border(top: BorderSide(color: Token.brass)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Text(m.titolo, style: Stile.serif(18.4)),
                      ),
                      Paragrafo(m.testo, style: Stile.sans(14.08, colore: Token.inkSoft, altezza: 1.6)),
                    ],
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

/* ---- dal gratuito alla lettura completa ------------------------------------------------------------------------- */

class _Percorso extends StatelessWidget {
  const _Percorso({required this.nIscrizione});

  final int nIscrizione;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final colonne = w.telefono ? 1 : 4;
    return ColoredBox(
      color: Token.plum,
      child: Fascia(
        child: DefaultTextStyle.merge(
          style: const TextStyle(color: Color(0xFFFFF8ED)),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Eyebrow(t.home_funnel_eyebrow, colore: Colori.eyebrowScuro),
              TitoloSezione(t.home_funnel_titolo, colore: const Color(0xFFFFF8ED)),
              IntroSezione(t.home_funnel_intro(nIscrizione), colore: const Color(0xFFD7C7DB)),
              const SizedBox(height: 13.6),
              Griglia(
                colonne: colonne,
                spazioColonne: 1,
                spazioRighe: 1,
                children: [
                  for (final p in t.homeFunnelPassi)
                    Container(
                      color: const Color(0xCC201026),
                      padding: EdgeInsets.symmetric(horizontal: w.telefono ? 16 : 20.8, vertical: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.only(bottom: 11.2),
                            child: Text(
                              p.etichetta.toUpperCase(),
                              style: Stile.sans(11.2, em: .09, colore: Token.brassPale, altezza: 1.6),
                            ),
                          ),
                          Paragrafo(p.testo, style: Stile.serif(16.8, altezza: 1.35, colore: const Color(0xFFEEE1E9))),
                        ],
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/* ---- la condivisione ----------------------------------------------------------------------------------------------- */

class _Condividi extends StatelessWidget {
  const _Condividi({required this.nInvito});

  final int nInvito;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final telefono = w.telefono;
    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(t.home_cond_eyebrow),
        TitoloSezione(t.home_cond_titolo, px: w.clampVw(25.6, 3, 38.4)),
        Padding(
          padding: const EdgeInsets.only(top: 9.6),
          child: Paragrafo(t.home_cond_testo(nInvito), style: Stile.sans(16, colore: Token.inkSoft, altezza: 1.6)),
        ),
      ],
    );
    final bottone = Bottone(t.home_cond_cta, href: '${R.profilo}#invito', variante: Variante.quieto);
    return Fascia(
      compatta: true,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: w.clampVw(24, 4, 40), vertical: w.clampVw(12, 2, 20)),
        decoration: BoxDecoration(
          color: Token.paperLight,
          border: Border.all(color: Token.line),
        ),
        child: telefono
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [testo, const SizedBox(height: 11.2), bottone],
              )
            : Row(
                children: [
                  Expanded(flex: 12, child: testo),
                  const SizedBox(width: 11.2),
                  Expanded(
                    flex: 8,
                    child: Align(alignment: AlignmentDirectional.centerStart, child: bottone),
                  ),
                ],
              ),
      ),
    );
  }
}

/// Il diario quando non ha ancora articoli: tre tessere fisse verso carte, stese e carta del giorno.
class _DiarioRiserva extends StatelessWidget {
  const _DiarioRiserva();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final riserva = t.homeDiarioRiserva;
    final voci = [
      (href: R.carte, img: 'maj-06', v: riserva[0]),
      (href: R.stese, img: 'maj-17', v: riserva[1]),
      (href: R.giorno, img: 'maj-02', v: riserva[2]),
    ];
    return Fascia(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _TestaSezione(
            eyebrow: t.home_diario_eyebrow,
            titolo: t.home_diario_titolo,
            lato: Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Bottone(t.home_diario_cta, href: R.blog, variante: Variante.quieto),
            ),
          ),
          GrigliaArticoli(
            children: [
              for (final (i, v) in voci.indexed)
                TesseraArticolo(
                  indice: i,
                  href: v.href,
                  immagine: ImmagineCartaArticolo(v.img),
                  etichetta: v.v.etichetta,
                  titolo: v.v.titolo,
                ),
            ],
          ),
        ],
      ),
    );
  }
}

/* ---- le domande -------------------------------------------------------------------------------------------------- */

class _Domande extends StatelessWidget {
  const _Domande();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
    final testa = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [Eyebrow(t.home_faq_eyebrow), TitoloSezione(t.home_faq_titolo)],
    );
    final elenco = Container(
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Token.line)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [for (final q in t.homeFaq) _Domanda(domanda: q.d, risposta: q.r)],
      ),
    );
    return Fascia(
      child: w.telefono
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [testa, const SizedBox(height: 8.8), elenco],
            )
          : Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 78, child: testa),
                const SizedBox(width: 64),
                Expanded(flex: 122, child: elenco),
              ],
            ),
    );
  }
}

/// `<details class="faq-item">`: la domanda col triangolo, la risposta che si apre al tocco.
class _Domanda extends StatefulWidget {
  const _Domanda({required this.domanda, required this.risposta});

  final String domanda;
  final String risposta;

  @override
  State<_Domanda> createState() => _DomandaState();
}

class _DomandaState extends State<_Domanda> {
  bool _aperta = false;

  @override
  Widget build(BuildContext context) {
    final telefono = _w(context).telefono;
    final stile = Stile.serif(telefono ? 16 : 17.28);
    return Container(
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Token.line)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Premibile(
            alTocco: () => setState(() => _aperta = !_aperta),
            etichetta: widget.domanda,
            costruisci: (context, premuto) => Container(
              constraints: const BoxConstraints(minHeight: 44),
              padding: const EdgeInsets.only(top: 8.8, bottom: 8.8, right: 32),
              child: Text.rich(
                TextSpan(
                  children: [
                    TextSpan(
                      text: _aperta ? '▾ ' : '▸ ',
                      style: stile.copyWith(fontFamily: 'DM Sans'),
                    ),
                    TextSpan(text: widget.domanda),
                  ],
                ),
                style: stile,
              ),
            ),
          ),
          if (_aperta)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Paragrafo(widget.risposta, style: Stile.sans(14.72, colore: Token.inkSoft, altezza: 1.6)),
            ),
        ],
      ),
    );
  }
}

/* ---- l'ultimo invito ----------------------------------------------------------------------------------------------- */

class _Finale extends StatelessWidget {
  const _Finale();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = _w(context);
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
                  Eyebrow(t.home_finale_eyebrow, colore: Token.mist, allinea: TextAlign.center),
                  Semantics(
                    header: true,
                    child: TestoBilanciato(
                      t.home_finale_titolo,
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
                        t.home_finale_testo,
                        textAlign: TextAlign.center,
                        style: Stile.sans(16, colore: const Color(0xFFDCEBE5), altezza: 1.6),
                      ),
                    ),
                  ),
                  Bottone(
                    t.home_cta_gratis,
                    href: R.leggi,
                    variante: Variante.ottone,
                    an: 'hero_cta_click',
                    anProprieta: const {'dove': 'finale'},
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
