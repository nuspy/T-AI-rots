// Il diario: il Markdown degli articoli (pacchetto `markdown` + le direttive di `frontend/v2/lib/direttive-blog.ts`),
// le scorciatoie verso carte, stese e articoli, i video, e le pagine con la rete finta.

import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:tarots/blog/markdown.dart';
import 'package:tarots/componenti/diario.dart';
import 'package:tarots/modelli/blog.dart';
import 'package:tarots/pagine/blog.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';
import 'catalogo_test.dart' show reteCatalogo;
import 'fixtures/prezzi/rete.dart';

Map<String, dynamic> _fixture(String nome) =>
    jsonDecode(File('test/fixtures/$nome').readAsStringSync()) as Map<String, dynamic>;

/// La posizione verticale del primo testo [testo] sulla pagina.
double _y(WidgetTester tester, String testo) => tester.getTopLeft(find.text(testo).first).dy;

const Riferimenti rif = Riferimenti(
  carte: {'the-fool': 'The Fool', 'maj-00': 'The Fool'},
  stese: {'three-card': 'Three cards'},
  articoli: {'altro': 'Another [article]'},
  idCarte: {'the-fool': 'maj-00'},
);

md.Element _primo(List<md.Node> nodi) => nodi.whereType<md.Element>().first;

