/// La barra dell'oracolo (`frontend/v2/componenti/dock.tsx`, `.oracolo` di v2.css): ferma in fondo, su ogni pagina.
///
/// Chiusa mostra ciò che l'oracolo propone da solo: per chi è dentro l'ultimo messaggio della chat proattiva
/// (`/chat/proattiva`, nella lingua del profilo), per chi non ha un account un tema scelto a caso fra quelli dei
/// dizionari (`comune.oracolo_temi`), che porta a una lettura gratuita. Un tocco la apre in verticale: la chat con lo
/// storico che scorre, la proposta «Leggi le carte su…» e il campo per rispondere; ✕, «indietro» o un tocco fuori la
/// richiudono.
///
/// Costi: ogni apertura proattiva è un'inferenza. Per chi è dentro l'oracolo apre da solo all'avvio (solo se la sua
/// ultima proposta ha più di 12 ore, una volta per visita) e dopo il silenzio deciso dalla console, ma al più N volte
/// per visita (`/impostazioni-chat` → `proattiva_max_per_visita`, predefinito 3). Una «visita» è il tempo in cui l'app
/// resta aperta: dopo mezz'ora in secondo piano ne comincia un'altra (nel sito: la sessione del browser).
///
/// Non c'è dove la conversazione è già nella pagina: la lettura, la lettura delle proprie carte, le letture condivise.
/// Il guscio la mette sotto la pagina (che le lascia così il suo spazio, come `--oracolo-h` nel sito).
library;

import 'dart:async';
import 'dart:math' as math;
import 'dart:ui' show ImageFilter;

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../l10n/testi.dart';
import '../modelli/account.dart';
import '../rotte/navigazione.dart';
import '../rotte/percorsi.dart';
import '../rotte/percorso.dart';
import '../tema/tema.dart';
import 'campi.dart' show Puntini;
import 'premibile.dart';

/// Le pagine senza la barra (la conversazione c'è già).
const List<String> paginaSenzaOracolo = [R.leggi, R.fisica, R.condivise];

/// Vero se la barra si vede sul percorso [p].
bool oracoloVisibile(String p) => !paginaSenzaOracolo.any((x) => p == x || p.startsWith('$x/'));

/// La chiave del silenzio (la stessa del sito).
const String chiaveMuto = 'tarots.chat.muto';

/// Dodici ore: l'ultima proposta dell'oracolo è «vecchia» e all'avvio se ne apre una nuova.
const Duration dodiciOre = Duration(hours: 12);

/// Dopo quanto tempo in secondo piano comincia una visita nuova.
const Duration fineVisita = Duration(minutes: 30);

/// La visita: le aperture automatiche già fatte e se quella iniziale c'è già stata (`sessionStorage` del sito).
class VisitaOracolo {
  /// Le aperture automatiche fatte in questa visita.
  int aperture = 0;

  /// La proposta all'avvio è già stata chiesta.
  bool iniziale = false;

  DateTime? _inPausaDal;

  /// L'app va in secondo piano.
  void pausa(DateTime ora) => _inPausaDal = ora;

  /// L'app torna: dopo [fineVisita] la visita ricomincia.
  void ripresa(DateTime ora) {
    final dal = _inPausaDal;
    _inPausaDal = null;
    if (dal != null && ora.difference(dal) >= fineVisita) {
      aperture = 0;
      iniziale = false;
    }
  }
}

/// La visita corrente.
final visitaOracoloProvider = Provider<VisitaOracolo>((ref) => VisitaOracolo());

/// Il rintocco (finto nei test).
final rintoccoProvider = Provider<Future<void> Function()>((ref) {
  AudioPlayer? lettore;
  ref.onDispose(() => unawaited(lettore?.dispose()));
  return () async {
    try {
      lettore ??= AudioPlayer();
      await lettore!.play(AssetSource('suoni/chime.wav'));
    } on Object catch (e) {
      debugPrint('Rintocco non riprodotto: $e');
    }
  };
});

/// L'altezza della barra (0 se nascosta): il primo avvio ci appoggia sopra il foglio dei consensi, come il sito.
class AltezzaOracolo extends Notifier<double> {
  @override
  double build() => 0;

  /// La barra si è misurata.
  void misura(double h) {
    if ((h - state).abs() > .5) state = h;
  }
}

