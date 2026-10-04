/// Il tavolo della lettura (`frontend/v2/lettura/tavolo.tsx`, `.tavolo` di `lettura.module.css`): le posizioni della
/// stesa, le carte posate, il punto che apre l'interpretazione di ciascuna.
///
/// La geometria è quella del sito: coordinate 0–1 dalla stesa, larghezza delle carte dalla stesa (×1,2), tavolo 16:12
/// (1:1 fino a 640 px e per le stese «quadrate», al massimo 640 px), e quando il tavolo è più alto che largo la
/// larghezza «stretta» della stesa. Il panno è prugna con un filo d'ottone e un anello; le carte calcolate compaiono
/// con la molla del sito; le carte scelte nel ventaglio volano al loro posto ([VoloCarte]). La geometria non si
/// specchia nelle lingue da destra a sinistra (`direction: ltr`).
///
/// La firma pubblica ([Posata], [Evidenzia], [Tavolo]) la usano anche la lettura delle proprie carte, la lettura
/// condivisa e il dettaglio della storia.
library;

import 'dart:math' as math;

import 'package:flutter/physics.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/carta.dart';
import '../componenti/premibile.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart';
import '../modelli/carta.dart';
import '../tema/tema.dart';
import 'comuni.dart';

/// Una carta sul tavolo (`Posata` del sito).
@immutable
class Posata {
  /// Una carta posata.
  const Posata({
    required this.posizione,
    this.slot,
    required this.calcolata,
    required this.rivelata,
    this.carta,
    this.rovescio,
    this.interpretazione,
    this.dignita,
    this.doppia = false,
  });

  /// Da una carta di una lettura salvata.
  factory Posata.da(CartaPosata c, {Dignita? dignita}) => Posata(
    posizione: c.posizione,
    calcolata: c.calcolata,
    rivelata: c.rivelata,
    carta: c.carta,
    rovescio: c.rovescio,
    interpretazione: c.interpretazione,
    dignita: dignita,
  );

  /// La posizione nella stesa.
  final int posizione;

  /// Il posto del ventaglio da cui viene (la carta vola da lì al suo posto).
  final int? slot;

  /// Una posizione calcolata.
  final bool calcolata;

  /// Girata.
  final bool rivelata;

  /// La carta (quando si conosce).
  final Carta? carta;

  /// Rovesciata.
  final bool? rovescio;

  /// L'interpretazione della posizione.
  final String? interpretazione;

  /// Le dignità elementali.
  final Dignita? dignita;

  /// Vale in due modi in questa posizione.
  final bool doppia;

  /// Una copia con qualche campo cambiato.
  Posata copia({
    int? slot,
    bool? rivelata,
    Carta? carta,
    bool? rovescio,
    String? interpretazione,
    Dignita? dignita,
    bool? doppia,
    bool? calcolata,
  }) => Posata(
    posizione: posizione,
    slot: slot ?? this.slot,
    calcolata: calcolata ?? this.calcolata,
    rivelata: rivelata ?? this.rivelata,
    carta: carta ?? this.carta,
    rovescio: rovescio ?? this.rovescio,
    interpretazione: interpretazione ?? this.interpretazione,
    dignita: dignita ?? this.dignita,
    doppia: doppia ?? this.doppia,
  );
}

/// Quale fase evidenzia il tavolo.
enum Evidenzia {
  /// Le carte si scelgono.
  scelta,

  /// Le carte si girano.
  rivelazione,
}

/// Il colore di chi parla una posizione nelle letture di due persone (`COLORE_SOGGETTO` della v2): leggibili sul
/// panno prugna, mai da soli (c'è la legenda, e il nome della posizione lo dice già).
const Map<String, Color> coloreSoggetto = {
  'tu': Color(0xFFD6B66D),
  'partner': Color(0xFF9FD8D2),
  'coppia': Color(0xFFF0C8A8),
  'strada-a': Color(0xFFE8A0B4),
  'strada-b': Color(0xFFB7C9F2),
};

/// `SCALA_CARTE`: le carte sono il 20% più grandi rispetto al tavolo, coi centri dove stavano.
const double scalaCarte = 1.2;

