/// «Elimina l'account» (`frontend/v2/pagine/elimina-account.tsx`, GDPR, Fase 1), alla rotta `/account/elimina`: cosa
/// succede e come fare, anche senza essere entrati.
///
/// - Chi non è entrato legge cosa succede ed entra per procedere.
/// - Chi è entrato può scaricare prima i suoi dati, poi conferma due volte: una casella («ho capito») e la parola da
///   scrivere. La richiesta chiude subito l'account e le sessioni; per 30 giorni, rientrando, la si può annullare; poi i
///   dati si cancellano (la contabilità resta, pseudonimizzata).
/// - **Nell'app** (Fase 9; Apple esige che si possa fare da qui): prima della richiesta questo telefono esce dalle
///   notifiche dell'account (con la sessione ancora valida); dopo, l'app esce da sola (revoca del token offline, token
///   locali cancellati: il server ha già chiuso le sessioni) e mostra la conferma. Un abbonamento comprato in uno store
///   non si ferma da solo: la pagina lo dice prima e dopo, col bottone per gestirlo nello store.
library;

import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../acquisti/acquisti.dart' show apriGestioneStore;
import '../auth/sessione.dart';
import '../componenti/bottoni.dart';
import '../componenti/campi.dart';
import '../componenti/formati.dart';
import '../componenti/pagina.dart';
import '../componenti/testi.dart';
import '../dati/dati.dart';
import '../l10n/testi.dart';
import '../lingua/lingua.dart';
import '../modelli/privacy.dart';
import '../profilo/comuni.dart';
import '../profilo/privacy_profilo.dart' show scaricaEsportazione;
import '../rotte/percorsi.dart';
import '../tema/tema.dart';

/// La pagina dell'eliminazione dell'account.
class EliminaAccount extends ConsumerStatefulWidget {
  /// La pagina.
  const EliminaAccount({super.key});

  @override
  ConsumerState<EliminaAccount> createState() => _EliminaAccountState();
}

class _EliminaAccountState extends ConsumerState<EliminaAccount> {
  /// La richiesta fatta (l'app è già uscita dall'account) e lo store dell'abbonamento, se ce n'era uno.
  ({StatoCancellazione stato, String? store})? _fatto;

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final sessione = ref.watch(sessioneProvider);
    final fatto = _fatto;
    final piccolo = Stile.sans(13.44, colore: Token.ink, altezza: 1.6);
    return Pagina(
      sezioni: [
        Sottotitolo(
          eyebrow: t.profilo_elimina_eyebrow,
          titolo: t.profilo_elimina_h1,
          intro: t.profilo_elimina_intro,
          compatta: true,
        ),
        Fascia(
          compatta: true,
          child: GrigliaProfilo(
            celle: [
              (
                widget: Sezione(
                  titolo: t.profilo_elimina_cosa_titolo,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12.8),
                      child: ElencoPuntato(
                        numerato: true,
                        spazio: 5.6,
                        voci: [
                          Text(t.profilo_elimina_passo1(30), style: piccolo),
                          Text(t.profilo_elimina_passo2, style: piccolo),
                          Text(t.profilo_elimina_passo3, style: piccolo),
                        ],
                      ),
                    ),
                    TitoloPannello(t.profilo_elimina_resta_titolo),
                    TestoPiccolo(t.profilo_elimina_resta),
                    TestoPiccolo(
                      t.profilo_elimina_app,
                      sotto: 0,
                      figlio: Collegamento(
                        t.profilo_stat_privacy,
                        href: R.privacy,
                        stile: Stile.sans(13.44, altezza: 1.6),
                      ),
                    ),
                  ],
                ),
                larga: true,
              ),
              if (fatto != null)
                (widget: _Fatto(stato: fatto.stato, store: fatto.store), larga: true)
              else if (sessione.pronta)
                (
                  widget: sessione.autenticata
                      ? _Conferma(alFatto: (r, store) => setState(() => _fatto = (stato: r, store: store)))
                      : const _Entra(),
                  larga: true,
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _Entra extends ConsumerWidget {
  const _Entra();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    return Sezione(
      titolo: t.profilo_elimina_entra_titolo,
      children: [
        TestoPiccolo(t.profilo_elimina_entra_testo),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(t.profilo_entra, alTocco: () => unawaited(entraDa(ref))),
        ),
      ],
    );
  }
}

/// L'abbonamento di uno store non si ferma con l'account: va disdetto nello store (Apple e Google lo chiedono).
class _AvvisoStore extends ConsumerWidget {
  const _AvvisoStore({required this.provider});

  /// `google_play` o `app_store`.
  final String provider;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final nome = provider == 'app_store' ? t.abbonamento_store_app_store : t.abbonamento_store_google_play;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.8),
      child: Avviso(
        null,
        sopra: 0,
        figlio: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(padding: const EdgeInsets.only(bottom: 9.6), child: Text(t.app_elimina_store(nome))),
            Bottone(
              t.abbonamento_store_apri(nome),
              variante: Variante.quieto,
              piccolo: true,
              alTocco: () => unawaited(apriGestioneStore(ref, provider)),
            ),
          ],
        ),
      ),
    );
  }
}

