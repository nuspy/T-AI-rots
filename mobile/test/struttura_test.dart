// La struttura della Fase 8: la barra dell'oracolo (temi per chi non ha un account, la chat per chi è dentro, il
// tetto delle aperture per visita), il banner della prova, il carrello sul telefono, il ritorno da un pagamento.

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/cassa/pagamento.dart';
import 'package:tarots/componenti/banner_prova.dart';
import 'package:tarots/componenti/oracolo.dart';
import 'package:tarots/consensi/consensi.dart';
import 'package:tarots/consensi/eta.dart';
import 'package:tarots/dati/carrello.dart';
import 'package:tarots/rotte/percorso.dart';
import 'package:tarots/rotte/router.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';

ArchivioMemoria _archivio() => ArchivioMemoria({
  'lingua': 'en',
  chiaveConsensi: const StatoConsensi(valori: {'statistiche': 'rifiutato', 'google_analytics': 'rifiutato'}).inJson(),
  chiaveEta: '16',
});

Future<ProviderContainer> _monta(
  WidgetTester tester, {
  bool autenticata = false,
  AdattatoreFinto? rete,
  ArchivioMemoria? archivio,
}) async {
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = const Size(390, 844);
  addTearDown(tester.view.reset);
  final c = ProviderContainer(
    overrides: sostituzioni(lingua: 'en', autenticata: autenticata, rete: rete, memoria: archivio ?? _archivio()),
    retry: (_, _) => null,
  );
  addTearDown(c.dispose);
  await tester.pumpWidget(UncontrolledProviderScope(container: c, child: const TarotsApp()));
  await assesta(tester);
  return c;
}

void main() {
  testWidgets('oracolo senza account: il tema, poi la domanda porta alla lettura gratuita', (tester) async {
    final c = await _monta(tester);
    // Il primo tema dei dizionari (il caso è fermo nei test).
    expect(find.text('Something in love is opening. Shall we look at what?'), findsOneWidget);
    await tester.tap(find.byType(Oracolo));
    await tester.pump();
    expect(find.text('Ask your own question…'), findsOneWidget);
    expect(find.text('Read the cards on this'), findsOneWidget);
    await tester.enterText(find.byType(EditableText).last, 'Will I find my way?');
    await tester.pump();
    await tester.testTextInput.receiveAction(TextInputAction.send);
    await assesta(tester);
    expect(c.read(percorsoProvider).path, '/read');
    final uri = uriVisibile(c.read(routerProvider).routerDelegate.currentConfiguration);
    expect(uri.queryParameters, {'question': 'Will I find my way?', 'source': 'dock'});
    // Sulla lettura la barra non c'è (la conversazione è già nella pagina).
    expect(find.text('Ask your own question…'), findsNothing);
    expect(c.read(altezzaOracoloProvider), 0);
  });

  testWidgets('oracolo per chi è dentro: lo storico, la proposta del giorno, il tetto per visita', (tester) async {
    final rete = apiDaFixture();
    var aperture = 0;
    rete.risposte['/chat/proattiva'] = (_) => RispostaFinta.json({
      'turni': [
        {
          'id': 'a',
          'ruolo': 'ai',
          'testo': 'Ieri parlavamo del lavoro.',
          'proposta': null,
          'creato': '2020-01-01T00:00:00Z',
        },
      ],
    });
    rete.risposte['/impostazioni-chat'] = (_) =>
        RispostaFinta.json({'proattiva_minuti_inattivita': 0, 'proattiva_max_per_visita': 1});
    rete.risposte['POST /chat/proattiva/avvio'] = (_) {
      aperture++;
      return RispostaFinta.json({
        'turno': {
          'id': 'b',
          'ruolo': 'ai',
          'testo': 'Oggi una carta per la tua settimana?',
          'proposta': {'argomento': 'la mia settimana', 'categoria': 'standard'},
          'creato': '2026-10-04T08:00:00Z',
        },
      }, stato: 201);
    };
    final c = await _monta(tester, autenticata: true, rete: rete);
    // L'ultima proposta era vecchia: l'oracolo ne apre una (una sola volta per visita).
    expect(aperture, 1);
    expect(find.text('Oggi una carta per la tua settimana?'), findsOneWidget);
    await tester.tap(find.byType(Oracolo));
    await tester.pump();
    expect(find.text('Ieri parlavamo del lavoro.'), findsOneWidget);
    expect(find.text('Read the cards about: la mia settimana'), findsOneWidget);
    expect(c.read(visitaOracoloProvider).aperture, 1);
  });

  testWidgets('il banner della prova: si vede, si chiude e resta chiuso per cinque giorni', (tester) async {
    final rete = apiDaFixture();
    rete.risposte['/abbonamenti/pubblico'] = (_) =>
        RispostaFinta.json({'banner_prova': true, 'prova_disponibile': true, 'giorni_prova': 14, 'sconto_prova': 50});
    final archivio = _archivio();
    final c = await _monta(tester, rete: rete, archivio: archivio);
    expect(find.text('14 days of included readings, free. Then −50% for life.'), findsOneWidget);
    await tester.tap(find.bySemanticsLabel('Hide the trial offer'));
    await tester.pump();
    expect(find.byType(BannerProva), findsOneWidget);
    expect(find.text('14 days of included readings, free. Then −50% for life.'), findsNothing);
    expect(c.read(bannerProvaNascostoProvider), isTrue);
    expect(archivio.leggi(chiaveBannerProva), contains('fino'));
  });

  test('il carrello letto dal telefono si ripulisce come nel sito', () {
    final voci = leggiCarrello(
      '[{"deckId":1,"tipo":"digitale","quantita":3},{"deckId":2,"tipo":"fisico","quantita":50},'
      '{"deckId":3,"tipo":"altro","quantita":1},{"tipo":"pdf"}]',
    );
    expect(voci.map((v) => (v.deckId, v.tipo, v.quantita)), [(1, 'digitale', 1), (2, 'fisico', 20)]);
    expect(leggiCarrello('non json'), isEmpty);
  });

  test('il carrello: un digitale una volta sola, le copie fino a 20, la riga sparisce a zero', () {
    final c = ProviderContainer(overrides: [archivioProvider.overrideWithValue(ArchivioMemoria())]);
    addTearDown(c.dispose);
    final carrello = c.read(carrelloProvider.notifier)
      ..aggiungi(1, 'digitale')
      ..aggiungi(1, 'digitale')
      ..aggiungi(2, 'fisico')
      ..quantita(2, 'fisico', 30);
    expect(c.read(carrelloProvider).map((v) => v.quantita), [1, 20]);
    carrello.quantita(2, 'fisico', 0);
    expect(c.read(carrelloProvider).single.deckId, 1);
    expect(c.read(archivioProvider).leggi(chiaveCarrello), contains('"deckId":1'));
  });

  test('il ritorno di un pagamento è un deep link dell\'app che diventa il suo percorso', () {
    expect(ritornoApp('/pricing', ios: true), 'chat.tarots.app://ritorno/pricing');
    // Su Android lo schema è già dell'accesso (flutter_appauth): il ritorno è la pagina del sito.
    expect(ritornoApp('/pricing', ios: false), '/pricing');
    expect(reindirizza(Uri.parse('chat.tarots.app://ritorno/pricing?checkout=abc')), '/pricing?checkout=abc');
    expect(reindirizza(Uri.parse('chat.tarots.app://ritorno/it/piano?checkout=abc')), '/pricing?checkout=abc');
    expect(reindirizza(Uri.parse('/pricing')), isNull);
  });
}