/// La larghezza di una carta come frazione del tavolo (`larghezzaBase()` del sito).
double larghezzaBase(Stesa s) => s.larghezza ?? .1;

/// Il tavolo.
class Tavolo extends ConsumerWidget {
  /// Il tavolo della [stesa] con le carte [posate].
  const Tavolo({
    super.key,
    required this.stesa,
    required this.posate,
    this.prossima,
    this.alRivela,
    this.rivelazioneInCorso = false,
    this.evidenzia,
    this.nomePartner,
    this.manuale = false,
    this.alSelezionaPosizione,
    this.testoAggiungi,
    this.testoModifica,
  });

  /// La stesa.
  final Stesa stesa;

  /// Le carte posate.
  final List<Posata> posate;

  /// La prossima posizione da girare.
  final int? prossima;

  /// Girare la carta di una posizione.
  final ValueChanged<int>? alRivela;

  /// Una rivelazione in corso (le altre carte aspettano).
  final bool rivelazioneInCorso;

  /// La fase evidenziata.
  final Evidenzia? evidenzia;

  /// Il nome dell'altra persona, nelle letture speciali.
  final String? nomePartner;

  /// Le proprie carte (mazzo fisico): le facce si vedono da subito.
  final bool manuale;

  /// Solo quando si posano le proprie carte: tocca una posizione per dire quale carta c'è.
  final ValueChanged<int>? alSelezionaPosizione;

  /// «Aggiungi la carta» sulle posizioni vuote.
  final String? testoAggiungi;

