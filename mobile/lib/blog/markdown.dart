/// Il testo di un articolo del diario (`frontend/v2/componenti/blog-markdown.tsx`, `blog.module.css`): lo stesso Markdown
/// sicuro del sito, letto col pacchetto ufficiale di Dart (`package:markdown`, il parser del team di Dart: CommonMark e
/// GitHub Flavored Markdown, come `remark-gfm` del sito) e disegnato qui con le regole del CSS, senza HTML né webview.
///
/// - Niente HTML eseguito (resta testo), immagini solo relative o https (`/blog/media/…` dall'API), il titolo
///   dell'immagine diventa la didascalia (`.md-figura`).
/// - Le scorciatoie `[[carta:…]]`, `[[stesa:…]]`, `[[articolo:…]]` (anche `card`, `spread`, `post`): su una riga da sola
///   una scheda verso la pagina, in mezzo al testo un collegamento col nome; se il nome non c'è, spariscono.
/// - Le direttive del testo ricco (`frontend/v2/lib/direttive-blog.ts`): `:testo[…]{colore=… dimensione=…}` (anche
///   `:text[…]{color=… size=…}`) e `:sottolineato[…]` (`:underline[…]`), solo con la tavolozza della v2; una direttiva
///   sconosciuta resta testo com'era scritta.
/// - I video `[[video:youtube|vimeo:id]]`: nel sito un riquadro incorporato; nell'app una tessera che apre il video
///   fuori (`apriFuori`), perché l'app non incorpora pagine web.
/// - Collegamenti interni (anche coi nomi della v1 o in italiano) con `vai()`, esterni nel browser.
library;

import 'dart:async';

import 'package:flutter/gestures.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:markdown/markdown.dart' as md;

import '../cassa/pagamento.dart' show apriFuori;
import '../componenti/carta.dart';
import '../componenti/diario.dart' show immagineMediaProvider;
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../config.dart';
import '../l10n/testi.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// I nomi delle carte, stese e articoli citati, per le scorciatoie (`Riferimenti` del sito).
class Riferimenti {
  /// I riferimenti.
  const Riferimenti({this.carte = const {}, this.stese = const {}, this.articoli = const {}, this.idCarte = const {}});

  /// Id o slug della carta → nome.
  final Map<String, String> carte;

  /// Id o slug della stesa → nome.
  final Map<String, String> stese;

  /// Slug dell'articolo → titolo.
  final Map<String, String> articoli;

  /// Id o slug della carta → id (l'immagine).
  final Map<String, String> idCarte;
}

/// Un tipo di scorciatoia.
enum TipoRiferimento {
  /// Una carta.
  carta,

  /// Una stesa.
  stesa,

  /// Un articolo.
  articolo,
}

const Map<String, TipoRiferimento> _canonico = {
  'carta': TipoRiferimento.carta,
  'card': TipoRiferimento.carta,
  'stesa': TipoRiferimento.stesa,
  'spread': TipoRiferimento.stesa,
  'articolo': TipoRiferimento.articolo,
  'post': TipoRiferimento.articolo,
};

final RegExp _blocco = RegExp(r'^[ \t]*\[\[(carta|card|stesa|spread|articolo|post):([a-z0-9-]+)\]\][ \t]*$');
final RegExp _inLinea = RegExp(r'\[\[(carta|card|stesa|spread|articolo|post):([a-z0-9-]+)\]\]');
final RegExp _bloccoVideo = RegExp(r'^[ \t]*\[\[video:(youtube|vimeo):([A-Za-z0-9_-]{6,20})\]\][ \t]*$');

String _indirizzo(TipoRiferimento tipo, String id) => switch (tipo) {
  TipoRiferimento.carta => R.carta(id),
  TipoRiferimento.stesa => R.stesa(id),
  TipoRiferimento.articolo => R.articolo(id),
};

String? _nomeDi(TipoRiferimento tipo, String id, Riferimenti rif) => switch (tipo) {
  TipoRiferimento.carta => rif.carte[id],
  TipoRiferimento.stesa => rif.stese[id],
  TipoRiferimento.articolo => rif.articoli[id],
};