/// L'altezza della barra.
final altezzaOracoloProvider = NotifierProvider<AltezzaOracolo, double>(AltezzaOracolo.new);

/// Il tema scelto a caso per chi non ha un account (uno per avvio, come uno per caricamento nel sito).
final temaOracoloProvider = Provider<int>((ref) => math.Random().nextInt(1000));

/// La barra dell'oracolo.
class Oracolo extends ConsumerStatefulWidget {
  /// La barra.
  const Oracolo({super.key});

  @override
  ConsumerState<Oracolo> createState() => _OracoloState();
}

class _OracoloState extends ConsumerState<Oracolo> with WidgetsBindingObserver {
  final TextEditingController _testo = TextEditingController();
  final FocusNode _fuoco = FocusNode(debugLabel: 'oracolo');
  final ScrollController _chat = ScrollController();
  bool _aperto = false;
  bool _muto = false;
  bool _inCorso = false;
  bool _nuovo = false;
  List<TurnoChat> _turni = [];
  ImpostazioniChat? _impostazioni;
  Timer? _silenzio;
  bool _caricato = false;
  String? _dentroPer;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _muto = ref.read(archivioProvider).leggi(chiaveMuto) == '1';
    _testo.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _silenzio?.cancel();
    _testo.dispose();
    _fuoco.dispose();
    _chat.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState stato) {
    final visita = ref.read(visitaOracoloProvider);
    if (stato == AppLifecycleState.paused) visita.pausa(DateTime.now());
    if (stato == AppLifecycleState.resumed) visita.ripresa(DateTime.now());
  }

  bool get _dentro => ref.read(sessioneProvider).autenticata;

  /// Lo storico e la prima proposta del giorno (una volta per visita, senza rintocco: l'app è appena stata aperta).
  Future<void> _carica() async {
    final api = ref.read(apiProvider);
    try {
      _impostazioni = await api.impostazioniChat();
    } on ErroreApi {
      _impostazioni = const ImpostazioniChat();
    }
    final List<TurnoChat> turni;
    try {
      turni = await api.storicoChat();
    } on ErroreApi {
      return;
    }
    if (!mounted) return;
    setState(() => _turni = turni);
    _riarmaSilenzio();
    final ultimaAi = turni.reversed.where((x) => x.ruolo == 'ai').firstOrNull;
    final creato = DateTime.tryParse(ultimaAi?.creato ?? '');
    final vecchia = creato == null || DateTime.now().difference(creato) > dodiciOre;
    final visita = ref.read(visitaOracoloProvider);
    final giaFatta = visita.iniziale;
    visita.iniziale = true;
    if (vecchia && !giaFatta) await _apertura(conSuono: false);
  }

  /// Un'apertura dell'oracolo (un'inferenza), entro il tetto della visita.
  Future<void> _apertura({required bool conSuono}) async {
    final visita = ref.read(visitaOracoloProvider);
    final tetto = _impostazioni?.proattivaMaxPerVisita ?? 3;
    if (visita.aperture >= tetto) return;
    visita.aperture++;
    final TurnoChat? turno;
    try {
      turno = await ref.read(apiProvider).avviaChat();
    } on ErroreApi {
      return;
    }
    if (turno == null || !mounted) return;
    setState(() {
      _turni = [..._turni, turno!];
      _nuovo = true;
    });
    _riarmaSilenzio();
    if (conSuono && !_muto) unawaited(ref.read(rintoccoProvider)());
  }

  /// Il silenzio: dopo i minuti decisi dalla console l'oracolo riapre da sé la conversazione. Riparte a ogni turno.
  void _riarmaSilenzio() {
    _silenzio?.cancel();
    final minuti = _impostazioni?.proattivaMinutiInattivita;
    if (minuti == null || minuti <= 0 || !_dentro) return;
    _silenzio = Timer(Duration(minutes: minuti), () => unawaited(_apertura(conSuono: true)));
  }

  void _scorriInFondo() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_chat.hasClients) _chat.jumpTo(_chat.position.maxScrollExtent);
    });
  }

  void _apri() {
    setState(() {
      _aperto = true;
      _nuovo = false;
    });
    _scorriInFondo();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) _fuoco.requestFocus();
    });
  }

  void _chiudi() {
    _fuoco.unfocus();
    setState(() => _aperto = false);
  }

  Future<void> _invia() async {
    final pulito = _testo.text.trim();
    if (pulito.isEmpty) return;
    if (!_dentro) {
      vai(context, '${R.leggi}?question=${Uri.encodeComponent(pulito)}&source=dock');
      return;
    }
    if (_inCorso) return;
    setState(() {
      _nuovo = false;
      _inCorso = true;
      _turni = [
        ..._turni,
        TurnoChat(id: 'locale-${DateTime.now().millisecondsSinceEpoch}', ruolo: 'utente', testo: pulito),
      ];
    });
    _testo.clear();
    _scorriInFondo();
    TurnoChat? risposta;
    try {
      risposta = await ref.read(apiProvider).inviaMessaggioChat(pulito);
    } on ErroreApi {
      risposta = null;
    }
    if (!mounted) return;
    setState(() {
      _inCorso = false;
      if (risposta != null) _turni = [..._turni, risposta];
    });
    _riarmaSilenzio();
    _scorriInFondo();
  }

  void _cambiaMuto() {
    setState(() => _muto = !_muto);
    unawaited(ref.read(archivioProvider).scrivi(chiaveMuto, _muto ? '1' : '0'));
  }

  @override
  Widget build(BuildContext context) {
    final percorso = ref.watch(percorsoProvider).path;
    final dentro = ref.watch(sessioneProvider.select((s) => s.autenticata));
    // Chi entra (o esce) ricomincia: lo storico è suo.
    final chi = dentro ? (ref.watch(sessioneProvider.select((s) => s.nome)) ?? '') : null;
    if (chi != _dentroPer) {
      _dentroPer = chi;
      _caricato = false;
      _silenzio?.cancel();
      _turni = [];
      _nuovo = false;
    }
    if (dentro && !_caricato) {
      _caricato = true;
      unawaited(_carica());
    }
    if (!oracoloVisibile(percorso)) {
      WidgetsBinding.instance.addPostFrameCallback((_) => ref.read(altezzaOracoloProvider.notifier).misura(0));
      return const SizedBox.shrink();
    }
    final t = context.t;
    final temi = t.comuneOracoloTemi;
    final tema = temi[ref.watch(temaOracoloProvider) % temi.length];
    final ultimaAi = _turni.reversed.where((x) => x.ruolo == 'ai').firstOrNull;
    final proposta = dentro ? (ultimaAi?.testo ?? t.comune_dock_vuoto) : tema.testo;

    final barra = _aperto
        ? _Espansa(
            dentro: dentro,
            muto: _muto,
            turni: _turni,
            tema: tema,
            inCorso: _inCorso,
            testo: _testo,
            fuoco: _fuoco,
            chat: _chat,
            alChiudi: _chiudi,
            alMuto: _cambiaMuto,
            alInvio: () => unawaited(_invia()),
            alVai: (href) => vai(context, href),
          )
        : _Chiusa(dentro: dentro, proposta: proposta, nuovo: _nuovo, alTocco: _apri);

    return PopScope(
      // Aperta, «indietro» la richiude (come Esc nel sito) invece di lasciare la pagina.
      canPop: !_aperto,
      onPopInvokedWithResult: (fatto, _) {
        if (!fatto && _aperto) _chiudi();
      },
      child: TapRegion(
        onTapOutside: _aperto ? (_) => _chiudi() : null,
        child: _Misura(
          alMisura: (h) => ref.read(altezzaOracoloProvider.notifier).misura(h),
          child: barra,
        ),
      ),
    );
  }
}