  /// «Cambia la carta» sulle posizioni piene.
  final String? testoModifica;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final String lingua = LinguaNomi.di(context) ?? ref.watch(linguaProvider);
    final schermo = MediaQuery.sizeOf(context).width;
    final volo = AmbitoVolo.di(context);
    return LayoutBuilder(
      builder: (context, vincoli) {
        final quadrata = stesa.forma == 'quadrata';
        final w = quadrata ? math.min(vincoli.maxWidth, 640.0) : vincoli.maxWidth;
        // `.tavolo { aspect-ratio: 16 / 12 }`, 1:1 fino a 640 px; `.tavoloQuadrato` sempre 1:1.
        final h = quadrata || schermo <= 640 ? w : w * 12 / 16;
        final stretto = w > 0 && h / w > .9;
        final base = larghezzaBase(stesa);
        final lc = math.max(
          30.0,
          w * (stretto && !quadrata ? (stesa.larghezzaStretto ?? base * 1.15) : base) * scalaCarte,
        );
        final hc = lc * 16 / 9;
        final perPosizione = {for (final p in posate) p.posizione: p};
        // Le carte di traverso sopra le altre (`z-index: 3`).
        final ordinate = [
          ...stesa.posizioni.where((p) => p.rotazione == 0),
          ...stesa.posizioni.where((p) => p.rotazione != 0),
        ];

        final figli = <Widget>[
          Positioned.fill(
            child: _Tappeto(tondo: quadrata, w: w, h: h),
          ),
        ];
        final punti = <Widget>[];
        for (final pos in ordinate) {
          final posata = perPosizione[pos.n];
          final nome = nomePosizione(pos, lingua);
          final attesa = prossima == pos.n;
          final scoperta = posata != null && (posata.rivelata || manuale);
          final soggetto = pos.soggetto == null ? null : coloreSoggetto[pos.soggetto];
          final cx = pos.x * w;
          final cy = pos.y * h;
          final angolo = pos.rotazione * math.pi / 180;

          Widget carta;
          if (posata == null) {
            carta = _Segnaposto(
              numero: pos.n,
              nome: nome,
              soggetto: soggetto,
              attivo: attesa && evidenzia == Evidenzia.scelta,
              testoAggiungi: alSelezionaPosizione == null ? null : testoAggiungi,
              alTocco: alSelezionaPosizione == null ? null : () => alSelezionaPosizione!(pos.n),
            );
          } else {
            final brilla = attesa && evidenzia == Evidenzia.rivelazione && !rivelazioneInCorso;
            Widget c = CartaV2(
              carta: posata.carta,
              rivelata: scoperta,
              rovescio: posata.rovescio ?? false,
              larghezza: lc,
              nome: posata.carta == null ? '' : nomeCarta(posata.carta!, lingua),
              brilla: brilla,
              alTocco: brilla && alRivela != null ? () => alRivela!(pos.n) : null,
              etichetta: scoperta ? null : '${pos.n}. $nome',
            );
            if (soggetto != null) c = CustomPaint(foregroundPainter: _Contorno(soggetto), child: c);
            if (alSelezionaPosizione != null) {
              c = Stack(
                clipBehavior: Clip.none,
                children: [
                  c,
                  Positioned(
                    left: 0,
                    right: 0,
                    bottom: 6,
                    child: Center(
                      child: _Modifica(testo: testoModifica ?? '', alTocco: () => alSelezionaPosizione!(pos.n)),
                    ),
                  ),
                ],
              );
            }
            if (posata.calcolata) c = _Comparsa(child: c);
            final nascosta = volo?.inVolo(pos.n) ?? false;
            carta = Opacity(opacity: nascosta ? 0 : 1, child: c);
          }
          carta = KeyedSubtree(
            key: volo?.chiavePosto(pos.n),
            child: SizedBox(width: lc, height: hc, child: carta),
          );

          figli.add(
            Positioned(
              left: cx - lc / 2,
              top: cy - hc / 2,
              width: lc,
              height: hc,
              child: Transform.rotate(angle: angolo, child: carta),
            ),
          );
          // `.etichettaPosizione`: il nome sotto la carta (non per quelle di traverso; nascosto fino a 640 px).
          if (pos.rotazione == 0 && schermo > 640) {
            figli.add(
              Positioned(
                left: cx - 100,
                width: 200,
                top: cy + hc / 2 + 4,
                child: IgnorePointer(
                  child: Text(
                    nome,
                    textAlign: TextAlign.center,
                    maxLines: 1,
                    softWrap: false,
                    overflow: TextOverflow.visible,
                    style: Stile.sans(10.56, colore: const Color(0xFFD9CADE), em: .04, altezza: 1.6),
                  ),
                ),
              ),
            );
          }
          // `.pallinoAncora` (e `.pallinoTraverso` per le carte di traverso): il punto sopra la carta scoperta.
          if (posata != null && scoperta && posata.carta != null) {
            final d = hc / 2 + (pos.rotazione == 0 ? 6 : 46);
            final punto = Offset(cx + d * math.sin(angolo), cy - d * math.cos(angolo));
            punti.add(
              Positioned(
                left: punto.dx - 22,
                top: punto.dy - 22,
                width: 44,
                height: 44,
                child: _Punto(posata: posata, titolo: '${pos.n}. $nome', lingua: lingua),
              ),
            );
          }
        }

        final tavolo = Directionality(
          textDirection: TextDirection.ltr,
          child: SizedBox(
            width: w,
            height: h,
            child: Stack(clipBehavior: Clip.none, children: [...figli, ...punti]),
          ),
        );
        return Padding(
          padding: const EdgeInsets.only(top: 6.4, bottom: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Center(child: tavolo),
              if (stesa.categoria != 'standard') ...[
                const SizedBox(height: 16 - 4.8),
                _Legenda(stesa: stesa, nomePartner: nomePartner),
              ],
            ],
          ),
        );
      },
    );
  }
}

/// `.tappeto`: il panno prugna (`#28152f`) col filo d'ottone e un anello concentrico; tondo per le stese quadrate.
class _Tappeto extends StatelessWidget {
  const _Tappeto({required this.tondo, required this.w, required this.h});

  final bool tondo;
  final double w;
  final double h;

