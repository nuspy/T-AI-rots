/// Il diario (`frontend/v2/pagine/blog.tsx`, `app/(v2)/blog/**`, `app/(v2)/explore`): un grafo di contenuti, non una
/// lista di post. Ogni articolo porta a una carta, una stesa, un mazzo, e infine a una domanda.
///
/// - [Blog]: la ricerca, l'articolo in evidenza, gli ultimi a pagine, dieci scelti a caso per la giornata (solo in
///   prima pagina), il ponte verso la lettura; accanto (sotto, sul telefono) le sezioni ad albero e le etichette;
/// - [BlogSezione], [BlogTag]: le briciole, le sottosezioni, le carte o le stese della sezione, gli articoli;
/// - [Articolo]: il testo (`lib/blog/markdown.dart`), le domande frequenti, ciò di cui parla, le etichette, la
///   condivisione (il foglio del telefono), il ponte, i correlati, precedente e successivo, i nove articoli;
/// - [Esplora]: le sei porte del grafo e il diario.
///
/// Niente spazi pubblicitari (niente pubblicità nell'app al lancio).
library;

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:share_plus/share_plus.dart';

import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../blog/markdown.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/diario.dart';
import '../componenti/formati.dart';
import '../componenti/griglia.dart';
import '../componenti/miniatura_stesa.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../config.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/blog.dart';
import '../modelli/carta.dart';
import '../modelli/pubblici.dart';
import '../rotte/indirizzi.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'prezzi.dart' show FasciaStretta;
import 'stese.dart' show nomeStesa;

/// Articoli per pagina, se non se ne sceglie un altro numero, negli elenchi del diario e delle pagine di carte e stese
/// (`PER_PAGINA_BLOG`).
const int perPaginaBlog = 25;

/// Le scelte del numero di articoli per pagina (`?per=` nell'indirizzo, come il sito).
const List<int> sceltePerPagina = [10, 25, 50];

/// Quanti articoli recenti chiedere a `GET /blog/nove` perché i dieci scelti a caso non ripetano la prima pagina: il
/// server ne dà al più 12 (`recenti` ≤ 12), anche se la pagina ne mostra 25 o 50.
int _recentiNove(int per) => math.min(per, 12);

/* ---- i dati ------------------------------------------------------------------------------------------------------- */

/// Una pagina dell'elenco degli articoli (la query: `pagina`, `per_pagina`, `q`, `sezione`, `tag`, `evidenza`).
final elencoArticoliProvider = FutureProvider.family<ElencoArticoli, String>((ref, query) {
  ref.watch(linguaProvider);
  return ref.read(apiProvider).articoli(Uri.splitQueryString(query));
});

/// L'albero delle sezioni.
final sezioniBlogProvider = FutureProvider<List<NodoSezione>>((ref) => ref.read(apiProvider).sezioni());

/// Le etichette.
final etichetteBlogProvider = FutureProvider<List<EtichettaConConteggio>>((ref) => ref.read(apiProvider).etichette());

/// Una sezione, nella lingua dei contenuti.
final sezioneBlogProvider = FutureProvider.family<DettaglioSezione, String>((ref, slug) {
  final lingua = ref.watch(linguaProvider);
  return ref.read(apiProvider).sezione(slug, lingua);
});

/// Un articolo.
final articoloBlogProvider = FutureProvider.family<ArticoloBlog, String>(
  (ref, slug) => ref.read(apiProvider).articolo(slug),
);

String _query(Map<String, Object?> p) => Uri(
  queryParameters: {
    for (final e in p.entries)
      if (e.value != null && '${e.value}'.isNotEmpty) e.key: '${e.value}',
  },
).query;

int _pagina(Map<String, String> parametri) => math.max(1, int.tryParse(parametri['page'] ?? '') ?? 1);

/// Gli articoli per pagina scelti nell'indirizzo (`?per=10|25|50`); un altro valore vale [perPaginaBlog].
int perPaginaDa(Map<String, String> parametri) {
  final n = int.tryParse(parametri['per'] ?? '');
  return sceltePerPagina.contains(n) ? n! : perPaginaBlog;
}

/// Gli articoli su una carta o una stesa, a pagine (`GET /blog/posts?carta=…|stesa=…`, v9.4).
final articoliSuProvider = FutureProvider.family<ElencoArticoli, ({String tipo, String id, int pagina, int per})>((
  ref,
  x,
) {
  ref.watch(linguaProvider);
  return ref.read(apiProvider).articoliSuPagine(x.tipo, x.id, pagina: x.pagina, perPagina: x.per);
});

/* ---- i pezzi comuni ----------------------------------------------------------------------------------------------- */

/// `.article` negli elenchi del diario: `min-height: 260px`; quella in evidenza (`.article-featured`) 380 px, col titolo
/// più grande e l'estratto.
class TesseraDiario extends ConsumerWidget {
  /// La tessera di [a].
  const TesseraDiario({super.key, required this.a, required this.indice, this.grande = false});

  /// L'articolo.
  final ArticoloBreve a;

  /// La posizione nella griglia (il colore della sfumatura).
  final int indice;

  /// In evidenza.
  final bool grande;

  static const List<Color> _sfumature = [Color(0xF0201026), Color(0xF219706F), Color(0xF23C1846)];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    final percorso = a.immagine?.mini ?? a.immagine?.url;
    final immagine = percorso == null
        ? const ImmagineCartaArticolo('maj-06')
        : Image(
            image: ref.watch(immagineMediaProvider)(percorso),
            fit: BoxFit.cover,
            excludeFromSemantics: true,
            errorBuilder: (context, e, s) => const SizedBox.shrink(),
          );
    final colore = _sfumature[indice % 3];
    final minimo = grande ? 380.0 : 260.0;
    final nota = Stile.sans(13.76, colore: const Color(0xFFE6D8E8), altezza: 1.6);
    return Premibile(
      alTocco: () => vai(context, R.articolo(a.slug)),
      collegamento: true,
      costruisci: (context, premuto) => ConstrainedBox(
        constraints: BoxConstraints(minHeight: minimo),
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
                constraints: BoxConstraints(minHeight: minimo - 44.8),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      (a.sezione?.nome ?? (a.tags.isNotEmpty ? a.tags.first.nome : t.blog_eyebrow)).toUpperCase(),
                      style: Stile.sans(11.2, peso: FontWeight.w700, em: .08, colore: Token.brassPale, altezza: 1.6),
                    ),
                    Padding(
                      padding: const EdgeInsets.only(top: 8.8),
                      child: TestoBilanciato(
                        a.titolo,
                        stile: Stile.serif(
                          grande ? w.clampVw(24, 2.8, 35.2) : 20.8,
                          altezza: 1.25,
                          colore: const Color(0xFFFFF8EC),
                        ),
                      ),
                    ),
                    if (grande && (a.estratto ?? '').isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Paragrafo(a.estratto!, style: nota),
                      ),
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(t.blog_min(a.tempoLettura), style: nota),
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

/// `.journal-grid`: `repeat(auto-fill, minmax(230px, 1fr))`, `gap: 1.1rem`.
class GrigliaDiario extends StatelessWidget {
  /// Le tessere.
  const GrigliaDiario({super.key, required this.children});

  /// Le tessere.
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, v) {
      final colonne = math.max(1, ((v.maxWidth + 17.6) / (230 + 17.6)).floor());
      return Griglia(colonne: colonne, spazioColonne: 17.6, spazioRighe: 17.6, allunga: false, children: children);
    },
  );
}