/// Riferisce l'altezza del figlio dopo ogni disposizione.
class _Misura extends SingleChildRenderObjectWidget {
  const _Misura({required this.alMisura, required super.child});

  final ValueChanged<double> alMisura;

  @override
  _RenderMisura createRenderObject(BuildContext context) => _RenderMisura(alMisura);

  @override
  void updateRenderObject(BuildContext context, _RenderMisura r) => r.alMisura = alMisura;
}

class _RenderMisura extends RenderProxyBox {
  _RenderMisura(this.alMisura);

  ValueChanged<double> alMisura;

  @override
  void performLayout() {
    super.performLayout();
    final h = size.height;
    WidgetsBinding.instance.addPostFrameCallback((_) => alMisura(h));
  }
}

/// Il fondo della barra: `.oracolo-barra` (prugna quasi opaca e sfocata, la riga d'ottone in alto, l'ombra verso la
/// pagina), con le imbottiture del sito e le safe area.
class _Fondo extends StatelessWidget {
  const _Fondo({required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final w = media.size.width;
    final gutter = w.gutter;
    return DecoratedBox(
      decoration: const BoxDecoration(
        boxShadow: [BoxShadow(color: Color(0x38201026), offset: Offset(0, -10), blurRadius: 28)],
      ),
      child: ClipRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Container(
            decoration: const BoxDecoration(
              color: Color(0xF7201026),
              border: Border(top: BorderSide(color: Token.brass, width: 2)),
            ),
            padding: EdgeInsets.fromLTRB(
              math.max(gutter, media.padding.left),
              w.piccolo ? 8 : 9.6,
              math.max(gutter, media.padding.right),
              math.max(9.6, media.padding.bottom),
            ),
            child: DefaultTextStyle(
              style: Stile.sans(16, colore: const Color(0xFFF6ECDD)),
              child: child,
            ),
          ),
        ),
      ),
    );
  }
}

