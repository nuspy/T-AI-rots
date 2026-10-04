/// La condivisione di una lettura (`frontend/v2/lettura/condivisione.tsx`, `condivisione.module.css`): il collegamento
/// pubblico, l'immagine composta nell'app e rifatta dal server in WebP (`immagine_condivisione.dart`), le parole di
/// chi condivide (si salvano dopo una pausa e rifanno l'immagine), i canali, il contatore delle condivisioni
/// verificate e i premi.
///
/// I canali come nel sito sul telefono: Facebook, X ed email aprono la loro pagina (o la posta) fuori dall'app;
/// Instagram e TikTok, che non hanno un indirizzo di condivisione, passano dal foglio di condivisione del sistema con
/// l'immagine e il testo (`share_plus`); «Solo il link» lo copia. «Scarica l'immagine» la passa al foglio del sistema,
/// che offre di salvarla. Ogni canale usato conta un clic (`share-click`) con l'identità anonima di chi condivide.
library;

import 'dart:async';
import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' show ImageFilter;

import 'package:flutter/services.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

import '../analytics/tracciato.dart';
import '../analytics/visitatore.dart';
import '../api/api.dart';
import '../api/errori.dart';
import '../cassa/pagamento.dart' show apriFuori;
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/carta.dart';
import '../componenti/icone.dart' show tracciato;
import '../componenti/premibile.dart';
import '../componenti/testi.dart';
import '../config.dart';
import '../l10n/testi.dart';
import '../modelli/account.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'immagine_condivisione.dart';

/// L'indirizzo pubblico di una lettura condivisa (`urlCondivisioneV2`): sul sito, che l'app apre se è installata.
String urlCondivisione(String token) => '${Config.sitoPubblico}${R.condivisa(token)}';

/// La lunghezza massima del testo personale (`LUNGHEZZA_TESTO`).
const int lunghezzaTesto = 200;

/// I canali, nell'ordine del sito.
const List<String> canali = ['instagram', 'facebook', 'tiktok', 'x', 'email', 'link'];

const Map<String, String> _nomiRete = {
  'instagram': 'Instagram',
  'facebook': 'Facebook',
  'tiktok': 'TikTok',
  'x': 'X',
  'email': 'Email',
  'link': 'Link',
};

/// L'indirizzo che apre la condivisione del canale, dove ne esiste una pubblica (`urlIntento`).
String? urlIntento(String canale, {required String url, required String testo, required String oggetto}) {
  const c = Uri.encodeComponent;
  return switch (canale) {
    'facebook' => 'https://www.facebook.com/sharer/sharer.php?u=${c(url)}',
    'x' => 'https://x.com/intent/post?text=${c(testo)}&url=${c(url)}',
    'email' => 'mailto:?subject=${c(oggetto)}&body=${c(testo.isNotEmpty ? '$testo\n\n$url' : url)}',
    _ => null,
  };
}

/// Apre il pannello di condivisione della lettura [id] (un dialogo, come il pannello del sito).
Future<void> apriCondivisione(BuildContext context, {required String id}) {
  return showGeneralDialog<void>(
    context: context,
    barrierDismissible: true,
    barrierLabel: context.t.comune_chiudi,
    barrierColor: const Color(0x00000000),
    transitionDuration: Token.durataTransizione,
    pageBuilder: (context, _, _) => _Finestra(
      titolo: context.t.lettura_cond_titolo,
      alChiudi: () => Navigator.of(context).pop(),
      child: PannelloCondivisione(id: id),
    ),
    transitionBuilder: (context, animazione, _, figlio) => FadeTransition(opacity: animazione, child: figlio),
  );
}

/// `.dialog` largo al più 860 px (`.finestra` di condivisione.module.css), col velo sfocato.
class _Finestra extends StatelessWidget {
  const _Finestra({required this.titolo, required this.alChiudi, required this.child});

