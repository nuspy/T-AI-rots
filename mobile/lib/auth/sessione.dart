/// La sessione dell'app: come `useSessione()` del sito (`pronta`, `autenticata`, `nome`, `entra`, `esci`), più il
/// token d'accesso per il client dell'API, rinnovato col refresh token quando sta per scadere.
///
/// Tre modi, come nel sito:
/// - **Keycloak** (`KEYCLOAK_URL` impostato): si entra col social della piattaforma, il refresh token (offline) sta
///   nella cassaforte del sistema e all'avvio si riprende la sessione;
/// - **sviluppo** (`AUTH_DISATTIVATA=true`): sempre dentro, senza token (il backend locale usa il suo utente);
/// - **senza accesso** (nessuno dei due): l'app funziona da anonima.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../config.dart';
import '../lingua/lingua.dart';
import 'cassaforte.dart';
import 'configurazione.dart';
import 'fornitore.dart';

/// Ciò che il client dell'API chiede alla sessione.
abstract interface class FonteToken {
  /// Il token d'accesso valido (rinnovato se scade entro poco), o `null` senza sessione.
  Future<String?> token();

  /// Un token nuovo dopo un 401, o `null` se la sessione non si può rinnovare (e allora è finita).
  Future<String?> rinnova();
}

/// Lo stato della sessione.
@immutable
class StatoSessione {
  /// Uno stato.
  const StatoSessione({
    required this.pronta,
    required this.autenticata,
    this.nome,
    this.sviluppo = false,
    this.email,
    this.interrotta = false,
  });

  /// Si sa già se c'è una sessione (all'avvio la ripresa dal refresh token richiede un momento).
  final bool pronta;

  /// C'è una persona dentro.
  final bool autenticata;

  /// Il nome da mostrare (`given_name` o `name` del token).
  final String? nome;

  /// La sessione di sviluppo (`AUTH_DISATTIVATA`).
  final bool sviluppo;

  /// L'email del token (per riconoscere «Nascondi la mia email» di Apple).
  final String? email;

  /// La sessione è finita da sola (il refresh token non vale più: per esempio dopo che il codice dell'app è stato usato
  /// sul sito e l'accesso è passato all'account di là): l'app lo dice e propone di rientrare.
  final bool interrotta;

  @override
  bool operator ==(Object other) =>
      other is StatoSessione &&
      other.pronta == pronta &&
      other.autenticata == autenticata &&
      other.nome == nome &&
      other.sviluppo == sviluppo &&
      other.email == email &&
      other.interrotta == interrotta;

  @override
  int get hashCode => Object.hash(pronta, autenticata, nome, sviluppo, email, interrotta);
}

/// La piattaforma corrente (Android → Google, iOS → Apple). I test la sostituiscono.
final piattaformaProvider = Provider<Piattaforma>((ref) => Platform.isIOS ? Piattaforma.ios : Piattaforma.android);

/// La configurazione di Keycloak, o `null` se l'accesso non è configurato.
final configAccessoProvider = Provider<ConfigAccesso?>((ref) => ConfigAccesso.per(ref.watch(piattaformaProvider)));

/// Il fornitore OAuth (finto nei test).
final fornitoreOAuthProvider = Provider<FornitoreOAuth>((ref) => FornitoreAppAuth());

/// La cassaforte del refresh token (in memoria nei test).
final cassaforteProvider = Provider<Cassaforte>((ref) => CassaforteSistema());

/// L'orologio (fermo nei test).
final orologioProvider = Provider<DateTime Function()>((ref) => DateTime.now);

/// Vero per la sessione di sviluppo (sostituibile nei test).
final authDisattivataProvider = Provider<bool>((ref) => Config.authDisattivata);

/// Il nome nel token (`given_name`, altrimenti `name`), senza verificarlo: lo verifica il server a ogni chiamata.
String? nomeDaToken(String? token) {
  if (token == null) return null;
  final parti = token.split('.');
  if (parti.length < 2) return null;
  try {
    final dati = jsonDecode(utf8.decode(base64Url.decode(base64Url.normalize(parti[1]))));
    if (dati is! Map) return null;
    final nome = dati['given_name'] ?? dati['name'];
    return nome is String && nome.isNotEmpty ? nome : null;
  } on FormatException {
    return null;
  }
}

/// L'email nel token (`email`), senza verificarlo.
String? emailDaToken(String? token) {
  if (token == null) return null;
  final parti = token.split('.');
  if (parti.length < 2) return null;
  try {
    final dati = jsonDecode(utf8.decode(base64Url.decode(base64Url.normalize(parti[1]))));
    final email = dati is Map ? dati['email'] : null;
    return email is String && email.isNotEmpty ? email : null;
  } on FormatException {
    return null;
  }
}

/// Vero per un'email di «Nascondi la mia email» di Apple: l'account dell'app è nuovo anche se ce n'è uno sul sito.
bool emailNascosta(String? email) => email?.toLowerCase().endsWith('@privaterelay.appleid.com') ?? false;

/// La sessione.
class Sessione extends Notifier<StatoSessione> implements FonteToken {
  /// Quanto prima della scadenza si rinnova il token d'accesso.
  static const Duration margine = Duration(seconds: 30);

  Credenziali? _credenziali;
  Future<String?>? _rinnovoInCorso;

  @override
  StatoSessione build() {
    if (ref.watch(authDisattivataProvider)) {
      return const StatoSessione(pronta: true, autenticata: true, nome: 'Sviluppo', sviluppo: true);
    }
    if (ref.watch(configAccessoProvider) == null) return const StatoSessione(pronta: true, autenticata: false);
    unawaited(Future<void>.microtask(_riprendi));
    return const StatoSessione(pronta: false, autenticata: false);
  }

