/// Il dialogo del sito (`frontend/v2/componenti/modale.tsx`, `.dialog` di v2.css): sfondo prugna velato e sfocato,
/// carta chiara con il bordo d'ottone in alto, titolo serif, la ✕ in alto a destra (44×44). Il gesto «indietro» e il
/// tocco sullo sfondo chiudono, come Esc e il clic fuori nel sito; il fuoco entra nel dialogo (è una rotta).
library;

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

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final fondo = scura ? Token.plum : Token.paperLight;
    final titoloColore = scura ? Token.brassPale : Token.ink;
    final chiudiColore = scura ? const Color(0xFFFFF7E8) : Token.inkSoft;
    final imbottitura = w.clampVw(20, 4, 32);
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
            16,
            16 + media.padding.top,
            16,
            media.padding.bottom > 16 ? media.padding.bottom : 16,
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
                    SingleChildScrollView(
                      padding: EdgeInsets.all(imbottitura),
                      child: DefaultTextStyle.merge(
                        style: Stile.corpo.copyWith(color: scura ? const Color(0xFFF6ECDD) : Token.ink),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Padding(
                              padding: const EdgeInsets.only(right: 40, bottom: 16),
                              child: Semantics(
                                header: true,
                                child: Text(titolo, style: Stile.serif(24, altezza: 1.25, colore: titoloColore)),
                              ),
                            ),
                            child,
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
