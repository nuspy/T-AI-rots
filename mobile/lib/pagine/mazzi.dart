/// I mazzi (`frontend/v2/pagine/mazzi.tsx`, montate da `app/(v2)/decks/page.tsx` e `decks/[slug]/page.tsx`): una casa
/// per più mazzi. Quelli disponibili arrivano dall'API (il predefinito, il Thoth, e quelli attivi adesso); quelli in
/// sviluppo sono dichiarati come tali, mai presentati come disponibili; poi l'invito al voto. Ogni mazzo ha la sua
/// pagina: il linguaggio delle immagini, la lettura, la biblioteca, l'edizione fisica e il PDF da stampare. Gli spazi
/// pubblicitari del sito non ci sono.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../cassa/pagamento.dart' show apriFuori;
import '../catalogo/comuni.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/cassa.dart';
import '../modelli/voto.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'voto.dart' show CampioniVoto, BarraPercentuale;

/// Le carte d'esempio di un mazzo.
const List<String> campioneMazzo = ['maj-00', 'maj-02', 'maj-06', 'maj-09', 'maj-17', 'maj-19'];

/// La cartella delle immagini di un mazzo: il predefinito (Thoth) nella cartella piatta (`''`), gli altri nella propria.
String cartellaDi(Mazzo m) => m.predefinito ? '' : m.slug;