  @override
  Widget build(BuildContext context) {
    final finestra = MediaQuery.sizeOf(context).height;
    final anello = math.min(w * .78, finestra * .92);
    return ClipRRect(
      borderRadius: BorderRadius.circular(tondo ? w : 0),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: const Color(0xFF28152F),
          border: Border.all(color: const Color(0x59D6B66D)),
          borderRadius: tondo ? BorderRadius.circular(w) : null,
        ),
        child: Center(
          child: Container(
            width: anello,
            height: anello,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: const Color(0x52B28336)),
              boxShadow: const [
                BoxShadow(color: Color(0x0AB28336), spreadRadius: 18),
                BoxShadow(color: Color(0x0A19706F), spreadRadius: 44),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// `.segnaposto`: il posto vuoto col suo numero; acceso (`.segnapostoAttivo`, il respiro d'ottone) quando tocca a
/// lui; premibile quando si posano le proprie carte (`.segnapostoManuale`).
class _Segnaposto extends StatefulWidget {
  const _Segnaposto({
    required this.numero,
    required this.nome,
    required this.soggetto,
    required this.attivo,
    this.testoAggiungi,
    this.alTocco,
  });

  final int numero;
  final String nome;
  final Color? soggetto;
  final bool attivo;
  final String? testoAggiungi;
  final VoidCallback? alTocco;

  @override
  State<_Segnaposto> createState() => _SegnapostoState();
}

class _SegnapostoState extends State<_Segnaposto> with SingleTickerProviderStateMixin {
  late final AnimationController _respiro = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 2400),
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _aggiorna();
  }

  @override
  void didUpdateWidget(_Segnaposto vecchio) {
    super.didUpdateWidget(vecchio);
    _aggiorna();
  }

  void _aggiorna() {
    if (widget.attivo && !MediaQuery.disableAnimationsOf(context)) {
      if (!_respiro.isAnimating) _respiro.repeat();
    } else {
      _respiro.stop();
      _respiro.value = 0;
    }
  }

  @override
  void dispose() {
    _respiro.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Widget corpo(bool premuto) => AnimatedBuilder(
      animation: _respiro,
      builder: (context, _) {
        final x = _respiro.value;
        final f = Curves.easeInOut.transform(x <= .5 ? x * 2 : (1 - x) * 2);
        final acceso = widget.attivo || premuto;
        return Container(
          decoration: BoxDecoration(
            color: widget.attivo
                ? const Color(0x29B28336)
                : (premuto ? const Color(0x1FD6B66D) : const Color(0x8C3C1846)),
            border: Border.all(color: widget.soggetto ?? (acceso ? Token.brassPale : const Color(0x4DD6B66D))),
            boxShadow: widget.attivo && f > 0
                ? [BoxShadow(color: Color.fromRGBO(214, 182, 109, .35 * f), spreadRadius: 4 * f)]
                : null,
          ),
          alignment: Alignment.center,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${widget.numero}',
                style: Stile.serif(14.4, colore: widget.attivo ? const Color(0xFFFFF7E8) : Token.brassPale),
              ),
              if (widget.testoAggiungi != null) ...[
                const SizedBox(height: 4),
                Text(
                  widget.testoAggiungi!.toUpperCase(),
                  textAlign: TextAlign.center,
                  style: Stile.sans(10.56, peso: FontWeight.w700, em: .06, colore: Token.brassPale, altezza: 1.2),
                ),
              ],
            ],
          ),
        );
      },
    );
    if (widget.alTocco == null) {
      return Semantics(label: '${widget.numero}. ${widget.nome}', child: corpo(false));
    }
    return Premibile(
      alTocco: widget.alTocco,
      etichetta: '${widget.numero}. ${widget.nome} — ${widget.testoAggiungi ?? ''}',
      costruisci: (context, premuto) =>
          ConstrainedBox(constraints: const BoxConstraints(minHeight: 48), child: corpo(premuto)),
    );
  }
}

/// `.cartaSoggetto`: il contorno del colore di chi parla la posizione (`outline: 2px; outline-offset: 2px`).
class _Contorno extends CustomPainter {
  _Contorno(this.colore);

  final Color colore;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(
      (Offset.zero & size).inflate(3),
      Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2
        ..color = colore,
    );
  }

  @override
  bool shouldRepaint(_Contorno vecchio) => vecchio.colore != colore;
}

/// `.modificaManuale`: «Cambia la carta» in basso sulla carta posata a mano.
class _Modifica extends StatelessWidget {
  const _Modifica({required this.testo, required this.alTocco});

  final String testo;
  final VoidCallback alTocco;