/// Le scorciatoie in mezzo al testo → collegamenti Markdown col nome (o niente, se il nome non c'è).
String inLinea(String testo, Riferimenti rif) => testo.replaceAllMapped(_inLinea, (m) {
  final tipo = _canonico[m[1]]!;
  final nome = _nomeDi(tipo, m[2]!, rif);
  return nome == null ? '' : '[${nome.replaceAll(RegExp(r'[\[\]]'), '')}](${_indirizzo(tipo, m[2]!)})';
});

/// Un pezzo del testo: Markdown, una scheda, un video.
sealed class Pezzo {
  const Pezzo();
}

/// Un tratto di Markdown.
class PezzoMd extends Pezzo {
  /// Il testo.
  const PezzoMd(this.md);

  /// Il Markdown.
  final String md;
}

/// Una scheda verso una carta, una stesa o un articolo.
class PezzoScheda extends Pezzo {
  /// La scheda.
  const PezzoScheda({required this.tipo, required this.id, required this.nome, this.idCarta});

  /// Il tipo.
  final TipoRiferimento tipo;

  /// L'id o lo slug scritto.
  final String id;

  /// Il nome.
  final String nome;

  /// L'id della carta (l'immagine).
  final String? idCarta;
}

/// Un video.
class PezzoVideo extends Pezzo {
  /// Il video.
  const PezzoVideo({required this.fonte, required this.id});

  /// `youtube` o `vimeo`.
  final String fonte;

  /// L'identificativo.
  final String id;

  /// Dove si guarda (fuori dall'app).
  String get url => fonte == 'vimeo' ? 'https://vimeo.com/$id' : 'https://www.youtube.com/watch?v=$id';

  /// Il nome della piattaforma.
  String get nome => fonte == 'vimeo' ? 'Vimeo' : 'YouTube';
}

/// Il testo diviso in pezzi, riga per riga, come il sito.
List<Pezzo> dividi(String testo, Riferimenti rif) {
  final pezzi = <Pezzo>[];
  var corrente = <String>[];
  void chiudi() {
    if (corrente.isNotEmpty) pezzi.add(PezzoMd(corrente.join('\n')));
    corrente = [];
  }

  for (final riga in testo.split('\n')) {
    final v = _bloccoVideo.firstMatch(riga);
    if (v != null) {
      chiudi();
      pezzi.add(PezzoVideo(fonte: v[1]!, id: v[2]!));
      continue;
    }
    final m = _blocco.firstMatch(riga);
    final tipo = m == null ? null : _canonico[m[1]];
    final nome = tipo == null ? null : _nomeDi(tipo, m![2]!, rif);
    if (tipo != null && nome != null) {
      chiudi();
      pezzi.add(PezzoScheda(tipo: tipo, id: m![2]!, nome: nome, idCarta: rif.idCarte[m[2]!]));
    } else {
      corrente.add(riga);
    }
  }
  chiudi();
  return pezzi;
}

/* ---- le direttive del testo ricco ---------------------------------------------------------------------------------- */

const Map<String, String> _colori = {
  'ottone': 'ottone',
  'brass': 'ottone',
  'prugna': 'prugna',
  'plum': 'prugna',
  'verderame': 'verderame',
  'verdigris': 'verderame',
  'tenue': 'tenue',
  'muted': 'tenue',
};

const Map<String, String> _dimensioni = {
  'piccolo': 'piccolo',
  'small': 'piccolo',
  'grande': 'grande',
  'large': 'grande',
  'titolo': 'titolo',
  'title': 'titolo',
};

/// Gli attributi di una direttiva: `colore=ottone dimensione="titolo"`.
Map<String, String> attributiDirettiva(String? testo) {
  final a = <String, String>{};
  for (final m in RegExp(r'''([\w-]+)\s*=\s*("[^"]*"|'[^']*'|[^\s"']+)''').allMatches(testo ?? '')) {
    var v = m[2]!;
    if (v.length >= 2 && (v.startsWith('"') || v.startsWith("'"))) v = v.substring(1, v.length - 1);
    a[m[1]!] = v;
  }
  return a;
}

/// `:testo[…]{…}`, `:sottolineato[…]` (e i nomi inglesi): un `span` con le classi della tavolozza, o un `u`.
class SintassiDirettiva extends md.InlineSyntax {
  /// La sintassi.
  SintassiDirettiva()
    : super(r':(testo|text|sottolineato|underline)\[([^\]\n]*)\](?:\{([^}\n]*)\})?', startCharacter: 0x3A);

