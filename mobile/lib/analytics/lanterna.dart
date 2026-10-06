/// Le statistiche interne: il porting di `lanterna-osservatore` (`E:\Projects\lanterna\js\index.js`, usato dal sito in
/// `frontend/v2/componenti/osservatore.tsx`). Stesso formato, stesso endpoint, stessi eventi, così la console somma
/// sito e app:
///
///     POST /e   {"v": 1, "lingua": "it", "id": "<identificativo>", "eventi": [{"n", "p", "dt", "x", …}]}
///
/// - `page_view` a ogni cambio di rotta, col **percorso del sito** (`/card-of-the-day`, `/it/carta-del-giorno`:
///   l'indirizzo che il sito manderebbe per la stessa pagina) e i parametri `utm_*` di un collegamento;
/// - `engagement`: il tempo **attivo** sulla pagina (app in primo piano e un'interazione negli ultimi 30 secondi) e la
///   profondità di scorrimento, mandato al cambio di pagina e quando l'app va in pausa;
/// - i tocchi sui widget [Tracciato] (l'equivalente di `[data-an]`) e gli eventi dell'app con [Lanterna.traccia].
///
/// **Due livelli, come il sito** (`frontend/lib/analytics.ts`, `frontend/v2/componenti/osservatore.tsx`):
/// - **base**, per tutti e senza consenso: visite, tempo attivo, tocchi ed eventi, senza nessun identificativo e senza
///   salvare niente sul telefono per le statistiche (il server conta le visite con un'impronta che cambia ogni giorno);
///   con un account il lotto porta il token, come il sito (il server rispetta l'opposizione scelta nel profilo);
/// - **esteso**, solo col consenso `statistiche`: anche l'identificativo casuale dell'installazione (`id`), che
///   riconosce i ritorni nei giorni successivi. Revocato il consenso, l'identificativo si cancella, il server lo
///   dimentica (`POST /e/dimentica`) e gli eventi tornano al livello base.
///
/// Ogni evento porta in `x` la dimensione `piattaforma` (`android`/`ios`), che lanterna salva con le proprietà.
/// Invio a lotti (10 eventi o 5 secondi), alla pausa e alla chiusura dell'app. Nessun errore esce di qui.
library;

import 'dart:async';
import 'dart:math';

/// Come mandare un lotto: `POST /e` (nei test, una funzione che li raccoglie).
typedef InvioLotto = Future<void> Function(Map<String, Object?> corpo);

final RegExp _nomeValido = RegExp(r'^[a-z][a-z0-9_]{0,63}$');

/// Un evento in coda.
class _Evento {
  _Evento(this.n, this.p, this.t, {this.d, this.x, this.u});

  final String n;
  final String p;
  final DateTime t;
  final int? d;
  final Map<String, Object?>? x;
  final Map<String, String>? u;
}

/// L'osservatore.
class Lanterna {
  /// Con il modo di inviare, la lingua corrente, la piattaforma e l'orologio (fermo nei test).
  Lanterna({
    required this.invia,
    required this.lingua,
    required this.piattaforma,
    DateTime Function()? adesso,
    this.intervallo = const Duration(seconds: 5),
    this.temporizzata = true,
    this.maxInCoda = 10,
    this.esclusi = const ['/admin', '/api'],
  }) : _adesso = adesso ?? DateTime.now {
    _ultimoTic = _adesso();
    _ultimaInterazione = _adesso();
  }

  /// Dopo quanto senza interazioni il tempo smette di contare come attivo.
  static const Duration inattivita = Duration(seconds: 30);

  /// Il trasporto.
  final InvioLotto invia;

  /// La lingua dell'interfaccia, letta a ogni invio.
  final String Function() lingua;

  /// `android` o `ios`.
  final String piattaforma;

  /// Ogni quanto si svuota la coda.
  final Duration intervallo;

  /// Falso nei test a schermo: niente invio periodico (la coda si svuota a 10 eventi, alla pausa, a mano).
  final bool temporizzata;

  /// Oltre quanti eventi si svuota subito.
  final int maxInCoda;

  /// I percorsi che non si contano.
  final List<String> esclusi;

  final DateTime Function() _adesso;
  final List<_Evento> _coda = [];
  Timer? _timer;
  bool _ferma = false;
  String? _id;
  String? _paginaCorrente;
  bool _visibile = true;
  int _attivoMs = 0;
  int _scrollMax = 0;
  late DateTime _ultimoTic;
  late DateTime _ultimaInterazione;

  /// Vero col consenso `statistiche`: i lotti portano l'identificativo.
  bool get estesa => _id != null;

  /// La pagina corrente (il percorso del sito).
  String? get paginaCorrente => _paginaCorrente;

  /// Gli eventi in attesa d'invio (per i test).
  int get inCoda => _coda.length;

  /// Il livello esteso, col consenso `statistiche`: da qui i lotti portano l'identificativo [id] di questa
  /// installazione (anche quelli ancora in coda: il sito lo legge al momento dell'invio).
  void estendi(String id) => _id = id;

  /// Di nuovo il livello base (consenso negato o revocato): niente più identificativo, gli eventi continuano.
  void riduci() => _id = null;

  void _avviaTimer() {
    if (_timer != null || _ferma || !temporizzata) return;
    _timer = Timer.periodic(intervallo, (_) {
      _tic();
      unawaited(svuota());
    });
  }

