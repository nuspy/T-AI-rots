// Il diario: il Markdown degli articoli (pacchetto `markdown` + le direttive di `frontend/v2/lib/direttive-blog.ts`),
// le scorciatoie verso carte, stese e articoli, i video, e le pagine con la rete finta.

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:markdown/markdown.dart' as md;
import 'package:tarots/blog/markdown.dart';
import 'package:tarots/pagine/blog.dart';

import 'aiuti/scena.dart';
import 'fixtures/prezzi/rete.dart';

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