  @override
  bool onMatch(md.InlineParser parser, Match match) {
    final nome = match[1]!;
    final figli = md.InlineParser(match[2]!, parser.document).parse();
    if (nome == 'sottolineato' || nome == 'underline') {
      parser.addNode(md.Element('u', figli));
      return true;
    }
    final a = attributiDirettiva(match[3]);
    final colore = _colori[a['colore'] ?? a['color'] ?? ''];
    final dimensione = _dimensioni[a['dimensione'] ?? a['size'] ?? ''];
    final e = md.Element('span', figli);
    final classi = [if (colore != null) 'md-colore-$colore', if (dimensione != null) 'md-dim-$dimensione'];
    if (classi.isNotEmpty) e.attributes['class'] = classi.join(' ');
    parser.addNode(e);
    return true;
  }
}

/// Il Markdown di un pezzo → i nodi (GFM: tabelle, barrato, collegamenti automatici; più le direttive).
List<md.Node> leggiMarkdown(String testo) {
  final documento = md.Document(
    extensionSet: md.ExtensionSet.gitHubFlavored,
    encodeHtml: false,
    inlineSyntaxes: [SintassiDirettiva()],
  );
  return documento.parseLines(testo.replaceAll('\r\n', '\n').split('\n'));
}

/* ---- il disegno ------------------------------------------------------------------------------------------------- */

/// Lo stile del testo dell'articolo: `.testo { font: 1.06rem/1.8 var(--serif) }`.
TextStyle get stileTestoArticolo => Stile.serif(16.96, altezza: 1.8, colore: Token.ink);

/// Il testo di un articolo.
class TestoArticolo extends ConsumerWidget {
  /// Il [testo] con i suoi [riferimenti].
  const TestoArticolo({super.key, required this.testo, required this.riferimenti});

  /// Il Markdown.
  final String testo;

  /// I nomi delle carte, stese e articoli citati.
  final Riferimenti riferimenti;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scala = MediaQuery.textScalerOf(context);
    final blocchi = <_Blocco>[];
    for (final p in dividi(testo, riferimenti)) {
      switch (p) {
        case PezzoMd(:final md):
          blocchi.addAll(_Disegno(context).blocchi(leggiMarkdown(inLinea(md, riferimenti))));
        case PezzoScheda():
          blocchi.add(_Blocco(_Scheda(p), 25.6, 25.6));
        case PezzoVideo():
          blocchi.add(_Blocco(_Video(p), 25.6, 25.6));
      }
    }
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: larghezzaCh(stileTestoArticolo, scala) * 68),
      child: DefaultTextStyle(
        style: stileTestoArticolo,
        child: _Colonna(blocchi: blocchi, togliPrimo: true),
      ),
    );
  }
}

/// Un blocco coi suoi margini sopra e sotto (che fra due blocchi si fondono: vale il più grande, come nel CSS).
class _Blocco {
  const _Blocco(this.widget, this.sopra, this.sotto);

  final Widget widget;
  final double sopra;
  final double sotto;
}

/// I blocchi uno sotto l'altro coi margini fusi; [togliPrimo] toglie il margine sopra il primo (dentro un riquadro).
class _Colonna extends StatelessWidget {
  const _Colonna({required this.blocchi, this.togliPrimo = false});

  final List<_Blocco> blocchi;
  final bool togliPrimo;

  @override
  Widget build(BuildContext context) {
    final figli = <Widget>[];
    for (var i = 0; i < blocchi.length; i++) {
      final b = blocchi[i];
      final spazio = i == 0
          ? (togliPrimo ? 0.0 : b.sopra)
          : (b.sopra > blocchi[i - 1].sotto ? b.sopra : blocchi[i - 1].sotto);
      if (spazio > 0) figli.add(SizedBox(height: spazio));
      figli.add(b.widget);
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: figli);
  }
}

/// Dai nodi del Markdown ai widget, con gli stili di `blog.module.css`.
class _Disegno {
  _Disegno(this.context);

  final BuildContext context;

  double get _w => MediaQuery.sizeOf(context).width;

