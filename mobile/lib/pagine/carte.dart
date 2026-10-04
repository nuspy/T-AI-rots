/// Le carte (`frontend/v2/pagine/carte.tsx`, montate da `app/(v2)/cards/page.tsx` e `cards/[id]/page.tsx`): la
/// biblioteca delle 78 carte coi filtri, e la scheda di una carta che porta verso una domanda (immagine, parole chiave,
/// la domanda di riflessione, i significati per livello, rovesciata, ambiti, corrispondenze, la nota di Crowley, la
/// carta prima e dopo, i nove articoli del diario). I testi arrivano dall'API nella lingua dei contenuti. Gli spazi
/// pubblicitari del sito non ci sono (niente pubblicità nell'app).
library;

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../catalogo/comuni.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/diario.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/carta.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// I filtri della biblioteca, nell'ordine del sito.
const List<String> filtriCarte = ['tutte', 'maggiori', 'bastoni', 'coppe', 'spade', 'dischi'];

/// Le 78 carte nella lingua dei contenuti (`P.carte(lingua)`).
final carteProvider = FutureProvider<List<Carta>>((ref) {
  final lingua = ref.watch(linguaProvider.select(linguaContenuti));
  return ref.read(apiProvider).carte(lingua);
});

/// La scheda completa di una carta (per id o slug), nella lingua dei contenuti.
final schedaCartaProvider = FutureProvider.family<Carta, String>((ref, id) {
  final lingua = ref.watch(linguaProvider.select(linguaContenuti));
  return ref.read(apiProvider).carta(id, lingua);
});

/// Il nome della carta nella lingua dell'interfaccia (`nomeDi` del sito).
String nomeDi(Carta c, String lingua) => c.nomeIn(lingua);

/// La pagina della biblioteca.
class Carte extends StatelessWidget {
  /// La biblioteca.
  const Carte({super.key});

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.carte_eyebrow, titolo: t.carte_titolo, intro: t.carte_intro, compatta: true),
        const Biblioteca(),
      ],
    );
  }
}

/// `Biblioteca`: i filtri (pillole) e la griglia delle carte.
class Biblioteca extends ConsumerStatefulWidget {
  /// La biblioteca.
  const Biblioteca({super.key});

  @override
  ConsumerState<Biblioteca> createState() => _BibliotecaState();
}

class _BibliotecaState extends ConsumerState<Biblioteca> {
  String _filtro = 'tutte';

  bool _visibile(Carta c) => switch (_filtro) {
    'tutte' => true,
    'maggiori' => c.arcano == 'maggiore',
    final seme => c.seme == seme,
  };

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final carte = ref.watch(carteProvider);
    final nomi = t.carteFiltri;
    final visibili = (carte.value ?? const <Carta>[]).where(_visibile).toList();
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 11.2),
            child: Semantics(
              label: t.carte_filtri_aria,
              container: true,
              child: Pillole(
                children: [
                  for (final f in filtriCarte)
                    Pillola(nomi[f] ?? f, acceso: f == _filtro, alTocco: () => setState(() => _filtro = f)),
                ],
              ),
            ),
          ),
          if (carte.hasError && !carte.hasValue) Errore(messaggioErrore(carte.error!, t), sopra: 0),
          GrigliaCarte(
            children: [
              for (final c in visibili)
                TesseraCarta(
                  id: c.id,
                  href: R.carta(c.slug ?? c.id),
                  alt: nomeDi(c, lingua),
                  nome: nomeDi(c, lingua),
                  mazzo: '',
                  sotto: c.arcanoLabel == null ? null : (c.arcano == 'maggiore' ? c.numeroRomano : c.semeLabel),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

/// La pagina di una carta.
class DettaglioCarta extends ConsumerWidget {
  /// La carta [id] (id o slug).
  const DettaglioCarta({super.key, required this.id});

  /// L'id o lo slug.
  final String id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final carta = ref.watch(schedaCartaProvider(id));
    final List<Widget> sezioni;
    if (carta.hasError && !carta.hasValue) {
      sezioni = [
        Fascia(
          compatta: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              IntroSezione(t.carte_non_trovata, sopra: 0),
              const SizedBox(height: 16),
              Bottone(t.carte_torna, href: R.carte, variante: Variante.quieto),
            ],
          ),
        ),
      ];
    } else if (carta.value == null) {
      sezioni = [const StatoFascia()];
    } else {
      final c = carta.value!;
      sezioni = [
        _SchedaCarta(c: c, lingua: lingua),
        DiarioNove(contesto: 'carta=${Uri.encodeQueryComponent(c.id)}'),
      ];
    }
    return Pagina(sezioni: sezioni);
  }
}

class _SchedaCarta extends ConsumerWidget {
  const _SchedaCarta({required this.c, required this.lingua});

