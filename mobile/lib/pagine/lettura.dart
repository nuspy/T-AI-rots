/// Il rito di lettura (`frontend/v2/lettura/lettura.tsx`, pagina `/read`), dall'inizio alla fine, con le stesse fasi e
/// le stesse API del sito:
///
///     preparazione (domanda, tipo, persone, stesa) → intervista → pronto a mescolare → mescolamento → taglio →
///     scelta → svelamento → sintesi → completata          (e `crisi`, `annullata`)
///
/// La messa in scena è quella della v2: la conversazione a sinistra, la console del rito a destra (sul telefono una
/// sotto l'altra, e durante il rito prima la console). Sul telefono tipo e stesa si scelgono in due dialoghi
/// all'apertura, e le fasi del rito si aprono in un dialogo scuro; chi lo chiude lo ritrova nella pagina.
///
/// v9.5, la prova 90/10 (`lettura/variante.dart`): `/read` sceglie fra questa pagina classica (`/read-classic`) e la
/// lettura tutta in chat (`/read-chat`, [PaginaLettura.inChat]): una colonna sola, dove domande, mazzo, taglio,
/// ventaglio, carte e responso arrivano uno dopo l'altro come messaggi, e la pagina li segue solo se si è in fondo.
///
/// Dall'indirizzo: `id` riprende una lettura; `question` precompila la domanda; `topic` la propone da un tema; `type`
/// sceglie il tipo; `spread` la stesa; `card` propone una domanda sulla carta; `deck` sceglie le immagini di un mazzo;
/// `source` (hero, dock, qr…) va solo alle statistiche. Chi non ha un account fa la lettura gratuita (una per
/// dispositivo, col cookie `tarots_anon` che il client tiene su disco) e riceve una prima risposta con l'invito a
/// tenere quella completa. Niente spazi pubblicitari.
library;

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/rendering.dart' show RenderAbstractViewport;
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../analytics/tracciato.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../api/sse.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/dialogo_limite.dart';
import '../componenti/modale.dart';
import '../componenti/pagina.dart';
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../consensi/eta.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lettura/comuni.dart';
import '../lettura/condivisione.dart';
import '../lettura/dialogo.dart';
import '../lettura/persone.dart';
import '../lettura/preparazione.dart';
import '../lettura/responso.dart';
import '../lettura/stampa.dart';
import '../lettura/tavolo.dart';
import '../lettura/variante.dart';
import '../lettura/ventaglio.dart';
import '../lingua/lingua.dart';
import '../modelli/account.dart' hide Ventaglio;
import '../modelli/carta.dart';
import '../modelli/cassa.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// Le fasi del rito, coi nomi del sito (per le statistiche).
enum FaseLettura {
  /// La domanda, il tipo, la stesa.
  preparazione('preparazione'),

  /// Le persone (letture di due persone).
  persone('persone'),

  /// Le domande del lettore.
  intervista('intervista'),

  /// L'intervista è finita: si può mescolare.
  prontoMescolare('pronto-mescolare'),

  /// Il mazzo si mescola.
  mescolamento('mescolamento'),

  /// Il taglio.
  taglio('taglio'),

  /// La scelta delle carte nel ventaglio.
  scelta('scelta'),

  /// Le carte sono sul tavolo, coperte.
  rivelazione('rivelazione'),

  /// Le carte si girano una per una.
  svelamento('svelamento'),

  /// Tutte girate: manca l'interpretazione.
  prontoSintesi('pronto-sintesi'),

  /// L'interpretazione arriva.
  sintesi('sintesi'),

  /// Finita.
  completata('completata'),

  /// L'uscita di crisi.
  crisi('crisi'),

  /// La lettura è in pausa.
  annullata('annullata');

  const FaseLettura(this.nome);

  /// Il nome del sito.
  final String nome;
}

/// `?type=`: i nomi inglesi della v2 e quelli italiani del sito.
String? comeCategoria(String? v) => switch (v) {
  'standard' || 'question' => 'standard',
  'compatibilita' || 'compatibility' => 'compatibilita',
  'coppia' || 'couple' => 'coppia',
  'lavoro' || 'work' || 'business' => 'lavoro',
  _ => null,
};

/// Le stese nella lingua dei contenuti.
final steseLetturaProvider = FutureProvider.family<List<Stesa>, String>(
  (ref, lingua) => ref.read(apiProvider).stese(lingua),
);

/// Gli id dei mazzi che si possono leggere (con un account).
final mieiMazziLetturaProvider = FutureProvider<List<int>>((ref) async {
  if (!ref.watch(sessioneProvider.select((s) => s.autenticata))) return const [];
  try {
    return await ref.read(apiProvider).mieiMazzi();
  } on ErroreApi {
    return const [];
  }
});

/// Le carte, per `?card=`.
final carteLetturaProvider = FutureProvider.family<List<Carta>, String>(
  (ref, lingua) => ref.read(apiProvider).carte(lingua),
);

/// La pagina della lettura.
class PaginaLettura extends ConsumerStatefulWidget {
  /// La lettura, coi [parametri] dell'indirizzo.
  const PaginaLettura({super.key, required this.parametri, this.inChat = false});

  /// I parametri della query (`question`, `type`, `spread`, `id`…).
  final Map<String, String> parametri;

  /// v9.5: la lettura tutta in chat (`/read-chat`); falso: la classica.
  final bool inChat;

  @override
  ConsumerState<PaginaLettura> createState() => _PaginaLetturaState();
}

class _PaginaLetturaState extends ConsumerState<PaginaLettura> {
  final ScrollController _scorri = ScrollController();
  final ChangeNotifier _cambi = ChangeNotifier();

  /// I registri del volo: uno per il rito nella pagina e uno per il dialogo del telefono. Le chiavi globali dei posti
  /// e del ventaglio non possono stare in due alberi insieme: quando il dialogo si chiude (allo svelamento) la pagina
  /// ridisegna il suo tavolo nello stesso fotogramma, e con le stesse chiavi Flutter le sposterebbe durante la
  /// disposizione (un'asserzione). Il volo avviene sempre dentro uno solo dei due.
  final VoloCarte _voloPagina = VoloCarte();
  final VoloCarte _voloDialogo = VoloCarte();

  /// Il registro del rito che si vede: il dialogo se è aperto, se no la pagina.
  VoloCarte get _volo => _dialogoRito != null ? _voloDialogo : _voloPagina;
  final GlobalKey _zonaMazzo = GlobalKey(debugLabel: 'zona-mazzo');
  final GlobalKey _zonaResponso = GlobalKey(debugLabel: 'zona-responso');
  final GlobalKey _scena = GlobalKey(debugLabel: 'scena');
  final TextEditingController _domanda = TextEditingController();
  int _contatore = 0;
  bool _vivo = true;

  late FaseLettura _fase;
  late TemaLettura _tema;
  DatiPersone _persone = const DatiPersone();
  bool _personeFatte = false;
  String? _nomePartner;
  String? _id;
  String? _stesaId;
  bool _domandaToccata = false;
  String? _disclaimer;
  String? _errore;
  bool _inCorso = false;

  /// Quale dei due invii della domanda: «Invia quesito e inizia a mescolare le carte» (vero: senza intervista) o
  /// «Invia domanda e chiedimi pure». Resta fino all'apertura, anche dopo l'avvertenza, l'età o il dialogo del limite.
  bool _saltaIntervista = false;

  List<Battuta> _battute = [];
  bool _attesa = false;
  int _slotTotali = 0;
  Set<int> _scelte = {};
  List<Posata> _posate = [];
  bool _rivelazioneInCorso = false;

  /// Le carte sono girate e il lettore le sta leggendo tutte insieme (una chiamata sola): un solo momento d'attesa.
  bool _lettoreLegge = false;
  bool _scegliendo = false;

  /// v9.5, i tre pulsanti. L'oracolo fa la prima domanda da sé; dopo ogni risposta il campo si chiude e chi legge
  /// sceglie fra «Passa alla lettura», «Voglio dire qualcosa di libero» e «Voglio rispondere a un'altra domanda»
  /// (quest'ultima finché non si arriva al massimo). Sotto la prima domanda ci sono già «Passa alla lettura» (se il
  /// minimo lo consente) e il testo libero.
  _ModoIntervista _modo = _ModoIntervista.risposta;
  int _minDomande = 0;
  int _maxDomande = 2;
  int _poste = 0;

  /// v9.5, la chat: chi legge è in fondo alla pagina (la pagina segue i messaggi nuovi solo allora).
  bool _inFondo = true;
  String _novita = '';
  bool _varianteAllineata = false;

  String _faseResponso = 'unione';
  String _testoResponso = '';
  ({String disclaimer, String? commitment, int? saldo, bool anonimo})? _fine;
  String _domandaLettura = '';
  String? _linguaLettura;
  bool _manuale = false;
  String? _mazzoScelto;
  bool _mazzoSceltoFatto = false;
  String? _mazzoLettura;
  bool _mazzoLetturaFatto = false;

  bool _ritoChiuso = false;
  Route<void>? _dialogoRito;
  bool _dialoghiAvviati = false;
  bool _caricata = false;
  bool _precompilato = false;
  bool _cartaProposta = false;
  bool _sorgenteTracciata = false;
  FaseLettura? _faseTracciata;

  /// Le stese e il mazzo attivo dell'ultimo disegno: i dialoghi li leggono da qui.
  List<Stesa> _steseCorrenti = const [];
  String? _slugCorrente;

  Map<String, String> get _p => widget.parametri;

  @override
  void initState() {
    super.initState();
    _fase = _p['id'] != null ? FaseLettura.intervista : FaseLettura.preparazione;
    _id = _p['id'];
    _tema = temaDi(comeCategoria(_p['type']));
    _stesaId = _p['spread'];
    _domandaToccata = _p['question'] != null;
    _domanda.text = _p['question'] ?? '';
    _domanda.addListener(() {
      if (!mounted) return;
      _set(() => _errore = null);
    });
    _scorri.addListener(_misuraFondo);
  }

  /// v9.5: la versione di questa pagina, coi nomi del server.
  String get _variante => widget.inChat ? VarianteLettura.chat : VarianteLettura.classica;

  @override
  void dispose() {
    _vivo = false;
    _scorri.removeListener(_misuraFondo);
    _scorri.dispose();
    _cambi.dispose();
    _voloPagina.dispose();
    _voloDialogo.dispose();
    _domanda.dispose();
    super.dispose();
  }

  /// Come `setState`, e il dialogo del rito si ridisegna con la pagina.
  void _set(VoidCallback f) {
    if (!mounted) return;
    setState(f);
    // ignore: invalid_use_of_protected_member, invalid_use_of_visible_for_testing_member
    _cambi.notifyListeners();
  }

  String _nuovoId() => 'b${++_contatore}';

  void _aggiungi(Autore autore, String testo, {String? titolo, bool macchina = false}) => _battute = [
    ..._battute,
    Battuta(id: _nuovoId(), autore: autore, testo: testo, titolo: titolo, macchina: macchina),
  ];

  void _traccia(String nome, [Map<String, Object?>? proprieta]) => ref.read(lanternaProvider).traccia(nome, proprieta);

  String get _lingua => ref.read(linguaProvider);

  bool get _autenticata => ref.read(sessioneProvider).autenticata;

  /* ---- dati derivati ---- */

