/// La sezione «Notifiche» del profilo (`NotificheProfilo` di `frontend/v2/componenti/notifiche.tsx`, Fase 9): accese o
/// spente su questo telefono, carta del giorno e la sua ora, promemoria, offerte (lo stesso consenso «Promozioni»
/// della privacy: il link di disiscrizione delle notifiche lo spegne, e qui si vede spento), ore di silenzio, il fuso.
///
/// Le preferenze sono quelle dell'account (`GET/PUT /me/preferenze-notifica`), le stesse del sito: valgono per il
/// telefono e per il browser. Se il permesso è negato, il bottone apre le impostazioni del telefono.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:material_ui/material_ui.dart' show TimeOfDay, showTimePicker;

import '../api/api.dart';
import '../api/errori.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/pagina.dart' show messaggioErrore;
import '../componenti/premibile.dart';
import '../consensi/consensi.dart';
import '../l10n/testi.dart';
import '../modelli/notifiche.dart';
import '../notifiche/notifiche.dart';
import '../notifiche/push.dart';
import '../tema/tema.dart';
import 'comuni.dart';
import 'dati_account.dart';

/// Le preferenze delle notifiche dell'account.
final preferenzeNotificaProvider = FutureProvider.autoDispose<PreferenzeNotifica>(
  (ref) => ref.read(apiProvider).preferenzeNotifica(),
);

/// La sezione «Notifiche».
class NotificheProfilo extends ConsumerStatefulWidget {
  /// La sezione.
  const NotificheProfilo({super.key});

  @override
  ConsumerState<NotificheProfilo> createState() => _NotificheProfiloState();
}

