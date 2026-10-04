/// I nove articoli del diario che chiudono molte pagine (`DiarioNove` e `Tessera` di `frontend/v2/pagine/blog.tsx`):
/// i 3 più recenti col collegamento all'elenco, poi 6 scelti fra quelli attinenti alla pagina, ciascuno col
/// collegamento alla sua sezione. Le tessere sono `.article`: l'immagine a tutta tessera, una sfumatura scura dal
/// basso (prugna, verderame, prugna, a turno) e il testo in fondo.
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../modelli/pubblici.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'bottoni.dart';
import 'carta.dart';
import 'griglia.dart';
import 'pagina.dart';
import 'premibile.dart';
import 'testi.dart';

/// L'immagine di una carta del sito come immagine di una tessera.
class ImmagineCartaArticolo extends ConsumerWidget {
  /// La carta [id].
  const ImmagineCartaArticolo(this.id, {super.key});

  /// L'identificativo della carta.
  final String id;

  @override
  Widget build(BuildContext context, WidgetRef ref) => Image(
    image: ref.watch(immagineCartaProvider)(id),
    fit: BoxFit.cover,
    excludeFromSemantics: true,
    errorBuilder: (context, e, s) => const SizedBox.shrink(),
  );
}

/// Le immagini degli articoli: percorsi relativi dell'API (`urlMedia` del sito). I test le sostituiscono.
final immagineMediaProvider = Provider<ImageProvider Function(String percorso)>(
  (ref) =>
      (percorso) => NetworkImage('${Config.apiUrl}$percorso'),
);

/// `.content-grid`: una colonna sul telefono, `1.2fr .8fr .8fr` più largo.
class GrigliaArticoli extends StatelessWidget {
  /// Le tessere.
  const GrigliaArticoli({super.key, required this.children});

  /// Le tessere.
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    return Griglia(
      colonne: telefono ? 1 : 3,
      pesi: telefono ? null : const [12, 8, 8],
      spazioColonne: 17.6,
      spazioRighe: 8,
      // Le tessere hanno già la stessa altezza minima; i collegamenti alle sezioni non sanno dare l'altezza intrinseca.
      allunga: false,
      children: children,
    );
  }
}

/// `.article`: una tessera del diario.
class TesseraArticolo extends StatelessWidget {
  /// Una tessera.
  const TesseraArticolo({
    super.key,
    required this.indice,
    required this.href,
    required this.immagine,
    required this.etichetta,
    required this.titolo,
    this.righe = const [],
  });

  /// La posizione nella griglia: sceglie il colore della sfumatura (`:nth-child(3n+…)`).
  final int indice;

  /// Dove porta.
  final String href;

  /// L'immagine di fondo.
  final Widget immagine;

  /// `<small>`: la sezione o l'etichetta.
  final String etichetta;

  /// `<h3>`.
  final String titolo;

  /// I paragrafi sotto il titolo (il tempo di lettura).
  final List<String> righe;

  static const List<Color> _sfumature = [Color(0xF0201026), Color(0xF219706F), Color(0xF23C1846)];

  @override
  Widget build(BuildContext context) {
    final colore = _sfumature[indice % 3];
    return Premibile(
      alTocco: () => vai(context, href),
      collegamento: true,
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 290),
        child: Stack(
          children: [
            const Positioned.fill(child: ColoredBox(color: Token.plumDeep)),
            Positioned.fill(child: immagine),
            Positioned.fill(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    stops: const [.2, 1],
                    colors: [colore.withValues(alpha: 0), colore],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(22.4),
              child: ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 290 - 44.8),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      etichetta.toUpperCase(),
                      style: Stile.sans(11.2, peso: FontWeight.w700, em: .08, colore: Token.brassPale, altezza: 1.6),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(top: 8.8),
                      child: TestoBilanciato(
                        titolo,
                        stile: Stile.serif(20.8, altezza: 1.25, colore: const Color(0xFFFFF8EC)),
                      ),
                    ),
                    for (final r in righe)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Paragrafo(r, style: Stile.sans(13.76, colore: const Color(0xFFE6D8E8), altezza: 1.6)),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// La tessera di un articolo dell'API.
class Tessera extends ConsumerWidget {
  /// La tessera di [a].
  const Tessera({super.key, required this.a, required this.indice});

  /// L'articolo.
  final ArticoloBreve a;

  /// La posizione nella griglia.
  final int indice;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final percorso = a.immagine?.mini ?? a.immagine?.url;
    final immagine = percorso == null
        ? const ImmagineCartaArticolo('maj-06')
        : Image(
            image: ref.watch(immagineMediaProvider)(percorso),
            fit: BoxFit.cover,
            excludeFromSemantics: true,
            errorBuilder: (context, e, s) => const SizedBox.shrink(),
          );
    return TesseraArticolo(
      indice: indice,
      href: R.articolo(a.slug),
      immagine: immagine,
      etichetta: a.sezione?.nome ?? (a.tags.isNotEmpty ? a.tags.first.nome : t.blog_eyebrow),
      titolo: a.titolo,
      righe: [t.blog_min(a.tempoLettura)],
    );
  }
}

/// I nove articoli.
class DiarioNove extends ConsumerWidget {
  /// I nove articoli per la pagina (il [contesto] come query: `carta=maj-17`), con [vuoto] se il diario è vuoto.
  const DiarioNove({super.key, this.contesto = '', this.eyebrow, this.titolo, this.vuoto});

  /// Il contesto della pagina.
  final String contesto;

  /// L'eyebrow (predefinita: quella del diario).
  final String? eyebrow;

  /// Il titolo (predefinito: quello del diario).
  final String? titolo;

  /// Cosa mostrare se non ci sono articoli.
  final Widget? vuoto;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final nove = ref.watch(noveProvider(contesto));
    if (nove.isLoading && !nove.hasValue) return const SizedBox.shrink();
    final dati = nove.value;
    final recenti = dati?.recenti ?? const [];
    final scelti = dati?.scelti ?? const [];
    if (recenti.isEmpty && scelti.isEmpty) return vuoto ?? const SizedBox.shrink();
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 14.4),
            // `.section-head`: sul telefono uno sotto l'altro, più largo il bottone a destra, in basso.
            child: telefono
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Eyebrow(eyebrow ?? t.blog_nove_eyebrow),
                      TitoloSezione(titolo ?? t.blog_nove_titolo),
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Bottone(t.blog_nove_ultimi, href: R.blog, variante: Variante.quieto),
                      ),
                    ],
                  )
                : Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Eyebrow(eyebrow ?? t.blog_nove_eyebrow),
                            TitoloSezione(titolo ?? t.blog_nove_titolo),
                          ],
                        ),
                      ),
                      const SizedBox(width: 11.2),
                      Bottone(t.blog_nove_ultimi, href: R.blog, variante: Variante.quieto),
                    ],
                  ),
          ),
          GrigliaArticoli(
            children: [for (final (i, a) in recenti.indexed) Tessera(a: a, indice: i)],
          ),
          if (scelti.isNotEmpty) ...[
            Padding(
              padding: const EdgeInsets.only(top: 11.2, bottom: 8),
              child: Text(t.blog_nove_attinenti, style: Stile.serif(20)),
            ),
            GrigliaArticoli(
              children: [
                for (final (i, a) in scelti.indexed)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Tessera(a: a, indice: i),
                      if (a.sezione != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 7.2),
                          child: Collegamento(
                            t.blog_nove_sezione(a.sezione!.nome),
                            href: R.blogSezione(a.sezione!.slug),
                            stile: Stile.sans(13.44, altezza: 1.6),
                          ),
                        ),
                    ],
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
