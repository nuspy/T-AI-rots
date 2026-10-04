// Le risposte dell'API che ogni schermata dei golden riceve, salvate per il confronto col sito
// (`confronto/rete/<nome>.json` e l'elenco `confronto/schermate.json`): `confronto/cattura_sito.py` le dà al sito con
// Playwright, così sito e app mostrano gli stessi dati.
//
//   flutter test tool/registra_rete_test.dart
//
// Si rilancia quando cambiano le fixture o le schermate dei golden.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

import '../test/aiuti/finti.dart';
import '../test/aiuti/scena.dart';
import '../test/catalogo_test.dart' show reteCatalogo;
import '../test/fixtures/prezzi/rete.dart' show retePrezziDiario;
import '../test/golden/lettura_test.dart' as lettura;
import '../test/golden/storia_test.dart' as storia;
import '../test/profilo_test.dart' show reteProfilo;

/// Una schermata: il nome dei golden (`<nome>_<larghezza>.png`), il titolo nel rapporto, la rotta dell'app, la rete
/// finta, le larghezze, e ciò che il sito deve sapere in più.
typedef Schermata = ({
  String nome,
  String titolo,
  String rotta,
  AdattatoreFinto Function() rete,
  List<int> misure,
  Map<String, Object?> extra,
});

const List<int> tutte = [360, 390, 1024];

List<Schermata> schermate() => [
  (nome: 'home', titolo: 'Home', rotta: '/', rete: apiDaFixture, misure: tutte, extra: {}),
  (nome: 'giorno', titolo: 'Carta del giorno', rotta: '/daily-card', rete: apiDaFixture, misure: tutte, extra: {}),
  for (final (n, t, r) in [
    ('carte', 'Le carte', '/cards'),
    ('carta', 'Una carta', '/cards/the-star'),
    ('stese', 'Le stese', '/spreads'),
    ('stesa', 'Una stesa', '/spreads/three-card'),
    ('mazzi', 'I mazzi', '/decks'),
    ('mazzo', 'Un mazzo', '/decks/thoth'),
    ('voto', 'Vota il prossimo mazzo', '/vote'),
    ('negozio', 'Il negozio', '/shop'),
    ('pagina_404', 'La pagina che non c\'è', '/non-esiste'),
  ])
    (nome: n, titolo: t, rotta: r, rete: reteCatalogo, misure: tutte, extra: <String, Object?>{}),
  (
    nome: 'carrello',
    titolo: 'Il carrello (il PDF del Thoth)',
    rotta: '/cart',
    rete: reteCatalogo,
    misure: tutte,
    extra: {
      'storage': {'tarots.v2.carrello': '[{"deckId":1,"tipo":"pdf","quantita":1}]'},
    },
  ),
  for (final (stato, rotta) in [
    ('preparazione', '/read?spread=tre-carte'),
    ('intervista', '/read?id=${lettura.idLettura}'),
    ('scelta', '/read?id=${lettura.idLettura}'),
    ('completata', '/read?id=${lettura.idLettura}'),
  ])
    (
      nome: 'lettura_$stato',
      titolo: 'Il rito: $stato',
      rotta: rotta,
      rete: () => lettura.rete(stato),
      misure: tutte,
      extra: stato == 'scelta'
          ? {'note': 'Sul telefono la scelta delle carte è nel dialogo scuro: nel sito si apre con «Open the ritual».'}
          : <String, Object?>{},
    ),
  (nome: 'storia', titolo: 'La mia storia', rotta: '/my-story', rete: storia.rete, misure: tutte, extra: {}),
  (
    nome: 'storia_lettura',
    titolo: 'Una lettura della storia',
    rotta: '/my-story/${storia.idLettura}',
    rete: storia.rete,
    misure: tutte,
    extra: {},
  ),
  (
    nome: 'condivisa',
    titolo: 'Una lettura condivisa',
    rotta: '/shared/${storia.tokenCondivisa}',
    rete: storia.rete,
    misure: tutte,
    extra: {},
  ),
  (nome: 'fisica', titolo: 'Le proprie carte', rotta: '/physical-reading', rete: storia.rete, misure: tutte, extra: {}),
  (nome: 'profilo', titolo: 'Il profilo', rotta: '/profile', rete: reteProfilo, misure: tutte, extra: {}),
  (
    nome: 'profilo_store',
    titolo: 'Il profilo con un abbonamento dello store',
    rotta: '/profile',
    rete: () => reteProfilo(abbonamento: 'store'),
    misure: [390],
    extra: {},
  ),
  (nome: 'privacy', titolo: 'Metodo e privacy', rotta: '/privacy', rete: reteProfilo, misure: tutte, extra: {}),
  (
    nome: 'elimina',
    titolo: 'Eliminare l\'account',
    rotta: '/account/elimina',
    rete: reteProfilo,
    misure: tutte,
    extra: {},
  ),
  for (final (n, t, r) in [
    ('prezzi', 'I prezzi', '/pricing'),
    ('prezzi_coupon', 'I prezzi con un codice sconto', '/pricing?coupon=LUNA30'),
    ('prova', 'La prova gratuita', '/trial'),
    ('blog', 'Il diario', '/blog'),
    ('blog_sezione', 'Una sezione del diario', '/blog/sezione/learn-tarot'),
    ('articolo', 'Un articolo', '/blog/how-to-read-tarot-cards'),
    ('esplora', 'Esplora', '/explore'),
  ])
    (nome: n, titolo: t, rotta: r, rete: retePrezziDiario, misure: tutte, extra: <String, Object?>{}),
];

/// Avvolge le risposte della rete per ricordare quelle date davvero (non lo streaming).
Map<String, Object?> registra(AdattatoreFinto rete) {
  final dato = <String, Object?>{};
  for (final e in rete.risposte.entries.toList()) {
    final originale = e.value;
    rete.risposte[e.key] = (r) {
      final risposta = originale(r);
      if (risposta.pezzi == null) {
        final chiave = '${r.method} ${r.uri.path}';
        Object? corpo;
        try {
          corpo = jsonDecode(risposta.corpo);
        } on FormatException {
          corpo = null;
        }
        if (corpo != null) dato[chiave] = {'stato': risposta.stato, 'json': corpo};
      }
      return risposta;
    };
  }
  return dato;
}

void main() {
  final cartella = Directory('confronto/rete')..createSync(recursive: true);
  final elenco = <Map<String, Object?>>[];
  for (final s in schermate()) {
    testWidgets('rete di ${s.nome}', (tester) async {
      final rete = s.rete();
      final dato = registra(rete);
      await montaApp(tester, rotta: s.rotta, larghezza: 390, altezza: 844, rete: rete);
      await assesta(tester);
      File('${cartella.path}/${s.nome}.json').writeAsStringSync(const JsonEncoder.withIndent(' ').convert(dato));
      elenco.add({
        'nome': s.nome,
        'titolo': s.titolo,
        'rotta': s.rotta,
        'golden': '${s.nome}_{w}.png',
        'rete': 'confronto/rete/${s.nome}.json',
        'misure': s.misure,
        ...s.extra,
      });
      debugDisableShadows = true;
    });
  }
  tearDownAll(() {
    File('confronto/schermate.json').writeAsStringSync(
      const JsonEncoder.withIndent(' ').convert({'comuni': <String, Object?>{}, 'schermate': elenco}),
    );
  });
}