  List<Stesa> _stese() => ref.watch(steseLetturaProvider(linguaContenuti(ref.watch(linguaProvider)))).value ?? const [];

  Stesa? _stesa(List<Stesa> stese) => stese.where((s) => s.id == _stesaId).firstOrNull;

  String _categoria(Stesa? stesa) =>
      stesa?.categoria ??
      (_tema == TemaLettura.amore
          ? 'compatibilita'
          : _tema == TemaLettura.lavoro
          ? 'lavoro'
          : 'standard');

  bool _speciale(String c) => c == 'compatibilita' || c == 'coppia';

  /// I mazzi con cui si può leggere: il predefinito e quelli posseduti (v8.5).
  List<Mazzo> _utilizzabili() {
    final miei = (ref.watch(mieiMazziLetturaProvider).value ?? const <int>[]).toSet();
    return [
      for (final m in ref.watch(mazziProvider).value ?? const <Mazzo>[])
        if (m.attivoOra && (m.predefinito || miei.contains(m.id))) m,
    ];
  }

  /// Il mazzo delle immagini: quello dell'indirizzo (`?deck=`), altrimenti il predefinito dell'utente.
  String? _slugMazzo() {
    final lista = ref.watch(mazziProvider).value ?? const <Mazzo>[];
    final deck = _p['deck'];
    final daIndirizzo = lista.where((m) => m.slug == deck && !m.predefinito && m.attivoOra).firstOrNull;
    if (daIndirizzo != null) return daIndirizzo.slug;
    final profilo = ref.watch(profiloProvider).value;
    return lista.where((m) => m.id == profilo?.mazzoPredefinitoId && !m.predefinito).firstOrNull?.slug;
  }

  String? _slugAttivo() => _mazzoLetturaFatto
      ? _mazzoLettura
      : _mazzoSceltoFatto
      ? _mazzoScelto
      : _slugMazzo();

  bool _senzaCrediti() {
    final c = ref.watch(contoProvider).value;
    if (c == null) return false;
    return c.limitiAttivi &&
        c.saldo <= 0 &&
        c.lettureComprese != true &&
        (c.uso['letture_al_giorno']?.restanti ?? 0) <= 0;
  }

  /* ---- gli effetti (come gli `useEffect` del sito) ---- */