void main() {
  group('scorciatoie e pezzi', () {
    test('in mezzo al testo: un collegamento col nome; senza nome sparisce', () {
      expect(inLinea('A [[card:the-fool]] B', rif), 'A [The Fool](/cards/the-fool) B');
      expect(inLinea('[[post:altro]]', rif), '[Another article](/blog/altro)');
      expect(inLinea('x [[carta:sconosciuta]] y', rif), 'x  y');
    });

    test('su una riga da sola: schede e video, il resto resta Markdown', () {
      final pezzi = dividi('Prima\n[[carta:the-fool]]\n  [[video:vimeo:123456789]]  \nDopo\n[[stesa:nessuna]]', rif);
      expect(pezzi, hasLength(4));
      expect((pezzi[0] as PezzoMd).md, 'Prima');
      final scheda = pezzi[1] as PezzoScheda;
      expect((scheda.tipo, scheda.nome, scheda.idCarta), (TipoRiferimento.carta, 'The Fool', 'maj-00'));
      final video = pezzi[2] as PezzoVideo;
      expect((video.nome, video.url), ('Vimeo', 'https://vimeo.com/123456789'));
      // Una scorciatoia senza nome resta testo (come nel sito, che poi la toglie in linea).
      expect((pezzi[3] as PezzoMd).md, 'Dopo\n[[stesa:nessuna]]');
      expect(const PezzoVideo(fonte: 'youtube', id: 'abcdefg').url, 'https://www.youtube.com/watch?v=abcdefg');
    });
  });

  group('direttive', () {
    test('gli attributi, anche fra virgolette', () {
      expect(attributiDirettiva('colore=ottone dimensione="titolo"'), {'colore': 'ottone', 'dimensione': 'titolo'});
      expect(attributiDirettiva("size='large'"), {'size': 'large'});
      expect(attributiDirettiva(null), isEmpty);
    });

    test(':testo e :text diventano span con le classi della tavolozza (valori sconosciuti ignorati)', () {
      final p = _primo(leggiMarkdown(':testo[uno]{colore=ottone dimensione=grande} :text[due]{color=plum size=enorme}'));
      final span = p.children!.whereType<md.Element>().toList();
      expect(span.map((e) => e.tag), ['span', 'span']);
      expect(span[0].attributes['class'], 'md-colore-ottone md-dim-grande');
      expect(span[0].textContent, 'uno');
      expect(span[1].attributes['class'], 'md-colore-prugna');
    });

    test(':sottolineato diventa u, con il Markdown dentro', () {
      final p = _primo(leggiMarkdown(':underline[**forte**]'));
      final u = p.children!.whereType<md.Element>().single;
      expect(u.tag, 'u');
      expect((u.children!.single as md.Element).tag, 'strong');
    });

    test('una direttiva sconosciuta resta testo com\'era scritta', () {
      expect(_primo(leggiMarkdown('ecco :nota[qui] e 10:30')).textContent, 'ecco :nota[qui] e 10:30');
    });

    test('GFM: tabelle e barrato; niente HTML eseguito', () {
      final nodi = leggiMarkdown('| a | b |\n| - | - |\n| 1 | 2 |\n\n~~no~~ <b>x</b>');
      expect(nodi.whereType<md.Element>().map((e) => e.tag), ['table', 'p']);
      final p = nodi.whereType<md.Element>().last;
      expect((p.children!.first as md.Element).tag, 'del');
      expect(p.textContent, contains('<b>x</b>'));
    });
  });

  group('v9.4: modelli e paginazione', () {
    test('l\'immagine di una sezione: oggetto {url, mini, alt}, la stringa di prima, niente', () {
      const c = ImmagineBlogJson();
      expect(c.fromJson('/media/images/a'), const ImmagineBlog(url: '/media/images/a'));
      expect(c.fromJson(<String, dynamic>{'url': '/u', 'mini': '/m', 'alt': 'A'})?.perTessera, '/m');
      expect(c.fromJson(<String, dynamic>{'url': '/u', 'mini': null})?.perTessera, '/u');
      expect(c.fromJson(''), isNull);
      expect(c.fromJson(null), isNull);
      // L'albero salvato ha una sezione ancora con la stringa: si legge lo stesso.
      final albero = (jsonDecode(File('test/fixtures/blog/sezioni.json').readAsStringSync()) as List<Object?>)
          .cast<Map<String, dynamic>>()
          .map(NodoSezione.fromJson)
          .toList();
      NodoSezione? cerca(List<NodoSezione> nodi, String slug) {
        for (final n in nodi) {
          if (n.slug == slug) return n;
          final f = cerca(n.figli, slug);
          if (f != null) return f;
        }
        return null;
      }

      expect(cerca(albero, 'tarot-journal')?.immagine?.url, startsWith('/media/images/'));
    });

    test('i figli di una sezione hanno immagine, conteggi del ramo e 3 articoli', () {
      final d = DettaglioSezione.fromJson(_fixture('blog/sezione_learn.json'));
      final figlio = d.figli.single;
      expect(figlio.immagine?.mini, endsWith('/mini'));
      expect(figlio.nStese, 19);
      expect(figlio.articoli, hasLength(3));
      final minori = DettaglioSezione.fromJson(_fixture('blog/sezione_minori.json'));
      expect(minori.figli.map((f) => f.slug), ['by-suit', 'by-number']);
      expect(minori.figli.last.figli.map((f) => f.filtro?['rango']), contains('cavaliere'));
    });

    test('le stese di una sezione «stese»: tradizione, carte, schema, immagine', () {
      final d = DettaglioSezione.fromJson(_fixture('blog/sezione_stese.json'));
      final stese = d.stese;
      expect(stese, hasLength(3));
      final prima = stese.first;
      expect(prima.carte, prima.posizioni.length);
      expect(prima.descrizioneBreve.length, lessThanOrEqualTo(161));
      expect(prima.tradizioneIn('it'), 'classica');
      expect(prima.tradizioneIn('en'), 'classic');
      expect(prima.immagine?.alt, isNotEmpty);
      expect(prima.comeStesa().posizioni, isNotEmpty);
      // Un elemento rotto si salta, senza rompere gli altri.
      final rotta = d.copyWith(
        elementi: [
          ...d.elementi,
          {'id': 'x'},
        ],
      );
      expect(rotta.stese, hasLength(3));
    });

    test('gli articoli hanno il soggetto', () {
      final e = ElencoArticoli.fromJson(_fixture('blog/elenco.json'));
      expect(e.articoli.first.soggetto?.ref, 'maj-10');
      expect(e.articoli.last.soggetto, isNull);
    });

    test('il numero per pagina: 10, 25, 50 dall\'indirizzo; altrimenti 25', () {
      expect(perPaginaBlog, 25);
      expect(perPaginaDa({'per': '50'}), 50);
      expect(perPaginaDa({'per': '10'}), 10);
      expect(perPaginaDa({'per': '7'}), 25);
      expect(perPaginaDa({}), 25);
    });

    test('i numeri delle pagine: la prima, l\'ultima, le vicine, «…» nei buchi', () {
      expect(PaginatoreBlog.numeri(1, 1), [1]);
      expect(PaginatoreBlog.numeri(2, 3), [1, 2, 3]);
      expect(PaginatoreBlog.numeri(5, 10), [1, null, 4, 5, 6, null, 10]);
      expect(PaginatoreBlog.numeri(1, 10, vicine: 2), [1, 2, 3, null, 10]);
      expect(PaginatoreBlog.numeri(3, 5), [1, 2, 3, 4, 5]);
    });

    test('i collegamenti conservano la ricerca e il numero per pagina (assente se è quello predefinito)', () {
      const p = PaginatoreBlog(pagina: 2, pagine: 4, base: '/blog', per: 50, q: 'luna');
      expect(p.href(1), '/blog?q=luna&per=50');
      expect(p.href(3), '/blog?q=luna&page=3&per=50');
      expect(p.href(1, conPer: 25), '/blog?q=luna');
      const s = PaginatoreBlog(pagina: 1, pagine: 2, base: '/blog/sezione/love');
      expect(s.href(2), '/blog/sezione/love?page=2');
    });
  });

  testWidgets('una sezione: le sotto-sezioni come riquadri con immagine, conteggi e 3 articoli', (tester) async {
    await montaApp(tester, rotta: '/blog/sezione/learn-tarot', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    expect(find.text('Tarot Spreads'), findsWidgets);
    expect(find.textContaining('19 spreads'), findsOneWidget);
    final articoli = DettaglioSezione.fromJson(_fixture('blog/sezione_learn.json')).figli.single.articoli;
    for (final a in articoli) {
      expect(find.text(a.titolo), findsWidgets);
    }
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('Minor Arcana: i contenitori «By suit» e «By number» con le loro sezioni', (tester) async {
    await montaApp(tester, rotta: '/blog/sezione/minor-arcana', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    expect(find.text('By suit'), findsWidgets);
    expect(find.text('By number'), findsWidgets);
    for (final nome in ['Wands', 'Disks', 'Aces', 'Knights']) {
      expect(find.text(nome), findsWidgets, reason: nome);
    }
    // Ogni sezione del contenitore si tocca bene (almeno 48 px).
    final aces = find.ancestor(of: find.text('Aces').last, matching: find.byType(ConstrainedBox)).first;
    expect(tester.getSize(aces).height, greaterThanOrEqualTo(48));
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('le stese: illustrazione e schema, tradizione, carte, intro, «inizia una lettura»', (tester) async {
    await montaApp(tester, rotta: '/blog/sezione/tarot-spreads', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    final stese = DettaglioSezione.fromJson(_fixture('blog/sezione_stese.json')).stese;
    for (final s in stese) {
      expect(find.text(s.nome), findsOneWidget, reason: s.id);
      expect(find.text(s.descrizioneBreve), findsOneWidget, reason: s.id);
    }
    expect(find.text('CLASSIC · 3 CARDS'), findsOneWidget);
    expect(find.text('Begin a reading with this spread'), findsNWidgets(3));
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('la pagina di una carta: prima gli scelti, poi gli ultimi; sotto, tutti gli articoli a pagine', (
    tester,
  ) async {
    final rete = reteCatalogo();
    rete.risposte['/blog/posts'] = (r) => RispostaFinta.fixture('blog/elenco.json');
    await montaApp(tester, rotta: '/cards/the-star', larghezza: 390, altezza: 844, rete: rete);
    expect(_y(tester, 'Chosen for this page'), lessThan(_y(tester, 'Latest articles')));
    expect(find.text('Every article about The Star'), findsOneWidget);
    final richiesta = rete.richieste.where((r) => r.uri.path == '/blog/posts').single.uri.queryParameters;
    expect(richiesta, containsPair('carta', 'maj-17'));
    expect(richiesta, containsPair('per_pagina', '25'));
    // Il navigatore: le pagine e la scelta 10 / 25 / 50.
    expect(find.bySemanticsLabel('Page 2 of 5'), findsOneWidget);
    expect(find.text('50'), findsOneWidget);
    await tester.ensureVisible(find.text('50'));
    await tester.tap(find.text('50'));
    await assesta(tester);
    expect(
      rete.richieste.where((r) => r.uri.path == '/blog/posts').last.uri.queryParameters,
      containsPair('per_pagina', '50'),
    );
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('altrove i nove restano com\'erano: prima gli ultimi', (tester) async {
    await montaApp(tester, rotta: '/explore', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    expect(find.byType(DiarioNove), findsOneWidget);
    expect(find.text('Latest articles'), findsNothing);
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('il testo ricco si disegna: titoli, elenchi, citazione, tabella, figura, scheda, video', (tester) async {
    await montaApp(tester, rotta: '/blog/ricco', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    expect(find.byType(TestoArticolo), findsOneWidget);
    expect(find.text('Colours and sizes'), findsOneWidget);
    expect(find.textContaining('Ask a real question.'), findsOneWidget);
    expect(find.text('The Lovers, on the reading table'), findsOneWidget);
    expect(find.text('Watch the video on YouTube'), findsOneWidget);
    expect(find.text('Three cards'), findsWidgets);
    expect(find.textContaining('an unknown :nota[directive]'), findsOneWidget);
    expect(find.textContaining('memorise every card', findRichText: true), findsOneWidget);
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('l\'indice: la ricerca, gli ultimi, le sezioni ad albero, le etichette', (tester) async {
    await montaApp(tester, rotta: '/blog', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    expect(find.text('Latest articles'.toUpperCase()), findsOneWidget);
    expect(find.byType(TesseraDiario), findsWidgets);
    expect(find.text('Learn Tarot'), findsWidgets);
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });
}
