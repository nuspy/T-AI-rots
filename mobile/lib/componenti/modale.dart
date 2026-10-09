/// Il dialogo del sito (`frontend/v2/componenti/modale.tsx`, `.dialog` di v2.css): sfondo prugna velato e sfocato,
/// carta chiara con il bordo d'ottone in alto, titolo serif, la ✕ in alto a destra (44×44). Il gesto «indietro» e il
/// tocco sullo sfondo chiudono, come Esc e il clic fuori nel sito; il fuoco entra nel dialogo (è una rotta).
library;

import 'dart:async';
import 'dart:math' as math;
import 'dart:ui' show ImageFilter;

import 'package:flutter/widgets.dart';

import '../l10n/testi.dart';
import '../tema/tema.dart';
import 'premibile.dart';

/// Apre un dialogo con [titolo] e il contenuto di [costruisci]; restituisce ciò che il contenuto passa a `pop`.
Future<T?> apriModale<T>(
  BuildContext context, {
  required String titolo,
  required WidgetBuilder costruisci,
  bool scura = false,
  bool larga = false,
  bool chiudibile = true,
  bool scorre = true,
}) {
  return showGeneralDialog<T>(
    context: context,
    barrierDismissible: chiudibile,
    barrierLabel: context.t.comune_chiudi,
    barrierColor: const Color(0x00000000),
    transitionDuration: Token.durataTransizione,
    pageBuilder: (context, _, _) => FinestraModale(
      titolo: titolo,
      scura: scura,
      larga: larga,
      scorre: scorre,
      alChiudi: chiudibile ? () => Navigator.of(context).pop() : null,
      child: Builder(builder: costruisci),
    ),
    transitionBuilder: (context, animazione, _, figlio) => FadeTransition(opacity: animazione, child: figlio),
  );
}

/// La finestra del dialogo con il suo velo: si usa da [apriModale] o direttamente sopra la pagina (il primo avvio).
class FinestraModale extends StatelessWidget {
  /// Una finestra.
  const FinestraModale({
    super.key,
    required this.titolo,
    required this.child,
    this.alChiudi,
    this.scura = false,
    this.larga = false,
    this.scorre = true,
  });

  /// Il titolo (`<h2>`).
  final String titolo;

  /// Il contenuto.
  final Widget child;

  /// La ✕ e il tocco sullo sfondo (assente: il dialogo si chiude solo dai suoi bottoni).
  final VoidCallback? alChiudi;

  /// Il fondo prugna del rito (`.dialog-scuro`).
  final bool scura;

  /// Quasi tutta la larghezza (`.dialog-wide`).
  final bool larga;