  final String titolo;
  final VoidCallback alChiudi;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final w = media.size.width;
    return Stack(
      children: [
        Positioned.fill(
          child: GestureDetector(
            onTap: alChiudi,
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 3, sigmaY: 3),
              child: const ColoredBox(color: Colori.velo),
            ),
          ),
        ),
        Padding(
          padding: EdgeInsets.fromLTRB(16, 16 + media.padding.top, 16, math.max(16, media.padding.bottom)),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 860),
              child: Container(
                decoration: const BoxDecoration(
                  color: Token.paperLight,
                  border: Border(
                    top: BorderSide(color: Token.brass, width: Token.bordoModale),
                  ),
                  boxShadow: [BoxShadow(color: Color(0x59201026), offset: Offset(0, 30), blurRadius: 60)],
                ),
                child: Stack(
                  children: [
                    SingleChildScrollView(
                      padding: EdgeInsets.all(w.clampVw(20, 4, 32)),
                      child: DefaultTextStyle.merge(
                        style: Stile.corpo,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Padding(
                              padding: const EdgeInsets.only(right: 40, bottom: 16),
                              child: Semantics(
                                header: true,
                                child: Text(titolo, style: Stile.serif(24, altezza: 1.25, colore: Token.ink)),
                              ),
                            ),
                            child,
                          ],
                        ),
                      ),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Premibile(
                        alTocco: alChiudi,
                        etichetta: context.t.comune_chiudi,
                        costruisci: (context, _) => SizedBox(
                          width: 44,
                          height: 44,
                          child: Center(
                            child: Text('✕', style: Stile.sans(17.6, colore: Token.inkSoft)),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

enum _Stato { preparo, pronto, errore }

/// Il contenuto del pannello.
class PannelloCondivisione extends ConsumerStatefulWidget {
  /// Il pannello della lettura [id].
  const PannelloCondivisione({super.key, required this.id});

  /// La lettura.
  final String id;

  @override
  ConsumerState<PannelloCondivisione> createState() => _PannelloCondivisioneState();
}

class _PannelloCondivisioneState extends ConsumerState<PannelloCondivisione> {
  final TextEditingController _testo = TextEditingController();
  _Stato _stato = _Stato.preparo;
  String? _token;
  LetturaCondivisa? _dati;
  Uint8List? _anteprima;
  ({String testo, String? href, String? etichetta})? _avviso;
  Condivisioni? _contatore;
  XFile? _file;
  int _richiesta = 0;
  String? _sincronizzato;
  Timer? _pausa;

  @override
  void initState() {
    super.initState();
    _testo.addListener(_cambiato);
    scheduleMicrotask(() => unawaited(_sincronizza(null)));
    unawaited(
      ref.read(apiProvider).profilo().then((p) {
        if (mounted) setState(() => _contatore = p.condivisioni);
      }, onError: (Object _) {}),
    );
  }

  @override
  void dispose() {
    _richiesta++;
    _pausa?.cancel();
    _testo.dispose();
    super.dispose();
  }

  /// Il testo cambia: dopo una pausa di 900 ms si salva e l'immagine si rifà.
  void _cambiato() {
    setState(() {});
    if (_stato == _Stato.errore || _sincronizzato == null || _testo.text == _sincronizzato) return;
    _pausa?.cancel();
    _pausa = Timer(const Duration(milliseconds: 900), () {
      if (!mounted) return;
      setState(() {
        _stato = _Stato.preparo;
        _avviso = null;
      });
      unawaited(_sincronizza(_testo.text));
    });
  }

  Future<void> _sincronizza(String? nuovoTesto) async {
    final numero = ++_richiesta;
    bool vecchia() => numero != _richiesta || !mounted;
    if (nuovoTesto != null) _sincronizzato = nuovoTesto;
    final api = ref.read(apiProvider);
    try {
      final r = await api.condividiLettura(widget.id, attiva: true, testo: nuovoTesto);
      if (vecchia()) return;
      final token = r.shareToken;
      if (token == null) {
        setState(() => _stato = _Stato.errore);
        return;
      }
      final pubblica = await api.letturaCondivisa(token);
      if (vecchia()) return;
      final fornitore = ref.read(immagineCartaProvider);
      final immagini = await caricaCarte(pubblica.cards, fornitore, (id) => percorsoCarta(pubblica.mazzo, id));
      final png = await componiImmagine(pubblica, immagini);
      for (final i in immagini.values) {
        i?.dispose();
      }
      if (vecchia()) return;
      if (png == null) {
        setState(() => _stato = _Stato.errore);
        return;
      }
      final webp = await api.caricaImmagineCondivisione(widget.id, png);
      if (vecchia()) return;
      _file = await _salvaFile(webp);
      if (vecchia()) return;
      setState(() {
        _anteprima = webp;
        _token = token;
        _dati = pubblica;
        if (nuovoTesto == null) {
          _sincronizzato = r.shareText ?? '';
          _testo.removeListener(_cambiato);
          _testo.text = r.shareText ?? '';
          _testo.addListener(_cambiato);
        }
        _stato = _Stato.pronto;
      });
    } on Object catch (e) {
      debugPrint('Condivisione non preparata: $e');
      if (!vecchia()) setState(() => _stato = _Stato.errore);
    }
  }

  /// L'immagine in un file temporaneo, per il foglio di condivisione del sistema.
  static Future<XFile?> _salvaFile(Uint8List webp) async {
    try {
      final cartella = await getTemporaryDirectory();
      final file = File('${cartella.path}/tarots-reading.webp');
      await file.writeAsBytes(webp, flush: true);
      return XFile(file.path, mimeType: 'image/webp', name: 'tarots-reading.webp');
    } on Object {
      return XFile.fromData(webp, mimeType: 'image/webp', name: 'tarots-reading.webp');
    }
  }

  bool get _pronto => _stato == _Stato.pronto && _token != null && _dati != null;
  String get _url => _token == null ? '' : urlCondivisione(_token!);
  String get _testoPost => _testo.text.trim().isNotEmpty ? _testo.text.trim() : (_dati?.question ?? '');
  String get _didascalia => [_testoPost, _url].where((s) => s.isNotEmpty).join('\n\n');

  void _registra(String canale) {
    ref.read(lanternaProvider).traccia('share_completed', {'canale': canale});
    final visitatore = ref.read(visitatoreProvider)();
    unawaited(
      ref.read(apiProvider).registraClicCondivisione(widget.id, canale, visitatore).then((c) {
        if (c != null && mounted) setState(() => _contatore = c);
      }, onError: (Object _) {}),
    );
  }

  Future<bool> _condividiFile({required String testo}) async {
    final f = _file;
    if (f == null) return false;
    try {
      final esito = await SharePlus.instance.share(ShareParams(files: [f], text: testo, title: 'TAROTS chat'));
      return esito.status == ShareResultStatus.success;
    } on Object catch (e) {
      debugPrint('Foglio di condivisione non aperto: $e');
      return false;
    }
  }

  Future<void> _scegli(String canale) async {
    if (!_pronto) return;
    final t = context.t;
    final intento = urlIntento(canale, url: _url, testo: _testoPost, oggetto: 'TAROTS chat');
    if (intento != null) {
      _registra(canale);
      await apriFuori(intento);
      return;
    }
    if (canale == 'link') {
      await Clipboard.setData(ClipboardData(text: _url));
      if (mounted) setState(() => _avviso = (testo: t.lettura_cond_copiato, href: null, etichetta: null));
      _registra('link');
      return;
    }
    // Instagram e TikTok: il foglio di condivisione del telefono, con l'immagine e il testo.
    if (await _condividiFile(testo: _didascalia)) _registra(canale);
  }

  Future<void> _disattiva() async {
    try {
      await ref.read(apiProvider).condividiLettura(widget.id, attiva: false);
      if (mounted) Navigator.of(context).pop();
    } on ErroreApi catch (e) {
      debugPrint('Condivisione non spenta: ${e.stato}');
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final w = MediaQuery.sizeOf(context).width;
    final messaggio = switch (_stato) {
      _Stato.errore => t.lettura_cond_errore,
      _Stato.preparo => t.lettura_cond_preparo,
      _Stato.pronto => t.lettura_cond_pronta,
    };
    final piccolo = Stile.sans(13.44, colore: Token.inkSoft, altezza: 1.6);

    final sinistra = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // `.cornice`: 4:3, bordo sottile, fondo prugna; mentre si rifà, velata.
        AnimatedOpacity(
          opacity: _stato == _Stato.preparo ? .55 : 1,
          duration: MediaQuery.disableAnimationsOf(context) ? Duration.zero : const Duration(milliseconds: 200),
          child: AspectRatio(
            aspectRatio: misuraFinale.width / misuraFinale.height,
            child: Container(
              decoration: BoxDecoration(
                color: Token.plumDeep,
                border: Border.all(color: Token.line),
              ),
              child: _anteprima == null
                  ? null
                  : Image.memory(_anteprima!, fit: BoxFit.cover, semanticLabel: t.lettura_cond_anteprima),
            ),
          ),
        ),
        const SizedBox(height: 16),
        CampoTesto(
          etichetta: t.lettura_cond_testo,
          controllore: _testo,
          righe: 3,
          minimoRighe: 2,
          lunghezzaMassima: lunghezzaTesto,
          attivo: _dati != null,
          segnaposto: t.lettura_cond_testo_segnaposto,
          nota: '${t.lettura_cond_testo_aiuto} ${_testo.text.length}/$lunghezzaTesto',
        ),
      ],
    );

    final c = _contatore;
    final destra = Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Semantics(
            liveRegion: true,
            child: Wrap(
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 6,
              children: [
                Text(messaggio, style: Stile.sans(14.4, colore: Token.inkSoft, altezza: 1.6)),
                if (_stato == _Stato.errore)
                  Bottone(
                    t.comune_riprova,
                    piccolo: true,
                    variante: Variante.quieto,
                    alTocco: () {
                      setState(() {
                        _stato = _Stato.preparo;
                        _avviso = null;
                      });
                      unawaited(_sincronizza(null));
                    },
                  ),
              ],
            ),
          ),
        ),
        Eyebrow(t.lettura_cond_su, sotto: 8),
        _Canali(attivi: _pronto, alScegli: (canale) => unawaited(_scegli(canale))),
        if (_avviso != null) Successo(_avviso!.testo),
        Padding(
          padding: const EdgeInsets.only(top: 16),
          child: Align(
            alignment: AlignmentDirectional.centerStart,
            child: Bottone(
              t.lettura_cond_scarica,
              piccolo: true,
              variante: Variante.quieto,
              alTocco: _pronto ? () => unawaited(_condividiFile(testo: _didascalia)) : null,
            ),
          ),
        ),
        // `.premio`: il riquadro prugna dei premi e il contatore.
        Container(
          margin: const EdgeInsets.symmetric(vertical: 19.2),
          padding: const EdgeInsets.all(16),
          color: Token.plum,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Semantics(
                  header: true,
                  child: Text(
                    t.lettura_cond_premio_titolo.toUpperCase(),
                    style: Stile.sans(11.84, peso: FontWeight.w700, em: .08, colore: Token.brassPale, altezza: 1.4),
                  ),
                ),
              ),
              for (final v in [
                t.lettura_cond_premio_1(c?.soglia ?? 5),
                t.lettura_cond_premio_2(c?.creditiIscrizione ?? 5),
                t.lettura_cond_premio_3,
              ])
                Padding(
                  padding: const EdgeInsets.only(left: 6, bottom: 2),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('•  ', style: Stile.sans(13.76, colore: const Color(0xFFE6D8E8))),
                      Expanded(
                        child: Text(v, style: Stile.sans(13.76, colore: const Color(0xFFE6D8E8))),
                      ),
                    ],
                  ),
                ),
              if (c != null && c.soglia > 0) ...[
                Semantics(
                  label: t.lettura_cond_premio_titolo,
                  value: '${c.soglia - c.prossimoTra}/${c.soglia}',
                  child: Container(
                    height: 6,
                    margin: const EdgeInsets.only(top: 9.6 + 9.6, bottom: 4.8),
                    color: const Color(0x26FFFFFF),
                    alignment: AlignmentDirectional.centerStart,
                    child: FractionallySizedBox(
                      widthFactor: ((c.soglia - c.prossimoTra) / c.soglia).clamp(0, 1),
                      child: const ColoredBox(color: Token.brassPale, child: SizedBox.expand()),
                    ),
                  ),
                ),
                Text(t.lettura_cond_contatore(c.verificate, c.prossimoTra), style: piccolo.copyWith(color: _tenue)),
              ],
              Padding(
                padding: const EdgeInsets.only(top: 13.44),
                child: Text(t.lettura_cond_verificata, style: piccolo.copyWith(color: _tenue)),
              ),
            ],
          ),
        ),
        if (_dati?.speciale ?? false)
          Padding(
            padding: const EdgeInsets.only(bottom: 13.44),
            child: Paragrafo(t.lettura_cond_speciale, style: piccolo),
          ),
        Padding(
          padding: const EdgeInsets.only(bottom: 13.44),
          child: Paragrafo(t.lettura_cond_attivo, style: piccolo),
        ),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(
            t.lettura_cond_disattiva,
            piccolo: true,
            variante: Variante.pericolo,
            alTocco: () => unawaited(_disattiva()),
          ),
        ),
      ],
    );

    // `.corpo`: due colonne, una sotto l'altra fino a 760 px.
    if (w.telefono) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [sinistra, const SizedBox(height: 24), destra],
      );
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(child: sinistra),
        const SizedBox(width: 24),
        Expanded(child: destra),
      ],
    );
  }
}

