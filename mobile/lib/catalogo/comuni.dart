/// I pezzi di v2.css che le pagine del catalogo (carte, stese, mazzi, voto, negozio) hanno in comune:
///
/// - [AperturaCatalogo]: `.subhero.subhero-compact` con quello che le schede ci mettono (un'etichetta sopra
///   l'occhiello, l'introduzione facoltativa, i bottoni sotto);
/// - [DisposizioneMazzo]: `.deck-layout` (`.8fr 1.2fr`, una colonna sul telefono);
/// - [VentaglioMazzo]: `.deck-spread`, tre carte a ventaglio;
/// - [Disponibile]: `.available` (e `.available.planned`);
/// - [GrigliaDifferenze] e [TesseraDifferenza]: `.difference-grid.even` e `.difference`;
/// - [GrigliaCarte] e [TesseraCarta]: `.cards-grid` e `.card-tile`;
/// - [BloccoProsa]: `.prose-block` (i testi lunghi dell'API, serif, al massimo 64ch);
/// - [LayoutLettura]: `.read-layout` con i due `.read-panel`;
/// - [GrigliaStoria]: `.story-grid`;
/// - [VoceMemoria]: `.memory-entry`;
/// - [CondivisioneStatica]: `.static-share` (il ponte verso la lettura delle proprie carte);
/// - [FasciaCondivisione]: `.share-band`.
library;

import 'dart:math' as math;

import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';

import '../componenti/carta.dart';
import '../componenti/griglia.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../rotte/navigazione.dart';
import '../tema/tema.dart';

/// La larghezza della finestra.
double larghezza(BuildContext context) => MediaQuery.sizeOf(context).width;

/// `.subhero.subhero-compact`: l'apertura di una scheda.
class AperturaCatalogo extends StatelessWidget {
  /// Un'apertura.
  const AperturaCatalogo({
    super.key,
    required this.eyebrow,
    required this.titolo,
    this.intro,
    this.sopra,
    this.sotto,
  });

  /// L'occhiello.
  final String eyebrow;

  /// Il titolo (`h1.display`, con la misura di `.subhero-compact`).
  final String titolo;

  /// L'introduzione (`.section-intro`), se c'è.
  final String? intro;

  /// Ciò che sta prima dell'occhiello (il segno «disponibile» di un mazzo).
  final Widget? sopra;

  /// Ciò che sta dopo l'introduzione (i bottoni di una stesa).
  final Widget? sotto;

  @override
  Widget build(BuildContext context) {
    final w = larghezza(context);
    final telefono = w.telefono;
    final alto = telefono ? 16.0 : w.clampVw(16, 2.1, 25.6);
    final basso = telefono ? 16.0 : 14.4;
    final display = Stile.serif(w.stretto ? 36.8 : w.clampVw(32, 4.2, 64), altezza: 1.05, em: -.055);
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: Token.larghezzaBanda),
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.fromLTRB(w.gutter, alto, w.gutter, basso),
          decoration: const BoxDecoration(
            border: Border(bottom: BorderSide(color: Token.line)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ?sopra,
              Eyebrow(eyebrow),
              Semantics(header: true, child: TestoBilanciato(titolo, stile: display, maxCh: 18)),
              if (intro != null) IntroSezione(intro!),
              ?sotto,
            ],
          ),
        ),
      ),
    );
  }
}

/// `.deck-layout`: due colonne `.8fr 1.2fr` (gap `clamp(.7rem, 2.1vw, 1.75rem)`), una sola sul telefono;
/// [inAlto] è `align-items: start`.
class DisposizioneMazzo extends StatelessWidget {
  /// La disposizione.
  const DisposizioneMazzo({super.key, required this.sinistra, required this.destra, this.inAlto = false});

  /// La colonna stretta (le carte).
  final Widget sinistra;

  /// La colonna larga (il testo).
  final Widget destra;

  /// `align-items: start` (altrimenti al centro).
  final bool inAlto;