  @override
  Widget build(BuildContext context) => Premibile(
    alTocco: alTocco,
    raggioFuoco: 18,
    costruisci: (context, premuto) => Container(
      constraints: const BoxConstraints(minHeight: 36),
      padding: const EdgeInsets.symmetric(horizontal: 11.2),
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: premuto ? const Color(0xF2201026) : const Color(0xD1201026),
        border: Border.all(color: const Color(0x99D6B66D)),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(testo, style: Stile.sans(11.52, colore: const Color(0xFFFFF7E8), altezza: 1.2)),
    ),
  );
}

/// La comparsa di una carta calcolata: da trasparente, piccola e storta al suo posto, con la molla del sito
/// (`initial={{ opacity: 0, scale: .4, rotate: -20 }}`, `stiffness: 120, damping: 18`).
class _Comparsa extends StatefulWidget {
  const _Comparsa({required this.child});

  final Widget child;

  @override
  State<_Comparsa> createState() => _ComparsaState();
}

class _ComparsaState extends State<_Comparsa> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController.unbounded(vsync: this, value: 0);

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_c.value == 0 && !_c.isAnimating) {
      if (MediaQuery.disableAnimationsOf(context)) {
        _c.value = 1;
      } else {
        _c.animateWith(SpringSimulation(mollaTavolo, 0, 1, 0));
      }
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
    builder: (context, figlio) {
      final t = _c.value;
      return Opacity(
        opacity: t.clamp(0, 1),
        child: Transform.rotate(
          angle: -20 * (1 - t) * math.pi / 180,
          child: Transform.scale(scale: .4 + .6 * t, child: figlio),
        ),
      );
    },
    child: widget.child,
  );
}

/// `.pallino`: il punto d'ottone sopra la carta scoperta (verderame e pulsante finché l'interpretazione non c'è);
/// piccolo all'occhio, 44 px al tocco. Al tocco apre il fumetto con la posizione, la carta e l'interpretazione.
class _Punto extends StatefulWidget {
  const _Punto({required this.posata, required this.titolo, required this.lingua});

  final Posata posata;
  final String titolo;
  final String lingua;

  @override
  State<_Punto> createState() => _PuntoState();
}

