// I prezzi e la prova: i codici sconto (normalizzazione, scadenza, etichetta, variante dell'anteprima), il codice del
// collegamento che resta per la sessione, le righe del risparmio, il ritorno dal pagamento.

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/cassa/coupon.dart';
import 'package:tarots/cassa/pagamento.dart';
import 'package:tarots/modelli/cassa.dart';

import 'aiuti/finti.dart';
import 'aiuti/scena.dart';
import 'fixtures/prezzi/rete.dart';

void main() {
  group('codici', () {
    test('maiuscolo e senza spazi, come il server', () {
      expect(normalizzaCodice(' luna 30\n'), 'LUNA30');
    });

    test('i giorni alla scadenza contano il calendario, non le ore', () {
      final ora = DateTime(2026, 10, 4, 22);
      expect(giorniAllaScadenza(DateTime(2026, 10, 4, 23, 59).toIso8601String(), adesso: ora), 0);
      expect(giorniAllaScadenza(DateTime(2026, 10, 5, 0, 30).toIso8601String(), adesso: ora), 1);
      expect(giorniAllaScadenza(DateTime(2026, 10, 20).toIso8601String(), adesso: ora), isNull);
      expect(giorniAllaScadenza(DateTime(2026, 10, 1).toIso8601String(), adesso: ora), isNull);
      expect(giorniAllaScadenza(null, adesso: ora), isNull);
    });

    test('l\'etichetta dello sconto: percentuale o importo nella valuta', () {
      const p = CouponPubblico(codice: 'A', tipo: 'percentuale', valore: 30, durata: 'una_volta');
      expect(etichettaSconto(p, 'EUR', 'en'), '−30%');
      const i = CouponPubblico(codice: 'B', tipo: 'importo', valore: 500, durata: 'una_volta');
      expect(etichettaSconto(i, 'EUR', 'it'), '−5,00 €');
    });

    test('la variante dell\'anteprima vera (`/coupon/anteprima` di LUNA30)', () {
      final a = AnteprimaCouponPubblica.fromJson(anteprimaLuna());
      final mensile = a.voce('mensile-base', annuale: false, rinnovo: true)!;
      expect((mensile.importo, mensile.risparmio, mensile.vince, mensile.rinnoviCoupon), (693, 297, 'coupon', 2));
      final prova = a.voce('mensile-base', annuale: true, rinnovo: false, prova: true)!;
      expect((prova.applicato, prova.vince), (false, 'prova'));
      expect(a.voce('inesistente', annuale: false, rinnovo: false), isNull);
    });
  });

  testWidgets('il collegamento con ?coupon= applica il codice: banda, prezzi barrati, risparmio', (tester) async {
    final c = await montaApp(
      tester,
      rotta: '/pricing?coupon=luna30',
      larghezza: 390,
      altezza: 844,
      rete: retePrezziDiario(),
    );
    expect(c.read(couponAttivoProvider), 'LUNA30');
    expect(find.byType(BandaCoupon), findsOneWidget);
    expect(find.text('Code LUNA30 applied'), findsOneWidget);
    expect(find.text('Expires in 3 days'), findsOneWidget);
    expect(find.textContaining('You save'), findsWidgets);
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });

  testWidgets('un codice che non vale lo dice nella banda', (tester) async {
    await montaApp(
      tester,
      rotta: '/pricing?coupon=nessuno',
      larghezza: 390,
      altezza: 844,
      rete: retePrezziDiario(codiceValido: false),
    );
    expect(find.text('This code does not exist.'), findsOneWidget);
    debugDisableShadows = true;
  });

  testWidgets('il ritorno dal pagamento chiede al server com\'è andata e chiude il pagamento in sospeso', (tester) async {
    final rete = retePrezziDiario();
    rete.risposte['/me/checkout/abc'] = (_) => RispostaFinta.json({
      'checkout_id': 'abc',
      'stato': 'pagato',
      'piano': 'pacchetto-15',
      'nome': '15 readings',
      'tipo': 'pacchetto',
    });
    final c = await montaApp(tester, rotta: '/pricing?checkout=abc', larghezza: 390, altezza: 844, rete: rete);
    expect(c.read(pagamentoInSospesoProvider), isNull);
    expect(find.textContaining('15 readings'), findsWidgets);
    expect(rete.richieste.any((r) => r.uri.path == '/me/checkout/abc'), isTrue);
    debugDisableShadows = true;
  });

  testWidgets('la prova: il vantaggio grande, i passi, i livelli', (tester) async {
    await montaApp(tester, rotta: '/trial', larghezza: 390, altezza: 844, rete: retePrezziDiario());
    expect(find.text('−50%'), findsOneWidget);
    expect(find.text('Monthly Gold'), findsOneWidget);
    expect(find.text('Start the trial with Monthly Gold'), findsOneWidget);
    expect(tester.takeException(), isNull);
    debugDisableShadows = true;
  });
}