class _NotificheProfiloState extends ConsumerState<NotificheProfilo> with WidgetsBindingObserver {
  bool _lavoro = false;
  bool _salvando = false;
  bool _salvato = false;
  EsitoAttivazione? _esito;
  String? _errore;
  Timer? _spegniSalvato;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _spegniSalvato?.cancel();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState stato) {
    // Tornati dalle impostazioni del telefono: il permesso può essere cambiato.
    if (stato == AppLifecycleState.resumed) unawaited(ref.read(notificheProvider.notifier).rileggiPermesso());
  }

  Future<void> _salva(Map<String, Object?> modifiche) async {
    setState(() {
      _salvando = true;
      _errore = null;
    });
    try {
      await ref.read(apiProvider).salvaPreferenzeNotifica(modifiche);
      ref.invalidate(preferenzeNotificaProvider);
      if (!mounted) return;
      setState(() => _salvato = true);
      _spegniSalvato?.cancel();
      _spegniSalvato = Timer(const Duration(seconds: 3), () {
        if (mounted) setState(() => _salvato = false);
      });
    } on ErroreApi catch (e) {
      if (mounted) setState(() => _errore = e.messaggio(context.t));
    } finally {
      if (mounted) setState(() => _salvando = false);
    }
  }

  /// «Offerte e novità»: è il consenso `marketing`, lo stesso della privacy.
  Future<void> _promozioni(bool acceso) async {
    setState(() {
      _salvando = true;
      _errore = null;
    });
    try {
      await ref.read(consensiProvider.notifier).scegli({'marketing': acceso ? 'accettato' : 'rifiutato'});
      ref.invalidate(preferenzeNotificaProvider);
      ref.invalidate(consensiAccountProvider);
      ref.invalidate(statoPrivacyProvider);
    } finally {
      if (mounted) setState(() => _salvando = false);
    }
  }

  Future<void> _attiva() async {
    setState(() {
      _lavoro = true;
      _esito = null;
    });
    final esito = await ref.read(notificheProvider.notifier).attiva();
    ref.invalidate(preferenzeNotificaProvider);
    if (mounted) {
      setState(() {
        _lavoro = false;
        _esito = esito;
      });
    }
  }

  Future<void> _disattiva() async {
    setState(() => _lavoro = true);
    await ref.read(notificheProvider.notifier).disattiva();
    ref.invalidate(preferenzeNotificaProvider);
    if (mounted) {
      setState(() {
        _lavoro = false;
        _esito = null;
      });
    }
  }

  Future<void> _scegliOra(String? attuale, void Function(String) alCambio) async {
    final parti = (attuale ?? '08:30').split(':');
    final scelta = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: int.tryParse(parti.first) ?? 8, minute: int.tryParse(parti.last) ?? 30),
    );
    if (scelta == null) return;
    String due(int n) => n.toString().padLeft(2, '0');
    alCambio('${due(scelta.hour)}:${due(scelta.minute)}');
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final stato = ref.watch(notificheProvider);
    final preferenze = ref.watch(preferenzeNotificaProvider);
    final p = preferenze.value;
    final negato = stato.permesso == PermessoPush.negato;
    // Gli altri dispositivi con le notifiche accese (i browser e gli altri telefoni): questo, se acceso, non conta.
    final altri = (p?.dispositivi.where((d) => d.attivo).length ?? 0) - (stato.attive ? 1 : 0);
    final erroreAttivazione = switch (_esito) {
      EsitoAttivazione.errore => t.notifiche_errore,
      EsitoAttivazione.nonSupportato => t.app_push_non_disponibile,
      _ => null,
    };

    return Sezione(
      titolo: t.notifiche_titolo,
      id: 'notifiche',
      children: [
        TestoPiccolo(t.notifiche_intro),
        if (stato.pronte && !stato.disponibili) TestoPiccolo(t.app_push_non_disponibile, tenue: true),
        if (stato.disponibili) ...[
          Semantics(
            liveRegion: true,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 9.6),
              child: Text(
                stato.attive ? t.app_push_stato_attive : t.app_push_stato_spente,
                style: Stile.sans(13.44, peso: FontWeight.w700, colore: Token.ink, altezza: 1.6),
              ),
            ),
          ),
          FilaBottoni(
            children: [
              if (stato.attive)
                Bottone(
                  t.app_push_disattiva,
                  variante: Variante.quieto,
                  piccolo: true,
                  an: 'notifiche_spente',
                  alTocco: _lavoro ? null : () => unawaited(_disattiva()),
                )
              else if (negato)
                Bottone(
                  t.app_push_impostazioni,
                  piccolo: true,
                  alTocco: () => unawaited(ref.read(notificheProvider.notifier).apriImpostazioni()),
                )
              else
                Bottone(
                  _lavoro ? t.notifiche_attivazione : t.app_push_attiva,
                  piccolo: true,
                  an: 'notifiche_accese',
                  alTocco: _lavoro ? null : () => unawaited(_attiva()),
                ),
            ],
          ),
          if (negato && !stato.attive) Errore(t.app_push_negato, sopra: 9.6),
          if (erroreAttivazione != null) Errore(erroreAttivazione, sopra: 9.6),
        ],
        if (altri > 0) TestoPiccolo(t.notifiche_altri(altri), tenue: true, sopra: 9.6),
        if (p != null) ..._scelte(t, p),
        if (preferenze.hasError && !preferenze.hasValue) Errore(messaggioErrore(preferenze.error!, t)),
        if (_errore != null) Errore(_errore!),
        Semantics(
          liveRegion: true,
          child: Padding(
            padding: const EdgeInsets.only(top: 6.4),
            child: Text(_salvato ? t.notifiche_salvato : '', style: stilePiccolo()),
          ),
        ),
      ],
    );
  }

  List<Widget> _scelte(AppLocalizations t, PreferenzeNotifica p) {
    final rientro = MediaQuery.sizeOf(context).width <= 480 ? 0.0 : 29.6;
    return [
      const SizedBox(height: 12.8),
      Casella(
        valore: p.cartaGiorno,
        titolo: t.notifiche_carta,
        testo: t.notifiche_carta_testo,
        attiva: !_salvando,
        alCambio: (v) => unawaited(_salva({'carta_giorno': v})),
      ),
      if (p.cartaGiorno)
        Padding(
          padding: EdgeInsetsDirectional.only(start: rientro, bottom: 9.6),
          child: _Ora(
            etichetta: t.notifiche_ora,
            valore: p.oraCarta,
            alTocco: _salvando ? null : () => unawaited(_scegliOra(p.oraCarta, (o) => _salva({'ora_carta': o}))),
          ),
        ),
      Casella(
        valore: p.promemoria,
        titolo: t.notifiche_promemoria,
        testo: t.notifiche_promemoria_testo,
        attiva: !_salvando,
        alCambio: (v) => unawaited(_salva({'promemoria': v})),
      ),
      Casella(
        valore: p.promozioni,
        titolo: t.notifiche_promozioni,
        testo: t.notifiche_promozioni_testo(p.tettoPromozioniSettimana),
        attiva: !_salvando,
        alCambio: (v) => unawaited(_promozioni(v)),
      ),
      Casella(
        valore: p.silenzio,
        titolo: t.notifiche_silenzio,
        testo: t.notifiche_silenzio_testo,
        attiva: !_salvando,
        alCambio: (v) => unawaited(_salva({'silenzio': v})),
      ),
      if (p.silenzio)
        Padding(
          padding: EdgeInsetsDirectional.only(start: rientro, bottom: 9.6),
          child: Row(
            children: [
              Expanded(
                child: _Ora(
                  etichetta: t.notifiche_dalle,
                  valore: p.silenzioDal,
                  alTocco: _salvando
                      ? null
                      : () => unawaited(_scegliOra(p.silenzioDal, (o) => _salva({'silenzio': true, 'silenzio_dal': o}))),
                ),
              ),
              const SizedBox(width: 12.8),
              Expanded(
                child: _Ora(
                  etichetta: t.notifiche_alle,
                  valore: p.silenzioAl,
                  alTocco: _salvando
                      ? null
                      : () => unawaited(_scegliOra(p.silenzioAl, (o) => _salva({'silenzio': true, 'silenzio_al': o}))),
                ),
              ),
            ],
          ),
        ),
      if (p.fusoOrario != null)
        TestoPiccolo(t.notifiche_fuso(p.fusoOrario!.replaceAll('_', ' ')), tenue: true, sopra: 6.4, sotto: 0),
    ];
  }
}

/// Un orario (`<input type="time">` del sito): l'etichetta e il valore, che apre l'orologio del telefono.
class _Ora extends StatelessWidget {
  const _Ora({required this.etichetta, required this.valore, required this.alTocco});

  final String etichetta;
  final String? valore;
  final VoidCallback? alTocco;

  @override
  Widget build(BuildContext context) {
    final testo = valore ?? '--:--';
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 192),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 5.6),
            child: Text(etichetta, style: stileEtichettaCampo()),
          ),
          Premibile(
            etichetta: '$etichetta: $testo',
            alTocco: alTocco,
            costruisci: (context, premuto) => Container(
              constraints: const BoxConstraints(minHeight: Token.altezzaBottone),
              padding: const EdgeInsets.symmetric(horizontal: 12.8, vertical: 11.2),
              decoration: BoxDecoration(
                color: premuto ? const Color(0xFFF7F3EC) : const Color(0xFFFFFFFF),
                border: Border.all(color: Token.line),
              ),
              child: Row(
                children: [
                  Expanded(child: Text(testo, style: Stile.sans(16, colore: Token.ink, altezza: 1.5))),
                  Text('◷', style: Stile.sans(14, colore: Token.inkSoft)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