  void _effetti(List<Stesa> stese, String categoria) {
    final sessione = ref.read(sessioneProvider);
    // La fase come passo dell'imbuto; mai la domanda né le carte.
    if (sessione.pronta && _faseTracciata != _fase) {
      _faseTracciata = _fase;
      _traccia('lettura_fase', {
        'fase': _fase.nome,
        'categoria': categoria,
        'anonima': !sessione.autenticata,
        'v2': true,
      });
    }
    final sorgente = _p['source'];
    if (!_sorgenteTracciata && sorgente != null) {
      _sorgenteTracciata = true;
      _traccia(sorgente == 'qr' ? 'qr_entry' : 'reading_entry', {'sorgente': sorgente, 'mazzo': _p['deck'] ?? ''});
    }
    // Una stesa dall'indirizzo decide anche il tema; senza stesa si propone la prima del tema.
    if (stese.isNotEmpty && _fase == FaseLettura.preparazione) {
      final daIndirizzo = _stesa(stese);
      if (daIndirizzo != null && !nelTema(daIndirizzo, _tema)) {
        _tema = temaDi(daIndirizzo.categoria);
      } else if (daIndirizzo == null) {
        final delTema = stese.where((s) => nelTema(s, _tema)).toList();
        final prima =
            delTema.where((s) => s.id == 'tre-carte' || s.posizioni.length == 3).firstOrNull ?? delTema.firstOrNull;
        if (prima != null) _stesaId = prima.id;
      }
    }
    // `?topic=`: la domanda proposta segue la lingua finché non la si tocca.
    final temaParam = _p['topic'];
    if (!_domandaToccata && temaParam != null) {
      final proposta = context.t.letturaTemi[temaParam];
      if (proposta != null && _domanda.text != proposta) _domanda.text = proposta;
    }
    // `?card=`: una domanda sulla carta, se la domanda è ancora vuota.
    final cartaParam = _p['card'];
    if (cartaParam != null && !_cartaProposta) {
      final carte = ref.watch(carteLetturaProvider(linguaContenuti(ref.read(linguaProvider)))).value;
      if (carte != null && carte.isNotEmpty) {
        _cartaProposta = true;
        final c = carte
            .where((x) => x.id == cartaParam || x.slug == cartaParam || x.slugs.values.contains(cartaParam))
            .firstOrNull;
        if (c != null && _domanda.text.isEmpty) {
          _domanda.text = context.t.lettura_domanda_carta(nomeCarta(c, _lingua));
        }
      }
    }
    // I dati del partner ricordato.
    final profilo = ref.watch(profiloProvider).value;
    if (!_precompilato && profilo != null) {
      _precompilato = true;
      _persone = personeDaProfilo(profilo, _persone);
    }
    // v9.5: chi ha un account ha la sua versione nel profilo (la prima con cui ha letto): se questa pagina è l'altra,
    // si passa a quella giusta con gli stessi parametri, e il dispositivo si allinea (lo smistatore lo legge). Non con
    // `?anteprima=`: la versione l'ha scelta un admin tenendo premuto «Inizia una lettura».
    final sua = profilo?.varianteLettura;
    if (!_varianteAllineata && VarianteLettura.valida(sua) && _p['anteprima'] == null) {
      _varianteAllineata = true;
      final archivio = ref.read(archivioProvider);
      if (archivio.leggi(chiaveVarianteLettura) != sua) unawaited(archivio.scrivi(chiaveVarianteLettura, sua));
      if (sua != _variante) {
        final verso = Uri(path: VarianteLettura.percorso(sua!), queryParameters: _p.isEmpty ? null : _p).toString();
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted) GoRouter.of(context).replace<void>(verso);
        });
      }
    }
    // La ripresa di una lettura (`?id=`).
    if (_p['id'] != null && !_caricata && sessione.pronta) {
      _caricata = true;
      WidgetsBinding.instance.addPostFrameCallback((_) => unawaited(_riprendiDaId(_p['id']!)));
    }
    // Sul telefono tipo e schema si scelgono in due dialoghi all'apertura della pagina.
    final stretto = MediaQuery.sizeOf(context).width.telefono;
    if (stretto && _fase == FaseLettura.preparazione && !_dialoghiAvviati && _p['id'] == null) {
      _dialoghiAvviati = true;
      if (_p['spread'] == null) WidgetsBinding.instance.addPostFrameCallback((_) => unawaited(_sceltaTipoMobile()));
    }
    // Il rito in dialogo sul telefono.
    WidgetsBinding.instance.addPostFrameCallback((_) => _allineaDialogoRito());
  }

  /* ---- la ripresa ---- */

  Future<void> _riprendiDaId(String id) async {
    if (!_autenticata) {
      // Una lettura anonima non si riprende: si ricomincia dalla domanda.
      _set(() {
        _fase = FaseLettura.preparazione;
        _id = null;
      });
      return;
    }
    try {
      final lt = await ref.read(apiProvider).lettura(id);
      _riprendi(lt);
      final ultima = lt.interview.lastOrNull;
      if (lt.status == 'intervista' && (ultima == null || ultima.ruolo == 'utente')) {
        await _passoIntervista(lt.id, null);
      }
      _interpretaLeMieCarte();
    } on ErroreApi {
      _set(() {
        _fase = FaseLettura.preparazione;
        _id = null;
      });
    }
  }

  void _riprendi(Lettura lt) {
    _set(() {
      _mazzoLettura = lt.mazzo;
      _mazzoLetturaFatto = true;
      _stesaId = lt.spreadId;
      _tema = temaDi(lt.categoria);
      _nomePartner = lt.persone?.partner.nome;
      _linguaLettura = comeLingua(lt.lang);
      _manuale = lt.manuale;
      _domandaLettura = lt.question;
      _disclaimer = lt.disclaimer;
      _battute = [
        Battuta(id: _nuovoId(), autore: Autore.utente, testo: lt.question),
        for (final x in lt.interview)
          Battuta(id: _nuovoId(), autore: x.ruolo == 'utente' ? Autore.utente : Autore.oracolo, testo: x.testo),
        if (lt.contextSummary != null)
          Battuta(id: _nuovoId(), autore: Autore.oracolo, titolo: '✦', testo: lt.contextSummary!),
      ];
      _poste = lt.interview.where((x) => x.ruolo != 'utente').length;
      _modo = lt.interview.lastOrNull?.ruolo == 'utente' ? _ModoIntervista.libero : _ModoIntervista.risposta;
      _scelte = {...lt.pickedSlots};
      _slotTotali = lt.slotCount ?? 0;
      final ordinati = [...lt.cards]..sort((a, b) => a.posizione.compareTo(b.posizione));
      var k = 0;
      _posate = [
        for (final c in ordinati)
          Posata(
            posizione: c.posizione,
            slot: c.calcolata ? null : (k < lt.pickedSlots.length ? lt.pickedSlots[k++] : null),
            calcolata: c.calcolata,
            rivelata: c.rivelata,
            carta: c.carta,
            rovescio: c.rovescio,
            interpretazione: c.interpretazione,
            dignita: lt.dignita['${c.posizione}'],
          ),
      ];
      if (lt.synthesis != null) _testoResponso = lt.synthesis!;
      _fase = switch (lt.status) {
        'ventaglio' => FaseLettura.prontoMescolare,
        'scelta' => FaseLettura.scelta,
        'rivelazione' || 'sintesi' => FaseLettura.rivelazione,
        'completata' => FaseLettura.completata,
        'annullata' => FaseLettura.annullata,
        _ => FaseLettura.intervista,
      };
      if (lt.status == 'completata') {
        _fine = (disclaimer: lt.disclaimer, commitment: lt.commitment, saldo: null, anonimo: false);
      }
    });
  }

  /* ---- l'intervista ---- */

  Future<void> _passoIntervista(String id, String? risposta, {bool basta = false, bool altra = false}) async {
    _set(() {
      _attesa = true;
      _errore = null;
    });
    try {
      final passo = await ref.read(apiProvider).rispondi(id, risposta, basta: basta, altra: altra);
      // v9.5: il numero della domanda, per vedere dopo quante domande ci si ferma (mai il testo).
      if (risposta != null) _traccia('interview_answered', {'n': passo.poste ?? 0});
      _set(() {
        if (passo.minDomande != null && passo.maxDomande != null) {
          _minDomande = passo.minDomande!;
          _maxDomande = passo.maxDomande!;
        }
        if (passo.poste != null) _poste = passo.poste!;
        if (passo.crisi) {
          _aggiungi(Autore.sistema, passo.messaggio ?? '');
          _fase = FaseLettura.crisi;
        } else if (passo.completa) {
          _aggiungi(Autore.oracolo, passo.riassunto ?? '', titolo: '✦', macchina: true);
          // Le proprie carte («Interpreta le mie carte»): già estratte e posate, niente mescolata né taglio. Il
          // server è già passato alla rivelazione: l'interpretazione parte da sola.
          _fase = _manuale ? FaseLettura.rivelazione : FaseLettura.prontoMescolare;
        } else if (passo.scelta) {
          _modo = _ModoIntervista.libero;
        } else if (passo.domanda != null) {
          _traccia('interview_question', {'n': passo.poste ?? 0});
          _aggiungi(Autore.oracolo, passo.domanda!, macchina: true);
          _modo = _ModoIntervista.risposta;
        }
      });
    } on ErroreApi catch (e) {
      _set(() => _errore = e.messaggio(context.t));
    } finally {
      _set(() => _attesa = false);
    }
    _interpretaLeMieCarte();
  }

  /// Le proprie carte, a intervista finita: niente da mescolare né da scegliere, si leggono subito (una volta: se
  /// l'interpretazione non riesce resta il pulsante per riprovare).
  bool _interpretazioneAvviata = false;

  void _interpretaLeMieCarte() {
    if (!_manuale || _fase != FaseLettura.rivelazione || _interpretazioneAvviata || !_vivo) return;
    _interpretazioneAvviata = true;
    unawaited(_rivelaTutto());
  }

  /// Salva il testo scritto: la risposta alla domanda che aspetta (senza chiedere la successiva), o un testo libero.
  /// Falso se la lettura si è fermata (un segnale di crisi) o la chiamata non è riuscita.
  Future<bool> _salvaTesto(String id, String testo) async {
    _set(() {
      _aggiungi(Autore.utente, testo);
      _attesa = true;
      _errore = null;
    });
    try {
      if (_modo == _ModoIntervista.risposta) {
        final passo = await ref.read(apiProvider).rispondi(id, testo);
        _traccia('interview_answered', {'n': passo.poste ?? 0});
        _set(() {
          if (passo.minDomande != null && passo.maxDomande != null) {
            _minDomande = passo.minDomande!;
            _maxDomande = passo.maxDomande!;
          }
          if (passo.poste != null) _poste = passo.poste!;
          if (passo.crisi) {
            _aggiungi(Autore.sistema, passo.messaggio ?? '');
            _fase = FaseLettura.crisi;
          }
        });
        return !passo.crisi;
      }
      final esito = await ref.read(apiProvider).aggiungiAllIntervista(id, testo);
      if (esito.crisi) {
        _set(() {
          _aggiungi(Autore.sistema, esito.messaggio ?? '');
          _fase = FaseLettura.crisi;
        });
        return false;
      }
      _traccia('interview_addition', {'n': _poste});
      return true;
    } on ErroreApi catch (e) {
      _set(() => _errore = e.messaggio(context.t));
      return false;
    } finally {
      _set(() => _attesa = false);
    }
  }

  /// Un invio: prima il testo (se c'è), poi il passo scelto (`basta`, `altra`, `dire`).
  Future<void> _inviaIntervista(String testo, String dopo) async {
    final id = _id;
    if (id == null) return;
    _traccia('interview_choice', {
      'scelta': switch (dopo) {
        'basta' => 'lettura',
        'altra' => 'altra',
        _ => 'libero',
      },
      'n': _poste,
    });
    if (testo.isNotEmpty && !await _salvaTesto(id, testo)) return;
    if (dopo == 'dire') {
      _set(() => _modo = _ModoIntervista.libero);
      return;
    }
    if (dopo == 'basta') _traccia('interview_skipped', {'n': _poste});
    await _passoIntervista(id, null, basta: dopo == 'basta', altra: dopo == 'altra');
  }

  /// Quali invii: «basta» quando le domande con risposta arrivano al minimo (a campo vuoto, solo se il minimo c'è già
  /// senza la domanda che aspetta); «un'altra domanda» finché non si arriva al massimo (a campo vuoto solo se nessuna
  /// domanda aspetta); «voglio dire una cosa» sempre, con un testo.
  List<InvioDialogo> _invii(AppLocalizations t) {
    if (_fase != FaseLettura.intervista || _id == null) return const [];
    final aspetta = _modo == _ModoIntervista.risposta;
    final risposte = _poste - (aspetta ? 1 : 0);
    return [
      if (_poste >= _minDomande)
        InvioDialogo(
          chiave: 'basta',
          etichetta: t.lettura_invia_basta,
          etichettaVuoto: risposte >= _minDomande ? t.lettura_basta_domande : null,
          primaria: true,
          alInvio: (testo) => unawaited(_inviaIntervista(testo, 'basta')),
        ),
      if (_poste < _maxDomande)
        InvioDialogo(
          chiave: 'altra',
          etichetta: t.lettura_invia_altra,
          etichettaVuoto: aspetta ? null : t.lettura_altra_domanda,
          alInvio: (testo) => unawaited(_inviaIntervista(testo, 'altra')),
        ),
      InvioDialogo(
        chiave: 'dire',
        etichetta: aspetta ? t.lettura_invia_dire : t.lettura_invia_dire_ancora,
        alInvio: (testo) => unawaited(_inviaIntervista(testo, 'dire')),
      ),
    ];
  }

  /* ---- l'apertura ---- */

  void _scegliTipo(TemaLettura c) => _set(() {
    _tema = c;
    _errore = null;
    _personeFatte = false;
    _stesaId = null;
  });

  Future<void> _chiediInizio(String categoria, bool domandaValida, {bool salta = false}) async {
    final t = context.t;
    _set(() => _saltaIntervista = salta);
    if (!domandaValida) {
      _set(() => _errore = t.lettura_domanda_corta);
      return;
    }
    if (_stesaId == null) return;
    if (_speciale(categoria) && !_personeFatte) {
      _set(() => _fase = FaseLettura.persone);
      return;
    }
    if (_senzaCrediti()) {
      _traccia('paywall_viewed', {'dove': 'inizio'});
      await _mostraAcquisto();
      return;
    }
    // L'avvertenza si accetta una volta (casella «ho capito»), poi il telefono la ricorda: niente dialogo.
    final archivio = ref.read(archivioProvider);
    if (archivio.leggi(chiaveAvvertenza) == '1') {
      await _inizia();
      return;
    }
    if (_disclaimer == null) {
      try {
        _disclaimer = await ref.read(apiProvider).disclaimer(_lingua);
      } on ErroreApi {
        // il disclaimer arriva comunque con la lettura
      }
    }
    if (!mounted) return;
    final ok = await apriModale<bool>(
      context,
      titolo: t.lettura_avviso_titolo,
      costruisci: (context) => _Avvertenza(testo: _disclaimer ?? ''),
    );
    if (ok == true) {
      await archivio.scrivi(chiaveAvvertenza, '1');
      await _inizia();
    }
  }

  Future<void> _mostraAcquisto() async {
    final t = context.t;
    final ritorno = _id != null ? '${R.leggi}?id=$_id' : R.leggi;
    final scelta = await apriModale<bool>(
      context,
      titolo: t.lettura_crediti_finiti,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Paragrafo(t.lettura_crediti_finiti_testo, style: Stile.sans(15.2, colore: Token.inkSoft)),
          const SizedBox(height: 16),
          FilaBottoni(
            children: [
              Bottone(t.lettura_vedi_prezzi, alTocco: () => Navigator.of(context).pop(true)),
              Bottone(t.comune_chiudi, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop()),
            ],
          ),
        ],
      ),
    );
    if (scelta == true && mounted) vai(context, '${R.prezzi}?ritorno=${Uri.encodeComponent(ritorno)}');
  }

  Future<void> _dimenticaPartner() async {
    try {
      await ref.read(apiProvider).cancellaPartner();
      _set(() => _persone = _persone.senzaPartner());
      ref.invalidate(profiloProvider);
    } on ErroreApi catch (e) {
      _set(() => _errore = e.messaggio(context.t));
    }
  }

  Future<void> _inizia({int? etaAnni, String? oltreLimite}) async {
    final stesaId = _stesaId;
    if (stesaId == null) return;
    final t = context.t;
    final stese = ref.read(steseLetturaProvider(linguaContenuti(_lingua))).value ?? const <Stesa>[];
    final stesa = stese.where((s) => s.id == stesaId).firstOrNull;
    final categoria = _categoria(stesa);
    final speciale = _speciale(categoria);
    final nomeAltra = _persone.nome.trim();
    final testoDomanda = _domanda.text.trim().isNotEmpty
        ? _domanda.text.trim()
        : speciale
        ? (categoria == 'coppia' ? t.lettura_domanda_coppia(nomeAltra) : t.lettura_domanda_compat(nomeAltra))
        : '';
    _set(() {
      _inCorso = true;
      _errore = null;
    });
    final api = ref.read(apiProvider);
    try {
      if (speciale) {
        final profilo = ref.read(profiloProvider).value;
        final mancanti = profilo?.relazioni.mancanti ?? const <String>[];
        if (mancanti.isNotEmpty) {
          await api.aggiornaProfilo({
            if (mancanti.contains('genere')) ...{
              'gender': _persone.tuGenere,
              'gender_custom': _persone.tuGenere == 'altro' ? _persone.tuGenereAltro.trim() : null,
              'is_trans': _persone.tuTrans,
            },
            if (mancanti.contains('nascita')) 'birth_date': _persone.tuNascita,
          });
          ref.invalidate(profiloProvider);
        }
      }
      final slug = _slugAttivo();
      final mazzo = slug != null && _utilizzabiliLetti().any((m) => m.slug == slug && !m.predefinito) ? slug : null;
      final Apertura a;
      if (_autenticata) {
        a = await api.apriLettura(
          spreadId: stesaId,
          domanda: testoDomanda,
          lingua: _lingua,
          mazzo: mazzo,
          oltreLimite: oltreLimite,
          partner: speciale ? partnerDa(_persone) : null,
          ricordaPartner: speciale && _persone.ricorda,
          variante: _variante,
        );
      } else {
        // L'età confermata al primo avvio vale anche qui: il server non la richiede una seconda volta.
        a = await api.apriLetturaAnonima(
          spreadId: stesaId,
          domanda: testoDomanda,
          lingua: _lingua,
          etaAnni: etaAnni ?? ref.read(etaProvider).anniConfermati,
          variante: _variante,
        );
      }
      _traccia('reading_started', {'categoria': categoria, 'anonima': !_autenticata});
      if (a.crisi) {
        _set(() {
          _linguaLettura = null;
          _battute = [Battuta(id: _nuovoId(), autore: Autore.sistema, testo: a.messaggio ?? '')];
          _fase = FaseLettura.crisi;
        });
        return;
      }
      final id = a.id;
      if (id == null) return;
      _set(() {
        _linguaLettura = comeLingua(a.lang) ?? _lingua;
        _id = id;
        _caricata = true;
        _nomePartner = speciale ? nomeAltra : null;
        _domandaLettura = testoDomanda;
        _battute = [Battuta(id: _nuovoId(), autore: Autore.utente, testo: testoDomanda)];
        _fase = FaseLettura.intervista;
        _modo = _ModoIntervista.risposta;
        _poste = 0;
      });
      ref.invalidate(contoProvider);
      ref.invalidate(profiloProvider);
      if (_saltaIntervista) {
        // Senza domande: il quadro dalla sola domanda, poi subito la mescolata. Se il server rifiuta (il minimo è
        // cambiato nel frattempo), si fa l'intervista.
        _traccia('interview_choice', {'scelta': 'salta', 'n': 0});
        await _passoIntervista(id, null, basta: true);
        if (_fase == FaseLettura.prontoMescolare) {
          _mescola();
          return;
        }
        _set(() => _errore = null);
      }
      await _passoIntervista(id, null);
    } on ErroreApi catch (e) {
      await _erroreApertura(e);
    } finally {
      _set(() => _inCorso = false);
    }
  }

  List<Mazzo> _utilizzabiliLetti() {
    final miei = (ref.read(mieiMazziLetturaProvider).value ?? const <int>[]).toSet();
    return [
      for (final m in ref.read(mazziProvider).value ?? const <Mazzo>[])
        if (m.attivoOra && (m.predefinito || miei.contains(m.id))) m,
    ];
  }

  Future<void> _erroreApertura(ErroreApi e) async {
    final t = context.t;
    final codice = e.codice;
    final dettaglio = e.dettaglio;
    if ((e.stato == 403 || e.stato == 422) && (codice == 'eta_da_confermare' || codice == 'eta_insufficiente')) {
      final anni = dettaglio is Map && dettaglio['anni'] is num ? (dettaglio['anni'] as num).toInt() : 16;
      await _dialogoEta(anni, insufficiente: codice == 'eta_insufficiente');
    } else if (e.stato == 402 && codice == 'limite_superato' && dettaglio is Map<String, dynamic>) {
      final limite = LimiteSuperato.fromJson(dettaglio);
      _traccia('limit_reached', {'limite': limite.limite, 'scelta': limite.scelta});
      final ritorno = _id != null ? '${R.leggi}?id=$_id' : R.leggi;
      final scelta = await apriDialogoLimite(context, limite, ritorno: ritorno);
      if (scelta != null) await _inizia(oltreLimite: scelta);
    } else if (e.stato == 402) {
      _traccia('paywall_viewed', {'dove': 'apertura'});
      await _mostraAcquisto();
    } else if (e.stato == 409 && codice == 'lettura_gratuita_gia_usata') {
      await _dialogoGiaUsata();
    } else if (e.stato == 422 && codice == 'profilo_incompleto') {
      ref.invalidate(profiloProvider);
      _set(() {
        _errore = e.messaggio(t);
        _fase = FaseLettura.persone;
      });
    } else {
      _set(() => _errore = e.stato == 0 ? t.lettura_err_lettura : e.messaggio(t));
    }
  }

  /// Vero mentre si riprova l'apertura con l'età già confermata sul telefono (una volta sola, poi il dialogo).
  bool _etaRiprovata = false;

  /// «Ho almeno N anni» (`DialogoEta` del sito): chi conferma, rifà la lettura. Se il telefono l'ha già confermata
  /// (per esempio prima di entrare con l'account), niente dialogo: la conferma va al server e la lettura riparte.
  Future<void> _dialogoEta(int anni, {required bool insufficiente}) async {
    final t = context.t;
    final giaConfermati = ref.read(etaProvider).anniConfermati;
    if (!insufficiente && !_etaRiprovata && giaConfermati != null && giaConfermati >= anni) {
      _etaRiprovata = true;
      try {
        await ref.read(etaProvider.notifier).conferma(giaConfermati);
        await _inizia(etaAnni: giaConfermati);
      } finally {
        _etaRiprovata = false;
      }
      return;
    }
    final confermati = await apriModale<int>(
      context,
      titolo: insufficiente ? t.comune_eta_titolo_no : t.comune_eta_titolo,
      costruisci: (context) => _ContenutoEta(anni: anni, insufficiente: insufficiente),
    );
    if (confermati == null || !mounted) return;
    await ref.read(etaProvider.notifier).conferma(confermati);
    await _inizia(etaAnni: confermati);
  }

  /// La lettura gratuita è già stata usata su questo dispositivo: l'invito a creare un account.
  Future<void> _dialogoGiaUsata() async {
    final t = context.t;
    final registra = await apriModale<bool>(
      context,
      titolo: t.lettura_gia_usata_cta,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Paragrafo(t.app_gia_usata, style: Stile.sans(15.2, colore: Token.inkSoft)),
          const SizedBox(height: 16),
          FilaBottoni(
            children: [
              Bottone(
                t.lettura_gia_usata_cta,
                variante: Variante.ottone,
                alTocco: () => Navigator.of(context).pop(true),
              ),
            ],
          ),
        ],
      ),
    );
    if (registra == true) await _registrati();
  }

  Future<void> _registrati() async {
    _traccia('signup_started', {'dove': 'anteprima'});
    await entraDa(ref);
  }

  /* ---- mescolata, taglio, scelta ---- */

  void _mescola() {
    if (_id == null) return;
    _set(() {
      _errore = null;
      _fase = FaseLettura.mescolamento;
    });
    _traccia('shuffle_started');
  }

  void _fermaMescolata() {
    _set(() => _fase = FaseLettura.taglio);
    _traccia('shuffle_interrupted');
  }

  Future<void> _taglia(double frazione) async {
    final id = _id;
    if (id == null) return;
    try {
      final v = await ref.read(apiProvider).apriVentaglio(id, taglio: frazione);
      _traccia('deck_cut');
      _set(() {
        _slotTotali = v.slotCount;
        _scelte = {...v.pickedSlots};
        _fase = FaseLettura.scelta;
      });
    } on ErroreApi catch (e) {
      _set(() {
        _errore = e.stato == 0 ? context.t.lettura_err_mazzo : e.messaggio(context.t);
        _fase = FaseLettura.prontoMescolare;
      });
    }
  }

  Future<void> _scegli(int slot, Stesa stesa) async {
    final id = _id;
    if (id == null || _scegliendo || _scelte.contains(slot)) return;
    _scegliendo = true;
    final partenza = _volo.partenza(slot);
    try {
      final r = await ref.read(apiProvider).scegliCarta(id, slot);
      _traccia('card_drawn');
      _set(() {
        _scelte = {..._scelte, slot};
        _posate = [
          ..._posate,
          Posata(posizione: r.posizione, slot: slot, calcolata: false, rivelata: false),
          if (r.tutteScelte)
            for (final n in r.posizioniCalcolate) Posata(posizione: n, calcolata: true, rivelata: false),
        ];
      });
      if (partenza != null && mounted) {
        final arrivo = stesa.posizioni.where((p) => p.n == r.posizione).firstOrNull?.rotazione ?? 0;
        unawaited(_volo.vola(_scena.currentContext ?? context, r.posizione, partenza, arrivo));
      }
      if (r.tutteScelte) {
        await Future<void>.delayed(const Duration(milliseconds: 700));
        if (_vivo) _set(() => _fase = FaseLettura.rivelazione);
      }
    } on ErroreApi catch (e) {
      _set(() => _errore = e.stato == 0 ? context.t.lettura_err_posa : e.messaggio(context.t));
    } finally {
      _scegliendo = false;
    }
  }

  /* ---- la rivelazione e l'interpretazione ---- */

  void _aggiornaPosata(int posizione, Posata Function(Posata p) f) =>
      _set(() => _posate = [for (final p in _posate) p.posizione == posizione ? f(p) : p]);

  /// Una carta si gira e la sua spiegazione arriva in streaming. Falso se qualcosa è andato storto.
  Future<bool> _rivelaCarta(String id, int posizione) async {
    _set(() => _errore = null);
    try {
      await for (final ev in ref.read(apiProvider).rivela(id, posizione)) {
        if (!_vivo) return false;
        switch (ev) {
          case EventoCarta():
            _traccia('card_revealed');
            _aggiornaPosata(
              posizione,
              (p) => Posata(
                posizione: p.posizione,
                slot: p.slot,
                calcolata: p.calcolata,
                rivelata: true,
                carta: ev.carta,
                rovescio: ev.rovescio,
                dignita: ev.dignita,
                doppia: ev.doppiaValenza,
                interpretazione: '',
              ),
            );
            _set(() => _lettoreLegge = true);
          case EventoToken():
            _set(() => _lettoreLegge = false);
            _aggiornaPosata(posizione, (p) => p.copia(interpretazione: (p.interpretazione ?? '') + ev.testo));
          case EventoSostituisci():
            _aggiornaPosata(posizione, (p) => p.copia(interpretazione: ev.testo));
          case EventoErrore():
            _set(() {
              _lettoreLegge = false;
              _errore = ev.messaggio;
            });
            return false;
          case EventoFineRivelazione():
            _set(() => _lettoreLegge = false);
            if (ev.interpretazione.isNotEmpty) {
              _aggiornaPosata(posizione, (p) => p.copia(interpretazione: ev.interpretazione));
            }
          default:
            break;
        }
      }
      return true;
    } on ErroreApi catch (e) {
      _set(() => _errore = e.stato == 0 ? context.t.lettura_err_giro : e.messaggio(context.t));
      return false;
    } on FormatException {
      _set(() => _errore = context.t.lettura_err_giro);
      return false;
    } finally {
      _set(() => _lettoreLegge = false);
    }
  }

  /// Tutte le carte insieme (v8.6): si girano subito, poi un solo momento d'attesa («il tuo lettore sta leggendo le
  /// carte…») mentre una chiamata sola le interpreta tutte, poi le spiegazioni carta per carta. `null`: il server non
  /// conosce ancora lo svelamento di tutte le carte (404/405), si torna a una carta alla volta.
  Future<bool?> _rivelaInsieme(String id) async {
    _set(() => _errore = null);
    var riuscita = true;
    try {
      await for (final ev in ref.read(apiProvider).rivelaTutte(id)) {
        if (!_vivo) return false;
        switch (ev) {
          case EventoCarta():
            _traccia('card_revealed');
            _aggiornaPosata(
              ev.posizione,
              (p) => Posata(
                posizione: p.posizione,
                slot: p.slot,
                calcolata: p.calcolata,
                rivelata: true,
                carta: ev.carta,
                rovescio: ev.rovescio,
                dignita: ev.dignita,
                doppia: ev.doppiaValenza,
                interpretazione: '',
              ),
            );
          case EventoFase(fase: 'lettura'):
            _set(() => _lettoreLegge = true);
          case EventoToken(:final posizione?):
            _set(() => _lettoreLegge = false);
            _aggiornaPosata(posizione, (p) => p.copia(interpretazione: (p.interpretazione ?? '') + ev.testo));
          case EventoSostituisci(:final posizione?):
            _aggiornaPosata(posizione, (p) => p.copia(interpretazione: ev.testo));
          case EventoErrore():
            // Una carta senza spiegazione (la ritroverà nel responso): le altre arrivano lo stesso.
            _set(() {
              _lettoreLegge = false;
              _errore = ev.messaggio;
            });
            riuscita = false;
          case EventoFineRivelazione():
            _set(() => _lettoreLegge = false);
            if (ev.interpretazione.isNotEmpty) {
              _aggiornaPosata(ev.posizione, (p) => p.copia(interpretazione: ev.interpretazione));
            }
          default:
            break;
        }
      }
      return riuscita;
    } on ErroreApi catch (e) {
      if (e.stato == 404 || e.stato == 405) return null;
      _set(() => _errore = e.stato == 0 ? context.t.lettura_err_giro : e.messaggio(context.t));
      return false;
    } on FormatException {
      _set(() => _errore = context.t.lettura_err_giro);
      return false;
    } finally {
      _set(() => _lettoreLegge = false);
    }
  }

  /// Una sola fase (v8.5): le carte si girano, ciascuna con la sua spiegazione, poi arriva l'interpretazione
  /// dell'insieme. Dalla v8.6 le carte si girano tutte insieme e una chiamata sola le interpreta.
  Future<void> _rivelaTutto() async {
    final id = _id;
    if (id == null || _rivelazioneInCorso) return;
    _set(() {
      _rivelazioneInCorso = true;
      _ritoChiuso = true;
      _fase = FaseLettura.svelamento;
    });
    unawaited(
      Future<void>.delayed(
        const Duration(milliseconds: 250),
        () => widget.inChat ? null : _portaInVista(_zonaResponso, allineamento: 0),
      ),
    );
    try {
      final coperte = [
        for (final p in _posate)
          if (!p.rivelata) p.posizione,
      ]..sort();
      if (coperte.isNotEmpty) {
        final esito = await _rivelaInsieme(id);
        if (esito == null) {
          for (final n in coperte) {
            if (!await _rivelaCarta(id, n)) {
              _set(() => _fase = FaseLettura.rivelazione);
              return;
            }
          }
        } else if (!esito) {
          _set(() => _fase = FaseLettura.rivelazione);
          return;
        }
      }
      await _chiediResponso(id);
    } finally {
      _set(() => _rivelazioneInCorso = false);
    }
  }

  Future<void> _chiediResponso(String id) async {
    _set(() {
      _fase = FaseLettura.sintesi;
      _faseResponso = 'unione';
      _testoResponso = '';
      _errore = null;
    });
    try {
      await for (final ev in ref.read(apiProvider).sintesi(id)) {
        if (!_vivo) return;
        switch (ev) {
          case EventoFase():
            _set(() => _faseResponso = ev.fase);
          case EventoToken():
            _set(() => _testoResponso += ev.testo);
          case EventoErrore():
            _set(() {
              _errore = ev.messaggio;
              _fase = FaseLettura.rivelazione;
            });
            return;
          case EventoFineSintesi():
            _set(() {
              _fine = (disclaimer: ev.disclaimer, commitment: ev.commitment, saldo: ev.saldo, anonimo: ev.anonimo);
              _fase = FaseLettura.completata;
            });
            _traccia('reading_completed', {'anonima': ev.anonimo});
            ref.invalidate(contoProvider);
          default:
            break;
        }
      }
    } on ErroreApi catch (e) {
      _set(() {
        _errore = e.stato == 0 ? context.t.lettura_err_responso : e.messaggio(context.t);
        _fase = FaseLettura.rivelazione;
      });
    } on FormatException {
      _set(() {
        _errore = context.t.lettura_err_responso;
        _fase = FaseLettura.rivelazione;
      });
    }
  }

  void _nuova() {
    _set(() {
      _fase = FaseLettura.preparazione;
      _tema = TemaLettura.standard;
      _stesaId = null;
      _nomePartner = null;
      _personeFatte = false;
      _id = null;
      _battute = [];
      _posate = [];
      _scelte = {};
      _testoResponso = '';
      _fine = null;
      _linguaLettura = null;
      _manuale = false;
      _interpretazioneAvviata = false;
      _mazzoLetturaFatto = false;
      _caricata = true;
      _modo = _ModoIntervista.risposta;
      _poste = 0;
    });
    _domanda.clear();
    ref.invalidate(profiloProvider);
    if (_scorri.hasClients) {
      unawaited(_scorri.animateTo(0, duration: const Duration(milliseconds: 400), curve: Curves.ease));
    }
  }

  Future<void> _stampa(String id) async {
    try {
      final lt = await ref.read(apiProvider).lettura(id);
      await stampaLettura(ref, lt, interfaccia: _lingua);
    } on ErroreApi catch (e) {
      if (mounted) _set(() => _errore = e.messaggio(context.t));
    }
  }

  /* ---- i dialoghi del telefono ---- */

  Future<void> _sceltaTipoMobile() async {
    if (!mounted) return;
    final t = context.t;
    final scelto = await apriModale<TemaLettura>(
      context,
      titolo: t.lettura_tipo_titolo,
      costruisci: (context) => SceltaTipo(tema: _tema, conTitolo: false, alScegli: (c) => Navigator.of(context).pop(c)),
    );
    if (scelto == null || !mounted) return;
    _scegliTipo(scelto);
    await _sceltaStesaMobile();
  }

  Future<void> _sceltaStesaMobile() async {
    if (!mounted) return;
    final t = context.t;
    final indietro = await apriModale<bool>(
      context,
      titolo: t.lettura_stesa_titolo,
      larga: true,
      costruisci: (dialogo) => Consumer(
        builder: (dialogo, ref, _) {
          final stese =
              ref.watch(steseLetturaProvider(linguaContenuti(ref.watch(linguaProvider)))).value ?? const <Stesa>[];
          final categoria = _categoria(_stesa(stese));
          final sessione = ref.watch(sessioneProvider);
          final serveAccount = _speciale(categoria) && sessione.pronta && !sessione.autenticata;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (serveAccount)
                _AvvisoAccount(alEntra: () => unawaited(entraDa(ref)))
              else
                SceltaStesa(
                  stese: [
                    for (final s in stese)
                      if (nelTema(s, _tema)) s,
                  ],
                  scelta: _stesaId,
                  conTitolo: false,
                  conStili: _tema == TemaLettura.amore,
                  alScegli: (s) {
                    _set(() => _stesaId = s);
                    Navigator.of(dialogo).pop(false);
                  },
                ),
              const SizedBox(height: 16),
              FilaBottoni(
                children: [
                  Bottone(t.comune_indietro, variante: Variante.quieto, alTocco: () => Navigator.of(dialogo).pop(true)),
                ],
              ),
            ],
          );
        },
      ),
    );
    if (indietro == true) await _sceltaTipoMobile();
  }

  bool _ritoInDialogo() {
    final stretto = MediaQuery.sizeOf(context).width.telefono;
    return !widget.inChat &&
        stretto &&
        !_ritoChiuso &&
        const {
          FaseLettura.mescolamento,
          FaseLettura.taglio,
          FaseLettura.scelta,
          FaseLettura.rivelazione,
          FaseLettura.prontoSintesi,
        }.contains(_fase);
  }

  /// Apre o chiude il dialogo scuro del rito secondo la fase.
  void _allineaDialogoRito() {
    if (!mounted) return;
    final serve = _ritoInDialogo();
    if (serve && _dialogoRito == null) {
      final t = context.t;
      final rotta = RawDialogRoute<void>(
        barrierDismissible: true,
        barrierLabel: t.comune_chiudi,
        barrierColor: const Color(0x00000000),
        transitionDuration: Token.durataTransizione,
        transitionBuilder: (context, a, _, figlio) => FadeTransition(opacity: a, child: figlio),
        pageBuilder: (dialogo, _, _) => ListenableBuilder(
          listenable: _cambi,
          builder: (dialogo, _) {
            final stese = _steseCorrenti;
            final stesa = _stesa(stese);
            return FinestraModale(
              titolo: _stato(dialogo.t, stesa).etichetta,
              scura: true,
              larga: true,
              alChiudi: () => Navigator.of(dialogo).pop(),
              child: _ambito(_contenutoRito(dialogo, stesa, inDialogo: true), volo: _voloDialogo),
            );
          },
        ),
      );
      _dialogoRito = rotta;
      unawaited(
        Navigator.of(context, rootNavigator: true).push(rotta).then((_) {
          if (_dialogoRito == rotta) {
            _dialogoRito = null;
            // Chiuso da chi legge (✕, indietro, fuori): il rito resta nella pagina.
            if (_vivo && _ritoInDialogo()) _set(() => _ritoChiuso = true);
          }
        }),
      );
    } else if (!serve && _dialogoRito != null) {
      final rotta = _dialogoRito!;
      _dialogoRito = null;
      if (rotta.isActive) Navigator.of(context, rootNavigator: true).removeRoute(rotta);
    }
  }

  /// Il mazzo, il registro del volo e la lingua dei nomi attorno al rito (nella pagina e nel dialogo).
  Widget _ambito(Widget figlio, {VoloCarte? volo}) => MazzoAttivo(
    slug: _slugCorrente,
    child: AmbitoVolo(
      notifier: volo ?? _voloPagina,
      child: LinguaNomi(lingua: _linguaLettura, child: figlio),
    ),
  );

  /// v9.5, la chat: chi legge è in fondo se mancano meno di 180 px alla fine della pagina.
  void _misuraFondo() {
    if (!_scorri.hasClients) return;
    final p = _scorri.position;
    _inFondo = p.pixels >= p.maxScrollExtent - 180;
  }

  /// v9.5, la chat: la pagina segue una novità solo se chi legge è già in fondo (se sta rileggendo più su non si
  /// muove), e si ferma all'INIZIO del messaggio nuovo ([allInizio]: una domanda, il mazzo, una carta che si gira, il
  /// responso), non alla fine; i pulsanti invece si portano solo in vista.
  void _segui(BuildContext? contesto, {required bool allInizio}) {
    if (!widget.inChat || !_inFondo || contesto == null || !mounted || !_scorri.hasClients) return;
    final oggetto = contesto.findRenderObject();
    if (oggetto == null || !oggetto.attached) return;
    final viewport = RenderAbstractViewport.maybeOf(oggetto);
    if (viewport == null) return;
    final p = _scorri.position;
    final verso = allInizio
        ? viewport.getOffsetToReveal(oggetto, 0).offset - 12
        : math.max(p.pixels, viewport.getOffsetToReveal(oggetto, 1).offset + 12);
    final meta = verso.clamp(p.minScrollExtent, p.maxScrollExtent);
    if ((meta - p.pixels).abs() < 2) return;
    if (MediaQuery.disableAnimationsOf(context)) {
      _scorri.jumpTo(meta);
    } else {
      unawaited(_scorri.animateTo(meta, duration: const Duration(milliseconds: 400), curve: Curves.ease));
    }
  }

  /// v9.5, la chat: dopo ogni disegno, se è cambiata la fase, il numero di carte girate o il responso, si segue
  /// l'inizio del blocco nuovo (il mazzo o le carte svelate). Le battute le segnala il dialogo ([_segui]).
  void _seguiRito() {
    if (!widget.inChat) return;
    final rivelate = _posate.where((p) => p.rivelata).length;
    final novita = '${_fase.nome}|$rivelate|${_testoResponso.isEmpty ? 0 : 1}';
    if (novita == _novita) return;
    final prima = _novita;
    _novita = novita;
    if (prima.isEmpty || _fase == FaseLettura.intervista) return;
    final suResponso =
        rivelate > 0 || const {FaseLettura.svelamento, FaseLettura.sintesi, FaseLettura.completata}.contains(_fase);
    final chiave = suResponso ? _zonaResponso : _zonaMazzo;
    Future<void>.delayed(const Duration(milliseconds: 120), () {
      if (_vivo) _segui(chiave.currentContext, allInizio: true);
    });
  }

  void _portaInVista(GlobalKey chiave, {double allineamento = .5}) {
    final ctx = chiave.currentContext;
    if (ctx == null || !mounted) return;
    unawaited(
      Scrollable.ensureVisible(
        ctx,
        alignment: allineamento,
        duration: MediaQuery.disableAnimationsOf(context) ? Duration.zero : const Duration(milliseconds: 400),
        curve: Curves.ease,
      ),
    );
  }

  /* ---- la pagina ---- */

  ({String etichetta, String? testo}) _stato(AppLocalizations t, Stesa? stesa) {
    final daScegliere = stesa == null ? 0 : stesa.carteDaScegliere - _posate.where((p) => !p.calcolata).length;
    return switch (_fase) {
      FaseLettura.intervista => (etichetta: t.lettura_console_intervista, testo: t.lettura_console_intervista_testo),
      FaseLettura.prontoMescolare => (etichetta: t.lettura_console_pronto, testo: t.lettura_console_pronto_testo),
      FaseLettura.mescolamento => (etichetta: t.lettura_console_mescola, testo: t.lettura_console_mescola_testo),
      FaseLettura.taglio => (etichetta: t.lettura_console_taglio, testo: t.lettura_console_taglio_testo),
      FaseLettura.scelta => (
        etichetta: t.lettura_console_scelta,
        testo: daScegliere == 1 ? t.lettura_scegli_uno : t.lettura_scegli_n(daScegliere),
      ),
      FaseLettura.rivelazione ||
      FaseLettura.prontoSintesi ||
      FaseLettura.svelamento => (etichetta: t.lettura_console_rivela, testo: t.lettura_console_rivela_testo),
      FaseLettura.crisi => (etichetta: t.lettura_crisi_titolo, testo: null),
      FaseLettura.annullata => (etichetta: t.lettura_pausa_titolo, testo: null),
      _ => (etichetta: t.lettura_console_sintesi, testo: null),
    };
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    final stese = _stese();
    final stesa = _stesa(stese);
    final categoria = _categoria(stesa);
    _steseCorrenti = stese;
    _slugCorrente = _slugAttivo();
    _effetti(stese, categoria);
    WidgetsBinding.instance.addPostFrameCallback((_) => _seguiRito());
    final preparazione = _fase == FaseLettura.preparazione || _fase == FaseLettura.persone;
    final sezioni = <Widget>[
      Sottotitolo(
        eyebrow: t.lettura_eyebrow,
        titolo: t.lettura_titolo,
        intro: sessione.autenticata ? t.lettura_intro_dentro : t.lettura_intro,
        compatta: true,
      ),
      if (preparazione) _preparazione(context, stese, stesa, categoria) else ..._lettura(context, stesa),
    ];
    return Pagina(controllore: _scorri, sezioni: sezioni);
  }

  /* ---- la preparazione ---- */

  /// «Invia quesito e inizia a mescolare le carte» (solo col minimo di domande a zero) e «Invia domanda e chiedimi
  /// pure»; nelle letture speciali, prima dei dati delle persone, solo «Avanti». Sul telefono uno per riga.
  Widget _inviiDomanda(
    AppLocalizations t,
    String categoria,
    bool domandaValida, {
    required bool speciale,
    required bool stretto,
  }) {
    final senzaMinimo = (ref.watch(impostazioniProvider).value?.intervistaMinDomande ?? 0) == 0;
    final bloccato = _stesaId == null || _inCorso;
    final bottoni = speciale && !_personeFatte
        ? [
            Bottone(
              _inCorso ? t.comune_carica : t.comune_avanti,
              variante: Variante.ottone,
              pieno: stretto,
              an: 'rito',
              anProprieta: const {'passo': 'inizia'},
              alTocco: bloccato ? null : () => unawaited(_chiediInizio(categoria, domandaValida)),
            ),
          ]
        : [
            if (senzaMinimo)
              Bottone(
                _inCorso && _saltaIntervista ? t.comune_carica : t.lettura_domanda_invia_mescola,
                variante: Variante.ottone,
                pieno: stretto,
                an: 'rito',
                anProprieta: const {'passo': 'inizia_mescola'},
                alTocco: bloccato || !domandaValida
                    ? null
                    : () => unawaited(_chiediInizio(categoria, domandaValida, salta: true)),
              ),
            Bottone(
              _inCorso && !_saltaIntervista ? t.comune_carica : t.lettura_domanda_invia_chiedi,
              variante: senzaMinimo ? Variante.quieto : Variante.ottone,
              pieno: stretto,
              an: 'rito',
              anProprieta: const {'passo': 'inizia'},
              alTocco: bloccato || !domandaValida ? null : () => unawaited(_chiediInizio(categoria, domandaValida)),
            ),
          ];
    return Padding(
      padding: const EdgeInsets.only(top: 12.8),
      child: stretto
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final (k, b) in bottoni.indexed) ...[if (k > 0) const SizedBox(height: 8), b],
              ],
            )
          : Wrap(spacing: 8, runSpacing: 8, children: bottoni),
    );
  }

  Widget _preparazione(BuildContext context, List<Stesa> stese, Stesa? stesa, String categoria) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    final lingua = ref.watch(linguaProvider);
    final speciale = _speciale(categoria);
    final serveAccount = speciale && sessione.pronta && !sessione.autenticata;
    final stretto = MediaQuery.sizeOf(context).width.telefono;
    final sceltaInline = !stretto;
    final domandaValida = speciale || _domanda.text.trim().length >= 3;
    final domandaPredefinita = speciale
        ? (categoria == 'coppia'
              ? t.lettura_domanda_coppia(_persone.nome.trim())
              : t.lettura_domanda_compat(_persone.nome.trim()))
        : '';
    final utilizzabili = _utilizzabili();
    final steseErrore = ref.watch(steseLetturaProvider(linguaContenuti(lingua))).error;

    final conversazione = _PannelloLettura(
      chiaro: true,
      children: [
        Eyebrow(t.lettura_pannello_conversazione),
        if (_fase == FaseLettura.preparazione) ...[
          _TitoloPannello(t.lettura_domanda_titolo),
          _CampoDomanda(
            controllore: _domanda,
            etichetta: t.lettura_domanda_etichetta,
            segnaposto: speciale && domandaPredefinita.isNotEmpty ? domandaPredefinita : t.lettura_domanda_segnaposto,
            alCambio: () {
              _domandaToccata = true;
            },
            alFuoco: () => _traccia('question_started'),
          ),
          if (speciale)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Paragrafo(t.lettura_domanda_facoltativa, style: stilePiccolo()),
            ),
          // I due invii, subito sotto la domanda: senza intervista (solo col minimo di domande a zero) o con.
          if (!serveAccount) _inviiDomanda(t, categoria, domandaValida, speciale: speciale, stretto: stretto),
          if (!domandaValida && _domanda.text.isNotEmpty) Avviso(t.lettura_domanda_corta, sopra: 12),
          if (_errore != null) Errore(_errore!, sopra: 12),
          if (sceltaInline)
            SceltaTipo(tema: _tema, alScegli: _scegliTipo)
          else
            _RiassuntoScelta(
              tema: testiTema(t, _tema).nome,
              stesa: stesa == null ? null : nomeStesa(stesa, lingua),
              alCambia: () => unawaited(_sceltaTipoMobile()),
            ),
          if (utilizzabili.length > 1)
            SceltaMazzo(
              mazzi: utilizzabili,
              scelto: _slugAttivo(),
              alScegli: (s) => _set(() {
                _mazzoScelto = s;
                _mazzoSceltoFatto = true;
              }),
            ),
          if (serveAccount)
            _AvvisoAccount(alEntra: () => unawaited(entraDa(ref)))
          else if (sceltaInline && stese.isNotEmpty)
            SceltaStesa(
              stese: [
                for (final s in stese)
                  if (nelTema(s, _tema)) s,
              ],
              scelta: _stesaId,
              conStili: _tema == TemaLettura.amore,
              alScegli: (s) => _set(() => _stesaId = s),
            ),
          if (steseErrore != null) Errore(messaggioErrore(steseErrore, t)),
        ] else ...[
          _TitoloPannello(t.lettura_persone_titolo),
          FormPersone(
            dati: _persone,
            alCambia: (d) => _set(() => _persone = d),
            profilo: ref.watch(profiloProvider).value,
            errore: _errore,
            alDimentica: () => unawaited(_dimenticaPartner()),
            alAvanti: () => _set(() {
              _errore = null;
              _personeFatte = true;
              _fase = FaseLettura.preparazione;
            }),
          ),
          Padding(
            padding: const EdgeInsets.only(top: 12.8),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              child: Bottone(
                t.comune_indietro,
                piccolo: true,
                variante: Variante.quieto,
                alTocco: () => _set(() => _fase = FaseLettura.preparazione),
              ),
            ),
          ),
        ],
      ],
    );

    final pronto = _fase == FaseLettura.preparazione && !serveAccount;
    final rito = _PannelloLettura(
      chiaro: false,
      children: [
        Eyebrow(t.lettura_pannello_rito, colore: Colori.eyebrowScuro),
        _Console(
          spazio: 16,
          children: [
            // Gli invii stanno sotto la domanda, nel pannello della conversazione.
            Semantics(header: true, child: Text(t.lettura_console_attesa.toUpperCase(), style: stileStatoConsole())),
            if (!(stesa != null && pronto)) _TestoConsole(t.lettura_console_attesa_testo),
            if (stesa != null && pronto)
              Facoltativo(
                titolo: t.lettura_stesa_info,
                child: StesaNellaConsole(stesa: stesa),
              ),
            if (pronto) Facoltativo(titolo: t.lettura_vero_info, child: const DichiarazioneBreve()),
            if (_senzaCrediti())
              Avviso(
                null,
                scuro: true,
                sopra: 0,
                figlio: Wrap(
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Text('${t.lettura_crediti_finiti}. ', style: Stile.sans(14.4, colore: const Color(0xFFEADBE9))),
                    Collegamento(
                      t.lettura_vedi_prezzi,
                      href: R.prezzi,
                      stile: Stile.sans(14.4, colore: Token.brassPale),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ],
    );

    return Fascia(
      compatta: true,
      // v9.5, la chat: anche la preparazione in una colonna sola.
      child: widget.inChat
          ? Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: _larghezzaChat),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [conversazione, const SizedBox(height: 16), rito],
                ),
              ),
            )
          : PannelliLettura(sinistra: conversazione, destra: rito),
    );
  }

  /* ---- la lettura ---- */

  List<Widget> _lettura(BuildContext context, Stesa? stesa) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    final lingua = ref.watch(linguaProvider);
    final ll = _linguaLettura ?? lingua;
    final tl = lookupAppLocalizations(Locale(ll));
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final inRito = _fase != FaseLettura.intervista;
    final ritoInDialogo = _ritoInDialogo();
    final stato = _stato(t, stesa);
    final (apre, chiude) = virgolette(lingua);
    final omaggi = ref.watch(impostazioniProvider).value?.creditiIscrizione ?? 3;

    final scena = Padding(
      padding: const EdgeInsets.only(bottom: 22.4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            [
              if (stesa != null) '${nomeStesa(stesa, ll)} · ${tl.lettura_n_carte(stesa.posizioni.length)}',
              if (_nomePartner != null) tl.lettura_tu_e(_nomePartner!),
            ].join(' · ').toUpperCase(),
            style: Stile.sans(11.84, peso: FontWeight.w700, em: .1, colore: Token.verdigris),
          ),
          if (_domandaLettura.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 4.8),
              child: Text(
                '$apre$_domandaLettura$chiude',
                style: Stile.serif(
                  MediaQuery.sizeOf(context).width.clampVw(20, 2.6, 27.2),
                  altezza: 1.35,
                  stile: FontStyle.italic,
                  colore: Token.ink,
                ),
              ),
            ),
        ],
      ),
    );

    final conversazione = _PannelloLettura(
      chiaro: true,
      children: [
        Eyebrow(t.lettura_pannello_conversazione),
        Dialogo(
          battute: _battute,
          attesa: _attesa,
          inputAttivo: _fase == FaseLettura.intervista && _id != null,
          libero: _modo == _ModoIntervista.libero,
          invii: _invii(t),
          fluido: widget.inChat,
          alNovita: _segui,
        ),
        if (_errore != null && _fase == FaseLettura.intervista)
          Padding(
            padding: const EdgeInsets.only(top: 12.8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Errore(_errore!, sopra: 0),
                if (_id != null && !_attesa)
                  Padding(
                    padding: const EdgeInsets.only(top: 9.6),
                    child: Bottone(
                      t.lettura_riprova,
                      piccolo: true,
                      variante: Variante.quieto,
                      alTocco: () => unawaited(_passoIntervista(_id!, null)),
                    ),
                  ),
              ],
            ),
          ),
      ],
    );

    final rito = KeyedSubtree(
      key: _zonaMazzo,
      child: _PannelloLettura(
        chiaro: false,
        rito: telefono && inRito,
        children: [
          if (!(telefono && inRito)) Eyebrow(t.lettura_pannello_rito, colore: Colori.eyebrowScuro),
          if (ritoInDialogo)
            _Console(
              spazio: telefono ? 8.8 : 16,
              children: [
                _Istruzione(stato.etichetta, pillola: telefono),
                Bottone(
                  t.lettura_rito_riapri,
                  variante: Variante.chiaro,
                  alTocco: () => _set(() => _ritoChiuso = false),
                ),
              ],
            )
          else
            _contenutoRito(context, stesa, inDialogo: false),
        ],
      ),
    );

    final mostraResponso =
        (_fase == FaseLettura.svelamento ||
            _fase == FaseLettura.sintesi ||
            _fase == FaseLettura.completata ||
            _posate.any((p) => p.rivelata)) &&
        stesa != null &&
        _id != null;

    final w = MediaQuery.sizeOf(context).width;
    // v9.5, la chat: una colonna sola, la conversazione e sotto, quando serve, il rito come un messaggio.
    final pannelli = widget.inChat
        ? Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: _larghezzaChat),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  conversazione,
                  if (inRito) Padding(padding: const EdgeInsets.only(top: 16), child: rito),
                ],
              ),
            ),
          )
        : PannelliLettura(sinistra: conversazione, destra: rito, primaDestra: inRito);
    return [
      _ambito(
        KeyedSubtree(
          key: _scena,
          child: Fascia(
            compatta: true,
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [scena, pannelli]),
          ),
        ),
      ),
      if (mostraResponso)
        KeyedSubtree(
          key: _zonaResponso,
          child: _ambito(
            Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  maxWidth: widget.inChat ? _larghezzaChat + 2 * w.gutter : Token.larghezzaBanda,
                ),
                child: Padding(
                  padding: EdgeInsets.fromLTRB(w.gutter, 0, w.gutter, w.telefono ? 16 : w.clampVw(16, 1.75, 22.4)),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      CarteSvelate(
                        stesa: stesa,
                        posate: _posate,
                        attiva: _fase == FaseLettura.svelamento || _rivelazioneInCorso,
                        lettoreLegge: _lettoreLegge,
                      ),
                      if (_fase == FaseLettura.sintesi && _testoResponso.isEmpty) FaseResponso(fase: _faseResponso),
                      if (_testoResponso.isNotEmpty)
                        Responso(
                          id: _id!,
                          testo: _testoResponso,
                          finito: _fase == FaseLettura.completata,
                          disclaimer: _fine?.disclaimer ?? _disclaimer ?? '',
                          commitment: _fine?.commitment,
                          saldo: _fine?.saldo,
                          anonimo: _fine?.anonimo ?? !sessione.autenticata,
                          omaggi: omaggi,
                          alNuova: _nuova,
                          alRegistrati: () => unawaited(_registrati()),
                          alCondividi: () => unawaited(apriCondivisione(context, id: _id!)),
                          alVai: (href) => vai(context, href),
                          alStampa: () => unawaited(_stampa(_id!)),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
    ];
  }

  /// La console del rito: l'istruzione, il tavolo, il mazzo (mescolata, taglio, ventaglio) e i comandi.
  Widget _contenutoRito(BuildContext context, Stesa? stesa, {required bool inDialogo}) {
    final t = context.t;
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final inRito = _fase != FaseLettura.intervista;
    final stato = _stato(t, stesa);
    // Sul telefono durante il rito (e nel dialogo) niente spiegazioni lunghe (`.soloAmpio`).
    final soloAmpio = !(telefono && inRito) && !inDialogo;
    final daScegliere = stesa == null ? 0 : stesa.carteDaScegliere - _posate.where((p) => !p.calcolata).length;
    final prossimaDaRivelare = _posate
        .where((p) => !p.rivelata)
        .map((p) => p.posizione)
        .fold<int?>(null, (m, n) => m == null || n < m ? n : m);
    final occupate = {for (final p in _posate) p.posizione};
    final prossimaDaScegliere = stesa?.posizioni.where((p) => !p.calcolata && !occupate.contains(p.n)).firstOrNull?.n;
    final durata = MediaQuery.disableAnimationsOf(context) ? Duration.zero : const Duration(milliseconds: 300);

    final Widget? zona = switch (_fase) {
      FaseLettura.mescolamento => Mescolamento(key: const ValueKey('m'), alFerma: _fermaMescolata),
      FaseLettura.taglio => SizedBox(
        key: const ValueKey('t'),
        width: double.infinity,
        child: Taglio(alTaglia: (f) => unawaited(_taglia(f))),
      ),
      _ => null,
    };

    // L'istruzione di ogni passo sta 5 px sopra il mazzo, grande (`_IstruzioneCarte`): per la mescolata è anche il
    // pulsante che la ferma. Durante taglio e scelta non si ripete in cima alla console.
    // Ogni mazzo lascia sopra le carte un margine per le sue animazioni (mescolata 18 + 10, taglio 8 + 12, ventaglio
    // 30): il mazzo sale di tanto, così le carte restano a 5 px dalla scritta.
    final (istruzioneCarte, margineMazzo) = switch (_fase) {
      FaseLettura.mescolamento => (_IstruzioneCarte(t.lettura_ferma, alTocco: _fermaMescolata), 28.0),
      FaseLettura.taglio => (_IstruzioneCarte(t.lettura_console_taglio), 20.0),
      FaseLettura.scelta => (
        _IstruzioneCarte(daScegliere == 1 ? t.lettura_scegli_uno : t.lettura_scegli_n(daScegliere)),
        30.0,
      ),
      _ => (null, 0.0),
    };
    final sopraLeCarte = _fase == FaseLettura.taglio || _fase == FaseLettura.scelta;

    return _Console(
      spazio: inDialogo ? 9.6 : (telefono && inRito ? 8.8 : 16),
      children: [
        if (!inDialogo && !sopraLeCarte) _Istruzione(stato.etichetta, pillola: telefono && inRito),
        if (stato.testo != null && soloAmpio && _fase != FaseLettura.scelta) _TestoConsole(stato.testo!),
        if (_fase == FaseLettura.scelta && soloAmpio)
          Paragrafo(t.lettura_console_scelta_sigillo, style: Stile.sans(13.44, colore: const Color(0xFFD9CADE))),
        if (stesa != null && _fase != FaseLettura.crisi)
          Tavolo(
            stesa: stesa,
            posate: _posate,
            prossima: _fase == FaseLettura.scelta
                ? prossimaDaScegliere
                : _fase == FaseLettura.rivelazione
                ? prossimaDaRivelare
                : null,
            alRivela: (_) => unawaited(_rivelaTutto()),
            rivelazioneInCorso: _rivelazioneInCorso,
            evidenzia: _fase == FaseLettura.scelta
                ? Evidenzia.scelta
                : _fase == FaseLettura.rivelazione
                ? Evidenzia.rivelazione
                : null,
            nomePartner: _nomePartner,
            manuale: _manuale,
          ),
        if (zona != null || _fase == FaseLettura.scelta)
          SizedBox(
            width: double.infinity,
            child: Column(
              children: [
                if (istruzioneCarte != null) ...[istruzioneCarte, const SizedBox(height: 5)],
                Transform.translate(
                  offset: Offset(0, -margineMazzo),
                  child: Column(
                    children: [
                      AnimatedSwitcher(
                        duration: durata,
                        child: zona ?? const SizedBox.shrink(key: ValueKey('vuoto')),
                      ),
                      if (_fase == FaseLettura.scelta && stesa != null)
                        Ventaglio(
                          quante: _slotTotali,
                          scelte: _scelte,
                          attivo: daScegliere > 0,
                          alScegli: (slot) => unawaited(_scegli(slot, stesa)),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        if (_fase == FaseLettura.prontoMescolare)
          Respiro(
            child: Bottone(t.lettura_mescola, variante: Variante.ottone, alTocco: _mescola),
          ),
        if (_fase == FaseLettura.rivelazione || _fase == FaseLettura.prontoSintesi)
          Respiro(
            attivo: !_rivelazioneInCorso,
            child: Bottone(
              t.lettura_rivela_tutto,
              variante: Variante.ottone,
              an: 'rito',
              anProprieta: const {'passo': 'rivela_e_interpreta'},
              alTocco: _rivelazioneInCorso ? null : () => unawaited(_rivelaTutto()),
            ),
          ),
        if (_fase == FaseLettura.crisi || _fase == FaseLettura.annullata)
          Bottone(t.lettura_nuova, variante: Variante.chiaro, alTocco: _nuova),
        if (_errore != null && _fase != FaseLettura.intervista) Errore(_errore!, sopra: 0),
      ],
    );
  }

  @override
  void didUpdateWidget(PaginaLettura vecchio) {
    super.didUpdateWidget(vecchio);
  }

  @override
  void setState(VoidCallback fn) {
    final prima = _fase;
    super.setState(fn);
    // A ogni fase il dialogo del rito si riapre, e il mazzo torna in vista.
    if (_fase != prima) {
      _ritoChiuso = _fase == FaseLettura.svelamento;
      if (const {
        FaseLettura.mescolamento,
        FaseLettura.taglio,
        FaseLettura.scelta,
        FaseLettura.prontoMescolare,
      }.contains(_fase)) {
        Future<void>.delayed(const Duration(milliseconds: 350), () {
          if (_vivo && !widget.inChat && !_ritoInDialogo()) _portaInVista(_zonaMazzo);
        });
      }
    }
  }
}

/* ---- i pezzi della pagina ---------------------------------------------------------------------------------------- */

/// v9.5, l'intervista: una domanda aspetta la risposta, i pulsanti aspettano una scelta, si scrive il testo libero.
enum _ModoIntervista { risposta, libero }

/// v9.5, la chat: la larghezza della colonna (come `.chatColonna` del sito, 46 rem).
const double _larghezzaChat = 736;

/// `.read-panel` (chiaro) e `.read-panel.dark` (prugna); durante il rito sul telefono `.inRito .pannelloRito`.
class _PannelloLettura extends StatelessWidget {
  const _PannelloLettura({required this.chiaro, required this.children, this.rito = false});

  final bool chiaro;
  final bool rito;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.sizeOf(context).width;
    final padding = rito
        ? const EdgeInsets.fromLTRB(8, 9.6, 8, 14.4)
        : EdgeInsets.symmetric(horizontal: w.clampVw(20, 4, 48), vertical: w.clampVw(12, 2, 24));
    return Container(
      color: chiaro ? const Color(0xFFFFFAF1) : Token.plum,
      padding: padding,
      child: DefaultTextStyle.merge(
        style: TextStyle(color: chiaro ? Token.ink : const Color(0xFFF6ECDD)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: children,
        ),
      ),
    );
  }
}

/// `.read-panel h2`.
class _TitoloPannello extends StatelessWidget {
  const _TitoloPannello(this.testo);

  final String testo;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 16),
    child: Semantics(header: true, child: TestoBilanciato(testo, stile: Stile.serif(25.6))),
  );
}

/// `.console`: tutto centrato, uno sotto l'altro.
class _Console extends StatelessWidget {
  const _Console({required this.children, required this.spazio});

  final List<Widget> children;
  final double spazio;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.center,
    mainAxisSize: MainAxisSize.min,
    children: [
      for (final (i, c) in children.indexed) ...[if (i > 0) SizedBox(height: spazio), c],
    ],
  );
}

/// `.console-status` (e, sul telefono durante il rito, `.istruzione`: una pillola più grande).
class _Istruzione extends StatelessWidget {
  const _Istruzione(this.testo, {required this.pillola});

  final String testo;
  final bool pillola;

  @override
  Widget build(BuildContext context) {
    final stile = pillola
        ? Stile.sans(13.76, peso: FontWeight.w700, em: .11, colore: Token.brassPale)
        : stileStatoConsole();
    final scritta = Semantics(
      header: true,
      liveRegion: true,
      child: Text(testo.toUpperCase(), textAlign: TextAlign.center, style: stile),
    );
    if (!pillola) return scritta;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 5.6),
      decoration: BoxDecoration(
        color: const Color(0x99201026),
        border: Border.all(color: const Color(0x73D6B66D)),
        borderRadius: BorderRadius.circular(999),
      ),
      child: scritta,
    );
  }
}

/// La chiave dell'archivio: l'avvertenza accettata (i tarocchi non hanno validità scientifica), come il cookie
/// `tarots_avvertenza` del sito.
const String chiaveAvvertenza = 'avvertenza.accettata';

/// Il contenuto del dialogo dell'avvertenza: il testo, la casella «ho capito» e il pulsante, attivo solo con la
/// casella spuntata. Chiude il dialogo con `true`.
class _Avvertenza extends StatefulWidget {
  const _Avvertenza({required this.testo});

  final String testo;

  @override
  State<_Avvertenza> createState() => _AvvertenzaState();
}

class _AvvertenzaState extends State<_Avvertenza> {
  bool _capita = false;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Paragrafo(widget.testo, style: Stile.sans(15.2, colore: Token.inkSoft)),
        const SizedBox(height: 12),
        Casella(valore: _capita, alCambio: (v) => setState(() => _capita = v), titolo: t.lettura_avviso_capito),
        const SizedBox(height: 16),
        FilaBottoni(
          children: [
            Bottone(
              t.lettura_avviso_accetta,
              variante: Variante.ottone,
              alTocco: _capita ? () => Navigator.of(context).pop(true) : null,
            ),
          ],
        ),
      ],
    );
  }
}