/// `.diario-nove-voce`: la tessera col collegamento alla sua sezione.
class _VoceConSezione extends StatelessWidget {
  const _VoceConSezione({required this.a, required this.indice});

  final ArticoloBreve a;
  final int indice;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TesseraDiario(a: a, indice: indice),
        if (a.sezione != null)
          Padding(
            padding: const EdgeInsets.only(top: 7.2),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: Collegamento(
                t.blog_nove_sezione(a.sezione!.nome),
                href: R.blogSezione(a.sezione!.slug),
                stile: Stile.sans(13.44, altezza: 1.6),
              ),
            ),
          ),
      ],
    );
  }
}

/// `.diario-nove-sotto`: il titoletto serif fra due gruppi.
Widget _sotto(String testo) => Padding(
  padding: const EdgeInsets.only(top: 11.2, bottom: 8),
  child: Semantics(
    header: true,
    child: Text(testo, style: Stile.serif(20, colore: Token.ink)),
  ),
);

/// I dieci a caso delle pagine del diario: sotto gli ultimi, solo in prima pagina, ognuno col collegamento alla sua
/// sezione. Stessa scelta per tutta la giornata (la decide il server).
class _SceltiACaso extends ConsumerWidget {
  const _SceltiACaso({required this.contesto});

  final String contesto;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scelti = ref.watch(noveProvider(contesto)).value?.scelti ?? const <ArticoloBreve>[];
    if (scelti.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 11.2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _sotto(context.t.blog_a_caso),
          GrigliaDiario(
            children: [for (final (i, a) in scelti.indexed) _VoceConSezione(a: a, indice: i)],
          ),
        ],
      ),
    );
  }
}

/// `nav.pager` (v9.4): «← più recenti», «pagina 2 di 5», «meno recenti →»; sotto, i numeri delle pagine (la prima,
/// l'ultima e le vicine a quella corrente, con «…» in mezzo) e la scelta di 10 / 25 / 50 articoli per pagina. Il numero
/// per pagina resta nei collegamenti (`?per=`, assente se è quello predefinito); cambiarlo riporta alla prima pagina.
/// Ogni bersaglio è alto almeno 48 px.
class PaginatoreBlog extends StatelessWidget {
  /// Il navigatore della pagina [pagina] di [pagine], con [per] articoli per pagina su [totale], verso [base].
  const PaginatoreBlog({
    super.key,
    required this.pagina,
    required this.pagine,
    required this.base,
    this.per = perPaginaBlog,
    this.totale = 0,
    this.q,
  });

  /// La pagina corrente (da 1).
  final int pagina;

  /// Quante pagine.
  final int pagine;

  /// L'indirizzo dell'elenco, senza query.
  final String base;

  /// Gli articoli per pagina.
  final int per;

  /// Gli articoli in tutto (la scelta per pagina si mostra solo se ce ne sono più della scelta minima).
  final int totale;

  /// La ricerca, da conservare nei collegamenti.
  final String? q;

  /// L'indirizzo della pagina [p], con [conPer] articoli per pagina (predefinito: quelli correnti).
  String href(int p, {int? conPer}) {
    final n = conPer ?? per;
    final query = _query({'q': q, if (p > 1) 'page': p, if (n != perPaginaBlog) 'per': n});
    return query.isEmpty ? base : '$base?$query';
  }

  /// I numeri da mostrare: 1, l'ultima, e [vicine] pagine attorno alla corrente; `null` dove ne mancano (i «…»).
  static List<int?> numeri(int pagina, int pagine, {int vicine = 1}) {
    final scelti = <int>{1, pagine, for (var i = pagina - vicine; i <= pagina + vicine; i++) i}
      ..removeWhere((p) => p < 1 || p > pagine);
    final ordinati = scelti.toList()..sort();
    final esito = <int?>[];
    int? ultimo;
    for (final p in ordinati) {
      if (ultimo != null && p - ultimo > 1) esito.add(null);
      esito.add(p);
      ultimo = p;
    }
    return esito;
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final conScelta = totale > sceltePerPagina.first;
    if (pagine <= 1 && !conScelta) return const SizedBox.shrink();
    final etichetta = t.blog_pagina(math.min(pagina, math.max(1, pagine)), math.max(1, pagine));
    final largo = !MediaQuery.sizeOf(context).width.telefono;
    return Semantics(
      container: true,
      label: etichetta,
      child: Padding(
        padding: const EdgeInsets.only(top: 11.2),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (pagine > 1) ...[
              Row(
                children: [
                  if (pagina > 1)
                    _Alto48(
                      child: Bottone(
                        t.blog_piu_recenti,
                        href: href(pagina - 1),
                        variante: Variante.quieto,
                        piccolo: true,
                      ),
                    )
                  else
                    const SizedBox.shrink(),
                  const Spacer(),
                  Text(etichetta, style: stilePiccolo()),
                  const Spacer(),
                  if (pagina < pagine)
                    _Alto48(
                      child: Bottone(
                        t.blog_meno_recenti,
                        href: href(pagina + 1),
                        variante: Variante.quieto,
                        piccolo: true,
                      ),
                    )
                  else
                    const SizedBox.shrink(),
                ],
              ),
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Wrap(
                  alignment: WrapAlignment.center,
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    for (final n in numeri(pagina, pagine, vicine: largo ? 2 : 1))
                      if (n == null)
                        SizedBox(
                          width: 24,
                          height: 48,
                          child: Center(
                            child: ExcludeSemantics(child: Text('…', style: stilePiccolo())),
                          ),
                        )
                      else
                        _NumeroPagina(
                          numero: n,
                          corrente: n == pagina,
                          href: href(n),
                          etichetta: t.blog_pagina(n, pagine),
                        ),
                  ],
                ),
              ),
            ],
            if (conScelta)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Semantics(
                  container: true,
                  label: t.blog_per_pagina,
                  child: Wrap(
                    alignment: WrapAlignment.center,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ExcludeSemantics(child: Text(t.blog_per_pagina, style: stilePiccolo())),
                      for (final n in sceltePerPagina)
                        _Alto48(
                          child: Pillola(
                            '$n',
                            acceso: n == per,
                            alTocco: () => vai(context, href(1, conPer: n)),
                          ),
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

/// Alto almeno 48 px (il bersaglio minimo del tocco su Android): il figlio si allunga fino a lì.
class _Alto48 extends StatelessWidget {
  const _Alto48({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) => ConstrainedBox(constraints: const BoxConstraints(minHeight: 48), child: child);
}

/// Il numero di una pagina: un quadrato di 48 px, prugna se è quella corrente.
class _NumeroPagina extends StatelessWidget {
  const _NumeroPagina({required this.numero, required this.corrente, required this.href, required this.etichetta});

  final int numero;
  final bool corrente;
  final String href;
  final String etichetta;

  @override
  Widget build(BuildContext context) => Premibile(
    alTocco: corrente ? null : () => vai(context, href),
    collegamento: true,
    selezionato: corrente,
    etichetta: etichetta,
    raggioFuoco: Token.raggio,
    costruisci: (context, premuto) => Container(
      constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
      padding: const EdgeInsets.symmetric(horizontal: 8),
      decoration: BoxDecoration(
        color: corrente ? Token.plum : (premuto ? const Color(0x0F3C1846) : null),
        border: Border.all(color: corrente ? Token.plum : Token.line),
        borderRadius: BorderRadius.circular(Token.raggio),
      ),
      child: Center(
        widthFactor: 1,
        heightFactor: 1,
        child: Text(
          '$numero',
          style: Stile.sans(15, colore: corrente ? const Color(0xFFFFF7E8) : Token.ink, altezza: 1.2),
        ),
      ),
    ),
  );
}

/// `.sezioni-box`: il riquadro con la riga d'ottone in alto e il titolo con la stella.
class _Riquadro extends StatelessWidget {
  const _Riquadro({required this.titolo, required this.child});

  final String titolo;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 13.6, vertical: 12),
      decoration: const BoxDecoration(
        color: Token.paperLight,
        border: Border(
          top: BorderSide(color: Token.brass, width: 3),
          left: BorderSide(color: Token.line),
          right: BorderSide(color: Token.line),
          bottom: BorderSide(color: Token.line),
        ),
        boxShadow: [BoxShadow(color: Color(0x0F3C1846), offset: Offset(0, 10), blurRadius: 24)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 7.2),
            child: Semantics(
              header: true,
              child: Row(
                children: [
                  ExcludeSemantics(
                    child: Text('✦', style: Stile.serif(13.6, colore: Token.brass)),
                  ),
                  const SizedBox(width: 7.2),
                  Expanded(
                    child: Text(titolo, style: Stile.serif(19.2, colore: Token.ink)),
                  ),
                ],
              ),
            ),
          ),
          child,
        ],
      ),
    );
  }
}

/// Le sezioni come un piccolo albero: ogni ramo collegato al padre da un tratto d'ottone, il numero degli articoli in
/// una pastiglia, la sezione corrente in prugna. Voci alte 44 px.
class _Albero extends StatelessWidget {
  const _Albero({required this.nodi, this.corrente, this.livello = 0});

