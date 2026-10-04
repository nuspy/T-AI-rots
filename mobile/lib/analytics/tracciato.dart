/// Il collegamento fra l'osservatore ([Lanterna]) e l'app: il provider, il widget [Tracciato] (l'equivalente di
/// `data-an` del sito) e [OsservatoreApp], che segue il ciclo di vita, le interazioni e lo scorrimento.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;

import 'package:dio/dio.dart';
import 'package:flutter/gestures.dart' show kTouchSlop;
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../lingua/lingua.dart';
import 'lanterna.dart';

/// L'osservatore dell'app: manda i lotti a `POST /e` con il client dell'API (stessa base, stesso token, come il
/// sito con `Authorization`), in `text/plain` come `fetch` del sito.
final lanternaProvider = Provider<Lanterna>((ref) {
  final dio = ref.watch(dioProvider);
  final lanterna = Lanterna(
    invia: (corpo) => dio.post<void>(
      '/e',
      data: jsonEncode(corpo),
      options: Options(contentType: 'text/plain', responseType: ResponseType.plain),
    ),
    lingua: () => ref.read(linguaProvider),
    piattaforma: Platform.isIOS ? 'ios' : 'android',
  );
  // Il contenitore si chiude solo con l'app (o alla fine di un test): niente più invii, i provider non ci sono più.
  ref.onDispose(lanterna.spegni);
  return lanterna;
});

/// Un widget le cui pressioni contano come `data-an="nome"`: alla pressione (un tocco che non diventa uno
/// scorrimento) si accoda l'evento [an] con le [proprieta] (`data-an-*`). Non intercetta niente: il tocco arriva
/// comunque al pulsante dentro, come il clic arriva all'elemento nel browser.
class Tracciato extends ConsumerStatefulWidget {
  /// Un elemento tracciato.
  const Tracciato({super.key, required this.an, this.proprieta = const {}, required this.child});

  /// Il nome dell'evento (minuscole, cifre, `_`).
  final String an;

  /// Le proprietà dell'evento.
  final Map<String, String> proprieta;

  /// Il contenuto.
  final Widget child;

  @override
  ConsumerState<Tracciato> createState() => _TracciatoState();
}

class _TracciatoState extends ConsumerState<Tracciato> {
  Offset? _inizio;

  @override
  Widget build(BuildContext context) {
    return Listener(
      behavior: HitTestBehavior.translucent,
      onPointerDown: (e) => _inizio = e.position,
      onPointerCancel: (_) => _inizio = null,
      onPointerUp: (e) {
        final inizio = _inizio;
        _inizio = null;
        if (inizio == null || (e.position - inizio).distance > kTouchSlop) return;
        ref.read(lanternaProvider).traccia(widget.an, widget.proprieta.isEmpty ? null : widget.proprieta);
      },
      child: widget.child,
    );
  }
}

/// In cima all'albero: le interazioni (ogni tocco tiene vivo il tempo attivo), lo scorrimento della pagina e il
/// ciclo di vita dell'app (pausa e chiusura svuotano la coda, come `visibilitychange` e `pagehide` nel sito).
class OsservatoreApp extends ConsumerStatefulWidget {
  /// Attorno a [child].
  const OsservatoreApp({super.key, required this.child});

  /// L'app.
  final Widget child;

  @override
  ConsumerState<OsservatoreApp> createState() => _OsservatoreAppState();
}

class _OsservatoreAppState extends ConsumerState<OsservatoreApp> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState stato) {
    final lanterna = ref.read(lanternaProvider);
    switch (stato) {
      case AppLifecycleState.resumed:
        lanterna.inPrimoPiano();
      case AppLifecycleState.paused || AppLifecycleState.hidden || AppLifecycleState.detached:
        unawaited(lanterna.inPausa());
      case AppLifecycleState.inactive:
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Listener(
      behavior: HitTestBehavior.translucent,
      onPointerDown: (_) => ref.read(lanternaProvider).interazione(),
      child: NotificationListener<ScrollUpdateNotification>(
        onNotification: (n) {
          // Solo lo scorrimento verticale della pagina (non i caroselli orizzontali dentro).
          if (n.metrics.axis == Axis.vertical && n.depth == 0 && n.metrics.maxScrollExtent > 0) {
            ref.read(lanternaProvider).scorrimento(n.metrics.pixels / n.metrics.maxScrollExtent);
          }
          return false;
        },
        child: widget.child,
      ),
    );
  }
}
