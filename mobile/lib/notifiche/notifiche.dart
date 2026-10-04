/// Le notifiche dell'app (Fase 9), come quelle del sito (`frontend/v2/lib/notifiche.ts`, `componenti/notifiche.tsx`).
///
/// - **Il permesso in due tempi**: mai all'avvio; dopo aver girato la carta del giorno («vuoi che te la ricordiamo
///   ogni mattina?», [InvitoNotifiche]) o dal profilo (sezione «Notifiche»). Un «non ora» fa tacere l'invito per un
///   mese, come sul sito.
/// - **Il dispositivo**: dato il permesso, il token FCM va a `POST /me/dispositivi` con piattaforma, lingua, fuso
///   (`flutter_timezone`) e versione dell'app; di nuovo a ogni avvio con la sessione aperta, a ogni token nuovo e a ogni
///   cambio di lingua (la riga è una sola per token). La scelta resta su questo telefono (`notifiche.attive`).
/// - **All'uscita** (e prima di chiudere l'account): `DELETE /me/dispositivi` con la sessione ancora valida, poi il
///   token si cancella e la scelta si dimentica: chi entra dopo su questo telefono deciderà da sé.
/// - **Il tocco** apre il percorso del sito in `data.link` con la rotta uguale dell'app (`indirizzi.dart`) e segna la
///   notifica come aperta (`POST /notifiche/aperta`, con la firma dell'invio).
/// - **Il fuso** del telefono va anche sul profilo una volta per avvio (`PUT /me/fuso-orario`), come
///   `FusoAutomatico` del sito: decide il giorno della carta del giorno.
library;

import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart' show Locale;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../archivio.dart';
import '../auth/sessione.dart';
import '../cassa/pagamento.dart' show apriFuori;
import '../config.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../rotte/indirizzi.dart';
import '../rotte/router.dart';
import 'fuso.dart';
import 'push.dart';

/// La scelta di ricevere le notifiche su questo telefono (`1`), presa dalla persona.
const String chiaveNotificheAttive = 'notifiche.attive';

/// Quando l'invito dopo la carta del giorno è stato chiuso con «non ora» (millisecondi).
const String chiaveInvitoNotifiche = 'notifiche.invito';

/// Dopo un «non ora», l'invito torna fra un mese (come sul sito).
const Duration riposoInvito = Duration(days: 30);

/// Com'è andata l'attivazione.
enum EsitoAttivazione {
  /// Attive.
  attive,

  /// Il telefono (o la persona) ha negato il permesso.
  negato,

  /// Le notifiche non ci sono in questa app (Firebase non configurato).
  nonSupportato,

  /// Il token non è arrivato o il server non l'ha preso.
  errore,
}

/// Lo stato delle notifiche su questo telefono.
@immutable
class StatoNotifiche {
  /// Uno stato.
  const StatoNotifiche({
    this.pronte = false,
    this.disponibili = false,
    this.attive = false,
    this.permesso = PermessoPush.nonChiesto,
  });

  /// Si sa già se ci sono.
  final bool pronte;

  /// Le notifiche ci sono (Firebase configurato).
  final bool disponibili;

  /// Questo telefono riceve le notifiche dell'account.
  final bool attive;

  /// Il permesso del telefono.
  final PermessoPush permesso;

  @override
  bool operator ==(Object other) =>
      other is StatoNotifiche &&
      other.pronte == pronte &&
      other.disponibili == disponibili &&
      other.attive == attive &&
      other.permesso == permesso;

  @override
  int get hashCode => Object.hash(pronte, disponibili, attive, permesso);
}

/// Le notifiche.
class Notifiche extends Notifier<StatoNotifiche> {
  final List<StreamSubscription<Object>> _ascolti = [];
  String? _token;
  bool _fusoSalvato = false;

  ServizioPush get _servizio => ref.read(servizioPushProvider);
  Archivio get _archivio => ref.read(archivioProvider);
  bool get _scelte => _archivio.leggi(chiaveNotificheAttive) == '1';

