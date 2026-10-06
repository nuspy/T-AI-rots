// v9.5, la prova 90/10: `/read` sceglie la versione della lettura, la ricorda sul dispositivo e tiene i parametri.

import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/lettura/variante.dart';

void main() {
  test('la versione salvata vince, coi parametri', () {
    final a = ArchivioMemoria({chiaveVarianteLettura: 'chat'});
    expect(
      smistaLettura(Uri.parse('/read?spread=tre-carte&source=hero'), a, 0),
      '/read-chat?spread=tre-carte&source=hero',
    );
    final b = ArchivioMemoria({chiaveVarianteLettura: 'classica'});
    expect(smistaLettura(Uri.parse('/read/'), b, 100), '/read-classic');
  });

  test('senza una versione salvata si sorteggia con la quota della console, e si salva', () async {
    final tutti = ArchivioMemoria();
    expect(smistaLettura(Uri.parse('/read'), tutti, 100), '/read-chat');
    await Future<void>.delayed(Duration.zero);
    expect(tutti.valori[chiaveVarianteLettura], 'chat');

    final nessuno = ArchivioMemoria();
    expect(smistaLettura(Uri.parse('/read'), nessuno, 0), '/read-classic');
    await Future<void>.delayed(Duration.zero);
    expect(nessuno.valori[chiaveVarianteLettura], 'classica');
  });

  test('la quota divide davvero: su 1000 persone, circa il 90% in chat', () {
    final caso = math.Random(7);
    var chat = 0;
    for (var i = 0; i < 1000; i++) {
      if (varianteDelDispositivo(ArchivioMemoria(), 90, caso: caso) == VarianteLettura.chat) chat++;
    }
    expect(chat, inInclusiveRange(860, 940));
  });

  test('un valore sconosciuto salvato si rifà; gli altri percorsi non si toccano', () {
    final a = ArchivioMemoria({chiaveVarianteLettura: 'boh'});
    expect(smistaLettura(Uri.parse('/read'), a, 100), '/read-chat');
    expect(smistaLettura(Uri.parse('/read-chat?x=1'), a, 100), isNull);
    expect(smistaLettura(Uri.parse('/reading'), a, 100), isNull);
    expect(smistaLettura(Uri.parse('/cards'), a, 100), isNull);
  });
}