/// `.oracolo-segno`: la stella in un quadrato di 44 px (32 nella testa della barra aperta), col punto verderame dei
/// messaggi nuovi.
class _Segno extends StatelessWidget {
  const _Segno({this.misura = 44, this.nuovo = false});

  final double misura;
  final bool nuovo;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: misura,
      height: misura,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Center(child: Text('✦', style: Stile.serif(18.4, altezza: 1, colore: Token.brassPale))),
          if (nuovo)
            Positioned(
              top: 4,
              right: 4,
              child: Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: Token.verdigris,
                  shape: BoxShape.circle,
                  border: Border.all(color: Token.plumDeep, width: 2, strokeAlign: BorderSide.strokeAlignOutside),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// `.button.button-brass.oracolo-invia`: «Begin»/«Send», o la freccia sola fino a 560 px.
class _Invia extends StatelessWidget {
  const _Invia({required this.dentro, this.alTocco, this.an});

  final bool dentro;
  final VoidCallback? alTocco;
  final String? an;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final piccolo = MediaQuery.sizeOf(context).width.piccolo;
    final etichetta = dentro ? t.comune_dock_invia : t.comune_dock_invia_anonimo;
    Widget corpo(bool premuto) => Opacity(
      opacity: alTocco == null && an != null ? .55 : 1,
      child: Container(
        constraints: BoxConstraints(minHeight: 44, minWidth: piccolo ? 44 : 0, maxWidth: piccolo ? 44 : double.infinity),
        padding: piccolo ? EdgeInsets.zero : const EdgeInsets.symmetric(horizontal: 17.6, vertical: 11.52),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: premuto ? const Color(0xFFC69543) : Token.brass,
          border: Border.all(color: Colori.bordoOttone),
          borderRadius: BorderRadius.circular(Token.raggio),
        ),
        child: piccolo
            ? Text('→', style: Stile.sans(19.2, peso: FontWeight.w700, altezza: 1, colore: Colori.testoOttone))
            : Text(etichetta, style: Stile.bottone().copyWith(color: Colori.testoOttone)),
      ),
    );
    // Nella barra chiusa il bottone è solo un segno: il tocco è della barra intera (`pointer-events: none`).
    if (an == null) return ExcludeSemantics(child: corpo(false));
    return Premibile(
      alTocco: alTocco,
      an: an,
      etichetta: etichetta,
      raggioFuoco: Token.raggio,
      costruisci: (context, premuto) => corpo(premuto),
    );
  }
}

/// Chiusa: la proposta dell'oracolo al posto del campo; un tocco ovunque la apre.
class _Chiusa extends StatelessWidget {
  const _Chiusa({required this.dentro, required this.proposta, required this.nuovo, required this.alTocco});

