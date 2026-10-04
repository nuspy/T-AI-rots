// La pagina dei prezzi e la prova con lo store (Fase 9): i prodotti dello store al posto del checkout web, coi prezzi
// localizzati dello store; il pulsante della carta solo dove il catalogo lo ammette (e lì i codici sconto); il
// ripristino; il prodotto della prova. Store finto (`aiuti/store_finto.dart`), API finta.

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/acquisti/acquisti.dart';
import 'package:tarots/cassa/coupon.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';
import 'aiuti/store_finto.dart';
import 'fixtures/prezzi/rete.dart';

/// Lo store finto coi prodotti del catalogo (`test/fixtures/catalogo_store.json`).
({PiattaformaFinta store, NegozioGoogleFinto negozio}) storeConProdotti() {
  final store = PiattaformaFinta(
    prodotti: [
      pacchettoGoogle('crediti_5', '€4.99'),
      pacchettoGoogle('crediti_15', '€11.99', micros: 11990000),
      pacchettoGoogle('crediti_50', '€34.99', micros: 34990000),
      ...abbonamentoGoogle('abbonamento_oro', [
        offertaGoogle('mensile', [fase('€9.99', 9990000, 'P1M')]),
        offertaGoogle('annuale', [fase('€99.99', 99990000, 'P1Y')]),
        offertaGoogle('prova', [fase('Free', 0, 'P2W', cicli: 1), fase('€49.99', 49990000, 'P1Y')], offerta: 'gratis'),
      ]),
      ...abbonamentoGoogle('abbonamento_base', [offertaGoogle('mensile', [fase('€4.99', 4990000, 'P1M')])]),
    ],
  );
  return (store: store, negozio: NegozioGoogleFinto(store));
}

AdattatoreFinto reteStore({bool carta = true}) {
  final rete = retePrezziDiario();
  rete.risposte['/billing/store/catalogo'] = (_) {
    final r = RispostaFinta.fixture('catalogo_store.json');
    return carta
        ? r
        : RispostaFinta(200, corpo: r.corpo.replaceAll('"mostra": true', '"mostra": false'), intestazioni: r.intestazioni);
  };
  return rete;
}

void main() {
  setUp(() => Acquisti.attesaRipristino = const Duration(milliseconds: 10));

  testWidgets('i prodotti dello store coi prezzi dello store; comprare passa dallo store', (tester) async {
    final s = storeConProdotti();
    await montaApp(tester, rotta: '/pricing', larghezza: 390, altezza: 844, rete: reteStore(), negozio: s.negozio);
    expect(find.text('€4.99', skipOffstage: false), findsWidgets);
    expect(find.text('€34.99', skipOffstage: false), findsOneWidget);
    expect(find.textContaining('€9.99', skipOffstage: false), findsOneWidget);
    expect(find.textContaining('You pay with Google Play', skipOffstage: false), findsOneWidget);
    expect(find.text('Restore purchases', skipOffstage: false), findsOneWidget);
    // Nello store i codici sconto non valgono: resta il regalo, con la nota.
    expect(find.text('Discount code', skipOffstage: false), findsNothing);
    expect(find.textContaining('Discount codes only apply to card payments', skipOffstage: false), findsOneWidget);

    final compra = find.text('Choose this package', skipOffstage: false).first;
    await tester.ensureVisible(compra);
    await tester.pump();
    await tester.tap(compra);
    await assesta(tester);
    expect(s.store.acquisti.single.productDetails.id, 'crediti_5');
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('la carta dove il catalogo la ammette: i prezzi del sito e i codici sconto', (tester) async {
    final s = storeConProdotti();
    await montaApp(tester, rotta: '/pricing', larghezza: 390, altezza: 844, rete: reteStore(), negozio: s.negozio);
    final carta = find.text('Pay by card', skipOffstage: false);
    expect(carta, findsOneWidget);
    await tester.ensureVisible(carta);
    await tester.pump();
    await tester.tap(carta);
    await assesta(tester);
    expect(find.text('Discount code', skipOffstage: false), findsOneWidget);
    expect(find.textContaining('Card payments go through Stripe', skipOffstage: false), findsOneWidget);
    expect(find.text('Restore purchases', skipOffstage: false), findsNothing);
    debugDisableShadows = true;
  });

  testWidgets('senza la carta (politica «nascosto»): niente pulsante, niente codici sconto', (tester) async {
    final s = storeConProdotti();
    await montaApp(
      tester,
      rotta: '/pricing?coupon=luna30',
      larghezza: 390,
      altezza: 844,
      rete: reteStore(carta: false),
      negozio: s.negozio,
    );
    expect(find.text('Pay by card', skipOffstage: false), findsNothing);
    expect(find.byType(BandaCoupon), findsNothing);
    expect(find.text('Discount code', skipOffstage: false), findsNothing);
    expect(find.textContaining('Discount codes only apply', skipOffstage: false), findsNothing);
    debugDisableShadows = true;
  });

  testWidgets('lo store non risponde: lo dice', (tester) async {
    final s = storeConProdotti();
    s.store.disponibile = false;
    await montaApp(tester, rotta: '/pricing', larghezza: 390, altezza: 844, rete: reteStore(), negozio: s.negozio);
    expect(find.textContaining('aren\'t available on this device', skipOffstage: false), findsOneWidget);
    debugDisableShadows = true;
  });

  testWidgets('la prova nello store: il prezzo dopo la prova dello store, e si compra il prodotto «prova»', (tester) async {
    final s = storeConProdotti();
    await montaApp(tester, rotta: '/trial', larghezza: 390, altezza: 844, rete: reteStore(), negozio: s.negozio);
    expect(find.textContaining('€49.99', skipOffstage: false), findsOneWidget);
    final inizia = find.text('Start the trial with Monthly Gold', skipOffstage: false);
    await tester.ensureVisible(inizia);
    await tester.pump();
    await tester.tap(inizia);
    await assesta(tester);
    expect(s.store.acquisti.single.productDetails.id, 'abbonamento_oro');
    expect(find.text('Restore purchases', skipOffstage: false), findsOneWidget);
    debugDisableShadows = true;
  });
}
