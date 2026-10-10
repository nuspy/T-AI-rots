/// v9.5: una parte di pagina coi testi tradotti nella lingua di lettura (`lingua_contenuti.dart`), come il riquadro
/// `AvvisoTraduzione` del sito: mentre traduce si vede l'originale; poi i testi tradotti e il riquadro «tradotto
/// automaticamente sul telefono · mostra l'originale». Chi chiama dice da che lingua sono i testi ([ConTraduzione.da])
/// e quali sono; nel costruire usa `tr(testo)` per ognuno e mette il riquadro dove serve.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../componenti/bottoni.dart';
import '../componenti/campi.dart' show Puntini;
import '../l10n/testi.dart';
import '../tema/tema.dart';
import 'lingua_contenuti.dart';
import 'motore.dart';
import 'testo_protetto.dart';

/// Le frasi già tradotte, per tutta la vita dell'app (`da>a|frase` → traduzione).
final memoriaTraduzioniProvider = Provider<Map<String, String>>((ref) => {});

/// Il punto della traduzione.
enum FaseTraduzione {
  /// Niente da tradurre (stessa lingua, motore assente, lingua non scelta).
  nessuna,

  /// Scaricamento del modello o traduzione.
  inCorso,

  /// Tradotta.
  tradotta,

  /// Chi legge ha chiesto l'originale.
  originale,

  /// Non è riuscita (di solito: niente rete per scaricare il modello).
  errore,
}

/// Una parte di pagina coi testi tradotti.
class ConTraduzione extends ConsumerStatefulWidget {
  /// I [testi] e i [markdown] nella lingua [da], per [costruisci].
  const ConTraduzione({
    super.key,
    required this.da,
    this.testi = const [],
    this.markdown = const [],
    required this.costruisci,
  });

  /// La lingua dei testi (`en`, `it`).
  final String da;

  /// I testi semplici.
  final List<String> testi;

  /// I testi in markdown (il corpo di un articolo).
  final List<String> markdown;

  /// La parte di pagina: `tr(testo)` dà la traduzione (o l'originale), [avviso] è il riquadro.
  final Widget Function(BuildContext context, String Function(String testo) tr, Widget avviso) costruisci;

  @override
  ConsumerState<ConTraduzione> createState() => _ConTraduzioneState();
}

class _ConTraduzioneState extends ConsumerState<ConTraduzione> {
  final Map<String, String> _fatti = {};
  FaseTraduzione _fase = FaseTraduzione.nessuna;
  bool _vuoleOriginale = false;
  int _giro = 0;
  ProviderSubscription<String>? _lingua;

  @override
  void initState() {
    super.initState();
    _lingua = ref.listenManual(linguaContenutiProvider, (_, _) {
      _fatti.clear();
      _vuoleOriginale = false;
      unawaited(_avvia());
    });
    unawaited(_avvia());
  }

  @override
  void didUpdateWidget(ConTraduzione vecchio) {
    super.didUpdateWidget(vecchio);
    final cambiati =
        vecchio.da != widget.da || !_uguali(vecchio.testi, widget.testi) || !_uguali(vecchio.markdown, widget.markdown);
    if (cambiati) unawaited(_avvia());
  }

  @override
  void dispose() {
    _lingua?.close();
    super.dispose();
  }

