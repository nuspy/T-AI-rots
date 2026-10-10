// Termini di servizio e privacy solo in inglese (10/10/2026): le pagine prendono sempre i testi inglesi, anche con
// l'app in italiano, con la nota che l'originale è l'inglese; il telefono li traduce nella lingua di lettura (qui il
// motore finto). Le scelte del telefono restano nella lingua dell'app; il piè di pagina porta ai termini.

import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/app.dart';
import 'package:tarots/componenti/bottoni.dart';
import 'package:tarots/l10n/testi.dart';
import 'package:tarots/pagine/termini.dart';
import 'package:tarots/rotte/router.dart';
import 'package:tarots/traduzione/motore.dart';

import 'aiuti/scena.dart';
import 'profilo_test.dart' show reteProfilo;
import 'traduzione_test.dart' show MotoreFinto;

final AppLocalizations en = lookupAppLocalizations(const Locale('en'));
final AppLocalizations it = lookupAppLocalizations(const Locale('it'));

/// L'app in [lingua] sulla [rotta], con l'API delle pagine dell'account (il titolare dalla console).
Future<void> monta(
  WidgetTester tester,
  String rotta, {
  String lingua = 'it',
  String? linguaContenuti,
  MotoreTraduzione? motore,
}) async {
  await tester.runAsync(caricaCaratteri);
  tester.platformDispatcher.accessibilityFeaturesTestValue = const FakeAccessibilityFeatures(disableAnimations: true);
  addTearDown(tester.platformDispatcher.clearAccessibilityFeaturesTestValue);
  tester.view.devicePixelRatio = 1;
  tester.view.physicalSize = const Size(390, 844);
  addTearDown(tester.view.reset);
  final c = ProviderContainer(
    overrides: sostituzioni(lingua: lingua, rete: reteProfilo(), linguaContenuti: linguaContenuti, motore: motore),
    retry: (_, _) => null,
  );
  addTearDown(c.dispose);
  await tester.pumpWidget(UncontrolledProviderScope(container: c, child: const TarotsApp()));
  c.read(routerProvider).go(rotta);
  await assesta(tester);
}

Finder testo(String s) => find.text(s, skipOffstage: false);

void main() {
  testWidgets('i termini sono in inglese anche con l\'app in italiano, con la nota dell\'originale', (tester) async {
    await monta(tester, '/terms');
    for (final s in [
      en.termini_titolo,
      en.termini_originale,
      en.termini_chi_titolo,
      en.termini_chi_testo('Andrea Taini'),
      en.termini_sezioni_0_titolo,
      en.termini_sezioni_13_testi_1,
      en.termini_versione,
    ]) {
      expect(testo(s), findsOneWidget, reason: s);
    }
    // Il titolare dalla console: niente indirizzo né codice (la fixture non li ha), la posta come collegamento.
    expect(find.textContaining('Postal address', skipOffstage: false), findsNothing);
    expect(
      find.byWidgetPredicate((w) => w is TestoSottolineato && w.testo == 'privacy@tarots.chat', skipOffstage: false),
      findsOneWidget,
    );
    // Il rimando alla privacy porta alla pagina.
    final privacy = find.byWidgetPredicate(
      (w) => w is TestoSottolineato && w.testo == en.termini_privacy_link,
      skipOffstage: false,
    );
    await tester.ensureVisible(privacy);
    await tester.pump();
    await tester.tap(privacy);
    await assesta(tester);
    expect(testo(en.privacy_titolo), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('i termini si leggono tradotti sul telefono, col riquadro della traduzione', (tester) async {
    final motore = MotoreFinto();
    await monta(tester, '/terms', lingua: 'en', linguaContenuti: 'hu', motore: motore);
    expect(motore.scaricati, contains('hu'));
    expect(testo('‹hu› ${en.termini_titolo}'), findsOneWidget);
    expect(testo('‹hu› ${en.termini_originale}'), findsOneWidget);
    expect(testo('‹hu› ${en.termini_sezioni_4_testi_5}'), findsOneWidget);
    expect(testo('Translated automatically on your device from English.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('la privacy è in inglese con l\'app in italiano; le scelte del telefono restano in italiano', (
    tester,
  ) async {
    await monta(tester, '/privacy');
    for (final s in [en.privacy_titolo, en.termini_originale, en.privacy_custode_titolo, en.privacy_finalita_titolo]) {
      expect(testo(s), findsOneWidget, reason: s);
    }
    expect(testo(it.privacy_titolo), findsNothing);
    expect(testo(it.privacy_custode_titolo), findsNothing);
    expect(find.textContaining('Andrea Taini', skipOffstage: false), findsOneWidget);
    // Le parti da usare: nella lingua dell'app.
    expect(testo(it.app_scelte_titolo), findsOneWidget);
    expect(testo(it.app_consenso_statistiche), findsOneWidget);
    expect(testo(it.privacy_diritti_cta_elimina), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('il piè di pagina porta ai termini', (tester) async {
    await monta(tester, '/privacy');
    final voce = testo(it.comune_piede_termini);
    expect(voce, findsOneWidget);
    await tester.ensureVisible(voce);
    await tester.pump();
    await tester.tap(voce);
    await assesta(tester);
    expect(testo(en.termini_titolo), findsOneWidget);
  });

  test('le sezioni dei termini sono tutte quelle del dizionario, nello stesso ordine', () {
    final arb = jsonDecode(File('lib/l10n/app_en.arb').readAsStringSync()) as Map<String, Object?>;
    final voci = [
      for (final e in arb.entries)
        if (e.key.startsWith('termini_sezioni_')) e.value! as String,
    ];
    final lette = [
      for (final s in sezioniTermini(en)) ...[s.titolo, ...s.testi],
    ];
    expect(lette, voci);
  });
}