  @override
  StatoNotifiche build() {
    ref.watch(servizioPushProvider);
    ref.read(primaDiUscireProvider).registra('notifiche', primaDiUscire);
    ref.listen(sessioneProvider.select((s) => s.autenticata), (prima, ora) {
      if (ora) unawaited(Future<void>.microtask(_allinea));
    });
    // Una lingua nuova: le notifiche arrivano in quella (il server la tiene per dispositivo).
    ref.listen(linguaProvider, (prima, ora) {
      if (prima == ora) return;
      if (state.disponibili) unawaited(_canali());
      if (state.attive) unawaited(_registra());
    });
    ref.onDispose(() {
      for (final a in _ascolti) {
        unawaited(a.cancel());
      }
      _ascolti.clear();
    });
    unawaited(Future<void>.microtask(_avvia));
    return const StatoNotifiche();
  }

  Future<void> _avvia() async {
    final servizio = _servizio;
    final disponibili = await servizio.avvia();
    if (!disponibili) {
      state = const StatoNotifiche(pronte: true);
      // Il fuso va sul profilo anche senza notifiche: decide il giorno della carta del giorno.
      await _allinea();
      return;
    }
    await _canali();
    _ascolti
      ..add(servizio.tokenNuovi.listen((token) {
        _token = token;
        if (state.attive) unawaited(_registra(token));
      }))
      ..add(servizio.toccate.listen((m) => unawaited(apri(m))));
    final permesso = await servizio.permesso();
    state = StatoNotifiche(
      pronte: true,
      disponibili: true,
      attive: _scelte && permesso == PermessoPush.concesso,
      permesso: permesso,
    );
    final iniziale = await servizio.iniziale();
    if (iniziale != null) unawaited(apri(iniziale));
    await _allinea();
  }

  /// I canali Android (`servizio`, `promozioni`) coi nomi nella lingua dell'app: si vedono nelle impostazioni del
  /// telefono, dove si può spegnere uno dei due.
  Future<void> _canali() async {
    final t = lookupAppLocalizations(Locale(ref.read(linguaProvider)));
    try {
      await _servizio.canali((
        servizio: t.app_canale_servizio,
        servizioTesto: t.app_canale_servizio_testo,
        promozioni: t.app_canale_promozioni,
        promozioniTesto: t.app_canale_promozioni_testo,
      ));
    } on Object catch (e) {
      debugPrint('Canali delle notifiche non creati: $e');
    }
  }

  /// Con la sessione aperta: il fuso sul profilo (una volta per avvio) e il token del telefono, se è stato scelto.
  Future<void> _allinea() async {
    if (!ref.read(sessioneProvider).autenticata) return;
    if (!_fusoSalvato) {
      final fuso = await ref.read(fusoProvider.future);
      if (fuso != null) {
        try {
          await ref.read(apiProvider).salvaFuso(fuso);
          _fusoSalvato = true;
        } on ErroreApi catch (e) {
          debugPrint('Fuso non salvato: $e');
        }
      }
    }
    if (state.attive) await _registra();
  }

  /// Manda il token di questo telefono al server. Vero se è andato.
  Future<bool> _registra([String? nuovo]) async {
    if (!ref.read(sessioneProvider).autenticata) return false;
    final token = nuovo ?? await _servizio.token();
    if (token == null || token.isEmpty) return false;
    _token = token;
    try {
      await ref
          .read(apiProvider)
          .registraDispositivo(
            token: token,
            piattaforma: ref.read(piattaformaProvider).name,
            lingua: ref.read(linguaProvider),
            fuso: await ref.read(fusoProvider.future),
            versione: Config.versione,
          );
      return true;
    } on ErroreApi catch (e) {
      debugPrint('Dispositivo delle notifiche non registrato: $e');
      return false;
    }
  }

  /// Accende le notifiche su questo telefono: chiede il permesso (deve partire da un tocco) e registra il token.
  Future<EsitoAttivazione> attiva() async {
    if (!state.pronte) await _servizio.avvia();
    if (!state.disponibili) return EsitoAttivazione.nonSupportato;
    final permesso = await _servizio.chiediPermesso();
    if (permesso != PermessoPush.concesso) {
      state = StatoNotifiche(pronte: true, disponibili: true, permesso: permesso);
      return permesso == PermessoPush.negato ? EsitoAttivazione.negato : EsitoAttivazione.errore;
    }
    if (!await _registra()) {
      state = StatoNotifiche(pronte: true, disponibili: true, permesso: permesso);
      return EsitoAttivazione.errore;
    }
    await _archivio.scrivi(chiaveNotificheAttive, '1');
    state = StatoNotifiche(pronte: true, disponibili: true, attive: true, permesso: permesso);
    return EsitoAttivazione.attive;
  }