  @override
  Widget build(BuildContext context) {
    final w = larghezza(context);
    final spazio = w.clampVw(11.2, 2.1, 28);
    if (w.telefono) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [sinistra, SizedBox(height: spazio), destra],
      );
    }
    return Row(
      crossAxisAlignment: inAlto ? CrossAxisAlignment.start : CrossAxisAlignment.center,
      children: [
        Expanded(flex: 8, child: sinistra),
        SizedBox(width: spazio),
        Expanded(flex: 12, child: destra),
      ],
    );
  }
}

/// `.deck-spread`: tre carte a ventaglio alte 390 px, la seconda sopra le altre.
class VentaglioMazzo extends StatelessWidget {
  /// Le carte [ids] (tre) del mazzo [mazzo] (`null`: il Thoth).
  const VentaglioMazzo({super.key, required this.ids, this.mazzo});

  /// Le tre carte, da sinistra.
  final List<String> ids;

  /// La cartella del mazzo.
  final String? mazzo;

  @override
  Widget build(BuildContext context) {
    const posizioni = [(-86.0, 5.0, -18.0), (0.0, -15.0, 0.0), (86.0, 7.0, 18.0)];
    Widget carta(int i) {
      final (dx, dy, gradi) = posizioni[i];
      return Transform.translate(
        offset: Offset(dx, dy),
        child: Transform.rotate(
          angle: gradi * math.pi / 180,
          child: Container(
            width: 125,
            decoration: const BoxDecoration(
              border: Border.fromBorderSide(BorderSide(color: Colori.cornice, width: 3)),
              boxShadow: [BoxShadow(color: Color(0x40201026), offset: Offset(0, 16), blurRadius: 26)],
            ),
            child: ImmagineCarta(ids[i], mazzo: mazzo ?? ''),
          ),
        ),
      );
    }

    return ExcludeSemantics(
      child: SizedBox(
        height: 390,
        // La seconda ha `z-index: 2`: si disegna per ultima.
        child: Stack(alignment: Alignment.center, children: [carta(0), carta(2), carta(1)]),
      ),
    );
  }
}

/// `.available`: «disponibile» in verderame; [pianificato] è `.available.planned` (solo il bordo).
class Disponibile extends StatelessWidget {
  /// Un segno.
  const Disponibile(this.testo, {super.key, this.pianificato = false, this.sotto = 16, this.px = 11.2});

  /// Il testo (in maiuscolo).
  final String testo;

  /// `.planned`.
  final bool pianificato;

  /// `margin-bottom`.
  final double sotto;

  /// La dimensione del testo (`.7rem`; `.66rem` nei mazzi futuri).
  final double px;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: sotto),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8.8, vertical: 4.48),
        decoration: BoxDecoration(
          color: pianificato ? null : Token.verdigris,
          border: pianificato ? Border.all(color: Token.line) : null,
        ),
        child: Text(
          testo.toUpperCase(),
          style: Stile.sans(
            px,
            peso: FontWeight.w700,
            em: .07,
            colore: pianificato ? Token.inkSoft : const Color(0xFFFFF7E8),
            altezza: 1.6,
          ),
        ),
      ),
    );
  }
}

/// `.difference-grid.even`: le tessere separate da una riga sottile, quattro colonne (`1.1fr 1fr 1fr 1fr`), due fino
/// a 1000 px, una sul telefono.
class GrigliaDifferenze extends StatelessWidget {
  /// Una griglia.
  const GrigliaDifferenze({super.key, required this.children});

  /// Le tessere.
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final w = larghezza(context);
    final colonne = w.telefono ? 1 : (w.medio ? 2 : 4);
    return Griglia.righe(
      colonne: colonne,
      pesi: colonne == 4 ? const [11, 10, 10, 10] : null,
      linea: Token.line,
      children: children,
    );
  }
}

/// `.difference` (dentro `.difference-grid.even`): il segno (o la miniatura), il titolo serif, il testo tenue; con
/// [href] è un collegamento (`a.difference`, più calda alla pressione).
class TesseraDifferenza extends StatelessWidget {
  /// Una tessera.
  const TesseraDifferenza({
    super.key,
    required this.titolo,
    this.simbolo,
    this.testa,
    this.testi = const [],
    this.href,
  });

  /// `h3`.
  final String titolo;

  /// Il segno (`span`: serif 1.7rem d'ottone, centrato sul telefono).
  final String? simbolo;

  /// Ciò che sta al posto del segno (la miniatura della stesa).
  final Widget? testa;