  final List<NodoSezione> nodi;
  final String? corrente;
  final int livello;

  static const Color _ramo = Color(0x80B28336);

  @override
  Widget build(BuildContext context) {
    final voci = [
      for (final n in nodi)
        Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Stack(
              clipBehavior: Clip.none,
              children: [
                // `.albero-rami > li::before`: il tratto orizzontale verso la voce.
                if (livello > 0)
                  const Positioned(
                    left: -12.8,
                    top: 22,
                    child: SizedBox(width: 10.4, child: Divider0(colore: _ramo)),
                  ),
                _VoceAlbero(nodo: n, attiva: n.slug == corrente, radice: livello == 0),
              ],
            ),
            if (n.figli.isNotEmpty) _Albero(nodi: n.figli, corrente: corrente, livello: livello + 1),
          ],
        ),
    ];
    final colonna = Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: voci);
    if (livello == 0) return colonna;
    // `.albero-rami { margin-left: .95rem; padding-left: .8rem; border-left: 1px solid … }`.
    return Container(
      margin: const EdgeInsets.only(left: 15.2),
      padding: const EdgeInsets.only(left: 12.8),
      decoration: const BoxDecoration(
        border: Border(left: BorderSide(color: _ramo)),
      ),
      child: colonna,
    );
  }
}

/// Una riga sottile (il tratto dell'albero).
class Divider0 extends StatelessWidget {
  /// Una riga di [colore].
  const Divider0({super.key, required this.colore});

  /// Il colore.
  final Color colore;

  @override
  Widget build(BuildContext context) => SizedBox(height: 1, child: ColoredBox(color: colore));
}

class _VoceAlbero extends StatelessWidget {
  const _VoceAlbero({required this.nodo, required this.attiva, required this.radice});

  final NodoSezione nodo;
  final bool attiva;
  final bool radice;