const Color _tenue = Color(0xFFD9CADE);

/// `.canali`: tre per riga, ciascuno col marchio del canale nel suo cerchio e il nome sotto.
class _Canali extends StatelessWidget {
  const _Canali({required this.attivi, required this.alScegli});

  final bool attivi;
  final ValueChanged<String> alScegli;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    Widget canale(String c) {
      final nome = c == 'email' ? t.lettura_cond_email : (c == 'link' ? t.lettura_cond_link : _nomiRete[c]!);
      return Premibile(
        alTocco: attivi ? () => alScegli(c) : null,
        etichetta: t.lettura_cond_con(nome),
        costruisci: (context, premuto) => Opacity(
          opacity: attivi ? 1 : .55,
          child: Container(
            constraints: const BoxConstraints(minHeight: 72),
            padding: const EdgeInsets.symmetric(horizontal: 4.8, vertical: 9.6),
            decoration: BoxDecoration(
              color: const Color(0xFFFFFFFF),
              border: Border.all(color: premuto ? Token.brass : Token.line),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _Marchio(canale: c),
                const SizedBox(height: 4.8),
                Text(
                  nome,
                  textAlign: TextAlign.center,
                  style: Stile.sans(12.48, colore: Token.ink, altezza: 1.3),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final righe = <Widget>[];
    for (var i = 0; i < canali.length; i += 3) {
      if (i > 0) righe.add(const SizedBox(height: 8));
      righe.add(
        IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (var j = i; j < i + 3; j++) ...[
                if (j > i) const SizedBox(width: 8),
                Expanded(child: canale(canali[j])),
              ],
            ],
          ),
        ),
      );
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: righe);
  }
}

/// Il marchio di un canale (`lib/loghi.tsx`): il cerchio di 34 px col colore del marchio e il segno bianco.
class _Marchio extends StatelessWidget {
  const _Marchio({required this.canale});

  final String canale;

  @override
  Widget build(BuildContext context) {
    final fondo = switch (canale) {
      'instagram' => const BoxDecoration(
        shape: BoxShape.circle,
        gradient: LinearGradient(
          begin: Alignment.bottomLeft,
          end: Alignment.topRight,
          colors: [Color(0xFFF9A13A), Color(0xFFEE2A7B), Color(0xFF6228D7)],
          stops: [0, .45, 1],
        ),
      ),
      'link' => const BoxDecoration(
        shape: BoxShape.circle,
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF8F6C24), Color(0xFFD8B45A)],
        ),
      ),
      'facebook' => const BoxDecoration(shape: BoxShape.circle, color: Color(0xFF1877F2)),
      'email' => const BoxDecoration(shape: BoxShape.circle, color: Color(0xFF4F5D75)),
      _ => const BoxDecoration(shape: BoxShape.circle, color: Color(0xFF010101)),
    };
    return ExcludeSemantics(
      child: Container(
        width: 34,
        height: 34,
        decoration: fondo,
        alignment: Alignment.center,
        child: CustomPaint(size: const Size.square(18), painter: _Logo(canale)),
      ),
    );
  }
}