  /// I paragrafi sotto il titolo (`p`); un widget va così com'è.
  final List<Object> testi;

  /// Dove porta.
  final String? href;

  @override
  Widget build(BuildContext context) {
    final telefono = larghezza(context).telefono;
    Widget corpo(bool premuto) => Container(
      color: premuto ? const Color(0xFFFFF3DC) : Colori.differenza,
      padding: EdgeInsets.symmetric(horizontal: telefono ? 17.6 : 22.4, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          ?testa,
          if (simbolo != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8.8),
              child: ExcludeSemantics(
                child: Text(
                  simbolo!,
                  textAlign: telefono ? TextAlign.center : TextAlign.start,
                  style: Stile.serif(27.2, colore: Token.brass),
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Semantics(
              header: true,
              child: TestoBilanciato(titolo, stile: Stile.serif(telefono ? 18.4 : 20.8, colore: Token.ink)),
            ),
          ),
          for (final p in testi)
            p is Widget
                ? p
                : Paragrafo('$p', style: Stile.sans(13.92, colore: Token.inkSoft, altezza: 1.6)),
        ],
      ),
    );
    if (href == null) return corpo(false);
    return Premibile(
      alTocco: () => vai(context, href!),
      collegamento: true,
      costruisci: (context, premuto) => corpo(premuto),
    );
  }
}

/// `.cards-grid`: sei colonne, quattro fino a 1000 px, tre sul telefono, due fino a 430 px; `gap: .5rem 1rem`.
class GrigliaCarte extends StatelessWidget {
  /// Una griglia.
  const GrigliaCarte({super.key, required this.children});

  /// Le tessere.
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final w = larghezza(context);
    final colonne = w.stretto ? 2 : (w.telefono ? 3 : (w.medio ? 4 : 6));
    return Griglia(colonne: colonne, spazioColonne: 16, spazioRighe: 8, allunga: false, children: children);
  }
}

/// `.card-tile`: l'immagine con l'ombra (e il bordo d'ottone alla pressione), il nome serif e la riga piccola.
class TesseraCarta extends StatelessWidget {
  /// Una tessera.
  const TesseraCarta({
    super.key,
    required this.id,
    required this.href,
    this.nome,
    this.sotto,
    this.alt = '',
    this.mazzo,
  });

  /// La carta.
  final String id;

  /// Dove porta.
  final String href;

  /// Il nome (`span`).
  final String? nome;

  /// La riga piccola (`small`).
  final String? sotto;

  /// Il testo alternativo dell'immagine.
  final String alt;

  /// La cartella del mazzo (`''`: il Thoth).
  final String? mazzo;

  @override
  Widget build(BuildContext context) {
    return Premibile(
      alTocco: () => vai(context, href),
      collegamento: true,
      etichetta: nome ?? (alt.isEmpty ? null : alt),
      costruisci: (context, premuto) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            curve: Curves.ease,
            transform: Matrix4.translationValues(0, premuto ? -5 : 0, 0),
            decoration: BoxDecoration(
              border: Border.all(color: premuto ? Token.brass : const Color(0x00000000), width: 2),
              boxShadow: const [BoxShadow(color: Color(0x21201026), offset: Offset(0, 10), blurRadius: 20)],
            ),
            child: ImmagineCarta(id, alt: alt, mazzo: mazzo),
          ),
          if (nome != null)
            Padding(
              padding: const EdgeInsets.only(top: 9.6),
              child: Text(nome!, style: Stile.serif(15.2, colore: Token.ink)),
            ),
          if (sotto != null) Text(sotto!, style: Stile.sans(12.16, colore: Token.inkSoft, altezza: 1.6)),
        ],
      ),
    );
  }
}

/// Un elemento di [BloccoProsa].
sealed class PezzoProsa {
  const PezzoProsa();
}

/// `h3`: serif 1.25rem prugna.
class TitoloProsa extends PezzoProsa {
  /// Un titolo.
  const TitoloProsa(this.testo);

  /// Il testo.
  final String testo;
}