  /// Falso: il dialogo non scorre tutto insieme; il titolo resta fermo e il contenuto prende lo spazio che resta (alto
  /// al massimo quanto lo schermo), così un elenco può scorrere nel suo riquadro e il pulsante sotto restare sempre in
  /// vista. Il contenuto mette in un `Flexible` la parte che scorre.
  final bool scorre;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final fondo = scura ? Token.plum : Token.paperLight;
    final titoloColore = scura ? Token.brassPale : Token.ink;
    final chiudiColore = scura ? const Color(0xFFFFF7E8) : Token.inkSoft;
    final imbottitura = w.clampVw(20, 4, 32);
    final titoloWidget = Padding(
      padding: const EdgeInsets.only(right: 40, bottom: 16),
      child: Semantics(
        header: true,
        child: Text(titolo, style: Stile.serif(24, altezza: 1.25, colore: titoloColore)),
      ),
    );
    final stileTesto = Stile.corpo.copyWith(color: scura ? const Color(0xFFF6ECDD) : Token.ink);
    // Le zone sicure: la tacca e i bordi curvi ai lati, la barra dei gesti e la tastiera in basso.
    final sotto = math.max(media.padding.bottom, media.viewInsets.bottom);
    return Stack(
      children: [
        // `.dialog-backdrop { background: rgba(32,16,38,.62); backdrop-filter: blur(3px) }`
        Positioned.fill(
          child: GestureDetector(
            onTap: alChiudi,
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 3, sigmaY: 3),
              child: const ColoredBox(color: Colori.velo),
            ),
          ),
        ),
        Padding(
          padding: EdgeInsets.fromLTRB(
            math.max(16, media.padding.left),
            16 + media.padding.top,
            math.max(16, media.padding.right),
            sotto > 16 ? sotto : 16,
          ),
          child: Center(
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: larga ? 1080 : Token.larghezzaModale),
              child: Container(
                decoration: BoxDecoration(
                  color: fondo,
                  border: Border(
                    top: BorderSide(color: scura ? Token.brassPale : Token.brass, width: Token.bordoModale),
                  ),
                  boxShadow: const [BoxShadow(color: Color(0x59201026), offset: Offset(0, 30), blurRadius: 60)],
                ),
                child: Stack(
                  children: [
                    if (scorre)
                      SingleChildScrollView(
                        padding: EdgeInsets.all(imbottitura),
                        child: DefaultTextStyle.merge(
                          style: stileTesto,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            mainAxisSize: MainAxisSize.min,
                            children: [titoloWidget, child],
                          ),
                        ),
                      )
                    else
                      Padding(
                        padding: EdgeInsets.all(imbottitura),
                        child: DefaultTextStyle.merge(
                          style: stileTesto,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              titoloWidget,
                              Flexible(child: child),
                            ],
                          ),
                        ),
                      ),
                    if (alChiudi != null)
                      Positioned(
                        top: 8,
                        right: 8,
                        child: Premibile(
                          alTocco: alChiudi,
                          etichetta: context.t.comune_chiudi,
                          costruisci: (context, _) => SizedBox(
                            width: 44,
                            height: 44,
                            child: Center(
                              child: Text('✕', style: Stile.sans(17.6, colore: chiudiColore)),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Un elenco da cui scegliere, per i dialoghi che non scorrono (`scorre: false`): sopra le parti ferme ([sopra]: un
/// testo, la ricerca), poi le [voci] in un riquadro bordato che scorre da sé, e sotto i [comandi], sempre in vista. Al
/// primo disegno la voce con la chiave [selezionata] si porta in vista dentro il riquadro.
class RiquadroElenco extends StatefulWidget {
  /// Un elenco nel suo riquadro.
  const RiquadroElenco({
    super.key,
    required this.voci,
    required this.comandi,
    this.sopra = const [],
    this.selezionata,
    this.etichetta,
  });

  /// Le voci (una sotto l'altra).
  final List<Widget> voci;

  /// Sotto il riquadro: il pulsante (o l'attesa, o l'errore).
  final Widget comandi;

  /// Sopra il riquadro.
  final List<Widget> sopra;

  /// La chiave della voce scelta, da portare in vista.
  final GlobalKey? selezionata;

  /// Il nome dell'elenco per i lettori di schermo.
  final String? etichetta;

  @override
  State<RiquadroElenco> createState() => _RiquadroElencoState();
}

class _RiquadroElencoState extends State<RiquadroElenco> {
  final ScrollController _scorri = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ctx = widget.selezionata?.currentContext;
      if (!mounted || ctx == null) return;
      unawaited(Scrollable.ensureVisible(ctx, alignment: .3));
    });
  }

  @override
  void dispose() {
    _scorri.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    mainAxisSize: MainAxisSize.min,
    children: [
      ...widget.sopra,
      Flexible(
        child: Semantics(
          container: true,
          label: widget.etichetta,
          child: DecoratedBox(
            decoration: BoxDecoration(border: Border.all(color: Token.line)),
            child: RawScrollbar(
              controller: _scorri,
              thumbVisibility: true,
              thickness: 4,
              radius: const Radius.circular(2),
              thumbColor: Token.brass,
              child: ListView(controller: _scorri, shrinkWrap: true, padding: EdgeInsets.zero, children: widget.voci),
            ),
          ),
        ),
      ),
      const SizedBox(height: 16),
      widget.comandi,
    ],
  );
}