/// L'istruzione di un passo del rito (ferma la mescolata, taglia, scegli), grande, subito sopra il mazzo. Con
/// [alTocco] è un pulsante a pillola (tocco ≥ 48 px).
class _IstruzioneCarte extends StatelessWidget {
  const _IstruzioneCarte(this.testo, {this.alTocco});

  final String testo;
  final VoidCallback? alTocco;

  @override
  Widget build(BuildContext context) {
    final scritta = Text(
      testo,
      textAlign: TextAlign.center,
      style: Stile.serif(24, altezza: 1.2, colore: const Color(0xFFFFF7E8)).copyWith(
        shadows: const [Shadow(color: Color(0x73000000), offset: Offset(0, 1), blurRadius: 2)],
      ),
    );
    final tocco = alTocco;
    if (tocco == null) return Semantics(header: true, liveRegion: true, child: scritta);
    return Premibile(
      alTocco: tocco,
      pulsante: true,
      etichetta: testo,
      costruisci: (context, premuto) => Container(
        constraints: const BoxConstraints(minHeight: 48),
        padding: const EdgeInsets.symmetric(horizontal: 17.6, vertical: 5.6),
        decoration: BoxDecoration(
          color: premuto ? const Color(0x5CB28336) : const Color(0x38B28336),
          border: Border.all(color: Token.brassPale),
          borderRadius: BorderRadius.circular(999),
        ),
        child: Center(widthFactor: 1, child: scritta),
      ),
    );
  }
}