  List<_Blocco> blocchi(List<md.Node> nodi, {TextStyle? stile}) {
    final s = stile ?? stileTestoArticolo;
    final fuori = <_Blocco>[];
    for (final n in nodi) {
      if (n is md.Text) {
        if (n.text.trim().isNotEmpty) {
          fuori.add(
            _Blocco(
              _Ricco(
                spans: (_) => [TextSpan(text: n.text)],
                stile: s,
              ),
              0,
              17.6,
            ),
          );
        }
        continue;
      }
      if (n is! md.Element) continue;
      final b = _blocco(n, s);
      if (b != null) fuori.add(b);
    }
    return fuori;
  }

  _Blocco? _blocco(md.Element e, TextStyle s) {
    switch (e.tag) {
      case 'p':
        final figli = e.children ?? const [];
        final sole = figli.where((x) => !(x is md.Text && x.text.trim().isEmpty)).toList();
        // Un'immagine da sola nel paragrafo: un blocco (con la didascalia dal titolo), come `.md-figura`.
        if (sole.length == 1 && sole.first is md.Element && (sole.first as md.Element).tag == 'img') {
          final img = sole.first as md.Element;
          final figura = _Figura(
            src: img.attributes['src'] ?? '',
            alt: img.attributes['alt'] ?? '',
            titolo: img.attributes['title'],
          );
          return _Blocco(figura, 24, 24 + 17.6);
        }
        return _Blocco(_Ricco(spans: (r) => _inline(figli, s, r), stile: s), 0, 17.6);
      case 'h1' || 'h2':
        final stile = Stile.serif(_w.clampVw(23.2, 2.6, 30.4), altezza: 1.25, em: -.02, colore: Token.plum);
        return _Blocco(_Titolo(spans: (r) => _inline(e.children ?? const [], stile, r), stile: stile), 38.4, 12.8);
      case 'h3':
        final stile = Stile.serif(20, altezza: 1.3, colore: Token.plum);
        return _Blocco(_Titolo(spans: (r) => _inline(e.children ?? const [], stile, r), stile: stile), 28.8, 9.6);
      case 'h4' || 'h5' || 'h6':
        final stile = s.copyWith(fontWeight: FontWeight.w700);
        return _Blocco(_Titolo(spans: (r) => _inline(e.children ?? const [], stile, r), stile: stile), 22.6, 22.6);
      case 'ul' || 'ol':
        return _Blocco(_lista(e, s), 16.96, 16.96);
      case 'blockquote':
        final stile = s.copyWith(fontStyle: FontStyle.italic, color: Token.inkSoft);
        return _Blocco(
          Container(
            padding: const EdgeInsets.fromLTRB(19.2, 6.4, 0, 6.4),
            decoration: const BoxDecoration(
              border: Border(left: BorderSide(color: Token.brass, width: 3)),
            ),
            child: DefaultTextStyle(
              style: stile,
              child: _Colonna(blocchi: blocchi(e.children ?? const [], stile: stile), togliPrimo: true),
            ),
          ),
          24,
          24,
        );
      case 'pre':
        return _Blocco(
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Container(
              padding: const EdgeInsets.all(12),
              color: Token.paperDeep,
              child: Text(
                e.textContent,
                style: s.copyWith(fontFamily: 'monospace', fontSize: s.fontSize! * .88, height: 1.5),
              ),
            ),
          ),
          16.96,
          16.96,
        );
      case 'hr':
        return const _Blocco(
          DecoratedBox(
            decoration: BoxDecoration(
              border: Border(top: BorderSide(color: Token.line)),
            ),
            child: SizedBox(width: double.infinity, height: 1),
          ),
          8.5,
          8.5,
        );
      case 'table':
        return _Blocco(_tabella(e), 22.4, 22.4);
      default:
        final figli = e.children;
        if (figli == null || figli.isEmpty) return null;
        return _Blocco(_Ricco(spans: (r) => _inline(figli, s, r), stile: s), 0, 17.6);
    }
  }

  /// `ul`/`ol` (`padding-left: 1.3rem`, `li { margin-bottom: .4rem }`).
  Widget _lista(md.Element e, TextStyle s) {
    final ordinata = e.tag == 'ol';
    final inizio = int.tryParse(e.attributes['start'] ?? '') ?? 1;
    final voci = (e.children ?? const []).whereType<md.Element>().where((x) => x.tag == 'li').toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (final (i, li) in voci.indexed)
          Padding(
            padding: const EdgeInsets.only(bottom: 6.4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 20.8,
                  child: Padding(
                    padding: const EdgeInsets.only(right: 5),
                    child: Text(ordinata ? '${inizio + i}.' : '•', textAlign: TextAlign.end, style: s),
                  ),
                ),
                Expanded(child: _voce(li, s)),
              ],
            ),
          ),
      ],
    );
  }

  /// Una voce d'elenco: testo in linea (elenco stretto) o blocchi (elenco largo, con i paragrafi).
  Widget _voce(md.Element li, TextStyle s) {
    final figli = li.children ?? const [];
    final aBlocchi = figli.any((x) => x is md.Element && const {'p', 'ul', 'ol', 'blockquote', 'pre'}.contains(x.tag));
    if (!aBlocchi) return _Ricco(spans: (r) => _inline(figli, s, r), stile: s);
    final b = blocchi(figli, stile: s);
    // L'ultimo paragrafo di una voce non porta il suo margine sotto (lo dà la voce).
    return _Colonna(
      blocchi: [for (final (i, x) in b.indexed) i == b.length - 1 ? _Blocco(x.widget, x.sopra, 0) : x],
      togliPrimo: true,
    );
  }

  /// `.tabella`: scorre di lato se non ci sta; `font: .92rem/1.5 var(--sans)`, le celle con la riga sotto.
  Widget _tabella(md.Element e) {
    final righe = <md.Element>[];
    void raccogli(md.Element x) {
      for (final c in (x.children ?? const []).whereType<md.Element>()) {
        if (c.tag == 'tr') {
          righe.add(c);
        } else {
          raccogli(c);
        }
      }
    }

    raccogli(e);
    final base = Stile.sans(14.72, altezza: 1.5, colore: Token.ink);
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Table(
        defaultColumnWidth: const IntrinsicColumnWidth(),
        border: const TableBorder(
          horizontalInside: BorderSide(color: Token.line),
          bottom: BorderSide(color: Token.line),
        ),
        children: [
          for (final tr in righe)
            TableRow(
              children: [
                for (final cella in (tr.children ?? const []).whereType<md.Element>())
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 11.2, vertical: 8.8),
                    child: _Ricco(
                      spans: (r) => _inline(
                        cella.children ?? const [],
                        cella.tag == 'th' ? base.copyWith(fontWeight: FontWeight.w700) : base,
                        r,
                      ),
                      stile: cella.tag == 'th' ? base.copyWith(fontWeight: FontWeight.w700) : base,
                    ),
                  ),
              ],
            ),
        ],
      ),
    );
  }

  /// Il testo in linea: grassetto, corsivo, barrato, codice, collegamenti, immagini, le direttive.
  List<InlineSpan> _inline(List<md.Node> nodi, TextStyle s, _Riconoscitori r) {
    final fuori = <InlineSpan>[];
    for (final n in nodi) {
      if (n is md.Text) {
        // Gli a capo morbidi del Markdown sono spazi.
        fuori.add(TextSpan(text: n.text.replaceAll('\n', ' '), style: s));
        continue;
      }
      if (n is! md.Element) continue;
      final figli = n.children ?? const [];
      switch (n.tag) {
        case 'strong':
          fuori.addAll(_inline(figli, s.copyWith(fontWeight: FontWeight.w700), r));
        case 'em':
          fuori.addAll(_inline(figli, s.copyWith(fontStyle: FontStyle.italic), r));
        case 'del':
          fuori.addAll(_inline(figli, s.copyWith(decoration: TextDecoration.lineThrough), r));
        case 'code':
          fuori.add(
            TextSpan(
              text: n.textContent,
              style: s.copyWith(fontFamily: 'monospace', fontSize: s.fontSize! * .88, backgroundColor: Token.paperDeep),
            ),
          );
        case 'br':
          fuori.add(const TextSpan(text: '\n'));
        case 'u':
          // `u { text-decoration-color: var(--brass) }`.
          fuori.addAll(
            _inline(figli, s.copyWith(decoration: TextDecoration.underline, decorationColor: Token.brass), r),
          );
        case 'span':
          fuori.addAll(_inline(figli, _classi(n.attributes['class'], s), r));
        case 'a':
          final href = n.attributes['href'] ?? '';
          final stile = s.copyWith(
            color: Token.plum,
            decoration: TextDecoration.underline,
            decorationColor: Token.brass,
          );
          final tocco = r.nuovo(() => _apri(href));
          fuori.addAll(_inline(figli, stile, r).map((x) => x is TextSpan ? _conTocco(x, tocco) : x));
        case 'img':
          final src = n.attributes['src'] ?? '';
          fuori.add(
            WidgetSpan(
              child: _Figura(src: src, alt: n.attributes['alt'] ?? '', titolo: null, inLinea: true),
            ),
          );
        default:
          fuori.addAll(_inline(figli, s, r));
      }
    }
    return fuori;
  }

  TextSpan _conTocco(TextSpan x, TapGestureRecognizer tocco) => TextSpan(
    text: x.text,
    style: x.style,
    recognizer: tocco,
    children: x.children?.map((c) => c is TextSpan ? _conTocco(c, tocco) : c).toList(),
  );

  /// Le classi della tavolozza (`.md-colore-*`, `.md-dim-*` di v2.css).
  TextStyle _classi(String? classi, TextStyle s) {
    var x = s;
    for (final c in (classi ?? '').split(' ')) {
      x = switch (c) {
        'md-colore-ottone' => x.copyWith(color: const Color(0xFF8A6424)),
        'md-colore-prugna' => x.copyWith(color: Token.plum),
        'md-colore-verderame' => x.copyWith(color: Token.verdigris),
        'md-colore-tenue' => x.copyWith(color: Token.inkSoft),
        'md-dim-piccolo' => x.copyWith(fontSize: x.fontSize! * .875),
        'md-dim-grande' => x.copyWith(fontSize: x.fontSize! * 1.25, height: 1.45),
        'md-dim-titolo' => x.copyWith(fontFamily: 'Libre Baskerville', fontSize: x.fontSize! * 1.6, height: 1.3),
        _ => x,
      };
    }
    return x;
  }

  void _apri(String href) {
    if (href.isEmpty || href.startsWith('#')) return;
    if (href.startsWith('/') && !href.startsWith('//')) {
      vai(context, href);
      return;
    }
    unawaited(apriFuori(href));
  }
}

