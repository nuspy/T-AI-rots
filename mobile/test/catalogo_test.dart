// Il catalogo (carte, stese, mazzi, voto, negozio e carrello, la pagina che non c'è) dentro l'app intera, con le
// risposte vere dell'API locale salvate in `test/fixtures/catalogo/` (GET su http://localhost:8100) e, per il negozio,
// un mazzo in vendita scritto a mano.

import 'dart:convert';
import 'dart:io';

import 'package:flutter/rendering.dart' show debugDisableShadows;
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/dati/dati.dart';
import 'package:tarots/pagine/errori.dart';
import 'package:tarots/rotte/router.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';

Object? _json(String nome) => jsonDecode(File('test/fixtures/catalogo/$nome').readAsStringSync());

/// Il mazzo Lovers in vendita (scritto a mano): digitale, PDF e scatola, con un'offerta sul digitale.
const Map<String, Object?> mazzoInVendita = {
  'id': 2,
  'slug': 'lovers',
  'nome': 'Lovers Tarot',
  'descrizione': 'A deck about bonds.',
  'predefinito': false,
  'attivo': true,
  'attivo_ora': true,
  'prezzo_digitale': 1500,
  'prezzo_digitale_scontato': 1200,
  'prezzo_stampa': 990,
  'prezzo_fisico': 3900,
  'offerta_attiva': true,
  'offerta_formati': ['digitale'],
  'offerta_valido_fino': '2026-12-31T23:59:59Z',
  'richiede_spedizione': true,
  'valuta': 'EUR',
  'rank': 1,
};

/// La rete del catalogo: le fixture della home più le risposte del catalogo; [conMazzoInVendita] aggiunge il Lovers.
AdattatoreFinto reteCatalogo({bool conMazzoInVendita = false, Map<String, Object?>? voto}) {
  final rete = apiDaFixture();
  final mazzi = [...(_json('mazzi_en.json')! as List<Object?>), if (conMazzoInVendita) mazzoInVendita];
  rete.risposte.addAll({
    '/cards': (_) => RispostaFinta.json(_json('carte_en.json')),
    '/cards/the-star': (_) => RispostaFinta.json(_json('carta_stella_en.json')),
    '/cards/maj-17': (_) => RispostaFinta.json(_json('carta_stella_en.json')),
    '/spreads': (_) => RispostaFinta.json(_json('stese_en.json')),
    '/decks': (_) => RispostaFinta.json(mazzi),
    '/voto/mazzi': (_) => RispostaFinta.json(voto ?? _json('voto.json')),
    '/voto/home': (_) => RispostaFinta.json(_json('voto_home.json')),
    '/me/decks': (_) => RispostaFinta.json(_json('miei_mazzi.json')),
    '/me/addresses': (_) => RispostaFinta.json(_json('indirizzi.json')),
    'POST /shop/quote': (r) {
      final voci = ((r.data as Map)['voci'] as List).cast<Map<Object?, Object?>>();
      final righe = [
        for (final v in voci)
          {
            'deck_id': v['deck_id'],
            'tipo': v['tipo'],
            'quantita': v['quantita'],
            'prezzo_pieno_unitario': 990,
            'prezzo_finale_unitario': 990,
          },
      ];
      final totale = righe.fold<int>(0, (s, x) => s + 990 * (x['quantita']! as int));
      return RispostaFinta.json({
        'righe': righe,
        'subtotale': totale,
        'scaglione_percentuale': 0,
        'sconto_scaglioni': 0,
        'totale': totale,
        'richiede_indirizzo': false,
        // Come il backend locale: i pagamenti risultano attivi (il simulatore), ma l'ordine qui sotto non ha l'indirizzo
        // di pagamento e si registra in attesa.
        'pagamento_attivo': true,
      });
    },
    'POST /orders': (_) => RispostaFinta.json({
      'id': '4aab16e2-cdac-467b-b81b-01602be6e2cb',
      'status': 'aperto',
      'importo_totale': 990,
      'sconto_scaglioni': 0,
      'valuta': 'EUR',
      'righe': <Object?>[],
      'url': null,
      'pagamento_attivo': false,
    }, stato: 201),
  });
  return rete;
}

/// Un test a schermo: `montaApp` accende le ombre vere (per i golden), qui si rimettono come le vuole flutter_test.
void prova(String nome, Future<void> Function(WidgetTester tester) corpo) {
  testWidgets(nome, (tester) async {
    try {
      await corpo(tester);
    } finally {
      debugDisableShadows = true;
    }
  });
}

