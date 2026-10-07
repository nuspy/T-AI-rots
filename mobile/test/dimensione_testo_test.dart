// A− / A+: la dimensione del testo scelta da chi legge, ricordata sul dispositivo e moltiplicata per quella del
// sistema.

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tarots/archivio.dart';
import 'package:tarots/componenti/dimensione_testo.dart';

void main() {
  test('si parte dal 100%, si scende e si sale a passi, entro i limiti, e si ricorda', () async {
    final archivio = ArchivioMemoria();
    final c = ProviderContainer(overrides: [archivioProvider.overrideWithValue(archivio)]);
    addTearDown(c.dispose);
    final n = c.read(dimensioneTestoProvider.notifier);
    expect(c.read(dimensioneTestoProvider), 100);
    n.passo(-1);
    expect(c.read(dimensioneTestoProvider), 90);
    await Future<void>.delayed(Duration.zero);
    expect(archivio.valori[chiaveDimensioneTesto], '90');
    for (var i = 0; i < 10; i++) {
      n.passo(-1);
    }
    expect(c.read(dimensioneTestoProvider), passiTesto.first);
    for (var i = 0; i < 20; i++) {
      n.passo(1);
    }
    expect(c.read(dimensioneTestoProvider), passiTesto.last);
  });

  test('un valore salvato si rilegge; uno sconosciuto torna al 100%', () {
    final ok = ProviderContainer(
      overrides: [
        archivioProvider.overrideWithValue(ArchivioMemoria({chiaveDimensioneTesto: '80'})),
      ],
    );
    addTearDown(ok.dispose);
    expect(ok.read(dimensioneTestoProvider), 80);
    final strano = ProviderContainer(
      overrides: [
        archivioProvider.overrideWithValue(ArchivioMemoria({chiaveDimensioneTesto: '85'})),
      ],
    );
    addTearDown(strano.dispose);
    expect(strano.read(dimensioneTestoProvider), 100);
  });

  testWidgets('la scala del sistema si moltiplica per la scelta', (tester) async {
    late TextScaler scala;
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          archivioProvider.overrideWithValue(ArchivioMemoria({chiaveDimensioneTesto: '80'})),
        ],
        child: MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(1.5)),
          child: ScalaTesto(
            child: Builder(
              builder: (context) {
                scala = MediaQuery.textScalerOf(context);
                return const SizedBox();
              },
            ),
          ),
        ),
      ),
    );
    expect(scala.scale(10), closeTo(12, .001));
  });
}