/// `p`: serif 1rem/1.75; [piccolo] è `p.small` (sans .86rem), [tenue] `.muted`, [corsivo] in corsivo.
class ParagrafoProsa extends PezzoProsa {
  /// Un paragrafo.
  const ParagrafoProsa(this.testo, {this.piccolo = false, this.tenue = false, this.inGrassetto, this.corsivo = false});

  /// Il testo.
  final String testo;

  /// `p.small`.
  final bool piccolo;

  /// `.muted`.
  final bool tenue;

  /// Una parte iniziale in grassetto (`<b>Love.</b> …`).
  final String? inGrassetto;

  /// In corsivo.
  final bool corsivo;
}

/// `ul`: serif 1rem/1.7 con i pallini, rientro 1.2rem; ogni voce con l'inizio in grassetto facoltativo.
class ElencoProsa extends PezzoProsa {
  /// Un elenco.
  const ElencoProsa(this.voci);

  /// Le voci: (inizio in grassetto o `null`, testo).
  final List<(String?, String)> voci;
}

/// `.prose-block`: i testi lunghi dell'API, al massimo 64ch.
class BloccoProsa extends StatelessWidget {
  /// Un blocco.
  const BloccoProsa(this.pezzi, {super.key});

  /// I pezzi, nell'ordine.
  final List<PezzoProsa> pezzi;

  @override
  Widget build(BuildContext context) {
    final serif = Stile.serif(16, altezza: 1.75, colore: Token.ink);
    final scala = MediaQuery.textScalerOf(context);
    final figli = <Widget>[];
    for (final (i, p) in pezzi.indexed) {
      switch (p) {
        case TitoloProsa(:final testo):
          figli.add(
            Padding(
              padding: EdgeInsets.only(top: i == 0 ? 0 : 28.8 - 14.4, bottom: 8),
              child: Semantics(
                header: true,
                child: TestoBilanciato(testo, stile: Stile.serif(20, colore: Token.plum)),
              ),
            ),
          );
        case ParagrafoProsa(:final testo, :final piccolo, :final tenue, :final inGrassetto, :final corsivo):
          final base = piccolo ? Stile.sans(13.76, altezza: 1.6, colore: Token.ink) : serif;
          final stile = base.copyWith(
            color: tenue ? Token.inkSoft : null,
            fontStyle: corsivo ? FontStyle.italic : null,
          );
          figli.add(
            Padding(
              padding: const EdgeInsets.only(bottom: 14.4),
              child: inGrassetto == null
                  ? Paragrafo(testo, style: stile)
                  : Text.rich(
                      TextSpan(
                        children: [
                          TextSpan(text: inGrassetto, style: const TextStyle(fontWeight: FontWeight.w700)),
                          TextSpan(text: ' $testo'),
                        ],
                      ),
                      style: stile,
                    ),
            ),
          );
        case ElencoProsa(:final voci):
          final elenco = Stile.serif(16, altezza: 1.7, colore: Token.ink);
          figli.add(
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final (b, testo) in voci)
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(width: 19.2, child: Text('•', textAlign: TextAlign.center, style: elenco)),
                        Expanded(
                          child: Text.rich(
                            TextSpan(
                              children: [
                                if (b != null) TextSpan(text: '$b ', style: const TextStyle(fontWeight: FontWeight.w700)),
                                TextSpan(text: testo),
                              ],
                            ),
                            style: elenco,
                          ),
                        ),
                      ],
                    ),
                ],
              ),
            ),
          );
      }
    }
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: larghezzaCh(serif, scala) * 64),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: figli),
    );
  }
}

/// `.read-layout`: due pannelli (`.9fr 1.1fr`) separati da una riga, uno sotto l'altro sul telefono.
class LayoutLettura extends StatelessWidget {
  /// Il pannello scuro (sinistra) e quello chiaro (destra).
  const LayoutLettura({super.key, required this.scuro, required this.chiaro});

  /// `.read-panel.dark`.
  final Widget scuro;

  /// `.read-panel`.
  final Widget chiaro;