class _Logo extends CustomPainter {
  _Logo(this.canale);

  final String canale;

  static const String _facebook =
      'M13.6 22v-8.2h2.8l.5-3.4h-3.3V8.3c0-1 .4-1.7 1.8-1.7H17V3.5c-.3 0-1.3-.2-2.4-.2-2.6 0-4.3 1.6-4.3 4.4v2.7H7.4v3.4h2.9V22z';
  static const String _tiktok =
      'M16.6 2h-3.3v13.4a2.9 2.9 0 1 1-2.9-2.9c.3 0 .6 0 .9.1V9.2a6.2 6.2 0 1 0 5.3 6.2V8.7a7.8 7.8 0 0 0 4.4 1.4V6.8a4.5 4.5 0 0 1-4.4-4.8z';
  static const String _x =
      'M18.9 1.15h3.68l-8.04 9.19L24 22.85h-7.4l-5.8-7.58-6.64 7.58H.47l8.6-9.83L0 1.15h7.6l5.24 6.93zm-1.29 19.5h2.04L6.49 3.24H4.3z';
  static const String _email = 'M3.6 7.4 12 13.4l8.4-6';
  static const String _link1 = 'M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71';
  static const String _link2 = 'M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71';

  @override
  void paint(Canvas canvas, Size size) {
    canvas.scale(size.width / 24);
    const bianco = Color(0xFFFFFFFF);
    final pieno = Paint()..color = bianco;
    final tratto = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..color = bianco;
    switch (canale) {
      case 'instagram':
        canvas.drawRRect(
          RRect.fromRectAndRadius(const Rect.fromLTWH(3, 3, 18, 18), const Radius.circular(5.2)),
          tratto,
        );
        canvas.drawCircle(const Offset(12, 12), 4.1, tratto);
        canvas.drawCircle(const Offset(17.4, 6.6), 1.1, pieno);
      case 'facebook':
        canvas.drawPath(tracciato(_facebook), pieno);
      case 'tiktok':
        canvas.drawPath(tracciato(_tiktok), pieno);
      case 'x':
        canvas.drawPath(tracciato(_x)..fillType = PathFillType.evenOdd, pieno);
      case 'email':
        canvas.drawRRect(
          RRect.fromRectAndRadius(const Rect.fromLTWH(3, 5, 18, 14), const Radius.circular(2.4)),
          tratto,
        );
        canvas.drawPath(tracciato(_email), tratto);
      default:
        canvas.drawPath(tracciato(_link1), tratto);
        canvas.drawPath(tracciato(_link2), tratto);
    }
  }

  @override
  bool shouldRepaint(_Logo vecchio) => vecchio.canale != canale;
}