  final bool dentro;
  final String proposta;
  final bool nuovo;
  final VoidCallback alTocco;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final piccolo = MediaQuery.sizeOf(context).width.piccolo;
    final spazio = piccolo ? 7.2 : 9.6;
    return Premibile(
      alTocco: alTocco,
      an: 'dock_apri',
      etichetta: '${t.comune_oracolo_apri}: $proposta',
      costruisci: (context, premuto) => _Fondo(
        child: Row(
          children: [
            _Segno(nuovo: nuovo),
            SizedBox(width: spazio),
            Expanded(
              // `.oracolo-chiusa .oracolo-proposta`: una riga sola coi puntini, `line-height: 1.95rem`.
              child: Container(
                constraints: const BoxConstraints(minHeight: 44),
                padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 8.8),
                decoration: BoxDecoration(
                  color: premuto ? const Color(0x1FFFFFFF) : const Color(0x12FFFFFF),
                  border: Border.all(color: const Color(0x66D6B66D)),
                  borderRadius: BorderRadius.circular(Token.raggio),
                ),
                child: Text(
                  proposta,
                  maxLines: 1,
                  softWrap: false,
                  overflow: TextOverflow.ellipsis,
                  style: Stile.serif(
                    piccolo ? 15.2 : 16,
                    stile: FontStyle.italic,
                    altezza: 31.2 / (piccolo ? 15.2 : 16),
                    colore: const Color(0xFFFFF7E8),
                  ),
                ),
              ),
            ),
            SizedBox(width: spazio),
            _Invia(dentro: dentro),
          ],
        ),
      ),
    );
  }
}

/// Aperta: la testa, due righe di chat (lo storico scorre) e il campo.
class _Espansa extends StatelessWidget {
  const _Espansa({
    required this.dentro,
    required this.muto,
    required this.turni,
    required this.tema,
    required this.inCorso,
    required this.testo,
    required this.fuoco,
    required this.chat,
    required this.alChiudi,
    required this.alMuto,
    required this.alInvio,
    required this.alVai,
  });

  final bool dentro;
  final bool muto;
  final List<TurnoChat> turni;
  final ({String testo, String domanda}) tema;
  final bool inCorso;
  final TextEditingController testo;
  final FocusNode fuoco;
  final ScrollController chat;
  final VoidCallback alChiudi;
  final VoidCallback alMuto;
  final VoidCallback alInvio;
  final ValueChanged<String> alVai;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final piccolo = MediaQuery.sizeOf(context).width.piccolo;
    final telefono = MediaQuery.sizeOf(context).width.telefono;
    final titolo = dentro ? t.comune_dock_titolo : t.comune_dock_titolo_anonimo;