  @override
  Widget build(BuildContext context) {
    final w = larghezza(context);
    Widget pannello(Widget figlio, bool buio) => Container(
      color: buio ? Token.plum : Colori.carta,
      padding: EdgeInsets.symmetric(horizontal: w.clampVw(20, 4, 48), vertical: w.clampVw(12, 2, 24)),
      child: DefaultTextStyle.merge(
        style: TextStyle(color: buio ? const Color(0xFFF6ECDD) : Token.ink),
        child: figlio,
      ),
    );
    return DecoratedBox(
      decoration: BoxDecoration(color: Token.line, border: Border.all(color: Token.line)),
      child: Padding(
        padding: const EdgeInsets.all(1),
        child: w.telefono
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [pannello(scuro, true), const SizedBox(height: 1), pannello(chiaro, false)],
              )
            : RigaUguale(pesi: const [9, 11], spazio: 1, children: [pannello(scuro, true), pannello(chiaro, false)]),
      ),
    );
  }
}

/// `.read-panel h2`: serif 1.6rem, `margin: 0 0 1rem`.
class TitoloPannelloLettura extends StatelessWidget {
  /// Un titolo.
  const TitoloPannelloLettura(this.testo, {super.key});

  /// Il testo.
  final String testo;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 16),
    child: Semantics(header: true, child: TestoBilanciato(testo, stile: Stile.serif(25.6))),
  );
}

/// `.story-grid`: due colonne (`.75fr 1.25fr`, gap `.7rem`) in alto, una sola sul telefono.
class GrigliaStoria extends StatelessWidget {
  /// La griglia.
  const GrigliaStoria({super.key, required this.sinistra, required this.destra});

  /// La colonna stretta.
  final Widget sinistra;

  /// La colonna larga.
  final Widget destra;

  @override
  Widget build(BuildContext context) {
    if (larghezza(context).telefono) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [sinistra, const SizedBox(height: 11.2), destra],
      );
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(flex: 75, child: sinistra),
        const SizedBox(width: 11.2),
        Expanded(flex: 125, child: destra),
      ],
    );
  }
}

/// `.memory-entry`: l'occhiello piccolo verderame, il titolo serif, il testo tenue, la riga sotto.
class VoceMemoria extends StatelessWidget {
  /// Una voce.
  const VoceMemoria({super.key, this.occhiello, required this.titolo, this.figli = const []});

  /// `small`.
  final String? occhiello;

  /// `h3`.
  final String titolo;

  /// Ciò che segue (paragrafi, barre).
  final List<Widget> figli;

  @override
  Widget build(BuildContext context) {
    final telefono = larghezza(context).telefono;
    return Container(
      padding: EdgeInsets.symmetric(vertical: telefono ? 12.8 : 17.6),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Token.line)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (occhiello != null)
            Text(
              occhiello!.toUpperCase(),
              style: Stile.sans(11.52, peso: FontWeight.w700, em: .05, colore: Token.verdigris, altezza: 1.6),
            ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.8),
            child: Semantics(header: true, child: TestoBilanciato(titolo, stile: Stile.serif(17.6, colore: Token.ink))),
          ),
          ...figli,
        ],
      ),
    );
  }
}

/// `.memory-entry p`: tenue, `.88rem`.
TextStyle stileVoceMemoria() => Stile.sans(14.08, colore: Token.inkSoft, altezza: 1.6);

/// `.static-share`: il riquadro prugna con la citazione in corsivo (il ponte verso le proprie carte).
class CondivisioneStatica extends StatelessWidget {
  /// Un riquadro.
  const CondivisioneStatica({
    super.key,
    required this.eyebrow,
    required this.citazione,
    required this.testo,
    required this.azione,
  });

  /// `p.eyebrow`.
  final String eyebrow;

  /// `q`.
  final String citazione;

  /// `p`.
  final String testo;

  /// Il bottone.
  final Widget azione;

  @override
  Widget build(BuildContext context) {
    final w = larghezza(context);
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 760),
      child: Container(
        width: double.infinity,
        color: Token.plum,
        padding: EdgeInsets.symmetric(horizontal: w.clampVw(20, 4, 32), vertical: w.clampVw(10.4, 2, 16)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Eyebrow(eyebrow),
            // `q` mette le virgolette della lingua: quelle tipografiche.
            Text(
              '“$citazione”',
              style: Stile.serif(24.8, altezza: 1.45, stile: FontStyle.italic, colore: const Color(0xFFFFF7E8)),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Paragrafo(testo, style: Stile.sans(16, colore: const Color(0xFFD8C8DB), altezza: 1.6)),
            ),
            Align(alignment: AlignmentDirectional.centerStart, child: azione),
          ],
        ),
      ),
    );
  }
}