  ConfigAccesso? get _config => ref.read(configAccessoProvider);
  Cassaforte get _cassaforte => ref.read(cassaforteProvider);

  /// All'avvio: se c'è un refresh token, la sessione riprende.
  Future<void> _riprendi() async {
    final refresh = await _cassaforte.leggi();
    if (refresh == null) {
      state = const StatoSessione(pronta: true, autenticata: false);
      return;
    }
    final token = await rinnova();
    if (token == null) return; // `_rinnova` ha già detto che la sessione si è interrotta
    final c = _credenziali;
    state = StatoSessione(
      pronta: true,
      autenticata: true,
      nome: nomeDaToken(c?.idToken ?? token),
      email: emailDaToken(c?.idToken ?? token),
    );
  }

  void _usa(Credenziali c) {
    _credenziali = c;
    state = StatoSessione(
      pronta: true,
      autenticata: true,
      nome: nomeDaToken(c.idToken ?? c.accessToken),
      email: emailDaToken(c.idToken ?? c.accessToken),
    );
  }

  /// Entra col social della piattaforma. Solleva [ErroreAccesso] se non riesce o se chi entra annulla.
  Future<void> entra() async {
    final config = _config;
    if (config == null) throw const ErroreAccesso('accesso non configurato (KEYCLOAK_URL)');
    final c = await ref.read(fornitoreOAuthProvider).entra(config, lingua: ref.read(linguaProvider));
    await _cassaforte.salva(c.refreshToken);
    _usa(c);
  }

  /// Esce: prima ciò che serve la sessione ancora valida ([primaDiUscireProvider]: toglie questo telefono dalle
  /// notifiche dell'account), poi revoca il token offline, chiude la sessione di Keycloak, cancella i token locali.
  Future<void> esci() async {
    await ref.read(primaDiUscireProvider).esegui();
    if (state.sviluppo) return;
    final config = _config;
    final c = _credenziali;
    final refresh = c?.refreshToken ?? await _cassaforte.leggi();
    _credenziali = null;
    await _cassaforte.salva(null);
    state = const StatoSessione(pronta: true, autenticata: false);
    if (config != null) await ref.read(fornitoreOAuthProvider).esci(config, refreshToken: refresh, idToken: c?.idToken);
  }

  /// L'avviso della sessione interrotta è stato letto.
  void avvisoLetto() {
    if (state.interrotta) state = StatoSessione(pronta: state.pronta, autenticata: state.autenticata);
  }

  @override
  Future<String?> token() async {
    if (state.sviluppo) return null;
    final c = _credenziali;
    if (c != null && !c.scadeEntro(margine, ref.read(orologioProvider)())) return c.accessToken;
    if (c == null && !state.autenticata && state.pronta) return null;
    return rinnova();
  }

  @override
  Future<String?> rinnova() => _rinnovoInCorso ??= _rinnova().whenComplete(() => _rinnovoInCorso = null);

  Future<String?> _rinnova() async {
    final config = _config;
    if (config == null || state.sviluppo) return null;
    final refresh = _credenziali?.refreshToken ?? await _cassaforte.leggi();
    if (refresh == null) return null;
    try {
      final c = await ref.read(fornitoreOAuthProvider).rinnova(config, refresh);
      if (c.refreshToken != null && c.refreshToken != refresh) await _cassaforte.salva(c.refreshToken);
      _usa(c);
      return c.accessToken;
    } on ErroreAccesso catch (e) {
      debugPrint('Sessione non rinnovata: ${e.motivo}');
      _credenziali = null;
      await _cassaforte.salva(null);
      state = const StatoSessione(pronta: true, autenticata: false, interrotta: true);
      return null;
    }
  }
}

/// La sessione dell'app.
final sessioneProvider = NotifierProvider<Sessione, StatoSessione>(Sessione.new);

/// Ciò che va fatto con la sessione ancora valida, appena prima di uscire (o di chiudere l'account): Fase 9, togliere
/// questo telefono dalle notifiche dell'account (`DELETE /me/dispositivi`). Ogni azione ha pochi secondi: l'uscita non
/// aspetta un server che non risponde.
class PrimaDiUscire {
  final Map<String, Future<void> Function()> _azioni = {};

  /// Registra (o sostituisce) l'azione [nome].
  void registra(String nome, Future<void> Function() azione) => _azioni[nome] = azione;

  /// Esegue tutte le azioni; un errore non ferma l'uscita.
  Future<void> esegui() async {
    for (final e in _azioni.entries) {
      try {
        await e.value().timeout(const Duration(seconds: 5));
      } on Object catch (errore) {
        debugPrint('Prima di uscire, «${e.key}» non è riuscito: $errore');
      }
    }
  }
}

/// Le azioni prima dell'uscita.
final primaDiUscireProvider = Provider<PrimaDiUscire>((ref) => PrimaDiUscire());

/// «Entra» da un bottone: l'accesso col social della piattaforma; un errore (o chi annulla) resta nel log, come il
/// sito che torna alla pagina. Vero se adesso c'è una sessione.
Future<bool> entraDa(WidgetRef ref) async {
  try {
    await ref.read(sessioneProvider.notifier).entra();
  } on Object catch (e) {
    debugPrint('Accesso non riuscito: $e');
  }
  return ref.read(sessioneProvider).autenticata;
}