    Widget azione(String segno, String etichetta, VoidCallback f) => Premibile(
      alTocco: f,
      etichetta: etichetta,
      raggioFuoco: 22,
      costruisci: (context, premuto) => Container(
        width: 44,
        height: 44,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: premuto ? const Color(0x1FFFFFFF) : const Color(0x0FFFFFFF),
          shape: BoxShape.circle,
        ),
        child: Text(segno, style: Stile.sans(16, altezza: 1, colore: const Color(0xFFFFF7E8))),
      ),
    );

    final testa = Row(
      children: [
        const _Segno(misura: 32),
        const SizedBox(width: 8),
        Expanded(
          child: Semantics(
            header: true,
            child: Text(
              titolo,
              style: Stile.sans(13.12, peso: FontWeight.w700, em: .04, colore: Token.brassPale, altezza: 1.6),
            ),
          ),
        ),
        if (dentro) ...[
          azione(muto ? '🔇' : '🔊', muto ? t.comune_dock_muto : t.comune_dock_suono, alMuto),
          const SizedBox(width: 4.8),
        ],
        azione('✕', t.comune_chiudi, alChiudi),
      ],
    );

    // `.message` (sul telefono più compatto) e `.message-user`.
    Widget messaggio(String testo, {bool utente = false}) => Align(
      alignment: utente ? AlignmentDirectional.centerEnd : AlignmentDirectional.centerStart,
      child: Container(
        padding: telefono
            ? const EdgeInsets.symmetric(horizontal: 12, vertical: 9.6)
            : const EdgeInsets.symmetric(horizontal: 16, vertical: 14.4),
        decoration: BoxDecoration(
          color: utente ? const Color(0x2419706F) : const Color(0x0EFFFFFF),
          border: utente
              ? const Border(right: BorderSide(color: Token.verdigris, width: 2))
              : const Border(left: BorderSide(color: Token.brass, width: 2)),
        ),
        child: Text(testo, style: Stile.sans(telefono ? 14.08 : 14.88, colore: const Color(0xFFF6ECDD))),
      ),
    );

    Widget leggi(String etichetta, String href, {String? an}) => Premibile(
      alTocco: () => alVai(href),
      an: an,
      raggioFuoco: Token.raggio,
      costruisci: (context, premuto) => Container(
        constraints: const BoxConstraints(minHeight: Token.altezzaBottonePiccolo),
        padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 8),
        decoration: BoxDecoration(
          color: premuto ? const Color(0x14FFFFFF) : null,
          border: Border.all(color: const Color(0x8CD6B66D)),
          borderRadius: BorderRadius.circular(Token.raggio),
        ),
        child: Text(etichetta, style: Stile.bottone(px: 12.8).copyWith(color: const Color(0xFFFFF7E8))),
      ),
    );

    final voci = <Widget>[
      if (dentro) ...[
        if (turni.isEmpty) messaggio(t.comune_dock_vuoto),
        for (final turno in turni)
          Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              messaggio(turno.testo, utente: turno.ruolo == 'utente'),
              if (turno.proposta != null)
                Padding(
                  padding: const EdgeInsets.only(top: 5.6),
                  child: Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: leggi(
                      t.comune_dock_proposta(turno.proposta!.argomento),
                      '${R.leggi}?question=${Uri.encodeComponent(turno.proposta!.argomento)}'
                      '&type=${turno.proposta!.categoria}&source=dock',
                    ),
                  ),
                ),
            ],
          ),
        if (inCorso)
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: Puntini(etichetta: t.comune_dock_attesa),
          ),
      ] else
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            messaggio(tema.testo),
            const SizedBox(height: 5.6),
            leggi(
              t.comune_oracolo_leggi,
              '${R.leggi}?question=${Uri.encodeComponent(tema.domanda)}&source=dock',
              an: 'dock_tema',
            ),
          ],
        ),
    ];

    final storico = ConstrainedBox(
      constraints: BoxConstraints(maxHeight: telefono && piccolo ? 121.6 : 137.6),
      child: Semantics(
        liveRegion: true,
        child: ListView.separated(
          controller: chat,
          shrinkWrap: true,
          padding: const EdgeInsets.only(right: 3.2),
          itemCount: voci.length,
          separatorBuilder: (context, _) => const SizedBox(height: 7.2),
          itemBuilder: (context, i) => voci[i],
        ),
      ),
    );

    final vuoto = testo.text.trim().isEmpty;
    final segnaposto = dentro ? t.comune_dock_segnaposto : t.comune_dock_segnaposto_anonimo;
    final campo = Container(
      constraints: const BoxConstraints(minHeight: 44, maxHeight: 120),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9.6),
      decoration: BoxDecoration(
        color: const Color(0x12FFFFFF),
        border: Border.all(color: fuoco.hasFocus ? Token.brassPale : const Color(0x66D6B66D)),
        borderRadius: BorderRadius.circular(Token.raggio),
      ),
      child: Semantics(
        textField: true,
        label: segnaposto,
        child: Stack(
          children: [
            if (vuoto)
              IgnorePointer(
                child: Text(segnaposto, style: Stile.sans(16, altezza: 1.4, colore: const Color(0xFFC2B4C8))),
              ),
            EditableText(
              controller: testo,
              focusNode: fuoco,
              style: Stile.sans(16, altezza: 1.4, colore: const Color(0xFFFFF7E8)),
              cursorColor: const Color(0xFFFFF7E8),
              backgroundCursorColor: Token.brassPale,
              selectionColor: const Color(0x66D6B66D),
              minLines: 1,
              maxLines: 5,
              keyboardType: TextInputType.multiline,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => alInvio(),
              inputFormatters: [LengthLimitingTextInputFormatter(2000)],
            ),
          ],
        ),
      ),
    );

    return _Fondo(
      child: Semantics(
        container: true,
        label: titolo,
        explicitChildNodes: true,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            testa,
            const SizedBox(height: 7.2),
            storico,
            const SizedBox(height: 7.2),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(child: campo),
                const SizedBox(width: 8),
                _Invia(dentro: dentro, alTocco: vuoto || (dentro && inCorso) ? null : alInvio, an: 'dock_invia'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