  @override
  Widget build(BuildContext context) {
    final chiaro = attiva ? const Color(0xFFFFF7E8) : Token.ink;
    return Premibile(
      alTocco: () => vai(context, R.blogSezione(nodo.slug)),
      collegamento: true,
      selezionato: attiva,
      raggioFuoco: Token.raggio,
      costruisci: (context, premuto) => Container(
        constraints: const BoxConstraints(minHeight: 44),
        padding: const EdgeInsets.symmetric(horizontal: 8.8, vertical: 4.8),
        decoration: BoxDecoration(
          color: attiva ? Token.plum : (premuto ? Token.mist : null),
          borderRadius: BorderRadius.circular(Token.raggio),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                nodo.nome,
                style: radice ? Stile.serif(16.32, colore: chiaro) : Stile.sans(16, colore: chiaro, altezza: 1.6),
              ),
            ),
            const SizedBox(width: 8),
            Container(
              constraints: const BoxConstraints(minWidth: 28.8),
              padding: const EdgeInsets.symmetric(horizontal: 7.2, vertical: .8),
              decoration: BoxDecoration(
                color: attiva ? const Color(0x2EFFFFFF) : const Color(0x29B28336),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(
                '${nodo.nArticoli}',
                textAlign: TextAlign.center,
                style: Stile.sans(12, colore: attiva ? const Color(0xFFFFF7E8) : Token.inkSoft, altezza: 1.6),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// `.journal-aside`: le sezioni e le etichette.
class _Laterale extends ConsumerWidget {
  const _Laterale({this.corrente});

  final String? corrente;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final albero = ref.watch(sezioniBlogProvider).value;
    final tag = ref.watch(etichetteBlogProvider).value ?? const <EtichettaConConteggio>[];
    return Semantics(
      container: true,
      label: t.blog_sezioni,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _Riquadro(
            titolo: t.blog_sezioni,
            child: albero == null ? const SizedBox.shrink() : _Albero(nodi: albero, corrente: corrente),
          ),
          if (tag.isNotEmpty) ...[
            const SizedBox(height: 11.2),
            _Riquadro(
              titolo: t.blog_etichette,
              child: Pillole(
                children: [
                  for (final e in tag.take(24)) Pillola(e.nome, alTocco: () => vai(context, R.blogTag(e.slug))),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

/// `.story-grid.journal-layout`: il contenuto (`1.3fr`) e accanto le sezioni (`.7fr`); sul telefono una sotto l'altra.
class _Disposizione extends StatelessWidget {
  const _Disposizione({required this.contenuto, required this.laterale});

  final Widget contenuto;
  final Widget laterale;

  @override
  Widget build(BuildContext context) {
    if (MediaQuery.sizeOf(context).width.telefono) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [contenuto, const SizedBox(height: 11.2), laterale],
      );
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(flex: 13, child: contenuto),
        const SizedBox(width: 11.2),
        Expanded(flex: 7, child: laterale),
      ],
    );
  }
}

/// Il ponte verso la lettura (`.share-band`): «Portalo in una domanda».
class _Ponte extends StatelessWidget {
  const _Ponte();

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    final testo = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Eyebrow(t.blog_ponte_titolo),
        Paragrafo(t.blog_ponte_testo, style: Stile.sans(16, colore: Token.inkSoft, altezza: 1.6)),
      ],
    );
    final bottone = Bottone(t.blog_ponte_cta, href: '${R.leggi}?source=journal', variante: Variante.ottone);
    return Container(
      margin: const EdgeInsets.only(top: 13.6),
      padding: EdgeInsets.symmetric(horizontal: w.clampVw(24, 4, 40), vertical: w.clampVw(12, 2, 20)),
      decoration: BoxDecoration(
        color: Token.paperLight,
        border: Border.all(color: Token.line),
      ),
      child: LayoutBuilder(
        builder: (context, v) => w.telefono
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

/// Le briciole (`nav` piccola e tenue, i collegamenti separati da «·»).
class _Briciole extends StatelessWidget {
  const _Briciole({required this.voci});

  final List<({String testo, String href})> voci;

  @override
  Widget build(BuildContext context) {
    final stile = Stile.sans(13.44, altezza: 1.6, colore: Token.inkSoft);
    return Semantics(
      container: true,
      label: context.t.blog_percorso,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Wrap(
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            for (final (i, v) in voci.indexed) ...[
              if (i > 0) Text(' · ', style: stile),
              Collegamento(v.testo, href: v.href, stile: stile),
            ],
          ],
        ),
      ),
    );
  }
}

/// `.subhero.subhero-compact` col contenuto della pagina (briciole, occhiello, titolo, introduzione, note).
class _Apertura extends StatelessWidget {
  const _Apertura({required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final sopra = w.telefono ? 16.0 : w.clampVw(16, 2.1, 25.6);
    final sotto = w.telefono ? 16.0 : 14.4;
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: Token.larghezzaBanda),
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.fromLTRB(w.gutter, sopra, w.gutter, sotto),
          decoration: const BoxDecoration(
            border: Border(bottom: BorderSide(color: Token.line)),
          ),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: children),
        ),
      ),
    );
  }
}

/// Il titolo grande di un'apertura compatta (`.subhero-compact .display`).
Widget _titoloApertura(BuildContext context, String testo, {double maxCh = 18}) {
  final w = MediaQuery.sizeOf(context).width;
  return Semantics(
    header: true,
    child: TestoBilanciato(testo, stile: Stile.serif(w.clampVw(32, 4.2, 64), altezza: 1.05, em: -.055), maxCh: maxCh),
  );
}

/// `.question-form` della ricerca: il campo e il bottone (uno sotto l'altro sul telefono).
class _Ricerca extends StatefulWidget {
  const _Ricerca({required this.iniziale});

  final String iniziale;

  @override
  State<_Ricerca> createState() => _RicercaState();
}

class _RicercaState extends State<_Ricerca> {
  late final TextEditingController _testo = TextEditingController(text: widget.iniziale);
  final FocusNode _fuoco = FocusNode(debugLabel: 'cerca-diario');

  @override
  void dispose() {
    _testo.dispose();
    _fuoco.dispose();
    super.dispose();
  }

  void _cerca() {
    final pulito = _testo.text.trim();
    vai(context, pulito.isEmpty ? R.blog : '${R.blog}?q=${Uri.encodeComponent(pulito)}');
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final campo = Semantics(
      textField: true,
      label: t.blog_cerca,
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 44),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Stack(
            alignment: AlignmentDirectional.centerStart,
            children: [
              ValueListenableBuilder(
                valueListenable: _testo,
                builder: (context, valore, _) => valore.text.isEmpty
                    ? IgnorePointer(
                        child: Text(
                          t.blog_cerca_segnaposto,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: Stile.sans(16, colore: Colori.segnaposto, altezza: 1.6),
                        ),
                      )
                    : const SizedBox.shrink(),
              ),
              EditableText(
                controller: _testo,
                focusNode: _fuoco,
                style: Stile.sans(16, colore: Token.ink, altezza: 1.6),
                cursorColor: Token.ink,
                backgroundCursorColor: Token.inkSoft,
                maxLines: 1,
                keyboardType: TextInputType.text,
                textInputAction: TextInputAction.search,
                onSubmitted: (_) => _cerca(),
                inputFormatters: const [],
                selectionColor: const Color(0x4019706F),
              ),
            ],
          ),
        ),
      ),
    );
    final bottone = Bottone(t.blog_cerca_vai, pieno: telefono, alTocco: _cerca);
    return Container(
      constraints: const BoxConstraints(maxWidth: 580),
      margin: const EdgeInsets.only(bottom: 11.2),
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
}

/* ---- l'indice ------------------------------------------------------------------------------------------------------ */

/// L'indice del diario (`/blog`, `?q=`, `?page=`).
class Blog extends ConsumerWidget {
  /// L'indice, coi parametri dell'indirizzo.
  const Blog({super.key, required this.parametri});

  /// I parametri della query (`q`, `page`).
  final Map<String, String> parametri;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final q = parametri['q'] ?? '';
    final pagina = _pagina(parametri);
    final per = perPaginaDa(parametri);
    final elenco = ref.watch(elencoArticoliProvider(_query({'q': q, 'pagina': pagina, 'per_pagina': per})));
    final evidenza = q.isNotEmpty || pagina > 1
        ? null
        : ref.watch(elencoArticoliProvider(_query({'evidenza': 'true', 'per_pagina': 1}))).value;
    final primo = evidenza?.articoli.firstOrNull;
    final dati = elenco.value;
    final lista = (dati?.articoli ?? const <ArticoloBreve>[]).where((a) => a.slug != primo?.slug).toList();

    final contenuto = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (q.isNotEmpty && dati != null)
          Semantics(
            liveRegion: true,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Text(t.blog_risultati(dati.totale, q), style: Stile.sans(16, colore: Token.ink, altezza: 1.6)),
            ),
          ),
        if (elenco.hasError && !elenco.hasValue) Errore(messaggioErrore(elenco.error!, t), sopra: 0),
        if (dati != null && lista.isEmpty && primo == null)
          Avviso(q.isNotEmpty ? t.blog_nessun_risultato : t.blog_vuoto, sopra: 0),
        if (primo != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: TesseraDiario(a: primo, indice: 0, grande: true),
          ),
        if (lista.isNotEmpty) ...[
          if (q.isEmpty) Eyebrow(t.blog_ultimi),
          GrigliaDiario(
            children: [for (final (i, a) in lista.indexed) TesseraDiario(a: a, indice: i)],
          ),
          PaginatoreBlog(pagina: pagina, pagine: dati!.pagine, totale: dati.totale, per: per, base: R.blog, q: q),
        ],
        if (q.isEmpty && pagina == 1) _SceltiACaso(contesto: _query({'recenti': _recentiNove(per), 'scelti': 10})),
        if (dati != null && lista.isEmpty)
          PaginatoreBlog(pagina: pagina, pagine: dati.pagine, totale: dati.totale, per: per, base: R.blog, q: q),
        const _Ponte(),
      ],
    );

    return Pagina(
      sezioni: [
        Sottotitolo(eyebrow: t.blog_eyebrow, titolo: t.blog_titolo, intro: t.blog_intro, compatta: true),
        FasciaStretta(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: _Ricerca(iniziale: q),
              ),
              _Disposizione(contenuto: contenuto, laterale: const _Laterale()),
            ],
          ),
        ),
      ],
    );
  }
}

/* ---- una sezione ---------------------------------------------------------------------------------------------------- */

/// `.cards-grid`: sei colonne, quattro fino a 1000 px, tre fino a 760, due fino a 430.
int colonneCarte(double w) => w.stretto ? 2 : (w.telefono ? 3 : (w.medio ? 4 : 6));