  final Carta c;
  final String lingua;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final nome = nomeDi(c, lingua);
    final elenco = ref.watch(carteProvider).value ?? const <Carta>[];
    final i = elenco.indexWhere((x) => x.id == c.id);
    final prima = i > 0 ? elenco[i - 1] : null;
    final dopo = i >= 0 && i < elenco.length - 1 ? elenco[i + 1] : null;
    final lettera = c.letteraEbraica;
    final corrispondenze = [
      if (lettera != null) '${lettera.nome} ${lettera.glifo}',
      if (c.percorso != null)
        t.carte_sentiero(c.percorso!) + (c.collega != null ? ' (${c.collega!.join(' – ')})' : ''),
      ?c.sefira,
      c.elementoLabel ?? c.elemento,
      c.astrologia,
    ].where((s) => s.isNotEmpty).toList();
    final arcano = c.arcanoLabel ?? (c.arcano == 'maggiore' ? t.carte_filtri_maggiori : (c.semeLabel ?? ''));
    final livelli = t.carteLivelli;
    final ambiti = t.carteAmbiti;
    final significati = c.significati ?? const <String, String>{};
    final ambitiCarta = c.ambiti ?? const <String, String>{};

    final immagine = Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 300),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // `.card-large`: la cornice crema di 5 px e l'ombra lunga.
            Container(
              decoration: const BoxDecoration(
                border: Border.fromBorderSide(BorderSide(color: Colori.cornice, width: 5)),
                boxShadow: [BoxShadow(color: Color(0x47201026), offset: Offset(0, 24), blurRadius: 40)],
              ),
              child: ImmagineCarta(c.id, alt: nome, mazzo: ''),
            ),
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Paragrafo(c.paroleChiave.join(' · '), style: stilePiccolo()),
            ),
          ],
        ),
      ),
    );

    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Eyebrow(t.carte_carta_riflessione),
        TitoloSezione(t.carte_carta_domanda(nome)),
        IntroSezione(t.carte_carta_nota),
        Padding(
          padding: const EdgeInsets.only(top: 8, bottom: 13.6),
          child: FilaBottoni(
            children: [
              Bottone(t.carte_cta_leggi, href: '${R.leggi}?card=${Uri.encodeQueryComponent(c.slug ?? c.id)}&source=card'),
              Bottone(t.carte_cta_fisica, href: R.fisica, variante: Variante.quieto),
            ],
          ),
        ),
        BloccoProsa([
          if (c.dritto != null) ...[TitoloProsa(t.carte_dritta), ParagrafoProsa(c.dritto!)],
          for (final e in significati.entries) ...[TitoloProsa(livelli[e.key] ?? e.key), ParagrafoProsa(e.value)],
          if (c.rovescio != null) ...[
            TitoloProsa(t.carte_rovesciata),
            ParagrafoProsa(t.carte_rovesciata_nota, piccolo: true, tenue: true),
            ParagrafoProsa(c.rovescio!),
          ],
          if (ambitiCarta.isNotEmpty) ...[
            TitoloProsa(t.carte_ambiti_titolo),
            for (final e in ambitiCarta.entries) ParagrafoProsa(e.value, inGrassetto: '${ambiti[e.key] ?? e.key}.'),
          ],
          TitoloProsa(t.carte_corrispondenze),
          ParagrafoProsa(corrispondenze.join(' · '), piccolo: true),
          if (c.notaCrowley != null) ...[TitoloProsa(t.carte_crowley), ParagrafoProsa(c.notaCrowley!)],
        ]),
        // `.pager`: la carta prima a sinistra, quella dopo a destra.
        Padding(
          padding: const EdgeInsets.only(top: 11.2),
          child: Semantics(
            label: t.carte_torna,
            container: true,
            child: Row(
              children: [
                Flexible(
                  child: prima == null
                      ? const SizedBox.shrink()
                      : Collegamento(
                          '← ${nomeDi(prima, lingua)}',
                          href: R.carta(prima.slug ?? prima.id),
                          stile: Stile.sans(16, altezza: 1.6),
                        ),
                ),
                const SizedBox(width: 16),
                Flexible(
                  child: Align(
                    alignment: AlignmentDirectional.centerEnd,
                    child: dopo == null
                        ? const SizedBox.shrink()
                        : Collegamento(
                            '${nomeDi(dopo, lingua)} →',
                            href: R.carta(dopo.slug ?? dopo.id),
                            stile: Stile.sans(16, altezza: 1.6),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        AperturaCatalogo(
          eyebrow: t.carte_carta_eyebrow(arcano),
          titolo: nome,
          intro: c.titoloThoth,
        ),
        Fascia(
          compatta: true,
          child: DisposizioneMazzo(inAlto: true, sinistra: immagine, destra: testo),
        ),
      ],
    );
  }
}