/// La pagina dei mazzi.
class Mazzi extends ConsumerWidget {
  /// L'elenco.
  const Mazzi({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final mazzi = ref.watch(mazziProvider);
    final disponibili = [
      for (final m in mazzi.value ?? const <Mazzo>[])
        if (m.predefinito || m.attivoOra) m,
    ];
    final w = larghezza(context);
    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.mazzi_eyebrow, titolo: t.mazzi_titolo, intro: t.mazzi_intro, compatta: true),
        if (mazzi.hasError && !mazzi.hasValue) StatoFascia(errore: mazzi.error),
        for (final (i, m) in disponibili.indexed)
          Fascia(
            compatta: true,
            child: DisposizioneMazzo(
              sinistra: VentaglioMazzo(
                ids: [campioneMazzo[i.isOdd ? 1 : 0], 'maj-06', 'maj-19'],
                mazzo: cartellaDi(m),
              ),
              destra: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Disponibile(t.mazzi_disponibile),
                  TitoloSezione(m.nome),
                  IntroSezione(m.descrizione ?? (m.predefinito ? t.mazzi_thoth_intro : '')),
                  if (m.predefinito)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 13.44),
                      child: Text(t.mazzi_incluso, style: stilePiccolo()),
                    ),
                  Bottone(t.mazzi_entra(m.nome), href: R.mazzo(m.slug)),
                ],
              ),
            ),
          ),
        Fascia(
          compatta: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Eyebrow(t.mazzi_in_sviluppo),
              GrigliaDifferenze(
                children: [
                  for (final x in t.mazziFuturi)
                    TesseraDifferenza(
                      simbolo: x.simbolo,
                      titolo: x.nome,
                      testi: [
                        Padding(
                          padding: const EdgeInsets.only(bottom: 9.6),
                          child: Align(
                            alignment: AlignmentDirectional.centerStart,
                            child: Disponibile(t.mazzi_pianificato, pianificato: true, sotto: 0, px: 10.56),
                          ),
                        ),
                        t.mazzi_futuro_testo,
                      ],
                    ),
                ],
              ),
              Padding(
                padding: const EdgeInsets.only(top: 11.2),
                child: FasciaCondivisione(
                  testo: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      TitoloSezione(t.mazzi_voto_titolo, px: w.clampVw(24, 2.6, 35.2)),
                      Padding(
                        padding: const EdgeInsets.only(top: 9.6),
                        child: Paragrafo(t.mazzi_voto_testo, style: Stile.sans(16, colore: Token.inkSoft)),
                      ),
                    ],
                  ),
                  azione: Bottone(t.mazzi_voto_cta, href: R.voto, variante: Variante.quieto),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// La pagina di un mazzo.
class DettaglioMazzo extends ConsumerWidget {
  /// Il mazzo [slug].
  const DettaglioMazzo({super.key, required this.slug});

  /// Lo slug.
  final String slug;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final mazzi = ref.watch(mazziProvider);
    if (mazzi.hasError && !mazzi.hasValue) return Pagina(sezioni: [StatoFascia(errore: mazzi.error)]);
    final elenco = mazzi.value;
    if (elenco == null) return const Pagina(sezioni: [StatoFascia()]);
    final m = elenco.where((x) => x.slug == slug).firstOrNull;
    if (m == null) {
      return Pagina(
        sezioni: [
          Fascia(
            compatta: true,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                IntroSezione(t.mazzi_non_trovato, sopra: 0),
                const SizedBox(height: 16),
                Bottone(t.comune_nav_mazzi, href: R.mazzi, variante: Variante.quieto),
              ],
            ),
          ),
        ],
      );
    }
    final cartella = cartellaDi(m);
    final leggiQui = m.predefinito ? '${R.leggi}?deck=${m.slug}' : '${R.leggi}?deck=${m.slug}&source=deck';
    final w = larghezza(context);
    final collegamento = Stile.sans(14.08, altezza: 1.6);
    return Pagina(
      sezioni: [
        AperturaCatalogo(
          sopra: Disponibile(t.mazzi_disponibile),
          eyebrow: t.mazzi_mazzo_eyebrow(m.nome),
          titolo: m.predefinito ? t.mazzi_thoth_titolo : m.nome,
          intro: m.predefinito ? t.mazzi_thoth_intro : (m.descrizione ?? t.mazzi_altro_titolo),
        ),
        Fascia(
          compatta: true,
          child: DisposizioneMazzo(
            sinistra: VentaglioMazzo(ids: const ['maj-02', 'maj-06', 'maj-17'], mazzo: cartella),
            destra: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TitoloSezione(t.mazzi_slogan),
                IntroSezione(t.mazzi_slogan_testo),
                // `.minor-cta`: i collegamenti sottolineati in fila (`gap: .4rem 1rem`).
                Padding(
                  padding: EdgeInsets.only(top: w.telefono ? 9.6 : 16),
                  child: Wrap(
                    spacing: 16,
                    runSpacing: 6.4,
                    children: [
                      Collegamento(
                        t.mazzi_cta_leggi,
                        href: leggiQui,
                        stile: collegamento,
                        an: 'deck_viewed',
                        anProprieta: {'mazzo': m.slug},
                      ),
                      Collegamento(t.mazzi_cta_carte, href: R.carte, stile: collegamento),
                      Collegamento(t.mazzi_cta_fisica, href: '${R.fisica}?deck=${m.slug}', stile: collegamento),
                      Collegamento(t.mazzi_cta_negozio, href: R.negozio, stile: collegamento),
                    ],
                  ),
                ),
                StampaMazzo(mazzo: m),
              ],
            ),
          ),
        ),
        Fascia(
          compatta: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Eyebrow(t.mazzi_campione),
              GrigliaCarte(
                children: [
                  for (final id in campioneMazzo) TesseraCarta(id: id, href: R.carta(id), mazzo: cartella),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// «Stampa i tuoi Tarocchi»: il PDF da stampare. Gratuito si scarica subito (nel browser di sistema); a pagamento va
/// nel carrello e si passa al carrello. Senza prezzo non si propone.
class StampaMazzo extends ConsumerWidget {
  /// Il bottone del [mazzo].
  const StampaMazzo({super.key, required this.mazzo});

  /// Il mazzo.
  final Mazzo mazzo;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final stampa = mazzo.prezzoStampa;
    if (stampa == null) return const SizedBox.shrink();
    final Widget bottone;
    if (stampa == 0) {
      bottone = Bottone(
        '${t.mazzi_stampa_cta} · ${t.negozio_pdf_gratis}',
        variante: Variante.ottone,
        an: 'deck_pdf_viewed',
        alTocco: () => unawaited(apriFuori(Api.urlPdfGratuito(mazzo.slug))),
      );
    } else {
      final prezzo = mazzo.prezzoStampaScontato ?? stampa;
      bottone = Bottone(
        '${t.mazzi_stampa_cta} · ${euro(prezzo, lingua, valuta: mazzo.valuta)}',
        variante: Variante.ottone,
        an: 'carrello_aggiunto',
        anProprieta: {'mazzo': mazzo.slug, 'tipo': 'pdf'},
        alTocco: () {
          ref.read(carrelloProvider.notifier).aggiungi(mazzo.id, 'pdf');
          vai(context, R.carrello);
        },
      );
    }
    return Padding(padding: const EdgeInsets.only(top: 8), child: bottone);
  }
}

/// Il riepilogo pubblico del voto (`GET /voto/home`): l'ultima tornata chiusa.
final votoRiepilogoProvider = FutureProvider<VotoHome>((ref) => ref.read(apiProvider).votoHome());

/// `RiepilogoVoto`: l'ultimo risultato per chi non è entrato (`.panel`).
class RiepilogoVoto extends ConsumerWidget {
  /// Il riepilogo.
  const RiepilogoVoto({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final r = ref.watch(votoRiepilogoProvider).value?.risultatoRecente;
    if (r == null || r.candidati.isEmpty) return const SizedBox.shrink();
    return Pannello(
      titolo: t.mazzi_voto_ultimo,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (final c in r.candidati)
            VoceMemoria(
              titolo: c.nome,
              figli: [
                CampioniVoto(nome: c.nome, campioni: c.campioni),
                BarraPercentuale(percentuale: c.percentuale, etichetta: t.mazzi_voto_percentuale(c.percentuale)),
                Text(t.mazzi_voto_percentuale(c.percentuale), style: Stile.sans(13.44, altezza: 1.6)),
              ],
            ),
        ],
      ),
    );
  }
}