  static bool _uguali(List<String> a, List<String> b) {
    if (a.length != b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }

  String get _a => ref.read(linguaContenutiProvider);

  Future<void> _avvia() async {
    final giro = ++_giro;
    final motore = ref.read(motoreTraduzioneProvider);
    final a = _a;
    if (a == widget.da || !motore.disponibile) {
      if (mounted) setState(() => _fase = FaseTraduzione.nessuna);
      return;
    }
    final mancanti = [
      for (final s in widget.testi)
        if (!_fatti.containsKey(s)) (s, false),
      for (final s in widget.markdown)
        if (!_fatti.containsKey(s)) (s, true),
    ];
    if (mancanti.isEmpty) {
      if (mounted) setState(() => _fase = _vuoleOriginale ? FaseTraduzione.originale : FaseTraduzione.tradotta);
      return;
    }
    if (mounted && !_vuoleOriginale) setState(() => _fase = FaseTraduzione.inCorso);
    try {
      // Anche la lingua di partenza serve sul telefono, se non è l'inglese (ML Kit passa per l'inglese).
      final pronti = (widget.da == 'en' || await motore.scarica(widget.da)) && await motore.scarica(a);
      if (!pronti) throw StateError('modello non scaricato');
      final memoria = ref.read(memoriaTraduzioniProvider);
      final da = widget.da;
      Future<String> frase(String f) async {
        final chiave = '$da>$a|$f';
        final pronta = memoria[chiave];
        if (pronta != null) return pronta;
        final tradotta = await motore.traduci(f, da: da, a: a);
        memoria[chiave] = tradotta;
        return tradotta;
      }

      for (final (testo, markdown) in mancanti) {
        final tradotto = markdown ? await traduciMarkdown(testo, frase) : await traduciRiga(testo, frase);
        if (giro != _giro || !mounted) return;
        _fatti[testo] = tradotto;
      }
      if (giro == _giro && mounted) {
        setState(() => _fase = _vuoleOriginale ? FaseTraduzione.originale : FaseTraduzione.tradotta);
      }
    } on Object {
      if (giro == _giro && mounted) setState(() => _fase = FaseTraduzione.errore);
    }
  }

  String _tr(String testo) => _fase == FaseTraduzione.tradotta ? (_fatti[testo] ?? testo) : testo;

  @override
  Widget build(BuildContext context) {
    ref.watch(linguaContenutiProvider);
    final avviso = AvvisoTraduzioneApp(
      fase: _fase,
      da: widget.da,
      a: _a,
      alOriginale: () => setState(() {
        _vuoleOriginale = true;
        _fase = FaseTraduzione.originale;
      }),
      alTraduci: () {
        _vuoleOriginale = false;
        unawaited(_avvia());
      },
    );
    return widget.costruisci(context, _tr, avviso);
  }
}

/// [ConTraduzione] per una pagina coi testi scritti in un posto solo (privacy, termini): [pagina] si costruisce una
/// prima volta con un `tr` che raccoglie i testi (quelli da tradurre, che [ConTraduzione] vuole prima) e poi con quello
/// vero, così l'elenco non ne dimentica nessuno. In [pagina] `tr` va chiamato subito, non dentro un costruttore pigro.
Widget conTestiRaccolti({
  required String da,
  required Widget Function(String Function(String testo) tr, Widget avviso) pagina,
}) {
  final testi = <String>[];
  pagina((testo) {
    testi.add(testo);
    return testo;
  }, const SizedBox.shrink());
  return ConTraduzione(da: da, testi: testi, costruisci: (context, tr, avviso) => pagina(tr, avviso));
}

/// Il riquadro della traduzione (`AvvisoTraduzione` del sito).
class AvvisoTraduzioneApp extends StatelessWidget {
  /// Il riquadro per la [fase].
  const AvvisoTraduzioneApp({
    super.key,
    required this.fase,
    required this.da,
    required this.a,
    required this.alOriginale,
    required this.alTraduci,
  });

  /// Il punto della traduzione.
  final FaseTraduzione fase;

  /// La lingua dell'originale e quella di lettura.
  final String da;
  final String a;

  /// «Mostra l'originale» e «Traduci».
  final VoidCallback alOriginale;
  final VoidCallback alTraduci;

  @override
  Widget build(BuildContext context) {
    if (fase == FaseTraduzione.nessuna) return const SizedBox.shrink();
    final t = context.t;
    final stile = Stile.sans(14.4, colore: Token.inkSoft, altezza: 1.5);
    final (String testo, Widget? azione) = switch (fase) {
      FaseTraduzione.inCorso => (t.comune_traduzione_in_corso, null),
      FaseTraduzione.tradotta => (
        t.comune_traduzione_tradotta(nomeLingua(da)),
        Bottone(
          t.comune_traduzione_originale(nomeLingua(da)),
          piccolo: true,
          variante: Variante.quieto,
          alTocco: alOriginale,
        ),
      ),
      FaseTraduzione.originale => (
        t.comune_traduzione_e_originale(nomeLingua(da)),
        Bottone(t.comune_traduzione_traduci_in_lingua(nomeLingua(a)), piccolo: true, alTocco: alTraduci),
      ),
      FaseTraduzione.errore => (
        t.comune_traduzione_errore,
        Bottone(t.comune_traduzione_traduci, piccolo: true, variante: Variante.quieto, alTocco: alTraduci),
      ),
      FaseTraduzione.nessuna => ('', null),
    };
    return Semantics(
      liveRegion: true,
      container: true,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.symmetric(horizontal: 14.4, vertical: 11.2),
        decoration: BoxDecoration(
          color: Token.paperLight,
          border: Border.all(color: Token.line),
        ),
        child: Wrap(
          spacing: 14.4,
          runSpacing: 8,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            if (fase == FaseTraduzione.inCorso) const Puntini(colore: Token.brass),
            Text(testo, style: stile),
            ?azione,
          ],
        ),
      ),
    );
  }
}
