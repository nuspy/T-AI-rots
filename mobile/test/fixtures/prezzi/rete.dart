/// La rete finta dei prezzi, della prova e del diario: le risposte vere dell'API salvate in `test/fixtures/prezzi/` (API
/// aggiornata, :8108, con le Fasi 2b e 2d) e `test/fixtures/blog/` (API locale, :8100), sopra quelle di [apiDaFixture].
library;

import 'dart:convert';
import 'dart:io';

import '../../aiuti/finti.dart';
import '../../aiuti/scena.dart';

Object? _json(String nome) => jsonDecode(File('test/fixtures/$nome').readAsStringSync());

/// L'anteprima del codice `LUNA30` con la scadenza fra [giorni] giorni (dalla data del test: il testo non cambia).
Map<String, Object?> anteprimaLuna({int giorni = 3}) {
  final a = (_json('prezzi/coupon.json')! as Map).cast<String, Object?>();
  final coupon = (a['coupon']! as Map).cast<String, Object?>();
  final ora = DateTime.now();
  coupon['valido_fino'] = DateTime(ora.year, ora.month, ora.day + giorni, 23, 59, 59).toUtc().toIso8601String();
  return {...a, 'coupon': coupon};
}

/// La rete dei prezzi e del diario.
AdattatoreFinto retePrezziDiario({bool codiceValido = true}) {
  final rete = apiDaFixture();
  rete.risposte.addAll({
    '/plans': (_) => RispostaFinta.fixture('prezzi/piani.json'),
    '/me/billing': (_) => RispostaFinta.fixture('prezzi/conto.json'),
    '/me/credits': (_) => RispostaFinta.fixture('prezzi/movimenti.json'),
    '/me/abbonamento': (_) => RispostaFinta.fixture('prezzi/mio_abbonamento.json'),
    '/abbonamenti/pubblico': (_) => RispostaFinta.fixture('prezzi/abbonamenti_pubblico.json'),
    '/impostazioni-pubbliche': (_) => RispostaFinta.fixture('prezzi/impostazioni.json'),
    'POST /coupon/anteprima': (_) => codiceValido
        ? RispostaFinta.json(anteprimaLuna())
        : RispostaFinta.json({
            'detail': {'motivo': 'coupon_sconosciuto', 'messaggio': 'Il codice non esiste.'},
          }, stato: 422),
    '/blog/posts': (r) {
      final q = r.uri.queryParameters;
      if (q['evidenza'] == 'true') return RispostaFinta.fixture('blog/evidenza.json');
      if (q['sezione'] == 'learn-tarot') return RispostaFinta.fixture('blog/elenco_learn.json');
      return RispostaFinta.fixture('blog/elenco.json');
    },
    '/blog/sections': (_) => RispostaFinta.fixture('blog/sezioni.json'),
    '/blog/sections/learn-tarot': (_) => RispostaFinta.fixture('blog/sezione_learn.json'),
    '/blog/sections/major-arcana': (_) => RispostaFinta.fixture('blog/sezione_maggiori.json'),
    // v9.4: le stese come schede ricche (gli elementi veri del catalogo, la prima con l'illustrazione) e Minor Arcana
    // coi contenitori «By suit» e «By number».
    '/blog/sections/tarot-spreads': (_) => RispostaFinta.fixture('blog/sezione_stese.json'),
    '/blog/sections/minor-arcana': (_) => RispostaFinta.fixture('blog/sezione_minori.json'),
    '/blog/tags': (_) => RispostaFinta.fixture('blog/etichette.json'),
    '/blog/nove': (r) {
      final q = r.uri.queryParameters;
      if (q['articolo'] != null) return RispostaFinta.fixture('blog/nove_articolo.json');
      if (q['sezione'] == 'learn-tarot') return RispostaFinta.fixture('blog/nove_learn.json');
      if (q['scelti'] == '10') return RispostaFinta.fixture('blog/nove_diario.json');
      return RispostaFinta.fixture('nove.json');
    },
    '/blog/posts/how-to-read-tarot-cards': (_) => RispostaFinta.fixture('blog/articolo.json'),
    '/blog/posts/ricco': (_) => RispostaFinta.fixture('blog/articolo_ricco.json'),
  });
  return rete;
}
