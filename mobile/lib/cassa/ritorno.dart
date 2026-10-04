/// Il ritorno da un pagamento quando il deep link non arriva: tornata l'app in primo piano con un pagamento in sospeso
/// ([pagamentoInSospesoProvider]), dopo un attimo (il tempo che il deep link, se c'è, arrivi per primo) si va alla
/// pagina di ritorno, che chiede al server com'è andata.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../rotte/router.dart';
import 'pagamento.dart';

/// Attorno all'app.
class RitornoPagamento extends ConsumerStatefulWidget {
  /// Attorno a [child].
  const RitornoPagamento({super.key, required this.child});

  /// L'app.
  final Widget child;

  @override
  ConsumerState<RitornoPagamento> createState() => _RitornoPagamentoState();
}

class _RitornoPagamentoState extends ConsumerState<RitornoPagamento> with WidgetsBindingObserver {
  Timer? _attesa;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _attesa?.cancel();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState stato) {
    if (stato != AppLifecycleState.resumed || ref.read(pagamentoInSospesoProvider) == null) return;
    _attesa?.cancel();
    _attesa = Timer(const Duration(milliseconds: 700), () {
      final ritorno = ref.read(pagamentoInSospesoProvider);
      if (ritorno == null || !mounted) return;
      ref.read(pagamentoInSospesoProvider.notifier).concluso();
      ref.read(routerProvider).go(ritorno);
    });
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