class _PuntoState extends State<_Punto> with TickerProviderStateMixin {
  final OverlayPortalController _fumetto = OverlayPortalController();
  final LayerLink _ancora = LayerLink();
  late final AnimationController _pulso = AnimationController(vsync: this, duration: const Duration(seconds: 2));
  late final AnimationController _comparsa = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 180),
  );

  bool get _attesa => (widget.posata.interpretazione ?? '').isEmpty;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _aggiorna();
  }

  @override
  void didUpdateWidget(_Punto vecchio) {
    super.didUpdateWidget(vecchio);
    _aggiorna();
  }

  void _aggiorna() {
    if (_attesa && !MediaQuery.disableAnimationsOf(context)) {
      if (!_pulso.isAnimating) _pulso.repeat();
    } else {
      _pulso.stop();
      _pulso.value = 0;
    }
  }

  @override
  void dispose() {
    _pulso.dispose();
    _comparsa.dispose();
    super.dispose();
  }

  void _apri() {
    _fumetto.show();
    _comparsa.forward(from: MediaQuery.disableAnimationsOf(context) ? 1 : 0);
    setState(() {});
  }

  void _chiudi() {
    _fumetto.hide();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final carta = widget.posata.carta!;
    final nome = nomeCarta(carta, widget.lingua);
    final dignita = widget.posata.dignita;
    final meta = [
      carta.astrologia,
      if (dignita != null && dignita.giudizio != 'neutra') '${t.lettura_dignita}: ${dignita.giudizio}',
      if (widget.posata.doppia) t.lettura_doppia,
    ].join(' · ');
    final larghezza = math.min(320.0, MediaQuery.sizeOf(context).width * .78);

    return TapRegion(
      groupId: this,
      onTapOutside: _fumetto.isShowing ? (_) => _chiudi() : null,
      child: OverlayPortal(
        controller: _fumetto,
        overlayChildBuilder: (context) => CompositedTransformFollower(
          link: _ancora,
          targetAnchor: Alignment.center,
          followerAnchor: Alignment.bottomCenter,
          offset: const Offset(0, -26),
          child: Align(
            alignment: Alignment.bottomCenter,
            child: TapRegion(
              groupId: this,
              child: AnimatedBuilder(
                animation: _comparsa,
                builder: (context, figlio) => Opacity(
                  opacity: _comparsa.value,
                  child: Transform.translate(offset: Offset(0, 6 * (1 - _comparsa.value)), child: figlio),
                ),
                child: Semantics(
                  container: true,
                  liveRegion: true,
                  child: Container(
                    width: larghezza,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14.4),
                    decoration: const BoxDecoration(
                      color: Token.paperLight,
                      border: Border(top: BorderSide(color: Token.brass, width: 3)),
                      boxShadow: [BoxShadow(color: Color(0x59201026), offset: Offset(0, 18), blurRadius: 36)],
                    ),
                    child: DefaultTextStyle(
                      style: Stile.corpo,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.titolo.toUpperCase(),
                            style: Stile.sans(10.88, peso: FontWeight.w700, em: .1, colore: Token.verdigris),
                          ),
                          Padding(
                            padding: const EdgeInsets.only(top: 1.6),
                            child: Text(
                              '$nome · ${widget.posata.rovescio == true ? t.lettura_rovesciata : t.lettura_dritta}',
                              style: Stile.serif(16.8, colore: Token.plum),
                            ),
                          ),
                          if (meta.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 2.4),
                              child: Text(meta, style: Stile.sans(12.16, colore: Token.inkSoft)),
                            ),
                          if (!_attesa)
                            Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Text(
                                widget.posata.interpretazione!,
                                style: Stile.serif(15.2, altezza: 1.55, colore: Token.ink),
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
        child: CompositedTransformTarget(
          link: _ancora,
          child: Premibile(
            alTocco: () => _fumetto.isShowing ? _chiudi() : _apri(),
            etichetta: '${widget.titolo}: $nome',
            raggioFuoco: 22,
            costruisci: (context, premuto) => Center(
              child: AnimatedBuilder(
                animation: _pulso,
                builder: (context, _) {
                  final x = _pulso.value;
                  final f = Curves.easeInOut.transform(x <= .5 ? x * 2 : (1 - x) * 2);
                  return Transform.scale(
                    scale: 1 + .22 * f,
                    child: Container(
                      width: 16,
                      height: 16,
                      decoration: BoxDecoration(
                        color: _attesa ? Token.verdigris : Token.brass,
                        shape: BoxShape.circle,
                        border: Border.all(color: const Color(0xFFFFF7E8), width: 2),
                        boxShadow: const [BoxShadow(color: Color(0x66201026), offset: Offset(0, 2), blurRadius: 6)],
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// `.legenda`: chi è chi, nelle letture di due persone (solo i soggetti che la stesa usa).
class _Legenda extends StatelessWidget {
  const _Legenda({required this.stesa, this.nomePartner});

  final Stesa stesa;
  final String? nomePartner;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final usati = stesa.posizioni.map((p) => p.soggetto).whereType<String>().toSet();
    final voci = [
      ('tu', t.lettura_soggetti_tu),
      ('partner', (nomePartner?.isNotEmpty ?? false) ? nomePartner! : t.lettura_soggetti_partner),
      ('coppia', t.lettura_soggetti_coppia),
      ('strada-a', t.lettura_soggetti_strada_a),
      ('strada-b', t.lettura_soggetti_strada_b),
    ].where((v) => usati.contains(v.$1));
    return Semantics(
      label: t.lettura_legenda,
      container: true,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Wrap(
          alignment: WrapAlignment.center,
          spacing: 16,
          runSpacing: 6.4,
          children: [
            for (final (chiave, testo) in voci)
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: coloreSoggetto[chiave],
                      shape: BoxShape.circle,
                      boxShadow: const [BoxShadow(color: Color(0x4D000000), spreadRadius: 1)],
                    ),
                  ),
                  const SizedBox(width: 7.2),
                  Text(testo, style: Stile.sans(13.12, colore: const Color(0xFFEADBE9))),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