/// I riconoscitori dei tocchi sui collegamenti di un testo: si creano a ogni disegno e si buttano al successivo.
class _Riconoscitori {
  final List<TapGestureRecognizer> _tutti = [];

  TapGestureRecognizer nuovo(VoidCallback f) {
    final r = TapGestureRecognizer()..onTap = f;
    _tutti.add(r);
    return r;
  }

  void butta() {
    for (final r in _tutti) {
      r.dispose();
    }
    _tutti.clear();
  }
}

/// Un testo composto coi collegamenti toccabili (`text-wrap: pretty` non si può avere con gli span: Flutter va a capo
/// da sé).
class _Ricco extends StatefulWidget {
  const _Ricco({required this.spans, required this.stile});

  final List<InlineSpan> Function(_Riconoscitori r) spans;
  final TextStyle stile;

  @override
  State<_Ricco> createState() => _RiccoState();
}

class _RiccoState extends State<_Ricco> {
  final _Riconoscitori _r = _Riconoscitori();

  @override
  void dispose() {
    _r.butta();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    _r.butta();
    return Text.rich(TextSpan(children: widget.spans(_r)), style: widget.stile);
  }
}

/// Un titolo (`h2`, `h3`): righe bilanciate come nel sito quando è testo semplice.
class _Titolo extends StatelessWidget {
  const _Titolo({required this.spans, required this.stile});