/// Una sezione del diario (`/blog/sezione/<slug>`).
class BlogSezione extends ConsumerWidget {
  /// La sezione [slug].
  const BlogSezione({super.key, required this.slug, required this.parametri});

  /// Lo slug.
  final String slug;

  /// I parametri della query (`page`).
  final Map<String, String> parametri;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final pagina = _pagina(parametri);
    final per = perPaginaDa(parametri);
    final sezione = ref.watch(sezioneBlogProvider(slug));
    final elenco = ref
        .watch(elencoArticoliProvider(_query({'sezione': slug, 'pagina': pagina, 'per_pagina': per})))
        .value;
    final w = MediaQuery.sizeOf(context).width;

    if (sezione.hasError && !sezione.hasValue) {
      return Pagina(sezioni: [FasciaStretta(child: Avviso(t.blog_vuoto, sopra: 0))]);
    }
    final d = sezione.value;
    if (d == null) return const Pagina(sezioni: [StatoFascia()]);
    final lista = elenco?.articoli ?? const <ArticoloBreve>[];
    final carte = d.tipo == 'carte'
        ? [for (final e in d.elementi) Carta.fromJson(Map<String, dynamic>.from(e))]
        : const <Carta>[];
    final stese = d.stese;

    // A tutta larghezza (sopra gli articoli e le sezioni di lato): le sotto-sezioni come riquadri con immagine, le
    // carte in una griglia ampia, le stese come schede ricche.
    final catalogo = <Widget>[
      if (d.figli.isNotEmpty) ...[
        Semantics(header: true, child: Eyebrow(t.blog_sottosezioni)),
        _RiquadriSezioni(nodi: d.figli),
      ],
      if (d.tipo == 'carte' && carte.isNotEmpty) ...[
        Padding(
          padding: EdgeInsets.only(top: d.figli.isEmpty ? 0 : 16),
          child: Semantics(header: true, child: Eyebrow(t.blog_carte_sezione)),
        ),
        Griglia(
          colonne: colonneCarte(w),
          spazioColonne: 16,
          spazioRighe: 8,
          allunga: false,
          children: [for (final c in carte) _TesseraCarta(carta: c, lingua: lingua)],
        ),
      ],
      if (stese.isNotEmpty) ...[
        Padding(
          padding: EdgeInsets.only(top: d.figli.isEmpty ? 0 : 16),
          child: Semantics(header: true, child: Eyebrow(t.blog_stese_sezione)),
        ),
        _GrigliaStese(stese: stese),
      ],
    ];

    final contenuto = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (lista.isNotEmpty) ...[
          Semantics(header: true, child: Eyebrow(t.blog_articoli)),
          GrigliaDiario(
            children: [for (final (i, a) in lista.indexed) TesseraDiario(a: a, indice: i)],
          ),
          PaginatoreBlog(
            pagina: pagina,
            pagine: elenco!.pagine,
            totale: elenco.totale,
            per: per,
            base: R.blogSezione(slug),
          ),
        ],
        if (pagina == 1) _SceltiACaso(contesto: _query({'sezione': slug, 'recenti': _recentiNove(per), 'scelti': 10})),
        if (elenco != null && lista.isEmpty && d.figli.isEmpty && d.tipo == 'articoli') Avviso(t.blog_vuoto, sopra: 0),
        const _Ponte(),
      ],
    );

    return Pagina(
      sezioni: [
        _Apertura(
          children: [
            _Briciole(
              voci: [
                (testo: t.blog_eyebrow, href: R.blog),
                for (final x in d.briciole.where((x) => x.slug != d.slug)) (testo: x.nome, href: R.blogSezione(x.slug)),
              ],
            ),
            _titoloApertura(context, d.nome),
            if ((d.descrizione ?? '').isNotEmpty) IntroSezione(d.descrizione!),
          ],
        ),
        FasciaStretta(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (catalogo.isNotEmpty) ...[...catalogo, const SizedBox(height: 19.2)],
              _Disposizione(
                contenuto: contenuto,
                laterale: _Laterale(corrente: slug),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Le colonne di una griglia di schede larghe almeno [minima] px (`repeat(auto-fill, minmax(…, 1fr))`), al più
/// [massimo].
int _colonne(double larghezza, double minima, {double spazio = 17.6, int massimo = 3}) =>
    ((larghezza + spazio) / (minima + spazio)).floor().clamp(1, massimo);

/// I conteggi di una sezione: articoli, e carte e stese del ramo se ce ne sono (`12 articles · 22 cards`); «0 articoli»
/// solo se non c'è altro da contare.
String _conteggi(AppLocalizations t, NodoSezione n) {
  final carte = n.nCarte > 0 ? n.nCarte : (n.tipo == 'carte' ? (n.nElementi ?? 0) : 0);
  final stese = n.nStese > 0 ? n.nStese : (n.tipo == 'stese' ? (n.nElementi ?? 0) : 0);
  return [
    if (n.nArticoli > 0 || carte + stese == 0) t.blog_conta_articoli(n.nArticoli),
    if (carte > 0) t.blog_conta_carte(carte),
    if (stese > 0) t.blog_conta_stese(stese),
  ].join(' · ');
}

/// Un'immagine del diario (sezione, stesa) da un percorso dell'API; se manca o non si carica, [riserva].
class _ImmagineDiario extends ConsumerWidget {
  const _ImmagineDiario({required this.immagine, required this.riserva});

  final ImmagineBlog? immagine;
  final Widget riserva;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final percorso = immagine?.perTessera;
    if (percorso == null) return riserva;
    final alt = (immagine?.alt ?? '').trim();
    return Image(
      image: ref.watch(immagineMediaProvider)(percorso),
      fit: BoxFit.cover,
      semanticLabel: alt.isEmpty ? null : alt,
      excludeFromSemantics: alt.isEmpty,
      errorBuilder: (context, e, s) => riserva,
    );
  }
}

/// Il fondo di un riquadro senza immagine: prugna, con il segno del tipo in ottone.
class _FondoSegno extends StatelessWidget {
  const _FondoSegno({required this.segno});

  final String segno;

  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: const BoxDecoration(
      gradient: LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Token.plumDeep, Color(0xFF3C1846)],
      ),
    ),
    child: Center(
      child: ExcludeSemantics(
        child: Text(segno, style: Stile.serif(40, colore: Token.brassPale)),
      ),
    ),
  );
}

/// Le sotto-sezioni di una sezione come riquadri (v9.4): una colonna sul telefono, fino a tre più largo.
class _RiquadriSezioni extends StatelessWidget {
  const _RiquadriSezioni({required this.nodi});

  final List<NodoSezione> nodi;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, v) => Griglia(
      colonne: _colonne(v.maxWidth, 280),
      spazioColonne: 17.6,
      spazioRighe: 17.6,
      allunga: false,
      children: [for (final n in nodi) _RiquadroSezione(nodo: n)],
    ),
  );
}

/// Il riquadro di una sotto-sezione: l'immagine (o il segno del tipo), il nome, la descrizione, i conteggi; sotto, le
/// sue sezioni (per i contenitori come «By suit» e «By number») e 3 articoli del ramo scelti per la giornata.
class _RiquadroSezione extends StatelessWidget {
  const _RiquadroSezione({required this.nodo});