/// `.consoleTesto`: il corsivo della console (al massimo 34ch).
class _TestoConsole extends StatelessWidget {
  const _TestoConsole(this.testo);

  final String testo;

  @override
  Widget build(BuildContext context) {
    final stile = Stile.serif(18.4, altezza: 1.45, stile: FontStyle.italic, colore: const Color(0xFFFBF3E5));
    return ConstrainedBox(
      constraints: BoxConstraints(maxWidth: larghezzaCh(stile, MediaQuery.textScalerOf(context)) * 34),
      child: Padding(
        padding: const EdgeInsets.only(top: 3.2, bottom: 9.6),
        child: TestoBilanciato(testo, stile: stile, allinea: TextAlign.center),
      ),
    );
  }
}

/// `.domanda`: il campo della domanda (alto 120 px, bordo d'ottone, ombra).
class _CampoDomanda extends StatefulWidget {
  const _CampoDomanda({
    required this.controllore,
    required this.etichetta,
    required this.segnaposto,
    required this.alCambio,
    required this.alFuoco,
  });

  final TextEditingController controllore;
  final String etichetta;
  final String segnaposto;
  final VoidCallback alCambio;
  final VoidCallback alFuoco;

  @override
  State<_CampoDomanda> createState() => _CampoDomandaState();
}