  final List<InlineSpan> Function(_Riconoscitori r) spans;
  final TextStyle stile;

  @override
  Widget build(BuildContext context) => Semantics(
    header: true,
    child: _Ricco(spans: spans, stile: stile),
  );
}

/// L'indirizzo di un'immagine dell'articolo: dall'API (`/blog/media/…`), dal sito (`/…`) o https; altro no.
String? urlImmagine(String src) {
  if (src.startsWith('/blog/media/')) return null; // dall'API, con [immagineMediaProvider]
  if (src.startsWith('/') && !src.startsWith('//')) return '${Config.sitoUrl}$src';
  if (src.startsWith('https://')) return src;
  return '';
}

/// `.md-figura`: l'immagine (larga al più quanto il testo) con la didascalia sotto; o un'immagine dentro una riga.
class _Figura extends ConsumerWidget {
  const _Figura({required this.src, required this.alt, required this.titolo, this.inLinea = false});

  final String src;
  final String alt;
  final String? titolo;
  final bool inLinea;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final url = urlImmagine(src);
    if (url != null && url.isEmpty) return const SizedBox.shrink();
    final provider = url == null ? ref.watch(immagineMediaProvider)(src) : NetworkImage(url);
    final immagine = Image(
      image: provider,
      semanticLabel: alt.isEmpty ? null : alt,
      excludeFromSemantics: alt.isEmpty,
      errorBuilder: (context, e, s) => const SizedBox.shrink(),
    );
    if (inLinea) return immagine;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Align(alignment: AlignmentDirectional.centerStart, child: immagine),
        if (titolo != null && titolo!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 24),
            child: Text(
              titolo!,
              textAlign: TextAlign.center,
              style: Stile.sans(13.6, altezza: 1.5, colore: Token.inkSoft),
            ),
          ),
      ],
    );
  }
}