  /// Spegne l'osservatore per sempre (l'app si chiude, il contenitore dei provider sparisce): la coda si butta.
  void spegni() {
    _ferma = true;
    _id = null;
    _coda.clear();
    _timer?.cancel();
    _timer = null;
    _attivoMs = 0;
    _scrollMax = 0;
  }

  /// v9.5: la versione della lettura dal percorso (prova 90/10), come `varianteDaPercorso` del sito: `chat` sotto
  /// `/read-chat`, `classica` sotto `/read` e `/read-classic` (anche `/it/…`); null fuori dalla lettura.
  static String? varianteLettura(String percorso) {
    final p = percorso.split(RegExp(r'[?#]')).first.replaceAll(RegExp(r'/$'), '');
    bool sotto(String b) => p == b || p.startsWith('$b/');
    if (sotto('/read-chat') || sotto('/it/read-chat')) return 'chat';
    if (sotto('/read-classic') || sotto('/it/read-classic') || sotto('/read') || sotto('/it/read')) return 'classica';
    return null;
  }

  bool _escluso(String p) => esclusi.any((e) => p == e || p.startsWith('${e.replaceAll(RegExp(r'/$'), '')}/'));

  void _accoda(String n, {String? p, int? d, Map<String, Object?>? x, Map<String, String>? u}) {
    if (_ferma || !_nomeValido.hasMatch(n)) return;
    final percorso = p ?? _paginaCorrente ?? '/';
    if (_escluso(percorso)) return;
    final variante = varianteLettura(percorso);
    _coda.add(_Evento(n, percorso, _adesso(), d: d,
        x: {...?x, 'piattaforma': piattaforma, 'variante': ?variante}, u: u));
    _avviaTimer();
    if (_coda.length >= maxInCoda) unawaited(svuota());
  }

  /// Manda la coda, a lotti di 20. Un lotto che non parte si perde (come nel sito): mai un errore all'app.
  Future<void> svuota() async {
    while (_coda.isNotEmpty && !_ferma) {
      final lotto = _coda.sublist(0, min(20, _coda.length));
      _coda.removeRange(0, lotto.length);
      final ora = _adesso();
      final corpo = <String, Object?>{
        'v': 1,
        'lingua': lingua(),
        'id': ?_id,
        'eventi': [
          for (final e in lotto)
            {
              'n': e.n,
              'p': e.p,
              'dt': max(0, ora.difference(e.t).inMilliseconds),
              'd': ?e.d,
              'x': ?e.x,
              if (e.u != null && e.u!.isNotEmpty) 'u': e.u,
            },
        ],
      };
      try {
        await invia(corpo);
      } on Object {
        // il lotto si perde, l'app no
      }
    }
  }

  /* ---- tempo attivo e scorrimento ---- */

  void _tic() {
    final ora = _adesso();
    if (_visibile && ora.difference(_ultimaInterazione) < inattivita) {
      _attivoMs += min(ora.difference(_ultimoTic).inMilliseconds, 5000);
    }
    _ultimoTic = ora;
  }

  /// Un tocco, una pressione di tasto, uno scorrimento: il tempo torna attivo.
  void interazione() {
    _tic();
    _ultimaInterazione = _adesso();
  }

  /// La posizione di scorrimento della pagina, da 0 a 1.
  void scorrimento(double frazione) {
    interazione();
    final pct = (frazione.clamp(0, 1) * 100).round();
    if (pct > _scrollMax) _scrollMax = pct;
  }

  void _chiudiPagina() {
    _tic();
    final p = _paginaCorrente;
    if (p != null && _attivoMs > 0) _accoda('engagement', p: p, d: _attivoMs, x: {'scroll': _scrollMax});
    _attivoMs = 0;
    _scrollMax = 0;
  }

  /// Una pagina nuova: `page_view` col percorso del sito e gli `utm_*` dell'indirizzo, se ci sono.
  void pagina(String percorso, {Map<String, String> utm = const {}}) {
    if (percorso == _paginaCorrente) return;
    _chiudiPagina();
    _paginaCorrente = percorso;
    _ultimoTic = _adesso();
    _ultimaInterazione = _adesso();
    final u = {
      for (final e in utm.entries)
        if (e.key.startsWith('utm_') && e.value.isNotEmpty)
          e.key: e.value.length > 200 ? e.value.substring(0, 200) : e.value,
    };
    _accoda('page_view', p: percorso, u: u.isEmpty ? null : u);
  }

  /// Un evento dell'app (`question_submitted`, …), come `traccia()` del sito.
  void traccia(String nome, [Map<String, Object?>? proprieta]) => _accoda(nome, x: proprieta);

  /// L'app torna in primo piano.
  void inPrimoPiano() {
    _visibile = true;
    _ultimoTic = _adesso();
    _ultimaInterazione = _adesso();
  }

  /// L'app va in pausa o si chiude: si chiude la pagina (engagement) e si manda tutto.
  Future<void> inPausa() async {
    _chiudiPagina();
    _visibile = false;
    await svuota();
  }

  /// Ferma l'osservatore (chiusura definitiva).
  Future<void> ferma() async {
    _chiudiPagina();
    await svuota();
    _timer?.cancel();
    _timer = null;
  }
}

/// Un identificativo casuale per il livello esteso: 128 bit da un generatore crittografico, in esadecimale.
String nuovoIdentificativo([Random? caso]) {
  final r = caso ?? Random.secure();
  return List.generate(16, (_) => r.nextInt(256).toRadixString(16).padLeft(2, '0')).join();
}