/// `.share-band`: il riquadro chiaro bordato, testo e azione (`1.2fr .8fr`), uno sotto l'altro sul telefono.
class FasciaCondivisione extends StatelessWidget {
  /// Una fascia.
  const FasciaCondivisione({super.key, required this.testo, required this.azione});

  /// Il testo (titolo e paragrafo).
  final Widget testo;

  /// L'azione.
  final Widget azione;

  @override
  Widget build(BuildContext context) {
    final w = larghezza(context);
    return Container(
      padding: EdgeInsets.symmetric(horizontal: w.clampVw(24, 4, 40), vertical: w.clampVw(12, 2, 20)),
      decoration: BoxDecoration(
        color: Token.paperLight,
        border: Border.all(color: Token.line),
      ),
      child: w.telefono
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [testo, const SizedBox(height: 11.2), azione],
            )
          : Row(
              children: [
                Expanded(flex: 12, child: testo),
                const SizedBox(width: 11.2),
                Expanded(flex: 8, child: Align(alignment: AlignmentDirectional.centerStart, child: azione)),
              ],
            ),
    );
  }
}

/// Una riga di colonne alte uguali (`display: grid` con `align-items: stretch`) senza le misure intrinseche: ogni
/// colonna si dispone una volta con l'altezza libera, poi tutte di nuovo alte quanto la più alta. Serve dove dentro c'è
/// un `LayoutBuilder` (il tavolo), che `IntrinsicHeight` non sa misurare.
class RigaUguale extends MultiChildRenderObjectWidget {
  /// Una riga con i [pesi] delle colonne (`fr`) e lo [spazio] fra l'una e l'altra.
  const RigaUguale({super.key, required this.pesi, this.spazio = 0, required super.children});

  /// I pesi delle colonne.
  final List<int> pesi;

  /// Lo spazio fra le colonne.
  final double spazio;

  @override
  RenderObject createRenderObject(BuildContext context) => _RenderRigaUguale(pesi, spazio);

  @override
  void updateRenderObject(BuildContext context, RenderObject renderObject) {
    final r = renderObject as _RenderRigaUguale;
    r
      ..pesi = pesi
      ..spazio = spazio
      ..markNeedsLayout();
  }
}

class _DatiRiga extends ContainerBoxParentData<RenderBox> {}

class _RenderRigaUguale extends RenderBox
    with ContainerRenderObjectMixin<RenderBox, _DatiRiga>, RenderBoxContainerDefaultsMixin<RenderBox, _DatiRiga> {
  _RenderRigaUguale(this.pesi, this.spazio);

  List<int> pesi;
  double spazio;

  @override
  void setupParentData(RenderBox figlio) {
    if (figlio.parentData is! _DatiRiga) figlio.parentData = _DatiRiga();
  }

  @override
  void performLayout() {
    final figli = getChildrenAsList();
    final totale = pesi.fold(0, (a, b) => a + b);
    final libera = constraints.maxWidth - spazio * (figli.length - 1);
    final larghezze = [for (var i = 0; i < figli.length; i++) libera * pesi[i % pesi.length] / totale];
    var alta = 0.0;
    for (var i = 0; i < figli.length; i++) {
      figli[i].layout(BoxConstraints.tightFor(width: larghezze[i]), parentUsesSize: true);
      alta = math.max(alta, figli[i].size.height);
    }
    var x = 0.0;
    for (var i = 0; i < figli.length; i++) {
      figli[i].layout(BoxConstraints.tightFor(width: larghezze[i], height: alta), parentUsesSize: true);
      (figli[i].parentData! as _DatiRiga).offset = Offset(x, 0);
      x += larghezze[i] + spazio;
    }
    size = constraints.constrain(Size(constraints.maxWidth, alta));
  }

  @override
  void paint(PaintingContext context, Offset offset) => defaultPaint(context, offset);

  @override
  bool hitTestChildren(BoxHitTestResult result, {required Offset position}) =>
      defaultHitTestChildren(result, position: position);
}