/// `.scheda`: la carta (con la sua immagine), la stesa o l'articolo citati su una riga da sola.
class _Scheda extends StatelessWidget {
  const _Scheda(this.p);

  final PezzoScheda p;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final etichetta = switch (p.tipo) {
      TipoRiferimento.carta => t.blog_tipo_carta,
      TipoRiferimento.stesa => t.blog_tipo_stesa,
      TipoRiferimento.articolo => t.blog_tipo_articolo,
    };
    return Align(
      alignment: AlignmentDirectional.centerStart,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520),
        child: Premibile(
          alTocco: () => vai(context, _indirizzo(p.tipo, p.id)),
          collegamento: true,
          etichetta: '$etichetta: ${p.nome}',
          costruisci: (context, premuto) => Container(
            padding: const EdgeInsets.all(14.4),
            decoration: BoxDecoration(
              color: Token.paperLight,
              border: Border(
                top: BorderSide(color: premuto ? Token.brass : Token.line),
                right: BorderSide(color: premuto ? Token.brass : Token.line),
                bottom: BorderSide(color: premuto ? Token.brass : Token.line),
                left: const BorderSide(color: Token.brass, width: 3),
              ),
            ),
            child: Row(
              children: [
                if (p.tipo == TipoRiferimento.carta) ...[
                  Container(
                    width: 60,
                    decoration: BoxDecoration(border: Border.all(color: Colori.cornice, width: 2)),
                    child: ImmagineCarta(p.idCarta ?? p.id, mazzo: ''),
                  ),
                  const SizedBox(width: 16),
                ],
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        etichetta.toUpperCase(),
                        style: Stile.sans(11.2, peso: FontWeight.w700, em: .08, altezza: 1.4, colore: Token.verdigris),
                      ),
                      Text(p.nome, style: Stile.serif(17.6, altezza: 1.4, colore: Token.ink)),
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

/// Il video: nell'app una tessera 16:9 che lo apre fuori (il sito lo incorpora, «nocookie»).
class _Video extends StatelessWidget {
  const _Video(this.p);

  final PezzoVideo p;

  @override
  Widget build(BuildContext context) {
    final testo = context.t.app_video_apri(p.nome);
    return Premibile(
      alTocco: () => unawaited(apriFuori(p.url)),
      collegamento: true,
      etichetta: testo,
      an: 'video_esterno',
      costruisci: (context, premuto) => AspectRatio(
        aspectRatio: 16 / 9,
        child: ColoredBox(
          color: premuto ? Token.plum : Token.plumDeep,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 56,
                  height: 56,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: Token.brassPale, width: 2),
                  ),
                  child: Text('▶', style: Stile.sans(22, altezza: 1, colore: Token.brassPale)),
                ),
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    testo,
                    textAlign: TextAlign.center,
                    style: Stile.sans(14.4, peso: FontWeight.w600, colore: const Color(0xFFFFF7E8)),
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
