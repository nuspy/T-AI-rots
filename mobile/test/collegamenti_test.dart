// I collegamenti fra sito e app (Fase 10): gli App Links del manifesto (solo le pagine dell'app, mai Keycloak né
// l'API), lo stesso elenco del backend (`PERCORSI_APP`, che scrive apple-app-site-association), il ritorno da un
// pagamento con carta che arriva come App Link, il deep link di iOS.

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/cassa/pagamento.dart';
import 'package:tarots/rotte/indirizzi.dart';
import 'package:tarots/rotte/percorsi.dart';
import 'package:tarots/rotte/router.dart';

/// I filtri del manifesto: (autoVerify, host, percorsi).
List<({bool verifica, List<String> host, List<String> percorsi})> filtri() {
  final xml = File('android/app/src/main/AndroidManifest.xml').readAsStringSync();
  return [
    for (final f in RegExp(r'<intent-filter([^>]*)>(.*?)</intent-filter>', dotAll: true).allMatches(xml))
      if (f.group(2)!.contains('android:host='))
        (
          verifica: f.group(1)!.contains('android:autoVerify="true"'),
          host: [for (final m in RegExp(r'android:host="([^"]+)"').allMatches(f.group(2)!)) m.group(1)!],
          percorsi: [for (final m in RegExp(r'android:path(?:Prefix)?="([^"]+)"').allMatches(f.group(2)!)) m.group(1)!],
        ),
  ];
}

/// Le prime parti dei percorsi dell'app (`/cards`, `/daily-card`…).
final Set<String> rotteApp = {
  for (final r in [
    R.home, R.leggi, R.fisica, R.storia, R.condivise, R.giorno, R.carte, R.stese, R.mazzi, R.voto, R.negozio,
    R.carrello, R.prezzi, R.esplora, R.prova, R.blog, R.profilo, R.privacy, R.elimina,
  ])
    r,
};

void main() {
  test('App Links: solo tarots.chat è verificato, e solo sulle pagine dell\'app', () {
    final f = filtri();
    final verificati = f.where((x) => x.verifica).toList();
    expect(verificati, hasLength(1));
    expect(verificati.single.host, ['tarots.chat']);
    // www reindirizza: non si può verificare, e non deve far fallire tarots.chat.
    expect(f.where((x) => x.host.contains('www.tarots.chat')).every((x) => !x.verifica), isTrue);
    for (final p in verificati.single.percorsi) {
      expect(p, isNot(anyOf(startsWith('/auth'), startsWith('/api'), startsWith('/admin'), startsWith('/old'))));
      // Ogni percorso porta a una pagina dell'app (gli indirizzi pubblici e della v1 attraverso `interno`).
      final campione = switch (p) {
        '/it/' => '/it/carte',
        '/s/' => '/s/abc',
        _ => p,
      };
      final rotta = interno(campione);
      expect(
        rotteApp.any((r) => r == '/' ? rotta == '/' : rotta == r || rotta.startsWith('$r/')),
        isTrue,
        reason: '$p → $rotta',
      );
    }
    expect(verificati.single.percorsi, containsAll(['/', '/pricing', '/daily-card', '/card-of-the-day', '/it/']));
  });

  test('lo stesso elenco del backend (PERCORSI_APP, per apple-app-site-association)', () {
    final py = File('../backend/tarot_core/domain/app_mobili_repositories.py').readAsStringSync();
    final blocco = RegExp(r'PERCORSI_APP: Tuple\[str, \.\.\.\] = \((.*?)\n\)', dotAll: true).firstMatch(py)!.group(1)!;
    final backend = {for (final m in RegExp(r'"(/[^"]*)"').allMatches(blocco)) m.group(1)!};
    final manifesto = filtri().singleWhere((x) => x.verifica).percorsi.toSet()
      ..removeAll(['/', '/it', '/it/']);
    // Il manifesto scrive `/s/` per non prendere `/shop` e `/spreads`; il backend `/s` (e `/s/*`).
    expect(manifesto.map((p) => p == '/s/' ? '/s' : p).toSet(), backend);
  });

  test('il ritorno da un pagamento con carta: App Link su Android, deep link su iOS', () {
    expect(ritornoApp('/pricing?dopo=%2Fread', ios: false), '/pricing?dopo=%2Fread');
    expect(ritornoApp('/pricing', ios: true), 'chat.tarots.app://ritorno/pricing');
    // L'App Link arriva al router com'è: nessun reindirizzamento, i parametri restano.
    expect(reindirizza(Uri.parse('https://tarots.chat/pricing?checkout=abc')), isNull);
    expect(reindirizza(Uri.parse('https://tarots.chat/it/piano?checkout=abc')), '/pricing?checkout=abc');
    expect(reindirizza(Uri.parse('chat.tarots.app://ritorno/trial?checkout=abc')), '/trial?checkout=abc');
    expect(eRitornoApp(Uri.parse('chat.tarots.app://ritorno/pricing')), isTrue);
    expect(eRitornoApp(Uri.parse('chat.tarots.app:/oauth2redirect')), isFalse);
  });

  test('iOS: Associated Domains e notifiche nelle capacità dell\'app', () {
    final diritti = File('ios/Runner/Runner.entitlements').readAsStringSync();
    expect(diritti, contains('applinks:tarots.chat'));
    expect(diritti, contains('aps-environment'));
    expect(File('ios/Runner.xcodeproj/project.pbxproj').readAsStringSync(), contains('Runner/Runner.entitlements'));
    final info = File('ios/Runner/Info.plist').readAsStringSync();
    expect(info, contains('remote-notification'));
    expect(info, contains('FirebaseMessagingAutoInitEnabled'));
  });
}
