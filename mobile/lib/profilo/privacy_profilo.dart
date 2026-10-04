/// «Privacy e consensi» nel profilo (`frontend/v2/pagine/privacy-profilo.tsx`, GDPR, Fase 1): ogni consenso, revocabile
/// come si è dato (una casella), il download dei propri dati, la cancellazione della chat e dell'account.
///
/// Le categorie: statistiche (dell'app), Google Analytics (Firebase), testi per statistiche e spunti del blog, dati
/// particolari (art. 9), promozioni. Dove il sito parla del browser e dei cookie l'app ha testi suoi
/// (`app_cons_*`). La pubblicità non c'è nell'app (decisione: niente pubblicità al lancio), quindi nemmeno la sua
/// casella. Le scelte passano da [consensiProvider]: statistiche e Google Analytics si applicano subito (lanterna e
/// Firebase, `app.dart`), le altre vanno al server con l'origine `android`/`ios`.
///
/// L'archivio dei dati (ZIP) si salva in un file temporaneo e si passa al foglio del telefono, che chiede dove
/// salvarlo o a chi mandarlo: l'equivalente del download del sito.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../api/api.dart';
import '../api/errori.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/modale.dart';
import '../componenti/premibile.dart';
import '../consensi/consensi.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../rotte/percorsi.dart';
import '../tema/tema.dart';
import 'comuni.dart';
import 'dati_account.dart';

/// Le categorie che il profilo mostra, nell'ordine del sito (senza la pubblicità).
const List<String> categorieProfilo = [
  'statistiche',
  'google_analytics',
  'testi_statistiche',
  'dati_particolari',
  'marketing',
];

/// Scarica l'archivio dei propri dati e lo passa al foglio del telefono. Il messaggio da mostrare: «pronto», o la data
/// dalla quale si potrà riscaricare (una volta ogni 24 ore); `null` se non è riuscito per un altro motivo ([ErroreApi]).
Future<String> scaricaEsportazione(WidgetRef ref, BuildContext context) async {
  final t = context.t;
  final lingua = ref.read(linguaProvider);
  try {
    final r = await ref.read(apiProvider).esportazione();
    if (!context.mounted) return t.app_file_pronto;
    await condividiFile(ref, context, byte: r.byte, nome: r.nome ?? 'tarots-chat-dati.zip', tipo: 'application/zip');
    return t.app_file_pronto;
  } on ErroreApi catch (e) {
    if (e.stato != 429) rethrow;
    final d = e.dettaglio;
    final prossima = d is Map ? d['prossima_dal'] as String? : null;
    return t.profilo_esporta_attendi(prossima == null ? '' : dataLunga(prossima, lingua));
  }
}

/// La sezione «Privacy e consensi».
class PrivacyProfilo extends ConsumerStatefulWidget {
  /// La sezione; [alCambio] quando si spengono i dati particolari (il profilo si rilegge: la casella trans sparisce).
  const PrivacyProfilo({super.key, this.alCambio, this.chiave});

  /// Dopo la revoca dei dati particolari.
  final VoidCallback? alCambio;

  /// L'ancora (`#privacy`).
  final GlobalKey? chiave;

  @override
  ConsumerState<PrivacyProfilo> createState() => _PrivacyProfiloState();
}

class _PrivacyProfiloState extends ConsumerState<PrivacyProfilo> with AzioneAccount {
  String? _salvando;
  bool _erroreScelta = false;
  String? _esportazione;
  bool _chatCancellata = false;
  final Map<String, String> _scelte = {};

  String? _valore(String tipo) {
    if (_scelte.containsKey(tipo)) return _scelte[tipo];
    if (categorieApp.contains(tipo)) {
      final locale = ref.watch(consensiProvider).valori[tipo];
      if (locale != null) return locale;
    }
    return ref.watch(consensiAccountProvider).value?[tipo];
  }

  Future<void> _cambia(String tipo, bool acceso) async {
    final valore = acceso ? 'accettato' : 'rifiutato';
    setState(() {
      _salvando = tipo;
      _erroreScelta = false;
    });
    try {
      // Le scelte delle categorie dell'app valgono subito anche sul telefono (lanterna, Firebase); le altre sono
      // dell'account: vanno al server, e lo stato si rilegge.
      await ref.read(consensiProvider.notifier).scegli({tipo: valore});
      final server = await ref.read(apiProvider).consensi();
      if (server[tipo] != valore) throw const ErroreApi(0);
      if (!mounted) return;
      setState(() => _scelte[tipo] = valore);
      ref.invalidate(statoPrivacyProvider);
      ref.invalidate(consensiAccountProvider);
      if (tipo == 'dati_particolari' && !acceso) widget.alCambio?.call();
    } on ErroreApi {
      if (mounted) setState(() => _erroreScelta = true);
    } finally {
      if (mounted) setState(() => _salvando = null);
    }
  }

  Future<void> _esporta() async {
    setState(() => _esportazione = null);
    final r = await esegui((_) => scaricaEsportazione(ref, context));
    if (r == null || !mounted) return;
    setState(() => _esportazione = r);
    ref.invalidate(statoPrivacyProvider);
  }