/// La richiesta è fatta: l'account è chiuso, i dati si cancelleranno alla data detta.
class _Fatto extends ConsumerWidget {
  const _Fatto({required this.stato, required this.store});

  final StatoCancellazione stato;
  final String? store;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final t = context.t;
    final lingua = ref.watch(linguaProvider);
    return Semantics(
      liveRegion: true,
      child: Sezione(
        titolo: t.profilo_elimina_fatto_titolo,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(t.profilo_elimina_fatto(dataLunga(stato.definitivaIl, lingua))),
          ),
          if (store != null) _AvvisoStore(provider: store!),
        ],
      ),
    );
  }
}

class _Conferma extends ConsumerStatefulWidget {
  const _Conferma({required this.alFatto});

  /// La richiesta è andata (e l'app è uscita dall'account): lo stato e lo store dell'abbonamento, se c'era.
  final void Function(StatoCancellazione stato, String? store) alFatto;

  @override
  ConsumerState<_Conferma> createState() => _ConfermaState();
}

class _ConfermaState extends ConsumerState<_Conferma> with AzioneAccount {
  final TextEditingController _parola = TextEditingController();
  bool _capito = false;
  String? _esportato;

  @override
  void initState() {
    super.initState();
    _parola.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _parola.dispose();
    super.dispose();
  }

  Future<void> _esporta() async {
    setState(() => _esportato = null);
    final r = await esegui((_) => scaricaEsportazione(ref, context));
    if (r != null && mounted) setState(() => _esportato = r);
  }

  Future<void> _elimina() async {
    final abbonamento = ref.read(contoProvider).value?.abbonamento;
    final store = abbonamento != null && abbonamento.store ? abbonamento.provider : null;
    // Con la sessione ancora valida: questo telefono esce dalle notifiche dell'account.
    await ref.read(primaDiUscireProvider).esegui();
    final r = await esegui((api) => api.chiediCancellazione());
    if (r == null || !mounted) return;
    widget.alFatto(r, store);
    // Il server ha chiuso le sessioni: l'app esce da sola (revoca del token offline, token locali cancellati).
    await ref.read(sessioneProvider.notifier).esci();
  }

  @override
  Widget build(BuildContext context) {
    final t = context.t;
    final abbonamento = ref.watch(contoProvider).value?.abbonamento;
    final parola = t.profilo_elimina_parola;
    final giusta = _parola.text.trim().toUpperCase() == parola.toUpperCase();
    return Sezione(
      titolo: t.profilo_elimina_titolo,
      children: [
        if (abbonamento != null && abbonamento.store && abbonamento.provider != null)
          _AvvisoStore(provider: abbonamento.provider!),
        TestoPiccolo(t.profilo_elimina_prima),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(
            t.profilo_esporta_cta,
            variante: Variante.quieto,
            piccolo: true,
            alTocco: inCorso ? null : () => unawaited(_esporta()),
          ),
        ),
        if (_esportato != null) Semantics(liveRegion: true, child: TestoPiccolo(_esportato!, sopra: 13.44, sotto: 0)),
        Padding(
          padding: const EdgeInsets.only(top: 12.8),
          child: Casella(
            valore: _capito,
            titolo: t.profilo_elimina_capito(30),
            alCambio: (v) => setState(() => _capito = v),
          ),
        ),
        // `.elimina-account .field input { max-width: 16rem }`.
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 256),
            child: CampoTesto(
              etichetta: t.profilo_elimina_scrivi(parola),
              controllore: _parola,
              maiuscole: true,
              attivo: _capito,
            ),
          ),
        ),
        Align(
          alignment: AlignmentDirectional.centerStart,
          child: Bottone(
            t.profilo_elimina_cta,
            variante: Variante.pericolo,
            alTocco: !_capito || !giusta || inCorso ? null : () => unawaited(_elimina()),
          ),
        ),
        if (errore != null) Errore(errore!),
      ],
    );
  }
}