class _CampoDomandaState extends State<_CampoDomanda> {
  final FocusNode _fuoco = FocusNode(debugLabel: 'domanda');
  final GlobalKey<EditableTextState> _campo = GlobalKey(debugLabel: 'campo');

  @override
  void initState() {
    super.initState();
    _fuoco.addListener(() {
      if (_fuoco.hasFocus) widget.alFuoco();
      setState(() {});
    });
  }

  @override
  void dispose() {
    _fuoco.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final stile = Stile.sans(16, altezza: 1.6, colore: Token.ink);
    return Semantics(
      textField: true,
      label: widget.etichetta,
      child: GestureDetector(
        onTap: () => mostraTastiera(_fuoco, _campo),
        child: Container(
          constraints: const BoxConstraints(minHeight: 120),
          padding: const EdgeInsets.all(13.6),
          decoration: BoxDecoration(
            color: const Color(0xFFFFFFFF),
            border: Border.all(color: const Color(0x8CB28336)),
            boxShadow: const [BoxShadow(color: Color(0x143C1846), offset: Offset(0, 10), blurRadius: 30)],
          ),
          foregroundDecoration: _fuoco.hasFocus
              ? BoxDecoration(border: Border.all(color: Token.verdigris, width: 2))
              : null,
          child: Stack(
            children: [
              if (widget.controllore.text.isEmpty)
                IgnorePointer(
                  child: Text(widget.segnaposto, style: stile.copyWith(color: Colori.segnaposto)),
                ),
              EditableText(
                key: _campo,
                controller: widget.controllore,
                focusNode: _fuoco,
                style: stile,
                cursorColor: Token.ink,
                backgroundCursorColor: Token.inkSoft,
                selectionColor: const Color(0x4019706F),
                minLines: 4,
                maxLines: 12,
                keyboardType: TextInputType.multiline,
                textInputAction: TextInputAction.newline,
                textCapitalization: TextCapitalization.sentences,
                onChanged: (_) => widget.alCambio(),
                inputFormatters: const [],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// `.sceltaRiassunto`: sul telefono, ciò che si è scelto nei dialoghi e il modo di cambiarlo.
class _RiassuntoScelta extends StatelessWidget {
  const _RiassuntoScelta({required this.tema, required this.stesa, required this.alCambia});

  final String tema;
  final String? stesa;
  final VoidCallback alCambia;

  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.symmetric(vertical: 9.6),
    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8.8),
    decoration: BoxDecoration(
      color: const Color(0xFFFFFAF1),
      border: Border.all(color: Token.line),
    ),
    child: Row(
      children: [
        Expanded(
          child: Text.rich(
            TextSpan(
              children: [
                TextSpan(
                  text: tema,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                if (stesa != null) TextSpan(text: ' · $stesa'),
              ],
            ),
            style: Stile.sans(16, colore: Token.ink),
          ),
        ),
        const SizedBox(width: 9.6),
        Bottone(context.t.lettura_cambia, piccolo: true, variante: Variante.quieto, alTocco: alCambia),
      ],
    ),
  );
}

/// L'avviso delle letture di due persone senza account, con «Entra per continuare».
class _AvvisoAccount extends StatelessWidget {
  const _AvvisoAccount({required this.alEntra});

  final VoidCallback alEntra;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    return Avviso(
      null,
      figlio: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Paragrafo(t.lettura_tipo_serve_account),
          const SizedBox(height: 12.8),
          Bottone(t.lettura_tipo_entra, piccolo: true, alTocco: alEntra),
        ],
      ),
    );
  }
}

/// Il contenuto del dialogo dell'età (`DialogoEta` di `privacy-accesso.tsx`): «ho almeno N anni», o, se la data di
/// nascita dice meno del minimo, solo la spiegazione col collegamento al profilo.
class _ContenutoEta extends StatefulWidget {
  const _ContenutoEta({required this.anni, required this.insufficiente});

  final int anni;
  final bool insufficiente;

  @override
  State<_ContenutoEta> createState() => _ContenutoEtaState();
}

class _ContenutoEtaState extends State<_ContenutoEta> {
  bool _spuntata = false;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final testo = Stile.sans(16, colore: Token.ink);
    if (widget.insufficiente) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Paragrafo(t.comune_eta_insufficiente(widget.anni), style: testo),
          const SizedBox(height: 16),
          FilaBottoni(
            children: [
              Bottone(
                t.comune_eta_correggi,
                variante: Variante.quieto,
                alTocco: () {
                  final router = Navigator.of(context);
                  router.pop();
                  vai(router.context, R.profilo);
                },
              ),
            ],
          ),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Paragrafo(t.comune_eta_testo(widget.anni), style: testo),
        const SizedBox(height: 8),
        Casella(
          valore: _spuntata,
          alCambio: (v) => setState(() => _spuntata = v),
          titolo: t.comune_eta_dichiaro(widget.anni),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12.8),
          child: Wrap(
            crossAxisAlignment: WrapCrossAlignment.end,
            children: [
              Text('${t.comune_eta_perche} ', style: stilePiccolo()),
              Premibile(
                collegamento: true,
                alTocco: () {
                  final router = Navigator.of(context);
                  router.pop();
                  vai(router.context, R.privacy);
                },
                costruisci: (context, premuto) => TestoSottolineato(
                  '${t.comune_cookie_leggi}.',
                  stile: stilePiccolo(),
                  colore: premuto ? Token.verdigris : Token.plum,
                ),
              ),
            ],
          ),
        ),
        FilaBottoni(
          children: [
            Bottone(t.comune_eta_conferma, alTocco: _spuntata ? () => Navigator.of(context).pop(widget.anni) : null),
            Bottone(t.comune_eta_non_ora, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop()),
          ],
        ),
      ],
    );
  }
}