  final NodoSezione nodo;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final n = nodo;
    final segno = switch (n.tipo) {
      'stese' => '▦',
      'contenitore' => '✶',
      _ => '✦',
    };
    final testa = Premibile(
      alTocco: () => vai(context, R.blogSezione(n.slug)),
      collegamento: true,
      costruisci: (context, premuto) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AspectRatio(
            aspectRatio: 16 / 9,
            child: Stack(
              fit: StackFit.expand,
              children: [
                _ImmagineDiario(
                  immagine: n.immagine,
                  riserva: _FondoSegno(segno: segno),
                ),
                if (premuto) const ColoredBox(color: Color(0x1F201026)),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12.8, 16, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Semantics(
                  header: true,
                  child: Text(
                    n.nome,
                    style: Stile.serif(20.8, altezza: 1.25, colore: premuto ? Token.plum : Token.ink),
                  ),
                ),
                if ((n.descrizione ?? '').isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 4.8),
                    child: Paragrafo(n.descrizione!, style: Stile.sans(14.4, colore: Token.inkSoft, altezza: 1.5)),
                  ),
                Padding(
                  padding: const EdgeInsets.only(top: 6.4, bottom: 4.8),
                  child: Text(_conteggi(t, n), style: stilePiccolo()),
                ),
              ],
            ),
          ),
        ],
      ),
    );
    // `.sezioni-box`: la riga d'ottone in alto, sopra l'immagine (il riempimento lascia vedere il bordo).
    return Container(
      padding: const EdgeInsets.fromLTRB(1, 3, 1, 1),
      decoration: const BoxDecoration(
        color: Token.paperLight,
        border: Border(
          top: BorderSide(color: Token.brass, width: 3),
          left: BorderSide(color: Token.line),
          right: BorderSide(color: Token.line),
          bottom: BorderSide(color: Token.line),
        ),
        boxShadow: [BoxShadow(color: Color(0x0F3C1846), offset: Offset(0, 10), blurRadius: 24)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          testa,
          if (n.figli.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 4, 16, 0),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  for (final f in n.figli)
                    _Alto48(child: Pillola(f.nome, alTocco: () => vai(context, R.blogSezione(f.slug)))),
                ],
              ),
            ),
          if (n.articoli.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  for (final a in n.articoli.take(3))
                    DecoratedBox(
                      decoration: const BoxDecoration(
                        border: Border(top: BorderSide(color: Token.line)),
                      ),
                      child: _VoceArticolo(a: a),
                    ),
                ],
              ),
            ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }
}

/// Un articolo in un riquadro di sezione: il titolo, alto almeno 48 px, che porta all'articolo.
class _VoceArticolo extends StatelessWidget {
  const _VoceArticolo({required this.a});

  final ArticoloBreve a;