  /// Spegne le notifiche su questo telefono: il server lo dimentica, il token si cancella.
  Future<void> disattiva() async {
    await _togli();
    state = StatoNotifiche(pronte: true, disponibili: state.disponibili, permesso: state.permesso);
  }

  /// Prima di uscire dall'account (o di chiuderlo), con la sessione ancora valida.
  Future<void> primaDiUscire() async {
    if (!_scelte && !state.attive) return;
    await _togli();
    state = StatoNotifiche(pronte: state.pronte, disponibili: state.disponibili, permesso: state.permesso);
  }

  Future<void> _togli() async {
    final token = _token ?? (state.disponibili ? await _servizio.token() : null);
    if (token != null && ref.read(sessioneProvider).autenticata) {
      try {
        await ref.read(apiProvider).togliDispositivo(token);
      } on ErroreApi catch (e) {
        debugPrint('Dispositivo delle notifiche non tolto dal server: $e');
      }
    }
    try {
      await _servizio.cancellaToken();
    } on Object catch (e) {
      debugPrint('Token delle notifiche non cancellato: $e');
    }
    _token = null;
    await _archivio.scrivi(chiaveNotificheAttive, null);
  }

  /// Apre le impostazioni delle notifiche del telefono (quando il permesso è negato).
  Future<void> apriImpostazioni() async {
    await _servizio.apriImpostazioni();
  }

  /// Rilegge il permesso (al ritorno dalle impostazioni del telefono).
  Future<void> rileggiPermesso() async {
    if (!state.disponibili) return;
    final permesso = await _servizio.permesso();
    final attive = _scelte && permesso == PermessoPush.concesso;
    state = StatoNotifiche(pronte: true, disponibili: true, attive: attive, permesso: permesso);
  }

  /// Il tocco su una notifica: la pagina del suo percorso, e l'apertura segnata al server.
  Future<void> apri(MessaggioPush m) async {
    final destinazione = destinazioneNotifica(m.link);
    if (destinazione == null) {
      await apriFuori(m.link);
    } else {
      unawaited(ref.read(routerProvider).push<void>(destinazione));
    }
    final invio = m.dati['invio'];
    final firma = m.dati['firma'];
    if (invio != null && firma != null) {
      try {
        await ref.read(apiProvider).notificaAperta(invio, firma);
      } on ErroreApi catch (e) {
        debugPrint('Apertura della notifica non segnata: $e');
      }
    }
  }

  /// L'invito dopo la carta del giorno: da mostrare (mai chiuso, o chiuso da più di un mese)?
  bool invitoDaMostrare(DateTime adesso) {
    final il = int.tryParse(_archivio.leggi(chiaveInvitoNotifiche) ?? '');
    return il == null || adesso.difference(DateTime.fromMillisecondsSinceEpoch(il)) > riposoInvito;
  }

  /// «Non ora» sull'invito.
  Future<void> invitoChiuso(DateTime adesso) =>
      _archivio.scrivi(chiaveInvitoNotifiche, '${adesso.millisecondsSinceEpoch}');
}

/// La rotta dell'app per il `link` di una notifica (un percorso del sito, o un indirizzo di tarots.chat); `null` per un
/// indirizzo di un altro sito, che si apre fuori.
String? destinazioneNotifica(String link) {
  final uri = Uri.tryParse(link.trim().isEmpty ? '/' : link.trim());
  if (uri == null) return '/';
  if (uri.hasScheme && !(uri.scheme == 'https' && (uri.host == 'tarots.chat' || uri.host == 'www.tarots.chat'))) {
    return null;
  }
  final percorso = interno(uri.path.isEmpty ? '/' : uri.path);
  return uri.hasQuery ? '$percorso?${uri.query}' : percorso;
}

/// Le notifiche del telefono.
final notificheProvider = NotifierProvider<Notifiche, StatoNotifiche>(Notifiche.new);