  Future<void> _cancellaChat() async {
    final t = context.t;
    final si = await apriModale<bool>(
      context,
      titolo: t.profilo_chat_cancella,
      costruisci: (context) => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 16), child: Text(t.profilo_chat_conferma)),
          FilaBottoni(
            children: [
              Bottone(
                t.profilo_chat_cancella,
                variante: Variante.pericolo,
                alTocco: () => Navigator.of(context).pop(true),
              ),
              Bottone(t.comune_annulla, variante: Variante.quieto, alTocco: () => Navigator.of(context).pop(false)),
            ],
          ),
        ],
      ),
    );
    if (si != true) return;
    final r = await esegui((api) async {
      await api.cancellaChat();
      return true;
    });
    if (r == true && mounted) setState(() => _chatCancellata = true);
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    final stato = ref.watch(statoPrivacyProvider).value;
    final pronti = ref.watch(consensiAccountProvider).hasValue;
    String data(String? iso) => iso == null ? '' : dataLunga(iso, lingua);
    final voci = {
      'statistiche': (titolo: t.app_consenso_statistiche, testo: t.app_cons_statistiche_testo),
      'google_analytics': (titolo: t.profilo_cons_google, testo: t.app_cons_google_testo),
      'testi_statistiche': (titolo: t.profilo_cons_testi, testo: t.profilo_cons_testi_testo),
      'dati_particolari': (titolo: t.profilo_cons_art9, testo: t.profilo_cons_art9_testo),
      'marketing': (titolo: t.profilo_cons_marketing, testo: t.profilo_cons_marketing_testo),
    };
    return Sezione(
      chiave: widget.chiave,
      titolo: t.profilo_privacy_titolo,
      id: 'privacy',
      children: [
        TestoPiccolo(
          t.profilo_privacy_testo,
          figlio: Collegamento(t.profilo_stat_privacy, href: R.privacy, stile: Stile.sans(13.44, altezza: 1.6)),
        ),
        // `.consensi-elenco`: una casella per categoria, una riga fra l'una e l'altra.
        Padding(
          padding: const EdgeInsets.only(top: 3.2, bottom: 12.8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              for (final (i, tipo) in categorieProfilo.indexed)
                Container(
                  decoration: i == 0
                      ? null
                      : const BoxDecoration(
                          border: Border(top: BorderSide(color: Token.line)),
                        ),
                  child: Builder(
                    builder: (context) {
                      final valore = _valore(tipo);
                      final il = stato?.consensi[tipo]?.il;
                      final statoTesto = valore == 'accettato'
                          ? t.profilo_cons_attivo
                          : valore == 'rifiutato'
                          ? t.profilo_cons_spento
                          : t.profilo_cons_mai;
                      return CasellaConsenso(
                        valore: valore == 'accettato',
                        attiva: pronti && _salvando == null,
                        alCambio: (v) => unawaited(_cambia(tipo, v)),
                        titolo: voci[tipo]!.titolo,
                        stato: il == null ? statoTesto : '$statoTesto · ${data(il)}',
                        testo: voci[tipo]!.testo,
                      );
                    },
                  ),
                ),
            ],
          ),
        ),
        if (_erroreScelta) Errore(t.comune_err_operazione, sopra: 0),
        TitoloPannello(t.profilo_esporta_titolo),
        TestoPiccolo(t.profilo_esporta_testo),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(t.profilo_esporta_cta, piccolo: true, alTocco: inCorso ? null : () => unawaited(_esporta())),
        ),
        if (_esportazione != null)
          Semantics(liveRegion: true, child: TestoPiccolo(_esportazione!, sopra: 13.44, sotto: 0)),
        if (_esportazione == null && stato?.esportazione.ultimaIl != null)
          TestoPiccolo(
            t.profilo_esporta_ultima(data(stato!.esportazione.ultimaIl)),
            tenue: true,
            sopra: 13.44,
            sotto: 0,
          ),
        TitoloPannello(t.profilo_chat_titolo),
        TestoPiccolo(t.profilo_chat_testo),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(
            t.profilo_chat_cancella,
            piccolo: true,
            variante: Variante.quieto,
            alTocco: inCorso ? null : () => unawaited(_cancellaChat()),
          ),
        ),
        if (_chatCancellata) Successo(t.profilo_chat_cancellata),
        TitoloPannello(t.profilo_elimina_titolo),
        TestoPiccolo(t.profilo_elimina_breve(stato?.cancellazione.giorniRipensamento ?? 30)),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(t.profilo_elimina_cta, href: R.elimina, piccolo: true, variante: Variante.pericolo),
        ),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}

/// Una casella di consenso (`.consensi-elenco .check`): il titolo in grassetto, lo stato (`.consenso-stato`) e la
/// spiegazione, tutto dentro lo stesso `<label>` (tutto si tocca).
class CasellaConsenso extends StatelessWidget {
  /// Una casella.
  const CasellaConsenso({
    super.key,
    required this.valore,
    required this.attiva,
    required this.alCambio,
    required this.titolo,
    required this.stato,
    required this.testo,
  });

  /// Acceso.
  final bool valore;

  /// Si può toccare.
  final bool attiva;

  /// Il nuovo valore.
  final ValueChanged<bool> alCambio;

  /// La categoria.
  final String titolo;

  /// «Attivo · 3 ottobre 2026».
  final String stato;

  /// La spiegazione.
  final String testo;

  @override
  Widget build(BuildContext context) {
    final piccolo = Stile.sans(12.8, colore: Token.inkSoft, altezza: 1.45);
    return MergeSemantics(
      child: Opacity(
        opacity: attiva ? 1 : .55,
        child: Premibile(
          alTocco: attiva ? () => alCambio(!valore) : null,
          pulsante: false,
          costruisci: (context, premuto) => ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 44),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 9.6),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 2.4),
                    child: Semantics(
                      checked: valore,
                      child: SizedBox(width: 20, height: 20, child: CustomPaint(painter: Casellina(valore))),
                    ),
                  ),
                  const SizedBox(width: 9.6),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          titolo,
                          style: Stile.sans(14.4, peso: FontWeight.w700, colore: Token.ink, altezza: 1.6),
                        ),
                        const SizedBox(height: 2.4),
                        Text(stato, style: piccolo.copyWith(fontWeight: FontWeight.w600)),
                        const SizedBox(height: 2.4),
                        Text(testo, style: piccolo),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