  @override
  Widget build(BuildContext context) => Premibile(
    alTocco: () => vai(context, R.articolo(a.slug)),
    collegamento: true,
    costruisci: (context, premuto) => ConstrainedBox(
      constraints: const BoxConstraints(minHeight: 48),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ExcludeSemantics(
              child: Text('→ ', style: Stile.sans(15.2, colore: Token.brass, altezza: 1.5)),
            ),
            Expanded(
              child: Text(
                a.titolo,
                style: Stile.sans(15.2, colore: premuto ? Token.verdigris : Token.plum, altezza: 1.5),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

/// Le stese di una sezione «stese» come schede ricche (v9.4): una colonna sul telefono, fino a tre più largo.
class _GrigliaStese extends StatelessWidget {
  const _GrigliaStese({required this.stese});

  final List<StesaSezione> stese;

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, v) => Griglia(
      colonne: _colonne(v.maxWidth, 290),
      spazioColonne: 17.6,
      spazioRighe: 17.6,
      allunga: false,
      children: [for (final s in stese) _SchedaStesa(s: s)],
    ),
  );
}

/// La scheda di una stesa: l'illustrazione con lo schema sul tavolo in un angolo (o lo schema solo, sul fondo prugna,
/// se l'illustrazione non c'è ancora), la tradizione e il numero di carte, il titolo, l'intro breve e «inizia una
/// lettura con questa stesa».
class _SchedaStesa extends ConsumerWidget {
  const _SchedaStesa({required this.s});

  final StesaSezione s;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final stesa = s.comeStesa();
    final nome = nomeStesa(stesa, lingua);
    final tradizione = s.tradizioneIn(lingua);
    final intro = s.descrizioneBreve.isNotEmpty ? s.descrizioneBreve : s.descrizione;
    final schema = DecoratedBox(
      decoration: BoxDecoration(
        color: Token.plumDeep,
        border: Border.all(color: const Color(0x8CD6B66D)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(6.4),
        child: Semantics(
          image: true,
          label: t.stese_stesa_diagramma,
          child: MiniaturaStesa(stesa: stesa),
        ),
      ),
    );
    final illustrazione = s.immagine?.perTessera != null;
    final testa = Premibile(
      alTocco: () => vai(context, R.stesa(s.slug ?? s.id)),
      collegamento: true,
      costruisci: (context, premuto) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AspectRatio(
            aspectRatio: 16 / 10,
            child: Stack(
              fit: StackFit.expand,
              children: [
                const ColoredBox(color: Token.plumDeep),
                if (illustrazione)
                  _ImmagineDiario(immagine: s.immagine, riserva: const SizedBox.shrink())
                else
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                    child: Center(child: MiniaturaStesa(stesa: stesa)),
                  ),
                if (illustrazione)
                  Align(
                    alignment: AlignmentDirectional.bottomEnd,
                    child: Padding(
                      padding: const EdgeInsets.all(9.6),
                      child: FractionallySizedBox(widthFactor: .42, child: schema),
                    ),
                  ),
                if (premuto) const ColoredBox(color: Color(0x1F201026)),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12.8, 16, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  [?tradizione, t.lettura_n_carte(s.carte)].join(' · ').toUpperCase(),
                  // Verderame come le eyebrow (l'ottone sul fondo chiaro non arriva a 4,5:1).
                  style: Stile.sans(11.2, peso: FontWeight.w700, em: .08, colore: Token.verdigris, altezza: 1.6),
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Semantics(
                    header: true,
                    child: Text(
                      nome,
                      style: Stile.serif(20.8, altezza: 1.25, colore: premuto ? Token.plum : Token.ink),
                    ),
                  ),
                ),
                if (intro.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 6.4),
                    child: Paragrafo(intro, style: Stile.sans(14.4, colore: Token.inkSoft, altezza: 1.5)),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
    return Container(
      padding: const EdgeInsets.all(1),
      decoration: BoxDecoration(
        color: Token.paperLight,
        border: Border.all(color: Token.line),
        boxShadow: const [BoxShadow(color: Color(0x0F3C1846), offset: Offset(0, 10), blurRadius: 24)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          testa,
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            child: _Alto48(
              child: Bottone(
                t.stese_stesa_cta,
                href: '${R.leggi}?spread=${Uri.encodeQueryComponent(s.id)}&source=journal',
                variante: Variante.ottone,
                pieno: true,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// L'elenco completo, a pagine, degli articoli su una carta o una stesa (v9.4, `GET /blog/posts?carta=…|stesa=…`),
/// per le loro pagine: sotto i nove articoli, con lo stesso navigatore del diario. Niente se non ce ne sono.
class ArticoliSu extends ConsumerWidget {
  /// Gli articoli su [tipo] (`carta` o `stesa`) [id], chiamato [nome], nella pagina [base] coi [parametri] (`page`,
  /// `per`).
  const ArticoliSu({
    super.key,
    required this.tipo,
    required this.id,
    required this.nome,
    required this.base,
    this.parametri = const {},
  });

  /// `carta` o `stesa`.
  final String tipo;

  /// L'id canonico.
  final String id;

  /// Il nome nella lingua dell'interfaccia.
  final String nome;

  /// L'indirizzo della pagina (per i collegamenti alle altre pagine dell'elenco).
  final String base;

  /// I parametri della query.
  final Map<String, String> parametri;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final pagina = _pagina(parametri);
    final per = perPaginaDa(parametri);
    final elenco = ref.watch(articoliSuProvider((tipo: tipo, id: id, pagina: pagina, per: per))).value;
    if (elenco == null || (elenco.articoli.isEmpty && pagina == 1)) return const SizedBox.shrink();
    return Fascia(
      compatta: true,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Eyebrow(t.blog_articoli),
          Padding(padding: const EdgeInsets.only(bottom: 14.4), child: TitoloSezione(t.blog_articoli_su(nome))),
          if (elenco.articoli.isEmpty) Avviso(t.blog_vuoto, sopra: 0),
          GrigliaDiario(
            children: [for (final (i, a) in elenco.articoli.indexed) TesseraDiario(a: a, indice: i)],
          ),
          PaginatoreBlog(pagina: pagina, pagine: elenco.pagine, totale: elenco.totale, per: per, base: base),
        ],
      ),
    );
  }
}

/// `.card-tile`: la carta e il suo nome.
class _TesseraCarta extends StatelessWidget {
  const _TesseraCarta({required this.carta, required this.lingua});

  final Carta carta;
  final String lingua;

  @override
  Widget build(BuildContext context) {
    final nome = carta.nomeIn(lingua);
    return Premibile(
      alTocco: () => vai(context, R.carta(carta.slug ?? carta.id)),
      collegamento: true,
      etichetta: nome,
      costruisci: (context, premuto) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            decoration: BoxDecoration(
              border: Border.all(color: premuto ? Token.brass : const Color(0x00000000), width: 2),
              boxShadow: const [BoxShadow(color: Color(0x21201026), offset: Offset(0, 10), blurRadius: 20)],
            ),
            child: ImmagineCarta(carta.id, mazzo: ''),
          ),
          Padding(
            padding: const EdgeInsets.only(top: 9.6),
            child: Text(nome, style: Stile.serif(15.2, altezza: 1.6, colore: Token.ink)),
          ),
        ],
      ),
    );
  }
}

/* ---- un'etichetta ------------------------------------------------------------------------------------------------- */

/// Gli articoli con un'etichetta (`/blog/tag/<slug>`).
class BlogTag extends ConsumerWidget {
  /// L'etichetta [slug].
  const BlogTag({super.key, required this.slug, required this.parametri});

  /// Lo slug.
  final String slug;

  /// I parametri della query (`page`).
  final Map<String, String> parametri;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final pagina = _pagina(parametri);
    final per = perPaginaDa(parametri);
    final tag = ref.watch(etichetteBlogProvider).value;
    final elenco = ref.watch(elencoArticoliProvider(_query({'tag': slug, 'pagina': pagina, 'per_pagina': per}))).value;
    final nome = tag?.where((e) => e.slug == slug).firstOrNull?.nome ?? slug;
    final lista = elenco?.articoli ?? const <ArticoloBreve>[];
    return Pagina(
      sezioni: [
        _Apertura(
          children: [
            _Briciole(voci: [(testo: t.blog_eyebrow, href: R.blog)]),
            Eyebrow(t.blog_etichette),
            _titoloApertura(context, nome),
          ],
        ),
        FasciaStretta(
          child: _Disposizione(
            contenuto: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (elenco != null && lista.isEmpty) Avviso(t.blog_vuoto, sopra: 0),
                GrigliaDiario(
                  children: [for (final (i, a) in lista.indexed) TesseraDiario(a: a, indice: i)],
                ),
                if (elenco != null)
                  PaginatoreBlog(
                    pagina: pagina,
                    pagine: elenco.pagine,
                    totale: elenco.totale,
                    per: per,
                    base: R.blogTag(slug),
                  ),
                if (pagina == 1)
                  _SceltiACaso(contesto: _query({'tag': slug, 'recenti': _recentiNove(per), 'scelti': 10})),
                const _Ponte(),
              ],
            ),
            laterale: const _Laterale(),
          ),
        ),
      ],
    );
  }
}

/* ---- un articolo -------------------------------------------------------------------------------------------------- */

List<String> _forme(String id, Map<String, String> slugs) => [id, ...slugs.values];

/// I riferimenti di un articolo per le scorciatoie del testo.
Riferimenti riferimentiDi(ArticoloBlog x) => Riferimenti(
  carte: {
    for (final c in x.collegamenti.carte)
      for (final k in _forme(c.id, c.slugs)) k: c.nome,
  },
  stese: {
    for (final s in x.collegamenti.stese)
      for (final k in _forme(s.id, s.slugs)) k: s.nome,
  },
  articoli: {for (final y in x.collegamenti.articoli) y.slug: y.titolo},
  idCarte: {
    for (final c in x.collegamenti.carte)
      for (final k in _forme(c.id, c.slugs)) k: c.id,
  },
);

/// Un articolo del diario (`/blog/<slug>`).
class Articolo extends ConsumerWidget {
  /// L'articolo [slug].
  const Articolo({super.key, required this.slug});

  /// Lo slug.
  final String slug;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final a = ref.watch(articoloBlogProvider(slug));
    if (a.hasError && !a.hasValue) {
      return Pagina(
        sezioni: [
          FasciaStretta(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                IntroSezione(t.blog_non_trovato),
                const SizedBox(height: 16),
                Bottone(t.blog_eyebrow, href: R.blog, variante: Variante.quieto),
              ],
            ),
          ),
        ],
      );
    }
    final x = a.value;
    if (x == null) return const Pagina(sezioni: [StatoFascia()]);
    final w = MediaQuery.sizeOf(context).width;
    final piccolo = stilePiccolo();
    final meta = [
      if (x.autore?.nome.isNotEmpty ?? false) t.blog_di(x.autore!.nome),
      if (x.pubblicatoIl != null) dataLunga(x.pubblicatoIl, lingua, utc: true),
      t.blog_min(x.tempoLettura),
      if (x.aggiornatoIl != null &&
          x.pubblicatoIl != null &&
          x.aggiornatoIl!.substring(0, 10) != x.pubblicatoIl!.substring(0, 10))
        t.blog_aggiornato(dataLunga(x.aggiornatoIl, lingua, utc: true)),
    ].join(' · ');
    final immagine = x.immagine?.url;
    final url = '${Config.sitoPubblico}${pubblico(linguaPubblica(x.lang), R.articolo(x.slug))}';
    final anno = x.pubblicatoIl ?? x.aggiornatoIl ?? '';

    Future<void> condividi() async {
      ref.read(lanternaProvider).traccia('share_started', {'cosa': 'articolo'});
      try {
        await SharePlus.instance.share(ShareParams(uri: Uri.parse(url), title: x.titolo, subject: x.titolo));
      } on Object catch (e) {
        debugPrint('Condivisione non riuscita: $e');
      }
    }

    return Pagina(
      sezioni: [
        _Apertura(
          children: [
            _Briciole(
              voci: [
                (testo: t.blog_eyebrow, href: R.blog),
                for (final y in x.briciole) (testo: y.nome, href: R.blogSezione(y.slug)),
              ],
            ),
            _titoloApertura(context, x.titolo, maxCh: 22),
            if ((x.sottotitolo ?? '').isNotEmpty) IntroSezione(x.sottotitolo!),
            Padding(
              padding: EdgeInsets.only(top: w.telefono ? 9.6 : 0),
              child: Text(meta, style: piccolo),
            ),
          ],
        ),
        FasciaStretta(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (immagine != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 11.2),
                  child: Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 960),
                      child: AspectRatio(
                        aspectRatio: (x.immagine?.larghezza ?? 1200) / (x.immagine?.altezza ?? 675),
                        child: Image(
                          image: ref.watch(immagineMediaProvider)(immagine),
                          fit: BoxFit.cover,
                          semanticLabel: (x.immagine?.alt ?? '').isEmpty ? null : x.immagine!.alt,
                          excludeFromSemantics: (x.immagine?.alt ?? '').isEmpty,
                          errorBuilder: (context, e, s) => const SizedBox.shrink(),
                        ),
                      ),
                    ),
                  ),
                ),
              TestoArticolo(testo: x.testo, riferimenti: riferimentiDi(x)),
              if (x.faq.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 13.6),
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      maxWidth: larghezzaCh(Stile.corpo, MediaQuery.textScalerOf(context)) * 68,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Eyebrow(t.blog_domande),
                        Container(
                          decoration: const BoxDecoration(
                            border: Border(top: BorderSide(color: Token.line)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [for (final q in x.faq) _Domanda(domanda: q.domanda, risposta: q.risposta)],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              if (x.collegamenti.carte.isNotEmpty || x.collegamenti.stese.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 13.6),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Eyebrow(t.blog_si_parla_di),
                      Pillole(
                        children: [
                          for (final c in x.collegamenti.carte)
                            Pillola('✦ ${c.nome}', alTocco: () => vai(context, R.carta(c.id))),
                          for (final s in x.collegamenti.stese)
                            Pillola('▦ ${s.nome}', alTocco: () => vai(context, R.stesa(s.id))),
                        ],
                      ),
                    ],
                  ),
                ),
              if (x.tags.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Semantics(
                    container: true,
                    label: t.blog_etichette,
                    child: Pillole(
                      children: [
                        for (final e in x.tags) Pillola('#${e.nome}', alTocco: () => vai(context, R.blogTag(e.slug))),
                      ],
                    ),
                  ),
                ),
              Padding(
                padding: const EdgeInsets.only(top: 8.8),
                child: Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: Bottone(
                    t.blog_condividi,
                    variante: Variante.quieto,
                    piccolo: true,
                    alTocco: () => unawaited(condividi()),
                  ),
                ),
              ),
              const _Ponte(),
              if (x.correlati.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 16.8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Eyebrow(t.blog_correlati),
                      GrigliaDiario(
                        children: [for (final (i, y) in x.correlati.take(3).indexed) TesseraDiario(a: y, indice: i)],
                      ),
                    ],
                  ),
                ),
              if (x.precedente != null || x.successivo != null)
                Padding(
                  padding: const EdgeInsets.only(top: 11.2),
                  child: Semantics(
                    container: true,
                    label: t.blog_articoli,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: x.precedente == null
                              ? const SizedBox.shrink()
                              : Collegamento('← ${x.precedente!.titolo}', href: R.articolo(x.precedente!.slug)),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: x.successivo == null
                              ? const SizedBox.shrink()
                              : Align(
                                  alignment: AlignmentDirectional.centerEnd,
                                  child: Collegamento(
                                    '${x.successivo!.titolo} →',
                                    href: R.articolo(x.successivo!.slug),
                                  ),
                                ),
                        ),
                      ],
                    ),
                  ),
                ),
              Container(
                margin: const EdgeInsets.only(top: 11.2),
                padding: const EdgeInsets.only(top: 8),
                decoration: const BoxDecoration(
                  border: Border(top: BorderSide(color: Token.line)),
                ),
                child: Paragrafo(t.blog_copyright(anno.length >= 4 ? anno.substring(0, 4) : anno), style: piccolo),
              ),
            ],
          ),
        ),
        DiarioNove(contesto: _query({'articolo': x.slug}), sceltiPrima: true),
      ],
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
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final stile = Stile.serif(telefono ? 16 : 17.28);
    return Container(
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Token.line)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Semantics(
            expanded: _aperta,
            child: Premibile(
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

/* ---- Esplora ------------------------------------------------------------------------------------------------------- */

/// «Esplora» (`/explore`): le sei porte del grafo (diario, carte, stese, mazzi, carta del giorno, le proprie carte) e
/// il diario.
class Esplora extends StatelessWidget {
  /// Esplora.
  const Esplora({super.key});

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    const dove = {
      'diario': R.blog,
      'carte': R.carte,
      'stese': R.stese,
      'mazzi': R.mazzi,
      'giorno': R.giorno,
      'fisica': R.fisica,
    };
    return Pagina(
      sezioni: [
        Sottotitolo(
          eyebrow: t.blog_esplora_eyebrow,
          titolo: t.blog_esplora_titolo,
          intro: t.blog_esplora_intro,
          compatta: true,
        ),
        FasciaStretta(
          // `.difference-grid.even` con `repeat(auto-fit, minmax(240px, 1fr))`.
          child: LayoutBuilder(
            builder: (context, v) => Griglia.righe(
              colonne: math.max(1, ((v.maxWidth - 2 + 1) / 241).floor()),
              linea: Token.line,
              children: [
                for (final e in t.blogEsploraVoci)
                  _Porta(simbolo: e.simbolo, titolo: e.titolo, testo: e.testo, href: dove[e.chiave] ?? R.blog),
              ],
            ),
          ),
        ),
        DiarioNove(eyebrow: t.blog_esplora_ultimi),
      ],
    );
  }
}

/// `a.difference` di una griglia `.even`: il simbolo d'ottone, il titolo, la riga sotto.
class _Porta extends StatelessWidget {
  const _Porta({required this.simbolo, required this.titolo, required this.testo, required this.href});

  final String simbolo;
  final String titolo;
  final String testo;
  final String href;

  @override
  Widget build(BuildContext context) {
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    return Premibile(
      alTocco: () => vai(context, href),
      collegamento: true,
      costruisci: (context, premuto) => Container(
        color: premuto ? const Color(0xFFFFF3DC) : Colori.differenza,
        padding: EdgeInsets.symmetric(horizontal: telefono ? 17.6 : 22.4, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.only(bottom: 8.8),
              child: ExcludeSemantics(
                child: Text(
                  simbolo,
                  textAlign: telefono ? TextAlign.center : TextAlign.start,
                  style: Stile.serif(27.2, colore: Token.brass),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(titolo, style: Stile.serif(telefono ? 18.4 : 20.8, colore: Token.ink)),
            ),
            Paragrafo(testo, style: Stile.sans(13.92, colore: Token.inkSoft, altezza: 1.6)),
          ],
        ),
      ),
    );
  }
}