void main() {
  prova('la biblioteca: 78 carte, i filtri le riducono ai semi', (tester) async {
    await montaApp(tester, rotta: '/cards', larghezza: 390, altezza: 844, rete: reteCatalogo());
    expect(find.text('The Fool'), findsOneWidget);
    await tester.tap(find.text('Cups').first);
    await tester.pump();
    expect(find.text('The Fool'), findsNothing);
    expect(find.textContaining('Cups'), findsWidgets);
    expect(tester.takeException(), isNull);
  });

  prova('la scheda di una carta: domanda, livelli, corrispondenze, la carta prima e dopo', (tester) async {
    await montaApp(tester, rotta: '/cards/the-star', larghezza: 390, altezza: 844, rete: reteCatalogo());
    expect(find.text('The Star'), findsWidgets);
    expect(find.text('What is The Star asking you to look at?'), findsOneWidget);
    expect(find.text('Within you'), findsOneWidget);
    expect(find.text('Correspondences'), findsOneWidget);
    expect(find.textContaining('He ה'), findsOneWidget);
    expect(find.bySemanticsLabel('← The Tower'), findsOneWidget);
    expect(find.bySemanticsLabel('The Moon →'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  prova('le stese per gruppo e la scheda di una stesa con le posizioni', (tester) async {
    final c = await montaApp(tester, rotta: '/spreads', larghezza: 390, altezza: 844, rete: reteCatalogo());
    expect(find.text('Classic spreads'), findsOneWidget);
    expect(find.text('Three-Card Spread'), findsOneWidget);
    c.read(routerProvider).go('/spreads/three-card');
    await assesta(tester);
    expect(find.text('The positions'), findsOneWidget);
    expect(find.text('POSITION 1'), findsOneWidget);
    expect(find.text('Begin a reading with this spread'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  prova('i mazzi e la scheda del Thoth col PDF da stampare', (tester) async {
    final c = await montaApp(tester, rotta: '/decks', larghezza: 390, altezza: 844, rete: reteCatalogo());
    expect(find.text('Enter the Thoth Tarot deck'), findsOneWidget);
    expect(find.text('The Lovers'), findsOneWidget);
    c.read(routerProvider).go('/decks/thoth');
    await assesta(tester);
    expect(find.text('Your deck. Your ritual. Your reader.'), findsOneWidget);
    expect(find.textContaining('Print your own Tarot'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  prova('il negozio: aggiungere al carrello, poi il carrello col preventivo del server e l\'ordine', (
    tester,
  ) async {
    final rete = reteCatalogo(conMazzoInVendita: true);
    final c = await montaApp(tester, rotta: '/shop', larghezza: 390, altezza: 844, rete: rete);
    final aggiungi = find.text('Add printable deck (PDF)').first;
    await tester.ensureVisible(aggiungi);
    await tester.pump();
    await tester.tap(aggiungi);
    await tester.pump();
    expect(c.read(pezziCarrelloProvider), 1);
    expect(find.text('1 item in your cart'), findsOneWidget);

    c.read(routerProvider).go('/cart');
    await assesta(tester);
    await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 300)));
    await assesta(tester);
    expect(rete.richieste.any((r) => r.uri.path == '/shop/quote'), isTrue);
    expect(find.text('Subtotal'), findsOneWidget);
    expect(find.text('Thoth Tarot'), findsOneWidget);
    final completa = find.text('Complete the order');
    await tester.ensureVisible(completa);
    await tester.pump();
    await tester.tap(completa);
    await assesta(tester);
    expect(rete.richieste.any((r) => r.method == 'POST' && r.uri.path == '/orders'), isTrue);
    expect(find.textContaining('Order 4AAB16E2 registered'), findsOneWidget);
    expect(c.read(carrelloProvider), isEmpty);
    expect(tester.takeException(), isNull);
  });

  prova('la galleria di un mazzo: le pillole filtrano, una carta si ingrandisce', (tester) async {
    await montaApp(tester, rotta: '/shop', larghezza: 390, altezza: 844, rete: reteCatalogo());
    final vedi = find.text('See the cards').last;
    await tester.ensureVisible(vedi);
    await tester.pump();
    await tester.tap(vedi);
    await assesta(tester);
    expect(find.text('The cards of Thoth Tarot'), findsOneWidget);
    await tester.tap(find.text('Disks').first);
    await tester.pump();
    await tester.tap(find.bySemanticsLabel(RegExp('^Enlarge Two of Disks')));
    await tester.pump();
    expect(find.text('Two of Disks — Change'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  prova('il voto: senza tornata aperta l\'avviso; con una tornata si vota', (tester) async {
    final rete = reteCatalogo(
      voto: {
        'tornata': {'id': 't1'},
        'mio_voto': null,
        'candidati': [
          {'id': 'a', 'nome': 'Lovers', 'descrizione': 'Love.', 'campioni': <Object?>[], 'percentuale': null},
          {'id': 'b', 'nome': 'Halloween', 'descrizione': null, 'campioni': <Object?>[], 'percentuale': null},
        ],
        'vincitori_precedenti': null,
      },
    );
    rete.risposte['POST /voto/mazzi/a'] = (_) => RispostaFinta.json({'esito': 'ok'});
    await montaApp(tester, rotta: '/vote', larghezza: 390, altezza: 844, rete: rete);
    expect(find.text('Lovers'), findsOneWidget);
    final vota = find.text('Vote for this deck').first;
    await tester.ensureVisible(vota);
    await tester.pump();
    await tester.tap(vota);
    await assesta(tester);
    expect(rete.richieste.any((r) => r.method == 'POST' && r.uri.path == '/voto/mazzi/a'), isTrue);
    expect(tester.takeException(), isNull);
  });

  prova('una rotta che non esiste mostra la pagina 404', (tester) async {
    await montaApp(tester, rotta: '/non-esiste-davvero', larghezza: 390, altezza: 844, rete: reteCatalogo());
    expect(find.byType(Errore404), findsOneWidget);
    expect(find.text('This page has not been drawn.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
